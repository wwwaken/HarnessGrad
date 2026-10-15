"""Verify independent hashes, source citations, runtime scope and additive registry edits."""
import ast
import hashlib
import json
from pathlib import Path
import re
import tarfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
facts = json.loads((OUT / 'facts.json').read_text())
assert facts['complete_pinned_native_surfaces'] == {'numerator': 3, 'denominator': 7}
module = ast.parse((ROOT / 'data/runtimes/__init__.py').read_text())
pins = ast.literal_eval(next(node.value for node in module.body if isinstance(node, ast.Assign)))
for dataset, fact in facts['datasets'].items():
    path = ROOT / pins[dataset]['manifest']
    manifest = json.loads(path.read_text())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == pins[dataset]['sha256'] == fact['manifest_sha256']
    capture = OUT / fact['capture']
    assert (capture / 'manifest.json').read_bytes() == path.read_bytes()
    raw_hashes = {}
    for record in json.loads((capture / 'invocations.json').read_text()):
        assert record['returncode'] == 0
        if record['argv'][0] == '/usr/bin/sha256sum':
            for row in (capture / (record['raw'] + '.stdout.txt')).read_text().splitlines():
                sha, source = row.split('  ', 1)
                raw_hashes[source] = sha
    assert len(manifest['files']) == fact['files']
    for target, entry in manifest['files'].items():
        source = Path(entry['source'])
        source = source if source.is_absolute() else ROOT / source
        assert hashlib.sha256(source.read_bytes()).hexdigest() == entry['sha256'] == raw_hashes[entry['source']], target
    archive = Path(fact['payload'])
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == raw_hashes[str(archive)]
    with tarfile.open(archive) as tar:
        assert set(tar.getnames()) == {p.lstrip('/') for p in manifest['files']}
        for target, entry in manifest['files'].items():
            assert hashlib.sha256(tar.extractfile(target.lstrip('/')).read()).hexdigest() == entry['sha256']
    loads = json.loads((OUT / f'{dataset}-scorer-loads.json').read_text())
    assert len(loads['loaded']) == fact['actual_check_elf_destinations_including_loader']
    assert set(loads['loaded']) <= manifest['files'].keys()
    control = json.loads((OUT / f'{dataset}-control-loads.json').read_text())
    for role, mapped in control['loads'].items():
        assert len(mapped) == fact['inherited_control_elf_counts'][role]
        assert set(mapped) <= manifest['files'].keys()
        assert control['ctypes_audit'][role]
        assert all(e['sha256'] in {v['sha256'] for v in manifest['files'].values()}
                   for e in control['ctypes_audit'][role])
    assert (OUT / 'pytest-targeted.stdout.txt').read_text().splitlines()[control['raw_line'] - 1].strip()
    for suffix in ['closure-files', 'actual-native', 'control-native']:
        text = (OUT / f'{dataset}-{suffix}.md').read_text()
        for relative, number in re.findall(r'((?:[a-z-]+capture/commands/\d+\.stdout\.txt|bound-replay-final\.strace\.txt|pytest-targeted\.stdout\.txt)):(\d+)', text):
            assert (OUT / relative).read_text().splitlines()[int(number) - 1].strip()

sites = json.loads((OUT / 'source-sites.json').read_text())
for entry in sites['sources']:
    source = Path(entry['file'])
    source = source if source.is_absolute() else ROOT / source
    snapshot = OUT / entry['snapshot']
    assert source.read_bytes() == snapshot.read_bytes()
    assert hashlib.sha256(source.read_bytes()).hexdigest() == entry['sha256']
for entry in sites['citations']:
    source = Path(entry['file'])
    source = source if source.is_absolute() else ROOT / source
    assert source.read_text().splitlines()[entry['line'] - 1] == entry['text']
    assert entry['text'].strip()

before = json.loads((OUT / 'registry-before.json').read_text())
after = json.loads((ROOT / 'docs/dataset-blockers.json').read_text())
prior = next(b for b in before['shared_blockers'] if b['id'] == 'scorer-offline-closure')
current = next(b for b in after['shared_blockers'] if b['id'] == 'scorer-offline-closure')
assert current['observed'].startswith(prior['observed'] + ' ')
addition = current['observed'][len(prior['observed']) + 1:]
assert addition in (ROOT / 'reports/w-hp3-receipts.md').read_text()
assert current['evidence'][:-1] == prior['evidence']
entry = current['evidence'][-1]
assert entry['path'] == 'reports/w-hp3-receipts.md'
assert entry['locator'] in (ROOT / entry['path']).read_text()
current['observed'], current['evidence'] = prior['observed'], prior['evidence']
assert after == before, 'registry mutation outside observation/evidence'
assert '## 2026-10-15 Jericho and ALFWorld sealed native closures - w-hp3' in (ROOT / 'docs/adapter-integration-journal.md').read_text()
print(json.dumps({'valid': True, 'native_surfaces': facts['complete_pinned_native_surfaces'],
                  'all_statuses_next_actions_histories_gates_unchanged': True,
                  'payload_archives_verified': [f['payload'] for f in facts['datasets'].values()],
                  'scope': 'bounded Jericho replay and ALFWorld synchronous tw-pddl replay; no production authorization'}, sort_keys=True))
