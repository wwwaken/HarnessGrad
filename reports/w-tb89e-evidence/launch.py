"""Three serial live-local-model diagnostics through unchanged production route."""
import datetime, hashlib, json, os, pathlib, secrets, shlex, shutil, subprocess, sys, threading, time

repo = pathlib.Path(__file__).resolve().parents[2]
packet = pathlib.Path(json.loads((repo/'reports/w-tb89e-evidence/location.json').read_text())['raw_root'])
sys.path.insert(0, str(repo))
from eval.policy import diagnostic_policy

# Shared operator endpoint use is explicitly permitted by this task; only this
# worker must be serial. Preserve known foreign-driver identity, never stop it.
known_operator_run = 'musique-full-qwen-t1-train'
process_argv = ['python3', '-c', "import pathlib; print('PID ARGS'); [(print(p.name,*(p/'cmdline').read_bytes().decode().split(chr(0))[:-1])) for p in pathlib.Path('/proc').iterdir() if p.name.isdigit() and (p/'cmdline').is_file() and (p/'comm').read_text().strip() in ('python','python3') and any(pathlib.Path(a).name=='driver.py' for a in (p/'cmdline').read_bytes().decode().split(chr(0))) ]"]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, value):
    with p.open('x') as f: json.dump(value, f, indent=2); f.write('\n')
def capture(where, name, argv, timeout=40):
    p = subprocess.run(argv, cwd=repo, capture_output=True, text=True, timeout=timeout)
    write(where / (name + '.json'), dict(argv=argv, returncode=p.returncode, stdout=p.stdout, stderr=p.stderr))
    return p

