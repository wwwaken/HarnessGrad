"""TriviaQA's official scorer, copied in, and a differential test against our check.

The rule this file exists to enforce
------------------------------------
The official scorer is `evaluation/triviaqa_evaluation.py` in `mandarjoshi/trivia_qa`.
The metric is **not** "does the prediction equal the answer string": it is

    metric_max_over_ground_truths(exact_match_score, prediction, get_ground_truths(answer))

-- one hit among **any** alias counts. The alias set comes from
`answer['NormalizedAliases']`, plus the normalised human answers where the official JSON
has them. Everything below is transcribed from that file, and `data/triviaqa.py` is
compared with it on cases chosen to separate the two plausible readings:

* the **official** one: hit any alias (`Dave Seville` scores for a gold of
  `["David Seville", "Dave Seville"]`);
* the **`value`-only** one: hit the canonical string (that same answer scores 0).

Both readings exist in the wild -- ReWOO's `Evaluator` uses `answer["value"]` -- and they
give **different numbers on the same transcripts**. That is why `data/triviaqa.py` names
the filter it uses, and why this file pins the difference instead of asserting agreement.
"""
from __future__ import annotations

import re
import string
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

DATA_ROOT = Path("/mnt/20t/xubuqiang/datasets/triviaqa")

# --------------------------------------------------------------- the reference ---


def ref_normalize_answer(s: str) -> str:
    """`triviaqa_evaluation.py::normalize_answer`, verbatim."""

    def remove_articles(text):
        return re.sub(r"\b(a|an|the)\b", " ", text)

    def white_space_fix(text):
        return " ".join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(str(s)))))


def ref_get_ground_truths(answer: dict) -> list[str]:
    """`triviaqa_evaluation.py::get_ground_truths`, verbatim.

        answer['NormalizedAliases'] + [normalize_answer(a) for a in answer['HumanAnswers']]
    """
    return list(answer.get("NormalizedAliases") or []) + [
        ref_normalize_answer(a) for a in answer.get("HumanAnswers") or []]


def ref_exact_match_score(prediction: str, ground_truth: str) -> float:
    """`triviaqa_evaluation.py::exact_match_score`, verbatim."""
    return float(ref_normalize_answer(prediction) == ref_normalize_answer(ground_truth))


def ref_metric_max_over_ground_truths(metric_fn, prediction: str,
                                      ground_truths: list[str]) -> float:
    """`triviaqa_evaluation.py::metric_max_over_ground_truths`, verbatim."""
    if not ground_truths:
        return 0.0
    return max(metric_fn(prediction, gt) for gt in ground_truths)


# ------------------------------------------------------------------- the cases ---

NORMALIZE_CASES = ["David Seville", "the David Seville!", "  spaced   out  ",
                   "A-Team", "an Apple", "YES", "", "The The"]

ALIAS_CASE = {"NormalizedAliases": ["david seville", "dave seville"],
              "HumanAnswers": ["Dave Seville!"]}


@pytest.fixture(scope="module")
def triviaqa():
    import data.triviaqa as module
    return module


def test_normalize_answer_matches_the_official_one(triviaqa):
    for text in NORMALIZE_CASES:
        assert triviaqa.normalize_answer(text) == ref_normalize_answer(text), text


def test_get_ground_truths_matches_the_official_one(triviaqa):
    assert triviaqa.get_ground_truths(ALIAS_CASE) == ref_get_ground_truths(ALIAS_CASE)


def test_exact_match_and_the_max_reduction_match_the_official_ones(triviaqa):
    for prediction in ["David Seville", "dave seville", "Dave Seville!", "nobody", ""]:
        for truth in ["david seville", "dave seville", "dave seville!"]:
            assert triviaqa.exact_match_score(prediction, truth) == \
                ref_exact_match_score(prediction, truth), (prediction, truth)
        assert triviaqa.metric_max_over_ground_truths(
            triviaqa.exact_match_score, prediction,
            triviaqa.get_ground_truths(ALIAS_CASE)) == \
            ref_metric_max_over_ground_truths(
                ref_exact_match_score, prediction, ref_get_ground_truths(ALIAS_CASE)), \
            prediction


