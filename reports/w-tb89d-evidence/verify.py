"""Check receipt custody, raw-derived results, seriality and additive registry scope."""
import base64,hashlib,json,pathlib,subprocess,tomllib
repo=pathlib.Path(__file__).resolve().parents[2];packet=repo/'reports/w-tb89d-evidence'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=read(packet/'result.json');rows=s['rows'];batch=s['batch']
inventory=read(packet/'inventory.json')
metadata=read(packet/'inventory-task-metadata-raw.json');assert metadata['returncode']==0
metadata=json.loads(metadata['stdout'])
assert len(inventory['rows'])==inventory['total_task_references']
for item in inventory['rows']:
    meta=tomllib.loads(metadata[item['task_id']])
    for key in ('environment','agent','verifier'):assert item[key]==meta[key]
    inspected=read(packet/('image-'+item['task_id']+'.json'))
    images=json.loads(inspected['stdout']) if inspected['returncode']==0 else []
    assert bool(images)==item['image_present']
    if images:
        assert images[0]['Id']==item['image_id'] and images[0]['RepoDigests']==item['repo_digests']
assert inventory['cached_images']==sum(item['image_present'] for item in inventory['rows'])
assert inventory['missing_images']==[item['task_id'] for item in inventory['rows'] if not item['image_present']]
assert set(inventory['missing_images'])=={'mteb-leaderboard','pytorch-model-recovery','reshard-c4-data'}
endpoint=read(packet/'endpoint-completion.json');assert endpoint['returncode']==0
body,status=endpoint['stdout'].rsplit('\n',1);assert status=='200' and json.loads(body)['model']=='qwen3.5-9b-local'
assert json.loads(body)['choices'][0]['message']['content']=='OK'
assert [r['task_id'] for r in rows]==batch['selected']
assert len(rows)==len(set(r['run_id'] for r in rows))
for r in rows:
    ev=pathlib.Path(r['evidence_dir']);run=pathlib.Path(r['run_dir']);tid=r['task_id'];dst=packet/'attempts'/tid
    assert not run.is_relative_to(repo) and not pathlib.Path(r['work_root']).is_relative_to(repo)
    inp=read(ev/'launch-input.json');env=inp['environment'];args=inp['argv']
    for key,value in {'HG_AGENT_BACKEND':'openai','HG_AGENT_MODEL':'qwen3.5-9b-local','HG_AGENT_BASE_URL':'http://127.0.0.1:8002/v1','HG_TB_TASKS':tid,'HG_TB_SPLIT':'none','HG_EGRESS_PROXY':'http://172.17.0.1:17890'}.items():assert env[key]==value
    for flag,value in {'--sampling':'diagnostic','--rounds':'0','--trials':'1','--jobs':'1','--side':'train','--harness':'loop','--improver':'none','--run-id':r['run_id'],'--runs-root':str(run.parent),'--work-root':r['work_root']}.items():assert args[args.index(flag)+1]==value
    assert '--authorize-unobserved-diagnostic' in args
    context=read(ev/'policy-input.json')['context'];assert context['gates']['status']=='unknown' and context['gates']['receipt_sha256'] is None
    assert context['hashes']==r['hashes'] and context['hashes']['model'] is None
    for path,digest in read(ev/'platform-source-files.json').items():assert sha(repo/path)==digest,path
    for k,file in [('source','source-files.json'),('split','split.json'),('harness','harness-files.json'),('manifest','launch-manifest.json')]:assert context['hashes'][k]==sha(ev/file)
    for rel,digest in read(ev/'source-files.json').items():
        if rel.startswith('tests/'):
            preimage=ev/'selected-tests'/pathlib.Path(rel).relative_to('tests')
        elif rel=='environment/Dockerfile':
            preimage=ev/'selected-Dockerfile'
        else:
            preimage=ev/('selected-'+rel)
        assert preimage.is_file() and sha(preimage)==digest,rel
    assert context['metric']['scorer_sha256']==sha(ev/'selected-tests/test.sh')
    for rel,digest in read(ev/'harness-files.json').items():assert sha(repo/'base_harness/loop'/rel)==digest
    if r['interrupted']:
        assert not r['native_execution_present']
        assert not (run/'diagnostic_execution.json').exists() and not (run/'diagnostic_receipt.json').exists()
        disposition=read(ev/'interrupted-disposition.json')
        assert r['raw_invalid'][tid]['detail']==disposition['reason']
        assert r['publication']['coverage'] is None and r['publication']['outcomes'] is None
        assert r['raw_score'] is None and not r['raw_measured'] and not r['ctrf_produced']
        assert r['model_gateway'] is None
        partial=ev/'interruption-cleanup/trace.jsonl'
        trace_entries=[json.loads(line) for line in partial.read_text().splitlines() if line.strip()]
        assert any('reply' in entry for entry in trace_entries), 'No actual agent call observation'
        assert r['launch_observation']['returncode'] is None
    else:
        ex=read(run/'diagnostic_execution.json');rec=read(run/'diagnostic_receipt.json')
        assert ex['per_task'].get(tid)==r['native_raw_score'] and ex['verdicts'].get(tid)==r['verifier_verdict']
        assert ex['invalid']==r['native_invalid']
        if r['agent_timeout_observed']:
            assert r['harness_output']['exit_code']==-1 and 'timeout after' in r['harness_output']['stderr']
            assert r['raw_invalid'][tid]['stage']=='observer-agent-timeout' and r['raw_score'] is None and not r['raw_measured']
        else:assert r['raw_invalid']==ex['invalid'] and r['raw_score']==r['native_raw_score']
        assert rec['coverage']==r['publication']['coverage'] and rec['score'] is None
        if ex['invalid'] or r['agent_timeout_observed']:
            assert all(o['status']=='invalid' for o in rec['outcomes'])
        else:
            assert all(o['status']=='unmeasured' and o['reason']=='policy_enforcement_not_observed' for o in rec['outcomes'])
        assert r['model_gateway']['target']=='127.0.0.1:8002' and r['model_gateway']['connections']>0
    assert r['identity_declared']['agent_model']==r['model'] and r['identity_declared']['agent_backend']=='openai'
    images=json.loads(read(ev/'image-inspect.json')['stdout']);assert images[0]['Id']==r['image_id'] and images[0]['RepoDigests']==r['repo_digests']
    for item in r['ctrf_files']+r['reward_files']:
        p=pathlib.Path(item['path']);assert sha(p)==item['sha256'] and p.stat().st_size==item['bytes']
    if r['raw_measured']:
        assert r['ctrf_files'] and r['reward_files'] and not ex['invalid']
        assert r['verifier_verdict']['scorer_isolation_class']=='snapshot-service'
        assert r['verifier_verdict']['scorer_isolation_declared']=='snapshot-service'
        assert all(float(i['text'])==r['raw_score'] for i in r['reward_files'])
        assert r['ctrf_files'][-1]['summary']['passed']==r['verifier_verdict']['tests']['passed']
        assert r['ctrf_files'][-1]['summary']['tests']==r['verifier_verdict']['tests']['tests']
    assert r['cleanup_observed_absent']
    resource=read(ev/'resource-observation-receipt.json')
    binding=dict(adapter_id='terminal_bench',run_id=r['run_id'],trial_id=tid+':1',manifest_sha256=r['hashes']['manifest'])
    assert resource['binding']==binding
    assert read(ev/'snapshot-observation-receipt.json')['binding']==binding
    assert read(ev/'cleanup-observation-receipt.json')['binding']==binding
    assert set(resource['roles'])==({'agent'} if r['interrupted'] else {'agent','verifier'})
    assert resource['roles']['agent']['image_id']==r['image_id']
    for role in resource['roles'].values():
        assert role['limits']['NanoCpus']==1000000000 and role['limits']['Memory']==2147483648
        assert 'bridge' in role['bridge_attachment_networks']
        attachment=role['bridge_attachment_inspection'];assert sha(pathlib.Path(attachment['path']))==attachment['sha256']
        attachment_raw=read(pathlib.Path(attachment['path']));assert attachment_raw['returncode']==0
        inspected=next(c for c in json.loads(attachment_raw['stdout']) if c['Id']==role['container_id'])
        assert 'bridge' in inspected['NetworkSettings']['Networks']
        assert role['limits']['MemorySwap']==4294967296 and role['limits']['PidsLimit']==1024 and role['limits']['ReadonlyRootfs'] is False
    for p in dst.rglob('*'):
        if not p.is_file() or 'source-preimages' in p.parts:continue
        assert (ev/p.name).is_file() and sha(p)==sha(ev/p.name), p
    for p in (dst/'source-preimages').rglob('*.json'):
        pre=read(p);src=pathlib.Path(pre['source']['path']);assert src.read_bytes()==base64.b64decode(pre['data']);assert sha(src)==pre['source']['sha256']
