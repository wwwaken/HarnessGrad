#!/usr/bin/env python3
"""Read the frozen w-net archive in memory; never extract or execute it."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "reports/w-net-evidence"
DEST = Path(__file__).resolve().parent
RUN = "w-net-terminal-bench-20261014T200818Z-fd0c4d1e"
TASK = "openssl-selfsigned-cert"


def sha(data):
    return hashlib.sha256(data).hexdigest()


archive = SOURCE / "run-artifacts.tar.gz"
archive_identity = json.loads((SOURCE / "archive-sha256.json").read_text())
inventory = json.loads((SOURCE / "artifact-inventory.json").read_text())["files"]
with tarfile.open(archive, "r:gz") as tar:
    # No extractall: only ordinary files are read as bytes in memory.
    members = {m.name: tar.extractfile(m).read() for m in tar if m.isfile()}

inventory_mismatches = []
for row in inventory:
    relative = row["path"].removeprefix("/tmp/hg-net/")
    actual = members.get(relative)
    if actual is None or len(actual) != row["bytes"] or sha(actual) != row["sha256"]:
        inventory_mismatches.append(relative)

input_manifest = []


def read(relative, save_as):
    data = members["runs/" + relative]
    (DEST / save_as).write_bytes(data)
    input_manifest.append(dict(archive_member="runs/" + relative,
                               output=save_as, bytes=len(data), sha256=sha(data)))
    return data


def read_json(relative, save_as):
    return json.loads(read(relative, save_as))


launch = RUN + "-launch-evidence/"
execution = RUN + "/"
ctrf_observation = read_json(launch + "verifier-file-observations.json", "verifier-file-observations.json")
ctrf_row = next(x for x in ctrf_observation if x["source"].endswith("/ctrf.json"))
reward_row = next(x for x in ctrf_observation if x["source"].endswith("/reward.txt"))
ctrf_bytes = read(launch + Path(ctrf_row["copy"]).name, "ctrf.json")
reward_bytes = read(launch + Path(reward_row["copy"]).name, "reward.txt")
ctrf = json.loads(ctrf_bytes)["results"]
status_counts = Counter(t["status"] for t in ctrf["tests"])
counts = {"tests": len(ctrf["tests"]), **{k: status_counts[k] for k in ("passed", "failed", "skipped", "pending", "other")}}
receipt = read_json(execution + "diagnostic_receipt.json", "diagnostic_receipt.json")
raw_execution = read_json(execution + "diagnostic_execution.json", "diagnostic_execution.json")
progress = read_json(execution + "progress/round-0/" + TASK + ".json", "progress.json")
selection = read_json(launch + "selection.json", "selection.json")
plan = read_json(execution + "staged_plan.json", "staged_plan.json")
trace_bytes = read(execution + "progress/round-0/traces/" + TASK + ".trial1.jsonl", "trace.jsonl")
trace = [json.loads(line) for line in trace_bytes.splitlines() if line.strip()]
reply_rows = [row for row in trace if "reply" in row]
usage = [row["usage"] for row in trace if "usage" in row]
verdict = raw_execution["verdicts"][TASK]

actor_observation = read_json(launch + "container-inspect-00000.json", "container-inspect-00000.json")
verifier_observation = read_json(launch + "container-inspect-00064.json", "container-inspect-00064.json")
snapshot_observation = read_json(launch + "snapshot-inspect-00072.json", "snapshot-inspect-00072.json")
actor = json.loads(actor_observation["stdout"])[0]
verifier = next(x for x in json.loads(verifier_observation["stdout"]) if x["Name"].startswith("/hg-verify-"))
snapshot = json.loads(snapshot_observation["stdout"])[0]
script = read(launch + "selected-verifier-test.sh", "selected-verifier-test.sh")

outcome_counts = Counter(row["status"] for row in receipt["outcomes"])
recomputed_coverage = dict(expected_trials=len(receipt["selected_task_ids"]) * receipt["trials"])
for status in ("measured", "unmeasured", "invalid"):
    rows = [r for r in receipt["outcomes"] if r["status"] == status]
    recomputed_coverage[status + "_trials"] = len(rows)
    recomputed_coverage[status + "_tasks"] = len({r["task_id"] for r in rows})
recomputed_coverage["selected_tasks"] = len(receipt["selected_task_ids"])
recomputed_coverage["eligible_tasks"] = len(set(selection["task_ids"]))
coverage_matches = all(receipt["coverage"][k] == v for k, v in recomputed_coverage.items())
isolation_fields = {
    "execution": raw_execution["scorer_isolation_class"],
    "execution_per_task": raw_execution["per_task_scorer_isolation"][TASK],
    "verdict": verdict["scorer_isolation_class"],
    "verdict_declared": verdict["scorer_isolation_declared"],
    "progress": progress["scorer_isolation_class"],
    "progress_trial": progress["trial_scorer_isolation"][0],
}
output = {
    "archive": {"bytes": archive.stat().st_size, "sha256": sha(archive.read_bytes()),
                "matches_preserved_identity": sha(archive.read_bytes()) == archive_identity["sha256"],
                "ordinary_file_members": len(members), "inventory_files": len(inventory),
                "inventory_mismatches": inventory_mismatches},
    "ctrf": {"independent_test_status_counts": counts,
             "reported_summary": {k: ctrf["summary"][k] for k in counts},
             "all_counts_match": all(ctrf["summary"][k] == v for k, v in counts.items()),
             "failed_names": [t["name"] for t in ctrf["tests"] if t["status"] == "failed"],
             "bytes": len(ctrf_bytes), "sha256": sha(ctrf_bytes),
             "matches_observer_digest": sha(ctrf_bytes) == ctrf_row["sha256"],
             "review_copy_identical": (SOURCE / "ctrf.json").read_bytes() == ctrf_bytes},
    "reward": {"raw_bytes_repr": repr(reward_bytes), "parsed_score": float(reward_bytes),
               "raw_execution_score": raw_execution["per_task"][TASK], "verdict_score": verdict["score"],
               "progress_score": progress["score"], "sha256": sha(reward_bytes),
               "matches_observer_digest": sha(reward_bytes) == reward_row["sha256"],
               "official_script_sha256": sha(script)},
    "model_calls": {"trace_reply_records": len(reply_rows),
                    "trace_reply_steps": [row["step"] for row in reply_rows],
                    "trace_usage": usage, "execution_tokens": raw_execution["tokens"],
                    "gateway_connections": raw_execution["model_gateway"]["connections"],
                    "env_usage": raw_execution["env_usage"]},
    "isolation": {"fields": isolation_fields,
                  "all_class_fields_agree": len(set(isolation_fields.values())) == 1,
                  "actor_container_id": actor["Id"], "verifier_container_id": verifier["Id"],
                  "actor_image": actor["Image"], "verifier_image": verifier["Image"],
                  "snapshot_id": snapshot["Id"], "snapshot_parent": snapshot["Parent"],
                  "different_containers": actor["Id"] != verifier["Id"],
                  "verifier_uses_snapshot_of_actor_image": verifier["Image"] == snapshot["Id"] and snapshot["Parent"] == actor["Image"],
                  "actor_networks": sorted(actor["NetworkSettings"]["Networks"]),
                  "verifier_networks": sorted(verifier["NetworkSettings"]["Networks"]),
                  "scorer_isolation_comparable": raw_execution["scorer_isolation_comparable"],
                  "publication_comparable": receipt["enforcement"]["comparable"]},
    "publication": {"stored_coverage": receipt["coverage"],
                    "independently_counted_coverage": recomputed_coverage,
                    "coverage_matches": coverage_matches, "outcome_status_counts": dict(outcome_counts),
                    "outcomes": receipt["outcomes"], "published_score": receipt["score"],
                    "enforcement": receipt["enforcement"],
                    "execution_invalid": raw_execution["invalid"],
                    "selection_task_ids": selection["task_ids"],
                    "selection_split": selection["split"],
                    "planned_selected_task_ids": plan["selected_task_ids"],
                    "plan_matches_final_selection": plan["selected_task_ids"] == receipt["selected_task_ids"],
                    "cleanup": receipt["cleanup"], "snapshot": receipt["snapshot"]},
}
(DEST / "input-members.json").write_text(json.dumps(input_manifest, indent=2) + "\n")
print(json.dumps(output, indent=2))
