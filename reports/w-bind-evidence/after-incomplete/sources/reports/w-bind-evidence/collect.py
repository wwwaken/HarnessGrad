"""Exclusive local Docker controls; genuine production results, no model or dataset run.

The only replacement is the deliberately hostile export producer / verdict producer
in the named defeat attempts. All exports still use export_state and all admission,
projection checks, container observations and scoring use unmodified production code.
"""
import argparse
import datetime
import hashlib
import inspect
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from eval.admission import artifact_admission as artifacts
from eval.containers import container
from eval.run import runner
from eval.verification import verifier


def save(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    base = args.work_root.resolve() / args.run_id
    assert not base.is_relative_to(REPO)
    base.mkdir(parents=True, exist_ok=False)
    packet = base / "packet"
    packet.mkdir()
    fixture = REPO / "tests/fixtures/hg_wpristine"
    for line in (fixture / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split("  ", 1)
        assert sha(fixture / name) == digest
    platform = base / "platform"
    shutil.copytree(fixture / "closure", platform / "closure")
    for name in ("bundle.json", "task-contract.json", "trusted-pins.json", "task-source.json"):
        shutil.copyfile(fixture / name, platform / name)
    pins = json.loads((platform / "trusted-pins.json").read_text())
    raw = (platform / "task-contract.json").read_bytes()
    task_id = json.loads(raw)["task_id"]
    spec = dict(kind="command", pass_when="exit0",
        argv=json.loads((platform / "bundle.json").read_text())["scorer"]["argv"],
        scorer_bundle=dict(isolation_class="pristine-offline", root=str(platform / "closure"),
            manifest=str(platform / "bundle.json"), manifest_sha256=pins["manifest_sha256"],
            artifact_contract=str(platform / "task-contract.json"), artifact_contract_sha256=pins["artifact_contract_sha256"]))
    source = base / "source"
    source.mkdir()
    (source / "answer.txt").write_bytes(b"42\n")
    sources = ["eval/admission/artifact_admission.py", "eval/verification/pristine.py",
               "eval/verification/verifier.py", "eval/run/runner.py", "reports/w-bind-evidence/collect.py"]
    for name in sources:
        target = packet / "sources" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / name, target)
    save(packet / "launch.json", dict(argv=sys.argv, utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        python=sys.executable, git_head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
        source_sha256={p: sha(REPO / p) for p in sources}, pins=pins, spec=spec,
        source=str(source), run_id=args.run_id, model=None, endpoint=None, production_authorized=False,
        metric="authored addition control: completed_check and exit0", selected_tasks=1, eligible_tasks=1,
        trials=1, jobs=1, limits=dict(timeout_s=60, memory="512m", cpus=1, pids=128)))
    native = "run_id" in inspect.signature(verifier._verify).parameters
    original_export, original_docker = artifacts.export_state, container.docker
    identity = dict(task_id=task_id, outer_run_id=args.run_id, trial_id="round-0.harness-.trial-1")

    def execute(label, foreign=None, omitted=False):
        case = packet / label
        case.mkdir()
        events, calls = [], []

        def export(*pos, **kw):
            producer = dict(identity)
            if foreign:
                producer[foreign] = identity[foreign] + "-foreign"
                if foreign == "task_id":
                    pos = list(pos)
                    contract = json.loads(pos[2])
                    contract["task_id"] = producer["task_id"]
                    pos[2] = json.dumps(contract).encode()
                    pos[3] = hashlib.sha256(pos[2]).hexdigest()
                if native:
                    kw["execution_binding"] = producer
            result = original_export(*pos, **kw)
            save(case / "producer-identity.json", producer)
            save(case / "export-receipt.json", result)
            (case / "export-answer.bin").write_bytes((pos[1] / "answer.txt").read_bytes())
            events.append(dict(event="genuine_export_return", monotonic_ns=time.monotonic_ns(), receipt=result))
            return result

        def docker(*pos, **kw):
            result = original_docker(*pos, **kw)
            calls.append(dict(argv=list(result.args), returncode=result.returncode,
                stdout=result.stdout, stderr=result.stderr, monotonic_ns=time.monotonic_ns()))
            return result

        save(case / "requested-identity.json", identity if not omitted else dict(task_id=task_id))
        artifacts.export_state, container.docker = export, docker
        try:
            kwargs = dict(task_id=task_id)
            if native and not omitted:
                kwargs.update(run_id=identity["outer_run_id"], trial_id=identity["trial_id"])
            verdict = verifier._verify(source, spec, "", sandbox=False, timeout_s=60, **kwargs)
        finally:
            artifacts.export_state, container.docker = original_export, original_docker
        save(case / "verdict.json", verdict)
        save(case / "events.json", events)
        save(case / "docker-calls.json", calls)
        cleanup = verdict.get("scorer_isolation_evidence", {}).get("cleanup")
        if cleanup:
            absent = original_docker("inspect", cleanup["container"], timeout=30)
            save(case / "absence.json", dict(argv=list(absent.args), returncode=absent.returncode,
                stdout=absent.stdout, stderr=absent.stderr))
        return verdict

    # Retain genuine environment-order refusals; each attempt has a fresh runtime UUID.
    for attempt in range(1, 4):
        good = execute(f"control-attempt-{attempt:02}")
        if good.get("score") == 1:
            selected = f"control-attempt-{attempt:02}"
            break
    else:
        raise RuntimeError("no measured control; inspect preserved attempts")
    execute("missing-identity", omitted=True)
    for dimension in identity:
        execute("foreign-export-" + dimension, foreign=dimension)
    original_run_one = runner.run_one
    replays = {}
    try:
        runner.run_one = lambda *_a, **_kw: dict(verdict=good, trace="", exit_code=0, stderr="")
        for dimension in identity:
            expected = dict(identity)
            expected[dimension] += "-foreign"
            result = runner._evaluate(base, [dict(task_id=expected["task_id"])], {},
                run_id=expected["outer_run_id"], round_no=1 if dimension == "trial_id" else 0,
                verifiers={expected["task_id"]: spec}, sandbox=False)
            save(packet / ("foreign-verdict-" + dimension + ".json"), result)
            replays[dimension] = dict(per_task=result["per_task"], invalid=result.get("invalid"))
    finally:
        runner.run_one = original_run_one
    outer_selected = None
    if native:
        harness = base / "harness"
        harness.mkdir()
        (harness / "harness.json").write_text(json.dumps(dict(name="binding-local-control", version="1", entrypoint="agent.py")))
        (harness / "agent.py").write_text(
            "import argparse,pathlib\n"
            "p=argparse.ArgumentParser();p.add_argument('--task');p.add_argument('--workdir')\n"
            "a=p.parse_args();pathlib.Path(a.workdir,'answer.txt').write_bytes(b'42\\n')\n")
        shutil.copytree(harness, packet / "harness-source")
        for attempt in range(1, 4):
            case = packet / f"native-outer-attempt-{attempt:02}"
            case.mkdir()
            calls, events = [], []

            def observe(frame, event, result):
                if frame.f_code is original_export.__code__ and event == "return" and isinstance(result, dict):
                    events.append(dict(event="genuine_export_return", receipt=result, monotonic_ns=time.monotonic_ns()))

            def record_docker(*pos, **kw):
                result = original_docker(*pos, **kw)
                calls.append(dict(argv=list(result.args), returncode=result.returncode,
                    stdout=result.stdout, stderr=result.stderr, monotonic_ns=time.monotonic_ns()))
                return result

            expected_run = args.run_id + f"-outer-attempt-{attempt:02}"
            save(case / "requested.json", dict(run_id=expected_run, task_id=task_id, trials=2,
                round_no=3, harness_sha=sha(harness / "agent.py"), jobs=1, source=harness.as_posix(),
                harness_revision_kind="SHA256 of exact authored agent.py bytes"))
            saved_profile = sys.getprofile()
            container.docker = record_docker
            sys.setprofile(observe)
            try:
                result = runner._evaluate(harness, [dict(task_id=task_id)], {},
                    run_id=expected_run, round_no=3, harness_sha=sha(harness / "agent.py"),
                    trials=2, jobs=1, verifiers={task_id: spec}, sandbox=False)
            finally:
                sys.setprofile(saved_profile)
                container.docker = original_docker
            save(case / "result.json", result)
            save(case / "events.json", events)
            save(case / "docker-calls.json", calls)
            for index, event in enumerate(events):
                absent = original_docker("inspect", event["receipt"]["run_id"], timeout=30)
                save(case / f"absence-{index+1}.json", dict(argv=list(absent.args), returncode=absent.returncode,
                    stdout=absent.stdout, stderr=absent.stderr))
            if result["per_task"] == {task_id: 1.0}:
                outer_selected = case.name
                break
        if outer_selected is None:
            raise RuntimeError("native outer runner failed; inspect preserved attempts")
    save(packet / "summary.json", dict(native_binding_api=native, selected_control=selected, replays=replays,
        selected_native_outer=outer_selected, original_verdict_path=selected + "/verdict.json",
        source_after_sha256=sha(source / "answer.txt")))
    files = sorted(p for p in packet.rglob("*") if p.is_file())
    (packet / "SHA256SUMS").write_text("".join(f"{sha(p)}  {p.relative_to(packet).as_posix()}\n" for p in files))
    print(packet)


if __name__ == "__main__":
    main()
