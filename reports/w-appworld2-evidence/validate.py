"""Read-only integrity and scope checks; no endpoint/container/scorer execution."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
def read(name):return json.loads((OUT/name).read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def check(ok, message):
    if not ok: raise AssertionError(message)

launch=read('launch-input.json'); e=read('execution/diagnostic_execution.json'); s=read('execution/diagnostic_receipt.json'); summary=read('result-summary.json')
argv=launch['argv']
for flag,value in [('--sampling','diagnostic'),('--rounds','0'),('--trials','1'),('--jobs','1'),('--side','train'),('--improver','none')]:
    check(argv[argv.index(flag)+1]==value,flag)
check('--tasks' not in argv,'no hand-selected task')
check('--authorize-unobserved-diagnostic' in argv,'explicit diagnostic authorization')
check(launch['fresh_run_absent'] and launch['fresh_work_absent'],'fresh paths')
check(not Path(launch['run_root']).resolve().is_relative_to(ROOT),'run root outside platform')
check(not Path(launch['work_root']).resolve().is_relative_to(ROOT),'work root outside platform')
check(launch['environment']['HG_AGENT_BASE_URL']=='http://127.0.0.1:8002/v1','only authorized endpoint')
check(launch['environment']['HG_AGENT_MODEL']=='qwen3.5-9b-local','model binding')
check(not read('inherited-overrides.json') and not read('dotenv-overrides.json'),'no inherited overrides')
check(read('endpoint-completion.raw.json')['choices'][0]['message']['content']=='OK','real completion')
check(read('driver-result.json')['returncode']==2,'retained publication refusal')
check(e['invalid']=={} and e['harness_failed']=={},'no runtime invalid substituted for zero')
raw=e['verdicts'][launch['task_id']]
check(raw['evidence']['measured'] is True and raw['evidence']['success'] is False and raw['score']==0.0,'authentic raw measured loss')
check(not raw.get('unmeasured'),'scorer measured')
check(len(raw['evidence']['passes'])==6 and len(raw['evidence']['failures'])==2 and raw['evidence']['num_tests']==8,'requirement coverage')
check(s['score'] is None and s['coverage']['measured_trials']==0 and s['coverage']['unmeasured_trials']==1 and s['coverage']['invalid_trials']==0,'formal unmeasured preserved')
check(s['enforcement']['policy_enforcement_observed'] is False and s['enforcement']['production_authorized'] is False and s['enforcement']['comparable'] is False,'no authorization claim')
check(s['context']['hashes']['model'] is None,'unknown weight hash retained')
check(e['identity_declared']['config']['max_steps']==32 and e['identity_declared']['config']['max_output_tokens']==2048,'unchanged budget')
check(summary['api_call_count']==14 and summary['actor_commands']==15 and len(summary['reply_steps'])==16,'trace coverage')
check(summary['submissions']==[dict(step=15,submitted=True,missing=[])],'voluntary early submission')
check(not any(c['url'].startswith('/supervisor') and c['method']!='get' for c in summary['api_routes']),'no supervisor completion')
roles=read('role-observations.json')
check(set(roles)=={'actor','service','verifier'},'three roles observed')
for role,data in roles.items():
    check(any(o['state']['Running'] for o in data['observations']),role+' running observation')
    check(data['observations'][-1]['state']['ExitCode']==(137 if role=='service' else 0),role+' exit')
    for obs in data['observations']:
        check(obs['resource']['NanoCpus']==2000000000 and obs['resource']['Memory']==4294967296 and obs['resource']['PidsLimit']==1024,role+' configured resources')
cleanup=read('cleanup-observations.json')
check(len(cleanup['containers'])==3 and all(o['returncode']==1 and o['stdout']=='[]\n' for o in cleanup['containers']),'role containers absent')
check(cleanup['networks'] and all(o['returncode']==1 for o in cleanup['networks']),'owned network absent')
check(all(not o['exists'] for o in cleanup['temporary_paths']),'temporary paths absent')
check(all(not o['proc_exists'] for o in read('cleanup-processes-after.json')['processes']),'sampled PIDs absent')
for row in read('artifact-copy-provenance.json'):
    for p in [Path(row['source']),OUT/row['copy']]:
        check(p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],'original/review copy '+str(p))
for row in read('review-source-hashes.json'):
    check(sha(ROOT/row['path'])==row['sha256'],'runtime source unchanged '+row['path'])
check(read('runtime-unchanged.json')['returncode']==0 and read('runtime-unchanged.json')['stdout']=='','runtime unchanged')
base=read('baseline.json')['stdout'].strip()
def git_at(path):
    return subprocess.check_output(['git','show',base+':'+path],cwd=ROOT,text=True)
old=json.loads(git_at('docs/dataset-blockers.json')); new=json.loads((ROOT/'docs/dataset-blockers.json').read_text())
oldtarget=next(x for x in old['datasets'] if x['dataset']=='appworld')['blockers'][0]
newtarget=next(x for x in new['datasets'] if x['dataset']=='appworld')['blockers'][0]
check({k:v for k,v in newtarget.items() if k not in {'observed','evidence'}}=={k:v for k,v in oldtarget.items() if k not in {'observed','evidence'}},'target status/family/next_action unchanged')
check(newtarget['observed'].startswith(oldtarget['observed']+' '),'observation append only')
check(newtarget['evidence'][:len(oldtarget['evidence'])]==oldtarget['evidence'],'old evidence preserved')
check(len(newtarget['evidence'])==len(oldtarget['evidence'])+2,'only two new locators')
restored=copy.deepcopy(new)
next(x for x in restored['datasets'] if x['dataset']=='appworld')['blockers'][0]=oldtarget
check(restored==old,'only exact target observed/evidence changed; shared, history, other datasets unchanged')
journal=(ROOT/'docs/adapter-integration-journal.md').read_text(); oldjournal=git_at('docs/adapter-integration-journal.md')
check(journal.startswith(oldjournal),'historical journal unchanged')
check('## 2026-10-15 AppWorld unchanged-budget actor diagnostic - w-appworld2' in journal[len(oldjournal):],'new journal heading')
for ev in newtarget['evidence']:
    if ev['kind']=='repository': check(ev['locator'] in (ROOT/ev['path']).read_text(),'verbatim locator '+ev['path'])
packet=OUT/'packet-sha256.json'
if packet.exists():
    manifest=read('packet-sha256.json')
    actual={str(p.relative_to(OUT)) for p in OUT.rglob('*') if p.is_file() and p!=packet and '__pycache__' not in p.parts}
    check(actual==set(manifest),'complete packet inventory')
    for rel,row in manifest.items():
        p=OUT/rel;check(sha(p)==row['sha256'] and p.stat().st_size==row['bytes'],'packet hash '+rel)
if '--index' in sys.argv:
    for rel in [*manifest, 'packet-sha256.json']:
        source=OUT/rel
        indexed=subprocess.check_output(['git','show',':'+str(source.relative_to(ROOT))],cwd=ROOT)
        check(hashlib.sha256(indexed).hexdigest()==sha(source),'index bytes '+rel)
print(json.dumps(dict(valid=True,run_id=launch['run_id'],raw_measured_loss=True,formal_unmeasured=True,
    copied_run_files=len(read('artifact-copy-provenance.json')),packet_files=(len(manifest) if packet.exists() else None),
    exact_registry_scope=True,unchanged_runtime=True,successful_task_blocker='OPEN',production_authorized=False),indent=2))
