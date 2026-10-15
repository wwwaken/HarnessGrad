"""Append observed S4 scope/evidence only; every status and action is preserved."""
import json,pathlib,runpy,subprocess
repo=pathlib.Path(__file__).resolve().parents[2];p=repo/'reports/w-tb89d-evidence'
read=lambda path:json.loads(path.read_text())
s=read(p/'result.json');raw=s['raw_execution_coverage'];pub=s['publication_coverage_sum_of_one_task_selections'];obs=(p/'registry-observation.txt').read_text().strip();available=read(p/'availability-all.json')
assert obs in (repo/'reports/w-tb89d-receipts.md').read_text()
heading='## '+s['rows'][0]['launch_observation']['started_at'][:10]+' — Broader bounded Terminal-Bench verifier execution - w-tb89d'
journal=repo/'docs/adapter-integration-journal.md';assert heading not in journal.read_text()
result=', '.join(r['task_id']+'='+('invalid' if r['raw_invalid'] else json.dumps(r['raw_score']))+' (CTRF='+str(r['ctrf_produced'])+')' for r in s['rows'])
entry=f'''

{heading}

- Two preserved fixed selections total {len(s['rows'])} unique new cached task surfaces. Initial five source/tool/image probes passed but did not verify the uv GitHub asset; four native attempts were invalid without CTRF. A separate no-model bootstrap probe failed at the pinned uv archive, with host release-assets TLS failure also retained. The fifth initial task was interrupted: launcher returned 143, driver absent, no native final receipt; partial trace retained and exactly owned orphan resources cleaned. None of these runs is replaced, resumed, rerun or scored as zero.
- Two additional pip-bootstrap tasks were fixed before their model trials, with complete pinned pip install, pytest CTRF-option and dependency version/import smoke checks. All absent images are skipped. Total selection stays within the nine-task bound. Outside both selections remain {available['cached_new_outside_batch']} cached tasks without prior measured coverage, including {available['metadata_new_outside_batch']} metadata-bounded candidates; they are not certified runnable. No further prerequisite-verified task remains queued.
- {result}. Raw ledger selected={raw['selected_tasks']}, expected_trials={raw['expected_trials']}, measured={raw['measured_tasks']}, invalid={raw['invalid_tasks']}, unmeasured={raw['unmeasured_tasks']}. Only official command/CTRF/reward evidence counts. New raw coverage={raw['measured_tasks']}/{s['inventory']['total_task_references']}; cumulative unique raw coverage={available['prior_measured_count']+raw['measured_tasks']}/{s['inventory']['total_task_references']}.
- Every launched task used a fresh ID and external work root, unchanged loop/train diagnostic admission, rounds=0/trials=1/jobs=1, HG_TB_SPLIT=none and HG_EGRESS_PROXY=http://172.17.0.1:17890. Worker concurrency stayed one with direct qwen3.5-9b-local at http://127.0.0.1:8002/v1; pre-existing operator proxy sharing was observed and permitted. No operator process or model server was changed. Native publication receipts available={s['native_execution_receipts']}, missing={s['missing_native_receipts']}; observed native publication measured={pub['measured_tasks']}, invalid={pub['invalid_tasks']}, unmeasured={pub['unmeasured_tasks']}, scores null. Missing publication is not fabricated; unknown enforcement stays unknown.
- Complete retained artifact roots: {', '.join('`'+root+'`' for root in s['batch']['runs_roots'])}. The hash-bound packet, source/image/scorer/manifest/model identities, resource/snapshot/cleanup observations and raw invalid/interruption evidence are indexed in reports/w-tb89d-receipts.md and reports/w-tb89d-evidence/. No complete offline transitive closure, comparable performance or trusted production admission follows.
- Only scorer-offline-closure observed/evidence is appended at this precise S4 scope. S4 remains PARTIAL; no shared or dataset blocker closes. All statuses, next_actions, dataset/history records, gates and production_authorized=false remain unchanged. Runtime/task/test/reference/method code, repository runs/ and frozen receipts are untouched. Validation: reports/w-tb89d-validation.txt. Commit only in registered /tmp/hg-tb89d for parent review; main is untouched.
'''
document=read(repo/'docs/dataset-blockers.json');blocker=next(b for b in document['shared_blockers'] if b['id']=='scorer-offline-closure')
assert 'Bounded live-local Terminal-Bench execution - w-tb89d:' not in blocker['observed']
blocker['observed']+=' '+obs
blocker['evidence'] += [dict(kind='repository',path='reports/w-tb89d-receipts.md',locator='## Exact registry observation - w-tb89d'),dict(kind='repository',path='docs/adapter-integration-journal.md',locator=heading)]
with journal.open('a') as f:f.write(entry)
module=runpy.run_path(str(repo/'tools/check_dataset_blockers.py'));module['validate'](read(repo/'docs/dataset-blockers.json'),root=repo);module['validate'](document,root=repo)
(repo/'docs/dataset-blockers.json').write_text(json.dumps(document,ensure_ascii=False,indent=2)+'\n')
args=['python3','tools/check_dataset_blockers.py'];r=subprocess.run(args,cwd=repo,capture_output=True,text=True)
(p/'blocker-check-after-edit.json').write_text(json.dumps(dict(argv=args,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr),indent=2)+'\n');assert r.returncode==0;print(r.stdout,end='')
