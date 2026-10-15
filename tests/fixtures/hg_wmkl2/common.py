"""Bounded command capture for package/source evidence, never benchmark execution."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def environment():
    env = dict(os.environ, CUDA_VISIBLE_DEVICES='', PYTHONDONTWRITEBYTECODE='1',
               MPLBACKEND='Agg', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
               MKL_NUM_THREADS='1', PIP_DISABLE_PIP_VERSION_CHECK='1')
    for key in ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy',
                'all_proxy', 'PYTHONPATH', 'PYTHONHOME', 'LD_LIBRARY_PATH', 'LD_PRELOAD'):
        env.pop(key, None)
    return env


def run(label, command, timeout=180, env=None):
    start = time.monotonic()
    try:
        p = subprocess.run(command, cwd=ROOT, env=environment() if env is None else env,
                           capture_output=True, text=True, timeout=timeout)
        code, stdout, stderr = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as exc:
        code = 124
        stdout, stderr = exc.stdout or b'', exc.stderr or b''
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors='replace')
        if isinstance(stderr, bytes):
            stderr = stderr.decode(errors='replace')
        stderr += '\nBounded command timed out.\n'
    target = HERE / label
    target.parent.mkdir(parents=True, exist_ok=True)
    target.with_suffix('.stdout.txt').write_text(stdout)
    target.with_suffix('.stderr.txt').write_text(stderr)
    receipt = {'command': command, 'cwd': str(ROOT), 'exit_code': code,
               'elapsed_seconds': round(time.monotonic() - start, 3)}
    save(target.with_suffix('.receipt.json'), receipt)
    print(label, code, flush=True)
    return receipt
