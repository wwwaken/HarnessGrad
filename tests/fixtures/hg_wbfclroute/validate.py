#!/usr/bin/env python3
"""Independently validate provenance bytes, refusal accounting and no closure drift."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
from compare import compare

P = Path(__file__).resolve().parent
R = P.parents[2]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load(name):
    return json.loads((P / name).read_text())

identity = load('identity.json')
for archive in identity['archives']:
    source = Path(archive['path'])
    if not source.is_absolute():
        source = R / source
    assert source.stat().st_size == archive['bytes'] and sha(source) == archive['sha256']
    with tarfile.open(source) as tar:
        for row in identity['sources']:
            if row['dataset'] != archive['dataset']:
                continue
            body = (P / row['path']).read_bytes()
            assert body == tar.extractfile(row['member']).read()
            assert hashlib.sha256(body).hexdigest() == row['sha256'] and len(body) == row['bytes']
            if 'original_path' in row:
                assert body == (R / row['original_path']).read_bytes()
for row in identity['local_sources']:
    assert sha(R / row['path']) == row['sha256']
assert (P / 'offline_exec.py').read_bytes() == (R / 'tests/fixtures/hg_woffscorer3/bfcl/offline_exec.py').read_bytes()
comparison = load('comparison.json')
assert compare() == comparison
source_hashes = {x['path']: x['sha256'] for x in identity['sources']}
commands = load('commands.json') + [load('ordered-import.command.json')]
removed = []
guarded = 0
for command in commands:
    assert command['cwd'] == str(R)
    name = command.get('name', 'ordered-import')
    expected_return = 1 if name.startswith('offline-wheel-') else 0
    assert command['returncode'] == expected_return, name
    if not any(x.endswith('/offline_exec.py') for x in command['argv']):
        assert name == 'pip-cache-list'
        continue
    guarded += 1
    stderr = (P / command['stderr']).read_text().splitlines()
    guard = json.loads(stderr[0])
    assert guard['production_runtime_observation'] is False
    assert all(x['errno'] == 1 and x['result'] == 'denied' for x in guard['socket_probes'].values())
    assert len(guard['socket_probes']) == 3
    assert 'io_uring_setup' in guard['denied_syscalls']
    assert guard['cpu_limit_seconds'] == 120 and guard['nofile_limit'] == 256
    assert sha(guard['interpreter']) == guard['interpreter_sha256']
    assert sha(guard['libseccomp']) == guard['libseccomp_sha256']
    assert json.loads(stderr[-1]) == {'blocked_external_dataset_reads': []}
    if name.startswith('offline-wheel-'):
        assert 'No matching distribution found' in '\n'.join(stderr)
        assert command['scratch_removed']
        continue
    result = load(command['stdout'])
    assert result['identity_sha256'] == sha(P / 'identity.json')
    assert result['inputs_sha256'] == sha(P / 'inputs.json')
    assert result['scratch_removed'] and not Path(result['scratch']).exists()
    removed.append(result['scratch'])
    assert {x['path']: x['sha256'] for x in result['source_checks']} == source_hashes
    for loaded in result['loaded_official_modules']:
        prefix = 'source/bfcl/' if loaded['module'].startswith('bfcl_eval') else 'source/chess/'
        module_path = loaded['module'].replace('.', '/')
        expected = source_hashes.get(prefix + module_path + '.py', source_hashes.get(prefix + module_path + '/__init__.py'))
        assert loaded['sha256'] == expected
    if name in {'bfcl-official', 'chess-board', 'chess-row'}:
        assert all(not x['measured'] and x['score'] is None and x['stage'].startswith('import_')
                   for x in result['rows'])
        assert not any(x['symbol'] in {'ast_checker', 'ast_file_runner', 'relevance_file_runner',
            'evaluate_task', 'evaluate_puzzle_from_board', 'evaluate_puzzle_from_pandas_row', 'main', 'runner'}
            for x in result['official_python_calls'])
    if name.endswith('-local'):
        assert result['dataset_cache_empty']
assert len(removed) == len(set(removed)), 'Every execution has fresh scratch'
# Only additive shared observation/evidence may differ from starting registry.
baseline_hash = load('baseline.json')['commands'][0]['stdout'].strip()
old = json.loads(subprocess.check_output(['git', 'show', baseline_hash + ':docs/dataset-blockers.json'], cwd=R))
current = json.loads((R / 'docs/dataset-blockers.json').read_text())
old_shared = next(x for x in old['shared_blockers'] if x['id'] == 'scorer-offline-closure')
current_shared = next(x for x in current['shared_blockers'] if x['id'] == 'scorer-offline-closure')
assert current_shared['observed'].startswith(old_shared['observed'])
assert current_shared['evidence'][:len(old_shared['evidence'])] == old_shared['evidence']
assert len(current_shared['evidence']) == len(old_shared['evidence']) + 1
current_shared['observed'] = old_shared['observed']
current_shared['evidence'] = old_shared['evidence']
assert current == old, 'Only scorer-offline-closure observed/evidence may change'
manifest_count = 0
for line in (P / 'SHA256SUMS').read_text().splitlines():
    digest, path = line.split('  ', 1)
    assert sha(P / path) == digest, path
    manifest_count += 1
print(json.dumps({'valid': True, 'source_members_rechecked': len(source_hashes),
    'manifest_members': manifest_count, 'guarded_processes': guarded,
    'removed_execution_scratch_roots': len(removed),
    'primary_controls': comparison['primary_controls'], 'numeric_pairs': comparison['primary_numeric_pairs'],
    'complete_dataset_routes_demonstrated': comparison['complete_dataset_routes_demonstrated'],
    'all_dataset_and_other_blocker_records_unchanged': True}, indent=2))
