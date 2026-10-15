"""Read-only audit of the preserved before/after real-daemon packets."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("historical_quiesce_auditor", REPO / "reports/w-quiesce-evidence/audit.py")
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)


def audit(root):
    phases = {}
    for phase in ("before", "after"):
        packet = root / phase
        launch = old.load(packet / "launch.json")
        assert launch["phase"] == phase and all(launch["fixture_checks"].values())
        for name, pin in launch["source_hashes"].items():
            assert old.sha(root / (phase + "-source") / name) == pin, name
        fixture = REPO / "tests/fixtures/hg_wpristine"
        assert old.check_seals(fixture) == len(launch["fixture_checks"])
        assert old.load(fixture / "trusted-pins.json") == launch["pins"]
        selection = old.load(packet / "selection.json")
        counts = dict(cases=0, native_measured=0, unmeasured=0, created=0, removed=0, started=0)
        results = {}
        for case in sorted(p for p in packet.iterdir() if p.is_dir()):
            counts["cases"] += 1
            binding = old.load(case / "binding.json")
            verdict = old.load(case / "verdict.json")
            evidence = verdict["scorer_isolation_evidence"]
            calls = old.load(case / "docker-calls.json")
            events = old.load(case / "events.json")
            assert binding["task_id"] == launch["task"]["task_id"] and binding["trial"] == 1
            assert verdict["outcome"] in {"measured", "unmeasured"}
            counts["native_measured" if verdict["outcome"] == "measured" else "unmeasured"] += 1
            created = next(c for c in calls if c["argv"][1] == "create")
            assert created["returncode"] == 0
            counts["created"] += 1
            name = created["argv"][created["argv"].index("--name") + 1]
            export = evidence["export"]
            assert export["run_id"] == name and export["task_id"] == binding["task_id"]
            assert export["contract_sha256"] == launch["pins"]["artifact_contract_sha256"]
            assert export["source_sha256"] == launch["pins"]["source_sha256"]
            assert export["bytes"] == 3 and export["inodes"] == 2
            assert export["limits"] == dict(max_bytes=16, max_inodes=2)
            assert export["files"] == [dict(path="answer.txt", bytes=3, sha256=old.sha(case / "export-answer.bin"))]
            assert old.sha(case / "source-before.bin") == old.sha(case / "source-after.bin") == export["files"][0]["sha256"]
            assert any(e["event"] == "wrong_run_refused" and e["reason"] == "state export receipt identity mismatch" for e in events)
            removed = next(c for c in calls if c["argv"][1] == "rm")
            assert removed["returncode"] == 0 and removed["argv"][-1] == name
            assert evidence["cleanup"]["removed"]
            counts["removed"] += 1
            absence = old.load(case / "absence.json")
            assert absence["returncode"] == 1 and json.loads(absence["stdout"]) == []
            assert old.load(case / "projection-after.json")["exists"] is False
            info = json.loads(next(c for c in calls if c["argv"][1] == "inspect")["stdout"])[0]
            assert len(info["Mounts"]) == 2 and all(not m["RW"] for m in info["Mounts"])
            assert {m["Destination"] for m in info["Mounts"]} == {"/control-input", "/control-scorer"}
            resources = {key: info["HostConfig"][key] for key in ("NanoCpus", "Memory", "MemorySwap", "PidsLimit", "Tmpfs")}
            starts = [c for c in calls if c["argv"][1] == "start"]
            assert len(starts) <= 1
            counts["started"] += len(starts)
            observation = evidence.get("source_observation")
            changed_fields = []
            if phase == "after":
                assert observation["quiescence_established"] is False
                assert observation["scope"] == "selected_source_file_endpoint_probes"
                assert observation["export_content_matches_before"] is True
                a, b = observation["before"]["files"][0], observation["after"]["files"][0]
                changed_fields = [key for key in a if a[key] != b[key]]
                assert a["sha256"] == b["sha256"] == export["files"][0]["sha256"]
                assert observation["before"]["finished_monotonic_ns"] <= observation["after"]["started_monotonic_ns"]
                native_binding = evidence["execution_binding"]
                assert native_binding["task_id"] == binding["task_id"] and native_binding["selected_task_checked"]
                assert native_binding["runtime_export_run_id"] == name
                assert native_binding["outer_run_id"] is None and native_binding["trial_id"] is None
                assert native_binding["outer_run_trial_binding"] == "not_provided"
            predicate = None
            if starts:
                predicate = old.predicate(starts[0], evidence["stopped_result"]["state"])
                assert evidence["start_result"]["stdout"] == starts[0]["stdout"]
                if binding["probe"] == "source-aba":
                    assert predicate["actual"] == "41" and predicate["expected"] == "42"
                    timeline = {e["event"]: e for e in events if e["event"] in {
                        "export_return", "source_write_42", "before_start", "after_start", "source_restore_41"}}
                    assert list(sorted(timeline, key=lambda k: timeline[k]["monotonic_ns"])) == [
                        "export_return", "source_write_42", "before_start", "after_start", "source_restore_41"]
                    changed_digest = hashlib.sha256(b"42\n").hexdigest()
                    for event in ("before_start", "after_start"):
                        assert old.inventory_answer(timeline[event]["source_inventory"])["sha256"] == changed_digest
                        assert old.inventory_answer(timeline[event]["projection_inventory"])["sha256"] == export["files"][0]["sha256"]
                    if phase == "after":
                        assert observation["before"]["finished_monotonic_ns"] <= timeline["export_return"]["monotonic_ns"]
                        assert timeline["source_restore_41"]["monotonic_ns"] <= observation["after"]["started_monotonic_ns"]
                        assert {"st_ctime_ns", "st_mtime_ns"} <= set(changed_fields)
                        assert observation["status"] == "difference_observed"
                        assert verdict["score"] is None and verdict["outcome"] == "unmeasured"
                    else:
                        assert verdict["score"] == 0.0 and verdict["outcome"] == "measured"
                else:
                    assert predicate["completed_check"] == "pass" and verdict["score"] == 1.0
                    if phase == "after":
                        assert not changed_fields and observation["status"] == "no_change_observed"
            else:
                assert verdict["score"] is None and "trusted artifact runtime boundary mismatch" in verdict["unmeasured"]
                assert info["Config"]["Env"] != ["PATH=/control-scorer", "HOME=/tmp", "TMPDIR=/tmp"]
            results[case.name] = dict(outcome=verdict["outcome"], score=verdict["score"], runtime_id=name,
                source_status=observation["status"] if observation else "not_implemented",
                changed_fields=changed_fields, predicate=predicate, resources=resources)
        assert results[selection["unchanged"]]["score"] == 1.0
        assert results[selection["source-aba"]]["source_status"] == ("difference_observed" if phase == "after" else "not_implemented")
        phases[phase] = dict(**counts, sealed_files=old.check_seals(packet), selected=selection, results=results)
    return dict(phases=phases, demonstrated_mutation_detected_after=True,
                source_quiescence_established=False, native_outer_run_trial_binding=False,
                production_authorized=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = audit(args.root)
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps(result, sort_keys=True))
