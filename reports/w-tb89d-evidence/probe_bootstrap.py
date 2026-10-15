"""No-model prerequisite diagnostic; no official tests, answers or scoring."""
import datetime,json,pathlib,secrets,subprocess
packet=pathlib.Path(__file__).resolve().parent
inv=json.loads((packet/'inventory.json').read_text());batch=json.loads((packet/'batch.json').read_text());root=pathlib.Path(batch['runs_root'])
row=next(r for r in inv['rows'] if r['task_id']=='gcode-to-text')
name='w-tb89d-bootstrap-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+secrets.token_hex(4)
ev=root/name;ev.mkdir(exist_ok=False)
script='''set -eux
apt-get update
apt-get install -y curl
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
. "$HOME/.local/bin/env"
uvx -p 3.13 -w pytest==8.4.1 -w pytest-json-ctrf==0.3.5 pytest --version
'''
(ev/'script.sh').write_text(script)
args=['docker','run','--rm','--pull=never','--name',name,'--label','harnessgrad.run='+name,'--network','bridge','--cpus','1','--memory','2048m','--pids-limit','128']
for key in ('HTTP_PROXY','HTTPS_PROXY','http_proxy','https_proxy'):args+=['-e',key+'=http://172.17.0.1:17890']
args+=['--entrypoint','/bin/bash',row['image_id'],'-c',script]
def cap(label,args,timeout=30):
 try:
  r=subprocess.run(args,capture_output=True,text=True,timeout=timeout);d=dict(argv=args,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)
 except subprocess.TimeoutExpired as exc:
  dec=lambda x:x.decode(errors='replace') if isinstance(x,bytes) else x
  d=dict(argv=args,returncode=None,timeout_s=timeout,stdout=dec(exc.stdout),stderr=dec(exc.stderr))
 (ev/(label+'.json')).write_text(json.dumps(d,indent=2)+'\n');return d
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
try:result=cap('bootstrap',args,180)
finally:
 cap('owned-cleanup',['docker','rm','-f',name]);cap('owned-after',['docker','inspect',name])
summary=dict(kind='No-model bootstrap prerequisite probe, not task execution or official verifier coverage',name=name,task_image_id=row['image_id'],started_at=started,ended_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),artifact_dir=str(ev),result=result)
(packet/'bootstrap-prerequisite-result.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
