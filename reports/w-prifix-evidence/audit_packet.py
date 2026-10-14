"""Read-only audit of a new pristine packet; writes one exclusive derived receipt."""
import hashlib
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from eval.admission import artifact_admission as artifacts
from eval.policy.diagnostic_policy import measurement_summary


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    control, followup, output = map(Path, sys.argv[1:])
    load = lambda root, name: json.loads((root / name).read_text())
    fixture = REPO / "tests/fixtures/hg_wpristine"
    pins = load(fixture, "trusted-pins.json")
    fixture_checks = {}
    for line in (fixture / "SHA256SUMS").read_text().splitlines():
        pin, name = line.split("  ", 1)
        fixture_checks[name] = sha(fixture / name) == pin
    assert all(fixture_checks.values())
    verdict = load(control, "verdict.json")
    launch = load(control, "launch.json")
    driver = load(control, "control-receipt.json")
    calls = load(control, "docker-calls.json")
    assert [c["argv"][1] for c in calls] == ["create", "inspect", "start", "inspect", "rm"]
    start = calls[2]
    info = load(control, "inspect-01.json")[0]
    stopped = load(control, "inspect-03.json")[0]["State"]
    native = verdict["scorer_isolation_evidence"]
    assert native["stopped_result"]["state"] == stopped
    assert native["stopped_result"]["stdout"] == calls[3]["stdout"]
    for key in ("returncode", "stdout", "stderr"):
        assert native["start_result"][key] == start[key]
        assert native["cleanup"][key] == calls[4][key]
    assert info["Config"]["User"] == artifacts.scorer_user()
    assert info["Config"]["Env"] == artifacts.SCORER_ENV
    assert info["Image"] == pins["runtime_image_id"]
    assert start["returncode"] == stopped["ExitCode"] == 1
    assert start["stderr"] == "" and stopped["Status"] == "exited"
    assert stopped["Running"] is stopped["OOMKilled"] is False and stopped["Error"] == ""
    markers = [line for line in start["stdout"].splitlines() if line.startswith("completed_check=")]
    assert markers == ["completed_check=fail"]
    assert "actual=41\n" in start["stdout"] and "expected=42\n" in start["stdout"]
    assert verdict["score"] == 0.0 and verdict["outcome"] == "measured" and not verdict.get("unmeasured")
    exported = native["export"]
    answer = next(row for row in exported["files"] if row["path"] == "answer.txt")
    assert answer["bytes"] == 3
    assert answer["sha256"] == hashlib.sha256(b"41\n").hexdigest()
    assert exported["limits"] == {"max_bytes": 16, "max_inodes": 2}
    assert exported["bytes"] == 3 and exported["inodes"] == 2
    summary = measurement_summary([exported["task_id"]], [dict(task_id=exported["task_id"],
        trial=1, status="measured", score=verdict["score"], reason=None)])
    for key in ("measured_trials", "unmeasured_trials", "invalid_trials"):
        assert summary["coverage"][key] == driver[key]
    assert driver["eligible_tasks"] == driver["selected_tasks"] == driver["expected_trials"] == 1
    assert native["cleanup"]["removed"] and calls[4]["returncode"] == 0
    absent = load(control, "post-removal-inspect.json")
    assert absent["returncode"] == 1 and "no such object" in absent["stderr"]
    projection = load(control, "post-return-projection.json")
    assert projection["exists"] is False and not Path(projection["path"]).exists()
    hashes = {name: sha(REPO / name) for name in launch["source_hashes"]}
    assert hashes == launch["source_hashes"], "packet must match final executed source bytes"
    kernel = dict(line.split("=", 1) for line in start["stdout"].splitlines() if line.startswith("cgroup."))
    resources = {key: info["HostConfig"][key] for key in
                 ("NanoCpus", "Memory", "MemorySwap", "PidsLimit", "Tmpfs", "CgroupnsMode")}
    refusals = load(control, "refusals-summary.json")
    assert len(refusals) == 3 and all(r["refused"] and r["removed"] and not r["started"] for r in refusals)
    attempts = load(followup, "summary.json")
    isolated = [r for r in attempts if r["exact_environment"] and r["refused"]]
    assert isolated
    r = isolated[0]
    net = load(followup / f"attempt-{r['attempt']:02d}", "inspect.json")
    contract = load(fixture, "task-contract.json")
    preceding = dict(image=net["Image"] == contract["runtime_image_id"],
        entrypoint=net["Config"]["Entrypoint"] == contract["scorer"]["argv"][:1],
        cmd=net["Config"]["Cmd"] == contract["scorer"]["argv"][1:],
        env=net["Config"]["Env"] == artifacts.SCORER_ENV,
        workdir=net["Config"]["WorkingDir"] == "/tmp",
        user=net["Config"]["User"] == artifacts.scorer_user(),
        no_added_groups=not net["HostConfig"].get("GroupAdd"),
        created=net["State"]["Status"] == "created", not_running=net["State"]["Running"] is False)
    assert all(preceding.values()) and net["HostConfig"]["NetworkMode"] == "bridge"
    assert all(p["removed"] and p["post_removal_inspect_returncode"] == 1 and not p["started"] for p in attempts)
    mount_followup = control.parent / "final-mount-followup"
    mount_attempts = load(mount_followup, "summary.json")
    assert all(p["refused"] and p["removed"] and not p["started"]
               and p["post_removal_inspect_returncode"] == 1 for p in mount_attempts)
    isolated_mount = next(p for p in mount_attempts if p["exact_environment"])
    assert isolated_mount["reason"] == "artifact-only read-only mounts required"
    mount_info = load(mount_followup / f"attempt-{isolated_mount['attempt']:02d}", "inspect.json")
    assert mount_info["Config"]["Env"] == artifacts.SCORER_ENV
    assert mount_info["HostConfig"]["NetworkMode"] == "none"
    assert len(mount_info["Mounts"]) == 3
    assert any(m["Destination"] == "/unexpected" and m["RW"] is False for m in mount_info["Mounts"])
    receipt = dict(run_id=launch["run_id"], metric_identity=launch["task"]["metric"],
        measurement=summary, raw_verdict_score=verdict["score"], outcome=verdict["outcome"],
        driver_counts={k: driver[k] for k in ("eligible_tasks", "selected_tasks", "expected_trials",
                        "measured_trials", "unmeasured_trials", "invalid_trials")},
        fixture_files_verified=len(fixture_checks), fixture_sha256sums=sha(fixture / "SHA256SUMS"),
        pins=pins, source_hashes=hashes, answer_export=answer, endpoint=launch["endpoint"], model=launch["model"],
        resources_from_created_inspection=resources, kernel_samples_from_scorer_stdout=kernel,
        mountinfo_samples=[line for line in start["stdout"].splitlines() if line.startswith("mountinfo=")],
        cleanup=native["cleanup"], post_removal_inspect=absent, post_return_projection=projection,
        original_refusals=refusals, network_followup=attempts, mount_followup=mount_attempts,
        network_attribution=dict(preceding_boundary_conditions=preceding,
            first_mismatching_clause='host["NetworkMode"] != "none"', raw_value="bridge",
            source="eval/admission/artifact_admission.py:_verify_artifact_runtime"),
        production_authorized=False, lifecycle=None,
        scope="locally authored exact-answer scorer-runtime control; not a dataset pilot")
    with output.open("x") as f:
        json.dump(receipt, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps(dict(valid=True, run_id=launch["run_id"], score=verdict["score"],
                         counts=receipt["driver_counts"], fixture_files_verified=len(fixture_checks),
                         network_attribution=receipt["network_attribution"]), sort_keys=True))


if __name__ == "__main__":
    main()
