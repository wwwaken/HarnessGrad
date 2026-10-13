"""Synthetic local bundle controls; no datasets, Docker, model or network work."""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from eval import artifact_admission as artifacts
from eval import scorer_bundle as bundles
from eval.pilot_admission import AdmissionError


@pytest.fixture(autouse=True)
def offline_only(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError("bundle control attempted subprocess/network execution")
    monkeypatch.setattr(subprocess, "run", refuse)
    monkeypatch.setattr(subprocess, "Popen", refuse)
    monkeypatch.setattr(socket, "socket", refuse)


@pytest.fixture
def example(tmp_path):
    root = tmp_path / "synthetic-bundle"
    root.mkdir()
    rows = []
    for path, role, requires in (
        ("check.txt", "scorer", ["bin/runtime.txt", "lib/dependency.txt"]),
        ("bin/runtime.txt", "runtime", ["lib/dependency.txt"]),
        ("lib/dependency.txt", "dependency", []),
    ):
        data = f"inert synthetic {role} bytes\n".encode()
        target = root / path
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(data)
        rows.append(dict(path=path, role=role, requires=requires,
                         bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
    manifest = dict(schema=bundles.SCHEMA, source_sha256="a" * 64,
                    runtime_image_id="sha256:" + "b" * 64, network="none",
                    scorer=dict(entrypoint="check.txt", files=rows,
                                argv=["/control-scorer/bin/runtime.txt", "/control-scorer/check.txt"]))
    return root, manifest


def test_task_independent_content_address_and_receipt(example):
    root, manifest = example
    raw, pin = bundles.seal_bundle(manifest)
    reordered = {key: manifest[key] for key in reversed(manifest)}
    assert bundles.seal_bundle(reordered) == (raw, pin)
    assert bundles.load_bundle(raw, pin) == manifest
    receipt = bundles.verify_bundle(root, raw, pin)
    assert receipt == dict(schema="harnessgrad.scorer-bundle-receipt.v1", bundle_sha256=pin,
                           source_sha256=manifest["source_sha256"],
                           runtime_image_id=manifest["runtime_image_id"], declared_network="none",
                           files=3, bytes=sum(row["bytes"] for row in manifest["scorer"]["files"]),
                           scope="local_declared_closure_integrity")
    assert "task_id" not in receipt


@pytest.mark.parametrize("change", ["source", "image", "command", "graph"])
def test_every_declared_identity_change_changes_address(example, change):
    _, manifest = example
    _, pin = bundles.seal_bundle(manifest)
    if change == "source":
        manifest["source_sha256"] = "c" * 64
    elif change == "image":
        manifest["runtime_image_id"] = "sha256:" + "d" * 64
    elif change == "command":
        manifest["scorer"]["argv"].append("--synthetic-option")
    else:
        manifest["scorer"]["files"][1]["requires"].clear()
    assert bundles.seal_bundle(manifest)[1] != pin


@pytest.mark.parametrize("change", ["tag", "network", "unknown_attestation", "task",
                                    "missing_dependency", "unused_dependency", "actor_runtime",
                                    "bool_size", "duplicate_path", "wrong_entrypoint", "malformed_files"])
def test_unclosed_or_unsupported_declarations_fail_before_file_access(example, change, monkeypatch):
    root, manifest = example
    scorer = manifest["scorer"]
    if change == "tag":
        manifest["runtime_image_id"] = "synthetic:latest"
    elif change == "network":
        manifest["network"] = "bridge"
    elif change == "unknown_attestation":
        manifest["official_verified"] = True
    elif change == "task":
        manifest["task_id"] = "synthetic-task"
    elif change == "missing_dependency":
        scorer["files"][0]["requires"].append("absent.txt")
    elif change == "unused_dependency":
        scorer["files"][0]["requires"] = ["bin/runtime.txt"]
        scorer["files"][1]["requires"].clear()
    elif change == "actor_runtime":
        scorer["argv"][0] = "/control-input/runtime.txt"
    elif change == "bool_size":
        scorer["files"][0]["bytes"] = True
    elif change == "duplicate_path":
        scorer["files"].append(copy.deepcopy(scorer["files"][0]))
    elif change == "wrong_entrypoint":
        scorer["entrypoint"] = []
    else:
        scorer["files"] = "not a file list"
    raw = json.dumps(manifest).encode()
    monkeypatch.setattr(artifacts, "_inventory", lambda *_: pytest.fail("invalid declaration read bundle"))
    with pytest.raises(AdmissionError):
        bundles.verify_bundle(root, raw, hashlib.sha256(raw).hexdigest())


def test_wrong_external_pin_and_duplicate_json_keys_are_rejected(example):
    root, manifest = example
    raw, pin = bundles.seal_bundle(manifest)
    with pytest.raises(AdmissionError, match="seal mismatch"):
        bundles.verify_bundle(root, raw + b" ", pin)
    duplicate = b'{"network":"bridge",' + raw[1:]
    with pytest.raises(AdmissionError, match="duplicate"):
        bundles.load_bundle(duplicate, hashlib.sha256(duplicate).hexdigest())


@pytest.mark.parametrize("raw", [b"[]", b"null", b"{", b"\xff"])
def test_malformed_manifest_has_typed_failure(raw):
    with pytest.raises(AdmissionError):
        bundles.load_bundle(raw, hashlib.sha256(raw).hexdigest())


@pytest.mark.parametrize("change", ["changed", "missing", "extra", "symlink", "hardlink", "extra_directory"])
def test_exact_bundle_inventory_and_local_bytes_are_required(example, change):
    root, manifest = example
    raw, pin = bundles.seal_bundle(manifest)
    dependency = root / "lib/dependency.txt"
    if change == "changed":
        data = dependency.read_bytes()
        dependency.write_bytes(b"X" + data[1:])
    elif change == "missing":
        dependency.unlink()
    elif change == "extra":
        (root / "extra.txt").write_bytes(b"inert extra file")
    elif change == "symlink":
        dependency.unlink()
        dependency.symlink_to("../check.txt")
    elif change == "hardlink":
        os.link(dependency, root.parent / "synthetic-alias")
    else:
        (root / "extra-directory").mkdir()
    with pytest.raises(AdmissionError):
        bundles.verify_bundle(root, raw, pin)


def artifact_contract(manifest, task_id):
    return dict(schema="harnessgrad.artifact-scorer.v1", task_id=task_id,
                source_sha256=manifest["source_sha256"], runtime_image_id=manifest["runtime_image_id"],
                scorer=copy.deepcopy(manifest["scorer"]),
                export=dict(files=[dict(path="answer.txt", max_bytes=8)], max_bytes=8, max_inodes=2),
                quota={"/tmp": dict(bytes=4096, inodes=8)})


def test_one_bundle_binds_multiple_task_contracts_and_legacy_receipts(example):
    root, manifest = example
    raw, pin = bundles.seal_bundle(manifest)
    for task_id in ("synthetic-task-a", "synthetic-task-b"):
        contract = artifact_contract(manifest, task_id)
        contract_raw = json.dumps(contract).encode()
        contract_pin = hashlib.sha256(contract_raw).hexdigest()
        assert bundles.require_contract_bundle(contract_raw, contract_pin, raw, pin) == contract
        receipt = artifacts.verify_scorer_closure(root, contract_raw, contract_pin)
        assert receipt["task_id"] == task_id
        assert receipt["files"] == bundles.verify_bundle(root, raw, pin)["files"]


@pytest.mark.parametrize("change", ["source", "image", "command"])
def test_task_contract_must_match_separately_pinned_bundle(example, change):
    _, manifest = example
    raw, pin = bundles.seal_bundle(manifest)
    contract = artifact_contract(manifest, "synthetic-task")
    if change == "source":
        contract["source_sha256"] = "c" * 64
    elif change == "image":
        contract["runtime_image_id"] = "sha256:" + "d" * 64
    else:
        contract["scorer"]["argv"].append("--changed-synthetic-command")
    contract_raw = json.dumps(contract).encode()
    with pytest.raises(AdmissionError, match="does not match"):
        bundles.require_contract_bundle(contract_raw, hashlib.sha256(contract_raw).hexdigest(), raw, pin)


def test_cli_emits_scoped_receipt_and_no_score(example, tmp_path, capsys):
    root, manifest = example
    raw, pin = bundles.seal_bundle(manifest)
    path = tmp_path / "synthetic-manifest.json"
    path.write_bytes(raw)
    argv = ["--root", str(root), "--manifest", str(path), "--sha256", pin]
    assert bundles.main(argv) == 0
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["scope"] == "local_declared_closure_integrity"
    assert "score" not in receipt and "passed" not in receipt
    (root / "check.txt").unlink()
    assert bundles.main(argv) == 2
    assert json.loads(capsys.readouterr().out) == dict(valid=False, scope="local_declared_closure_integrity")
