"""Reproduce inert row/split custody from preserved bytes; no upstream code execution.

--capture reads the four installed files once and records their path, bytes and
digest. Default/--check use ONLY preserved bytes. Nothing selects or runs tasks.
The package/pool and ReWOO acquisition packets are verified separately.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NAMES = ("physicsquestions", "strategyqa", "sportsunderstanding", "reasoning_gym")
MEMBERS = dict(physicsquestions="physics_question.csv", strategyqa="strategy_qa.csv",
               sportsunderstanding="sports_understanding.csv")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode()


def literal(path, name):
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError((path, name))


def input_path(name):
    if name == "reasoning_gym":
        return Path("/mnt/20t/xubuqiang/datasets/reasoning_gym/pool.jsonl")
    return Path("/mnt/20t/xubuqiang/datasets") / name / (
        "ReWOO-9cd0283043ff4be0c9d614fda2789d143ca6ffd1/data/bigbench/" + MEMBERS[name])


def capture():
    target = ROOT / "installed"
    target.mkdir()  # Refuse to overwrite a previous capture.
    files = {}
    for name in NAMES:
        source = input_path(name)
        raw = source.read_bytes()
        output = target / (name + (".jsonl" if name == "reasoning_gym" else ".csv"))
        output.write_bytes(raw)
        files[name] = {"source_path": str(source), "resolved_path": str(source.resolve()),
                       "fixture": str(output.relative_to(ROOT)), "bytes": len(raw),
                       "sha256": sha(raw)}
    (ROOT / "installed-receipt.json").write_text(json.dumps({
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "method": "read_bytes only; no writes to dataset roots; no scorer/generator/import/run",
        "files": files,
        "limit": "Point-in-time host observation, not pristine-verifier execution custody.",
    }, indent=2) + "\n")


def derive():
    receipt = json.loads((ROOT / "installed-receipt.json").read_text())
    summary = {}
    manifests = {}
    for name in NAMES:
        info = receipt["files"][name]
        raw = (ROOT / info["fixture"]).read_bytes()
        assert len(raw) == info["bytes"] and sha(raw) == info["sha256"]
        adapter = ROOT / "source/data/datasets" / (name + ".py")
        if name == "reasoning_gym":
            source_rows = [json.loads(line) for line in raw.decode().splitlines() if line.strip()]
            rows = source_rows
            split_name = "eval"
            prepare = ROOT / "source/data/datasets/reasoning_gym/prepare.py"
            families = literal(prepare, "FAMILIES")
            size = literal(adapter, "PER_FAMILY")
            assert len(families) == 89 and size == 20
            assert literal(adapter, "SEED") == literal(prepare, "SEED") == 20261008
            assert literal(adapter, "VERSION") == literal(prepare, "VERSION") == "0.1.25"
            assert sha(raw) == literal(adapter, "POOL_SHA256")
            assert [(r["family"], r["index"]) for r in rows] == [
                (family, i) for family in families for i in range(size)]
            assert all(r["entry"].get("answer") is not None
                       and str(r["entry"]["answer"]).strip() for r in rows)
            assert all(r["question"] == str(r["entry"]["question"]).strip() for r in rows)
        else:
            source_rows = list(csv.DictReader(io.StringIO(raw.decode(), newline="")))
            rows = [r for r in source_rows if str(r.get("input") or "").strip()] \
                if name == "physicsquestions" else source_rows
            split_name = "test"
            assert len(rows) == literal(adapter, "N_TOTAL")
            assert all(str(r["input"]).strip() for r in rows)
            if name == "physicsquestions":
                for row in rows:
                    assert row["target"].startswith("Can be one of ")
                    accepted = ast.literal_eval(row["target"][len("Can be one of "):])
                    assert isinstance(accepted, list) and accepted and all(
                        isinstance(answer, str) and answer for answer in accepted)
            else:
                labels = literal(adapter, "LABELS")
                assert all(str(r["target"]).strip() in labels for r in rows)
        ids = [f"{name}/{split_name}/{i}" for i in range(len(rows))]
        train = [t for t in ids if hashlib.sha256(t.encode()).digest()[0] % 3 != 0]
        evaluation = [t for t in ids if hashlib.sha256(t.encode()).digest()[0] % 3 == 0]
        evaluation_set = set(evaluation)
        assert train and evaluation and len(set(ids)) == len(rows)
        row_manifest = []
        for i, (tid, row) in enumerate(zip(ids, rows)):
            item = {"task_id": tid, "loaded_position": i, "parsed_row_sha256": sha(encoded(row)),
                    "declared_side": "eval" if tid in evaluation_set else "train"}
            if name == "reasoning_gym":
                item.update(family=row["family"], family_index=row["index"])
            row_manifest.append(item)
        # Same JSON serialization as registry.split_hash; an ID split hash alone
        # never proves content identity, so source and row hashes travel with it.
        split_sha = sha(json.dumps({"train": sorted(train), "eval": sorted(evaluation)},
                                  sort_keys=True).encode())
        manifests[name] = {
            "dataset": name, "source_sha256": sha(raw), "source_bytes": len(raw),
            "source_pool_split": split_name,
            "row_hash_encoding": "UTF-8 json.dumps(ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)",
            "loaded_rows": row_manifest,
            "structurally_eligible_ids": ids,
            "eligibility_limit": "Loader/gold shape and nonempty content only; no scoring, offline or admission gates tested.",
            "declared_split": {"source": "hash", "train": train, "eval": evaluation,
                               "official_eval": None, "split_sha256": split_sha},
            "official_mode_eval_ids": ids,
            "official_mode_limit": "Whole adapter pool; not evidence of original benchmark completeness or heldout split.",
            "selected_manifest": None,
            "selected_manifest_limit": "No run-specific selected manifest or run ID supplied for these blockers. Pool/eligible/split inventories do not attest selection or selected-only runtime export.",
        }
        summary[name] = {"installed_sha256": sha(raw), "installed_bytes": len(raw),
                         "source_rows": len(source_rows), "loaded_rows": len(rows),
                         "nonempty_questions": len(rows),
                         "declared_train_ids": len(train), "declared_eval_ids": len(evaluation),
                         "split_sha256": split_sha,
                         "structural_eligible_digest": sha(encoded(sorted(set(ids)))),
                         "selected_manifest": None,
                         "run_id": None, "measured_trials": None, "invalid_trials": None,
                         "unmeasured_trials": None, "production_authorized": False}
        if name == "reasoning_gym":
            summary[name].update(family_counts=dict(sorted(Counter(r["family"] for r in rows).items())),
                                 family_rule_reference_empty_scores_verified=False,
                                 generation_seed_verified_by_structural_check=False)
    return manifests, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.capture:
        capture()
    manifests, summary = derive()
    for name, content in manifests.items():
        path = ROOT / "manifests" / (name + ".json")
        body = json.dumps(content, ensure_ascii=False, indent=2) + "\n"
        if args.check:
            assert path.read_text() == body, path
        else:
            path.write_text(body)
    path = ROOT / "custody-summary.json"
    body = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        assert path.read_text() == body, path
    else:
        path.write_text(body)
    print(json.dumps({"valid": True, "datasets": {name: {
        key: value for key, value in detail.items() if key != "family_counts"}
        for name, detail in summary.items()},
        "scorer_generator_model_gpu_pilot_executed_by_this_check": False}, indent=2))


if __name__ == "__main__":
    main()
