"""Require additive observation/evidence only; preserve all blockers, history and gates."""
import copy
import json
import subprocess
from common import HERE, ROOT

baseline = (HERE / 'baseline.stdout.txt').read_text().strip()
old = json.loads(subprocess.check_output(['git', 'show', baseline + ':docs/dataset-blockers.json'], cwd=ROOT, text=True))
new = json.loads((ROOT / 'docs/dataset-blockers.json').read_text())
remaining = copy.deepcopy(new)
before = next(b for b in old['shared_blockers'] if b['id'] == 'scorer-offline-closure')
after = next(b for b in remaining['shared_blockers'] if b['id'] == 'scorer-offline-closure')
assert after['observed'].startswith(before['observed'] + ' DS-1000 import profile completion - w-mkl2: ')
assert after['evidence'][:-1] == before['evidence']
assert after['evidence'][-1] == {'kind': 'repository', 'path': 'reports/w-mkl2-ds1000.md',
                                 'locator': '## DS-1000 import profile completion - w-mkl2'}
after['observed'], after['evidence'] = before['observed'], before['evidence']
assert remaining == old
assert new['review']['production_authorized'] is False
paths = subprocess.check_output(['git', 'diff', baseline, '--name-only'], cwd=ROOT, text=True).splitlines()
allowed = {'docs/dataset-blockers.json', 'docs/adapter-integration-journal.md',
           'reports/w-mkl2-ds1000.md', 'reports/w-mkl2-validation.txt'}
assert all(path in allowed or path.startswith('tests/fixtures/hg_wmkl2/') for path in paths), paths
journal = (ROOT / 'docs/adapter-integration-journal.md').read_text()
old_journal = subprocess.check_output(['git', 'show', baseline + ':docs/adapter-integration-journal.md'], cwd=ROOT, text=True)
assert journal.startswith(old_journal)
assert journal.count('## 2026-10-15 DS-1000 compatible import payload completion - w-mkl2') == 1
print(json.dumps({'baseline': baseline, 'additive_observed_and_evidence_only': True,
                  'all_statuses_next_actions_dataset_history_and_gates_unchanged': True,
                  'production_authorized': False, 'changed_paths': paths}, indent=2))
