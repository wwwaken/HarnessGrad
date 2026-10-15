"""Run exact read-only parent audits and focused source-only registry regressions."""
import json,os,shlex,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2]
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',CUDA_VISIBLE_DEVICES='')
commands=[
 ['python3','tests/fixtures/hg_woffscorer3/bfcl/verify.py'],
 ['python3','tests/fixtures/hg_woffscorer3/code_chess/verify.py'],
 ['python3','tests/fixtures/hg_woffscorer3/worlds/verify.py'],
 ['python3','tests/fixtures/hg_woffscorer3/gaia_tau/verify.py'],
 ['python3','tests/fixtures/hg_woffscorer3/verify.py'],
 ['python3','tools/check_dataset_blockers.py'],
 ['python3','-m','pytest','-q','tests/quality/test_dataset_blockers.py','--basetemp=/tmp/harnessgrad-pytest-woffscorer3'],
 ['git','diff','--exit-code','9f78bcd','--','data/datasets','data/scaffolds','eval','tools/check_dataset_blockers.py'],
 ['git','diff','9f78bcd','--check','--','.',':!tests/fixtures/hg_woffscorer3/bfcl/official-source/',':!tests/fixtures/hg_woffscorer3/gaia_tau/source/',':!tests/fixtures/hg_woffscorer3/worlds/source/',':!tests/fixtures/hg_woffscorer3/worlds/*inspection.txt'],
]
log=R/'reports/w-offscorer3-validation.txt'
with log.open('w') as f:
 f.write('Parent validation cwd: '+str(R)+'\nBaseline: 9f78bcd\nInvocation: PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/hg_woffscorer3/validate.py\nEnvironment: PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=\nNo scorers/worlds/models are replayed by validation.\n\n')
 for cmd in commands:
  f.write('$ '+shlex.join(cmd)+'\n');f.flush()
  result=subprocess.run(cmd,cwd=R,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=180)
  f.write(result.stdout+'exit_code='+str(result.returncode)+'\n\n');f.flush()
  if result.returncode:print(result.stdout);raise SystemExit(result.returncode)
 # Record expected verbatim upstream source whitespace separately from owned changes.
 cmd=['git','diff','9f78bcd','--check']
 f.write('$ '+shlex.join(cmd)+'\n');result=subprocess.run(cmd,cwd=R,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=30)
 f.write(json.dumps({'raw_stdout':result.stdout})+'\nexit_code='+str(result.returncode)+'\nOnly verbatim upstream source/inspection whitespace is excluded from the passing owned-change check above.\n')
 if result.returncode not in (0,2):raise SystemExit(result.returncode)
print('Parent packet validators, source scope, registry checker and focused tests passed; exact output: '+str(log))
