"""Runner refusal regressions using authored facts; no backend or dataset access."""
from copy import deepcopy
import json
from pathlib import Path
import socket
import subprocess
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from eval.run import runner
from eval.admission import runner_admission
from eval.verification.isolation import IsolationMismatch, require_comparable

TASK = {"task_id": "synthetic-admission-163"}


@pytest.fixture(autouse=True)
def no_backend_execution(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError("admission test attempted backend execution")

    monkeypatch.setattr(subprocess, "run", refuse)
    monkeypatch.setattr(subprocess, "Popen", refuse)
    monkeypatch.setattr(socket, "socket", refuse)
    monkeypatch.setattr(runner.container_mod, "docker", refuse)
    monkeypatch.setattr(runner.sandbox_mod, "run", refuse)
    monkeypatch.setattr(runner.services_mod, "start", refuse)
    monkeypatch.setattr(runner, "_run_one_container_state", refuse)
    # Do not hash platform/dataset files while testing the score aggregation seam.
    monkeypatch.setattr(runner, "snapshot", lambda *args: {})
    monkeypatch.setattr(runner, "diff", lambda *args: {})


def assert_refusal(result):
    assert result["exit_code"] is None
    assert "verdict" not in result
    invalid = result["invalid"]
    assert invalid["stage"] == "admission"
    assert invalid["detail"] == "backend_observation_unavailable"
    receipt = invalid["receipt"]
    assert receipt["status"] == "blocked"
    assert receipt["observation"] == "unknown"
    assert receipt["measured"] is False
    assert receipt["production_authorized"] is False
    assert "score" not in receipt
    assert len(json.dumps(receipt).encode()) <= runner_admission.MAX_RECEIPT_BYTES


@pytest.mark.parametrize("env", [
    {"cpus": 2}, {"memory_mb": 128},
    {"resources": {}}, {"filesystems": {}},
    {"resource_policy": None}, {"network_policy": {}}, {"artifact_policy": {}},
    {"kind": "exec", "image": "synthetic-image"},
    {"kind": "exec", "network": "none"},
    {"kind": "exec", "state": "container"},
    {"kind": "exec", "network": "services", "services": [{"name": "synthetic"}]},
    {"kind": "exec", "network": "bridge"},
])
@pytest.mark.parametrize("sandbox", [True, False])
def test_policy_refusal_precedes_manifest_storage_and_backend_dispatch(
        tmp_path, monkeypatch, env, sandbox):
    def refuse(*args, **kwargs):
        raise AssertionError("policy refusal must precede manifest/storage access")

    before = deepcopy(env)
    monkeypatch.setattr(Path, "read_text", refuse)
    monkeypatch.setattr(runner.tempfile, "mkdtemp", refuse)
    result = runner.run_one(tmp_path / "absent-harness", TASK, env=env, sandbox=sandbox,
                            setup={"files": [{"path": "unused", "from": "absent"}]})
    assert_refusal(result)
    assert env == before


@pytest.mark.parametrize("env", [
    {"kind": "files", "network": "none"},
    {"agent_timeout_s": 5}, {"verify_timeout_s": 5},
    {"kind": "files"}, {},
    {"kind": "files", "network": "none", "agent_timeout_s": 5, "verify_timeout_s": 5},
])
def test_platform_applied_policies_need_no_backend_observation(env):
    before = deepcopy(env)
    assert runner._refuse_unobserved_policies(TASK, env, None) is None
    assert env == before


@pytest.mark.parametrize("route", [{"kind": "exec"}, {"state": "container"}])
@pytest.mark.parametrize("declare_network", [True, False])
def test_external_network_trigger_requires_a_declaration(route, declare_network):
    env = {**route, **({"network": "none"} if declare_network else {})}
    refusal = runner._refuse_unobserved_policies(TASK, env, None)
    assert_refusal(refusal)
    fields = refusal["invalid"]["receipt"]["policy_fields"]
    assert ("env.network" in fields) is declare_network


@pytest.mark.parametrize("verifier", [{"artifact_policy": None}])
def test_verifier_artifact_policy_refuses_before_scoring(tmp_path, verifier):
    assert_refusal(runner.run_one(tmp_path / "absent-harness", TASK, verifier=verifier))


def test_a_verifier_timeout_is_not_a_backend_observation_trigger():
    """The platform enforces a verifier deadline itself, so it is not refused.

    `eval/verification/verifier.py` passes `timeout_s` to `phase_timeout` and to the verifier
    subprocess' `timeout=`, and records expiry as an explicit unmeasured outcome.
    Nothing outside this process has to be observed, so demanding an observation
    refused every adapter that declares a deadline -- the shared QA scaffold sets
    3600s for all of its datasets -- and made their local controls unusable without
    making a run any safer. Asserted against the hook directly, because a full
    `run_one` would fail later for unrelated reasons (absent harness).
    """
    assert runner._refuse_unobserved_policies(TASK, {}, {"timeout_s": 5}) is None
    # The trigger that does remain is asserted above and below.
    assert runner._refuse_unobserved_policies(TASK, {}, {"artifact_policy": None}) is not None


@pytest.mark.parametrize("observation", [None, {}, "unknown", {
    "status": "passed", "enforced": True, "production_authorized": True,
}])
def test_adapter_evidence_cannot_override_missing_trusted_observer(tmp_path, observation):
    env = {"kind": "exec", "network": "none", "observation": observation,
           "admission_receipt": observation}
    result = runner.run_one(tmp_path / "absent-harness", TASK, env=env)
    assert_refusal(result)
    assert "enforced" not in json.dumps(result)


@pytest.mark.parametrize("trials,jobs", [(1, 1), (3, 1), (1, 2), (3, 2)])
def test_unknown_observations_refuse_before_cache_and_never_become_zero_scores(
        tmp_path, monkeypatch, trials, jobs):
    tasks = [TASK, {"task_id": "synthetic-artifact-163"}]
    cache = {f"synthetic-sha:{task['task_id']}:{trials}": {
        "score": 1.0, "trace": "synthetic stale trace", "verdict": {"passed": True},
    } for task in tasks}
    before = deepcopy(cache)

    def refuse(*args, **kwargs):
        raise AssertionError("a policy-bearing task must not execute a trial")

    monkeypatch.setattr(runner, "run_one", refuse)
    result = runner._evaluate(
        tmp_path / "absent-harness", tasks, {}, harness_sha="synthetic-sha", cache=cache,
        envs={TASK["task_id"]: {"kind": "exec", "network": "none"},
              tasks[1]["task_id"]: {"artifact_policy": {}}},
        progress_dir=tmp_path, trials=trials, jobs=jobs,
    )
    assert result["per_task"] == result["verdicts"] == result["per_task_trials"] == {}
    assert result["cached_tasks"] == result["not_run"] == []
    assert set(result["invalid"]) == {task["task_id"] for task in tasks}
    assert cache == before
    for task in tasks:
        record = json.loads((tmp_path / "progress" / "round-0" /
                             f"{task['task_id']}.json").read_text())
        assert record["invalid"] == result["invalid"][task["task_id"]]
        assert record["invalid"]["receipt"]["measured"] is False
        assert "score" not in record


def test_legacy_files_path_without_policy_declarations_still_scores(tmp_path, monkeypatch):
    repo = tmp_path / "synthetic-harness"
    repo.mkdir()
    (repo / "harness.json").write_text(json.dumps({"entrypoint": "unused.py"}))
    monkeypatch.setattr(runner.tempfile, "tempdir", str(tmp_path))
    monkeypatch.setattr(runner, "harness_env", lambda: {})
    monkeypatch.setattr(runner.harness_runtime, "lookup", lambda *args, **kwargs: None)

    def synthetic_run(*args, task_dir, **kwargs):
        (task_dir / "answer.txt").write_text("synthetic answer")
        (task_dir / "trace.jsonl").write_text("{}\n")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(runner.sandbox_mod, "run", synthetic_run)
    result = runner.run_one(repo, TASK, env={"kind": "files"},
                            verifier={"kind": "answer", "expected": "synthetic answer"})
    assert "invalid" not in result
    assert result["verdict"]["passed"] is True


@pytest.mark.parametrize("class_", [None, "in-process"])
def test_only_selected_tasks_are_checked_and_legacy_cache_is_preserved(tmp_path, monkeypatch, class_):
    cache = {f"synthetic-sha:{TASK['task_id']}:1": {
        "score": 1.0, "trace": "synthetic trace", "verdict": {"passed": True},
    }}
    if class_ is not None:
        next(iter(cache.values()))["verdict"]["scorer_isolation_class"] = class_
    before = deepcopy(cache)

    def refuse(*args, **kwargs):
        raise AssertionError("legacy cache hit must not execute")

    monkeypatch.setattr(runner, "run_one", refuse)
    result = runner._evaluate(tmp_path, [TASK], {}, cache=cache, harness_sha="synthetic-sha",
                              envs={"unselected": {"network": "none"}})
    assert result["per_task"] == {TASK["task_id"]: 1.0}
    assert result["cached_tasks"] == [TASK["task_id"]]
    assert result["invalid"] == {}
    assert cache == before
    if class_ is None:
        # Aggregation refusal asserted the write-path bug. Legacy cache evidence
        # stays intact and readable, but absent observations still forbid comparison.
        assert result["scorer_isolation_class"] == "unknown"
        assert result["scorer_isolation_comparable"] is False
        with pytest.raises(IsolationMismatch, match="unknown"):
            require_comparable(result, result)


@pytest.mark.parametrize("stage,policy", [
    ("runtime", {"resources": {"cpu_millis": 1000, "memory_bytes": 4096,
                              "swap_bytes": 0, "pids": 1, "timeout_ms": 1000},
                 "network": "none", "filesystems": {}}),
    ("snapshot", {"max_bytes": 1, "max_inodes": 1, "reserve_bytes": 1,
                  "reserve_inodes": 1, "timeout_ms": 1}),
    ("cleanup", {"owned": [], "timeout_ms": 1}),
])
@pytest.mark.parametrize("observation", [None, {}, "unknown"])
def test_shared_contracts_refuse_malformed_or_unbound_observations(stage, policy, observation):
    binding = {"adapter_id": "synthetic-163", "run_id": "synthetic-run-163",
               "trial_id": "synthetic-trial-1", "manifest_sha256": "a" * 64}
    with pytest.raises(runner_admission.AdmissionError) as error:
        getattr(runner_admission, "admit_" + stage)(binding, policy, observation)
    assert error.value.code == "invalid_observation"
    assert error.value.receipt["measured"] is False
    assert error.value.receipt["production_authorized"] is False
    if stage == "cleanup":
        assert error.value.receipt["lease_action"] == "quarantine"
