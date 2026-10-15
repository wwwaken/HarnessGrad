#!/usr/bin/env bash
set -euxo pipefail
export PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1
python3 tools/check_dataset_blockers.py
python3 tests/fixtures/hg_we5/verify.py
python3 -m pytest tests/quality/test_we5_equivalence.py tests/quality/test_terminal_artifact_admission.py tests/quality/test_scorer_bundle_codex170.py tests/quality/test_dataset_blockers.py -q --basetemp=/tmp/harnessgrad-pytest-we5-final-review
python3 - <<'PY'
import json
from pathlib import Path
import subprocess
baseline = Path('tests/fixtures/hg_we5/commands.stdout.txt').read_text().splitlines()[0]
before = json.loads(subprocess.check_output(['git', 'show', baseline + ':docs/dataset-blockers.json']))
after = json.loads(Path('docs/dataset-blockers.json').read_text())
old = next(b for b in before['shared_blockers'] if b['id'] == 'artifact-only-state-export')
new = next(b for b in after['shared_blockers'] if b['id'] == 'artifact-only-state-export')
assert new['observed'].startswith(old['observed'] + ' ')
assert new['evidence'][:-1] == old['evidence']
new['observed'], new['evidence'] = old['observed'], old['evidence']
assert before == after
print('registry diff is additive artifact-only-state-export observed/evidence only; statuses, next_actions, datasets, history and authorization unchanged')
lines = Path('docs/adapter-integration-journal.md').read_text().splitlines()
assert any(line.startswith('## ') and line.endswith(' - w-e5') for line in lines)
status = subprocess.check_output(['git', 'status', '--porcelain', '-uall'], text=True).splitlines()
allowed = ('docs/dataset-blockers.json', 'docs/adapter-integration-journal.md', 'tests/fixtures/hg_we5/',
           'tests/quality/test_we5_equivalence.py', 'reports/w-e5-')
assert all(line[3:].startswith(allowed) for line in status), status
print('changed-path scope valid; production, runs and pre-existing receipts untouched')
PY
python3 - <<'PY'
import json
import subprocess
raw = subprocess.run(['git', 'diff', '--cached', '--check'], capture_output=True, text=True)
print(json.dumps({'raw_staged_whitespace_returncode': raw.returncode,
                  'stdout': raw.stdout, 'stderr': raw.stderr}, sort_keys=True))
retained_raw = ['tests/fixtures/hg_we5/commands.initial.stdout.txt',
                'tests/fixtures/hg_we5/commands.stdout.txt',
                'tests/fixtures/hg_we5/evidence/strategyqa-positive/exported/answer.txt',
                'tests/fixtures/hg_we5/evidence/strategyqa-positive/source/answer.txt',
                'tests/fixtures/hg_we5/pytest-initial.txt', 'tests/fixtures/hg_we5/source-audit.txt']
subprocess.run(['git', 'diff', '--cached', '--check', '--', '.',
                *[':!' + path for path in retained_raw]], check=True)
print('owned-change whitespace check passed; only verbatim raw outputs/source excerpts and intentional answer whitespace excluded')
PY
git diff --check
git status --short --untracked-files=no
