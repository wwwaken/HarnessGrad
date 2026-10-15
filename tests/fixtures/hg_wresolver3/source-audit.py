"""Recompute import-site roots and preserve exact source and wheel preimages."""
import ast
import importlib.metadata as installed
import json
from pathlib import Path
import shutil
import zipfile

from common import HERE, ROOT, digest, save, run

assert not (HERE / 'source-audit.json').exists()
inputs = json.loads((HERE / 'inputs.json').read_text())
records = {a['key']: a for a in inputs['artifacts']}
sources = []


def preserve(origin, data, rel):
    dest = HERE / 'source' / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    lines = data.decode().splitlines()
    relevant = [{'line': i, 'text': text} for i, text in enumerate(lines, 1)
                if any(s in text for s in ['import ', 'parquet_rows(', 'base.tables(', '"version":', '"package":', 'Requires-Dist:', 'Provides-Extra:'])]
    record = {'origin': str(origin), 'preimage': str(dest.relative_to(ROOT)),
              'sha256': digest(dest), 'bytes': len(data), 'excerpts': relevant}
    sources.append(record)
    return record


repo = ['data/datasets/' + n + '.py' for n in inputs['profiles']]
repo += ['data/scaffolds/qa/' + n for n in ['read.py', 'base.py', 'verify/check.py']]
repo += ['data/datasets/alfworld/lib/gym_env.py', 'data/datasets/alfworld/verify/check.py',
         'data/datasets/livecodebench/verify/check.py']
for path in repo:
    preserve(path, (ROOT / path).read_bytes(), 'repository/' + path)
upstream = Path('/mnt/20t/xubuqiang/datasets/livecodebench/_src/upstream/LiveCodeBench-28fef95ea8c9f7a547c8329f2cd3d32b92c1fa24/lcb_runner/evaluation')
for name in ['testing_util.py', 'pass_k_utils.py']:
    preserve(upstream / name, (upstream / name).read_bytes(), 'livecodebench-upstream/' + name)
members = {
    'alfworld': ['alfworld/agents/environment/alfred_tw_env.py'],
    'textworld': ['textworld/__init__.py', 'textworld/gym/__init__.py', 'textworld/envs/pddl/pddl.py'],
}
for key, names in members.items():
    wheel = Path(records[key]['path'])
    assert digest(wheel) == records[key]['sha256']
    with zipfile.ZipFile(wheel) as archive:
        for name in names:
            preserve(str(wheel) + ':' + name, archive.read(name), 'wheels/' + key + '/' + name)
for key in ['alfworld', 'textworld', 'pyarrow', 'numpy', 'fast-downward-textworld']:
    for suffix in ['METADATA', 'WHEEL']:
        info = records[key]['metadata'][suffix]
        preserve(records[key]['path'] + ':' + info['member'], (ROOT / info['path']).read_bytes(),
                 'wheels/' + key + '/' + info['member'])

# AST establishes exact external module names, without executing scorers or tasks.
imports = {}
for record in sources:
    if not record['preimage'].endswith('.py'):
        continue
    tree = ast.parse((ROOT / record['preimage']).read_text())
    imports[record['origin']] = sorted({alias.name.split('.')[0] for node in ast.walk(tree)
        if isinstance(node, ast.Import) for alias in node.names} |
        {node.module.split('.')[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module})
version_observations = {key: {'version': installed.version(key),
                            'installed_metadata': installed.distribution(key).read_text('METADATA')}
                        for key in ['numpy', 'pyarrow']}
assert version_observations['pyarrow']['version'] == records['pyarrow']['version']
assert version_observations['numpy']['version'] == records['numpy']['version']
save(HERE / 'source-audit.json', {'sources': sources, 'imports': imports,
     'root_requirements': inputs['profiles'], 'version_observations': version_observations,
     'scope': 'Default metadata graph for actual adapter/scorer imports; QA pyarrow is conditional on Parquet reading. ALFWorld pddl extra is mandatory transitively. No dynamic native/library/model/task execution claim.'})
run('source-sha256sum', ['sha256sum', *[ROOT / r['preimage'] for r in sources]])
print(json.dumps({'sources': len(sources), 'profiles': inputs['profiles'],
                  'imports': imports}, sort_keys=True))
