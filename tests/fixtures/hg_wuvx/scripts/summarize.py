#!/usr/bin/env python3
import sys,pathlib,json,hashlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
apt=[]
for p in sorted((ROOT/'artifacts/apt').glob('*.deb')):
 command=['dpkg-deb','-f',str(p),'Package','Version','Architecture','Depends','Pre-Depends']
 c=subprocess.run(command,text=True,capture_output=True,check=True)
 apt.append({'path':str(p.relative_to(ROOT)),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'argv':command,'stdout':c.stdout,'stderr':c.stderr})
(ROOT/'raw/apt-artifacts.json').write_text(json.dumps(apt,indent=2)+'\n')
on=json.loads((ROOT/'raw/online-python.json').read_text());off=json.loads((ROOT/'raw/offline-python.json').read_text());wh=json.loads((ROOT/'artifacts/wheels.json').read_text())
def packages(r):return {d['name'].lower():d['version'] for d in r['distributions']}
assert packages(on)==packages(off)
for k in ['version','real_executable','implementation','cache_tag','SOABI','EXT_SUFFIX','platform','libc','openssl','sqlite']:assert on[k]==off[k],k
assert (ROOT/'raw/online-dpkg.txt').read_bytes()==(ROOT/'raw/offline-dpkg.txt').read_bytes()
checks=[]
for w in wh:
 matches=[]
 for n,m in w['metadata'].items():
  candidates=[f for d in on['distributions'] for f in d['files'] if f['path'].endswith(n)]
  assert len(candidates)==1,(n,candidates)
  assert m['sha256']==candidates[0]['sha256'],n
  matches.append({'member':n,'sha256':m['sha256'],'matches_online_installed_file':True})
 checks.append({'wheel':w['path'],'metadata_checks':matches})
for phase in ['online','offline']:
 c=json.loads((ROOT/f'raw/{phase}-container-inspect.stdout.txt').read_text())[0]
 assert c['State']['ExitCode']==0
 assert c['HostConfig']['NetworkMode']==('none' if phase=='offline' else 'bridge')
 assert json.loads((ROOT/f'raw/{phase}-cleanup.command.json').read_text())['returncode']==0
result={'task':'openssl-selfsigned-cert','coverage':'one fresh tooling-bootstrap resolution; not historical transitive recovery or scoring','packages':packages(on),'python':{k:on[k] for k in ['version','real_executable','cache_tag','SOABI','libc','openssl']},'apt_artifacts':len(apt),'wheel_artifacts':len(wh),'online_offline_package_and_python_abi_equal':True,'online_offline_dpkg_equal':True,'wheel_metadata_matches_online_installed':checks,'containers_exit_and_cleanup_success':True}
(ROOT/'resolution.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
