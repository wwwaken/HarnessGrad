"""Proposed docs contract only; authored fixtures, no runner/scorer/runtime imports.

The semantic oracle below is test-only specification, not a production validator.
Task 237 authors these tests without executing them or any benchmark.
"""
from copy import deepcopy
import json
from pathlib import Path
import re

import jsonschema
import pytest


ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "docs" / "task-237-ordinary-run-receipt.md"
SCHEMA = ROOT / "docs" / "task-237-ordinary-run-receipt.schema.json"
STAGED_SCHEMA = ROOT / "eval" / "diagnostic_receipt.schema.json"


def example():
    blocks = re.findall(r"^```json\n(.*?)\n```", PAGE.read_text(encoding="utf-8"), re.M | re.S)
    assert len(blocks) == 1, "Keep one unambiguous illustrative receipt on the page"
    return json.loads(blocks[0])


@pytest.fixture(scope="module")
def validator():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(schema)


def assert_semantics(receipt, validator):
    """Reference checks that JSON Schema alone cannot express; no external facts."""
    json.dumps(receipt, allow_nan=False)
    validator.validate(receipt)
    assert type(receipt["trials"]) is int
    count = receipt["trials"]
    selected = receipt["selected_task_ids"]
    planned = {(task, trial) for task in selected for trial in range(1, count + 1)}
    actual = [(row["task_id"], row["trial"]) for row in receipt["outcomes"]]
    assert len(actual) == len(set(actual)), "Duplicate task/trial cell"
    assert set(actual) == planned, "Every selected task/trial needs exactly one outcome"
    for row in receipt["outcomes"]:
        assert type(row["trial"]) is int
        if row["status"] == "measured":
            assert type(row["score"]) in (int, float)

    coverage = receipt["coverage"]
    for key, value in coverage.items():
        assert type(value) is int or (key == "eligible_tasks" and value is None)
    assert coverage["selected_tasks"] == len(selected)
    assert coverage["expected_task_trials"] == len(planned)
    eligible = coverage["eligible_tasks"]
    assert eligible is None or eligible >= len(selected)
    for state in ("measured", "invalid", "unmeasured"):
        assert coverage[f"{state}_trials"] == sum(
            row["status"] == state for row in receipt["outcomes"])

    for value in receipt["filesystem_quota"]["requested"].values():
        assert value is None or type(value) is int
    for boundary in receipt["sandbox"].values():
        assert boundary["plan_version"] is None or type(boundary["plan_version"]) is int

    lifecycle = (receipt["cleanup"]["status"], receipt["snapshot"]["status"])
    if coverage["invalid_trials"] or "failed" in lifecycle:
        expected_status = "invalid"
    elif coverage["unmeasured_trials"] or "unknown" in lifecycle:
        expected_status = "unmeasured"
    else:
        expected_status = "measured"
    assert receipt["status"] == expected_status, "Failure precedence must survive aggregation"
    if expected_status == "measured":
        assert type(receipt["score"]) in (int, float)
        assert receipt["score"] == sum(row["score"] for row in receipt["outcomes"]) / len(planned)
    else:
        assert receipt["score"] is None


def local_zero():
    """Authored measured-zero shape, never an observed run or actual scorer result."""
    receipt = example()
    receipt["status"] = "measured"
    receipt["score"] = 0.0
    receipt["outcomes"][0].update(status="measured", score=0.0, reason=None)
    receipt["coverage"].update(measured_trials=1, unmeasured_trials=0)
    receipt["cleanup"].update(status="passed", detail="Authored local absence observation shape.")
    return receipt


def test_documented_example_is_unmeasured_and_explicitly_illustrative(validator):
    receipt = example()
    assert_semantics(receipt, validator)
    assert receipt["record_origin"] == "illustrative"
    assert receipt["score"] is None
    assert receipt["endpoint"] is None
    assert all(value is None for value in receipt["hashes"].values())
    assert receipt["coverage"]["unmeasured_trials"] == 1


@pytest.mark.parametrize("quota", [False, "unknown"])
@pytest.mark.parametrize("score", [0, 0.25, 1])
def test_local_measurement_does_not_require_quota_administration_or_authorize_production(
    validator, quota, score
):
    receipt = local_zero()
    receipt["filesystem_quota"].update(enforced=quota, detail="Authored uncovered/unknown quota shape.")
    receipt["score"] = receipt["outcomes"][0]["score"] = score
    assert_semantics(receipt, validator)
    assert receipt["label"] == "NON-PRODUCTION ORDINARY RUN — NOT FORMAL BENCHMARK EVIDENCE"
    assert all(receipt[key] is False for key in (
        "production_authorized", "formal_benchmark_evidence", "publication_ready"))
    assert receipt["metric"]["official_equivalence"] == "unverified"
    assert receipt["record_origin"] == "illustrative"


@pytest.mark.parametrize("value", [True, None, 0, 1, "false", "true", "", {}])
def test_quota_values_are_not_truthiness_coerced(validator, value):
    receipt = example()
    receipt["filesystem_quota"]["enforced"] = value
    assert not validator.is_valid(receipt)


