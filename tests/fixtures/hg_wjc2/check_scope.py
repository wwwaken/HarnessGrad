"""Check the requested additive observation boundary against the starting registry."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NAMES = {"fever", "physicsquestions", "reasoning_gym", "sportsunderstanding",
         "spreadsheetbench", "strategyqa"}
before = json.loads((HERE / "registry-before.json").read_text())
after = json.loads((ROOT / "docs/dataset-blockers.json").read_text())
trimmed = []
changed = []
for doc in (before, after):
    clone = deepcopy(doc)
    for row in clone["datasets"]:
        if row["dataset"] in NAMES:
            for blocker in row["blockers"]:
                blocker.pop("observed")
    trimmed.append(clone)
assert trimmed[0] == trimmed[1], "Only six observed fields may change"
for old, new in zip(before["datasets"], after["datasets"], strict=True):
    if old != new:
        assert old["dataset"] in NAMES
        changed.append(old["dataset"])
paths = subprocess.check_output(["git", "diff", "--name-only", "31ff5916", "--"], cwd=ROOT).decode().splitlines()
allowed = {"docs/dataset-blockers.json", "docs/adapter-integration-journal.md",
           "reports/w-jc2-review.md", "reports/w-jc2-validation.txt"}
assert all(p in allowed or p.startswith("tests/fixtures/hg_wjc2/") for p in paths), paths
assert subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT).decode().strip() == "wg-jc2"
assert after["review"]["production_authorized"] is False
print(json.dumps({"valid": True, "observed_fields_changed": changed,
                  "shared_blockers_unchanged": True, "statuses_and_next_actions_unchanged": True,
                  "historical_records_unchanged": True, "production_authorized": False,
                  "tracked_changed_paths": paths}, indent=2))
