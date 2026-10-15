#!/usr/bin/env python3
"""Read-only packet verification: no Docker, source adapter imports, network or task tests."""
import pathlib,json,hashlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];repo=ROOT.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=ROOT/'SHA256SUMS';members={}
for line in manifest.read_text().splitlines():
 h,name=line.split('  ',1);p=ROOT/name
 assert p.is_file() and sha(p)==h,name
 assert name not in members,name
 members[name]=h
actual={str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and p!=manifest and '__pycache__' not in p.parts}
assert actual==set(members),(actual-set(members),set(members)-actual)
for line in (ROOT/'artifacts/SHA256SUMS').read_text().splitlines():
 h,name=line.split('  ',1);assert sha(ROOT/'artifacts'/name)==h,name
r=json.loads((ROOT/'resolution.json').read_text());assert r['wheel_artifacts']==6 and r['apt_artifacts']==19
assert r['online_offline_package_and_python_abi_equal'] and r['online_offline_dpkg_equal']
s=json.loads((ROOT/'source/summary.json').read_text());assert s['tasks_in_recorded_surface']==89 and s['files_checked']==369 and s['all_match']
assert (s['uvx_tasks'],s['uv_tasks'],s['pip_tasks'])==(82,1,6)
for phase in ['online','offline']:
 c=json.loads((ROOT/f'raw/{phase}-container-inspect.stdout.txt').read_text())[0]
 assert c['State']['ExitCode']==0
 assert c['HostConfig']['NetworkMode']==('none' if phase=='offline' else 'bridge')
 assert c['Image']=='sha256:4c948a4e630af2435ae0a19108fc0814a946ac2fa29a512469e0fc77b38c8c12'
 assert c['HostConfig']['NanoCpus']==1000000000 and c['HostConfig']['Memory']==1073741824 and c['HostConfig']['PidsLimit']==128
 assert json.loads((ROOT/f'raw/{phase}-cleanup.command.json').read_text())['returncode']==0
assert json.loads((ROOT/'raw/attempt1-online.command.json').read_text())['returncode']==1
assert 'pytest 8.4.1' in (ROOT/'raw/offline.stdout.txt').read_text()
assert '--ctrf=CTRF' in (ROOT/'raw/offline.stdout.txt').read_text()
assert (ROOT/'raw/offline.stdout.txt').read_text().count('Network is unreachable')==2
before=json.loads(subprocess.check_output(['git','show',(ROOT/'source/platform-baseline.txt').read_text().strip()+':docs/dataset-blockers.json'],cwd=repo,text=True));after=json.loads((repo/'docs/dataset-blockers.json').read_text())
b=next(x for x in before['shared_blockers'] if x['id']=='scorer-offline-closure');a=next(x for x in after['shared_blockers'] if x['id']=='scorer-offline-closure')
assert a['observed'].startswith(b['observed'])
assert a['evidence'][:len(b['evidence'])]==b['evidence']
assert len(a['evidence'])==len(b['evidence'])+1
b['observed']=a['observed'];b['evidence']=a['evidence'];assert before==after,'Unrelated registry mutation'
for block in after['shared_blockers']:
 for e in block['evidence']:
  if e['kind']=='repository':assert e['locator'] in (repo/e['path']).read_text(),e
assert after['review']['production_authorized'] is False
print(json.dumps({'valid':True,'manifest_files':len(members),'wheels':6,'debs':19,'source_files_compared':369,'task_sources':89,'offline_bootstrap_tasks':1,'offline_docker_network':'none','registry_change':'observed append and one evidence entry only','production_authorized':False},indent=2))
