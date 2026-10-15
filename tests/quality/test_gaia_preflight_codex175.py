"""Authored metadata/refusal regressions; no dataset or runtime observations."""
from copy import deepcopy
import ast
import builtins
import json
from pathlib import Path
import socket
import subprocess
import sys

import pytest

from eval.policy import gaia_preflight as preflight, gaia_snapshot_attestation as compatibility
from eval.run import runner

ROOT = Path(__file__).resolve().parents[2]
ARGS = ["--reference-commit", "a" * 40, "--candidate-commit", "b" * 40]
HOST_RUN = subprocess.run
HOST_POPEN = subprocess.Popen


def source(commit):
    return {"schema": compatibility.SOURCE_SCHEMA, "commit": commit, "tree": "c" * 40,
            "files": {p: {"mode": "100644", "oid": "d" * 40}
                      for p in compatibility.REQUIRED_SOURCE}}


def binding():
    return {"schema": compatibility.RUNTIME_SCHEMA, "dataset_revision": "e" * 40,
            "split": "validation", "image_id": "sha256:" + "f" * 64,
            "verifier_image_id": "sha256:" + "1" * 64, "container_plan": 1,
            "snapshot_max_bytes": 16 << 30, "snapshot_reserve_bytes": 1 << 30,
            "limits": {"cpus": 2, "memory_mb": 4096, "pids": 256},
            **{key: "2" * 64 for key in compatibility.RUNTIME_HASHES}}


