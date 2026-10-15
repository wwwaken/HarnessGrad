"""Corroborate failures against the entire inherited wheel directory, still offline."""
import json
import os
from pathlib import Path
import shutil
import socket
import tempfile
import venv

from common import HERE, ROOT, digest, save, run, clean_env

assert not (HERE / 'supplement-results.json').exists()
work = Path(tempfile.mkdtemp(prefix='hg-wresolver-supplement-'))
env = clean_env(work)
route = Path('/proc/net/route').read_text()
network = {'netns': os.readlink('/proc/self/ns/net'), 'route': route, 'interfaces': socket.if_nameindex()}
with socket.socket() as s:
    try:
        s.connect(('198.51.100.1', 443))
        raise AssertionError('Unexpected external route')
    except OSError as exc:
        network.update(errno=exc.errno, error=str(exc))
save(HERE / 'raw/supplement-network.json', network)
assert network['errno'] == 101 and not route.splitlines()[1:]
venv.EnvBuilder(with_pip=True, system_site_packages=False).create(work / 'venv')
python = work / 'venv/bin/python'
manifest = json.loads((ROOT / 'tests/fixtures/hg_wwheelhouse/manifest.json').read_text())
corpus = Path(manifest['payload_directory'])
save(HERE / 'supplement-corpus.json', {'directory': str(corpus),
     'filenames': sorted(p.name for p in corpus.iterdir() if p.is_file()),
     'extra_available': [{'name': k, 'path': manifest['artifacts'][k]['local_path'],
                          'sha256': digest(manifest['artifacts'][k]['local_path'])}
                         for k in ['termcolor', 'pygments']]})
base = [python, '-m', 'pip', '--isolated', '--disable-pip-version-check', 'install',
        '--dry-run', '--ignore-installed', '--no-index', '--no-cache-dir',
        '--only-binary=:all:', '--find-links', corpus]
results = {}
for name in ['jericho', 'reasoning_gym', 'spreadsheetbench']:
    results[name] = run(HERE / 'raw', 'fullcorpus-' + name, base + ['-vv',
        '-r', HERE / 'profiles' / name / 'roots.in', '-c', HERE / 'profiles' / name / 'constraints.txt'], env=env)
results['mkl-service'] = run(HERE / 'raw', 'missing-mkl-service', base + ['mkl-service==' + manifest['artifacts']['mkl-service']['version']], env=env)
assert all(r['exit_code'] != 0 for r in results.values())
save(HERE / 'supplement-results.json', results)
shutil.rmtree(work)
save(HERE / 'raw/supplement-cleanup.json', {'directory': str(work), 'removed': not work.exists()})
print(json.dumps({k: v['exit_code'] for k, v in results.items()}))
