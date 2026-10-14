"""Synthetic topology aggregation controls; no dataset or backend execution."""
from __future__ import annotations

import copy
import json

import pytest

from data.scaffolds.scorer_isolation import CLASSES
from eval.observe.tracing import _write_progress
from eval.run import runner
from eval.verification.isolation import (
    IsolationMismatch, common_class, observed_class, require_comparable,
)
from harnessgrad.records import _curve_point, _write_curve
from harnessgrad.store.schema import read_curve


def result(class_, score):
    verdict = {"score": score, "passed": bool(score)}
    if class_ is not None:
        verdict["scorer_isolation_class"] = class_
    return dict(verdict=verdict, trace="", exit_code=0, stderr="")


def point(classes):
    return _curve_point(
        run_id="synthetic-w-obs", round_index=0, identity={}, sampling={},
        scores=[1.0, 0.0], task_ids=["a", "b"], cost={}, cumulative={},
        per_task_scorer_isolation=dict(zip(["a", "b"], classes)))


@pytest.mark.parametrize("classes", [
    ["pristine-offline", "snapshot-service"], ["actor-workdir", "unknown"],
])
def test_mixed_class_aggregate_refuses(classes):
    with pytest.raises(IsolationMismatch, match="class mismatch"):
        common_class(iter(classes))
    with pytest.raises(IsolationMismatch, match="class mismatch"):
        point(classes)


@pytest.mark.parametrize("class_", [None, "unknown", "unsupported", 123])
@pytest.mark.parametrize("location", ["trials", "tasks", "cached", "cached_trials"])
def test_unknown_scores_are_recorded_as_noncomparable_at_runner_boundaries(tmp_path, monkeypatch, class_, location):
    values = [result(class_, 1.0), result(class_, 0.0)]
    emitted = iter(values)
    monkeypatch.setattr(runner, "run_one", lambda *_a, **_kw: next(emitted))
    tasks = [{"task_id": "a"}]
    trials = 2 if location in {"trials", "cached_trials"} else 1
    cache = {}
    if location == "tasks":
        tasks.append({"task_id": "b"})
    if location.startswith("cached"):
        monkeypatch.setattr(runner, "run_one", lambda *_a, **_kw: pytest.fail("cache miss"))
        cache[f":a:{trials}"] = dict(score=0.5, trace="", verdict=values[-1]["verdict"])
        if location == "cached_trials":
            cache[f":a:{trials}"]["trial_verdicts"] = [v["verdict"] for v in values]
    before = copy.deepcopy(cache)
    # Raising here asserted the write-path bug. Keep the raw facts, but never
    # promote absent/malformed observations into comparable measurements.
    recorded = runner._evaluate(tmp_path, tasks, {}, trials=trials, cache=cache)
    assert recorded["scorer_isolation_class"] == "unknown"
    assert recorded["scorer_isolation_comparable"] is False
    assert recorded["per_task_scorer_isolation"] == {t["task_id"]: "unknown" for t in tasks}
    expected = {"a": 0.5} if trials == 2 or location == "cached" else {"a": 1.0}
    if location == "tasks":
        expected["b"] = 0.0
    assert recorded["per_task"] == expected
    with pytest.raises(IsolationMismatch, match="unknown"):
        require_comparable(recorded, recorded)
    # A fresh run can cache raw facts; existing legacy cache evidence stays intact.
    if location.startswith("cached"):
        assert cache == before
    assert all(observed_class(entry.get("verdict")) == "unknown" for entry in cache.values())


@pytest.mark.parametrize("class_", sorted(CLASSES - {"unknown"}))
def test_uniform_observed_class_aggregates_trials_tasks_progress_and_curve(tmp_path, monkeypatch, class_):
    emitted = iter([result(class_, score) for score in [1.0, 0.0, 0.0, 1.0]])
    monkeypatch.setattr(runner, "run_one", lambda *_a, **_kw: next(emitted))
    cache = {}
    tasks = [{"task_id": tid} for tid in ["a", "b"]]
    measured = runner._evaluate(tmp_path, tasks, {}, trials=2, cache=cache, progress_dir=tmp_path)
    assert measured["per_task"] == {"a": 0.5, "b": 0.5}
    assert measured["scorer_isolation_class"] == class_
    assert measured["scorer_isolation_comparable"] is True
    assert measured["per_task_scorer_isolation"] == {"a": class_, "b": class_}
    assert runner._evaluate(tmp_path, tasks, {}, trials=2, cache=cache)["per_task"] == measured["per_task"]
    progress = json.loads((tmp_path / "progress/round-0/a.json").read_text())
    assert progress["score"] == 0.5 and progress["scorer_isolation_class"] == class_
    assert progress["scorer_isolation_comparable"] is True
    recorded = point([class_, class_])
    assert recorded["score"] == 0.5 and recorded["scorer_isolation_class"] == class_
    assert recorded["scorer_isolation_comparable"] is True
    assert require_comparable(measured, recorded) == class_
    _write_curve(tmp_path / "curve.jsonl", [recorded, recorded])
    assert read_curve(tmp_path) == ([recorded, recorded], [])


