"""Synthetic saved-verdict writer/report regressions; no benchmark execution."""
from __future__ import annotations

import builtins
from copy import deepcopy
import io
import json
from pathlib import Path
import socket
import subprocess

import pytest

from eval.appworld_reporting import TGC_METRIC, build_report, make_manifest, receipts_from_verdicts
from harnessgrad.records import _save_verdicts

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = "FABRICATED_PRIVATE_CODEX183"


@pytest.fixture(autouse=True)
def reporting_only(monkeypatch, tmp_path):
    """Guard the exercised writer/report path against payload reads or execution."""
    original_import, original_open = builtins.__import__, io.open

    def guarded_import(name, *args, **kwargs):
        assert name.split(".")[0] not in {"data", "appworld"}
        assert name not in {"eval.runner", "eval.container", "harnessgrad.trusted_runner"}
        return original_import(name, *args, **kwargs)

    def guarded_open(path, *args, **kwargs):
        if isinstance(path, (str, bytes, Path)):
            resolved = Path(path).resolve()
            assert resolved.is_relative_to(ROOT) or resolved.is_relative_to(tmp_path)
            assert not resolved.is_relative_to(ROOT / "data")
        return original_open(path, *args, **kwargs)

    def denied(*args, **kwargs):
        pytest.fail("writer/report attempted networking or runtime execution")

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    monkeypatch.setattr(io, "open", guarded_open)
    monkeypatch.setattr(socket, "socket", denied)
    monkeypatch.setattr(subprocess, "Popen", denied)


def selected():
    return make_manifest([
        {"task_id": f"{scenario}_{variant}", "source_split": split}
        for scenario, split in (("synthetic_n", "test_normal"),
                                ("synthetic_c", "test_challenge"))
        for variant in (1, 2, 3)
    ])


def verdict(row, *, success=True, trial=None, identity="verdict", **flags):
    value = {"score": 0.25, "passed": False, "kind": "command", "detail": PRIVATE,
             "evidence": {"task_id": row["task_id"], "source_split": row["source_split"],
                          "metric": TGC_METRIC, "measured": True, "success": success,
                          "passes": [PRIVATE]}, **flags}
    if trial is not None:
        (value if identity == "verdict" else value["evidence"])["trial"] = trial
    return value


def persist(tmp_path, result):
    before = deepcopy(result)
    _save_verdicts(tmp_path, 7, result, [row["task_id"] for row in selected()])
    assert result == before
    directory = tmp_path / "verdicts/round-7"
    saved = [json.loads(path.read_text()) for path in sorted(directory.glob("*.json"))]
    return saved


def report(saved, *, trials=3):
    before = deepcopy(saved)
    result = build_report(selected(), receipts_from_verdicts(saved, trials=trials), trials=trials)
    assert saved == before
    assert PRIVATE not in json.dumps(result)
    return result


@pytest.mark.parametrize("identity", ["verdict", "evidence"])
@pytest.mark.parametrize("records", ["verdicts", "trial_verdicts"])
def test_evidence_only_selected_records_keep_scorer_facts_and_original_ids(tmp_path, identity, records):
    values = {row["task_id"]: verdict(row, success=row["variant"] != 3,
                                     trial=3, identity=identity) for row in selected()}
    result = {records: {tid: [value] if records == "trial_verdicts" else value
                        for tid, value in values.items()}}
    result[records]["unselected_1"] = [None] if records == "trial_verdicts" else None
    # The unselected score is also excluded from this writer's selected task set.
    result["per_task"] = {"unselected_1": 1.0}
    saved = persist(tmp_path, result)
    assert len(saved) == 6
    for entry in saved:
        cell = entry["trials"][0] if records == "trial_verdicts" else entry
        assert entry["score"] is None
        assert cell["evidence"] == values[entry["task_id"]]["evidence"]
        assert (cell if identity == "verdict" else cell["evidence"])["trial"] == 3
        assert cell["trial_aligned"] is True
    measured = report(saved)
    assert measured["TGC"] == pytest.approx(2 / 3) and measured["SGC"] == 0.0
    assert measured["coverage"]["missing_task_trials"] == 12
    assert measured["by_split"]["test_normal"]["label"] == "Test-N"
    assert measured["by_split"]["test_challenge"]["label"] == "Test-C"


