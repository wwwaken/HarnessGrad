"""Extract exact earlier import witnesses; retain current host source and build records."""
import hashlib
import json
import pathlib
import sys
from acquire import HERE, save

old=HERE.parent/'hg_wwheelhouse'
records=json.loads((old/'installed-distributions.json').read_text())
service=records['mkl-service']
scope=json.loads((old/'source-scope.json').read_text())['datasets']
witnesses={'recorded_provider':service, 'affected':{}, 'recorded_modules':{}}
for name,r in scope.items():
    if 'mkl-service' not in [x.lower().replace('_','-') for x in r.get('imported_distributions',[])]:continue
    witnesses['affected'][name]={'source_paths':r.get('source_paths',[]), 'imported_distributions':r['imported_distributions']}
for p in sorted((old/'audit').glob('*.stdout.json')):
    d=json.loads(p.read_text())
    mods=[m for m in d['modules'] if m['name']=='numpy' or m['name']=='mkl' or m['name'].startswith('mkl.')]
    if mods:witnesses['recorded_modules'][p.name]={'requested':d['requested'],'errors':d['errors'],'mkl_numpy_modules':mods}
for witness in service['source_witnesses']:
    path=pathlib.Path(witness['path']);lines=path.read_text().splitlines()
    assert lines[witness['line']-1].strip()==witness['text']
    witnesses['current_host_witness']={'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(), 'lines':lines}
    (HERE/'numpy-distributor-init.numbered.txt').write_text(''.join(f'{path}:{i}: {s}\n' for i,s in enumerate(lines,1)))
for rel in ['numpy/__init__.py','mkl/__init__.py']:
    p=pathlib.Path(sys.prefix)/'lib/python3.12/site-packages'/rel
    (HERE/(rel.split('/')[0]+'-init.numbered.txt')).write_text(''.join(f'{p}:{i}: {s}\n' for i,s in enumerate(p.read_text().splitlines(),1)))
save(HERE/'profile-evidence.json',witnesses)
print(json.dumps({'affected_recorded_groups':list(witnesses['affected']), 'provider':service},indent=2))
