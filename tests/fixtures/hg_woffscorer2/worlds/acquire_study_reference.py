#!/usr/bin/env python3
"""Read only acorncourt's installed study walkthrough; no task search or generation."""
import hashlib
import json
from pathlib import Path
from jericho import FrotzEnv

HERE = Path(__file__).resolve().parent
assert hashlib.sha256(b"acorncourt").digest()[0] % 3 != 0
env = FrotzEnv(str(HERE / "acorncourt.z5"), seed=4)
try:
    selected = {"task_id": "acorncourt", "selected_seed": env.bindings["seed"],
                "reference_actions": env.get_walkthrough(), "declared_hash_eval": False,
                "source": "installed jericho 3.3.1 FrotzEnv.get_walkthrough() for only acorncourt",
                "max_actions_bound": 20, "reference_kind": "study reference, not authored control"}
    assert len(selected["reference_actions"]) <= selected["max_actions_bound"]
finally:
    env.close()
(HERE / "reference-selection.json").write_text(json.dumps(selected, indent=2, sort_keys=True) + "\n")
inputs = json.loads((HERE / "inputs.json").read_text())
inputs["jericho"]["label"] = "Four authored bounded traces plus one explicitly reference-derived non-heldout acorncourt study trace"
inputs["jericho"]["cases"] = [c for c in inputs["jericho"]["cases"] if c["id"] != "j-study-reference-full"]
inputs["jericho"]["cases"].append({"id": "j-study-reference-full", "actions": selected["reference_actions"],
    "input_kind": "selected upstream study walkthrough", "source_receipt": "reference-selection.json"})
(HERE / "inputs.json").write_text(json.dumps(inputs, indent=2, sort_keys=True) + "\n")
print(json.dumps(selected, indent=2, sort_keys=True))
