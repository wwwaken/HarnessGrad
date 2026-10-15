#!/usr/bin/env python3
"""Bounded serial collection; keep every command, exit and raw stream."""
import json
import os
from pathlib import Path
import subprocess
import sys

P = Path(__file__).resolve().parent
R = P.parents[2]
assert not (P / 'commands.json').exists(), 'Never overwrite a prior collection'
commands = []

def execute(name, argv):
    assert not (P / (name + '.stdout.txt')).exists(), name
    env = os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE='1', CUDA_VISIBLE_DEVICES='', OMP_NUM_THREADS='1',
               OPENBLAS_NUM_THREADS='1', JAX_PLATFORMS='cpu')
    with (P / (name + '.stdout.txt')).open('w') as stdout, (P / (name + '.stderr.txt')).open('w') as stderr:
        process = subprocess.run(argv, cwd=R, env=env, stdout=stdout, stderr=stderr, timeout=160)
    receipt = {'name': name, 'argv': argv, 'cwd': str(R), 'returncode': process.returncode,
               'environment_overrides': {k: env[k] for k in ['PYTHONDONTWRITEBYTECODE', 'CUDA_VISIBLE_DEVICES',
                                           'OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'JAX_PLATFORMS']},
               'stdout': name + '.stdout.txt', 'stderr': name + '.stderr.txt'}
    commands.append(receipt)
    (P / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    print(json.dumps({'name': name, 'returncode': process.returncode}), flush=True)

def controlled(name, args):
    execute(name, ['timeout', '150s', sys.executable, str(P / 'offline_exec.py'), str(P / 'execute.py'), *args])

controlled('environment', ['environment'])
modules = [
 'bfcl_eval.eval_checker.eval_runner',
 'bfcl_eval.eval_checker.ast_eval.ast_checker',
 'bfcl_eval.model_handler.utils',
 'bfcl_eval.model_handler.local_inference.qwen',
 'bfcl_eval.constants.model_config',
 'bfcl_eval.model_handler.parser.java_parser',
 'bfcl_eval.model_handler.parser.js_parser',
 'bfcl_eval.eval_checker.ast_eval.type_convertor.java_type_converter',
 'bfcl_eval.eval_checker.ast_eval.type_convertor.js_type_converter',
 'bfcl_eval.eval_checker.eval_runner_helper',
 'searchless_chess.src.puzzles',
 'searchless_chess.src.engines.constants',
 'searchless_chess.src.engines.engine',
 'searchless_chess.src.engines.stockfish_engine',
 'searchless_chess.src.engines.lc0_engine',
 'searchless_chess.src.engines.neural_engines',
 'searchless_chess.src.training_utils',
 'searchless_chess.src.utils',
]
for i, module in enumerate(modules):
    controlled(f'import-{i:02}', ['import', module])
for mode in ['bfcl-official', 'bfcl-local', 'chess-board', 'chess-row', 'chess-local']:
    controlled(mode, [mode])
# Cache inventory and candidate resolution use no index, cache, endpoint or install.
execute('pip-cache-list', ['timeout', '30s', sys.executable, '-m', 'pip', 'cache', 'list', '--format=abspath'])
for name, requirement in [('tree-sitter', 'tree_sitter==0.21.3'), ('absl', 'absl-py')]:
    import tempfile
    with tempfile.TemporaryDirectory(prefix='hg-wbfclroute-wheel-probe-') as temporary:
        execute('offline-wheel-' + name, ['timeout', '45s', sys.executable,
            str(P / 'offline_exec.py'), str(P / 'pip_probe.py'), requirement, temporary])
        assert not list(Path(temporary).iterdir()), 'Unexpected local wheel: review before claiming unavailable'
    commands[-1]['scratch_removed'] = not Path(temporary).exists()
(P / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
