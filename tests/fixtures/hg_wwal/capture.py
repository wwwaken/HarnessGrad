"""Preserve exact argv, cwd, raw streams and actual return code for one bounded command."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument("stem", type=Path)
parser.add_argument("argv", nargs=argparse.REMAINDER)
args = parser.parse_args()
args.stem.parent.mkdir(parents=True, exist_ok=True)
command = args.argv[1:] if args.argv[:1] == ["--"] else args.argv
metadata = {"argv": command, "cwd": str(Path.cwd()), "timeout_seconds": 150}
with Path(str(args.stem) + ".stdout.txt").open("xb") as stdout, Path(str(args.stem) + ".stderr.txt").open("xb") as stderr:
    try:
        proc = subprocess.run(command, stdout=stdout, stderr=stderr, timeout=150)
        metadata["returncode"] = proc.returncode
    except subprocess.TimeoutExpired:
        metadata["timed_out"] = True
        metadata["returncode"] = None
Path(str(args.stem) + ".command.json").write_text(json.dumps(metadata, sort_keys=True, indent=2) + "\n")
print(json.dumps(metadata, sort_keys=True))
raise SystemExit(metadata["returncode"] if metadata["returncode"] is not None else 124)
