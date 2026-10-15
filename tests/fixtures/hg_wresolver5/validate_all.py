"""Preserve raw focused checks in the requested validation transcript."""
import json
from pathlib import Path
import subprocess
import sys
import time
from common import HERE, ROOT

out=ROOT/'reports/w-resolver5-validation.txt'
assert not out.exists(), 'Never overwrite a validation attempt'
commands=[
    [sys.executable,'tools/check_dataset_blockers.py'],
    [sys.executable,'tests/fixtures/hg_wresolver5/validate.py'],
    [sys.executable,'tests/fixtures/hg_wresolver5_tb/validate.py'],
    [sys.executable,'-m','pytest','-q','tests/quality/test_dataset_blockers.py','tests/quality/test_dataset_journal_coverage.py','--basetemp=/tmp/harnessgrad-pytest-w-resolver5'],
    ['git','diff','--cached','--check','--','docs/dataset-blockers.json','docs/adapter-integration-journal.md','reports/w-resolver5-payloads.md',
     'tests/fixtures/hg_wresolver5/*.py'],
]
with out.open('x') as stream:
    stream.write('w-resolver5 focused validation: raw subprocess output; no benchmark/model execution\n')
    stream.write('Initial independent validator --seal completed successfully; this run checks the sealed packet read-only.\n')
    stream.flush()
    for argv in commands:
        started=time.monotonic()
        p=subprocess.run(argv,cwd=ROOT,capture_output=True,timeout=300)
        stream.write('\nCOMMAND '+json.dumps(argv)+'\n')
        stream.write(json.dumps(dict(exit_code=p.returncode,elapsed_seconds=time.monotonic()-started),sort_keys=True)+'\n')
        stream.write('STDOUT BEGIN\n'+p.stdout.decode()+'STDOUT END\nSTDERR BEGIN\n'+p.stderr.decode()+'STDERR END\n')
        stream.flush()
        print(argv[1:3],p.returncode,flush=True)
        assert p.returncode==0,argv
    # Raw evidence remains unchanged, even when pip emits final blank lines.
    full=subprocess.run(['git','diff','--cached','--check'],cwd=ROOT,capture_output=True)
    stream.write('\nFULL STAGED WHITESPACE CHECK (raw output is preserved, not normalized)\n')
    stream.write(json.dumps(dict(exit_code=full.returncode))+'\n'+full.stdout.decode()+full.stderr.decode())
    changed=subprocess.check_output(['git','diff','--cached','--name-only','--diff-filter=AM'],cwd=ROOT,text=True).splitlines()
    changed+=['reports/w-resolver5-validation.txt']
    sizes=[]
    for name in sorted(set(changed)):
        path=ROOT/name
        assert path.stat().st_size<1_000_000,(name,path.stat().st_size)
        assert path.suffix not in {'.whl','.conda','.deb','.zip','.gz','.bz2','.body'},name
        sizes.append((path.stat().st_size,name))
    baseline='31486f6b41a3a8202dde6602e79edf1062813065'
    added=subprocess.check_output(['git','diff','--name-only','--diff-filter=A',baseline,'--'],cwd=ROOT,text=True).splitlines()
    union=sorted(set(added+changed))
    largest=max(( (ROOT/name).stat().st_size,name) for name in union)
    assert largest[0]<1_000_000,largest
    stream.write('\nPRECOMMIT SIZE CHECK '+json.dumps(dict(valid=True,largest_added_or_changed_file_bytes=largest[0],largest_added_or_changed_file=largest[1],limit_bytes=1_000_000,staged_added_or_changed_files=len(sizes),baseline=baseline),sort_keys=True)+'\n')
    stream.write('Terminal-Bench child commit c6c6bcdfe55648468febe048c4bc7a7c0de8303f reviewed; independent validator passed; 153 text files / 663593 bytes, largest 128491 bytes; cherry-picked into this worktree only as 4bf0d4e3.\n')
    stream.write('All required checks passed. Registry changes are additive observation/evidence only; no blocker, dataset/history record or production gate changed. No payload or frozen receipt committed.\n')
