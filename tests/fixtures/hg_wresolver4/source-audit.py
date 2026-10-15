"""Recompute requirement sites and retain exact source preimages without imports."""
import ast
import json
from pathlib import Path
import re
from common import HERE,ROOT,save,digest,run

assert not (HERE/'source-audit.json').exists()
paths=[ROOT/'data/datasets'/p for p in ['gaia.py','gaia/Dockerfile','gaia/prepare.py','gaia/verify/check.py','appworld.py','appworld/Dockerfile','appworld/Dockerfile.agent','appworld/service.py','appworld/server.sh','appworld/verify/check.py']]
paths.append(Path('/mnt/20t/xubuqiang/datasets/gaia/_src/scorer.py'))
records=[]
for source in paths:
 rel=source.relative_to(ROOT) if source.is_relative_to(ROOT) else Path('external/gaia/scorer.py')
 target=HERE/'source'/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
 lines=source.read_text().splitlines();imports=[]
 if source.suffix=='.py':
  for n in ast.walk(ast.parse(source.read_text())):
   if isinstance(n,(ast.Import,ast.ImportFrom)):
    imports.append({'line':n.lineno,'text':lines[n.lineno-1],'ast':ast.dump(n)})
 excerpts=[{'line':i,'text':s} for i,s in enumerate(lines,1) if re.search(r'from |import |pip install|^FROM |appworld.cli|uvicorn|HG_APPWORLD_VERIFIER_IMAGE',s)]
 records.append({'source':str(source.relative_to(ROOT)) if source.is_relative_to(ROOT) else str(source),'preimage':str(target.relative_to(ROOT)),'sha256':digest(source),'bytes':source.stat().st_size,'imports':imports,'excerpts':excerpts})
profile={'gaia':{'roots':['numpy','openpyxl','pillow','requests','beautifulsoup4','lxml','pyarrow'],'derivation':'Verifier imports upstream scorer, whose line 6 imports numpy. Dockerfile line 22 declares six image roots; prepare.py line 113 conditionally imports pyarrow.parquet. Union is a finite metadata reconstruction; native apt/image installed-byte equivalence remains unclaimed. Bare source roots use freshly host-observed exact candidates, not upstream pins.'},'appworld':{'roots':['appworld==0.1.3.post1','uvicorn<1'],'derivation':'Verifier line 44 and service line 15 import AppWorld; service lines 13/14 import fastapi/munch; Dockerfile line 4 declares appworld/uvicorn on Python 3.11 and line 5 invokes CLI install. Python default dependency graph and CLI installed source must both be accounted for before complete dataset credit.'}}
save(HERE/'source-audit.json',{'sources':records,'profiles':profile})
run('source-sha256sum',['sha256sum',*[ROOT/r['preimage'] for r in records]])
print(json.dumps({'sources':len(records),'profiles':profile},indent=2,sort_keys=True))
for r in records:
 print(r['sha256'],r['source'])
 for e in r['excerpts']:print(f"{r['source']}:{e['line']}: {e['text']}")
