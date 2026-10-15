"""Reacquire exact wheel-only discovery selection through captured versioned JSON."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import sysconfig
import tempfile
from common import HERE,ROOT,save,digest,run
from artifacts_appworld import fetch,inspect,records,rank
from pip._vendor.packaging.markers import default_environment

assert not (HERE/'inputs-appworld.json').exists()
candidates=Path('/tmp/hg-wresolver4-appworld-candidates')
files=sorted(candidates.glob('*.whl'))
assert files and len(files)<=120
assert sum(p.stat().st_size for p in files)<=320*1024*1024
assert max(p.stat().st_size for p in files)<=64*1024*1024
work=Path(tempfile.mkdtemp(prefix='hg-wresolver4-appworld-payloads-'))
wheels=work/'wheels';wheels.mkdir()
for source in files:
 # Inspect candidate bytes first, then independently fetch exact same public artifact.
 rec=inspect(source,{'kind':'wheel-only-discovery'})
 key,version=rec['key'],rec['version']
 url=f'https://pypi.org/pypi/{key}/{version}/json'
 data=json.loads(fetch(url,HERE/'index-appworld'/f'{key}-{version}.json',8*1024*1024))
 a=next(a for a in data['urls'] if a['filename']==source.name)
 assert a['packagetype']=='bdist_wheel' and not a.get('yanked')
 dest=wheels/source.name
 fetch(a['url'],dest,64*1024*1024)
 shutil.move(str(dest.with_name(dest.name+'.http.json')),HERE/'index-appworld'/(dest.name+'.http.json'))
 assert digest(dest)==a['digests']['sha256']==digest(source) and dest.stat().st_size==a['size']
 inspect(dest,{'kind':'pypi-exact-version','index_url':url,'url':a['url'],'advertised_sha256':a['digests']['sha256'],'candidate_path':str(source),'candidate_sha256':digest(source)})
 save(HERE/'appworld-progress.json',{'artifacts':list(records.values())})
profile=HERE/'profiles/appworld';profile.mkdir(parents=True)
profile.joinpath('roots.in').write_text('appworld==0.1.3.post1\nuvicorn<1\n')
profile.joinpath('constraints.txt').write_text(''.join(f'{a["name"]}=={a["version"]}\n' for a in records.values()))
save(HERE/'inputs-appworld.json',{'wheel_directory':str(wheels),'artifacts':list(records.values()),'profiles':{'appworld':profile.joinpath('roots.in').read_text().splitlines()}})
save(HERE/'target-appworld.json',{'sys_version':sys.version,'executable':sys.executable,'sha256':digest(sys.executable),'SOABI':sysconfig.get_config_var('SOABI'),'tags':list(map(str,rank)),'marker_environment':default_environment(),'baseline_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()})
run('appworld-wheel-sha256sum',['sha256sum',*[a['path'] for a in records.values()]])
print(json.dumps({'artifacts':len(records),'bytes':sum(a['bytes'] for a in records.values()),'payloads':str(wheels),'target':sys.version},sort_keys=True))
