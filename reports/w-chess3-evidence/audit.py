"""Read-only verification of this control's evidence, scope and closure."""
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tarfile

import chess

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
BASELINE_COMMIT = json.loads((OUT / "execution/launch/manifest.json").read_text())["platform_commit"]
sys.path.insert(0, str(ROOT))
from eval.policy import diagnostic_policy as policy
from tools import check_dataset_blockers as checker


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def baseline(path):
    return subprocess.check_output(["git", "show", BASELINE_COMMIT + ":" + path], cwd=ROOT, text=True)


def main():
    registry = load(ROOT / "docs/dataset-blockers.json")
    checked = checker.validate(registry)
    original_registry = json.loads(baseline("docs/dataset-blockers.json"))
    expected = copy.deepcopy(original_registry)
    row = next(r for r in expected["datasets"] if r["dataset"] == "chessbench_puzzles")
    prior = next(b for b in row["blockers"] if b["id"] == "trusted-stepwise-transport")
    corrected = load(OUT / "corrected-blocker-before-run.json")
    assert "AGENT'S OWN GENERATED SCRIPT" in corrected["observed"]
    assert "not platform mishandling" in corrected["observed"]
    assert {k: v for k, v in prior.items() if k != "observed"} == {
        k: v for k, v in corrected.items() if k != "observed"}
    for evidence in corrected["evidence"]:
        if evidence["kind"] == "repository":
            assert evidence["locator"] in (ROOT / evidence["path"]).read_text()
    row["blockers"].remove(prior)
    assert registry["review"]["notes"][-1].startswith("w-chess3: Corrected")
    expected["review"]["notes"].append(registry["review"]["notes"][-1])
    assert registry == expected, "registry changed outside the target and appended note"
    journal = (ROOT / "docs/adapter-integration-journal.md").read_text()
    old_journal = baseline("docs/adapter-integration-journal.md")
    assert journal.startswith(old_journal)
    heading = "## ChessBench diagnostic control terminal exchange - 2026-10-15 - w-chess3"
    assert journal.count(heading) == 1 and heading not in old_journal
    protected = ["eval", "data", "base_harness", "tools", "driver.py", "ckpt",
                 "harnessgrad", "methods", "improvers", "AGENTS.md"]
    assert subprocess.check_output(
        ["git", "diff", BASELINE_COMMIT, "--name-only", "--", *protected], cwd=ROOT, text=True) == ""

    e = OUT / "execution"
    identity = load(e / "identity.json")
    run = Path(identity["run_dir"])
    assert not run.is_relative_to(ROOT) and not Path(identity["work_root"]).is_relative_to(ROOT)
    r = load(e / "task-result.json")
    v = r["verdict"]
    ev = v["evidence"]
    assert r["exit_code"] == 0 and r["stderr"] == ""
    assert v["protocol"] == "chessbench_puzzles.stepwise.v1"
    assert v["scorer_isolation_class"] == "in-process"
    assert ev["status"] == "complete" and ev["measured"] is True
    assert ev["transport"]["status"] == "terminal"
    assert all(ev["cleanup"].values())
    assert ev["connections"] == 1 and ev["rejected_connections"] == 0
    events = [json.loads(s) for s in r["trace"].splitlines()]
    observations = [event["observation"] for event in events if event["event"] == "observation"]
    answers = [event["answer"] for event in events if event["event"] == "submission"]
    delivered = [json.loads(event["message"]) for event in ev["transport"]["events"]
                 if event["kind"] == "observation"]
    received = [json.loads(event["message"]) for event in ev["transport"]["events"]
                if event["kind"] == "submission"]
    assert delivered == observations and received == answers
    assert len(answers) == ev["transport"]["submissions"]
    assert observations[0]["solver_turn"] == 0
    assert observations[-1]["status"] in {"solved", "failed"}
    assert events[-1] == dict(event="completed", terminal_received=True, channel_closed=True)
    for observation, answer in zip(observations, answers):
        assert chess.Move.from_uci(answer["uci"]) in chess.Board(observation["fen"]).legal_moves
    assert r["trace"] == (e / "actor-trace.jsonl").read_text()
    d = load(e / "diagnostic_receipt.json")
    policy.validate_receipt(d)
    assert d["score"] is None and d["enforcement"]["production_authorized"] is False
    assert d["outcomes"][0]["reason"] == "policy_enforcement_not_observed"
    assert load(OUT / "raw-controller-summary.json")["coverage"] == policy.measurement_summary(
        d["selected_task_ids"], load(e / "raw-controller-outcomes.json"))["coverage"]
    assert d["context"]["hashes"]["manifest"] == sha(e / "launch/manifest.json")
    assert load(e / "launch/platform-diff.json") == dict(added=[], removed=[], modified=[])
    manifest = load(e / "launch/manifest.json")
    assert manifest["harness_files_sha256"] == sha(e / "launch/harness-files.json")
    assert manifest["task_sha256"] == sha(e / "launch/task.json")
    assert manifest["source_sha256"] == sha(e / "launch/source.json")
    harness_files = load(e / "launch/harness-files.json")
    for name in ("actor.py", "harness.json"):
        assert sha(ROOT / "reports/w-chess3-control" / name) == harness_files[name]
    assert sha(OUT / "launch.py") == sha(e / "launch/launch.py")
    assert (OUT / "invocation.txt").read_text().splitlines()[1] == (e / "launch/command.txt").read_text().strip()
    report = (ROOT / "reports/w-chess3-receipts.md").read_text()
    blocks = [json.loads(block) for block in re.findall(r"```json\n(.*?)\n```", report, re.S)]
    reported = [identity, {k: r[k] for k in ("exit_code", "stderr", "verdict")},
                {k: d[k] for k in ("stage", "trials", "jobs", "score", "outcomes", "coverage")},
                {k: d["context"][k] for k in ("metric", "hashes", "endpoint", "limits", "gates", "comparability_notes")},
                {k: d[k] for k in ("cleanup", "snapshot", "lifecycle")},
                load(OUT / "raw-controller-summary.json")]
    for name in ("launch/selection.json", "launch/source.json", "launch/manifest.json",
                 "launch/model-binding.json", "launch/harness-files.json",
                 "launch/harness-after.json", "launch/sandbox-preflight.json", "cleanup-observation.json"):
        reported.append(load(e / name))
    assert all(value in blocks for value in reported), "reported raw JSON differs from artifacts"
    assert r["trace"] in report

    inventory = load(OUT / "artifact-inventory.json")
    archive = OUT / "run-artifacts.tar.gz"
    with tarfile.open(archive) as bundle:
        for item in inventory:
            source = Path(item["source"])
            copied = ROOT / item["copy"]
            assert source.stat().st_size == copied.stat().st_size == item["bytes"]
            assert sha(source) == sha(copied) == item["sha256"]
            assert hashlib.sha256(bundle.extractfile(run.name + "/" + item["relative_path"]).read()).hexdigest() == item["sha256"]
    archived = load(OUT / "archive-sha256.json")
    assert archive.stat().st_size == archived["bytes"] and sha(archive) == archived["sha256"]
    before = load(OUT / "runs-before.json")
    runs = ROOT / "runs"
    now = {str(p.relative_to(runs)): dict(bytes=p.stat().st_size, sha256=sha(p))
           for p in runs.rglob("*") if p.is_file()} if runs.exists() else {}
    assert before == dict(path=str(runs.resolve()), exists=runs.exists(), files=now)
    result = dict(registry=checked, correction_verified=True,
                  registry_scope="remove target only plus append correction/closure review note",
                  interruption_and_history_unchanged=True, shared_gates_unchanged=True,
                  journal_append_only=True, protected_sources_unchanged=True,
                  original_copy_archive_files_checked=len(inventory), all_copy_archive_hashes_match=True,
                  actor_matches_preexecution_source=True, source_manifest_binding_matches=True,
                  reported_raw_json_matches=True,
                  terminal_delivered_and_received=True, actor_exit_code=r["exit_code"],
                  submissions=ev["transport"]["submissions"], relay_cleanup=ev["cleanup"],
                  controller_score=v["score"], policy_score=d["score"],
                  policy_coverage=d["coverage"], model_used=identity["model_used"],
                  endpoint=identity["endpoint"], external_run_and_work_root=True,
                  runs_unchanged=True, runs_exists=runs.exists(), blocker_closed=True)
    (OUT / "report-audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
