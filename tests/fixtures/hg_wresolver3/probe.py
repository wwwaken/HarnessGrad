"""Dependency-aware wheel resolution in a kernel-denied network namespace."""
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

assert not (HERE / 'results.json').exists(), 'Never overwrite a capture'
inputs = json.loads((HERE / 'inputs.json').read_text())
assert inputs['graph_satisfied'], 'Conflicting exact candidates require investigation'
work = Path(tempfile.mkdtemp(prefix='hg-wresolver3-offline-'))
env = clean_env(work)
route = Path('/proc/net/route').read_text()
network = {'netns': os.readlink('/proc/self/ns/net'), 'route': route,
           'interfaces': socket.if_nameindex()}
with socket.socket() as connection:
    connection.settimeout(1)
    try:
        connection.connect(('198.51.100.1', 443))
        raise AssertionError('Unexpected external route')
    except OSError as exc:
        network.update(errno=exc.errno, error=str(exc))
save(HERE / 'raw/network.json', network)
assert network['errno'] == 101 and not route.splitlines()[1:]
assert network['interfaces'] == [(1, 'lo')]
save(HERE / 'raw/runtime.json', {'sys_version': sys.version,
     'executable': sys.executable, 'executable_sha256': digest(sys.executable),
     'SOABI': sysconfig.get_config_var('SOABI'), 'work_directory': str(work),
     'environment': {k: v for k, v in env.items() if k in ['HOME', 'XDG_CACHE_HOME', 'PIP_CONFIG_FILE', 'CUDA_VISIBLE_DEVICES']}})
results = {}
try:
    for name, missing in [('alfworld', 'fast-downward-textworld'), ('gsm8k', 'pyarrow'),
                          ('hotpotqa', 'pyarrow'), ('triviaqa', 'pyarrow'), ('livecodebench', 'numpy')]:
        profile = HERE / 'profiles' / name
        directory = work / name
        venv.EnvBuilder(with_pip=True, system_site_packages=False).create(directory)
        python = directory / 'bin/python'
        (HERE / 'raw' / (name + '-pyvenv.cfg')).write_text((directory / 'pyvenv.cfg').read_text())
        run(name + '-pip-version', [python, '-m', 'pip', '--version'], env=env)
        base = [python, '-m', 'pip', '--isolated', '--disable-pip-version-check', 'install',
                '--ignore-installed', '--no-index', '--no-cache-dir', '--only-binary=:all:']
        result = run('resolve-' + name, base + ['--dry-run', '-vv', '--find-links', inputs['wheel_directory'],
                     '--report', HERE / 'raw' / (name + '.pip-report.json'),
                     '-r', profile / 'roots.in', '-c', profile / 'constraints.txt'], env=env)
        if result['exit_code'] == 0:
            report = json.loads((HERE / 'raw' / (name + '.pip-report.json')).read_text())
            selected = [{'name': e['metadata']['name'], 'version': e['metadata']['version'],
                         'sha256': e['download_info']['archive_info']['hashes']['sha256']}
                        for e in report['install']]
            (profile / 'resolved.lock').write_text(''.join(
                f"{e['name']}=={e['version']} --hash=sha256:{e['sha256']}\n" for e in selected))
            result.update(selected=selected)
            result['install'] = run('install-' + name, base + ['--find-links', inputs['wheel_directory'],
                '--require-hashes', '-r', profile / 'resolved.lock'], env=env)
            result['check'] = run('check-' + name, [python, '-m', 'pip', 'check'], env=env)
            assert result['install']['exit_code'] == result['check']['exit_code'] == 0
        # Missing original dependency must still refuse even after installation.
        negative = work / ('missing-' + missing)
        negative.mkdir()
        for artifact in inputs['artifacts']:
            if artifact['key'] != missing:
                source = Path(artifact['path'])
                (negative / source.name).symlink_to(source)
        result['negative'] = run('negative-' + name, base + ['--dry-run', '--find-links', negative,
            '-r', profile / 'roots.in', '-c', profile / 'constraints.txt'], env=env)
        assert result['negative']['exit_code'] != 0
        results[name] = result
        save(HERE / 'results.json', results)
finally:
    shutil.rmtree(work)
    save(HERE / 'raw/cleanup.json', {'directory': str(work), 'removed': not work.exists()})
print(json.dumps({name: {'resolve': r['exit_code'], 'negative': r['negative']['exit_code'],
                        'selected': len(r.get('selected', []))} for name, r in results.items()}, sort_keys=True))
