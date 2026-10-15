#!/usr/bin/env python3
"""Authored BFCL controls: unchanged upstream AST bodies versus actual adapter.

No fake model catalogue, dependency shim, handler constructor or generation call.
The full import failures are separate findings from source-function execution.
"""
from __future__ import annotations

import ast
import copy
import hashlib
import importlib
import importlib.abc
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import tarfile
import tempfile
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
PIN = ROOT / 'tests/fixtures/hg_bfcl/inventory.json'


def sha(body):
    return hashlib.sha256(body).hexdigest()


def identity():
    pin = json.loads(PIN.read_bytes())
    archive_path = ROOT / pin['archive']['path']
    assert sha(archive_path.read_bytes()) == pin['archive']['sha256']
    responses = ROOT / 'tests/fixtures/hg_bfcl/responses'
    tag = json.loads((responses / 'tag.body').read_bytes())
    commit = json.loads((responses / 'commit.body').read_bytes())
    assert tag['ref'] == pin['tag']
    assert tag['object']['sha'] == commit['sha'] == pin['commit']
    assert commit['tree']['sha'] == pin['root_tree']
    members = []
    with tarfile.open(archive_path, 'r:gz') as archive:
        assert archive.pax_headers['comment'] == pin['commit']
        for row in pin['files']:
            body = (ROOT / row['path']).read_bytes()
            blob = hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()
            assert sha(body) == row['sha256'] and blob == row['git_blob_sha1']
            # Exact allowlisted code/license/spec member only; never task data.
            assert body == archive.extractfile(row['archive_member']).read()
            members.append({'path': row['path'], 'original_path': row['original_path'],
                            'bytes': len(body), 'sha256': sha(body), 'git_blob_sha1': blob})
    sources = {}
    for name, suffix in [('ast_checker.py', 'bfcl_eval/eval_checker/ast_eval/ast_checker.py'),
                         ('utils.py', 'bfcl_eval/model_handler/utils.py')]:
        original = next(r for r in members if r['original_path'].endswith('/' + suffix))
        path = HERE / 'official-source' / name
        assert path.read_bytes() == (ROOT / original['path']).read_bytes()
        sources[name] = {'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes()),
                         'original_path': original['original_path']}
    return {'repository': 'https://github.com/ShishirPatil/gorilla',
            'tag': pin['tag'], 'commit': pin['commit'], 'root_tree': pin['root_tree'],
            'archive_path': pin['archive']['path'], 'archive_sha256': sha(archive_path.read_bytes()),
            'custody_inventory_path': str(PIN.relative_to(ROOT)), 'custody_inventory_sha256': sha(PIN.read_bytes()),
            'metadata_receipts': {str((responses / name).relative_to(ROOT)): sha((responses / name).read_bytes())
                                  for name in ('tag.body', 'commit.body')},
            'verified_members': members, 'verified_member_count': len(members), 'sources': sources}


class RetainedSourceFinder(importlib.abc.MetaPathFinder):
    """Resolve the retained code-only package across its historical fixture roots."""
    def __init__(self):
        self.modules = {}
        for row in json.loads(PIN.read_bytes())['files']:
            original = row['original_path']
            prefix = 'berkeley-function-call-leaderboard/'
            if original.startswith(prefix) and original.endswith('.py'):
                name = original[len(prefix):-3].replace('/', '.')
                if name.endswith('.__init__'):
                    name = name[:-len('.__init__')]
                self.modules[name] = ROOT / row['path']

    def find_spec(self, fullname, path=None, target=None):
        if fullname in self.modules:
            return importlib.util.spec_from_file_location(fullname, self.modules[fullname])
        return None


def import_attempt():
    finder = RetainedSourceFinder()
    sys.meta_path.insert(0, finder)
    rows = []
    try:
        with tempfile.TemporaryDirectory(prefix='hg-woffscorer3-bfcl-import-') as scratch:
            os.environ['BFCL_PROJECT_ROOT'] = scratch
            for module in ['bfcl_eval.eval_checker.ast_eval.ast_checker',
                           'bfcl_eval.model_handler.utils',
                           'bfcl_eval.model_handler.local_inference.base_oss_handler']:
                try:
                    imported = importlib.import_module(module)
                    rows.append({'module': module, 'imported': True, 'file': imported.__file__})
                except Exception as exc:
                    rows.append({'module': module, 'imported': False,
                                 'error': type(exc).__name__, 'message': str(exc),
                                 'traceback': traceback.format_exc()})
            imported_files = []
            for name, module in list(sys.modules.items()):
                if name.startswith('bfcl_eval') and getattr(module, '__file__', None):
                    path = Path(module.__file__)
                    imported_files.append({'module': name, 'path': str(path.relative_to(ROOT)),
                                           'sha256': sha(path.read_bytes())})
            writes = sorted(str(p.relative_to(scratch)) for p in Path(scratch).rglob('*'))
    finally:
        sys.meta_path.remove(finder)
    return {'identity': identity(), 'attempts': rows, 'imported_files': imported_files,
            'isolated_project_root_entries_before_cleanup': writes,
            'temporary_project_root_removed': not Path(scratch).exists(),
            'handler_constructed': False, 'generation_called': False}


