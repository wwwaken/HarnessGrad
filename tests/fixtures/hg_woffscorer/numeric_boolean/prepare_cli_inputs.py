#!/usr/bin/env python3
"""Project authored inputs to the unchanged official StrategyQA CLI file schema."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
cases = json.loads((ROOT / "inputs.json").read_text())["strategyqa"]
for panel in ("valid_official_boolean", "adapter_text_official_out_of_contract"):
    subset = [x for x in cases if x["panel"] == panel]
    golds = [{"qid": x["id"], "answer": x["gold_answer"], "question": "Authored control; no benchmark question."} for x in subset]
    predictions = {x["id"]: {"answer": x["prediction"]} for x in subset}
    (ROOT / f"strategyqa-{panel}-golds.json").write_text(json.dumps(golds, indent=2) + "\n")
    (ROOT / f"strategyqa-{panel}-predictions.json").write_text(json.dumps(predictions, indent=2) + "\n")
