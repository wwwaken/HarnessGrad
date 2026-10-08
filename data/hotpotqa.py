r"""HotpotQA as a dataset -- refused, because its leaderboard metric needs supporting facts.

    python3 tools/datasets.py --fetch --dataset hotpotqa   # stages the table
    python3 data/qa/control.py --dataset hotpotqa          # says why there is no control
    python3 tools/dataset_lint.py --dataset hotpotqa       # REFUSED, not FAIL

Where the data is
-----------------
`hotpot_qa`, config **`fullwiki`**, split **`validation`** (7,405 questions, 28 MB). The
config matters: `distractor` ships ten candidate paragraphs with each question and
`fullwiki` ships the whole-Wikipedia setting, and the two are different benchmarks with
different numbers. ReWOO used `fullwiki`, and so does this adapter.

Why this dataset refuses to load
--------------------------------
HotpotQA's **leaderboard metric is `joint`** (`hotpotqa/hotpot/hotpot_evaluate_v1.py`):

    joint_em    = em * sp_em
    joint_prec  = prec * sp_prec
    joint_recall = recall * sp_recall

`sp_*` are supporting-fact scores: `update_sp` compares the set of `(title, sentence
index)` pairs the system claims to have used with the gold set, and `em = 1.0 if fp + fn
== 0` -- **exact set equality**. The answer contract carries only `answer.txt`, so there
are no supporting facts, and `joint` does not exist. `data/qa/evidence_scorers.py`
transcribes the upstream functions and `hotpot_update_sp` raises `MissingEvidence`.

Answer-only EM/F1 **are** computable, and papers quote them. They are a different metric --
by a lot, which is the point: `docs/dataset-onboarding-skill.md` records that a table
showing one and claiming the other cannot be told apart from the numbers. So this adapter
refuses and names the interface change: the answer contract would have to carry evidence,
the same conclusion the first adaptation reached independently.

One thing worth knowing if this is ever revisited: unlike FEVER, **this dataset's own rows
carry `supporting_facts`** (the gold pairs, per question). That makes a future
contract-with-evidence version straightforward to build and easy to verify -- the gold is
here, it is the *answer channel* that does not exist.
"""
from __future__ import annotations

from data.qa import base

KIND = "dataset"

DATASET_ROOT = base.Path("/mnt/20t/xubuqiang/datasets/hotpotqa")
REVISION = "1908d6afbbead072334abe2965f91bd2709910ab"
CONFIG = "fullwiki"
VALIDATION = f"{CONFIG}/validation-00000-of-00001.parquet"
TEST = f"{CONFIG}/test-00000-of-00001.parquet"

REFUSED = (
    "hotpotqa: the benchmark's leaderboard metric is `joint` "
    "(`joint_em = em * sp_em`), and the supporting-fact half needs the `(title, sentence "
    "index)` pairs the system claims to have used, compared as an **exact set**. The "
    "answer contract carries only a final answer, so `joint` cannot be computed; "
    "answer-only EM/F1 are a different, much higher metric and are not what the "
    "leaderboard reports. The scorer is transcribed in `data/qa/evidence_scorers.py` and "
    "raises `MissingEvidence`. Refusing rather than reporting answer-only EM under the "
    "benchmark's name."
)


def _rows() -> list[dict]:
    path = DATASET_ROOT / VALIDATION
    if not path.is_file():
        raise FileNotFoundError(f"no {VALIDATION} at {path}")
    return base.parquet_rows(path)


_SPEC = base.QASpec(
    name="hotpotqa",
    root=DATASET_ROOT,
    rows=lambda: {"validation": _rows()},
    question=lambda row: str(row["question"]),
    gold=lambda row: {"answer": str(row["answer"]),
                      "supporting_facts": row.get("supporting_facts")},
    goal=lambda question, gold: question,
    score=lambda prediction, gold: (_ for _ in ()).throw(NotImplementedError(REFUSED)),
    downloads=lambda: [
        {
            "kind": "hf-dataset",
            "name": "hotpot_qa (fullwiki)",
            "repo": "hotpot_qa",
            "version": REVISION,
            "size": "~28 MB (fullwiki validation; the full repository is ~750 MB)",
            "files": [VALIDATION],
            "sha256": {
                VALIDATION: "78933c0a31a5f7b420d4effdf4cd4eed573b28c6a3da6179dcf7a02b39e51d03",
            },
            "dst": ".",
            "note": "Trap 1: `hotpot_qa` has two configs and they are different "
                    "benchmarks -- `distractor` ships ten candidate paragraphs per "
                    "question, `fullwiki` ships the whole-Wikipedia setting. Trap 2: only "
                    "the `fullwiki/validation` file is fetched; `fullwiki/train` alone is "
                    "330 MB and the `distractor` config another 360 MB, none of it scored. "
                    "Trap 3: the `supporting_facts` column is the gold evidence a future "
                    "answer contract would need -- it is here, the answer channel is what "
                    "does not exist.",
        },
    ],
    split="validation",
    source="hotpot_qa@1908d6afbbead072334abe2965f91bd2709910ab (config `fullwiki`)",
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


__all__ = ["KIND", "DATASET_ROOT", "REFUSED", "load", "downloads"]