@pytest.mark.parametrize("count", [1, 2])
def test_anonymous_compacted_histories_cannot_gain_alignment_from_report_coverage(tmp_path, count):
    histories = {row["task_id"]: [verdict(row, trial_aligned=True) for _ in range(count)]
                 for row in selected()}
    saved = persist(tmp_path, {"trial_verdicts": histories})
    for entry in saved:
        assert all("trial" not in cell and "trial" not in cell["evidence"]
                   and cell["trial_aligned"] is False for cell in entry["trials"])
    for planned in (count, 3):
        measured = report(saved, trials=planned)
        assert measured["TGC"] == 1.0 and measured["SGC"] is None
        assert measured["coverage"]["measured_task_trials"] == 6 * count
        assert measured["coverage"]["measured_scenario_trials"] == 0
        assert all(scenario["trials"][0]["status"] == "unaligned_trials"
                   for scenario in measured["per_scenario"].values())


def test_anonymous_final_verdict_is_unaligned_even_for_one_report_slot(tmp_path):
    saved = persist(tmp_path, {"verdicts": {row["task_id"]: verdict(row)
                                          for row in selected()}})
    assert all(entry["trial_aligned"] is False and "trial" not in entry for entry in saved)
    measured = report(saved, trials=1)
    assert measured["TGC"] == 1.0 and measured["SGC"] is None


@pytest.mark.parametrize("flag,status", [("invalid", "invalid"), ("unmeasured", "unmeasured")])
def test_result_level_flags_are_saved_without_scores_and_override_claimed_success(tmp_path, flag, status):
    values = {row["task_id"]: verdict(row, trial=2) for row in selected()}
    result = {"verdicts": values, flag: {tid: {"detail": PRIVATE} for tid in values}}
    saved = persist(tmp_path, result)
    assert all(entry[flag] == {"detail": PRIVATE} for entry in saved)
    measured = report(saved)
    assert measured["TGC"] is None and measured["SGC"] is None
    assert all(task["trials"][1]["status"] == status
               and task["trials"][1]["success"] is None
               for task in measured["per_task"].values())


def test_flag_only_receipts_stay_recorded_and_missing_is_distinct(tmp_path):
    saved = persist(tmp_path, {"invalid": {"synthetic_n_1": {"stage": "cleanup"}},
                               "unmeasured": {"synthetic_c_1": "scorer unavailable"}})
    assert len(saved) == 2 and all(entry["score"] is None for entry in saved)
    measured = report(saved, trials=1)
    assert measured["TGC"] is None
    assert measured["coverage"]["invalid_task_trials"] == 1
    assert measured["coverage"]["recorded_unmeasured_task_trials"] == 1
    assert measured["coverage"]["missing_task_trials"] == 4


def test_trial_flags_do_not_poison_other_explicit_trials(tmp_path):
    histories = {row["task_id"]: [verdict(row, trial=3, invalid=False, unmeasured=False),
                                       verdict(row, trial=1, invalid={"stage": "cleanup"}),
                                       verdict(row, trial=2, unmeasured=PRIVATE)]
                 for row in selected()}
    saved = persist(tmp_path, {"trial_verdicts": histories,
                               "verdicts": {tid: cells[-1] for tid, cells in histories.items()}})
    for entry in saved:
        assert "invalid" not in entry and "unmeasured" not in entry and "trial" not in entry
        assert entry["trials"][0]["invalid"] is False
        assert entry["trials"][0]["unmeasured"] is False
    measured = report(saved)
    assert measured["TGC"] == 1.0 and measured["SGC"] == 1.0
    assert measured["coverage"]["invalid_task_trials"] == 6
    assert measured["coverage"]["recorded_unmeasured_task_trials"] == 6
    assert all([cell["status"] for cell in task["trials"]] ==
               ["invalid", "unmeasured", "measured"]
               for task in measured["per_task"].values())


