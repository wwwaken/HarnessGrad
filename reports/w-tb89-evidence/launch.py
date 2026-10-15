"""Four serial no-model controls through unchanged production diagnostic route."""
import datetime, hashlib, json, os, pathlib, secrets, shlex, shutil, subprocess, sys, threading, time

repo = pathlib.Path(__file__).resolve().parents[2]
packet = repo / 'reports/w-tb89-evidence'
sys.path.insert(0, str(repo))
from eval.policy import diagnostic_policy

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, value):
    with p.open('x') as f: json.dump(value, f, indent=2); f.write('\n')
def capture(where, name, argv, timeout=40):
    p = subprocess.run(argv, cwd=repo, capture_output=True, text=True, timeout=timeout)
    write(where / (name + '.json'), dict(argv=argv, returncode=p.returncode, stdout=p.stdout, stderr=p.stderr))
    return p

inventory = json.loads((packet/'inventory.json').read_text())
shortlist = ['cancel-async-tasks','fix-git','log-summary-date-ranges','regex-log']
selection_rule = 'Purposeful four-task surface diversity: async code, Git/file state, CSV aggregation and regex output; require cached image, complete local verifier sources, standard pytest/CTRF-only uvx bootstrap, zero GPU, no MCP/service prerequisite, <=1 CPU and <=2048 MiB. No result-dependent substitutions. Other cached tasks remain unexecuted, not certified runnable.'
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
runs = pathlib.Path('/tmp') / ('w-tb89-controls-' + stamp + '-' + secrets.token_hex(4))
runs.mkdir(exist_ok=False)
write(packet/'batch.json', dict(runs_root=str(runs), selected=shortlist, selection_rule=selection_rule, endpoint=None, model=None, total_serial_tasks=len(shortlist)))
shutil.copyfile(__file__, runs/'launch.py')
for tid in shortlist:
    row = next(r for r in inventory['rows'] if r['task_id']==tid)
    assert row['image_present'] and not row['missing_source']
    assert row['environment']['gpus']==0 and not row['environment'].get('mcp_servers')
    assert row['environment']['cpus']<=1 and row['environment']['memory_mb']<=2048
    run_id = 'w-tb89-' + tid + '-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + secrets.token_hex(4)
    ev = runs / (run_id + '-evidence'); ev.mkdir(exist_ok=False)
    work = pathlib.Path('/tmp') / (run_id + '-work')
    run = runs / run_id
    assert not run.exists() and not work.exists()
    write(ev/'identity.json', dict(run_id=run_id, task_id=tid, run_dir=str(run), work_root=str(work), evidence_dir=str(ev)))
    print(json.dumps(dict(starting=tid, run_id=run_id, evidence=str(ev))), flush=True)
    capture(ev,'processes-preflight',['ps','-eo','pid,args'])
    capture(ev,'image-inspect',['docker','image','inspect',row['image_ref']])
    probe_name = run_id + '-prereq'
    probe = capture(ev,'prerequisite-probe',['docker','run','--rm','--pull=never','--name',probe_name,'--network','none','--cpus','1','--memory','256m','--pids-limit','64','--entrypoint','/bin/bash',row['image_id'],'-lc','set -e; command -v bash; command -v apt-get; command -v python3; python3 --version; test -d /app; test -w /app'],timeout=60)
    capture(ev,'prerequisite-cleanup',['docker','inspect',probe_name])
    if probe.returncode:
        write(ev/'prerequisite-failure.json',dict(task_id=tid, reason='See exact prerequisite-probe.json stdout/stderr; not executed or counted as scorer evidence.'))
        continue
    for label,url in [('proxy-astral','https://astral.sh/uv/0.9.5/install.sh'),('proxy-pypi','https://pypi.org/simple/')]:
        p = capture(ev,label,['curl','--max-time','25','-x','http://172.17.0.1:17890','-LsS','-o','/dev/null','-w','%{http_code}',url])
        assert p.returncode==0 and p.stdout=='200', label
    td = pathlib.Path('/mnt/20t/xubuqiang/datasets/terminal-bench')/tid
    source = {str(p.relative_to(td)):sha(p) for p in sorted(td.rglob('*')) if p.is_file() and ('tests' in p.parts or p.name in ('instruction.md','task.toml','Dockerfile'))}
    hr = repo/'base_harness/loop'
    harness = {str(p.relative_to(hr)):sha(p) for p in sorted(hr.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
    write(ev/'source-files.json', source); write(ev/'harness-files.json', harness)
    write(ev/'split.json',dict(HG_TB_SPLIT='none', split=None, selected=[tid]))
    limits = dict(cpus=row['environment']['cpus'], memory_mb=row['environment']['memory_mb'], agent_timeout_s=900, verify_timeout_s=int(row['verifier']['timeout_sec']))
    env_values = dict(HG_EGRESS_PROXY='http://172.17.0.1:17890', HG_TB_TASKS=tid, HG_TB_SPLIT='none', HG_AGENT_BACKEND='mock', HG_AGENT_MODEL='', HG_AGENT_BASE_URL='', HG_AGENT_API_KEY='', HG_AGENT_MAX_STEPS='1', CUDA_VISIBLE_DEVICES='')
    write(ev/'launch-manifest.json',dict(kind='observer pre-execution binding; not admission evidence', run_id=run_id,task_id=tid,trial=1, image_id=row['image_id'],repo_digests=row['repo_digests'], platform_commit=json.loads((packet/'inventory/platform-commit.json').read_text())['stdout'].strip(), dataset_commit=json.loads((packet/'inventory/dataset-commit.json').read_text())['stdout'].strip(), source_sha256=sha(ev/'source-files.json'),split_sha256=sha(ev/'split.json'),harness_sha256=sha(ev/'harness-files.json'),endpoint=None,model=None,environment=env_values,limits=limits,selection_rule=selection_rule))
    context = dict(dataset='terminal_bench',side='train',metric=dict(name='Terminal-Bench reward_file /logs/verifier/reward.txt',scorer_sha256=sha(td/'tests/test.sh')),hashes=dict(source=sha(ev/'source-files.json'),split=sha(ev/'split.json'),manifest=sha(ev/'launch-manifest.json'),model=None,harness=sha(ev/'harness-files.json')),endpoint=None,limits=dict(resource=limits,budget=None),gates=dict(status='unknown',receipt_sha256=None,detail='Operator authorized bounded no-model controls; dataset enforcement remains unknown; no blocker closure or production authorization.'),comparability_notes=['One-task diagnostic selection, HG_TB_SPLIT=none; train CLI required by unchanged authorization guard. Four controls in serial, one mock step, zero improvement rounds.', 'No model or endpoint binding; not comparable to the historical model task or benchmark performance. Raw verifier evidence is separate from withheld policy publication.', 'Source and scorer hashes do not establish transitive offline dependency closure. Declared verifier bridge egress via documented free proxy is allowed; this is not a network-denied run.'])
    diagnostic_policy.validate_context(context)
    write(ev/'policy-input.json',dict(context=context))
    reason='Operator explicitly authorizes a bounded handful of fresh local no-model Terminal-Bench diagnostic controls for S4 broader execution evidence. This is one preselected task, mock backend only, HG_TB_SPLIT=none, documented egress proxy; unknown enforcement remains unknown, no pilot expansion, blocker closure or production authorization.'
    argv=['python3','driver.py','--harness','loop','--dataset','terminal_bench','--sampling','diagnostic','--policy-evidence',str(ev/'policy-input.json'),'--authorize-unobserved-diagnostic',reason,'--rounds','0','--trials','1','--jobs','1','--side','train','--improver','none','--run-id',run_id,'--runs-root',str(runs),'--work-root',str(work)]
    (ev/'command.txt').write_text(shlex.join(['env']+[k+'='+v for k,v in env_values.items()]+argv)+'\n')
    write(ev/'launch-input.json',dict(argv=argv,cwd=str(repo),environment=env_values,endpoint=None,model=None))
    capture(ev,'containers-before',['docker','ps','-a','--filter','label=harnessgrad.run='+run_id,'--format','{{json .}}'])
    stop = threading.Event(); observations=[]; containers={}; snapshots={}; observer_errors=[]
    def observe():
        seq=0; last_stats=0
        while not stop.is_set():
            try:
                p=subprocess.run(['docker','ps','-aq','--filter','label=harnessgrad.run='+run_id],capture_output=True,text=True,timeout=15)
                if p.stdout.split():
                    q=subprocess.run(['docker','inspect',*p.stdout.split()],capture_output=True,text=True,timeout=15)
                    if q.returncode==0:
                        cs=json.loads(q.stdout)
                        for c in cs:
                            if c['Id'] not in containers:
                                containers[c['Id']]=c
                                write(ev/('container-first-'+c['Id']+'.json'),c)
                            if c['Name'].startswith('/hg-verify-'):
                                for m in c['Mounts']:
                                    if m['Destination']=='/logs/verifier':
                                        for name in ('reward.txt','ctrf.json'):
                                            src=pathlib.Path(m['Source'])/name
                                            try: data=src.read_bytes()
                                            except OSError: continue
                                            digest=hashlib.sha256(data).hexdigest(); dest=ev/('verifier-'+name+'-'+digest)
                                            if not dest.exists():
                                                dest.write_bytes(data)
                                                observations.append(dict(source=str(src),copy=str(dest),sha256=digest,bytes=len(data),container_id=c['Id'],observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat()))
                        if time.monotonic()-last_stats>5:
                            capture(ev,'container-inspect-%04d'%seq,['docker','inspect','--size',*p.stdout.split()])
                            capture(ev,'container-stats-%04d'%seq,['docker','stats','--no-stream','--format','{{json .}}',*p.stdout.split()])
                            last_stats=time.monotonic();seq+=1
                stop.wait(0.04)
            except Exception as exc: observer_errors.append(repr(exc)); stop.wait(0.1)
    observer=threading.Thread(target=observe,daemon=True);observer.start()
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (ev/'docker-events.jsonl').open('w') as events, (ev/'docker-events.stderr.txt').open('w') as ee, (ev/'driver.stdout.txt').open('w') as out, (ev/'driver.stderr.txt').open('w') as err:
        ep=subprocess.Popen(['docker','events','--since',started,'--filter','label=harnessgrad.run='+run_id,'--format','{{json .}}'],stdout=events,stderr=ee)
        child=subprocess.Popen(argv,cwd=repo,env={**os.environ,**env_values},stdout=out,stderr=err)
        write(ev/'driver-process.json',dict(pid=child.pid,started_at=started))
        code=child.wait()
        ep.terminate();ep.wait(timeout=15)
    stop.set();observer.join(timeout=45)
    write(ev/'verifier-file-observations.json', observations)
    write(ev/'observer-errors.json',observer_errors)
    write(ev/'launch-observation.json',dict(returncode=code,started_at=started,ended_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),endpoint=None,model=None))
    for label,args in [('containers',['docker','ps','-a']),('networks',['docker','network','ls']),('volumes',['docker','volume','ls'])]:
        capture(ev,label+'-after',args+['--filter','label=harnessgrad.run='+run_id,'--format','{{json .}}'])
    capture(ev,'snapshots-after',['docker','image','ls','--filter','reference=hg-snapshot:*'+run_id+'*','--no-trunc','--format','{{json .}}'])
    for i,c in enumerate(containers.values()):
        capture(ev,'container-exact-after-%02d'%i,['docker','inspect',c['Id']])
    capture(ev,'disk-after',['df','-B1','/','/tmp'])
    print(json.dumps(dict(completed=tid,returncode=code,run_dir=str(run),verifier_file_observations=len(observations))),flush=True)
print(json.dumps(dict(batch_complete=True,runs_root=str(runs))),flush=True)
