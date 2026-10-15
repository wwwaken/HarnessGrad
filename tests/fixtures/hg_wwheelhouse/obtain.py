"""Obtain exact-version public artifacts, recomputing every digest from the payload."""
import concurrent.futures
import hashlib
import importlib.metadata as md
import json
import os
import pathlib
import tempfile
import time
import urllib.error
import urllib.request
from packaging.tags import sys_tags
from packaging.utils import parse_wheel_filename

HERE = pathlib.Path(__file__).resolve().parent
TAGS = list(sys_tags())
RANK = {t:i for i,t in enumerate(TAGS)}
PROXY = 'http://172.17.0.1:17890'
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY}))

def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        while b := f.read(4*1024*1024): h.update(b)
    return h.hexdigest()

def obtain(item):
    key, installed = item
    version = installed['version']
    url = f'https://pypi.org/pypi/{key}/{version}/json'
    result = {'name': installed['name'], 'version': version, 'index': 'https://pypi.org/simple/',
              'metadata_url': url, 'role': installed.get('role','scoring-import'),
              'installed_wheel': installed.get('installed_wheel'), 'installed_direct_url': installed.get('direct_url')}
    try:
        with OPENER.open(url, timeout=60) as response:
            raw = response.read()
            result['metadata_http_status'] = response.status
        (HERE/'index'/f'{key}.json').write_bytes(raw)
        result['metadata_sha256'] = hashlib.sha256(raw).hexdigest()
        data = json.loads(raw)
        wheels = []
        for a in data['urls']:
            if a['packagetype'] != 'bdist_wheel': continue
            try: tags = parse_wheel_filename(a['filename'])[3]
            except ValueError: continue
            ranks = [RANK[t] for t in tags if t in RANK]
            if ranks: wheels.append((min(ranks),a))
        candidates = [min(wheels,key=lambda x:x[0])[1]] if wheels else [a for a in data['urls'] if a['packagetype']=='sdist']
        if not candidates:
            result.update(status='not-obtainable-on-target', reason='PyPI release has no compatible CPython 3.12 Linux x86_64 wheel and no sdist; see preserved release JSON.')
            return key,result
        a = candidates[0]
        result.update(filename=a['filename'], url=a['url'], advertised_sha256=a['digests']['sha256'],
                      kind=a['packagetype'], advertised_bytes=a['size'])
        if a['packagetype']=='bdist_wheel':
            result['artifact_tags'] = sorted(str(t) for t in parse_wheel_filename(a['filename'])[3])
            result['matching_target_tags'] = [str(t) for t in TAGS if t in parse_wheel_filename(a['filename'])[3]]
        else:
            result['artifact_tags'] = []
            result['tag_note'] = 'Source distribution has no wheel/platform tag; an offline build is required.'
        path = PAYLOADS / a['filename']
        start = time.monotonic()
        with OPENER.open(a['url'], timeout=180) as r, path.open('xb') as f:
            result['http_status'] = r.status
            result['response_url'] = r.url
            result['response_headers'] = dict(r.headers)
            while b := r.read(4*1024*1024): f.write(b)
        result.update(local_path=str(path), bytes=path.stat().st_size, sha256=digest(path),
                      elapsed_seconds=round(time.monotonic()-start,3))
        assert result['bytes']==a['size'], 'Length mismatch'
        assert result['sha256']==a['digests']['sha256'], 'Digest mismatch'
        result['status']='obtained-wheel' if a['packagetype']=='bdist_wheel' else 'obtained-sdist-build-pending'
    except Exception as exc:
        result.update(status='obtain-failed', reason=repr(exc))
    return key,result

if __name__=='__main__':
    records=json.loads((HERE/'installed-distributions.json').read_text())
    # Build-only tools are separate from runtime requirements; no arbitrary new versions.
    for key in ['setuptools','wheel']:
        if key not in records:
            d=md.distribution(key)
            records[key]={'name':d.metadata['Name'],'version':d.version,'role':'sdist-build-only',
                          'installed_wheel':d.read_text('WHEEL'),'direct_url':d.read_text('direct_url.json')}
    PAYLOADS=pathlib.Path(tempfile.mkdtemp(prefix='hg-wwheelhouse-payloads-'))
    (HERE/'index').mkdir(exist_ok=True)
    out={'schema':1, 'payload_directory':str(PAYLOADS), 'target_tags':[str(t) for t in TAGS],
         'command':'python3 tests/fixtures/hg_wwheelhouse/obtain.py', 'proxy':PROXY,
         'policy':'Exact installed versions; compatible wheels first, sdist otherwise. No dependency auto-expansion. Payloads retained outside git; receipts are committed.',
         'artifacts':{}}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for key,r in pool.map(obtain, sorted(records.items())):
            out['artifacts'][key]=r
            (HERE/'manifest.json').write_text(json.dumps(out,indent=2)+'\n')
            print(key,r['version'],r['status'],r.get('filename',r.get('reason')),flush=True)
    (HERE/'SHA256SUMS.downloads').write_text(''.join(f"{r['sha256']}  {r['local_path']}\n" for r in out['artifacts'].values() if 'sha256' in r))
