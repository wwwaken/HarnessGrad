"""Read-only validation of fresh receipts and unchanged authorization boundary."""
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
read = lambda p: json.loads(p.read_text())
normalize = lambda s: re.sub(r'[-_.]+', '-', s).lower()
inputs = read(HERE / 'inputs.json')
records = {a['key']: a for a in inputs['artifacts']}
target = read(HERE / 'target.json')
tags = {tag for literal in target['tags'] for tag in parse_tag(literal)}
independent = dict(line.split(maxsplit=1)[::-1] for line in (HERE / 'raw/wheel-sha256sum.stdout.txt').read_text().splitlines())
for key, record in records.items():
    path = Path(record['path'])
    assert path.stat().st_size == record['bytes']
    assert digest(path) == record['sha256'] == independent[str(path)]
    assert parse_wheel_filename(path.name)[3] & tags
    with zipfile.ZipFile(path) as archive:
        for member in record['metadata'].values():
            preimage = ROOT / member['path']
            assert archive.read(member['member']) == preimage.read_bytes()
            assert digest(preimage) == member['sha256']
    metadata = email.message_from_bytes((ROOT / record['metadata']['METADATA']['path']).read_bytes())
    assert normalize(metadata['Name']) == key and metadata['Version'] == record['version']
    assert metadata.get_all('Requires-Dist', []) == record['requires_dist']
    if record['requires_python']:
        assert SpecifierSet(record['requires_python']).contains('3.12.4')
    provenance = record['provenance']
    if provenance['kind'] == 'pypi-exact-version':
        index_path = HERE / 'index' / f"{key}-{record['version']}.json"
        http = read(index_path.with_name(index_path.name + '.http.json'))
        assert http['status'] == 200 and digest(index_path) == http['sha256']
        assert http['request_url'] == provenance['index_url']
        offered = next(a for a in read(index_path)['urls'] if a['filename'] == path.name)
        get = read(HERE / 'index' / (path.name + '.http.json'))
        assert get['status'] == 200 and get['request_url'] == provenance['url'] == offered['url']
        assert get['bytes'] == record['bytes'] == offered['size']
        assert get['sha256'] == record['sha256'] == offered['digests']['sha256'] == provenance['advertised_sha256']
        assert read(HERE / 'observed-candidates.json')[key]['version'] == record['version']
    else:
        assert digest(provenance['source']) == provenance['source_sha256'] == record['sha256']
        if provenance['kind'] == 'retained-local-build':
            stdout = ROOT / provenance['build_stdout']
            assert digest(stdout) == provenance['build_stdout_sha256']
            assert 'sha256=' + record['sha256'] in stdout.read_text()

retained_hashes = dict(line.split(maxsplit=1)[::-1] for line in
                      (HERE / 'raw/retained-target-sha256sum.stdout.txt').read_text().splitlines())
for record in read(HERE / 'retained-targets.json'):
    path = ROOT / record['path']
    assert digest(path) == retained_hashes[str(path)] == record['sha256'] == records[record['key']]['sha256']
    assert path.stat().st_size == record['bytes']
for record in read(HERE / 'acquisition-chain.json'):
    assert digest(ROOT / record['path']) == record['sha256'] == digest(ROOT / record['origin'])
    if 'advertised_sha256' in record:
        assert record['advertised_sha256'] == record['sha256']
planner = read(HERE / 'raw/planner-elf-members.stdout.txt')
assert planner['sha256'] == records['fast-downward-textworld']['sha256']
with zipfile.ZipFile(planner['wheel']) as archive:
    actual = []
    for member in archive.infolist():
        if not member.is_dir():
            with archive.open(member) as stream:
                if stream.read(4) == b'\x7fELF':
                    actual.append({'member': member.filename, 'bytes': member.file_size})
    assert actual == planner['ELF_members'] and actual
prior_records = {a['key']: a for a in read(ROOT / 'tests/fixtures/hg_wresolver2/inputs.json')['artifacts']}
for key, old in prior_records.items():
    assert records[key]['version'] == old['version'] and records[key]['sha256'] == old['sha256']

results = read(HERE / 'results-complete.json')
assert results == read(HERE / 'results.json') | read(HERE / 'results-retry.json')
assert results.keys() == inputs['profiles'].keys()
environment = default_environment()
assert environment['python_full_version'] == '3.12.4'
missing = {'alfworld': 'fast-downward-textworld', 'gsm8k': 'pyarrow', 'hotpotqa': 'pyarrow',
           'triviaqa': 'pyarrow', 'livecodebench': 'numpy'}
