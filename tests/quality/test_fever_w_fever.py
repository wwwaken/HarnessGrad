"""Synthetic FEVER grouping and metric-identity regressions; no dataset execution."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from data.datasets import fever
from data.scaffolds.qa.evidence_scorers import fever_is_strictly_correct


@pytest.mark.parametrize("label", ["SUPPORTS", "REFUTES"])
def test_flat_export_requires_both_sentences(label):
    evidence = [["A", "0", "first required sentence"],
                ["B", "1", "second required sentence"]]
    before = json.dumps(evidence)
    assert not fever_is_strictly_correct(label, label, evidence, [["A", 0]])
    assert not fever_is_strictly_correct(label, label, evidence, [["B", 1]])
    assert fever_is_strictly_correct(label, label, evidence, [["B", 1], ["A", 0]])
    assert not fever_is_strictly_correct(label, "NOT ENOUGH INFO", evidence,
                                        [["A", 0], ["B", 1]])
    assert json.dumps(evidence) == before


def test_nested_official_alternatives_still_require_a_complete_group():
    evidence = [[[1, 2, "A", 0], [3, 4, "B", 1]], [[5, 6, "C", 2]]]
    assert not fever_is_strictly_correct("SUPPORTS", "SUPPORTS", evidence, [["A", 0]])
    assert fever_is_strictly_correct("SUPPORTS", "SUPPORTS", evidence, [["C", 2]])
    assert fever_is_strictly_correct("SUPPORTS", "SUPPORTS", evidence,
                                     [["A", 0], ["B", 1]])


def test_nested_triples_preserve_alternative_groups():
    evidence = [[["A", "0", "first"], ["B", "1", "second"]],
                [["C", "2", "alternative"]]]
    assert not fever_is_strictly_correct("REFUTES", "REFUTES", evidence, [["A", 0]])
    assert fever_is_strictly_correct("REFUTES", "REFUTES", evidence, [["C", 2]])


def test_prefix_order_duplicates_and_overlong_groups():
    evidence = [["A", "0", "first"], ["B", "1", "second"]]
    assert not fever_is_strictly_correct("SUPPORTS", "SUPPORTS", evidence,
                                        [["A", 0]] * 5 + [["B", 1]])
    assert fever_is_strictly_correct("SUPPORTS", "SUPPORTS", evidence,
                                     [["A", 0]] * 4 + [["B", 1]])
    six = [["Page", str(i), "required"] for i in range(6)]
    assert not fever_is_strictly_correct("SUPPORTS", "SUPPORTS", six,
                                        [["Page", i] for i in range(6)])


@pytest.mark.parametrize("prediction", [{"answer": "supports"},
                                       {"answer": "supports", "predicted_evidence": []}])
def test_missing_evidence_has_zero_strict_reward_but_correct_label_counts(prediction):
    result = fever.score_prediction(prediction, {"answer": "SUPPORTS", "evidence": []})
    assert result["reward"] == 0.0
    assert result["official"]["metric"] == fever.REWARD_METRIC
    counts = result["official"]["classification"]
    assert counts["metric"] == "classification_macro_f1"
    assert counts["per_label"]["SUPPORTS"] == {"tp": 1, "fp": 0, "fn": 0}
    assert counts["per_label"]["REFUTES"] == {"tp": 0, "fp": 0, "fn": 0}


def test_nei_exemption_and_exact_label_comparison():
    gold = {"answer": "NOT ENOUGH INFO", "evidence": []}
    assert fever.score("NOT ENOUGH INFO", gold)["reward"] == 1.0
    result = fever.score("NOT ENOUGH INFO.", gold)
    assert result["reward"] == 0.0
    assert result["official"]["classification"]["per_label"]["NOT ENOUGH INFO"]["fn"] == 1


def test_macro_f1_is_aggregated_from_counts_not_per_task_accuracy():
    pairs = [("SUPPORTS", "SUPPORTS"), ("SUPPORTS", "REFUTES"),
             ("REFUTES", "REFUTES"), ("NOT ENOUGH INFO", "NOT ENOUGH INFO")]
    counts = {label: {key: 0 for key in ("tp", "fp", "fn")} for label in fever.LABELS}
    for gold, prediction in pairs:
        result = fever.score(prediction, {"answer": gold, "evidence": []})
        for label, values in result["official"]["classification"]["per_label"].items():
            for key, value in values.items():
                counts[label][key] += value
    f1s = []
    for values in counts.values():
        denominator = 2 * values["tp"] + values["fp"] + values["fn"]
        f1s.append(2 * values["tp"] / denominator if denominator else 0.0)
    assert sum(f1s) / 3 == pytest.approx(7 / 9)
    assert sum(f1s) / 3 != pytest.approx(3 / 4)


def test_isolated_synthetic_verifier_emits_both_metric_records(tmp_path):
    record = {"task_id": "fever/validation/synthetic-w-fever",
              "gold": {"answer": "SUPPORTS", "evidence": [
                  ["A", "0", "first required sentence"],
                  ["B", "1", "second required sentence"]]}}
    spec = fever._SPEC.verifier(record)
    for entry in spec["inputs"]:
        path = tmp_path / entry["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        if "content" in entry:
            path.write_text(entry["content"], encoding="utf-8")
        else:
            path.write_bytes(Path(entry["from"]).read_bytes())
    (tmp_path / "prediction.json").write_text(json.dumps({
        "schema_version": 1, "answer": "SUPPORTS", "predicted_evidence": [["A", 0]]}))
    proc = subprocess.run(spec["argv"], cwd=tmp_path,
                          env=dict(os.environ, PYTHONPATH=str(tmp_path)),
                          text=True, capture_output=True)
    assert proc.returncode == 1, (proc.stdout, proc.stderr)  # Valid measured zero.
    result = json.loads((tmp_path / "verifier/evidence.json").read_text())
    assert result["measured"] is True  # Synthetic verifier contract only.
    assert result["reward"] == 0.0
    assert result["official"]["metric"] == fever.REWARD_METRIC
    assert result["official"]["classification"]["per_label"]["SUPPORTS"]["tp"] == 1
    assert float((tmp_path / "verifier/reward.txt").read_text()) == 0.0
