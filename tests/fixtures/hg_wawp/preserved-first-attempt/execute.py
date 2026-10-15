"""Bounded offline collector. Never invokes a driver, model, GPU, or service."""
import json
from pathlib import Path
import shlex
import subprocess
import sys
import uuid

F = Path(__file__).resolve().parent
ROOT = F.parents[2]
IMAGE = 'sha256:f3cb916b9bdc297d4c73dd9646e9550befb7c6e23827d937b90a0640373e97ca'
DATA = '/mnt/20t/xubuqiang/datasets/appworld/_src/unpacked/data'
CASES = json.loads((F/'inputs.json').read_text())['cases']
commands = []
cleanup = []
for case in CASES:
    for mode in ['official', 'local']:
        if len(sys.argv) > 1 and case['id'] != sys.argv[1]:
            continue
        name = 'hg-wawp-' + uuid.uuid4().hex[:12]
        target = F/'raw'/case['id']/mode
        target.mkdir(parents=True, exist_ok=False)
        argv = ['docker', 'create', '--pull=never', '--name', name, '--network', 'none',
                '--read-only', '--tmpfs', '/tmp:rw,nosuid,size=512m', '--tmpfs', '/appworld:ro,size=1m',
                '--cpus', '1', '--memory', '2g', '--pids-limit', '128',
                '--ulimit', 'cpu=120:120', '--ulimit', 'nofile=256:256',
                '-e', 'PYTHONDONTWRITEBYTECODE=1', '-e', 'CUDA_VISIBLE_DEVICES=',
                '--mount', f'type=bind,src={F},dst=/fixture,readonly',
                '--mount', f'type=bind,src={ROOT}/data/datasets/appworld/verify/check.py,dst=/adapter/check.py,readonly',
                '--mount', f'type=bind,src={DATA}/base_dbs,dst=/base-dbs,readonly',
                '--entrypoint', 'python', IMAGE, '/fixture/run_case.py', mode, case['id']]
        item = {'case': case['id'], 'mode': mode, 'container_name': name, 'commands': []}
        def run(args, stem, timeout=30):
            item['commands'].append(shlex.join(args))
            result = subprocess.run(args, capture_output=True, timeout=timeout)
            (target/(stem+'.stdout.txt')).write_bytes(result.stdout)
            (target/(stem+'.stderr.txt')).write_bytes(result.stderr)
            (target/(stem+'.returncode.txt')).write_text(str(result.returncode)+'\n')
            return result
        try:
            created = run(argv, 'create')
            if created.returncode:
                raise RuntimeError(created.stderr.decode())
            run(['docker', 'inspect', name], 'inspect-before')
            try:
                run(['docker', 'start', '-a', name], 'execute', timeout=150)
            except subprocess.TimeoutExpired as exc:
                (target/'collector-timeout.json').write_text(json.dumps({'seconds': exc.timeout})+'\n')
                run(['docker', 'kill', name], 'kill')
            run(['docker', 'inspect', name], 'inspect-after')
        finally:
            removed = run(['docker', 'rm', '-f', name], 'remove')
            absent = run(['docker', 'inspect', name], 'absence')
            cleanup.append({'container': name, 'removed': removed.returncode == 0,
                            'absent': absent.returncode != 0})
            commands.append(item)
            # Incremental receipts survive a later collector failure.
            (F/'execution-commands.json').write_text(json.dumps(commands, indent=2)+'\n')
            (F/'cleanup.json').write_text(json.dumps(cleanup, indent=2)+'\n')
        print(case['id'], mode, flush=True)
