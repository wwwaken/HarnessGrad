"""Preserve exact executed evidence commands and raw final validation output."""
import json
import shlex
import subprocess
import tempfile
from common import HERE, ROOT, digest

# Manifest excludes only itself and ignored interpreter bytecode, never raw failed attempts.
entries = []
for path in sorted(HERE.rglob('*')):
    if path.is_file() and '__pycache__' not in path.parts and path.name != 'SHA256SUMS':
        entries.append(f'{digest(path)}  {path.relative_to(ROOT)}\n')
(HERE / 'SHA256SUMS').write_text(''.join(entries))
base = (HERE / 'baseline.stdout.txt').read_text().strip()
report = ROOT / 'reports/w-mkl2-validation.txt'
with report.open('w') as output:
    output.write('w-mkl2 raw command and validation evidence\nBaseline: ' + base + '\n')
    output.write('No benchmark/scorer/model/GPU/endpoint execution. Package imports and source/metadata checks only.\n')
    output.write('Earlier failures are preserved; successful final imports are offline/retry-completed-imports and offline/exact-named-imports.\n')
    for path in sorted(HERE.rglob('*.receipt.json')):
        record = json.loads(path.read_text())
        if 'command' not in record:
            continue
        output.write('\nreceipt: ' + str(path.relative_to(ROOT)) + '\n$ ' + shlex.join(record['command']) + '\n')
        output.write('recorded exit_code: ' + str(record['exit_code']) + '\n')
        stem = path.name.removesuffix('.receipt.json')
        for suffix in ['stdout.txt', 'stderr.txt']:
            raw = path.with_name(stem + '.' + suffix)
            if raw.exists():
                output.write('raw ' + suffix + ': ' + str(raw.relative_to(ROOT)) + '\n')
    temp = tempfile.mkdtemp(prefix='harnessgrad-pytest-w-mkl2-')
    commands = [
        ['python3', 'tests/fixtures/hg_wmkl2/validate.py'],
        ['sha256sum', '--check', 'tests/fixtures/hg_wmkl2/SHA256SUMS'],
        ['sha256sum', '--check', 'tests/fixtures/hg_wmkl2/EXTERNAL_SHA256SUMS'],
        ['python3', 'tests/fixtures/hg_wmkl2/review_scope.py'],
        ['python3', 'tools/check_dataset_blockers.py'],
        ['python3', '-m', 'pytest', 'tests/quality/test_dataset_blockers.py', '-q', '--basetemp=' + temp],
        ['git', 'diff', '--cached', '--check', '--', 'docs/dataset-blockers.json',
         'docs/adapter-integration-journal.md', 'reports/w-mkl2-ds1000.md',
         'tests/fixtures/hg_wmkl2/*.py', 'tests/fixtures/hg_wmkl2/*.lock',
         'tests/fixtures/hg_wmkl2/README.md'],
    ]
    for command in commands:
        output.write('\n$ ' + shlex.join(command) + '\n')
        output.flush()
        p = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=240)
        output.write(p.stdout + p.stderr + 'exit_code: ' + str(p.returncode) + '\n')
        output.flush()
        assert p.returncode == 0, (command, p.returncode)
print(str(report))
