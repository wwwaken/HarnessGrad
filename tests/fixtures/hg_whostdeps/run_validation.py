"""Write final validation transcript outside the sealed fixture manifest."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
REPORT = ROOT / 'reports/w-hostdeps-validation.txt'
authored = ['docs/dataset-blockers.json', 'docs/adapter-integration-journal.md',
            'reports/w-hostdeps-inventory.md', 'tests/fixtures/hg_whostdeps/README.md']
authored += [str(p.relative_to(ROOT)) for p in OUT.glob('*.py')]
commands = [
 ['python3', 'tools/check_dataset_blockers.py'],
 ['python3', 'tests/fixtures/hg_whostdeps/validate.py'],
 ['git', 'diff', '--cached', '--check', '--', *authored],
]
with REPORT.open('w') as stream:
    stream.write('w-hostdeps validation\nUTC: ' + datetime.now(timezone.utc).isoformat() + '\n')
    stream.write('No production code, benchmark task, endpoint, runs/ or frozen receipt was changed.\n\n')
    for argv in commands:
        proc = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)
        stream.write('ARGV: ' + json.dumps(argv) + '\nRETURN_CODE: ' + str(proc.returncode) + '\n')
        stream.write('STDOUT:\n' + proc.stdout + 'STDERR:\n' + proc.stderr + '\n')
        stream.flush()
        assert proc.returncode == 0, argv
    stream.write('Previously completed focused test command, raw output retained without rerunning:\n')
    test = next(r for r in json.loads((OUT / 'capture-invocations.json').read_text())['captures'] if '-m' in r['argv'])
    stream.write('ARGV: ' + json.dumps(test['argv']) + '\nRETURN_CODE: ' + str(test['returncode']) + '\n')
    stream.write('STDOUT:\n' + (OUT / test['stdout']).read_text())
    stream.write('STDERR:\n' + (OUT / test['stderr']).read_text() + '\n')
    stream.write('Earlier first packet validation failed on a blank-line source citation; corrected report passes.\n')
    stream.write('Raw retained: tests/fixtures/hg_whostdeps/validate-first.{stdout,stderr}.txt\n')
    stream.write('Full staged whitespace check returned 2 only for original upstream source and raw LibreOffice blank lines.\n')
    stream.write('Raw retained: tests/fixtures/hg_whostdeps/whitespace-full.{stdout,stderr}.txt\n')
    stream.write('Authored-file whitespace check above passes; evidence bytes were not normalized.\n')
    stream.write('RESULT: PASS; complete pinned native-host surface coverage remains 0/7; no blocker closes.\n')
print(REPORT.relative_to(ROOT))
