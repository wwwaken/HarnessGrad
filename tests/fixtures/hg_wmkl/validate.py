"""Validate the payload packet and fresh-prefix receipts, then write a SHA-256 manifest."""
import hashlib
import json
import pathlib
import subprocess
import tarfile
import zipfile
import zstandard
from acquire import HERE, save

ROOT=HERE.parents[2]
records=json.loads((HERE/'artifacts.json').read_text())+json.loads((HERE/'support-artifacts.json').read_text())
metadata={}
for r in records:
    p=HERE/'artifacts'/r['fn']
    assert r['verified'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],p
    with zipfile.ZipFile(p) as z:
        info=next(n for n in z.namelist() if n.startswith('info-') and n.endswith('.tar.zst'))
        with z.open(info) as f, zstandard.ZstdDecompressor().stream_reader(f) as stream, tarfile.open(fileobj=stream,mode='r|') as t:
            for member in t:
                if member.name=='info/index.json':
                    d=json.load(t.extractfile(member));break
        assert (d['name'],d['version'],d['build'],d['subdir'])==(r['name'],r['version'],r['build'],'linux-64')
        metadata[r['name']]=d
        if r['name'] in ['mkl','mkl-service']:
            pkg=next(n for n in z.namelist() if n.startswith('pkg-') and n.endswith('.tar.zst'))
            with z.open(pkg) as f, zstandard.ZstdDecompressor().stream_reader(f) as stream, tarfile.open(fileobj=stream,mode='r|') as t:
                files=[m.name for m in t]
            (HERE/(r['name']+'-payload-files.txt')).write_text('\n'.join(files)+'\n')
            if r['name']=='mkl':assert not any('/site-packages/mkl/' in f for f in files)
            else:assert 'lib/python3.12/site-packages/mkl/__init__.py' in files
save(HERE/'conda-package-metadata.json',metadata)
alternative=json.loads((HERE/'alternative-artifact.json').read_text())
assert hashlib.sha256((HERE/'artifacts'/alternative['filename']).read_bytes()).hexdigest()==alternative['digests']['sha256']
for r in json.loads((HERE/'reused-artifacts.json').read_text()).values():
    assert hashlib.sha256(pathlib.Path(r['path']).read_bytes()).hexdigest()==r['sha256'],r['path']
summary=json.loads((HERE/'final-summary.json').read_text())
host=json.loads((HERE/'host-runtime-retry.json').read_text())
for name,r in summary.items():
    assert r['conda_install']['exit_code']==r['pip_install']['exit_code']==0
    assert r['import']['exit_code']==(1 if name=='ds1000' else 0)
    result=json.loads((HERE/'offline'/f'retry-import-{name}.stdout.txt').read_text())
    assert result['mkl_version']==host['mkl_runtime_version']
    assert result['numpy_mkl_version']==host['numpy_mkl_version']
    assert result['imports']['mkl']['ok']
    prefix=pathlib.Path(r['prefix'])
    init=prefix/'lib/python3.12/site-packages/numpy/_distributor_init.py'
    evidence=json.loads((HERE/'profile-evidence.json').read_text())
    assert hashlib.sha256(init.read_bytes()).hexdigest()==evidence['current_host_witness']['sha256']
    assert all(pathlib.Path(p).is_relative_to(prefix) for p in result['native_providers'] if 'libmkl' in p or 'libiomp' in p)
    if name=='ds1000':
        assert {k for k,v in result['imports'].items() if not v['ok']}=={'gensim','tensorflow','xgboost'}
# Record the real ELF dependency chain; no package execution.
prefix=pathlib.Path(summary['livecodebench']['prefix'])
core=next((prefix/'lib/python3.12/site-packages/numpy/core').glob('_multiarray_umath*.so'))
service=next((prefix/'lib/python3.12/site-packages/mkl').glob('_mklinit*.so'))
for label,p in [('numpy-core',core),('mkl-init',service)]:
    cmd=['readelf','-d',str(p)]
    proc=subprocess.run(cmd,capture_output=True,text=True,timeout=20)
    (HERE/f'{label}-readelf.stdout.txt').write_text(proc.stdout)
    (HERE/f'{label}-readelf.stderr.txt').write_text(proc.stderr)
    save(HERE/f'{label}-readelf.receipt.json',{'command':cmd,'exit_code':proc.returncode,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    assert proc.returncode==0 and 'libmkl_rt.so.2' in proc.stdout
for filename in ['network.json','retry-import-network.json']:
    net=json.loads((HERE/'offline'/filename).read_text())
    assert net['errno']==101 and [x[1] for x in net['interfaces']]==['lo']
    assert not net['route'].splitlines()[1:]
empty=['bfcl_v3','bird_minidev','fever','musique','physicsquestions','sportsunderstanding','strategyqa','twowikimultihopqa']
newly_complete=['alfworld','gsm8k','hotpotqa','jericho','livecodebench','reasoning_gym','spreadsheetbench','triviaqa']
coverage={
    'scope':'Recorded scorer-import installation payloads only; not full metadata resolver or runtime/scorer closure.',
    'newly_complete':newly_complete,
    'previously_complete':['chessbench_puzzles','scienceworld'],
    'no_third_party_payload_required':empty,
    'partial':{'ds1000':['Gensim 4.3.2 imports scipy.linalg.triu, absent in SciPy 1.13.1.',
                         'TensorFlow and XGBoost are referenced by recorded contexts but have no installed version to pin; imports remain absent.']},
    'mkl_obtainable':True,
    'native_artifacts':len(records),
    'native_artifact_bytes':sum((HERE/'artifacts'/r['fn']).stat().st_size for r in records),
    'production_authorized':False,
}
save(HERE/'coverage.json',coverage)
# Include all retained raw responses, failed transfers, scripts and receipts. Exclude only this manifest and ignored bytecode.
lines=[]
for p in sorted(HERE.rglob('*')):
    if not p.is_file() or '__pycache__' in p.parts or p.name=='SHA256SUMS':continue
    lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT)}\n")
(HERE/'SHA256SUMS').write_text(''.join(lines))
print(json.dumps(dict(coverage,manifest_entries=len(lines)),indent=2))
