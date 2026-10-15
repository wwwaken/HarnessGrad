#!/usr/bin/env python3
import sys,pathlib,datetime,json
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from collect import ROOT,run
name='hg-wuvx-offline-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S')
image='sha256:4c948a4e630af2435ae0a19108fc0814a946ac2fa29a512469e0fc77b38c8c12'
try:
 p=run('offline',['docker','run','--name',name,'--pull=never','--network=none','--cpus=1','--memory=1g','--pids-limit=128','-v',f'{ROOT}:/packet:ro',image,'bash','/packet/scripts/offline.sh'])
 run('offline-container-inspect',['docker','inspect',name])
 for f in ['offline-python.json','offline-dpkg.txt','offline-pytest-help.txt','offline-venv-paths.txt']:
  run('copy-'+f.replace('.','-'),['docker','cp',f'{name}:/tmp/{f}',str(ROOT/'raw'/f)])
 sys.exit(p.returncode)
finally:run('offline-cleanup',['docker','rm','-f',name])
