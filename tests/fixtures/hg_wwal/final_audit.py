"""Confirm registry append-only scope, evidence locators, and protected paths."""
import copy
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
before = json.loads(subprocess.run(['git','show','HEAD:docs/dataset-blockers.json'], cwd=ROOT,
                                  check=True,capture_output=True,text=True).stdout)
after = json.loads((ROOT / 'docs/dataset-blockers.json').read_text())
normalized = copy.deepcopy(after)
old = next(x for x in before['shared_blockers'] if x['id']=='artifact-only-state-export')
new = next(x for x in normalized['shared_blockers'] if x['id']=='artifact-only-state-export')
assert new['observed'].startswith(old['observed'])
assert new['evidence'][:len(old['evidence'])] == old['evidence']
assert len(new['evidence']) > len(old['evidence'])
for row in new['evidence'][len(old['evidence']):]:
    assert row['locator'] in (ROOT / row['path']).read_text()
new['observed'] = old['observed']
new['evidence'] = old['evidence']
assert normalized == before
headings = [line for line in (ROOT/'docs/adapter-integration-journal.md').read_text().splitlines() if line.startswith('## ')]
assert headings[-1].endswith(' - w-wal')
print(json.dumps({'registry_only_appended_observation_and_evidence': True,
                  'all_blockers_status_next_actions_datasets_history_gates_unchanged': True,
                  'evidence_locators_found_verbatim': True,
                  'production_authorized': after['review']['production_authorized']}, sort_keys=True))
argv=['git','diff','--exit-code','HEAD','--','runs/','tests/fixtures/hg_we5/','reports/w-e5-equivalence.md','reports/w-e5-validation.txt']
p=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True)
print(json.dumps(dict(argv=argv,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr),sort_keys=True))
assert p.returncode==0
