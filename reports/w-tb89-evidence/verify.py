"""Read-only evidence validation; no model, Docker run or task execution."""
import base64, hashlib, json, pathlib, subprocess
repo=pathlib.Path(__file__).resolve().parents[2];packet=repo/'reports/w-tb89-evidence'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r=read(packet/'result.json');inv=read(packet/'inventory.json')
assert len(inv['rows'])==inv['task_references']==89
assert sum(row['image_present'] for row in inv['rows'])==inv['cached']==86
assert len(inv['absent'])==3
for row in inv['rows']:
    cap=read(packet/'inventory'/('image-'+row['task_id']+'.json'))
    assert cap['argv']==['docker','image','inspect',row['image_ref']]
    if row['image_present']:
        assert cap['returncode']==0
        image=json.loads(cap['stdout'])[0]
        assert image['Id']==row['image_id'] and image['RepoDigests']==row['repo_digests']
    else:
        assert cap['returncode']!=0 and row['image_id'] is None and cap['stderr']
    sources=pathlib.Path(r['runs_root'])/'preparation-packet/inventory/sources'/row['task_id']
    for rel,digest in row['source_hashes'].items():assert sha(sources/rel)==digest
assert len(r['attempts'])==r['driver_attempts']==r['selected']==4
assert r['new_raw_measured_tasks']==r['new_ctrf_tasks']==r['task_trials_started']==0
assert r['observer_ledger']['measured']==r['observer_ledger']['invalid']==0
assert r['observer_ledger']['unmeasured']==4 and r['native_trial_coverage'] is None
assert r['cumulative_official_execution_fraction']=='1/89' and r['new_execution_fraction']=='0/89'
assert r['model'] is r['endpoint'] is None
encoded=read(packet/'inventory/sources/regex-log/instruction.md.json')
original=pathlib.Path(r['runs_root'])/'preparation-packet/inventory/sources/regex-log/instruction.md'
assert base64.b64decode(encoded['bytes_base64'])==original.read_bytes()
assert encoded['sha256']==sha(original)
for a in r['attempts']:
    ev=pathlib.Path(a['evidence_dir']);copy=packet/'attempts'/a['task_id']
    assert not pathlib.Path(a['run_dir']).exists() and not pathlib.Path(a['work_root']).exists()
    assert not a['ctrf_produced'] and a['raw_verifier_score'] is a['raw_verifier_verdict'] is None
    assert a['native_coverage'] is None and not a['native_receipt_present']
    assert (ev/'driver.stderr.txt').read_text()=='refusing staged policy: bind evidence to the live local agent endpoint\n'
    assert read(ev/'launch-observation.json')['returncode']==2
    launch=read(ev/'launch-input.json');env=launch['environment'];argv=launch['argv']
    assert env['HG_AGENT_BACKEND']=='mock' and env['HG_TB_SPLIT']=='none'
    assert env['HG_EGRESS_PROXY']=='http://172.17.0.1:17890'
    assert env['HG_AGENT_MODEL']==env['HG_AGENT_BASE_URL']==env['HG_AGENT_API_KEY']==''
    for flag,value in [('--sampling','diagnostic'),('--rounds','0'),('--trials','1'),('--jobs','1'),('--side','train'),('--improver','none')]:assert argv[argv.index(flag)+1]==value
    assert '--authorize-unobserved-diagnostic' in argv
    context=read(ev/'policy-input.json')['context'];assert context['endpoint'] is None and context['gates']['status']=='unknown'
    for key,name in [('source','source-files.json'),('split','split.json'),('manifest','launch-manifest.json'),('harness','harness-files.json')]:assert context['hashes'][key]==sha(ev/name)
    assert context['hashes']['model'] is None
    for name in ('containers','networks','volumes','snapshots'):
        c=read(ev/(name+'-after.json'));assert c['returncode']==0 and c['stdout']==''
    for p in ev.iterdir():
        if p.is_file():assert sha(p)==sha(copy/p.name)
for p in (packet/'preflight-only').glob('*/prerequisite-cleanup.json'):
    c=read(p);assert c['returncode']!=0 and 'no such object:' in c['stderr'].lower()
for p in (packet/'attempts').glob('*/prerequisite-cleanup.json'):
    c=read(p);assert c['returncode']!=0 and 'no such object:' in c['stderr'].lower()
artifacts=read(packet/'run-artifact-inventory.json')
for f in artifacts['files']:
    p=pathlib.Path(f['path']);assert p.stat().st_size==f['bytes'] and sha(p)==f['sha256'],str(p)
for line in (packet/'SHA256SUMS').read_text().splitlines():
    digest,rel=line.split('  ',1);assert sha(packet/rel)==digest,rel
# Check the exact authorized registry scope against this worktree's baseline.
baseline=json.loads(subprocess.check_output(['git','show','HEAD:docs/dataset-blockers.json'],cwd=repo))
current=read(repo/'docs/dataset-blockers.json')
old=next(b for b in baseline['shared_blockers'] if b['id']=='scorer-offline-closure')
new=next(b for b in current['shared_blockers'] if b['id']=='scorer-offline-closure')
assert new['observed'].startswith(old['observed'])
new['observed']=old['observed'];new['evidence']=old['evidence']
assert current==baseline,'Unexpected registry scope change'
print(json.dumps(dict(verified=True,task_references=len(inv['rows']),driver_refusals=len(r['attempts']),new_raw_measured=0,cumulative_raw_coverage=r['cumulative_official_execution_fraction'],external_artifacts_verified=len(artifacts['files']),registry_scope='scorer-offline-closure observed/evidence only',endpoint=None)))
