"""Reporting integration from fabricated events/results; no AppWorld payloads.

Use the current Console, progress and verdict writers without calling a runner,
verifier, adapter, model or container. The report subprocess denies those imports,
dataset file access, networking and subprocess execution.
"""
from __future__ import annotations

import io
import json
from pathlib import Path
import subprocess
import sys

import pytest

from eval.appworld_reporting import TGC_METRIC, build_report, make_manifest, receipts_from_verdicts
from eval.console import Console
from eval.tracing import _write_progress
from harnessgrad.records import _save_verdicts

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools/report_appworld.py"
PRIVATE = "FABRICATED_PRIVATE_FIELD"

# Install guards before running the CLI, including for imports that are attempted
# but subsequently caught. Dataset access and execution must never be necessary.
CLI_BOOTSTRAP = """
import importlib.abc
from pathlib import Path
import runpy
import sys

dataset_root = Path(sys.argv[1]).resolve().parents[1] / 'data'
class DenyExecutionImports(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if (fullname.split('.')[0] in {'data', 'appworld'}
                or fullname in {'eval.runner', 'eval.container', 'harnessgrad.trusted_runner'}):
            raise AssertionError('report attempted an execution/dataset import')
sys.meta_path.insert(0, DenyExecutionImports())
def deny_execution(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes)):
        name = args[0].decode() if isinstance(args[0], bytes) else args[0]
        if Path(name).resolve().is_relative_to(dataset_root):
            raise AssertionError('report attempted a dataset file read')
    if event.startswith(('socket.', 'subprocess.')) or event == 'os.system':
        raise AssertionError('report attempted networking or execution')
sys.addaudithook(deny_execution)
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name='__main__')
"""


def manifest():
    return make_manifest([
        {"task_id": f"{scenario}_{variant}", "source_split": split,
         "instruction": PRIVATE, "answer": PRIVATE}
        for scenario, split in (("normal", "test_normal"), ("challenge", "test_challenge"))
        for variant in (1, 2, 3)
    ])


def verdict(tid, success, split, **evidence_fields):
    return {"passed": success, "score": float(success), "kind": "command",
            "detail": PRIVATE,
            "evidence": {"task_id": tid, "source_split": split,
                         "metric": TGC_METRIC, "measured": True, "success": success,
                         "passes": [PRIVATE], "failures": [PRIVATE], **evidence_fields}}


def invoke(tmp_path, selected, source, *, trials=1, extra=(), out_name="report.json"):
    selected_path = tmp_path / "selected.json"
    selected_path.write_text(json.dumps(selected))
    out = tmp_path / out_name
    proc = subprocess.run(
        [sys.executable, "-c", CLI_BOOTSTRAP, str(TOOL),
         "--manifest", str(selected_path), "--verdicts", str(source),
         "--trials", str(trials), "--out", str(out), *extra],
        cwd=tmp_path, capture_output=True, text=True, timeout=10,
    )
    return proc, out


def fabricate_run(tmp_path, selected, trial_verdicts, *, round_no=4):
    """Persist fake results through current production writers; execute no tasks."""
    console = Console(tmp_path / "events.jsonl", stream=io.StringIO())
    try:
        console.emit("header", dataset="appworld", run_id="fabricated-codex169",
                     split={"train": [], "eval": [r["task_id"] for r in selected]})
        for index, row in enumerate(selected, 1):
            tid = row["task_id"]
            for v in trial_verdicts[tid]:
                with console.reporter.task(tid, round_no=round_no, index=index,
                                           total=len(selected)) as held:
                    console.progress("phase", task=tid, round=round_no,
                                     phase="verify", status="done", detail=PRIVATE)
                    held.score = v["score"]
            _write_progress(tmp_path, round_no, tid,
                            [{"verdict": v} for v in trial_verdicts[tid]], None)
        console.emit("round", round=round_no, score=0.75, detail=PRIVATE)
    finally:
        console.close()
    result = {
        "per_task": {tid: sum(v["score"] for v in vs) / len(vs)
                     for tid, vs in trial_verdicts.items()},
        "verdicts": {tid: vs[-1] for tid, vs in trial_verdicts.items()},
        "trial_verdicts": trial_verdicts,
    }
    _save_verdicts(tmp_path, round_no, result, [r["task_id"] for r in selected])
    return tmp_path / "verdicts" / f"round-{round_no}", tmp_path / "progress" / f"round-{round_no}"


