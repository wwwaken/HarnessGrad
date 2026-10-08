r"""2WikiMultihopQA dev, supplied-context multi-hop QA: the official **Ans EM/F1**.

Ho et al., COLING 2020, https://arxiv.org/abs/2011.01060. The official evaluator
`2wikimultihop_evaluate_v1.1.py` (`Alab-NII/2wikimultihop`@`209e7618`) is transcribed
**verbatim** below -- all 250 lines of it, including the three quarters this platform does
not report. `data/musique.py` has the shape for the rest.

    python3 tools/datasets.py --fetch --dataset twowikimultihopqa
    python3 data/qa/control.py --dataset twowikimultihopqa --oracle --platform
    python3 tools/dataset_lint.py --dataset twowikimultihopqa

Which number is the reward, and which three are missing
-------------------------------------------------------
The evaluator reports four groups: `em/f1/prec/recall` (answers), `sp_*` (sentence-level
supporting facts), `evi_*` (evidence triples), `joint_*`. The leaderboard prints them as
**separate columns** (Ans EM, Ans F1, Sup EM, Sup F1, Evi EM, Evi F1, Joint EM, Joint F1),
so `Ans F1` is a column of the official metric in its own right -- the same reading
`data/musique.py` makes of MuSiQue's separate `answer_f1`, and the reason this adapter is
not the refusal `data/hotpotqa.py` is: HotpotQA's leaderboard number is `joint`, and this
one's is not. Reward is per-question Ans F1; `correct` is Ans EM.

`Sup`, `Evi` and `Joint` are transcribed, runnable, and **not reported**: each needs an
evidence channel (`supporting_facts`, `evidences`) that the answer contract does not carry,
and `joint` is the product of all three. This repository's rule for that situation is
`data/qa/evidence_scorers.py`'s -- "a refusal is only credible if the code that computes
the missing number is present and says what is missing" -- and it applies here in the other
direction: the dataset loads, and the columns it does not report are named rather than
silently dropped. A run of this adapter is comparable to published Ans F1, and to nothing
else.

Two traps, both measured here
-----------------------------
1. **Normalization order.** Upstream lowercases *first*, then strips punctuation, then
   removes articles. Removing articles first leaves a capitalised `The`/`A`/`An` in place,
   and that changes the normalized form of **196 of the first 2,000 dev gold answers
   (9.8%)**. Measured against the unmodified upstream script: the wrong order turns a
   500-row Ans F1 of **68.18 into 68.67**. This is not a style choice, so the differential
   test runs the upstream file itself rather than a second transcription of it.

2. **The alias channel is part of the metric.** The gold set is `{answer}` plus the
   Wikidata aliases of `answer_id` from `id_aliases.json` (203,297 Q-ids). 10,603 of the
   12,576 dev rows carry an `answer_id`, **all 10,603 resolve**, and 5,869 carry an alias
   beyond the gold span. Dropping the alias file costs 0.64 Ans F1 on that same 500-row
   slice (67.54 vs 68.18). Every parquet conversion of this dataset ships the answer
   column and *not* the id columns, so a parquet mirror cannot reproduce the metric -- which
   is why the pool is the official JSON and the parquet is kept only as a witness.

Where the data is, and how far its identity is established
---------------------------------------------------------
`dev.json` (12,576 rows, 57,614,142 bytes) and `id_aliases.json` (17,501,406 bytes) are the
December-2020 id-enriched release, from the HF mirror `kamelliao/2wikimultihopqa`
@`f4f0d7e4`. The official host is a Dropbox link that is **unreachable from the machine
this was onboarded on**, so identity against the official zip was not established directly.
What *was* established: a second, independently published mirror
(`framolfese/2WikiMultihopQA`@`fe713bfb`) agrees with `dev.json` on **all 12,576 rows** for
question, answer **and** supporting facts; and every `answer_id` in the file resolves in the
alias file, which a reconstructed alias table would not do. `validation.parquet` is that
witness, on disk and declared, and read by no run.

The upstream dev split is used as a fixed task pool with a platform hash train/eval
partition, not presented as the benchmark's official hidden test set. `train.json` exists at
the same revision (167,454 rows) and is not loaded, so the pool holds no study material.
"""
from __future__ import annotations

