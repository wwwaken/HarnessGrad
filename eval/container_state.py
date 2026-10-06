"""Measure one task whose state *is* the container's filesystem.

Split out of `eval/runner.py` (stage 4). INTERFACE.md §2.5.9: the harness runs inside the
task's own image, the platform snapshots the container afterwards, and the check runs
against that snapshot. It is the longest single path in the platform and the one with the
most moving parts -- a model gateway, a published network, a snapshot image, a teardown that
has to run even when the path above raised -- so it is the single function this split most
needed to isolate.

The seam: it takes a task and its environment and returns a result dict. It reads traces
through `eval.tracing` and takes verdicts through `eval.verifier`.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import eval.container as container_mod
import eval.harness_runtime as harness_runtime
import eval.modelgate as modelgate_mod
import eval.progress as progress_mod
import eval.services as services_mod
from eval.services import label
from ckpt.git_state import STATE_DIRNAME
from eval.integrity import PLATFORM_ROOT
from eval.tracing import _last_identity, _materialize
from eval.verifier import _verify_container_state

def _run_one_container_state(repo: Path, task: dict, *, env_spec: dict, setup,
                             verifier, timeout_s: int, verify_timeout_s: int,
                             run_id: str, run_seed: str,
                             recordings_root: Path | None,
                             runtime_paths: tuple[Path, ...] = ()) -> dict:
    """Run a task whose state is the container's own filesystem. INTERFACE.md §2.5.9.

    The order is the design, so it is spelled out here in the same steps the contract
    uses. What makes it worth its extra moving parts is step 6-7: the check's inputs and
    its reward directory are created **after** the harness has stopped, so the harness
    never had access to either -- which is what keeps §2.2's invariants true even though
    the task state travels by snapshot rather than by re-materialization.
    """
    repo = Path(repo).resolve()
    task_mount = env_spec.get("workdir") or container_mod.DEFAULT_WORKDIR
    tid = task["task_id"]
    name = label(f"hg-{run_id or 'run'}-{tid}")
    snapshot_tag = f"hg-snapshot:{label(f'{run_id or "run"}-{tid}')}"
    snapshot = None
    created = False
    network_name = None
    gateway = None
    answer = trace = ""
    #: The task this work belongs to, and the phases it reports. `None` outside a run
    #: (a unit test, a direct call), in which case every phase below is a no-op.
    held = progress_mod.task_of()
    phases = progress_mod.phases_for(held)

    # A throwaway host directory for what has to be copied in or read back out. Not a
    # bind mount: that is the whole point of this state kind.
    with tempfile.TemporaryDirectory(prefix="hg-cstate-") as tmp:
        staging = Path(tmp)
        try:
            # Step 1. The harness tree read-only at its own host path, and its scratch
            # space as a **tmpfs** -- so nothing the containerised harness writes as root
            # lands on the host, and the scratch is not committed into the graded
            # snapshot either.
            state_dir = repo / STATE_DIRNAME
            state_dir.mkdir(exist_ok=True)

            with phases("create"):
                # The internal network is created unconditionally: it is where the model
                # gateway is published, and a harness with no model is not being measured.
                network_name = services_mod.create_network(run_id or "run", tid)
                # The harness's own dependencies, resolved for this image's Python
                # version and mounted read-only from outside the image. It is a **bind
                # mount**, which is what keeps it out of the graded snapshot: measured,
                # `docker commit` records the mount target as an empty directory and
                # nothing under it, so the check's fresh container never sees these
                # packages. See `eval/harness_runtime.py`.
                image_python_here = container_mod.image_python(env_spec["image"])
                overlay = harness_runtime.lookup(
                    repo, image_python_here or sys.executable,
                    image=env_spec["image"],
                    image_digest=env_spec.get("image_digest"))

                container_mod.create(
                    name, image=env_spec["image"],
                    limits=container_mod.limits_from(env_spec), network=network_name,
                    run_id=run_id, task_id=task["task_id"],
                    extra_mounts=tuple(
                        ["--mount", f"type=bind,src={repo},dst={repo},readonly"]
                        + [a for pth in (tuple(runtime_paths)
                                         + harness_runtime.extra_paths(overlay)
                                         + (() if image_python_here
                                            else container_mod.interpreter_paths()))
                           for a in ("--mount",
                                     f"type=bind,src={pth},dst={pth},readonly")]),
                    # The harness's scratch and its HOME/XDG/TMPDIR are tmpfs, so nothing
                    # the platform created for its own bookkeeping ends up inside the
                    # snapshot the check grades. The snapshot should be the harness's work,
                    # not the platform's plumbing.
                    tmpfs=(str(state_dir),
                           container_mod.env_home(task_mount)))
            created = True
            if env_spec.get("network") == "bridge":
                container_mod.network_connect(name, "bridge")

            with phases("prepare"):
                # Step 2. SETUP, copied in rather than mounted.
                if setup and setup.get("files"):
                    _materialize(staging / "setup", setup.get("files"), PLATFORM_ROOT)
                    container_mod.cp_in(name, staging / "setup", task_mount,
                                        contents=True)

                manifest = json.loads((repo / "harness.json").read_text())
                entry = manifest["entrypoint"]
                task_file = staging / "task.json"
                task_file.write_text(json.dumps(task))
                container_mod.cp_in(name, task_file, f"{task_mount}/task.json")
                # No `mkdir` for the scratch or the home directory: they are `--tmpfs`
                # mounts, and docker creates their mount points at **create** time. The
                # first version called `mkdir_in` here, which uses `docker exec` -- and a
                # container that has not been started cannot be exec'd. Measured:
                # `container ... is not running`.

                image_python = container_mod.image_python(env_spec["image"])
                argv = [image_python or sys.executable, str(repo / entry), "--task",
                        f"{task_mount}/task.json", "--workdir", task_mount]

                child_env = container_mod.container_env(task_mount, deadline_s=timeout_s)
                child_env["HARNESSGRAD_STATE"] = str(state_dir)
                # Prepended, not replacing: a harness that sets its own `PYTHONPATH` is not
                # the platform's to overwrite.
                child_env.update(harness_runtime.env_for(overlay))

                # Step 3's precondition: the model has to be reachable from inside, and the
                # wrong fix is giving the task the internet it did not ask for.
                base = child_env.get("HG_AGENT_BASE_URL")
                if base and os.environ.get("HG_AGENT_BACKEND", "mock") != "mock" \
                        and modelgate_mod.is_host_local(base):
                    target, path = modelgate_mod.split(base)
                    bind = services_mod.gateway_ip(network_name)
                    gateway = modelgate_mod.ModelGateway(
                        bind_host=bind, target=target, path=path).start()
                    child_env["HG_AGENT_BASE_URL"] = gateway.base_url

                container_mod.start(name)

            # Step 3.
            exit_code, stderr = None, ""
            with phases("agent"):
                try:
                    proc = container_mod.exec_in(name, argv, cwd=task_mount,
                                                 env=child_env, timeout_s=timeout_s)
                    exit_code, stderr = proc.returncode, proc.stderr[-2000:]
                except subprocess.TimeoutExpired:
                    exit_code, stderr = -1, f"timeout after {timeout_s}s"

            with phases("snapshot"):
                # Step 4. Stopping the whole container is what makes "nothing the harness
                # started is still running" structural rather than best-effort, and a
                # stopped container is still committable.
                container_mod.stop(name)
                snapshot = container_mod.commit(name, snapshot_tag)

                # What the harness produced, read back out of the snapshot. `cp_out` is a
                # best-effort read: a harness that wrote no trace is a fact to record.
                if container_mod.cp_out(name, f"{task_mount}/trace.jsonl",
                                        staging / "trace.jsonl"):
                    trace = (staging / "trace.jsonl").read_text()
                if container_mod.cp_out(name, f"{task_mount}/answer.txt",
                                        staging / "answer.txt"):
                    answer = (staging / "answer.txt").read_text()

            # Steps 5-9.
            with phases("verify"):
                verdict = _verify_container_state(
                    snapshot, verifier, task_mount=task_mount, staging=staging,
                    timeout_s=verify_timeout_s, run_id=run_id or "run", task_id=tid,
                    network=env_spec.get("network", "none"),
                    limits=container_mod.limits_from(env_spec))

            return {"task_id": tid, "answer": answer, "trace": trace,
                    "exit_code": exit_code, "stderr": stderr, "verdict": verdict,
                    "env_usage": {}, "identity": _last_identity(trace),
                    "harness_runtime": harness_runtime.record(
                        overlay, platform_interpreter=(image_python_here is None)),
                    "model_gateway": ({"published": True,
                                       "target": f"{gateway.target[0]}:{gateway.target[1]}",
                                       **gateway.account()}
                                      if gateway is not None else None)}
        finally:
            # Teardown is a phase like any other, and it is the one that used to be
            # invisible while it took minutes: removing one image per task plus the
            # network, with nothing printed. It runs inside the task's context, so it
            # reports even when the path above raised.
            with phases("teardown"):
                if gateway is not None:
                    gateway.stop()
                if snapshot is not None:
                    container_mod.remove_image(snapshot)
                if created:
                    container_mod.remove_container(name)
                if network_name is not None:
                    services_mod.remove_network(network_name)
