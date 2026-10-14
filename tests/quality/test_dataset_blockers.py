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


def test_every_journal_coverage_dataset_points_to_a_checked_in_review(document):
    """Every `journal-coverage` closure must point at a review that states its disposition.

    Deliberately convention-free about *how* the review is filed. Two reviews landed in
    parallel and named things differently -- one file per dataset with `Closed:`/`Next:`,
    one file with per-dataset sections using `CLOSED:`/`OPEN:` -- and a guard that demanded
    one worker's heading text would have reported the other worker's real work as missing,
    which is how a guard gets weakened later. What is actually required is that the review
    exists, is checked in, is about *this* dataset, and says both what it closed and what it
    left open. Those four things are checked; the wording is not.
    """
    CLOSED = ("CLOSED:", "Closed:", "Closed at source-review level:")
    OPEN = ("OPEN:", "Next:", "Still open")
    covered = set()
    for entry in document["datasets"]:
        for blocker in entry["blockers"]:
            if blocker["family"] != "journal-coverage":
                continue
            name = entry["dataset"]
            reviews = []
            for evidence in blocker["evidence"]:
                if evidence["kind"] != "repository":
                    continue
                relative = Path(evidence["path"])
                if not (relative.parts and relative.parts[0] == "docs"
                        and relative.suffix == ".md"):
                    continue
                assert not relative.is_absolute() and ".." not in relative.parts
                path = ROOT / relative
                assert path.resolve().is_relative_to(ROOT.resolve())
                assert path.is_file(), f"{name}: missing checked-in review {relative}"
                source = path.read_text(encoding="utf-8")
                headings = [line for line in source.splitlines()
                            if line.lstrip().startswith("#")]
                # Dataset names and prose titles differ in word breaks (`physicsquestions`
                # against "Physics Questions"), so compare on a normalised form rather than
                # requiring one spelling.
                def _norm(text):
                    return "".join(ch for ch in text.lower() if ch.isalnum())
                assert any(_norm(name) in _norm(h) for h in headings), \
                    f"{name}: {relative} has no heading naming this dataset"
                assert any(m in source for m in CLOSED), \
                    f"{name}: {relative} does not say what it closed"
                assert any(m in source for m in OPEN), \
                    f"{name}: {relative} does not say what it left open"
                reviews.append(path)
                break
            assert reviews, f"{name}: registry must point at its checked-in source review"
            covered.add(name)
    assert covered, "journal-coverage guard must not silently become vacuous"
    expected = {e["dataset"] for e in document["datasets"]
                for b in e["blockers"] if b["family"] == "journal-coverage"}
    assert covered == expected, \
        f"guard did not reach every journal-coverage dataset: {sorted(expected - covered)}"


def test_new_declared_dataset_fails_coverage_even_when_its_import_would_fail(document, tmp_path):
    (tmp_path / "data" / "datasets").mkdir(parents=True)
    for name in checker.published_declarations():
        (tmp_path / "data" / "datasets" / f"{name}.py").write_text('KIND = "dataset"\n')
    (tmp_path / "data" / "datasets" / "new_dataset.py").write_text(
        'KIND = "dataset"\nraise RuntimeError("cannot import")\n')
    (tmp_path / "tools").mkdir()
    original = (ROOT / "tools/dataset_classes.py").read_text()
    (tmp_path / "tools/dataset_classes.py").write_text(original)
    with pytest.raises(checker.RegistryError, match="taxonomy/published declarations differ"):
        checker.validate(document, root=tmp_path)


def test_fixtures_are_not_published_and_metadata_is_never_executed(tmp_path):
    (tmp_path / "data" / "datasets").mkdir(parents=True)
    (tmp_path / "data" / "datasets" / "fixture.py").write_text('KIND = "fixture"\nraise AssertionError\n')
    (tmp_path / "data" / "datasets" / "default.py").write_text('raise AssertionError\n')
    (tmp_path / "data" / "datasets" / "published.py").write_text('KIND: str = "dataset"\nraise AssertionError\n')
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


def test_agentdojo_metadata_closure_keeps_the_production_route_blocked(document):
    blockers = {item["id"]: item for item in row(document, "agentdojo")["blockers"]}
    assert "selected-metadata-review" not in blockers
    production = blockers["production-route-admission"]
    assert production["status"] == "runtime"
    assert production["family"] == "trusted-verifier-runtime"
    assert document["review"]["production_authorized"] is False
    evidence = {item["path"] for item in production["evidence"]}
    assert "docs/adapter-integration-journal.md" in evidence
    assert "reports/agentdojo-metadata-privacy-codex180-report.md" in evidence


