"""Complete dependencies skipped by an over-broad earlier reuse test; retain failures."""
import json
import os
from pathlib import Path
import socket
import sys
from common import HERE, environment, run, save

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
assert [name for _, name in net['interfaces']] == ['lo'] and not net['routes'].splitlines()[1:]
save(HERE / 'offline/retry-network.json', net)
old = HERE.parent / 'hg_wmkl'
installed_keys = {line.split('==')[0].lower().replace('_', '-') for line in (old / 'ds1000.lock').read_text().splitlines()}
plan = json.loads((HERE / 'offline/plan.json').read_text())
lines = []
for record in plan['install']:
    name = record['metadata']['name'].lower().replace('_', '-')
    if (name in installed_keys and name != 'scipy') or name == 'numpy':
        continue
    sha = record['download_info']['archive_info']['hashes']['sha256']
    lines.append(f"{record['metadata']['name']}=={record['metadata']['version']} --hash=sha256:{sha}\n")
(HERE / 'additions.lock').write_text(''.join(sorted(lines)))
work = Path(json.loads((HERE / 'work.json').read_text())['directory'])
prefix = work / 'ds1000'
python = str(prefix / 'bin/python')
payloads = json.loads((HERE / 'acquisition.json').read_text())['payload_directory']
env = environment()
env.update(PIP_NO_INDEX='1', XDG_CACHE_HOME=str(work / 'cache'))
assert run('offline/retry-additions-install', [python, '-m', 'pip', 'install', '--no-index', '--no-cache-dir',
           '--no-deps', '--require-hashes', '--find-links', payloads, '-r', str(HERE / 'additions.lock')],
           timeout=240, env=env)['exit_code'] == 0
r = run('offline/retry-completed-imports', [python, '-I', str(HERE / 'probe.py')], timeout=180, env=env)
assert r['exit_code'] == 0
assert run('offline/installed-distributions', [python, '-m', 'pip', 'list', '--format=json'], env=env)['exit_code'] == 0
save(HERE / 'result.json', {'state': 'complete-recorded-import-payload', 'prefix': str(prefix),
                          'original_pair_failure_reproduced': True, 'network_denied': True,
                          'import_probe_exit_code': r['exit_code'], 'admission_or_eligibility_changed': False,
                          'final_import_receipt': 'offline/retry-completed-imports.receipt.json',
                          'scope': 'Recorded source-led imports plus exact named context import sites; not full DS1000 resolution/scoring/ABI closure.'})
