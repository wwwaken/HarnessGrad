#!/usr/bin/env python3
"""Check evidence provenance, input alignment, counts and CLI metric correspondence."""
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
for source in json.loads((ROOT / "acquisition-with-contract.json").read_text())["source_files"]:
    data = (ROOT / source["destination"]).read_bytes()
    assert len(data) == source["bytes"]
    assert hashlib.sha256(data).hexdigest() == source["sha256"]
    assert hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest() == source["git_blob_sha1"]
inputs = json.loads((ROOT / "inputs.json").read_text())
comparisons = json.loads((ROOT / "comparison.json").read_text())
for dataset in ["gsm8k", "strategyqa"]:
    for scorer in ["official", "local"]:
        result = json.loads((ROOT / f"{dataset}-{scorer}.json").read_text())
        identity = result["identity"]
        assert hashlib.sha256((REPO / identity["source"]).read_bytes()).hexdigest() == identity["source_sha256"]
        assert len(result["results"]) == len(inputs[dataset])
        for case, measured in zip(inputs[dataset], result["results"]):
            assert (case["id"], case["prediction"], case["gold_answer"]) == (measured["id"], measured["prediction"], measured["canonical_gold"])
    counts = Counter("agreement" if row["agreement"] else "divergence" for row in comparisons[dataset]["cases"])
    assert dict(counts) == comparisons[dataset]["counts"]
for panel in ["valid_official_boolean", "adapter_text_official_out_of_contract"]:
    cases = [x for x in json.loads((ROOT / "strategyqa-official.json").read_text())["results"] if x["panel"] == panel]
    cli = json.loads((ROOT / f"strategyqa-{panel}-cli-metrics.json").read_text())
    assert cli["Accuracy"] == sum(x["correct"] for x in cases) / len(cases)
projected = json.loads((ROOT / "strategyqa-local-projected.json").read_text())["results"]
projection_rows = comparisons["strategyqa_semantic_boolean_projection"]["cases"]
assert len(projected) == len(projection_rows) == len(inputs["strategyqa"][:4])
for raw, row in zip(projected, projection_rows):
    assert raw["passed_prediction"] == ("Yes" if raw["prediction"] else "No")
    assert raw["correct"] == row["local_correct"]
    assert row["agreement"] == (row["official_correct"] == row["local_correct"])
projection_counts = Counter("agreement" if x["agreement"] else "divergence" for x in projection_rows)
assert dict(projection_counts) == comparisons["strategyqa_semantic_boolean_projection"]["counts"]
for path in ROOT.glob("*-offline.txt"):
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    assert all(x["errno"] == 1 and x["result"] == "denied" for x in rows[0]["socket_probes"].values())
    assert rows[0]["production_runtime_observation"] is False
    assert "blocked_external_dataset_reads" in rows[-1]
print("PASS: acquired source bytes/revisions, local identities, shared input alignment, comparison counts, official CLI metrics and offline receipts verified")
