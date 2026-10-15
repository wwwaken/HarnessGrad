"""Acquire exact artifacts into /tmp; retain URLs/digests/metadata, never bodies."""
import email
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import urllib.parse
import urllib.request
import zipfile
from common import HERE, clean_env, digest, run, save

assert not (HERE/'artifacts.json').exists()
work = Path(tempfile.mkdtemp(prefix='hg-wresolver5-acquire-'))
candidates = work/'candidates'
candidates.mkdir()
exact = work/'exact'
exact.mkdir()
max_file = 384*1024*1024
max_total = 1536*1024*1024


def fetch(url, destination, limit):
    assert not destination.exists()
    request = urllib.request.Request(url, headers={'User-Agent':'HarnessGrad-offline-metadata-audit'})
    count = 0
    with urllib.request.urlopen(request, timeout=45) as response, destination.open('xb') as stream:
        while block := response.read(1024*1024):
            count += len(block)
            if count > limit:
                raise ValueError(f'Byte limit exceeded: {url}')
            stream.write(block)
        stream.flush()
        receipt = dict(url=url, final_url=response.url, status=response.status,
                       filename=destination.name, bytes=count, sha256=digest(destination))
    print(json.dumps(receipt,sort_keys=True),flush=True)
    return receipt


def version_index(name, version):
    path = work/(name+'-'+version+'.json')
    receipt = fetch(f'https://pypi.org/pypi/{name}/{version}/json', path, 8*1024*1024)
    data = json.loads(path.read_text())
    return data, receipt


pip_index, pip_index_receipt = version_index('pip','25.0.1')
pip_info = next(x for x in pip_index['urls'] if x['filename']=='pip-25.0.1-py3-none-any.whl')
pip_path = work/pip_info['filename']
pip_receipt = fetch(pip_info['url'],pip_path,8*1024*1024)
assert pip_receipt['sha256'] == pip_info['digests']['sha256']
save(HERE/'tool.json', dict(artifact=pip_receipt, index=pip_index_receipt, outside_directory=str(work)))
env = clean_env(work)
env['PYTHONPATH'] = str(pip_path)
target_code = """import json,platform,sys,sysconfig
from pip._vendor.packaging.markers import default_environment
from pip._vendor.packaging.tags import sys_tags
print(json.dumps(dict(executable=sys.executable,version=sys.version,SOABI=sysconfig.get_config_var('SOABI'),marker_environment=default_environment(),tags=[str(x) for x in sys_tags()]),sort_keys=True))
"""
target_result = run('target',['/usr/bin/python3.10','-c',target_code], env=env)
assert target_result['exit_code']==0
target = json.loads((HERE/'raw/target.stdout.txt').read_text())
target['executable_sha256'] = digest(target['executable'])
save(HERE/'target.json',target)

torch_index_path = work/'torch-cpu-index.html'
torch_index = fetch('https://download.pytorch.org/whl/cpu/torch/',torch_index_path,8*1024*1024)
links = [urllib.parse.urljoin(torch_index['final_url'],s) for s in re.findall(r'href="([^"]+)"',torch_index_path.read_text())]
links = [s for s in links if urllib.parse.unquote(s.split('#')[0]).endswith('torch-2.2.0+cpu-cp310-cp310-linux_x86_64.whl')]
assert len(links)==1, links
torch_url, fragment = urllib.parse.urldefrag(links[0])
torch_path = candidates/urllib.parse.unquote(torch_url.rsplit('/',1)[1])
torch_receipt = fetch(torch_url,torch_path,max_file)
assert torch_receipt['sha256']==urllib.parse.parse_qs(fragment)['sha256'][0]
save(HERE/'torch-origin.json',dict(index=torch_index,artifact=torch_receipt,selected_link=links[0]))
constraint = work/'torch-constraint.txt'
constraint.write_text('torch==2.2.0+cpu\n')
result = run('discovery', ['/usr/bin/python3.10','-m','pip','--isolated','--disable-pip-version-check','download',
             '--only-binary=:all:','--no-cache-dir','--progress-bar','off','--timeout','25','--retries','1',
             '--index-url','https://pypi.org/simple','--find-links',candidates,'-r',HERE/'profile/roots.in',
             '-c',constraint,'--dest',candidates],env=env,timeout=900)
assert result['exit_code']==0, result
files = sorted(candidates.glob('*.whl'))
assert len(files)<=150 and sum(p.stat().st_size for p in files)<=max_total
records = []
for path in files:
    with zipfile.ZipFile(path) as wheel:
        metadata = email.message_from_bytes(wheel.read(next(n for n in wheel.namelist() if n.endswith('.dist-info/METADATA'))))
        wheel_meta = email.message_from_bytes(wheel.read(next(n for n in wheel.namelist() if n.endswith('.dist-info/WHEEL'))))
    name, version = metadata['Name'], metadata['Version']
    if name.lower()=='torch':
        receipt = fetch(torch_url,exact/path.name,max_file)
        index_receipt = torch_index
        expected = torch_receipt['sha256']
    else:
        index, index_receipt = version_index(name,version)
        entry = next(e for e in index['urls'] if e['filename']==path.name)
        receipt = fetch(entry['url'],exact/path.name,max_file)
        expected = entry['digests']['sha256']
    assert receipt['sha256']==expected==digest(path)
    records.append(dict(name=name,version=version,**receipt,index=index_receipt,
                        requires_python=metadata.get('Requires-Python'),requires_dist=metadata.get_all('Requires-Dist',[]),
                        provides_extra=metadata.get_all('Provides-Extra',[]),wheel_tags=wheel_meta.get_all('Tag',[])))
assert sum(r['bytes'] for r in records)<=max_total
save(HERE/'artifacts.json',dict(directory=str(exact),candidate_directory=str(candidates),artifacts=records,
     limits=dict(max_wheels=150,max_profile_bytes=max_total,max_file_bytes=max_file,index_bytes=8*1024*1024,http_timeout_seconds=45),
     acquisition_note='Discovery pip has process/network time bounds and post-download count/size checks; exact independent refetch streams enforce byte limits. No pre-download pip quota is claimed.'))
constraints = ''.join(f"{r['name']}=={r['version']}\n" for r in sorted(records,key=lambda r:r['name'].lower()))
assert not (HERE/'profile/constraints.txt').exists()
(HERE/'profile/constraints.txt').write_text(constraints)
run('wheel-sha256sum',['sha256sum',*[exact/r['filename'] for r in records]])
print(json.dumps(dict(artifacts=len(records),bytes=sum(r['bytes'] for r in records),outside_directory=str(work)),sort_keys=True))
