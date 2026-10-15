#!/usr/bin/env python3
"""Recheck retained outputs; no daemon, model, source mutation or network."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
runs = {p.parent.name: json.loads(p.read_bytes()) for p in HERE.glob('w-snapfix-*/summary.json')}
before = [k for k, v in runs.items() if v['mode'] == 'before']
after = [k for k, v in runs.items() if 'recomputed' in v]
assert len(before) == len(after) == 1
b, a = runs[before[0]], runs[after[0]]
assert b['foreign_refused'] is b['committed_file_preserved'] is False
assert b['checks_failed'] == 2 and b['checks_passed'] == 0
assert a['foreign_refused'] is a['committed_file_preserved'] is a['checker_observed_committed_bytes'] is True
assert a['checks_passed'] == 2 and a['checks_failed'] == 0
for name, summary in runs.items():
    directory = HERE / name
    for command in summary['commands']:
        stem = directory / command['stem']
        raw = json.loads(stem.with_suffix('.command.json').read_bytes())
        assert raw['returncode'] == command['returncode']
        assert raw['argv'] and raw['timeout_s'] <= 1800
        assert stem.with_suffix('.stdout.txt').is_file()
        assert stem.with_suffix('.stderr.txt').is_file()
    assert summary['snapshot'] != summary['base']
    assert all(c['absence_rc'] == 1 for c in summary['cleanup'])
    assert summary['model_gpu_endpoint_calls'] == summary['benchmark_scores'] == 0
for row in json.loads((HERE / 'input-packet-rehash.json').read_bytes()):
    assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256']

def raw(name, label):
    summary = runs[name]
    rows = [c for c in summary['commands'] if c['stem'].endswith('-' + label)]
    assert len(rows) == 1, label
    return (HERE / name / (rows[0]['stem'] + '.stdout.txt')).read_bytes()

assert (HERE / before[0] / 'before-start.txt').read_bytes() == b'committed-before-start\n'
assert (HERE / before[0] / 'after-start.txt').read_bytes() == b'changed-during-start\n'
assert (HERE / after[0] / 'before-start.txt').read_bytes() == b'committed-before-start\n'
assert (HERE / after[0] / 'after-start.txt').read_bytes() == b'committed-before-start\n'
assert raw(after[0], 'helper-exec') == b'committed-before-start\n'
info = json.loads(raw(after[0], 'verifier-after-start-inspect'))[0]
assert info['Image'] == info['Config']['Image'] == a['snapshot']
assert info['State']['Running'] is True
assert info['Path'].startswith('/hg-snapshot-idle-') and info['Path'].endswith('/busybox')
assert info['Args'] == ['sleep', '2147483647']
assert info['Config']['Healthcheck'] == {'Test': ['NONE']}
assert len(info['Mounts']) == 1 and info['Mounts'][0]['RW'] is False
assert info['HostConfig']['NetworkMode'] == a['run_id'] + '-service'
assert info['HostConfig']['Memory'] == 256 * 1024 * 1024
assert info['HostConfig']['NanoCpus'] == 1000000000 and info['HostConfig']['PidsLimit'] == 64
metadata = HERE / after[0] / 'fresh-metadata'
manifest_bytes = (metadata / 'manifest.json').read_bytes()
manifest = json.loads(manifest_bytes)
assert 'sha256:' + hashlib.sha256(manifest_bytes).hexdigest() == a['snapshot']
assert 'sha256:' + hashlib.sha256((metadata / 'config.json').read_bytes()).hexdigest() == manifest['config']['digest']
for relative, pin in a['source_sha256'].items():
    assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == pin
print(json.dumps(dict(valid=True, baseline_binding_checks_failed=2, final_binding_checks_passed=2,
                     all_capture_attempts_preserved=len(runs), cleanup_absence_observations=sum(len(s['cleanup']) for s in runs.values()),
                     retained_input_packet_unchanged=True, final_manifest_config_rehashed=True,
                     final_checker_observed_committed_bytes=True, layer_payloads_rechecked_now=False), sort_keys=True))