import itertools
import json
import re
import string
from collections import Counter
from pathlib import Path

from data.qa import base

KIND = "dataset"

#: The oracle control submits the benchmark's own released reference; see
#: `data/dataset.schema.json` (`module.oracle_about`) for what the other value means.
ORACLE_SOURCE = "released"

DATASET_ROOT = Path("/mnt/20t/xubuqiang/datasets/twowikimultihopqa")
DATA_FILE = "dev.json"
ALIAS_FILE = "id_aliases.json"
WITNESS_FILE = "validation.parquet"
REVISION = "f4f0d7e4ae275d9281e90c46c93e66d6cdda3674"
WITNESS_REVISION = "fe713bfbd1afbca1a65246741a75890405d56a3a"
DATA_SHA256 = "79f77ae104088ea8e25b1a65dbece768d45771194663bc5660ec9a98070dadf5"
ALIAS_SHA256 = "f08ffcb6c2cefca9bdbe86b4248d6ad7a7743762d3f7264c14ff0bae85726fb6"
WITNESS_SHA256 = "408e2dbb28edc6c8b9ca3ba0c94d4fc7bf17ffb923766593a3a7f546ab4cba59"
OFFICIAL_COMMIT = "209e761834d1ce055856fc11072c0a5aab47601d"
#: The compressed archive, which is what `downloads()` declares and `--fetch` verifies.
SOURCE_SHA256 = "01c0b699569cce142614d5d7a0e1f4864031aeaf035394af3084cc2c1d97dc3c"
#: **The file inside it** -- the program transcribed verbatim below. Two digests because
#: they answer two questions ("is this the archive I declared?" and "is this the program I
#: copied?"), and the first version of the drift test compared the archive's digest to the
#: extracted file and failed on its own pin rather than on a drift.
EVALUATOR_SHA256 = "7c09ee2ec98c7ecb57df79eb68dba22eb381ab58d50e730dfcefafb4dda31458"
EXPECTED_ROWS = 12576

