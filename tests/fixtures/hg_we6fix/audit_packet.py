"""Read-only validation of w-e6fix evidence and narrowly additive registry scope."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
PACKET = ROOT / 'reports/w-e6fix-evidence'


def load(path):
    return json.loads(path.read_text())


def packet(phase):
    paths = list(PACKET.glob('w-e6fix-' + phase + '-*/summary.json'))
    assert len(paths) == 1
    path = paths[0]
    summary = load(path)
    for name, digest in summary['sources'].items():
        saved = path.parent / ('source-' + Path(name).name)
        assert hashlib.sha256(saved.read_bytes()).hexdigest() == digest
    assert summary['model'] is summary['endpoint'] is None
    assert summary['benchmark_scoring'] is False
    assert summary['service_after_native_stop'] is None
    assert summary['final_service'] is None
    assert all(v is None for v in summary['final_verifiers'].values())
    assert summary['rescue_stop_problems'] == []
    assert summary['final_network']['returncode'] != 0
    assert 'not found' in summary['final_network']['stderr']
    normal = summary['modes']['normal']['verdict']
    timeout = summary['modes']['timeout']['verdict']
    assert normal['passed'] and normal['score'] == 1
    assert timeout['outcome'] == 'timeout' and timeout['unmeasured']
    assert not timeout['passed'] and 'score' not in timeout
    live = summary['modes']['timeout']['live_inspections']
    assert len(live) == 1
    obj = live[0]
    cfg = obj['HostConfig']
    assert cfg['ReadonlyRootfs'] and cfg['PidsLimit'] == 1024
    assert cfg['Memory'] == 4294967296 and cfg['NanoCpus'] == 2000000000
    mounts = {m['Destination']: m for m in obj['Mounts']}
    assert mounts['/recordings/recording']['RW'] is False
    assert mounts['/app']['RW'] is False and mounts['/verifier']['RW'] is True
    commands = [load(p) for p in path.parent.glob('[0-9]*.json')]
    for mode in summary['modes'].values():
        for seen in mode['live_inspections']:
            assert seen['Image'] == summary['service_before']['Image']
    if phase == 'before':
        assert summary['native_stop_problems']
        assert 'has active endpoints' in summary['native_stop_problems'][0]
        assert summary['network_after_native_stop']['returncode'] == 0
        leaked = summary['before_rescue'][obj['Id']]
        assert leaked['State']['Running']
        assert any(c['argv'] == ['docker', 'rm', '--force', obj['Id']] for c in commands)
    else:
        assert not summary['native_stop_problems']
        assert summary['network_after_native_stop']['returncode'] != 0
        assert 'not found' in summary['network_after_native_stop']['stderr']
        assert all(v is None for v in summary['before_rescue'].values())
        assert not any(c['argv'][:3] == ['docker', 'rm', '--force']
                       and c['argv'][3] in summary['before_rescue'] for c in commands)
        name = obj['Name'].lstrip('/')
        assert name.startswith('hg-run-')
        assert any(c['argv'] == ['docker', 'rm', '--force', name] for c in commands)
        assert obj['Id'] not in summary['network_after_native_stop']['stdout']
    return {'run_id': summary['run_id'], 'image': summary['image'],
            'timeout_verifier': obj['Id'], 'native_stop_problems': summary['native_stop_problems'],
            'network_removed_before_rescue': summary['network_after_native_stop']['returncode'] != 0}


before, after = packet('before'), packet('after')
assert before['run_id'] != after['run_id']
assert before['image'] == after['image']
old_source = ast.parse((PACKET / 'container-before.py').read_text())
new_source = ast.parse((ROOT / 'eval/containers/container.py').read_text())
definitions = lambda tree: {n.name: n for n in tree.body
                           if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
old_defs, new_defs = definitions(old_source), definitions(new_source)
assert old_defs.keys() == new_defs.keys()
assert [k for k in old_defs if ast.dump(old_defs[k]) != ast.dump(new_defs[k])] == ['run']
old_body, new_body = old_defs['run'].body, new_defs['run'].body
assert [ast.dump(n) for n in old_body[:-1]] == [ast.dump(n) for n in new_body[:len(old_body) - 1]]
assert ast.dump(old_body[-1]) == ast.dump(new_body[-1].body[0])
baseline_tests = (PACKET / 'tests-before.txt').read_text()
final_tests = (PACKET / 'tests-after.txt').read_text()
assert re.search(r'7 failed, 1 passed in ', baseline_tests)
assert re.search(r'8 passed in ', final_tests)
regressions = (PACKET / 'regressions.txt').read_text()
assert re.search(r'3 failed, 105 passed, 1 deselected in ', regressions)
baseline_network = (PACKET / 'network-baseline.txt').read_text()
assert re.search(r'3 failed in ', baseline_network)
failed = lambda text: set(re.findall(r'^FAILED ([^ ]+)', text, re.M))
assert failed(regressions) == failed(baseline_network)
old = load(PACKET / 'registry-before.json')
new = load(ROOT / 'docs/dataset-blockers.json')
old_shared = next(b for b in old['shared_blockers'] if b['id'] == 'artifact-only-state-export')
new_shared = next(b for b in new['shared_blockers'] if b['id'] == old_shared['id'])
assert new_shared['observed'].startswith(old_shared['observed'])
assert 'w-e6fix' in new_shared['observed'][len(old_shared['observed']):]
assert new_shared['evidence'][:len(old_shared['evidence'])] == old_shared['evidence']
added = new_shared['evidence'][len(old_shared['evidence']):]
assert added and all(e['path'].startswith(('reports/w-e6fix', 'tests/quality/test_w_e6fix')) for e in added)
for evidence in added:
    assert evidence['locator'] in (ROOT / evidence['path']).read_text()
restored = copy.deepcopy(new)
target = next(b for b in restored['shared_blockers'] if b['id'] == old_shared['id'])
target['observed'] = old_shared['observed']
target['evidence'] = old_shared['evidence']
assert restored == old, 'Only scoped observed/evidence additions are permitted'
print(json.dumps({'valid': True, 'before': before, 'after': after,
                  'focused_before': {'failed': 7, 'passed': 1},
                  'focused_after': {'passed': 8},
                  'regressions': {'passed': 105, 'preexisting_failed': 3, 'deselected_live': 1},
                  'source_scope': 'only run changed; original admission/command statements and return call identical',
                  'registry_scope': 'artifact-only-state-export observed/evidence additions only'}, indent=2))