def test_any_alias_scores_and_the_canonical_value_does_not_have_to(triviaqa):
    """The official rule versus the `value`-only rule, on the same input.

    `Dave Seville` is an alias of `David Seville`. The official metric counts it; a
    comparison with `answer["value"]` does not. Both are reachable readings of "TriviaQA
    accuracy", and the record has to say which one produced the number.
    """
    gold = {"answer": "David Seville", "value": "David Seville",
            "accepted": triviaqa.get_ground_truths(ALIAS_CASE)}
    official = triviaqa.metric_max_over_ground_truths(
        triviaqa.exact_match_score, "Dave Seville", gold["accepted"])
    value_only = triviaqa.exact_match_score("Dave Seville", gold["value"])
    assert official == 1.0
    assert value_only == 0.0
    assert triviaqa.score("Dave Seville", gold)["reward"] == 1.0
    assert triviaqa.score("Dave Seville", gold)["official"]["canonical_value"] == \
        "David Seville"


def test_the_scorer_agrees_with_the_official_metric_on_real_rows(triviaqa):
    """The differential test, over the staged table.

    Skipped when the data is not provisioned: this compares against the table, and a
    machine without it cannot make the claim either way.
    """
    from data.qa.read import parquet_rows
    path = DATA_ROOT / triviaqa.VALIDATION
    if not path.is_file():
        pytest.skip(f"no TriviaQA data at {path}")
    rows = parquet_rows(path)
    checked = 0
    for row in rows[:50]:
        gold = triviaqa._gold(row)
        answer = dict(row["answer"])
        # The reference takes the official `NormalizedAliases`/`HumanAnswers` keys; the
        # Hub copy lower-cases them. Translating here -- rather than passing the row
        # through -- is what makes this a comparison between two implementations instead
        # of two spellings that both happen to be empty.
        official_gold = ref_get_ground_truths({
            "NormalizedAliases": answer.get("normalized_aliases") or [],
            "HumanAnswers": answer.get("human_answers") or [],
        })
        assert official_gold, "the official reference produced an empty gold set"
        # Our gold set is the official one; the cap in `_gold` never binds on this config.
        assert gold["accepted"] == official_gold[:len(gold["accepted"])]
        for prediction in (gold["value"], "definitely not the answer"):
            want = ref_metric_max_over_ground_truths(
                ref_exact_match_score, prediction, official_gold)
            mine = triviaqa.score(prediction, gold)
            assert bool(mine["reward"]) == bool(want), (row["question"][:50], prediction)
        checked += 1
    assert checked == 50


def test_the_test_split_is_not_scored_because_its_gold_is_withheld(triviaqa):
    """The trap that makes `validation` the scored split.

    Measured on the staged `test` copy: every `answer["value"]` is `<unk>` and every alias
    list is empty. Scoring it would report the fraction of systems that answer `<unk>`.
    """
    from data.qa.read import parquet_rows
    path = DATA_ROOT / triviaqa.TEST
    if not path.is_file():
        pytest.skip(f"no TriviaQA test split at {path}")
    rows = parquet_rows(path)
    assert rows, "the test split should not be empty"
    blinded = 0
    for row in rows[:200]:
        answer = dict(row.get("answer") or {})
        if str(answer.get("value") or "") == "<unk>" and not (
                answer.get("normalized_aliases") or []):
            blinded += 1
    assert blinded == 200, ("the test split's gold is no longer withheld; if upstream "
                            "published it, this dataset could score `test` instead")
    with pytest.raises(ValueError, match="no answer aliases"):
        triviaqa._gold({"answer": {"value": "<unk>", "normalized_aliases": []}})
