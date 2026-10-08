r"""GSM8K as a dataset: grade-school math word problems, graded by numeric equality.

    python3 tools/datasets.py --fetch --dataset gsm8k
    python3 data/qa/control.py --dataset gsm8k --oracle
    python3 data/qa/control.py --dataset gsm8k --oracle --platform
    driver.py --dataset gsm8k ...

Where the tasks come from
-------------------------
Cobbe et al., *Training Verifiers to Solve Math Word Problems* (arXiv:2110.14168),
`openai/gsm8k`, config `main`, both released splits: **test** (1,319 rows) is what this
adapter scores and what the paper's numbers are computed on, and **train** (7,473 rows)
is loaded as well, as the study side. GSM8K publishes the division, so the platform uses
it instead of imposing one -- see "The split" below.

The metric, and the one genuinely hard thing about it
----------------------------------------------------
There is no `gsm8k` scorer in the dataset's own repository -- the reference
implementation is the evaluation table in lm-evaluation-harness, and its GSM8K config
declares **two** extraction filters with two different numbers:

| filter | rule | regex (verbatim) |
| --- | --- | --- |
| `strict-match` | the answer must contain `#### <number>` | `#### (\-?[0-9\.\,]+)` |
| `flexible-extract` | the last number anywhere in the answer | `(-?[$]?\\d[\\d,]*)` |

They disagree on real transcripts -- an answer of `18` is 1 under flexible and 0 under
strict -- so the number is not comparable unless the filter is named. This adapter
scores with **flexible-extract** (the headline in the harness's own config table) and
records the strict verdict beside it in the evidence, so a reader can see both. The
comparison is numeric after the same `,`/`$` stripping the harness does, not string
equality: `18.0` and `18` are the same answer, and the harness compares floats.

Which bytes are graded
----------------------
`answer.txt`, written by the harness (or by `python3 qa submit`). The reasoning is not
graded, not read and not required: a harness that emits only `18` scores the same as one
that emits a full derivation ending in `18`, which is what "flexible-extract" means.

The split
---------
GSM8K states its own: `train` is the study side, `test` is the exam. This adapter loads
both, so `--split declared` (the default) and `--split official` resolve to the same
division -- 7,473 study tasks, 1,319 scored -- and `--split default` imposes the
platform's hash third on the whole 8,792 instead. That second one is a legitimate
division and is *not* a GSM8K number; `split_sha` on the run is what tells the two apart
on a curve (`INTERFACE.md` §2.3).
"""
from __future__ import annotations

import re

from data.qa import base

KIND = "dataset"

#: The oracle control submits the benchmark's own released reference; see
#: `data/dataset.schema.json` (`module.oracle_about`) for what the other value means.
ORACLE_SOURCE = "released"

DATASET_ROOT = base.Path("/mnt/20t/xubuqiang/datasets/gsm8k")

#: The pinned revision of `openai/gsm8k`. A commit sha, not `main`: `main` is not a
#: version, and a fetch that cannot be re-played byte-for-byte makes every number
#: attached to it unreproducible.
REVISION = "740312add88f781978c0658806c59bc2815b9866"

#: The files this adapter reads. `main/train` is provisioned but never scored.
TEST = "main/test-00000-of-00001.parquet"
TRAIN = "main/train-00000-of-00001.parquet"

#: The gold answer lives after this marker in the `answer` field.
ANSWER_MARK = "####"

#: lm-evaluation-harness' `flexible-extract` filter, character for character:
#: `lm_eval/tasks/gsm8k/gsm8k.yaml` declares
#: `regex_pattern: "(-?[$]?\\d[\\d,]*)"` and takes the **last** match. The pattern
#: matches a decimal's fraction as a separate number (`3.5` -> `5`); that limitation is
#: upstream's and is reproduced rather than repaired, because a repaired filter is a
#: different scorer and a different number.
FLEXIBLE_RE = re.compile(r"(-?[$]?\d[\d,]*)")

#: lm-evaluation-harness' `strict-match` filter: the same file declares
#: `regex_pattern: "#### (\\-?[0-9\\.\\,]+)"` and takes the last match.
STRICT_RE = re.compile(r"#### (\-?[0-9\.\,]+)")


