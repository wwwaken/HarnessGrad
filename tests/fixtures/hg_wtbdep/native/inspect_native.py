"""Read-only native dependency inspection; never instantiates a benchmark environment."""
import ast
import hashlib
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import sysconfig
from packaging.requirements import Requirement

OUT = Path(__file__).resolve().parent
SITE = Path(sysconfig.get_path('purelib'))
ROOT = OUT.parents[3]

def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

save('host.json', {'command': 'python3 tests/fixtures/hg_wtbdep/native/inspect_native.py',
 'executable': sys.executable, 'version': sys.version, 'SOABI': sysconfig.get_config_var('SOABI'),
 'platform': platform.platform(), 'site_packages': str(SITE),
 'which': {x: shutil.which(x) for x in ['python3','java','soffice','libreoffice','ldd','readelf','gcc']}})

# Distribution declarations, recursively following default requirements plus the TextWorld PDDL extra.
queue = ['alfworld','textworld','scienceworld','py4j','openpyxl','lxml','defusedxml','Pillow']
seen = set(); rows = []
while queue:
    name = queue.pop(0)
    key = name.lower().replace('_','-')
    if key in seen: continue
    seen.add(key)
    try:
        dist = metadata.distribution(name)
    except metadata.PackageNotFoundError:
        rows.append({'name': name, 'installed': False}); continue
    deps = []
    for raw in dist.requires or []:
        req = Requirement(raw)
        active = req.marker is None or req.marker.evaluate({'extra': ''})
        if key == 'textworld': active = active or req.marker.evaluate({'extra': 'pddl'}) if req.marker else True
        deps.append({'requirement': raw, 'active_default_or_textworld_pddl': active})
        if active: queue.append(req.name)
    rows.append({'name': dist.metadata['Name'], 'version': dist.version,
        'location': str(dist.locate_file('')), 'requirements': deps})
save('distribution-closure.json', rows)

# Copy only source needed to expose transitive imports/native loading and optional imports.
rels = ['alfworld/__init__.py','alfworld/agents/environment/__init__.py',
 'alfworld/agents/environment/alfred_tw_env.py','alfworld/agents/utils/misc.py',
 'alfworld/agents/expert/__init__.py','alfworld/agents/expert/handcoded_expert.py',
 'alfworld/agents/expert/handcoded_expert_tw.py','alfworld/agents/expert/handcoded_expert_thor.py',
 'textworld/__init__.py','textworld/utils.py','textworld/helpers.py','textworld/generator/__init__.py',
 'textworld/generator/inform7/world2inform7.py','textworld/envs/__init__.py','textworld/envs/pddl/pddl.py',
 'textworld/envs/pddl/logic.py','textworld/envs/zmachine/jericho.py','textworld/gym/__init__.py',
 'textworld/gym/utils.py','textworld/gym/envs/textworld_batch.py',
 'fast_downward/__init__.py','fast_downward/interface.py',
 'scienceworld/__init__.py','scienceworld/constants.py','scienceworld/scienceworld.py',
 'scienceworld/utils.py','py4j/java_gateway.py',
 'openpyxl/__init__.py','openpyxl/compat/numbers.py','openpyxl/xml/__init__.py',
 'openpyxl/xml/functions.py','openpyxl/drawing/image.py','openpyxl/reader/excel.py']
sources=[]
for rel in rels:
    path=SITE/rel
    if not path.is_file(): sources.append({'path': str(path), 'exists': False}); continue
    raw=path.read_bytes(); dest=OUT/'sources'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
    sources.append({'path': str(path), 'fixture': str(dest.relative_to(ROOT)), 'sha256': hashlib.sha256(raw).hexdigest()})
save('source-custody.json',sources)

