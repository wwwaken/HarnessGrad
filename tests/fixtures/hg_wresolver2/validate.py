"""Read-only receipt audit; --seal creates a checksum manifest after collection."""
import argparse
import copy
import email
import json
from pathlib import Path
import re
import zipfile

from packaging.markers import default_environment
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.tags import parse_tag
from packaging.utils import parse_wheel_filename

from common import HERE, ROOT, digest

parser = argparse.ArgumentParser()
parser.add_argument('--seal', action='store_true')
args = parser.parse_args()
read = lambda path: json.loads(path.read_text())
normalize = lambda name: re.sub(r'[-_.]+', '-', name).lower()
inputs = read(HERE / 'inputs.json')
target = read(HERE / 'target.json')
tags = {tag for literal in target['tags'] for tag in parse_tag(literal)}
records = {r['key']: r for r in inputs['artifacts']}
independent = dict(line.split(maxsplit=1)[::-1] for line in (HERE / 'raw/wheel-sha256sum.stdout.txt').read_text().splitlines())
for key, record in records.items():
    path = Path(record['path'])
    assert path.stat().st_size == record['bytes']
    assert digest(path) == record['sha256'] == independent[str(path)]
    assert parse_wheel_filename(path.name)[3] & tags
    with zipfile.ZipFile(path) as archive:
        for value in record['metadata'].values():
            preimage = ROOT / value['path']
            assert archive.read(value['member']) == preimage.read_bytes()
            assert digest(preimage) == value['sha256']
    meta = email.message_from_bytes((ROOT / record['metadata']['METADATA']['path']).read_bytes())
    assert normalize(meta['Name']) == key and meta['Version'] == record['version']
    assert meta.get_all('Requires-Dist', []) == record['requires_dist']
    if record['requires_python']:
        assert SpecifierSet(record['requires_python']).contains('3.12.4')
    provenance = record['provenance']
    if provenance['kind'] == 'pypi-exact-version':
        index_path = HERE / 'index' / f"{key}-{record['version']}.json"
        http = read(index_path.with_name(index_path.name + '.http.json'))
        assert http['status'] == 200 and digest(index_path) == http['sha256']
        assert http['request_url'] == provenance['index_url']
        offered = next(r for r in read(index_path)['urls'] if r['filename'] == path.name)
        assert offered['url'] == provenance['url']
        assert offered['digests']['sha256'] == record['sha256'] == provenance['advertised_sha256']
        get = read(HERE / 'index' / (path.name + '.http.json'))
        assert get['status'] == 200 and get['request_url'] == provenance['url']
        assert get['sha256'] == record['sha256'] and get['bytes'] == record['bytes']
        assert read(HERE / 'observed-candidates.json')[key]['version'] == record['version']
    else:
        assert digest(provenance['source']) == provenance['source_sha256'] == record['sha256']
retained_hashes = dict(line.split(maxsplit=1)[::-1] for line in
                      (HERE / 'raw/retained-target-sha256sum.stdout.txt').read_text().splitlines())
retained = read(HERE / 'retained-targets.json')
assert {r['key'] for r in retained} == {'spacy', 'contourpy', 'et-xmlfile'}
for record in retained:
    path = ROOT / record['path']
    assert path.stat().st_size == record['bytes']
    assert digest(path) == retained_hashes[str(path)] == record['sha256'] == records[record['key']]['sha256']

environment = default_environment()
environment['extra'] = ''
assert environment['python_full_version'] == '3.12.4'
results = read(HERE / 'results.json')
for name, result in results.items():
    profile = HERE / 'profiles' / name
    prior = ROOT / 'tests/fixtures/hg_wresolver/profiles' / name
    assert (profile / 'roots.in').read_bytes() == (prior / 'roots.in').read_bytes()
    assert (profile / 'constraints.txt').read_bytes().startswith((prior / 'constraints.txt').read_bytes())
    assert result['exit_code'] == result['install']['exit_code'] == result['check']['exit_code'] == 0
    for key in ['argv']:
        assert '--no-deps' not in result[key]
        for flag in ['--ignore-installed', '--no-index', '--no-cache-dir', '--only-binary=:all:', '--dry-run']:
            assert flag in result[key]
    assert '--require-hashes' in result['install']['argv'] and '--no-deps' not in result['install']['argv']
    assert 'include-system-site-packages = false' in (HERE / 'raw' / (name + '-pyvenv.cfg')).read_text()
    report = read(HERE / 'raw' / (name + '.pip-report.json'))
    selected = {normalize(e['metadata']['name']): e for e in report['install']}
    lock = (profile / 'resolved.lock').read_text()
    for key, entry in selected.items():
        record = records[key]
        assert entry['metadata']['version'] == record['version']
        assert entry['download_info']['archive_info']['hashes']['sha256'] == record['sha256']
        assert f"{record['name']}=={record['version']} --hash=sha256:{record['sha256']}" in lock
        for literal in record['requires_dist']:
            req = Requirement(literal)
            if req.marker and not req.marker.evaluate(environment):
                continue
            assert not req.extras and not req.url
            assert req.specifier.contains(selected[normalize(req.name)]['metadata']['version'])
    assert (HERE / 'raw' / ('check-' + name + '.stdout.txt')).read_text().strip() == 'No broken requirements found.'
    assert result['negative']['exit_code'] == 1
    missing = {'jericho': 'spacy', 'reasoning_gym': 'contourpy', 'spreadsheetbench': 'et-xmlfile'}[name]
    refusal = (HERE / 'raw' / ('negative-' + name + '.stdout.txt')).read_text()
    assert f'depends on {missing}' in refusal
    assert f'The user requested (constraint) {missing}=={records[missing]["version"]}' in refusal
    assert 'ResolutionImpossible' in (HERE / 'raw' / ('negative-' + name + '.stderr.txt')).read_text()