def _rows() -> dict[str, list[dict]]:
    return {
        # `test` first: it is the scored split, and a reader should meet it first too.
        "test": base.parquet_rows(DATASET_ROOT / TEST),
        "train": base.parquet_rows(DATASET_ROOT / TRAIN),
    }


def _question(row: dict) -> str:
    return str(row["question"]).strip()


def _gold(row: dict) -> dict:
    """The gold number, plus the field it was read from.

    Kept as `answer` (a string) rather than a float: the comparison is numeric and done
    by the scorer, and keeping the text means the evidence can show what the dataset
    actually said when a grader disagrees with it.
    """
    field = str(row["answer"])
    value = field.split(ANSWER_MARK)[-1].strip() if ANSWER_MARK in field else field.strip()
    return {"answer": value, "verbatim": field[-80:]}


def official_flexible(text: str) -> str:
    """The last `(-?[$]?\\d[\\d,]*)` match, `,`/`$` stripped; `""` when there is none.

    The `re.findall` + `[-1]` is lm-evaluation-harness' `RegexFilter` behaviour
    (`group_select: -1`). Meaningless for an empty match, which is reported as a *format*
    failure rather than as a wrong number -- see `score()`.
    """
    found = FLEXIBLE_RE.findall(text)
    if not found:
        return ""
    return found[-1].replace(",", "").replace("$", "")


def official_strict(text: str) -> str:
    r"""The last `#### (\-?[0-9\.\,]+)` match, or `""` when the marker is absent."""
    found = STRICT_RE.findall(text)
    if not found:
        return ""
    return found[-1].replace(",", "")


def numeric_equal(got: str, want: str) -> bool:
    """The harness's own comparison: `float(got) == float(want)`.

    A string that does not parse is **not** an exception here -- a scorer may not take
    the whole run down because an answer was prose. It is reported as a format failure by
    the caller, which is a different fact from "the number was wrong".
    """
    try:
        return abs(float(got) - float(want)) < 1e-6
    except (TypeError, ValueError):
        return False


def score(prediction: str, gold: dict) -> dict:
    """The dataset's grade. Called by the shared check (`data/qa/verify/check.py`)."""
    want = str(gold.get("answer", "")).strip()
    flexible = official_flexible(prediction or "")
    strict = official_strict(prediction or "")
    ok = numeric_equal(flexible, want)
    return {
        "reward": 1.0 if ok else 0.0,
        "correct": ok,
        "official": {"filter": "flexible-extract", "strict_match": strict,
                     "flexible_extract": flexible},
        "why": (
            f"flexible-extract {flexible or '<no number>'} vs {want} -> "
            f"{'match' if ok else 'no match'}"
            + (f"; strict-match {strict or '<no #### marker>'} "
               f"({'match' if numeric_equal(strict, want) else 'no match'})"
               if strict or ANSWER_MARK not in (prediction or "") else "")
        ),
    }


def _goal(question: str, gold: dict) -> str:
    return (
        "# Task\n"
        "\n"
        "Solve this grade-school math problem.\n"
        "\n"
        f"{question}\n"
        "\n"
        "## How to answer\n"
        "\n"
        "Write the final answer -- the number alone, or your working followed by the\n"
        f"number -- to `{base.ANSWER_FILE}` in your working directory, or submit it with\n"
        "\n"
        f"    python3 {base.CLI_FILE} submit \"<the number>\"\n"
        "\n"
        "For example, a correct submission is `18` or `1250` after the commas are\n"
        "dropped. Units, currency signs and explanatory prose are stripped before the\n"
        "comparison; the reasoning is not graded.\n"
        "\n"
        "## How it is scored\n"
        "\n"
        "- The last number in your answer is compared numerically with the reference\n"
        "  answer (lm-evaluation-harness' `flexible-extract` filter for GSM8K).\n"
        "- `18`, `18.0` and `The answer is 18` all score 1 if the reference is 18.\n"
        "- Nothing else you print is read.\n"
    )


