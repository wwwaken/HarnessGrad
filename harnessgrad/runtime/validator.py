"""Structural and semantic validation for eight-stage event streams."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - production installs jsonschema
    Draft202012Validator = None

SCHEMA = Path(__file__).resolve().parents[2] / "schemas" / "eight_stage_protocol.schema.json"
STAGES = {"select_context", "execute", "organize_feedback", "propose_changes", "build_validate",
          "evaluate_candidates", "select_deploy", "stop_continue"}
PAYLOAD_KEYS = {
    "context_selection": {"payload_kind", "task_set_sha", "parent_refs", "selection_basis"},
    "execution": {"payload_kind", "execution_mode", "replay_kind", "source_trace_ids", "new_execution", "training_scope"},
    "feedback": {"payload_kind", "source_artifact_ids", "consumer_scope", "feedback_consumers", "consumer_role"},
    "proposal": {"payload_kind", "candidate_ids", "artifact_kind", "hypothesis"},
    "validation": {"payload_kind", "candidate_ids", "valid", "checks"},
    "study_evaluation": {"payload_kind", "score_kind", "candidate_ids", "scorer_revision", "evaluation_completeness"},
    "selection_result": {"payload_kind", "selected_candidate_ids", "basis", "tentative", "later_eval_ref"},
    "deployment_fact": {"payload_kind", "deployment_id", "deployed_candidate_ids", "status", "from_snapshot", "to_snapshot", "rollback_ref"},
    "continuation": {"payload_kind", "action", "next_scope"}, "archive": {"payload_kind", "member_ids", "retention_rule"},
    "reconciliation": {"payload_kind", "reconciles_event_ids"}, "empty_result": {"payload_kind", "reason"},
}


class ProtocolError(ValueError):
    pass


def _schema() -> dict[str, Any]:
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def schema_errors(event: dict[str, Any]) -> list[Any]:
    if Draft202012Validator is None:
        return []
    schema = _schema(); Draft202012Validator.check_schema(schema)
    return sorted(Draft202012Validator(schema).iter_errors(event), key=lambda e: list(e.path))


def validate_event(event: dict[str, Any]) -> bool:
    return validate_events([event])


def _artifact_index(events: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for e in events:
        for a in e.get("artifacts", []) + e.get("input_artifacts", []) + e.get("output_artifacts", []):
            aid = a["artifact_id"]
            if aid in out and out[aid] != a:
                raise ProtocolError(f"artifact_conflict:{aid}")
            out[aid] = a
    return out


def _ancestors(aid: str, arts: dict[str, dict[str, Any]], seen: set[str] | None = None) -> set[str]:
    seen = set() if seen is None else seen
    if aid in seen: return set()
    seen.add(aid)
    a = arts.get(aid)
    if not a: return set()
    parents = set(a.get("parents", []))
    parents |= {x.get("parent_id") for x in a.get("lineage", []) if x.get("parent_id")}
    out = set(parents)
    for parent in parents: out |= _ancestors(parent, arts, seen)
    return out


def _check_parent_refs(payload: dict[str, Any]) -> None:
    refs = payload.get("parent_refs")
    if refs is None: return
    if not isinstance(refs, list): raise ProtocolError("parent_refs_not_array")
    ids: set[str] = set(); roles: set[str] = set()
    for ref in refs:
        if isinstance(ref, dict) and isinstance(ref.get("parent_id"), str):
            aid, role = ref["parent_id"], ref.get("role", "base")
        else: raise ProtocolError("typed_parent_ref_required")
        if aid in ids: raise ProtocolError("duplicate_parent_ref")
        ids.add(aid); roles.add(role)
    if "crossover" in roles and len(ids) < 2: raise ProtocolError("crossover_requires_multiple_parents")


def validate_events(events: list[dict[str, Any]]) -> bool:
    if not events: raise ProtocolError("empty_event_stream")
    if Draft202012Validator is not None:
        validator = Draft202012Validator(_schema())
        for i, e in enumerate(events):
            errors = sorted(validator.iter_errors(e), key=lambda x: list(x.path))
            if errors: raise ProtocolError(f"schema_event_{i}:{errors[0].message}")
    boots = [e for e in events if e.get("event_kind") == "protocol_bootstrap"]
    if len(boots) != 1: raise ProtocolError("exactly_one_bootstrap")
    boot, run_id = boots[0], boots[0]["run_id"]
    if boot["producer"]["role"] not in {"framework", "recorder"}: raise ProtocolError("bootstrap_authority")
    event_ids: dict[str, dict[str, Any]] = {}; idem: dict[str, str] = {}
    for e in events:
        if e["run_id"] != run_id: raise ProtocolError("run_id_mismatch")
        eid = e["event_id"]
        if eid in event_ids and event_ids[eid] != e: raise ProtocolError(f"duplicate_event_conflict:{eid}")
        event_ids[eid] = e
        key = e.get("idempotency_key")
        if key and key in idem and idem[key] != eid: raise ProtocolError(f"idempotency_conflict:{key}")
        if key: idem[key] = eid
    arts = _artifact_index(events)
    graph = {e["event_id"]: set(e.get("causal_parent_events", [])) for e in events}
    for eid, parents in graph.items():
        if eid in parents: raise ProtocolError(f"event_cycle:{eid}")
        if not parents <= set(graph): raise ProtocolError(f"missing_causal_parent:{eid}")
    done: set[str] = set()
    def visit(node: str, active: set[str]) -> None:
        if node in active: raise ProtocolError(f"event_cycle:{node}")
        if node in done: return
        active.add(node)
        for parent in graph[node]: visit(parent, active)
        active.remove(node); done.add(node)
    for node in graph: visit(node, set())
    declared = boot.get("bootstrap", {}).get("stage_modes", {})
    for e in events:
        if e.get("event_kind") == "protocol_bootstrap": continue
        stage, mode, impl = e["stage"], e["stage"]["mode"], e["implementation"]
        if stage["id"] not in STAGES: raise ProtocolError("bad_stage")
        if stage["id"] in declared and declared[stage["id"]] != mode: raise ProtocolError("undeclared_stage_mode")
        if impl.get("mode") and impl["mode"] != mode: raise ProtocolError("mode_mismatch")
        if not impl.get("module"): raise ProtocolError("implementation_module_required")
        life = e["lifecycle"]
        if e["event_kind"] == "stage_started" and life != "running": raise ProtocolError("started_must_be_running")
        if e["event_kind"] == "stage_failed" and life != "failed": raise ProtocolError("failed_event_lifecycle")
        if life == "failed" and "failure" not in e: raise ProtocolError("failed_without_failure")
        if life != "failed" and "failure" in e: raise ProtocolError("failure_on_nonfailed")
        failure = e.get("failure")
        if failure:
            infra = {"delegate_error", "evaluator_error", "recorder_error", "infrastructure_unavailable"}
            if failure["class"] in infra:
                if failure["subject_or_infrastructure"] != "infrastructure" or e["evidence"] != "unobserved":
                    raise ProtocolError("infrastructure_failure_must_be_unobserved")
            elif failure["subject_or_infrastructure"] != "subject" or e["evidence"] != "measured":
                raise ProtocolError("subject_failure_must_be_measured")
        if mode == "delegated":
            for key in ("delegate_id", "capabilities", "timeout_ms", "request_artifact_id", "response_artifact_id"):
                if not impl.get(key): raise ProtocolError(f"delegated_missing:{key}")
            if impl["delegate_id"] not in {d["delegate_id"] for d in boot["bootstrap"].get("delegates", [])}:
                raise ProtocolError("delegate_not_declared")
        if mode == "skip":
            if not e.get("reason") or not e.get("preconditions") or not e.get("invariants"):
                raise ProtocolError("skip_contract_missing")
            if e["evidence"] == "measured" and not impl.get("independent_measurement_refs"):
                raise ProtocolError("skip_measured_without_independent_evidence")
        payload = e["payload"]; pk = payload["payload_kind"]
        if pk not in PAYLOAD_KEYS: raise ProtocolError(f"unknown_payload:{pk}")
        if set(payload) - PAYLOAD_KEYS[pk]: raise ProtocolError(f"untyped_payload:{pk}")
        if pk == "context_selection": _check_parent_refs(payload)
        if pk == "feedback" and "feedback_consumers" in payload:
            consumers = payload["feedback_consumers"]
            if not isinstance(consumers, list) or len(set(consumers)) != len(consumers):
                raise ProtocolError("feedback_consumers_must_be_unique")
        if pk == "execution":
            if payload["execution_mode"] == "replay":
                if not payload.get("replay_kind") or not payload.get("source_trace_ids") or payload.get("new_execution") is not False:
                    raise ProtocolError("replay_execution_contract")
            elif payload.get("replay_kind") or payload.get("source_trace_ids"):
                raise ProtocolError("online_replay_fields")
        if pk == "study_evaluation" and payload.get("evaluation_completeness") == "heldout":
            raise ProtocolError("study_payload_claims_heldout")
        producer_role = e["producer"]["role"]
        if pk == "deployment_fact" and producer_role not in {"framework", "deployer", "recorder"}:
            raise ProtocolError("method_forged_deployment")
        if pk == "selection_result" and producer_role not in {"framework", "method", "meta_agent", "delegate", "recorder"}:
            raise ProtocolError("selection_producer")
        if pk == "study_evaluation" and producer_role not in {"framework", "evaluator", "recorder", "delegate"}:
            raise ProtocolError("study_score_authority")
        for a in e.get("artifacts", []) + e.get("output_artifacts", []):
            if a["kind"] == "heldout_score":
                if a["producer"]["role"] not in {"framework", "evaluator", "recorder", "delegate"}:
                    raise ProtocolError("heldout_producer")
                if a["visibility"] != "heldout_private" or a.get("score_kind") != "heldout":
                    raise ProtocolError("heldout_visibility_or_kind")
            if a["kind"] == "candidate":
                root, parents = a.get("root") is True, a.get("parents", [])
                if root == bool(parents): raise ProtocolError("candidate_root_parent_contradiction")
                if a.get("lineage") and {x["parent_id"] for x in a["lineage"]} - set(parents):
                    raise ProtocolError("lineage_parent_mismatch")
                if any(x.get("role") == "crossover" for x in a.get("lineage", [])) and len(parents) < 2:
                    raise ProtocolError("crossover_requires_multiple_parents")
        if stage["id"] in {"organize_feedback", "propose_changes", "select_deploy"}:
            for a in e.get("input_artifacts", []):
                chain = {a["artifact_id"]} | _ancestors(a["artifact_id"], arts)
                if any(arts.get(x, {}).get("kind") == "heldout_score" for x in chain):
                    raise ProtocolError("heldout_taint_to_adaptation")
    return True