@pytest.fixture(autouse=True)
def metadata_only(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("preflight attempted file, backend or scoring access")

    monkeypatch.setattr(compatibility, "collect_source", lambda repo, commit, **kw: source(commit))
    monkeypatch.setattr(subprocess, "run", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(runner, "run_one", forbidden)
    monkeypatch.setattr(runner, "_evaluate", forbidden)
    monkeypatch.setattr(runner, "_verify", forbidden)
    monkeypatch.setattr(runner, "snapshot", forbidden)
    monkeypatch.setattr(runner.container_mod, "docker", forbidden)
    monkeypatch.setattr(runner.container_mod.shutil, "disk_usage", forbidden)
    monkeypatch.setattr(runner.services_mod, "start", forbidden)


def review(capsys, args=ARGS):
    assert preflight.main(args) == 2
    captured = capsys.readouterr()
    assert captured.err == ""
    report = json.loads(captured.out)
    assert report["execution_status"] == "blocked"
    assert report["measured"] is False
    for key in ("production_authorized", "lifecycle_authorized", "evidence_reusable"):
        assert report[key] is False
    assert report["receipt_validation"] == "not-performed"
    assert "score" not in report
    return report


def test_source_review_uses_only_fixed_repo_and_clean_candidate(monkeypatch, capsys):
    calls = []

    def collect(repo, commit, **kwargs):
        calls.append((repo, commit, kwargs))
        return source(commit)

    monkeypatch.setattr(compatibility, "collect_source", collect)
    report = review(capsys)
    assert calls == [(ROOT, "b" * 40, {"require_checkout": True}), (ROOT, "a" * 40, {})]
    assert report["preflight_status"] == "review-only"
    assert report["source_manifests"]["candidate"] == source("b" * 40)
    assert report["source_comparison"]["source_compatible_only"] is True
    assert report["source_comparison"]["checkout_lock"] == "not-held"
    assert report["runtime_compatibility"]["status"] == "not-performed"
    assert report["runner_refusal"]["reason"] == "backend_observation_unavailable"


@pytest.mark.parametrize("change", [False, True])
def test_complete_bindings_compare_without_authorization_or_reuse(capsys, change):
    candidate = deepcopy(binding())
    if change:
        candidate["limits"]["pids"] += 1
    report = review(capsys, ARGS + ["--reference-runtime", json.dumps(binding()),
                                   "--candidate-runtime", json.dumps(candidate)])
    attestation = report["runtime_compatibility"]
    assert attestation["compatible"] is (not change)
    assert attestation["lifecycle_authorized"] is False
    assert attestation["evidence_reusable"] is False
    assert report["runtime_binding_provenance"] == "caller-declared-not-authenticated"


def test_new_cli_and_its_report_are_not_review_only_exemptions(monkeypatch, capsys):
    def collect(repo, commit, **kwargs):
        manifest = source(commit)
        if kwargs:
            for path in ("eval/policy/gaia_preflight.py", "docs/gaia-preflight-codex175-report.md"):
                manifest["files"][path] = {"mode": "100644", "oid": "3" * 40}
        return manifest

    monkeypatch.setattr(compatibility, "collect_source", collect)
    report = review(capsys)
    assert report["source_comparison"]["source_compatible_only"] is False
    assert report["source_comparison"]["runtime_changed_paths"] == [
        "docs/gaia-preflight-codex175-report.md", "eval/policy/gaia_preflight.py"]


@pytest.mark.parametrize("extra", [
    ["--execute", "private-task-content"], ["--task-id", "private-task-content"],
    ["--repo", "/private/payload"], ["--output", "/private/payload"],
    ["--reference-runtime", "@/private/payload"],
    ["--reference-runtime", '{"gold":"private-task-content"}', "--candidate-runtime", "{}"],
    ["--reference-runtime", '{"schema":1,"schema":2}', "--candidate-runtime", "{}"],
    ["--reference-runtime", '{"schema":NaN}', "--candidate-runtime", "{}"],
    ["--reference-runtime", "[" * 1100, "--candidate-runtime", "{}"],
    ["--reference-runtime", "x" * (preflight.MAX_BINDING_CHARS + 1), "--candidate-runtime", "{}"],
])
def test_invalid_inputs_are_sanitized_without_any_metadata_or_file_reads(
        monkeypatch, capsys, extra):
    def forbidden(*args, **kwargs):
        raise AssertionError("invalid input must precede collection and file access")

    monkeypatch.setattr(compatibility, "collect_source", forbidden)
    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(Path, "read_text", forbidden)
    monkeypatch.setattr(Path, "read_bytes", forbidden)
    report = review(capsys, ARGS + extra)
    assert report["preflight_status"] == "invalid-metadata"
    assert "private" not in json.dumps(report)


@pytest.mark.parametrize("fault", ["dirty", "missing-refusal"])
def test_source_failure_or_changed_hook_cannot_fall_through(monkeypatch, capsys, fault):
    if fault == "dirty":
        def collect(*args, **kwargs):
            raise compatibility.CompatibilityError("private dirty path")
        monkeypatch.setattr(compatibility, "collect_source", collect)
    else:
        monkeypatch.setattr(runner, "_refuse_unobserved_policies", lambda *args, **kw: None)
    report = review(capsys)
    assert report["preflight_status"] == "invalid-metadata"
    assert "private" not in json.dumps(report)


def test_fixed_probe_matches_gaia_source_policy_presence():
    # Read only committed adapter source; never import its lazy data attributes.
    tree = ast.parse((ROOT / "data/datasets/gaia.py").read_text())
    env = next(node.value for node in tree.body if isinstance(node, ast.AnnAssign)
               and isinstance(node.target, ast.Name) and node.target.id == "ENV_BASE")
    keys = {key.value for key in env.keys}
    receipt = preflight._runner_refusal()
    fields = {"env." + key for key in keys & {
        "cpus", "memory_mb", "agent_timeout_s", "verify_timeout_s", "network",
        "resources", "filesystems", "resource_policy", "network_policy", "artifact_policy"}}
    # `verifier.timeout_s` is absent on purpose: the platform enforces that deadline
    # itself and records expiry, so it is not a backend-observation trigger. GAIA is
    # still refused through its exec defaults, container state and service network.
    assert set(receipt["policy_fields"]) == fields | {
        "env.exec_defaults", "env.state=container"}
    assert "verifier.timeout_s" not in receipt["policy_fields"]
    values = dict(zip((key.value for key in env.keys), env.values))
    assert ast.literal_eval(values["kind"]) == "exec"
    assert ast.literal_eval(values["state"]) == "container"
    assert ast.literal_eval(values["network"]) == "services"
    verifier = next(node for node in tree.body
                    if isinstance(node, ast.FunctionDef) and node.name == "_verify")
    assert any(isinstance(node, ast.Dict)
               and any(isinstance(key, ast.Constant) and key.value == "timeout_s"
                       for key in node.keys) for node in ast.walk(verifier))


def test_fresh_module_import_and_review_have_no_payload_or_backend_access(monkeypatch):
    # A fresh interpreter guards import side effects as well as the entrypoint.
    code = '''
import json, pathlib, runpy, sys
def guard(event, args):
    if event == "open" and isinstance(args[0], (str, bytes)):
        path = str(args[0])
        if not path.endswith((".py", ".pyc")):
            raise AssertionError("non-source file access")
    if event in {"subprocess.Popen", "os.system", "socket.__new__", "socket.connect"}:
        raise AssertionError("backend access")
sys.addaudithook(guard)
from eval.policy import gaia_snapshot_attestation as compatibility
compatibility.collect_source = lambda repo, commit, **kw: SOURCE
sys.argv = ["gaia_preflight", "--reference-commit", "a" * 40, "--candidate-commit", "b" * 40]
runpy.run_module("eval.policy.gaia_preflight", run_name="__main__")
'''.replace("SOURCE", repr(source("a" * 40)))
    # This one subprocess is the guarded Python test, never an execution backend.
    with monkeypatch.context() as patch:
        # The autouse Popen guard remains installed; restore only for this child.
        patch.setattr(subprocess, "Popen", HOST_POPEN)
        result = HOST_RUN([sys.executable, "-B", "-c", code], cwd=ROOT,
                          capture_output=True, text=True, timeout=30)
    assert result.returncode == 2, result.stderr
    assert json.loads(result.stdout)["preflight_status"] == "review-only"