# ---------------------------------------------------------------------------------------
# `2wikimultihop_evaluate_v1.1.py`, lines 15-264, byte for byte.
#
# The module header above it is where this file differs, and only there: upstream does
# `import ujson as json` and this adapter imports `json`. The transcription starts at
# `def normalize_answer` so that the region itself needs **no** substitution -- which is
# what lets `test_the_transcription_is_byte_identical_to_upstream` assert equality instead
# of "equality modulo the edits we remember making". `sys`, `pickle` and `os` are imported
# by upstream and used by neither half; they are not transcribed.
#
# Nothing below is re-implemented for the platform's convenience, which has one visible
# consequence worth naming: `update_answer` mutates a metrics dict and returns the max
# `em`, `prec` and `recall` -- **not** the max `f1`, which it only accumulates. `score()`
# therefore reads `f1` back out of a dict it seeded with zeroes; see `_one_question`.
# ---------------------------------------------------------------------------------------
def normalize_answer(s):

    def remove_articles(text):
        return re.sub(r'\b(a|an|the)\b', ' ', text)

    def white_space_fix(text):
        return ' '.join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return ''.join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def f1_score(prediction, ground_truth):
    normalized_prediction = normalize_answer(prediction)
    normalized_ground_truth = normalize_answer(ground_truth)

    ZERO_METRIC = (0, 0, 0)

    if normalized_prediction in ['yes', 'no', 'noanswer'] and normalized_prediction != normalized_ground_truth:
        return ZERO_METRIC
    if normalized_ground_truth in ['yes', 'no', 'noanswer'] and normalized_prediction != normalized_ground_truth:
        return ZERO_METRIC

    prediction_tokens = normalized_prediction.split()
    ground_truth_tokens = normalized_ground_truth.split()
    common = Counter(prediction_tokens) & Counter(ground_truth_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return ZERO_METRIC
    precision = 1.0 * num_same / len(prediction_tokens)
    recall = 1.0 * num_same / len(ground_truth_tokens)
    f1 = (2 * precision * recall) / (precision + recall)
    return f1, precision, recall


def exact_match_score(prediction, ground_truth):
    return (normalize_answer(prediction) == normalize_answer(ground_truth))


def eval_answer(prediction, gold):
    em = exact_match_score(prediction, gold)
    f1, prec, recall = f1_score(prediction, gold)
    return em, f1, prec, recall


def update_answer(metrics, prediction, golds):
    max_em, max_f1, max_prec, max_recall = 0, 0, 0, 0

    for gold in golds:
        em, f1, prec, recall = eval_answer(prediction, gold)

        max_em = max(max_em, em)
        max_f1 = max(max_f1, f1)
        max_prec = max(max_prec, prec)
        max_recall = max(max_recall, recall)

    metrics['em'] += float(max_em)
    metrics['f1'] += max_f1
    metrics['prec'] += max_prec
    metrics['recall'] += max_recall

    return max_em, max_prec, max_recall


def normalize_sp(sps):
    new_sps = []
    for sp in sps:
        sp = list(sp)
        sp[0] = sp[0].lower()
        new_sps.append(sp)
    return new_sps


def update_sp(metrics, prediction, gold):
    cur_sp_pred = normalize_sp(set(map(tuple, prediction)))
    gold_sp_pred = normalize_sp(set(map(tuple, gold)))
    tp, fp, fn = 0, 0, 0
    for e in cur_sp_pred:
        if e in gold_sp_pred:
            tp += 1
        else:
            fp += 1
    for e in gold_sp_pred:
        if e not in cur_sp_pred:
            fn += 1
    prec = 1.0 * tp / (tp + fp) if tp + fp > 0 else 0.0
    recall = 1.0 * tp / (tp + fn) if tp + fn > 0 else 0.0
    f1 = 2 * prec * recall / (prec + recall) if prec + recall > 0 else 0.0
    em = 1.0 if fp + fn == 0 else 0.0
    metrics['sp_em'] += em
    metrics['sp_f1'] += f1
    metrics['sp_prec'] += prec
    metrics['sp_recall'] += recall
    return em, prec, recall


def normalize_evi(evidences):

    def white_space_fix(text):
        return ' '.join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return ''.join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    def recurse(arr):
        for i in range(len(arr)):
            if isinstance(arr[i], str):
                arr[i] = white_space_fix(remove_punc(lower(arr[i])))
            else:
                recurse(arr[i])

    recurse(evidences)

    return evidences


def update_evi(metrics, prediction, gold):
    prediction_normalize = normalize_evi(prediction)
    gold_normalize = normalize_evi(gold)
    #
    cur_evi_pred = set(map(tuple, prediction_normalize))
    gold_evi_pred = list(map(lambda e: set(map(tuple, e)), gold_normalize))
    #
    num_matches = 0
    num_preds = len(cur_evi_pred)
    num_golds = len(gold_evi_pred)

    for pred_evidence in cur_evi_pred:
        for gold_evidences in gold_evi_pred:
            if pred_evidence in gold_evidences:
                num_matches += 1
                break

    prec = num_preds and num_matches / num_preds
    recall = num_golds and num_matches / num_golds
    f1 = 2 * prec * recall / (prec + recall) if prec + recall > 0 else 0.0
    em = 1.0 if num_matches == num_preds == num_golds else 0.0
    
    metrics['evi_em'] += em
    metrics['evi_f1'] += f1
    metrics['evi_prec'] += prec
    metrics['evi_recall'] += recall

    return em, prec, recall


def eval(prediction_file, gold_file, alias_file):
    aliases = {}

    with open(prediction_file) as f:
        prediction = json.load(f)
    with open(gold_file) as f:
        gold = json.load(f)
    with open(alias_file) as f:
        for json_line in map(json.loads, f):
            aliases[json_line["Q_id"]] = {
                "aliases": set(json_line["aliases"] + json_line["demonyms"])
            }

    metrics = {'em': 0, 'f1': 0, 'prec': 0, 'recall': 0,
        'sp_em': 0, 'sp_f1': 0, 'sp_prec': 0, 'sp_recall': 0,
        'evi_em': 0, 'evi_f1': 0, 'evi_prec': 0, 'evi_recall': 0,
        'joint_em': 0, 'joint_f1': 0, 'joint_prec': 0, 'joint_recall': 0}

    for dp in gold:
        cur_id = dp['_id']
        can_eval_joint = True
        # answer prediction task
        if cur_id not in prediction['answer']:
            print('missing answer {}'.format(cur_id))
            can_eval_joint = False
        else:
            gold_answers = {dp['answer']}  # Gold span

            if dp['answer_id'] in aliases and aliases[dp['answer_id']]["aliases"]:
                gold_answers.update(aliases[dp['answer_id']]["aliases"])

            em, prec, recall = update_answer(
                metrics, prediction['answer'][cur_id], gold_answers)
        # sentence-level supporting facts prediction task
        if cur_id not in prediction['sp']:
            print('missing sp fact {}'.format(cur_id))
            can_eval_joint = False
        else:
            sp_em, sp_prec, sp_recall = update_sp(
                metrics, prediction['sp'][cur_id], dp['supporting_facts'])
        # evidence generation task
        if cur_id not in prediction['evidence']:
            print('missing evidence {}'.format(cur_id))
            can_eval_joint = False
        else:
            gold_evidences = []

            for evidence_idx, (sub_str, rel_str, obj_str) in enumerate(dp['evidences']):
                sub_strs = {sub_str}
                obj_strs = {obj_str}

                if dp['evidences_id'] != []:
                    #
                    assert len(dp['evidences_id']) == len(dp['evidences'])
                    sub_id, rel_id, obj_id = dp['evidences_id'][evidence_idx]
                    
                    assert rel_id == rel_str

                    if sub_id in aliases:
                        sub_strs.update(aliases[sub_id]["aliases"])
                    if obj_id in aliases:
                        obj_strs.update(aliases[obj_id]["aliases"])
                    
                gold_evidence = []

                for sub_str, obj_str in itertools.product(sub_strs, obj_strs):
                    gold_evidence.append([sub_str, rel_str, obj_str])

                gold_evidences.append(gold_evidence)

            evi_em, evi_prec, evi_recall = update_evi(
                metrics, prediction['evidence'][cur_id], gold_evidences)

        if can_eval_joint:
            joint_prec = prec * sp_prec * evi_prec
            joint_recall = recall * sp_recall * evi_recall
            #
            if joint_prec + joint_recall > 0:
                joint_f1 = 2 * joint_prec * joint_recall / (joint_prec + joint_recall)
            else:
                joint_f1 = 0.
            joint_em = em * sp_em * evi_em

            metrics['joint_em'] += joint_em
            metrics['joint_f1'] += joint_f1
            metrics['joint_prec'] += joint_prec
            metrics['joint_recall'] += joint_recall

    N = len(gold)

    for k in metrics.keys():
        metrics[k] = round(metrics[k] / N * 100, 2)

    print(json.dumps(metrics, indent=4))


# ------------------------------------------------------------------- the platform ---


def _one_question(prediction: str, golds) -> dict:
    """Upstream's `update_answer`, applied to one question and a fresh accumulator.

    The per-question metric *is* this call: `update_answer` writes `metrics['f1'] +=
    max_f1` and returns the other three, so a dict seeded at zero comes back holding this
    question's answers and nothing else. Re-deriving the max here instead would be a second
    implementation of the metric, which is the thing the drift test exists to prevent.
    """
    metrics = {"em": 0.0, "f1": 0.0, "prec": 0.0, "recall": 0.0}
    update_answer(metrics, prediction, golds)
    return metrics


def score(prediction: str, gold: dict) -> dict:
    """Ans F1, the official answer column, over `{answer} | aliases`.

    A gold with no `answer` is reported rather than scored: it did not come from this
    adapter's pool, and scoring it would invent a zero. (Reasoning Gym taught this one --
    a missing field is a platform bug, not a wrong answer.)
    """
    if not gold.get("answer"):
        return {"reward": 0.0, "correct": False,
                "official": {"metric": None},
                "why": "gold has no answer: not a row of this pool"}
    metrics = _one_question(prediction, {gold["answer"], *gold.get("aliases", [])})
    return {
        "reward": float(metrics["f1"]),
        "correct": bool(metrics["em"]),
        "official": {"metric": "2WikiMultihopQA Ans F1 (official v1.1 evaluator)",
                     "em": metrics["em"], "f1": metrics["f1"],
                     "prec": metrics["prec"], "recall": metrics["recall"],
                     "id": gold.get("id"), "type": gold.get("type")},
        "why": (f"Ans F1={metrics['f1']:g}, Ans EM={metrics['em']:g}; Sup/Evi/Joint are "
                "computed by this module and not reported (no evidence channel)"),
    }


_ALIASES: dict[str, list[str]] | None = None


def _aliases() -> dict[str, list[str]]:
    """`{Q-id: [alias, ...]}`, from the official alias table. Loaded once.

    Only the **pool's** half of the platform reads this: the gold travels to the verifier
    with the aliases inline, so the check in the verification namespace never opens a file
    under `DATASET_ROOT` (it cannot see one; `docs/dataset-onboarding-skill.md` §16).
    """
    global _ALIASES
    if _ALIASES is None:
        table: dict[str, list[str]] = {}
        with (DATASET_ROOT / ALIAS_FILE).open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                entry = json.loads(line)
                # Sorted and de-duplicated so the gold a task carries is a function of the
                # row, not of the file's line order.
                table[entry["Q_id"]] = sorted(set(entry["aliases"]) | set(entry["demonyms"]))
        _ALIASES = table
    return _ALIASES


def _rows() -> dict[str, list[dict]]:
    with (DATASET_ROOT / DATA_FILE).open(encoding="utf-8") as handle:
        rows = json.load(handle)
    if len(rows) != EXPECTED_ROWS or len({row["_id"] for row in rows}) != EXPECTED_ROWS:
        raise ValueError(f"expected exactly {EXPECTED_ROWS} unique 2WikiMultihopQA dev rows")
    if not all(row["answer"] and row.get("context") for row in rows):
        raise ValueError("this adapter requires dev rows with an answer and a context")
    return {"dev": rows}


def _question(row: dict) -> str:
    """The question plus the ten released paragraphs, in the released order.

    Nothing else: `supporting_facts`, `evidences`, `evidences_id`, `answer_id`,
    `entity_ids` and `type` are annotations, and a prompt that carried them would grade
    the agent's reading of a label rather than of the paragraphs.
    """
    context = "\n\n".join(f"{title}\n{' '.join(sentences)}"
                           for title, sentences in row["context"])
    return f"Question: {row['question']}\n\nContext paragraphs:\n{context}"


def _gold(row: dict) -> dict:
    return {"answer": row["answer"],
            "aliases": _aliases().get(row.get("answer_id"), []),
            "id": row["_id"], "type": row["type"]}


def _goal(question: str, gold: dict) -> str:
    return (question + "\n\nAnswer with the short answer only. Reward is the official "
            "2WikiMultihopQA **Ans F1** over the gold answer and its Wikidata aliases; the "
            "official evaluator's Sup, Evi and Joint columns need evidence this interface "
            "does not carry and are not reported.\n\n"
            "Write `answer.txt`, or use the qa submit command:\n"
            '    python3 qa/bin/qa submit "<answer>"\n')


def _downloads() -> list[dict]:
    return [
        {"kind": "hf-dataset", "name": "2WikiMultihopQA dev, with answer_id (official "
                                      "December 2020 release)",
         "repo": "kamelliao/2wikimultihopqa", "version": REVISION,
         "size": "57,614,142 + 17,501,406 bytes", "files": [DATA_FILE, ALIAS_FILE],
         "dst": ".", "sha256": {DATA_FILE: DATA_SHA256, ALIAS_FILE: ALIAS_SHA256},
         "note": "The id-enriched release the v1.1 evaluator needs: `answer_id` on 10,603 of 12,576 rows, and the official 203,297-entry alias table. The official host is a Dropbox link unreachable from the onboarding machine, so this third-party mirror is pinned by digest; identity against the official zip rests on a second independent mirror agreeing on every row (see WITNESS_FILE) and on every answer_id resolving. A parquet mirror is NOT a substitute: it has no answer_id, and without the alias channel Ans F1 drops (measured 68.18 -> 67.54 on 500 rows). No agent-visible field comes from here beyond the question and its ten paragraphs."},
        {"kind": "hf-dataset", "name": "2WikiMultihopQA validation, independent mirror "
                                      "(witness only)",
         "repo": "framolfese/2WikiMultihopQA", "version": WITNESS_REVISION,
         "size": "29,505,064 bytes (12,576 dev rows)", "files": [WITNESS_FILE],
         "dst": ".", "sha256": {WITNESS_FILE: WITNESS_SHA256},
         "note": "Kept as the **witness**, not as the pool: no run reads it. Its 12,576 rows agree with dev.json on question, answer and supporting facts for every row, which is the only evidence available on this machine that dev.json is the official dev set. It carries no answer_id, which is why it cannot be the pool."},
        {"kind": "http", "name": "2WikiMultihopQA official evaluation code",
         "version": OFFICIAL_COMMIT,
         "url": f"https://codeload.github.com/Alab-NII/2wikimultihop/tar.gz/{OFFICIAL_COMMIT}",
         "size": "389,466 bytes compressed source", "sha256": SOURCE_SHA256,
         "dst": "_src/2wikimultihop.tar.gz", "extract_to": "_src",
         "note": "Pins `2wikimultihop_evaluate_v1.1.py`, the file transcribed verbatim in this module, and `2wikimultihop_evaluate.py` v1.0 beside it. The tests read it from `_src` and compare bytes; no run imports it. Upstream prints a 16-key metrics dict and rounds to 2 decimals at the end, so the aggregate is order-sensitive and is asserted against this file rather than against a paraphrase."},
    ]


_SPEC = base.QASpec(name="twowikimultihopqa", root=DATASET_ROOT, rows=_rows,
                   question=_question, gold=_gold, goal=_goal, score=score,
                   downloads=_downloads, split="dev",
                   source=f"2WikiMultihopQA dev (id-enriched release), "
                          f"kamelliao/2wikimultihopqa@{REVISION}")
_BUILT = _SPEC.build()
DEFAULT_ENV = _BUILT["DEFAULT_ENV"]
ENV = _BUILT["ENV"]
SPLIT = _BUILT["SPLIT"]

#: The benchmark's own evaluation set, within this adapter's pool. The pool is the dev
#: split, which is what the paper's dev columns report on; `test` is not released with
#: answers.
#:
#: `None` because the benchmark released no *study* split for this table: `train.json`
#: exists at the same revision and is deliberately not loaded, so the pool **is** the
#: scored split and every task in it belongs to the evaluation set -- which claims nothing
#: about whether the pool is the whole of it. `--split official --side eval` scores the
#: whole pool, the comparable run; `--split declared` keeps the platform's hash third
#: (`SPLIT_SOURCE == "hash"`).
OFFICIAL_EVAL = _BUILT["OFFICIAL_EVAL"]

#: Which rule produced `SPLIT`: `"hash"` here -- the benchmark published no study split
#: this adapter loads, so the platform imposes one. See `data/qa/base.py::division`.
SPLIT_SOURCE = _BUILT["SPLIT_SOURCE"]


def __getattr__(name):
    return base.module_getattr(_SPEC, name)


def load():
    return _SPEC.load()


def downloads():
    return _downloads()


def provision_status():
    return _SPEC.provision_status()
