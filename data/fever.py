r"""FEVER as a dataset -- refused, because its headline metric needs evidence we cannot ask for.

    python3 tools/datasets.py --fetch --dataset fever   # stages the table
    python3 data/qa/control.py --dataset fever          # says why there is no control
    python3 tools/dataset_lint.py --dataset fever       # REFUSED, not FAIL

Where the data is
-----------------
`copenlu/fever_gold_evidence` (a Hub mirror of the FEVER gold-evidence release):
`valid.jsonl` (6.5 MB), `test.jsonl` (6.6 MB), `train.jsonl` (97 MB). Each row is a
`claim` plus a three-way `label` (`SUPPORTS` / `REFUTES` / `NOT ENOUGH INFO`) and the
gold `evidence` groups.

Why this dataset refuses to load
--------------------------------
FEVER's **official headline metric is `strict_score`** (`sheffieldnlp/fever-scorer`,
`src/fever/scorer.py`): a claim counts only when the label is right **and** a whole gold
evidence group appears among the model's first five predicted `(page, line)` pairs. The
platform's answer contract carries the final answer and nothing else -- `answer.txt`, one
string -- so `predicted_evidence` does not exist, and neither does the metric.

The functions are transcribed in `data/qa/evidence_scorers.py`, and
`fever_is_strictly_correct` raises `MissingEvidence` rather than returning `False`: a
`False` would enter a table as "the system got it wrong", which is a different claim from
"nobody measured it".

`is_correct_label` alone -- the plain label accuracy -- **is** computable, and it is what
several papers quote. It is not what FEVER's leaderboard reports, and it is not the same
rule for every row: `NOT ENOUGH INFO` items are evidence-exempt upstream, so a label-only
number silently scores the three classes under different rules. Reporting it under the
dataset's name without saying so is the error `docs/dataset-onboarding-skill.md` §1 and §2
describe. This adapter therefore refuses, and names the interface change that would make
it reachable: the answer contract would have to carry evidence, the same conclusion the
first adaptation of this work reached independently.
"""
from __future__ import annotations

from data.qa import base

KIND = "dataset"

DATASET_ROOT = base.Path("/mnt/20t/xubuqiang/datasets/fever")
REVISION = "a6b8d891d393e97a4efac791afffb2d7de5e57c6"
VALID = "valid.jsonl"
TEST = "test.jsonl"
TRAIN = "train.jsonl"
LABELS = ("SUPPORTS", "REFUTES", "NOT ENOUGH INFO")

REFUSED = (
    "fever: the benchmark's headline metric is the FEVER score (`strict_score`), which "
    "requires the model's `predicted_evidence` -- up to five `(page, line)` pairs -- and "
    "the answer contract carries only a final answer. Plain label accuracy is computable "
    "but is a different metric, and it is not even the same rule on every row: "
    "`NOT ENOUGH INFO` items are evidence-exempt upstream. This contract has no evidence "
    "field, so the official number cannot be produced; the scorer is transcribed in "
    "`data/qa/evidence_scorers.py` and raises `MissingEvidence`. Refusing rather than "
    "reporting label accuracy under the benchmark's name."
)


def _rows() -> list[dict]:
    path = DATASET_ROOT / VALID
    if not path.is_file():
        raise FileNotFoundError(f"no {VALID} at {path}")
    return base.jsonl_rows(path)


_SPEC = base.QASpec(
    name="fever",
    root=DATASET_ROOT,
    rows=lambda: {"test": _rows()},
    question=lambda row: str(row["claim"]),
    gold=lambda row: {"answer": str(row["label"]), "evidence": row.get("evidence")},
    goal=lambda question, gold: question,
    score=lambda prediction, gold: (_ for _ in ()).throw(NotImplementedError(REFUSED)),
    downloads=lambda: [
        {
            "kind": "hf-dataset",
            "name": "copenlu/fever_gold_evidence",
            "repo": "copenlu/fever_gold_evidence",
            "version": REVISION,
            "size": "~110 MB (test 6.6 MB + valid 6.5 MB + train 97 MB)",
            # `dst` must be the **path `--fetch` writes**, which for `hf-dataset` entries
            # is built by appending the file to `dst`. A first version of this entry set
            # `dst` to the file name as well, which produced `.../valid.jsonl/valid.jsonl`
            # and a 404 -- a duplicate key in one dict, and the fetch is where it showed.
            "files": [VALID],
            "dst": ".",
            "note": "Trap: FEVER's headline metric needs predicted evidence, so this "
                    "adapter refuses to load -- staging the table is still useful because "
                    "the refusal has to be demonstrable on real rows, and because the "
                    "evidence groups are what a future answer contract would carry. The "
                    "repository also ships `test.jsonl` and a 97 MB `train.jsonl`; the "
                    "adapter reads `valid.jsonl` and declares only it, so `--check` does "
                    "not report a missing 97 MB file as an error. `sha256` is left null "
                    "because the HuggingFace JSONL export is regenerated by the Hub and "
                    "the pinned revision is the guarantee; the lint requires a pinned "
                    "version, not a checksum.",
        },
    ],
    split="test",
    source="copenlu/fever_gold_evidence@a6b8d891d393e97a4efac791afffb2d7de5e57c6",
)

_BUILT = _SPEC.build()


def __getattr__(name: str):
    return base.module_getattr(_SPEC, name)


def load() -> tuple[list[dict], dict[str, str]]:
    raise ValueError(REFUSED)


def downloads() -> list[dict]:
    return _SPEC._downloads()


def provision_status() -> dict:
    return _SPEC.provision_status()


__all__ = ["KIND", "DATASET_ROOT", "REFUSED", "LABELS", "load", "downloads"]