def _downloads() -> list[dict]:
    return [
        {
            "kind": "hf-dataset",
            "name": "openai/gsm8k (main)",
            "repo": "openai/gsm8k",
            "version": REVISION,
            "size": "~2.7 MB (`main` config, both splits)",
            "files": [TEST, TRAIN],
            # Measured on the copy this adapter was validated against, so
            # `python3 tools/datasets.py --check` can tell a re-download that changed
            # bytes from the revision it is supposed to be. A mapping, because this entry
            # brings two files and a single digest would only cover the first.
            "sha256": {
                TEST: "ee7b8da9e381df27b9e3f7758a159ab2bdaa4dbaa910546cbbc47e0cb44e4f59",
                TRAIN: "ea82612ea9582142387730c793eb67d3b12849002bc0b7fa6f8efafa7351419d",
            },
            "dst": ".",
            "note": "GSM8K's own table, `main` config. Trap: the repository's `main` and "
                    "`socratic` configs are different data (the socratic one rewrites "
                    "each solution as a dialogue) and both are 2 splits under one name -- "
                    "naming the config is part of naming the file. Scores are reported on "
                    "the `test` split, so only that one is scored; `train` is loaded as the "
                    "study side, which is what makes `--split declared` here GSM8K's own "
                    "division rather than the platform's hash.",
        },
        {
            "kind": "pip",
            "name": "pyarrow",
            "package": "pyarrow",
            "version": "23.0.0",
            "size": "~40 MB",
            "note": "Reads the parquet files the pinned revision ships. The check runs "
                    "inside the verification namespace and must not need the HuggingFace "
                    "`datasets` package, which pulls `pandas`, `requests` and a cache "
                    "layout; `pyarrow` is one import and no network.",
        },
    ]


_SPEC = base.QASpec(
    name="gsm8k",
    root=DATASET_ROOT,
    rows=_rows,
    question=_question,
    gold=_gold,
    goal=_goal,
    score=score,
    downloads=_downloads,
    split="test",
    # **The benchmark publishes both sides, so the platform takes its division rather than
    # imposing one.** This is the only QA adapter in the repository for which that is true:
    # every other table in the batch is a single scored split with no study material
    # released, which is why the platform's hash rule exists at all.
    study=("train",),
    source="openai/gsm8k@740312add88f781978c0658806c59bc2815b9866 (config `main`, "
           "splits `train` + `test`)",
)

_BUILT = _SPEC.build()

DEFAULT_ENV = _BUILT["DEFAULT_ENV"]
ENV = _BUILT["ENV"]
SPLIT = _BUILT["SPLIT"]

#: The benchmark's own evaluation set, within this adapter's pool.
#:
#: The pool holds **both** released splits (8,792 tasks: 7,473 `train` + 1,319 `test`), so
#: the answer is a list and not `None` -- the `test` ids, which are the questions GSM8K's
#: published numbers are computed on. Read from `QASpec.division()`, so there is exactly one
#: place in this file that decides what the division is.
#:
#: What the three divisions mean for this dataset:
#:
#: * `--split declared` (the default) and `--split official` are **the same division here**,
#:   and that is the point of the whole mechanism: GSM8K states its own two sides, so the
#:   platform does not impose one. `--side train` studies all 7,473 official training
#:   questions; `--side eval` reports on all 1,319 official test questions, which is the
#:   only comparison a GSM8K number from this platform can be put beside a published one.
#: * `--split default` is a *different* division of the same 8,792 tasks -- the platform's
#:   hash third, blind to the split labels. It is legitimate for an experiment that wants a
#:   held-out third of everything, and it is not a GSM8K number; `split_sha` is what keeps
#:   the two apart on a curve.
OFFICIAL_EVAL = _BUILT["OFFICIAL_EVAL"]

#: Which rule produced `SPLIT`: `"declared"` here -- see `data/qa/base.py::division`.
SPLIT_SOURCE = _BUILT["SPLIT_SOURCE"]


def __getattr__(name: str):
    """`SETUP`, `VERIFY`, `_RECORDS`, `_LOAD_ERROR`, built on first use.

    See `data/qa/base.py::module_getattr`: the two per-task maps are lazy so importing
    the adapter does not render every goal, and `_RECORDS` is the same cached list
    `load()` returns from.
    """
    return base.module_getattr(_SPEC, name)


def load() -> tuple[list[dict], dict[str, str]]:
    return _SPEC.load()


def downloads() -> list[dict]:
    return _SPEC._downloads()


def provision_status() -> dict:
    return _SPEC.provision_status()


__all__ = ["KIND", "DATASET_ROOT", "REVISION", "load", "downloads", "score",
           "official_flexible", "official_strict", "numeric_equal", "SPLIT",
           "OFFICIAL_EVAL", "SPLIT_SOURCE"]
