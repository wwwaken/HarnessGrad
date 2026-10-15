"""Rehash local input sources and archive exact source excerpts; never run scorers."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NAMES = (
    "bfcl_v3", "chessbench_puzzles", "fever", "gsm8k", "hotpotqa", "musique",
    "physicsquestions", "reasoning_gym", "sportsunderstanding", "strategyqa",
    "triviaqa", "twowikimultihopqa",
)


def identity(path):
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            size += len(block)
            digest.update(block)
    return {"path": str(path), "bytes": size, "sha256": digest.hexdigest()}


def main():
    print(json.dumps({"baseline": subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "scope": "local source/input identity only; no scorer or benchmark execution"}))
    for name in NAMES:
        manifest = ROOT / f"tests/fixtures/hg_wclo_actor/gold/{name}.json"
        record = json.loads(manifest.read_text())
        artifacts = []
        for item in record["artifacts"]:
            actual = identity(Path(item["path"]))
            actual["matches_closure_record"] = actual["sha256"] == item["sha256"]
            assert actual["matches_closure_record"], actual
            artifacts.append(actual)
        print(json.dumps({"dataset": name, "closure_manifest": identity(manifest),
                          "source_artifacts_rehashed": artifacts}, sort_keys=True))

    # Current file+line evidence and complete-file identities, read directly from disk.
    excerpts = {
        "data/scaffolds/qa/base.py": [(247, 258), (337, 360)],
        "data/scaffolds/qa/verify/check.py": [(75, 89), (160, 191), (251, 261)],
        "eval/verification/verifier.py": [(480, 535), (564, 572), (680, 724)],
        "eval/run/runner.py": [(525, 529)],
        "eval/observe/tracing.py": [(314, 325)],
        "data/datasets/alfworld.py": [(342, 360)],
        "data/datasets/alfworld/verify/check.py": [(131, 145), (155, 160)],
        "data/datasets/bird_minidev.py": [(251, 265)],
        "data/datasets/bird_minidev/verify/check.py": [(90, 111)],
        "data/datasets/ds1000.py": [(180, 205)],
        "data/datasets/ds1000/verify/check.py": [(20, 32)],
        "data/datasets/jericho.py": [(252, 273)],
        "data/datasets/jericho/verify/check.py": [(84, 94), (105, 120)],
        "data/datasets/jericho/lib/jer_env.py": [(49, 62)],
        "data/datasets/livecodebench.py": [(262, 282)],
        "data/datasets/livecodebench/verify/check.py": [(138, 156)],
        "data/datasets/scienceworld.py": [(306, 328)],
        "data/datasets/scienceworld/verify/check.py": [(125, 139), (157, 166)],
        "data/datasets/scienceworld/lib/scw_env.py": [(130, 145)],
        "data/datasets/spreadsheetbench.py": [(231, 253)],
        "data/datasets/spreadsheetbench/verify/check.py": [(305, 327), (370, 376)],
    }
    for name in NAMES:
        path = ROOT / f"data/datasets/{name}.py"
        lines = path.read_text().splitlines()
        selected = [(n, line) for n, line in enumerate(lines, 1)
                    if any(token in line for token in (
                        "def _gold(", "gold=", "base.QASpec", "def verifier(",
                        "super().verifier(", "def verify_for(", "_SPEC.verifier(",
                        "QASpec.verifier(", "def score(", "def score_prediction("))]
        if name == "bfcl_v3":
            selected += [(n, lines[n - 1]) for n in range(491, 506)]
        print(json.dumps({"adapter": identity(path), "selected_lines": selected}, sort_keys=True))
    for rel, spans in excerpts.items():
        path = ROOT / rel
        lines = path.read_text().splitlines()
        print(json.dumps({"source": identity(path), "excerpts": [
            {"line": n, "text": lines[n - 1]} for start, end in spans
            for n in range(start, min(end, len(lines)) + 1)]}, sort_keys=True))


if __name__ == "__main__":
    main()
