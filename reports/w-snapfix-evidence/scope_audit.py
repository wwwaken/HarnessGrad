#!/usr/bin/env python3
"""Check exact production/test/registry scope against this worktree's base commit."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
report = {}
for path, names in {
    'eval/containers/container.py': ['looks_pinned', 'snapshot_admission', 'stop', 'commit'],
    'eval/verification/verifier.py': ['_verify', '_copy_verifier_inputs', '_copy_relative_input'],
}.items():
    before = ast.parse((HERE / 'before' / path).read_bytes())
    after = ast.parse((ROOT / path).read_bytes())
    def functions(tree):
        return {n.name: ast.dump(n, include_attributes=False) for n in tree.body if isinstance(n, ast.FunctionDef)}
    a, b = functions(before), functions(after)
    for name in names:
        report[path + ':' + name] = {'unchanged': a[name] == b[name]}
        assert a[name] == b[name]
path = 'eval/verification/verifier.py'
a, b = (HERE / 'before' / path).read_text(), (ROOT / path).read_text()
marker = '# Step 9. `reward_file` first:'
assert a[a.index(marker):a.index('    finally:\n', a.index(marker))] == b[b.index(marker):b.index('    finally:\n', b.index(marker))]
report['snapshot_scoring_logic_unchanged'] = True
for path in ['eval/verification/pristine.py', 'eval/admission/artifact_admission.py', 'eval/service/services.py']:
    old = subprocess.run(['git', 'show', 'HEAD:' + path], cwd=ROOT, capture_output=True, check=True).stdout
    assert old == (ROOT / path).read_bytes()
    report[path] = {'unchanged': True}
old = json.loads((HERE / 'registry-before.json').read_bytes())
new = json.loads((ROOT / 'docs/dataset-blockers.json').read_bytes())
assert old['datasets'] == new['datasets'] and old['review'] == new['review']
for a, b in zip(old['shared_blockers'], new['shared_blockers'], strict=True):
    assert a.keys() == b.keys()
    assert all(a[k] == b[k] for k in a if k not in ('observed', 'evidence'))
    assert b['observed'].startswith(a['observed']) and b['evidence'][:-1] == a['evidence']
report['registry_only_shared_observed_and_evidence_appended'] = True
report['production_sources'] = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in
                                ['eval/containers/container.py', 'eval/containers/container_state.py', 'eval/verification/verifier.py']}
print(json.dumps(report, indent=2, sort_keys=True))
