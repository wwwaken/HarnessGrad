"""Bounded resolver evidence helpers. No benchmark imports or scoring calls."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def save(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def run(directory, label, argv, *, env=None, timeout=120):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    try:
        p = subprocess.run(list(map(str, argv)), capture_output=True, env=env,
                           timeout=timeout)
        code, stdout, stderr = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as exc:
        code, stdout, stderr = 124, exc.stdout or b'', exc.stderr or b''
    (directory / (label + '.stdout.txt')).write_bytes(stdout)
    (directory / (label + '.stderr.txt')).write_bytes(stderr)
    record = {'argv': list(map(str, argv)), 'exit_code': code,
              'elapsed_seconds': time.monotonic() - started,
              'timeout_seconds': timeout}
    save(directory / (label + '.command.json'), record)
    print(label, 'exit_code', code, flush=True)
    return record


def clean_env(work):
    env = {k: v for k, v in os.environ.items()
           if not k.lower().endswith('_proxy')
           and not k.startswith(('PIP_', 'UV_', 'PYTHON'))}
    env.update(HOME=str(work), XDG_CACHE_HOME=str(work / 'cache'),
               PIP_CONFIG_FILE='/dev/null', UV_NO_CONFIG='1',
               CUDA_VISIBLE_DEVICES='', PYTHONDONTWRITEBYTECODE='1', LC_ALL='C.UTF-8')
    return env
