"""Offline input-binding controls; adapter scorers are replaced, never executed.

The two records come from local released tables, not invented benchmark identities.
Only the shared check and native dispatch are exercised. Stub rewards are unit-test
sentinels and are not benchmark measurements.
"""
from __future__ import annotations

import builtins
import copy
import hashlib
import importlib
import json
import socket
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from data.scaffolds.qa.verify import check
from eval.verification import verifier

DATASETS = (
    "bfcl_v3", "chessbench_puzzles", "fever", "gsm8k", "hotpotqa", "musique",
    "physicsquestions", "reasoning_gym", "sportsunderstanding", "strategyqa",
    "triviaqa", "twowikimultihopqa",
)


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError("w-tbi controls must remain offline")
    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(socket.socket, "connect_ex", deny)
    monkeypatch.setattr(socket, "create_connection", deny)
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "")


def gold_bytes(spec):
    return next(e["content"].encode("utf-8") for e in spec["inputs"]
                if e.get("path") == "gold.json")


@pytest.fixture(scope="module", params=DATASETS)
def case(request):
    module = importlib.import_module(f"data.datasets.{request.param}")
    records = module._ensure() if request.param == "bfcl_v3" else module._SPEC.ensure()
    assert records, (request.param, module._SPEC.load_error)
    build = getattr(module, "verify_for", module._SPEC.verifier)
    first = records[0]
    spec = build(first)
    second = next(r for r in records[1:] if r["gold"] != first["gold"])
    other = build(second)
    return SimpleNamespace(name=request.param, record=first, other_record=second,
                           spec=spec, other=other)


def invoke(case, spec, payload, tmp_path, monkeypatch, *, mutate=False):
    """Invoke the actual check with a spy in place of every dataset scoring call."""
    calls = []
    original_import = builtins.__import__

    def score(prediction, gold, **options):
        calls.append(copy.deepcopy(gold))
        return {"reward": 0.25, "why": "w-tbi unit-test sentinel; no dataset scorer"}

    def spy_import(name, *args, **kwargs):
        if name == f"data.datasets.{case.name}":
            if mutate:
                (tmp_path / "gold.json").write_bytes(gold_bytes(case.other))
            return SimpleNamespace(score=score)
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", spy_import)
    monkeypatch.chdir(tmp_path)
    (tmp_path / "gold.json").write_bytes(payload)
    code = check.main(spec["argv"][2:])
    evidence = json.loads((tmp_path / "verifier/evidence.json").read_text())
    return code, evidence, calls


def test_generated_contract_pins_task_and_exact_serialized_input(case):
    expected = {"task_id": case.record["task_id"], "path": "gold.json",
                "sha256": hashlib.sha256(gold_bytes(case.spec)).hexdigest()}
    print(json.dumps({"dataset": case.name, "selected": expected,
                      "foreign_task_id": case.other_record["task_id"],
                      "foreign_sha256": hashlib.sha256(gold_bytes(case.other)).hexdigest()}))
    assert case.spec.get("scorer_input") == expected
    argv = case.spec["argv"]
    assert argv[argv.index("--task-id") + 1] == expected["task_id"]
    assert argv[argv.index("--gold-sha256") + 1] == expected["sha256"]


def test_check_records_identity_of_the_buffer_it_passes_to_scorer(case, tmp_path, monkeypatch):
    code, evidence, calls = invoke(case, case.spec, gold_bytes(case.spec),
                                   tmp_path, monkeypatch, mutate=True)
    assert code == 1  # unchanged unit-test sentinel, not a benchmark score
    assert calls == [case.record["gold"]]
    assert evidence.get("scorer_input") == {
        **case.spec["scorer_input"], "expected_sha256": case.spec["scorer_input"]["sha256"],
        "verified": True,
    }
    assert (tmp_path / "gold.json").read_bytes() == gold_bytes(case.other)


def test_different_tasks_gold_is_refused_before_any_scorer_call(case, tmp_path, monkeypatch):
    code, evidence, calls = invoke(case, case.spec, gold_bytes(case.other), tmp_path, monkeypatch)
    print(json.dumps({"dataset": case.name, "case": "foreign-gold", "exit": code,
                      "measured": evidence.get("measured"), "scorer_calls": len(calls),
                      "scorer_input": evidence.get("scorer_input")}))
    assert code == 3
    assert evidence["measured"] is False
    assert "scorer input" in evidence["error"]
    assert calls == []
    assert not (tmp_path / "verifier/reward.txt").exists()


