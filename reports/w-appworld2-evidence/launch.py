#!/usr/bin/env python3
"""One real diagnostic, with passive Docker observations; no runtime overrides.

This observer does not supply backend admission evidence or alter any gate.
Only the driver launches benchmark containers. Inspect/event commands are read-only.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import secrets
import shlex
import subprocess
import sys
import threading
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from data.datasets import appworld
from eval.policy import diagnostic_policy
from eval.run.metrics import diagnostic_task_set


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(name, body):
    (OUT / name).write_text(json.dumps(body, indent=2, default=str) + "\n")


def command(argv):
    p = subprocess.run(argv, capture_output=True, text=True, timeout=40)
    return dict(command=argv, observed_at=now(), returncode=p.returncode,
                stdout=p.stdout, stderr=p.stderr)


def main():
    run_id = "w-appworld2-" + datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ") + "-" + secrets.token_hex(4)
    work = Path("/tmp") / (run_id + "-work")
    runs_root = Path("/tmp/hg-appworld2-run-artifacts")
    run = runs_root / run_id
    assert not work.exists() and not run.exists()
    assert not (OUT / "launch-input.json").exists(), "never relaunch this packet"
    eligible = list(appworld.SPLIT["train"])
    selected = diagnostic_task_set(eligible)
    tid = selected[0]
    environment = {
        "HG_AGENT_BACKEND": "openai", "HG_AGENT_MODEL": "qwen3.5-9b-local",
        "HG_AGENT_BASE_URL": "http://127.0.0.1:8002/v1", "HG_AGENT_API_KEY": "local",
    }
    # Refuse hidden inherited policy/image/actor overrides instead of changing them.
    overrides = {k: v for k, v in os.environ.items() if k.startswith((
        "HG_APPWORLD_", "HG_AGENT_", "HG_SNAPSHOT_"))}
    save("inherited-overrides.json", overrides)
    assert not overrides, "review inherited overrides before launching"
    for name, argv in {
        "git-head.json": ["git", "rev-parse", "HEAD"],
        "git-status-before.json": ["git", "status", "--short"],
        "containers-before.json": ["docker", "ps", "-a", "--no-trunc", "--format", "{{json .}}"],
        "networks-before.json": ["docker", "network", "ls", "--no-trunc"],
        "disk-before.json": ["df", "-h", "/tmp", "/var/lib/docker"],
    }.items():
        save(name, command(argv))
    # Preserve relevant process lines only; never dump unrelated command-line secrets.
    ps = command(["ps", "-eo", "pid,comm,args"])
    ps["stdout"] = "\n".join(line for line in ps["stdout"].splitlines()
        if any(x in line for x in ("driver.py", "vllm", "unix_model_relay", "model_gateway"))) + "\n"
    ps["scope"] = "raw matching lines only; unrelated process arguments omitted"
    save("processes-before.json", ps)
    from driver import load_env
    # Match driver .env precedence and refuse hidden task/model/budget overrides.
    load_env(ROOT / ".env")
    hidden = {k: ("<redacted>" if "KEY" in k else v) for k,v in os.environ.items()
              if k.startswith(("HG_AGENT_", "HG_APPWORLD_", "HG_SNAPSHOT_")) and k not in environment}
    save("dotenv-overrides.json", hidden)
    assert not hidden, "review hidden .env overrides before launching"
    with urllib.request.urlopen(environment["HG_AGENT_BASE_URL"] + "/models", timeout=15) as response:
        models = json.load(response)
    save("endpoint-models.json", dict(url=environment["HG_AGENT_BASE_URL"] + "/models",
         observed_at=now(), body=models, model_completion_probe_sent=False))
    assert any(m["id"] == environment["HG_AGENT_MODEL"] for m in models["data"])
    request_body = dict(model=environment["HG_AGENT_MODEL"],
        messages=[dict(role="user", content="Reply with OK.")], max_tokens=16, temperature=0)
    request = urllib.request.Request(environment["HG_AGENT_BASE_URL"] + "/chat/completions",
        data=json.dumps(request_body).encode(), headers={"Content-Type": "application/json", "Authorization": "Bearer local"})
    with urllib.request.urlopen(request, timeout=90) as response:
        completion_bytes = response.read()
        completion_status = response.status
    (OUT / "endpoint-completion.raw.json").write_bytes(completion_bytes)
    save("endpoint-completion-request.json", dict(url=request.full_url, body=request_body,
        status=completion_status, observed_at=now(), purpose="generic connectivity probe, no task content"))
    completion = json.loads(completion_bytes)
    assert completion["choices"], "endpoint did not return a completion"
    images = dict(actor=appworld.IMAGE, service=appworld.SERVICE_IMAGE,
                  verifier=appworld.VERIFIER_IMAGE)
    for role, ref in images.items():
        result = command(["docker", "image", "inspect", ref])
        save("image-" + role + ".json", result)
        assert result["returncode"] == 0
    sources = [ROOT / "data/datasets/appworld.py", ROOT / "data/datasets/appworld/verify/check.py",
               ROOT / "data/datasets/appworld/cli/aw", appworld.BUNDLE, appworld.POOL]
    source_hashes = {str(p): sha(p) for p in sources}
    harness_hashes = {str(p.relative_to(ROOT)): sha(p) for p in sorted(
        (ROOT / "base_harness/loop").rglob("*")) if p.is_file() and "__pycache__" not in p.parts}
    split = dict(source=appworld.SPLIT_SOURCE, split=appworld.SPLIT,
                 eligible=eligible, selected=selected,
                 selected_metadata=appworld.reporting_manifest(selected))
    save("source-hashes.json", source_hashes)
    save("harness-hashes.json", harness_hashes)
    save("split-selection.json", split)
    manifest = dict(kind="observer launch manifest; not backend attestation", run_id=run_id,
                    trial_id=tid + ":1", images=images, environment=appworld.ENV[tid],
                    verifier=appworld.VERIFY[tid], selected=appworld.reporting_manifest(selected),
                    source_hashes=source_hashes, harness_hashes=harness_hashes,
                    endpoint=environment["HG_AGENT_BASE_URL"], model=environment["HG_AGENT_MODEL"],
                    model_weights_sha256=None, rounds=0, trials=1, jobs=1, work_root=str(work))
    save("launch-manifest.json", manifest)
    policy = dict(context=dict(dataset="appworld", side="train",
        metric=dict(name="appworld.task_goal_completion (TGC)",
                    scorer_sha256=sha(ROOT / "data/datasets/appworld/verify/check.py")),
        hashes=dict(source=diagnostic_policy.receipt_digest(source_hashes),
                    split=diagnostic_policy.receipt_digest(split),
                    manifest=diagnostic_policy.receipt_digest(manifest), model=None,
                    harness=diagnostic_policy.receipt_digest(harness_hashes)),
        endpoint=environment["HG_AGENT_BASE_URL"],
        limits=dict(resource=dict(cpus=2, memory_mb=4096, pids=1024,
                                  agent_timeout_s=900, verify_timeout_s=900),
                    budget=dict(max_steps=32, max_output_tokens_per_call=2048)),
        gates=dict(status="unknown", receipt_sha256=None,
                   detail="User authorizes one fresh unchanged-budget AppWorld actor diagnostic seeking authentic measured success. Shared and successful-task blockers remain open; no backend enforcement attestation."),
        comparability_notes=[
            "One deterministic task from the declared train+dev study pool; exact eligible count is in split-selection.json. No eval-side task or oracle is supplied to actor.",
            "Raw official scorer evidence and passive Docker observations are separate from staged publication; enforcement remains unobserved.",
            "No tuning, improvement, pilot expansion or production authorization. Model weight hash is unknown; source hashes are not complete transitive closure.",
            "Resource limits in policy describe requested actor/verifier configuration; service limits must be read from Docker observations."]))
    diagnostic_policy.validate_context(policy["context"])
    save("policy-input.json", policy)
    reason = ("User explicitly requests ONE fresh AppWorld diagnostic to attempt authentic successful measured actor-task evidence with the unchanged generic loop and existing budget. Dataset/shared gates remain unresolved and enforcement unobserved; preserve raw scorer outcome and formal publication refusal separately. No tuning, budget increase, expansion or production authorization.")
    argv = ["python3", "driver.py", "--harness", "loop", "--dataset", "appworld",
            "--sampling", "diagnostic", "--policy-evidence", str(OUT / "policy-input.json"),
            "--authorize-unobserved-diagnostic", reason, "--rounds", "0", "--trials", "1",
            "--jobs", "1", "--side", "train", "--improver", "none", "--run-id", run_id,
            "--runs-root", str(runs_root), "--work-root", str(work)]
    save("launch-input.json", dict(cwd=str(ROOT), argv=argv, environment=environment,
                                  run_id=run_id, task_id=tid, work_root=str(work), run_root=str(run),
                                  fresh_run_absent=True, fresh_work_absent=True))
    (OUT / "command.txt").write_text(shlex.join(["env", *[k+"="+v for k,v in environment.items()], *argv]) + "\n")
    seen, nets, copied, paths = {}, {}, set(), set()
    lock = threading.Lock()
    stop = threading.Event()
    since = str(int(time.time()) - 1)
    event_error = (OUT / "docker-events.stderr.txt").open("w")
    events = subprocess.Popen(["docker", "events", "--since", since, "--format", "{{json .}}"],
                              stdout=subprocess.PIPE, stderr=event_error, text=True, bufsize=1)

    def inspect_container(ident):
        probe = command(["docker", "inspect", ident])
        if probe["returncode"]:
            return
        obj = json.loads(probe["stdout"])[0]
        if not (run_id in json.dumps(obj.get("Mounts", []))
                or run_id in obj.get("Name", "")):
            return
        # No credential-bearing Config.Env is stored. Only explicit local bindings.
        obj["Config"]["Env"] = [e for e in obj["Config"].get("Env", []) if e.startswith((
            "HG_AGENT_BASE_URL=", "HG_AGENT_MODEL=", "HG_SVC_", "HG_ENV_TASK_ID="))]
        cid = obj["Id"]
        fingerprint = diagnostic_policy.receipt_digest(obj)
        with lock:
            if seen.get(cid) != fingerprint:
                seen[cid] = fingerprint
                with (OUT / "container-observations.jsonl").open("a") as f:
                    f.write(json.dumps(dict(observed_at=now(), command=probe["command"], inspect=obj)) + "\n")
            for mount in obj.get("Mounts", []):
                if mount.get("Type") != "bind":
                    continue
                src = Path(mount["Source"])
                if (src.name.startswith(("hg-task-", "hg-verdict-"))):
                    paths.add(str(src))
                if mount["Destination"] == "/verifier":
                    for filename in ("reward.txt", "evidence.json"):
                        source = src / filename
                        try:
                            data = source.read_bytes()
                        except OSError:
                            continue
                        digest = hashlib.sha256(data).hexdigest()
                        if (str(source), digest) not in copied:
                            target = "verifier-" + filename + "-" + digest
                            (OUT / target).write_bytes(data)
                            with (OUT / "verifier-file-observations.jsonl").open("a") as f:
                                f.write(json.dumps(dict(observed_at=now(), container_id=cid,
                                    source=str(source), target=target, sha256=digest, bytes=len(data))) + "\n")
                            copied.add((str(source), digest))
        for net in obj.get("NetworkSettings", {}).get("Networks", {}):
            if run_id not in net:
                continue
            p = command(["docker", "network", "inspect", net])
            if p["returncode"] == 0 and nets.get(net) != p["stdout"]:
                with lock:
                    nets[net] = p["stdout"]
                    with (OUT / "network-observations.jsonl").open("a") as f:
                        f.write(json.dumps(p) + "\n")

    def event_loop():
        for line in events.stdout:
            event = json.loads(line)
            attrs = event.get("Actor", {}).get("Attributes", {})
            if run_id in line or attrs.get("image") in images.values():
                ident = event.get("Actor", {}).get("ID", event.get("id"))
                if event.get("Type") == "container":
                    inspect_container(ident)
                if run_id in line or ident in seen:
                    with (OUT / "docker-events.jsonl").open("a") as f:
                        f.write(line)

    def poll_loop():
        while not stop.is_set():
            p = command(["docker", "ps", "-aq", "--no-trunc"])
            for ident in p["stdout"].split():
                inspect_container(ident)
            stop.wait(0.2)

    threads = [threading.Thread(target=event_loop), threading.Thread(target=poll_loop)]
    for t in threads:
        t.start()
    started = now()
    with (OUT / "driver.stdout.txt").open("w") as stdout, (OUT / "driver.stderr.txt").open("w") as stderr:
        p = subprocess.Popen(argv, cwd=ROOT, env={**os.environ, **environment}, stdout=stdout, stderr=stderr)
        save("driver-process.json", dict(pid=p.pid, started_at=started, run_id=run_id))
        rc = p.wait()
    stop.set()
    threads[1].join(timeout=50)
    events.terminate()
    events.wait(timeout=10)
    threads[0].join(timeout=50)
    event_error.close()
    save("driver-result.json", dict(returncode=rc, started_at=started, ended_at=now(),
                                   run_id=run_id, run_root=str(run), work_root=str(work)))
    cleanup = dict(run_id=run_id, observed_at=now(),
        containers=[command(["docker", "inspect", cid]) for cid in seen],
        networks=[command(["docker", "network", "inspect", net]) for net in nets],
        temporary_paths=[dict(path=p, exists=Path(p).exists()) for p in sorted(paths)],
        scoped_containers=command(["docker", "ps", "-a", "--filter", "label=harnessgrad.run="+run_id, "--no-trunc"]),
        scoped_networks=command(["docker", "network", "ls", "--filter", "label=harnessgrad.run="+run_id, "--no-trunc"]))
    save("cleanup-observations.json", cleanup)
    print(json.dumps(dict(run_id=run_id, returncode=rc, containers=len(seen), networks=len(nets))))


if __name__ == "__main__":
    main()
