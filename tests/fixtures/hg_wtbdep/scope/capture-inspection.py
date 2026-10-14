import json,shutil,subprocess,hashlib,importlib.metadata
from pathlib import Path
base=Path('tests/fixtures/hg_wtbdep/scope')
site=Path('/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages')
d=importlib.metadata.distribution('reasoning-gym');shutil.copyfile(d._path/'METADATA',base/'reasoning-gym-METADATA.txt')
dsite=Path('/mnt/20t/xubuqiang/datasets/agentdojo/runtime/lib/python3.12/site-packages')
for rel in ['agent_pipeline/__init__.py','agent_pipeline/agent_pipeline.py','task_suite/load_suites.py','task_suite/task_suite.py','functions_runtime.py','attacks/base_attacks.py','default_suites/__init__.py']:
 p=dsite/'agentdojo'/rel
 if p.exists():
  out=base/'installed-source'/'agentdojo'/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,out)
shutil.copyfile(site/'arckit'/'data.py',base/'installed-source'/'arckit-data.py')
summaries=[];libs=set()
for filename in ['reasoning-gym-import-only.json','jericho-import-only.json','agentdojo-import-only.json']:
 obj=json.loads((base/filename).read_text())
 summaries.append(f"{filename}: inspection={obj['inspection']}; error={obj['error']}; Python={obj['python_version']}; executable={obj['executable']}; SOABI={obj['soabi']}")
 for name,data in sorted(obj['packages'].items()):summaries.append(f"{filename}: {name}=={data['version']}; Requires-Dist={data['requires_dist']}")
 native=[m for m in obj['modules'] if m['file'] and m['file'].endswith('.so')]
 for m in native:
  summaries.append(f"{filename}: loaded native module {m['module']}: {m['file']}")
  if any(k in m['module'] for k in ['_multiarray_umath','pycosat','pydantic_core','_rust','_cffi_backend','_path','_imaging','_openblas','_mkl']):libs.add(m['file'])
libs.add(str(site/'jericho'/'libfrotz.so'));libs.add('/mnt/8t/xubuqiang/anaconda3/bin/python3.12')
(base/'import-package-summary.txt').write_text('\n'.join(summaries)+'\n')
with (base/'native-needed-readelf.txt').open('w') as f:
 for lib in sorted(libs):
  path=Path(lib)
  f.write(f"FILE {lib}\nSHA256 {hashlib.sha256(path.read_bytes()).hexdigest()}\n")
  proc=subprocess.run(['readelf','-d',lib],capture_output=True,text=True)
  f.write(proc.stdout+proc.stderr)
  f.write('RETURN_CODE '+str(proc.returncode)+'\n')
