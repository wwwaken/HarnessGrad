"""Pin the existing SICA port's math and its recorded historical incumbent.

Upstream `sica/runner.py:118-135` reads the highest mean's ci_lower and accepts >=.
The existing pure-rule tests below pin the port's highest-lower-bound, strict->
comparison, score fallback, and diagnostic continuation observation. Those existing
assertions are preserved; the mathematical differences are documented in method.json.

The main() tests verify that the selected historical round reaches the real trajectory
step, and that an unavailable comparison CI never becomes an invented kept decision.
"""
from __future__ import annotations

import importlib.util
import io
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def _load():
    spec = importlib.util.spec_from_file_location(
        "sica_ci", ROOT / "methods" / "sica_ci" / "run.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SICA = _load()


def _point(round_no: int, score: float | None, ci: list | None = None) -> dict:
    point = {"round": round_no, "score_kind": "training", "score": score,
             "per_task": {"a": score} if score is not None else {}}
    if ci is not None:
        point["score_ci95"] = ci
    return point


# --------------------------------------------------------------- 下界 ---


def test_the_bound_is_the_lower_end_of_the_interval():
    assert SICA._ci_lower(_point(0, 0.7, [0.55, 0.85])) == 0.55


def test_a_point_without_an_interval_falls_back_to_its_score():
    """Zero width, on purpose: it then cannot clear a real bound *by accident*.

    `score > bound` is strict, so a point whose bound is its own score never clears
    itself -- which is what the docstring promises and what this test holds it to.
    """
    bare = _point(0, 0.8)
    assert SICA._ci_lower(bare) == 0.8
    assert SICA._ci_lower(_point(0, None)) == 0.0
    chosen, why = SICA._select_base([bare])
    assert chosen["round"] == 0
    assert "no round clears" in why


# --------------------------------------------------------------- 选择 ---


def test_it_builds_on_a_lower_mean_when_the_higher_one_is_inside_the_noise():
    """The whole point of the rule, in one history.

    Round 0 has by far the highest mean (0.90) but a wide interval, so its lower bound
    is only 0.40. Round 1 is tight (bound 0.50) and round 2 is worse. The rule must
    return round 1: not the highest mean, and not the newest round.
    """
    history = [_point(0, 0.90, [0.40, 1.40]),
               _point(1, 0.55, [0.50, 0.60]),
               _point(2, 0.30, [0.20, 0.40])]
    chosen, why = SICA._select_base(history)
    assert chosen["round"] == 1
    assert "0.550" in why and "0.500" in why

    highest_mean = max(history, key=lambda p: p["score"])["round"]
    newest = max(history, key=lambda p: p["round"])["round"]
    assert chosen["round"] != highest_mean
    assert chosen["round"] != newest


def test_the_newest_clearing_round_wins_among_statistical_equals():
    """`sica/runner.py`'s tie-break: an older iteration is a longer walk away."""
    history = [_point(0, 0.60, [0.50, 0.70]),
               _point(1, 0.62, [0.50, 0.74]),
               _point(2, 0.45, [0.30, 0.60])]
    chosen, _ = SICA._select_base(history)
    assert chosen["round"] == 1, "both 0 and 1 clear the 0.50 bound; the newer one is used"


def test_when_nothing_clears_the_bound_the_bound_holder_is_returned():
    """Two rounds with no interval: each bound equals its own score, so neither clears.

    The rule then keeps the bound holder and says so, rather than picking arbitrarily.
    """
    history = [_point(0, 0.80), _point(1, 0.90)]
    chosen, why = SICA._select_base(history)
    assert chosen["round"] == 1
    assert "no round clears the best lower bound 0.900" in why


def test_an_empty_history_says_so():
    chosen, why = SICA._select_base([])
    assert chosen == {}
    assert why == "no history yet"


# ------------------------------------------------------------- 是否继续 ---


def test_worth_continuing_needs_two_rounds():
    ok, why = SICA._worth_continuing([_point(0, 0.5, [0.4, 0.6])])
    assert ok is True and "too little history" in why


def test_worth_continuing_when_the_incumbent_clears_the_previous_bound():
    history = [_point(0, 0.50, [0.40, 0.60]),
               _point(1, 0.70, [0.60, 0.80])]
    ok, why = SICA._worth_continuing(history)
    assert ok is True
    assert "0.700" in why and "0.400" in why


def test_worth_continuing_stops_when_the_incumbent_is_inside_the_noise():
    """The stop that saves a model call: every round is inside the best one's interval."""
    history = [_point(0, 0.80, [0.50, 1.10]),
               _point(1, 0.45, [0.40, 0.50])]
    ok, why = SICA._worth_continuing(history)
    assert ok is False
    assert "0.450" in why and "0.500" in why
    assert "noise" in why


def test_the_stop_compares_against_the_best_other_round_not_the_last():
    """Round 1's own interval must not be what stops round 2 -- it is not the comparison."""
    history = [_point(0, 0.30, [0.20, 0.40]),
               _point(1, 0.90, [0.80, 1.00])]
    ok, _ = SICA._worth_continuing(history)
    assert ok is True, "0.90 clears the best *other* bound (0.20)"
    assert SICA._worth_continuing(history)[0] is True


def test_a_missing_interval_is_not_read_as_a_strong_bound():
    """A bare point contributes its own score as a zero-width interval.

    That makes `0.6` the bound when the other half has none, and the incumbent (0.7)
    clears it -- so the missing field weakens the bound instead of inventing one.
    """
    history = [_point(0, 0.60), _point(1, 0.70)]
    assert SICA._ci_lower(history[0]) == 0.60
    assert SICA._worth_continuing(history)[0] is True


# ------------------------------------------------------ 选择写入 trajectory ---


def _invoke_main(tmp_path, monkeypatch, history, reply):
    """Exercise real edit/report serialization with a local, deterministic proposer."""
    base = tmp_path / "base"
    history_dir = base / "_harnessgrad" / "history"
    history_dir.mkdir(parents=True)
    (base / "harness.json").write_text(json.dumps(
        {"name": "probe", "version": "1.0", "entrypoint": "agent.py"}))
    (base / "agent.py").write_text("print('hello')\n")
    for point in history:
        (history_dir / f"round-{point['round']}.json").write_text(json.dumps(point))
    trajectory_out = tmp_path / "trajectory.json"
    request = {
        "platform_api_version": "0.1.0", "mode": "A",
        "base_harness": str(base), "workspace": str(tmp_path / "workspace"),
        "round_index": max((p["round"] for p in history), default=-1) + 1,
        "trajectory_out": str(trajectory_out),
    }
    monkeypatch.setattr(SICA.editor, "ask", lambda *args, **kwargs: reply)
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(request)))
    output = io.StringIO()
    monkeypatch.setattr(sys, "stdout", output)
    assert SICA.main() == 0
    trajectory = json.loads(trajectory_out.read_text())
    assert len(trajectory["steps"]) == 1
    return trajectory["steps"][0], json.loads(output.getvalue())


