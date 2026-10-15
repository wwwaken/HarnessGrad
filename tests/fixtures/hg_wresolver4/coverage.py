"""Derive coverage only from completed final process receipts and prior evidence."""
import json
from common import HERE,ROOT,save
read=lambda p:json.loads(p.read_text())
prior=read(ROOT/'tests/fixtures/hg_wresolver3/summary.json')
rows={r['dataset']:dict(r) for r in read(ROOT/'tests/fixtures/hg_wresolver3/dataset-coverage.json')}
results=read(HERE/'results.json')|read(HERE/'results-appworld-retry.json')
assert results.keys()=={'gaia','appworld'}
for name,r in results.items():
 assert r['exit_code']==r['install']['exit_code']==r['check']['exit_code']==0 and r['negative']['exit_code']==1
 rows[name].update(status='resolved-full-python-metadata-profile',evidence=f'tests/fixtures/hg_wresolver4/raw/{"appworld-retry-" if name=="appworld" else ""}{name}.pip-report.json',reason='Complete finite source-scoped declared Python metadata graph: fresh dependency-aware kernel-network-denied resolve, hash-required installation, pip check and required-wheel refusal. Gaia covers scorer/image/preparation union on CPython3.12.4; AppWorld declared service/scorer roots and default dependencies on CPython3.11.15, with shipped installer statically shown to unpack local bundled source. No installed-image/source/runtime/native equivalence is claimed.')
for name in results:rows[name].pop('gap_evidence',None)
for name,r in read(HERE/'remainder-audit.json')['datasets'].items():
 rows[name]['reason']=r['reason'];rows[name]['gap_evidence']='tests/fixtures/hg_wresolver4/remainder-audit.json'
refs={r['dataset'] for r in read(HERE/'registry-before.json')['datasets'] if 'scorer-offline-closure' in r['shared_blockers']}
assert rows.keys()==refs
complete=sum(r['status']=='resolved-full-python-metadata-profile' for r in rows.values())
summary={'new_profiles_resolved':len(results),'target_profiles':len(results),'bounded_profiles':prior['bounded_profiles']+len(results),'bounded_profiles_resolved':prior['bounded_profiles_resolved']+len(results),'prior_bounded_profiles':prior['bounded_profiles'],'prior_bounded_profiles_resolved':prior['bounded_profiles_resolved'],'prior_complete_nonempty_python_profiles':prior['complete_nonempty_python_profiles'],'shared_datasets':len(refs),'complete_nonempty_python_profiles':complete,'not_demonstrated_at_dataset_profile_scope':len(refs)-complete,'no_third_party_payload':sum(r['status'].startswith('no-third-party') for r in rows.values()),'remaining_datasets':sorted(n for n,r in rows.items() if r['status']!='resolved-full-python-metadata-profile'),'tb_demonstrated_tasks':prior['tb_demonstrated_tasks'],'tb_tasks':prior['tb_tasks'],'selected_distributions':{n:len(r['selected']) for n,r in results.items()},'missing_wheel_refusals':{n:r['negative']['exit_code'] for n,r in results.items()},'new_candidate_artifacts':sum(len(read(HERE/f'inputs-{n}.json')['artifacts']) for n in results),'new_candidate_bytes':sum(sum(a['bytes'] for a in read(HERE/f'inputs-{n}.json')['artifacts']) for n in results),'production_authorized':False,'meaning':'Source-scoped Python default metadata reconstruction only, explicit inherited successes and two target interpreters. Native/source/installed-image equivalence and official execution remain separate.'}
assert complete==prior['complete_nonempty_python_profiles']+len(results)
save(HERE/'results-complete.json',results);save(HERE/'dataset-coverage.json',list(rows.values()));save(HERE/'summary.json',summary)
print(json.dumps(summary,indent=2,sort_keys=True))
