from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from harnessgrad.runtime import (  # noqa: E402
    ArtifactKind, EventRecorder, ImplementationMode, Owner, ParentRef, Scope, Stage, StageID,
    artifact, validate_events,
)
from harnessgrad.runtime.compat import LegacyCompatibilityWrapper  # noqa: E402
from harnessgrad.runtime.validator import ProtocolError  # noqa: E402

H = "sha256:" + "a" * 64


def boot():
    return {"protocol_version": "1.0", "run_id": "run-1", "event_id": "boot-1",
        "event_kind": "protocol_bootstrap", "producer": {"role": "framework", "id": "framework-1"},
        "bootstrap": {"profile_opt_in": "test.v1", "stage_modes": {},
            "task_plan": {"task_set_sha": H}, "evidence_mode": "trusted_events",
            "budget": {"unit": "generations", "limit": 2}, "delegates": []}}


def ev(eid, stage, payload, *, producer="framework", lifecycle="completed", evidence="measured",
       mode="custom", inputs=None, outputs=None, artifacts=None, **kwargs):
    return {"protocol_version": "1.0", "run_id": "run-1", "event_id": eid,
        "event_kind": "stage_completed" if lifecycle == "completed" else "stage_failed",
        "scope": {"run_id": "run-1", "session_id": "s-1", "iteration_id": "i-1", "branch_id": "b-1"},
        "stage": {"id": stage, "invocation_id": "inv-" + eid, "mode": mode},
        "lifecycle": lifecycle, "evidence": evidence,
        "owner": {"role": producer, "id": producer + "-1"},
        "producer": {"role": producer, "id": producer + "-1"},
        "implementation": {"module": "test.module", "compliance": "declared", "fidelity": "unknown"},
        "artifacts": artifacts or [], "input_artifacts": inputs or [], "output_artifacts": outputs or [],
        "result_kind": "artifact" if outputs else "empty", "attempt_id": "attempt-" + eid,
        "attempt": 1, "idempotency_key": "idem-" + eid,
        "started_at": "2026-10-09T00:00:00Z", "finished_at": "2026-10-09T00:00:01Z",
        "payload": payload, **kwargs}


def art(aid, kind, *, producer="framework", **kwargs):
    return {"artifact_id": aid, "kind": kind, "sha256": H, "visibility": "public_record",
        "producer": {"role": producer, "id": producer + "-1"}, **kwargs}


def test_multi_parent_dgm_archive_and_typed_crossover():
    p1, p2 = art("parent-1", "parent_state", root=True), art("parent-2", "parent_state", root=True)
    child = art("candidate-1", "candidate", parents=["parent-1", "parent-2"],
                lineage=[{"parent_id": "parent-1", "role": "base"},
                         {"parent_id": "parent-2", "role": "crossover"}], content_kind="tree")
    events = [boot(), ev("ctx-1", "select_context", {"payload_kind": "context_selection", "task_set_sha": H,
        "parent_refs": [{"parent_id": "parent-1", "role": "base"}, {"parent_id": "parent-2", "role": "crossover"}],
        "selection_basis": "archive sampling"}, artifacts=[p1, p2]),
        ev("proposal-1", "propose_changes", {"payload_kind": "proposal", "candidate_ids": ["candidate-1"],
            "artifact_kind": "tree", "hypothesis": "combine"}, artifacts=[child]),
        ev("archive-1", "select_context", {"payload_kind": "archive", "member_ids": ["parent-1", "parent-2", "candidate-1"],
            "retention_rule": "keep_all"})]
    assert validate_events(events)


def test_dream_replay_is_not_new_execution():
    events = [boot(), ev("replay-1", "execute", {"payload_kind": "execution", "execution_mode": "replay",
        "replay_kind": "stored_counterfactual", "source_trace_ids": ["trace-1"], "new_execution": False},
        outputs=[art("trace-2", "experience")])]
    assert validate_events(events)
    events[1]["payload"]["new_execution"] = True
    try: validate_events(events)
    except ProtocolError as exc: assert "replay_execution_contract" in str(exc)
    else: raise AssertionError("replay claimed new execution")


def test_full_file_sica_artifact_kind_and_root_lineage():
    candidate = art("candidate-1", "candidate", root=True, content_kind="full_file")
    events = [boot(), ev("proposal-1", "propose_changes", {"payload_kind": "proposal", "candidate_ids": ["candidate-1"],
        "artifact_kind": "full_file", "hypothesis": "rewrite whole source"}, artifacts=[candidate])]
    assert validate_events(events)


def test_nested_proposer_training_and_feedback_fanout():
    parent_scope = {"run_id": "run-1", "session_id": "s-1", "iteration_id": "train-1", "branch_id": "proposer",
                   "parent_scope": "outer-1"}
    event_value = ev("train-1", "execute", {"payload_kind": "execution", "execution_mode": "online",
        "new_execution": True})
    event_value["claims"] = {"training_scope": "proposer"}
    event_value["scope"] = parent_scope
    fb = ev("fb-1", "organize_feedback", {"payload_kind": "feedback", "source_artifact_ids": [],
        "consumer_scope": "outer-1", "feedback_consumers": ["proposer-trainer", "outer-policy"]})
    assert validate_events([boot(), event_value, fb])