expected_raw=dict(selected_tasks=len(rows),expected_trials=len(rows),measured_tasks=sum(r['raw_measured'] for r in rows),measured_trials=sum(r['raw_measured'] for r in rows),invalid_tasks=sum(bool(r['raw_invalid']) or not r['ctrf_produced'] for r in rows),unmeasured_tasks=sum(not r['raw_measured'] and not r['raw_invalid'] and r['ctrf_produced'] for r in rows))
assert s['raw_execution_coverage']==expected_raw
published=[r for r in rows if r['publication']['coverage'] is not None]
assert s['native_execution_receipts']==len(published) and s['missing_native_receipts']==len(rows)-len(published)
expected_pub={k:sum(r['publication']['coverage'][k] for r in published) for k in published[0]['publication']['coverage']}
assert s['publication_coverage_sum_of_one_task_selections']==expected_pub
prior_packet=read(packet/'prior-tb89b-result.json');assert prior_packet['returncode']==0
prior= json.loads(json.loads(prior_packet['stdout'])['stdout'])
prior_rows={r['task_id']:r['raw_score'] for r in prior['rows'] if r['raw_measured']}
assert len(prior_rows)==prior['raw_execution_coverage']['measured_tasks']
net_packet=read(packet/'prior-openssl-result.json');assert net_packet['returncode']==0
net_raw=json.loads(json.loads(json.loads(net_packet['stdout'])['stdout'])['stdout'])
assert net_raw['ctrf_files'] and not net_raw['invalid']
prior_rows.update(net_raw['raw_per_task'])
previous=json.loads(read(packet/'prior-tb89c-result.json')['stdout'])
prior_rows.update({r['task_id']:r['raw_score'] for r in previous['rows'] if r['raw_measured']})
assert len(prior_rows)==9 and not (set(prior_rows)&set(batch['selected']))
available=read(packet/'availability-all.json')
assert set(available['prior_unique_measured'])==set(prior_rows)
assert available['cached_new_outside_batch']==len({r['task_id'] for r in inventory['rows'] if r['image_present']}-set(prior_rows)-set(batch['selected']))
assert available['remaining_certified_queue_after_fixed_batch']==len(batch['prerequisite_verified_not_selected'])==0
audit=read(packet/'concurrency-audit.json')
foreign={item['pid']:item for item in audit['foreign_drivers']}
for item in foreign.values():
    meta_raw=item['run_meta_raw'];assert meta_raw['returncode']==0
    meta=json.loads(meta_raw['stdout'])
    if meta['run_id']=='musique-full-qwen-t1-train':
        assert meta['agent_backend']=='openai' and meta['config']['agent']['base_url']=='http://127.0.0.1:8010/v1'
        routing=audit['routing_observation'];assert routing['operator_run']==meta['run_id']
        assert 'BACKENDS = [("127.0.0.1", 8001), ("127.0.0.1", 8002)]' in routing['proxy_source']
    else:
        assert meta['dataset']=='verify_demo' and meta['agent_backend']=='mock'
        assert meta['config']['agent']['backend']=='mock' and not meta['config']['agent']['model'] and not meta['config']['agent']['base_url']
        assert meta['env']['model_gateway'] is None and meta['config']['environment']['model'] is None
        assert meta['config']['method']['model'] is None and meta['config']['improver']['model'] is None
    for sample in item['samples']:assert sha(pathlib.Path(sample['path']))==sample['sha256']
