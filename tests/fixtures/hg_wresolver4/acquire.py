"""Bounded exact-candidate wheel acquisition. No packages/builds are executed."""
import importlib.metadata as installed
import json
from pathlib import Path
import shutil
import subprocess
import sys
import sysconfig
import tempfile
from packaging.requirements import Requirement
from common import HERE,ROOT,save,digest,run
from artifacts import fetch,inspect,records,rank,normalize
from packaging.utils import parse_wheel_filename

assert not (HERE/'inputs-gaia.json').exists()
work=Path(tempfile.mkdtemp(prefix='hg-wresolver4-gaia-payloads-'))
wheels=work/'wheels';wheels.mkdir()
roots=['numpy','openpyxl','pillow','requests','beautifulsoup4','lxml','pyarrow']
prior=json.loads((ROOT/'tests/fixtures/hg_wresolver3/inputs.json').read_text())
old={a['key']:a for a in prior['artifacts']}
observed={}
pending=[Requirement(n) for n in roots]
edges=[]
while pending:
 req=pending.pop(0);key=normalize(req.name)
 if key in records:
  assert req.specifier.contains(records[key]['version'])
  continue
 assert len(records)<120
 d=installed.distribution(key);version=d.version
 observed[key]={'version':version,'metadata':d.read_text('METADATA'),'wheel':d.read_text('WHEEL')}
 save(HERE/'observed-gaia.json',observed)
 assert req.specifier.contains(version),(str(req),version)
 if key in old and old[key]['version']==version:
  a=old[key];source=Path(a['path']);assert digest(source)==a['sha256']
  dest=wheels/source.name;shutil.copyfile(source,dest)
  rec=inspect(dest,{'kind':'retained-w-resolver3','source':str(source),'source_sha256':digest(source)})
 else:
  url=f'https://pypi.org/pypi/{key}/{version}/json'
  data=json.loads(fetch(url,HERE/'index'/f'{key}-{version}.json',8*1024*1024))
  choices=[]
  for a in data['urls']:
   if a['packagetype']=='bdist_wheel' and not a.get('yanked'):
    matching=parse_wheel_filename(a['filename'])[3]&rank.keys()
    if matching:choices.append((min(rank[t] for t in matching),a['filename'],a))
  save(HERE/'index'/f'{key}-{version}-selection.json',{'compatible':[a[1] for a in sorted(choices)],'sdists':[a['filename'] for a in data['urls'] if a['packagetype']=='sdist']})
  assert choices,f'No compatible exact wheel {key}=={version}; investigate retained payloads and upstream'
  a=sorted(choices)[0][2];dest=wheels/a['filename']
  fetch(a['url'],dest,64*1024*1024)
  shutil.move(str(dest.with_name(dest.name+'.http.json')),HERE/'index'/(dest.name+'.http.json'))
  assert digest(dest)==a['digests']['sha256'] and dest.stat().st_size==a['size']
  rec=inspect(dest,{'kind':'pypi-exact-version','index_url':url,'url':a['url'],'advertised_sha256':a['digests']['sha256']})
 assert rec['version']==version
 for literal in rec['requires_dist']:
  child=Requirement(literal);active=child.marker is None or child.marker.evaluate({'extra':''})
  edges.append({'parent':key,'requirement':literal,'active':active})
  if active:pending.append(child)
 assert sum(a['bytes'] for a in records.values())<=320*1024*1024
 save(HERE/'gaia-progress.json',{'artifacts':list(records.values()),'edges':edges,'pending':list(map(str,pending))})
profile=HERE/'profiles/gaia';profile.mkdir(parents=True)
profile.joinpath('roots.in').write_text(''.join(f'{n}=={observed[n]["version"]}\n' for n in roots))
profile.joinpath('constraints.txt').write_text(''.join(f'{a["name"]}=={a["version"]}\n' for a in records.values()))
save(HERE/'inputs-gaia.json',{'wheel_directory':str(wheels),'artifacts':list(records.values()),'profiles':{'gaia':profile.joinpath('roots.in').read_text().splitlines()},'edges':edges})
save(HERE/'target-gaia.json',{'sys_version':sys.version,'executable':sys.executable,'sha256':digest(sys.executable),'SOABI':sysconfig.get_config_var('SOABI'),'tags':list(map(str,rank)),'baseline_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()})
run('gaia-wheel-sha256sum',['sha256sum',*[a['path'] for a in records.values()]])
print(json.dumps({'artifacts':len(records),'bytes':sum(a['bytes'] for a in records.values()),'roots':profile.joinpath('roots.in').read_text().splitlines(),'payloads':str(wheels)},sort_keys=True))
