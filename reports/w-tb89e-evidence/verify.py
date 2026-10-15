"""Recompute external artifact custody, raw coverage and additive-only registry scope."""
import hashlib,json,pathlib,subprocess,tomllib
repo=pathlib.Path(__file__).resolve().parents[2];packet=repo/'reports/w-tb89e-evidence'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
raw=pathlib.Path(read(packet/'location.json')['raw_root']);assert '"batch_complete": true' in (raw/'launch.stdout.txt').read_text();s=read(raw/'result.json');batch=read(raw/'batch.json');inv=read(raw/'inventory.json')
baseline=read(raw/'platform-commit.json')['stdout'].strip()
assert s['batch']==batch and len(batch['selected'])<=9
endpoint=read(raw/'endpoint-completion.json');body,status=endpoint['stdout'].rsplit('\n',1);assert endpoint['returncode']==0 and status=='200' and json.loads(body)['choices'][0]['message']['content']=='OK'
assert inv['total_task_references']==89
assert len(inv['rows'])==len(set(r['task_id'] for r in inv['rows']))
assert inv['cached_images']==sum(r['image_present'] for r in inv['rows'])
assert inv['missing_images']==[r['task_id'] for r in inv['rows'] if not r['image_present']]
assert not set(inv['missing_images'])&set(batch['selected'])
metadata=json.loads(read(raw/'inventory-task-metadata-raw.json')['stdout'])
for r in inv['rows']:
 meta=tomllib.loads(metadata[r['task_id']])
 for key in ('environment','agent','verifier'):assert r[key]==meta[key]
 d=read(raw/('image-'+r['task_id']+'.json'))
 if r['image_present']:
  assert d['returncode']==0
  i=json.loads(d['stdout'])[0];assert i['Id']==r['image_id'] and i['RepoDigests']==r['repo_digests']
 else:assert d['returncode']!=0
prior=read(raw/'prior-tb89d.json');assert prior['returncode']==0
prior_s=json.loads(prior['stdout']);assert prior_s['raw_execution_coverage']['measured_tasks']==1
prior_a=read(raw/'prior-tb89d-availability.json');assert prior_a['returncode']==0
prior_ids=json.loads(prior_a['stdout'])['prior_unique_measured']
assert set(batch['prior_measured'])==set(prior_ids)|{r['task_id'] for r in prior_s['rows'] if r['raw_measured']}
# The nine pre-d IDs are retained verbatim in the prior report, then union with its measured rows.
prior_report=subprocess.check_output(['git','show',baseline+':reports/w-tb89d-receipts.md'],cwd=repo,text=True)
for tid in batch['prior_measured']:assert '`'+tid+'`' in prior_report
assert len(set(batch['prior_measured']))==10
assert read(raw/'prerequisites-complete.json')['verified']==batch['selected']
assert read(pathlib.Path(batch['runs_root'])/'preparation-packet/batch.json')==batch
assert read(raw/'prerequisites-complete.json')['observed_at']<s['rows'][0]['launch_observation']['started_at']
for tid in batch['selected']:
 for prefix in ('shell-syntax-','prerequisite-','dependency-bootstrap-'):
  q=read(raw/(prefix+tid+'.json'));assert q['returncode']==0
  if prefix=='dependency-bootstrap-':assert '--ctrf' in q['stdout']