seen_foreign=set()
for r in rows:
    if not r['ctrf_produced']:
        assert r['raw_invalid'] and not r['raw_measured'] and r['raw_score'] is None
    preflight=read(pathlib.Path(r['evidence_dir'])/'concurrency-preflight.json')
    assert preflight['total_worker_concurrency']==1
    assert all('--run-id musique-full-qwen-t1-train' in line for line in preflight['active_platform_drivers'])
    assert (packet/('prerequisite-'+r['task_id']+'.json')).is_file()
    assert read(packet/('prerequisite-'+r['task_id']+'.json'))['returncode']==0
    # Samples are process observations; there is no lock on operator endpoint usage.
    ownpid=read(pathlib.Path(r['evidence_dir'])/'driver-process.json')['pid']
    for f in pathlib.Path(r['evidence_dir']).glob('processes-sample-*.json'):
        raw=read(f)
        active=[line for line in raw['stdout'].splitlines() if len(line.split())>2 and 'python' in line.split()[1] and any(pathlib.Path(arg).name=='driver.py' for arg in line.split()[2:])]
        for line in active:
            pid=int(line.split()[0])
            if pid==ownpid:continue
            assert pid in foreign and line==foreign[pid]['process_line'],line
            assert any(sample['path']==str(f) for sample in foreign[pid]['samples'])
            seen_foreign.add(pid)
