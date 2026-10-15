"""Verify copied native Docker binding controls and their source/content seals."""
import hashlib
import json
from pathlib import Path
import sys


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def audit(root):
    repo = root.resolve().parents[1]
    provenance = read(root / "copy-provenance-initial.json") + read(root / "copy-provenance-final.json")
    for row in provenance:
        path = repo / row["destination"]
        assert sha(path) == row["sha256"] and path.stat().st_size == row["bytes"]
    result = dict(production_authorized=False, source_quiescence_established=False, phases={})
    for phase in ("before", "after-initial", "after-incomplete", "after"):
        packet = root / phase
        launch = read(packet / "launch.json")
        sealed = 0
        if (packet / "SHA256SUMS").exists():
            for line in (packet / "SHA256SUMS").read_text().splitlines():
                digest, name = line.split("  ", 1)
                assert sha(packet / name) == digest
                sealed += 1
        else:
            assert phase == "after-incomplete"  # Preserved collector exception, not a completed packet.
        for name, digest in launch["source_sha256"].items():
            assert sha(packet / "sources" / name) == digest
            if phase == "after" and not name.endswith("collect.py"):
                assert sha(repo / name) == digest
        cases, counts = {}, dict(created=0, started=0, removed=0, verdicts_measured=0,
                                 verdicts_unmeasured=0, completed_pass=0)
        for case in sorted(p for p in packet.iterdir() if p.is_dir() and (p / "docker-calls.json").exists()):
            calls = read(case / "docker-calls.json")
            for action, count in (("create", "created"), ("start", "started"), ("rm", "removed")):
                counts[count] += sum(c["argv"][1] == action and (c["returncode"] == 0 or action == "start") for c in calls)
            counts["completed_pass"] += sum(c["argv"][1] == "start" and c["returncode"] == 0
                                            and "completed_check=pass\n" in c["stdout"] for c in calls)
            for absence in case.glob("absence*.json"):
                observed = read(absence)
                assert observed["returncode"] != 0 and "no such object" in observed["stderr"].lower()
            verdict_paths = sorted(case.glob("verdict*.json"))
            records = []
            for path in verdict_paths:
                verdict = read(path)
                evidence = verdict["scorer_isolation_evidence"]
                measured = verdict.get("score") is not None
                counts["verdicts_measured" if measured else "verdicts_unmeasured"] += 1
                if "cleanup" in evidence:
                    assert evidence["cleanup"]["removed"] is True
                if measured:
                    assert verdict["score"] == 1.0 and verdict["outcome"] == "measured"
                    assert "actual=42\n" in evidence["start_result"]["stdout"]
                    assert "expected=42\n" in evidence["start_result"]["stdout"]
                    assert "completed_check=pass\n" in evidence["start_result"]["stdout"]
                    assert evidence["stopped_result"]["state"]["ExitCode"] == 0
                    if phase != "before":
                        identity = {key: evidence["execution_binding"][key] for key in ("task_id", "outer_run_id", "trial_id")}
                        assert identity == evidence["export"]["execution_binding"] == evidence["runtime"]["execution_binding"]
                        assert evidence["export"]["schema"] == "harnessgrad.state-export-receipt.v2"
                elif phase != "before" and case.name.startswith("foreign-export-"):
                    assert "state export receipt identity mismatch" in verdict["unmeasured"]
                    assert not any(c["argv"][1] == "start" for c in calls)
                records.append(dict(path=path.relative_to(root).as_posix(), score=verdict["score"],
                    outcome=verdict.get("outcome"), reason=verdict.get("unmeasured"),
                    execution_binding=evidence.get("execution_binding")))
            if (case / "export-receipt.json").exists():
                exported = read(case / "export-receipt.json")
                answer = case / "export-answer.bin"
                assert answer.read_bytes() == b"42\n" and sha(answer) == exported["files"][0]["sha256"]
            cases[case.name] = records
        assert counts["created"] == counts["removed"]
        replay = {}
        for dimension in ("task_id", "outer_run_id", "trial_id"):
            consumer = read(packet / ("foreign-verdict-" + dimension + ".json"))
            if phase == "before":
                assert len(consumer["per_task"]) == 1 and not consumer["invalid"]
            else:
                assert not consumer["per_task"] and consumer["invalid"]
                assert "execution binding" in json.dumps(consumer["invalid"])
            replay[dimension] = dict(per_task=consumer["per_task"], invalid=consumer["invalid"])
        result["phases"][phase] = dict(sealed_files=sealed, counts=counts, cases=cases, verdict_replays=replay)
    final = root / "after"
    summary = read(final / "summary.json")
    if summary["selected_native_outer"] is not None:
        case = final / summary["selected_native_outer"]
        expected, measured = read(case / "requested.json"), read(case / "result.json")
        task = expected["task_id"]
        assert measured["per_task"] == {task: 1.0} and not measured["invalid"]
        bindings = [v["scorer_isolation_evidence"]["execution_binding"] for v in measured["trial_verdicts"][task]]
        for ordinal, binding in enumerate(bindings, 1):
            assert binding["outer_run_id"] == expected["run_id"] and binding["task_id"] == task
            assert binding["trial_id"] == f"round-3.harness-{expected['harness_sha']}.trial-{ordinal}"
        assert len(bindings) == 2
        result["native_outer"] = dict(case=summary["selected_native_outer"], bindings=bindings)
    else:
        result["native_outer"] = dict(case=None, reason="retained runtime admission failures")
    result["copied_files"] = len(provenance)
    return result


if __name__ == "__main__":
    root, output = map(Path, sys.argv[1:])
    result = audit(root)
    with output.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps(result, sort_keys=True))
