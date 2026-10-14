"""Validate literal citation locators and complete fixture manifest; source reads only."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
REPORT=ROOT/'reports/w-tbdep-transitive-inventory.md'
PATTERN=re.compile(r'((?:data|docs|eval|tests|tools|reports)/[A-Za-z0-9_./-]+):(\d+)')
p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
texts=[REPORT,OUT/'runtime/appworld-imported-package-surface.md',
       OUT/'runtime/terminal-bench-source-surface.md']
locators=[]
for path,num in sorted({(path,int(num)) for doc in texts for path,num in PATTERN.findall(doc.read_text())}):
    f=ROOT/path
    assert f.is_file(), f'missing citation file: {path}'
    lines=f.read_text().splitlines()
    assert 0<num<=len(lines), f'citation out of range: {path}:{num}'
    locator=lines[num-1]
    assert locator.strip(), f'empty citation: {path}:{num}'
    assert locator in f.read_text(), f'nonliteral locator: {path}:{num}'
    locators.append({'path':path,'line':num,'locator':locator})
if args.write:
    (OUT/'evidence-locators.json').write_text(json.dumps(locators,indent=2)+'\n')
else:
    assert json.loads((OUT/'evidence-locators.json').read_text())==locators,'stale locator inventory'
print(f'Citation checks: {len(locators)} literal path/line/locator records valid')
# Whole root manifest includes subordinate manifests; only itself is excluded.
files=sorted(f for f in OUT.rglob('*') if f.is_file() and f!=OUT/'SHA256SUMS')
assert not any('__pycache__' in f.parts for f in files), 'unexpected bytecode fixture'
expected=''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+str(f.relative_to(OUT))+'\n' for f in files)
if args.write:(OUT/'SHA256SUMS').write_text(expected)
else:assert (OUT/'SHA256SUMS').read_text()==expected,'fixture checksum/coverage mismatch'
print(f'Manifest checks: {len(files)} files covered; no missing or extra files')
