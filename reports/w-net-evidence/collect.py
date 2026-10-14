"""Preserve real run files and manifest-bound observer facts; never score or alter a task."""
import hashlib, json, pathlib, shutil, subprocess, tarfile
ROOT=pathlib.Path('/tmp/hg-net')
OUT=ROOT/'reports/w-net-evidence'
RUN_ID='w-net-terminal-bench-20261014T200818Z-fd0c4d1e'
run=ROOT/'runs'/RUN_ID
evidence=ROOT/'runs'/(RUN_ID+'-launch-evidence')
def read(path): return json.loads(path.read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name,value):
    p=evidence/name
    with p.open('x') as stream: json.dump(value,stream,indent=2); stream.write('\n')
    return p
def capture(name,argv):
    p=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,timeout=30)
    return write(name,dict(argv=argv,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr))
receipt=read(run/'diagnostic_receipt.json')
execution=read(run/'diagnostic_execution.json')
manifest_sha=sha(evidence/'launch-manifest.json')
assert receipt['context']['hashes']['manifest']==manifest_sha
binding=dict(adapter_id='terminal_bench',run_id=RUN_ID,trial_id='openssl-selfsigned-cert:1',manifest_sha256=manifest_sha)
roles={}
all_containers={}
for p in sorted(evidence.glob('container-inspect-*.json')):
    captured=read(p)
    if captured['returncode'] != 0: continue
    for c in json.loads(captured['stdout']):
        all_containers[c['Id']]=c
        role='verifier' if c['Name'].startswith('/hg-verify-') else 'agent'
        row=dict(source=str(p),source_sha256=sha(p),id=c['Id'],name=c['Name'],image=c['Image'],state=c['State'],size_rw=c.get('SizeRw'),limits={k:c['HostConfig'].get(k) for k in ('NanoCpus','Memory','MemorySwap','PidsLimit','ReadonlyRootfs')},networks=c['NetworkSettings']['Networks'],mounts=c['Mounts'])
        roles.setdefault(role,dict(first=row,last=row))['last']=row
resource=write('resource-observation-receipt.json',dict(kind='manifest-bound observer receipt; not runtime admission or peak usage attestation',binding=binding,roles=roles,declared=receipt['context']['limits'],statistics=[dict(path=str(p),sha256=sha(p)) for p in sorted(evidence.glob('container-stats-*.json'))],runtime_admission_receipt=None))
snapshots={}
for p in sorted(evidence.glob('snapshot-inspect-*.json')):
    captured=read(p)
    if captured['returncode'] == 0:
        for c in json.loads(captured['stdout']):
            snapshots[c['Id']]=dict(source=str(p),source_sha256=sha(p),id=c['Id'],repo_tags=c['RepoTags'],size=c['Size'],parent=c.get('Parent'))
snapshot=write('snapshot-observation-receipt.json',dict(kind='manifest-bound observer receipt; not snapshot admission',binding=binding,snapshots=list(snapshots.values()),events_path=str(run/'events.jsonl'),events_sha256=sha(run/'events.jsonl'),driver_snapshot=receipt['snapshot']))
raw_cache=read(evidence/'image-inspect.json')
image=write('image-observation-receipt.json',dict(kind='manifest-bound observer receipt',binding=binding,cache_inspection_path=str(evidence/'image-inspect.json'),cache_inspection_sha256=sha(evidence/'image-inspect.json'),cache_images=[dict(id=c['Id'],repo_digests=c['RepoDigests'],repo_tags=c['RepoTags']) for c in json.loads(raw_cache['stdout'])],launched_images={role:row['first']['image'] for role,row in roles.items()}))
exact=[]
for i,cid in enumerate(all_containers):
    exact.append(capture(f'container-exact-after-{i:02d}.json',['docker','inspect',cid]))
for i,sid in enumerate(snapshots):
    exact.append(capture(f'snapshot-exact-after-{i:02d}.json',['docker','image','inspect',sid]))
for kind,argv in [('volumes',['docker','volume','ls']),('networks',['docker','network','ls']),('containers',['docker','ps','-a'])]:
    exact.append(capture(f'{kind}-final.json',argv+['--filter',f'label=harnessgrad.run={RUN_ID}','--format','{{json .}}']))
