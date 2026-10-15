"""Account for observed operator sharing while proving serial worker intervals."""
import hashlib,json,pathlib,subprocess
repo=pathlib.Path(__file__).resolve().parents[2];packet=repo/'reports/w-tb89d-evidence'
def read(p):return json.loads(p.read_text())
roots=[pathlib.Path(r) for r in read(packet/'review-batch.json')['runs_roots']];foreign={};rows=[]
for ev in [ev for root in roots for ev in root.glob('*-evidence')]:
 if not (ev/'driver-process.json').is_file():continue
 own=read(ev/'driver-process.json')['pid']
 if (ev/'launch-observation.json').exists():rows.append(read(ev/'launch-observation.json'))
 else:rows.append(dict(started_at=read(ev/'driver-process.json')['started_at'],ended_at=read(ev/'interrupted-disposition.json')['observed_at']))
 for f in ev.glob('processes-sample-*.json'):
  raw=read(f);assert raw['returncode']==0,f
  for line in raw['stdout'].splitlines():
   parts=line.split()
   if len(parts)<=2 or 'python' not in parts[1] or not any(pathlib.Path(a).name=='driver.py' for a in parts[2:]) or int(parts[0])==own:continue
   item=foreign.setdefault(parts[0],dict(pid=int(parts[0]),process_line=line,samples=[]))
   assert item['process_line']==line
   item['samples'].append(dict(path=str(f),sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
   if '--run-id musique-full-qwen-t1-train' in line:
    meta_path=ev/'operator-run-meta.json'
    if not meta_path.exists():meta_path=next(roots[0].glob('*-evidence/operator-run-meta.json'))
    meta_raw=read(meta_path);assert meta_raw['returncode']==0
    meta=json.loads(meta_raw['stdout']);assert meta['run_id']=='musique-full-qwen-t1-train'
    assert meta['config']['agent']['base_url']=='http://127.0.0.1:8010/v1'
    item['classification']='Pre-existing operator run on 8010 proxy to 8001/8002; sharing explicitly permitted by user. Worker concurrency one, direct 8002 only.'
   else:
    args=parts[1:];meta_path=pathlib.Path(args[args.index('--runs-root')+1])/args[args.index('--run-id')+1]/'run_meta.json'
    result=subprocess.run(['cat',str(meta_path)],capture_output=True,text=True)
    meta_raw=dict(argv=['cat',str(meta_path)],returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
    assert result.returncode==0
    meta=json.loads(result.stdout)
    assert meta['dataset']=='verify_demo' and meta['agent_backend']=='mock'
    assert meta['config']['agent']['backend']=='mock' and not meta['config']['agent']['model'] and not meta['config']['agent']['base_url']
    assert meta['env']['model_gateway'] is None and meta['config']['environment']['model'] is None
    assert meta['config']['method']['model'] is None and meta['config']['improver']['model'] is None
    item['classification']='Foreign pytest verify_demo synthetic driver; retained metadata proves mock backend and no model/endpoint/gateway.'
   item['run_meta_raw']=meta_raw

rows.sort(key=lambda r:r['started_at'])
for a,b in zip(rows,rows[1:]):assert a['ended_at']<=b['started_at']
result=dict(foreign_drivers=list(foreign.values()),worker_serial=True,operator_endpoint_sharing_observed=bool(foreign),routing_observation=read(packet/'operator-routing-observation.json'),note='No endpoint exclusivity claimed; operator processes left untouched. No platform gate/admission/refusal changed.')
with (packet/'concurrency-audit.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(dict(foreign_drivers=len(foreign),worker_serial=True,operator_sharing_permitted=True),indent=2))
