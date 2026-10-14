"""Static installed native-package inspection; never import ML/scientific packages."""
import hashlib
import importlib.metadata as md
import json
from pathlib import Path
import re
import subprocess

names={'numpy','scipy','torch','pandas','scikit-learn','pillow','matplotlib','torchvision','lxml','mujoco'}
patterns=re.compile(r'_multiarray_umath|_umath_linalg|_fblas|_flapack|_sparsetools|_nd_image|_imaging|ft2font|_path\.|/algos\.|_openmp_helpers|murmurhash|/torch/_C\.|/torch/lib/(libtorch_cpu|libtorch_python|libc10)\.so|/torchvision/_C\.|/lxml/etree\.|/mujoco/.*\.so')
result={'scope':'static ELF only; packages are not imported and no model/GPU/task code is invoked',
        'distribution_native_inventory':[],'objects':[]}
queue=[]
for d in md.distributions():
    name=d.metadata.get('Name','')
    if not name or name.lower() not in names:continue
    files=[]
    for f in d.files or []:
        if '.so' not in Path(str(f)).name:continue
        p=Path(d.locate_file(f))
        if not p.is_file():continue
        files.append({'path':str(p),'size':p.stat().st_size})
        if patterns.search(str(p)):queue.append(p)
    result['distribution_native_inventory'].append({'name':name,'version':d.version,'native_files':files})
seen=set()
while queue:
    p=queue.pop(0)
    if str(p.resolve()) in seen:continue
    seen.add(str(p.resolve()))
    try:
        with p.open('rb') as stream:
            if stream.read(4)!=b'\x7fELF':continue
            stream.seek(0);h=hashlib.sha256()
            for b in iter(lambda:stream.read(1024*1024),b''):h.update(b)
        rec={'path':str(p),'resolved':str(p.resolve()),'sha256':h.hexdigest(),'size':p.stat().st_size}
        for argv in [['ldd',str(p)]]:
            proc=subprocess.run(argv,capture_output=True,text=True,timeout=20)
            rec['ldd']={'argv':argv,'returncode':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr}
            rec['unresolved_sonames']=re.findall(r'^\s*(\S+)\s+=>\s+not found',proc.stdout,re.M)
            for path in re.findall(r'(/[^\s()]+)',proc.stdout):
                if Path(path).is_file():queue.append(Path(path))
        result['objects'].append(rec)
    except Exception as e:result['objects'].append({'path':str(p),'error':repr(e)})
print(json.dumps(result,indent=2,sort_keys=True))
