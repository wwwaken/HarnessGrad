"""Synthetic lifecycle/regression checks; forbid external execution and sockets."""
from copy import deepcopy
import json
from pathlib import Path
import socket
import subprocess

import pytest

from eval import diagnostic_policy as policy, lifecycle_receipt as lifecycle
from lifecycle_fixtures_codex177 import attest, completed_lifecycle, stage_evidence, summaries

BINDING = dict(adapter_id="synthetic-adapter-177", run_id="unit-diagnostic",
               trial_id="synthetic-trial-1", manifest_sha256="c" * 64)
OUTCOMES = [dict(task_id="synthetic-task-177", trial=1, status="measured", score=0.0, reason=None)]


@pytest.fixture(autouse=True)
def no_external_execution(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError("synthetic lifecycle attempted external execution")
    monkeypatch.setattr(subprocess, "run", refuse)
    monkeypatch.setattr(subprocess, "Popen", refuse)
    monkeypatch.setattr(socket, "socket", refuse)


@pytest.fixture
def context():
    return dict(dataset="synthetic-dataset-177", side="train",
                metric=dict(name="synthetic metric", scorer_sha256="b" * 64),
                hashes={key: "c" * 64 for key in policy.HASH_NAMES},
                endpoint=policy.ENDPOINTS[0], limits=dict(resource=dict(bytes=1), budget=dict(calls=1)),
                gates=dict(status="passed", receipt_sha256="a" * 64, detail="synthetic gate"),
                comparability_notes=["Synthetic tests only; no model/H0 or production evidence."])


def checkpoint(stop="scope"):
    receipt = lifecycle.start_lifecycle(BINDING, "a" * 64)
    for stage, evidence in stage_evidence(BINDING, OUTCOMES).items():
        if receipt["state"] == stop:
            break
        receipt = lifecycle.transition(receipt, stage, evidence)
    return receipt


def test_all_checkpoints_are_immutable_and_only_cleanup_permits_publication():
    receipt = checkpoint()
    for stage, evidence in stage_evidence(BINDING, OUTCOMES).items():
        before = deepcopy((receipt, evidence))
        advanced = lifecycle.transition(receipt, stage, evidence)
        assert (receipt, evidence) == before
        assert advanced["publication_ready"] == (stage == "cleanup")
        assert advanced["production_authorized"] is False
        assert "score" not in advanced
        lifecycle.validate_lifecycle_receipt(advanced)
        receipt = advanced
    assert len(json.dumps(receipt).encode()) < lifecycle.MAX_BYTES


@pytest.mark.parametrize("current", lifecycle.STAGES)
@pytest.mark.parametrize("requested", lifecycle.STAGES[1:])
def test_skips_repeats_and_cleanup_before_seal_are_refused(current, requested):
    receipt = checkpoint(current)
    if current != "cleanup" and requested == lifecycle.STAGES[lifecycle.STAGES.index(current) + 1]:
        return
    before = deepcopy(receipt)
    with pytest.raises(ValueError):
        lifecycle.transition(receipt, requested, stage_evidence(BINDING, OUTCOMES)[requested])
    assert receipt == before


@pytest.mark.parametrize("stage", ["execute", "quiesce", "score", "seal"])
@pytest.mark.parametrize("status", ["failed", "unknown"])
def test_failures_allow_cleanup_but_never_measurement(stage, status):
    previous = lifecycle.STAGES[lifecycle.STAGES.index(stage) - 1]
    receipt = lifecycle.transition(checkpoint(previous), stage, attest(BINDING, stage, status=status))
    with pytest.raises(ValueError, match="only attempt cleanup"):
        lifecycle.transition(receipt, "score", stage_evidence(BINDING, OUTCOMES)["score"])
    final = lifecycle.transition(receipt, "cleanup", stage_evidence(BINDING, OUTCOMES)["cleanup"])
    assert final["status"] == status and not final["publication_ready"]
    assert final["events"][-1]["status"] == "passed"


@pytest.mark.parametrize("stage", ["admit", "cleanup"])
def test_admission_and_cleanup_refusals_are_preserved(stage):
    receipt = checkpoint("scope" if stage == "admit" else "seal")
    facts = stage_evidence(BINDING, OUTCOMES)[stage]
    if stage == "admit":
        facts["observed"]["read_only_root"] = False
    else:
        facts["observed"]["objects"][0]["absent"] = False
    final = lifecycle.transition(receipt, stage, facts)
    lifecycle.validate_lifecycle_receipt(final)
    assert final["status"] == "failed" and not final["publication_ready"]
    refusal = final["events"][-1]["evidence"]["refusal"]
    assert refusal["status"] == "blocked"
    if stage == "cleanup":
        assert refusal["lease_action"] == "quarantine"


@pytest.mark.parametrize("key", BINDING)
@pytest.mark.parametrize("stage", lifecycle.STAGES[1:])
def test_cross_run_trial_adapter_and_manifest_evidence_cannot_publish(stage, key):
    receipt = checkpoint(lifecycle.STAGES[lifecycle.STAGES.index(stage) - 1])
    facts = stage_evidence(BINDING, OUTCOMES)[stage]
    binding = facts["observed"]["binding"] if stage in ("admit", "cleanup") else facts["binding"]
    binding[key] = "f" * 64 if key == "manifest_sha256" else "stale-synthetic-identity"
    if stage in ("admit", "cleanup"):
        assert not lifecycle.transition(receipt, stage, facts)["publication_ready"]
    else:
        with pytest.raises(ValueError, match="stale"):
            lifecycle.transition(receipt, stage, facts)


@pytest.mark.parametrize("change", ["preflight_only", "missing_artifact", "timeout", "oom", "exit",
                                   "inodes", "binding", "outcomes", "worker_runtime"])
def test_seal_requires_matching_result_and_completed_snapshot(change):
    evidence = stage_evidence(BINDING, OUTCOMES)["seal"]
    snapshot = evidence["facts"]["snapshot"]
    facts = snapshot["facts"]
    if change == "preflight_only":
        evidence["facts"]["snapshot"] = facts["preflight"]
    elif change == "missing_artifact":
        facts["artifact_sha256"] = None
    elif change == "timeout":
        facts["timed_out"] = True
    elif change == "oom":
        facts["oom_killed"] = True
    elif change == "exit":
        facts["exit_code"] = 137
    elif change == "inodes":
        facts["preflight"]["observed"]["free_inodes"] = 0
    elif change == "binding":
        snapshot["binding"]["run_id"] = "stale-synthetic-run"
    elif change == "outcomes":
        evidence["facts"]["outcomes_sha256"] = "f" * 64
    elif change == "worker_runtime":
        facts["runtime"]["observed"]["read_only_root"] = False
    with pytest.raises((ValueError, RuntimeError)):
        lifecycle.transition(checkpoint("score"), "seal", evidence)


@pytest.mark.parametrize("mutation", [
    lambda r: r.update(publication_ready=True), lambda r: r.update(production_authorized=True),
    lambda r: r.update(state="cleanup"), lambda r: r["events"].pop(0),
    lambda r: r["events"][-1].update(status="failed"),
    lambda r: r["events"][-1].update(receipt_sha256="f" * 64),
])
def test_replay_refuses_tampered_state_status_and_event_receipts(mutation):
    receipt = checkpoint("seal")
    mutation(receipt)
    with pytest.raises(ValueError):
        lifecycle.validate_lifecycle_receipt(receipt)


def diagnostic(context, *, complete=True, cleanup_status="passed", snapshot_status="passed"):
    selected = [OUTCOMES[0]["task_id"]]
    receipt = completed_lifecycle(context, selected, selected, OUTCOMES)
    cleanup, snapshot = summaries(receipt)
    if cleanup_status != "passed":
        cleanup.update(status=cleanup_status, receipt_sha256=None)
    if snapshot_status != "passed":
        snapshot.update(status=snapshot_status, receipt_sha256=None)
    return policy.build_receipt(run_id=BINDING["run_id"], stage="diagnostic", eligible=selected,
                                selected=selected, context=context, outcomes=OUTCOMES,
                                cleanup=cleanup, snapshot=snapshot,
                                lifecycle=receipt if complete else None)


def test_completed_lifecycle_publishes_valid_measured_zero(context):
    receipt = diagnostic(context)
    policy.validate_receipt(receipt)
    assert receipt["score"] == 0.0 and receipt["coverage"]["measured_trials"] == 1


@pytest.mark.parametrize("field", ["cleanup_status", "snapshot_status"])
@pytest.mark.parametrize("status", ["failed", "unknown"])
def test_pending_attestations_withhold_all_scores_and_recompute_coverage(context, field, status):
    receipt = diagnostic(context, **{field: status})
    policy.validate_receipt(receipt)
    assert receipt["score"] is None and receipt["coverage"]["measured_trials"] == 0
    assert receipt["coverage"]["unmeasured_trials"] == 1
    assert receipt["outcomes"][0]["score"] is None and receipt["outcomes"][0]["reason"]
    assert OUTCOMES[0]["score"] == 0.0


@pytest.mark.parametrize("stage", lifecycle.STAGES)
def test_each_pending_checkpoint_withholds_scores_until_cleanup(context, stage):
    selected = [OUTCOMES[0]["task_id"]]
    receipt = completed_lifecycle(context, selected, selected, OUTCOMES)
    cleanup, snapshot = summaries(receipt)
    checkpoint_receipt = lifecycle.start_lifecycle(receipt["binding"], receipt["scope_sha256"])
    for step, evidence in stage_evidence(receipt["binding"], OUTCOMES).items():
        if checkpoint_receipt["state"] == stage:
            break
        checkpoint_receipt = lifecycle.transition(checkpoint_receipt, step, evidence)
    row = policy.build_receipt(run_id=BINDING["run_id"], stage="diagnostic", eligible=selected,
                               selected=selected, context=context, outcomes=OUTCOMES,
                               cleanup=cleanup, snapshot=snapshot, lifecycle=checkpoint_receipt)
    policy.validate_receipt(row)
    assert row["score"] == (0.0 if stage == "cleanup" else None)
    assert row["coverage"]["measured_trials"] == (1 if stage == "cleanup" else 0)


def test_passing_summary_booleans_alone_cannot_publish(context, tmp_path):
    receipt = diagnostic(context, complete=False)
    policy.write_receipt(tmp_path / "synthetic-receipt-177.json", receipt)
    assert receipt["score"] is None and receipt["lifecycle"] is None
    receipt["outcomes"] = deepcopy(OUTCOMES)
    receipt["score"] = 0.0
    receipt["coverage"].update(measured_tasks=1, measured_trials=1, unmeasured_tasks=0, unmeasured_trials=0)
    with pytest.raises(ValueError):
        policy.write_receipt(tmp_path / "refused-receipt-177.json", receipt)
    assert not (tmp_path / "refused-receipt-177.json").exists()
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((Path(__file__).resolve().parents[2] / "eval/diagnostic_receipt.schema.json").read_text())
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(receipt, schema)


@pytest.mark.parametrize("change", ["outcomes", "cleanup", "snapshot", "scope", "run"])
def test_changed_publication_cannot_reuse_a_completed_lifecycle(context, change):
    receipt = diagnostic(context)
    if change == "outcomes":
        receipt["outcomes"][0]["score"] = receipt["score"] = 1.0
    elif change in ("cleanup", "snapshot"):
        receipt[change]["receipt_sha256"] = "f" * 64
    elif change == "scope":
        receipt["context"]["limits"]["budget"]["calls"] = 2
    else:
        receipt["run_id"] = "stale-synthetic-run"
    with pytest.raises(ValueError):
        policy.validate_receipt(receipt)


def test_receipt_size_is_bounded_before_replay():
    receipt = checkpoint("seal")
    receipt["events"][0]["evidence"]["untrusted_payload"] = "x" * lifecycle.MAX_BYTES
    with pytest.raises(ValueError, match="too large"):
        lifecycle.validate_lifecycle_receipt(receipt)


def test_rejected_observations_are_not_exported_to_lifecycle_receipts():
    evidence = stage_evidence(BINDING, OUTCOMES)["admit"]
    evidence["observed"]["private_log"] = "synthetic-private-sentinel-177"
    receipt = lifecycle.transition(checkpoint(), "admit", evidence)
    assert "synthetic-private-sentinel-177" not in json.dumps(receipt)
    assert receipt["events"][0]["evidence"]["refusal"]["reason"] == "invalid_observation"
    lifecycle.validate_lifecycle_receipt(receipt)
