"""Write exact final validation commands/results after parent scorer replay."""
from pathlib import Path
import shlex
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
report=ROOT/'reports/w-offscorer-validation.txt'
replay=Path('/tmp/hg-offscorer-replay.txt').read_text()
assert '\0' not in replay
with report.open('w') as log:
    log.write('w-offscorer parent validation; cwd=/tmp/hg-offscorer; baseline=fdfdbce\n')
    log.write('Public-source acquisition commands/receipts remain in component directories; not repeated.\n')
    log.write('Parent reviewed isolated-worktree commits b243de5, 28dee6c, dd43fd7 and c795945 before integration.\n')
    log.write('\n$ PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/hg_woffscorer/replay.py\n')
    log.write(replay)
    commands=[
       ['env','PYTHONDONTWRITEBYTECODE=1','python3','tests/fixtures/hg_woffscorer/build_report.py'],
       ['env','PYTHONDONTWRITEBYTECODE=1','python3','tests/fixtures/hg_woffscorer/refresh_manifest.py'],
       ['env','PYTHONDONTWRITEBYTECODE=1','python3','tests/fixtures/hg_woffscorer/bigbench/verify.py'],
       ['env','PYTHONDONTWRITEBYTECODE=1','python3','tests/fixtures/hg_woffscorer/numeric_boolean/validate.py'],
       ['env','PYTHONDONTWRITEBYTECODE=1','python3','tests/fixtures/hg_woffscorer/public_qa/verify.py'],
       ['python3','tools/check_dataset_blockers.py'],
       ['env','PYTHONDONTWRITEBYTECODE=1','python3','tests/fixtures/hg_woffscorer/verify.py'],
       ['env','PYTHONDONTWRITEBYTECODE=1','python3','-m','pytest','-q','tests/quality/test_dataset_blockers.py',
        '--basetemp=/tmp/harnessgrad-pytest-w-offscorer'],
       ['git','diff','--check','fdfdbce','--','.',
        ':(exclude)tests/fixtures/hg_woffscorer/public_qa/source/**',
        ':(exclude)tests/fixtures/hg_woffscorer/numeric_boolean/source/**',
        ':(exclude)tests/fixtures/hg_woffscorer/public_qa/validation.txt',
        ':(exclude)tests/fixtures/hg_woffscorer/initial-parent-validation.txt',
        ':(exclude)reports/w-offscorer-validation.txt'],
    ]
    for cmd in commands:
        log.write('\n$ '+shlex.join(cmd)+'\n');log.flush()
        result=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        log.write(f'exit_code={result.returncode}\n');log.flush()
        assert result.returncode==0,cmd
    log.write('\nPinned unmodified upstream source whitespace and raw diagnostic copies of it are preserved; the complete check follows.\n')
    cmd=['git','diff','--check','fdfdbce']
    log.write('$ '+shlex.join(cmd)+'\n');log.flush()
    result=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    log.write(f'exit_code={result.returncode}; preserved upstream source whitespace and raw diagnostics\n')
print(f'PASS: exact commands and raw validation results in {report.relative_to(ROOT)}')
