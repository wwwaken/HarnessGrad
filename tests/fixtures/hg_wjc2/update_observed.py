"""Apply independently reviewed observations, preserving registry byte layout."""
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
path = ROOT / "docs/dataset-blockers.json"
raw = path.read_text()
document = json.loads(raw)
additions = json.loads((HERE / "observed-additions.json").read_text())
assert set(additions) == {"fever", "physicsquestions", "reasoning_gym",
                         "sportsunderstanding", "spreadsheetbench", "strategyqa"}
for row in document["datasets"]:
    name = row["dataset"]
    if name not in additions:
        continue
    blocker = next(b for b in row["blockers"] if b["id"] == "dataset-journal-gap")
    before = blocker["observed"]
    assert additions[name] not in before, "Observation already applied"
    encodings = {json.dumps(before, ensure_ascii=ascii) for ascii in (True, False)}
    matches = [s for s in encodings if s in raw]
    assert len(matches) == 1 and raw.count(matches[0]) == 1, name
    old = matches[0]
    escaped = old == json.dumps(before, ensure_ascii=True)
    raw = raw.replace(old, json.dumps(before + " " + additions[name], ensure_ascii=escaped))
# All semantic differences are checked before the only write.
new = json.loads(raw)
for old_row, new_row in zip(document["datasets"], new["datasets"], strict=True):
    if old_row["dataset"] in additions:
        for old_b, new_b in zip(old_row["blockers"], new_row["blockers"], strict=True):
            if old_b["id"] == "dataset-journal-gap":
                new_b["observed"] = old_b["observed"]
assert new == document
path.write_text(raw)
result = subprocess.run(["python3", "tools/check_dataset_blockers.py"], cwd=ROOT,
                        capture_output=True)
print(result.stdout.decode(), end="")
print(result.stderr.decode(), end="")
assert result.returncode == 0
print(json.dumps({"updated_observed_only": sorted(additions), "valid": True}))
