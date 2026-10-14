"""Public API contracts using inert bytes and fabricated observations only."""
from __future__ import annotations

import copy
import hashlib
import inspect
import json
from pathlib import Path
import socket
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from eval.admission import artifact_admission as artifacts
from eval.admission import scorer_admission as admission
from eval.admission import scorer_bundle as bundles
from eval.admission.pilot_admission import AdmissionError, LOG_CONFIG


@pytest.fixture(autouse=True)
def offline_only(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError("synthetic API contract attempted execution or network")
    monkeypatch.setattr(subprocess, "run", refuse)
    monkeypatch.setattr(subprocess, "Popen", refuse)
    monkeypatch.setattr(socket, "socket", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)


def seal(contract):
    raw = json.dumps(contract, sort_keys=True).encode()
    return raw, hashlib.sha256(raw).hexdigest()


@pytest.fixture
def example(tmp_path):
    closure, source, artifact = (tmp_path / name for name in ("closure", "source", "artifact"))
    closure.mkdir()
    source.mkdir()
    rows = []
    for name, role, requires in (("check.txt", "scorer", ["runtime.txt"]),
                                 ("runtime.txt", "runtime", [])):
        data = f"inert synthetic {role} bytes\n".encode()
        (closure / name).write_bytes(data)
        if role == "runtime":
            (closure / name).chmod(0o755)
        rows.append(dict(path=name, role=role, requires=requires, bytes=len(data),
                         sha256=hashlib.sha256(data).hexdigest()))
    (source / "answer.txt").write_bytes(b"answer")
    # Export must remain selected-only even through the facade.
    (source / "unselected-link").symlink_to("missing")
    manifest = dict(schema=bundles.SCHEMA, source_sha256="a" * 64,
                    runtime_image_id="sha256:" + "b" * 64, network="none",
                    scorer=dict(entrypoint="check.txt", files=rows,
                                argv=["/control-scorer/runtime.txt", "/control-scorer/check.txt"]))
    contract = dict(schema="harnessgrad.artifact-scorer.v1", task_id="synthetic-task-173",
                    source_sha256=manifest["source_sha256"],
                    runtime_image_id=manifest["runtime_image_id"], scorer=copy.deepcopy(manifest["scorer"]),
                    export=dict(files=[dict(path="answer.txt", max_bytes=8)], max_bytes=8, max_inodes=2),
                    quota={"/tmp": dict(bytes=4096, inodes=8)})
    bundle_raw, bundle_pin = admission.seal_bundle(manifest)
    contract_raw, contract_pin = seal(contract)
    exported = admission.export_state(source, artifact, contract_raw, contract_pin,
                                      run_id="synthetic-run-173")
    info = dict(Image=contract["runtime_image_id"], State=dict(Status="created", Running=False),
                Config=dict(Volumes={}, User=artifacts.scorer_user(), Entrypoint=contract["scorer"]["argv"][:1],
                            Cmd=contract["scorer"]["argv"][1:], Env=list(artifacts.SCORER_ENV),
                            WorkingDir="/tmp"), NetworkSettings=dict(Networks={"none": {}}),
                HostConfig=dict(NetworkMode="none", ReadonlyRootfs=True, Privileged=False,
                                CapDrop=["ALL"], SecurityOpt=["no-new-privileges"],
                                LogConfig=copy.deepcopy(LOG_CONFIG),
                                Tmpfs=admission.runtime_tmpfs(contract_raw, contract_pin)),
                Mounts=[dict(Type="bind", Source=str(root), Destination=target, RW=False)
                        for root, target in ((artifact, "/control-input"), (closure, "/control-scorer"))])
    arguments = dict(bundle_raw=bundle_raw, bundle_sha256=bundle_pin,
                     contract_raw=contract_raw, contract_sha256=contract_pin,
                     closure_root=closure, artifact_root=artifact, export_receipt=exported,
                     info=info, run_id="synthetic-run-173")
    return manifest, contract, arguments


def bundle_arguments(arguments):
    return {key: arguments[key] for key in ("closure_root", "bundle_raw", "bundle_sha256")}


def refused(check, arguments, stage, status):
    before = copy.deepcopy(arguments)
    with pytest.raises(admission.ScorerAdmissionError) as error:
        check(**arguments)
    receipt = error.value.receipt
    suffix = "contract_refused" if status == "blocked" else "evidence_unavailable"
    assert isinstance(error.value, AdmissionError)
    assert receipt == dict(schema="harnessgrad.scorer-admission.v1", stage=stage, status=status,
                           measured=False, production_authorized=False,
                           reason=f"{stage}_{suffix}")
    assert error.value.code == receipt["reason"]
    assert arguments == before
    assert "evidence" not in receipt and "score" not in receipt
    return receipt


def test_public_surface_and_separate_required_trust_inputs():
    assert set(admission.__all__) == {
        "AdmissionError", "EvidenceUnavailable", "ScorerAdmissionError", "seal_bundle", "load_bundle",
        "load_contract", "export_state", "verify_state_export", "runtime_tmpfs",
        "validate_bundle", "admit_runtime",
    }
    parameters = inspect.signature(admission.admit_runtime).parameters
    assert set(parameters) == {"bundle_raw", "bundle_sha256", "contract_raw", "contract_sha256",
                               "closure_root", "artifact_root", "export_receipt", "info", "run_id"}
    assert all(p.kind == inspect.Parameter.KEYWORD_ONLY and p.default == inspect.Parameter.empty
               for p in parameters.values())
    assert admission.AdmissionError is AdmissionError
    assert admission.EvidenceUnavailable is artifacts.EvidenceUnavailable
    assert admission.seal_bundle is bundles.seal_bundle
    assert admission.load_contract is artifacts.load_contract


def test_bundle_receipt_is_stable_task_independent_and_scoped(example):
    manifest, _, arguments = example
    kwargs = bundle_arguments(arguments)
    before = copy.deepcopy(kwargs)
    receipt = admission.validate_bundle(**kwargs)
    assert receipt == admission.validate_bundle(**kwargs)
    assert receipt == dict(schema="harnessgrad.scorer-admission.v1", stage="bundle", status="passed",
                           measured=False, production_authorized=False,
                           evidence=bundles.verify_bundle(arguments["closure_root"],
                                                          arguments["bundle_raw"], arguments["bundle_sha256"]))
    assert "task_id" not in receipt["evidence"] and "score" not in receipt
    assert receipt["evidence"]["scope"] == "local_declared_closure_integrity"
    assert admission.load_bundle(arguments["bundle_raw"], arguments["bundle_sha256"]) == manifest
    assert kwargs == before
    assert json.loads(json.dumps(receipt)) == receipt


def test_runtime_receipt_keeps_both_pins_and_legacy_scope_without_authorization(example, monkeypatch):
    _, contract, arguments = example
    before = copy.deepcopy(arguments)
    legacy = artifacts.require_artifact_runtime(arguments["info"], arguments["contract_raw"],
                arguments["contract_sha256"], artifact_root=arguments["artifact_root"],
                closure_root=arguments["closure_root"], export_receipt=arguments["export_receipt"],
                run_id=arguments["run_id"])
    verify_files = artifacts.verify_scorer_files
    checked = []

    def record(root, spec):
        checked.append(root)
        return verify_files(root, spec)

    monkeypatch.setattr(artifacts, "verify_scorer_files", record)
    monkeypatch.setattr(bundles, "verify_scorer_files", record)
    receipt = admission.admit_runtime(**arguments)
    assert checked == [arguments["closure_root"]]
    assert receipt["status"] == "passed"
    assert receipt["measured"] is False and receipt["production_authorized"] is False
    assert receipt["evidence"]["runtime"] == legacy
    assert receipt["evidence"]["runtime"]["task_id"] == contract["task_id"]
    assert receipt["evidence"]["runtime"]["contract_sha256"] == arguments["contract_sha256"]
    assert receipt["evidence"]["bundle"]["bundle_sha256"] == arguments["bundle_sha256"]
    assert receipt["evidence"]["bundle"]["bundle_sha256"] != arguments["contract_sha256"]
    assert receipt["evidence"]["run_id"] == arguments["run_id"]
    assert receipt["evidence"]["runtime"]["scope"] == "inspected_runtime_contract"
    assert arguments == before
    assert json.loads(json.dumps(receipt)) == receipt


@pytest.mark.parametrize("key", ["bundle_sha256", "contract_sha256"])
def test_each_external_pin_is_required_independently(example, key, monkeypatch):
    _, _, arguments = example
    arguments[key] = "c" * 64
    monkeypatch.setattr(artifacts, "_inventory", lambda *_: pytest.fail("invalid pin read local bytes"))
    refused(admission.admit_runtime, arguments, "runtime", "blocked")


@pytest.mark.parametrize("change", ["source_sha256", "runtime_image_id", "scorer"])
def test_individually_valid_but_unrelated_declarations_are_blocked_before_file_access(example, change,
                                                                                       monkeypatch):
    _, contract, arguments = example
    if change == "source_sha256":
        contract[change] = "d" * 64
    elif change == "runtime_image_id":
        contract[change] = "sha256:" + "d" * 64
    else:
        contract["scorer"]["argv"].append("--different-synthetic-command")
    arguments["contract_raw"], arguments["contract_sha256"] = seal(contract)
    monkeypatch.setattr(artifacts, "_inventory", lambda *_: pytest.fail("unrelated declarations read bytes"))
    refused(admission.admit_runtime, arguments, "runtime", "blocked")


@pytest.mark.parametrize("change", ["quota", "export"])
def test_task_policy_stays_independent_of_bundle_identity(example, change):
    _, contract, arguments = example
    if change == "quota":
        contract["quota"]["/tmp"]["bytes"] = 8192
    else:
        contract["export"]["max_bytes"] = 16
    arguments["contract_raw"], arguments["contract_sha256"] = seal(contract)
    assert admission.validate_bundle(**bundle_arguments(arguments))["status"] == "passed"
    refused(admission.admit_runtime, arguments, "runtime", "blocked")


def test_same_bundle_serves_another_task_with_fresh_projection(example, tmp_path):
    _, contract, arguments = example
    pin = arguments["bundle_sha256"]
    contract["task_id"] = "another-synthetic-task-173"
    contract["export"]["max_bytes"] = 16
    arguments["contract_raw"], arguments["contract_sha256"] = seal(contract)
    arguments["artifact_root"] = tmp_path / "another-artifact"
    arguments["run_id"] = "another-synthetic-run-173"
    arguments["export_receipt"] = admission.export_state(tmp_path / "source", arguments["artifact_root"],
                arguments["contract_raw"], arguments["contract_sha256"], run_id=arguments["run_id"])
    arguments["info"]["Mounts"][0]["Source"] = str(arguments["artifact_root"])
    receipt = admission.admit_runtime(**arguments)
    assert receipt["evidence"]["bundle"]["bundle_sha256"] == pin
    assert receipt["evidence"]["runtime"]["task_id"] == contract["task_id"]
    assert list(arguments["artifact_root"].iterdir()) == [arguments["artifact_root"] / "answer.txt"]


@pytest.mark.parametrize("key,value", [("info", None), ("info", {}),
                                      ("export_receipt", None), ("export_receipt", {})])
def test_missing_or_incomplete_observer_evidence_remains_unknown(example, key, value):
    _, _, arguments = example
    arguments[key] = value
    refused(admission.admit_runtime, arguments, "runtime", "unknown")


@pytest.mark.parametrize("state,status", [
    (dict(Status="exited", Running=False), "blocked"),
    (dict(Running=False), "unknown"),
    (dict(Status="created"), "unknown"),
])
def test_pristine_scorer_requires_created_and_not_running_observation(example, state, status):
    # Task 220: a stopped runtime is not the required created-state observation.
    _, _, arguments = example
    arguments["info"]["State"] = state
    refused(admission.admit_runtime, arguments, "runtime", status)


def test_invalid_pin_remains_blocked_even_when_observation_is_missing(example):
    _, _, arguments = example
    arguments["bundle_sha256"] = "c" * 64
    arguments["info"] = None
    refused(admission.admit_runtime, arguments, "runtime", "blocked")


@pytest.mark.parametrize("stage", ["bundle", "runtime"])
def test_unavailable_platform_tree_remains_unknown(example, stage):
    _, _, arguments = example
    arguments["closure_root"] = arguments["closure_root"].parent / "unavailable"
    if stage == "bundle":
        refused(admission.validate_bundle, bundle_arguments(arguments), stage, "unknown")
    else:
        refused(admission.admit_runtime, arguments, stage, "unknown")


@pytest.mark.parametrize("stage", ["bundle", "runtime"])
def test_file_io_failure_remains_unknown(example, stage, monkeypatch):
    _, _, arguments = example

    def unavailable(*args, **kwargs):
        raise OSError("synthetic read unavailable")

    monkeypatch.setattr(artifacts, "_regular", unavailable)
    if stage == "bundle":
        refused(admission.validate_bundle, bundle_arguments(arguments), stage, "unknown")
    else:
        refused(admission.admit_runtime, arguments, stage, "unknown")


def test_missing_projection_root_remains_unknown(example):
    _, _, arguments = example
    arguments["artifact_root"] = arguments["artifact_root"].parent / "unavailable-projection"
    refused(admission.admit_runtime, arguments, "runtime", "unknown")


@pytest.mark.parametrize("change", ["closure", "projection", "network", "quota", "run_id"])
def test_observed_mismatches_are_blocked_and_every_call_rechecks_bytes(example, change):
    _, _, arguments = example
    assert admission.admit_runtime(**arguments)["status"] == "passed"
    if change == "closure":
        (arguments["closure_root"] / "check.txt").write_bytes(b"changed inert bytes")
    elif change == "projection":
        (arguments["artifact_root"] / "answer.txt").write_bytes(b"change")
    elif change == "network":
        arguments["info"]["HostConfig"]["NetworkMode"] = "bridge"
    elif change == "quota":
        arguments["info"]["HostConfig"]["Tmpfs"]["/tmp"] = "rw"
    else:
        arguments["run_id"] = "unrelated-synthetic-run"
    refused(admission.admit_runtime, arguments, "runtime", "blocked")


@pytest.mark.parametrize("kind", ["bundle", "contract"])
@pytest.mark.parametrize("raw", [b"[]", b"null", b"{", b"\xff", None])
def test_shared_sealed_json_has_typed_failures(kind, raw):
    loader = admission.load_bundle if kind == "bundle" else admission.load_contract
    pin = hashlib.sha256(raw).hexdigest() if isinstance(raw, bytes) else "a" * 64
    with pytest.raises(AdmissionError):
        loader(raw, pin)


@pytest.mark.parametrize("kind", ["bundle", "contract"])
def test_both_sealed_loaders_reject_duplicate_json_keys(example, kind):
    _, _, arguments = example
    original = arguments[kind + "_raw"]
    duplicate = b'{"source_sha256":"' + b"c" * 64 + b'",' + original[1:]
    loader = admission.load_bundle if kind == "bundle" else admission.load_contract
    with pytest.raises(AdmissionError, match="duplicate"):
        loader(duplicate, hashlib.sha256(duplicate).hexdigest())


def test_cleanup_failure_keeps_unknown_evidence_as_legacy_admission_error(example, tmp_path, monkeypatch):
    _, _, arguments = example
    (tmp_path / "source" / "answer.txt").unlink()

    def unavailable_cleanup(path):
        raise OSError("synthetic cleanup unavailable")

    monkeypatch.setattr(artifacts.shutil, "rmtree", unavailable_cleanup)
    with pytest.raises(admission.EvidenceUnavailable, match="cleanup.*retained") as error:
        admission.export_state(tmp_path / "source", tmp_path / "partial-export",
                               arguments["contract_raw"], arguments["contract_sha256"],
                               run_id="synthetic-incomplete-run-173")
    assert isinstance(error.value, AdmissionError)
    assert (tmp_path / "partial-export").exists()
