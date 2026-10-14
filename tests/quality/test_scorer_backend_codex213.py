"""Synthetic API composition only; no backend, dataset, model or scorer runs."""
from __future__ import annotations

import copy
import inspect
import json

import pytest

from eval import lifecycle_receipt as lifecycle, runner_admission, scorer_admission
from eval import scorer_backend as backend
from lifecycle_fixtures_codex177 import attest, gate_facts
# Reuse the public-API inert bundle/export fixture and its execution/socket guards.
from test_scorer_admission_codex173 import example, offline_only


@pytest.fixture
def request_inputs(example):
    _, contract, arguments = example
    binding = dict(adapter_id="synthetic-adapter-213", run_id=arguments["run_id"],
                   trial_id="synthetic-trial-213", manifest_sha256="c" * 64)
    checkpoint = lifecycle.start_lifecycle(binding, "a" * 64)
    checkpoint = lifecycle.transition(checkpoint, "admit", gate_facts(binding, "admit"))
    checkpoint = lifecycle.transition(checkpoint, "execute", attest(
        binding, "execute", dict(exit_code=0, oom_killed=False, timed_out=False)))
    checkpoint = lifecycle.transition(checkpoint, "quiesce", attest(
        binding, "quiesce", dict(exit_code=0, oom_killed=False, timed_out=False, running=False)))
    enforcement = gate_facts(binding, "admit")
    enforcement["policy"]["filesystems"] = copy.deepcopy(contract["quota"])
    enforcement["observed"]["filesystems"] = {
        path: dict(**limits, backend="tmpfs", scope_id=f"synthetic-quota-213-{index}",
                   evidence_sha256="d" * 64)
        for index, (path, limits) in enumerate(contract["quota"].items())}
    return dict(binding=binding, scope_sha256="a" * 64, lifecycle_receipt=checkpoint,
                **{key: value for key, value in arguments.items() if key != "run_id"},
                runtime_policy=copy.deepcopy(enforcement["policy"]),
                runtime_policy_sha256=lifecycle.digest(enforcement["policy"]),
                runtime_observed=copy.deepcopy(enforcement["observed"]))


def refused(arguments, stage, status):
    before = copy.deepcopy(arguments)
    with pytest.raises(backend.ScorerBackendError) as error:
        backend.check_backend(**arguments)
    suffix = "evidence_unavailable" if status == "unknown" else "contract_refused"
    assert isinstance(error.value, scorer_admission.AdmissionError)
    assert error.value.code == f"{stage}_{suffix}"
    assert error.value.receipt == dict(
        schema=backend.SCHEMA, stage=stage, status=status, measured=False,
        production_authorized=False, execution_authorized=False, publication_ready=False,
        reason=error.value.code)
    assert str(error.value) == error.value.code
    assert arguments == before
    return error.value.receipt


def test_public_surface_requires_all_independent_inputs():
    assert backend.__all__ == ("ScorerBackendError", "check_backend")
    parameters = inspect.signature(backend.check_backend).parameters
    assert set(parameters) == {
        "binding", "scope_sha256", "lifecycle_receipt", "bundle_raw", "bundle_sha256",
        "contract_raw", "contract_sha256", "closure_root", "artifact_root", "export_receipt",
        "info", "runtime_policy", "runtime_policy_sha256", "runtime_observed"}
    assert all(p.kind == inspect.Parameter.KEYWORD_ONLY and p.default is inspect.Parameter.empty
               for p in parameters.values())


def test_composes_real_checks_without_mutation_execution_or_lifecycle_progress(request_inputs,
                                                                             monkeypatch):
    before = copy.deepcopy(request_inputs)

    def refuse(*args, **kwargs):
        pytest.fail("preflight attempted export writes or lifecycle progress")

    monkeypatch.setattr(scorer_admission, "export_state", refuse)
    monkeypatch.setattr(lifecycle, "transition", refuse)
    checked = backend.check_backend(**request_inputs)
    scorer_arguments = {key: request_inputs[key] for key in (
        "bundle_raw", "bundle_sha256", "contract_raw", "contract_sha256", "closure_root",
        "artifact_root", "export_receipt", "info")}
    scorer_arguments["run_id"] = request_inputs["binding"]["run_id"]
    assert checked == dict(
        schema=backend.SCHEMA, stage="preflight", status="passed", measured=False,
        production_authorized=False, execution_authorized=False, publication_ready=False,
        binding=request_inputs["binding"], scope_sha256=request_inputs["scope_sha256"],
        evidence=dict(lifecycle_sha256=lifecycle.digest(request_inputs["lifecycle_receipt"]),
                      export_sha256=lifecycle.digest(request_inputs["export_receipt"]),
                      scorer=scorer_admission.admit_runtime(**scorer_arguments),
                      resources=runner_admission.admit_runtime(
                          request_inputs["binding"], request_inputs["runtime_policy"],
                          request_inputs["runtime_observed"])))
    assert checked["evidence"]["resources"]["policy_sha256"] == request_inputs["runtime_policy_sha256"]
    assert request_inputs == before
    assert json.loads(json.dumps(checked)) == checked
    assert "answer.txt" not in json.dumps(checked)
    assert str(request_inputs["artifact_root"]) not in json.dumps(checked)
    assert request_inputs["lifecycle_receipt"]["state"] == "quiesce"
    checked["binding"]["run_id"] = "mutated-output"
    assert request_inputs == before


