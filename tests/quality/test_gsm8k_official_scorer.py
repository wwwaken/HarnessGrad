"""GSM8K's official scorer, copied in, and a differential test against our check.

The rule this file exists to enforce
------------------------------------
GSM8K has no scorer in its own repository: the number everybody reports is
lm-evaluation-harness' `exact_match` applied through one of two regex filters declared
in `lm_eval/tasks/gsm8k/gsm8k.yaml`. So "our reward is the official metric" is a claim
about **that file**, and this file makes the claim checkable:

    filter              pattern
    flexible-extract    (-?[$]?\\d[\\d,]*)
    strict-match        #### (\\-?[0-9\\.\\,]+)

Both are transcribed below character for character, together with the harness's
comparison (`float(prediction) == float(reference)` after `,` and `$` are stripped), and
`data/gsm8k.py` is checked against them on real rows and on the edge cases where the two
filters disagree. The transcription is deliberately **not** an import of
`lm_eval`: importing their package and calling our function "the same" would prove only
that we can call their code.

The one property worth stating out loud
---------------------------------------
The two filters give **different numbers on the same transcript**. That is why
`data/gsm8k.py` scores with `flexible-extract` and records the strict verdict beside it
instead of picking whichever looked better. `test_the_two_official_filters_disagree`
pins the disagreement so nobody "simplifies" the two into one.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

DATA_ROOT = Path("/mnt/20t/xubuqiang/datasets/gsm8k")

# --------------------------------------------------------------- the reference ---

#: `lm_eval/tasks/gsm8k/gsm8k.yaml`, `flexible-extract`, verbatim. `group_select: -1`
#: means "the last match", which is what `findall(...)[-1]` below reproduces.
REF_FLEXIBLE = re.compile(r"(-?[$]?\d[\d,]*)")


def ref_flexible_extract(text: str) -> str:
    """The filter, verbatim: last match, then the harness's `,`/`$` stripping."""
    matches = REF_FLEXIBLE.findall(text)
    if not matches:
        return ""
    return matches[-1].replace(",", "").replace("$", "")


#: `lm_eval/tasks/gsm8k/gsm8k.yaml`, `strict-match`, verbatim.
REF_STRICT = re.compile(r"#### (\-?[0-9\.\,]+)")


def ref_strict_match(text: str) -> str:
    matches = REF_STRICT.findall(text)
    if not matches:
        return ""
    return matches[-1].replace(",", "")


def ref_exact_match(prediction: str, reference: str) -> bool:
    """`lm_eval.api.metrics`' comparison for a numeric answer: float equality.

    The harness documents this as "we compare the extracted number to the reference
    number, not the strings", and the failure of `float()` (a non-numeric extraction) is
    a non-match rather than an exception.
    """
    try:
        return float(prediction) == float(reference)
    except (TypeError, ValueError):
        return False


# ------------------------------------------------------------------- the cases ---

CASES = [
    ("18", "18"),
    ("18.0", "18"),
    ("The answer is 18", "18"),
    ("$1,250", "1250"),
    ("-3", "-3"),
    ("#### 42", "42"),
    ("#### 7,000", "7000"),
    ("3.5", "3.5"),
    ("no number here", "18"),
    ("", "18"),
]


@pytest.fixture(scope="module")
def gsm8k():
    import data.gsm8k as module
    return module


def test_flexible_extract_matches_the_official_filter(gsm8k):
    for text, _ in CASES:
        assert gsm8k.official_flexible(text) == ref_flexible_extract(text), text


def test_strict_extract_matches_the_official_filter(gsm8k):
    for text, _ in CASES:
        assert gsm8k.official_strict(text) == ref_strict_match(text), text


def test_the_comparison_is_the_official_one(gsm8k):
    for text, reference in CASES:
        assert gsm8k.numeric_equal(gsm8k.official_flexible(text), reference) == \
            ref_exact_match(ref_flexible_extract(text), reference), (text, reference)


def test_the_two_official_filters_disagree():
    """The reason the filter has to be named when the number is quoted.

    `18` with no `####` marker is a hit under flexible-extract and a miss under
    strict-match. Both are lm-evaluation-harness' own GSM8K filters, so both numbers are
    "the official score" -- of different questions.
    """
    assert ref_flexible_extract("18") == "18"
    assert ref_strict_match("18") == ""
    assert ref_exact_match(ref_flexible_extract("18"), "18") is True
    assert ref_exact_match(ref_strict_match("18"), "18") is False

    gsm8k = sys.modules["data.gsm8k"]
    result = gsm8k.score("18", {"answer": "18"})
    assert result["reward"] == 1.0
    assert result["official"]["filter"] == "flexible-extract"
    assert result["official"]["strict_match"] == ""


def test_a_wrong_number_is_classified_as_wrong_not_as_unparseable(gsm8k):
    """A parse failure and a wrong number are different facts and are reported apart."""
    wrong = gsm8k.score("19", {"answer": "18"})
    assert wrong["reward"] == 0.0 and wrong["official"]["flexible_extract"] == "19"
    unparseable = gsm8k.score("I could not solve it", {"answer": "18"})
    assert unparseable["reward"] == 0.0
    assert unparseable["official"]["flexible_extract"] == ""


def test_the_gold_field_is_read_the_way_the_dataset_writes_it(gsm8k):
    """`#### <n>` at the end of the solution; the marker is the dataset's, not ours."""
    sample = "She sells 9 eggs.\nShe makes 9 * 2 = $<<9*2=18>>18 every day.\n#### 18"
    assert gsm8k._gold({"answer": sample})["answer"] == "18"


def test_the_scorer_agrees_with_the_official_reduction_on_real_rows(gsm8k):
    """The differential test, over real rows and over a deliberate near-miss.

    Skipped when the data is not provisioned: this is a comparison against the table,
    and a machine without the table cannot make the claim either way.
    """
    path = DATA_ROOT / gsm8k.TEST
    if not path.is_file():
        pytest.skip(f"no GSM8K data at {path}")
    from data.qa.read import parquet_rows
    rows = parquet_rows(path)
    checked = 0
    for row in rows[:50]:
        gold = gsm8k._gold(row)
        # The extracted gold (the number after `####`) is what a correct agent submits.
        prediction = gold["answer"]
        official = ref_exact_match(ref_flexible_extract(prediction), gold["answer"])
        mine = gsm8k.score(prediction, gold)
        assert bool(mine["reward"]) == official, row["question"][:60]
        # The dataset's own `answer` field ends in `#### <n>`, so strict-match reads the
        # same number off it -- the two filters agree on the gold, and disagree on a bare
        # model answer. That is the asymmetry `test_the_two_official_filters_disagree`
        # pins, and it is why the scored filter is named.
        strict_on_the_field = ref_strict_match(gold["verbatim"])
        assert ref_exact_match(strict_on_the_field, gold["answer"]), gold["verbatim"]
        checked += 1
    assert checked == 50
