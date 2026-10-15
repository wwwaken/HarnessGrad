"""Offline characterization for the four-dataset receipt review; no benchmark rows."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def load_source(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def hotpot_boundary(monkeypatch, tmp_path):
    from data.scaffolds.qa import base

    # Import-time QASpec.build normally loads the pool. Supply no rows instead.
    monkeypatch.setattr(base.QASpec, "records", lambda self: [])
    monkeypatch.setattr(base, "parquet_rows", lambda *_: pytest.fail("no benchmark reads"))
    adapter = load_source("hg_b3_hotpot", "data/datasets/hotpotqa.py")
    monkeypatch.setitem(sys.modules, "data.datasets.hotpotqa", adapter)
    check = load_source("hg_b3_qa_check", "data/scaffolds/qa/verify/check.py")
    monkeypatch.chdir(tmp_path)
    (tmp_path / "gold.json").write_text(json.dumps({
        "answer": "answer", "supporting_facts": [["A", 0], ["B", 1]],
    }))

    def run(prediction):
        (tmp_path / "prediction.json").write_text(prediction)
        code = check.main([
            "--dataset", "hotpotqa", "--prediction", "prediction.json",
            "--gold", "gold.json", "--reward-file", "verifier/reward.txt",
            "--evidence-file", "verifier/evidence.json",
        ])
        return (code, json.loads((tmp_path / "verifier/evidence.json").read_text()),
                tmp_path / "verifier/reward.txt")

    return run


@pytest.mark.parametrize("prediction", [
    "{",
    json.dumps({"schema_version": 1, "answer": "answer", "predicted_evidence": "A"}),
    json.dumps({"schema_version": 1, "answer": "answer", "predicted_evidence": [["A", True]]}),
    json.dumps({"schema_version": 1, "answer": "answer", "predicted_evidence": [["A", -1]]}),
])
def test_hotpot_malformed_predictions_are_unmeasured(hotpot_boundary, prediction):
    code, evidence, reward = hotpot_boundary(prediction)
    assert code == 3
    assert evidence["measured"] is False
    assert "prediction file" in evidence["error"]
    assert not reward.exists()


@pytest.mark.parametrize("support, expected", [
    ({}, 0.0),
    ({"predicted_evidence": []}, 0.0),
    ({"predicted_evidence": [["A", 0]]}, 0.0),
    ({"predicted_evidence": [["A", 0], ["B", 1]]}, 1.0),
])
def test_hotpot_valid_support_uses_joint_em(hotpot_boundary, support, expected):
    code, evidence, reward = hotpot_boundary(json.dumps({
        "schema_version": 1, "answer": "answer", **support,
    }))
    assert code == (0 if expected else 1)
    assert evidence["measured"] is True
    assert float(reward.read_text()) == expected
    assert evidence["official"]["em"] == 1.0
    assert evidence["official"]["joint_em"] == expected


def test_timeout_detail_alone_does_not_close_aggregation_gate(monkeypatch, tmp_path):
    from eval.verification import verifier
    from eval.run import runner

    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired("synthetic verifier", 1)

    monkeypatch.setattr(verifier.subprocess, "run", timeout)
    verdict = verifier._verify(
        tmp_path, {"kind": "command", "argv": ["synthetic-check"]}, "",
        sandbox=False, timeout_s=1, env={"kind": "files"},
    )
    assert "timed out" in verdict["detail"]
    assert "score" not in verdict
    assert verdict["outcome"] == "timeout"
    assert verdict["unmeasured"] == verdict["detail"]
    monkeypatch.setattr(runner, "run_one", lambda *a, **kw: {
        "verdict": verdict, "trace": "", "exit_code": 0, "stderr": "",
    })
    result = runner._evaluate(tmp_path, [{"task_id": "synthetic-timeout"}], {}, trials=1)
    # The originally demonstrated fallback is now explicitly unmeasured.
    assert result["per_task"] == {}
    assert result["invalid"]["synthetic-timeout"] == {
        "stage": "check", "outcome": "timeout", "detail": verdict["detail"]}


@pytest.mark.parametrize("failure, measured", [("prediction", True), ("gold", False)])
def test_bird_schema_failure_depends_on_which_query_failed(monkeypatch, tmp_path, failure, measured):
    import sqlite3

    check = load_source("hg_b3_bird_check", "data/datasets/bird_minidev/verify/check.py")
    db = tmp_path / "database.sqlite"
    with sqlite3.connect(db) as connection:
        connection.execute("create table t (value integer)")
        connection.execute("insert into t values (1)")
    good, bad = "select value from t", "select missing_column from t"
    (tmp_path / "gold.sql").write_text(bad if failure == "gold" else good)
    (tmp_path / "answer.sql").write_text(bad if failure == "prediction" else good)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["check", "--db", str(db), "--gold", "gold.sql",
                                     "--pred", "answer.sql"])
    assert check.main() == (0 if measured else 3)
    evidence = json.loads((tmp_path / "verifier/evidence.json").read_text())
    assert evidence["measured"] is measured
    reward = tmp_path / "verifier/reward.txt"
    assert reward.exists() is measured
    if measured:
        assert float(reward.read_text()) == 0.0
    assert "missing_column" in evidence.get("why", evidence.get("error", ""))


def test_ds1000_timeout_result_needs_classification_beyond_measured_flag(monkeypatch, tmp_path):
    check = load_source("hg_b3_ds1000_check", "data/datasets/ds1000/verify/check.py")
    monkeypatch.chdir(tmp_path)
    (tmp_path / "context.json").write_text(json.dumps({"code_context": "# synthetic"}))
    (tmp_path / "execution.py").write_text("# inert synthetic verifier input\n")
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    monkeypatch.setattr(check.tempfile, "mkdtemp", lambda *a, **kw: str(scratch))
    monkeypatch.setattr(check.subprocess, "run", lambda *a, **kw:
                        subprocess.CompletedProcess(a, 0, '{"passed":false,"result":"timed out"}', ""))
    monkeypatch.setattr(sys, "argv", ["check"])
    assert check.main() == 0
    evidence = json.loads((tmp_path / "verifier/evidence.json").read_text())
    assert evidence["measured"] is True
    assert evidence["official"]["result"] == "timed out"
    assert float((tmp_path / "verifier/reward.txt").read_text()) == 0.0


@pytest.mark.parametrize("dataset, active_id, status, retired", [
    ("alfworld", None, None, "current-runtime-identity"),
    ("bird_minidev", "sql-coverage-reconciliation", "measurement", None),
    ("ds1000", "host-slice-archive-review", "measurement", None),
    ("hotpotqa", "historical-comparison-receipts", "measurement", "timeout-aggregation-admission"),
])
def test_review_preserves_unresolved_gates_and_original_history(dataset, active_id, status, retired):
    document = json.loads((ROOT / "registry/dataset-blockers.json").read_text())
    baseline = json.loads((ROOT / "tests/fixtures/dataset_blockers/history-codex178.json").read_text())
    target = next(row for row in document["datasets"] if row["dataset"] == dataset)
    blockers = {item["id"]: item for item in target["blockers"]}
    # hotpotqa joined the withdrawn branch on 2026-10-15 when its blocker closed under reading (A)
    # (registry/blocker-closure-assessment.md, "Closed under reading A - hotpotqa"). Its withdrawal
    # section carries a longer header than the other two, so it is looked up explicitly rather than
    # interpolated, and its own wording is asserted below.
    withdrawn = dataset in {"bird_minidev", "ds1000", "hotpotqa"}
    if withdrawn:
        assert active_id not in blockers
        withdrawal = (ROOT / "registry/withdrawn-requirements.md").read_text(encoding="utf-8")
        header = (f"### `{dataset} / {active_id} / original-v4-receipts`" if dataset == "hotpotqa"
                  else f"### `{dataset} / {active_id}`")
        section = withdrawal.split(header, 1)[1].split("\n##", 1)[0]
        assert "**Searched:**" in section
        if dataset == "bird_minidev":
            assert "the tracked-source inventory" in section
            assert "only summaries exist" in section
            assert "**not present in\nthis repository**" in section
            assert "not published upstream" in section
        elif dataset == "hotpotqa":
            # The wording that distinguishes HotpotQA from the never-captured pair: these receipts
            # existed and were lost, so "not published upstream" would have overstated the case.
            assert "**local pilot of this platform**" in section
            assert "the receipts existed and were" in section
            assert "lost, rather than never being captured" in section
            assert "`hotpotqa-h0-10pct-v4`" in section
            assert "`historical_runs` keeps `run_id=null` and `effect=null`" in section
            assert "`/tmp/harnessgrad-runs/hotpotqa-h0-10pct-v4`" in section
        else:
            assert "the same inventory" in section
            assert "**do not exist in the repository**" in section
            assert "`ds1000-v4-pending-review`" in section
            assert "`effect=null`" in section
    elif active_id is not None:
        assert blockers[active_id]["status"] == status
    if retired:
        assert retired not in blockers
    # BIRD/DS1000's old B3 citation membership checks lost their active carriers.
    # Their failed archive searches are checked above.
    if active_id is not None and not withdrawn:
        locator = {
            "hotpotqa": "## HotpotQA: schema/timeout review closed; timeout aggregation still blocked",
        }[dataset]
        assert {"kind": "external-reference", "path": "/site/measurement-coverage-hg-b3-review.md",
                "locator": locator} in blockers[active_id]["evidence"]
    elif active_id is None:
        # w-alf established current selected noop/scorer/limits/cleanup identity.
        # Raw scorer zero is distinct from deliberately withheld publication.
        assert dataset == "alfworld" and blockers == {}
        assert "current-runtime-review" not in blockers
        journal = (ROOT / "docs/adapter-integration-journal.md").read_text()
        assert 'reports/w-alf-receipts.md` ("## CLOSED: alfworld / current-runtime-identity")' in journal
    assert target["historical_runs"] == [
        item["record"] for item in baseline["records"] if item["dataset"] == dataset]
    if dataset == "hotpotqa":
        assert "schema-timeout-measurement" not in blockers
        # Track the live shared set instead of a hardcoded list. `runtime-observations`
        # closed after this assertion was written; a literal here would silently stop
        # meaning "carries every shared gate" the moment the shared set changes again.
        assert set(target["shared_blockers"]) == {
            item["id"] for item in document["shared_blockers"]}
        if withdrawn:
            # The blocker is gone, so the timeout-closure citation moved to the closure record.
            # The exact evidence pair is asserted there rather than dropped.
            assessment = (ROOT / "registry/blocker-closure-assessment.md").read_text(encoding="utf-8")
            assert "/site/w-hotpot-timeout-closure.md" in assessment
            assert ("# HotpotQA timeout outcome/persistence/aggregation closure - w-hotpot"
                    in assessment)
        else:
            assert {"kind": "external-reference", "path": "/site/w-hotpot-timeout-closure.md",
                    "locator": "# HotpotQA timeout outcome/persistence/aggregation closure - w-hotpot"
                    } in blockers[active_id]["evidence"]
    else:
        assert set(target["shared_blockers"]) == {item["id"] for item in document["shared_blockers"]}
    assert document["review"]["production_authorized"] is False


def test_archived_alfworld_runtime_receipts(site_archive):
    report = site_archive("/site/w-alf-receipts.md").read_text()
    assert "## CLOSED: alfworld / current-runtime-identity" in report
    evidence = site_archive("/site/w-alf-evidence/execution/diagnostic_receipt.json").parents[1]
    receipt = json.loads((evidence / "execution/diagnostic_receipt.json").read_text())
    raw = json.loads((evidence / "runtime-attempt/run-one-result.json").read_text())
    assert receipt["score"] is None
    assert receipt["coverage"]["invalid_trials"] == 0
    assert receipt["coverage"]["unmeasured_trials"] == 1
    assert receipt["enforcement"]["production_authorized"] is False
    assert raw["verdict"]["scorer_isolation_class"] == "actor-workdir"
    assert raw["verdict"]["evidence"]["measured"] is True
    assert raw["verdict"]["score"] == 0.0
    assert raw["runtime_boundary"]["agent_timeout_s"] == 3600
    assert raw["runtime_boundary"]["verifier_timeout_s"] == 300
    bindings = json.loads((evidence / "artifact-bindings.json").read_text())
    assert bindings["oracle_actions_present"] is False
    assert bindings["walkthrough_present"] is False
    assert all(row["equal"] for row in bindings["materialized_inputs"].values())
    cleanup = json.loads((evidence / "cleanup-observations.json").read_text())
    assert not any(row["exists_after"] for row in cleanup["temporary_directories"])
