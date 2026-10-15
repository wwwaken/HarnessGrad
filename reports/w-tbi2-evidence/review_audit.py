"""Check final source/registry preservation assertions; source-only."""
from __future__ import annotations
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = 'bf917b3'


def old_file(path, revision=BASE):
    return subprocess.check_output(['git', 'show', f'{revision}:{path}'], cwd=ROOT)


def main():
    current = json.loads((ROOT / 'docs/dataset-blockers.json').read_text())
    baseline = json.loads(old_file('docs/dataset-blockers.json'))
    expected = json.loads(json.dumps(baseline))
    old = next(b for b in expected['shared_blockers'] if b['id'] == 'scorer-offline-closure')
    new = next(b for b in current['shared_blockers'] if b['id'] == 'scorer-offline-closure')
    old['observed'], old['evidence'] = new['observed'], new['evidence']
    assert current == expected
    assert new['status'] == 'code-solvable'
    qa_paths = ['data/scaffolds/qa/base.py', 'data/scaffolds/qa/verify/check.py']
    qa = {}
    for rel in qa_paths:
        raw = (ROOT / rel).read_bytes()
        assert raw == old_file(rel)
        qa[rel] = hashlib.sha256(raw).hexdigest()
    tests = {}
    for rel, revision in [
        ('tests/quality/test_task_bound_native_inputs_w_tbi2.py', '6ad4151'),
        ('tests/quality/test_native_engine_input_paths_w_tbi2.py', '4e44c66')]:
        raw = (ROOT / rel).read_bytes()
        assert raw == old_file(rel, revision)
        tests[rel] = hashlib.sha256(raw).hexdigest()
    sources = []
    for line in (ROOT / 'reports/w-tbi2-evidence/current-source-audit.jsonl').read_text().splitlines():
        record = json.loads(line)
        if 'source' not in record:
            continue
        source = record['source']
        raw = (ROOT / source['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == source['sha256']
        sources.append(source)
    changed = subprocess.check_output(['git', 'diff', BASE, '--name-only'], cwd=ROOT, text=True).splitlines()
    assert not any(p.startswith('runs/') for p in changed)
    assert not any(p.startswith(('tests/fixtures/', 'reports/w-tbi-')) for p in changed)
    branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip()
    assert branch == 'wg-tbi2'
    print(json.dumps({'base': BASE, 'branch': branch,
        'registry_only_scorer_observed_and_evidence_changed': True,
        'dataset_records_history_shared_status_next_actions_gates_unchanged': True,
        'qa_bytes_unchanged': qa, 'same_final_test_files': tests,
        'current_source_hashes_match': sources, 'runs_and_frozen_receipts_diff_absent': True},
        indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
