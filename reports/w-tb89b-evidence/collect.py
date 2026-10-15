"""Derive bounded coverage and compact review copies from actual native/raw artifacts."""
import base64, hashlib, json, pathlib, shutil, subprocess
repo=pathlib.Path(__file__).resolve().parents[2]
packet=repo/'reports/w-tb89b-evidence'
batch=json.loads((packet/'batch.json').read_text());runs=pathlib.Path(batch['runs_root'])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def read(p):return json.loads(p.read_text())
def ref(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
rows=[]
for tid in batch['selected']:
    matches=[d for d in runs.glob('*-evidence') if read(d/'identity.json')['task_id']==tid]
    assert len(matches)==1, (tid,matches)
    ev=matches[0];ident=read(ev/'identity.json');run=pathlib.Path(ident['run_dir'])
    assert (ev/'launch-observation.json').is_file(), f'not finished: {tid}'
    execution=read(run/'diagnostic_execution.json');receipt=read(run/'diagnostic_receipt.json')
    progress_path=run/'progress/round-0'/f'{tid}.json'
    progress=read(progress_path)
    shutil.copy2(progress_path,ev/'native-progress.json')
    trace_paths=list((run/'progress/round-0/traces').glob(tid+'*.jsonl'))
    trace_usage=None;trace_identity=None
    for trace in trace_paths:
        shutil.copy2(trace,ev/('native-trace-'+trace.name))
        for line in trace.read_text().splitlines():
            try: entry=json.loads(line)
            except ValueError:continue
            if 'usage' in entry:trace_usage=entry['usage']
            if 'harness_identity' in entry:trace_identity=entry['harness_identity']
    tokens=execution.get('tokens')
    if trace_usage is not None:
        tokens=dict(input=trace_usage['input_tokens'],output=trace_usage['output_tokens'],calls=trace_usage['calls'],source='retained native trial trace usage',trace_paths=[str(p) for p in trace_paths])
    gateway=execution.get('model_gateway') or progress.get('harness_output',{}).get('model_gateway')
    identity=execution.get('identity_declared') or trace_identity
    verdict=execution.get('verdicts',{}).get(tid)
    ctrfs=[];rewards=[]
    for p in sorted(ev.glob('verifier-ctrf.json-*')):
        try:
            d=read(p);ctrfs.append(dict(**ref(p),summary=d['results']['summary']))
        except (ValueError,KeyError):pass
    for p in sorted(ev.glob('verifier-reward.txt-*')):rewards.append(dict(**ref(p),text=p.read_text()))
    measured=(tid in execution.get('per_task',{}) and isinstance(verdict,dict) and verdict.get('kind')=='command' and verdict.get('score') is not None and bool(ctrfs) and bool(rewards) and tid not in execution.get('invalid',{}))
    context=read(ev/'policy-input.json')['context'];binding=dict(adapter_id='terminal_bench',run_id=ident['run_id'],trial_id=tid+':1',manifest_sha256=sha(ev/'launch-manifest.json'))
    roles={};inspections=[];stats=[];snapshots={}
    for p in sorted(ev.glob('container-inspect-*.json')):
        d=read(p)
        if d['returncode']!=0:continue
        inspections.append(ref(p))
        for c in json.loads(d['stdout']):
            role='verifier' if c['Name'].startswith('/hg-verify-') else 'agent'
            lim={k:c['HostConfig'].get(k) for k in ('NanoCpus','Memory','MemorySwap','PidsLimit','ReadonlyRootfs','StorageOpt')}
            r=roles.setdefault(role,dict(container_id=c['Id'],name=c['Name'],image_id=c['Image'],first_inspection=ref(p),limits=lim,networks=list(c['NetworkSettings']['Networks'])))
            r.update(last_inspection=ref(p),last_sample_size_rw=c.get('SizeRw'),last_sample_size_root_fs=c.get('SizeRootFs'))
    for p in sorted(ev.glob('container-stats-*.json')):
        d=read(p);stats.append(ref(p))
    for p in sorted(ev.glob('snapshot-inspect-*.json')):
        d=read(p)
        if d['returncode']==0:
            for image in json.loads(d['stdout']):snapshots[image['Id']]=dict(source=ref(p),id=image['Id'],repo_tags=image.get('RepoTags'),size=image.get('Size'),parent=image.get('Parent'))
    resource=dict(kind='observer samples, not trusted enforcement or peaks',binding=binding,declared=context['limits'],roles=roles,inspection_samples=inspections,stats_samples=stats)
    cleanup=[]
    for pattern in ('containers-after.json','networks-after.json','volumes-after.json','snapshots-after.json','container-exact-after-*.json','snapshot-exact-after-*.json'):
        for p in sorted(ev.glob(pattern)):cleanup.append(dict(**ref(p),**read(p)))
    cleanup_ok=all(p['returncode']==0 and not p['stdout'].strip() for p in cleanup if '-exact-' not in p['path']) and all(p['returncode']!=0 and 'no such' in p['stderr'].lower() for p in cleanup if '-exact-' in p['path'])
    write(ev/'resource-observation-receipt.json',resource)
    write(ev/'snapshot-observation-receipt.json',dict(binding=binding,snapshots=list(snapshots.values()),note='Observed images only; sampling may miss short-lived snapshots.'))
    write(ev/'cleanup-observation-receipt.json',dict(binding=binding,all_owned_objects_observed_absent=cleanup_ok,probes=cleanup,note='Owned-object absence observations, not atomic lease release or production authorization. Work/native receipts retained.'))
    manifest=read(ev/'launch-manifest.json')
    row=dict(**ident,image_id=manifest['image_id'],repo_digests=manifest['repo_digests'],ctrf_produced=bool(ctrfs),raw_measured=measured,verifier_verdict=verdict,raw_score=execution.get('per_task',{}).get(tid),raw_invalid=execution.get('invalid',{}),raw_not_run=execution.get('not_run'),ctrf_files=ctrfs,reward_files=rewards,endpoint=manifest['endpoint'],model=manifest['model'],model_weights_sha256=None,model_gateway=gateway,identity_declared=identity,agent_tokens=tokens,native_aggregate_tokens=execution.get('tokens'),env_usage=execution.get('env_usage'),trace_usage=trace_usage,publication=dict(score=receipt.get('score'),coverage=receipt.get('coverage'),outcomes=receipt.get('outcomes'),enforcement=execution.get('enforcement')),hashes=context['hashes'],scorer=context['metric'],declared_limits=context['limits'],resource_receipt=ref(ev/'resource-observation-receipt.json'),snapshot_receipt=ref(ev/'snapshot-observation-receipt.json'),cleanup_receipt=ref(ev/'cleanup-observation-receipt.json'),cleanup_observed_absent=cleanup_ok,launch_observation=read(ev/'launch-observation.json'))
    write(ev/'result.json',row);rows.append(row)
    dst=packet/'attempts'/tid;dst.mkdir(parents=True,exist_ok=True)
    # Preserve all raw samples externally; keep a compact, hash-bound review packet.
    prefixes=('container-inspect-','container-stats-','container-list-','snapshot-list-','snapshot-inspect-')
    omit={'processes-preflight.json','selected-instruction.md','selected-Dockerfile','selected-task.toml'}
    for p in ev.iterdir():
        if not p.is_file() or p.name.startswith(prefixes) or p.name in omit:continue
        shutil.copy2(p,dst/p.name)
    for p in [ev/'selected-instruction.md',ev/'selected-Dockerfile',ev/'selected-task.toml',*sorted((ev/'selected-tests').rglob('*'))]:
        if p.is_file():
            rel=str(p.relative_to(ev));out=dst/'source-preimages'/pathlib.Path(rel+'.json');out.parent.mkdir(parents=True,exist_ok=True)
            write(out,dict(source=ref(p),encoding='base64',data=base64.b64encode(p.read_bytes()).decode('ascii')))
    # Make first/last role observations available in the review packet too.
    for role in roles.values():
        for key in ('first_inspection','last_inspection'):
            p=pathlib.Path(role[key]['path']);shutil.copy2(p,dst/p.name)
    for s in snapshots.values():
        p=pathlib.Path(s['source']['path']);shutil.copy2(p,dst/p.name)
raw=dict(selected_tasks=len(rows),expected_trials=len(rows),measured_tasks=sum(r['raw_measured'] for r in rows),measured_trials=sum(r['raw_measured'] for r in rows),invalid_tasks=sum(bool(r['raw_invalid']) for r in rows),unmeasured_tasks=sum(not r['raw_measured'] and not r['raw_invalid'] for r in rows))
publication={k:sum(r['publication']['coverage'][k] for r in rows) for k in rows[0]['publication']['coverage']}
summary=dict(batch=batch,inventory={k:read(packet/'inventory.json')[k] for k in ('total_task_references','cached_images','missing_images')},raw_execution_coverage=raw,publication_coverage_sum_of_four_one_task_selections=publication,rows=rows,scope='Purposeful four-task diagnostics. Raw verifier execution is distinct from policy publication; no complete offline closure or benchmark-comparable score.')
write(packet/'result.json',summary);write(runs/'result.json',summary)
# Hash all retained run artifacts only after execution and derived receipts finish.
files=[ref(p) for p in sorted(runs.rglob('*')) if p.is_file() and p.name!='run-artifact-inventory.json']
write(packet/'run-artifact-inventory.json',dict(root=str(runs),files=files));shutil.copy2(packet/'run-artifact-inventory.json',runs/'run-artifact-inventory.json')
print(json.dumps(dict(raw=raw,publication=publication,retained_files=len(files),runs_root=str(runs)),indent=2))
