"""Review evidence consistency and ensure the registry change cannot close a gate."""
import copy
import json
import pathlib
import subprocess

HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASELINE=json.loads((HERE/'review-baseline.json').read_text())['commit']
def old(path):return subprocess.check_output(['git','show',BASELINE+':'+path],cwd=ROOT,text=True)
p='docs/dataset-blockers.json'
a=json.loads(old(p));z=json.loads((ROOT/p).read_text())
ab=next(b for b in a['shared_blockers'] if b['id']=='scorer-offline-closure')
zb=next(b for b in z['shared_blockers'] if b['id']=='scorer-offline-closure')
assert zb['observed'].startswith(ab['observed'])
assert zb['evidence'][:len(ab['evidence'])]==ab['evidence']
assert len(zb['evidence'])==len(ab['evidence'])+2
for e in zb['evidence'][-2:]:assert e['locator'] in (ROOT/e['path']).read_text()
normalized=copy.deepcopy(z)
b=next(b for b in normalized['shared_blockers'] if b['id']=='scorer-offline-closure')
b['observed']=ab['observed'];b['evidence']=ab['evidence']
assert normalized==a,'Registry changes beyond shared observed/evidence'
p='docs/adapter-integration-journal.md'
journal=(ROOT/p).read_text();assert journal.startswith(old(p))
heading='## 2026-10-15 — Pinned offline scorer installation payloads - w-wheelhouse'
assert journal.count(heading)==1
branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
assert branch and branch!='main',branch
worktrees=subprocess.check_output(['git','worktree','list','--porcelain'],cwd=ROOT,text=True)
assert f'worktree {ROOT}\n' in worktrees
changed=subprocess.check_output(['git','diff','--name-only',BASELINE],cwd=ROOT,text=True).splitlines()
allowed={'docs/dataset-blockers.json','docs/adapter-integration-journal.md','reports/w-wheelhouse-payloads.md','reports/w-wheelhouse-validation.txt'}
assert all(p in allowed or p.startswith('tests/fixtures/hg_wwheelhouse/') for p in changed),changed
coverage=json.loads((HERE/'dataset-payloads.json').read_text())
assert len(coverage)==19
assert sum(r['payload_status']=='complete-python-import-payloads' for r in coverage.values())==2
assert sum(r['payload_status']=='no-third-party-payload-required' for r in coverage.values())==8
assert sum(r['payload_status']=='partial-current-host-import-payloads' for r in coverage.values())==9
assert all(not r['production_authorized'] for r in coverage.values())
installs=json.loads((HERE/'install-summary.json').read_text())
assert len(installs)==9 and all(r['install']['exit_code']==0 for r in installs.values())
assert sum(r['import']['exit_code']==0 for r in installs.values())==8
for name in ['chessbench_puzzles','scienceworld']:
    assert json.loads((HERE/f'offline/pip-check-{name}.receipt.json').read_text())['exit_code']==0
retry=json.loads((HERE/'offline/retry-import-ds1000-with-native-providers.stdout.txt').read_text())
assert retry['torch']['ok'] and not retry['gensim']['ok']
print(json.dumps({'registry_scope':'shared observed + two evidence anchors only','all_statuses_next_actions_dataset_history_unchanged':True,
    'journal_append_only':True,'registered_worktree':str(ROOT),'branch':branch,'coverage':'2 nonempty complete Python import profiles / 8 empty / 9 partial',
    'offline_install_receipts':9,'initial_successful_import_profiles':8,'torch_retry':'import repaired; Gensim failure retained','production_authorized':False},indent=2))
