"""Record the exact verification commands and their raw output for parent review."""
import hashlib
import json
import pathlib
import shlex
import subprocess

HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[2]
commands=[['python3','tests/fixtures/hg_wwheelhouse/validate.py'],
          ['python3','tests/fixtures/hg_wwheelhouse/review_scope.py'],
          ['python3','tools/check_dataset_blockers.py'],['git','diff','--cached','--check']]
parts=['w-wheelhouse validation; cwd=/tmp/hg-wheelhouse\n',
'''Acquisition/build/install commands actually executed earlier (raw output retained at these paths):
python3 tests/fixtures/hg_wwheelhouse/audit.py > tests/fixtures/hg_wwheelhouse/audit-summary.txt 2> tests/fixtures/hg_wwheelhouse/audit-stderr.txt
python3 tests/fixtures/hg_wwheelhouse/obtain.py > tests/fixtures/hg_wwheelhouse/obtain.stdout.txt 2> tests/fixtures/hg_wwheelhouse/obtain.stderr.txt
python3 tests/fixtures/hg_wwheelhouse/supplement.py > tests/fixtures/hg_wwheelhouse/supplement.stdout.txt 2> tests/fixtures/hg_wwheelhouse/supplement.stderr.txt
unshare -Urn python3 tests/fixtures/hg_wwheelhouse/offline.py build > tests/fixtures/hg_wwheelhouse/build.stdout.txt 2> tests/fixtures/hg_wwheelhouse/build.stderr.txt
unshare -Urn python3 tests/fixtures/hg_wwheelhouse/offline.py build-retry > tests/fixtures/hg_wwheelhouse/build-retry.stdout.txt 2> tests/fixtures/hg_wwheelhouse/build-retry.stderr.txt
unshare -Urn python3 tests/fixtures/hg_wwheelhouse/offline.py install > tests/fixtures/hg_wwheelhouse/install.stdout.txt 2> tests/fixtures/hg_wwheelhouse/install.stderr.txt
python3 tests/fixtures/hg_wwheelhouse/native_providers.py > tests/fixtures/hg_wwheelhouse/native-providers.stdout.txt 2> tests/fixtures/hg_wwheelhouse/native-providers.stderr.txt
python3 tests/fixtures/hg_wwheelhouse/retry_downloads.py > tests/fixtures/hg_wwheelhouse/retry-downloads.stdout.txt 2> tests/fixtures/hg_wwheelhouse/retry-downloads.stderr.txt
unshare -Urn python3 tests/fixtures/hg_wwheelhouse/torch_retry.py > tests/fixtures/hg_wwheelhouse/torch-retry.stdout.txt 2> tests/fixtures/hg_wwheelhouse/torch-retry.stderr.txt
python3 tests/fixtures/hg_wwheelhouse/refine_witnesses.py > tests/fixtures/hg_wwheelhouse/refined-witnesses.txt
python3 tests/fixtures/hg_wwheelhouse/coverage.py > tests/fixtures/hg_wwheelhouse/coverage-summary.txt
python3 tests/fixtures/hg_wwheelhouse/render_report.py

Inner pip/wheel/import/check command arrays, exit codes and unedited stdout/stderr: tests/fixtures/hg_wwheelhouse/offline/.
Independent full sha256sum command and its raw output: tests/fixtures/hg_wwheelhouse/sha256sum.command.json and sha256sum.payloads.txt.
The initial obtain attempt failed on an absent build-tool metadata lookup before any transfer; preserved in obtain-first-attempt.stderr.txt. Three native-provider truncated transfers and initial source-build/import failures remain retained and excluded from successful artifact claims.

Fresh final checks (command, raw stdout/stderr, exit code):
''']
for cmd in commands:
    p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
    parts+=['$ '+shlex.join(cmd)+'\n',p.stdout,p.stderr,f'exit_code={p.returncode}\n\n']
    print(shlex.join(cmd),'exit_code',p.returncode,flush=True)
    if p.returncode:
        (ROOT/'reports/w-wheelhouse-validation.txt').write_text(''.join(parts).rstrip()+'\n');raise SystemExit(p.returncode)
(ROOT/'reports/w-wheelhouse-validation.txt').write_text(''.join(parts).rstrip()+'\n')
# Hash all committed evidence candidates, excluding this self-referential sums file and bytecode.
paths=sorted(p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='SHA256SUMS.evidence')
(HERE/'SHA256SUMS.evidence').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(ROOT))+'\n' for p in paths))
print('evidence files hashed',len(paths))