@pytest.mark.parametrize("field,value", [
    ("production_authorized", True), ("production_authorized", 0),
    ("formal_benchmark_evidence", True), ("publication_ready", True),
    ("schema", "harnessgrad.diagnostic-receipt.v2"), ("run_kind", "diagnostic"),
    ("evidence_class", "formal"), ("label", "Benchmark score"),
])
def test_ordinary_receipts_cannot_claim_formal_identity(validator, field, value):
    receipt = local_zero()
    receipt[field] = value
    assert not validator.is_valid(receipt)


def test_required_limitation_and_identity_fields_cannot_be_omitted(validator):
    receipt = example()
    schema = validator.schema
    for key in schema["required"]:
        changed = deepcopy(receipt)
        del changed[key]
        assert not validator.is_valid(changed), key
    for key in receipt["metric"]:
        changed = deepcopy(receipt)
        del changed["metric"][key]
        assert not validator.is_valid(changed), key
    changed = deepcopy(receipt)
    changed["filesystem_quota"]["enforced"] = False
    del changed["filesystem_quota"]["detail"]
    assert not validator.is_valid(changed)


@pytest.mark.parametrize("key,value", [
    ("id", " "), ("unit", ""), ("direction", "unknown"),
    ("aggregation", "measured_subset_mean"), ("official_equivalence", "official"),
    ("scorer_sha256", "unknown"), ("scorer_sha256", "a" * 63),
])
def test_metric_identity_is_explicit_even_without_a_score(validator, key, value):
    receipt = example()
    receipt["metric"][key] = value
    assert not validator.is_valid(receipt)


@pytest.mark.parametrize("part", ["host", "task"])
@pytest.mark.parametrize("requested,effective", [
    ("bwrap", "bwrap"), ("bwrap", "unknown"),
    ("container", "container"), ("container", "unknown"),
    ("none", "none"), ("unknown", "unknown"),
])
def test_requested_sandbox_is_separate_from_observation(validator, part, requested, effective):
    receipt = example()
    receipt["sandbox"][part].update(requested=requested, effective=effective)
    assert_semantics(receipt, validator)
    assert receipt["filesystem_quota"]["enforced"] == "unknown"
    assert receipt["formal_benchmark_evidence"] is False


def test_host_bwrap_and_task_container_are_distinct_facts(validator):
    receipt = example()
    receipt["sandbox"]["host"].update(requested="bwrap", effective="bwrap", plan_version=2)
    receipt["sandbox"]["task"].update(requested="container", effective="container")
    assert_semantics(receipt, validator)
    assert receipt["production_authorized"] is False


@pytest.mark.parametrize("effective", ["none", "container"])
def test_requested_boundary_cannot_silently_change(validator, effective):
    receipt = example()
    receipt["sandbox"]["host"].update(requested="bwrap", effective=effective)
    assert not validator.is_valid(receipt)


@pytest.mark.parametrize("state", ["invalid", "unmeasured"])
@pytest.mark.parametrize("score,reason", [(0, "Failure"), (None, None), (None, " ")])
def test_non_measurements_require_null_scores_and_meaningful_reasons(validator, state, score, reason):
    receipt = example()
    receipt["outcomes"][0].update(status=state, score=score, reason=reason)
    assert not validator.is_valid(receipt)


@pytest.mark.parametrize("stage,state,expected", [
    ("cleanup", "failed", "invalid"), ("cleanup", "unknown", "unmeasured"),
    ("snapshot", "failed", "invalid"), ("snapshot", "unknown", "unmeasured"),
])
def test_lifecycle_failure_withholds_aggregate_even_with_local_measured_zero(
    validator, stage, state, expected
):
    receipt = local_zero()
    receipt[stage].update(status=state, detail="Authored lifecycle failure/uncertainty shape.")
    receipt.update(status=expected, score=None)
    assert_semantics(receipt, validator)
    assert receipt["outcomes"][0]["score"] == 0.0
    incorrect = deepcopy(receipt)
    incorrect.update(status="measured", score=0.0)
    assert not validator.is_valid(incorrect)


@pytest.mark.parametrize("snapshot", ["passed", "not_required"])
def test_only_completed_or_genuinely_unplanned_snapshot_allows_local_aggregate(validator, snapshot):
    receipt = local_zero()
    receipt["snapshot"]["status"] = snapshot
    assert_semantics(receipt, validator)
    receipt["cleanup"]["status"] = "not_required"
    assert not validator.is_valid(receipt)


