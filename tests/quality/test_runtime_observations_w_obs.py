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
def test_unknown_scores_refuse_at_runner_boundaries(tmp_path, monkeypatch, class_, location):
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
    with pytest.raises(IsolationMismatch, match="unknown: aggregation invalid"):
        runner._evaluate(tmp_path, tasks, {}, trials=trials, cache=cache)
    assert cache == before  # Legacy evidence is neither rewritten nor promoted.


@pytest.mark.parametrize("class_", sorted(CLASSES - {"unknown"}))
def test_uniform_observed_class_aggregates_trials_tasks_progress_and_curve(tmp_path, monkeypatch, class_):
    emitted = iter([result(class_, score) for score in [1.0, 0.0, 0.0, 1.0]])
    monkeypatch.setattr(runner, "run_one", lambda *_a, **_kw: next(emitted))
    cache = {}
    tasks = [{"task_id": tid} for tid in ["a", "b"]]
    measured = runner._evaluate(tmp_path, tasks, {}, trials=2, cache=cache, progress_dir=tmp_path)
    assert measured["per_task"] == {"a": 0.5, "b": 0.5}
    assert measured["scorer_isolation_class"] == class_
    assert measured["per_task_scorer_isolation"] == {"a": class_, "b": class_}
    assert runner._evaluate(tmp_path, tasks, {}, trials=2, cache=cache)["per_task"] == measured["per_task"]
    progress = json.loads((tmp_path / "progress/round-0/a.json").read_text())
    assert progress["score"] == 0.5 and progress["scorer_isolation_class"] == class_
    recorded = point([class_, class_])
    assert recorded["score"] == 0.5 and recorded["scorer_isolation_class"] == class_
    _write_curve(tmp_path / "curve.jsonl", [recorded, recorded])
    assert read_curve(tmp_path) == ([recorded, recorded], [])


@pytest.mark.parametrize("classes", [[None, None], ["unknown", "unknown"], ["unsupported", None]])
def test_unknown_progress_refuses_score_persistence(tmp_path, capsys, classes):
    measured = [result(class_, score) for class_, score in zip(classes, [1.0, 0.0])]
    _write_progress(tmp_path, 0, "a", measured, None)
    assert not (tmp_path / "progress/round-0/a.json").exists()
    assert "unknown: aggregation invalid" in capsys.readouterr().err


@pytest.mark.parametrize("classes", [[None, None], ["unknown", "unknown"], ["unsupported", None]])
def test_legacy_unknown_curve_is_readable_but_cannot_be_aggregated_or_rewritten(tmp_path, classes):
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
    with pytest.raises(IsolationMismatch, match="unknown"):
        point(classes)
    with pytest.raises(IsolationMismatch, match="unknown"):
        _write_curve(path, records)
    assert path.read_text() == raw


def test_no_measurement_preserves_empty_unknown_result(tmp_path):
    assert common_class(iter([])) == "unknown"
    empty = runner._evaluate(tmp_path, [], {})
    assert empty["per_task"] == {} and empty["scorer_isolation_class"] == "unknown"
