"""Synthetic ALFWorld protocol controls; no dataset, TextWorld or model is run."""
from __future__ import annotations

import ast
import hashlib
import json
import os
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "data/datasets/alfworld"


def _module(name, path):
    module = ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_text(), str(path), "exec"), module.__dict__)
    return module


@pytest.fixture
def protocol(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT))
    gym = _module("alfworld_fidelity_gym", ASSETS / "lib/gym_env.py")
    monkeypatch.setitem(sys.modules, "gym_env", gym)
    check = _module("alfworld_fidelity_check", ASSETS / "verify/check.py")
    cli = _module("alfworld_fidelity_cli", ASSETS / "cli/alf")
    return gym, check, cli


def test_upstream_budget_defaults_agree(protocol):
    gym, check, cli = protocol
    assert gym.STEP_BUDGET == 50
    assert gym.build.__defaults__ == gym.replay.__defaults__ == (50,)
    assert check.parse_args([]).budget == cli._parse_global([])[0].budget == 50
    tree = ast.parse((ROOT / "data/datasets/alfworld.py").read_text())
    declaration = next(n for n in tree.body if isinstance(n, ast.Assign)
                       and any(isinstance(t, ast.Name) and t.id == "STEP_BUDGET"
                               for t in n.targets))
    assert ast.unparse(declaration.value) == "_GYM_ENV.STEP_BUDGET"


@pytest.mark.parametrize("winning_step", [31, 50, 51])
def test_replay_can_win_after_thirty_but_stops_at_fifty(protocol, monkeypatch,
                                                       winning_step):
    gym, _, _ = protocol
    calls, closed = [], []
    env = SimpleNamespace(close=lambda: closed.append(True))

    def build(game, budget):
        assert game == "synthetic-game" and budget == 50
        return env

    def step(actual_env, action):
        assert actual_env is env
        calls.append(action)
        return {"won": len(calls) == winning_step,
                "done": len(calls) >= min(winning_step, 50),
                "observation": "synthetic", "admissible": []}

    monkeypatch.setattr(gym, "build", build)
    monkeypatch.setattr(gym, "reset", lambda _: {
        "won": False, "observation": "synthetic", "admissible": []})
    monkeypatch.setattr(gym, "step", step)
    state = gym.replay("synthetic-game", ["look"] * 60)
    assert len(state["records"]) == min(winning_step, 50)
    assert state["won"] is (winning_step <= 50)
    assert closed == [True]


@pytest.mark.parametrize("logged,replayed,won,done", [
    (0, 0, False, False),
    (49, 49, False, False),
    (50, 50, False, True),  # TextWorld can signal done when the cap is reached.
    (51, 50, False, True),
    (50, 50, False, False),
    (50, 50, True, True),   # Winning on the last step is not exhaustion.
    (51, 50, True, True),
    (51, 3, False, True),   # Early non-winning termination is not budget exhaustion.
    (50, 3, True, True),
])
def test_budget_evidence_distinguishes_cap_from_win(protocol, monkeypatch, tmp_path,
                                                   logged, replayed, won, done):
    gym, check, _ = protocol
    game, log = tmp_path / "game", tmp_path / "actions.jsonl"
    game.write_text("synthetic game; never loaded")
    log.write_text("".join(json.dumps({"kind": "action", "action": "look"}) + "\n"
                           for _ in range(logged)))
    records = [{"action": "look", "observation": "synthetic",
                "won": won and i == replayed - 1,
                "done": done and i == replayed - 1}
               for i in range(replayed)]

    def replay(actual_game, actions, budget):
        assert actual_game == str(game) and len(actions) == logged and budget == 50
        return {"records": records, "won": won}

    monkeypatch.setattr(gym, "replay", replay)
    args = check.parse_args(["--game", str(game), "--log", str(log), "--budget", "50",
                             "--reward-file", str(tmp_path / "reward"),
                             "--evidence-file", str(tmp_path / "evidence")])
    assert check._score(args, {str(game): game}, {"synthetic": True}) == (0 if won else 1)
    evidence = json.loads(args.evidence_file.read_text())
    reached = replayed == 50
    assert evidence["budget_exhausted"] is (reached and not won)
    assert evidence["budget_reached"] is reached
    assert evidence["episode_done"] is done
    assert evidence["actions_not_replayed"] == logged - replayed
    assert evidence["reward"] == evidence["official_game_points"] == int(won)
    assert args.reward_file.read_text() == f"{int(won)}\n"
    if reached and not won:
        assert "50-step budget" in evidence["why"]


