"""`placement: "inside"` selects the service container, and nothing else changes.

`placement` was declared by every `exec` dataset and read by no code: the value reached
`run_one` and was never looked at, so an environment that said `inside` and named a
service got a **second** container from `env.image` beside the service. These tests pin the
two halves of the fix:

* `inside` + exactly one service selects `eval/containers/service_exec.py`, and the argv is
  `docker exec -u <uid:gid> -w <task dir>` against that service's container;
* `placement` absent, `"beside"`, any other word, a `files` environment, or an environment
  with no service keeps the path it had before -- asserted by driving `_run_one` and
  checking **which launcher** was called, not by inspecting a string.

No Docker daemon is used here: `service_exec.run` is faked at the container boundary, and
the one test that needs a real daemon (`docker exec true` into a container this platform
started) skips on a host without one.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import uuid
from pathlib import Path
import pytest

import eval.containers.container as container_mod
import eval.containers.harness_runtime as harness_runtime
import eval.containers.sandbox as sandbox_mod
import eval.containers.service_exec as service_exec
import eval.run.runner as runner
import eval.service.services as services
from eval.containers import model_route, tool_route


def _service(**overrides) -> dict:
    spec = {"name": "appworld", "image": "harnessgrad/appworld-service@sha256:"
                                        + "d" * 64,
            "port": 8000, "cpus": 2, "memory_mb": 4096,
            "health": {"argv": ["true"], "timeout_s": 5}, "record": True}
    spec.update(overrides)
    return spec


def _env(**overrides) -> dict:
    spec = {"kind": "exec", "image": "harnessgrad/appworld-agent@sha256:" + "a" * 64,
            "workdir": "/appworld", "state": "mount", "network": "services",
            "placement": "inside", "services": [_service()],
            "cpus": 2, "memory_mb": 4096}
    spec.update(overrides)
    return spec


# --------------------------------------------------------------- the selection ---

def test_inside_with_one_service_selects_that_service_container():
    plan = service_exec.plan(_env())
    assert plan is not None
    assert plan.name == "appworld"
    assert plan.image == _service()["image"]


@pytest.mark.parametrize("placement", ["beside", "host", "outside", ""])
def test_every_other_placement_keeps_the_path_it_had(placement):
    """`beside` is the documented alternative; anything unrecognised is treated the same.

    Refusing to guess is the point: a word the platform does not implement must not be
    silently read as `inside`, because that is a different container and a different
    measurement.
    """
    assert service_exec.plan(_env(placement=placement)) is None


def test_placement_absent_keeps_the_path_it_had():
    """Truthiness alone is not the test: the *declaration* has to be there."""
    env = _env()
    del env["placement"]
    assert service_exec.plan(env) is None


def test_an_environment_with_no_service_is_not_rerouted():
    assert service_exec.plan(_env(services=[])) is None


def test_a_files_environment_never_execs_into_a_service():
    assert service_exec.plan({"kind": "files", "network": "none",
                              "placement": "inside", "services": [_service()]}) is None


def test_a_container_state_environment_is_not_rerouted():
    """`state: "container"` has its own long path and its own teardown."""
    assert service_exec.plan(_env(state="container")) is None


def test_two_services_are_refused_rather_than_guessed():
    with pytest.raises(service_exec.ServiceExecUnavailable) as exc:
        service_exec.plan(_env(services=[_service(), _service(name="other")]))
    assert "one service" in str(exc.value) or "exactly one" in str(exc.value)


# ------------------------------------------------------------------- the argv ---

def test_the_exec_argv_carries_the_declared_user_workdir_and_env(tmp_path):
    argv = service_exec.argv(container="cid123", workdir=tmp_path,
                             command=["python3", "agent.py", "--task", "t"],
                             env={"HG_AGENT_MODEL": "m", "LANG": "C"})
    assert argv[:2] == ["docker", "exec"]
    assert argv[2:4] == ["-u", service_exec.user()]
    assert argv[4:6] == ["-w", str(tmp_path)]
    # `-e KEY=VALUE` pairs, sorted, before the container name: the container is the last
    # positional, so nothing after it can be mistaken for an exec option.
    assert argv[6:10] == ["-e", "HG_AGENT_MODEL=m", "-e", "LANG=C"]
    assert argv[10] == "cid123"
    assert argv[11:] == ["python3", "agent.py", "--task", "t"]


def test_the_exec_user_is_the_one_the_service_was_started_with(monkeypatch):
    """`services.start` passes `--user uid:gid`; the exec must not become root."""
    monkeypatch.setattr(service_exec.os, "getuid", lambda: 4242)
    monkeypatch.setattr(service_exec.os, "getgid", lambda: 4343)
    assert service_exec.user() == "4242:4343"


def test_run_routes_through_the_container_client(monkeypatch):
    """The exec is an ordinary `docker exec` on the platform's own client, so it streams
    and beats inside a task (`eval/containers/container.py:docker`)."""
    seen = {}

    def fake_docker(*args, timeout=120):
        seen["args"] = args
        seen["timeout"] = timeout
        return subprocess.CompletedProcess(["docker", *args], 0, "", "")

    monkeypatch.setattr(container_mod, "docker", fake_docker)
    proc = service_exec.run(["true"], container="cid", workdir="/tmp/t", timeout_s=42)
    assert proc.returncode == 0
    assert seen["args"][:3] == ("exec", "-u", service_exec.user())
    assert seen["args"][-2:] == ("cid", "true")
    assert seen["timeout"] == 42


# ----------------------------------------------------------------- the mounts ---

def test_the_service_container_gets_the_task_tree_at_its_host_path(tmp_path):
    task = tmp_path / "hg-task-abc"
    harness = tmp_path / "workspace"
    state = harness / ".state"
    for path in (task, harness, state):
        path.mkdir(parents=True, exist_ok=True)
    mounts = service_exec.mounts(task_dir=task, harness_root=harness, state_dir=state)
    assert f"type=bind,src={task},dst={task}" in mounts          # writable, host path
    assert f"type=bind,src={harness},dst={harness},readonly" in mounts
    assert f"type=bind,src={state},dst={state}" in mounts        # writable scratch
    # The dataset's declared workdir is NOT a mount point: inside the service image it is
    # already the service's own data root.
    assert not any("/appworld" in mount for mount in mounts)


def test_the_mount_plan_publishes_the_sockets_at_the_fixed_destinations(tmp_path):
    """Same destinations as the bwrap path, so a harness cannot tell the placements apart."""
    source = tmp_path / "tool.sock"
    model = tmp_path / "model.sock"
    for path in (source, model):
        _touch_socket(path)
    tool_mounts = service_exec.mounts(task_dir=tmp_path / "task", harness_root=tmp_path,
                                      tool_socket=source, network="services")
    assert f"src={source},dst={tool_route.SOCKET},readonly" in " ".join(tool_mounts)
    assert f"src={tool_route.TRANSPORT_SOURCE},dst={tool_route.TRANSPORT},readonly" \
        in " ".join(tool_mounts)
    # The model route keeps its own rule (`network == "none"`), which is the rule it has on
    # every other path -- reaching for the model socket on a network is refused there too.
    model_mounts = service_exec.mounts(task_dir=tmp_path / "task", harness_root=tmp_path,
                                       model_socket=model, network="none")
    assert f"src={model},dst={model_route.ROOT / 'model.sock'},readonly" in " ".join(model_mounts)
    assert f"src={model_route.FORWARDER},dst={model_route.ROOT / 'forwarder.py'},readonly" \
        in " ".join(model_mounts)
    with pytest.raises(Exception):
        service_exec.mounts(task_dir=tmp_path / "task", harness_root=tmp_path,
                            model_socket=model, network="services")


def test_a_mount_path_docker_cannot_express_is_refused(tmp_path):
    awkward = tmp_path / "a,b"
    awkward.mkdir()
    with pytest.raises(service_exec.ServiceExecUnavailable):
        service_exec.mounts(task_dir=awkward, harness_root=tmp_path)


# ------------------------------------------------- the runner's own dispatch ---

class _FakeRunning:
    def __init__(self, name: str):
        self.network = "hg-run-task"
        self.containers = {name: "cid-" + name}
        self.recordings: dict[str, Path] = {}
        self.services = []

    def stop(self):
        return []

    def usage(self):
        return {}


def _repo(tmp_path: Path, *, env_kinds=("exec", "files")) -> Path:
    repo = tmp_path / "workspace"
    repo.mkdir()
    (repo / "harness.json").write_text(json.dumps(
        {"name": "fake", "entrypoint": "agent.py", "env_kinds": list(env_kinds),
         "runtime_paths": []}))
    (repo / "agent.py").write_text("# a harness\n")
    return repo


@pytest.fixture()
def launched(monkeypatch, tmp_path):
    """Everything `_run_one` needs except a daemon, and a record of what it launched."""
    calls: dict[str, object] = {"service_exec": [], "container_run": [],
                                "sandbox_run": [], "services_start": []}
    monkeypatch.setattr(container_mod, "image_python", lambda image: "/usr/bin/python3")
    monkeypatch.setattr(harness_runtime, "lookup", lambda *a, **k: None)

    def fake_start(specs, **kwargs):
        calls["services_start"].append({"specs": specs, **kwargs})
        return _FakeRunning(specs[0]["name"])

    monkeypatch.setattr(services, "start", fake_start)

    def fake_exec(command, **kwargs):
        calls["service_exec"].append({"command": command, **kwargs})
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(service_exec, "run", fake_exec)

    def fake_container_run(argv, **kwargs):
        calls["container_run"].append({"argv": argv, **kwargs})
        return subprocess.CompletedProcess(argv, 0, "", "")

    monkeypatch.setattr(container_mod, "run", fake_container_run)

    def fake_sandbox_run(argv, **kwargs):
        calls["sandbox_run"].append({"argv": argv, **kwargs})
        return subprocess.CompletedProcess(argv, 0, "", "")

    monkeypatch.setattr(sandbox_mod, "run", fake_sandbox_run)
    monkeypatch.setattr(runner, "_verify",
                        lambda *a, **k: {"kind": "command", "passed": True, "score": 1.0})
    return calls


def _task() -> dict:
    return {"task_id": "t1", "goal": "do the thing"}


def _run(repo: Path, env: dict) -> dict:
    return runner._run_one(repo, _task(), timeout_s=60, sandbox=True, setup=None,
                           verifier={"kind": "command"}, verify_timeout_s=60,
                           env=env, run_id="run", run_seed="0", recordings_root=None)


def test_inside_launches_one_exec_into_the_service_container(launched, tmp_path):
    repo = _repo(tmp_path)
    result = _run(repo, _env())
    assert not launched["container_run"], "a second container must not be started"
    assert not launched["sandbox_run"], "the host path must not be used"
    execs = launched["service_exec"]
    assert len(execs) == 1
    call = execs[0]
    assert call["container"] == "cid-appworld"
    # The task's *host* path as the working directory, and the same path in the argv: no
    # translation, which is what lets the harness's own record match the filesystem.
    assert call["workdir"].name.startswith("hg-task-")
    command = call["command"]
    assert command[0] == "/usr/bin/python3"
    assert command[2] == "--task" and command[3].endswith("/task.json")
    assert command[4] == "--workdir" and command[5] == str(call["workdir"])
    receipt = result["runtime_boundary"]
    assert receipt["agent_placement"] == "inside-service"
    assert receipt["service"] == "appworld"
    assert receipt["container"] == "cid-appworld"
    assert receipt["teardown"].startswith("service container removal")


def test_inside_hands_the_service_container_the_task_tree(launched, tmp_path):
    repo = _repo(tmp_path)
    _run(repo, _env())
    start = launched["services_start"][0]
    mounts = start["exec_mounts"]["appworld"]
    task_bind = [m for m in mounts if m.startswith("type=bind,src=") and
                 ",readonly" not in m]
    assert task_bind, mounts
    assert f"dst={task_bind[0].split('dst=')[1]}" in task_bind[0]
    assert "src=" + str(repo.resolve()) in " ".join(mounts)


def test_placement_absent_keeps_the_host_launcher(launched, tmp_path):
    """The pin the change must not move: no observation, no second opinion, same launcher."""
    repo = _repo(tmp_path)
    env = _env()
    del env["placement"]
    env["kind"] = "files"
    env.pop("services")
    env["network"] = "none"
    _run(repo, env)
    assert not launched["service_exec"], "a files environment must never exec into anything"
    assert len(launched["sandbox_run"]) == 1
    # `sandbox_mod.run` takes the harness's *own* argv and wraps it, so the namespace is
    # proved here by the call itself and by `sandbox.command` below.
    call = launched["sandbox_run"][0]
    assert call["task_dir"].name.startswith("hg-task-")
    assert call["network"] == "none"


def test_the_host_path_still_builds_a_bwrap_argv_and_no_exec(tmp_path):
    """The other half of the same pin: what `sandbox_mod.run` would have produced."""
    task = tmp_path / "hg-task-x"
    task.mkdir()
    argv = sandbox_mod.command(["python", "agent.py"], platform=runner.PLATFORM_ROOT,
                               work_root=tmp_path, task_dir=task, env={})
    assert Path(argv[0]).name.endswith("bwrap") or "bwrap" in argv[0]
    assert "docker" not in argv
    assert "exec" not in argv
    assert argv[-2:] == ["python", "agent.py"]


def test_beside_keeps_the_second_container_launcher(launched, tmp_path):
    repo = _repo(tmp_path)
    _run(repo, _env(placement="beside"))
    assert not launched["service_exec"]
    assert len(launched["container_run"]) == 1
    assert launched["container_run"][0]["image"] == _env()["image"]


def test_no_service_keeps_the_second_container_launcher(launched, tmp_path):
    repo = _repo(tmp_path)
    _run(repo, _env(services=[], network="none"))
    assert not launched["service_exec"]
    assert len(launched["container_run"]) == 1
    # Without a service there is nothing to bind into, and the service call is never made.
    assert not launched["services_start"]


# ------------------------------------------------------------- a real container ---

def _touch_socket(path: Path) -> None:
    import socket
    path.parent.mkdir(parents=True, exist_ok=True)
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.bind(str(path))


def _usable_image() -> str | None:
    """A tiny image already on this daemon. Never pulled: a test may not use the network."""
    if shutil.which("docker") is None:
        return None
    for candidate in ("python:3.11-slim", "docker.m.daocloud.io/library/python:3.11-slim",
                      "busybox:latest", "busybox", "debian:bookworm-slim"):
        try:
            proc = subprocess.run(["docker", "image", "inspect", candidate],
                                  capture_output=True, text=True, timeout=60)
        except (OSError, subprocess.TimeoutExpired):
            return None
        if proc.returncode == 0:
            return candidate
    return None


@pytest.mark.skipif(shutil.which("docker") is None, reason="no docker client on this host")
def test_a_real_container_can_be_exec_d_into_and_is_then_removed(tmp_path):
    """The end-to-end shape, on whatever daemon this host has.

    Starts one service container the way `services.start` does, `docker exec`s into it
    through this module, checks that the task directory really is visible at its host path
    and that the process really is the container's declared user, and then asserts the
    container and its network are gone. Skips rather than fails when the daemon is absent
    or unusable, because a unit-test lane is not a host qualification.
    """
    image = _usable_image()
    if image is None:
        pytest.skip("no small image on this daemon to start a container from")
    try:
        pinned = container_mod.resolve_digest(image)
    except container_mod.ContainerUnavailable as exc:
        pytest.skip(f"the daemon is not usable: {exc}")
    if container_mod.available() is None:
        pytest.skip("docker is installed but no daemon answers")

    task_dir = tmp_path / ("hg-task-" + uuid.uuid4().hex)
    task_dir.mkdir()
    (task_dir / "task.json").write_text("{}")
    harness = tmp_path / "workspace"
    harness.mkdir()
    name = "tiny"
    run_id = "unit-" + uuid.uuid4().hex[:12]
    spec = {"name": name, "image": pinned, "port": 8000,
            "health": {"argv": ["true"], "timeout_s": 30},
            "command": ["sleep", "300"], "record": False}
    running = services.start([spec], recordings_root=tmp_path / "recordings",
                             run_id=run_id, task_id="t1", run_seed="0",
                             exec_mounts={name: service_exec.mounts(
                                 task_dir=task_dir, harness_root=harness)})
    container = running.containers[name]
    try:
        proc = service_exec.run(
            ["sh", "-c", f"pwd && test -f {task_dir}/task.json && id -u"],
            container=container, workdir=task_dir, timeout_s=120)
    finally:
        problems = running.stop()
    assert not problems, problems
    assert proc.returncode == 0, proc.stderr
    lines = proc.stdout.splitlines()
    assert lines[0] == str(task_dir), "the task directory is not where the host path says"
    assert lines[1] == str(service_exec.os.getuid()), "the exec did not run as the platform's uid"
    left = subprocess.run(["docker", "container", "ls", "--all", "--quiet",
                           "--filter", f"name={run_id}"],
                          capture_output=True, text=True, timeout=60)
    assert not left.stdout.strip(), "the service container was left behind"
    nets = subprocess.run(["docker", "network", "ls", "--quiet",
                           "--filter", f"name={run_id}"],
                          capture_output=True, text=True, timeout=60)
    assert not nets.stdout.strip(), "the task network was left behind"