@pytest.mark.parametrize("evidence,status", [
    (None, "unmeasured"),
    ({"metric": TGC_METRIC, "measured": False, "success": True}, "unmeasured"),
    ({"metric": "generic.score", "measured": True, "success": True}, "invalid"),
    ({"metric": TGC_METRIC, "measured": True, "success": 1}, "invalid"),
    ({"metric": TGC_METRIC, "measured": True}, "invalid"),
])
def test_generic_success_never_fills_missing_or_malformed_scorer_facts(tmp_path, evidence, status):
    values = {row["task_id"]: {"score": 1.0, "passed": True, "trial": 1}
              for row in selected()}
    if evidence is not None:
        for value in values.values():
            value["evidence"] = deepcopy(evidence)
    saved = persist(tmp_path, {"per_task": {tid: 1.0 for tid in values}, "verdicts": values})
    assert all(entry.get("evidence") == evidence for entry in saved)
    measured = report(saved, trials=1)
    assert measured["TGC"] is None and measured["SGC"] is None
    assert all(task["trials"][0]["status"] == status
               for task in measured["per_task"].values())


@pytest.mark.parametrize("history", [False, True])
def test_malformed_evidence_is_not_silently_downgraded_to_absence(tmp_path, history):
    value = {"trial": 1, "evidence": ["malformed synthetic evidence"]}
    result = {"per_task": {"synthetic_n_1": 1.0}, "verdicts": {"synthetic_n_1": value}}
    if history:
        result["trial_verdicts"] = {"synthetic_n_1": [value]}
    saved = persist(tmp_path, result)
    cell = saved[0]["trials"][0] if history else saved[0]
    assert cell["evidence"] == value["evidence"]
    with pytest.raises(ValueError, match="invalid saved evidence"):
        report(saved, trials=1)


@pytest.mark.parametrize("flag", ["invalid", "unmeasured"])
@pytest.mark.parametrize("null_score", [False, True])
def test_nonmeasurement_trials_with_unknown_scores_are_written_without_inferred_zero(
    tmp_path, flag, null_score,
):
    value = {"trial": 2, "passed": True, flag: PRIVATE}
    if null_score:
        value["score"] = None
    saved = persist(tmp_path, {"trial_verdicts": {"synthetic_n_1": [value]}})
    assert saved[0]["trial_scores"] == [None]
    assert "evidence" not in saved[0]["trials"][0]
    measured = report(saved)
    assert measured["TGC"] is None and measured["SGC"] is None
    assert measured["per_task"]["synthetic_n_1"]["trials"][1]["status"] == flag


def test_explicit_empty_history_is_preserved_for_reader_refusal(tmp_path):
    row = selected()[0]
    saved = persist(tmp_path, {"verdicts": {row["task_id"]: verdict(row, trial=1)},
                               "trial_verdicts": {row["task_id"]: []}})
    assert saved[0]["trials"] == [] and saved[0]["trial_scores"] == []
    with pytest.raises(ValueError, match="invalid saved trials"):
        report(saved, trials=1)


def test_registry_closes_only_the_saved_writer_blocker():
    registry = json.loads((ROOT / "docs/dataset-blockers.json").read_text())
    appworld = next(row for row in registry["datasets"] if row["dataset"] == "appworld")
    assert "trusted-trial-evidence-writer" not in {b["id"] for b in appworld["blockers"]}
    assert "successful-task-evidence" in {b["id"] for b in appworld["blockers"]}
    assert {"runtime-observations", "official-scorer-identity", "snapshot-owned-cleanup"} <= \
        set(appworld["shared_blockers"])
    assert registry["review"]["production_authorized"] is False