end=None;new=[]
for r in s['rows']:
 ev=pathlib.Path(r['evidence_dir']);tid=r['task_id'];run=pathlib.Path(r['run_dir'])
 assert ev.is_relative_to(pathlib.Path(batch['runs_root'])) and run.is_relative_to(pathlib.Path(batch['runs_root']))
 assert not pathlib.Path(r['work_root']).is_relative_to(repo)
 assert r['model_gateway']['target']=='127.0.0.1:8002' and r['model_gateway']['connections']>0
 assert r['identity_declared']['agent_model']=='qwen3.5-9b-local'
 assert r['endpoint']=='http://127.0.0.1:8002/v1' and r['model']=='qwen3.5-9b-local'
 launch=read(ev/'launch-input.json');argv=launch['argv'];env=launch['environment']
 for k,v in {'--sampling':'diagnostic','--rounds':'0','--trials':'1','--jobs':'1','--run-id':r['run_id']}.items():assert argv[argv.index(k)+1]==v
 assert '--authorize-unobserved-diagnostic' in argv
 assert env['HG_TB_SPLIT']=='none' and env['HG_EGRESS_PROXY']=='http://172.17.0.1:17890' and env['HG_AGENT_BASE_URL']==r['endpoint']
 assert read(ev/'image-inspect.json')['returncode']==0
 assert json.loads(read(ev/'image-inspect.json')['stdout'])[0]['Id']==r['image_id']
 assert read(ev/'launch-manifest.json')['selection_rule']==batch['selection_rule']
 context=read(ev/'policy-input.json')['context']
 for key,name in [('source','source-files.json'),('split','split.json'),('harness','harness-files.json'),('manifest','launch-manifest.json')]:assert context['hashes'][key]==sha(ev/name)
 assert r['hashes']==context['hashes'] and context['hashes']['model'] is None
 for rel,digest in read(ev/'platform-source-files.json').items():assert sha(repo/rel)==digest
 for rel,digest in read(ev/'harness-files.json').items():assert sha(repo/'base_harness/loop'/rel)==digest
 for rel,digest in read(ev/'source-files.json').items():
  p=ev/'selected-tests'/pathlib.Path(rel).relative_to('tests') if rel.startswith('tests/') else ev/('selected-Dockerfile' if rel=='environment/Dockerfile' else 'selected-'+rel)
  assert sha(p)==digest
 assert sha(ev/'selected-tests/test.sh')==r['scorer']['scorer_sha256']
 for key in ('resource_receipt','snapshot_receipt','cleanup_receipt'):
  ref=r[key];p=pathlib.Path(ref['path']);assert sha(p)==ref['sha256'] and p.stat().st_size==ref['bytes']
 assert r['cleanup_observed_absent']
 resource=read(ev/'resource-observation-receipt.json')
 binding=dict(adapter_id='terminal_bench',run_id=r['run_id'],trial_id=tid+':1',manifest_sha256=r['hashes']['manifest'])
 assert resource['binding']==binding
 for key in ('snapshot','cleanup'):assert read(ev/(key+'-observation-receipt.json'))['binding']==binding
 for role in resource['roles'].values():
  assert role['limits']['NanoCpus']==1000000000
  assert role['limits']['Memory']==2147483648
 native=read(run/'diagnostic_execution.json');assert native['invalid']==r['native_invalid']
 measured=bool(r['ctrf_files'] and r['reward_files'] and tid in native.get('per_task',{}) and r['verifier_verdict'] and r['verifier_verdict']['kind']=='command' and not r['raw_invalid'])
 assert measured==r['raw_measured']
 if not r['ctrf_files']:assert not measured and r['raw_score'] is None
 if r['agent_timeout_observed']:assert not measured and r['raw_score'] is None
 if measured:
  assert r['raw_score']==r['verifier_verdict']['score']==native['per_task'][tid]
  assert r['verifier_verdict']['scorer_isolation_class']=='snapshot-service'
  assert r['verifier_verdict']['scorer_isolation_declared']=='snapshot-service'
  assert r['ctrf_files'][-1]['summary']['passed']==r['verifier_verdict']['tests']['passed']
  assert r['ctrf_files'][-1]['summary']['tests']==r['verifier_verdict']['tests']['tests']
  assert float(r['reward_files'][-1]['text'])==r['raw_score'];new.append(tid)
 for f in r['ctrf_files']:
  p=pathlib.Path(f['path']);assert sha(p)==f['sha256']
  assert read(p)['results']['summary']==f['summary']
 obs=r['launch_observation'];assert end is None or end<=obs['started_at'];end=obs['ended_at']
 assert r['publication']['score'] is None
 assert r['publication']['coverage']['measured_tasks']==0
rows=s['rows'];counts=s['raw_execution_coverage']
assert counts==dict(selected_tasks=len(rows),expected_trials=len(rows),measured_tasks=len(new),measured_trials=len(new),invalid_tasks=sum(bool(r['raw_invalid']) or not r['ctrf_produced'] for r in rows),unmeasured_tasks=sum(not r['raw_measured'] and not r['raw_invalid'] and r['ctrf_produced'] for r in rows))
assert not set(new)&set(batch['prior_measured'])
assert batch['cached_unmeasured_before']==len([r for r in inv['rows'] if r['image_present'] and r['task_id'] not in batch['prior_measured']])
assert batch['cached_unmeasured_outside_selection']==len([r for r in inv['rows'] if r['image_present'] and r['task_id'] not in batch['prior_measured']+batch['selected']])
for f in read(raw/'run-artifact-inventory.json')['files']+read(raw/'preparation-artifact-inventory.json')['files']:
 p=pathlib.Path(f['path']);assert p.stat().st_size==f['bytes'] and sha(p)==f['sha256'],str(p)
base=json.loads(subprocess.check_output(['git','show',baseline+':docs/dataset-blockers.json'],cwd=repo,text=True));current=read(repo/'docs/dataset-blockers.json')
a=next(b for b in base['shared_blockers'] if b['id']=='scorer-offline-closure');b=next(b for b in current['shared_blockers'] if b['id']=='scorer-offline-closure')
assert b['observed'].startswith(a['observed']+' ')
assert b['evidence'][:len(a['evidence'])]==a['evidence'] and len(b['evidence'])==len(a['evidence'])+2
b['observed']=a['observed'];b['evidence']=a['evidence'];assert current==base
report=(repo/'reports/w-tb89e-receipts.md').read_text();observation=(packet/'registry-observation.txt').read_text().strip();assert observation in report
for p in packet.rglob('*'):
 if p.is_file():assert p.stat().st_size<1000000,str(p)
print(json.dumps(dict(raw=s['raw_execution_coverage'],publication=s['publication_coverage_sum_of_one_task_selections'],new_measured=new,cumulative=len(set(batch['prior_measured'])|set(new)),denominator=inv['total_task_references'],serial=True,all_artifact_hashes_verified=True,registry_additive_only=True),indent=2))