network = read(HERE / 'raw/network.json')
assert network['errno'] == 101 and not network['route'].splitlines()[1:]
assert [entry[1] for entry in network['interfaces']] == ['lo']
cleanup = read(HERE / 'raw/cleanup.json')
assert cleanup['removed'] and not Path(cleanup['directory']).exists()
assert read(HERE / 'raw/runtime.json')['executable_sha256'] == target['sha256']
source = read(HERE / 'source-audit.json')
for record in source['sources']:
    preimage = ROOT / record['preimage']
    assert digest(preimage) == record['sha256']
    if '.whl:' in record['origin']:
        archive_path, member = record['origin'].split('.whl:', 1)
        with zipfile.ZipFile(archive_path + '.whl') as archive:
            assert archive.read(member) == preimage.read_bytes()
    else:
        assert digest(ROOT / record['origin']) == record['sha256']
for wheel in source['wheels']:
    assert digest(wheel['path']) == wheel['sha256']
    with zipfile.ZipFile(wheel['path']) as archive:
        for member in wheel['members']:
            assert digest(ROOT / member['preimage']) == member['sha256']
            assert archive.read(member['origin'].split('.whl:', 1)[1]) == (ROOT / member['preimage']).read_bytes()


def check_locators(value):
    if isinstance(value, dict):
        if 'preimage' in value and 'line' in value:
            lines = (ROOT / value['preimage']).read_text().splitlines()
            assert lines[value['line'] - 1] == value['text']
        for child in value.values():
            check_locators(child)
    elif isinstance(value, list):
        for child in value:
            check_locators(child)


check_locators(source)
report_text = (ROOT / 'reports/w-resolver2-payloads.md').read_text()
for path, number in sorted(set(re.findall(r'`([^`\n]+):(\d+)`', report_text))):
    lines = (ROOT / path).read_text().splitlines()
    assert lines[int(number) - 1].strip(), (path, number)
before = read(HERE / 'registry-before.json')
after = read(ROOT / 'docs/dataset-blockers.json')
baseline = next(r for r in before['shared_blockers'] if r['id'] == 'scorer-offline-closure')
updated = next(r for r in after['shared_blockers'] if r['id'] == 'scorer-offline-closure')
observation = (HERE / 'observation.txt').read_text().strip()
assert updated['observed'] == baseline['observed'] + ' ' + observation
assert observation in (ROOT / 'reports/w-resolver2-payloads.md').read_text()
assert updated['evidence'][:len(baseline['evidence'])] == baseline['evidence']
assert len(updated['evidence']) == len(baseline['evidence']) + 3
comparison = copy.deepcopy(after)
row = next(r for r in comparison['shared_blockers'] if r['id'] == 'scorer-offline-closure')
row['observed'], row['evidence'] = baseline['observed'], baseline['evidence']
assert comparison == before, 'Only additive observed/evidence at this shared scope may change'
for row in after['shared_blockers'] + after['datasets']:
    for evidence in row.get('evidence', []):
        if evidence['kind'] == 'repository':
            assert evidence['locator'] in (ROOT / evidence['path']).read_text()
summary = read(HERE / 'summary.json')
coverage = read(HERE / 'dataset-coverage.json')
assert summary['new_profiles_resolved'] == sum(r['exit_code'] == 0 for r in results.values())
assert summary['complete_nonempty_python_profiles'] == sum(r['status'] == 'resolved-full-python-metadata-profile' for r in coverage)
assert summary['shared_datasets'] == len(coverage) == sum('scorer-offline-closure' in r['shared_blockers'] for r in before['datasets'])
assert summary['not_demonstrated_at_dataset_profile_scope'] == summary['shared_datasets'] - summary['complete_nonempty_python_profiles']
assert summary['bounded_profiles_resolved'] == read(ROOT / 'tests/fixtures/hg_wresolver/summary.json')['bounded_profiles_resolved'] + summary['new_profiles_resolved']
assert all(edge.get('satisfied', True) for edge in read(HERE / 'graph.json'))
if args.seal:
    entries = [p for p in sorted(HERE.rglob('*')) if p.is_file()
               and p.name != 'SHA256SUMS' and '__pycache__' not in p.parts]
    (HERE / 'SHA256SUMS').write_text(''.join(f'{digest(p)}  {p.relative_to(HERE)}\n' for p in entries))
else:
    for line in (HERE / 'SHA256SUMS').read_text().splitlines():
        expected, rel = line.split(maxsplit=1)
        assert digest(HERE / rel) == expected, rel
print(json.dumps({'valid': True, 'candidate_wheels': len(records),
                  'fresh_http_artifacts': sum(r['provenance']['kind'] == 'pypi-exact-version' for r in records.values()),
                  'new_profiles_resolved': summary['new_profiles_resolved'],
                  'bounded_coverage': f"{summary['bounded_profiles_resolved']}/{summary['bounded_profiles']}",
                  'complete_nonempty_python_coverage': f"{summary['complete_nonempty_python_profiles']}/{summary['shared_datasets']}",
                  'production_authorized': False}, sort_keys=True))
