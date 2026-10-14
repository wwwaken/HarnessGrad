#!/usr/bin/env python3
"""Independently audit packet integrity and the authorized registry/source scope."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = '9dab533'


def load(path):
    return json.loads(path.read_text())


def original(path):
    return subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)


listed = set()
for line in (HERE / 'SHA256SUMS').read_text().splitlines():
    digest, name = line.split('  ', 1)
    path = HERE / name
    assert path.is_file() and not path.is_symlink(), name
    assert name not in listed and hashlib.sha256(path.read_bytes()).hexdigest() == digest, name
    listed.add(name)
actual = {str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file()
          and '__pycache__' not in p.parts and p != HERE / 'SHA256SUMS'}
assert listed == actual, {'unlisted': sorted(actual-listed), 'missing': sorted(listed-actual)}

before = json.loads(original('docs/dataset-blockers.json'))
after = load(ROOT / 'docs/dataset-blockers.json')
assert {k:v for k,v in before.items() if k != 'shared_blockers'} == {
    k:v for k,v in after.items() if k != 'shared_blockers'}
changes = []
for b,a in zip(before['shared_blockers'], after['shared_blockers'], strict=True):
    if b == a:
        continue
    assert b['id'] == a['id'] == 'scorer-offline-closure'
    assert {k:v for k,v in b.items() if k not in {'observed','evidence'}} == {
        k:v for k,v in a.items() if k not in {'observed','evidence'}}
    assert a['observed'].startswith(b['observed'])
    assert a['evidence'][:len(b['evidence'])] == b['evidence']
    for item in a['evidence']:
        if item['kind'] == 'repository':
            assert item['locator'] in (ROOT / item['path']).read_text(), item
    changes.append(a['id'])
assert changes == ['scorer-offline-closure']
journal = (ROOT / 'docs/adapter-integration-journal.md').read_bytes()
assert journal.startswith(original('docs/adapter-integration-journal.md'))
assert journal.count(b'## Bounded official scorer extension - 2026-10-15 - w-offscorer2') == 1
changed = subprocess.check_output(['git','diff',BASE,'--name-only'],cwd=ROOT,text=True).splitlines()
allowed = {'docs/dataset-blockers.json','docs/adapter-integration-journal.md',
           'reports/w-offscorer2-coverage.md','reports/w-offscorer2-validation.txt',
           'reports/w-offscorer2-reasoning-gym.md','reports/w-offscorer2-bird-ds.md',
           'reports/w-offscorer2-spreadsheet.md','reports/w-offscorer2-worlds.md',
           'reports/w-offscorer2-spreadsheet-validation.txt',
           'reports/w-offscorer2-worlds-validation.txt'}
assert all(p in allowed or p.startswith('tests/fixtures/hg_woffscorer2/') for p in changed), changed
pins = load(HERE / 'local-source-pins.json')
assert pins['baseline'] == BASE
for item in pins['files']:
    body = (ROOT / item['path']).read_bytes()
    assert hashlib.sha256(body).hexdigest() == item['sha256']
    assert body == original(item['path'])

rg = HERE / 'reasoning_gym'
inputs = load(rg / 'inputs.json')
off, loc, comp = (load(rg / name) for name in ('official.json','local.json','compare.json'))
assert off['identity'] == loc['identity']
identity = off['identity']
assert hashlib.sha256((ROOT / identity['wheel_path']).read_bytes()).hexdigest() == identity['wheel_sha256']
provenance = ROOT / 'tests/fixtures/hg_wprov/reasoning_gym/responses'
for name,digest in identity['provenance_receipts'].items():
    assert hashlib.sha256((provenance / name).read_bytes()).hexdigest() == digest
assert hashlib.sha256(json.dumps(identity['installed_package_members'],sort_keys=True).encode()).hexdigest() == identity['package_manifest_sha256']
assert off['identity']['package_member_count'] == len(off['identity']['installed_package_members'])
for member in off['identity']['installed_package_members']:
    assert hashlib.sha256(Path(member['path']).read_bytes()).hexdigest() == member['sha256']
for out in (off,loc):
    assert out['inputs_sha256'] == hashlib.sha256((rg / 'inputs.json').read_bytes()).hexdigest()
    assert out['adapter_sha256'] == hashlib.sha256((ROOT/'data/datasets/reasoning_gym.py').read_bytes()).hexdigest()
assert len(inputs['cases']) == len(off['cases']) == len(loc['cases']) == comp['controlled_inputs']
agreements = divergences = errors = 0
for inp,o,l,c in zip(inputs['cases'],off['cases'],loc['cases'],comp['cases'],strict=True):
    assert inp['id'] == o['id'] == l['id'] == c['id']
    if o['error'] or l['error']:
        errors += 1
        assert c['agreement'] is None and o['score'] is None and l['score'] is None
    else:
        assert l['raw_return']['reward'] == l['score']
        assert c['agreement'] == (o['raw_return'] == l['score'])
        agreements += c['agreement']
        divergences += not c['agreement']
assert (agreements,divergences,errors) == (comp['agreements'],comp['divergences'],comp['nonnumeric_inputs'])
for receipt in rg.glob('*-offline.txt'):
    lines = receipt.read_text().splitlines()
    guard = json.loads(lines[0])
    assert all(v == {'errno':1,'result':'denied'} for v in guard['socket_probes'].values())
    assert guard['production_runtime_observation'] is False
    denied = json.loads(lines[-1])['blocked_external_dataset_reads']
    expected = ([{'event':'open', 'path':'/mnt/20t/xubuqiang/datasets/reasoning_gym/pool.jsonl'}]
                if receipt.name == 'local-offline.txt' else [])
    assert denied == expected

# Independently join the workbook raw returns, rather than trusting summary flags.
spread = HERE / 'spreadsheetbench'
sc = load(spread / 'comparison.json')
so, sl, sm, cli = (load(spread / (name + '.json')) for name in
                   ('official','local','local-main','official-cli'))
direct_agree = direct_errors = caller_agree = caller_unmeasured = 0
for o,l,m,u,c,d in zip(so['inputs'],sl['inputs'],sm['inputs'],cli['metrics'],
                       sc['direct_function']['per_input'],sc['caller_profile']['per_input'],strict=True):
    assert o['id'] == l['id'] == m['id'] == u['id'] == c['id'] == d['id']
    if 'return' in o and 'return' in l:
        match = bool(o['return'][0]) == bool(l['return'][0])
        assert c['agreement'] == match
        direct_agree += match
    else:
        direct_errors += 1
        assert c['agreement'] is None
    assert len(set(u['test_case_results'])) == 1
    if m['evidence']['measured']:
        match = m['reward'] == u['test_case_results'][0]
        assert d['agreement'] == match
        caller_agree += match
    else:
        caller_unmeasured += 1
        assert 'reward' not in m and d['agreement'] is None
assert direct_agree == sc['direct_function']['agreements']
assert direct_errors == sc['direct_function']['nonnumeric_inputs']
assert caller_agree == sc['caller_profile']['agreements']
assert caller_unmeasured == sc['caller_profile']['local_unmeasured_inputs']
formula = load(spread / 'local-formula-netns.json')['inputs'][0]
upstream = next(v for v in cli['metrics'] if v['id'] == formula['id'])
assert formula['evidence']['measured'] and formula['evidence']['recalculated']
assert formula['reward'] == sc['formula_netns_profile']['local_recalculated_reward']
assert upstream['test_case_results'][0] == sc['formula_netns_profile']['official_data_only_result']
assert int(formula['reward'] != upstream['test_case_results'][0]) == sc['formula_netns_profile']['divergences']

# Check the actual runtime guard receipts for both independent world paths.
worlds = HERE / 'worlds'
for side in ('official','local'):
    guard = json.loads((worlds / f'jericho-{side}-offline.txt').read_text().splitlines()[0])
    assert guard['production_runtime_observation'] is False
    assert all(v == {'errno':1,'result':'denied'} for v in guard['socket_probes'].values())
    guard = json.loads((worlds / f'scienceworld-{side}-offline.txt').read_text().splitlines()[0])
    assert guard['production_runtime_observation'] is False
    assert guard['parent_netns'] != guard['netns']
    assert len(guard['ipv4_routes'].splitlines()) == 1
    assert [v.split(':')[0].strip() for v in guard['network_devices'].splitlines()[2:]] == ['lo']
    assert guard['external_probe']['result'] == 'no route'
print(json.dumps({'verified_fixture_files':len(listed), 'registry_changes':changes,
                  'unchanged_source_files':len(pins['files']),
                  'dataset_blocker_changes':0, 'production_source_changes':0,
                  'journal_append_only':True, 'reasoning_gym_numeric_agreements':agreements,
                  'reasoning_gym_numeric_divergences':divergences,
                  'reasoning_gym_nonnumeric_inputs':errors,'production_authorized':False},indent=2))
