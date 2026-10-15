"""Fresh raw inventory and endpoint observations; no benchmark execution."""
import datetime,json,pathlib,subprocess,sys,tomllib
repo=pathlib.Path(__file__).resolve().parents[2];packet=repo/'reports/w-tb89d-evidence'
root=pathlib.Path('/mnt/20t/xubuqiang/datasets/terminal-bench')
def write(n,d):
 with (packet/n).open('x') as f:json.dump(d,f,indent=2);f.write('\n')
def cap(n,args,timeout=60):
 r=subprocess.run(args,cwd=repo,capture_output=True,text=True,timeout=timeout)
 write(n+'.json',dict(argv=args,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));return r
for name,args in [('platform-commit',['git','rev-parse','HEAD']),('platform-status',['git','status','--short']),('dataset-commit',['git','-C',str(root),'rev-parse','HEAD']),('dataset-status',['git','-C',str(root),'status','--short']),('worktree-registration',['git','worktree','list','--porcelain']),('disk-before',['df','-B1','/','/tmp']),('processes-before',['ps','-eo','pid,args']),('blocker-check-before',['python3','tools/check_dataset_blockers.py']),('prior-tb89c-result',['git','show','HEAD:reports/w-tb89c-evidence/result.json']),('prior-tb89b-result',['git','show','HEAD:reports/w-tb89c-evidence/prior-tb89b-result.json']),('prior-openssl-result',['git','show','HEAD:reports/w-tb89c-evidence/prior-openssl-result.json'])]:
 r=cap(name,args);assert r.returncode==0
code="import json,pathlib; r=pathlib.Path("+repr(str(root))+");print(json.dumps({p.parent.name:p.read_text() for p in sorted(r.glob('*/task.toml'))}))"
r=cap('inventory-task-metadata-raw',['python3','-c',code]);assert r.returncode==0
rows=[]
for tid,raw in json.loads(r.stdout).items():
 m=tomllib.loads(raw);ref=m['environment']['docker_image'];q=cap('image-'+tid,['docker','image','inspect',ref]);imgs=json.loads(q.stdout) if q.returncode==0 else []
 rows.append(dict(task_id=tid,image_ref=ref,image_present=bool(imgs),image_id=imgs[0]['Id'] if imgs else None,repo_digests=imgs[0]['RepoDigests'] if imgs else [],environment=m['environment'],agent=m['agent'],verifier=m['verifier'],missing_source=[p for p in ('task.toml','instruction.md','environment/Dockerfile','tests/test.sh','tests/test_outputs.py') if not (root/tid/p).is_file()]))
inv=dict(total_task_references=len(rows),cached_images=sum(r['image_present'] for r in rows),missing_images=[r['task_id'] for r in rows if not r['image_present']],rows=rows)
write('inventory.json',inv)
r=cap('endpoint-models',['curl','--noproxy','*','--max-time','20','-sS','-w','\n%{http_code}','http://127.0.0.1:8002/v1/models']);body,status=r.stdout.rsplit('\n',1);assert r.returncode==0 and status=='200' and any(m['id']=='qwen3.5-9b-local' for m in json.loads(body)['data'])
payload=json.dumps(dict(model='qwen3.5-9b-local',messages=[dict(role='user',content='Reply OK.')],max_tokens=64,temperature=0,chat_template_kwargs=dict(enable_thinking=False)))
r=cap('endpoint-completion',['curl','--noproxy','*','--max-time','60','-sS','-w','\n%{http_code}','-H','Content-Type: application/json','-d',payload,'http://127.0.0.1:8002/v1/chat/completions']);body,status=r.stdout.rsplit('\n',1);assert r.returncode==0 and status=='200' and json.loads(body)['choices']
print(json.dumps({k:v for k,v in inv.items() if k!='rows'},indent=2));print('Local completion:',body)
