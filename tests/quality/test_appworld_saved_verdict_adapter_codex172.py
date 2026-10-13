"""Fabricated writer-to-report tests; no dataset, runtime, model or H0 execution."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from eval.appworld_reporting import TGC_METRIC, build_report, make_manifest, receipts_from_verdicts
from harnessgrad.records import _save_verdicts

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = "FABRICATED_PRIVATE_CODEX172"
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
    return make_manifest([{"task_id": f"fabricated_{v}", "source_split": "test_normal"}
                          for v in (1, 2, 3)])


def verdict(tid, success=True, *, trial=None, identity="verdict", **flags):
    v = {"score": 1.0, "passed": True, "kind": "command", "detail": PRIVATE,
         "evidence": {"task_id": tid, "source_split": "test_normal", "metric": TGC_METRIC,
                      "measured": True, "success": success, "passes": [PRIVATE]}, **flags}
    if trial is not None:
        (v if identity == "verdict" else v["evidence"])["trial"] = trial
    return v


def write_and_report(tmp_path, histories, *, trials, keep_history=True):
    result = {"per_task": {tid: 1.0 for tid in histories},
              "verdicts": {tid: vs[-1] for tid, vs in histories.items()}}
    if keep_history:
        result["trial_verdicts"] = histories
    before = deepcopy(result)
    _save_verdicts(tmp_path, 0, result, list(histories))
    assert result == before
    source = tmp_path / "verdicts/round-0"
    # Only selected paths may be read by the CLI.
    (source / "unselected_1.json").write_text("not JSON")
    selected = tmp_path / "manifest.json"
    selected.write_text(json.dumps(manifest()))
    out = tmp_path / "report.json"
    proc = subprocess.run(
        [sys.executable, "-c", CLI_BOOTSTRAP, str(ROOT / "tools/report_appworld.py"),
         "--manifest", str(selected), "--verdicts", str(source),
         "--trials", str(trials), "--out", str(out)],
        cwd=tmp_path, capture_output=True, text=True, timeout=10,
    )
    return proc, out, source


@pytest.mark.parametrize("identity", ["verdict", "evidence"])
@pytest.mark.parametrize("trial_ids", [(3, 1), (3,)])
def test_writer_cli_preserves_sparse_original_identities(tmp_path, identity, trial_ids):
    histories = {r["task_id"]: [verdict(r["task_id"], not (r["variant"] == 3 and t == 1),
                                       trial=t, identity=identity) for t in trial_ids]
                 for r in manifest()}
    proc, out, source = write_and_report(tmp_path, histories, trials=3)
    assert proc.returncode == 0, proc.stderr
    report = json.loads(out.read_text())
    assert report["TGC"] == pytest.approx(5 / 6 if len(trial_ids) == 2 else 1.0)
    assert report["SGC"] == (0.5 if len(trial_ids) == 2 else 1.0)
    scenario = report["per_scenario"]["fabricated"]["trials"]
    assert scenario[1]["status"] == "unmeasured" and scenario[2]["success"] is True
    for row in manifest():
        cells = report["per_task"][row["task_id"]]["trials"]
        assert cells[1]["status"] == "missing"
        assert all(cells[t - 1]["trial_aligned"] for t in trial_ids)
        saved = json.loads((source / (row["task_id"] + ".json")).read_text())
        assert len(saved["trials"]) == len(trial_ids)
        assert [(v if identity == "verdict" else v["evidence"])["trial"]
                for v in saved["trials"]] == list(trial_ids)
    assert PRIVATE not in out.read_text() and "unselected" not in out.read_text()


def test_writer_cli_preserves_identity_without_a_trial_history(tmp_path):
    histories = {r["task_id"]: [verdict(r["task_id"], trial=2)] for r in manifest()}
    proc, out, source = write_and_report(tmp_path, histories, trials=3, keep_history=False)
    assert proc.returncode == 0, proc.stderr
    report = json.loads(out.read_text())
    assert report["TGC"] == 1.0 and report["SGC"] == 1.0
    assert report["coverage"]["missing_task_trials"] == 6
    assert report["per_scenario"]["fabricated"]["trials"][1]["success"] is True
    assert json.loads((source / "fabricated_1.json").read_text())["trial"] == 2


@pytest.mark.parametrize("count", [1, 2])
def test_writer_cli_compacted_positions_stay_unaligned(tmp_path, count):
    histories = {r["task_id"]: [verdict(r["task_id"]) for _ in range(count)]
                 for r in manifest()}
    proc, out, _ = write_and_report(tmp_path, histories, trials=3)
    assert proc.returncode == 0, proc.stderr
    report = json.loads(out.read_text())
    assert report["TGC"] == 1.0 and report["SGC"] is None
    assert report["coverage"]["measured_task_trials"] == 3 * count
    for task in report["per_task"].values():
        assert all(c["trial_aligned"] is False for c in task["trials"][:count])
    assert all(c["status"] == "unaligned_trials"
               for c in report["per_scenario"]["fabricated"]["trials"][:count])


@pytest.mark.parametrize("planned_trials", [2, 3])
def test_writer_cli_mixed_history_reserves_known_identities(tmp_path, planned_trials):
    histories = {r["task_id"]: [verdict(r["task_id"], trial=3), verdict(r["task_id"])]
                 for r in manifest()}
    histories["fabricated_2"].reverse()
    proc, out, _ = write_and_report(tmp_path, histories, trials=planned_trials)
    if planned_trials == 2:
        assert proc.returncode != 0 and "trial outside requested coverage" in proc.stderr
        assert not out.exists()
    else:
        assert proc.returncode == 0, proc.stderr
    # The adapter assigns anonymous cells to unused coverage slots, never to trial 3.
    saved = [{"task_id": tid, "trials": vs} for tid, vs in histories.items()]
    before = deepcopy(saved)
    receipts = receipts_from_verdicts(saved, trials=3)
    assert saved == before
    report = build_report(manifest(), receipts, trials=3)
    if planned_trials == 3:
        assert json.loads(out.read_text()) == report
    assert report["SGC"] == 1.0
    for task in report["per_task"].values():
        assert task["trials"][0]["trial_aligned"] is False
        assert task["trials"][1]["status"] == "missing"
        assert task["trials"][2]["trial_aligned"] is True


@pytest.mark.parametrize("flags,status", [
    ({"invalid": {"stage": "cleanup", "detail": PRIVATE}}, "invalid"),
    ({"unmeasured": PRIVATE}, "unmeasured"),
])
@pytest.mark.parametrize("keep_history", [True, False])
def test_writer_cli_retains_nonmeasurement_flags(tmp_path, flags, status, keep_history):
    histories = {r["task_id"]: [verdict(r["task_id"], trial=2, **flags)] for r in manifest()}
    if keep_history:
        for tid, vs in histories.items():
            vs.insert(0, verdict(tid, trial=1))
    proc, out, _ = write_and_report(tmp_path, histories, trials=2, keep_history=keep_history)
    assert proc.returncode == 0, proc.stderr
    report = json.loads(out.read_text())
    assert report["TGC"] == (1.0 if keep_history else None)
    assert report["SGC"] == (1.0 if keep_history else None)
    for task in report["per_task"].values():
        assert task["trials"][1]["status"] == status
        assert task["trials"][1]["success"] is None
        assert task["trials"][0]["status"] == ("measured" if keep_history else "missing")
    assert PRIVATE not in out.read_text()


@pytest.mark.parametrize("success,generic_score", [(None, 1.0), (False, 1.0), (True, 0.0)])
def test_writer_cli_never_uses_generic_score_or_passed_for_success(tmp_path, success, generic_score):
    histories = {r["task_id"]: [verdict(r["task_id"], success, trial=t) for t in (1, 2)]
                 for r in manifest()}
    for vs in histories.values():
        for v in vs:
            v["score"] = generic_score
            v["passed"] = bool(generic_score)
            if success is None:
                del v["evidence"]
    proc, out, _ = write_and_report(tmp_path, histories, trials=2)
    assert proc.returncode == 0, proc.stderr
    report = json.loads(out.read_text())
    assert report["TGC"] == (float(success) if success is not None else None)
    assert report["SGC"] == (float(success) if success is not None else None)
    assert report["coverage"]["measured_task_trials"] == (6 if success is not None else 0)
    assert report["coverage"]["recorded_unmeasured_task_trials"] == (0 if success is not None else 6)


@pytest.mark.parametrize("contradiction,match", [
    ("duplicate", "duplicate task/trial receipt"),
    ("evidence", "evidence trial mismatch"),
])
def test_writer_cli_refuses_identity_contradictions(tmp_path, contradiction, match):
    histories = {r["task_id"]: [verdict(r["task_id"], trial=t) for t in (1, 2)]
                 for r in manifest()}
    second = histories["fabricated_1"][1]
    if contradiction == "duplicate":
        second["trial"] = 1
    else:
        second["evidence"]["trial"] = 1
    proc, out, _ = write_and_report(tmp_path, histories, trials=2)
    assert proc.returncode != 0 and match in proc.stderr
    assert not out.exists()


@pytest.mark.parametrize("saved,match", [
    ({"trial": True}, "trial outside"),
    ({"trial": 0}, "trial outside"),
    ({"trial": 4}, "trial outside"),
    ({"trial": "2"}, "trial outside"),
    ({"trial": None}, "trial outside"),
    ({"trial": 1, "evidence": {"trial": 2}}, "trial mismatch"),
    ({"trials": [{"trial": 2}, {"trial": 2}]}, "duplicate"),
    ({"trials": []}, "invalid saved trials"),
    ({"trials": [None]}, "invalid saved trial verdict"),
    ({"trials": [{}, {}, {}, {}]}, "exceed requested coverage"),
    ({"evidence": []}, "invalid saved evidence"),
])
def test_adapter_refuses_malformed_or_contradictory_identities(saved, match):
    entry = {"task_id": "fabricated_1", **saved}
    before = deepcopy(entry)
    with pytest.raises(ValueError, match=match):
        receipts_from_verdicts([entry], trials=3)
    assert entry == before


@pytest.mark.parametrize("trials", [0, True, "2"])
def test_adapter_refuses_invalid_planned_coverage(trials):
    with pytest.raises(ValueError, match="positive integer"):
        receipts_from_verdicts([], trials=trials)


def test_explicit_unaligned_marker_is_preserved_even_with_identity(tmp_path):
    histories = {r["task_id"]: [verdict(r["task_id"], trial=1, trial_aligned=False)]
                 for r in manifest()}
    proc, out, _ = write_and_report(tmp_path, histories, trials=1)
    assert proc.returncode == 0, proc.stderr
    report = json.loads(out.read_text())
    assert report["TGC"] == 1.0 and report["SGC"] is None
    assert report["per_scenario"]["fabricated"]["trials"][0]["status"] == "unaligned_trials"


def test_direct_report_refuses_evidence_trial_contradiction():
    v = verdict("fabricated_1", trial=2, identity="evidence")
    with pytest.raises(ValueError, match="evidence trial mismatch"):
        build_report(manifest(), [{"task_id": "fabricated_1", "trial": 1,
                                   "evidence": v["evidence"]}], trials=2)