for name, result in results.items():
    prefix = result.get('capture_prefix', '')
    profile = HERE / 'profiles' / name
    assert (profile / 'roots.in').read_text().splitlines() == inputs['profiles'][name]
    constraints = (profile / 'constraints.txt').read_text().splitlines()
    assert set(constraints) == {f"{a['name']}=={a['version']}" for a in records.values()}
    for key, label in [(None, 'resolve-'), ('install', 'install-'), ('check', 'check-'), ('negative', 'negative-')]:
        actual = result if key is None else result[key]
        assert actual == read(HERE / 'raw' / (prefix + label + name + '.command.json')) or (
            key is None and all(actual[k] == v for k, v in read(HERE / 'raw' / (prefix + label + name + '.command.json')).items()))
    assert result['exit_code'] == result['install']['exit_code'] == result['check']['exit_code'] == 0
    for item in [result, result['install'], result['negative']]:
        assert '--no-deps' not in item['argv']
        for flag in ['--ignore-installed', '--no-index', '--no-cache-dir', '--only-binary=:all:']:
            assert flag in item['argv']
    assert '--dry-run' in result['argv'] and '--require-hashes' in result['install']['argv']
    assert 'include-system-site-packages = false' in (HERE / 'raw' / (prefix + name + '-pyvenv.cfg')).read_text()
    report = read(HERE / 'raw' / (prefix + name + '.pip-report.json'))
    selected = {normalize(e['metadata']['name']): e for e in report['install']}
    for key, entry in selected.items():
        record = records[key]
        assert entry['metadata']['version'] == record['version']
        assert entry['download_info']['archive_info']['hashes']['sha256'] == record['sha256']
        assert f"{record['name']}=={record['version']} --hash=sha256:{record['sha256']}" in (profile / 'resolved.lock').read_text()
    # Independent extras-aware traversal on pip's actual selection; do not drop
    # requested transitive extras as the old default-only traversal would do.
    pending = [Requirement(r) for r in inputs['profiles'][name]]
    extras, visited = {}, set()
    while pending:
        req = pending.pop(0)
        key = normalize(req.name)
        assert key in selected and req.specifier.contains(selected[key]['metadata']['version'])
        assert not req.url
        extras.setdefault(key, set()).update(req.extras)
        state = (key, tuple(sorted(extras[key])))
        if state in visited:
            continue
        visited.add(state)
        for literal in records[key]['requires_dist']:
            child = Requirement(literal)
            if any(child.marker is None or child.marker.evaluate(dict(environment, extra=e)) for e in [''] + sorted(extras[key])):
                pending.append(child)
    assert {k for k, e in visited} == selected.keys()
    if name == 'alfworld':
        assert 'pddl' in extras['textworld'] and 'fast-downward-textworld' in selected
    assert (HERE / 'raw' / (prefix + 'check-' + name + '.stdout.txt')).read_text().strip() == 'No broken requirements found.'
    assert result['negative']['exit_code'] == 1
    text = (HERE / 'raw' / (prefix + 'negative-' + name + '.stdout.txt')).read_text()
    assert f"The user requested (constraint) {missing[name]}=={records[missing[name]]['version']}" in text
    if name == 'alfworld':
        assert 'textworld[pddl] 1.7.0 depends on fast-downward-textworld' in text
    assert 'ResolutionImpossible' in (HERE / 'raw' / (prefix + 'negative-' + name + '.stderr.txt')).read_text()

for prefix in ['', 'retry-']:
    network = read(HERE / 'raw' / (prefix + 'network.json'))
    assert network['errno'] == 101 and not network['route'].splitlines()[1:]
    assert [item[1] for item in network['interfaces']] == ['lo']
    cleanup = read(HERE / 'raw' / (prefix + 'cleanup.json'))
    assert cleanup['removed'] and not Path(cleanup['directory']).exists()
    assert read(HERE / 'raw' / (prefix + 'runtime.json'))['executable_sha256'] == target['sha256']
assert 'FileExistsError' in (HERE / 'probe.stderr.txt').read_text()
assert 'fast-downward-textworld==20.6.4' in (HERE / 'attempts/obtain-attempt1.stderr.txt').read_text()
for record in read(HERE / 'source-audit.json')['sources']:
    preimage = ROOT / record['preimage']
    assert digest(preimage) == record['sha256']
    if '.whl:' in record['origin']:
        archive, member = record['origin'].split('.whl:', 1)
        with zipfile.ZipFile(archive + '.whl') as wheel:
            assert wheel.read(member) == preimage.read_bytes()
    else:
        assert digest(ROOT / record['origin']) == record['sha256']
    for line in record['excerpts']:
        assert preimage.read_text().splitlines()[line['line'] - 1] == line['text']
