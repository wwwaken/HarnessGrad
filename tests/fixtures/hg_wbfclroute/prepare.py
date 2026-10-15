#!/usr/bin/env python3
"""Stage exact complete code-only modules; never read released task members."""
import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tarfile

P = Path(__file__).resolve().parent
R = P.parents[2]

def digest(body):
    return hashlib.sha256(body).hexdigest()

def write(name, value):
    (P / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def command(argv):
    result = subprocess.run(argv, cwd=R, text=True, capture_output=True, timeout=30)
    return dict(argv=argv, returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)

pins = json.loads((R / 'tests/fixtures/hg_bfcl/inventory.json').read_bytes())
identity = {'archives': [], 'sources': [], 'local_sources': [],
            'provenance_limit': 'Rechecked preserved custody, not new remote provenance or dependency closure.'}
archive_path = R / pins['archive']['path']
body = archive_path.read_bytes()
assert digest(body) == pins['archive']['sha256']
identity['archives'].append(dict(dataset='bfcl_v3', path=str(archive_path.relative_to(R)),
                                sha256=digest(body), bytes=len(body), revision=pins['commit']))
with tarfile.open(archive_path) as archive:
    assert archive.pax_headers['comment'] == pins['commit']
    for row in pins['files']:
        body = (R / row['path']).read_bytes()
        assert digest(body) == row['sha256']
        assert body == archive.extractfile(row['archive_member']).read()
        prefix = 'berkeley-function-call-leaderboard/'
        relative = row['original_path'].removeprefix(prefix)
        if relative == 'LICENSE':
            relative = 'LICENSE'
        target = P / 'source/bfcl' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
        identity['sources'].append(dict(dataset='bfcl_v3', path=str(target.relative_to(P)),
                                       original_path=row['path'], member=row['archive_member'],
                                       sha256=digest(body), bytes=len(body)))
# Code, requirements and licenses only, with no CSV, checkpoint or benchmark records.
chess_archive = Path('/mnt/20t/xubuqiang/datasets/chessbench_puzzles/_src/searchless_chess.tar.gz')
body = chess_archive.read_bytes()
from data.datasets import chessbench_puzzles
expected = next(x['sha256'] for x in chessbench_puzzles.downloads()
                if x.get('dst') == '_src/searchless_chess.tar.gz')
assert digest(body) == expected
identity['archives'].append(dict(dataset='chessbench_puzzles', path=str(chess_archive),
                                sha256=digest(body), bytes=len(body), revision=chessbench_puzzles.REVISION,
                                revision_basis='adapter pin and archive member prefix; no new remote attestation'))
with tarfile.open(chess_archive) as archive:
    for member in archive.getmembers():
        if not member.isfile():
            continue
        relative = member.name.split('/', 1)[1]
        assert '..' not in Path(relative).parts
        if not ((relative.startswith('src/') and relative.endswith('.py')) or
                relative in {'LICENSE', 'requirements.txt', 'pyproject.toml', 'setup.py', 'setup.cfg'}):
            continue
        body = archive.extractfile(member).read()
        target = P / 'source/chess/searchless_chess' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
        identity['sources'].append(dict(dataset='chessbench_puzzles', path=str(target.relative_to(P)),
                                       member=member.name, sha256=digest(body), bytes=len(body)))
for relative in ['data/datasets/bfcl_v3.py', 'data/datasets/chessbench_puzzles.py',
                 'data/scaffolds/qa/base.py', 'data/scaffolds/qa/verify/check.py',
                 'tests/fixtures/hg_woffscorer3/bfcl/offline_exec.py']:
    body = (R / relative).read_bytes()
    identity['local_sources'].append(dict(path=relative, sha256=digest(body), bytes=len(body)))
shutil.copyfile(R / 'tests/fixtures/hg_woffscorer3/bfcl/offline_exec.py', P / 'offline_exec.py')
write('identity.json', identity)
# Reuse explicitly authored controls, not their historical results.
bfcl = json.loads((R / 'tests/fixtures/hg_woffscorer3/bfcl/inputs.json').read_bytes())['cases']
for case in bfcl:
    case['category'] = 'simple'
    case['route'] = 'bfcl_eval.eval_checker.eval_runner.ast_file_runner'
for name, prediction in [('none', 'NONE'), ('empty-list', '[]'), ('full-call', 'draw(width=2)'),
                         ('bare-name', 'draw'), ('empty', '')]:
    bfcl.append(dict(id='irrelevance-' + name, prediction=prediction, function=[], possible_answer=[],
                     local_gold={'functions': [], 'subset': 'irrelevance'}, category='irrelevance',
                     route='bfcl_eval.eval_checker.eval_runner.relevance_file_runner'))
chess = json.loads((R / 'tests/fixtures/hg_woffscorer3/code_chess/inputs.json').read_bytes())['chessbench_puzzles']
for case in chess:
    case['route'] = 'searchless_chess.src.puzzles.evaluate_puzzle_from_board'
write('inputs.json', dict(scope='Authored offline controls; predeclared before execution; zero benchmark rows.',
                          bfcl_v3=bfcl, chessbench_puzzles=chess))
# AST use here only inventories entrypoints and import statements; execution uses importlib.
entries, imports = [], []
for source in identity['sources']:
    path = P / source['path']
    if path.suffix != '.py':
        continue
    tree = ast.parse(path.read_bytes(), filename=source['path'])
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            entries.append(dict(path=source['path'], symbol=node.name, line=node.lineno, end_line=node.end_lineno))
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(dict(path=source['path'], line=node.lineno, statement=ast.get_source_segment(path.read_text(), node)))
write('source-entrypoints.json', entries)
write('source-imports.json', imports)
# Preserve raw numbered complete source for reviewable file+line citations.
with (P / 'source-lines.txt').open('w') as output:
    for row in identity['sources']:
        if row['path'].endswith('.py') or row['path'].endswith('requirements.txt') or row['path'].endswith('pyproject.toml'):
            output.write('\nFILE ' + row['path'] + '\n')
            for number, line in enumerate((P / row['path']).read_text().splitlines(), 1):
                output.write(f'{number:5} {line}\n')
write('baseline.json', {'commands': [command(x) for x in [
    ['git', 'rev-parse', 'HEAD'], ['git', 'branch', '--show-current'], ['git', 'worktree', 'list', '--porcelain'],
    ['python3', 'tools/check_dataset_blockers.py']]],
    'source_member_counts': {d: sum(s['dataset'] == d for s in identity['sources'])
                             for d in ['bfcl_v3', 'chessbench_puzzles']},
    'controlled_input_counts': {d: len(x) for d, x in [('bfcl_v3', bfcl), ('chessbench_puzzles', chess)]}})
print(json.dumps({'archives': identity['archives'], 'staged_source_members': len(identity['sources']),
                  'controlled_input_counts': {'bfcl_v3': len(bfcl), 'chessbench_puzzles': len(chess)}}, indent=2))
