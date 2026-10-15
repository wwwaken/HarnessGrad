"""Read-only audit of this packet. Does not repeat any runtime execution."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
PACKET = ROOT / 'reports/w-e6-evidence'
source = json.loads((PACKET / 'source-audit.json').read_text())
for name, expected in source['sources'].items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected['sha256'], name
registry = json.loads((ROOT / 'docs/dataset-blockers.json').read_text())
baseline = json.loads(subprocess.check_output(['git', 'show', 'bf917b3:docs/dataset-blockers.json'], cwd=ROOT))
assert registry['datasets'] == baseline['datasets']
assert registry['review'] == baseline['review']
for old, new in zip(baseline['shared_blockers'], registry['shared_blockers']):
    assert old['id'] == new['id']
    for field in ('family', 'status', 'next_action'):
        assert old[field] == new[field]

observations = {'source_files_verified': len(source['sources']), 'shared_dataset_count': source['shared_dataset_count'], 'docker': [], 'native': []}
for summary_path in sorted(PACKET.glob('w-e6-*/summary.json')):
    if summary_path.parent.name.startswith('w-e6-native-'):
        continue
    out = summary_path.parent
    summary = json.loads(summary_path.read_text())
    for name, digest in summary.get('executed_sources', {}).items():
        assert hashlib.sha256((out / ('executed-' + Path(name).name)).read_bytes()).hexdigest() == digest
    commands = []
    for meta in (out / 'commands').glob('*.json'):
        commands.append((meta, json.loads(meta.read_text())))
    samples = [json.loads(row)['inspect'] for row in (out / 'samples.jsonl').read_text().splitlines()]
    live = {obj['Id']: obj for obj in samples if obj['State']['Running']}
    roles = []
    for cid, obj in live.items():
        host = obj['HostConfig']
        assert (host['NanoCpus'], host['Memory'], host['PidsLimit']) == (2000000000, 4294967296, 1024)
        found_absent = [(p, m) for p, m in commands if m['argv'] == ['docker', 'inspect', cid] and m.get('returncode') == 1 and 'final-after-rescue' in p.name]
        assert found_absent, cid
        assert 'no such object' in found_absent[0][0].with_suffix('.stderr.txt').read_text().lower()
        roles.append({'id': cid, 'name': obj['Name'], 'image': obj['Image'], 'mounts': obj['Mounts'],
                      'observed_limits': {k: host.get(k) for k in ('NanoCpus', 'Memory', 'MemorySwap', 'PidsLimit', 'ReadonlyRootfs', 'Tmpfs', 'StorageOpt', 'Ulimits')},
                      'absence_command': str(found_absent[0][0].relative_to(ROOT))})
    if 'appworld' in summary['routes']:
        app = summary['routes']['appworld']
        assert app['modes']['normal']['passed'] is True
        assert app['modes']['timeout']['outcome'] == 'timeout'
        assert app['native_stop_problems'] and 'active endpoints' in app['native_stop_problems'][0]
        # The service is gone before collector rescue; exactly one verifier still runs.
        survivors = [cid for cid, state in summary['before_collector_rescue'].items() if state and state['Running']]
        assert len(survivors) == 1
        survivor = survivors[0]
        service_id = next(obj['Id'] for obj in live.values() if any(m['Destination'] == '/recordings/appworld' and m['RW'] for m in obj['Mounts']))
        assert summary['before_collector_rescue'][service_id] is None
        retained = live[survivor]
        assert any(m['Destination'] == '/recordings/appworld' and m['RW'] is False for m in retained['Mounts'])
        assert all(not state['same_starttime_present'] for state in summary['processes_after_cleanup'].values())
    for dataset in ('gaia', 'tau_bench'):
        if dataset not in summary['routes']:
            continue
        route = summary['routes'][dataset]
        assert route['modes']['normal']['passed'] is True
        assert route['modes']['timeout']['outcome'] == 'timeout'
        assert route['network_cleanup'] == []
        for mode in ('normal', 'timeout'):
            name = '/hg-verify-' + summary['run_id'] + '-' + dataset + '-' + mode
            cid = next(cid for cid, info in summary['known_containers'].items() if info['name'] == name)
            assert summary['before_collector_rescue'][cid] is None
    # Every fresh committed image has a real final absent-image command.
    for dataset, route in summary['routes'].items():
        if 'snapshot' in route:
            assert any(m['argv'] == ['docker', 'image', 'inspect', route['snapshot']]
                       and m.get('returncode') == 1 and 'snapshot-absent-after' in p.name
                       for p, m in commands)
    for path, state in summary['temporary_binds_after_native'].items():
        assert state == {'exists': False, 'is_mountpoint': False}, path
    proc_limits = []
    for p in (out / 'proc').glob('*.json'):
        d = json.loads(p.read_text())
        files = d.get('cgroup_files', {})
        if files:
            for suffix, expected in (('/cpu.max', '200000 100000\n'), ('/memory.max', '4294967296\n'), ('/pids.max', '1024\n')):
                assert any(str(key).endswith(suffix) and value == expected for key, value in files.items()), p
            proc_limits.append(str(p.relative_to(ROOT)))
    assert proc_limits
    observations['docker'].append({'packet': str(out.relative_to(ROOT)), 'roles': roles,
                   'cgroup_limit_samples': proc_limits, 'known_container_count': len(summary['known_containers']),
                   'native_service_cleanup_problems': summary['routes']['appworld']['native_stop_problems']})

for summary_path in sorted(PACKET.glob('w-e6-native-*/summary.json')):
    out = summary_path.parent
    summary = json.loads(summary_path.read_text())
    modes = summary['modes']
    for mode, result in modes.items():
        assert result['returncode'] == 0
        assert all(not state['same_starttime_present'] for state in result['process_identities_after_native'].values())
    normal = modes['normal']['verdict']
    if normal['passed']:
        obs = normal['evidence']['observation']
        assert obs['child_returncode'] == 0 and obs['child_proc_exists_after_wait'] is False
        assert modes['timeout']['verdict']['outcome'] == 'timeout'
        assert 'wait4' in (out / 'normal/syscalls.txt').read_text()
        assert 'SIGKILL' in (out / 'timeout/syscalls.txt').read_text()
        status = 'normal-and-timeout-observed'
    else:
        assert 'Read-only file system' in normal['detail']
        status = 'scratch-prerequisite-failed-before-child-launch; not measured failures'
    observations['native'].append({'packet': str(out.relative_to(ROOT)), 'status': status,
                  'captured_process_count': {mode: len(list((out / mode / 'proc').glob('*.json'))) for mode in modes}})
print(json.dumps(observations, indent=2))
