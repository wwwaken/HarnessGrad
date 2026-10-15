"""Run one bounded evidence command; retain argv, stdout, stderr and exit status."""
import json
from pathlib import Path
import subprocess
import sys

out = Path(__file__).parent
name, *argv = sys.argv[1:]
assert not (out / (name + '.command.json')).exists(), name
proc = subprocess.run(argv, capture_output=True)
(out / (name + '.stdout.txt')).write_bytes(proc.stdout)
(out / (name + '.stderr.txt')).write_bytes(proc.stderr)
(out / (name + '.command.json')).write_text(json.dumps(
    {'argv': argv, 'returncode': proc.returncode}, indent=2) + '\n')
print(json.dumps({'name': name, 'returncode': proc.returncode}))
sys.exit(proc.returncode)
