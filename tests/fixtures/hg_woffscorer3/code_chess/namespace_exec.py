#!/usr/bin/env python3
"""Network namespace guard for upstream multiprocessing.Manager's AF_UNIX IPC."""
import errno
import hashlib
import json
import os
from pathlib import Path
import resource
import runpy
import socket
import sys
resource.setrlimit(resource.RLIMIT_CPU,(120,120))
resource.setrlimit(resource.RLIMIT_NOFILE,(256,256))
os.environ['CUDA_VISIBLE_DEVICES']=''
os.environ['HF_HUB_OFFLINE']='1';os.environ['HF_DATASETS_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
sys.dont_write_bytecode=True
for p in Path('/proc/self/fd').iterdir():
 try:
  if int(p.name)>2 and os.readlink(p).startswith('socket:'): os.close(int(p.name))
 except FileNotFoundError: pass
netns=os.readlink('/proc/self/ns/net')
assert netns!=os.environ['HG_WOFFSCORER3_PARENT_NETNS']
dev=Path('/proc/net/dev').read_text();assert [line.split(':')[0].strip() for line in dev.splitlines()[2:]]==['lo']
routes=Path('/proc/net/route').read_text();assert not routes.splitlines()[1:]
with socket.socket() as s:
 try: s.connect(('198.18.0.1',9))
 except OSError as e:
  assert e.errno in (errno.ENETUNREACH,errno.EHOSTUNREACH);probe={'errno':e.errno,'result':'no route'}
 else: raise AssertionError('unexpected external connection')
print(json.dumps({'guard':'fresh bubblewrap network namespace; local IPC allowed','parent_netns':os.environ['HG_WOFFSCORER3_PARENT_NETNS'],'netns':netns,'network_devices':dev,'ipv4_routes':routes,'ipv6_routes':Path('/proc/net/ipv6_route').read_text(),'external_probe':probe,'cpu_limit_seconds':120,'nofile_limit':256,'interpreter':str(Path(sys.executable).resolve()),'interpreter_sha256':hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),'bwrap_sha256':hashlib.sha256(Path('/usr/bin/bwrap').read_bytes()).hexdigest(),'production_runtime_observation':False}),file=sys.stderr,flush=True)
denied=[]
def audit(event,args):
 if event in ('open','os.listdir','os.scandir') and args and isinstance(args[0],(str,bytes,os.PathLike)):
  path=os.fsdecode(args[0])
  if path.startswith(('/mnt/20t/xubuqiang/datasets/','/mnt/8t/xubuqiang/datasets/')):
   denied.append({'event':event,'path':path});raise PermissionError('controlled fixture excludes external dataset payload reads')
sys.addaudithook(audit)
script=Path(sys.argv[1]).resolve();sys.argv=sys.argv[1:];sys.path.insert(0,str(script.parent))
try: runpy.run_path(str(script),run_name='__main__')
finally: print(json.dumps({'blocked_external_dataset_reads':denied}),file=sys.stderr,flush=True)
