"""Compute extension coverage from real final process receipts, never scores."""
import json
from common import HERE, ROOT, save

read = lambda p: json.loads(p.read_text())
first = read(HERE / 'results.json')
retry = read(HERE / 'results-retry.json')
assert not first.keys() & retry.keys()
results = first | retry
save(HERE / 'results-complete.json', results)
rows = {r['dataset']: dict(r) for r in read(ROOT / 'tests/fixtures/hg_wresolver2/dataset-coverage.json')}
prior = read(ROOT / 'tests/fixtures/hg_wresolver2/summary.json')
gaps = read(HERE / 'gap-audit.json')['datasets']
registry = read(HERE / 'registry-before.json')
references = {r['dataset'] for r in registry['datasets'] if 'scorer-offline-closure' in r['shared_blockers']}
assert rows.keys() == references
for name, result in results.items():
    success = result['exit_code'] == result['install']['exit_code'] == result['check']['exit_code'] == 0
    assert result['negative']['exit_code'] == 1
    rows[name].update(status='resolved-full-python-metadata-profile' if success else 'resolution-failed',
       evidence='tests/fixtures/hg_wresolver3/raw/' + result.get('capture_prefix', '') + name + '.pip-report.json',
       reason='Fresh dependency-aware network-denied resolution, hash-required installation and pip check; required wheel removal refuses. QA scope includes conditional Parquet reader; ALFWorld includes transitively requested pddl extra.')
for name, gap in gaps.items():
    rows[name]['reason'] = gap['reason']
    rows[name]['gap_evidence'] = 'tests/fixtures/hg_wresolver3/gap-audit.json'
    if name == 'tau_bench':
        rows[name]['status'] = 'no-third-party-resolver-needed; not-counted-as-demonstration'
complete = sum(r['status'] == 'resolved-full-python-metadata-profile' for r in rows.values())
new = sum(r['exit_code'] == r['install']['exit_code'] == r['check']['exit_code'] == 0 for r in results.values())
summary = {
    'target_profiles': len(results), 'new_profiles_resolved': new,
    'bounded_profiles': prior['bounded_profiles'] + len(results),
    'bounded_profiles_resolved': prior['bounded_profiles_resolved'] + new,
    'prior_bounded_profiles': prior['bounded_profiles'],
    'prior_bounded_profiles_resolved': prior['bounded_profiles_resolved'],
    'shared_datasets': len(references), 'complete_nonempty_python_profiles': complete,
    'not_demonstrated_at_dataset_profile_scope': len(references) - complete,
    'no_third_party_payload': sum(r['status'].startswith('no-third-party') for r in rows.values()),
    'untested_profiles': sorted(n for n, r in rows.items() if r['status'] == 'not-demonstrated'),
    'tb_demonstrated_tasks': prior['tb_demonstrated_tasks'], 'tb_tasks': prior['tb_tasks'],
    'selected_distributions': {n: len(r['selected']) for n, r in results.items()},
    'missing_wheel_refusals': {n: r['negative']['exit_code'] for n, r in results.items()},
    'production_authorized': False,
    'meaning': 'Finite source-scoped Python metadata reconstruction only, with explicit inherited successes; no scorer/runtime/native/production closure.'}
assert complete == prior['complete_nonempty_python_profiles'] + new
save(HERE / 'dataset-coverage.json', list(rows.values()))
save(HERE / 'summary.json', summary)
print(json.dumps(summary, sort_keys=True))
