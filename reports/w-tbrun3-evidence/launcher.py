import datetime, hashlib, json, os, pathlib, secrets, shlex, shutil, subprocess, sys, time, urllib.request
root = pathlib.Path('/tmp/hg-tbrun3')
run_id = 'w-tbrun3-terminal-bench-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + secrets.token_hex(4)
runs = root / 'runs'
evidence = runs / (run_id + '-launch-evidence')
evidence.mkdir(parents=True, exist_ok=False)
run_dir = runs / run_id
work = pathlib.Path('/tmp') / (run_id + '-work')
assert not run_dir.exists() and not work.exists()
def write(name, value):
    (evidence / name).write_text(json.dumps(value, indent=2) + '\n')
def capture(name, argv):
    p = subprocess.run(argv, capture_output=True, text=True, timeout=30, cwd=root)
    write(name, dict(argv=argv, returncode=p.returncode, stdout=p.stdout, stderr=p.stderr))
    return p
write('identity.json', dict(run_id=run_id, run_dir=str(run_dir), evidence_dir=str(evidence), work_root=str(work), launcher=str(pathlib.Path(__file__).resolve())))
print(json.dumps(dict(run_id=run_id,evidence=str(evidence))), flush=True)
shutil.copy2(__file__, evidence / 'launcher.py')
capture('platform-status.json', ['git','status','--short'])
capture('platform-commit.json', ['git','rev-parse','HEAD'])
capture('dataset-commit.json', ['git','-C','/mnt/20t/xubuqiang/datasets/terminal-bench','rev-parse','HEAD'])
capture('dataset-status.json', ['git','-C','/mnt/20t/xubuqiang/datasets/terminal-bench','status','--short'])
capture('cached-jevloop-images.json', ['docker','images','--no-trunc','jevloop-tb'])
p = capture('image-inspect.json', ['docker','image','inspect','alexgshaw/openssl-selfsigned-cert:20251031','jevloop-tb:openssl-selfsigned-cert'])
assert p.returncode == 0
images=json.loads(p.stdout)
assert images[0]['Id'] == images[1]['Id']
task_root=pathlib.Path('/mnt/20t/xubuqiang/datasets/terminal-bench/openssl-selfsigned-cert')
for src, dst in [('task.toml','selected-task.toml'),('environment/Dockerfile','selected-Dockerfile'),('tests/test.sh','selected-verifier-test.sh')]:
    shutil.copy2(task_root / src, evidence / dst)
shutil.copy2(root/'base_harness/loop/harness.json', evidence/'harness-descriptor.json')
with urllib.request.urlopen('http://127.0.0.1:8002/v1/models',timeout=15) as response:
    data=response.read()
    (evidence/'endpoint-models.json').write_bytes(data)
    available=any(m['id']=='qwen3.5-9b-local' for m in json.loads(data)['data'])
    write('endpoint-probe.json',dict(url=response.url,http_status=response.status,requested_model_available=available))
    assert response.status==200 and available
