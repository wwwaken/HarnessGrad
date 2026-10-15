"""Capture the original writer's input; never bypass its isolation guard.

Run from the assigned worktree; pass a fresh output directory to replay safely.
Only the records module is loaded from the observed baseline revision, in
memory. The driver, fixture and guard stay real.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import traceback
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent
artifacts = ["before-capture-driver.txt", "before-attempted-bad-candidate.curve.jsonl",
             "before-capture-persisted.curve.jsonl"]
if any((OUT / name).exists() for name in artifacts):
    raise SystemExit("Refusing to overwrite evidence; pass a fresh output directory.")
OUT.mkdir(parents=True, exist_ok=True)
BASELINE = "2525a653efd3383c25601109ab22c22129664b53"
os.environ["HG_AGENT_BACKEND"] = "mock"
scratch = Path(tempfile.mkdtemp(prefix="isolationmix-capture-", dir="/tmp"))
os.environ["TMPDIR"] = str(scratch)
tempfile.tempdir = str(scratch)
try:
    import harnessgrad.records as records

    source = subprocess.check_output(
        ["git", "show", f"{BASELINE}:harnessgrad/records.py"], cwd=ROOT, text=True)
    exec(compile(source, records.__file__, "exec"), records.__dict__)
    original = records._write_curve
    attempted = []

    def capture(path, curve):
        attempted.append("".join(json.dumps(point) + "\n" for point in curve))
        original(path, curve)

    records._write_curve = capture
    fixture = runpy.run_path(str(ROOT / "tests/quality/test_candidate_apply.py"))
    method = scratch / "inputs" / "bad_method.py"
    method.parent.mkdir()
    method.write_text(fixture["_BAD_METHOD"])
    run_id = "isolationmix-before-" + uuid.uuid4().hex
    sys.argv = [str(ROOT / "driver.py"), "--harness", "loop_plain", "--mode", "A",
                "--rounds", "1", "--run-id", run_id, "--dataset", "demo",
                "--sampling", "all", "--side", "train", "--runs-root",
                str(scratch / "runs"), "--work-root", str(scratch / "work"),
                "--method-entrypoint", f"{sys.executable} {method}"]
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(captured):
        try:
            runpy.run_path(str(ROOT / "driver.py"), run_name="__main__")
        except BaseException:
            traceback.print_exc()
    (OUT / "before-capture-driver.txt").write_text(captured.getvalue())
    (OUT / "before-attempted-bad-candidate.curve.jsonl").write_text(attempted[-1])
    persisted = scratch / "runs" / run_id / "curve.jsonl"
    shutil.copyfile(persisted, OUT / "before-capture-persisted.curve.jsonl")
    print(f"BASELINE records.py: {BASELINE}")
    print(f"FRESH RUN ID: {run_id}")
    for point in map(json.loads, (OUT / "before-attempted-bad-candidate.curve.jsonl").read_text().splitlines()):
        print(json.dumps({key: point.get(key) for key in (
            "round", "score", "n_scored", "scorer_isolation_class", "measured_by_platform", "unmeasured")}, sort_keys=True))
    assert "IsolationMismatch: scorer isolation class mismatch: in-process, unknown" in captured.getvalue()
    print("ORIGINAL GUARD RAISED: scorer isolation class mismatch: in-process, unknown")
finally:
    shutil.rmtree(scratch)
    print(f"DELETED {scratch}")
