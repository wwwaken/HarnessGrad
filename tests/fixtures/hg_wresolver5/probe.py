"""Execute with /usr/bin/python3.10 under unshare -Urn; no task imports."""
import json
import os
from pathlib import Path
import shutil
import socket
import sys
import sysconfig
import tempfile
import venv
import zipfile
from common import HERE, clean_env, digest, run, save

assert not (HERE/'result.json').exists()
assert sys.version_info[:2] == (3,10)
inputs = json.loads((HERE/'artifacts.json').read_text())
tool = json.loads((HERE/'tool.json').read_text())['artifact']
work = Path(tempfile.mkdtemp(prefix='hg-wresolver5-offline-'))
env = clean_env(work)
network = dict(namespace=os.readlink('/proc/self/ns/net'),route=Path('/proc/net/route').read_text(),
               interfaces=socket.if_nameindex())
with socket.socket() as connection:
    connection.settimeout(1)
    try:
        connection.connect(('198.51.100.1',443))
        raise AssertionError('Unexpected external route')
    except OSError as exc:
        network.update(errno=exc.errno,error=str(exc))
save(HERE/'raw/network.json',network)
assert network['errno']==101 and not network['route'].splitlines()[1:]
assert network['interfaces']==[(1,'lo')]
save(HERE/'raw/runtime.json',dict(version=sys.version,executable=sys.executable,
     executable_sha256=digest(sys.executable),SOABI=sysconfig.get_config_var('SOABI'),work_directory=str(work),
     environment={k:v for k,v in env.items() if k in ['HOME','XDG_CACHE_HOME','PIP_CONFIG_FILE','CUDA_VISIBLE_DEVICES']}))
try:
    directory = work/'venv'
    venv.EnvBuilder(with_pip=False,system_site_packages=False,symlinks=True).create(directory)
    python = directory/'bin/python'
    # Debian's stdlib venv has no ensurepip here. Seed the exact pure-Python pip
    # tooling wheel locally, verify its hash, and keep it outside the dataset graph.
    pip_path = Path(json.loads((HERE/'tool.json').read_text())['outside_directory'])/tool['filename']
    assert digest(pip_path)==tool['sha256']
    purelib = directory/'lib/python3.10/site-packages'
    with zipfile.ZipFile(pip_path) as wheel:
        assert all(not n.startswith('/') and '..' not in Path(n).parts for n in wheel.namelist())
        wheel.extractall(purelib)
    (HERE/'raw/pyvenv.cfg').write_text((directory/'pyvenv.cfg').read_text())
    assert run('pip-version',[python,'-m','pip','--version'],env=env)['exit_code']==0
    base = [python,'-m','pip','--isolated','--disable-pip-version-check','install','--ignore-installed',
            '--no-index','--no-cache-dir','--only-binary=:all:','--progress-bar','off']
    result = run('resolve',base+['--dry-run','--find-links',inputs['directory'],
                 '--report',work/'pip-report.json','-r',HERE/'profile/roots.in','-c',HERE/'profile/constraints.txt'],env=env)
    if result['exit_code']==0:
        report = json.loads((work/'pip-report.json').read_text())
        # Full pip report descriptions are bulk metadata: preserve only the graph
        # fields needed to independently audit pip's actual decision.
        selected = [dict(name=e['metadata']['name'],version=e['metadata']['version'],
                        url=e['download_info']['url'],sha256=e['download_info']['archive_info']['hashes']['sha256'],
                        requested=e['requested'],requires_dist=e['metadata'].get('requires_dist',[]),
                        requires_python=e['metadata'].get('requires_python')) for e in report['install']]
        save(HERE/'selection.json',dict(environment=report['environment'],selected=selected,
              full_report=dict(outside_path=str(work/'pip-report.json'),sha256=digest(work/'pip-report.json'),bytes=(work/'pip-report.json').stat().st_size),
              note='Full temporary pip report is removed with probe workdir; graph-only fields retained, no report body committed.'))
        (HERE/'profile/resolved.lock').write_text(''.join(
            f"{e['name']}=={e['version']} --hash=sha256:{e['sha256']}\n" for e in selected))
        result['install'] = run('install',base+['--find-links',inputs['directory'],'--require-hashes','-r',HERE/'profile/resolved.lock'],env=env,timeout=600)
        result['check'] = run('check',[python,'-m','pip','check'],env=env)
        assert result['install']['exit_code']==result['check']['exit_code']==0
        negative = work/'missing-flatbuffers'
        negative.mkdir()
        omitted = []
        for artifact in inputs['artifacts']:
            path = Path(inputs['directory'])/artifact['filename']
            if artifact['name'].lower()=='flatbuffers':
                omitted.append(dict(name=artifact['name'],version=artifact['version'],filename=artifact['filename']))
            else:
                (negative/path.name).symlink_to(path)
        assert len(omitted)==1
        save(HERE/'raw/negative-inventory.json',dict(omitted=omitted,retained_candidates=len(list(negative.iterdir()))))
        result['negative'] = run('negative',base+['--dry-run','--find-links',negative,'-r',HERE/'profile/roots.in','-c',HERE/'profile/constraints.txt'],env=env)
        assert result['negative']['exit_code']!=0
    save(HERE/'result.json',result)
    print(json.dumps(result,sort_keys=True))
finally:
    shutil.rmtree(work)
    save(HERE/'raw/cleanup.json',dict(directory=str(work),removed=not work.exists()))
