"""LiveCodeBench release_v6: refused because the release ships **tests but no solution**.

The measurement that decides this one was made twice, and the first version of this file
got it wrong in a way worth recording: it refused because "the released rows carry no
reference solution, so gate 1 cannot reach 1". The first half of that is true and the
second half is not. Gate 1 asks whether the **check** is reachable, and here it is: the
tests are in the release, they decode offline with the standard library, and a program that
passes them is a completion the official scorer counts. What is genuinely absent is a
*released* reference completion -- the thing `oracle_files(task)` is supposed to return as
data -- so an oracle for this benchmark has to be **authored by us** and validated by the
released tests. That is a contract change (`data/qa/control.py --oracle` submits the
dataset's own reference answer; there is none here), and a contract change is a platform
decision, not a detail to slip into an adapter.

Measured, and re-checkable from the pinned artifacts
---------------------------------------------------
* `livecodebench/code_generation_lite@0fe84c3912ea0c4d4a78037083943e8f0c4dd505`, six
  cumulative shards, **1,055** problems, **4,485,994,821** bytes; every shard's sha256 was
  verified against the declared digest in `downloads()`, which is what makes the pool
  reproducible at all.
* The rows carry `question_id`, `question_title`, `question_content`, `platform`,
  `contest_id`, `contest_date`, `difficulty`, `starter_code`, `public_test_cases`,
  `private_test_cases`, `metadata` -- and **no** field holding a solution, in any spelling.
* `public_test_cases` is plaintext JSON; `private_test_cases` is
  `json.loads(pickle.loads(zlib.decompress(base64.b64decode(...))))`, the released decode
  step transcribed below. It needs no key: the tests are **available**, and pass@k is
  computable offline.
* The metric is `lcb_runner/evaluation/pass_k_utils.py` -- `estimate_pass_at_k` and
  `compute_metrics_from_results`, both transcribed below -- applied to per-test booleans
  produced by `testing_util.run_test`. The platform's verification namespace supplies the
  sandbox upstream warns it does not have, so nothing here is unimplementable.

What would make it reachable
----------------------------
An explicit contract for authored reference completions -- one reference program per task,
validated by the released tests and kept out of the agent's view -- or an upstream release
that ships solutions. Until one of those exists the honest statement is "the metric is
computable and the pool is pinned; the oracle is not derivable from the release", which is
what `REFUSED` says. `estimate_pass_at_k` lives here, runnable and differential-tested
against the pinned archive, for the reason `data/qa/evidence_scorers.py` gives: a refusal is
only credible if the code that would compute the number exists.
"""
from __future__ import annotations

import base64
import json
import pickle
import zlib

import numpy as np
from pathlib import Path

KIND = "dataset"
DATASET_ROOT = Path("/mnt/20t/xubuqiang/datasets/livecodebench")
REVISION = "0fe84c3912ea0c4d4a78037083943e8f0c4dd505"
UPSTREAM_COMMIT = "28fef95ea8c9f7a547c8329f2cd3d32b92c1fa24"
#: The union of the six cumulative shards, measured once: counting it again costs 4.5 GB of
#: parsing, and the shards' digests are what actually pin it.
PROBLEMS = 1055

REFUSED = (
    "livecodebench: the pinned release_v6 (1,055 problems, 4,485,994,821 bytes across six "
    "cumulative shards, every sha256 verified) carries prompts, starter code and both test "
    "sets, but **no reference completion** -- and the answer contract has no channel for an "
    "authored one, while gate 1's oracle must be derived from the benchmark's own data. The "
    "metric itself is not the obstacle: private_test_cases decodes offline as "
    "json.loads(pickle.loads(zlib.decompress(base64.b64decode(...)))), and the official "
    "pass@k is transcribed and differential-tested in this module. Onboarding needs an "
    "explicit contract change (authored, test-validated reference completions held out of "
    "the agent's view) or an upstream release containing solutions; until one of those "
    "exists this adapter refuses rather than reporting a pass rate under the benchmark's name."
)

#: Shard name -> sha256, verified at onboarding against the files on disk.
_FILES = {
    "test.jsonl": "2bd02b38beb48e8c46b5b9987095d999ff38cd8efc255ea5d58974317c48f63f",
    "test2.jsonl": "095df7c5daf15f882c51a9deb84085cff1e073495a5dbcf95015a564d485f3a3",
    "test3.jsonl": "28ed26cc83363ce3f1fe2d5fad9f8393077beb1907b167a31bd3b32f80801b79",
    "test4.jsonl": "d711138ddaebfcf5f8ec6a4283ee677298c0f5c5d374a235af92aaf0584510da",
    "test5.jsonl": "7f77571c2a6df0c2a72a3277650309f67e01e0008e18117e624633df53f81214",
    "test6.jsonl": "bb4c364f71921c4495a6ad15abe1a927350b720009f4933e2e71f8af0f6fd1f5",
}
SOURCE_SHA256 = "56c7c42aee979def86b69547ecd6d5a877a0e4940af8923bf4325ca0defecbaf"


