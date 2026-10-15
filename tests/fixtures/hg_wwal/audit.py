"""Read-only source/receipt audit, including inherited source-pin drift."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
print('IDENTITY')
for argv in (["git", "rev-parse", "HEAD"], ["git", "branch", "--show-current"],
             ["git", "worktree", "list"], ["git", "status", "--short"]):
    p = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True, check=True)
    print(json.dumps({'argv': argv, 'returncode': p.returncode}))
    print(p.stdout, end='')

spans = {
 'data/scaffolds/scorer_input.py': [(1, 123)],
 'data/datasets/bird_minidev.py': [(13, 18), (253, 269)],
 'data/datasets/bird_minidev/verify/check.py': [(89, 142)],
 'eval/admission/artifact_admission.py': [(326, 355), (369, 385), (405, 446)],
 'eval/observe/tracing.py': [(298, 339)],
 'eval/containers/container_state.py': [(179, 211)],
 'eval/containers/container.py': [(830, 870), (935, 970)],
 'eval/verification/verifier.py': [(301, 318), (416, 464), (560, 570)],
 'data/datasets/appworld.py': [(1, 19), (263, 286), (293, 320)],
 'data/datasets/appworld/verify/check.py': [(35, 60)],
 'eval/service/services.py': [(374, 407), (475, 509)],
 'tests/fixtures/hg_woffscorer3/worlds/source/appworld/apps/model_lib.py': [(261, 279), (286, 303), (2179, 2203)],
 'tests/fixtures/hg_woffscorer3/worlds/source/appworld/collections/models.py': [(59, 80)],
 'tests/fixtures/hg_woffscorer3/worlds/source/appworld/environment.py': [(225, 239)],
 'tests/fixtures/hg_woffscorer3/worlds/source/appworld/evaluator.py': [(478, 497)],
}
for rel, ranges in spans.items():
    raw = (ROOT / rel).read_bytes()
    print(f'\nSOURCE {rel} sha256={hashlib.sha256(raw).hexdigest()}')
    lines = raw.decode().splitlines()
    for start, end in ranges:
        for number in range(start, min(end, len(lines)) + 1):
            print(f'{rel}:{number}: {lines[number-1]}')

rel = 'data/scaffolds/scorer_input.py'
raw = subprocess.run(['git','show',f'HEAD:{rel}'], cwd=ROOT, capture_output=True, check=True).stdout
print(f'\nBASELINE {rel} sha256={hashlib.sha256(raw).hexdigest()}')
for n, line in enumerate(raw.decode().splitlines(), 1):
    print(f'HEAD:{rel}:{n}: {line}')

print('\nINHERITED E5 PIN DRIFT (HEAD and working bytes independently hashed)')
for name in ['evidence/source-pins.json', 'execution-source-pins.json']:
    pins = json.loads((ROOT / 'tests/fixtures/hg_we5' / name).read_text())
    for rel, expected in pins.items():
        work = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        head_raw = subprocess.run(['git','show',f'HEAD:{rel}'], cwd=ROOT, capture_output=True, check=True).stdout
        head = hashlib.sha256(head_raw).hexdigest()
        if work != expected or head != expected:
            print(json.dumps(dict(pin_file=name,path=rel,expected=expected,HEAD=head,working=work), sort_keys=True))

print('\nEXISTING E5 WAL OBSERVATIONS (read only)')
base = ROOT / 'tests/fixtures/hg_we5/evidence/sqlite-wal-dependency'
for path in [base / 'observations.json', base / 'pre/scorer-output/reward.txt',
             base / 'post-main-only/scorer-output/reward.txt', base / 'post-checkpointed/scorer-output/reward.txt']:
    raw = path.read_bytes()
    print(f'{path.relative_to(ROOT)} sha256={hashlib.sha256(raw).hexdigest()}')
    print(raw.decode())

print('\nFROZEN PATH DIFF CHECK')
argv = ['git','diff','--exit-code','HEAD','--','runs/','tests/fixtures/hg_we5/','reports/w-e5-equivalence.md','reports/w-e5-validation.txt']
p = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True)
print(json.dumps(dict(argv=argv,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr), sort_keys=True))
assert p.returncode == 0
