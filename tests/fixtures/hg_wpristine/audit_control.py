"""Reconcile a preserved production verdict with actual control completion.

Only the authored scorer's completed_check marker establishes that its metric ran.
The first driver version inferred measurement from the numeric verdict alone;
this independent audit preserves that historical output and records the failure.
"""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    root = args.evidence
    load = lambda name: json.loads((root / name).read_text())
    verdict = load("verdict.json")
    launch = load("launch.json")
    calls = load("docker-calls.json")
    started = next((c for c in calls if c["argv"][1] == "start"), {})
    completed = "completed_check=" in started.get("stdout", "")
    measured = (completed and isinstance(verdict.get("score"), (float, int))
                and not verdict.get("unmeasured"))
    receipt = dict(schema="harnessgrad.w-pristine-audited-control.v1",
        run_id=launch["run_id"], metric_identity=launch["task"]["metric"],
        eligible_tasks=1, selected_tasks=1, expected_trials=1,
        measured_trials=int(measured), unmeasured_trials=int(not measured and completed),
        invalid_trials=int(not completed), count_categories="disjoint",
        completed_answer_checks=int(completed), score=verdict.get("score") if measured else None,
        raw_verdict_score=verdict.get("score"),
        raw_scorer_isolation_class=verdict["scorer_isolation_class"],
        scorer_completion_marker_observed=completed,
        scorer_stderr=started.get("stderr"),
        reason="completed_control_check" if measured else "scorer_failed_before_control_check",
        lifecycle=None, cpu_effective_kernel_observation="unknown",
        memory_effective_kernel_observation="unknown", pids_effective_kernel_observation="unknown",
        tmpfs_effective_kernel_observation="unknown", production_authorized=False,
        source_artifacts=["verdict.json", "launch.json", "docker-calls.json", "docker-02.json"],
        historical_driver_receipt="control-receipt.json retained unchanged; its measured count is not valid")
    with (root / "measurement-audit.json").open("x") as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
