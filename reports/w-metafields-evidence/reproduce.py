"""Capture the budget tests' driver invocations without pytest's output truncation.

Run from the worktree root. Evidence goes to the supplied persistent directory;
all materialisation goes to an owned temporary directory, removed in finally.
"""
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import time

root = Path.cwd()
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
module = runpy.run_path(str(root / 'tests/quality/test_unified_budget.py'))
for suffix, source, rounds in (
    ('batch', module['_BATCH_METHOD'], 5),
    ('single', module['_BATCH_METHOD'].replace('for i in range(3):', 'for i in range(1):'), 3),
    ('kept', module['_KEEPING_METHOD'], 4),
):
    tmp = Path(tempfile.mkdtemp(prefix=f'metafields-direct-{suffix}-', dir='/tmp'))
    run_id = tmp.name
    method = tmp / f'{run_id}.py'
    method.write_text(source, encoding='utf-8')
    argv = [sys.executable, 'driver.py', '--harness', 'loop_plain', '--mode', 'A',
            '--rounds', str(rounds), '--run-id', run_id, '--dataset', 'demo',
            '--sampling', 'all', '--side', 'train', '--no-sandbox',
            '--runs-root', str(tmp / 'runs'), '--work-root', str(tmp / 'work'),
            '--method-entrypoint', f'{sys.executable} {method}']
    env = {**os.environ, 'HG_AGENT_BACKEND': 'mock'}
    receipt = {
        'argv': argv, 'cwd': str(root), 'timeout_s': 900,
        'environment_expression': "{**os.environ, 'HG_AGENT_BACKEND': 'mock'}",
        'environment_overrides': {'HG_AGENT_BACKEND': 'mock'},
        'inherited_TMPDIR': os.environ.get('TMPDIR'),
        'inherited_environment_values': 'not dumped; may contain credentials',
    }
    start = time.monotonic()
    try:
        try:
            proc = subprocess.run(argv, cwd=root, env=env, capture_output=True,
                                  text=True, timeout=900)
            receipt.update(returncode=proc.returncode, timed_out=False)
            stdout, stderr = proc.stdout, proc.stderr
        except subprocess.TimeoutExpired as exc:
            receipt.update(returncode=None, timed_out=True)
            stdout, stderr = exc.stdout or b'', exc.stderr or b''
            stdout = stdout.decode() if isinstance(stdout, bytes) else stdout
            stderr = stderr.decode() if isinstance(stderr, bytes) else stderr
        receipt['elapsed_s'] = time.monotonic() - start
        (out / f'direct-{suffix}-stdout.txt').write_text(stdout)
        (out / f'direct-{suffix}-stderr.txt').write_text(stderr)
        for name in ('run_meta.json', 'curve.jsonl', 'events.jsonl'):
            path = tmp / 'runs' / run_id / name
            if path.exists():
                shutil.copyfile(path, out / f'direct-{suffix}-{name}')
    finally:
        shutil.rmtree(tmp)
        receipt['temporary_root_removed'] = not tmp.exists()
        (out / f'direct-{suffix}-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'case': suffix, **receipt}), flush=True)
