"""Derive comparisons from retained raw bytes, including exit/measurement failures."""
import hashlib
import json
from pathlib import Path

F = Path(__file__).resolve().parent
load = lambda p: json.loads(p.read_text())
inputs = load(F/'inputs.json')
inventory = load(F/'inventory.json')
rows = []
exercised = set()
for case in inputs['cases']:
    row = {'id': case['id'], 'task_id': case['task_id'], 'control': case['control']}
    trackers = {}
    for mode in ['official', 'local']:
        raw = F/'raw'/case['id']/mode
        artifacts = {}
        for line in (raw/'execute.stdout.txt').read_text().splitlines():
            if line.startswith('HG_WAWP_ARTIFACT '):
                item = json.loads(line.removeprefix('HG_WAWP_ARTIFACT '))
                artifacts[item['name']] = item['content']
        receipts = [json.loads(line.removeprefix('HG_WAWP_RECEIPT '))
                    for line in (raw/'execute.stderr.txt').read_text().splitlines()
                    if line.startswith('HG_WAWP_RECEIPT ')]
        after = load(raw/'inspect-after.stdout.txt')[0]
        item = {'docker_attach_exit': int((raw/'execute.returncode.txt').read_text()),
                'container_exit': after['State']['ExitCode'], 'oom_killed': after['State']['OOMKilled'],
                'artifacts': artifacts, 'receipts': receipts}
        if mode == 'official' and 'result.json' in artifacts:
            result = json.loads(artifacts['result.json'])
            item.update(measured=result['measured'], reward=result['reward'])
            trackers[mode] = result['tracker']
        elif mode == 'local' and 'evidence.json' in artifacts:
            evidence = json.loads(artifacts['evidence.json'])
            item['measured'] = evidence.get('measured', False)
            item['reward'] = float(artifacts['reward.txt']) if 'reward.txt' in artifacts else None
            trackers[mode] = {k: evidence[k] for k in ['success', 'num_tests', 'passes', 'failures'] if k in evidence}
        else:
            item['measured'] = False
            item['reward'] = None
        if mode in trackers and item['measured']:
            t = trackers[mode]
            item.update(num_tests=t['num_tests'], passes=len(t['passes']), failures=len(t['failures']))
        for receipt in receipts:
            for call in receipt['predicate_calls']:
                if call['file'].endswith('/tasks/'+case['task_id']+'/ground_truth/evaluation.py'):
                    exercised.add(case['task_id'])
        out = F/'outputs'/case['id']/mode
        out.mkdir(parents=True, exist_ok=True)
        for name, content in artifacts.items():
            (out/name).write_text(content)
        (out/'parsed.json').write_text(json.dumps(item, indent=2)+'\n')
        row[mode] = {k: item[k] for k in ['measured', 'reward', 'container_exit', 'docker_attach_exit',
                                         'num_tests', 'passes', 'failures'] if k in item}
    a, b = row['official'], row['local']
    numeric = all(s['measured'] and s['reward'] is not None and s['container_exit'] == 0
                  and s['docker_attach_exit'] == 0 for s in [a, b])
    row['numeric_comparison'] = numeric
    row['numeric_agreement'] = a['reward'] == b['reward'] if numeric else None
    row['tracker_agreement'] = all(trackers['official'].get(k) == trackers['local'].get(k)
                                   for k in ['success', 'num_tests', 'passes', 'failures']) if numeric else None
    rows.append(row)
counts = {'controlled_inputs': len(rows), 'released_predicates_exist': inventory['evaluator_count'],
          'released_predicates_exercised': len(exercised), 'numeric_comparisons': sum(r['numeric_comparison'] for r in rows),
          'numeric_agreements': sum(r['numeric_agreement'] is True for r in rows),
          'numeric_divergences': sum(r['numeric_agreement'] is False for r in rows),
          'tracker_agreements': sum(r['tracker_agreement'] is True for r in rows),
          'tracker_divergences': sum(r['tracker_agreement'] is False for r in rows),
          'official_unmeasured': sum(not r['official']['measured'] for r in rows),
          'local_unmeasured': sum(not r['local']['measured'] for r in rows),
          'official_exit_failures': sum(r['official']['container_exit'] != 0 for r in rows),
          'local_exit_failures': sum(r['local']['container_exit'] != 0 for r in rows)}
for mode in ['official', 'local']:
    for field in ['num_tests', 'passes', 'failures']:
        counts[mode+'_'+field] = sum(r[mode].get(field, 0) for r in rows)
reachability = []
for predicate in inventory['evaluators']:
    row = dict(predicate)
    row['dynamic_reachability'] = ('executed official and local; see raw/ and outputs/' if row['task_id'] in exercised
                                   else 'not attempted; bounded study selection' if row['split'] in ['train', 'dev']
                                   else 'not attempted; held-out execution excluded')
    reachability.append(row)
(F/'reachability.json').write_text(json.dumps({'exercised': sorted(exercised),
            'unexercised': len(reachability)-len(exercised), 'evaluators': reachability}, indent=2)+'\n')
summary = {'counts': counts, 'comparisons': rows,
           'coverage_fraction': f"{len(exercised)}/{inventory['evaluator_count']}",
           'not_actor_or_benchmark_evidence': True}
(F/'comparison.json').write_text(json.dumps(summary, indent=2)+'\n')
print(json.dumps(summary, indent=2))
