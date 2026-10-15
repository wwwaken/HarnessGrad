"""Real daemon diagnostics; unchanged sealed fixture and production scoring code.

The profile callback observes production calls. Only the explicitly named negative
probes write source/export bytes; no function, receipt or Docker observation is replaced.
All outputs are exclusive, outside the repository. No model or benchmark is run.
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
import uuid

REPO = Path(__file__).resolve().parents[2]
FIXTURE = REPO / "tests/fixtures/hg_wpristine"
sys.path.insert(0, str(REPO))
from eval.admission import artifact_admission as artifacts
from eval.admission import scorer_bundle as bundles
from eval.admission.pilot_admission import AdmissionError
from eval.containers import container
from eval.verification import verifier


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def snapshot(root):
    return [dict(path=p.relative_to(root).as_posix(), bytes=p.stat().st_size,
                 sha256=sha(p), mode=oct(stat.S_IMODE(p.stat().st_mode)),
                 uid=p.stat().st_uid, gid=p.stat().st_gid, nlink=p.stat().st_nlink,
                 inode=p.stat().st_ino, mtime_ns=p.stat().st_mtime_ns,
                 ctime_ns=p.stat().st_ctime_ns)
            for p in sorted(root.rglob("*")) if p.is_file()]


def command(result):
    return dict(argv=list(result.args), returncode=result.returncode,
                stdout=result.stdout, stderr=result.stderr, monotonic_ns=time.monotonic_ns())


def source_tree(path, answer, *, decoy=True):
    path.mkdir()
    (path / "answer.txt").write_bytes(answer)
    if decoy:
        (path / "unselected.txt").write_bytes(b"Diagnostic decoy; not scorer input.\n")
    for p in path.iterdir():
        p.chmod(0o444)
    path.chmod(0o555)
    return path


def rewrite(path, data):
    # Deliberately exercise the existing platform-UID writer, including reversible
    # read-only permissions. Never claim this callback is a real dataset actor.
    mode = stat.S_IMODE(path.stat().st_mode)
    path.chmod(0o600)
    path.write_bytes(data)
    path.chmod(mode)


def production(case, source, spec, task_id, raw, pin, *, probe=None):
    case.mkdir()
    events, calls = [], []
    projection = None
    admission_passed = False
    changed = False
    saved_profile = sys.getprofile()

    def event(name, **values):
        events.append(dict(event=name, monotonic_ns=time.monotonic_ns(), **values))

    def observe(frame, kind, result):
        nonlocal projection, admission_passed, changed
        name, filename = frame.f_code.co_name, frame.f_code.co_filename
        if filename == artifacts.__file__:
            if name == "export_state" and kind == "call":
                event("before_export", source=str(source), inventory=snapshot(source))
            if name == "export_state" and kind == "return" and isinstance(result, dict):
                projection = frame.f_locals["destination"]
                event("export_return", projection=str(projection), receipt=result,
                      source_inventory=snapshot(source), projection_inventory=snapshot(projection))
                (case / "export-answer.bin").write_bytes((projection / "answer.txt").read_bytes())
                try:
                    artifacts.verify_state_export(projection, result, raw, pin,
                                                  run_id=result["run_id"] + "-wrong")
                except AdmissionError as exc:
                    event("wrong_run_refused", exception=type(exc).__name__, reason=str(exc))
                else:
                    raise AssertionError("wrong run was admitted")
                if probe == "projection-tamper":
                    rewrite(projection / "answer.txt", b"42\n")
                    event("projection_tamper", inventory=snapshot(projection))
                    (case / "tampered-answer.bin").write_bytes((projection / "answer.txt").read_bytes())
            if name in {"verify_scorer_files", "verify_state_export", "require_artifact_runtime"}:
                if kind == "return":
                    event("check_return", function=name, returned=result)
                    if name == "require_artifact_runtime" and isinstance(result, dict):
                        admission_passed = True
        if filename == container.__file__ and name == "docker":
            argv = frame.f_locals["args"]
            if kind == "call" and argv[0] == "start":
                if probe == "source-aba":
                    assert admission_passed and not changed
                    rewrite(source / "answer.txt", b"42\n")
                    changed = True
                    event("source_write_42", inventory=snapshot(source), projection=snapshot(projection))
                event("before_start", source_inventory=snapshot(source), projection_inventory=snapshot(projection))
            if kind == "return" and isinstance(result, subprocess.CompletedProcess):
                calls.append(command(result))
                if argv[0] == "start":
                    event("after_start", source_inventory=snapshot(source), projection_inventory=snapshot(projection))
                    if changed:
                        rewrite(source / "answer.txt", b"41\n")
                        changed = False
                        event("source_restore_41", inventory=snapshot(source))

    save(case / "binding.json", dict(outer_run_id=case.parent.parent.name + "-" + case.name,
         diagnostic_id=case.name, trial=1, task_id=task_id, source=str(source),
         source_before=snapshot(source), spec=spec, probe=probe,
         binding_scope="observer envelope; production receives task_id only, no outer run/trial"))
    (case / "source-before.bin").write_bytes((source / "answer.txt").read_bytes())
    sys.setprofile(observe)
    try:
        verdict = verifier._verify(source, spec, "", sandbox=False, timeout_s=60, task_id=task_id)
    finally:
        sys.setprofile(saved_profile)
        if changed:
            rewrite(source / "answer.txt", b"41\n")
        save(case / "events.json", events)
        save(case / "docker-calls.json", calls)
    save(case / "verdict.json", verdict)
    save(case / "source-after.json", snapshot(source))
    (case / "source-after.bin").write_bytes((source / "answer.txt").read_bytes())
    cleanup = verdict.get("scorer_isolation_evidence", {}).get("cleanup")
    if cleanup:
        save(case / "absence.json", command(container.docker("inspect", cleanup["container"], timeout=30)))
    if projection:
        save(case / "projection-after.json", dict(path=str(projection), exists=projection.exists()))
    return verdict, calls


def direct(case, source, receipt, create_template, raw, pin, bundle_raw, bundle_pin, closure):
    """Score the actual pre-state root, with a genuine export receipt and all gates.

    The initial materialization permits a legitimate selected-only reference mount.
    This is not a direct mount of a full arbitrary actor tree.
    """
    case.mkdir()
    calls = []
    name = receipt["run_id"]
    argv = create_template[1:].copy()  # discard only the docker executable
    argv[argv.index("--name") + 1] = name
    for i, value in enumerate(argv):
        if "dst=/control-input" in value:
            argv[i] = f"type=bind,src={source},dst=/control-input,readonly"

    def docker(*args):
        result = container.docker(*args, timeout=60)
        calls.append(command(result))
        return result

    save(case / "binding.json", dict(outer_run_id=case.parent.parent.name + "-" + case.name, diagnostic_id=case.name,
         trial=1, task_id=receipt["task_id"], source=str(source), export_receipt=receipt))
    save(case / "before.json", snapshot(source))
    error = None
    try:
        bundles.verify_bundle(closure, bundle_raw, bundle_pin)
        bundles.require_contract_bundle(raw, pin, bundle_raw, bundle_pin)
        docker(*argv).check_returncode()
        observed = docker("inspect", name)
        observed.check_returncode()
        admission = artifacts.require_artifact_runtime(json.loads(observed.stdout)[0], raw, pin,
            artifact_root=source, closure_root=closure, export_receipt=receipt, run_id=name)
        save(case / "admission.json", admission)
        started = docker("start", "--attach", name)
        stopped = docker("inspect", name)
        stopped.check_returncode()
        save(case / "result.json", dict(start_result=command(started),
             state=json.loads(stopped.stdout)[0]["State"]))
    except AdmissionError as exc:
        error = dict(exception=type(exc).__name__, reason=str(exc))
        save(case / "refusal.json", error)
    finally:
        removed = docker("rm", "--force", name)
        save(case / "cleanup.json", dict(removed=removed.returncode == 0, result=command(removed)))
        save(case / "absence.json", command(docker("inspect", name)))
        save(case / "docker-calls.json", calls)
        save(case / "after.json", snapshot(source))
    return error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    base = args.work_root.resolve()
    if base == REPO or REPO in base.parents:
        raise SystemExit("work root must be outside repository")
    if not args.run_id or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_." for c in args.run_id) or args.run_id in {".", ".."}:
        raise SystemExit("invalid fresh run label")
    run = base / args.run_id
    run.mkdir(parents=True, exist_ok=False)
    packet = run / "packet"
    packet.mkdir()
    fixture_checks = {}
    for line in (FIXTURE / "SHA256SUMS").read_text().splitlines():
        pin, name = line.split("  ", 1)
        fixture_checks[name] = sha(FIXTURE / name) == pin
    assert all(fixture_checks.values())
    pins = json.loads((FIXTURE / "trusted-pins.json").read_text())
    task = json.loads((FIXTURE / "task-source.json").read_text())
    platform = run / "platform"
    shutil.copytree(FIXTURE / "closure", platform / "closure")
    for name in ("bundle.json", "task-contract.json", "trusted-pins.json", "task-source.json"):
        shutil.copyfile(FIXTURE / name, platform / name)
    closure = platform / "closure"
    raw, bundle_raw = (platform / "task-contract.json").read_bytes(), (platform / "bundle.json").read_bytes()
    pin, bundle_pin = pins["artifact_contract_sha256"], pins["manifest_sha256"]
    spec = dict(kind="command", pass_when="exit0", argv=json.loads(bundle_raw)["scorer"]["argv"],
         scorer_bundle=dict(isolation_class="pristine-offline", root=str(closure),
             manifest=str(platform / "bundle.json"), manifest_sha256=bundle_pin,
             artifact_contract=str(platform / "task-contract.json"), artifact_contract_sha256=pin))
    names = ["eval/verification/pristine.py", "eval/verification/verifier.py",
             "eval/admission/artifact_admission.py", "eval/admission/scorer_bundle.py",
             "eval/containers/container.py", str(Path(__file__).relative_to(REPO))]
    save(packet / "launch.json", dict(run_id=args.run_id, run_root=str(run),
         argv=sys.argv, command=shlex.join([sys.executable, *sys.argv]), cwd=str(Path.cwd()),
         timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
         git_head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
         source_hashes={name: sha(REPO / name) for name in names}, pins=pins,
         fixture_checks=fixture_checks, fixture_manifest_sha256=sha(FIXTURE / "SHA256SUMS"),
         task=task, metric_identity=task["metric"], endpoint=None, model=None,
         model_sha256=None, split=None, jobs=1, trials_per_diagnostic=1,
         eligible_tasks=1, selected_tasks=1, benchmark=False, staged_pilot=False,
         timeout_s=60, production_authorized=False, lifecycle=None,
         comparability="authored control only; no applicable dataset or H0 claim"))
    save(packet / "host.json", {name: command(subprocess.run(argv, capture_output=True, text=True,
         timeout=30)) for name, argv in [("id", ["id"]), ("docker-info", ["docker", "info"]),
         ("image", ["docker", "image", "inspect", pins["runtime_image_id"]])]})
    os.environ["HARNESSGRAD_WORK_ROOT"] = str(base)
    actor = source_tree(run / "control-source", task["control_submission"].encode())
    selection = {}

    def measured(label, source, *, probe=None, expected=0.0):
        # Environment order is a real existing Docker/admission refusal. Preserve
        # every failed fresh execution; never edit/normalize observations or seals.
        for attempt in range(1, 21):
            name = f"{label}-attempt-{attempt:02d}"
            verdict, calls = production(packet / name, source, spec, task["task_id"], raw, pin, probe=probe)
            if verdict.get("outcome") == "measured":
                assert verdict["score"] == expected, verdict
                selection[label] = name
                return verdict, calls
            assert "trusted artifact runtime boundary mismatch" in verdict.get("unmeasured", ""), verdict
        raise AssertionError(f"no admitted fresh {label} attempt within bound; all receipts retained")

    verdict, calls = measured("working-control", actor)
    template = next(c["argv"] for c in calls if c["argv"][1] == "create")
    # Legitimate first projection supplies the reference's real receipt. It is then
    # the actual source of the second (production) export, not a forged source seal.
    for attempt in range(1, 21):
        pre = run / f"paired-source-{attempt:02d}"
        receipt = artifacts.export_state(actor, pre, raw, pin,
                                        run_id="hg-wquiesce-pre-" + uuid.uuid4().hex)
        pre.chmod(0o555)
        (pre / "answer.txt").chmod(0o444)
        name = f"pre-state-attempt-{attempt:02d}"
        error = direct(packet / name, pre, receipt, template, raw, pin, bundle_raw, bundle_pin, closure)
        if error is None:
            selection["pre-state"] = name
            save(packet / "source-materialization.json", receipt)
            break
        assert error["reason"] == "trusted artifact runtime boundary mismatch", error
    else:
        raise AssertionError("no admitted fresh pre-state attempt within bound")
    measured("post-export", pre)
    mutation_source = source_tree(run / "aba-source", b"41\n")
    measured("source-aba", mutation_source, probe="source-aba")
    production(packet / "projection-tamper", actor, spec, task["task_id"], raw, pin, probe="projection-tamper")
    changed_source = source_tree(run / "changed-answer-source", b"42\n")
    measured("changed-answer", changed_source, expected=1.0)
    production(packet / "wrong-task", actor, spec, task["task_id"] + "-wrong", raw, pin)
    save(packet / "source-final.json", {p.name: snapshot(p) for p in (actor, pre, mutation_source, changed_source)})
    save(packet / "selection.json", selection)
    # Manifest seals captured raw bytes; the separately invoked audit writes a new
    # file and never modifies these receipts. The external original is preserved.
    with (packet / "SHA256SUMS").open("x") as stream:
        for path in sorted(packet.rglob("*")):
            if path.is_file() and path.name != "SHA256SUMS":
                stream.write(f"{sha(path)}  {path.relative_to(packet).as_posix()}\n")
    print(json.dumps(dict(packet=str(packet), run_id=args.run_id, fixture_files=len(fixture_checks))))


if __name__ == "__main__":
    main()
