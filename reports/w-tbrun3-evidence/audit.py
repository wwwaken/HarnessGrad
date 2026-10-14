"""Read-only review of archived receipts and the original on-disk artifacts."""
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

ROOT = Path('/tmp/hg-tbrun3')
OUT = ROOT / 'reports/w-tbrun3-evidence'
inventory = json.loads((OUT / 'artifact-inventory.json').read_text())['files']
archive = json.loads((OUT / 'archive-sha256.json').read_text())
archive_path = Path(archive['path'])
assert hashlib.sha256(archive_path.read_bytes()).hexdigest() == archive['sha256']
with tarfile.open(archive_path) as tar:
    for item in inventory:
        path = Path(item['path'])
        raw = path.read_bytes()
        archived = tar.extractfile(str(path.relative_to(ROOT))).read()
        assert len(raw) == item['bytes']
        assert hashlib.sha256(raw).hexdigest() == item['sha256']
        assert archived == raw

changed = subprocess.check_output(
    ['git', 'diff', '--name-only', 'HEAD'], cwd=ROOT, text=True).splitlines()
assert all(name in {'docs/dataset-blockers.json', 'docs/adapter-integration-journal.md'}
           or name.startswith('reports/w-tbrun3-') for name in changed)
status = subprocess.check_output(
    ['git', 'status', '--porcelain', '--untracked-files=all'], cwd=ROOT, text=True)
for line in status.splitlines():
    name = line[3:]
    assert (name in {'docs/dataset-blockers.json', 'docs/adapter-integration-journal.md'}
            or name.startswith('reports/w-tbrun3-'))

registry = json.loads((ROOT / 'docs/dataset-blockers.json').read_text())
terminal = next(row for row in registry['datasets'] if row['dataset'] == 'terminal_bench')
assert any(b['id'] == 'cached-runtime-admission' for b in terminal['blockers'])
assert terminal['shared_blockers'] == ['scorer-offline-closure', 'artifact-only-state-export']
assert registry['review']['production_authorized'] is False

summary = dict(archive_sha256_verified=True, original_and_archived_files_verified=len(inventory),
               production_code_changed=False, tests_changed=False,
               cached_runtime_admission_still_open=True)
(OUT / 'integrity-audit.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary))
