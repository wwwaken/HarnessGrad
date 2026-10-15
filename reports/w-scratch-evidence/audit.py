#!/usr/bin/env python3
"""Read-only assertions over the newly collected scratch evidence."""
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]


def read(path):
    return json.loads(path.read_text())


summary = {}
for phase, runtimes in (("before", ("ds1000", "livecodebench", "bird_minidev")),
                        ("after", ("ds1000",))):
    execution = read(ROOT / phase / "execution.json")
    assert execution["model"] is None and execution["endpoint"] is None
    assert execution["benchmark"] is False and execution["jobs"] == 1
    assert read(ROOT / phase / "root-cleanup.json")["absent"] is True
    for runtime in runtimes:
        case = ROOT / phase / runtime
        process = read(case / "process-summary.json")
        assert process["returncode"] == 0 and process["timed_out"] is False
        assert not process["remaining_before_collector_path_cleanup"]
        assert not process["collector_waitpid"]
        assert not (case / "collector-forced-cleanup.json").exists()
        cleanup = read(case / "cleanup.json")
        assert cleanup["case_absent"] and cleanup["scratch_absent"]
        assert all(cleanup["observed_pid_absence"].values())
        verdict = read(case / "output/evidence.json")
        assert verdict["measured"] is True and verdict["reward"] == 1
        leftovers = [row for row in read(case / "scratch-observations.json")["after_check"]
                     if row["path"] not in ("control", "home")]
        assert bool(leftovers) == (phase == "before" and runtime == "ds1000")
        sources = read(case / "sources.json")
        recorded = next(row for row in sources if row["path"].endswith("/verify/check.py"))
        assert hashlib.sha256((case / "inputs/verify/check.py").read_bytes()).hexdigest() == recorded["sha256"]
        summary[f"{phase}/{runtime}"] = dict(run_id=execution["run_id"],
            leftovers=leftovers, returncode=process["returncode"], measured=True,
            collector_reaping=False, forced_cleanup=False, owned_paths_absent=True)
before_ds = ROOT / "before/ds1000/after-scratch"
for name in ("execution.py", "program.json", "run_ds1000.py"):
    original = REPO / "reports/w-jvm-evidence/followup/ds1000/after-scratch/ds1000-check-rugl1mm4" / name
    assert next(before_ds.glob(f"ds1000-check-*/{name}")).read_bytes() == original.read_bytes()
trace = gzip.open(ROOT / "after/ds1000/syscalls.txt.gz", "rt").read()
assert 'rmdir("/tmp/ds1000-check-k37wwntg") = 0' in trace
old_host = read(ROOT / "host-before/observation.json")
new_host = read(ROOT / "host-after/observation.json")
assert old_host["after_check"] == old_host["after_task_removal"]
assert old_host["after_check"]
assert not new_host["after_check"] and not new_host["after_task_removal"]
assert old_host["task_absent"] and new_host["task_absent"]
assert old_host["collector_root_absent"] and new_host["collector_root_absent"]
assert old_host["evidence"] == new_host["evidence"]
assert old_host["stdout"] == new_host["stdout"]
summary["host"] = dict(before_leftovers_survive_task_removal=True,
                       after_leftovers=False, verdict_and_stdout_unchanged=True,
                       collector_roots_absent=True)
print(json.dumps(summary, indent=2, sort_keys=True))
