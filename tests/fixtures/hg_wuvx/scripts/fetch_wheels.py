#!/usr/bin/env python3
import sys,json,re,hashlib,pathlib,zipfile,tarfile
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from collect import ROOT,run
log=(ROOT/'raw/online.stderr.txt').read_text()
urls=sorted(set(re.findall(r'TRACE Sending fresh GET request for (https://files\.pythonhosted\.org/\S+\.whl)\s*',log)))
assert len(urls)==6,urls
rows=[]
for i,url in enumerate(urls):
 p=ROOT/'artifacts/wheels'/url.rsplit('/',1)[1]
 r=run(f'wheel-{i+1}',['curl','--proxy','http://172.17.0.1:17890','-fLsS','--max-time','120','-D',str(ROOT/'raw'/f'wheel-{i+1}.headers.txt'),url,'-o',str(p)],150)
 assert r.returncode==0
 with zipfile.ZipFile(p) as z:
  metadata={n:{'sha256':hashlib.sha256(z.read(n)).hexdigest(),'text':z.read(n).decode()} for n in z.namelist() if n.endswith(('/METADATA','/WHEEL'))}
 rows.append({'url':url,'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size,'metadata':metadata})
(ROOT/'artifacts/wheels.json').write_text(json.dumps(rows,indent=2)+'\n')
pins=[]
for r in rows:
 m=next(x['text'] for k,x in r['metadata'].items() if k.endswith('/METADATA'))
 name=re.search(r'^Name: (.+)$',m,re.M)[1];v=re.search(r'^Version: (.+)$',m,re.M)[1]
 pins.append(f'{name}=={v} --hash=sha256:{r["sha256"]}')
(ROOT/'artifacts/requirements.lock').write_text('\n'.join(sorted(pins))+'\n')
with tarfile.open(ROOT/'artifacts/uv-x86_64-unknown-linux-gnu.tar.gz') as t:
 uv=[{'path':m.name,'sha256':hashlib.sha256(t.extractfile(m).read()).hexdigest(),'size':m.size} for m in t if m.isfile()]
(ROOT/'artifacts/uv-members.json').write_text(json.dumps(uv,indent=2)+'\n')
print(json.dumps({'wheels':[{k:v for k,v in r.items() if k!='metadata'} for r in rows],'uv':uv},indent=2))