def test_cli_allows_fiftieth_action_and_refuses_fifty_first(protocol, monkeypatch,
                                                          tmp_path):
    gym, _, cli = protocol
    (tmp_path / gym.GAME_FILENAME).write_text("synthetic game; never loaded")
    log = tmp_path / gym.LOG_FILENAME
    log.write_text((json.dumps({"kind": "action", "action": "look"}) + "\n") * 49)
    replay_calls = []

    def replay(game, actions, budget):
        replay_calls.append((len(actions), budget))
        return {"won": False, "records": [
            {"observation": "synthetic", "admissible": [], "done": i == 49}
            for i in range(len(actions))]}

    monkeypatch.setattr(gym, "replay", replay)
    assert cli.main(["--workdir", str(tmp_path), "do", "look"]) == 0
    assert len(gym.action_log_records(log)) == 50
    assert cli.main(["--workdir", str(tmp_path), "do", "look"]) == 2
    assert replay_calls == [(50, 50)]
    assert len(gym.action_log_records(log)) == 50


def _declared_split(ids):
    """Execute the actual split declarations with synthetic records, without adapter I/O."""
    tree = ast.parse((ROOT / "data/datasets/alfworld.py").read_text())
    nodes = [n for n in tree.body if
             (isinstance(n, ast.FunctionDef) and n.name == "_is_eval") or
             (isinstance(n, ast.Assign) and any(
                 isinstance(t, ast.Name) and t.id == "_split_mode" for t in n.targets)) or
             (isinstance(n, ast.If) and ast.unparse(n.test) == "_split_mode == 'none'")]
    assert len(nodes) == 3
    # `_STUDY` is empty here on purpose: this test pins the **hash** rule, which is the
    # path a run without a study file takes. The study branch has its own test
    # (`test_alfworld_study_pool.py`), where the ids are known.
    scope = {"hashlib": hashlib, "os": os, "_STUDY": [],
             "_RECORDS": [{"task_id": t} for t in ids]}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "alfworld-split", "exec"), scope)
    return scope["SPLIT"], scope["_is_eval"]


def test_declared_split_groups_trials_and_is_order_independent(monkeypatch):
    monkeypatch.delenv("HG_ALFWORLD_SPLIT", raising=False)
    ids = [f"synthetic-game-{game}__trial_{trial}"
           for game in range(80) for trial in range(3)] + ["game-without-trials"]
    split, is_eval = _declared_split(ids)
    expected_eval = {t for t in ids if
                     hashlib.sha256(t.split("__trial_")[0].encode()).digest()[0] % 3 == 0}
    assert set(split["eval"]) == expected_eval
    assert set(split["train"]) == set(ids) - expected_eval
    assert set(split["train"]).isdisjoint(split["eval"])
    for game in range(80):
        assert len({is_eval(f"synthetic-game-{game}__trial_{trial}")
                    for trial in range(3)}) == 1
    reversed_split, _ = _declared_split(list(reversed(ids)))
    extended_split, _ = _declared_split(ids + ["new-game__trial_0"])
    repeated_split, _ = _declared_split(ids)
    assert repeated_split == split
    for side in ("train", "eval"):
        assert set(reversed_split[side]) == set(split[side])
        assert set(extended_split[side]) & set(ids) == set(split[side])


def test_no_declared_split_override_is_preserved(monkeypatch):
    monkeypatch.setenv("HG_ALFWORLD_SPLIT", "none")
    assert _declared_split(["synthetic-game__trial_0"])[0] is None
