"""Obtain declared native support and inspect an alternative PyPI provider wheel."""
import concurrent.futures
import json
import sys
import zipfile
from acquire import HERE, HOST, fetch, save

records=[]
for name in ['libgcc-ng','libstdcxx-ng','libgomp','libffi','zlib','_openmp_mutex','_libgcc_mutex','blas']:
    d=next(d for p in (HOST/'conda-meta').glob(name+'-*.json') if (d:=json.loads(p.read_text()))['name']==name)
    records.append({k:d.get(k) for k in ['name','version','build','subdir','channel','url','fn','sha256','md5','depends']})
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    results=list(pool.map(lambda d:fetch('support-'+d['name'],d['url'],HERE/'artifacts'/d['fn']),records))
for d,r in zip(records,results):
    d['acquisition']=r;d['verified']=r['exit_code']==0 and r['sha256']==d['sha256']
save(HERE/'support-artifacts.json',records)
assert all(d['verified'] for d in records)
summary=json.loads((HERE/'index-summary.json').read_text())
r=summary['pypi-mkl-service']['compatible_wheels'][0]
result=fetch('pypi-alternative-service',r['url'],HERE/'artifacts'/r['filename'])
assert result['exit_code']==0 and result['sha256']==r['digests']['sha256']
with zipfile.ZipFile(HERE/'artifacts'/r['filename']) as z:
    files=z.namelist()
    (HERE/'alternative-service-contents.txt').write_text('\n'.join(files)+'\n')
    meta=z.read(next(n for n in files if n.endswith('.dist-info/METADATA'))).decode()
    (HERE/'alternative-service-METADATA.txt').write_text(meta)
save(HERE/'alternative-artifact.json',dict(r, acquisition=result, purpose='Inspected alternative; exact host version is obtained from Conda instead.'))
print(json.dumps({'support':[{k:d[k] for k in ['name','fn','verified']} for d in records], 'alternative':r['filename']},indent=2))
