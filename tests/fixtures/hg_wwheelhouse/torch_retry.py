"""Retry the failed DS-1000 import after supplying its import-time native libraries."""
import json
import os
import pathlib
import socket
import sys
import offline

HERE=pathlib.Path(__file__).resolve().parent
net={'netns':os.readlink('/proc/self/ns/net'),'route':pathlib.Path('/proc/net/route').read_text(),
     'interfaces':socket.if_nameindex()}
try:
    with socket.socket() as s:s.connect(('198.51.100.1',443))
    raise AssertionError('external connection succeeded')
except OSError as e:
    net.update(error=repr(e),errno=e.errno);assert e.errno==101
(HERE/'offline/torch-retry-network.json').write_text(json.dumps(net,indent=2)+'\n')
summary=json.loads((HERE/'install-summary.json').read_text())
python=summary['ds1000-partial-public-wheels']['install']['command'][0]
m=json.loads((HERE/'manifest.json').read_text())
keys=sorted(k for k,r in m['artifacts'].items() if r['role']=='torch-import-time-native-provider')
assert len(keys)==12 and all(m['artifacts'][k]['status']=='obtained-wheel' for k in keys)
lp=HERE/'ds1000-native-providers.lock';offline.lock(lp,keys,m['artifacts'])
install=offline.run('retry-install-ds1000-native-providers',[python,'-m','pip','install','--no-index','--no-cache-dir','--no-deps',
    '--require-hashes','--find-links',m['payload_directory'],'-r',str(lp)],timeout=300)
code='''import importlib,json,sys
mods=['numpy','pandas','scipy','sklearn','matplotlib.pyplot','seaborn','torch','gensim']
results={}
for name in mods:
 try:
  m=importlib.import_module(name)
  results[name]={'ok':True,'version':getattr(m,'__version__',None)}
 except Exception as e:results[name]={'ok':False,'error':repr(e)}
print(json.dumps(results,indent=2))
raise SystemExit(any(not r['ok'] for r in results.values()))
'''
probe=offline.run('retry-import-ds1000-with-native-providers',[python,'-c',code])
(HERE/'ds1000-retry-summary.json').write_text(json.dumps({'install':install,'import':probe,
    'note':'Package imports only, CUDA_VISIBLE_DEVICES empty; no tensor, model, GPU, scorer or benchmark execution.'},indent=2)+'\n')
for name in ['chessbench_puzzles','scienceworld']:
    py=summary[name]['install']['command'][0]
    r=offline.run('pip-check-'+name,[py,'-m','pip','check'])
    assert r['exit_code']==0
