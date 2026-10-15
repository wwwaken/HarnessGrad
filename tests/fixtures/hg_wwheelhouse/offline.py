"""Network-namespace install/build receipt; no task, world, scorer or model calls."""
import hashlib
import json
import os
import pathlib
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import venv
import zipfile

HERE = pathlib.Path(__file__).resolve().parent
M = json.loads((HERE/'manifest.json').read_text())
PAYLOADS = pathlib.Path(M['payload_directory'])
LOGS = HERE/'offline'
LOGS.mkdir(exist_ok=True)
ENV = dict(os.environ, CUDA_VISIBLE_DEVICES='', PIP_NO_INDEX='1', PIP_DISABLE_PIP_VERSION_CHECK='1',
           PYTHONDONTWRITEBYTECODE='1', MPLBACKEND='Agg', SOURCE_DATE_EPOCH='0')
for key in ['HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy']:
    ENV.pop(key, None)

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while b:=f.read(4*1024*1024):h.update(b)
    return h.hexdigest()

def run(label,cmd,timeout=180):
    start=time.monotonic()
    print('+',__import__('shlex').join(cmd),flush=True)
    try:
        p=subprocess.run(cmd,env=ENV,capture_output=True,text=True,timeout=timeout)
        code=p.returncode;stdout=p.stdout;stderr=p.stderr
    except subprocess.TimeoutExpired as exc:
        code=124;stdout=(exc.stdout or b'').decode() if isinstance(exc.stdout,bytes) else (exc.stdout or '')
        stderr=(exc.stderr or b'').decode() if isinstance(exc.stderr,bytes) else (exc.stderr or '')
        stderr+='\nBounded installation/build timed out.\n'
    (LOGS/f'{label}.stdout.txt').write_text(stdout)
    (LOGS/f'{label}.stderr.txt').write_text(stderr)
    r={'command':cmd,'exit_code':code,'elapsed_seconds':round(time.monotonic()-start,3)}
    (LOGS/f'{label}.receipt.json').write_text(json.dumps(r,indent=2)+'\n')
    print(label,'exit_code',code,flush=True)
    return r

def lock(path,keys,artifacts):
    lines=[]
    for k in sorted(keys):
        r=artifacts[k]
        lines.append(f"{r['name']}=={r['version']} --hash=sha256:{r['sha256']}\n")
    path.write_text(''.join(lines))

