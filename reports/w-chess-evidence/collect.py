"""Preserve this attempt's immutable receipts; no run or receipt is rewritten."""
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import tarfile

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'runs/w-chess-stepwise-20261014T202226Z-11489149'
OUT = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write(name, value):
    with (OUT / name).open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


assert (RUN / 'task-result.json').is_file()
assert (RUN / 'diagnostic_receipt.json').is_file()
live = json.loads((RUN / 'launch/live-path-observation.json').read_text())
paths = [live['task_path']] + [p['path'] for p in live['candidate_stepwise_paths']]
write('cleanup-observation.json', dict(
    observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    attribution='Task path matched selected task.json; socket path also appears in actor trace. No paths removed by observer.',
    paths=[dict(path=p, exists=Path(p).exists()) for p in paths],
    workspace_retained_for_evidence=json.loads((RUN / 'identity.json').read_text())['workspace']))
shutil.copytree(RUN, OUT / 'execution')
inventory = []
for src in sorted(RUN.rglob('*')):
    if not src.is_file():
        continue
    rel = src.relative_to(RUN)
    data = src.read_bytes()
    copy = OUT / 'execution' / rel
    assert copy.read_bytes() == data
    inventory.append(dict(source=str(src), copy=str(copy.relative_to(ROOT)),
                          relative_path=str(rel), bytes=len(data), sha256=sha(data)))
write('artifact-inventory.json', inventory)
archive = OUT / 'run-artifacts.tar.gz'
with tarfile.open(archive, 'x:gz') as tar:
    tar.add(RUN, arcname=RUN.name)
with tarfile.open(archive) as tar:
    for row in inventory:
        data = tar.extractfile(RUN.name + '/' + row['relative_path']).read()
        assert len(data) == row['bytes'] and sha(data) == row['sha256']
write('archive-sha256.json', dict(path=str(archive.relative_to(ROOT)),
                                bytes=archive.stat().st_size, sha256=sha(archive.read_bytes())))
write('integrity-audit.json', dict(original_copy_archive_files_checked=len(inventory),
    all_copies_and_archive_match=True,
    policy_manifest_matches=(json.loads((RUN / 'diagnostic_receipt.json').read_text())
                             ['context']['hashes']['manifest'] == sha((RUN / 'launch/manifest.json').read_bytes())),
    production_diff_paths=__import__('subprocess').check_output(
        ['git', 'diff', '--name-only', '--', 'eval', 'data', 'driver.py', 'base_harness'],
        cwd=ROOT, text=True).splitlines()))
print(json.dumps(json.loads((OUT / 'integrity-audit.json').read_text()), indent=2))
