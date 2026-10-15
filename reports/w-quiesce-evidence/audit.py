"""Read-only reconciliation of the collected raw packet; exclusive output only."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def check_seals(root):
    sealed = {}
    for line in (root / "SHA256SUMS").read_text().splitlines():
        pin, name = line.split("  ", 1)
        assert name not in sealed and not Path(name).is_absolute() and ".." not in Path(name).parts
        assert sha(root / name) == pin, name
        sealed[name] = pin
    files = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()
             and p.name != "SHA256SUMS" and "__pycache__" not in p.parts}
    assert set(sealed) == files
    return len(sealed)


def predicate(start, state):
    """Compare scoring observations, excluding changing mount/cgroup telemetry."""
    assert state["Status"] == "exited" and state["Running"] is False
    assert state["OOMKilled"] is False and state["Error"] == ""
    rows = {}
    for key in ("expected", "actual", "completed_check"):
        values = [line.split("=", 1)[1] for line in start["stdout"].splitlines()
                  if line.startswith(key + "=")]
        assert len(values) == 1, (key, values)
        rows[key] = values[0]
    assert rows["completed_check"] in {"pass", "fail"}
    code = 0 if rows["completed_check"] == "pass" else 1
    assert start["returncode"] == state["ExitCode"] == code and start["stderr"] == ""
    return dict(**rows, exit_code=code, score=float(code == 0))


def inventory_answer(rows):
    return next(row for row in rows if row["path"] == "answer.txt")


def audit(root):
    sealed_files = check_seals(root)
    fixture = REPO / "tests/fixtures/hg_wpristine"
    fixture_files = check_seals(fixture)
    launch = load(root / "launch.json")
    for name, pin in launch["source_hashes"].items():
        assert sha(REPO / name) == pin, name
    assert all(launch["fixture_checks"].values()) and len(launch["fixture_checks"]) == fixture_files
    assert launch["fixture_manifest_sha256"] == sha(fixture / "SHA256SUMS")
    pins = load(fixture / "trusted-pins.json")
    assert pins == launch["pins"]
    assert sha(fixture / "task-contract.json") == pins["artifact_contract_sha256"]
    assert sha(fixture / "bundle.json") == pins["manifest_sha256"]
    assert sha(fixture / "task-source.json") == pins["source_sha256"]
    selection = load(root / "selection.json")
    a41 = hashlib.sha256(b"41\n").hexdigest()
    a42 = hashlib.sha256(b"42\n").hexdigest()
    results, runtime_bindings, refused, intervals = {}, {}, {}, {}
    runtime_names, source_run_ids, resource_observations = set(), set(), {}
    for case in sorted(p for p in root.iterdir() if p.is_dir()):
        binding = load(case / "binding.json")
        expected_task = launch["task"]["task_id"] + ("-wrong" if case.name == "wrong-task" else "")
        assert binding["task_id"] == expected_task and binding["trial"] == 1
        assert binding["outer_run_id"] not in source_run_ids
        source_run_ids.add(binding["outer_run_id"])
        calls = load(case / "docker-calls.json")
        created = next((c for c in calls if c["argv"][1] == "create"), None)
        starts = [c for c in calls if c["argv"][1] == "start"]
        assert len(starts) <= 1
        verdict = load(case / "verdict.json") if (case / "verdict.json").exists() else None
        if created:
            assert created["returncode"] == 0
            name = created["argv"][created["argv"].index("--name") + 1]
            assert name not in runtime_names
            runtime_names.add(name)
            removed = next(c for c in calls if c["argv"][1] == "rm")
            assert removed["returncode"] == 0 and removed["argv"][-1] == name
            absent = load(case / "absence.json")
            assert absent["returncode"] == 1 and json.loads(absent["stdout"]) == []
            assert "no such object" in absent["stderr"].lower()
            if verdict:
                assert verdict["scorer_isolation_evidence"]["cleanup"]["removed"]
                assert load(case / "projection-after.json")["exists"] is False
                export = verdict["scorer_isolation_evidence"]["export"]
            else:
                assert load(case / "cleanup.json")["removed"]
                export = binding["export_receipt"]
            assert export["run_id"] == name and export["task_id"] == binding["task_id"]
            assert export["contract_sha256"] == pins["artifact_contract_sha256"]
            assert export["source_sha256"] == pins["source_sha256"]
            assert export["bytes"] == 3 and export["inodes"] == 2
            assert export["limits"] == {"max_bytes": 16, "max_inodes": 2}
            assert export["files"] == [dict(path="answer.txt", bytes=3,
                 sha256=a42 if case.name.startswith("changed-answer") else a41)]
            inspected = next(c for c in calls if c["argv"][1] == "inspect" and c["returncode"] == 0)
            info = json.loads(inspected["stdout"])[0]
            assert info["Image"] == pins["runtime_image_id"]
            assert len(info["Mounts"]) == 2 and all(m["RW"] is False for m in info["Mounts"])
            assert [m["Destination"] for m in info["Mounts"]] == ["/control-input", "/control-scorer"]
            mounted_input = next(m["Source"] for m in info["Mounts"] if m["Destination"] == "/control-input")
            if verdict:
                exported_event = next(e for e in load(case / "events.json") if e["event"] == "export_return")
                assert mounted_input == exported_event["projection"]
                assert exported_event["receipt"] == export
                assert load(case / "projection-after.json")["path"] == mounted_input
            else:
                assert mounted_input == binding["source"]
            runtime_bindings[case.name] = dict(outer_run_id=binding["outer_run_id"], trial=1,
                 task_id=binding["task_id"], runtime_export_id=name,
                 source=binding["source"], export=export)
            resource_observations[case.name] = {key: info["HostConfig"][key] for key in
                 ("NanoCpus", "Memory", "MemorySwap", "PidsLimit", "Tmpfs", "CgroupnsMode")}
        if starts:
            stopped = next(c for c in reversed(calls) if c["argv"][1] == "inspect" and c["returncode"] == 0)
            state = json.loads(stopped["stdout"])[0]["State"]
            result = predicate(starts[0], state)
            assert info["Config"]["Env"] == ["PATH=/control-scorer", "HOME=/tmp", "TMPDIR=/tmp"]
            if verdict:
                native = verdict["scorer_isolation_evidence"]
                assert verdict["score"] == result["score"] and verdict["outcome"] == "measured"
                assert verdict["scorer_isolation_class"] == "pristine-offline"
                assert native["stopped_result"]["state"] == state
                for key in ("stdout", "stderr", "returncode"):
                    assert native["start_result"][key] == starts[0][key]
                events = load(case / "events.json")
                checks = [e for e in events if e["event"] == "check_return"]
                assert [e["function"] for e in checks] == ["verify_scorer_files", "verify_scorer_files",
                     "verify_state_export", "require_artifact_runtime"]
                assert isinstance(checks[-1]["returned"], dict)
                assert checks[-1]["monotonic_ns"] < starts[0]["monotonic_ns"]
                wrong = next(e for e in events if e["event"] == "wrong_run_refused")
                assert wrong["reason"] == "state export receipt identity mismatch"
                runtime_bindings[case.name]["wrong_export_run_refused"] = True
            else:
                recorded = load(case / "result.json")
                assert recorded["state"] == state
                assert load(case / "admission.json")["scope"] == "inspected_runtime_contract"
            results[case.name] = result
        else:
            assert verdict and verdict["score"] is None and verdict["outcome"] == "unmeasured"
            refused[case.name] = dict(reason=verdict["unmeasured"], started=False, score=None)

    # Actual pre-state is the same selected-only root which the next export reads.
    pre, post = root / selection["pre-state"], root / selection["post-export"]
    pre_binding, post_binding = load(pre / "binding.json"), load(post / "binding.json")
    assert pre_binding["source"] == post_binding["source"]
    before, after = inventory_answer(load(pre / "before.json")), inventory_answer(load(pre / "after.json"))
    events = load(post / "events.json")
    pre_export = inventory_answer(next(e["inventory"] for e in events if e["event"] == "before_export"))
    exported = inventory_answer(next(e["projection_inventory"] for e in events if e["event"] == "export_return"))
    assert before == after == pre_export
    assert before["mode"] == "0o444" and exported["mode"] == "0o640"
    assert before["inode"] != exported["inode"]
    for row in (before, exported):
        assert row["sha256"] == a41 and row["bytes"] == 3 and row["nlink"] == 1
    assert sha(post / "source-before.bin") == sha(post / "export-answer.bin") == a41
    assert results[pre.name] == results[post.name] == dict(expected="42", actual="41",
         completed_check="fail", exit_code=1, score=0.0)
    # Same closure paths, successful real checks, and rehashed sealed fixture bytes.
    pre_calls, post_calls = load(pre / "docker-calls.json"), load(post / "docker-calls.json")
    def closure_mount(calls):
        info = json.loads(next(c["stdout"] for c in calls if c["argv"][1] == "inspect" and c["returncode"] == 0))[0]
        return next(m["Source"] for m in info["Mounts"] if m["Destination"] == "/control-scorer")
    assert closure_mount(pre_calls) == closure_mount(post_calls)
    private = {}
    for row in load(fixture / "task-contract.json")["scorer"]["files"]:
        assert sha(fixture / "closure" / row["path"]) == row["sha256"]
        private[row["path"]] = row["sha256"]

    aba = root / selection["source-aba"]
    es = load(aba / "events.json")
    def one(name):
        return next(e for e in es if e["event"] == name)
    sequence = [one("export_return"), next(e for e in es if e.get("function") == "require_artifact_runtime"),
         one("source_write_42"), one("before_start"), one("after_start"), one("source_restore_41")]
    assert all(a["monotonic_ns"] < b["monotonic_ns"] for a, b in zip(sequence, sequence[1:]))
    actual_start_return = next(c for c in load(aba / "docker-calls.json") if c["argv"][1] == "start")
    assert one("before_start")["monotonic_ns"] < actual_start_return["monotonic_ns"] < one("after_start")["monotonic_ns"]
    assert sha(aba / "source-before.bin") == sha(aba / "source-after.bin") == a41
    for name in ("before_start", "after_start"):
        assert inventory_answer(one(name)["source_inventory"])["sha256"] == a42
        assert inventory_answer(one(name)["projection_inventory"])["sha256"] == a41
    assert results[aba.name]["score"] == 0.0 and results[aba.name]["actual"] == "41"
    intervals[aba.name] = {e["event"] + ("_" + e.get("function", "")): e["monotonic_ns"] for e in sequence}
    # A same-size selected-byte change is score-significant, but an unsealed edit
    # of that byte fails before start. Fresh legitimate 42 is a separate control.
    tamper = root / "projection-tamper"
    assert sha(tamper / "export-answer.bin") == a41 and sha(tamper / "tampered-answer.bin") == a42
    assert "state projection seal mismatch" in refused[tamper.name]["reason"]
    assert "artifact contract task differs from selected task" in refused["wrong-task"]["reason"]
    assert load(root / "wrong-task/docker-calls.json") == []
    assert results[selection["changed-answer"]] == dict(expected="42", actual="42",
         completed_check="pass", exit_code=0, score=1.0)
    return dict(valid=True, sealed_files=sealed_files, fixture_files=fixture_files,
         run_id=launch["run_id"], results=results, refusals=refused, bindings=runtime_bindings,
         source_change_interval_monotonic_ns=intervals, private_closure_sha256=private,
         answer41_sha256=a41, answer42_sha256=a42,
         production_measured=sum((root / name / "verdict.json").exists() for name in results),
         direct_reference_measured=sum(not (root / name / "verdict.json").exists() for name in results),
         production_unmeasured=len(refused), invalid_measurements=0, created=len(runtime_names),
         removed=len(runtime_names), resources=resource_observations,
         source_quiescence_established=False, source_limitation_demonstrated=True,
         execution_binding_scope="observer-run/trial envelope plus native task/contract/runtime/export; no native outer-run/trial inputs",
         equivalence_scope="selected-only pre-state to actual production export, authored control predicate only",
         dataset_equivalence_established=False, production_authorized=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = audit(args.packet)
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