def source_functions():
    """Select original nodes without rewriting bodies or filling missing globals.

    Python-only undotted Simple uses no catalogue or Java/JavaScript converter.
    The source selection is deliberately narrower than a full module import.
    """
    namespace = {'ast': ast, 're': re}
    selected = {}
    requests = {
        'utils.py': {'ast_parse', 'resolve_ast_call', 'resolve_ast_by_type', 'default_decode_ast_prompting'},
        'ast_checker.py': {'ast_checker', 'find_description', 'get_possible_answer_type',
                           'convert_func_name', 'type_checker', 'standardize_string', 'string_checker',
                           'list_checker', 'dict_checker', 'list_dict_checker', 'simple_function_checker'},
    }
    for name, wanted in requests.items():
        path = HERE / 'official-source' / name
        source = path.read_text()
        tree = ast.parse(source, filename=str(path))
        nodes = [n for n in tree.body if (isinstance(n, ast.FunctionDef) and n.name in wanted)
                 or (name == 'ast_checker.py' and isinstance(n, ast.Assign))]
        assert {n.name for n in nodes if isinstance(n, ast.FunctionDef)} == wanted
        selected[name] = [{'name': n.name if isinstance(n, ast.FunctionDef) else ast.unparse(n.targets[0]),
                            'line': n.lineno, 'end_line': n.end_lineno,
                            'source_sha256': sha(ast.get_source_segment(source, n).encode())} for n in nodes]
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), namespace)
    return namespace, selected


def execute(side, inputs):
    if side == 'official':
        namespace, selected = source_functions()
    else:
        from data.datasets import bfcl_v3 as adapter
        assert adapter._RECORDS == []
        selected = None
    rows = []
    for row in inputs['cases']:
        assert all('.' not in f['name'] for f in row['function'])
        if row['possible_answer']:
            assert row['local_gold']['functions'] == [next(iter(call)) for call in row['possible_answer']]
        try:
            if side == 'official':
                decoded = namespace['default_decode_ast_prompting'](row['prediction'], 'Python')
                raw = namespace['ast_checker'](copy.deepcopy(row['function']), decoded,
                      copy.deepcopy(row['possible_answer']), 'Python', 'simple', 'controlled-no-model')
                score = float(raw['valid'])
            else:
                decoded = None
                raw = adapter.score(row['prediction'], copy.deepcopy(row['local_gold']))
                score = raw['reward']
            rows.append({'id': row['id'], 'prediction': row['prediction'], 'raw_return': raw,
                         'decoded': decoded, 'score': score, 'error': None})
        except Exception as exc:
            rows.append({'id': row['id'], 'prediction': row['prediction'], 'score': None,
                         'error': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()})
    if side == 'local':
        assert adapter._RECORDS == []
    return {'side': side, 'inputs_sha256': sha((HERE / 'inputs.json').read_bytes()),
            'identity': identity(), 'selected_original_nodes': selected,
            'adapter_sha256': sha((ROOT / 'data/datasets/bfcl_v3.py').read_bytes()),
            'scope': 'unchanged AST-selected Python prompting parser and undotted Simple checker; no full module/handler claim',
            'cases': rows, 'production_runtime_observation': False}


def compare(inputs):
    official = json.loads((HERE / 'official.json').read_text())
    local = json.loads((HERE / 'local.json').read_text())
    assert official['identity'] == local['identity']
    assert official['inputs_sha256'] == local['inputs_sha256'] == sha((HERE / 'inputs.json').read_bytes())
    rows = []
    for inp, off, loc in zip(inputs['cases'], official['cases'], local['cases'], strict=True):
        assert inp['id'] == off['id'] == loc['id']
        assert inp['prediction'] == off['prediction'] == loc['prediction']
        numeric = off['error'] is None and loc['error'] is None
        rows.append({'id': inp['id'], 'official_score': off['score'], 'local_score': loc['score'],
                     'official_error': off['error'], 'local_error': loc['error'],
                     'numeric_comparison': numeric, 'agreement': off['score'] == loc['score'] if numeric else None})
    return {'controlled_inputs': len(rows), 'numeric_comparisons': sum(r['numeric_comparison'] for r in rows),
            'agreements': sum(r['agreement'] is True for r in rows),
            'divergences': sum(r['agreement'] is False for r in rows),
            'official_errors': sum(r['official_error'] is not None for r in rows),
            'local_errors': sum(r['local_error'] is not None for r in rows),
            'nonnumeric_inputs': sum(not r['numeric_comparison'] for r in rows), 'cases': rows}


if __name__ == '__main__':
    mode = sys.argv[1]
    inputs = json.loads((HERE / 'inputs.json').read_text())
    result = import_attempt() if mode == 'import' else compare(inputs) if mode == 'compare' else execute(mode, inputs)
    print(json.dumps(result, indent=2, sort_keys=True))
