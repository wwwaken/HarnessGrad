"""Write exact recorded commands and run the bounded final checks into the report."""
import json
import pathlib
import shlex
import subprocess
import sys
from acquire import HERE

ROOT=HERE.parents[2]
report=ROOT/'reports/w-mkl-validation.txt'
with report.open('w') as out:
    out.write('w-mkl command and validation evidence\nBaseline: bf917b3b237e352ac46373fdba501d35004c7911\n')
    out.write('No scorer/task/model/GPU/endpoint operation is requested by these commands.\n\n')
    out.write('Acquisition/install/import commands actually executed (from immutable raw receipt arrays).\n')
    out.write('Initial failures are retained; final import receipts are retry-import-*.receipt.json.\n')
    for p in sorted(HERE.rglob('*.receipt.json')):
        r=json.loads(p.read_text())
        if 'command' not in r:continue
        out.write('\nreceipt: '+str(p.relative_to(ROOT))+'\n')
        out.write('$ '+shlex.join(r['command'])+'\n')
        out.write('recorded exit_code: '+str(r['exit_code'])+'\n')
        for key in ['bytes','sha256']:
            if key in r:out.write(key+': '+str(r[key])+'\n')
        stem=p.name.removesuffix('.receipt.json')
        for suffix in ['stdout.txt','stderr.txt']:
            raw=p.with_name(stem+'.'+suffix)
            if raw.exists():out.write('raw '+suffix+': '+str(raw.relative_to(ROOT))+'\n')
    out.write('\nNamespace launch commands executed:\n')
    out.write('$ unshare -Urn python3 tests/fixtures/hg_wmkl/offline.py\n')
    out.write('raw original: tests/fixtures/hg_wmkl/offline.{stdout,stderr}.txt (route-header assertion failed)\n')
    out.write('raw installation retry: tests/fixtures/hg_wmkl/offline-retry.{stdout,stderr}.txt (installs succeeded; probe lookup failed)\n')
    out.write('$ unshare -Urn python3 tests/fixtures/hg_wmkl/retry_imports.py\n')
    out.write('raw final: tests/fixtures/hg_wmkl/retry-imports.{stdout,stderr}.txt\n')
    out.write((HERE/'retry-imports.stdout.txt').read_text())
    out.write('\nFinal validation commands and unedited captured output follow.\n')
    commands=[
        ['python3','tests/fixtures/hg_wmkl/validate.py'],
        ['sha256sum','--check','tests/fixtures/hg_wmkl/SHA256SUMS'],
        ['python3','tests/fixtures/hg_wmkl/review_scope.py'],
        ['python3','tools/check_dataset_blockers.py'],
        ['python3','-m','pytest','tests/quality/test_dataset_blockers.py','-q','--basetemp=/tmp/harnessgrad-pytest-w-mkl-validation'],
        ['git','diff','--cached','--check','--','docs/dataset-blockers.json',
         'docs/adapter-integration-journal.md','reports/w-mkl-payloads.md',
         'tests/fixtures/hg_wmkl/*.py','tests/fixtures/hg_wmkl/*.lock','tests/fixtures/hg_wmkl/README.md'],
    ]
    for cmd in commands:
        out.write('\n$ '+shlex.join(cmd)+'\n');out.flush()
        p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=240)
        out.write(p.stdout);out.write(p.stderr);out.write('exit_code: '+str(p.returncode)+'\n');out.flush()
        assert p.returncode==0,(cmd,p.returncode)
print(str(report))