@pytest.mark.parametrize("key,stage", [
    ("lifecycle_receipt", "lifecycle"), ("runtime_policy", "resources"),
    ("runtime_observed", "resources"), ("export_receipt", "scorer"), ("info", "scorer")])
def test_absent_evidence_stays_unknown(request_inputs, key, stage):
    request_inputs[key] = None
    refused(request_inputs, stage, "unknown")


@pytest.mark.parametrize("key", ["adapter_id", "run_id", "trial_id", "manifest_sha256"])
def test_expected_binding_cannot_be_taken_from_incoming_checkpoint(request_inputs, key):
    request_inputs["binding"][key] = "f" * 64 if key == "manifest_sha256" else "different-213"
    refused(request_inputs, "lifecycle", "blocked")


def test_scope_pin_is_independent(request_inputs):
    request_inputs["scope_sha256"] = "f" * 64
    refused(request_inputs, "lifecycle", "blocked")


@pytest.mark.parametrize("stage", ["scope", "admit", "execute"])
def test_only_quiesced_checkpoint_can_reach_file_checks(request_inputs, stage, monkeypatch):
    def refuse(**kwargs):
        pytest.fail("unquiesced checkpoint reached artifact checks")

    monkeypatch.setattr(scorer_admission, "admit_runtime", refuse)
    checkpoint = lifecycle.start_lifecycle(request_inputs["binding"], request_inputs["scope_sha256"])
    for event in request_inputs["lifecycle_receipt"]["events"]:
        if checkpoint["state"] == stage:
            break
        checkpoint = lifecycle.transition(checkpoint, event["stage"], event["evidence"])
    request_inputs["lifecycle_receipt"] = checkpoint
    refused(request_inputs, "lifecycle", "blocked")


@pytest.mark.parametrize("status", ["failed", "unknown"])
def test_nonpassing_quiescence_is_never_accepted(request_inputs, status):
    checkpoint = lifecycle.start_lifecycle(request_inputs["binding"], request_inputs["scope_sha256"])
    for event in request_inputs["lifecycle_receipt"]["events"][:-1]:
        checkpoint = lifecycle.transition(checkpoint, event["stage"], event["evidence"])
    request_inputs["lifecycle_receipt"] = lifecycle.transition(
        checkpoint, "quiesce", attest(request_inputs["binding"], "quiesce", status=status))
    refused(request_inputs, "lifecycle", "blocked")


def test_lifecycle_is_replayed_rather_than_trusting_derived_status(request_inputs):
    request_inputs["lifecycle_receipt"]["events"][-1]["evidence"]["facts"]["running"] = True
    refused(request_inputs, "lifecycle", "blocked")


@pytest.mark.parametrize("change", ["policy_pin", "binding", "resources", "filesystem", "backend"])
def test_resource_gate_and_external_policy_pin_are_required(request_inputs, change):
    observed = request_inputs["runtime_observed"]
    if change == "policy_pin":
        request_inputs["runtime_policy_sha256"] = "f" * 64
    elif change == "binding":
        observed["binding"]["trial_id"] = "different-trial-213"
    elif change == "resources":
        observed["resources"]["pids"] += 1
    elif change == "filesystem":
        observed["filesystems"]["/tmp"]["inodes"] += 1
    else:
        observed["resource_backend"] = "unknown"
    refused(request_inputs, "resources", "blocked")


def test_separately_valid_resource_policy_must_match_artifact_quota(request_inputs):
    # runner_admission alone permits this empty filesystem policy; composition
    # must still require the task contract's /tmp hard byte AND inode limits.
    request_inputs["runtime_policy"]["filesystems"] = {}
    request_inputs["runtime_observed"]["filesystems"] = {}
    request_inputs["runtime_policy_sha256"] = lifecycle.digest(request_inputs["runtime_policy"])
    assert runner_admission.admit_runtime(request_inputs["binding"], request_inputs["runtime_policy"],
                                         request_inputs["runtime_observed"])["status"] == "passed"
    refused(request_inputs, "resources", "blocked")


@pytest.mark.parametrize("key,stage", [("contract_sha256", "resources"), ("bundle_sha256", "scorer")])
def test_bundle_and_contract_pins_remain_independent(request_inputs, key, stage):
    request_inputs[key] = "f" * 64
    refused(request_inputs, stage, "blocked")


def test_export_receipt_must_match_this_run(request_inputs):
    request_inputs["export_receipt"]["run_id"] = "different-run-213"
    refused(request_inputs, "scorer", "blocked")


def test_runtime_observation_must_be_complete(request_inputs):
    request_inputs["info"] = {}
    refused(request_inputs, "scorer", "unknown")


@pytest.mark.parametrize("root,name", [("artifact_root", "answer.txt"), ("closure_root", "check.txt")])
def test_pass_never_caches_local_bytes(request_inputs, root, name):
    assert backend.check_backend(**request_inputs)["status"] == "passed"
    target = request_inputs[root] / name
    target.write_bytes(b"x" * target.stat().st_size)
    refused(request_inputs, "scorer", "blocked")


@pytest.mark.parametrize("root", ["artifact_root", "closure_root"])
def test_unavailable_projection_is_unknown_after_prior_pass(request_inputs, root):
    assert backend.check_backend(**request_inputs)["status"] == "passed"
    path = request_inputs[root]
    path.rename(path.with_name(path.name + "-unavailable-213"))
    refused(request_inputs, "scorer", "unknown")
