"""Re-run w-quiesce's real daemon observer with fresh before/after identities.

The imported observer mutates only caller-owned source after runtime admission,
restores after attached scoring, and never replaces observations or gate returns.
"""
import argparse
import datetime
import importlib.util
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
spec = importlib.util.spec_from_file_location("previous_quiesce_collector", REPO / "reports/w-quiesce-evidence/collect.py")
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--phase", choices=["before", "after"], required=True)
    args = parser.parse_args()
    base = args.work_root.resolve()
    assert not base.is_relative_to(REPO)
    assert args.run_id and all(c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_." for c in args.run_id)
    assert args.run_id not in {".", ".."}
    run = base / args.run_id
    run.mkdir(parents=True, exist_ok=False)
    packet = run / "packet"
    packet.mkdir()
    platform = run / "platform"
    shutil.copytree(old.FIXTURE, platform)
    pins = json.loads((platform / "trusted-pins.json").read_text())
    task = json.loads((platform / "task-source.json").read_text())
    raw = (platform / "task-contract.json").read_bytes()
    bundle_raw = (platform / "bundle.json").read_bytes()
    fixture_checks = {name: old.sha(platform / name) == digest for digest, name in
                      (line.split("  ", 1) for line in (platform / "SHA256SUMS").read_text().splitlines())}
    assert all(fixture_checks.values())
    verifier_spec = dict(kind="command", pass_when="exit0", argv=json.loads(bundle_raw)["scorer"]["argv"],
        scorer_bundle=dict(isolation_class="pristine-offline", root=str(platform / "closure"),
            manifest=str(platform / "bundle.json"), manifest_sha256=pins["manifest_sha256"],
            artifact_contract=str(platform / "task-contract.json"), artifact_contract_sha256=pins["artifact_contract_sha256"]))
    names = ["eval/verification/pristine.py", "eval/verification/verifier.py",
             "eval/admission/artifact_admission.py", "eval/admission/scorer_bundle.py",
             "eval/containers/container.py", "reports/w-quiesce-evidence/collect.py",
             str(Path(__file__).relative_to(REPO))]
    old.save(packet / "launch.json", dict(run_id=args.run_id, phase=args.phase, run_root=str(run),
        command=shlex.join([sys.executable, *sys.argv]), timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        git_head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
        source_hashes={name: old.sha(REPO / name) for name in names}, pins=pins, fixture_checks=fixture_checks,
        metric_identity=task["metric"], task=task, source_kind="locally authored control", split=None,
        endpoint=None, model=None, model_sha256=None, jobs=1, trials_per_case=1, eligible_tasks=1, selected_tasks=1,
        timeout_s=60, lifecycle=None, production_authorized=False, benchmark=False,
        comparability="same sealed authored control before/after source-observation change; no dataset equivalence"))
    old.save(packet / "host.json", {label: old.command(subprocess.run(argv, capture_output=True, text=True, timeout=30))
        for label, argv in [("id", ["id"]), ("image", ["docker", "image", "inspect", pins["runtime_image_id"]])]})
    os.environ["HARNESSGRAD_WORK_ROOT"] = str(base)
    selected = {}
    for label, answer, probe in [("unchanged", b"42\n", None), ("source-aba", b"41\n", "source-aba")]:
        source = old.source_tree(run / (label + "-source"), answer)
        for attempt in range(1, 21):
            case = f"{label}-attempt-{attempt:02d}"
            verdict, calls = old.production(packet / case, source, verifier_spec, task["task_id"], raw,
                                             pins["artifact_contract_sha256"], probe=probe)
            if "trusted artifact runtime boundary mismatch" in verdict.get("unmeasured", ""):
                continue  # Preserve every real refusal; use a fresh runtime/export UUID.
            selected[label] = case
            break
        else:
            raise AssertionError("no admitted fresh attempt; all refusals preserved")
    old.save(packet / "selection.json", selected)
    with (packet / "SHA256SUMS").open("x") as stream:
        for path in sorted(packet.rglob("*")):
            if path.is_file() and path.name != "SHA256SUMS":
                stream.write(f"{old.sha(path)}  {path.relative_to(packet).as_posix()}\n")
    print(json.dumps(dict(packet=str(packet), phase=args.phase, selected=selected)))


if __name__ == "__main__":
    main()
