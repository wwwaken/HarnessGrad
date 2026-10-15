"""Offline metadata/source/receipt integrity; no adapter, external read or execution."""
import ast
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "tests/fixtures/hg_migration_site/b6-blocker-evidence"


@pytest.fixture(autouse=True)
def optional_evidence_packet(request):
    if request.node.name == "test_active_registry_retires_reviews_without_promoting_historical_results":
        return
    if not EVIDENCE.is_dir():
        pytest.skip("B6 exported evidence packet absent from this clone")


def read(path):
    return json.loads((EVIDENCE / path).read_bytes())


def digest(data):
    return hashlib.sha256(data).hexdigest()


@pytest.fixture(autouse=True)
def offline_source_only(monkeypatch):
    import builtins
    import io
    import socket
    original_import, original_open = builtins.__import__, io.open

    def guarded_import(name, *args, **kwargs):
        assert name != "data" and not name.startswith("data."), "no dataset imports"
        return original_import(name, *args, **kwargs)

    def guarded_open(path, *args, **kwargs):
        if isinstance(path, (str, bytes, Path)):
            assert Path(path).resolve().is_relative_to(ROOT), "no external receipt reads"
        return original_open(path, *args, **kwargs)

    def denied(*args, **kwargs):
        pytest.fail("no network/subprocess execution")

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    monkeypatch.setattr(io, "open", guarded_open)
    monkeypatch.setattr(socket, "socket", denied)
    monkeypatch.setattr(subprocess, "Popen", denied)


def test_manifest_pins_all_evidence_and_every_response_hop():
    expected = {}
    for line in (EVIDENCE / "SHA256SUMS").read_text().splitlines():
        sha, relative = line.split("  ", 1)
        assert relative not in expected
        expected[relative] = sha
        assert digest((EVIDENCE / relative).read_bytes()) == sha
    assert set(expected) == {str(p.relative_to(EVIDENCE)) for p in EVIDENCE.rglob("*")
                             if p.is_file() and p.name != "SHA256SUMS"}
    for response in read("review.json")["responses"]:
        if "error" in response:
            assert "sha256" not in response
            continue
        folder = EVIDENCE / response["acquisition"]
        body = (folder / f"hop-{response['hop']}.body").read_bytes()
        headers = (folder / f"hop-{response['hop']}.headers").read_bytes()
        assert len(body) == response["bytes"]
        assert digest(body) == response["sha256"]
        assert digest(headers) == response["headers_sha256"]
        assert response["complete"] is True


@pytest.mark.parametrize("name,pin", [
    ("twowiki-hub-proxy-revision", "6340521cf170fac8e82785cd21a5e9941306ea6ee54963438b6555561b09d21a"),
    ("lcb-hub-proxy-revision", "501d60839cc3f592b476d5d79b1093f29ade0144fb3318f1b261d3ece274e4d4"),
    ("ujson-immutable-commit", "6d56bf2aeebe121f69fb290be85a307bfc2d01723ee8cefd09af9b3af3013fe3"),
])
def test_origin_responses_have_independent_pins(name, pin):
    assert digest((EVIDENCE / name / "hop-0.body").read_bytes()) == pin
    receipt = read(f"{name}/receipt.json")[0]
    assert receipt["status"] == 200
    assert receipt["url"].startswith(("https://huggingface.co/", "https://api.github.com/"))


def test_canonical_hub_artifact_pins_and_distinct_builder_routes():
    twowiki = read("twowiki-hub-proxy-revision/hop-0.body")
    assert twowiki["sha"] == "f4f0d7e4ae275d9281e90c46c93e66d6cdda3674"
    files = {p["rfilename"]: p for p in twowiki["siblings"]}
    assert files["data/dev.json"]["lfs"]["sha256"] == "79f77ae104088ea8e25b1a65dbece768d45771194663bc5660ec9a98070dadf5"
    assert files["data/id_aliases.json"]["lfs"]["sha256"] == "f08ffcb6c2cefca9bdbe86b4248d6ad7a7743762d3f7264c14ff0bae85726fb6"
    builder = (EVIDENCE / "twowiki-hub-proxy-loader/hop-1.body").read_text()
    assert '"answer_id"' not in builder and '"evidences_id"' not in builder
    assert 'datasets.Split.VALIDATION: f"{_URL_BASE}/dev.json"' in builder
    assert 'license=' not in builder
    lcb = (EVIDENCE / "lcb-hub-proxy-builder/hop-1.body").read_text()
    allowed = next(n for n in ast.parse(lcb).body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == "ALLOWED_FILES" for t in n.targets))
    assert ast.literal_eval(allowed.value)["release_v6"] == ["test.jsonl", "test2.jsonl", "test3.jsonl", "test4.jsonl", "test5.jsonl", "test6.jsonl"]
    assert 'name=datasets.Split.TEST' in lcb


def test_source_bytes_are_bound_to_acquired_git_blobs():
    for name, source in read("review.json")["sources"].items():
        if name in ("twowiki-hub-proxy-loader", "lcb-hub-proxy-builder"):
            data = (EVIDENCE / name / "hop-1.body").read_bytes()
        else:
            response = read(f"{name}/hop-0.body")
            data = base64.b64decode(response["content"])
            assert response["sha"] == source["git_blob_sha1"]
        assert hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == source["git_blob_sha1"]
        assert digest(data) == source["sha256"]


