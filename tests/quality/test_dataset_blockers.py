"""Source-only index regressions: no adapters, task pools or external receipts."""
from __future__ import annotations

import builtins
import copy
import hashlib
import io
import json
from pathlib import Path
import socket
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import check_dataset_blockers as checker  # noqa: E402


@pytest.fixture(autouse=True)
def source_only(monkeypatch, tmp_path):
    original_import = builtins.__import__
    original_open = io.open
    allowed_tmp = tmp_path.resolve()

    def guarded_import(name, *args, **kwargs):
        assert name != "data" and not name.startswith("data."), "adapter imports forbidden"
        return original_import(name, *args, **kwargs)

    def guarded_open(path, *args, **kwargs):
        if isinstance(path, (str, bytes, Path)):
            resolved = Path(path).resolve()
            assert (resolved.is_relative_to(ROOT) or resolved.is_relative_to(allowed_tmp)), \
                "external file reads forbidden"
        return original_open(path, *args, **kwargs)

    def denied(*args, **kwargs):
        pytest.fail("network/runtime/subprocess execution forbidden")

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    monkeypatch.setattr(io, "open", guarded_open)
    monkeypatch.setattr(socket, "socket", denied)
    monkeypatch.setattr(subprocess, "Popen", denied)


@pytest.fixture
def document():
    return checker.read_json(checker.REGISTRY)


def row(document, name):
    return next(item for item in document["datasets"] if item["dataset"] == name)


def test_source_inventory_and_taxonomy_cover_every_publishable_dataset(document):
    counts = checker.validate(document)
    taxonomy = checker.literal_declarations(ROOT / "tools/dataset_classes.py", {"CAPABILITY"})
    assert {entry["dataset"] for entry in document["datasets"]} == set(taxonomy["CAPABILITY"])
    assert counts["datasets"] == len(checker.published_declarations())
    assert counts["historical_records"] == len(checker.read_json(checker.HISTORY)["records"])
    # Refusal and absent provisioning must never make a dataset disappear.
    assert {"api_bank", "nestful", "sotuqa", "tau2_bench"} <= set(checker.published_declarations())


def test_new_declared_dataset_fails_coverage_even_when_its_import_would_fail(document, tmp_path):
    (tmp_path / "data").mkdir()
    for name in checker.published_declarations():
        (tmp_path / "data" / f"{name}.py").write_text('KIND = "dataset"\n')
    (tmp_path / "data" / "new_dataset.py").write_text(
        'KIND = "dataset"\nraise RuntimeError("cannot import")\n')
    (tmp_path / "tools").mkdir()
    original = (ROOT / "tools/dataset_classes.py").read_text()
    (tmp_path / "tools/dataset_classes.py").write_text(original)
    with pytest.raises(checker.RegistryError, match="taxonomy/published declarations differ"):
        checker.validate(document, root=tmp_path)


def test_fixtures_are_not_published_and_metadata_is_never_executed(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "fixture.py").write_text('KIND = "fixture"\nraise AssertionError\n')
    (tmp_path / "data" / "default.py").write_text('raise AssertionError\n')
    (tmp_path / "data" / "published.py").write_text('KIND: str = "dataset"\nraise AssertionError\n')
    assert checker.published_declarations(tmp_path) == ("published",)


@pytest.mark.parametrize("mutation, message", [
    ("missing", "missing published datasets"),
    ("duplicate", "duplicate dataset"),
    ("fixture", "unpublished dataset"),
    ("demand", "demand x surface drift"),
    ("surface", "demand x surface drift"),
    ("exercises", "exercise drift"),
    ("flat-category", "fields must be"),
    ("unknown-status", "unknown status"),
    ("unknown-family", "unknown blocker family"),
    ("unknown-shared", "unknown shared blocker"),
    ("duplicate-blocker", "duplicate blocker"),
    ("missing-action", "empty text"),
    ("missing-evidence", "evidence required"),
    ("stale-anchor", "stale evidence locator"),
    ("missing-path", "missing evidence"),
    ("escape-path", "must stay inside root"),
    ("authorize", "cannot authorize production"),
])
def test_registry_refuses_incomplete_or_misleading_entries(document, mutation, message):
    target = row(document, "jericho")
    blocker = target["blockers"][0]
    if mutation == "missing":
        document["datasets"].remove(target)
    elif mutation == "duplicate":
        document["datasets"].append(copy.deepcopy(target))
    elif mutation == "fixture":
        target["dataset"] = "demo"
    elif mutation in {"demand", "surface"}:
        target[mutation] = "memory"
    elif mutation == "exercises":
        target["exercises"] = [target["surface"]]
    elif mutation == "flat-category":
        target["category"] = "interactive_fiction"
    elif mutation == "unknown-status":
        blocker["status"] = "ready"
    elif mutation == "unknown-family":
        blocker["family"] = "all-clear"
    elif mutation == "unknown-shared":
        target["shared_blockers"].append("imaginary")
    elif mutation == "duplicate-blocker":
        target["blockers"].append(copy.deepcopy(blocker))
    elif mutation == "missing-action":
        blocker["next_action"] = ""
    elif mutation == "missing-evidence":
        blocker["evidence"] = []
    elif mutation == "stale-anchor":
        blocker["evidence"][0]["locator"] = "fabricated absent journal entry"
    elif mutation == "missing-path":
        blocker["evidence"][0]["path"] = "docs/does-not-exist.txt"
    elif mutation == "escape-path":
        blocker["evidence"][0]["path"] = "../external-receipt.json"
    elif mutation == "authorize":
        document["review"]["production_authorized"] = True
    with pytest.raises(checker.RegistryError, match=message):
        checker.validate(document)


