"""MuSiQue-Ans v1.0 dev: supplied-context multi-hop QA, official answer F1.

Trivedi et al., TACL 2022, https://arxiv.org/abs/2108.00573. Official
`evaluate_v1.0.py` reports answer_f1, answer_em and support_f1 separately. Reward is
unrounded per-question answer_f1; its mean (rounded to 3 decimals by upstream) is the
answer_f1 column, never the support or sufficiency column.

All released context paragraphs are given in original order. Answers, aliases,
question_decomposition and is_supporting flags stay out of agent-visible data.
The upstream dev split is used as a fixed task pool with a platform hash train/eval
partition, not presented as the benchmark's official hidden test set.

HF canonical access timed out during onboarding. Data was verified through hf-mirror
against the pinned revision's LFS sha256; identity against canonical HF bytes has not
been independently established. Official scorer code was fetched from canonical codeload.
"""
from __future__ import annotations

import collections
import json
import re
import string
from pathlib import Path

from data.qa import base

KIND = "dataset"

#: The oracle control submits the benchmark's own released reference; see
#: `data/dataset.schema.json` (`module.oracle_about`) for what the other value means.
ORACLE_SOURCE = "released"
DATASET_ROOT = Path("/mnt/20t/xubuqiang/datasets/musique")
DATA_FILE = "musique_ans_v1.0_dev.jsonl"
REVISION = "c8f4f8c9465fb69d31a8eae894c3fd509c4ca321"
DATA_SHA256 = "15fa63794d18a94ce12411aca6e2327e65b6e83b0b1490efab3f1962e48abf3b"
OFFICIAL_COMMIT = "922ac98f19a201998dbdae6d7f2887a5258dbdeb"
SOURCE_SHA256 = "c1cc3d121e3f623f9925857559030d48c136142ee2c9cdb52214bb6134c02272"


def normalize_answer(s):
    """Lower text and remove punctuation, articles and extra whitespace."""
    def remove_articles(text):
        return re.sub(r"\b(a|an|the)\b", " ", text, flags=re.UNICODE)
    def remove_punc(text):
        return "".join(ch for ch in text if ch not in set(string.punctuation))
    return " ".join(remove_articles(remove_punc(s.lower())).split())


def compute_exact(a_gold, a_pred):
    return int(normalize_answer(a_gold) == normalize_answer(a_pred))


def compute_f1(a_gold, a_pred):
    gold_toks = normalize_answer(a_gold).split() if a_gold else []
    pred_toks = normalize_answer(a_pred).split() if a_pred else []
    num_same = sum((collections.Counter(gold_toks) & collections.Counter(pred_toks)).values())
    if len(gold_toks) == 0 or len(pred_toks) == 0:
        return int(gold_toks == pred_toks)
    if num_same == 0:
        return 0
    precision = num_same / len(pred_toks)
    recall = num_same / len(gold_toks)
    return (2 * precision * recall) / (precision + recall)


def score(prediction: str, gold: dict) -> dict:
    answers = [gold["answer"], *gold["aliases"]]
    reward = max(compute_f1(prediction, answer) for answer in answers)
    em = max(compute_exact(prediction, answer) for answer in answers)
    return {"reward": float(reward), "correct": bool(em),
            "official": {"metric": "MuSiQue-Ans answer_f1", "answer_f1": reward,
                         "answer_em": em, "id": gold["id"]},
            "why": f"answer_f1={reward:g}, answer_em={em}; independent answer metric"}


def _rows():
    with (DATASET_ROOT / DATA_FILE).open(encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    if len(rows) != 2417 or len({r["id"] for r in rows}) != 2417:
        raise ValueError("expected exactly 2417 unique MuSiQue-Ans dev questions")
    if not all(r["answerable"] and r["answer"] for r in rows):
        raise ValueError("this adapter requires answerable MuSiQue-Ans rows with gold")
    return {"dev": rows}


def _question(row):
    context = "\n\n".join(f"[{p['idx']}] {p['title']}\n{p['paragraph_text']}"
                          for p in row["paragraphs"])
    return f"Question: {row['question']}\n\nContext paragraphs:\n{context}"


def _gold(row):
    return {"answer": row["answer"], "aliases": list(row["answer_aliases"]), "id": row["id"]}


def _goal(question, gold):
    return (question + "\n\nAnswer with the short answer only. All provided paragraphs may be "
            "used; their order is unchanged. Reward is official answer F1 over the canonical "
            "answer and aliases; supporting-fact and sufficiency scores are not reported.\n\n"
            "Write `answer.txt`, or use the qa submit command:\n"
            '    python3 qa/bin/qa submit "<answer>"\n')


def _downloads():
    return [
        {"kind": "hf-dataset", "name": "MuSiQue-Ans dev (third-party HF release)",
         "repo": "dgslibisey/MuSiQue", "version": REVISION,
         "size": "30,439,728 bytes (2417 dev rows)", "files": [DATA_FILE], "dst": ".",
         "sha256": {DATA_FILE: DATA_SHA256},
         "note": "Canonical HF timed out; pinned data and LFS digest verified via hf-mirror, not independently against HF. Preserve all paragraphs; strip answer, aliases, decomposition and supporting labels. Official answer_f1 is separate from support_f1."},
        {"kind": "http", "name": "MuSiQue official evaluation code", "version": OFFICIAL_COMMIT,
         "url": f"https://codeload.github.com/StonyBrookNLP/musique/tar.gz/{OFFICIAL_COMMIT}",
         "size": "1,281,842 bytes compressed source",
         "sha256": SOURCE_SHA256, "dst": "_src/musique.tar.gz", "extract_to": "_src",
         "note": "Pinned evaluate_v1.0.py and metrics/answer.py. The evaluator uses each row's answer_aliases, not the repository-global .answer_aliases.json. Code archive never enters agent SETUP."},
    ]


_SPEC = base.QASpec(name="musique", root=DATASET_ROOT, rows=_rows,
                   question=_question, gold=_gold, goal=_goal, score=score,
                   downloads=_downloads, split="dev",
                   source=f"MuSiQue-Ans v1.0 dev, dgslibisey/MuSiQue@{REVISION}")
_BUILT = _SPEC.build()
DEFAULT_ENV = _BUILT["DEFAULT_ENV"]
ENV = _BUILT["ENV"]
SPLIT = _BUILT["SPLIT"]

#: The benchmark's own evaluation set, within this adapter's pool. The pool is MuSiQue-Ans `dev`, the answerable split the benchmark reports on.
#: `train` exists at the same pinned revision and is not loaded, so this pool holds no study
#: material.
#:
#: Read from `QASpec.division()` -- the one place that decides what this pool's
#: division is -- and `None` because the benchmark released no study split for this
#: table: the pool **is** the scored split, so every task in it belongs to the
#: evaluation set, and that claims nothing about whether the pool is the whole of it.
#: `--split official --side eval` scores the whole pool, which is the comparable run;
#: `--split declared` keeps the platform's hash third (`SPLIT_SOURCE == "hash"`).
OFFICIAL_EVAL = _BUILT["OFFICIAL_EVAL"]

#: Which rule produced `SPLIT`: `"hash"` here -- the benchmark published no study
#: split, so the platform imposes one. See `data/qa/base.py::division`.
SPLIT_SOURCE = _BUILT["SPLIT_SOURCE"]


def __getattr__(name):
    return base.module_getattr(_SPEC, name)


def load():
    return _SPEC.load()


def downloads():
    return _downloads()


def provision_status():
    return _SPEC.provision_status()
