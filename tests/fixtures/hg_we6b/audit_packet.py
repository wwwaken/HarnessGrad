"""Independent receipt assertions. Never launches a workload or scorer."""
import hashlib
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[3]
base = root / 'reports/w-e6b-evidence'
packets = [json.loads(p.read_text()) | {'packet': p.parent} for p in base.glob('w-e6b-*/summary.json')]
# The first packet's observer failed: reject its empty/tautological absence map.
usable = [s for s in packets if s['before_rescue_objects'] and not s.get('collector_exception')]
assert len(usable) == 1
s = usable[0]
packet = s['packet']
expected = {'mounted-' + m for m in ('timeout', 'missing-reward', 'malformed-reward', 'missing-evidence', 'writable-helper-timeout')}
expected |= {'snapshot-missing-argv', 'snapshot-staging-error', 'unsandboxed-normal',
             'unsandboxed-single-timeout', 'unsandboxed-missing-command', 'service-health-failure'}
assert set(s['cases']) == expected
assert s['jobs'] == 1 and s['model'] is None and s['endpoint'] is None
assert not s['rescue_containers'] and not s['native_service_stop_problems']
assert s['service_after_native_stop'] is None
assert s['network_after_native_stop']['returncode'] != 0
assert 'not found' in s['network_after_native_stop']['stderr']
assert all(v is None for v in s['before_rescue_objects'].values())
assert s['temporary_bind_sources_after'] and not any(s['temporary_bind_sources_after'].values())
assert s['final_process_observations'] and not any(v['same_starttime_present'] for v in s['final_process_observations'].values())

rows = {p.stem: [json.loads(line) for line in p.read_text().splitlines()] for p in packet.glob('*.jsonl')}
commands = [r for items in rows.values() for r in items if r['kind'] == 'command']
observed = {}
proc = {}
for records in rows.values():
    for r in records:
        if r['kind'] == 'proc-observation':
            proc[r['identity']] = r['raw']
        if r['kind'] == 'command' and r.get('argv', [])[:3] == ['docker', 'inspect', '--format'] and r.get('returncode') == 0:
            try:
                obj = json.loads(r['stdout'])
            except ValueError:
                continue
            if isinstance(obj, dict) and 'NanoCpus' in obj:
                observed[obj['Id']] = obj
assert set(observed) == set(s['before_rescue_objects'])
for cid, obj in observed.items():
    assert (obj['NanoCpus'], obj['Memory'], obj['PidsLimit']) == (2000000000, 4294967296, 1024)
    absent = [r for r in commands if r['argv'][:3] == ['docker', 'inspect', '--format'] and r['argv'][-1] == cid and r.get('returncode') != 0]
    assert absent and all('no such object:' in r['stderr'].lower() for r in absent)
    if obj['State']['Running']:
        cg = next(d['cgroup_files'] for d in proc.values() if any(cid in p for p in d['cgroup_files']))
        for name, value in (('cpu.max', '200000 100000\n'), ('memory.max', '4294967296\n'), ('pids.max', '1024\n')):
            assert any(cid in p and p.endswith('/' + name) and v == value for p, v in cg.items())

for name, result in s['cases'].items():
    assert all(v is None for v in result['native_after_objects'].values())
    assert not any(v['same_starttime_present'] for v in result['native_after_processes'].values())
    if name.startswith('mounted-'):
        assert len(result['live']) == 1
        obj = result['live'][0]
        assert obj['ReadonlyRootfs'] and '/tmp' in obj['Tmpfs']
        assert next(m for m in obj['Mounts'] if m['Destination'] == '/app')['RW'] == ('writable-helper' in name)
        if 'writable-helper' not in name:
            assert not next(m for m in obj['Mounts'] if m['Destination'] == '/recordings/recording')['RW']
            assert next(m for m in obj['Mounts'] if m['Destination'] == '/verifier')['RW']
        else:
            assert not any(m['Destination'].startswith('/recordings') for m in obj['Mounts'])
            assert any(m['Destination'].endswith('/.state') and m['RW'] for m in obj['Mounts'])
for name in ('mounted-timeout', 'mounted-writable-helper-timeout'):
    result = s['cases'][name]
    assert len(result['observed_proc_identities']) >= 2  # actual checker + sleeping child
    assert json.loads(result['probe_files']['started.json'])['child'] is not None
