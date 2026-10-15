"""One TB tooling resolver only, inside a fresh network=none base container."""
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import socket
import sys
import sysconfig
import tarfile

from common import digest, save, run, clean_env

out = Path('/out')
prior = Path('/prior')
work = Path('/tmp/resolver')
work.mkdir()
env = clean_env(work)
env['UV_CACHE_DIR'] = str(work / 'compile-cache')
route = Path('/proc/net/route').read_text()
network = {'route': route, 'netns': os.readlink('/proc/self/ns/net'),
           'interfaces': socket.if_nameindex()}
with socket.socket() as s:
    s.settimeout(1)
    try:
        s.connect(('198.51.100.1', 443))
        raise AssertionError('Unexpected external route')
    except OSError as exc:
        network.update(connect_error=str(exc), errno=exc.errno)
save(out / 'network.json', network)
assert network['errno'] == 101 and not route.splitlines()[1:], network
save(out / 'runtime.json', {'sys_version': sys.version, 'executable': sys.executable,
     'executable_sha256': digest(sys.executable), 'SOABI': sysconfig.get_config_var('SOABI')})
inputs = json.loads(Path('/packet/tests/fixtures/hg_wresolver/inputs.json').read_text())
for artifact in inputs['uvx_artifacts']:
    p = prior / Path(artifact['path']).relative_to('tests/fixtures/hg_wuvx/artifacts')
    assert digest(p) == artifact['sha256']
with tarfile.open(prior / 'uv-x86_64-unknown-linux-gnu.tar.gz') as archive:
    archive.extractall(work, filter='data')
members = json.loads((prior / 'uv-members.json').read_text())
for member in members:
    assert digest(work / member['path']) == member['sha256']
save(out / 'uv-binaries.json', [{'path': m['path'], 'sha256': digest(work / m['path'])} for m in members])
uv = work / 'uv-x86_64-unknown-linux-gnu/uv'
uvx = work / 'uv-x86_64-unknown-linux-gnu/uvx'
env['PATH'] = str(uv.parent) + os.pathsep + env['PATH']
run(out, 'uv-version', [uv, '--version'], env=env)
roots = out / 'roots.in'
roots.write_text('pytest==8.4.1\npytest-json-ctrf==0.3.5\n')
result = run(out, 'compile', [uv, 'pip', 'compile', '-vv', '--offline', '--no-index',
    '--find-links', prior / 'wheels', '--no-python-downloads', '--python', sys.executable,
    '--generate-hashes', '--no-header', '--output-file', out / 'resolved.lock', roots], env=env)
assert result['exit_code'] == 0
# Fresh independent cache for the actual uvx resolver/launcher, without a task.
env['UV_CACHE_DIR'] = str(work / 'uvx-cache')
assert not Path(env['UV_CACHE_DIR']).exists()
argv = [uvx, '-vv', '--offline', '--no-index', '--find-links', prior / 'wheels',
        '--no-python-downloads', '-p', sys.executable,
        '-w', 'pytest==8.4.1', '-w', 'pytest-json-ctrf==0.3.5', 'pytest', '--version']
launch = run(out, 'uvx-version', argv, env=env)
assert launch['exit_code'] == 0
cfgs = list(Path(env['UV_CACHE_DIR']).rglob('pyvenv.cfg'))
assert len(cfgs) == 1
python = cfgs[0].parent / 'bin/python'
metadata = run(out, 'selected-distributions', [python, '-c',
    'import importlib.metadata,json; print(json.dumps(sorted((d.metadata["Name"],d.version) '
    'for d in importlib.metadata.distributions())))'], env=env)
assert metadata['exit_code'] == 0
negative = work / 'missing-pluggy'
negative.mkdir()
for p in (prior / 'wheels').glob('*.whl'):
    if not p.name.startswith('pluggy-'):
        shutil.copyfile(p, negative / p.name)
env['UV_CACHE_DIR'] = str(work / 'negative-cache')
negative_argv = [str(negative) if str(a) == str(prior / 'wheels') else a for a in argv]
refusal = run(out, 'negative-missing-pluggy', negative_argv, env=env)
assert refusal['exit_code'] != 0
save(out / 'result.json', {'task': 'openssl-selfsigned-cert', 'compile': result,
     'uvx': launch, 'negative': refusal,
     'scope': 'one fresh tooling resolution and --version; no tests or benchmark scoring'})
