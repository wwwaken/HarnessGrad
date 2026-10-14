"""No-model egress control: cached image, internal vs default bridge; no task/scorer."""
import datetime,json,pathlib,secrets,shlex,subprocess
root=pathlib.Path('/tmp/hg-tbrun4')
control_id='w-tbrun4-egress-control-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+secrets.token_hex(4)
evidence=root/'runs'/control_id
evidence.mkdir(exist_ok=False)
(evidence/'control.py').write_bytes(pathlib.Path(__file__).read_bytes())
network='hg-'+control_id
image='sha256:4c948a4e630af2435ae0a19108fc0814a946ac2fa29a512469e0fc77b38c8c12'
script='''import json, pathlib, urllib.request
print(json.dumps({'routes':pathlib.Path('/proc/net/route').read_text()}),flush=True)
opener=urllib.request.build_opener(urllib.request.ProxyHandler({'https':'http://172.17.0.1:17890'}))
for url in ('https://pypi.org/simple/','https://astral.sh/uv/0.9.5/install.sh'):
    try:
        with opener.open(url,timeout=8) as r: print(json.dumps({'url':url,'status':r.status}),flush=True)
    except Exception as e: print(json.dumps({'url':url,'error':str(e),'error_class':type(e).__name__}),flush=True)
'''
def capture(name,argv):
    p=subprocess.run(argv,capture_output=True,text=True,timeout=45)
    result=dict(argv=argv,command=shlex.join(argv),returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
    (evidence/name).write_text(json.dumps(result,indent=2)+'\n')
    return result
(evidence/'identity.json').write_text(json.dumps(dict(control_id=control_id,network=network,image=image,purpose='No model, task or scorer: reproduce declared proxy reachability on each Docker network',model_calls=False),indent=2)+'\n')
try:
    r=capture('network-create.json',['docker','network','create','--internal','--label',f'harnessgrad.run={control_id}',network])
    assert r['returncode']==0
    capture('network-inspect.json',['docker','network','inspect',network])
    for mode in ('bridge',network):
        name='bridge' if mode=='bridge' else 'internal'
        capture(name+'.json',['docker','run','--rm','--pull=never','--name','hg-'+control_id+'-'+name,'--label',f'harnessgrad.run={control_id}','--network',mode,'--cpus','1','--memory','2147483648','--pids-limit','1024',image,'python3','-c',script])
finally:
    capture('network-remove.json',['docker','network','rm',network])
    capture('containers-after.json',['docker','ps','-a','--filter',f'label=harnessgrad.run={control_id}','--format','{{json .}}'])
    capture('networks-after.json',['docker','network','ls','--filter',f'label=harnessgrad.run={control_id}','--format','{{json .}}'])
print(str(evidence),flush=True)
print((evidence/'bridge.json').read_text())
print((evidence/'internal.json').read_text())
