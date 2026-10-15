#!/usr/bin/env python3
import subprocess,pathlib,json,datetime,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def run(label,argv,timeout=600):
 stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();p=subprocess.run(argv,capture_output=True,timeout=timeout)
 (ROOT/'raw'/f'{label}.stdout.txt').write_bytes(p.stdout);(ROOT/'raw'/f'{label}.stderr.txt').write_bytes(p.stderr)
 (ROOT/'raw'/f'{label}.command.json').write_text(json.dumps({'argv':argv,'cwd':str(pathlib.Path.cwd()),'start_utc':stamp,'returncode':p.returncode},indent=2)+'\n')
 print(label,p.returncode, len(p.stdout),len(p.stderr),flush=True)
 return p
image='sha256:4c948a4e630af2435ae0a19108fc0814a946ac2fa29a512469e0fc77b38c8c12'
if __name__=='__main__':
 run('checkout',['git','-C','/mnt/20t/xubuqiang/datasets/terminal-bench','rev-parse','HEAD'])
 run('image-inspect',['docker','image','inspect',image])
 run('base-probe',['docker','run','--rm','--pull=never','--network=none','--cpus=1','--memory=1g','--pids-limit=128','-v',f'{ROOT}:/packet',image,'bash','-c','python3 /packet/scripts/probe.py; command -v uv || true; command -v uvx || true; dpkg-query -W'])
 name='hg-wuvx-online-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S')
 try:
  p=run('online',['docker','run','--name',name,'--pull=never','--network=bridge','--cpus=1','--memory=1g','--pids-limit=128','-e','HTTP_PROXY=http://172.17.0.1:17890','-e','HTTPS_PROXY=http://172.17.0.1:17890','-e','http_proxy=http://172.17.0.1:17890','-e','https_proxy=http://172.17.0.1:17890','-v',f'{ROOT}:/packet',image,'bash','/packet/scripts/online.sh'])
  run('online-container-inspect',['docker','inspect',name]);sys.exit(p.returncode)
 finally:run('online-cleanup',['docker','rm','-f',name])
