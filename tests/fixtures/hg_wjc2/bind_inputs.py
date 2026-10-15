"""Derive whole-pool gold hashes without adapter imports, scores or gold exports.

Execute only source-extracted standard-library projection helpers; bind their
source bytes, ordered input rows and exact QA verifier serialization together.
The output is a custody inventory, never a manifest or an eligibility claim.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import io
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NAMES = ("physicsquestions", "sportsunderstanding", "strategyqa")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode()


def derive():
    sources = {}
    inventories = {}
    for name in NAMES:
        path = ROOT / "data/datasets" / f"{name}.py"
        raw = path.read_bytes()
        tree = ast.parse(raw)
        literals = {}
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in {"CSV_PATH", "N_TOTAL", "LABELS"}:
                        literals[target.id] = ast.literal_eval(node.value)
        # These exact source helpers perform no I/O or scoring. In particular,
        # extracting them does not run the adapter's import-time build/load.
        helpers = {"_gold"}
        if name == "physicsquestions":
            helpers.add("accepted_answers")
        nodes = []
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name in helpers:
                nodes.append(node)
            elif name == "physicsquestions" and isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id in {"_TARGET", "_QUOTED"} for t in node.targets
            ):
                nodes.append(node)
        assert {n.name for n in nodes if isinstance(n, ast.FunctionDef)} == helpers
        namespace = {"re": re, **literals}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)
        source = {"sha256": sha(raw), "bytes": len(raw), "extracted_lines": [n.lineno for n in nodes]}
        sources[str(path.relative_to(ROOT))] = source
        data_path = Path("/mnt/20t/xubuqiang/datasets") / name / literals["CSV_PATH"]
        data_raw = data_path.read_bytes()
        rows = list(csv.DictReader(io.StringIO(data_raw.decode(), newline="")))
        if name == "physicsquestions":
            rows = [r for r in rows if str(r.get("input") or "").strip()]
        assert len(rows) == literals["N_TOTAL"]
        old = json.loads((ROOT / "tests/fixtures/hg_wjournalcov" / f"{name}-inventory.json").read_text())
        assert len(rows) == len(old["rows"])
        bound_rows = []
        for i, (row, previous) in enumerate(zip(rows, old["rows"], strict=True)):
            task_id = f"{name}/test/{i}"
            row_hash = sha(canonical(row))
            assert previous["task_id"] == task_id and previous["parsed_row_sha256"] == row_hash
            side = "eval" if hashlib.sha256(task_id.encode()).digest()[0] % 3 == 0 else "train"
            assert previous["declared_side"] == side
            gold = namespace["_gold"](row)
            # Exact encoding at data/scaffolds/qa/base.py:339; intentionally
            # different from the compact canonical parsed-row hash encoding.
            serialized = json.dumps(gold, ensure_ascii=False, sort_keys=True).encode("utf-8")
            assert str(gold["answer"]).strip()
            bound_rows.append({"task_id": task_id, "loaded_position": i,
                               "parsed_row_sha256": row_hash, "declared_side": side,
                               "gold_bytes": len(serialized), "gold_sha256": sha(serialized)})
        split = {side: sorted(r["task_id"] for r in bound_rows if r["declared_side"] == side)
                 for side in ("train", "eval")}
        split_hash = sha(json.dumps(split, sort_keys=True).encode())
        assert split_hash == old["declared_split"]["split_sha256"]
        inventories[name] = {"dataset": name, "input_path": str(data_path),
                             "input_bytes": len(data_raw), "input_sha256": sha(data_raw),
                             "rows": bound_rows, "loaded_rows": len(rows),
                             "default_split_sha256": split_hash,
                             "default_side_counts": {s: len(ids) for s, ids in split.items()},
                             "source_sha256": source["sha256"],
                             "scope": "Whole pool projection hashes; no selected gold/export, scoring or eligibility.",
                             "selection_packet": None, "run_id": None,
                             "chosen_split_mode": None, "chosen_side": None,
                             "selected_only_export": None, "measured_trials": None,
                             "invalid_trials": None, "unmeasured_trials": None}
    for rel in ("data/scaffolds/qa/base.py", "data/scaffolds/qa/verify/check.py",
                "data/scaffolds/scorer_input.py", "data/scaffolds/registry.py"):
        raw = (ROOT / rel).read_bytes()
        sources[rel] = {"sha256": sha(raw), "bytes": len(raw)}
    return {"sources.json": sources, **{f"{n}-gold-bindings.json": v for n, v in inventories.items()}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = derive()
    summary = {}
    for filename, value in outputs.items():
        encoded = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()
        target = HERE / filename
        if args.check:
            assert target.read_bytes() == encoded, filename
        else:
            assert not target.exists(), filename
            target.write_bytes(encoded)
        summary[filename] = {"sha256": sha(encoded), "bytes": len(encoded)}
        if "loaded_rows" in value:
            summary[filename].update({k: v for k, v in value.items() if k not in {"rows", "scope"}})
    print(json.dumps({"valid": True, "outputs": summary}, indent=2))


if __name__ == "__main__":
    main()
