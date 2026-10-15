#!/usr/bin/env python3
"""Bounded direct-host authored control; allocate and remove only a fresh root."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def inventory(root):
    rows = []
    for path in sorted(root.rglob("*")):
        row = {"path": str(path), "kind": "directory" if path.is_dir() else "file"}
        if path.is_file():
            raw = path.read_bytes()
            row.update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        rows.append(row)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    check = args.check.resolve(strict=True)
    args.output.mkdir(exist_ok=False)
    inputs = Path(__file__).resolve().parent / "before/ds1000/inputs"
    root = Path(tempfile.mkdtemp(prefix="w-scratch-host-"))
    report = {"root": str(root), "check": str(check),
              "check_sha256": hashlib.sha256(check.read_bytes()).hexdigest(),
              "scope": "one authored arithmetic control; no dataset rows, model or endpoint",
              "outer_wall_bound_seconds": 8}
    try:
        work = root / "task"
        scratch = root / "ambient-tmp"
        work.mkdir()
        scratch.mkdir()
        for name in ("execution.py", "context.json", "solution.py"):
            shutil.copyfile(inputs / name, work / name)
        # Isolate this reproduction's host temp files from every other run.
        env = dict(os.environ, TMPDIR=str(scratch), PYTHONDONTWRITEBYTECODE="1")
        command = [sys.executable, "-B", str(check)]
        report.update(command_argv=command, cwd=str(work), TMPDIR=str(scratch))
        proc = subprocess.run(command, cwd=work, env=env, capture_output=True,
                              text=True, timeout=8)
        report.update(returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr,
                      reward=(work / "verifier/reward.txt").read_text(),
                      evidence=json.loads((work / "verifier/evidence.json").read_text()),
                      after_check=inventory(scratch))
        shutil.copytree(scratch, args.output / "after-scratch")
        shutil.rmtree(work)
        report.update(task_absent=not work.exists(), after_task_removal=inventory(scratch))
        assert proc.returncode == 0
    finally:
        shutil.rmtree(root)
        report["collector_root_absent"] = not root.exists()
        (args.output / "observation.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
