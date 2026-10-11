"""Structured QA predictions preserve legacy text scoring and official evidence metrics."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def test_prediction_schema_is_closed_and_pair_typed():
    from data.qa.prediction import validate_prediction

    good = {"schema_version": 1, "answer": "SUPPORTS",
            "predicted_evidence": [["Page", 0]]}
    assert validate_prediction(good) == (good, None)
    assert validate_prediction({"schema_version": 1, "answer": "x", "gold": "y"})[1]
    assert validate_prediction({"schema_version": 1, "predicted_evidence": []})[1]
    assert validate_prediction({"schema_version": 1, "answer": "x",
                                "predicted_evidence": [["Page", True]]})[1]


@pytest.mark.parametrize("evidence", [[], [["A", 0], ["B", 1], ["C", 2],
                                           ["D", 3], ["E", 4], ["F", 5]]])
def test_cli_validates_structured_prediction_and_stores_only_it(tmp_path, evidence):
    cli = ROOT / "data/qa/cli/qa"
    (tmp_path / "input.json").write_text(json.dumps({
        "schema_version": 1, "answer": "SUPPORTS", "predicted_evidence": evidence,
    }))
    proc = subprocess.run([sys.executable, str(cli), "submit-json", "@input.json"],
                          cwd=tmp_path, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert json.loads((tmp_path / "prediction.json").read_text())["answer"] == "SUPPORTS"
    assert not (tmp_path / "answer.txt").exists()


def test_prediction_artifacts_are_scoped_to_each_task_workdir(tmp_path):
    cli = ROOT / "data/qa/cli/qa"
    first, second = tmp_path / "task-a", tmp_path / "task-b"
    first.mkdir()
    second.mkdir()
    (first / "input.json").write_text(json.dumps({"schema_version": 1, "answer": "A"}))
    subprocess.run([sys.executable, str(cli), "submit-json", "@input.json"], cwd=first,
                   check=True, capture_output=True, text=True)
    subprocess.run([sys.executable, str(cli), "submit", "B"], cwd=second,
                   check=True, capture_output=True, text=True)
    assert (first / "prediction.json").is_file()
    assert not (second / "prediction.json").exists()
    assert (second / "answer.txt").read_text() == "B\n"


def test_cli_rejects_gold_and_malformed_json(tmp_path):
    cli = ROOT / "data/qa/cli/qa"
    (tmp_path / "input.json").write_text('{"schema_version":1,"answer":"x","gold":1}')
    bad_schema = subprocess.run([sys.executable, str(cli), "submit-json", "@input.json"],
                                cwd=tmp_path, capture_output=True, text=True)
    assert bad_schema.returncode == 2
    (tmp_path / "input.json").write_text("{")
    malformed = subprocess.run([sys.executable, str(cli), "submit-json", "@input.json"],
                               cwd=tmp_path, capture_output=True, text=True)
    assert malformed.returncode == 2
    assert not (tmp_path / "prediction.json").exists()


def test_verifier_marks_malformed_structured_json_unmeasured(tmp_path):
    from data.qa import base

    # Materialize the isolated QA check package. Parsing happens before importing the
    # adapter, so the check can reject bad JSON without any dataset data being present.
    check_dir = tmp_path / "qa/lib/verify"
    check_dir.mkdir(parents=True)
    (check_dir / "check.py").write_bytes((ROOT / "data/qa/verify/check.py").read_bytes())
    (tmp_path / "data/qa").mkdir(parents=True)
    (tmp_path / "data/qa/prediction.py").write_bytes((ROOT / "data/qa/prediction.py").read_bytes())
    (tmp_path / "gold.json").write_text('{"answer":"x"}')
    (tmp_path / "prediction.json").write_text("{")
    env = dict(os.environ, PYTHONPATH=str(tmp_path))
    proc = subprocess.run([sys.executable, str(check_dir / "check.py"),
                           "--dataset", "fever", "--prediction", "prediction.json",
                           "--gold", "gold.json", "--reward-file", "verifier/reward.txt",
                           "--evidence-file", "verifier/evidence.json"],
                          cwd=tmp_path, env=env, capture_output=True, text=True)
    assert proc.returncode == 3
    assert not (tmp_path / "verifier/reward.txt").exists()
    assert json.loads((tmp_path / "verifier/evidence.json").read_text())["measured"] is False


def test_fever_prediction_uses_strict_evidence_and_nei_exemption():
    from data.fever import score, score_prediction

    gold = {"answer": "SUPPORTS", "evidence": [[[None, None, "P", 0]] ]}
    missing = score("SUPPORTS", gold)
    assert missing["reward"] == 0.0
    assert score_prediction({"answer": "SUPPORTS", "predicted_evidence": [["P", 0]]},
                            gold)["reward"] == 1.0
    nei = {"answer": "NOT ENOUGH INFO", "evidence": []}
    assert score_prediction({"answer": "NOT ENOUGH INFO"}, nei)["reward"] == 1.0
    six = [["wrong", i] for i in range(5)] + [["P", 0]]
    assert score_prediction({"answer": "SUPPORTS", "predicted_evidence": six},
                            gold)["reward"] == 0.0


def test_hotpot_uses_answer_metrics_and_joint_exact_set():
    from data.hotpotqa import score, score_prediction

    gold = {"answer": "The answer", "supporting_facts": [["A", 0], ["B", 1]]}
    missing = score("answer", gold)
    assert missing["reward"] == 0.0
    correct = score_prediction({"answer": "answer", "predicted_evidence": [
        ["A", 0], ["B", 1]]}, gold)
    assert correct["official"]["joint_em"] == 1.0
    partial = score_prediction({"answer": "answer", "predicted_evidence": [["A", 0]]}, gold)
    assert partial["official"]["joint_em"] == 0.0


def test_evidence_is_in_verifier_gold_only_and_adapters_are_loadable():
    import data.fever as fever
    import data.hotpotqa as hotpot

    for module, field in ((fever, "evidence"), (hotpot, "supporting_facts")):
        spec = module.VERIFY[next(iter(module.VERIFY))]
        gold_entry = next(entry for entry in spec["inputs"] if entry["path"] == "gold.json")
        assert field in json.loads(gold_entry["content"])
        assert field not in module.load()[0][0]
        assert "gold" not in module.load()[0][0]["goal"].lower()
        assert "prediction.json" in module.load()[0][0]["goal"]


def test_oracle_prediction_has_gold_evidence_only_in_control_path():
    from data.qa.control import _oracle_prediction
    import data.fever as fever
    record = {"gold": {"answer": "SUPPORTS",
                       "evidence": [[[None, None, "P", 0]]]}}
    assert _oracle_prediction(fever, record) == {
        "schema_version": 1, "answer": "SUPPORTS", "predicted_evidence": [["P", 0]]}


def test_legacy_adapter_scores_still_take_strings():
    from data.gsm8k import score as gsm_score
    from data.triviaqa import score as trivia_score

    assert gsm_score("#### 42", {"answer": "42"})["reward"] == 1.0
    assert trivia_score("Paris", {"accepted": ["paris"]})["reward"] == 1.0
