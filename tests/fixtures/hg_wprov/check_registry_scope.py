"""Check the registry diff against the captured Git base; never import adapters."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
base = json.loads((ROOT / "source-receipt.json").read_text())["base_commit"]
before = json.loads(subprocess.check_output(
    ["git", "show", base + ":docs/dataset-blockers.json"], cwd=REPO, text=True))
after = json.loads((REPO / "docs/dataset-blockers.json").read_text())
owned = {"physicsquestions", "strategyqa", "sportsunderstanding", "reasoning_gym"}
for key in before.keys() - {"datasets"}:
    assert before[key] == after[key], key
assert len(before["datasets"]) == len(after["datasets"])
changed = []
for original, current in zip(before["datasets"], after["datasets"]):
    name = original["dataset"]
    assert current["dataset"] == name
    if name not in owned:
        assert original == current, name
        continue
    assert {k: v for k, v in original.items() if k != "blockers"} == {
        k: v for k, v in current.items() if k != "blockers"}
    assert len(original["blockers"]) == len(current["blockers"]) == 1
    a, b = original["blockers"][0], current["blockers"][0]
    for key in a.keys() - {"observed", "next_action", "evidence"}:
        assert a[key] == b[key], (name, key)
    assert a["evidence"] == b["evidence"][:len(a["evidence"])], name
    assert b["observed"] != a["observed"] and b["next_action"] != a["next_action"]
    assert b["status"] == "measurement"
    changed.append(name)
assert set(changed) == owned
print(json.dumps({"valid": True, "base_commit": base,
                  "only_changed_blockers": changed,
                  "only_changed_fields": ["observed", "next_action", "evidence"],
                  "statuses_histories_shared_and_other_datasets_unchanged": True,
                  "blockers_closed": 0}, indent=2))
