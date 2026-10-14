"""AST-only read of adapters, checks and common verifier wiring; no adapter imports."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
paths=set(ROOT.glob('data/datasets/*.py'))
paths.update(ROOT.glob('data/datasets/*/verify/*.py'))
paths.update(ROOT.glob('data/datasets/*/lib/*.py'))
paths.update(ROOT.glob('data/datasets/*/Dockerfile*'))
paths.update([ROOT/'data/scaffolds/qa/base.py',ROOT/'data/scaffolds/qa/verify/check.py',
 ROOT/'eval/verification/verifier.py',ROOT/'eval/containers/sandbox.py',ROOT/'eval/run/runner.py',
 ROOT/'docs/dataset-blockers.json'])
rows=[]
for p in sorted(paths):
    raw=p.read_bytes();row={'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest()}
    if p.suffix=='.py':
        tree=ast.parse(raw)
        row['imports']=[{'line':n.lineno,'text':ast.get_source_segment(raw.decode(),n)}
            for n in ast.walk(tree) if isinstance(n,(ast.Import,ast.ImportFrom))]
        row['runtime_declarations']=[{'line':n,'text':s} for n,s in enumerate(raw.decode().splitlines(),1)
           if any(t in s for t in ['"kind": "files"','"kind": "container"','"image"',
                                  'HG_','"python3"','sys.executable','"version":','"sha256":'])]
    rows.append(row)
(OUT/'repository-inspection.json').write_text(json.dumps({'command':'python3 tests/fixtures/hg_wtbdep/inspect_repository.py',
 'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'files':rows},indent=2,sort_keys=True)+'\n')