@pytest.mark.parametrize("classes", [[None, None], ["unknown", "unknown"], ["unsupported", None]])
def test_unknown_progress_preserves_complete_noncomparable_evidence(tmp_path, capsys, classes):
    measured = [result(class_, score) for class_, score in zip(classes, [1.0, 0.0])]
    for index, trial in enumerate(measured):
        trial["trace"] = json.dumps({"synthetic_trial": index}) + "\n"
    _write_progress(tmp_path, 0, "a", measured, None)
    # Missing files/warnings asserted exactly the bug: safety requires a complete
    # explicitly noncomparable record, not discarded diagnostic evidence.
    dest = tmp_path / "progress/round-0"
    recorded = json.loads((dest / "a.json").read_text())
    assert recorded["scorer_isolation_class"] == "unknown"
    assert recorded["scorer_isolation_comparable"] is False
    assert recorded["score"] == 0.5 and recorded["trial_scores"] == [1.0, 0.0]
    assert recorded["trial_scorer_isolation"] == ["unknown", "unknown"]
    assert recorded["n_trials"] == 2 and recorded["complete"] is True
    for index, trial in enumerate(measured, start=1):
        assert (dest / f"traces/a.trial{index}.jsonl").read_text() == trial["trace"]
    assert capsys.readouterr().err == ""
    with pytest.raises(IsolationMismatch, match="unknown"):
        require_comparable(recorded, recorded)


@pytest.mark.parametrize("classes", [[None, None], ["unknown", "unknown"], ["unsupported", None]])
def test_legacy_unknown_curve_stays_noncomparable_when_aggregated_or_rewritten(tmp_path, classes):
    legacy = [dict(score=score, **({"scorer_isolation_class": class_} if class_ is not None else {}))
              for class_, score in zip(classes, [1.0, 0.0])]
    path = tmp_path / "curve.jsonl"
    raw = "".join(json.dumps(row) + "\n" for row in legacy)
    path.write_text(raw)
    records, problems = read_curve(tmp_path)
    assert records == legacy and problems == []
    assert [observed_class(row) for row in records] == ["unknown", "unknown"]
    with pytest.raises(IsolationMismatch, match="unknown"):
        require_comparable(*records)
    # Read-only access must still preserve legacy bytes and never invent observations.
    assert path.read_text() == raw
    # Curve construction/rewrite refusal also asserted the write-path bug. Retain
    # the score with an explicit noncomparability flag; comparison must still refuse.
    recorded = point(classes)
    assert recorded["score"] == 0.5 and recorded["scorer_isolation_class"] == "unknown"
    assert recorded["scorer_isolation_comparable"] is False
    with pytest.raises(IsolationMismatch, match="unknown"):
        require_comparable(recorded, recorded)
    _write_curve(path, records)
    saved, problems = read_curve(tmp_path)
    assert problems == []
    assert saved == [{**row, "scorer_isolation_class": "unknown",
                      "scorer_isolation_comparable": False} for row in legacy]
    assert records == legacy  # Explicit writing never mutates the source evidence.
    with pytest.raises(IsolationMismatch, match="unknown"):
        require_comparable(*saved)


def test_no_measurement_preserves_empty_unknown_result(tmp_path):
    assert common_class(iter([])) == "unknown"
    empty = runner._evaluate(tmp_path, [], {})
    assert empty["per_task"] == {} and empty["scorer_isolation_class"] == "unknown"
    assert empty["scorer_isolation_comparable"] is False


@pytest.mark.parametrize("classes", [
    ["pristine-offline", "snapshot-service"], ["actor-workdir", "unknown"],
])
def test_mixed_progress_and_curve_history_still_refuse(tmp_path, capsys, classes):
    _write_progress(tmp_path, 0, "a", [result(c, 1.0) for c in classes], None)
    assert not (tmp_path / "progress/round-0/a.json").exists()
    assert "class mismatch" in capsys.readouterr().err
    path = tmp_path / "curve.jsonl"
    path.write_text("preserved record\n")
    with pytest.raises(IsolationMismatch, match="class mismatch"):
        _write_curve(path, [dict(scorer_isolation_class=c) for c in classes])
    assert path.read_text() == "preserved record\n"


def test_curve_writer_cannot_promote_unknown_via_claimed_comparability(tmp_path):
    path = tmp_path / "curve.jsonl"
    forged = {"score": 0.5, "scorer_isolation_comparable": True}
    _write_curve(path, [forged])
    saved, problems = read_curve(tmp_path)
    assert problems == [] and saved == [{**forged, "scorer_isolation_class": "unknown",
                                        "scorer_isolation_comparable": False}]
    assert forged == {"score": 0.5, "scorer_isolation_comparable": True}
    with pytest.raises(IsolationMismatch, match="unknown"):
        require_comparable(forged, saved[0])
