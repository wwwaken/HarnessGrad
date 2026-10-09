"""Offline fidelity checks for RRSI's pool selection and calibration rules."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "methods"))

from rrsi.fidelity import (  # noqa: E402
    Candidate,
    SelectionConfig,
    calibrate_delta,
    role_prompt,
    select_candidates,
)


def test_multiple_candidates_selects_highest_admissible_score_only():
    result = select_candidates(
        [
            Candidate("A", score=0.96, cost=300, gate_failure="critic_reject"),
            Candidate("B", score=0.91, cost=130),
            Candidate("C", score=0.87, cost=101),
        ],
        incumbent_id="incumbent", incumbent_score=0.80, incumbent_cost=100,
        s_star=0.90, delta=0.02, config=SelectionConfig(),
    )
    assert result.parent_id == "B"
    assert result.winner_id == "B"
    assert result.accepted_ids == ("B",)
    assert result.decisions[0].admissible is False
    assert "gate failure" in result.decisions[0].reason
    assert result.decisions[2].stage == "floor"


def test_highest_score_can_fail_cost_rule_and_all_rejected_keeps_incumbent():
    # A clears the score floor and has the highest score, but the above-band
    # cost budget is 0.10 + 40*0.20 = 8.1, below its 9x relative cost increase.
    # B is below the floor. The no-admissible branch must retain the incumbent.
    result = select_candidates(
        [Candidate("A", score=0.95, cost=1000),
         Candidate("B", score=0.70, cost=100)],
        incumbent_id="incumbent", incumbent_score=0.75, incumbent_cost=100,
        s_star=0.90, delta=0.05,
    )
    assert result.decisions[0].admissible is False
    assert result.decisions[0].stage == "cost"
    assert result.decisions[1].stage == "floor"
    assert result.parent_id == "incumbent"
    assert result.incumbent_retained is True
    assert result.winner_id is None
    assert result.accepted_ids == ()


def test_calibration_uses_repeated_base_or_single_measurement_trial_spread():
    repeated = calibrate_delta([0.4, 0.6, 0.5], z=2)
    assert repeated.source == "repeated_base_evaluations"
    assert repeated.delta == pytest.approx(2 * math.sqrt(0.02))

    platform = calibrate_delta(score_std=0.094, n_trials=3, z=2)
    assert platform.source == "platform_trial_spread"
    assert platform.delta == pytest.approx(2 * math.sqrt(2) * 0.094)

    with pytest.raises(ValueError, match="calibration needs"):
        calibrate_delta(score_std=0.0, n_trials=1)


def test_role_prompts_are_distinct_and_never_admit_heldout_context():
    prompts = {role: role_prompt(role, "evolve score report")
               for role in ("digester", "analyst", "proposer", "critic")}
    assert len(set(prompts.values())) == 4
    assert all("held-out evidence is inaccessible" in p for p in prompts.values())
    assert "read-only" in prompts["digester"]
    assert "batch analyst" in prompts["analyst"]
    assert "proposer" in prompts["proposer"]
    assert "pre-evaluation critic" in prompts["critic"]
    assert all("evolve score report" in p for p in prompts.values())