def test_vendored_source_tree_and_notices_are_carried_without_wheel_mutation():
    tree = read("ujson-source-tree/hop-0.body")
    commit = read("ujson-immutable-commit/hop-0.body")
    assert tree["sha"] == commit["sha"] == "59875e089937c8b05c2f4b474530e3a9ec706a56"
    assert commit["tree"]["sha"] == "f68f465c6b5d55dc9520b51c5bc666ddeb0dd2b5"
    assert next(e for e in tree["tree"] if e["path"] == "deps/double-conversion")["sha"] == "629e1ff9b56216eb1423941ad615573354a857e4"
    notices = EVIDENCE / "ujson-supplemental-notices"
    assert digest((notices / "double-conversion-LICENSE").read_bytes()) == "4af93c12062c58058378de2397dc1c92bbff9ddfb1d583a01c84127557ce97ca"
    assert (notices / "ujson-LICENSE.txt").read_bytes() == (ROOT / "tests/fixtures/ujson_pypi_codex226/LICENSE.txt").read_bytes()
    assert "V8 project authors" in (notices / "double-conversion-LICENSE").read_text()


def test_preserved_coverage_is_separate_and_original_invalids_stay_invalid():
    review = read("review.json")
    original, recovery = (review["twowiki_runs"][k] for k in ("original", "recovery"))
    assert (original["selected_count"], original["scored_tasks"], original["recorded_trial_values"], original["invalid_tasks"]) == (50, 48, 144, 2)
    assert (recovery["selected_count"], recovery["scored_tasks"], recovery["recorded_trial_values"], recovery["invalid_tasks"]) == (2, 2, 6, 0)
    assert original["harness_sha"] != recovery["harness_sha"]
    assert original["split_sha256"] == recovery["split_sha256"]
    assert original["per_trial_metric_identity_bound"] is recovery["per_trial_metric_identity_bound"] is False
    first = read("preserved-receipts/twowiki-original-curve.jsonl")
    second = read("preserved-receipts/twowiki-recovery-curve.jsonl")
    assert set(first["invalid"]) == set(second["sampling"]["task_ids"])
    assert not set(first["invalid"]) & set(first["per_task"])
    assert first["n_invalid"] == 2
    for item in review["preserved_receipts"]["files"]:
        assert digest((EVIDENCE / "preserved-receipts" / item["path"]).read_bytes()) == item["sha256"]


def test_denominator_policies_are_distinct_from_run_coverage():
    policies = read("review.json")["denominator_policies"]
    assert policies["twowikimultihopqa"]["corpus_metrics"]["denominator"] == "gold_rows"
    assert policies["musique"]["corpus_metrics"]["denominator"] == "provided_results"
    for name in policies:
        assert policies[name]["run_reward"]["denominator"] == "measured_tasks"


def test_official_code_and_planning_receipt_do_not_become_a_smoke_execution():
    executor = (EVIDENCE / "lcb-executor/decoded.source").read_text()
    assert digest(executor.encode()) == "b7cb6a8a69807bb868150a61742e25d7bb5328bbe01d514471b6ec43c9fa9ed2"
    assert 'def run_test(sample, test=None, debug=False, timeout=6):' in executor
    assert 'reliability_guard()' in executor
    assert 'def reliability_guard(maximum_memory_bytes=None):' in executor
    assert 'get_function(compiled_sol, "wrapped_function")' in executor
    launch = read("preserved-receipts/lcb-smoke-launch.json")
    assert launch["launch_executed"] is launch["H0_authorized"] is False
    assert "official 2s/1024MiB" in " ".join(launch["known_deviations"])


def test_active_registry_retires_reviews_without_promoting_historical_results():
    registry = json.loads((ROOT / "registry/dataset-blockers.json").read_bytes())
    rows = {r["dataset"]: r for r in registry["datasets"]}
    assert {b["id"] for b in rows["twowikimultihopqa"]["blockers"]} == {"hub-data-provenance", "ujson-native-offline-closure"}
    assert {b["id"] for b in rows["livecodebench"]["blockers"]} == {"row-attestation"}
    for name in ("twowikimultihopqa", "livecodebench"):
        assert all(b["status"] == "external" for b in rows[name]["blockers"])
    assert registry["review"]["production_authorized"] is False
    # Pin the exported review identity without pretending /site is a local file.
    for name, blocker_id, locator in (
        ("twowikimultihopqa", "ujson-native-offline-closure", "## 2Wiki: ujson-native-offline-closure"),
        ("twowikimultihopqa", "hub-data-provenance", "## 2Wiki: hub-data-provenance"),
        ("livecodebench", "row-attestation", "## LiveCodeBench: row-attestation"),
    ):
        blocker = next(b for b in rows[name]["blockers"] if b["id"] == blocker_id)
        assert {"kind": "external-reference", "path": "/site/b6-dataset-blocker-review.md",
                "locator": locator} in blocker["evidence"]


def test_archived_review_does_not_authorize_execution():
    review = read("review.json")
    assert review["production_authorized"] is review["benchmark_execution"] is False
    assert review["model_calls"] == 0
