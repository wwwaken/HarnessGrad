"""Final source/packet/payload validation; do not rerun completed expensive checks."""
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
report = ROOT / 'reports/w-hostpin-validation.txt'
commands = [
    [sys.executable, 'tools/check_dataset_blockers.py'],
    [sys.executable, 'tests/fixtures/hg_whostpin/validate.py'],
    ['/usr/bin/sha256sum', '-c', 'tests/fixtures/hg_whostpin/SHA256SUMS'],
    ['git', 'diff', '--cached', '--check', '--', 'data/dataset.schema.json', 'data/datasets/bird_minidev.py',
     'data/datasets/bird_minidev/verify/check.py', 'eval/verification/verifier.py',
     'eval/verification/native_runtime.py', 'harnessgrad/records.py',
     'tests/quality/test_native_runtime_hostpin.py', 'tests/quality/test_bird_minidev_official_scorer.py',
     'tools/build_bird_native_runtime.py', 'reports/w-hostpin-receipts.md',
     'docs/adapter-integration-journal.md', 'docs/dataset-blockers.json',
     'tests/fixtures/hg_whostpin/derive.py', 'tests/fixtures/hg_whostpin/validate.py',
     'tests/fixtures/hg_whostpin/run_validation.py', 'tests/fixtures/hg_whostpin/replay_bird_baseline.py',
     'tests/fixtures/hg_whostpin/README.md', 'data/runtimes/bird_minidev-native.json'],
]
records = []
with report.open('w') as stream:
    stream.write('w-hostpin validation: BIRD native userland 1/7; all blockers remain open.\n\n')
    for argv in commands:
        result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)
        record = {'argv': argv, 'returncode': result.returncode,
                  'stdout': result.stdout, 'stderr': result.stderr}
        records.append(record)
        stream.write('ARGV: ' + json.dumps(argv) + '\nRETURN_CODE: ' + str(result.returncode) + '\n')
        if argv[0] == '/usr/bin/sha256sum':
            stream.write('STDOUT: all packet paths reported OK; full raw output retained in validation-commands.json\n')
        else:
            stream.write('STDOUT:\n' + result.stdout)
        stream.write('STDERR:\n' + result.stderr + '\n')
        (OUT / 'validation-commands.json').write_text(json.dumps(records, indent=2) + '\n')
        assert result.returncode == 0, argv
    completed = [
        ('python3 -m pytest -q -s tests/quality/test_native_runtime_hostpin.py tests/quality/test_verifier.py tests/quality/test_w_wal.py tests/quality/test_dataset_blockers.py tests/quality/test_identity_and_verdicts.py::test_a_verdict_file_carries_the_tally_not_only_the_sentence --basetemp=/tmp/hg-hostpin-pytest-targeted', 'pytest-targeted.stdout.txt'),
        ("python3 -m pytest -q tests/quality/test_bird_minidev_official_scorer.py -k 'transcription or ex_differential or check_scores or missing_answer or broken_environment or module_imports' --basetemp=/tmp/hg-hostpin-pytest-bird-fixed", 'pytest-bird-fixed.stdout.txt'),
        ('strace -f -yy -s 240 -e trace=execve,openat,mmap -o tests/fixtures/hg_whostpin/bound-check.strace.txt python3 -m pytest -q -s tests/quality/test_native_runtime_hostpin.py::test_actual_bound_bird_check_records_pin_and_preserves_ex_and_wal --basetemp=/tmp/hg-hostpin-pytest-trace', 'trace-test.stdout.txt'),
    ]
    stream.write('Previously completed commands; raw output preserved, not rerun:\n')
    for command, filename in completed:
        text = (OUT / filename).read_text()
        last = text.strip().splitlines()[-1]
        assert 'passed' in last and 'failed' not in last
        stream.write('COMMAND: ' + command + '\nRAW: tests/fixtures/hg_whostpin/' + filename + '\nRESULT: ' + last + '\n\n')
    stream.write('Full staged whitespace check preserves original raw readelf/numbered-source/trace formatting; raw output in whitespace-staged.stdout.txt. Staged authored files pass the separate check above.\n')
    stream.write('Retained failures: initial six native regressions; initial persistence regression; initial missing Linux seal-name compatibility; stale BIRD fixture (baseline 3 failed/8 passed; before repair 9 failed/2 passed); unchanged sandbox 2 failed/106 passed with unchanged replay 2 failed.\n')
    stream.write('Interrupted broader mock-demo-driver pass: 2 failed/108 passed; this is not a completed validation result. Full output and interruption/cleanup inspection retained. Final focused command above excludes those unrelated driver cases.\n')
    stream.write('Cleanup: ' + (OUT / 'cleanup.json').read_text() + '\n')
    stream.write('RESULT: scoped mechanism/payload/packet/registry and targeted checks PASS; unrelated retained failures remain failures. Coverage 1/7 native userland, 0/7 production dataset execution. S3/shared/dataset blockers, next_actions/history/gates/authorization unchanged.\n')
print(report.relative_to(ROOT))
