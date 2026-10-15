"""Identify every foreign sampled driver; require retained proof of no model use."""
import hashlib, json, pathlib, subprocess
repo=pathlib.Path(__file__).resolve().parents[2]; packet=repo/'reports/w-tb89c-evidence'
def read(p):return json.loads(p.read_text())
root=pathlib.Path(read(packet/'batch.json')['runs_root']); foreign={}
for ev in root.glob('*-evidence'):
    own=read(ev/'driver-process.json')['pid']
    for f in ev.glob('processes-sample-*.json'):
        for line in read(f)['stdout'].splitlines():
            parts=line.split()
            if len(parts)<=2 or 'python' not in parts[1] or not any(pathlib.Path(a).name=='driver.py' for a in parts[2:]) or int(parts[0])==own:continue
            item=foreign.setdefault(parts[0],dict(pid=int(parts[0]),process_line=line,samples=[]))
            assert item['process_line']==line
            item['samples'].append(dict(path=str(f),sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
for item in foreign.values():
    args=item['process_line'].split()
    m=pathlib.Path(args[args.index('--runs-root')+1])/args[args.index('--run-id')+1]/'run_meta.json'
    r=subprocess.run(['cat',str(m)],capture_output=True,text=True)
    item['run_meta_raw']=dict(argv=['cat',str(m)],returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)
    assert r.returncode==0
    meta=json.loads(r.stdout)
    assert meta['dataset']=='verify_demo' and meta['agent_backend']=='mock'
    assert meta['config']['agent']['backend']=='mock' and meta['config']['agent']['model'] is None and not meta['config']['agent']['base_url']
    assert meta['env']['model_gateway'] is None and meta['config']['environment']['model'] is None
    assert meta['config']['method']['model'] is None and meta['config']['improver']['model'] is None
    item['classification']='Other worktree pytest synthetic verify_demo driver; mock backend and no endpoint/model/gateway configured.'
result=dict(foreign_drivers=list(foreign.values()),other_endpoint_driver_observed=False,note='All sampled foreign drivers accounted for above; arbitrary direct clients and endpoint reservation remain unobserved.')
with (packet/'concurrency-audit.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(dict(foreign_drivers=len(foreign),all_foreign_synthetic_mock=True),indent=2))
