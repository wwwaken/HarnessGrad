"""One real production pristine verifier call, plus three stopped refusal probes.

sys.setprofile observes original function returns; nothing replaces Docker, gates,
or verifier functions. Refusal probes use real newly created Docker instances and
the same production require_artifact_runtime checker, and never start a scorer.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import stat
import subprocess
import sys
import time

FIXTURE = Path(__file__).resolve().parent
REPO = FIXTURE.parents[2]
sys.path.insert(0, str(REPO))
from eval.admission import artifact_admission as artifacts
from eval.admission.pilot_admission import AdmissionError
from eval.containers import container
from eval.verification import verifier


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def inventory(root):
    return [dict(path=str(p.relative_to(root)), sha256=digest(p), bytes=p.stat().st_size,
                 mode=oct(stat.S_IMODE(p.stat().st_mode)), uid=p.stat().st_uid,
                 nlink=p.stat().st_nlink) for p in sorted(root.rglob("*")) if p.is_file()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    base = args.work_root.resolve()
    if base == REPO or REPO in base.parents:
        raise SystemExit("work root must be outside platform tree")
    run = base / args.run_id
    run.mkdir(parents=True, exist_ok=False)
    out = run / "evidence"
    out.mkdir()
    scorer = run / "platform/scorer"
    contracts = run / "platform/contracts"
    scorer.mkdir(parents=True)
    contracts.mkdir(parents=True)
    shutil.copytree(FIXTURE / "closure", scorer / "closure")
    shutil.copyfile(FIXTURE / "bundle.json", scorer / "bundle.json")
    shutil.copyfile(FIXTURE / "task-contract.json", contracts / "task.json")
    shutil.copyfile(FIXTURE / "trusted-pins.json", run / "platform/trusted-pins.json")
    pins = json.loads((run / "platform/trusted-pins.json").read_text())
    task = json.loads((FIXTURE / "task-source.json").read_text())
    actor = run / "actor"
    actor.mkdir()
    (actor / "answer.txt").write_text(task["control_submission"])
    (actor / "unselected.txt").write_text("Diagnostic decoy; must not enter export.\n")
    for path in actor.iterdir():
        path.chmod(0o444)
    actor.chmod(0o555)
    spec = dict(kind="command", pass_when="exit0",
        argv=json.loads((scorer / "bundle.json").read_text())["scorer"]["argv"],
        scorer_bundle=dict(isolation_class="pristine-offline", manifest=str(scorer / "bundle.json"),
            manifest_sha256=pins["manifest_sha256"], root=str(scorer / "closure"),
            artifact_contract=str(contracts / "task.json"),
            artifact_contract_sha256=pins["artifact_contract_sha256"]))
    save(out / "verifier-spec.json", spec)
    save(out / "launch.json", dict(run_id=args.run_id, work_root=str(base), run_root=str(run),
        argv=sys.argv, command=shlex.join([sys.executable, *sys.argv]),
        cwd=str(Path.cwd()), timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        task=task, pins=pins, endpoint=None, model=None, trials=1, jobs=1,
        production_authorized=False, control_kind="synthetic-diagnostic-only",
        source_snapshot=inventory(actor), closure_snapshot=inventory(scorer / "closure"),
        actor_pid=None, source_quiescence="No actor launched; prepared read-only files; same-UID custody only",
        git_head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
        source_hashes={name:digest(REPO / name) for name in [
            "eval/verification/pristine.py", "eval/verification/verifier.py",
            "eval/admission/artifact_admission.py", "eval/admission/scorer_bundle.py",
            "eval/containers/container.py", str(Path(__file__).relative_to(REPO))]}))
    calls, events = [], []
    watched = {"verify_scorer_files", "verify_state_export", "require_artifact_runtime",
               "_verify_artifact_runtime"}

    def observe(frame, event, result):
        filename = frame.f_code.co_filename
        name = frame.f_code.co_name
        if event == "return" and filename == container.__file__ and name == "docker":
            if isinstance(result, subprocess.CompletedProcess):
                index = len(calls)
                record = dict(index=index, argv=list(result.args), returncode=result.returncode,
                              stdout=result.stdout, stderr=result.stderr,
                              monotonic_ns=time.monotonic_ns())
                calls.append(record)
                save(out / f"docker-{index:02d}.json", record)
                if result.args[1] == "inspect" and result.returncode == 0:
                    save(out / f"inspect-{index:02d}.json", json.loads(result.stdout))
        if filename == artifacts.__file__ and name in watched and event in ("call", "return"):
            record = dict(function=name, event=event, monotonic_ns=time.monotonic_ns())
            if event == "return":
                record["returned"] = result
                for key in ("root", "artifact_root", "closure_root"):
                    if isinstance(frame.f_locals.get(key), Path):
                        root = frame.f_locals[key]
                        record[key] = str(root)
                        record[key + "_inventory"] = inventory(root)
            events.append(record)

    os.environ["HARNESSGRAD_WORK_ROOT"] = str(base)
    sys.setprofile(observe)
    try:
        verdict = verifier._verify(actor, spec, "", sandbox=False, timeout_s=60,
                                   task_id=task["task_id"])
    finally:
        sys.setprofile(None)
        save(out / "projection-rechecks.json", events)
    save(out / "verdict.json", verdict)
    save(out / "docker-calls.json", calls)
    create = next((c for c in calls if c["argv"][1] == "create" and c["returncode"] == 0), None)
    control_name = verdict.get("scorer_isolation_evidence", {}).get("cleanup", {}).get("container")
    if control_name:
        result = container.docker("inspect", control_name)
        save(out / "post-removal-inspect.json", dict(argv=result.args, returncode=result.returncode,
             stdout=result.stdout, stderr=result.stderr))
    exports = [c for c in calls if c["argv"][1] == "create"]
    if exports:
        mount = next(v for v in exports[0]["argv"] if "dst=/control-input" in v)
        source = Path(mount.split("src=", 1)[1].split(",", 1)[0])
        save(out / "post-return-projection.json", dict(path=str(source), exists=source.exists()))
    measured = isinstance(verdict.get("score"), (float, int)) and not verdict.get("unmeasured")
    save(out / "control-receipt.json", dict(schema="harnessgrad.w-pristine-control.v1",
        run_id=args.run_id, metric_identity=task["metric"], eligible_tasks=1, selected_tasks=1,
        task_coverage=[task["task_id"]], expected_trials=1, measured_trials=int(measured),
        unmeasured_trials=int(not measured), invalid_trials=0, score=verdict.get("score"),
        production_authorized=False, benchmark=False, staged_pilot=False,
        lifecycle=None, snapshot=dict(status="unknown", reason="no actor snapshot used"),
        scorer_isolation_class=verdict["scorer_isolation_class"],
        comparability="Authored exact-answer control only; no dataset/method equivalence or H0 authorization"))

    # Real stopped-instance negative controls. No observations are forged or edited.
    refusals = []
    if create:
        raw = (contracts / "task.json").read_bytes()
        alternate = container.docker("image", "inspect", "python:3.11-slim")
        save(out / "alternate-image-inspect.json", dict(argv=alternate.args,
            returncode=alternate.returncode, stdout=alternate.stdout, stderr=alternate.stderr))
        alternate.check_returncode()
        alternate_id = json.loads(alternate.stdout)[0]["Id"]
        for change in ("image", "network", "mount"):
            probe = run / ("refusal-" + change)
            probe.mkdir()
            name = "hg-wpristine-refusal-" + change + "-" + args.run_id
            exported = artifacts.export_state(actor, probe / "input", raw,
                pins["artifact_contract_sha256"], run_id=name)
            save(out / f"refusal-{change}-export.json", exported)
            cmd = create["argv"][1:].copy()
            cmd[cmd.index("--name") + 1] = name
            for i, value in enumerate(cmd):
                if "dst=/control-input" in value:
                    cmd[i] = f"type=bind,src={probe / 'input'},dst=/control-input,readonly"
            if change == "image":
                cmd[cmd.index(pins["runtime_image_id"])] = alternate_id
            elif change == "network":
                cmd[cmd.index("--network") + 1] = "bridge"
            else:
                extra = probe / "extra"
                extra.mkdir()
                cmd[1:1] = ["--mount", f"type=bind,src={extra},dst=/unexpected,readonly"]
            probe_calls = []

            def real(*argv):
                result = container.docker(*argv, timeout=30)
                probe_calls.append(dict(argv=result.args, returncode=result.returncode,
                    stdout=result.stdout, stderr=result.stderr))
                return result

            record = dict(change=change, run_id=name, score=None, started=False)
            try:
                real(*cmd).check_returncode()
                inspected = real("inspect", name)
                inspected.check_returncode()
                info = json.loads(inspected.stdout)[0]
                save(out / f"refusal-{change}-inspect.json", info)
                try:
                    admitted = artifacts.require_artifact_runtime(info, raw,
                        pins["artifact_contract_sha256"], artifact_root=probe / "input",
                        closure_root=scorer / "closure", export_receipt=exported, run_id=name)
                    record.update(refused=False, admission=admitted)
                except AdmissionError as exc:
                    record.update(refused=True, exception=type(exc).__name__, reason=str(exc))
            finally:
                removed = real("rm", "--force", name)
                record["removed"] = removed.returncode == 0
                absent = real("inspect", name)
                record["post_removal_inspect_returncode"] = absent.returncode
                save(out / f"refusal-{change}-commands.json", probe_calls)
                save(out / f"refusal-{change}-result.json", record)
            refusals.append(record)
    save(out / "refusals-summary.json", refusals)
    print(json.dumps(dict(evidence=str(out), verdict=verdict, refusals=refusals), indent=2))


if __name__ == "__main__":
    main()
