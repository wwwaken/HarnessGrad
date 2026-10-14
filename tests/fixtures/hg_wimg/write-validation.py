"""Write a review log from offline checks and existing immutable command receipts."""
from pathlib import Path
import json
import shlex
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
lines=['w-img validation: local image/ABI inspection only; no benchmark/model/GPU/endpoint calls.',
       'Source baseline: '+(HERE/'capture/baseline/git-head.stdout.txt').read_text().strip(), '',
       'Collection/derivation commands (already executed; do not rerun into frozen receipt directories):']
for program,meaning in [
    ('collect.py','94 configured refs, 91 local, 3 missing; CAPTURE COMPLETE'),
    ('supplement.py','86 present Terminal-Bench images: installed tools/providers; SUPPLEMENT COMPLETE'),
    ('native-supplement.py','16 bases: static native-package inspection, no ML imports; NATIVE SUPPLEMENT COMPLETE'),
    ('summarize.py','94 derived rows; 101 rehashed manifest blobs; 60 TB Python + 26 shell-only records')]:
    lines+=['$ python3 tests/fixtures/hg_wimg/'+program,'exit=0; '+meaning]
lines+=['', 'Manifest generation (executed after final fixture edits):',
        '$ python3 - <<\'PY\'', 'from pathlib import Path', 'import hashlib',
        "r=Path('tests/fixtures/hg_wimg'); m=r/'SHA256SUMS'",
        "m.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(r))+'\\n' for p in sorted(r.rglob('*')) if p.is_file() and p!=m))",
        'PY', 'exit=0', '', 'Fresh focused checks:']
authored=['docs/dataset-blockers.json','docs/adapter-integration-journal.md',
          'reports/w-img-abi-custody.md','reports/w-img-validation.txt']
authored += [str(p.relative_to(ROOT)) for p in sorted(HERE.glob('*.py'))]
authored += [str(p.relative_to(ROOT)) for p in sorted(HERE.glob('*.sh'))]
checks=[(['python3','tests/fixtures/hg_wimg/validate.py'],ROOT),
        (['python3','tools/check_dataset_blockers.py'],ROOT),
        (['sha256sum','--check','--quiet','SHA256SUMS'],HERE),
        (['git','diff','--cached','--check','--',*authored],ROOT)]
for argv,cwd in checks:
    proc=subprocess.run(argv,cwd=cwd,capture_output=True,text=True)
    lines+=['$ '+shlex.join(argv)+(' [cwd=tests/fixtures/hg_wimg]' if cwd==HERE else ''),
            'exit='+str(proc.returncode),proc.stdout.rstrip(),proc.stderr.rstrip()]
    assert proc.returncode==0,(argv,proc.stdout,proc.stderr)
lines+=['', 'Review limits:',
        'Raw acquired stdout/stderr retain original whitespace and are not normalized for git whitespace checks.',
        'Missing images (3) and python3-absent import probes (26, exit 127) are explicit findings, not passed scorers.',
        'The direct containerd socket refusal and separate successful read-only local content-store read are retained.',
        'No registry request, image pull/build, package install, benchmark, model, GPU or endpoint call occurred.',
        'All 194 disposable inspection containers have removal receipts; all three owned-name queries are empty.',
        'The native supplement records standalone ldd unresolved SONAMEs without asserting failed imports or image absence.',
        'No complete offline closure, post-bootstrap/snapshot ABI or trusted production lifecycle evidence is certified.',
        'Blocker status/next_action unchanged; production_authorized=false.', '',
        'Exact nested inspection commands from the retained command receipts:',
        '(Each key has original stdout/stderr beside it; return code is inspection acquisition status, not a task score.)']
commands=sorted(HERE.rglob('*.command.json'))
for path in commands:
    value=json.loads(path.read_text())
    lines+=['',str(path.relative_to(ROOT)),'$ '+shlex.join(value['argv']),'exit='+str(value['returncode'])]
(ROOT/'reports/w-img-validation.txt').write_text('\n'.join(lines)+'\n')
print('Validation written; nested inspection commands:',len(commands))
