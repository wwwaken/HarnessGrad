"""Four scorer regressions using only authored inputs and a virtual LCB clock.

Run as a script with --workdir /tmp/metricfix-synthetic to print grades without
asserting them, so the same inputs can demonstrate the before and after behavior.
No released dataset, upstream executor, model, or wall-clock wait is used.
"""
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def _load(relative, monkeypatch):
    # QASpec.build() calls ensure() at import time. Refuse all dataset reads.
    from data.scaffolds.qa import base

    with monkeypatch.context() as patch:
        patch.setattr(base.QASpec, "ensure", lambda self: [])
        spec = importlib.util.spec_from_file_location("metricfix_synthetic", ROOT / relative)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


def _inputs(work):
    work.mkdir(parents=True, exist_ok=True)
    cases = {
        "physics": {"prediction": "7 km.", "gold": {"accepted": ["7 km"]}},
        "sports": {"prediction": "not plausible", "gold": {"answer": "implausible"}},
        "gsm8k": {"prediction": "#### 18 then the total is 20", "gold": {"answer": "18"}},
        "livecodebench": {"n_tests": 103, "simulated_completion_s": 650},
    }
    path = work / "cases.json"
    if not path.exists():
        path.write_text(json.dumps(cases, sort_keys=True) + "\n", encoding="utf-8")
    return json.loads(path.read_text(encoding="utf-8"))


def _qa_score(name, case, monkeypatch):
    module = _load(f"data/datasets/{name}.py", monkeypatch)
    return module, module.score(case["prediction"], case["gold"])


def _lcb_score(work, case, monkeypatch):
    module = _load("data/datasets/livecodebench/verify/check.py", monkeypatch)
    total = case["n_tests"]
    tests = work / "tests.json"
    tests.write_text(json.dumps({"inputs": ["1\n"] * total,
                                 "outputs": ["1\n"] * total}), encoding="utf-8")
    solution = work / "solution.py"
    solution.write_text("print(input())\n", encoding="utf-8")
    joins = []
    state = {"killed": False}

    class VirtualProcess:
        def __init__(self, *, target, args):
            assert target is module._child
            assert args[:2] == (tests.read_text(encoding="utf-8"), solution.read_text())

        def start(self):
            pass

        def join(self, timeout=None):
            if timeout is not None:
                joins.append(timeout)

        def is_alive(self):
            return not state["killed"] and joins[-1] < case["simulated_completion_s"]

        def kill(self):
            state["killed"] = True

    aggregator = ModuleType("pass_k_utils")

    def compute_metrics_from_results(results, k_list):
        # Synthetic stand-in for upstream aggregation, never an upstream execution claim.
        assert results == {"task": [[True] * total]} and k_list == [1]
        return {"pass@1": 1.0}

    aggregator.compute_metrics_from_results = compute_metrics_from_results
    with monkeypatch.context() as patch:
        patch.setattr(module.multiprocessing, "Process", VirtualProcess)
        patch.setattr(module.multiprocessing, "Queue", lambda: SimpleNamespace(
            empty=lambda: False, get=lambda: {"results": [True] * total}))
        patch.setitem(sys.modules, "pass_k_utils", aggregator)
        args = SimpleNamespace(tests=str(tests), solution=str(solution),
                               reward_file=str(work / "reward.txt"),
                               evidence_file=str(work / "evidence.json"))
        assert module._score(args, {str(tests): tests}, {"synthetic": True}) == 0
    evidence = json.loads((work / "evidence.json").read_text())
    return {"reward": evidence["reward"], "join_budget_s": joins[0],
            "killed": state["killed"], "passed": evidence["tests"]["passed"]}


def test_physics_trailing_period_on_prediction(tmp_path, monkeypatch):
    case = _inputs(tmp_path)["physics"]
    module, result = _qa_score("physicsquestions", case, monkeypatch)
    assert result["reward"] == 1.0
    for prediction, gold in [(" 7 km... ", "7 km."), ("7 km", "7 km...")]:
        assert module.exact_str_match(prediction, gold)
    for prediction in ("7 KM.", "7.0 km.", "7km.", "7.2 km", "7 km ."):
        assert not module.exact_str_match(prediction, "7 km")


