"""Check exact registry mutation scope and preserve production/dataset/history state."""
import copy
import json
import pathlib
import subprocess
from acquire import HERE

ROOT=HERE.parents[2]
baseline=subprocess.check_output(['git','rev-parse','bf917b3'],cwd=ROOT,text=True).strip()
old=json.loads(subprocess.check_output(['git','show',baseline+':docs/dataset-blockers.json'],cwd=ROOT,text=True))
new=json.loads((ROOT/'docs/dataset-blockers.json').read_text())
adjusted=copy.deepcopy(new)
before=next(b for b in old['shared_blockers'] if b['id']=='scorer-offline-closure')
after=next(b for b in adjusted['shared_blockers'] if b['id']=='scorer-offline-closure')
assert after['observed'].startswith(before['observed']+' MKL payload obtainability and offline import coverage - w-mkl: ')
assert after['evidence'][:-1]==before['evidence']
assert after['evidence'][-1]=={'kind':'repository','path':'reports/w-mkl-payloads.md','locator':'## MKL payload obtainability and offline import coverage - w-mkl'}
after['observed']=before['observed'];after['evidence']=before['evidence']
assert adjusted==old,'Only shared scorer-offline-closure observed/evidence may change'
paths=subprocess.check_output(['git','diff',baseline,'--name-only'],cwd=ROOT,text=True).splitlines()
allowed={'docs/dataset-blockers.json','docs/adapter-integration-journal.md','reports/w-mkl-payloads.md','reports/w-mkl-validation.txt'}
assert all(p in allowed or p.startswith('tests/fixtures/hg_wmkl/') for p in paths),paths
journal=(ROOT/'docs/adapter-integration-journal.md').read_text()
assert journal.count('## 2026-10-15 Exact host MKL payload obtainability and offline imports - w-mkl')==1
print(json.dumps({'baseline':baseline,'registry_scope_valid':True,'production_changes':False,
 'dataset_status_next_action_history_unchanged':True,'production_authorized':new['review']['production_authorized']},indent=2))
