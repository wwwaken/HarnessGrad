"""Offline admission contracts for trusted adapter runtime observations.

These functions inspect supplied facts only. They install no quotas, execute no
probes and grant no production authorization. A backend must independently collect
complete, fresh observations and enforce the declared bounds before using them.
"""
from __future__ import annotations

from functools import wraps
import hashlib
import json
import posixpath
import re

MAX_RECEIPT_BYTES = 16 * 1024
MAX_SURFACES = 32
MAX_OWNED = 64
RESOURCE_KEYS = {"cpu_millis", "memory_bytes", "swap_bytes", "pids", "timeout_ms"}
KINDS = {"container", "network", "snapshot", "volume", "workspace"}


class AdmissionError(RuntimeError):
    """A refused contract, with a bounded, unmeasured receipt for persistence."""

    def __init__(self, code: str, receipt: dict | None = None):
        super().__init__(code)
        self.code = code
        self.receipt = receipt


def _require(ok: bool, code: str) -> None:
    if not ok:
        raise AdmissionError(code)


def _object(value, keys: set[str], code: str) -> None:
    _require(isinstance(value, dict) and set(value) == keys, code)


def _integer(value, code: str, *, positive: bool = False) -> None:
    _require(type(value) is int and (1 if positive else 0) <= value <= 2**63 - 1, code)


def _text(value, code: str) -> None:
    _require(isinstance(value, str) and 0 < len(value) <= 256, code)
    try:
        _require(len(value.encode()) <= 256 and not any(ord(c) < 32 for c in value), code)
    except UnicodeError as exc:
        raise AdmissionError(code) from exc


def _sha(value, code: str) -> None:
    _require(isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) is not None, code)


def _hash(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    allow_nan=False).encode()).hexdigest()


def _binding(value) -> dict:
    _object(value, {"adapter_id", "run_id", "trial_id", "manifest_sha256"}, "invalid_binding")
    for key in ("adapter_id", "run_id", "trial_id"):
        _text(value[key], "invalid_binding")
    _sha(value["manifest_sha256"], "invalid_binding")
    return dict(value)


def _gate(stage):
    def decorate(check):
        @wraps(check)
        def wrapped(binding, policy, observed):
            receipt = dict(schema="harnessgrad.runner-admission.v1", stage=stage,
                           status="blocked", measured=False, production_authorized=False)
            if stage == "cleanup":
                receipt["lease_action"] = "quarantine"
            try:
                receipt["binding"] = _binding(binding)
                evidence = check(binding, policy, observed)
                receipt.update(status="passed", policy_sha256=_hash(policy),
                               observation_sha256=_hash(observed), evidence=evidence)
                if stage == "cleanup":
                    receipt["lease_action"] = "release"
                _require(len(json.dumps(receipt).encode()) <= MAX_RECEIPT_BYTES,
                         "receipt_too_large")
                return receipt
            except AdmissionError as exc:
                receipt.pop("evidence", None)
                receipt.update(status="blocked", reason=exc.code)
                if stage == "cleanup":
                    receipt["lease_action"] = "quarantine"
                raise AdmissionError(exc.code, receipt) from exc
        return wrapped
    return decorate


def _observation(binding, observed, keys):
    _object(observed, keys | {"binding", "evidence_sha256"}, "invalid_observation")
    _require(_binding(observed["binding"]) == binding, "stale_observation")
    _sha(observed["evidence_sha256"], "invalid_evidence_hash")


def _resources(values, code):
    _object(values, RESOURCE_KEYS, code)
    for key, value in values.items():
        _integer(value, code, positive=key != "swap_bytes")


def _surfaces(value):
    _require(isinstance(value, dict) and len(value) <= MAX_SURFACES, "invalid_surfaces")
    for path in value:
        _text(path, "invalid_surface_path")
        _require(path.startswith("/") and path != "/" and not path.startswith("//")
                 and posixpath.normpath(path) == path, "invalid_surface_path")


@_gate("runtime")
def admit_runtime(binding: dict, policy: dict, observed: dict) -> dict:
    """Check actual resource/network limits and every writable filesystem surface."""
    _object(policy, {"resources", "network", "filesystems"}, "invalid_runtime_policy")
    _resources(policy["resources"], "invalid_resource_policy")
    _require(policy["network"] == "none", "network_policy_not_supported")
    _surfaces(policy["filesystems"])
    for limits in policy["filesystems"].values():
        _object(limits, {"bytes", "inodes"}, "invalid_filesystem_policy")
        for value in limits.values():
            _integer(value, "invalid_filesystem_policy", positive=True)
    _observation(binding, observed, {"resources", "resource_backend", "timeout_backend", "network",
                                   "attachments", "read_only_root", "filesystems"})
    _resources(observed["resources"], "invalid_resource_observation")
    _require(observed["resource_backend"] in ("cgroup-v1", "cgroup-v2"),
             "resource_enforcement_unproven")
    _require(observed["timeout_backend"] == "host-supervisor", "deadline_enforcement_unproven")
    _require(observed["resources"] == policy["resources"], "resource_limit_mismatch")
    _require(observed["network"] == "none" and observed["attachments"] == [],
             "network_enforcement_unproven")
    _require(observed["read_only_root"] is True, "writable_root_unbounded")
    _surfaces(observed["filesystems"])
    _require(set(observed["filesystems"]) == set(policy["filesystems"]),
             "writable_surface_inventory_mismatch")
    scopes = set()
    for path, limits in policy["filesystems"].items():
        actual = observed["filesystems"][path]
        _object(actual, {"bytes", "inodes", "backend", "scope_id", "evidence_sha256"},
                "filesystem_enforcement_unproven")
        _require(actual["backend"] in ("tmpfs", "project-quota"),
                 "filesystem_enforcement_unproven")
        _text(actual["scope_id"], "invalid_quota_scope")
        _require(actual["scope_id"] not in scopes, "shared_quota_scope")
        scopes.add(actual["scope_id"])
        _sha(actual["evidence_sha256"], "invalid_evidence_hash")
        for key in ("bytes", "inodes"):
            _integer(actual[key], "invalid_filesystem_observation", positive=True)
            _require(actual[key] == limits[key], "filesystem_limit_mismatch")
    return dict(resources=dict(observed["resources"]), network="none", read_only_root=True,
                filesystems={path: dict(row) for path, row in observed["filesystems"].items()})


