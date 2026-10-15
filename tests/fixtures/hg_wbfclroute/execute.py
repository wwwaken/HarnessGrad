#!/usr/bin/env python3
"""Complete-module import/call attempts, with no selected-function fallback."""
from __future__ import annotations
import contextlib
import copy
import hashlib
import importlib
import importlib.metadata as metadata
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import traceback

P = Path(__file__).resolve().parent
R = P.parents[2]
sys.path.insert(0, str(R))
INPUTS = json.loads((P / 'inputs.json').read_bytes())
IDENTITY = json.loads((P / 'identity.json').read_bytes())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def failure(exc):
    return {'type': type(exc).__name__, 'message': str(exc),
            'exception_verbatim': ''.join(traceback.format_exception_only(type(exc), exc)).rstrip('\n'),
            'traceback': traceback.format_exc()}


def loaded():
    rows = []
    for name, module in sorted(sys.modules.copy().items()):
        path = getattr(module, '__file__', None)
        if path and name.startswith(('bfcl_eval', 'searchless_chess')):
            rows.append({'module': name, 'path': str(Path(path).resolve()), 'sha256': sha(path)})
    return rows


def run(mode, module_name=None):
    result = {'mode': mode, 'argv': sys.argv, 'inputs_sha256': sha(P / 'inputs.json'),
              'identity_sha256': sha(P / 'identity.json'), 'production_runtime_observation': False,
              'rows': []}
    calls = []
    def profile(frame, event, arg):
        if event != 'call':
            return
        filename = frame.f_code.co_filename
        if '/bfcl_eval/' in filename or '/searchless_chess/' in filename:
            item = {'file': filename, 'symbol': frame.f_code.co_name, 'line': frame.f_code.co_firstlineno}
            if item not in calls:
                calls.append(item)
    with tempfile.TemporaryDirectory(prefix='hg-wbfclroute-') as scratch:
        scratch = Path(scratch)
        os.environ['BFCL_PROJECT_ROOT'] = str(scratch / 'project')
        # Actual importable full packages in private scratch. Only original bytes copied.
        for kind in ['bfcl', 'chess']:
            shutil.copytree(P / 'source' / kind, scratch / kind)
            sys.path.insert(0, str(scratch / kind))
        sys.setprofile(profile)
        try:
            if mode == 'import':
                try:
                    module = importlib.import_module(module_name)
                    result.update(imported=True, module=module_name, file=module.__file__)
                except Exception as exc:
                    result.update(imported=False, module=module_name, error=failure(exc))
            elif mode == 'bfcl-official':
                for row in INPUTS['bfcl_v3']:
                    entry = {'id': row['id'], 'category': row['category'], 'prediction': row['prediction'],
                             'route': row['route'], 'score': None, 'measured': False,
                             'stage': 'import_complete_eval_runner', 'main_entered': False}
                    stdout, stderr = io.StringIO(), io.StringIO()
                    try:
                        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                            runner = importlib.import_module('bfcl_eval.eval_checker.eval_runner')
                            category = row['category']
                            case_root = scratch / 'cases' / row['id']
                            results = case_root / 'results' / 'Qwen_Qwen3-0.6B'
                            results.mkdir(parents=True)
                            data = scratch / 'bfcl/bfcl_eval/data'
                            (data / 'possible_answer').mkdir(parents=True, exist_ok=True)
                            name = 'BFCL_v3_' + category + '.json'
                            def jsonl(path, obj):
                                path.write_text(json.dumps(obj) + '\n')
                            case_id = category + '_0'
                            jsonl(data / name, {'id': case_id, 'function': row['function']})
                            jsonl(data / 'possible_answer' / name,
                                  {'id': case_id, 'ground_truth': row['possible_answer']})
                            jsonl(results / name, {'id': case_id, 'result': row['prediction']})
                            entry.update(stage='complete_main', main_entered=True)
                            runner.main(['Qwen/Qwen3-0.6B'], [category], results.parent, case_root / 'score')
                            score_file = case_root / 'score' / 'Qwen_Qwen3-0.6B' / ('BFCL_v3_' + category + '_score.json')
                            entry['score_file_raw'] = score_file.read_text()
                            record = json.loads(entry['score_file_raw'].splitlines()[0])
                            entry.update(score=record['accuracy'], measured=True,
                                         correct_count=record['correct_count'], total_count=record['total_count'])
                    except Exception as exc:
                        entry['error'] = failure(exc)
                    entry.update(stdout=stdout.getvalue(), stderr=stderr.getvalue())
                    result['rows'].append(entry)
            elif mode in {'chess-board', 'chess-row'}:
                for row in INPUTS['chessbench_puzzles']:
                    entry = {'id': row['id'], 'prediction': row['prediction'], 'gold': row['gold'],
                             'score': None, 'measured': False, 'scorer_entered': False,
                             'stage': 'import_complete_puzzles', 'requested_boards': []}
                    try:
                        puzzles = importlib.import_module('searchless_chess.src.puzzles')
                        import chess
                        class ScriptedPredictionSupplier:
                            """Only supplies authored predictions; contains no scoring logic."""
                            def __init__(self):
                                self.tokens = iter(row['prediction'].split())
                            def play(self, board):
                                entry['requested_boards'].append(board.fen())
                                return chess.Move.from_uci(next(self.tokens))
                        engine = ScriptedPredictionSupplier()
                        entry.update(stage='call_complete_module', scorer_entered=True)
                        if mode == 'chess-board':
                            raw = puzzles.evaluate_puzzle_from_board(chess.Board(row['gold']['fen']),
                                                                     row['gold']['moves'], engine)
                        else:
                            import pandas as pd
                            # Empty game with setup FEN gives the same pre-setup board as board route.
                            pgn = '[SetUp "1"]\n[FEN "' + row['gold']['fen'] + '"]\n\n*\n'
                            entry['pgn'] = pgn
                            raw = puzzles.evaluate_puzzle_from_pandas_row(pd.Series(
                                {'PGN': pgn, 'Moves': ' '.join(row['gold']['moves'])}), engine)
                        entry.update(raw_return=raw, score=float(raw), measured=True)
                    except Exception as exc:
                        entry['error'] = failure(exc)
                    result['rows'].append(entry)
            elif mode in {'bfcl-local', 'chess-local'}:
                dataset = 'bfcl_v3' if mode == 'bfcl-local' else 'chessbench_puzzles'
                module = importlib.import_module('data.datasets.' + dataset)
                for row in INPUTS[dataset]:
                    entry = {'id': row['id'], 'prediction': row['prediction'], 'score': None, 'measured': False}
                    try:
                        gold = row['local_gold'] if dataset == 'bfcl_v3' else row['gold']
                        raw = module.score(row['prediction'], copy.deepcopy(gold))
                        entry.update(raw_return=raw, score=raw['reward'], measured=True)
                    except Exception as exc:
                        entry['error'] = failure(exc)
                    result['rows'].append(entry)
                empty_cache = module._RECORDS == [] if dataset == 'bfcl_v3' else module._BUILT is None
                assert empty_cache
                result.update(adapter_sha256=sha(module.__file__), dataset_cache_empty=empty_cache)
            elif mode == 'environment':
                names = ['tree-sitter', 'tree-sitter-java', 'tree-sitter-javascript', 'absl-py', 'chess',
                         'jax', 'dm-haiku', 'chex', 'grain-nightly', 'optax', 'orbax-checkpoint', 'apache-beam',
                         'jaxtyping', 'cohere', 'mistralai', 'google-genai', 'qwen-agent', 'writer-sdk', 'overrides']
                result['distributions'] = {}
                for name in names:
                    try:
                        result['distributions'][name] = {'version': metadata.version(name)}
                    except metadata.PackageNotFoundError as exc:
                        result['distributions'][name] = {'version': None, 'error': failure(exc)}
                wheelhouse = Path('/tmp/hg-wwheelhouse-payloads-e5uywviu')
                result['wheelhouse'] = {'path': str(wheelhouse), 'exists': wheelhouse.is_dir(),
                                        'filenames': sorted(x.name for x in wheelhouse.iterdir() if x.is_file())}
                result['python'] = sys.version
            else:
                raise ValueError(mode)
            result['loaded_official_modules'] = loaded()
            result['official_python_calls'] = calls
            result['scratch_entries_before_cleanup'] = sorted(str(p.relative_to(scratch)) for p in scratch.rglob('*'))
            result['source_checks'] = []
            for row in IDENTITY['sources']:
                parts = Path(row['path']).parts
                target = scratch / parts[1] / Path(*parts[2:])
                actual = sha(target)
                assert actual == row['sha256']
                result['source_checks'].append({'path': row['path'], 'sha256': actual})
        finally:
            sys.setprofile(None)
    result['scratch'] = str(scratch)
    result['scratch_removed'] = not scratch.exists()
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == '__main__':
    run(*sys.argv[1:])
