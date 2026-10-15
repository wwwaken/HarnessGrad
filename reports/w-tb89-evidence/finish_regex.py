"""Correct the overly strict probe assumption; preserve its failed identity intact.

python3 absent on PATH is not a route refusal: container_state.py supports a host
interpreter. Attempt the requested unchanged driver once under a new identity.
"""
import datetime, hashlib, json, os, pathlib, secrets, shlex, subprocess
repo=pathlib.Path(__file__).resolve().parents[2]
packet=repo/'reports/w-tb89-evidence'
batch=json.loads((packet/'batch.json').read_text()); runs=pathlib.Path(batch['runs_root'])
row=next(r for r in json.loads((packet/'inventory.json').read_text())['rows'] if r['task_id']=='regex-log')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
    with p.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
def capture(name,argv):
    p=subprocess.run(argv,cwd=repo,capture_output=True,text=True,timeout=45)
    write(ev/(name+'.json'),dict(argv=argv,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr));return p
rid='w-tb89-regex-log-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+secrets.token_hex(4)
ev=runs/(rid+'-evidence');ev.mkdir(exist_ok=False)
work=pathlib.Path('/tmp')/(rid+'-work');run=runs/rid
assert not work.exists() and not run.exists()
write(ev/'identity.json',dict(run_id=rid,task_id='regex-log',run_dir=str(run),work_root=str(work),evidence_dir=str(ev)))
td=pathlib.Path('/mnt/20t/xubuqiang/datasets/terminal-bench/regex-log')
hr=repo/'base_harness/loop'
write(ev/'source-files.json',{str(p.relative_to(td)):sha(p) for p in sorted(td.rglob('*')) if p.is_file() and ('tests' in p.parts or p.name in ('task.toml','instruction.md','Dockerfile'))})
write(ev/'harness-files.json',{str(p.relative_to(hr)):sha(p) for p in sorted(hr.rglob('*')) if p.is_file() and '__pycache__' not in p.parts})
write(ev/'split.json',dict(HG_TB_SPLIT='none',split=None,selected=['regex-log']))
env=dict(HG_EGRESS_PROXY='http://172.17.0.1:17890',HG_TB_TASKS='regex-log',HG_TB_SPLIT='none',HG_AGENT_BACKEND='mock',HG_AGENT_MODEL='',HG_AGENT_BASE_URL='',HG_AGENT_API_KEY='',HG_AGENT_MAX_STEPS='1',CUDA_VISIBLE_DEVICES='')
write(ev/'launch-manifest.json',dict(kind='observer pre-execution binding; not admission evidence',run_id=rid,task_id='regex-log',trial=1,image_id=row['image_id'],repo_digests=row['repo_digests'],endpoint=None,model=None,environment=env,source_sha256=sha(ev/'source-files.json'),split_sha256=sha(ev/'split.json'),harness_sha256=sha(ev/'harness-files.json')))
first=next(p for p in sorted(runs.glob('*-evidence/policy-input.json')))
policy=json.loads(first.read_text());c=policy['context']
c['metric']['scorer_sha256']=sha(td/'tests/test.sh')
c['hashes'].update(source=sha(ev/'source-files.json'),split=sha(ev/'split.json'),harness=sha(ev/'harness-files.json'),manifest=sha(ev/'launch-manifest.json'))
c['comparability_notes'].append('Earlier regex-log preflight stopped at missing python3; platform host-interpreter fallback means that probe does not establish inability to run. This is a fresh driver attempt, with no old identity resumed.')
write(ev/'policy-input.json',policy)
reason='Operator explicitly authorizes a bounded handful of fresh local no-model Terminal-Bench diagnostic controls for S4 broader execution evidence. One selected regex-log task, mock backend only, HG_TB_SPLIT=none and documented egress proxy; unknown enforcement stays unknown; no pilot expansion, blocker closure or production authorization.'
argv=['python3','driver.py','--harness','loop','--dataset','terminal_bench','--sampling','diagnostic','--policy-evidence',str(ev/'policy-input.json'),'--authorize-unobserved-diagnostic',reason,'--rounds','0','--trials','1','--jobs','1','--side','train','--improver','none','--run-id',rid,'--runs-root',str(runs),'--work-root',str(work)]
(ev/'command.txt').write_text(shlex.join(['env']+[k+'='+v for k,v in env.items()]+argv)+'\n')
write(ev/'launch-input.json',dict(argv=argv,cwd=str(repo),environment=env,endpoint=None,model=None))
capture('image-inspect',['docker','image','inspect',row['image_ref']])
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (ev/'driver.stdout.txt').open('w') as out,(ev/'driver.stderr.txt').open('w') as err:
    p=subprocess.run(argv,cwd=repo,env={**os.environ,**env},stdout=out,stderr=err,timeout=60)
write(ev/'launch-observation.json',dict(returncode=p.returncode,started_at=started,ended_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),endpoint=None,model=None,run_exists=run.exists(),work_exists=work.exists()))
for label,args in [('containers',['docker','ps','-a']),('networks',['docker','network','ls']),('volumes',['docker','volume','ls'])]:
    capture(label+'-after',args+['--filter','label=harnessgrad.run='+rid,'--format','{{json .}}'])
capture('snapshots-after',['docker','image','ls','--filter','reference=hg-snapshot:*'+rid+'*','--no-trunc','--format','{{json .}}'])
print(json.dumps(dict(task_id='regex-log',run_id=rid,evidence=str(ev),returncode=p.returncode,stderr=(ev/'driver.stderr.txt').read_text(),run_exists=run.exists(),work_exists=work.exists())))
