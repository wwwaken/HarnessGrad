"""Run bounded read-only packet, registry and existing focused checks."""
import hashlib,pathlib,shlex,subprocess,sys
repo=pathlib.Path(__file__).resolve().parents[2];packet=repo/'reports/w-tb89-evidence'
files=sorted(p for p in packet.rglob('*') if p.is_file() and p.name!='SHA256SUMS' and '__pycache__' not in p.parts)
(packet/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(packet))+'\n' for p in files))
commands=[['python3','reports/w-tb89-evidence/verify.py'],['python3','tools/check_dataset_blockers.py'],['python3','-m','pytest','-q','tests/quality/test_dataset_blockers.py','tests/quality/test_dataset_journal_coverage.py','tests/quality/test_diagnostic_policy.py','tests/quality/test_unobserved_diagnostic_c2.py','--basetemp=/tmp/harnessgrad-pytest-w-tb89'],['git','diff','--check']]
with (repo/'reports/w-tb89-validation.txt').open('x') as f:
    f.write('w-tb89 focused validation; raw commands/output; no model or task execution\n')
    for argv in commands:
        f.write('\n$ '+shlex.join(argv)+'\n');f.flush()
        p=subprocess.run(argv,cwd=repo,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        f.write('stdout:\n'+p.stdout+'stderr:\n'+p.stderr+'\nreturncode: '+str(p.returncode)+'\n');f.flush()
        print(shlex.join(argv)+': '+str(p.returncode),flush=True)
        if p.returncode:sys.exit(p.returncode)
