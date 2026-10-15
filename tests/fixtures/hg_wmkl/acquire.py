"""Bounded public-index acquisition. No scoring, adapters, models or endpoints."""
import concurrent.futures
import hashlib
import json
import pathlib
import platform
import subprocess
import sys
from packaging.tags import sys_tags
from packaging.utils import parse_wheel_filename

HERE = pathlib.Path(__file__).resolve().parent
HOST = pathlib.Path(sys.prefix)

def save(path, obj):
    path.write_text(json.dumps(obj, indent=2) + '\n')

def fetch(label, url, dest):
    cmd = ['curl', '--location', '--fail-with-body', '--silent', '--show-error',
           '--connect-timeout', '15', '--max-time', '180', '--dump-header',
           str(HERE/'index'/f'{label}.headers.txt'), '--output', str(dest), url]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=200)
    (HERE/'index'/f'{label}.stdout.txt').write_text(p.stdout)
    (HERE/'index'/f'{label}.stderr.txt').write_text(p.stderr)
    r = {'command': cmd, 'exit_code': p.returncode, 'url': url,
         'bytes': dest.stat().st_size if dest.exists() else None,
         'sha256': hashlib.sha256(dest.read_bytes()).hexdigest() if dest.exists() else None}
    save(HERE/'index'/f'{label}.receipt.json', r)
    return r

if __name__ == '__main__':
    tags = set(sys_tags())
    save(HERE/'target.json', {'python':sys.version, 'executable':sys.executable,
         'platform':platform.platform(), 'tags':[str(t) for t in sys_tags()]})
    queries = [('pypi-mkl-service', 'https://pypi.org/pypi/mkl-service/json'),
               ('pypi-mkl-service-2.4.0', 'https://pypi.org/pypi/mkl-service/2.4.0/json'),
               ('pypi-mkl', 'https://pypi.org/pypi/mkl/json'),
               ('anaconda-mkl-service','https://api.anaconda.org/package/anaconda/mkl-service')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda q:fetch(q[0],q[1],HERE/'index'/f'{q[0]}.json'), queries))
    assert all(r['exit_code']==0 for r in results), results
    summary = {}
    for label, _ in queries:
        d=json.loads((HERE/'index'/f'{label}.json').read_text())
        if label.startswith('pypi'):
            releases=d.get('releases', {d['info']['version']: d.get('urls',[])})
            found=[];sdists=[]
            for version, rows in releases.items():
                for r in rows:
                    if r['filename'].endswith('.whl'):
                        if parse_wheel_filename(r['filename'])[3] & tags:
                            found.append({k:r[k] for k in ['filename','url','digests','size','requires_python','yanked']})
                    elif r['packagetype']=='sdist':sdists.append({k:r[k] for k in ['filename','url','digests','size']})
            summary[label]={'compatible_wheels':found,'sdists':sdists,
                            'version_count':len(releases), 'artifact_count':sum(map(len,releases.values()))}
        else:
            summary[label]={'exact_linux_cp312':[r for r in d['files'] if r['version']=='2.4.0' and r['attrs'].get('subdir')=='linux-64' and 'py312' in r['basename']]}
    save(HERE/'index-summary.json',summary)
    names=['mkl-service','mkl','intel-openmp','tbb','numpy','numpy-base']
    records=[]
    for name in names:
        candidates=[json.loads(p.read_text()) for p in (HOST/'conda-meta').glob(name+'-*.json')]
        d=next(d for d in candidates if d['name']==name)
        records.append({k:d.get(k) for k in ['name','version','build','subdir','channel','url','fn','sha256','md5','depends']})
    save(HERE/'host-conda-records.json',records)
    # Fetch exact published host artifacts, not reconstructed wheels or host cache copies.
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        acquired=list(pool.map(lambda d:fetch('artifact-'+d['name'], d['url'], HERE/'artifacts'/d['fn']),records))
    for d,r in zip(records,acquired):
        d['acquisition']=r
        d['verified']=r['exit_code']==0 and d['sha256']==r['sha256']
    save(HERE/'artifacts.json',records)
    print(json.dumps({'artifacts':[{k:d[k] for k in ['name','version','fn','verified']} for d in records],
          'pypi_service_compatible_count':len(summary['pypi-mkl-service']['compatible_wheels']),
          'exact_conda_candidates':len(summary['anaconda-mkl-service']['exact_linux_cp312'])},indent=2))
    assert all(d['verified'] for d in records)
