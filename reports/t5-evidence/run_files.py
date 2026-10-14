"""Run only the seven requested files, sequentially, with separate external temps."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path('/tmp/hg-t5')
OUT = ROOT / 'reports/t5-evidence'
PHASE = sys.argv[1]
FILES = sys.argv[2:] or [
    'test_container.py', 'test_services.py', 'test_container_state.py',
    'test_web_gateway.py', 'test_jericho_runtime_admission.py',
    'test_jericho_runtime_boundaries.py', 'test_appworld_service_diagnosis.py',
]
Path('/mnt/20t/xubuqiang/.hg-pytest/t5').mkdir(parents=True, exist_ok=True)
env = dict(os.environ)
env['PYTHONPATH'] = str(OUT / 'scope_guard') + os.pathsep + str(ROOT) + os.pathsep + env.get('PYTHONPATH', '')
for filename in FILES:
    name = Path(filename).stem
    argv = [sys.executable, '-m', 'pytest', 'tests/quality/' + filename,
            '--basetemp=/mnt/20t/xubuqiang/.hg-pytest/t5/' + PHASE + '-' + name,
            '-vv', '--tb=long', '-ra', '--color=no',
            '--junitxml=' + str(OUT / (PHASE + '-' + name + '.xml'))]
    log = OUT / (PHASE + '-' + name + '.log')
    print('START', filename, flush=True)
    with log.open('w') as stream:
        stream.write('$ ' + ' '.join(argv) + '\n')
        stream.flush()
        result = subprocess.run(argv, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
        stream.write(f'\nexit_code={result.returncode}\n')
    print('DONE', filename, 'exit_code=' + str(result.returncode), flush=True)
    for label, command in [('containers', ['docker', 'ps', '-a', '--no-trunc']),
                           ('networks', ['docker', 'network', 'ls', '--no-trunc'])]:
        state = subprocess.run(command, capture_output=True, text=True)
        (OUT / (PHASE + '-' + name + '-' + label + '.txt')).write_text(
            '$ ' + ' '.join(command) + '\n' + state.stdout + state.stderr)
