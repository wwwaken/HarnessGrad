import datetime, hashlib, json, os, pathlib, secrets, shlex, shutil, subprocess, sys, time, urllib.request
root = pathlib.Path('/tmp/hg-tbrun4')
run_id = 'w-tbrun4-terminal-bench-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + secrets.token_hex(4)
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
# Observer-authored launch manifest, written before execution; not an admission attestation.
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
source_files = {str(p.relative_to(task_root)): sha(p) for p in sorted(task_root.rglob('*')) if p.is_file() and (p.name == 'task.toml' or 'tests' in p.parts or p.name == 'instruction.md' or p.name == 'Dockerfile')}
harness_root = root/'base_harness/loop'
harness_files = {str(p.relative_to(harness_root)): sha(p) for p in sorted(harness_root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and '.git' not in p.parts}
write('source-files.json', source_files)
write('harness-files.json', harness_files)
write('split-selection.json', dict(HG_TB_SPLIT='none', split=None, selected_task_ids=selection['task_ids']))
write('launch-manifest.json', dict(kind='observer-authored pre-execution launch manifest, not an admission attestation', run_id=run_id, trial_id='openssl-selfsigned-cert:1', selection=selection, image_id=images[0]['Id'], image_repo_digests=images[0]['RepoDigests'], platform_commit=json.loads((evidence/'platform-commit.json').read_text())['stdout'].strip(), dataset_commit=json.loads((evidence/'dataset-commit.json').read_text())['stdout'].strip(), source_files_sha256=sha(evidence/'source-files.json'), harness_files_sha256=sha(evidence/'harness-files.json'), split_sha256=sha(evidence/'split-selection.json'), endpoint='http://127.0.0.1:8002/v1', model='qwen3.5-9b-local', model_weights_sha256=None, egress_proxy='http://172.17.0.1:17890', rounds=0, trials=1, jobs=1, work_root=str(work), runs_root=str(runs), harness='loop', side='train'))
policy['context']['hashes'].update(source=sha(evidence/'source-files.json'), split=sha(evidence/'split-selection.json'), harness=sha(evidence/'harness-files.json'), manifest=sha(evidence/'launch-manifest.json'))
policy['context']['comparability_notes'] += ['Scorer hash binds test.sh only, not transitive dependencies. This is a fresh rounds=0 attempt, not a resume of w-tbrun.']
diagnostic_policy.validate_context(policy['context'])
write('policy-input.json',policy)
env_values=dict(HG_EGRESS_PROXY='http://172.17.0.1:17890',HG_TB_TASKS='openssl-selfsigned-cert',HG_TB_SPLIT='none',HG_AGENT_BACKEND='openai',HG_AGENT_MODEL='qwen3.5-9b-local',HG_AGENT_BASE_URL='http://127.0.0.1:8002/v1',HG_AGENT_API_KEY='local')
reason='Operator explicitly requests one real cached openssl-selfsigned-cert diagnostic with HG_TB_SPLIT=none and the documented verifier egress proxy to obtain CTRF and a raw verifier score; runtime observations remain incomplete, with no comparable score publication, pilot expansion or production authorization.'
argv=['python3','driver.py','--harness','loop','--dataset','terminal_bench','--sampling','diagnostic','--policy-evidence',str(evidence/'policy-input.json'),'--authorize-unobserved-diagnostic',reason,'--rounds','0','--trials','1','--jobs','1','--side','train','--improver','none','--run-id',run_id,'--runs-root',str(runs),'--work-root',str(work)]
(evidence/'command.txt').write_text(shlex.join(['env']+[f'{k}={v}' for k,v in env_values.items()]+argv)+'\n')
write('launch-input.json',dict(cwd=str(root),argv=argv,environment=env_values,rounds=0,trials=1,jobs=1,task_id='openssl-selfsigned-cert',endpoint_verified=True))
capture('containers-before.json',['docker','ps','-a','--no-trunc','--filter',f'label=harnessgrad.run={run_id}','--format','{{json .}}'])
capture('networks-before.json',['docker','network','ls','--no-trunc','--filter',f'label=harnessgrad.run={run_id}','--format','{{json .}}'])
capture('disk-preflight.json',['df','-B1','/','/tmp'])
capture('h0-processes-preflight.json',['ps','-eo','pid,args'])
for name, url in [('proxy-astral.json','https://astral.sh/uv/0.9.5/install.sh'), ('proxy-pypi.json','https://pypi.org/simple/')]:
    p=capture(name, ['curl','--max-time','25','-x','http://172.17.0.1:17890','-LsS','-o','/dev/null','-w','%{http_code}',url])
    assert p.returncode == 0 and p.stdout == '200', name
start=datetime.datetime.now(datetime.timezone.utc)
# Preserve verifier bind files while they exist; no writes into runtime containers.
import threading
observations=[]
observer_stop=threading.Event()
def observe():
    while not observer_stop.is_set():
        try:
            p=subprocess.run(['docker','ps','-aq','--filter',f'label=harnessgrad.run={run_id}'],capture_output=True,text=True,timeout=20)
            if p.stdout.strip():
                q=subprocess.run(['docker','inspect',*p.stdout.split()],capture_output=True,text=True,timeout=20)
                if q.returncode == 0:
                    for c in json.loads(q.stdout):
                        if not c['Name'].startswith('/hg-verify-'): continue
                        for m in c['Mounts']:
                            if m['Destination'] != '/logs/verifier': continue
                            for name in ('reward.txt','ctrf.json'):
                                f=pathlib.Path(m['Source'])/name
                                try: data=f.read_bytes()
                                except OSError: continue
                                digest=hashlib.sha256(data).hexdigest()
                                dst=evidence/f'verifier-{name}-{digest}'
                                if not dst.exists():
                                    dst.write_bytes(data)
                                    observations.append(dict(observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),container_id=c['Id'],source=str(f),copy=str(dst),sha256=digest,bytes=len(data)))
                                    write('verifier-file-observations.json',observations)
        except Exception as exc:
            with (evidence/'observer-errors.txt').open('a') as stream: stream.write(repr(exc)+'\n')
        observer_stop.wait(0.1)
observer_thread=threading.Thread(target=observe,daemon=True)
observer_thread.start()
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
observer_stop.set()
observer_thread.join(timeout=25)
write('verifier-observer-completion.json',dict(file_observations=len(observations)))
write('launch-observation.json',dict(returncode=code,started_at=start.isoformat(),ended_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),driver_pid=child.pid,run_id=run_id,run_dir_exists=run_dir.exists(),work_root_exists=work.exists(),endpoint_binding={k:v for k,v in env_values.items() if k!='HG_AGENT_API_KEY'}))
capture('containers-after.json',['docker','ps','-a','--no-trunc','--filter',f'label=harnessgrad.run={run_id}','--format','{{json .}}'])
capture('networks-after.json',['docker','network','ls','--no-trunc','--filter',f'label=harnessgrad.run={run_id}','--format','{{json .}}'])
capture('snapshot-images-after.json',['docker','image','ls','--no-trunc','--filter',f'reference=hg-snapshot:*{run_id}*','--format','{{json .}}'])
print(json.dumps(dict(returncode=code,run_dir=str(run_dir),evidence=str(evidence))),flush=True)