@pytest.mark.parametrize("reply,changed", [
    ({"files": [{"path": "agent.py", "content": "print('hello world')\n"}],
      "hypothesis": "change the greeting"}, True),
    ({"no_change": "no supported edit"}, False),
    ({"files": []}, False),
], ids=["edited", "no-change", "unusable"])
def test_main_reports_the_selected_historical_round_not_the_latest(
        tmp_path, monkeypatch, reply, changed):
    """sica/runner.py:124-135 returns a historical iteration; the step must name it."""
    history = [_point(2, 0.90, [0.40, 1.40]),
               _point(5, 0.55, [0.50, 0.60]),
               _point(9, 0.30, [0.20, 0.40])]
    step, response = _invoke_main(tmp_path, monkeypatch, history, reply)
    assert step["method_reported"]["sica_rule"]["selected_base_round"] == 5
    assert step.get("incumbent_round") == 5
    assert response["changed"] is changed
    assert response["stop"] is False


@pytest.mark.parametrize("ci", [
    None, [None, None], [float("nan"), float("nan")],
    [0.4, float("inf")], [0.8, 0.2],
], ids=["missing", "unavailable", "nan", "infinite", "reversed"])
def test_main_omits_incumbent_round_when_the_ci_is_unavailable(
        tmp_path, monkeypatch, ci):
    """A score fallback is not an observed confidence interval or a kept decision."""
    step, _ = _invoke_main(
        tmp_path, monkeypatch, [_point(4, 0.6, ci)], {"no_change": "no edit"})
    assert "incumbent_round" not in step
    reason = step["method_reported"]["sica_rule"]["incumbent_reason"]
    assert "CI unavailable" in reason
    assert "no kept round specified" in reason


def test_main_omits_incumbent_round_without_history(tmp_path, monkeypatch):
    step, _ = _invoke_main(tmp_path, monkeypatch, [], {"no_change": "no edit"})
    assert "incumbent_round" not in step
    rule = step["method_reported"]["sica_rule"]
    assert rule["selected_base_round"] is None
    assert "no history" in rule["incumbent_reason"]
    assert "no kept round specified" in rule["incumbent_reason"]


def test_main_records_round_zero_without_treating_it_as_missing(tmp_path, monkeypatch):
    step, _ = _invoke_main(
        tmp_path, monkeypatch,
        [_point(0, 0.8, [0.7, 0.9]), _point(3, 0.2, [0.1, 0.3])],
        {"no_change": "no edit"})
    assert step.get("incumbent_round") == 0


def test_main_does_not_publish_a_bound_derived_from_a_missing_ci(tmp_path, monkeypatch):
    # The existing selector can let a bare score dominate an available lower bound.
    # Preserve that math, but do not advertise the fallback as a CI-based kept choice.
    step, _ = _invoke_main(
        tmp_path, monkeypatch,
        [_point(0, 0.8), _point(3, 0.6, [0.5, 0.7])],
        {"no_change": "no edit"})
    assert "incumbent_round" not in step
    assert "CI unavailable" in step["method_reported"]["sica_rule"]["incumbent_reason"]
