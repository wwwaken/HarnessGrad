#!/usr/bin/env python3
"""Compute literal per-case agreement; keep incompatible input panels separate."""
from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
comparisons = {}
for dataset in ("gsm8k", "strategyqa"):
    official = json.loads((ROOT / f"{dataset}-official.json").read_text())["results"]
    local = json.loads((ROOT / f"{dataset}-local.json").read_text())["results"]
    assert len(official) == len(local)
    rows = []
    counts = Counter()
    panel_counts = {}
    for a, b in zip(official, local):
        assert (a["id"], a["prediction"], a["canonical_gold"]) == (b["id"], b["prediction"], b["canonical_gold"])
        agreement = a["correct"] == b["correct"]
        row = {"id": a["id"], "panel": a["panel"], "prediction": a["prediction"],
               "canonical_gold": a["canonical_gold"], "official_correct": a["correct"],
               "local_correct": b["correct"], "agreement": agreement}
        rows.append(row)
        key = "agreement" if agreement else "divergence"
        counts[key] += 1
        panel_counts.setdefault(a["panel"], Counter())[key] += 1
    comparisons[dataset] = {"counts": dict(counts), "panel_counts": {k: dict(v) for k, v in panel_counts.items()},
                            "cases": rows}
official = json.loads((ROOT / "strategyqa-official.json").read_text())["results"][:4]
projected = json.loads((ROOT / "strategyqa-local-projected.json").read_text())["results"]
rows = []
counts = Counter()
for a, b in zip(official, projected):
    assert (a["id"], a["prediction"], a["canonical_gold"]) == (b["id"], b["prediction"], b["canonical_gold"])
    agreement = a["correct"] == b["correct"]
    rows.append({"id": a["id"], "canonical_prediction": a["prediction"],
                 "local_passed_prediction": b["passed_prediction"],
                 "official_correct": a["correct"], "local_correct": b["correct"], "agreement": agreement})
    counts["agreement" if agreement else "divergence"] += 1
comparisons["strategyqa_semantic_boolean_projection"] = {"counts": dict(counts), "cases": rows,
    "caveat": "Separate fixture-only type projection; raw prediction values differ. Not production text-scoring equivalence."}
print(json.dumps(comparisons, indent=2, sort_keys=True))