def test_task_trial_partition_preserves_invalid_unmeasured_and_zero(validator):
    receipt = example()
    receipt["trials"] = 3
    task = receipt["selected_task_ids"][0]
    receipt["outcomes"] = [
        dict(task_id=task, trial=1, status="measured", score=0, reason=None),
        dict(task_id=task, trial=2, status="invalid", score=None, reason="Observed timeout"),
        dict(task_id=task, trial=3, status="unmeasured", score=None, reason="Scorer unavailable"),
    ]
    receipt["coverage"].update(expected_task_trials=3, measured_trials=1, invalid_trials=1)
    receipt.update(status="invalid", score=None)
    assert_semantics(receipt, validator)
    wrong_precedence = deepcopy(receipt)
    wrong_precedence["status"] = "unmeasured"
    with pytest.raises(AssertionError, match="Failure precedence"):
        assert_semantics(wrong_precedence, validator)
    receipt["score"] = 0
    assert not validator.is_valid(receipt)


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "unselected", "wrong_trial", "counts", "eligible"])
def test_shape_valid_coverage_errors_still_fail_semantic_contract(validator, mutation):
    receipt = example()
    if mutation == "missing":
        receipt["trials"] = 2
        receipt["coverage"].update(expected_task_trials=2, unmeasured_trials=2)
    elif mutation == "duplicate":
        receipt["outcomes"].append(deepcopy(receipt["outcomes"][0]))
    elif mutation == "unselected":
        receipt["outcomes"][0]["task_id"] = "unselected-illustrative-cell"
    elif mutation == "wrong_trial":
        receipt["outcomes"][0]["trial"] = 2
    elif mutation == "counts":
        receipt["coverage"]["unmeasured_trials"] = 0
    else:
        receipt["coverage"]["eligible_tasks"] = 0
    assert validator.is_valid(receipt), "This case must exercise the semantic layer"
    with pytest.raises(AssertionError):
        assert_semantics(receipt, validator)


def test_mean_uses_every_planned_trial_and_cannot_be_arbitrarily_changed(validator):
    receipt = local_zero()
    receipt["trials"] = 2
    row = deepcopy(receipt["outcomes"][0])
    row.update(trial=2, score=1)
    receipt["outcomes"].append(row)
    receipt["coverage"].update(expected_task_trials=2, measured_trials=2)
    receipt["score"] = 0.5
    assert_semantics(receipt, validator)
    receipt["score"] = 1
    assert validator.is_valid(receipt)
    with pytest.raises(AssertionError):
        assert_semantics(receipt, validator)


@pytest.mark.parametrize("value", [True, float("nan"), float("inf"), float("-inf")])
def test_boolean_and_nonfinite_values_are_not_local_scores(validator, value):
    receipt = local_zero()
    receipt["score"] = receipt["outcomes"][0]["score"] = value
    with pytest.raises((AssertionError, ValueError, jsonschema.ValidationError)):
        assert_semantics(receipt, validator)


@pytest.mark.parametrize("location", ["trials", "coverage", "outcome", "quota", "plan_version"])
def test_integral_float_encodings_do_not_pass_the_semantic_contract(validator, location):
    receipt = example()
    if location == "trials":
        receipt["trials"] = 1.0
    elif location == "coverage":
        receipt["coverage"]["selected_tasks"] = 1.0
    elif location == "outcome":
        receipt["outcomes"][0]["trial"] = 1.0
    elif location == "quota":
        receipt["filesystem_quota"]["requested"]["bytes"] = 1.0
    else:
        receipt["sandbox"]["host"]["plan_version"] = 1.0
    assert validator.is_valid(receipt), "JSON Schema accepts mathematically integral numbers"
    with pytest.raises(AssertionError):
        assert_semantics(receipt, validator)


def test_unknown_provenance_does_not_become_false_hashes_or_formal_evidence(validator):
    receipt = local_zero()
    assert_semantics(receipt, validator)
    receipt["hashes"]["model"] = "unknown"
    assert not validator.is_valid(receipt)
    receipt["hashes"]["model"] = "a" * 64
    assert_semantics(receipt, validator)
    assert receipt["formal_benchmark_evidence"] is False


def test_payloads_and_unreviewed_extensions_are_not_metadata(validator):
    receipt = example()
    receipt["task_payload"] = "Authored placeholder, not dataset content"
    assert not validator.is_valid(receipt)
    del receipt["task_payload"]
    receipt["filesystem_quota"]["preflight_only"] = True
    assert not validator.is_valid(receipt)


def test_ordinary_discriminator_is_rejected_by_existing_staged_schema(validator):
    staged = json.loads(STAGED_SCHEMA.read_text(encoding="utf-8"))
    assert not jsonschema.Draft202012Validator(staged).is_valid(example())
    # Use only the existing discriminator constraint: no diagnostic producer import.
    existing_identity = jsonschema.Draft202012Validator(staged["properties"]["schema"])
    assert not existing_identity.is_valid(example()["schema"])
    assert not validator.is_valid({**example(), "schema": staged["properties"]["schema"]["const"]})


def test_documentation_links_resolve_within_this_worktree():
    for target in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", PAGE.read_text(encoding="utf-8")):
        resolved = (PAGE.parent / target).resolve()
        assert resolved.is_relative_to(ROOT.resolve()), target
        assert resolved.is_file(), target
