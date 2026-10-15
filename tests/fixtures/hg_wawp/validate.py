"""Verify retained released bytes, input identity, real executions, and cleanup receipts."""
import hashlib
import json
from pathlib import Path
import subprocess

F = Path(__file__).resolve().parent
ROOT = F.parents[2]
load = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
inv = load(F/'inventory.json')
pins = load(F/'selected-byte-pins.json')
summary = load(F/'comparison.json')
rows = summary['comparisons']
assert inv['evaluator_count'] == len(inv['evaluators']) == inv['evaluate_function_count']
assert sum(inv['split_counts'].values()) == inv['evaluator_count']
assert inv['image_identical_evaluators'] == inv['evaluator_count']
assert len({p['task_id'] for p in inv['evaluators']}) == inv['evaluator_count']
selected = load(F/'inputs.json')
by_id = {p['task_id']: p for p in inv['evaluators']}
for pin in load(F/'local-source-pins.json')['files']:
    assert sha(ROOT/pin['path']) == pin['sha256'], pin
for pin in pins['members']:
    assert pin['sha256'] == pin['image_sha256'] == pin['host_sha256'], pin
    path = (F/'selected-root'/pin['member']) if not pin['member'].startswith('data/base_dbs/') else Path(pin['host_path'])
    assert sha(path) == pin['sha256'], pin
assert pins['count'] == len(pins['members'])
assert pins['bytes'] == sum(p['bytes'] for p in pins['members'])
assert hashlib.sha256(Path(inv['bundle_path']).read_bytes()).hexdigest() == inv['bundle_sha256']
call_counts = {'official': 0, 'local': 0}
for case in selected['cases']:
    assert case['source_split'] in ['train', 'dev']
    log = F/'inputs'/(case['id']+'.jsonl')
    assert [json.loads(line) for line in log.read_text().splitlines()] == case['calls']
    assert by_id[case['task_id']]['selected']
    for mode in ['official', 'local']:
        p = F/'outputs'/case['id']/mode/'parsed.json'
        result = load(p)
        assert result['container_exit'] == result['docker_attach_exit'] == 0, p
        assert result['measured'] is True and result['oom_killed'] is False, p
        assert len(result['receipts']) == 1, p
        receipt = result['receipts'][0]
        assert receipt['identity']['predicate_sha256'] == by_id[case['task_id']]['sha256'], p
        assert receipt['identity']['input_sha256'] == sha(log), p
        assert receipt['identity']['local_check_sha256'] == sha(ROOT/'data/datasets/appworld/verify/check.py'), p
        assert len(receipt['predicate_calls']) == 1, p
        call = receipt['predicate_calls'][0]
        assert call['line'] == by_id[case['task_id']]['lines'][0] and call['symbol'] == 'evaluate', p
        assert call['file'].endswith('/tasks/'+case['task_id']+'/ground_truth/evaluation.py'), p
        assert receipt['network']['errno'] == 101, p
        assert result['num_tests'] == result['passes'] + result['failures'], p
        call_counts[mode] += len(receipt['predicate_calls'])
        raw = F/'raw'/case['id']/mode
        before = load(raw/'inspect-before.stdout.txt')[0]
        assert before['Image'] == 'sha256:f3cb916b9bdc297d4c73dd9646e9550befb7c6e23827d937b90a0640373e97ca'
        assert before['HostConfig']['NetworkMode'] == 'none'
        assert before['HostConfig']['ReadonlyRootfs'] is True
        assert before['HostConfig']['NanoCpus'] == 1000000000
        assert before['HostConfig']['Memory'] == 2147483648
        assert before['HostConfig']['PidsLimit'] == 128
        assert all(m['RW'] is False for m in before['Mounts'])
        assert any(m['Destination'] == '/adapter/check.py' for m in before['Mounts'])
        assert 'HG_WAWP_CLEANUP ' in (raw/'execute.stderr.txt').read_text()
for attempt in [F, F/'preserved-first-attempt', F/'preserved-second-attempt']:
    cleanup = load(attempt/'cleanup.json')
    assert all(c['removed'] and c['absent'] for c in cleanup), attempt
assert len(load(F/'cleanup.json')) == 2 * len(selected['cases'])
# Re-derive outputs from raw files; the previously reported result must be stable.
previous = (F/'comparison.json').read_bytes()
subprocess.run(['python3', str(F/'compare.py')], check=True, stdout=subprocess.DEVNULL)
assert (F/'comparison.json').read_bytes() == previous
print(json.dumps({'valid': True, 'inventory_evaluators': inv['evaluator_count'],
      'rehashed_selected_members': pins['count'], 'executed_predicate_calls': call_counts,
      'counts': summary['counts'], 'cleanup_containers': len(load(F/'cleanup.json'))}, indent=2))
