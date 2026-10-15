"""Synthetic timeout admission regression; no dataset, model or runtime launches."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from eval.run import runner
from eval.verification import verifier


@pytest.fixture(params=["host", "sandbox", "exec", "snapshot"])
def expired_verdict(request, monkeypatch, tmp_path):
    mode = request.param
    launches, removed = [], []
    spec = {"kind": "command", "argv": ["synthetic-check"], "timeout_s": 1,
            "reward_file": "/verifier/reward.txt"}

    def timeout(*args, **kwargs):
        launches.append(kwargs.get("timeout_s", kwargs.get("timeout")))
        raise subprocess.TimeoutExpired("synthetic-check", 1)

    # Fail closed if any unmocked transport is reached; no Docker or sandbox starts.
    def denied(*args, **kwargs):
        pytest.fail("unexpected runtime launch")

    monkeypatch.setattr(verifier.subprocess, "run", denied)
    monkeypatch.setattr(verifier.sandbox_mod, "run", denied)
    monkeypatch.setattr(verifier.container_mod, "run", denied)
    monkeypatch.setattr(verifier.container_mod, "create", denied)
    if mode == "snapshot":
        snapshot = (ROOT / "tests/fixtures/hg_wsnap/raw/015.stdout.txt").read_text().strip()
        monkeypatch.setattr(verifier.container_mod, "docker",
                            lambda *a, **k: subprocess.CompletedProcess(a, 0, snapshot, ""))
        monkeypatch.setattr(verifier.container_mod, "create", lambda *a, **k: None)
        monkeypatch.setattr(verifier.container_mod, "start", lambda *a, **k: None)
        monkeypatch.setattr(verifier.container_mod, "mkdir_in", lambda *a, **k: None)
        monkeypatch.setattr(verifier.container_mod, "remove_container", removed.append)
        monkeypatch.setattr(verifier.container_mod, "exec_in", timeout)
        verdict = verifier._verify_container_state(
            snapshot, spec, expected_snapshot=snapshot, task_mount="/app", staging=tmp_path,
            timeout_s=10, run_id="synthetic-w-hotpot", task_id="synthetic-timeout")
        assert len(removed) == 1
    else:
        target = {"host": verifier.subprocess, "sandbox": verifier.sandbox_mod,
                  "exec": verifier.container_mod}[mode]
        monkeypatch.setattr(target, "run", timeout)
        verdict = verifier._verify(
            tmp_path, spec, "", sandbox=mode != "host", timeout_s=10,
            env={"kind": "exec", "image": "synthetic-image"}
            if mode == "exec" else {"kind": "files"})
    assert launches == [1]
    assert "timed out after 1s" in verdict["detail"]
    return verdict


@pytest.mark.parametrize("trials, timeout_trial", [(1, 1), (3, 2)])
def test_timeout_is_unmeasured_through_persistence_and_aggregation(
        expired_verdict, monkeypatch, tmp_path, trials, timeout_trial):
    """Timeouts cannot enter task/trial scores or cache, even after a good trial."""
    calls = {}

    def synthetic_run(_repo, task, **kwargs):
        tid = task["task_id"]
        calls[tid] = calls.get(tid, 0) + 1
        score = 0.0 if tid == "synthetic-zero" else 1.0
        verdict = (expired_verdict
                   if tid == "synthetic-timeout" and calls[tid] == timeout_trial
                   else {"kind": "command", "passed": bool(score), "score": score,
                         "scorer_isolation_class": expired_verdict["scorer_isolation_class"],
                         "detail": "synthetic completed check"})
        return {"verdict": verdict, "trace": "synthetic trace\n",
                "exit_code": 0, "stderr": ""}

    monkeypatch.setattr(runner, "run_one", synthetic_run)
    cache = {}
    result = runner._evaluate(
        tmp_path, [{"task_id": tid} for tid in (
            "synthetic-pass", "synthetic-zero", "synthetic-timeout")], {}, cache=cache,
        trials=trials, jobs=1, progress_dir=tmp_path, round_no=0)

    assert result["per_task"] == {"synthetic-pass": 1.0, "synthetic-zero": 0.0}
    assert sum(result["per_task"].values()) / len(result["per_task"]) == 0.5
    assert calls["synthetic-timeout"] == timeout_trial
    assert set(result["invalid"]) == {"synthetic-timeout"}
    invalid = result["invalid"]["synthetic-timeout"]
    assert invalid == {"stage": "check", "outcome": "timeout",
                       "detail": "the verifier timed out after 1s"}
    assert expired_verdict["outcome"] == "timeout"
    assert expired_verdict["unmeasured"] == invalid["detail"]
    assert "score" not in expired_verdict
    assert "synthetic-timeout" not in result["per_task_trials"]
    assert "synthetic-timeout" not in result["trial_verdicts"]
    assert "synthetic-timeout" not in result["verdicts"]
    assert len(cache) == 2
    assert sorted(entry["score"] for entry in cache.values()) == [0.0, 1.0]

    progress = tmp_path / "progress" / "round-0"
    record = json.loads((progress / "synthetic-timeout.json").read_text())
    assert record["invalid"] == invalid
    assert not {"score", "trial_scores", "complete"}.intersection(record)
    assert (progress / "traces" / "synthetic-timeout.invalid.jsonl").read_text() == "synthetic trace\n"
    zero = json.loads((progress / "synthetic-zero.json").read_text())
    assert zero["score"] == 0.0 and zero["complete"] is True


def test_timeout_only_round_has_no_measurement_or_cache(
        expired_verdict, monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "run_one", lambda *a, **k: {
        "verdict": expired_verdict, "trace": "", "exit_code": 0, "stderr": ""})
    cache = {}
    result = runner._evaluate(
        tmp_path, [{"task_id": "synthetic-timeout"}], {}, cache=cache,
        progress_dir=tmp_path, trials=1, jobs=1)
    assert result["per_task"] == {}
    assert result["per_task_trials"] == {}
    assert result["invalid"]["synthetic-timeout"]["outcome"] == "timeout"
    assert cache == {}