def test_async_late_events_idempotent_retry_and_reconciliation(tmp_path):
    rec = EventRecorder("run-1", "s-1", stream=tmp_path / "events.jsonl")
    rec.bootstrap(task_set_sha=H)
    scope = Scope("run-1", "s-1", "i-1", "b-1")
    kwargs = dict(scope=scope, stage=Stage(StageID.EVALUATE_CANDIDATES, "inv-1", ImplementationMode.CUSTOM),
        payload={"payload_kind": "study_evaluation", "score_kind": "study", "candidate_ids": [],
                 "scorer_revision": "v1", "evaluation_completeness": "partial"},
        implementation={"module": "evaluator.v1", "compliance": "verified", "fidelity": "measured"},
        event_id="late-1", idempotency_key="trial-attempt-1", attempt_id="attempt-1", attempt=1)
    first = rec.record(**kwargs)
    assert first == rec.record(**kwargs)
    rec.record(**{**kwargs, "event_id": "late-2", "idempotency_key": "late-result-2", "attempt_id": "attempt-2", "attempt": 2})
    rec.reconcile(scope=scope, stage=Stage(StageID.EVALUATE_CANDIDATES, "reconcile-1", "custom"),
                  event_ids=["late-1", "late-2"], reason="late attempt arrived")
    assert [e["event_id"] for e in rec.events][1:3] == ["late-1", "late-2"]
    assert validate_events(list(rec.events))
    lines = (tmp_path / "events.jsonl").read_text().splitlines()
    assert len(lines) == 4
    try: rec.record(**{**kwargs, "claims": {"different": True}})
    except ValueError as exc: assert "idempotency_conflict" in str(exc)
    else: raise AssertionError("conflicting idempotent retry accepted")


def test_selection_and_deployment_are_distinct_facts():
    events = [boot(), ev("select-1", "select_deploy", {"payload_kind": "selection_result",
        "selected_candidate_ids": ["candidate-a", "candidate-b"], "basis": ["study-a"], "tentative": True},
        producer="method"), ev("deploy-1", "select_deploy", {"payload_kind": "deployment_fact",
        "deployment_id": "deploy-1", "deployed_candidate_ids": [], "status": "none",
        "from_snapshot": H, "to_snapshot": H}, producer="deployer")]
    assert validate_events(events)


def test_healthy_measured_empty_and_unobserved_legacy_claim():
    empty = ev("empty-1", "propose_changes", {"payload_kind": "proposal", "candidate_ids": [],
        "artifact_kind": "none", "hypothesis": "no change"})
    assert validate_events([boot(), empty])


def test_heldout_taint_rejected_through_indirect_lineage():
    hidden = art("hidden-score", "heldout_score", producer="evaluator", visibility="heldout_private", score_kind="heldout")
    summary = art("summary", "feedback", parents=["hidden-score"])
    feedback = ev("feedback-1", "organize_feedback", {"payload_kind": "feedback",
        "source_artifact_ids": ["summary"], "consumer_scope": "s-1"}, inputs=[summary], artifacts=[summary])
    with_hidden = ev("score-1", "evaluate_candidates", {"payload_kind": "study_evaluation", "score_kind": "study",
        "candidate_ids": [], "scorer_revision": "v1", "evaluation_completeness": "partial"},
        producer="evaluator", outputs=[hidden])
    try: validate_events([boot(), with_hidden, feedback])
    except ProtocolError as exc: assert "heldout_taint_to_adaptation" in str(exc)
    else: raise AssertionError("heldout indirect taint accepted")


def test_compatibility_wrapper_preserves_one_json_stdout_and_marks_unknown(tmp_path):
    method = tmp_path / "legacy.py"
    method.write_text("import json,sys\nr=json.load(sys.stdin)\nprint(json.dumps({'steps': 1, 'changed': True}))\n")
    stream = tmp_path / "events.jsonl"
    result = LegacyCompatibilityWrapper([sys.executable, str(method)], event_stream=stream).run({
        "run_id": "run-1", "session_id": "s-1", "task_ids": ["task-1"], "trajectory_out": str(tmp_path / "trajectory.json")})
    assert result.response == {"steps": 1, "changed": True}
    assert result.returncode == 0
    assert len(result.events) == 9  # bootstrap + one legacy proposal + seven unobserved phases
    proposal = next(e for e in result.events if e.get("stage", {}).get("id") == "propose_changes")
    assert proposal["evidence"] == "unobserved"
    assert proposal["implementation"]["compliance"] == "unverified"
    assert proposal["claims"]["legacy_changed"] is True
    assert validate_events(list(result.events))
    assert len(stream.read_text().splitlines()) == 9


def test_validator_rejects_forged_platform_deployment():
    forged = ev("deploy-1", "select_deploy", {"payload_kind": "deployment_fact", "deployment_id": "d-1",
        "deployed_candidate_ids": ["candidate-1"], "status": "deployed", "from_snapshot": H, "to_snapshot": H}, producer="method")
    try: validate_events([boot(), forged])
    except ProtocolError as exc: assert "method_forged_deployment" in str(exc)
    else: raise AssertionError("method claim promoted to deployment fact")