assert seen_foreign==set(foreign)
for a,b in zip(rows,rows[1:]):assert a['launch_observation']['ended_at']<=b['launch_observation']['started_at']
for f in read(packet/'run-artifact-inventory.json')['files']:
    p=pathlib.Path(f['path']);assert p.is_file() and sha(p)==f['sha256'] and p.stat().st_size==f['bytes'],str(p)
baseline_commit=read(packet/'platform-commit.json')['stdout'].strip()
base=json.loads(subprocess.check_output(['git','show',baseline_commit+':docs/dataset-blockers.json'],cwd=repo,text=True))
current=read(repo/'docs/dataset-blockers.json')
old=next(b for b in base['shared_blockers'] if b['id']=='scorer-offline-closure')
new=next(b for b in current['shared_blockers'] if b['id']=='scorer-offline-closure')
assert new['observed'].startswith(old['observed'])
observation=(packet/'registry-observation.txt').read_text().strip()
assert observation in new['observed'] and observation in (repo/'reports/w-tb89d-receipts.md').read_text()
assert len(new['evidence'])==len(old['evidence'])+2
for item in new['evidence'][len(old['evidence']):]:
    assert item['locator'] in (repo/item['path']).read_text()
assert '## Exact registry observation - w-tb89d' in (repo/'reports/w-tb89d-receipts.md').read_text()
assert new['evidence'][:len(old['evidence'])]==old['evidence']
for d in (base,current):
    b=next(b for b in d['shared_blockers'] if b['id']=='scorer-offline-closure')
    b.pop('observed');b.pop('evidence')
assert base==current,'only shared scorer observed/evidence may change'
print(json.dumps(dict(verified=True,raw_execution=s['raw_execution_coverage'],publication=s['publication_coverage_sum_of_one_task_selections'],retained_artifacts=len(read(packet/'run-artifact-inventory.json')['files']),serial=True,foreign_sampled_drivers=len(foreign),all_foreign_drivers_accounted=True,operator_sharing_permitted=True,cumulative_raw_tasks=len(prior_rows)+expected_raw['measured_tasks'],denominator=s['inventory']['total_task_references'],registry_additive_only=True),indent=2))
