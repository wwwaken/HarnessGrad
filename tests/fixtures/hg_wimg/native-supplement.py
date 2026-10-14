"""Fresh static-native receipts for bases with installed scientific packages."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import json
from pathlib import Path
import shlex
import subprocess
import uuid

HERE=Path(__file__).resolve().parent
OUT=HERE/'native-supplement'
OUT.mkdir(exist_ok=False)
SESSION='hg-wimg-native-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]
summary=json.loads((HERE/'summary.json').read_text())
names={'numpy','scipy','torch','pandas','scikit-learn','pillow','matplotlib','torchvision'}
selected=[x for x in summary if x['dataset']=='terminal_bench' and x['abi'] and x['abi']['python']
          and any(n.lower() in names for n in x['abi']['distributions'])]


def run(key,argv,timeout=180):
    dest=OUT/key;dest.parent.mkdir(parents=True,exist_ok=True)
    try:
        p=subprocess.run(argv,capture_output=True,timeout=timeout)
        rc,out,err=p.returncode,p.stdout,p.stderr
    except subprocess.TimeoutExpired as e:rc,out,err=124,e.stdout or b'',(e.stderr or b'')+b'\nTIMEOUT\n'
    Path(str(dest)+'.command.json').write_text(json.dumps({'argv':argv,'shell_display':shlex.join(argv),
        'returncode':rc,'captured_utc':datetime.now(timezone.utc).isoformat()},indent=2)+'\n')
    Path(str(dest)+'.stdout.txt').write_bytes(out);Path(str(dest)+'.stderr.txt').write_bytes(err)
    return rc


def inspect(x):
    name=SESSION+'-'+x['task'];key=x['task']
    argv=['docker','create','--name',name,'--pull=never','--network=none','--read-only','--cpus=1',
          '--memory=512m','--memory-swap=512m','--pids-limit=64','--cap-drop=ALL',
          '--security-opt=no-new-privileges','--mount','type=bind,src='+str(HERE)+',dst=/wimg,readonly',
          '--entrypoint=python3',x['image_id'],'-I','-B','/wimg/native-probe.py']
    if run(key+'/create',argv)==0:
        try:
            run(key+'/inspect-before',['docker','inspect',name])
            run(key+'/start',['docker','start','--attach',name])
            run(key+'/inspect-after',['docker','inspect',name])
        finally:run(key+'/remove',['docker','rm','-f',name])
    print(key,flush=True)


(OUT/'selected.json').write_text(json.dumps([x['task'] for x in selected],indent=2)+'\n')
with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(inspect,selected))
run('final-owned-container-check',['docker','ps','-a','--filter','name='+SESSION,'--format','{{.Names}}'])
print('NATIVE SUPPLEMENT COMPLETE',flush=True)
