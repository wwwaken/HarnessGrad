"""Generate exact scope/counts and command index from raw collection receipts."""
import json
from pathlib import Path

F = Path(__file__).resolve().parent
load = lambda name: json.loads((F/name).read_text())
inv = load('inventory.json')
reach = load('reachability.json')
counts = load('comparison.json')['counts']
summary = {'entrypoint_definition': 'one task-specific released ground_truth/evaluation.py:evaluate',
           'released_evaluate_entrypoints': inv['evaluator_count'],
           'unique_evaluation_file_sha256': len({r['sha256'] for r in inv['evaluators']}),
           'split_counts': inv['split_counts'],
           'executed': reach['exercised'],
           'unexercised_by_split': {s: sum(r['split'] == s and r['task_id'] not in reach['exercised']
                                           for r in inv['evaluators']) for s in inv['split_counts']},
           'static_missing_from_image': sum(not r['image_present'] for r in inv['evaluators']),
           'static_bundle_image_digest_mismatches': sum(r['sha256'] != r['image_sha256'] for r in inv['evaluators']),
           'selected_base_db_members': sum(p['member'].startswith('data/base_dbs/') for p in load('selected-byte-pins.json')['members']),
           'final_counts': counts}
(F/'inventory-summary.json').write_text(json.dumps(summary, indent=2)+'\n')
commands = []
for attempt in ['preserved-first-attempt', 'preserved-second-attempt', '.']:
    commands.append('# ' + attempt)
    for item in load(attempt+'/execution-commands.json'):
        commands.append('# '+item['case']+' '+item['mode'])
        commands.extend(item['commands'])
(F/'commands-exact.txt').write_text('\n'.join(commands)+'\n')
print(json.dumps(summary, indent=2))