# ---------------------------------------------------------------------------------------
# `lcb_runner/evaluation/pass_k_utils.py` lines 4-53, byte for byte: `estimate_pass_at_k`
# with its inner `estimator`, and `compute_metrics_from_results`. numpy is imported at
# module level the way upstream does it, because the alternative -- moving that import
# inside the functions -- makes the transcription *almost* verbatim, and "almost verbatim"
# is a claim no test can check. The cost is one numpy import in a module that refuses; the
# alternative is a drift that the diff below cannot see.
# ---------------------------------------------------------------------------------------
def estimate_pass_at_k(num_samples, num_correct, k):
    """Estimates pass@k of each problem and returns them in an array."""

    def estimator(n: int, c: int, k: int) -> float:
        """Calculates 1 - comb(n - c, k) / comb(n, k)."""
        if n - c < k:
            return 1.0
        return 1.0 - np.prod(1.0 - k / np.arange(n - c + 1, n + 1))

    import itertools

    if isinstance(num_samples, int):
        num_samples_it = itertools.repeat(num_samples, len(num_correct))
    else:
        assert len(num_samples) == len(num_correct)
        num_samples_it = iter(num_samples)

    return np.array(
        [estimator(int(n), int(c), k) for n, c in zip(num_samples_it, num_correct)]
    )


def compute_metrics_from_results(results, k_list=[1, 5]):
    total = []
    correct = []
    task_ids = []
    for task_id, res in results.items():
        all_correct = []
        for generation in res:
            gen = np.array(generation)
            all_correct.append(np.all(gen > 0))
        task_ids.append(task_id)
        total.append(len(all_correct))
        correct.append(sum(all_correct))
    total = np.array(total)
    correct = np.array(correct)
    ks = k_list
    detail_pass_at_k = {
        f"pass@{k}": estimate_pass_at_k(total, correct, k).tolist()
        for k in ks
        if (total >= k).all()
    }
    pass_at_k = {
        f"pass@{k}": estimate_pass_at_k(total, correct, k).mean()
        for k in ks
        if (total >= k).all()
    }
    detail_metrics = {k: dict(zip(task_ids, v)) for k, v in detail_pass_at_k.items()}
    pass_at_k["detail"] = detail_metrics
    return pass_at_k


def decode_private_test_cases(value: str) -> list[dict]:
    """The released decode step, from
    `lcb_runner/benchmarks/code_generation.py::CodeGenerationProblem.__post_init__`: the
    field is plaintext JSON when it already is, and base64+zlib+pickle otherwise.

    This function is what makes the refusal precise -- it proves the tests are *available*,
    so "the metric cannot be computed" is not the reason this dataset is not onboarded.
    """
    try:
        cases = json.loads(value)
    except ValueError:
        cases = json.loads(
            pickle.loads(zlib.decompress(base64.b64decode(value.encode("utf-8")))))
    return cases


def downloads() -> list[dict]:
    base = "https://hf-mirror.com/datasets/livecodebench/code_generation_lite/resolve/"
    entries = []
    for name, digest in _FILES.items():
        entries.append({
            "kind": "http", "name": name, "version": REVISION,
            "url": base + REVISION + "/" + name, "dst": "_src/" + name,
            "sha256": digest, "size": "release_v6 cumulative JSONL shard",
            "note": "Pinned release_v6 shard; all six cumulative shards are the official 1,055-task pool, and the union -- not any single shard's row count -- is what the six digests pin. Every digest was verified against the files on disk at onboarding."})
    entries.append({
        "kind": "http", "name": "LiveCodeBench scorer", "version": UPSTREAM_COMMIT,
        "url": "https://codeload.github.com/LiveCodeBench/LiveCodeBench/tar.gz/" + UPSTREAM_COMMIT,
        "dst": "_src/upstream.tar.gz", "size": "3,361,935 bytes compressed source",
        "sha256": SOURCE_SHA256,
        "note": "Pinned upstream source: pass_k_utils.py (transcribed verbatim in this module), testing_util.py (run_test, the sandbox upstream warns it is not) and benchmarks/code_generation.py (the private-test decode step, also transcribed). It supplies the tests and pass@k but no reference solutions, which is exactly why gate 1 has no oracle here. Never enters an agent SETUP."})
    return entries


def load():
    raise ValueError(REFUSED)


def provision_status() -> dict:
    src = DATASET_ROOT / "_src"
    return {"root": str(DATASET_ROOT),
            "present": all((src / name).is_file() for name in _FILES),
            "tasks": PROBLEMS}


__all__ = ["KIND", "DATASET_ROOT", "REFUSED", "PROBLEMS", "SOURCE_SHA256", "downloads",
           "load", "provision_status", "estimate_pass_at_k",
           "compute_metrics_from_results", "decode_private_test_cases"]
