"""Append the exact new S4 observation while preserving every blocker/action/status."""
import json,pathlib,runpy,subprocess
repo=pathlib.Path(__file__).resolve().parents[2];packet=repo/'reports/w-tb89e-evidence'
read=lambda p:json.loads(p.read_text())
s=read(packet/'result.json');obs=(packet/'registry-observation.txt').read_text().strip();assert obs in (repo/'reports/w-tb89e-receipts.md').read_text()
heading='## '+s['rows'][0]['launch_observation']['started_at'][:10]+' — Broader bounded Terminal-Bench verifier execution - w-tb89e'
journal=repo/'docs/adapter-integration-journal.md';assert heading not in journal.read_text()
entry='\n\n'+heading+'\n\n'+obs+'\n\n'
entry+='Preselected tasks: '+', '.join('`'+r['task_id']+'`' for r in s['rows'])+'. Per-task raw outcomes: '+', '.join(r['task_id']+'='+('invalid ('+str(r['raw_exclusion_reason'])+')' if not r['raw_measured'] else str(r['raw_score'])) for r in s['rows'])+'.\n\n'
entry+='Receipt: reports/w-tb89e-receipts.md. Compact hash-bound evidence: reports/w-tb89e-evidence/result.json. Raw preparation: `'+s['raw_root']+'`; native/observer run artifacts: `'+s['runs_root']+'`; fresh external work roots are listed per task in the report. Validation: reports/w-tb89e-validation.txt. All run artifacts remain intact; no old receipt or ID is overwritten/resumed. Only scorer-offline-closure observed/evidence is appended. No task/scorer/runtime/admission/gate/method changes, no model server startup, no paid endpoint, no repository runs/ or frozen receipt edits. Commit only in the registered /tmp/hg-tb89e worktree for parent review; main is untouched.\n'
doc=read(repo/'docs/dataset-blockers.json');blocker=next(b for b in doc['shared_blockers'] if b['id']=='scorer-offline-closure');assert 'Bounded live-local Terminal-Bench execution - w-tb89e:' not in blocker['observed']
blocker['observed']+=' '+obs
blocker['evidence'] += [dict(kind='repository',path='reports/w-tb89e-receipts.md',locator='## Exact registry observation - w-tb89e'),dict(kind='repository',path='docs/adapter-integration-journal.md',locator=heading)]
with journal.open('a') as f:f.write(entry)
module=runpy.run_path(str(repo/'tools/check_dataset_blockers.py'));module['validate'](read(repo/'docs/dataset-blockers.json'),root=repo);module['validate'](doc,root=repo)
(repo/'docs/dataset-blockers.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
args=['python3','tools/check_dataset_blockers.py'];r=subprocess.run(args,cwd=repo,capture_output=True,text=True)
(packet/'blocker-check-after-edit.json').write_text(json.dumps(dict(argv=args,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr),indent=2)+'\n');assert r.returncode==0;print(r.stdout,end='')