def test_saved_receipts_measure_tgc_source_splits_and_same_trial_sgc(tmp_path):
    selected = manifest()
    # Normal variants 1/2 pass opposite trials. Each task has a positive mean,
    # but no normal scenario trial succeeds. Challenge succeeds in both trials.
    trials = {
        r["task_id"]: [verdict(r["task_id"],
                              r["scenario_id"] == "challenge" or r["variant"] == 3
                              or r["variant"] == trial,
                              r["source_split"], trial=trial)
                       for trial in (1, 2)]
        for r in selected
    }
    saved, _ = fabricate_run(tmp_path, selected, trials)
    # Reading only selected paths is essential; this must never be parsed.
    (saved / "unselected_1.json").write_text("not JSON: fabricated unselected receipt")
    proc, out = invoke(tmp_path, selected, saved, trials=2)
    assert proc.returncode == 0, proc.stderr
    report = json.loads(out.read_text())
    assert report["schema_version"] == 2
    assert report["metrics"]["TGC"]["identity"] == TGC_METRIC
    assert report["TGC"] == pytest.approx(5 / 6)
    assert report["SGC"] == 0.5
    assert report["by_split"]["test_normal"]["label"] == "Test-N"
    assert report["by_split"]["test_normal"]["TGC"] == pytest.approx(2 / 3)
    assert report["by_split"]["test_normal"]["SGC"] == 0.0
    assert report["by_split"]["test_challenge"]["label"] == "Test-C"
    assert report["by_split"]["test_challenge"]["SGC"] == 1.0
    assert report["coverage"]["measured_task_trials"] == 12
    assert report["coverage"]["measured_scenario_trials"] == 4
    assert report["coverage"]["unmeasured_task_trials"] == 0
    assert PRIVATE not in out.read_text() and "unselected" not in out.read_text()
    # Fresh output is required; existing receipts/reports cannot be overwritten.
    before = out.read_bytes()
    proc, _ = invoke(tmp_path, selected, saved, trials=2)
    assert proc.returncode != 0 and out.read_bytes() == before


def test_current_progress_and_events_cannot_substitute_for_tgc_evidence(tmp_path):
    selected = manifest()
    trials = {r["task_id"]: [verdict(r["task_id"], True, r["source_split"])]
              for r in selected}
    _, progress = fabricate_run(tmp_path, selected, trials)
    record = json.loads((progress / "normal_1.json").read_text())
    assert record["complete"] is True and record["score"] == 1.0
    assert record["trial_scores"] == [1.0]
    assert "evidence" not in record and "trials" not in record
    events = [json.loads(line) for line in (tmp_path / "events.jsonl").read_text().splitlines()]
    task_events = [e for e in events if e["kind"] == "task"]
    assert any(e.get("score") == 1.0 for e in task_events)
    assert all("trial" not in e and "evidence" not in e for e in task_events)

    # A progress directory fits the CLI's task-file shape but lacks scorer evidence.
    proc, out = invoke(tmp_path, selected, progress)
    assert proc.returncode == 0, proc.stderr
    report = json.loads(out.read_text())
    assert report["TGC"] is None and report["SGC"] is None
    assert report["coverage"]["measured_task_trials"] == 0
    assert report["coverage"]["recorded_unmeasured_task_trials"] == 6
    assert report["coverage"]["invalid_task_trials"] == 0
    assert report["coverage"]["missing_task_trials"] == 0
    assert PRIVATE not in out.read_text()

    proc, out = invoke(tmp_path, selected, progress, out_name="events-report.json",
                       extra=("--events", str(tmp_path / "events.jsonl")))
    assert proc.returncode != 0 and "unrecognized arguments: --events" in proc.stderr
    assert not out.exists()
    proc, out = invoke(tmp_path, selected, tmp_path / "events.jsonl", out_name="file-report.json")
    assert proc.returncode != 0 and "verdict directory does not exist" in proc.stderr
    assert not out.exists()


