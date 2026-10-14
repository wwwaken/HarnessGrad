"""Read-only integrity and measurement checks for the preserved diagnostic packet."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
sys.path.insert(0, str(REPO))
from eval.admission.scorer_bundle import verify_bundle, require_contract_bundle
from eval.policy.diagnostic_policy import measurement_summary


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name):
    return json.loads((ROOT / name).read_text())


def main():
    manifest = {}
    for line in (ROOT / "SHA256SUMS").read_text().splitlines():
        pin, name = line.split("  ", 1)
        assert name not in manifest
        manifest[name] = pin
        assert sha(ROOT / name) == pin, name
    files = {str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file()
             and "__pycache__" not in p.parts and p.name != "SHA256SUMS"}
    assert files == set(manifest)
    pins = load("trusted-pins.json")
    raw, contract = (ROOT / "bundle.json").read_bytes(), (ROOT / "task-contract.json").read_bytes()
    bundle = verify_bundle(ROOT / "closure", raw, pins["manifest_sha256"])
    require_contract_bundle(contract, pins["artifact_contract_sha256"], raw, pins["manifest_sha256"])
    calls = load("evidence/docker-calls.json")
    assert [c["argv"][1] for c in calls] == ["create", "inspect", "start", "inspect", "rm"]
    assert calls[2]["returncode"] == 1 and calls[2]["stdout"] == ""
    assert "Permission denied" in calls[2]["stderr"]
    info = load("evidence/inspect-01.json")[0]
    stopped = load("evidence/inspect-03.json")[0]["State"]
    assert info["State"]["Status"] == "created" and info["Image"] == pins["runtime_image_id"]
    assert [(m["Destination"], m["RW"]) for m in info["Mounts"]] == [
        ("/control-input", False), ("/control-scorer", False)]
    assert stopped["Status"] == "exited" and stopped["ExitCode"] == 1
    assert not stopped["OOMKilled"] and not stopped["Error"]
    events = load("evidence/projection-rechecks.json")
    returns = [e for e in events if e["event"] == "return"]
    assert [e["function"] for e in returns] == ["verify_scorer_files", "verify_scorer_files",
        "verify_state_export", "_verify_artifact_runtime", "require_artifact_runtime"]
    assert calls[1]["monotonic_ns"] < returns[1]["monotonic_ns"]
    assert returns[-1]["monotonic_ns"] < calls[2]["monotonic_ns"]
    verdict = load("evidence/verdict.json")
    assert verdict["score"] == 0.0 and verdict["scorer_isolation_class"] == "pristine-offline"
    assert set(verdict["scorer_isolation_evidence"]) == {"bundle", "export", "runtime", "cleanup"}
    assert calls[-1]["returncode"] == 0 and verdict["scorer_isolation_evidence"]["cleanup"]["removed"]
    assert load("evidence/post-removal-inspect.json")["returncode"] == 1
    assert load("evidence/post-return-projection.json")["exists"] is False
    audit = load("evidence/measurement-audit.json")
    summary = measurement_summary(["w-pristine-addition-control"], [dict(
        task_id="w-pristine-addition-control", trial=1, status="invalid", score=None,
        reason=audit["reason"])])
    assert summary["score"] is audit["score"] is None
    for key in ("measured_trials", "unmeasured_trials", "invalid_trials"):
        assert summary["coverage"][key] == audit[key]
    refusals = load("evidence/refusals-summary.json")
    assert len(refusals) == 3 and all(r["refused"] and r["removed"] and not r["started"] for r in refusals)
    assert all(r["score"] is None for r in refusals)
    network = load("evidence/refusal-network-inspect.json")
    assert network["HostConfig"]["NetworkMode"] == "bridge"
    assert network["Config"]["Env"] != info["Config"]["Env"]  # preserved confound
    launch = load("evidence/launch.json")
    for name, pin in launch["source_hashes"].items():
        path = ROOT / "evidence/driver-executed.py" if name.endswith("run_control.py") else REPO / name
        assert sha(path) == pin, name
    base = launch["git_head"]
    previous = json.loads(subprocess.check_output(["git", "show", base + ":docs/dataset-blockers.json"],
                                                  cwd=REPO, text=True))
    current = json.loads((REPO / "docs/dataset-blockers.json").read_text())
    assert current["datasets"] == previous["datasets"]
    for old, new in zip(previous["shared_blockers"], current["shared_blockers"]):
        assert {k:v for k,v in old.items() if k not in ("observed", "evidence")} == {
            k:v for k,v in new.items() if k not in ("observed", "evidence")}
        assert new["observed"].startswith(old["observed"])
        assert new["evidence"][:-1] == old["evidence"]
    journal = subprocess.check_output(["git", "show", base + ":docs/adapter-integration-journal.md"],
                                     cwd=REPO, text=True)
    assert (REPO / "docs/adapter-integration-journal.md").read_text().startswith(journal)
    print(json.dumps(dict(valid=True, fixture_files=len(manifest), bundle=bundle,
        measurement=summary, real_stopped_refusals=len(refusals), network_causality="confounded",
        production_sources_unchanged=True, dataset_records_unchanged=True,
        journal_append_only=True, production_authorized=False), sort_keys=True))


if __name__ == "__main__":
    main()