cleanup=write('cleanup-observation-receipt.json',dict(kind='manifest-bound observer receipt; owned-object absence observations, not atomic lease release or admission',binding=binding,scoped_and_exact_probes=[dict(path=str(p),sha256=sha(p),**read(p)) for p in exact]+[dict(path=str(evidence/name),sha256=sha(evidence/name),**read(evidence/name)) for name in ('containers-after.json','networks-after.json','snapshot-images-after.json')],docker_events_path=str(evidence/'docker-events.jsonl'),docker_events_sha256=sha(evidence/'docker-events.jsonl'),driver_cleanup=receipt['cleanup'],driver_lifecycle=receipt['lifecycle'],cleanup_admission_receipt=None,lease_release_attested=False))
work=pathlib.Path(read(evidence/'identity.json')['work_root'])/RUN_ID/'workspace'
# The staged git tree and manifest are observations from the actual executed harness.
capture('harness-tree.json',['git','-C',str(work),'rev-parse','HEAD^{tree}'])
provenance=write('provenance.json',dict(binding=binding,platform=read(run/'run_meta.json').get('platform'),dataset=read(evidence/'dataset-commit.json'),source_sha256=receipt['context']['hashes']['source'],split_sha256=receipt['context']['hashes']['split'],harness_files_sha256=receipt['context']['hashes']['harness'],harness_manifest_path=str(work/'harness.json'),harness_manifest_sha256=sha(work/'harness.json'),model_weights_sha256=None,scorer_script_sha256=receipt['context']['metric']['scorer_sha256'],note='Model weights and transitive dependency closure remain unknown; launch manifest is observer-authored and bound before execution.'))
verifier=execution.get('verdicts',{}).get('openssl-selfsigned-cert')
progress_path=run/'progress/round-0/openssl-selfsigned-cert.json'
progress=read(progress_path) if progress_path.exists() else {}
trace_paths=sorted((run/'progress/round-0/traces').glob('*.jsonl'))
usage=[]
for p in trace_paths:
    for line in p.read_text().splitlines():
        try: row=json.loads(line)
        except ValueError: continue
        if 'usage' in row: usage.append(dict(path=str(p),usage=row['usage']))
write('agent-execution-observation.json', dict(binding=binding,aggregate_tokens=execution.get('tokens'),aggregate_env_usage=execution.get('env_usage'),trace_usage=usage,progress_path=str(progress_path),harness_output=progress.get('harness_output'),note='Agent trace usage and gateway transport counters are separate from environment-service spend. No model completion probe was sent for this launch.'))

ctrfs=[]
for p in sorted(evidence.glob('verifier-ctrf.json-*')):
    try: parsed=read(p)
    except ValueError: continue
    if parsed.get('results',{}).get('summary'):
        ctrfs.append(dict(path=str(p),sha256=sha(p),summary=parsed['results']['summary']))
result=write('result.json',dict(binding=binding,driver_returncode=read(evidence/'launch-observation.json')['returncode'],verifier_verdict=verifier,raw_per_task=execution.get('per_task'),invalid=execution.get('invalid'),raw_reward_files={str(p):p.read_text() for p in sorted(evidence.glob('verifier-reward.txt-*'))},ctrf_files=ctrfs,coverage=receipt['coverage'],driver_score=receipt['score'],outcomes=receipt['outcomes'],enforcement=receipt['enforcement'],observation_receipts={k:dict(path=str(p),sha256=sha(p)) for k,p in [('resource',resource),('snapshot',snapshot),('image',image),('cleanup',cleanup),('provenance',provenance)]},curve_present=(run/'curve.jsonl').exists()))
# Preserve review copies with the original layout and complete byte inventory.
for directory in (run,evidence):
    dest=OUT/('execution' if directory==run else 'launch')
    shutil.copytree(directory,dest,dirs_exist_ok=False,ignore=(shutil.ignore_patterns('container-inspect-*.json','container-stats-*.json','snapshot-inspect-*.json') if directory==evidence else None))
files=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for directory in (run,evidence) for p in sorted(directory.rglob('*')) if p.is_file()]
(OUT/'artifact-inventory.json').write_text(json.dumps(dict(files=files),indent=2)+'\n')
archive=OUT/'run-artifacts.tar.gz'
with tarfile.open(archive,'w:gz') as tar:
    for directory in (run,evidence): tar.add(directory,arcname=str(directory.relative_to(ROOT)))
(OUT/'archive-sha256.json').write_text(json.dumps(dict(path=str(archive),sha256=sha(archive),bytes=archive.stat().st_size,original_directories=[str(run),str(evidence)]),indent=2)+'\n')
print(json.dumps(read(result),indent=2))