@_gate("snapshot")
def admit_snapshot(binding: dict, policy: dict, observed: dict) -> dict:
    """Validate quiescence, disk/inode headroom and a finite snapshot deadline.

    This is preflight capacity evidence, not writable-layer quota enforcement.
    The snapshot worker's CPU/memory/PID limits need a separate runtime admission.
    """
    _object(policy, {"max_bytes", "max_inodes", "reserve_bytes", "reserve_inodes", "timeout_ms"},
            "invalid_snapshot_policy")
    for value in policy.values():
        _integer(value, "invalid_snapshot_policy", positive=True)
    _observation(binding, observed, {"writable_bytes", "writable_inodes", "free_bytes",
                                   "free_inodes", "running", "exit_code", "oom_killed",
                                   "timeout_ms", "device_id"})
    _require(observed["running"] is False and type(observed["exit_code"]) is int
             and observed["exit_code"] == 0 and observed["oom_killed"] is False,
             "snapshot_quiescence_unproven")
    _text(observed["device_id"], "invalid_snapshot_device")
    for key in ("writable_bytes", "writable_inodes", "free_bytes", "free_inodes"):
        _integer(observed[key], "invalid_snapshot_observation")
    _integer(observed["timeout_ms"], "invalid_snapshot_deadline", positive=True)
    _require(observed["timeout_ms"] == policy["timeout_ms"], "snapshot_deadline_mismatch")
    for unit in ("bytes", "inodes"):
        _require(observed["writable_" + unit] <= policy["max_" + unit],
                 "snapshot_size_exceeded")
        _require(observed["free_" + unit] >= observed["writable_" + unit] + policy["reserve_" + unit],
                 "snapshot_headroom_insufficient")
    evidence = {key: observed[key] for key in observed if key not in {"binding", "evidence_sha256"}}
    evidence.update(limits=dict(policy),
                    required_bytes=observed["writable_bytes"] + policy["reserve_bytes"],
                    required_inodes=observed["writable_inodes"] + policy["reserve_inodes"])
    return evidence


def _inventory(value):
    _require(isinstance(value, list) and len(value) <= MAX_OWNED, "invalid_owned_inventory")
    identities = set()
    for item in value:
        _object(item, {"kind", "id"}, "invalid_owned_inventory")
        _require(isinstance(item["kind"], str) and item["kind"] in KINDS, "invalid_owned_kind")
        _text(item["id"], "invalid_owned_id")
        identity = (item["kind"], item["id"])
        _require(identity not in identities, "duplicate_owned_resource")
        identities.add(identity)
    return identities


@_gate("cleanup")
def admit_cleanup(binding: dict, policy: dict, observed: dict) -> dict:
    """Release only after exact owned-object and complete namespace absence checks."""
    _object(policy, {"owned", "timeout_ms"}, "invalid_cleanup_policy")
    owned = _inventory(policy["owned"])
    _integer(policy["timeout_ms"], "invalid_cleanup_policy", positive=True)
    _observation(binding, observed, {"objects", "namespaces", "timeout_ms"})
    _require(observed["timeout_ms"] == policy["timeout_ms"]
             and type(observed["timeout_ms"]) is int, "cleanup_deadline_mismatch")
    objects = observed["objects"]
    _require(isinstance(objects, list) and len(objects) <= MAX_OWNED, "invalid_cleanup_objects")
    identities = []
    for item in objects:
        _object(item, {"kind", "id", "absent", "evidence_sha256"}, "invalid_cleanup_object")
        identities.append({key: item[key] for key in ("kind", "id")})
        _require(item["absent"] is True, "owned_absence_unproven")
        _sha(item["evidence_sha256"], "invalid_evidence_hash")
    _require(_inventory(identities) == owned, "cleanup_inventory_mismatch")
    namespaces = observed["namespaces"]
    _object(namespaces, KINDS, "cleanup_namespace_coverage_incomplete")
    for row in namespaces.values():
        _object(row, {"remaining", "evidence_sha256"}, "invalid_cleanup_namespace")
        _require(row["remaining"] == [], "owned_namespace_absence_unproven")
        _sha(row["evidence_sha256"], "invalid_evidence_hash")
    return dict(owned_count=len(owned), checked_kinds=sorted(KINDS), timeout_ms=policy["timeout_ms"])
