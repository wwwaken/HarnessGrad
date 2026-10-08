"""Verbatim MuSiQue answer functions + source drift + differential tests.

StonyBrookNLP/musique@922ac98f19a201998dbdae6d7f2887a5258dbdeb,
metrics/answer.py:12-63. evaluate_v1.0.py:43-46 chooses answer + answer_aliases;
83-85 outputs answer_f1 and support_f1 independently. No composite is claimed here.
"""
from __future__ import annotations

import collections
import inspect
import json
import re
import string
import subprocess
import sys
from pathlib import Path

import pytest

import data.musique as dataset

SOURCE_ROOT = (dataset.DATASET_ROOT / "_src" / f"musique-{dataset.OFFICIAL_COMMIT}")
SOURCE = SOURCE_ROOT / "metrics" / "answer.py"


def normalize_answer(s):
    """Lower text and remove punctuation, articles and extra whitespace."""

    def remove_articles(text):
        regex = re.compile(r"\b(a|an|the)\b", re.UNICODE)
        return re.sub(regex, " ", text)

    def white_space_fix(text):
        return " ".join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def get_tokens(s):
    if not s:
        return []
    return normalize_answer(s).split()


def compute_exact(a_gold, a_pred):
    return int(normalize_answer(a_gold) == normalize_answer(a_pred))


def compute_f1(a_gold, a_pred):
    gold_toks = get_tokens(a_gold)
    pred_toks = get_tokens(a_pred)
    common = collections.Counter(gold_toks) & collections.Counter(pred_toks)
    num_same = sum(common.values())
    if len(gold_toks) == 0 or len(pred_toks) == 0:
        # If either is no-answer, then F1 is 1 if they agree, 0 otherwise
        return int(gold_toks == pred_toks)
    if num_same == 0:
        return 0
    precision = 1.0 * num_same / len(pred_toks)
    recall = 1.0 * num_same / len(gold_toks)
    f1 = (2 * precision * recall) / (precision + recall)
    return f1


def metric_max_over_ground_truths(metric_fn, prediction, ground_truths):
    scores_for_ground_truths = []
    for ground_truth in ground_truths:
        score = metric_fn(prediction, ground_truth)
        scores_for_ground_truths.append(score)
    return max(scores_for_ground_truths)


def test_verbatim_functions_have_not_drifted():
    assert SOURCE.is_file(), "fetch the declared official source archive"
    upstream = SOURCE.read_text().splitlines()
    for function, start, end in [(normalize_answer, 12, 29), (get_tokens, 32, 35),
                                 (compute_exact, 38, 39), (compute_f1, 42, 55),
                                 (metric_max_over_ground_truths, 58, 63)]:
        actual = inspect.getsource(function)
        # The test copy carries this module's required `self-contained` globals; compare
        # the function body itself, not its enclosing test module docstring/imports.
        assert actual == "\n".join(upstream[start-1:end]) + "\n"


@pytest.mark.parametrize("prediction,answer", [
    ("The City", "city"), ("a blue, bird", "blue bird"), ("red green", "red"),
    ("completely wrong", "right"), ("", ""), ("a", ""), ("foo foo", "foo"),
    ("United States", "United States of America"), ("don't", "dont"),
    ("MÜNCHEN", "münchen"), ("abc-def", "abcdef")])
def test_answer_functions_differential(prediction, answer):
    assert dataset.compute_f1(answer, prediction) == compute_f1(answer, prediction)
    assert dataset.compute_exact(answer, prediction) == compute_exact(answer, prediction)


def test_partial_reward_and_alias_max():
    gold = {"answer": "canonical name", "aliases": ["short name"], "id": "x"}
    assert dataset.score("short name", gold)["reward"] == 1.0
    assert dataset.score("short", gold)["reward"] == pytest.approx(2/3)
    assert "support_f1" not in dataset.score("short name", gold)["official"]


def test_upstream_aggregate_uses_ordered_float_accumulation():
    # evaluate_v1.0.py's AnswerMetric loops `self._total_f1 += f1` and rounds only at
    # get_metric(). Python's `sum(list)` uses a different summation path in 3.12; preserve
    # the upstream accumulator because this is a published 3-decimal metric.
    rows = dataset._rows()["dev"][:100]
    total = 0.0
    for row in rows:
        gold = dataset._gold(row)
        total += dataset.score(row["answer"].split()[0], gold)["reward"]
    assert round(total / len(rows), 3) == 0.649


def test_all_released_gold_and_aliases_match_official_metric():
    rows = dataset._rows()["dev"]
    assert len(rows) == 2417
    for row in rows:
        gold = dataset._gold(row)
        assert dataset.score(row["answer"], gold)["reward"] == 1.0
        assert dataset.score("", gold)["reward"] == 0.0
        # Check alias and partial-overlap predictions, not just the trivial oracle.
        for prediction in [*row["answer_aliases"], row["answer"].split()[0]]:
            expected = metric_max_over_ground_truths(compute_f1, prediction,
                                                     [row["answer"], *row["answer_aliases"]])
            assert dataset.score(prediction, gold)["reward"] == expected


def test_context_retains_all_paragraphs_but_not_annotation_fields():
    raw = dataset._rows()["dev"][0]
    question = dataset._question(raw)
    for paragraph in raw["paragraphs"]:
        assert paragraph["title"] in question
        assert paragraph["paragraph_text"] in question
    assert "is_supporting" not in question
    assert "question_decomposition" not in question
    setup = json.dumps(dataset.SETUP[dataset._RECORDS[0]["task_id"]])
    assert raw["answer"] not in setup


@pytest.mark.parametrize("arm,expected", [("--oracle", "1.0"), ("--noop", "0.0")])
def test_platform_control(arm, expected):
    proc = subprocess.run([sys.executable, "data/qa/control.py", "--dataset", "musique",
                           arm, "--platform"], capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert f"score    {expected}" in proc.stdout
    assert "sandbox=True" in proc.stdout
