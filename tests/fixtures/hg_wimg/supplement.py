"""Independent fresh receipts for task tool lookup; never execute those tools."""
import ast
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import uuid

HERE=Path(__file__).resolve().parent
OUT=HERE/'supplement'
OUT.mkdir(exist_ok=False)
SESSION='hg-wimg-tools-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]


def run(key,argv,timeout=90):
    p=OUT/key
    p.parent.mkdir(parents=True,exist_ok=True)
    start=datetime.now(timezone.utc).isoformat()
    try:
        r=subprocess.run(argv,capture_output=True,timeout=timeout)
        rc,out,err=r.returncode,r.stdout,r.stderr
    except subprocess.TimeoutExpired as e:
        rc,out,err=124,e.stdout or b'',(e.stderr or b'')+b'\nCOLLECTOR TIMEOUT\n'
    Path(str(p)+'.stdout.txt').write_bytes(out)
    Path(str(p)+'.stderr.txt').write_bytes(err)
    Path(str(p)+'.command.json').write_text(json.dumps({'argv':argv,'shell_display':shlex.join(argv),
        'returncode':rc,'started_utc':start,'ended_utc':datetime.now(timezone.utc).isoformat()},indent=2)+'\n')
    return rc,out


images=json.loads((HERE/'capture/image-inventory.json').read_text())
tbroot=Path(os.environ.get('HG_TERMINAL_BENCH','/mnt/20t/xubuqiang/datasets/terminal-bench'))
surfaces=[]
common='sh bash python python3 uv uvx pytest curl apt-get gcc g++ cc make cmake node java ruby R Rscript go rustc cargo sqlite3 ffmpeg stockfish openssl pdflatex'.split()
for x in images:
    if x['dataset']!='terminal_bench':continue
    d=tbroot/x['task']
    if not d.is_dir():d=tbroot/'tasks'/x['task']
    imports=[]; calls=[]; tools=set(common)
    for p in sorted((d/'tests').rglob('*.py')):
        text=p.read_text(errors='replace')
        try: tree=ast.parse(text)
        except SyntaxError:continue
        for n in ast.walk(tree):
            if isinstance(n,(ast.Import,ast.ImportFrom)):
                names=[v.name for v in n.names] if isinstance(n,ast.Import) else [n.module or '']
                imports.append({'file':str(p),'line':n.lineno,'modules':names,'text':ast.get_source_segment(text,n)})
            if isinstance(n,ast.Call):
                func=ast.unparse(n.func)
                if func.startswith(('subprocess.','os.system','os.popen')):
                    rec={'file':str(p),'line':n.lineno,'text':ast.get_source_segment(text,n),'dynamic_argv':True}
                    if n.args:
                        arg=n.args[0]
                        first=arg.elts[0] if isinstance(arg,(ast.List,ast.Tuple)) and arg.elts else arg
                        if isinstance(first,ast.Constant) and isinstance(first.value,str):
                            try: command=shlex.split(first.value)[0]
                            except (ValueError,IndexError):command=''
                            if re.fullmatch(r'[A-Za-z0-9_./+:-]+',command):
                                tools.add(command);rec['literal_program']=command
                            rec['dynamic_argv']=not isinstance(arg,ast.Constant)
                    calls.append(rec)
    surfaces.append({'task':x['task'],'image':x['reference'],'imports':imports,'process_calls':calls,
                     'tool_lookup_candidates':sorted(tools),
                     'note':'Static imports/calls are a required-surface inventory. Common tool candidates are a conservative superset, not evidence that every candidate is needed. Dynamic/candidate/runtime downloads remain unresolved.'})
(OUT/'verifier-surfaces.json').write_text(json.dumps(surfaces,indent=2)+'\n')
bytask={x['task']:x for x in surfaces}


def probe(x):
    if not x['present'] or x['dataset']!='terminal_bench':return
    name=SESSION+'-'+x['task']
    key=x['task']
    rc,_=run(key+'/create',['docker','create','--name',name,'--pull=never','--network=none','--read-only',
        '--cpus=1','--memory=256m','--memory-swap=256m','--pids-limit=64','--cap-drop=ALL',
        '--security-opt=no-new-privileges','--mount','type=bind,src='+str(HERE)+',dst=/wimg,readonly',
        '--entrypoint=/bin/sh',x['image_id'],'/wimg/tools-probe.sh',*bytask[x['task']]['tool_lookup_candidates']])
    if rc==0:
        try:
            run(key+'/inspect-before',['docker','inspect',name])
            run(key+'/start',['docker','start','--attach',name])
            run(key+'/inspect-after',['docker','inspect',name])
        finally:run(key+'/remove',['docker','rm','-f',name])
    print(key,flush=True)


with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(probe,images))
run('final-owned-container-check',['docker','ps','-a','--filter','name='+SESSION,'--format','{{.Names}}'])
print('SUPPLEMENT COMPLETE',flush=True)
