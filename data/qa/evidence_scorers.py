r"""The official scorers whose headline metric this contract cannot carry.

Both FEVER and HotpotQA publish a metric that needs a field the answer contract does not
have, so both datasets refuse to load (`data/fever.py`, `data/hotpotqa.py`). This module
holds the upstream functions **verbatim** anyway, for one reason: a refusal is only
credible if the code that computes the missing number is present and says what is missing.
`MissingEvidence` is raised by the two functions that need evidence -- it is a distinct
outcome from a score of 0, and the tests pin that distinction.

Nothing here is a scorer for a runnable dataset. `data/registry.py` never imports
it; the tests do.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any, Sequence

import re
import string


class MissingEvidence(Exception):
    """The input has no evidence field, so this metric **cannot be computed**.

    Distinct from "the score is 0". A nearby number reported in place of it makes an
    interface gap and a wrong answer look the same in a table -- the error
    `docs/dataset-onboarding-skill.md` §1 is about.
    """


# --------------------------------------------------------------- HotpotQA ---
# `hotpotqa/hotpot/hotpot_evaluate_v1.py`, transcribed.


def hotpot_normalize_answer(s: str) -> str:
    """`hotpot_evaluate_v1.py::normalize_answer`, verbatim."""

    def remove_articles(text: str) -> str:
        return re.sub(r"\b(a|an|the)\b", " ", text)

    def white_space_fix(text: str) -> str:
        return " ".join(text.split())

    def remove_punc(text: str) -> str:
        return "".join(ch for ch in text if ch not in set(string.punctuation))

    def lower(text: str) -> str:
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(str(s)))))


def hotpot_f1_score(prediction: str, ground_truth: str) -> tuple[float, float, float]:
    """`hotpot_evaluate_v1.py::f1_score`, verbatim. Returns `(f1, precision, recall)`."""
    p, g = hotpot_normalize_answer(prediction), hotpot_normalize_answer(ground_truth)
    if p in ("yes", "no", "noanswer") and p != g:
        return 0.0, 0.0, 0.0
    if g in ("yes", "no", "noanswer") and p != g:
        return 0.0, 0.0, 0.0
    pt, gt = p.split(), g.split()
    common = Counter(pt) & Counter(gt)
    num_same = sum(common.values())
    if num_same == 0:
        return 0.0, 0.0, 0.0
    precision = 1.0 * num_same / len(pt)
    recall = 1.0 * num_same / len(gt)
    return (2 * precision * recall) / (precision + recall), precision, recall


def hotpot_exact_match(prediction: str, ground_truth: str) -> float:
    """`hotpot_evaluate_v1.py::exact_match_score`, verbatim."""
    return float(hotpot_normalize_answer(prediction) == hotpot_normalize_answer(ground_truth))


@dataclass(frozen=True)
class SpScore:
    """Supporting-facts scores, named rather than positional.

    Upstream `update_sp` returns `(em, prec, recall)` -- three floats, and `f1` is only
    accumulated into the metrics dict. A first version of this transcription returned
    `(em, f1, prec)`; a caller unpacking `sp_em, sp_prec, sp_recall` would then have used
    f1 as precision, and every number on the page would have looked normal. An interface
    whose order can be wrong should not be expressed as an order.
    """

    em: float
    f1: float
    prec: float
    recall: float


def hotpot_update_sp(sp_prediction: Sequence[Sequence[Any]] | None,
                     sp_gold: Sequence[Sequence[Any]] | None) -> SpScore:
    """`hotpot_evaluate_v1.py::update_sp`, with the missing-field guard.

    `em = 1.0 if fp + fn == 0 else 0.0` -- exact set equality, not F1.
    """
    if not sp_prediction:
        raise MissingEvidence(
            "HotpotQA's supporting-fact scores need the model to output the "
            "(title, sentence index) pairs it used, and the answer contract carries only "
            "the final answer. Its leaderboard reports **joint** "
            "(`joint_em = em * sp_em`), so an answer-only number is a different metric; "
            "reporting it under the benchmark's name is the error this refusal avoids.")
    cur = set(map(tuple, sp_prediction))
    gold = set(map(tuple, sp_gold or []))
    tp = sum(1 for e in cur if e in gold)
    fp = sum(1 for e in cur if e not in gold)
    fn = sum(1 for e in gold if e not in cur)
    prec = tp / (tp + fp) if tp + fp > 0 else 0.0
    recall = tp / (tp + fn) if tp + fn > 0 else 0.0
    f1 = 2 * prec * recall / (prec + recall) if prec + recall > 0 else 0.0
    return SpScore(em=1.0 if fp + fn == 0 else 0.0, f1=f1, prec=prec, recall=recall)


def hotpot_joint(em: float, prec: float, recall: float, sp: SpScore) -> tuple[float, float]:
    """`hotpot_evaluate_v1.py::eval`'s joint lines, verbatim.

    `joint_em = em * sp_em`; `joint_prec = prec * sp_prec`, `joint_recall = recall *
    sp_recall`, and `joint_f1` is the harmonic mean of the two joint components.
    """
    joint_prec = prec * sp.prec
    joint_recall = recall * sp.recall
    joint_f1 = (2 * joint_prec * joint_recall / (joint_prec + joint_recall)
                if joint_prec + joint_recall > 0 else 0.0)
    return em * sp.em, joint_f1


# ---------------------------------------------------------------- FEVER ---
# `sheffieldnlp/fever-scorer/src/fever/scorer.py`, transcribed.


def fever_is_correct_label(label: str, predicted_label: str) -> bool:
    """`scorer.py::is_correct_label`, verbatim.

    `.upper()` and nothing else -- **no punctuation stripping**. Measured consequence,
    pinned by the tests: `NOT ENOUGH INFO.` (one trailing full stop) is wrong. That is
    upstream's strictness, not an implementation shortcut, and "fixing" it here would
    produce a number higher than the published one.
    """
    return str(label).upper() == str(predicted_label).upper()


def fever_is_strictly_correct(label: str, predicted_label: str,
                              evidence: Sequence[Any] | None,
                              predicted_evidence: Sequence[Any] | None,
                              *, max_evidence: int = 5) -> bool:
    """`scorer.py::is_strictly_correct`, with the missing-field guard.

    A label is strictly correct when it is right **and** one whole gold evidence group is
    contained in the first `max_evidence` predictions. `NOT ENOUGH INFO` items are exempt
    from evidence -- that branch returns immediately, which is why an "answer-only FEVER
    score" is not even the same rule for the three classes.
    """
    if str(label).upper() != "NOT ENOUGH INFO" and not predicted_evidence:
        raise MissingEvidence(
            "FEVER's headline metric is `strict_score`, which needs the model to output "
            "`predicted_evidence` ((page, line) pairs, judged on the first 5). The answer "
            "contract carries only the final label. FEVER's not-enough-info items are "
            "evidence-exempt, so a label-only number would be a different rule for "
            "different rows -- not a lower-fidelity version of the same one.")
    correct = fever_is_correct_label(label, predicted_label)
    if str(label).upper() != "NOT ENOUGH INFO" and correct:
        head = [list(e) for e in (predicted_evidence or [])[:max_evidence]]
        for group in evidence or []:
            actual = [[e[2], e[3]] for e in group]
            if all(sentence in head for sentence in actual):
                return True
        return False
    if str(label).upper() == "NOT ENOUGH INFO" and correct:
        return True
    return False


__all__ = ["MissingEvidence", "SpScore",
           "hotpot_normalize_answer", "hotpot_f1_score", "hotpot_exact_match",
           "hotpot_update_sp", "hotpot_joint",
           "fever_is_correct_label", "fever_is_strictly_correct"]
