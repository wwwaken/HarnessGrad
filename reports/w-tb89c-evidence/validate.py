"""Preserve final focused validation commands and raw outputs."""
import datetime, hashlib, pathlib, shlex, subprocess
repo=pathlib.Path(__file__).resolve().parents[2]; packet=repo/'reports/w-tb89c-evidence'
with (repo/'reports/w-tb89c-validation.txt').open('x') as out:
    out.write('w-tb89c validation — '+datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n')
    out.write('Exact commands and raw outputs. No gate/runtime/task/test changes.\n\n')
    def run(argv):
        out.write('$ '+shlex.join(argv)+'\n'); out.flush()
        r=subprocess.run(argv,cwd=repo,capture_output=True,text=True)
        out.write(r.stdout); out.write(r.stderr); out.write(f'\n[exit {r.returncode}]\n\n'); out.flush()
        assert r.returncode==0,argv
    run(['python3','tools/check_dataset_blockers.py'])
    run(['python3','reports/w-tb89c-evidence/verify.py'])
    run(['python3','-m','pytest','-q','tests/quality/test_dataset_blockers.py','--basetemp=/tmp/harnessgrad-pytest-w-tb89c-final'])
    run(['git','diff','--check'])
    files=[p for p in sorted(packet.rglob('*')) if p.is_file() and p.name!='SHA256SUMS' and '__pycache__' not in p.parts]
    files.append(repo/'reports/w-tb89c-receipts.md')
    (packet/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(repo))+'\n' for p in files))
    out.write(f'Generated SHA256SUMS from {len(files)} existing review/report files.\n\n')
    run(['sha256sum','--check','--quiet','reports/w-tb89c-evidence/SHA256SUMS'])
    run(['git','diff','--stat'])
print('Focused validation passed; raw outputs: reports/w-tb89c-validation.txt')