assert s['cases']['mounted-timeout']['verdict']['outcome'] == 'timeout'
assert s['cases']['mounted-timeout']['verdict']['unmeasured']
assert 'TimeoutExpired' in s['cases']['mounted-writable-helper-timeout']['exception']
assert s['cases']['mounted-missing-evidence']['verdict']['unmeasured']
assert not s['cases']['mounted-malformed-reward']['verdict']['passed']
assert not s['cases']['mounted-missing-reward']['verdict']['passed']
assert 'needs `argv`' in s['cases']['snapshot-missing-argv']['verdict']['detail']
assert 'does not exist' in s['cases']['snapshot-staging-error']['exception']
for name, started in (('snapshot-missing-argv', True), ('snapshot-staging-error', False)):
    assert any(r['argv'][:2] == ['docker', 'create'] for r in rows[name] if r['kind'] == 'command')
    assert any(r['argv'][:2] == ['docker', 'start'] for r in rows[name] if r['kind'] == 'command') == started
    assert any(r['argv'][:3] == ['docker', 'rm', '--force'] for r in rows[name] if r['kind'] == 'command')
assert s['cases']['unsandboxed-normal']['verdict']['passed']
waited = json.loads(s['cases']['unsandboxed-normal']['probe_files']['waited.json'])
assert waited['child_proc_absent_after_wait'] and waited['child_returncode'] == -15
assert s['cases']['unsandboxed-single-timeout']['verdict']['outcome'] == 'timeout'
assert 'does not exist' in s['cases']['unsandboxed-missing-command']['verdict']['detail']
health = s['cases']['service-health-failure']
assert 'not healthy' in health['exception'] and 'exit 7' in health['exception']
assert health['container_after_native_failure'] is None and health['network_after_native_failure']['returncode'] != 0

for rel, digest in s['source_hashes'].items():
    assert hashlib.sha256((root / rel).read_bytes()).hexdigest() == digest
for summary in packets:
    for name in ('collect.py', 'probe.py'):
        rel = 'tests/fixtures/hg_we6b/' + name
        assert hashlib.sha256((summary['packet'] / ('executed-' + name)).read_bytes()).hexdigest() == summary['source_hashes'][rel]

# Evaluate the same exact-object absence predicate against the retained live pre-fix
# receipt. Its failure proves this regression assertion discriminates the old defect.
before_path = root / 'reports/w-e6fix-evidence/w-e6fix-before-9d6a0ecfe85a41a69a6edf96146436dc/summary.json'
before = json.loads(before_path.read_text())
before_absent = all(v is None for v in before['modes']['timeout']['after_return'].values())
assert not before_absent

baseline = next(r['stdout'].strip() for r in rows['preflight']
                if r.get('argv') == ['git', 'rev-parse', 'HEAD'])
old = json.loads(subprocess.run(['git', 'show', baseline + ':docs/dataset-blockers.json'], cwd=root,
                               text=True, capture_output=True, check=True).stdout)
new = json.loads((root / 'docs/dataset-blockers.json').read_text())
assert old['datasets'] == new['datasets'] and old['review'] == new['review']
for left, right in zip(old['shared_blockers'], new['shared_blockers'], strict=True):
    if left['id'] != 'artifact-only-state-export':
        assert left == right
    else:
        assert {k: v for k, v in left.items() if k not in ('observed', 'evidence')} == {k: v for k, v in right.items() if k not in ('observed', 'evidence')}
        assert right['observed'].startswith(left['observed'])
        assert right['evidence'][:len(left['evidence'])] == left['evidence']

files = [p for p in base.rglob('*') if p.is_file()]
assert max(p.stat().st_size for p in files) < 1000000
print(json.dumps({'audit': 'PASS', 'packet': str(packet.relative_to(root)), 'live_cases': len(s['cases']),
                  'observed_owned_containers': len(observed), 'observed_pid_starttime_identities': len(proc),
                  'temporary_bind_sources_absent': len(s['temporary_bind_sources_after']),
                  'all_exact_objects_absent_before_rescue': True, 'rescues': len(s['rescue_containers']),
                  'historical_before_fix_same_absence_predicate': before_absent,
                  'registry_boundary': 'observed/evidence only; blockers unchanged',
                  'reviewed_baseline_commit': baseline,
                  'largest_evidence_file_bytes': max(p.stat().st_size for p in files)}, indent=2))
