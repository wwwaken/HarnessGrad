"""Preselect three fresh pip-route task surfaces and verify bootstrap without scoring."""
import ast,datetime,json,pathlib,secrets,subprocess
repo=pathlib.Path(__file__).resolve().parents[2]
packet=pathlib.Path(json.loads((repo/'reports/w-tb89e-evidence/location.json').read_text())['raw_root'])
dataset=pathlib.Path('/mnt/20t/xubuqiang/datasets/terminal-bench')
inv=json.loads((packet/'inventory.json').read_text())
def write(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def cap(name,args,timeout=240):
 r=subprocess.run(args,cwd=repo,capture_output=True,text=True,timeout=timeout)
 write(packet/(name+'.json'),dict(argv=args,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));return r
prior=cap('prior-tb89d',['git','show','HEAD:reports/w-tb89d-evidence/result.json']);assert prior.returncode==0
prior=json.loads(prior.stdout)
prior_measured=['cancel-async-tasks','db-wal-recovery','extract-elf','fix-git','git-leak-recovery','openssl-selfsigned-cert','polyglot-c-py','regex-log','sanitize-git-repo']+[r['task_id'] for r in prior['rows'] if r['raw_measured']]
# Purposeful independent surfaces using pip instead of the known uv asset gap.
selected=['build-cython-ext','headless-terminal','largest-eigenval']
metadata=[r['task_id'] for r in inv['rows'] if r['image_present'] and not r['missing_source'] and r['environment']['gpus']==0 and not r['environment'].get('mcp_servers') and r['environment']['cpus']<=1 and r['environment']['memory_mb']<=2048 and r['agent']['timeout_sec']<=900 and r['verifier']['timeout_sec']<=900]
assert set(selected)<=set(metadata) and not set(selected)&set(prior_measured) and not set(selected)&{r['task_id'] for r in prior['rows']}
runs=pathlib.Path('/tmp')/('w-tb89e-runs-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+secrets.token_hex(4));runs.mkdir()
rule='Fixed three previously unattempted pip-route surfaces among cached metadata-bounded tasks: Cython extension build, headless interactive terminal and dominant eigenpair implementation. Avoid the previously observed uv release asset bootstrap gap and tasks requiring a model server. Require complete official source, shell/Python parse, no GPU/MCP, <=1 CPU/2048 MiB and declared timeouts <=900s. Bootstrap exact scorer dependencies in disposable containers before any trial, without official tests/reference solutions/model. No result-dependent substitution, rerun or performance sample. Three tasks are within ceil(10% of 89)=9.'
batch=dict(runs_root=str(runs),selected=selected,selection_rule=rule,endpoint='http://127.0.0.1:8002/v1',model='qwen3.5-9b-local',metadata_candidates=metadata,prior_measured=prior_measured,cached_unmeasured_before=len([r for r in inv['rows'] if r['image_present'] and r['task_id'] not in prior_measured]),cached_unmeasured_outside_selection=len([r for r in inv['rows'] if r['image_present'] and r['task_id'] not in prior_measured+selected]),metadata_unmeasured_outside_selection=len(set(metadata)-set(prior_measured)-set(selected)))
write(packet/'batch.json',batch)
for tid in selected:
 row=next(r for r in inv['rows'] if r['task_id']==tid)
 q=cap('shell-syntax-'+tid,['bash','-n',str(dataset/tid/'tests/test.sh')]);assert q.returncode==0
 for f in (dataset/tid/'tests').rglob('*.py'):ast.parse(f.read_text(),filename=str(f))
 check='command -v bash; command -v pip; command -v python; test "$PWD" != /'
 if tid=='headless-terminal':check+='; test -s /app/base_terminal.py; command -v tmux; command -v screen; command -v expect'
 if tid=='largest-eigenval':check+='; test -s /app/eigen.py; test -s /app/eval.py'
 if tid=='build-cython-ext':check+='; command -v git; command -v gcc'
 q=cap('prerequisite-'+tid,['docker','run','--rm','--pull=never','--network','none','--read-only','--cpus','1','--memory','2048m','--pids-limit','128','--entrypoint','/bin/sh',row['image_id'],'-ec',check]);assert q.returncode==0
 bootstrap='pip install pytest==8.4.1 pytest-json-ctrf==0.3.5'
 if tid=='headless-terminal':bootstrap='apt-get update && apt-get install -y vim && '+bootstrap+' requests==2.32.5'
 if tid=='largest-eigenval':bootstrap+=' --break-system-packages'
 bootstrap+='\npython -m pytest --version\npython -m pytest --help\npython -c "import importlib.metadata; print(importlib.metadata.version(\'pytest-json-ctrf\'))"'
 args=['docker','run','--rm','--pull=never','--network','bridge','--cpus','1','--memory','2048m','--pids-limit','128']
 for k in ('HTTP_PROXY','HTTPS_PROXY','http_proxy','https_proxy'):args+=['-e',k+'=http://172.17.0.1:17890']
 args+=['-e','NO_PROXY=localhost,127.0.0.1,::1','-e','no_proxy=localhost,127.0.0.1,::1','--entrypoint','/bin/sh',row['image_id'],'-ec',bootstrap]
 q=cap('dependency-bootstrap-'+tid,args);assert q.returncode==0 and '--ctrf' in q.stdout
write(packet/'prerequisites-complete.json',dict(selected=selected,verified=selected,queued=len(selected),observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat()))
print(json.dumps(batch,indent=2))
