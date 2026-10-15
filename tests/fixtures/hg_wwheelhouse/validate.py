"""Independently validate retained payload hashes, wheel identities and source witnesses."""
import hashlib
import json
import pathlib
import subprocess
import sys
import zipfile
from email.parser import BytesParser
from packaging.tags import sys_tags
from packaging.utils import canonicalize_name, parse_wheel_filename
from packaging.version import Version

HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while b:=f.read(4*1024*1024):h.update(b)
    return h.hexdigest()

m=json.loads((HERE/'manifest.json').read_text())
b=json.loads((HERE/'built-artifacts.json').read_text())
for key,r in m['artifacts'].items():
    if 'sha256' in r:
        assert r['status'] in ['obtained-wheel','obtained-sdist-build-pending'],key
        assert r['sha256']==r['advertised_sha256'],key
        assert r['bytes']==r['advertised_bytes'],key
        assert r['url'].startswith('https://files.pythonhosted.org/'),key
for key,r in b.items():
    assert r['status']=='built-offline',key
    assert r['source_sha256']==m['artifacts'][key]['sha256'],key
artifacts=[dict(key=k,**r) for k,r in m['artifacts'].items() if 'sha256' in r]
artifacts += [dict(key=k,kind='locally-built-wheel',**r) for k,r in b.items() if r['status']=='built-offline']
paths=[]
tags=set(sys_tags())
for r in artifacts:
    p=pathlib.Path(r['local_path'])
    assert p.name==r['filename'] and p.stat().st_size==r['bytes'],p
    assert sha(p)==r['sha256'],p
    paths.append(str(p))
    if p.suffix=='.whl':
        name,version,_,wt=parse_wheel_filename(p.name)
        assert wt & tags,p
        assert canonicalize_name(r['name'])==name and Version(r['version'])==version,p
        with zipfile.ZipFile(p) as z:
            meta=BytesParser().parsebytes(z.read(next(n for n in z.namelist() if n.endswith('.dist-info/METADATA'))))
            assert canonicalize_name(meta['Name'])==name and Version(meta['Version'])==version,p
        r['verified_tags']=sorted(str(t) for t in wt)
# A second, independent implementation supplies raw, recomputed digest output.
cmd=['sha256sum','--',*paths]
p=subprocess.run(cmd,capture_output=True,text=True,check=True)
(HERE/'sha256sum.payloads.txt').write_text(p.stdout)
(HERE/'sha256sum.command.json').write_text(json.dumps({'command':cmd,'exit_code':p.returncode},indent=2)+'\n')
for r,line in zip(artifacts,p.stdout.splitlines(),strict=True):assert line.split()[0]==r['sha256']
by_hash={r['sha256']:r for r in artifacts}
for lp in HERE.glob('*.lock'):
    for line in lp.read_text().splitlines():
        requirement,hash_spec=line.split()
        name,version=requirement.split('==')
        payload=by_hash[hash_spec.removeprefix('--hash=sha256:')]
        assert canonicalize_name(name)==canonicalize_name(payload['name']),lp
        assert Version(version)==Version(payload['version']),lp
(HERE/'SHA256SUMS.payloads').write_text(''.join(f"{r['sha256']}  {r['filename']}\n" for r in artifacts))
(HERE/'payload-index.json').write_text(json.dumps({'payload_directory':m['payload_directory'],'artifacts':artifacts},indent=2)+'\n')
source_records=json.loads((HERE/'source-imports.json').read_text())
for s in source_records:
    p=pathlib.Path(s['path']);p=p if p.is_absolute() else ROOT/p
    assert sha(p)==s['sha256'],p
    lines=p.read_text().splitlines()
    for i in s['imports']:
        assert i['text'].splitlines()[0] in lines[i['line']-1],(p,i)
for d in json.loads((HERE/'installed-distributions.json').read_text()).values():
    assert d['source_witnesses'],d['name']
    for w in d['source_witnesses']:
        p=pathlib.Path(w['path']);p=p if p.is_absolute() else ROOT/p
        assert w['text'].splitlines()[0] in p.read_text().splitlines()[w['line']-1],w
print(json.dumps({'payloads_rehashed_twice':len(artifacts),'total_bytes':sum(r['bytes'] for r in artifacts),
    'sources_rehashed':len(source_records),'wheel_identity_and_host_tag_checks':'PASS',
    'unavailable':[k for k,r in m['artifacts'].items() if 'sha256' not in r],
    'builds':{k:r['status'] for k,r in b.items()}},indent=2))
