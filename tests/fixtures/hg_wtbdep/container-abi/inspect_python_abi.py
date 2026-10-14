"""Static ELF/stdlib inspection of already saved images; never runs an image executable."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile

OUT=Path(__file__).resolve().parent
records=[]
with tarfile.open(sys.argv[1]) as archive:
    manifest=json.load(archive.extractfile('manifest.json'))
    for image in manifest:
        label=image['RepoTags'][0].split('/')[1].split(':')[0].replace('-','_')
        selected={}
        for layer in image['Layers']:
            with tarfile.open(fileobj=archive.extractfile(layer)) as members:
                for member in members:
                    name=member.name.lstrip('./')
                    if not member.isfile():continue
                    wanted=(re.fullmatch(r'usr/local/lib/python3\.\d+/(hashlib|ssl)\.py',name)
                            or re.fullmatch(r'usr/local/bin/python3\.\d+',name)
                            or re.fullmatch(r'usr/local/lib/libpython3\.\d+\.so\.1\.0',name)
                            or re.fullmatch(r'usr/local/lib/python3\.\d+/lib-dynload/_(hashlib|ssl|sqlite3)\..*\.so',name))
                    if wanted:selected[name]=members.extractfile(member).read()
        for name,raw in sorted(selected.items()):
            row={'image':image['RepoTags'][0], 'image_config':image['Config'], 'path':name,
                 'sha256':hashlib.sha256(raw).hexdigest()}
            dest=OUT/label/(Path(name).name+'.txt');dest.parent.mkdir(parents=True,exist_ok=True)
            if name.endswith('.py'):dest.write_bytes(raw)
            else:
                with tempfile.NamedTemporaryFile() as f:
                    f.write(raw);f.flush()
                    r=subprocess.run(['readelf','-d',f.name],capture_output=True,text=True)
                    dest.write_text(r.stdout+r.stderr)
                    row.update({'command':['readelf','-d','<saved member '+name+'>'],'returncode':r.returncode})
            row['fixture']=str(dest.relative_to(OUT.parent))
            records.append(row)
(OUT/'custody.json').write_text(json.dumps({'command':'python3 tests/fixtures/hg_wtbdep/container-abi/inspect_python_abi.py /tmp/hg-wtbdep-runtime-images.tar','members':records},indent=2)+'\n')
print('Preserved static Python ABI/source observations:',len(records),'members')