gap = read(HERE / 'gap-audit.json')
for record in gap['sources']:
    preimage = ROOT / record['preimage']
    assert digest(preimage) == record['sha256'] == digest(ROOT / record['source_path'])
    for line in record['excerpts'] + record['imports_ast']:
        assert preimage.read_text().splitlines()[line['line'] - 1] == line['text']
assert gap['datasets']['tau_bench']['third_party_absolute_import_records'] == []

before = read(HERE / 'registry-before.json')
after = read(ROOT / 'docs/dataset-blockers.json')
baseline = next(r for r in before['shared_blockers'] if r['id'] == 'scorer-offline-closure')
updated = next(r for r in after['shared_blockers'] if r['id'] == 'scorer-offline-closure')
observation = (HERE / 'observation.txt').read_text().strip()
assert updated['observed'] == baseline['observed'] + ' ' + observation
assert observation in (ROOT / 'reports/w-resolver3-payloads.md').read_text()
assert updated['evidence'][:len(baseline['evidence'])] == baseline['evidence']
assert len(updated['evidence']) == len(baseline['evidence']) + 3
comparison = copy.deepcopy(after)
row = next(r for r in comparison['shared_blockers'] if r['id'] == 'scorer-offline-closure')
row['observed'], row['evidence'] = baseline['observed'], baseline['evidence']
assert comparison == before, 'Only additive shared observation/evidence may change'
for row in after['shared_blockers'] + after['datasets']:
    for evidence in row.get('evidence', []):
        if evidence['kind'] == 'repository':
            assert evidence['locator'] in (ROOT / evidence['path']).read_text()
summary = read(HERE / 'summary.json')
coverage = read(HERE / 'dataset-coverage.json')
prior = read(ROOT / 'tests/fixtures/hg_wresolver2/summary.json')
assert summary['new_profiles_resolved'] == len(results)
assert summary['bounded_profiles_resolved'] == prior['bounded_profiles_resolved'] + len(results)
assert summary['bounded_profiles'] == prior['bounded_profiles'] + len(results)
assert summary['complete_nonempty_python_profiles'] == sum(r['status'] == 'resolved-full-python-metadata-profile' for r in coverage)
assert summary['shared_datasets'] == len(coverage) == sum('scorer-offline-closure' in r['shared_blockers'] for r in before['datasets'])
assert summary['not_demonstrated_at_dataset_profile_scope'] == summary['shared_datasets'] - summary['complete_nonempty_python_profiles']
assert summary['no_third_party_payload'] == sum(r['status'].startswith('no-third-party') for r in coverage)
assert all(edge.get('satisfied', True) for edge in read(HERE / 'graph.json'))
report_text = (ROOT / 'reports/w-resolver3-payloads.md').read_text()
known_hashes = {r['sha256'] for r in records.values()} | {r['sha256'] for r in read(HERE / 'acquisition-chain.json')}
assert set(re.findall(r'\b[a-f0-9]{64}\b', report_text)) <= known_hashes
for path, number in set(re.findall(r'`([^`\n]+):(\d+)`', report_text)):
    assert (ROOT / path).read_text().splitlines()[int(number) - 1].strip()
assert f"**{summary['bounded_profiles_resolved']}/{summary['bounded_profiles']} bounded profiles and {summary['complete_nonempty_python_profiles']}/{summary['shared_datasets']} complete nonempty dataset Python profiles**" in report_text
if args.seal:
    entries = [p for p in sorted(HERE.rglob('*')) if p.is_file()
               and p.name != 'SHA256SUMS' and '__pycache__' not in p.parts]
    (HERE / 'SHA256SUMS').write_text(''.join(f'{digest(p)}  {p.relative_to(HERE)}\n' for p in entries))
else:
    sealed = set()
    for line in (HERE / 'SHA256SUMS').read_text().splitlines():
        expected, rel = line.split(maxsplit=1)
        assert digest(HERE / rel) == expected, rel
        sealed.add(rel)
    assert sealed == {str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file()
                      and p.name != 'SHA256SUMS' and '__pycache__' not in p.parts}
print(json.dumps({'valid': True, 'candidate_wheels': len(records),
      'fresh_profiles': len(results), 'missing_wheel_refusals': len(results),
      'bounded_coverage': f"{summary['bounded_profiles_resolved']}/{summary['bounded_profiles']}",
      'complete_nonempty_python_coverage': f"{summary['complete_nonempty_python_profiles']}/{summary['shared_datasets']}",
      'production_authorized': False}, sort_keys=True))