def test_within_task_memory_exercise_does_not_create_a_memory_demand(document):
    target = row(document, "jericho")
    assert target["demand"] == "environment"
    assert target["surface"] == "interactive_fiction"
    assert "memory" in target["exercises"]
    assert not any(entry["demand"] == "memory" for entry in document["datasets"])


@pytest.mark.parametrize("mutation", ["remove", "complete", "zero", "coverage", "path", "id", "move"])
def test_historical_incompletes_cannot_be_removed_reclassified_or_rescored(document, mutation):
    target = row(document, "chessbench_puzzles")
    history = target["historical_runs"][-1]
    if mutation == "remove":
        target["historical_runs"].remove(history)
    elif mutation == "complete":
        history["status"] = "complete"
    elif mutation == "zero":
        history["effect"] = 0.0
    elif mutation == "coverage":
        history["observation"] = "150/150 scored"
    elif mutation == "path":
        history["evidence"][-1]["path"] += ".rewritten"
    elif mutation == "id":
        history["run_id"] = "reused-id"
    elif mutation == "move":
        target["historical_runs"].remove(history)
        row(document, "gsm8k")["historical_runs"].append(history)
    with pytest.raises(checker.RegistryError, match="historical"):
        checker.validate(document)


def test_history_baseline_pin_is_independent_and_checked(document, monkeypatch):
    assert hashlib.sha256(checker.HISTORY.read_bytes()).hexdigest() == checker.HISTORY_SHA256
    monkeypatch.setattr(checker, "HISTORY_SHA256", "0" * 64)
    with pytest.raises(checker.RegistryError, match="baseline pin changed"):
        checker.validate(document)


@pytest.mark.parametrize("record_id", [
    "appworld-initial-infrastructure-smoke", "bird-v4-incomplete", "bird-v5-partial-coverage",
    "chess-original-incomplete", "chess-recovery-incomplete", "ds1000-v4-pending-review",
    "gaia-v2-incomplete", "gaia-v3-incomplete", "hotpot-v4-incomplete",
    "scienceworld-v4-incomplete", "twowiki-original-invalid-pilot",
])
def test_every_reviewed_historical_record_is_required(document, record_id):
    for entry in document["datasets"]:
        entry["historical_runs"] = [record for record in entry["historical_runs"]
                                    if record["record_id"] != record_id]
    with pytest.raises(checker.RegistryError, match=f"removed or changed: {record_id}"):
        checker.validate(document)


def test_history_can_append_without_overwriting_old_records(document):
    target = row(document, "chessbench_puzzles")
    new = copy.deepcopy(target["historical_runs"][-1])
    new["record_id"] = "new-independent-interruption"
    new["run_id"] = "new-run-id"
    target["historical_runs"].append(new)
    assert checker.validate(document)["historical_records"] == 12


def test_new_historical_record_cannot_reuse_an_existing_run_id(document):
    target = row(document, "chessbench_puzzles")
    new = copy.deepcopy(target["historical_runs"][-1])
    new["record_id"] = "different-record-same-run"
    target["historical_runs"].append(new)
    with pytest.raises(checker.RegistryError, match="duplicate historical run ID"):
        checker.validate(document)


@pytest.mark.parametrize("raw", ['{"datasets": [], "datasets": []}', '{"score": NaN}'])
def test_noncanonical_json_is_rejected(tmp_path, raw):
    path = tmp_path / "registry.json"
    path.write_text(raw)
    with pytest.raises(checker.RegistryError):
        checker.read_json(path)


def test_cli_produces_counts_and_nonzero_invalid_result(document, tmp_path, capsys):
    assert checker.main([]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["valid"] is True and output["production_authorized"] is False
    document["datasets"].pop()
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(document))
    assert checker.main(["--registry", str(path)]) == 2
    assert json.loads(capsys.readouterr().out)["valid"] is False
