"""Fresh, local-only custody capture. Never imports adapters or invokes their tests.

Output directory must be fresh. Each argv, status and raw stream is retained.
Recollection must use another directory; do not overwrite these receipts.
"""
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
import sys
import tomllib
import uuid

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OUT = HERE / 'capture'
OUT.mkdir(exist_ok=False)
SESSION = 'hg-wimg-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:6]


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def run(key, argv, timeout=60):
    dest = OUT / key
    dest.parent.mkdir(parents=True, exist_ok=True)
    start = datetime.now(timezone.utc).isoformat()
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout)
        rc, stdout, stderr = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        rc, stdout, stderr = 124, e.stdout or b'', (e.stderr or b'') + b'\nCOLLECTOR TIMEOUT\n'
    Path(str(dest)+'.stdout.txt').write_bytes(stdout)
    Path(str(dest)+'.stderr.txt').write_bytes(stderr)
    write(Path(str(dest)+'.command.json'), {'argv': argv, 'shell_display': shlex.join(argv),
          'started_utc': start, 'ended_utc': datetime.now(timezone.utc).isoformat(), 'returncode': rc})
    return rc, stdout, stderr


def source(path, pattern=None):
    p = Path(path)
    if not p.is_file():
        return {'path': str(p), 'missing': True}
    text = p.read_text(errors='replace')
    return {'path': str(p.relative_to(REPO)) if p.is_relative_to(REPO) else str(p),
            'sha256': sha(p), 'lines': [{'line': i, 'text': s} for i,s in enumerate(text.splitlines(),1)
             if pattern is None or re.search(pattern,s)]}


run('baseline/registry', ['python3', 'tools/check_dataset_blockers.py'])
run('baseline/git-head', ['git', 'rev-parse', 'HEAD'])
run('baseline/docker-version', ['docker', 'version'])
run('baseline/docker-images', ['docker', 'image', 'ls', '--digests', '--no-trunc'])
run('baseline/docker-context', ['docker', 'context', 'inspect', '--format', '{{json .Endpoints.docker.Host}}'])
run('baseline/containerd-direct', ['ctr', '--address', '/run/containerd/containerd.sock', '--namespace', 'moby', 'content', 'ls'])
env_names = ['HG_GAIA_IMAGE', 'HG_TAU_IMAGE', 'HG_APPWORLD_IMAGE', 'HG_APPWORLD_SERVICE_IMAGE',
             'HG_APPWORLD_VERIFIER_IMAGE', 'HG_TERMINAL_BENCH', 'HG_TB_TASKS']
write(OUT/'environment.json', {k: os.environ.get(k) for k in env_names})
adapters = ['gaia', 'tau_bench', 'appworld', 'terminal_bench', 'chessbench_puzzles', 'alfworld',
            'scienceworld', 'bird_minidev', 'ds1000', 'spreadsheetbench']
snapshots = [source(REPO/'data/datasets'/f'{n}.py', r'image|IMAGE|kind.*files|state|VERIFIER|argv|python3|class') for n in adapters]
snapshots += [source(REPO/p, r'pin_image|RepoDigests|snapshot|create\(|image|scorer_isolation_class') for p in
              ['eval/containers/container.py', 'eval/containers/container_state.py', 'eval/verification/verifier.py']]
write(OUT/'source-locators.json', snapshots)
prior=[]
for name in ('hg_wclo_runtime', 'hg_wtbdep', 'hg_wujson'):
    root=REPO/'tests/fixtures'/name
    manifest=root/'SHA256SUMS'
    records=[]
    if manifest.is_file():
        for line in manifest.read_text().splitlines():
            if not line.strip():
                continue
            expected, rel=line.split(None,1)
            p=root/rel.lstrip('* ')
            records.append({'path': str(p.relative_to(REPO)), 'present': p.is_file(),
                            'current_sha256': sha(p) if p.is_file() else None,
                            'matches_historical_manifest': sha(p)==expected if p.is_file() else False})
    prior.append({'fixture':name,'manifest_present':manifest.is_file(),'records':records})
write(OUT/'prior-fixture-audit.json',prior)
images=[]
for dataset,var in [('gaia','IMAGE'),('tau_bench','IMAGE'),('appworld','IMAGE'),('appworld','SERVICE_IMAGE'),('appworld','VERIFIER_IMAGE')]:
    tree=ast.parse((REPO/'data/datasets'/f'{dataset}.py').read_text())
    node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==var for t in n.targets))
    default=ast.literal_eval(node.value.args[1])
    envvar=ast.literal_eval(node.value.args[0])
    label=dataset if dataset!='appworld' else {'IMAGE':'appworld-actor','SERVICE_IMAGE':'appworld-service','VERIFIER_IMAGE':'appworld-verifier'}[var]
    images.append({'key':label,'dataset':dataset,'role':var,'reference':os.environ.get(envvar,default),
                   'default_reference':default,'env_override':envvar,'adapter':f'data/datasets/{dataset}.py',
                   'line':node.lineno,'literal_line':node.value.args[1].lineno})
