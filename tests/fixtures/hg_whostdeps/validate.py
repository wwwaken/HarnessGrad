"""Validate the inventory evidence and exact additive registry scope."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def read(name):
    return json.loads((OUT / name).read_text())


def sha(p):
    with p.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def parse_hashes(paths):
    result = {}
    for path in paths:
        for line in path.read_text().splitlines():
            digest, name = line.split('  ', 1)
            assert re.fullmatch('[0-9a-f]{64}', digest)
            if name in result:
                assert result[name] == digest, name
            result[name] = digest
    return result


hashes = parse_hashes(list((OUT / 'sha256sum').glob('*.stdout.txt')) +
                     [OUT / 'supplement-sha256sum.stdout.txt'])
objects = read('objects.json')
supplement = read('supplement-objects.json')
for path, row in {**objects, **supplement}.items():
    assert hashes[path] == row['sha256'], path
    for name in ['ldd', 'readelf'] if row.get('elf') else []:
        assert row[name]['returncode'] == 0, (path, name, row[name])
        assert row[name]['argv'][-1] == path
    for provider in row.get('resolved_providers', []):
        assert provider in objects or provider in supplement, provider
print('PASS: independent raw sha256sum matches every selected object and provider; raw ELF commands succeeded')
for record in read('distributions.json')['records'].values():
    for member in record.get('native_members', []):
        assert str(Path(member).resolve()) in objects, member
print('PASS: every reachable native member in the declared installed-package superset is digest-recorded')

for dataset, module_list in read('summary.json')['datasets'].items():
    capture = read('imports/' + dataset + '.command.json')
    assert capture['returncode'] == 0 and not capture['error'], capture
    imported = read('imports/' + dataset + '.stdout.txt')
    failures = [r for r in imported['records'] if r['status'] != 'imported']
    if dataset == 'ds1000':
        assert [r['module'] for r in failures] == ['gensim']
        assert "cannot import name 'triu' from 'scipy.linalg'" in failures[0]['traceback']
    else:
        assert not failures, failures
    for path in imported['native_paths']:
        assert str(Path(path).resolve()) in objects, path
for command in sorted(OUT.rglob('*.command.json')):
    capture = json.loads(command.read_text())
    assert capture['returncode'] == 0 and not capture.get('error'), (command, capture)
assert 'lo:' in read('host.json')['net_devices'] and not read('host.json')['net_routes'].strip()
assert not Path(read('cleanup.json')['import_scratch']).exists()
print('PASS: namespace, actual import maps, retained Gensim failure, bounded version launches and scratch cleanup')

for source in read('source-index.json'):
    if not source.get('fixture'):
        continue
    assert sha(ROOT / source['fixture']) == source['sha256'], source
    # Fresh installed/current source still matches the captured preimage.
    assert sha(Path(source['path'])) == source['sha256'], source
for site in read('source-sites.json'):
    lines = (ROOT / site['fixture_path']).read_text().splitlines()
    assert lines[site['line'] - 1] == site['text'], site
print('PASS: source preimages, current-source hashes and exact dependency line text')

# Expand every full file:line citation; shorthand :line references share the
# previous file citation. Preserve exact text as an independently checkable
# repository evidence locator, not merely an existence assertion.
report = (ROOT / 'reports/w-hostdeps-inventory.md').read_text()
locators = []
for match in re.finditer(r'(?P<path>(?:data/|eval/|source/)[A-Za-z0-9_./-]+):(?P<line>\d+)', report):
    name, number = match['path'], int(match['line'])
    p = OUT / name if name.startswith('source/') else ROOT / name
    assert p.is_file(), p
    lines = p.read_text().splitlines()
    assert number <= len(lines), (p, number)
    text = lines[number - 1]
    assert text.strip(), (p, number)
    locators.append({'path': str(p.relative_to(ROOT)), 'line': number, 'locator': text})
(OUT / 'evidence-locators.json').write_text(json.dumps(locators, indent=2, sort_keys=True) + '\n')

for path, digest in parse_hashes([OUT / 'runtime-resources-sha256sum.stdout.txt']).items():
    assert any(r['path'] == path and r.get('sha256') == digest for r in read('runtime-resources.json')), path
archive = read('jre-archive.json')
assert archive['matches_source_declaration']
assert archive['sha256'] == archive['source_sha_declaration']
assert parse_hashes([OUT / 'jre-archive-sha256sum.stdout.txt'])[archive['path']] == archive['sha256']
for artifact in read('jvm-artifacts.json'):
    assert hashes[artifact['path']] == artifact['sha256'], artifact
assert read('facts.json')['pinned_complete_native_surfaces'] == {'numerator': 0, 'denominator': 7}
assert len(set(objects) | set(supplement)) == read('facts.json')['unique_digest_recorded_files']
assert len(read('ds1000-eligible-imports.json')['eligible_external_import_roots']) == 9
known_digests = {r['sha256'] for r in list(objects.values()) + list(supplement.values())}
known_digests |= {r['sha256'] for r in read('jvm-artifacts.json')}
known_digests.add(archive['sha256'])
for digest in re.findall(r'\b[0-9a-f]{64}\b', report):
    assert digest in known_digests, digest
print('PASS: report locators, source-declared JRE archive pin, JAR/resource hashes and derived coverage')

before = read('registry-before.json')
after = json.loads((ROOT / 'docs/dataset-blockers.json').read_text())
expected = deepcopy(before)
b = next(r for r in expected['shared_blockers'] if r['id'] == 'scorer-offline-closure')
paragraph = report.split('## Exact registry observation - w-hostdeps\n\n', 1)[1].strip()
b['observed'] += ' ' + paragraph
b['evidence'] += [
 {'kind': 'repository', 'path': 'reports/w-hostdeps-inventory.md', 'locator': '## Exact registry observation - w-hostdeps'},
 {'kind': 'repository', 'path': 'tests/fixtures/hg_whostdeps/README.md', 'locator': '# w-hostdeps evidence packet'},
 {'kind': 'repository', 'path': 'docs/adapter-integration-journal.md',
  'locator': '## 2026-10-15 Native host dependency inventory - w-hostdeps'},
]
assert expected == after, 'registry changed outside the exact observed/evidence addition'
for blocker in after['shared_blockers']:
    for item in blocker['evidence']:
        if item['kind'] == 'repository':
            assert item['locator'] in (ROOT / item['path']).read_text(), item
print('PASS: only scorer-offline-closure observed/evidence appended; every blocker status/next_action, dataset/history and authorization unchanged')
print('PASS: every shared-blocker evidence locator appears VERBATIM in its referenced file')

manifest = OUT / 'SHA256SUMS'
if manifest.exists():
    entries = parse_hashes([manifest])
    for path, digest in entries.items():
        assert sha(OUT / path) == digest, path
    assert set(entries) == {str(p.relative_to(OUT)) for p in OUT.rglob('*')
                           if p.is_file() and p != manifest}, 'packet manifest coverage differs'
    print('PASS: complete fixture SHA256SUMS')
else:
    print('Manifest not generated yet; run final validation after generation')
