"""Discover exact bootstrap candidates then independently fetch public wheels outside repo."""
import email
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from packaging.markers import default_environment
from packaging.tags import sys_tags
from packaging.utils import canonicalize_name, parse_wheel_filename
from common import HERE, ROOT, digest, run, save, clean_env

assert not (HERE/'inputs.json').exists()
audit=json.loads((HERE/'source-audit.json').read_text())
work=Path(tempfile.mkdtemp(prefix='hg-wresolver5-tb-artifacts-'))
wheelhouse=work/'exact-wheels';wheelhouse.mkdir()
env=clean_env(work)
profiles={};candidates={}
for r in audit['selected']:
    name=r['task_id'];dest=work/('discovery-'+name);dest.mkdir()
    command=run('discover-'+name,[sys.executable,'-m','pip','--isolated','--disable-pip-version-check','download',
        '--no-cache-dir','--only-binary=:all:','--dest',dest,'-r',HERE/'profiles'/name/'roots.in'],env=env)
    assert command['exit_code']==0, name
    files=sorted(dest.glob('*.whl'))
    assert len(files)<=32 and sum(p.stat().st_size for p in files)<=64*1024*1024
    profiles[name]=[]
    for p in files:
        key,version,_,_=parse_wheel_filename(p.name);key=canonicalize_name(key)
        artifact_key=key+'=='+str(version)
        profiles[name].append(artifact_key)
        if artifact_key in candidates:
            assert digest(p)==candidates[artifact_key]['discovery_sha256']
        else:candidates[artifact_key]={'key':key,'version':str(version),'filename':p.name,'discovery_path':str(p),'discovery_sha256':digest(p)}
artifacts=[]
for key,record in sorted(candidates.items()):
    url=f"https://pypi.org/pypi/{record['key']}/{record['version']}/json"
    with urllib.request.urlopen(url,timeout=45) as response:
        body=response.read(1024*1024+1);status=response.status
    assert len(body)<=1024*1024 and status==200
    index=json.loads(body);offered=next(x for x in index['urls'] if x['filename']==record['filename'])
    record['index_receipt']={'url':url,'status':status,'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest(),'body_retained':False}
    path=wheelhouse/record['filename']
    with urllib.request.urlopen(offered['url'],timeout=45) as response, path.open('xb') as stream:
        total=0
        while data:=response.read(65536):
            total+=len(data);assert total<=16*1024*1024
            stream.write(data)
        status=response.status
    assert status==200
    computed=digest(path)
    assert computed==record['discovery_sha256']==offered['digests']['sha256']
    assert path.stat().st_size==offered['size']
    record.update(path=str(path),url=offered['url'],status=status,sha256=computed,bytes=path.stat().st_size,
                  advertised_sha256=offered['digests']['sha256'],advertised_size=offered['size'])
    with zipfile.ZipFile(path) as archive:
        metaname=next(x for x in archive.namelist() if x.endswith('.dist-info/METADATA'))
        wheelname=next(x for x in archive.namelist() if x.endswith('.dist-info/WHEEL'))
        metadata=archive.read(metaname); wheel=archive.read(wheelname)
        meta=email.message_from_bytes(metadata)
        assert canonicalize_name(meta['Name'])==record['key'] and meta['Version']==record['version']
        # Retain exact small metadata text, no package/source payloads.
        out=HERE/'metadata'/key;out.mkdir(parents=True)
        (out/'METADATA.txt').write_bytes(metadata);(out/'WHEEL.txt').write_bytes(wheel)
        record['metadata']={kind:{'member':member,'path':str((out/(kind+'.txt')).relative_to(ROOT)),
            'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)} for kind,member,data in [('METADATA',metaname,metadata),('WHEEL',wheelname,wheel)]}
        record['requires_dist']=meta.get_all('Requires-Dist',[])
        record['requires_python']=meta.get('Requires-Python')
    record['matching_tags']=sorted(map(str,parse_wheel_filename(path.name)[3]&set(sys_tags())))
    assert record['matching_tags']
    artifacts.append(record)
for name,keys in profiles.items():
    (HERE/'profiles'/name/'constraints.txt').write_text(''.join(key+'\n' for key in sorted(keys)))
save(HERE/'inputs.json',{'artifact_directory':str(work),'wheel_directory':str(wheelhouse),'profiles':profiles,'artifacts':artifacts,
    'bounds':{'max_wheels_per_profile':32,'max_bytes_per_profile':64*1024*1024,'max_http_wheel_bytes':16*1024*1024,'max_index_response_bytes':1024*1024,'http_timeout_seconds':45,'subprocess_timeout_seconds':180},
    'python':{'version':sys.version,'executable':sys.executable,'sha256':digest(sys.executable),'marker_environment':default_environment(),'tags':list(map(str,sys_tags()))}})
run('wheel-sha256sum',['sha256sum',*[a['path'] for a in artifacts]])
print(json.dumps({'artifact_directory':str(work),'unique_wheels':len(artifacts),'unique_bytes':sum(a['bytes'] for a in artifacts),
    'profiles':{n:{'wheels':len(keys),'bytes':sum(a['bytes'] for a in artifacts if a['key']+'=='+a['version'] in keys)} for n,keys in profiles.items()},'artifacts':artifacts},indent=2))
