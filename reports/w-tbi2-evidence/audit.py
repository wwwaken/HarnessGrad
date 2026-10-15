"""Recompute current source identities and archive exact lines; no scorer execution."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NAMES = ('alfworld', 'bird_minidev', 'ds1000', 'jericho', 'livecodebench',
         'scienceworld', 'spreadsheetbench')


def identity(path):
    digest = hashlib.sha256()
    size = 0
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            size += len(block)
            digest.update(block)
    return {'path': str(path.relative_to(ROOT)), 'bytes': size, 'sha256': digest.hexdigest()}


def main():
    print(json.dumps({'base': subprocess.check_output(['git', 'rev-parse', 'HEAD'],
                     cwd=ROOT, text=True).strip(),
                     'scope': 'source and raw control identities; no benchmark execution'}))
    paths = [ROOT / 'data/scaffolds/scorer_input.py', ROOT / 'eval/verification/verifier.py',
             ROOT / 'data/dataset.schema.json', ROOT / 'data/datasets/jericho/lib/jer_env.py',
             ROOT / 'data/datasets/scienceworld/lib/scw_env.py']
    paths += [ROOT / f'data/datasets/{n}.py' for n in NAMES]
    paths += [ROOT / f'data/datasets/{n}/verify/check.py' for n in NAMES]
    paths += [ROOT / 'data/scaffolds/qa/base.py', ROOT / 'data/scaffolds/qa/verify/check.py']
    for path in paths:
        lines = path.read_text().splitlines()
        # Full line-numbered source avoids brittle substring-only source locators.
        print(json.dumps({'source': identity(path), 'lines': [
            {'line': n, 'text': line} for n, line in enumerate(lines, 1)]}, sort_keys=True))
    for rel in ('reports/w-tbi-receipts.md', 'reports/w-tbi-evidence/input-source-audit.jsonl',
                'reports/w-tbi-evidence/tests-before.txt', 'reports/w-tbi-evidence/tests-after.txt',
                'tests/quality/test_task_bound_native_inputs_w_tbi2.py'):
        print(json.dumps({'read_evidence': identity(ROOT / rel)}, sort_keys=True))


if __name__ == '__main__':
    main()