request_body = dict(model='qwen3.5-9b-local', messages=[dict(role='user',content='Reply with OK.')], max_tokens=16, temperature=0, chat_template_kwargs=dict(enable_thinking=False))
write('endpoint-completion-request.json',request_body)
request=urllib.request.Request('http://127.0.0.1:8002/v1/chat/completions',data=json.dumps(request_body).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer local'})
with urllib.request.urlopen(request,timeout=60) as response:
    completion=response.read()
    (evidence/'endpoint-completion-response.json').write_bytes(completion)
    write('endpoint-completion-probe.json',dict(url=response.url,http_status=response.status))
    assert json.loads(completion)['choices']
sys.path.insert(0,str(root))
os.environ['HG_TB_TASKS']='openssl-selfsigned-cert'
os.environ['HG_TB_SPLIT']='none'
from data.datasets import terminal_bench as tb
from eval.policy import diagnostic_policy
selection=dict(task_ids=[t['task_id'] for t in tb.load()[0]], split=tb.SPLIT, environment=tb.ENV['openssl-selfsigned-cert'])
write('selection.json', selection)
assert selection['task_ids']==['openssl-selfsigned-cert'] and tb.SPLIT is None
policy=json.loads(pathlib.Path('/tmp/hg-tbrun/reports/w-tbrun-evidence/policy-input.json').read_text())
policy['context']['comparability_notes'] = ['Single cached task, HG_TB_SPLIT=none; train CLI flag required by driver.py unobserved-diagnostic guard; no improver and no generalization or production claim.', 'All unknown gate, budget and provenance input fields remain null; raw scorer output is distinct from publication permission.']
policy['context']['metric']['scorer_sha256']=hashlib.sha256((task_root/'tests/test.sh').read_bytes()).hexdigest()
policy['context']['comparability_notes'] += ['Scorer hash binds test.sh only, not transitive dependencies. This is a fresh rounds=0 attempt, not a resume of w-tbrun.']
diagnostic_policy.validate_context(policy['context'])
write('policy-input.json',policy)
env_values=dict(HG_TB_TASKS='openssl-selfsigned-cert',HG_TB_SPLIT='none',HG_AGENT_BACKEND='openai',HG_AGENT_MODEL='qwen3.5-9b-local',HG_AGENT_BASE_URL='http://127.0.0.1:8002/v1',HG_AGENT_API_KEY='local')
reason='Operator explicitly requests one cached Terminal-Bench task with HG_TB_SPLIT=none at round 0 to obtain its real verifier reward and lifecycle artifacts; backend enforcement observations remain absent, with no production authorization or comparable score publication.'
argv=['python3','driver.py','--harness','loop','--dataset','terminal_bench','--sampling','diagnostic','--policy-evidence',str(evidence/'policy-input.json'),'--authorize-unobserved-diagnostic',reason,'--rounds','0','--trials','1','--jobs','1','--side','train','--improver','none','--run-id',run_id,'--runs-root',str(runs),'--work-root',str(work)]
(evidence/'command.txt').write_text(shlex.join(['env']+[f'{k}={v}' for k,v in env_values.items()]+argv)+'\n')
write('launch-input.json',dict(cwd=str(root),argv=argv,environment=env_values,rounds=0,trials=1,jobs=1,task_id='openssl-selfsigned-cert',endpoint_verified=True))
capture('containers-before.json',['docker','ps','-a','--no-trunc','--filter',f'label=harnessgrad.run={run_id}','--format','{{json .}}'])
capture('networks-before.json',['docker','network','ls','--no-trunc','--filter',f'label=harnessgrad.run={run_id}','--format','{{json .}}'])
capture('disk-preflight.json',['df','-B1','/','/tmp'])
capture('h0-processes-preflight.json',['ps','-eo','pid,args'])
start=datetime.datetime.now(datetime.timezone.utc)
with (evidence/'docker-events.jsonl').open('w') as events, (evidence/'docker-events.stderr.txt').open('w') as eventerr:
    eventproc=subprocess.Popen(['docker','events','--since',start.isoformat(),'--filter',f'label=harnessgrad.run={run_id}','--format','{{json .}}'],stdout=events,stderr=eventerr,text=True)
    with (evidence/'driver.stdout.txt').open('w') as out, (evidence/'driver.stderr.txt').open('w') as err:
        child=subprocess.Popen(argv,cwd=root,env={**os.environ,**env_values},stdout=out,stderr=err,text=True)
        write('launch-process.json',dict(pid=child.pid,started_at=start.isoformat()))
        count=0
        while child.poll() is None:
            p=subprocess.run(['docker','ps','-aq','--filter',f'label=harnessgrad.run={run_id}'],capture_output=True,text=True,timeout=30)
            ids=p.stdout.split()
            if ids:
                capture(f'container-inspect-{count:05d}.json',['docker','inspect','--size',*ids])
                capture(f'container-stats-{count:05d}.json',['docker','stats','--no-stream','--format','{{json .}}',*ids])
                count+=1
            images_p = subprocess.run(['docker','image','ls','--no-trunc','--filter',f'reference=hg-snapshot:*{run_id}*','--format','{{.ID}}'],capture_output=True,text=True,timeout=30)
            snapshot_ids = images_p.stdout.split()
            if snapshot_ids:
                capture(f'snapshot-inspect-{count:05d}.json',['docker','image','inspect',*snapshot_ids])
            time.sleep(1)
        code=child.wait()
    eventproc.terminate()
    eventproc.wait(timeout=15)
write('launch-observation.json',dict(returncode=code,started_at=start.isoformat(),ended_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),driver_pid=child.pid,run_id=run_id,run_dir_exists=run_dir.exists(),work_root_exists=work.exists(),endpoint_binding={k:v for k,v in env_values.items() if k!='HG_AGENT_API_KEY'}))
capture('containers-after.json',['docker','ps','-a','--no-trunc','--filter',f'label=harnessgrad.run={run_id}','--format','{{json .}}'])
capture('networks-after.json',['docker','network','ls','--no-trunc','--filter',f'label=harnessgrad.run={run_id}','--format','{{json .}}'])
capture('snapshot-images-after.json',['docker','image','ls','--no-trunc','--filter',f'reference=hg-snapshot:*{run_id}*','--format','{{json .}}'])
print(json.dumps(dict(returncode=code,run_dir=str(run_dir),evidence=str(evidence))),flush=True)