def test_scienceworld_code_review_keeps_runtime_and_v4_history_blocked(document):
    target = row(document, "scienceworld")
    blocker = next(item for item in target["blockers"]
                   if item["id"] == "prevent-platform-writes")
    assert blocker["status"] == "runtime"
    assert blocker["family"] == "platform-integrity"
    evidence = {item["path"] for item in blocker["evidence"]}
    assert "tests/quality/test_scienceworld_platform_writes_codex186.py" in evidence
    assert "tests/quality/test_scienceworld_integrity_codex181.py" in evidence
    assert "reports/scienceworld-platform-writes-codex186-report.md" in evidence
    assert "runtime-observations" in target["shared_blockers"]
    assert document["review"]["production_authorized"] is False
    baseline = checker.read_json(checker.HISTORY)
    assert target["historical_runs"] == [
        item["record"] for item in baseline["records"] if item["dataset"] == "scienceworld"
    ]
    assert target["historical_runs"][0]["status"] == "incomplete"
    assert target["historical_runs"][0]["effect"] is None


def test_bfcl_ast_work_remains_blocked_on_independent_source_and_index_custody(document):
    blockers = {item["id"]: item for item in row(document, "bfcl_v3")["blockers"]}
    assert blockers["release-index-custody"]["status"] == "external"
    ast_contract = blockers["simple-ast-contract"]
    assert ast_contract["status"] == "external"
    assert ast_contract["family"] == "official-scorer-execution"
    assert "tests/fixtures/bfcl_ast_source/README.md" in {
        item["path"] for item in ast_contract["evidence"]}
    assert document["review"]["production_authorized"] is False


def test_twowiki_source_closure_keeps_dependency_and_data_gates_external(document):
    target = row(document, "twowikimultihopqa")
    blockers = {item["id"]: item for item in target["blockers"]}
    assert "independent-evaluator-source" not in blockers
    assert "independent-evaluator-source" not in target["shared_blockers"]
    for blocker_id, family in (
        ("ujson-native-offline-closure", "scorer-dependency-network"),
        ("hub-data-provenance", "source-provenance"),
    ):
        blocker = blockers[blocker_id]
        assert blocker["status"] == "external"
        assert blocker["family"] == family
        assert "docs/task-206-twowiki-provenance-review.md" in {
            item["path"] for item in blocker["evidence"]
        }


def test_twowiki_source_closure_preserves_shared_gates_and_mixed_metric_history(document):
    target = row(document, "twowikimultihopqa")
    # `paired-filesystem-quotas` was withdrawn by operator decision on 2026-10-15; see
    # `docs/filesystem-quota-decision.md`. It is removed from this set deliberately and
    # visibly rather than by loosening the assertion: enforcement still does not exist, the
    # decision was that the platform does not require it.
    assert set(target["shared_blockers"]) == {
        "runtime-observations", "scorer-offline-closure",
        "pristine-verifier", "artifact-only-state-export", "official-scorer-identity",
        "snapshot-owned-cleanup", "pilot-guidance-conflict",
    }
    assert "paired-filesystem-quotas" not in target["shared_blockers"]
    comparability = next(item for item in target["blockers"]
                         if item["id"] == "recovery-comparability")
    assert comparability["status"] == "measurement"
    assert comparability["family"] == "metric-comparability"
    baseline = checker.read_json(checker.HISTORY)
    assert target["historical_runs"] == [
        item["record"] for item in baseline["records"]
        if item["dataset"] == "twowikimultihopqa"
    ]
    original, = target["historical_runs"]
    assert original["record_id"] == "twowiki-original-invalid-pilot"
    assert original["run_id"] is None
    assert original["status"] == "partial-measurement"
    assert original["effect"] is None
    for fact in ("48 scored tasks", "two malformed-output invalids",
                 "mixed legacy Answer F1/structured Joint F1"):
        assert fact in original["observation"]
    assert document["review"]["production_authorized"] is False


def test_twowiki_task_capability_is_separate_from_harness_exercises(document):
    target = row(document, "twowikimultihopqa")
    assert (target["demand"], target["surface"]) == ("evidence", "information_seeking")
    assert target["exercises"] == ["context"]
    assert "category" not in target



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


def test_chess_future_launch_guidance_requires_new_ids_and_preserves_history(document):
    target = row(document, "chessbench_puzzles")
    assert "recovery-id-conflict" not in {blocker["id"] for blocker in target["blockers"]}
    assert "interruption-closure" in {blocker["id"] for blocker in target["blockers"]}
    baseline = checker.read_json(checker.HISTORY)
    assert target["historical_runs"] == [
        item["record"] for item in baseline["records"]
        if item["dataset"] == "chessbench_puzzles"
    ]
    journal = (ROOT / "docs/adapter-integration-journal.md").read_text(encoding="utf-8")
    audit = next(line for line in journal.splitlines()
                 if line.startswith("- Interruption audit: termination authority is undetermined"))
    guidance = (ROOT / "docs/dataset-blockers.md").read_text(encoding="utf-8")
    for text in (audit, " ".join(guidance.split())):
        assert "Every future attempt must use a genuinely new unique run ID" in text
        assert "never resume or overwrite any used run ID" in text
        for history in target["historical_runs"]:
            assert history["status"] == "incomplete" and history["effect"] is None
            assert f'`{history["run_id"]}`' in text
            assert f'launch a fresh `{history["run_id"]}`' not in journal


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
