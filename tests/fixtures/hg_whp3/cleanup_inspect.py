"""Read-only observation of this worktree's control processes and retained files."""
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
excluded = set()
pid = os.getpid()
while pid > 1:
    excluded.add(pid)
    try:
        status = Path(f'/proc/{pid}/status').read_text()
        pid = int(next(line.split()[1] for line in status.splitlines() if line.startswith('PPid:')))
    except (OSError, StopIteration):
        break

matches = []
for directory in Path('/proc').iterdir():
    if not directory.name.isdigit() or int(directory.name) in excluded:
        continue
    try:
        argv = (directory / 'cmdline').read_bytes().split(b'\0')
        argv = [arg.decode(errors='replace') for arg in argv if arg]
    except OSError:
        continue
    if any('/tmp/hg-hp3' in arg or 'hg_whp3/' in arg for arg in argv):
        matches.append({'pid': int(directory.name), 'argv': argv})

facts = json.loads((Path(__file__).parent / 'facts.json').read_text())
archives = []
for name, fact in facts['datasets'].items():
    path = Path(fact['payload'])
    archives.append({'dataset': name, 'path': str(path), 'exists': path.is_file(),
                     'compressed_bytes': path.stat().st_size})
changed = subprocess.check_output(
    ['git', 'diff', '--name-only', '31ff5916'], cwd=ROOT, text=True).splitlines()
assert not any(path.startswith('runs/') for path in changed)
print(json.dumps({'matching_worktree_processes_excluding_inspector_ancestors': matches,
                  'retained_final_archives': archives,
                  'retained_external_test_roots': sorted(str(p) for p in Path('/tmp').glob('hg-hp3-pytest-*')),
                  'tracked_runs_paths_changed': [],
                  'scope': 'read-only local control observation; not a production lifecycle receipt'}, indent=2))
assert not matches, 'inspect matching processes; do not stop operator work'
