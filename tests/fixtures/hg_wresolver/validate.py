"""Read-only packet verification; --seal binds new citation/checksum records."""
import argparse
import copy
import email
import hashlib
import json
from pathlib import Path
import re
import zipfile

from packaging.markers import default_environment
from packaging.requirements import Requirement
from packaging.tags import parse_tag, sys_tags
from common import HERE, ROOT, digest, save

parser = argparse.ArgumentParser()
parser.add_argument('--seal', action='store_true')
args = parser.parse_args()
read = lambda p: json.loads(Path(p).read_text())
inputs = read(HERE / 'inputs.json')
normalize = lambda s: re.sub(r'[-_.]+', '-', s).lower()
artifacts = {r['key']: r for r in inputs['artifacts']}
independent = dict(line.split(maxsplit=1)[::-1] for line in
                   (HERE / 'raw/wheel-sha256sum.stdout.txt').read_text().splitlines())
tags = set(sys_tags())
for r in artifacts.values():
    p = Path(r['path'])
    assert p.stat().st_size == r['bytes']
    assert digest(p) == r['sha256'] == r['prior_sha256'] == independent[str(p)]
    assert digest(r['provided_path']) == r['sha256']
    with zipfile.ZipFile(p) as z:
        for suffix, record in r['metadata'].items():
            assert z.read(record['member']) == (ROOT / record['path']).read_bytes()
            assert digest(ROOT / record['path']) == record['sha256']
    meta = email.message_from_bytes((ROOT / r['metadata']['METADATA']['path']).read_bytes())
    assert meta['Version'] == r['version'] and normalize(meta['Name']) == r['key']
    wheel = (ROOT / r['metadata']['WHEEL']['path']).read_text()
    wheel_tags = {tag for line in wheel.splitlines() if line.startswith('Tag: ')
                  for tag in parse_tag(line[5:])}
    assert wheel_tags & tags
independent_uv = dict(line.split(maxsplit=1)[::-1] for line in
                      (HERE / 'raw/uvx-sha256sum.stdout.txt').read_text().splitlines())
for r in inputs['uvx_artifacts']:
    p = ROOT / r['path']
    assert p.stat().st_size == r['bytes'] and digest(p) == r['sha256'] == independent_uv[str(p)]
native = read(HERE / 'native-results.json')
env = default_environment()
env['extra'] = ''
for name in inputs['profiles']:
    result = native[name]
    assert '--no-deps' not in result['argv']
    for required in ['--ignore-installed', '--no-index', '--no-cache-dir', '--only-binary=:all:', '--dry-run']:
        assert required in result['argv']
    if result['exit_code'] != 0:
        assert 'No matching distribution found' in (HERE / f'raw/resolve-{name}.stderr.txt').read_text()
        continue
    report = read(HERE / f'raw/{name}.pip-report.json')
    selected = {normalize(r['metadata']['name']): r for r in report['install']}
    for key, entry in selected.items():
        artifact = artifacts[key]
        assert entry['metadata']['version'] == artifact['version']
        assert entry['download_info']['archive_info']['hashes']['sha256'] == artifact['sha256']
        for literal in artifact['requires_dist']:
            requirement = Requirement(literal)
            if requirement.marker and not requirement.marker.evaluate(env):
                continue
            dependency = selected[normalize(requirement.name)]
            assert requirement.specifier.contains(dependency['metadata']['version'])
    assert result['install']['exit_code'] == result['pip_check']['exit_code'] == 0
    assert '--require-hashes' in result['install']['argv']
    assert '--no-deps' not in result['install']['argv']
    assert (HERE / f'raw/check-{name}.stdout.txt').read_text().strip() == 'No broken requirements found.'
assert native['negative-missing-py4j']['exit_code'] != 0
assert 'py4j' in (HERE / 'raw/negative-missing-py4j.stderr.txt').read_text()
for suffix in ['native', 'supplement']:
    network = read(HERE / f'raw/{suffix}-network.json')
    assert network['errno'] == 101 and not network['route'].splitlines()[1:]
    assert [r[1] for r in network['interfaces']] == ['lo']
    assert read(HERE / f'raw/{suffix}-cleanup.json')['removed'] is True
supplement = read(HERE / 'supplement-results.json')
assert all(r['exit_code'] != 0 for r in supplement.values())
mkl = read(HERE / 'mkl-release-audit.json')
assert digest(ROOT / mkl['source']) == mkl['source_sha256']
assert mkl['compatible_wheels'] == 0 and mkl['sdists'] == 0
tb = read(HERE / 'tb3/result.json')
assert tb['compile']['exit_code'] == tb['uvx']['exit_code'] == 0 and tb['negative']['exit_code'] != 0
assert '--no-deps' not in tb['compile']['argv'] + tb['uvx']['argv']
network = read(HERE / 'tb3/network.json')
assert network['errno'] == 101 and not network['route'].splitlines()[1:]
assert [r[1] for r in network['interfaces']] == ['lo']
assert (HERE / 'tb3/uvx-version.stdout.txt').read_text().strip() == 'pytest 8.4.1'
selected_tb = dict(read(HERE / 'tb3/selected-distributions.stdout.txt'))
lock = (HERE / 'tb3/resolved.lock').read_text()
for p in (ROOT / 'tests/fixtures/hg_wuvx/artifacts/wheels').glob('*.whl'):
    with zipfile.ZipFile(p) as z:
        meta = email.message_from_bytes(z.read(next(n for n in z.namelist() if n.endswith('.dist-info/METADATA'))))
    assert selected_tb[meta['Name']] == meta['Version']
    assert normalize(meta['Name']) + '==' + meta['Version'] in lock
    assert '--hash=sha256:' + digest(p) in lock