# Importing package modules is inspection, not replay/scoring. Run fresh child interpreters, never constructors.
for name in ['textworld.gym','alfworld.agents.environment.alfred_tw_env','scienceworld','openpyxl']:
    code = '''import importlib,json,sys,traceback
before=set(sys.modules)
try:
 importlib.import_module(%r)
 status='imported'
except Exception:
 status=traceback.format_exc()
print(json.dumps({'requested':%r,'status':status,'modules':{k:getattr(v,'__file__',None) for k,v in sorted(sys.modules.items()) if k not in before}},indent=2,sort_keys=True))
''' % (name,name)
    proc=subprocess.run([sys.executable,'-c',code],capture_output=True,text=True,timeout=60)
    (OUT/('import-'+name+'.json')).write_text(proc.stdout)
    (OUT/('import-'+name+'.stderr.txt')).write_text(proc.stderr)

# Read-only version/dependency observations; no Java environment or workbook is loaded.
commands = [['ldd','--version'], ['soffice','--version'],
 ['dpkg-query','-W','libreoffice-core','libreoffice-calc','libc6','libstdc++6']]
java=Path('/mnt/20t/xubuqiang/datasets/scienceworld/jre/jdk-17.0.20.1+1-jre/bin/java')
if java.is_file(): commands += [[str(java),'-version'],['ldd',str(java)]]
for label,path in [('fast_downward', SITE/'fast_downward'),('scienceworld', SITE/'scienceworld')]:
    for f in sorted(path.rglob('*.so')):
        commands.append(['ldd',str(f)])
for f in [Path('/usr/lib/libreoffice/program/soffice.bin'),Path('/usr/lib/libreoffice/program/libscfiltlo.so')]:
    if f.is_file(): commands.append(['ldd',str(f)])
results=[]
for cmd in commands:
    try:
        proc=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
        results.append({'command':cmd,'returncode':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr})
    except (OSError,subprocess.TimeoutExpired) as e: results.append({'command':cmd,'error':str(e)})
save('binary-inspection.json', results)

# Imported native extensions plus the JVM's dynamically loaded libraries expose ABI, not a closure proof.
package_map = metadata.packages_distributions()
import_summary = []
native_files=set()
for name in ['textworld.gym','alfworld.agents.environment.alfred_tw_env','scienceworld','openpyxl']:
    record=json.loads((OUT/('import-'+name+'.json')).read_text())
    roots={x.split('.')[0] for x,path in record['modules'].items() if path and str(path).startswith(str(SITE) + os.sep)}
    packages={dist for root in roots for dist in package_map.get(root,[])}
    import_summary.append({'requested':name, 'status':record['status'],
       'distributions':{n:metadata.version(n) for n in sorted(packages)}})
    for path in record['modules'].values():
        if path and path.endswith('.so') and Path(path).is_file():native_files.add(path)
if java.is_file():
    native_files.update(str(f) for f in java.parent.parent.rglob('*.so'))
elf=[]
for path in sorted(native_files):
    raw=Path(path).read_bytes()
    proc=subprocess.run(['ldd',path],capture_output=True,text=True,timeout=30)
    elf.append({'path':path,'sha256':hashlib.sha256(raw).hexdigest(), 'command':['ldd',path],
                'returncode':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr})
save('import-summary.json',import_summary)
save('import-and-jvm-elf.json',elf)

import zipfile
jar=SITE/'scienceworld/scienceworld.jar'
with zipfile.ZipFile(jar) as z:
    names=z.namelist()
    save('scienceworld-jar.json',{'path':str(jar),'sha256':hashlib.sha256(jar.read_bytes()).hexdigest(),
       'entries':names, 'metadata': {n:z.read(n).decode('utf-8','replace') for n in names
          if n.endswith(('pom.properties','MANIFEST.MF'))}})
for rel in ['textworld/envs/pddl/logic/__init__.py','textworld/envs/pddl/logic/model.py',
 'jericho/jericho.py','jericho/__init__.py']:
    f=SITE/rel
    if f.is_file():
        dest=OUT/'sources'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(f.read_bytes())
# Recompute custody after supplementary copied files, preserving raw bytes and original line numbers.
save('source-custody.json',[{'path':str(SITE/f.relative_to(OUT/'sources')),
 'fixture':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
 for f in sorted((OUT/'sources').rglob('*')) if f.is_file()])
