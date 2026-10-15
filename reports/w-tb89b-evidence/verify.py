"""Check receipt custody, raw-derived results, seriality and additive registry scope."""
import base64,hashlib,json,pathlib,subprocess
repo=pathlib.Path(__file__).resolve().parents[2];packet=repo/'reports/w-tb89b-evidence'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=read(packet/'result.json');rows=s['rows'];batch=s['batch']
assert [r['task_id'] for r in rows]==batch['selected']
assert len(rows)==len(set(r['run_id'] for r in rows))
for r in rows:
    ev=pathlib.Path(r['evidence_dir']);run=pathlib.Path(r['run_dir']);tid=r['task_id'];dst=packet/'attempts'/tid
    assert not run.is_relative_to(repo) and not pathlib.Path(r['work_root']).is_relative_to(repo)
    inp=read(ev/'launch-input.json');env=inp['environment'];args=inp['argv']
    for key,value in {'HG_AGENT_BACKEND':'openai','HG_AGENT_MODEL':'qwen3.5-9b-local','HG_AGENT_BASE_URL':'http://127.0.0.1:8002/v1','HG_TB_TASKS':tid,'HG_TB_SPLIT':'none','HG_EGRESS_PROXY':'http://172.17.0.1:17890'}.items():assert env[key]==value
    for flag,value in {'--sampling':'diagnostic','--rounds':'0','--trials':'1','--jobs':'1','--side':'train','--harness':'loop','--improver':'none','--run-id':r['run_id'],'--runs-root':batch['runs_root'],'--work-root':r['work_root']}.items():assert args[args.index(flag)+1]==value
    assert '--authorize-unobserved-diagnostic' in args
    context=read(ev/'policy-input.json')['context'];assert context['gates']['status']=='unknown' and context['gates']['receipt_sha256'] is None
    assert context['hashes']==r['hashes'] and context['hashes']['model'] is None
    for path,digest in read(ev/'platform-source-files.json').items():assert sha(repo/path)==digest,path
    for k,file in [('source','source-files.json'),('split','split.json'),('harness','harness-files.json'),('manifest','launch-manifest.json')]:assert context['hashes'][k]==sha(ev/file)
    ex=read(run/'diagnostic_execution.json');rec=read(run/'diagnostic_receipt.json')
    assert ex['per_task'].get(tid)==r['raw_score'] and ex['verdicts'].get(tid)==r['verifier_verdict']
    assert ex['invalid']==r['raw_invalid']
    assert rec['coverage']==r['publication']['coverage'] and rec['score'] is None
    if r['raw_invalid']:
        assert all(o['status']=='invalid' and 'ctrf.json' in o['reason'] for o in rec['outcomes'])
    else:
        assert all(o['status']=='unmeasured' and o['reason']=='policy_enforcement_not_observed' for o in rec['outcomes'])
    assert r['model_gateway']['target']=='127.0.0.1:8002' and r['model_gateway']['connections']>0
    assert r['identity_declared']['agent_model']==r['model'] and r['identity_declared']['agent_backend']=='openai'
    images=json.loads(read(ev/'image-inspect.json')['stdout']);assert images[0]['Id']==r['image_id'] and images[0]['RepoDigests']==r['repo_digests']
    for item in r['ctrf_files']+r['reward_files']:
        p=pathlib.Path(item['path']);assert sha(p)==item['sha256'] and p.stat().st_size==item['bytes']
    if r['raw_measured']:
        assert r['ctrf_files'] and r['reward_files'] and not ex['invalid']
        assert all(float(i['text'])==r['raw_score'] for i in r['reward_files'])
        assert r['ctrf_files'][-1]['summary']['passed']==r['verifier_verdict']['tests']['passed']
        assert r['ctrf_files'][-1]['summary']['tests']==r['verifier_verdict']['tests']['tests']
    assert r['cleanup_observed_absent']
    resource=read(ev/'resource-observation-receipt.json')
    assert set(resource['roles'])=={'agent','verifier'}
    assert resource['roles']['agent']['image_id']==r['image_id']
    for role in resource['roles'].values():
        assert role['limits']['NanoCpus']==1000000000 and role['limits']['Memory']==2147483648
        assert 'bridge' in role['networks']
        assert role['limits']['MemorySwap']==4294967296 and role['limits']['PidsLimit']==1024 and role['limits']['ReadonlyRootfs'] is False
    for p in dst.rglob('*'):
        if not p.is_file() or 'source-preimages' in p.parts:continue
        assert (ev/p.name).is_file() and sha(p)==sha(ev/p.name), p
    for p in (dst/'source-preimages').rglob('*.json'):
        pre=read(p);src=pathlib.Path(pre['source']['path']);assert src.read_bytes()==base64.b64decode(pre['data']);assert sha(src)==pre['source']['sha256']
expected_raw=dict(selected_tasks=len(rows),expected_trials=len(rows),measured_tasks=sum(r['raw_measured'] for r in rows),measured_trials=sum(r['raw_measured'] for r in rows),invalid_tasks=sum(bool(r['raw_invalid']) for r in rows),unmeasured_tasks=sum(not r['raw_measured'] and not r['raw_invalid'] for r in rows))
assert s['raw_execution_coverage']==expected_raw
expected_pub={k:sum(r['publication']['coverage'][k] for r in rows) for k in rows[0]['publication']['coverage']}
assert s['publication_coverage_sum_of_four_one_task_selections']==expected_pub
prior=read(packet/'previous-official-result.json');assert prior['returncode']==0
prior=json.loads(prior['stdout']);assert prior['raw_per_task']=={'openssl-selfsigned-cert':0.0} and prior['ctrf_files'] and not prior['invalid']
for a,b in zip(rows,rows[1:]):assert a['launch_observation']['ended_at']<=b['launch_observation']['started_at']
for f in read(packet/'run-artifact-inventory.json')['files']:
    p=pathlib.Path(f['path']);assert p.is_file() and sha(p)==f['sha256'] and p.stat().st_size==f['bytes'],str(p)
baseline_commit=read(packet/'platform-commit.json')['stdout'].strip()
base=json.loads(subprocess.check_output(['git','show',baseline_commit+':docs/dataset-blockers.json'],cwd=repo,text=True))
current=read(repo/'docs/dataset-blockers.json')
old=next(b for b in base['shared_blockers'] if b['id']=='scorer-offline-closure')
new=next(b for b in current['shared_blockers'] if b['id']=='scorer-offline-closure')
assert new['observed'].startswith(old['observed'])
assert new['evidence'][:len(old['evidence'])]==old['evidence']
for d in (base,current):
    b=next(b for b in d['shared_blockers'] if b['id']=='scorer-offline-closure')
    b.pop('observed');b.pop('evidence')
assert base==current,'only shared scorer observed/evidence may change'
print(json.dumps(dict(verified=True,raw_execution=s['raw_execution_coverage'],publication=s['publication_coverage_sum_of_four_one_task_selections'],retained_artifacts=len(read(packet/'run-artifact-inventory.json')['files']),serial=True,registry_additive_only=True),indent=2))
