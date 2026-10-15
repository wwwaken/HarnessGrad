"""Fresh local installs/imports in a kernel network namespace, no scorers."""
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import venv
from common import HERE, ROOT, digest, environment, run, save

old = HERE.parent / 'hg_wmkl'
older = HERE.parent / 'hg_wwheelhouse'
net = {'command': sys.orig_argv, 'namespace': os.readlink('/proc/self/ns/net'),
       'interfaces': socket.if_nameindex(), 'routes': Path('/proc/net/route').read_text()}
try:
    with socket.socket() as sock:
        sock.settimeout(1)
        sock.connect(('198.51.100.1', 443))
    raise AssertionError('Network unexpectedly reachable')
except OSError as exc:
    net.update(errno=exc.errno, exception=repr(exc))
    assert exc.errno == 101
assert [name for _, name in net['interfaces']] == ['lo']
assert not net['routes'].splitlines()[1:]
save(HERE / 'offline/network.json', net)
work = Path(tempfile.mkdtemp(prefix='hg-wmkl2-offline-'))
save(HERE / 'work.json', {'directory': str(work), 'base_python': sys.executable,
                          'system_site_packages': False, 'base_interpreter_stdlib_OS_ABI_external': True})
env = environment()
env.update(PIP_NO_INDEX='1', CONDA_NO_PLUGINS='true', CONDA_SOLVER='classic',
           CONDA_OFFLINE='true', CONDA_PKGS_DIRS=str(work / 'pkgs'),
           CONDA_ENVS_PATH=str(work / 'envs'), XDG_CACHE_HOME=str(work / 'cache'))
# Negative controls and exact host failure are distinct from the new installed prefix.
venv.EnvBuilder(with_pip=True, system_site_packages=False).create(work / 'negative')
for name in ['gensim', 'tensorflow', 'xgboost']:
    r = run('offline/negative-' + name, [str(work / 'negative/bin/python'), '-I', '-c', 'import ' + name], env=env)
    assert r['exit_code'] == 1
r = run('offline/host-original-pair', [sys.executable, '-I', str(HERE / 'reproduce.py')], env=env)
assert r['exit_code'] == 1
assert "cannot import name 'triu' from 'scipy.linalg'" in (HERE / 'offline/host-original-pair.stderr.txt').read_text()
conda_records = json.loads((old / 'artifacts.json').read_text()) + json.loads((old / 'support-artifacts.json').read_text())
paths = []
used = []
for record in conda_records:
    path = old / 'artifacts' / record['fn']
    assert digest(path) == record['sha256']
    paths.append(str(path))
    used.append({'path': str(path), 'sha256': digest(path), 'bytes': path.stat().st_size, 'role': 'exact-host-conda-payload'})
prefix = work / 'ds1000'
r = run('offline/conda-install', [str(Path(sys.prefix) / 'bin/conda'), 'create', '--offline', '--yes', '--no-deps',
        '--solver', 'classic', '--no-default-packages', '--prefix', str(prefix), *paths], timeout=240, env=env)
assert r['exit_code'] == 0
venv.EnvBuilder(with_pip=True, system_site_packages=False).create(prefix)
python = str(prefix / 'bin/python')
legacy = json.loads((old / 'reused-artifacts.json').read_text())
legacy_dir = json.loads((older / 'manifest.json').read_text())['payload_directory']
for line in (old / 'ds1000.lock').read_text().splitlines():
    key = line.split('==')[0].lower().replace('_', '-')
    record = legacy[key]
    path = Path(record['path'])
    assert digest(path) == record['sha256'], path
    used.append(dict(record, role='previous-ds1000-python-payload'))
r = run('offline/original-profile-install', [python, '-m', 'pip', 'install', '--no-index', '--no-cache-dir', '--no-deps',
        '--require-hashes', '--find-links', legacy_dir, '-r', str(old / 'ds1000.lock')], timeout=300, env=env)
assert r['exit_code'] == 0
r = run('offline/fresh-original-pair', [python, '-I', str(HERE / 'reproduce.py')], env=env)
assert r['exit_code'] == 1
assert "cannot import name 'triu' from 'scipy.linalg'" in (HERE / 'offline/fresh-original-pair.stderr.txt').read_text()
# Resolver is bounded to the added scientific roots and unchanged existing pins, with local bytes only.
payloads = Path(json.loads((HERE / 'acquisition.json').read_text())['payload_directory'])
for path in sorted(payloads.glob('*.whl')):
    used.append({'path': str(path), 'sha256': digest(path), 'bytes': path.stat().st_size, 'role': 'downloaded-wheel'})
save(HERE / 'reused-and-downloaded-artifacts.json', used)
plan = HERE / 'offline/plan.json'
r = run('offline/local-resolver', [python, '-m', 'pip', 'install', '--dry-run', '--ignore-installed', '--no-index',
        '--no-cache-dir', '--find-links', str(payloads), '--find-links', legacy_dir,
        '--constraint', str(HERE / 'existing-pins.constraints.txt'), '--report', str(plan),
        'gensim==4.3.2', 'scipy==1.12.0', 'numpy==1.26.4', 'tensorflow-cpu==2.16.1', 'xgboost==2.0.3'], timeout=180, env=env)
assert r['exit_code'] == 0
installed_keys = {line.split('==')[0].lower().replace('_', '-') for line in (old / 'ds1000.lock').read_text().splitlines()}
selected = json.loads(plan.read_text())['install']
lines = []
for record in selected:
    name = record['metadata']['name'].lower().replace('_', '-')
    if (name in installed_keys and name != 'scipy') or name == 'numpy':
        # These exact versions are already installed from rehashed original payloads / Conda NumPy.
        continue
    sha = record['download_info']['archive_info']['hashes']['sha256']
    lines.append(f"{record['metadata']['name']}=={record['metadata']['version']} --hash=sha256:{sha}\n")
(HERE / 'additions.lock').write_text(''.join(sorted(lines)))
r = run('offline/additions-install', [python, '-m', 'pip', 'install', '--no-index', '--no-cache-dir', '--no-deps',
        '--require-hashes', '--find-links', str(payloads), '-r', str(HERE / 'additions.lock')], timeout=300, env=env)
assert r['exit_code'] == 0
r = run('offline/completed-imports', [python, '-I', str(HERE / 'probe.py')], timeout=180, env=env)
assert r['exit_code'] == 0
assert run('offline/installed-distributions', [python, '-m', 'pip', 'list', '--format=json'], env=env)['exit_code'] == 0
save(HERE / 'result.json', {'state': 'complete-recorded-import-payload', 'prefix': str(prefix),
                          'original_pair_failure_reproduced': True, 'network_denied': True,
                          'import_probe_exit_code': r['exit_code'], 'admission_or_eligibility_changed': False,
                          'scope': 'Recorded source-led imports plus exact named context import sites; not full DS1000 resolution/scoring/ABI closure.'})
