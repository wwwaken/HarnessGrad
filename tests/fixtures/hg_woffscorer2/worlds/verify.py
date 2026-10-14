#!/usr/bin/env python3
"""Recompute external/code identities and check retained measured comparisons."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
identity = json.loads((HERE / "identities.json").read_text())
observed_repo = Path(json.loads((HERE / "execution-scope.json").read_text())["repo"])
checked = []
def check(item):
    source = Path(item["path"])
    if source.is_relative_to(observed_repo):
        source = REPO / source.relative_to(observed_repo)
    actual = hashlib.sha256(source.read_bytes()).hexdigest()
    assert actual == item["sha256"], item["path"]
    assert source.stat().st_size == item["bytes"], item["path"]
    checked.append(item["path"])
check(identity["interpreter"])
check(identity["rom"])
assert hashlib.sha256((HERE / "acorncourt.z5").read_bytes()).hexdigest() == identity["rom"]["sha256"]
for package, item in identity["packages"].items():
    for entry in item["files"] + item["metadata"]:
        check(entry)
        copied = HERE / "official-source" / package / Path(entry["path"]).name
        if copied.is_file():
            assert hashlib.sha256(copied.read_bytes()).hexdigest() == entry["sha256"]
for entries in identity["local"].values():
    for entry in entries:
        check(entry)
for entry in identity["java"]:
    check(entry)
check(identity["py4j_java_archive"])
check(identity["controlled_split"]["fold_source"])
inputs = json.loads((HERE / "inputs.json").read_text())
comparison = json.loads((HERE / "comparison.json").read_text())
for dataset in ("jericho", "scienceworld"):
    official = json.loads((HERE / f"{dataset}-official.json").read_text())
    local = json.loads((HERE / f"{dataset}-local.json").read_text())
    assert [c["id"] for c in inputs[dataset]["cases"]] == [c["id"] for c in official["cases"]] == [c["id"] for c in local["cases"]]
    for actual, local_actual, input_case in zip(official["cases"], local["cases"], inputs[dataset]["cases"]):
        assert len(input_case["actions"]) <= 20
        assert actual["measured"] and local_actual["evidence"]["measured"]
        expected_score = (actual["raw_steps"][-1]["info"]["score"] if actual["raw_steps"] else
                          actual["initial_native_score"] if dataset == "jericho" else int(round(100 * actual["initial_native_score"])))
        assert actual["score"] == expected_score
        assert actual["score"] == local_actual["evidence"]["score"]
        assert actual["official_normalized_fraction"] == float(local_actual["reward_file"])
    rows = comparison[dataset]["rows"]
    assert comparison[dataset]["inputs"] == len(inputs[dataset]["cases"])
    assert comparison[dataset]["agreements"] == sum(r["agreement"] is True for r in rows)
    assert comparison[dataset]["divergences"] == sum(r["agreement"] is False for r in rows)
    assert comparison[dataset]["unmeasured"] == sum(not r["both_measured"] for r in rows)
assert not identity["controlled_split"]["jericho_acorncourt_declared_hash_eval"]
assert not identity["controlled_split"]["scienceworld_task_3_find_non_living_thing_variation_0_in_test_fold"]
first = json.loads((HERE / "preserved-first-attempt/scienceworld-official.json").read_text())
first_errors = [c for c in first["cases"] if c.get("exception") == "FileNotFoundError"]
assert len(first_errors) == len(first["cases"])
assert json.loads((HERE / "cleanup.json").read_text())["scratch_removed"]
local_jvm_pids = [c["pid"] for entry in json.loads((HERE / "scienceworld-local.json").read_text())["cases"]
                  for c in entry.get("child_cleanup", [])]
process_observation = [{"pid": pid, "exists_after_execution": Path(f"/proc/{pid}").exists()} for pid in local_jvm_pids]
assert not any(p["exists_after_execution"] for p in process_observation)
print(json.dumps({"status": "verified", "external_identities_recomputed": len(checked),
    "comparisons": comparison, "preserved_first_attempt_scienceworld_FileNotFoundError_count": len(first_errors),
    "local_java_child_after_execution_observation": process_observation,
    "source_revision_provenance": "installed version plus byte identities; no authenticated upstream Git revision claimed"}, indent=2, sort_keys=True))