def test_missing_invalid_unmeasured_and_measured_zero_remain_distinct(tmp_path):
    selected = manifest()
    result = {
        "per_task": {"normal_1": 0.0, "normal_3": 1.0,
                     "challenge_1": 1.0, "challenge_3": 1.0},
        "verdicts": {
            "normal_1": verdict("normal_1", False, "test_normal"),
            "normal_3": verdict("normal_3", True, "test_normal", measured=False),
            "challenge_1": {"passed": True, "score": 1.0},  # legacy generic score
            "challenge_3": verdict("challenge_3", True, "test_challenge", metric="generic.score"),
        },
        "invalid": {"normal_2": {"stage": "provider", "detail": PRIVATE}},
    }
    _save_verdicts(tmp_path, 0, result, [r["task_id"] for r in selected])
    proc, out = invoke(tmp_path, selected, tmp_path / "verdicts/round-0")
    assert proc.returncode == 0, proc.stderr
    report = json.loads(out.read_text())
    assert report["TGC"] == 0.0 and report["SGC"] is None
    expected = {"normal_1": "measured", "normal_2": "invalid", "normal_3": "unmeasured",
                "challenge_1": "unmeasured", "challenge_2": "missing", "challenge_3": "invalid"}
    for tid, status in expected.items():
        cell = report["per_task"][tid]["trials"][0]
        assert cell["status"] == status
        assert cell["success"] is (False if status == "measured" else None)
    coverage = report["coverage"]
    assert coverage["measured_task_trials"] == 1
    assert coverage["invalid_task_trials"] == 2
    assert coverage["recorded_unmeasured_task_trials"] == 2
    assert coverage["missing_task_trials"] == 1
    assert coverage["unmeasured_task_trials"] == 5  # aggregate non-measurements
    assert coverage["expected_task_trials"] == 6
    assert report["by_split"]["test_challenge"]["TGC"] is None
    assert PRIVATE not in out.read_text()


@pytest.mark.parametrize("flags,expected", [
    ({"invalid": {"stage": "cleanup"}}, "invalid"),
    ({"unmeasured": "scorer did not run"}, "unmeasured"),
])
@pytest.mark.parametrize("position", ["task", "trial"])
def test_explicit_nonmeasurement_overrides_success_evidence(flags, expected, position):
    tid = "fabricated_1"
    saved = {"task_id": tid, "trials": [verdict(tid, True, "test_normal")]}
    (saved if position == "task" else saved["trials"][0]).update(flags)
    report = build_report(make_manifest([{"task_id": tid, "source_split": "test_normal"}]),
                          receipts_from_verdicts([saved]))
    assert report["TGC"] is None and report["SGC"] is None
    assert report["per_task"][tid]["trials"][0]["status"] == expected


def test_incomplete_saved_histories_never_claim_same_trial_sgc(tmp_path):
    selected = manifest()[:3]  # one complete fabricated challenge scenario
    trials = {r["task_id"]: [verdict(r["task_id"], True, r["source_split"])
                             for _ in range(1 if r["variant"] == 3 else 2)]
              for r in selected}
    saved, _ = fabricate_run(tmp_path, selected, trials)
    proc, out = invoke(tmp_path, selected, saved, trials=2)
    assert proc.returncode == 0, proc.stderr
    report = json.loads(out.read_text())
    assert report["TGC"] == 1.0 and report["SGC"] is None
    scenario = report["per_scenario"]["challenge"]
    assert scenario["trials"][0]["status"] == "unaligned_trials"
    assert report["coverage"]["measured_task_trials"] == 5
    assert report["coverage"]["missing_task_trials"] == 1


def test_source_split_contradiction_refuses_to_write_report(tmp_path):
    selected = manifest()
    trials = {r["task_id"]: [verdict(r["task_id"], True, r["source_split"])]
              for r in selected}
    trials["normal_1"][0]["evidence"]["source_split"] = "test_challenge"
    saved, _ = fabricate_run(tmp_path, selected, trials)
    proc, out = invoke(tmp_path, selected, saved)
    assert proc.returncode != 0 and "evidence source split mismatch" in proc.stderr
    assert not out.exists()


def test_cli_help_explains_input_and_trial_limits_without_dataset_access(tmp_path):
    proc, out = invoke(tmp_path, manifest(), tmp_path / "absent", extra=("--help",))
    assert proc.returncode == 0, proc.stderr
    help_text = " ".join(proc.stdout.split())
    assert "progress scores and events lack TGC evidence" in help_text
    assert "compacted histories cannot establish SGC" in help_text
    assert "existing files are never overwritten" in help_text
    assert not out.exists()