for attempt in ['tb', 'tb2', 'tb3']:
    assert read(HERE / f'raw/{attempt}-container-cleanup.command.json')['exit_code'] == 0
    assert (HERE / f'raw/{attempt}-container-absence.stdout.txt').read_text() == ''
container = read(HERE / 'raw/tb3-container-inspect.stdout.txt')[0]
assert container['State']['ExitCode'] == 0 and not container['State']['OOMKilled']
config = container['HostConfig']
assert config['NetworkMode'] == 'none' and config['ReadonlyRootfs'] is True
assert config['NanoCpus'] == 1000000000 and config['Memory'] == 536870912 and config['PidsLimit'] == 64
assert config['CapDrop'] == ['ALL']
assert all(not r['IPAddress'] and not r['Gateway'] for r in container['NetworkSettings']['Networks'].values())
source_records = read(HERE / 'source-inventory.json')
for record in source_records:
    assert digest(record['path']) == digest(ROOT / record['preimage']) == record['sha256']
    lines = (ROOT / record['preimage']).read_text().splitlines()
    assert all(lines[r['line'] - 1] == r['text'] for r in record['imports'])
for row in read(HERE / 'tb-task-source-audit.json'):
    assert digest(ROOT / row['path']) == digest(row['external_path']) == row['sha256'] == row['external_sha256']
before = read(HERE / 'registry-before.json')
after = read(ROOT / 'docs/dataset-blockers.json')
baseline = next(r for r in before['shared_blockers'] if r['id'] == 'scorer-offline-closure')
updated = next(r for r in after['shared_blockers'] if r['id'] == 'scorer-offline-closure')
assert updated['observed'].startswith(baseline['observed']) and updated['observed'] != baseline['observed']
assert updated['evidence'][:len(baseline['evidence'])] == baseline['evidence']
comparison = copy.deepcopy(after)
row = next(r for r in comparison['shared_blockers'] if r['id'] == 'scorer-offline-closure')
row['observed'], row['evidence'] = baseline['observed'], baseline['evidence']
assert comparison == before, 'Only the exact shared observed/evidence scope may change'
report = (ROOT / 'reports/w-resolver-payloads.md').read_text()
locators = []
for path, number in sorted(set(re.findall(r'`([^`\n]+):(\d+)`', report))):
    p = Path(path) if Path(path).is_absolute() else ROOT / path
    text = p.read_text().splitlines()[int(number) - 1]
    assert text.strip(), (path, number)
    locators.append({'path': path, 'line': int(number), 'locator': text})
if args.seal:
    save(HERE / 'evidence-locators.json', locators)
else:
    assert read(HERE / 'evidence-locators.json') == locators
for row in after['shared_blockers']:
    for evidence in row['evidence']:
        if evidence['kind'] == 'repository':
            assert evidence['locator'] in (ROOT / evidence['path']).read_text()
summary = read(HERE / 'summary.json')
assert summary['bounded_profiles_resolved'] == sum(native[n]['exit_code'] == 0 for n in inputs['profiles']) + 1
assert summary['bounded_profiles_failed'] == sum(native[n]['exit_code'] != 0 for n in inputs['profiles'])
assert summary['complete_nonempty_python_profiles'] == sum(native[n]['exit_code'] == 0 for n in inputs['profiles'])
assert summary['shared_datasets'] == len(read(HERE / 'dataset-coverage.json'))
assert summary['no_third_party_payload'] == sum(r['status'].startswith('no-third-party') for r in read(HERE / 'dataset-coverage.json'))
assert summary['tb_task_sources'] == len(read(HERE / 'tb-task-source-audit.json'))
if args.seal:
    entries = [p for p in sorted(HERE.rglob('*')) if p.is_file()
               and p.name != 'SHA256SUMS' and '__pycache__' not in p.parts]
    (HERE / 'SHA256SUMS').write_text(''.join(f'{digest(p)}  {p.relative_to(HERE)}\n' for p in entries))
else:
    for line in (HERE / 'SHA256SUMS').read_text().splitlines():
        expected, rel = line.split(maxsplit=1)
        assert digest(HERE / rel) == expected, rel
print(json.dumps({'valid': True, 'candidate_wheels': len(artifacts),
     'source_files': len(source_records), 'source_citations': len(locators),
     'bounded_profiles_resolved': summary['bounded_profiles_resolved'],
     'bounded_profiles': summary['bounded_datasets'],
     'complete_nonempty_python_profiles': summary['complete_nonempty_python_profiles'],
     'shared_datasets': summary['shared_datasets'], 'production_authorized': False}, sort_keys=True))
