"""Static imports/exclusion census; never execute released code or retain solutions."""
import ast
import collections
import importlib.metadata as md
import importlib.util
import json
import platform
import re
import sys
from pathlib import Path
from common import HERE, ROOT, digest, save

DATA = Path('/mnt/20t/xubuqiang/datasets/ds1000/_src')
UPSTREAM = DATA / 'DS-1000-b39aab71'
source_dir = HERE / 'source'
source_dir.mkdir(exist_ok=True)
sources = [ROOT / 'data/datasets/ds1000.py', ROOT / 'data/datasets/ds1000/verify/check.py',
           UPSTREAM / 'environment.yml', UPSTREAM / 'execution.py']
records = []
for path in sources:
    name = path.name if path.parent == UPSTREAM else str(path.relative_to(ROOT)).replace('/', '__')
    target = source_dir / (name + '.numbered.txt')
    target.write_text(''.join(f'{i:4}\t{line}\n' for i, line in enumerate(path.read_text().splitlines(), 1)))
    records.append({'path': str(path), 'sha256': digest(path), 'numbered_copy': str(target.relative_to(ROOT))})
# Extract literal exclusion table and exact pattern without importing the adapter.
adapter = ast.parse(sources[0].read_text())
for node in adapter.body:
    if isinstance(node, ast.AnnAssign) and getattr(node.target, 'id', '') == 'MEASURED_EXCLUSIONS':
        measured = {i: cause for cause, indices in ast.literal_eval(node.value).items() for i in indices}
    if isinstance(node, ast.Assign) and any(getattr(t, 'id', '') == '_TF_PATTERN' for t in node.targets):
        tf_pattern = re.compile(ast.literal_eval(node.value.args[0]))
rows = [json.loads(line) for line in (DATA / 'test.jsonl').read_text().splitlines() if line.strip()]
tf_indices = {i for i, row in enumerate(rows) if tf_pattern.search(row['code_context'])}
excluded = tf_indices | set(measured)
imports = []
by_root = collections.defaultdict(set)
for index, row in enumerate(rows):
    context = row['code_context']
    tree = ast.parse(context)
    # Both top-level imports and imports hidden inside executed constant strings.
    trees = [(tree, 0, 'context')]
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and any(
                token in node.value for token in ('import tensorflow', 'from tensorflow', 'import xgboost', 'from gensim')):
            try:
                trees.append((ast.parse(node.value), node.lineno - 1, 'constant-string'))
            except SyntaxError:
                pass
    for subtree, offset, kind in trees:
        for node in ast.walk(subtree):
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            roots = [n.name.split('.')[0] for n in node.names] if isinstance(node, ast.Import) else [(node.module or '').split('.')[0]]
            for root in set(roots) & {'gensim', 'tensorflow', 'xgboost'}:
                line = node.lineno + offset
                by_root[root].add(index)
                imports.append({'root': root, 'jsonl_line': index + 1, 'row_index': index,
                                'context_line': line, 'kind': kind,
                                'text': context.splitlines()[line - 1],
                                'context_sha256': __import__('hashlib').sha256(context.encode()).hexdigest(),
                                'offered': index not in excluded,
                                'exclusion_reason': 'tensorflow-absent' if index in tf_indices else measured.get(index)})
summary = {'released_rows': len(rows), 'excluded_rows': len(excluded), 'offered_rows': len(rows) - len(excluded),
           'tensorflow_exclusion_rows': len(tf_indices), 'measured_exclusion_rows': len(measured),
           'imports': {root: {'released_rows': len(indices), 'offered_rows': len(indices - excluded),
                              'row_indices': sorted(indices)} for root, indices in sorted(by_root.items())}}
save(HERE / 'source-audit.json', {'sources': records, 'contexts_path': str(DATA / 'test.jsonl'),
                                'contexts_sha256': digest(DATA / 'test.jsonl'),
                                'summary': summary, 'imports': imports,
                                'scope': 'Only import statements, locations and derived counts; no task/context execution, questions or reference solutions.'})
print(json.dumps(summary, indent=2))
packages = {}
for name in ['gensim', 'scipy', 'tensorflow', 'tensorflow-cpu', 'tensorflow-gpu', 'tf-nightly', 'tf-nightly-cpu', 'xgboost']:
    try:
        packages[name] = {'version': md.version(name)}
    except md.PackageNotFoundError as exc:
        packages[name] = {'error': str(exc), 'exception': repr(exc)}
host = {'executable': sys.executable, 'python': sys.version, 'platform': platform.platform(),
        'packages': packages, 'specs': {name: repr(importlib.util.find_spec(name)) for name in ['tensorflow', 'xgboost']}}
save(HERE / 'host.json', host)
print(json.dumps(host, indent=2))
