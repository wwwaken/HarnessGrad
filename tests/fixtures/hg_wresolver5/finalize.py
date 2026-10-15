"""Fresh exact-candidate audit after redundant refetch was stopped; no rediscovery.

Initial pip discovery obtained the complete candidate wheels outside git. Audit
those bytes against exact version-index entries, independently rehash them, and
retain an explicit correction for unflushed initial index-digest receipts.
"""
import email
import json
from pathlib import Path
import urllib.request
import zipfile
from common import HERE, digest, run, save

assert not (HERE/'artifacts.json').exists()
work=Path(json.loads((HERE/'tool.json').read_text())['outside_directory'])
candidates=work/'candidates'
initial=[]
for line in (HERE/'acquire.stdout.txt').read_text().splitlines():
    if line.startswith('{'):
        initial.append(json.loads(line))
corrections=[]
for receipt in initial:
    if receipt['filename'].endswith(('.json','.html')):
        path=work/receipt['filename']
        actual=digest(path)
        if actual!=receipt['sha256']:
            corrections.append(dict(path=str(path),captured_sha256=receipt['sha256'],
                                    recomputed_sha256=actual,bytes=path.stat().st_size,
                                    reason='Initial fetch hashed before flushing a small buffered file. Actual response bytes remain outside git; independently rehashed after close.'))
save(HERE/'attempts/acquisition-correction.json',dict(initial_process_exit_code=143,
     disposition='Parent deliberately SIGTERMed only its redundant refetch process after identifying the unflushed-small-index hash bug and a stalled redundant wheel transfer. Initial completed pip discovery and all payloads/partial transfers are preserved outside git. No dataset/scorer/run ID was launched or resumed.',
     original_script='attempts/acquire-executed-initial.py',corrections=corrections))
assert json.loads((HERE/'raw/discovery.command.json').read_text())['exit_code']==0
torch=json.loads((HERE/'torch-origin.json').read_text())
records=[]
index_paths=[]
for path in sorted(candidates.glob('*.whl')):
    with zipfile.ZipFile(path) as wheel:
        meta=email.message_from_bytes(wheel.read(next(n for n in wheel.namelist() if n.endswith('.dist-info/METADATA'))))
        wheel_meta=email.message_from_bytes(wheel.read(next(n for n in wheel.namelist() if n.endswith('.dist-info/WHEEL'))))
    name,version=meta['Name'],meta['Version']
    if name.lower()=='torch':
        index_path=work/'torch-cpu-index.html'
        source=torch['artifact']
        expected=source['sha256']
        index_url=torch['index']['url']
        status=torch['index']['status']
    else:
        index_path=work/(name+'-'+version+'.json')
        index_url=f'https://pypi.org/pypi/{name}/{version}/json'
        if not index_path.exists():
            request=urllib.request.Request(index_url,headers={'User-Agent':'HarnessGrad-offline-metadata-audit'})
            with urllib.request.urlopen(request,timeout=45) as response:
                body=response.read(8*1024*1024+1)
                assert len(body)<=8*1024*1024
                index_path.write_bytes(body)
                status=response.status
        else:
            prior=next(r for r in initial if r['url']==index_url)
            status=prior['status']
        index=json.loads(index_path.read_text())
        source=next(e for e in index['urls'] if e['filename']==path.name)
        expected=source['digests']['sha256']
        assert path.stat().st_size==source['size']
    assert status==200
    sha=digest(path)
    assert sha==expected,(path.name,sha,expected)
    record=dict(name=name,version=version,filename=path.name,bytes=path.stat().st_size,
                sha256=sha,url=source['url'],status=200,
                index=dict(url=index_url,status=status,bytes=index_path.stat().st_size,sha256=digest(index_path)),
                requires_python=meta.get('Requires-Python'),requires_dist=meta.get_all('Requires-Dist',[]),
                provides_extra=meta.get_all('Provides-Extra',[]),wheel_tags=wheel_meta.get_all('Tag',[]))
    records.append(record)
    index_paths.append(index_path)
    print(json.dumps(record,sort_keys=True),flush=True)
assert len(records)<=150 and sum(r['bytes'] for r in records)<=1536*1024*1024
assert all(r['bytes']<=384*1024*1024 for r in records)
save(HERE/'artifacts.json',dict(directory=str(candidates),artifacts=records,
     limits=dict(max_wheels=150,max_profile_bytes=1536*1024*1024,max_file_bytes=384*1024*1024,index_bytes=8*1024*1024,http_timeout_seconds=45),
     acquisition_note='Pip discovery has a 900s subprocess bound and post-download count/size checks; no enforced pip pre-download quota is claimed. Complete original candidate wheels, not partial redundant refetches, are independently matched to exact public index entries and sha256sum. All bodies/payloads remain outside git.'))
(HERE/'profile/constraints.txt').write_text(''.join(f"{r['name']}=={r['version']}\n" for r in sorted(records,key=lambda r:r['name'].lower())))
run('wheel-sha256sum',['sha256sum',*[candidates/r['filename'] for r in records]])
run('index-sha256sum',['sha256sum',*index_paths])
print(json.dumps(dict(artifacts=len(records),bytes=sum(r['bytes'] for r in records),corrected_index_receipts=len(corrections)),sort_keys=True))