if __name__=='__main__':
    assert len(sys.argv)==2 and sys.argv[1] in ['build','build-retry','install']
    net={'netns':os.readlink('/proc/self/ns/net'), 'route':pathlib.Path('/proc/net/route').read_text(),
         'interfaces':socket.if_nameindex(), 'command':__import__('shlex').join(sys.orig_argv)}
    try:
        with socket.socket() as s:
            s.settimeout(1);s.connect(('198.51.100.1',443))
        raise AssertionError('External connection unexpectedly succeeded')
    except OSError as exc:
        net['external_connect_error']=repr(exc);net['errno']=exc.errno
        assert exc.errno==101,net
    assert not any('00000000\t' in line for line in net['route'].splitlines()[1:]),net
    (LOGS/f'{sys.argv[1]}-network.json').write_text(json.dumps(net,indent=2)+'\n')
    print(json.dumps(net),flush=True)
    work=pathlib.Path(tempfile.mkdtemp(prefix=f'hg-wwheelhouse-{sys.argv[1]}-'))
    venv.EnvBuilder(with_pip=True,system_site_packages=False).create(work/'venv')
    python=str(work/'venv/bin/python')
    ENV['PATH']=str(work/'venv/bin')+os.pathsep+ENV['PATH']
    if sys.argv[1] in ['build','build-retry']:
        retry=sys.argv[1]=='build-retry'
        prefix='retry-' if retry else ''
        keys=['setuptools','wheel','numpy','packaging']
        if retry: keys+=['cmake','cppy','setuptools-scm','pkgconfig']
        tool_lock=HERE/(prefix+'build-tools.lock')
        lock(tool_lock,keys,M['artifacts'])
        r=run(prefix+'build-bootstrap',[python,'-m','pip','install','--no-index','--no-cache-dir','--no-deps','--require-hashes',
            '--find-links',str(PAYLOADS),'-r',str(tool_lock)])
        assert r['exit_code']==0
        built=json.loads((HERE/'built-artifacts.json').read_text()) if retry else {}
        for k,r in M['artifacts'].items():
            if r.get('kind')!='sdist':continue
            if retry and built[k]['status']=='built-offline':continue
            out=work/k;out.mkdir()
            result=run(prefix+'build-'+k,[python,'-m','pip','wheel','--no-index','--no-cache-dir','--no-deps',
                '--no-build-isolation','--find-links',str(PAYLOADS),'--wheel-dir',str(out),r['local_path']],timeout=300)
            result.update(source_sha256=r['sha256'],source_url=r['url'])
            wheels=list(out.glob('*.whl'))
            if result['exit_code']==0 and len(wheels)==1:
                p=wheels[0]
                with zipfile.ZipFile(p) as z:
                    meta=z.read(next(n for n in z.namelist() if n.endswith('.dist-info/METADATA'))).decode()
                    wheel=z.read(next(n for n in z.namelist() if n.endswith('.dist-info/WHEEL'))).decode()
                version=next(l[9:] for l in meta.splitlines() if l.startswith('Version: '))
                if version!=r['version']:
                    result.update(status='built-version-mismatch',actual_version=version)
                else:
                    dest=PAYLOADS/p.name;shutil.copyfile(p,dest)
                    result.update(status='built-offline',name=r['name'],version=version,filename=p.name,
                        local_path=str(dest),sha256=sha(dest),bytes=dest.stat().st_size,wheel_metadata=wheel,
                        artifact_tags=[l[5:] for l in wheel.splitlines() if l.startswith('Tag: ')])
            else:result['status']='offline-build-failed'
            if retry: result['prior_attempt']=built[k]
            built[k]=result
            (HERE/'built-artifacts.json').write_text(json.dumps(built,indent=2)+'\n')
    else:
        artifacts={k:r for k,r in M['artifacts'].items() if r['status']=='obtained-wheel'}
        artifacts.update({k:r for k,r in json.loads((HERE/'built-artifacts.json').read_text()).items() if r['status']=='built-offline'})
        # These profiles contain only packages imported by the corresponding scorer.
        groups={
            'chessbench_puzzles':(['chess'],['chess']),
            'scienceworld':(['scienceworld','py4j'],['scienceworld']),
            'livecodebench-public-numpy':(['numpy'],['numpy']),
            'qa-parquet-public-wheels':(['pyarrow','numpy','cloudpickle','typing-extensions'],['pyarrow.parquet']),
            'jericho-public-wheels':(['jericho','numpy'],['jericho']),
        }
        scope=json.loads((HERE/'source-scope.json').read_text())['datasets']
        def normalized(s):return s.lower().replace('_','-')
        for name,mods in [
            ('alfworld',['textworld.gym','alfworld.agents.environment.alfred_tw_env']),
            ('reasoning_gym',['reasoning_gym']),('spreadsheetbench',['openpyxl']),
            ('ds1000',['numpy','pandas','scipy','sklearn','matplotlib.pyplot','seaborn','torch','gensim'])]:
            keys=[normalized(s) for s in scope[name]['imported_distributions'] if normalized(s)!='mkl-service']
            groups[name+'-partial-public-wheels']=(keys,mods)
        all_results={}
        for name,(keys,mods) in groups.items():
            venv.EnvBuilder(with_pip=True,system_site_packages=False).create(work/name)
            python=str(work/name/'bin/python')
            ENV['PATH']=str(work/name/'bin')+os.pathsep+os.environ['PATH']
            lp=HERE/f'{name}.lock'
            if any(k not in artifacts for k in keys):
                all_results[name]={'status':'missing-build','missing':[k for k in keys if k not in artifacts]};continue
            lock(lp,keys,artifacts)
            r=run('install-'+name,[python,'-m','pip','install','--no-index','--no-cache-dir','--no-deps',
                '--require-hashes','--find-links',str(PAYLOADS),'-r',str(lp)])
            # Import only: no adapters, datasets, game objects, score functions or JVM launches.
            probe=run('import-'+name,[python,'-c','import importlib, json; '
                f'mods={mods!r}; [importlib.import_module(x) for x in mods]; '
                'print(json.dumps({"imports":mods,"ok":True}))'])
            all_results[name]={'install':r,'import':probe,'status':'installed-and-imported' if r['exit_code']==probe['exit_code']==0 else 'failed'}
        run('final-list',[python,'-m','pip','list','--format=json'])
        (HERE/'install-summary.json').write_text(json.dumps(all_results,indent=2)+'\n')
    print('work_directory',work,flush=True)
