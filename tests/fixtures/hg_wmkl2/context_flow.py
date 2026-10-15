"""Retain only import-related control-flow sites, no questions/solutions or contexts."""
import ast
import json
from pathlib import Path
from common import HERE, digest, save

path = Path('/mnt/20t/xubuqiang/datasets/ds1000/_src/test.jsonl')
rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
result = []
for index in [379, 380, 706, 837, 838, 936, 937]:
    context = rows[index]['code_context']
    sites = []
    for node in ast.walk(ast.parse(context)):
        kind = None
        if isinstance(node, ast.FunctionDef) and node.name == 'test_execution':
            kind = 'test_execution-definition'
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'exec':
            kind = 'exec-call'
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'exec_context' for target in node.targets):
            kind = 'exec_context-string-start'
        if kind:
            sites.append({'context_line': node.lineno, 'kind': kind, 'text': context.splitlines()[node.lineno-1]})
    result.append({'row_index': index, 'jsonl_line': index + 1, 'sites': sorted(sites, key=lambda v: v['context_line'])})
save(HERE / 'context-flow-sites.json', {'path': str(path), 'sha256': digest(path), 'rows': result})
print(json.dumps(result, indent=2))
