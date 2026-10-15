"""Recompute denominators from receipts and the unchanged shared references."""
import json

from common import HERE, ROOT, save

read = lambda path: json.loads(path.read_text())
registry = read(HERE / 'registry-before.json')
prior = read(ROOT / 'tests/fixtures/hg_wresolver/dataset-coverage.json')
prior_summary = read(ROOT / 'tests/fixtures/hg_wresolver/summary.json')
results = read(HERE / 'results.json')
rows = {r['dataset']: dict(r) for r in prior}
references = {r['dataset'] for r in registry['datasets'] if 'scorer-offline-closure' in r['shared_blockers']}
assert references == rows.keys()
for name, result in results.items():
    success = result['exit_code'] == result['install']['exit_code'] == result['check']['exit_code'] == 0
    rows[name]['status'] = 'resolved-full-python-metadata-profile' if success else 'resolution-failed'
    rows[name]['evidence'] = 'tests/fixtures/hg_wresolver2/raw/' + name + '.pip-report.json'
    rows[name]['reason'] = 'Fresh dependency-aware resolution, hash-required install and pip check under kernel network denial.' if success else 'See fresh raw refusal.'
for name, row in rows.items():
    if row.get('reason'):
        continue
    if row['status'].startswith('no-third-party'):
        row['reason'] = 'N/A: no third-party requirement on the inherited inspected path; not a successful reconstruction or runtime closure.'
    elif name == 'terminal_bench':
        row['reason'] = 'Only openssl-selfsigned-cert tooling previously resolved; remaining task-specific bootstrap graphs not demonstrated.'
    elif row['status'] == 'not-demonstrated':
        row['reason'] = 'Not exercised by either resolver packet; prior import/image/ABI inventories do not demonstrate a dependency-aware metadata solve.'
    else:
        row['reason'] = 'Prior w-resolver successful metadata reconstruction, unchanged.'
complete = sum(r['status'] == 'resolved-full-python-metadata-profile' for r in rows.values())
summary = {
    'target_profiles': len(results), 'new_profiles_resolved': sum(r['exit_code'] == 0 for r in results.values()),
    'bounded_profiles': prior_summary['bounded_datasets'],
    'bounded_profiles_resolved': prior_summary['bounded_profiles_resolved'] + sum(r['exit_code'] == 0 for r in results.values()),
    'shared_datasets': len(references), 'complete_nonempty_python_profiles': complete,
    'not_demonstrated_at_dataset_profile_scope': len(references) - complete,
    'no_third_party_payload': sum(r['status'].startswith('no-third-party') for r in rows.values()),
    'untested_profiles': sorted(n for n, r in rows.items() if r['status'] == 'not-demonstrated'),
    'tb_demonstrated_tasks': prior_summary['tb_demonstrated_tasks'], 'tb_tasks': prior_summary['tb_task_sources'],
    'selected_distributions': {n: len(r['selected']) for n, r in results.items()},
    'production_authorized': False,
    'meaning': 'Python default metadata reconstruction only; unchanged old evidence is carried forward explicitly, not rerun.'}
save(HERE / 'dataset-coverage.json', list(rows.values()))
save(HERE / 'summary.json', summary)
print(json.dumps(summary, sort_keys=True))
