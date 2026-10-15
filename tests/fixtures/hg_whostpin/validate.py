"""Validate the exact native-scope packet and additive-only registry change."""
from pathlib import Path
import hashlib
import json
import re
import tarfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
manifest_path = ROOT / 'data/runtimes/bird_minidev-native.json'
manifest = json.loads(manifest_path.read_text())
facts = json.loads((OUT / 'facts.json').read_text())
digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
assert facts['manifest_sha256'] == digest
adapter = (ROOT / 'data/datasets/bird_minidev.py').read_text()
assert f'"sha256": "{digest}"' in adapter
assert facts['files'] == len(manifest['files'])
assert facts['unique_payload_digests'] == len({e['sha256'] for e in manifest['files'].values()})
assert facts['complete_pinned_native_surfaces'] == {'numerator': 1, 'denominator': 7}

# Independently captured raw hashes bind every admission payload.
commands = json.loads((OUT / 'final-capture/invocations.json').read_text())
raw_hashes = {}
for record in commands:
    assert record['returncode'] == 0
    if record['argv'][0] == '/usr/bin/sha256sum':
        for row in (OUT / 'final-capture' / (record['raw'] + '.stdout.txt')).read_text().splitlines():
            sha, name = row.split('  ', 1)
            raw_hashes[name] = sha
for target, entry in manifest['files'].items():
    source = Path(entry['source'])
    assert hashlib.sha256((source if source.is_absolute() else ROOT / source).read_bytes()).hexdigest() == entry['sha256'], target
    assert raw_hashes[entry['source']] == entry['sha256']
archive = Path(json.loads((OUT / 'final-capture/build-summary.json').read_text())['payload'])
assert hashlib.sha256(archive.read_bytes()).hexdigest() == raw_hashes[str(archive)]
with tarfile.open(archive) as tar:
    assert set(tar.getnames()) == {name.lstrip('/') for name in manifest['files']}
    for target, entry in manifest['files'].items():
        assert hashlib.sha256(tar.extractfile(target.lstrip('/')).read()).hexdigest() == entry['sha256'], target

# Every source/trace/binary line citation is real, nonblank and retained.
for site in json.loads((OUT / 'source-sites.json').read_text()):
    assert (ROOT / site['file']).read_text().splitlines()[site['line'] - 1] == site['text']
    assert site['text'].strip()
for appendix in ['closure-files.md', 'actual-scorer-native.md']:
    text = (OUT / appendix).read_text()
    for relative, number in re.findall(r'((?:final-capture/commands/\d+\.stdout\.txt|bound-check\.strace\.txt)):(\d+)', text):
        assert (OUT / relative).read_text().splitlines()[int(number) - 1].strip()
loads = json.loads((OUT / 'scorer-loads.json').read_text())
assert len(loads['loaded']) == facts['actual_scorer_elf_destinations_including_loader']
assert set(loads['loaded']) <= manifest['files'].keys()

# Revert ONLY the permitted additive observation/evidence in a comparison copy.
before = json.loads((OUT / 'registry-before.json').read_text())
after = json.loads((ROOT / 'docs/dataset-blockers.json').read_text())
prior = next(b for b in before['shared_blockers'] if b['id'] == 'scorer-offline-closure')
current = next(b for b in after['shared_blockers'] if b['id'] == 'scorer-offline-closure')
assert current['observed'].startswith(prior['observed'] + ' ')
addition = current['observed'][len(prior['observed']) + 1:]
assert addition in (ROOT / 'reports/w-hostpin-receipts.md').read_text()
assert current['evidence'][:-1] == prior['evidence']
evidence = current['evidence'][-1]
assert evidence['path'] == 'reports/w-hostpin-receipts.md'
assert evidence['locator'] in (ROOT / evidence['path']).read_text()
current['observed'], current['evidence'] = prior['observed'], prior['evidence']
assert after == before, 'registry change outside native-scope observation/evidence'
assert (ROOT / 'docs/adapter-integration-journal.md').read_text().count('## 2026-10-15 BIRD immutable native userland closure - w-hostpin') == 1
print(json.dumps({'valid': True, 'manifest_sha256': digest, 'payload_files': len(manifest['files']),
                  'payload_archive_verified': str(archive), 'registry_scope': 'additive S3 BIRD native userland observation/evidence only',
                  'all_statuses_next_actions_dataset_history_gates_unchanged': True}, sort_keys=True))
