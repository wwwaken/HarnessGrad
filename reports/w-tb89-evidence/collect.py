"""Derive refusal ledger from raw commands; never turn admission failure into zero."""
import hashlib, json, pathlib, shutil, subprocess
repo=pathlib.Path(__file__).resolve().parents[2]
packet=repo/'reports/w-tb89-evidence'
batch=json.loads((packet/'batch.json').read_text());runs=pathlib.Path(batch['runs_root'])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
    with p.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
def capture(name,argv):
    p=subprocess.run(argv,cwd=repo,capture_output=True,text=True,timeout=45)
    write(packet/(name+'.json'),dict(argv=argv,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr));return p

# Preserve the original complete preparation packet, including all source preimages.
shutil.copytree(packet,runs/'preparation-packet')
inventory=json.loads((packet/'inventory.json').read_text())
attempts=[];preflight_only=[]
for ev in sorted(runs.glob('*-evidence')):
    identity=json.loads((ev/'identity.json').read_text());run=pathlib.Path(identity['run_dir']);work=pathlib.Path(identity['work_root'])
    observation=ev/'launch-observation.json'
    if not observation.exists():
        preflight_only.append(dict(**identity,probe=json.loads((ev/'prerequisite-probe.json').read_text()),interpretation='The probe overrequired image-local python3. The production route has host-interpreter fallback; this is not counted as a driver attempt or task failure. A distinct fresh regex-log driver attempt is retained.'))
        continue
    stderr=(ev/'driver.stderr.txt').read_text()
    assert stderr=='refusing staged policy: bind evidence to the live local agent endpoint\n'
    assert not run.exists() and not work.exists()
    assert not list(ev.glob('verifier-ctrf.json-*'))
    observed=json.loads(observation.read_text());assert observed['returncode']==2
    tid=identity['task_id']; row=next(r for r in inventory['rows'] if r['task_id']==tid)
    after={}
    for k in ['containers','networks','volumes','snapshots']:
        p=ev/(k+'-after.json');raw=json.loads(p.read_text())
        assert raw['returncode']==0 and raw['stdout']==''
        after[k]=dict(path=str(p),sha256=sha(p),returncode=raw['returncode'],stdout=raw['stdout'],stderr=raw['stderr'])
    record=dict(**identity,image_id=row['image_id'],repo_digests=row['repo_digests'],driver_returncode=observed['returncode'],driver_stderr=stderr,ctrf_produced=False,raw_verifier_verdict=None,raw_verifier_score=None,raw_unmeasured_reason=stderr.strip(),observer_status='unmeasured-before-task-execution',native_coverage=None,native_receipt_present=False,run_dir_exists=False,work_root_exists=False,endpoint=None,model=None,cleanup=after,context=json.loads((ev/'policy-input.json').read_text())['context'])
    attempts.append(record)
    shutil.copytree(ev,packet/'attempts'/tid)
assert sorted(a['task_id'] for a in attempts)==sorted(batch['selected'])
for old in preflight_only:
    shutil.copytree(pathlib.Path(old['evidence_dir']),packet/'preflight-only'/old['task_id'])
previous=pathlib.Path('/tmp/hg-net/reports/w-net-evidence/launch/result.json')
p=capture('previous-official-result',['cat',str(previous)])
prev=json.loads(p.stdout)
assert prev['verifier_verdict']['score']==0.0 and prev['ctrf_files']
capture('driver-guard-source',['python3','-c',"from pathlib import Path; p=Path('driver.py'); t=p.read_text().splitlines(); print('\\n'.join(f'{i+1}: {t[i]}' for a,b in [(197,213),(389,414),(439,447)] for i in range(a,b)))"])
capture('interpreter-fallback-source',['python3','-c',"from pathlib import Path; p=Path('eval/containers/container_state.py'); t=p.read_text().splitlines(); print('\\n'.join(f'{i+1}: {t[i]}' for a,b in [(81,103),(127,136),(150,162)] for i in range(a,b)))"])
capture('disk-final',['df','-B1','/','/tmp'])
capture('processes-final',['ps','-eo','pid,args'])
capture('containers-final',['docker','ps','-a','--no-trunc','--format','{{json .}}'])
capture('dataset-status-final',['git','-C','/mnt/20t/xubuqiang/datasets/terminal-bench','status','--short'])
summary=dict(task_references=inventory['task_references'],cached_images=inventory['cached'],missing_images=inventory['absent'],missing_source_tasks=[r['task_id'] for r in inventory['rows'] if r['missing_source']],selected=len(batch['selected']),driver_attempts=len(attempts),task_trials_started=0,new_ctrf_tasks=sum(a['ctrf_produced'] for a in attempts),new_raw_measured_tasks=0,observer_ledger=dict(measured=0,invalid=0,unmeasured=len(attempts),definition='Administrative ledger of refused requested tasks, not native trial coverage; no task trials or native diagnostic receipts exist.'),native_trial_coverage=None,prior_official_tasks=len(prev['raw_per_task']),cumulative_official_execution_fraction=f"{len(prev['raw_per_task'])}/{inventory['task_references']}",new_execution_fraction=f"0/{inventory['task_references']}",selected_fraction=f"{len(attempts)}/{inventory['task_references']}",endpoint=None,model=None,attempts=attempts,preflight_only=preflight_only,selection_rule=batch['selection_rule'],runs_root=str(runs))
write(packet/'result.json',summary)
write(runs/'result.json',summary)
# Original all-task preimages remain intact in preparation-packet. Commit only the
# selected task sources, retaining every image-inspection command output in git.
for p in (packet/'inventory/sources').iterdir():
    if p.name not in batch['selected']:shutil.rmtree(p)
write(packet/'source-custody.json',dict(all_task_source_preimages=str(runs/'preparation-packet/inventory/sources'),selected_repository_copies='reports/w-tb89-evidence/inventory/sources',inventory='reports/w-tb89-evidence/inventory.json',note='Only unselected repository review copies were omitted after an intact external preparation copy; no run evidence or original source was deleted.'))
files=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(runs.rglob('*')) if p.is_file()]
write(packet/'run-artifact-inventory.json',dict(root=str(runs),files=files))
print(json.dumps({k:v for k,v in summary.items() if k not in ('attempts','preflight_only')},indent=2))
