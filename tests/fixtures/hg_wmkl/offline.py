"""Fresh-prefix offline installation and imports; never run scoring/task operations."""
import hashlib
import json
import os
import pathlib
import shlex
import socket
import subprocess
import sys
import tempfile
import time
import venv
from acquire import HERE, save

LOGS=HERE/'offline'
OLD=HERE.parent/'hg_wwheelhouse'
work=pathlib.Path(tempfile.mkdtemp(prefix='hg-wmkl-offline-'))
ENV=dict(os.environ, CUDA_VISIBLE_DEVICES='', PIP_NO_INDEX='1', PIP_DISABLE_PIP_VERSION_CHECK='1',
         PYTHONDONTWRITEBYTECODE='1', MPLBACKEND='Agg', CONDA_NO_PLUGINS='true',
         CONDA_SOLVER='classic', CONDA_OFFLINE='true', CONDA_PKGS_DIRS=str(work/'pkgs'),
         CONDA_ENVS_PATH=str(work/'envs'), XDG_CACHE_HOME=str(work/'cache'),
         OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
for key in ['HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy',
            'PYTHONPATH','PYTHONHOME','LD_LIBRARY_PATH','LD_PRELOAD']:
    ENV.pop(key,None)

def run(label, cmd, timeout=180):
    print('+',shlex.join(cmd),flush=True)
    start=time.monotonic()
    try:
        p=subprocess.run(cmd,env=ENV,capture_output=True,text=True,timeout=timeout)
        code=p.returncode;out=p.stdout;err=p.stderr
    except subprocess.TimeoutExpired as e:
        code=124;out=e.stdout or b'';err=e.stderr or b''
        if isinstance(out,bytes):out=out.decode(errors='replace')
        if isinstance(err,bytes):err=err.decode(errors='replace')
        err+='\nBounded command timed out.\n'
    (LOGS/f'{label}.stdout.txt').write_text(out)
    (LOGS/f'{label}.stderr.txt').write_text(err)
    r={'command':cmd,'exit_code':code,'elapsed_seconds':round(time.monotonic()-start,3)}
    save(LOGS/f'{label}.receipt.json',r)
    print(label,code,flush=True)
    return r

net={'command':sys.orig_argv,'netns':os.readlink('/proc/self/ns/net'),
     'route':pathlib.Path('/proc/net/route').read_text(),'interfaces':socket.if_nameindex()}
try:
    with socket.socket() as s:
        s.settimeout(1);s.connect(('198.51.100.1',443))
    raise AssertionError('External connection succeeded')
except OSError as e:
    net.update(error=repr(e),errno=e.errno)
    assert e.errno==101,net
assert not net['route'].splitlines()[1:],net
assert [n for _,n in net['interfaces']]==['lo'],net
save(LOGS/'network.json',net)
save(HERE/'work.json',{'directory':str(work),'system_site_packages':False,
                      'base_python':sys.executable,'note':'Base Python/stdlib/OS ABI remain prerequisites.'})
records=json.loads((HERE/'artifacts.json').read_text())+json.loads((HERE/'support-artifacts.json').read_text())
paths=[HERE/'artifacts'/d['fn'] for d in records]
for d,p in zip(records,paths):
    assert d['verified'] and hashlib.sha256(p.read_bytes()).hexdigest()==d['sha256'],p
# A fresh venv must not see the host's mkl module before payload installation.
venv.EnvBuilder(with_pip=True,system_site_packages=False).create(work/'negative')
negative=run('negative-import-mkl',[str(work/'negative/bin/python'),'-I','-c','import mkl'])
assert negative['exit_code']==1
assert "No module named 'mkl'" in (LOGS/'negative-import-mkl.stderr.txt').read_text()

manifest=json.loads((OLD/'manifest.json').read_text())
artifacts={k:r for k,r in manifest['artifacts'].items() if r['status']=='obtained-wheel'}
artifacts.update({k:r for k,r in json.loads((OLD/'built-artifacts.json').read_text()).items() if r['status']=='built-offline'})
scope=json.loads((OLD/'source-scope.json').read_text())['datasets']
groups={
    'livecodebench':(['numpy'],['numpy']),
    'qa-parquet-startup':(['pyarrow','numpy','cloudpickle','typing-extensions'],['pyarrow.parquet']),
    'jericho':(['jericho','numpy'],['jericho']),
}
for name,mods in [('alfworld',['textworld.gym','alfworld.agents.environment.alfred_tw_env']),
                  ('reasoning_gym',['reasoning_gym']),('spreadsheetbench',['openpyxl']),
                  ('ds1000',['numpy','pandas','scipy','sklearn','matplotlib.pyplot','seaborn','torch','gensim','tensorflow','xgboost'])]:
    keys=[s.lower().replace('_','-') for s in scope[name]['imported_distributions']]
    if name=='ds1000':
        keys+=sorted(k for k,r in manifest['artifacts'].items() if r['role']=='torch-import-time-native-provider')
    groups[name]=(keys,mods)

probe='''import importlib,json,pathlib,sys
mods=MODS
results={}
for name in ['mkl']+mods:
 try:
  m=importlib.import_module(name)
  results[name]={'ok':True,'version':getattr(m,'__version__',None),'path':getattr(m,'__file__',None)}
 except Exception as e:results[name]={'ok':False,'error':repr(e)}
import mkl,numpy
prefix=pathlib.Path(sys.prefix)
assert pathlib.Path(mkl.__file__).is_relative_to(prefix)
assert pathlib.Path(numpy.__file__).is_relative_to(prefix)
assert mkl.__version__=='2.4.0' and numpy.__version__=='1.26.4'
assert numpy._distributor_init.__mkl_version__=='2023.0.1'
maps=pathlib.Path('/proc/self/maps').read_text().splitlines()
providers=sorted(set(line.split()[-1] for line in maps if any(x in line for x in ['libmkl','libiomp','libtbb','libstdc++','libgcc_s'])))
assert any('libmkl' in x for x in providers)
assert all(pathlib.Path(x).is_relative_to(prefix) for x in providers if any(k in x for k in ['libmkl','libiomp','libtbb']))
assert not any(str(pathlib.Path(sys.base_prefix)/'lib/python3.12/site-packages') in line for line in maps)
print(json.dumps({'imports':results,'mkl_version':mkl.get_version(),'numpy_mkl_version':numpy._distributor_init.__mkl_version__,
 'native_providers':providers,'prefix':sys.prefix,'base_prefix':sys.base_prefix,'sys_path':sys.path},indent=2,default=lambda b:b.decode() if isinstance(b,bytes) else repr(b)))
raise SystemExit(any(not r['ok'] for r in results.values()))
'''
results={}
used={}
for name,(keys,mods) in groups.items():
    prefix=work/name
    r=run('conda-'+name,[str(pathlib.Path(sys.prefix)/'bin/conda'),'create','--offline','--yes','--no-deps',
          '--solver','classic','--no-default-packages','--prefix',str(prefix)]+[str(p) for p in paths],timeout=180)
    assert r['exit_code']==0,r
    venv.EnvBuilder(with_pip=True,system_site_packages=False).create(prefix)
    python=str(prefix/'bin/python')
    # The exact published Conda NumPy package replaces the public OpenBLAS wheel.
    selected={k:artifacts[k] for k in keys if k not in ['numpy','mkl-service']}
    lp=HERE/(name+'.lock')
    lines=[]
    for k,d in sorted(selected.items()):
        p=pathlib.Path(d['local_path'])
        assert hashlib.sha256(p.read_bytes()).hexdigest()==d['sha256'],p
        used[k]={'filename':p.name,'path':str(p),'sha256':d['sha256'],'bytes':p.stat().st_size}
        lines.append(f"{d['name']}=={d['version']} --hash=sha256:{d['sha256']}\n")
    lp.write_text(''.join(lines))
    install=run('pip-'+name,[python,'-m','pip','install','--no-index','--no-cache-dir','--no-deps','--require-hashes',
             '--find-links',manifest['payload_directory'],'-r',str(lp)],timeout=300)
    assert install['exit_code']==0
    check=run('import-'+name,[python,'-I','-c',probe.replace('MODS',repr(mods))],timeout=180)
    listing=run('list-'+name,[python,'-m','pip','list','--format=json'])
    results[name]={'conda_install':r,'pip_install':install,'import':check,
                   'status':'complete-import-payload' if check['exit_code']==0 else 'partial-import-payload',
                   'prefix':str(prefix)}
    save(HERE/'offline-summary.json',results)
    save(HERE/'reused-artifacts.json',used)
print(json.dumps(results,indent=2))