def test_foreign_verifier_spec_is_refused_against_selected_task(case, tmp_path, monkeypatch):
    calls = []
    def inner(*args, **kwargs):
        calls.append(True)
        return {"kind": "command", "passed": True, "score": 0.25}
    monkeypatch.setattr(verifier, "_verify_inner", inner)
    result = verifier._verify(tmp_path, case.other, "", sandbox=False, timeout_s=5,
                              task_id=case.record["task_id"])
    assert result.get("unmeasured")
    assert result.get("score") is None
    assert not calls


@pytest.mark.parametrize("fault", ["missing", "foreign-task", "foreign-digest", "unverified"])
def test_native_verdict_cannot_omit_or_relabel_consumed_identity(case, tmp_path, monkeypatch, fault):
    binding = case.spec.get("scorer_input", {})
    receipt = {**binding, "expected_sha256": binding.get("sha256"), "verified": True}
    if fault == "foreign-task":
        receipt["task_id"] = case.other_record["task_id"]
    elif fault == "foreign-digest":
        receipt["sha256"] = hashlib.sha256(gold_bytes(case.other)).hexdigest()
    elif fault == "unverified":
        receipt["verified"] = False
    evidence = {"measured": True}
    if fault != "missing":
        evidence["scorer_input"] = receipt
    monkeypatch.setattr(verifier, "_verify_inner", lambda *a, **kw: {
        "kind": "command", "passed": True, "score": 0.25, "evidence": evidence})
    result = verifier._verify(tmp_path, case.spec, "", sandbox=False, timeout_s=5,
                              task_id=case.record["task_id"])
    assert result.get("unmeasured")
    assert result.get("score") is None


def test_native_matching_identity_preserves_reward(case, tmp_path, monkeypatch):
    spec = copy.deepcopy(case.spec)
    # The sealed runtime requires sandbox=True; exercise identity binding on the
    # generic route that reaches this test's verifier boundary spy.
    spec.pop("native_runtime", None)
    binding = case.spec.get("scorer_input", {})
    receipt = {**binding, "expected_sha256": binding.get("sha256"), "verified": True}
    monkeypatch.setattr(verifier, "_verify_inner", lambda *a, **kw: {
        "kind": "command", "passed": True, "score": 0.25,
        "evidence": {"measured": True, "scorer_input": receipt}})
    result = verifier._verify(tmp_path, spec, "", sandbox=False, timeout_s=5,
                              task_id=case.record["task_id"])
    assert not result.get("unmeasured")
    assert result["score"] == 0.25


def test_native_missing_selected_task_is_refused(case, tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(verifier, "_verify_inner", lambda *a, **kw: calls.append(True) or {})
    result = verifier._verify(tmp_path, case.spec, "", sandbox=False, timeout_s=5)
    assert result.get("unmeasured")
    assert result.get("score") is None
    assert not calls


@pytest.mark.parametrize("mode", ["unchanged", "foreign-gold", "unbound-check"])
def test_native_materialization_check_and_verdict_consumption(case, tmp_path, monkeypatch, mode):
    """Use real staging and verdict reads; intercept only the process/scorer boundary."""
    spec = copy.deepcopy(case.spec)
    # The sealed runtime requires sandbox=True; exercise identity binding on the
    # generic route that reaches this test's process boundary spy.
    spec.pop("native_runtime", None)
    if mode == "unbound-check":
        for flag in ("--task-id", "--gold-sha256"):
            if flag in spec["argv"]:
                index = spec["argv"].index(flag)
                del spec["argv"][index:index + 2]
    results = []

    def process(argv, **kwargs):
        # Staging has completed. A foreign input is substituted at the last moment
        # before the real check reads it, rather than editing the trusted spec's pin.
        payload = gold_bytes(case.other if mode == "foreign-gold" else spec)
        code, evidence, calls = invoke(case, spec, payload, tmp_path, monkeypatch)
        results.append((evidence, calls))
        return subprocess.CompletedProcess(argv, code, "", "")

    monkeypatch.setattr(verifier.subprocess, "run", process)
    result = verifier._verify(tmp_path, spec, "", sandbox=False, timeout_s=5,
                              task_id=case.record["task_id"])
    evidence, calls = results[0]
    print(json.dumps({"dataset": case.name, "case": f"native-{mode}",
                      "score": result.get("score"), "unmeasured": result.get("unmeasured"),
                      "scorer_calls": len(calls), "scorer_input": evidence.get("scorer_input")}))
    if mode == "unchanged":
        assert result["score"] == 0.25
        assert not result.get("unmeasured")
        assert calls == [case.record["gold"]]
    else:
        assert result.get("score") is None
        assert result.get("unmeasured")
        if mode == "foreign-gold":
            assert not calls
            assert not (tmp_path / "verifier/reward.txt").exists()
        else:
            assert evidence["scorer_input"]["verified"] is False
