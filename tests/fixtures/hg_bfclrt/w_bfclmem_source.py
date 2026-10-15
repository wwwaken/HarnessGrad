#!/usr/bin/env python3
"""Static exact-wheel import/dynamic sites, including optional branches."""
import ast
import json
from pathlib import Path
import zipfile

from w_bfclmem import OUT, chunks, write

modules, edges, errors = [], [], []
archives = [json.loads(l) for l in (OUT / 'w-bfclmem-archives.jsonl').open()]
for ai, archive in enumerate(archives, 1):
    with zipfile.ZipFile(archive['path']) as z:
        for member in z.namelist():
            if not member.endswith('.py'):
                continue
            origin = len(modules) + 1
            module = member[:-3].replace('/', '.')
            if module.endswith('.__init__'):
                module = module[:-9]
            modules.append(dict(id=origin, module=module, member=member,
                                archive=f'tests/fixtures/hg_bfclrt/w-bfclmem-archives.jsonl:{ai}'))
            content = z.read(member)
            try:
                tree = ast.parse(content, filename=member)
            except (SyntaxError, ValueError) as e:
                errors.append(dict(module_id=origin, state='UNKNOWN unparsed source',
                                   exception=type(e).__name__, detail=str(e)))
                continue

            def visit(node, guard=()):
                if isinstance(node, (ast.If, ast.Try, ast.FunctionDef, ast.AsyncFunctionDef)):
                    guard = guard + (f'{type(node).__name__}:{node.lineno}',)
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    targets = [a.name for a in node.names] if isinstance(node, ast.Import) else [
                        '.' * node.level + (node.module or '')]
                    edges.append(dict(module_id=origin, line=node.lineno, targets=targets,
                                      names=[a.name for a in node.names], guard=list(guard),
                                      text=ast.get_source_segment(content.decode('utf-8-sig'), node),
                                      state='FOUND syntactic import; execution not inferred'))
                if isinstance(node, ast.Call):
                    func = ast.unparse(node.func)
                    if func in ['eval', 'exec', '__import__', 'importlib.import_module',
                                'ctypes.CDLL', 'ctypes.PyDLL', 'ctypes.cdll.LoadLibrary']:
                        edges.append(dict(module_id=origin, line=node.lineno, dynamic_call=func,
                                          guard=list(guard), text=ast.unparse(node)[:2000],
                                          state='FOUND dynamic site; runtime target UNKNOWN'))
                for child in ast.iter_child_nodes(node):
                    visit(child, guard)
            visit(tree)
chunks('w-bfclmem-source-modules', modules)
chunks('w-bfclmem-source-edges', edges)
write('w-bfclmem-source-summary.jsonl', [dict(
    modules=len(modules), edges=len(edges), errors=errors,
    dynamic_sites=sum('dynamic_call' in e for e in edges),
    scope='all .py members of selected wheels; static guards retained; neither runtime reachability nor arbitrary dlopen closure proven')])
