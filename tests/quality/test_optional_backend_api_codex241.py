"""Optional integration semantics, using authored bytes and supplied facts only.

Resolution A forbids elevation while allowing identity reads and owner-preserving
own-group changes required by eval/admission/artifact_admission.py:351.
"""
from __future__ import annotations

from copy import deepcopy
import os

import pytest

from eval.admission import lifecycle_receipt as lifecycle
from eval.admission import scorer_backend as backend
from lifecycle_fixtures_codex177 import attest, gate_facts, stage_evidence
from test_scorer_admission_codex173 import example, offline_only
from test_scorer_backend_codex213 import request_inputs


@pytest.fixture(autouse=True)
def no_admin_operations(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError("offline API attempted privilege elevation or shell execution")

    # Identity reads and own-group export access do not change process identity.
    # Existing offline_only guards forbid subprocesses and sockets as well.
    for name in ("setuid", "seteuid", "setreuid", "setresuid", "setgid", "setegid",
                 "setregid", "setresgid", "setgroups", "system"):
        if hasattr(os, name):
            monkeypatch.setattr(os, name, refuse)

    calls = []

    def group_only(operation):
        def record(path, uid, gid, **kwargs):
            assert uid == -1, "offline API attempted owner-changing chown"
            assert gid == os.getegid(), "offline API attempted foreign-group chown"
            result = operation(path, uid, gid, **kwargs)
            calls.append((operation.__name__, path, uid, gid))
            return result
        return record

    for name in ("chown", "fchown", "lchown"):
        if hasattr(os, name):
            monkeypatch.setattr(os, name, group_only(getattr(os, name)))
    return calls


@pytest.mark.parametrize("operation", ["chown", "fchown", "lchown"])
def test_own_group_change_preserves_owner_and_reaches_os(tmp_path, no_admin_operations,
                                                       operation):
    path = tmp_path / "own-group.txt"
    path.write_bytes(b"inert")
    before = path.stat()
    with path.open("rb") as stream:
        target = stream.fileno() if operation == "fchown" else path
        assert getattr(os, operation)(target, -1, os.getegid()) is None
        assert no_admin_operations == [(operation, target, -1, os.getegid())]
    after = path.stat()
    assert after.st_uid == before.st_uid
    assert after.st_gid == os.getegid()


@pytest.mark.parametrize("operation", ["chown", "fchown", "lchown"])
@pytest.mark.parametrize("change", ["owner", "foreign_group"])
def test_elevating_ownership_change_is_refused(tmp_path, no_admin_operations,
                                             operation, change):
    path = tmp_path / "refused.txt"
    path.write_bytes(b"inert")
    before = path.stat()
    uid, gid = (0, os.getegid()) if change == "owner" else (-1, os.getegid() + 1)
    reason = "owner-changing" if change == "owner" else "foreign-group"
    with path.open("rb") as stream:
        target = stream.fileno() if operation == "fchown" else path
        with pytest.raises(AssertionError, match=reason):
            getattr(os, operation)(target, uid, gid)
    assert no_admin_operations == []
    after = path.stat()
    assert (after.st_uid, after.st_gid) == (before.st_uid, before.st_gid)


@pytest.mark.parametrize("operation,args", [
    ("setuid", (0,)), ("seteuid", (0,)), ("setreuid", (0, 0)),
    ("setresuid", (0, 0, 0)), ("setgid", (0,)), ("setegid", (0,)),
    ("setregid", (0, 0)), ("setresgid", (0, 0, 0)), ("setgroups", ([],)),
    ("system", ("true",)),
])
def test_identity_setters_and_shell_remain_forbidden(operation, args):
    with pytest.raises(AssertionError, match="privilege elevation or shell execution"):
        getattr(os, operation)(*args)


@pytest.mark.parametrize("operation", ["getuid", "geteuid", "getgid", "getegid"])
def test_identity_reads_remain_available(operation):
    assert isinstance(getattr(os, operation)(), int)


def test_preflight_and_completed_lifecycle_need_no_admin_operations(request_inputs,
                                                                 no_admin_operations):
    root = request_inputs["artifact_root"]
    assert no_admin_operations == [
        ("chown", root, -1, os.getegid()),
        ("chown", root / "answer.txt", -1, os.getegid()),
    ]
    before = deepcopy(request_inputs)
    checked = backend.check_backend(**request_inputs)
    assert checked["status"] == "passed"
    assert all(checked[key] is False for key in (
        "measured", "production_authorized", "execution_authorized", "publication_ready"))

    # Empty synthetic outcomes suffice for the lifecycle structural contract.
    receipt = request_inputs["lifecycle_receipt"]
    for stage, evidence in stage_evidence(request_inputs["binding"], []).items():
        if stage in ("score", "seal", "cleanup"):
            receipt = lifecycle.transition(receipt, stage, evidence)
    lifecycle.validate_lifecycle_receipt(receipt)
    snapshot = receipt["events"][-2]["evidence"]["facts"]["snapshot"]
    assert lifecycle.require_publication(
        receipt, run_id=request_inputs["binding"]["run_id"],
        manifest_sha256=request_inputs["binding"]["manifest_sha256"],
        scope_sha256=request_inputs["scope_sha256"], outcomes_sha256=lifecycle.digest([]),
        cleanup_sha256=receipt["events"][-1]["receipt_sha256"],
        snapshot_sha256=lifecycle.digest(snapshot)) is None
    assert receipt["publication_ready"] is True
    assert receipt["production_authorized"] is False
    assert request_inputs == before


@pytest.mark.parametrize("missing", ["all", "resources", "filesystems"])
def test_incomplete_resource_observation_stays_blocked(request_inputs, missing):
    if missing == "all":
        request_inputs["runtime_observed"] = {}
    else:
        del request_inputs["runtime_observed"][missing]
    with pytest.raises(backend.ScorerBackendError) as error:
        backend.check_backend(**request_inputs)
    assert error.value.code == "resources_contract_refused"
    assert error.value.receipt["status"] == "blocked"
    assert error.value.receipt["measured"] is False
    assert error.value.receipt["production_authorized"] is False


@pytest.mark.parametrize("observation,status", [(None, "unknown"), ({}, "blocked")])
def test_preflight_refusal_can_be_recorded_before_cleanup(request_inputs, observation, status):
    request_inputs["runtime_observed"] = observation
    before = deepcopy(request_inputs)
    with pytest.raises(backend.ScorerBackendError) as error:
        backend.check_backend(**request_inputs)
    refusal = error.value.receipt
    assert refusal["status"] == status
    assert request_inputs == before

    # The orchestrator records an unsuccessful score stage; preflight itself
    # never advances lifecycle and never supplies a score.
    score_status = "unknown" if status == "unknown" else "failed"
    evidence = attest(request_inputs["binding"], "score", status=score_status)
    evidence.update(receipt_sha256=lifecycle.digest(refusal), detail=error.value.code)
    pending = lifecycle.transition(request_inputs["lifecycle_receipt"], "score", evidence)
    finished = lifecycle.transition(pending, "cleanup", gate_facts(request_inputs["binding"], "cleanup"))
    lifecycle.validate_lifecycle_receipt(finished)
    assert finished["status"] == score_status
    assert finished["events"][-1]["status"] == "passed"
    assert finished["publication_ready"] is False
    assert finished["production_authorized"] is False
    assert "score" not in finished
    assert request_inputs == before
