"""Run real pip metadata checks with networking denied by a fresh kernel namespace."""
import json
import os
from pathlib import Path
import shutil
import socket
import sys
import tempfile
import venv
from common import HERE, digest, run, save, clean_env

assert not (HERE/'results.json').exists(), 'Never overwrite an offline capture'
inputs=json.loads((HERE/'inputs.json').read_text())
work=Path(tempfile.mkdtemp(prefix='hg-wresolver5-tb-offline-'))
env=clean_env(work)
network={'netns':os.readlink('/proc/self/ns/net'),'interfaces':socket.if_nameindex(),'route':Path('/proc/net/route').read_text()}
with socket.socket() as connection:
    connection.settimeout(1)
    try:connection.connect(('198.51.100.1',443));raise AssertionError('Unexpected external route')
    except OSError as exc:network.update(errno=exc.errno,error=str(exc))
save(HERE/'raw/network.json',network)
assert network['errno']==101 and network['interfaces']==[(1,'lo')] and not network['route'].splitlines()[1:]
save(HERE/'raw/runtime.json',{'version':sys.version,'executable':sys.executable,'sha256':digest(sys.executable),
    'work_directory':str(work),'environment':{k:env[k] for k in ['HOME','XDG_CACHE_HOME','PIP_CONFIG_FILE','CUDA_VISIBLE_DEVICES']}})
results={}
try:
    for name,keys in inputs['profiles'].items():
        profile=HERE/'profiles'/name
        directory=work/name
        venv.EnvBuilder(with_pip=True,system_site_packages=False,symlinks=True).create(directory)
        python=directory/'bin/python'
        (HERE/'raw'/(name+'-pyvenv.cfg')).write_text((directory/'pyvenv.cfg').read_text())
        run(name+'-pip-version',[python,'-m','pip','--version'],env=env)
        # Each profile has its own exact candidate set, with no alternate or foreign version.
        candidates=work/('wheels-'+name);candidates.mkdir()
        for a in inputs['artifacts']:
            if a['key']+'=='+a['version'] in keys:
                (candidates/a['filename']).symlink_to(a['path'])
        base=[python,'-m','pip','--isolated','--disable-pip-version-check','install','--ignore-installed','--no-index','--no-cache-dir','--only-binary=:all:']
        result=run('resolve-'+name,base+['--dry-run','--find-links',candidates,'--report',HERE/'raw'/(name+'.pip-report.json'),
            '-r',profile/'roots.in','-c',profile/'constraints.txt'],env=env)
        assert result['exit_code']==0
        report=json.loads((HERE/'raw'/(name+'.pip-report.json')).read_text())
        selected=[{'name':x['metadata']['name'],'version':x['metadata']['version'],'sha256':x['download_info']['archive_info']['hashes']['sha256']} for x in report['install']]
        (profile/'resolved.lock').write_text(''.join(f"{x['name']}=={x['version']} --hash=sha256:{x['sha256']}\n" for x in selected))
        result['selected']=selected
        result['install']=run('install-'+name,base+['--find-links',candidates,'--require-hashes','-r',profile/'resolved.lock'],env=env)
        result['check']=run('check-'+name,[python,'-m','pip','check'],env=env)
        assert result['install']['exit_code']==result['check']['exit_code']==0
        # pytest's mandatory pluggy dependency is absent; installed pluggy must not mask it.
        absent=next(a for a in inputs['artifacts'] if a['key']=='pluggy' and a['key']+'=='+a['version'] in keys)
        removed=candidates/absent['filename'];removed.unlink()
        result['negative_removed']={'name':absent['key'],'version':absent['version'],'filename':absent['filename'],'remaining_files':sorted(p.name for p in candidates.iterdir())}
        result['negative']=run('negative-'+name,base+['--dry-run','--find-links',candidates,'-r',profile/'roots.in','-c',profile/'constraints.txt'],env=env)
        assert result['negative']['exit_code']!=0
        results[name]=result
        save(HERE/'results.json',results)
finally:
    shutil.rmtree(work)
    save(HERE/'raw/cleanup.json',{'directory':str(work),'removed':not work.exists()})
print(json.dumps({n:{'resolve':r['exit_code'],'install':r['install']['exit_code'],'check':r['check']['exit_code'],
    'selected':len(r['selected']),'removed':r['negative_removed'],'negative':r['negative']['exit_code']} for n,r in results.items()},indent=2))
