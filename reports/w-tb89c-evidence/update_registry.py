"""Append evidence at the exact observed scope; preserve every blocker/status/gate."""
import json, pathlib, runpy, subprocess
repo=pathlib.Path(__file__).resolve().parents[2]; packet=repo/'reports/w-tb89c-evidence'
def read(p): return json.loads(p.read_text())
s=read(packet/'result.json'); raw=s['raw_execution_coverage']; pub=s['publication_coverage_sum_of_one_task_selections']
obs=(packet/'registry-observation.txt').read_text().strip()
assert obs in (repo/'reports/w-tb89c-receipts.md').read_text()
prior=json.loads(read(packet/'prior-tb89b-result.json')['stdout'])
old={r['task_id'] for r in prior['rows'] if r['raw_measured']}
net=json.loads(json.loads(read(packet/'prior-openssl-result.json')['stdout'])['stdout'])
old.update(net['raw_per_task'])
cumulative=len(old)+raw['measured_tasks']; total=s['inventory']['total_task_references']
date=s['rows'][0]['launch_observation']['started_at'][:10]
heading=f'## {date} — Broader bounded Terminal-Bench verifier execution - w-tb89c'
journal=repo/'docs/adapter-integration-journal.md'
assert heading not in journal.read_text()
results=', '.join(f"{r['task_id']}={'invalid' if r['raw_invalid'] else json.dumps(r['raw_score'])} (CTRF={r['ctrf_produced']})" for r in s['rows'])
entry=f'''

{heading}

- Fixed selection and prerequisites: {len(s['rows'])} new cached tasks with complete official sources, parsed verifier scripts and fresh read-only network-disabled tool/input probes; no GPU/MCP, <=1 CPU/2048 MiB and declared timeouts <=900s. No absent image execution/pull, rerun or result-dependent substitution. The inventory and exact selection rule are preserved in reports/w-tb89c-evidence/.
- {results}. Raw ledger selected={raw['selected_tasks']}, expected_trials={raw['expected_trials']}, measured={raw['measured_tasks']}, invalid={raw['invalid_tasks']}, unmeasured={raw['unmeasured_tasks']}; missing CTRF is invalid and excluded from measured coverage. New raw coverage={raw['measured_tasks']}/{total}; cumulative unique raw coverage={cumulative}/{total}, with the prior/new union preserved in reports/w-tb89c-receipts.md.
- Each fresh one-task loop/train diagnostic used rounds=0/trials=1/jobs=1, HG_TB_SPLIT=none and HG_EGRESS_PROXY=http://172.17.0.1:17890, bound to qwen3.5-9b-local at http://127.0.0.1:8002/v1. Worker concurrency was one; preflight and repeated process samples are checked for other platform drivers. No operator process or model server was changed. Native publication measured={pub['measured_tasks']}, invalid={pub['invalid_tasks']}, unmeasured={pub['unmeasured_tasks']}, all scores null; unknown policy enforcement stays unknown.
- Full run/observer artifacts remain intact at `{s['batch']['runs_root']}`, with work roots outside the platform. Compact hash-bound review copies preserve CTRF/rewards, image/manifest/source/scorer bindings, model trace/gateway usage, resource samples, observed snapshots and scoped/exact cleanup probes. Resource/lifecycle observations do not establish trusted enforcement, offline transitive closure or production admission.
- Only shared scorer-offline-closure observed/evidence gains this bounded S4 execution scope. S1/S3/S4/S5/S6 remain PARTIAL; no shared or dataset blocker closes. All statuses, next_actions, dataset/history records, gates and production_authorized=false remain unchanged. Runtime/admission/task/test/reference code, repository runs/ and frozen receipts are untouched. Validation: reports/w-tb89c-validation.txt. Commit only in registered /tmp/hg-tb89c for parent review; main is untouched.
'''
document=read(repo/'docs/dataset-blockers.json')
blocker=next(b for b in document['shared_blockers'] if b['id']=='scorer-offline-closure')
assert 'Bounded live-local Terminal-Bench execution - w-tb89c:' not in blocker['observed']
blocker['observed']+=' '+obs
blocker['evidence'] += [dict(kind='repository',path='reports/w-tb89c-receipts.md',locator='## Exact registry observation - w-tb89c'),dict(kind='repository',path='docs/adapter-integration-journal.md',locator=heading)]
# Locators exist before the registry edit, so the registry remains valid throughout.
with journal.open('a') as f: f.write(entry)
module=runpy.run_path(str(repo/'tools/check_dataset_blockers.py'))
module['validate'](read(repo/'docs/dataset-blockers.json'),root=repo)
module['validate'](document,root=repo)
(repo/'docs/dataset-blockers.json').write_text(json.dumps(document,ensure_ascii=False,indent=2)+'\n')
r=subprocess.run(['python3','tools/check_dataset_blockers.py'],cwd=repo,capture_output=True,text=True)
(packet/'blocker-check-after-edit.json').write_text(json.dumps(dict(argv=['python3','tools/check_dataset_blockers.py'],returncode=r.returncode,stdout=r.stdout,stderr=r.stderr),indent=2)+'\n')
assert r.returncode==0
print(r.stdout,end='')
