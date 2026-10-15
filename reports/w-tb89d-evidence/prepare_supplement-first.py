"""Fix two additional pip-bootstrap surfaces after retaining uv-bootstrap failures."""
import ast,datetime,json,pathlib,secrets,subprocess
repo=pathlib.Path(__file__).resolve().parents[2];packet=repo/'reports/w-tb89d-evidence';dataset=pathlib.Path('/mnt/20t/xubuqiang/datasets/terminal-bench');inv=json.loads((packet/'inventory.json').read_text())
checks={
 'fix-code-vulnerability':('command -v bash; command -v sh; command -v python; command -v pip; command -v git; test -s /app/bottle.py; test -d /app/test', 'pip install pytest==8.4.1 pytest-json-ctrf==0.3.5\npython -m pytest --version\npython -c "import pytest,pytest_json_ctrf; print(pytest.__version__); print(pytest_json_ctrf.__file__)"'),
 'kv-store-grpc':('command -v bash; command -v sh; command -v python; command -v pip; test -d /app', 'pip install pytest==8.4.2 requests==2.32.5 psutil==7.0.0 pytest-json-ctrf==0.3.5 grpcio==1.73.0 grpcio-tools==1.73.0\npython -m pytest --version\npython -c "import pytest,pytest_json_ctrf,requests,psutil,grpc,grpc_tools; print(pytest.__version__); print(grpc.__version__)"')}
def cap(name,args,timeout=180):
 r=subprocess.run(args,cwd=repo,capture_output=True,text=True,timeout=timeout)
 with (packet/(name+'.json')).open('x') as f:json.dump(dict(argv=args,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr),f,indent=2);f.write('\n')
 assert r.returncode==0,(name,r.stderr[-2000:]);return r
verified=[]
for tid,(check,bootstrap) in checks.items():
 row=next(r for r in inv['rows'] if r['task_id']==tid);e=row['environment'];assert row['image_present'] and not row['missing_source'] and e['gpus']==0 and not e['mcp_servers'] and e['cpus']<=1 and e['memory_mb']<=2048 and row['agent']['timeout_sec']<=900 and row['verifier']['timeout_sec']<=900
 cap('shell-syntax-'+tid,['bash','-n',str(dataset/tid/'tests/test.sh')])
 for f in (dataset/tid/'tests').rglob('*.py'):ast.parse(f.read_text(),filename=str(f))
 cap('prerequisite-'+tid,['docker','run','--rm','--pull=never','--network','none','--read-only','--cpus','1','--memory','2048m','--pids-limit','128','--entrypoint','/bin/sh',row['image_id'],'-ec',check])
 # Bootstrap-only dependency readiness: no model, official tests, answer or scoring.
 args=['docker','run','--rm','--pull=never','--network','bridge','--cpus','1','--memory','2048m','--pids-limit','128']
 for k in ('HTTP_PROXY','HTTPS_PROXY','http_proxy','https_proxy'):args+=['-e',k+'=http://172.17.0.1:17890']
 args+=['-e','NO_PROXY=localhost,127.0.0.1,::1','-e','no_proxy=localhost,127.0.0.1,::1','--entrypoint','/bin/sh',row['image_id'],'-ec',bootstrap]
 cap('dependency-bootstrap-'+tid,args)
 verified.append(tid)
runroot=pathlib.Path('/tmp')/('w-tb89d-supplement-runs-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+secrets.token_hex(4));runroot.mkdir(exist_ok=False)
first=json.loads((packet/'batch.json').read_text());assert len(first['selected'])+len(verified)<=9 and not set(first['selected'])&set(verified)
batch=dict(runs_root=str(runroot),selected=verified,selection_rule='Two additional new cached surfaces: Bottle vulnerability repair with original/additional official tests, and gRPC key/value service construction. Fixed before either model trial, after a no-model probe identified the initial uv release-download gap. Same immutable cache/source/shell/Python/CPU/memory/GPU/MCP/timeout bounds; additionally run the exact pinned pip test-dependency installation and import/version smoke checks in disposable images with the documented proxy. No official tests/solutions or model are used in probes. Initial five attempts are retained, never replaced or rerun. Total preselected new task surfaces across both batches is seven, within ceil(10% * 89)=9. This is purposeful execution coverage, no performance sample.',endpoint=first['endpoint'],model=first['model'],total_serial_tasks=len(verified),metadata_candidates=first['metadata_candidates'],prerequisite_verified=verified,prerequisite_verified_not_selected=[],cached_unselected=inv['cached_images']-len(first['selected'])-len(verified),note='Pip-route bootstrap verified end to end before these two trials. Initial five local probes passed but transitive uv download readiness did not; all failures remain invalid, excluded from coverage.')
with (packet/'batch-supplement.json').open('x') as f:json.dump(batch,f,indent=2);f.write('\n')
print(json.dumps(batch,indent=2))