inventory = json.loads((packet/'inventory.json').read_text())
batch = json.loads((packet/'batch.json').read_text())
shortlist = batch['selected']
selection_rule = batch['selection_rule']
runs = pathlib.Path(batch['runs_root'])
assert json.loads((packet/'prerequisites-complete.json').read_text())['verified'] == shortlist
shutil.copyfile(__file__, runs/'launch.py')
shutil.copytree(packet, runs/'preparation-packet', ignore=shutil.ignore_patterns('launch.stdout.txt','launch.stderr.txt'))
for tid in shortlist:
    row = next(r for r in inventory['rows'] if r['task_id']==tid)
    assert row['image_present']
    td_check = pathlib.Path('/mnt/20t/xubuqiang/datasets/terminal-bench')/tid
    assert all((td_check/p).is_file() for p in ('task.toml','instruction.md','environment/Dockerfile','tests/test.sh','tests/test_outputs.py'))
    assert row['environment']['gpus']==0 and not row['environment'].get('mcp_servers')
    assert row['environment']['cpus']<=1 and row['environment']['memory_mb']<=2048
    run_id = 'w-tb89e-' + tid + '-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + secrets.token_hex(4)
    ev = runs / (run_id + '-evidence'); ev.mkdir(exist_ok=False)
    work = pathlib.Path('/tmp') / (run_id + '-work')
    run = runs / run_id
    assert not run.exists() and not work.exists()
    write(ev/'identity.json', dict(run_id=run_id, task_id=tid, run_dir=str(run), work_root=str(work), evidence_dir=str(ev)))
    print(json.dumps(dict(starting=tid, run_id=run_id, evidence=str(ev))), flush=True)
    processes = capture(ev,'processes-preflight',process_argv)
    # Do not overlap a known operator platform driver; never stop their work.
    active = [line for line in processes.stdout.splitlines() if len(line.split()) > 2 and any(pathlib.Path(a).name == 'driver.py' for a in line.split()[2:]) and ('python' in line.split()[1])]
    write(ev/'concurrency-preflight.json', dict(active_platform_drivers=active, own_jobs=1, total_worker_concurrency=1, note='Point-in-time host process observation, not an endpoint reservation.'))
    unexpected = [line for line in active if '--run-id '+known_operator_run not in line]
    assert not unexpected, 'Unaccounted driver; retain packet before launch.'
    if active:
        meta_path = pathlib.Path('/mnt/20t/xubuqiang/hg-census/runs')/known_operator_run/'run_meta.json'
        known = capture(ev,'operator-run-meta',['cat',str(meta_path)])
        meta = json.loads(known.stdout)
        assert meta['run_id']==known_operator_run and meta['config']['agent']['base_url']=='http://127.0.0.1:8010/v1'
        write(ev/'shared-endpoint-observation.json',dict(operator_run=known_operator_run,worker_concurrency=1,note='User explicitly permits sharing with operator; known operator proxy forwards 8001/8002. Operator is unchanged. Worker uses only direct 8002 serially.'))
    fresh_image = capture(ev,'image-inspect',['docker','image','inspect',row['image_ref']])
    assert fresh_image.returncode == 0 and json.loads(fresh_image.stdout)[0]['Id'] == row['image_id'], 'Image changed since preselection'
    # Match the earlier live diagnostic recipe; the platform owns task admission.
    p = capture(ev, 'endpoint-models', ['curl','--noproxy','*','--max-time','20','-sS','http://127.0.0.1:8002/v1/models'])
    assert p.returncode == 0 and any(m['id']=='qwen3.5-9b-local' for m in json.loads(p.stdout)['data'])
    for label,url in [('proxy-astral','https://astral.sh/uv/0.9.5/install.sh'),('proxy-pypi','https://pypi.org/simple/')]:
        p = capture(ev,label,['curl','--max-time','25','-x','http://172.17.0.1:17890','-LsS','-o','/dev/null','-w','%{http_code}',url])
        # Host proxy probes are observations; actual bootstrap remains the verifier's responsibility.
    td = pathlib.Path('/mnt/20t/xubuqiang/datasets/terminal-bench')/tid
    source = {str(p.relative_to(td)):sha(p) for p in sorted(td.rglob('*')) if p.is_file() and ('tests' in p.parts or p.name in ('instruction.md','task.toml','Dockerfile'))}
    shutil.copytree(td/'tests',ev/'selected-tests')
    for name in ('task.toml','instruction.md'):
        shutil.copy2(td/name,ev/('selected-'+name))
    shutil.copy2(td/'environment/Dockerfile',ev/'selected-Dockerfile')
    platform_files = {str(p.relative_to(repo)):sha(p) for base in ('eval','harnessgrad','base_harness/loop') for p in sorted((repo/base).rglob('*.py')) if '__pycache__' not in p.parts}
    platform_files['driver.py']=sha(repo/'driver.py')
    platform_files['data/datasets/terminal_bench.py']=sha(repo/'data/datasets/terminal_bench.py')
    write(ev/'platform-source-files.json',platform_files)
    hr = repo/'base_harness/loop'
    harness = {str(p.relative_to(hr)):sha(p) for p in sorted(hr.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
    write(ev/'source-files.json', source); write(ev/'harness-files.json', harness)
    write(ev/'split.json',dict(HG_TB_SPLIT='none', split=None, selected=[tid]))
    limits = dict(cpus=row['environment']['cpus'], memory_mb=row['environment']['memory_mb'], agent_timeout_s=900, verify_timeout_s=int(row['verifier']['timeout_sec']))
    env_values = dict(HG_EGRESS_PROXY='http://172.17.0.1:17890', HG_TB_TASKS=tid, HG_TB_SPLIT='none', HG_AGENT_BACKEND='openai', HG_AGENT_MODEL='qwen3.5-9b-local', HG_AGENT_BASE_URL='http://127.0.0.1:8002/v1', HG_AGENT_API_KEY='local')
    write(ev/'launch-manifest.json',dict(kind='observer pre-execution binding; not admission evidence', run_id=run_id,task_id=tid,trial=1, image_id=row['image_id'],repo_digests=row['repo_digests'], platform_commit=json.loads((packet/'platform-commit.json').read_text())['stdout'].strip(), dataset_commit=json.loads((packet/'dataset-commit.json').read_text())['stdout'].strip(), source_sha256=sha(ev/'source-files.json'),split_sha256=sha(ev/'split.json'),harness_sha256=sha(ev/'harness-files.json'),endpoint=batch['endpoint'],model=batch['model'],environment=env_values,limits=limits,selection_rule=selection_rule,platform_source_sha256=sha(ev/'platform-source-files.json'),model_weights_sha256=None))
    context = dict(dataset='terminal_bench',side='train',metric=dict(name='Terminal-Bench reward_file /logs/verifier/reward.txt',scorer_sha256=sha(td/'tests/test.sh')),hashes=dict(source=sha(ev/'source-files.json'),split=sha(ev/'split.json'),manifest=sha(ev/'launch-manifest.json'),model=None,harness=sha(ev/'harness-files.json')),endpoint=batch['endpoint'],limits=dict(resource=limits,budget=None),gates=dict(status='unknown',receipt_sha256=None,detail='Operator authorized bounded live-local-model diagnostics; dataset enforcement remains unknown; no blocker closure or production authorization.'),comparability_notes=['One-task diagnostic selection, HG_TB_SPLIT=none; train CLI required by unchanged authorization guard. Three live-local-model diagnostics in serial, default harness steps, zero improvement rounds.', 'Local endpoint/model binding; no model weight digest or benchmark-performance comparability. Raw verifier evidence is separate from withheld policy publication.', 'Source and scorer hashes do not establish transitive offline dependency closure. Declared verifier bridge egress via documented free proxy is allowed; this is not a network-denied run.'])
    diagnostic_policy.validate_context(context)
    write(ev/'policy-input.json',dict(context=context))
    reason='Operator explicitly authorizes three fresh preselected cached pip-bootstrap Terminal-Bench live-local-model diagnostics for S4 broader execution evidence; all exact verifier dependency bootstrap probes passed without official tests or model. Prior attempts and IDs are untouched. This is one preselected task, qwen3.5-9b-local at http://127.0.0.1:8002/v1, jobs=1, HG_TB_SPLIT=none, documented egress proxy; unknown enforcement remains unknown. Raw CTRF/scorer evidence only, no comparable score publication, pilot expansion, blocker closure or production authorization.'
    argv=['python3','driver.py','--harness','loop','--dataset','terminal_bench','--sampling','diagnostic','--policy-evidence',str(ev/'policy-input.json'),'--authorize-unobserved-diagnostic',reason,'--rounds','0','--trials','1','--jobs','1','--side','train','--improver','none','--run-id',run_id,'--runs-root',str(runs),'--work-root',str(work)]
    (ev/'command.txt').write_text(shlex.join(['env']+[k+'='+v for k,v in env_values.items()]+argv)+'\n')
    write(ev/'launch-input.json',dict(argv=argv,cwd=str(repo),environment=env_values,endpoint=batch['endpoint'],model=batch['model']))
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
                stop.wait(0.04)
            except Exception as exc: observer_errors.append(repr(exc)); stop.wait(0.1)
    def resources():
        seq=0
        while not stop.is_set():
            try:
                capture(ev,'processes-sample-%04d'%seq,process_argv)
                p=capture(ev,'container-list-%04d'%seq,['docker','ps','-aq','--filter','label=harnessgrad.run='+run_id])
                if p.stdout.split():
                    capture(ev,'container-inspect-%04d'%seq,['docker','inspect','--size',*p.stdout.split()])
                    capture(ev,'container-stats-%04d'%seq,['docker','stats','--no-stream','--format','{{json .}}',*p.stdout.split()])
                p=capture(ev,'snapshot-list-%04d'%seq,['docker','image','ls','--no-trunc','--filter','reference=hg-snapshot:*'+run_id+'*','--format','{{.ID}}'])
                if p.stdout.split():
                    q=capture(ev,'snapshot-inspect-%04d'%seq,['docker','image','inspect',*p.stdout.split()])
                    if q.returncode==0:
                        for i in json.loads(q.stdout): snapshots[i['Id']]=i
                seq+=1
            except Exception as exc: observer_errors.append(repr(exc))
            stop.wait(3)
    resource_thread=threading.Thread(target=resources,daemon=True);resource_thread.start()
    observer=threading.Thread(target=observe,daemon=True);observer.start()
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (ev/'docker-events.jsonl').open('w') as events, (ev/'docker-events.stderr.txt').open('w') as ee, (ev/'driver.stdout.txt').open('w') as out, (ev/'driver.stderr.txt').open('w') as err:
        ep=subprocess.Popen(['docker','events','--since',started,'--filter','label=harnessgrad.run='+run_id,'--format','{{json .}}'],stdout=events,stderr=ee)
        child=subprocess.Popen(argv,cwd=repo,env={**os.environ,**env_values},stdout=out,stderr=err)
        write(ev/'driver-process.json',dict(pid=child.pid,started_at=started))
        code=child.wait()
        ep.terminate();ep.wait(timeout=15)
    stop.set();observer.join(timeout=45);resource_thread.join(timeout=45)
    write(ev/'verifier-file-observations.json', observations)
    write(ev/'observer-errors.json',observer_errors)
    write(ev/'launch-observation.json',dict(returncode=code,started_at=started,ended_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),endpoint=batch['endpoint'],model=batch['model']))
    for label,args in [('containers',['docker','ps','-a']),('networks',['docker','network','ls']),('volumes',['docker','volume','ls'])]:
        capture(ev,label+'-after',args+['--filter','label=harnessgrad.run='+run_id,'--format','{{json .}}'])
    capture(ev,'snapshots-after',['docker','image','ls','--filter','reference=hg-snapshot:*'+run_id+'*','--no-trunc','--format','{{json .}}'])
    for i,c in enumerate(containers.values()):
        capture(ev,'container-exact-after-%02d'%i,['docker','inspect',c['Id']])
    for i,img in enumerate(snapshots.values()):
        capture(ev,'snapshot-exact-after-%02d'%i,['docker','image','inspect',img['Id']])
    capture(ev,'disk-after',['df','-B1','/','/tmp'])
    for name in ('diagnostic_receipt.json','diagnostic_execution.json','staged_plan.json','run_meta.json','selection.json'):
        if (run/name).is_file(): shutil.copy2(run/name,ev/('native-'+name))
    print(json.dumps(dict(completed=tid,returncode=code,run_dir=str(run),verifier_file_observations=len(observations))),flush=True)
print(json.dumps(dict(batch_complete=True,runs_root=str(runs))),flush=True)
