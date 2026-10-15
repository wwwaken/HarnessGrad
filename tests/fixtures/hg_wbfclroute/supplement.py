#!/usr/bin/env python3
import json
import os
from pathlib import Path
import subprocess
import sys
P = Path(__file__).resolve().parent
assert not (P / 'ordered-import.command.json').exists()
env = os.environ.copy()
env.update(PYTHONDONTWRITEBYTECODE='1', CUDA_VISIBLE_DEVICES='', OMP_NUM_THREADS='1',
           OPENBLAS_NUM_THREADS='1', JAX_PLATFORMS='cpu')
argv = ['timeout', '150s', sys.executable, str(P / 'offline_exec.py'), str(P / 'ordered_probe.py')]
with (P / 'ordered-import.stdout.txt').open('w') as out, (P / 'ordered-import.stderr.txt').open('w') as err:
    proc = subprocess.run(argv, cwd=P.parents[2], env=env, stdout=out, stderr=err, timeout=160)
(P / 'ordered-import.command.json').write_text(json.dumps({'argv': argv, 'returncode': proc.returncode,
    'cwd': str(P.parents[2]), 'stdout': 'ordered-import.stdout.txt', 'stderr': 'ordered-import.stderr.txt'}, indent=2) + '\n')
print(json.dumps({'returncode': proc.returncode}))
