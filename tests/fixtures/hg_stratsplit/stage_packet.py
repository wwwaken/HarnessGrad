"""Stage only this worker's small evidence files, never payload symlinks."""
from pathlib import Path
import shlex
import subprocess

root = Path('tests/fixtures/hg_stratsplit')
paths = sorted(str(p) for p in root.iterdir() if p.is_file() and not p.is_symlink())
paths += ['registry/w-stratsplit-membership.md', 'registry/w-stratsplit-validation.txt',
          'registry/proposals/w-stratsplit.json']
assert all(Path(p).stat().st_size < 1_000_000 for p in paths)
assert all(not p.endswith('.body') for p in paths)
cmd = ['git', 'add', '-f', '--', *paths]
print('$ ' + shlex.join(cmd), flush=True)
subprocess.run(cmd, check=True)
staged = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '-z']).decode().strip('\0').split('\0')
assert set(staged) == set(paths)
assert all(subprocess.check_output(['git', 'diff', '--cached', '--diff-filter=A', '--name-only', '--', p]).decode().strip() == p for p in paths)
print('PASS: exactly', len(paths), 'worker-created files staged; all under 1 MB; no raw payload or symlink staged.')
