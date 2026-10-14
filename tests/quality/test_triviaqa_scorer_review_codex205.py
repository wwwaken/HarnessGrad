"""Synthetic scorer review; shared fixtures forbid payload reads and network access."""
import json
import string
import sys

import pytest

from tests.quality.test_triviaqa_official_scorer import (
    FIXTURE,
    no_network,  # noqa: F401 - autouse pytest fixture
    read_upstream_fixture,
    triviaqa,  # noqa: F401 - payload-free pytest fixture
    upstream_em_namespace,
)


def test_punctuation_and_unicode_normalization_match_original_source(triviaqa):
    upstream = upstream_em_namespace(read_upstream_fixture())
    # Cover the corrected separator set and Unicode characters upstream preserves.
    separators = tuple(string.punctuation + "‘’´") + ("–", "—", "“", "”", "\t", "\n")
    for separator in separators:
        for text in (f"Red{separator}Blue", f"The{separator}A-Team"):
            assert triviaqa.normalize_answer(text) == upstream["normalize_answer"](text), text
            assert triviaqa.exact_match_score(text, "red blue") == upstream[
                "exact_match_score"](text, "red blue"), text


@pytest.mark.parametrize("kind", ["normalized_aliases", "human_answers", "mixed"])
def test_match_after_alias_200_survives_gold_materialization(triviaqa, kind):
    upstream = upstream_em_namespace(read_upstream_fixture())
    aliases = [f"synthetic nonmatching alias {i}" for i in range(200)]
    target = "The Invented_Blue-Town!"
    if kind == "normalized_aliases":
        normalized, human = aliases + [upstream["normalize_answer"](target)], []
    elif kind == "human_answers":
        normalized, human = [], aliases + [target]
    else:
        normalized, human = aliases, [target]
    official_gold = upstream["get_ground_truths"]({
        "NormalizedAliases": normalized, "HumanAnswers": human})
    gold = triviaqa._gold({"answer": {
        "value": aliases[0], "normalized_aliases": normalized, "human_answers": human}})
    expected = upstream["metric_max_over_ground_truths"](
        upstream["exact_match_score"], target, official_gold)
    assert expected == 1
    assert triviaqa.score(target, gold)["reward"] == float(expected)
    assert gold["accepted"] == official_gold
    assert gold["accepted_total"] == len(official_gold) == 201


@pytest.mark.parametrize("prediction", ["Invented Blue Town", "wrong"])
def test_verifier_records_new_adapter_identity_and_pinned_reference(
        triviaqa, monkeypatch, tmp_path, prediction):
    from data.scaffolds.qa.verify import check

    read_upstream_fixture()
    receipt = json.loads((FIXTURE / "provenance.json").read_text())
    monkeypatch.setitem(sys.modules, "data.triviaqa", triviaqa)
    monkeypatch.chdir(tmp_path)
    (tmp_path / "answer.txt").write_text(prediction)
    gold = triviaqa._gold({"answer": {
        "value": "Invented Blue Town", "normalized_aliases": ["invented blue town"]}})
    (tmp_path / "gold.json").write_text(json.dumps(gold))
    assert check.main([
        "--dataset", "triviaqa", "--reward-file", "reward.txt",
        "--evidence-file", "evidence.json"]) == (0 if prediction != "wrong" else 1)
    evidence = json.loads((tmp_path / "evidence.json").read_text())
    assert evidence["measured"] is True
    assert evidence["official"]["scorer_identity"] == (
        "triviaqa-alias-max-em-upstream-normalization-all-aliases-v2")
    assert evidence["official"]["reference"] == {
        "repository": receipt["repository"], "commit": receipt["commit"],
        "source_path": receipt["source_path"],
        "source_sha256": receipt["files"][receipt["source_path"]]["sha256"],
    }
    assert "f1" not in evidence["official"]
