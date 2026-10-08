"""LiveCodeBench release_v6: refused pending a released oracle solution.

The pinned release contains 1,055 prompts, starter programs, and public/private tests
(six cumulative JSONL files), but no reference program.  The official scorer is
``codegen_metrics``: it runs each model completion through ``run_test`` and computes
pass@k from the resulting booleans.  That is a model-evaluation metric, not a
gold-answer table.  Without a reference completion an oracle control cannot reach 1;
using a hand-written solution or a model completion would be a different benchmark.
"""
from __future__ import annotations

from pathlib import Path

KIND = "dataset"
DATASET_ROOT = Path("/mnt/20t/xubuqiang/datasets/livecodebench")
REVISION = "0fe84c3912ea0c4d4a78037083943e8f0c4dd505"
UPSTREAM_COMMIT = "28fef95ea8c9f7a547c8329f2cd3d32b92c1fa24"
REFUSED = (
    "livecodebench: release_v6 is unreproducible as an oracle dataset. The pinned "
    "Hugging Face release has 1,055 prompts/tests in six files (4,485,994,821 bytes) "
    "but publishes no reference solution. The official codegen_metrics scorer runs "
    "model-generated completions with run_test and reports pass@k; it cannot produce "
    "an oracle completion from the released rows. A hand-written or model-generated "
    "completion would change the benchmark, so gate 1 cannot reach 1. An upstream "
    "release containing reference programs, or an explicitly different contract, is "
    "needed before onboarding."
)

_FILES = {
    "test.jsonl": "2bd02b38beb48e8c46b5b9987095d999ff38cd8efc255ea5d58974317c48f63f",
    "test2.jsonl": "095df7c5daf15f882c51a9deb84085cff1e073495a5dbcf95015a564d485f3a3",
    "test3.jsonl": "28ed26cc83363ce3f1fe2d5fad9f8393077beb1907b167a31bd3b32f80801b79",
    "test4.jsonl": "d711138ddaebfcf5f8ec6a4283ee677298c0f5c5d374a235af92aaf0584510da",
    "test5.jsonl": "7f77571c2a6df0c2a72a3277650309f67e01e0008e18117e624633df53f81214",
    "test6.jsonl": "bb4c364f71921c4495a6ad15abe1a927350b720009f4933e2e71f8af0f6fd1f5",
}


def downloads() -> list[dict]:
    base = "https://hf-mirror.com/datasets/livecodebench/code_generation_lite/resolve/"
    entries = []
    for name, digest in _FILES.items():
        entries.append({"kind": "http", "name": name, "version": REVISION,
                        "url": base + REVISION + "/" + name, "dst": "_src/" + name,
                        "sha256": digest, "size": "release_v6 cumulative JSONL shard",
                        "note": "Pinned release_v6 shard; all six cumulative shards are required for the official 1,055-task pool."})
    return entries + [{"kind": "http", "name": "LiveCodeBench scorer", "version": UPSTREAM_COMMIT,
                       "url": "https://codeload.github.com/LiveCodeBench/LiveCodeBench/tar.gz/" + UPSTREAM_COMMIT,
                       "dst": "_src/upstream.tar.gz", "size": "pinned source archive",
                       "note": "Pinned upstream scorer and executor; it supplies tests and pass@k but no reference solutions for an oracle."}]


def load():
    raise ValueError(REFUSED)


def provision_status():
    return {"root": str(DATASET_ROOT), "present": all((DATASET_ROOT / "_src" / n).is_file() for n in _FILES), "tasks": 1055}


__all__ = ["KIND", "DATASET_ROOT", "REFUSED", "load", "downloads", "provision_status"]