def test_sports_negation_selects_complement(tmp_path, monkeypatch):
    case = _inputs(tmp_path)["sports"]
    module, result = _qa_score("sportsunderstanding", case, monkeypatch)
    assert result["reward"] == 1.0
    for label, complement in (("plausible", "implausible"), ("implausible", "plausible")):
        for prefix in ("not", "no", "n't", "isn't", "isn’t", "wasn't", "is not"):
            prediction = f"This is {prefix} {label}."
            assert module.score(prediction, {"answer": complement})["reward"] == 1.0
            assert module.score(prediction, {"answer": label})["reward"] == 0.0
        assert module.score(label.upper(), {"answer": label})["reward"] == 1.0
        assert module.score(label, {"answer": complement})["reward"] == 0.0
        for prediction in ("plausible or implausible", "not plausible but implausible",
                           "not implausible, plausible", "plausible but not plausible", ""):
            assert module.score(prediction, {"answer": label})["reward"] == 0.0
    assert not module.substring_choice("implausible", "plausible")
    assert not module.names_both("not plausible")
    assert module.names_both("not plausible but implausible")


def test_gsm8k_first_marker_overrides_later_number(tmp_path, monkeypatch):
    case = _inputs(tmp_path)["gsm8k"]
    module, result = _qa_score("gsm8k", case, monkeypatch)
    assert result["reward"] == 1.0
    assert result["official"]["strict_match"] == "18"
    assert result["official"]["flexible_extract"] == "20"
    for prediction, gold in (("#### 18 then #### 20", "18"),
                             ("#### 3.5 then 20", "3.5"),
                             ("#### -1,250 then 20", "-1250"),
                             ("18 then 20", "20"), ("$18.0", "18")):
        assert module.score(prediction, {"answer": gold})["reward"] == 1.0
    for prediction in ("#### invalid then 18", "#### invalid then #### 18", "####18"):
        assert module.score(prediction, {"answer": "18"})["reward"] == 0.0
    assert module.score("#### 20 then 18", {"answer": "18"})["reward"] == 0.0
    assert module.numeric_equal("0.0000009", "0")
    assert not module.numeric_equal("0.000001", "0")


def test_livecodebench_correct_child_can_finish_after_600_seconds(tmp_path, monkeypatch):
    case = _inputs(tmp_path)["livecodebench"]
    result = _lcb_score(tmp_path, case, monkeypatch)
    assert result == {"reward": 1.0, "join_budget_s": 726, "killed": False, "passed": 103}
    # Retain the upstream timeout/kill path, and budget scaling for smaller payloads.
    for total, finish, reward, budget, killed in ((102, 650, 1.0, 719, False),
                                                (103, 727, 0.0, 726, True),
                                                (1, 13, 0.0, 12, True)):
        got = _lcb_score(tmp_path, {"n_tests": total, "simulated_completion_s": finish}, monkeypatch)
        assert (got["reward"], got["join_budget_s"], got["killed"]) == (reward, budget, killed)
    # Inspect the adapter declaration without importing it or opening its pool.
    tree = ast.parse((ROOT / "data/datasets/livecodebench.py").read_text(encoding="utf-8"))
    verify = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                  and node.name == "_verify")
    timeouts = [ast.literal_eval(value) for node in ast.walk(verify) if isinstance(node, ast.Dict)
                for key, value in zip(node.keys, node.values)
                if isinstance(key, ast.Constant) and key.value == "timeout_s"]
    assert timeouts == [900]


def demonstrate(work):
    cases = _inputs(work)
    with pytest.MonkeyPatch.context() as patch:
        for key, name in (("physics", "physicsquestions"), ("sports", "sportsunderstanding"),
                          ("gsm8k", "gsm8k")):
            module, result = _qa_score(name, cases[key], patch)
            summary = {"case": key, "reward": result["reward"]}
            if key == "sports":
                summary["affirmative_gold_reward"] = module.score(
                    cases[key]["prediction"], {"answer": "plausible"})["reward"]
            if key == "gsm8k":
                summary.update(result["official"])
            print(json.dumps(summary, sort_keys=True))
        print(json.dumps({"case": "livecodebench", **_lcb_score(work, cases["livecodebench"], patch)},
                         sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workdir", type=Path, required=True)
    demonstrate(parser.parse_args().workdir)
