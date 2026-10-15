#!/usr/bin/env python3
"""Capture exact read-only inspection subprocess output; no generator execution."""
import datetime, hashlib, json, pathlib, subprocess, sys
root = pathlib.Path(__file__).resolve().parent
name, *argv = sys.argv[1:]
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
proc = subprocess.run(argv, capture_output=True)
for stream in ("stdout", "stderr"):
    root.joinpath(name+"."+stream+".txt").write_bytes(getattr(proc, stream))
record = {"argv": argv, "cwd": str(pathlib.Path.cwd()), "started_utc": started, "returncode": proc.returncode,
          "stdout_sha256": hashlib.sha256(proc.stdout).hexdigest(), "stderr_sha256": hashlib.sha256(proc.stderr).hexdigest()}
root.joinpath(name+".command.json").write_text(json.dumps(record, indent=2)+"\n")
sys.stdout.buffer.write(proc.stdout)
sys.stderr.buffer.write(proc.stderr)
sys.exit(proc.returncode)
