"""Two scores produced by different known topologies never share one aggregate;
a scoreless point never blocks a record from being written.
"""
from __future__ import annotations

import copy
import json

import pytest

from eval.run import runner
from eval.verification.isolation import IsolationMismatch, require_comparable
from harnessgrad.records import _curve_point, _write_curve


@pytest.mark.parametrize("position", [0, 1, 2])
@pytest.mark.parametrize("class_", ["unknown", "snapshot-service"])
@pytest.mark.parametrize("coverage", [
    dict(score=None), dict(score=0.0, measured_by_platform=False), dict(score=0.0, n_scored=0),
])
def test_scoreless_point_does_not_participate_in_curve_axis(tmp_path, position, class_, coverage):
    scored = dict(score=0.0, scorer_isolation_class="in-process")
    scoreless = dict(scorer_isolation_class=class_, **coverage)
    curve = [scored, scored.copy()]
    curve.insert(position, scoreless)
    before = copy.deepcopy(curve)
    path = tmp_path / "curve.jsonl"
    _write_curve(path, curve)
    saved = [json.loads(line) for line in path.read_text().splitlines()]
    assert len(saved) == 3 and saved[position]["score"] == coverage["score"]
    assert saved[position]["scorer_isolation_class"] == class_
    assert saved[position]["scorer_isolation_comparable"] is (class_ != "unknown")
    assert [p["score"] for index, p in enumerate(saved) if index != position] == [0.0, 0.0]
    assert curve == before


@pytest.mark.parametrize("unknown", [{}, {"scorer_isolation_class": "unknown"}])
def test_explicit_null_score_is_sufficient_without_measurement_flag(tmp_path, unknown):
    path = tmp_path / "curve.jsonl"
    _write_curve(path, [dict(score=1.0, scorer_isolation_class="in-process"),
                        dict(score=None, **unknown)])
    saved = [json.loads(line) for line in path.read_text().splitlines()]
    assert saved[1]["score"] is None
    assert saved[1]["scorer_isolation_class"] == "unknown"
    assert saved[1]["scorer_isolation_comparable"] is False
    with pytest.raises(IsolationMismatch, match="unknown"):
        require_comparable(saved[1], saved[1])


@pytest.mark.parametrize("class_", ["snapshot-service", "unknown"])
@pytest.mark.parametrize("score", [0.0, 1.0])
def test_scored_mismatch_refuses_before_opening_destination(tmp_path, class_, score):
    path = tmp_path / "curve.jsonl"
    path.write_text("previous record\n")
    curve = [dict(score=1.0, scorer_isolation_class="in-process"),
             dict(score=None, scorer_isolation_class="unknown"),
             dict(score=score, measured_by_platform=True, n_scored=1, scorer_isolation_class=class_)]
    with pytest.raises(IsolationMismatch) as exc:
        _write_curve(path, curve)
    assert str(exc.value) == f"scorer isolation class mismatch: in-process, {class_}"
    assert path.read_text() == "previous record\n"


def test_all_scoreless_curve_is_preserved(tmp_path):
    path = tmp_path / "curve.jsonl"
    curve = [dict(score=None, scorer_isolation_class=c)
             for c in ["in-process", "unknown", "snapshot-service"]]
    _write_curve(path, curve)
    saved = [json.loads(line) for line in path.read_text().splitlines()]
    assert [p["score"] for p in saved] == [None, None, None]
    assert [p["scorer_isolation_class"] for p in saved] == [
        "in-process", "unknown", "snapshot-service"]


@pytest.mark.parametrize("failure", ["invalid", "unmeasured"])
def test_runner_and_point_aggregate_only_scored_tasks(tmp_path, monkeypatch, failure):
    def run_one(_repo, task, **_kwargs):
        if task["task_id"] == "good":
            return dict(verdict=dict(score=0.0, scorer_isolation_class="in-process"),
                        trace="", stderr="", exit_code=0)
        if failure == "invalid":
            return dict(invalid=dict(stage="test", detail="synthetic nonmeasurement"))
        return dict(verdict=dict(score=None, unmeasured="synthetic nonmeasurement"),
                    trace="", stderr="", exit_code=0)

    monkeypatch.setattr(runner, "run_one", run_one)
    tasks = [dict(task_id=tid) for tid in ["good", "bad"]]
    cache = {}
    measured = runner._evaluate(tmp_path, tasks, {}, cache=cache, progress_dir=tmp_path)
    assert measured["per_task"] == {"good": 0.0}
    assert measured["per_task_scorer_isolation"] == {"good": "in-process"}
    assert measured["scorer_isolation_class"] == "in-process"
    assert "bad" in measured["invalid"]
    progress = tmp_path / "progress/round-0"
    assert json.loads((progress / "good.json").read_text())["scorer_isolation_class"] == "in-process"
    invalid = json.loads((progress / "bad.json").read_text())
    assert invalid["invalid"] and "score" not in invalid
    assert set(cache) == {":good:1"}
    cached = runner._evaluate(tmp_path, [tasks[0]], {}, cache=cache)
    assert cached["per_task_scorer_isolation"] == {"good": "in-process"}
    point = _curve_point(run_id="synthetic-isolationmix", round_index=0,
                         identity={}, sampling={}, cost={}, cumulative={},
                         scores=list(measured["per_task"].values()),
                         task_ids=list(measured["per_task"]),
                         per_task_scorer_isolation=measured["per_task_scorer_isolation"])
    assert point["score"] == 0.0 and point["scorer_isolation_class"] == "in-process"
    empty = _curve_point(run_id="synthetic-isolationmix", round_index=1,
                         identity={}, sampling={}, cost={}, cumulative={},
                         scores=[], task_ids=[],
                         per_task_scorer_isolation={"bad": "snapshot-service"})
    assert empty["n_scored"] == 0 and empty["per_task"] == {}
    assert empty["scorer_isolation_class"] == "unknown"
    _write_curve(tmp_path / "curve.jsonl", [point, empty])


def test_direct_property_control(tmp_path):
    path = tmp_path / "curve.jsonl"
    known = dict(score=1.0, scorer_isolation_class="in-process")
    other = dict(score=0.0, scorer_isolation_class="snapshot-service")
    with pytest.raises(IsolationMismatch) as exc:
        _write_curve(path, [known, other])
    assert str(exc.value) == "scorer isolation class mismatch: in-process, snapshot-service"
    assert not path.exists()
    print(f"REFUSED: {exc.value}")
    _write_curve(path, [known, dict(score=0.0, measured_by_platform=False, n_scored=0,
                                  scorer_isolation_class="unknown"), known])
    saved = [json.loads(line) for line in path.read_text().splitlines()]
    assert [p["scorer_isolation_class"] for p in saved] == ["in-process", "unknown", "in-process"]
    assert saved[1]["measured_by_platform"] is False and saved[1]["n_scored"] == 0
    assert [p["score"] for p in saved] == [1.0, 0.0, 1.0]
    print("WROTE: " + json.dumps(saved, sort_keys=True))
