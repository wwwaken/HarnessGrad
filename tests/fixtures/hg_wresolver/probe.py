"""Run in unshare -Urn. Resolve declared dependencies; never use --no-deps."""
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import socket
import sys
import sysconfig
import tempfile
import venv

from common import HERE, digest, save, run, clean_env

assert not (HERE / 'native-results.json').exists(), 'Never overwrite a prior capture'
inputs = json.loads((HERE / 'inputs.json').read_text())
work = Path(tempfile.mkdtemp(prefix='hg-wresolver-native-'))
env = clean_env(work)
route = Path('/proc/net/route').read_text()
network = {'netns': os.readlink('/proc/self/ns/net'), 'route': route,
           'interfaces': socket.if_nameindex()}
with socket.socket() as s:
    s.settimeout(1)
    try:
        s.connect(('198.51.100.1', 443))
        raise AssertionError('Unexpected external route')
    except OSError as exc:
        network.update(connect_error=str(exc), errno=exc.errno)
save(HERE / 'raw/native-network.json', network)
assert network['errno'] == 101 and not route.splitlines()[1:], network
venv.EnvBuilder(with_pip=True, system_site_packages=False).create(work / 'venv')
python = work / 'venv/bin/python'
save(HERE / 'raw/native-runtime.json', {'sys_version': sys.version, 'executable': sys.executable,
     'executable_sha256': digest(sys.executable), 'SOABI': sysconfig.get_config_var('SOABI'),
     'pyvenv_cfg': (work / 'venv/pyvenv.cfg').read_text(), 'work_directory': str(work)})
run(HERE / 'raw', 'pip-version', [python, '-m', 'pip', '--version'], env=env)
base = [python, '-m', 'pip', '--isolated', '--disable-pip-version-check', 'install',
        '--no-index', '--no-cache-dir', '--only-binary=:all:', '--ignore-installed']
artifacts = {r['key']: r for r in inputs['artifacts']}
results = {}
for name, profile in inputs['profiles'].items():
    directory = HERE / 'profiles' / name
    result = run(HERE / 'raw', 'resolve-' + name, base + ['--dry-run', '-vv',
        '--find-links', inputs['wheel_directory'], '--report', HERE / 'raw' / (name + '.pip-report.json'),
        '-r', directory / 'roots.in', '-c', directory / 'constraints.txt'], env=env)
    if result['exit_code'] == 0:
        report = json.loads((HERE / 'raw' / (name + '.pip-report.json')).read_text())
        selected = []
        for entry in report['install']:
            selected.append({'name': entry['metadata']['name'], 'version': entry['metadata']['version'],
                             'sha256': entry['download_info']['archive_info']['hashes']['sha256']})
        (directory / 'resolved.lock').write_text(''.join(
            f"{r['name']}=={r['version']} --hash=sha256:{r['sha256']}\n" for r in selected))
        install = run(HERE / 'raw', 'install-' + name, base + ['--find-links', inputs['wheel_directory'],
            '--require-hashes', '-r', directory / 'resolved.lock'], env=env)
        check = run(HERE / 'raw', 'check-' + name, [python, '-m', 'pip', 'check'], env=env)
        assert install['exit_code'] == check['exit_code'] == 0
        result.update(selected=selected, install=install, pip_check=check)
    results[name] = result
# Real negative control: even an already installed py4j must not satisfy an
# ignore-installed reconstruction with its wheel removed.
negative = work / 'missing-py4j'
negative.mkdir()
science = artifacts['scienceworld']
shutil.copyfile(science['path'], negative / Path(science['path']).name)
results['negative-missing-py4j'] = run(HERE / 'raw', 'negative-missing-py4j', base +
    ['--dry-run', '--find-links', negative, '-r', HERE / 'profiles/scienceworld/roots.in'], env=env)
assert results['negative-missing-py4j']['exit_code'] != 0
save(HERE / 'native-results.json', results)
shutil.rmtree(work)
save(HERE / 'raw/native-cleanup.json', {'directory': str(work), 'removed': not work.exists()})
print(json.dumps({k: v['exit_code'] for k, v in results.items()}))