tbroot=Path(os.environ.get('HG_TERMINAL_BENCH','/mnt/20t/xubuqiang/datasets/terminal-bench'))
run('baseline/terminal-bench-head', ['git','-C',str(tbroot),'rev-parse','HEAD'])
dirs=sorted(p.parent for p in tbroot.glob('*/task.toml')) or sorted(p.parent for p in tbroot.glob('tasks/*/task.toml'))
surface=[]
for d in dirs:
    task=tomllib.loads((d/'task.toml').read_text())
    ref=task['environment']['docker_image']
    line=next(i for i,s in enumerate((d/'task.toml').read_text().splitlines(),1) if re.match(r'\s*docker_image\s*=',s))
    images.append({'key':'tb-'+d.name,'dataset':'terminal_bench','task':d.name,'reference':ref,
                   'adapter':'data/datasets/terminal_bench.py','line':198,'manifest':str(d/'task.toml'),'manifest_line':line})
    records=[source(d/'task.toml'), source(d/'environment/Dockerfile')]
    for p in sorted((d/'tests').rglob('*')):
        if p.is_file() and p.suffix in ('.sh','.py','.toml','.txt'):
            records.append(source(p, r'import |from |apt|curl|wget|uv|pip|pytest|subprocess|os\.system|Popen|download|java|gcc|g\+\+|rust|cargo|node|ruby|pdflatex'))
    surface.append({'task':d.name,'image':ref,'files':records})
write(OUT/'terminal-bench-source-surface.json',surface)


def inspect(item):
    rc,out,_=run('images/'+item['key']+'/inspect',['docker','image','inspect',item['reference']])
    item['present']=rc==0
    item['configured_pin']='digest' if '@sha256:' in item['reference'] else 'movable-tag'
    if rc==0:
        info=json.loads(out)[0]
        item.update(image_id=info['Id'],repo_digests=info.get('RepoDigests',[]),descriptor=info.get('Descriptor'))
    return item


with ThreadPoolExecutor(max_workers=4) as pool:
    images=list(pool.map(inspect,images))
write(OUT/'image-inventory.json',images)
print(json.dumps({'session':SESSION,'adapter_images':len(images),'present':sum(x['present'] for x in images),
                  'missing':[x['key'] for x in images if not x['present']]}),flush=True)
# The local containerd socket is root-owned. Read only the selected content blobs
# through a read-only Docker bind; no registry requests, pulls or content writes.
meta=next(x for x in images if x['key']=='tau_bench')
name=SESSION+'-metadata'
code='''import hashlib,json,pathlib,sys
root=pathlib.Path('/content'); output={}
def visit(digest):
 if digest in output:return
 p=root/digest.split(':',1)[1]
 try:
  b=p.read_bytes(); obj=json.loads(b); actual='sha256:'+hashlib.sha256(b).hexdigest()
  output[digest]={'computed_digest':actual,'matches':actual==digest,'raw_utf8':b.decode()}
  for m in obj.get('manifests',[]):visit(m['digest'])
 except Exception as e: output[digest]={'error':repr(e)}
for d in json.loads(sys.argv[1]):visit(d)
print(json.dumps(output,indent=2,sort_keys=True))
'''
descriptors=sorted({x['descriptor']['digest'] for x in images if x.get('descriptor')})
rc,_,_=run('manifest-read/create',['docker','create','--name',name,'--pull=never','--network=none','--read-only',
        '--cpus=1','--memory=256m','--memory-swap=256m','--pids-limit=64','--cap-drop=ALL',
        '--security-opt=no-new-privileges','--mount','type=bind,src=/var/lib/containerd/io.containerd.content.v1.content/blobs/sha256,dst=/content,readonly',
        '--entrypoint=python3',meta['image_id'],'-I','-B','-c',code,json.dumps(descriptors)])
if rc==0:
    try:
        run('manifest-read/inspect-before',['docker','inspect',name])
        run('manifest-read/start',['docker','start','--attach',name],timeout=90)
        run('manifest-read/inspect-after',['docker','inspect',name])
    finally:
        run('manifest-read/remove',['docker','rm','-f',name])


def probe(item):
    if not item['present']:
        return
    name=SESSION+'-'+item['key']
    # Image ID obtained in this capture binds each probe to these inspected bytes.
    argv=['docker','create','--name',name,'--pull=never','--network=none','--read-only',
          '--cpus=1','--memory=1536m','--memory-swap=1536m','--pids-limit=128','--cap-drop=ALL',
          '--security-opt=no-new-privileges','--tmpfs=/tmp:rw,exec,nosuid,nodev,size=128m',
          '--env=OPENBLAS_NUM_THREADS=1','--env=OMP_NUM_THREADS=1','--env=PYTHONDONTWRITEBYTECODE=1',
          '--env=HOME=/tmp','--mount','type=bind,src='+str(HERE)+',dst=/wimg,readonly',
          '--workdir=/tmp','--entrypoint=/bin/sh',item['image_id'],'/wimg/probe.sh',item['key']]
    key='images/'+item['key']
    rc,_,_=run(key+'/create',argv)
    if rc==0:
        try:
            run(key+'/inspect-before',['docker','inspect',name])
            rc,out,err=run(key+'/start',['docker','start','--attach',name],timeout=120)
            run(key+'/inspect-after',['docker','inspect',name])
            marker=b'=== Python collector follows ===\n'
            try:
                value=json.loads(out.split(marker,1)[1])
                write(OUT/key/'abi.json',value)
                item['abi_collected']=True
            except Exception as e:
                item['abi_collected']=False
                item['abi_parse_error']=repr(e)
            item['probe_returncode']=rc
        finally:
            run(key+'/remove',['docker','rm','-f',name])
    else:
        item['create_failed']=True
    print(item['key'],item.get('probe_returncode'),flush=True)


with ThreadPoolExecutor(max_workers=2) as pool:
    list(pool.map(probe,images))
write(OUT/'image-inventory.json',images)
run('native/host-probe',['python3','-I','-B',str(HERE/'probe.py'),'native'],timeout=120)
run('final-owned-container-check',['docker','ps','-a','--filter','name='+SESSION,'--format','{{.Names}}'])
run('final-registry',['python3','tools/check_dataset_blockers.py'])
write(OUT/'session.json',{'session':SESSION,'images':len(images),'scope':'import/ABI inspection only; no tasks, models, GPUs or endpoints'})
print('CAPTURE COMPLETE',flush=True)
