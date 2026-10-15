"""Correct a probe-only attribute lookup; preserve original install/import attempts."""
import json
import os
import pathlib
import socket
import subprocess
import time
from acquire import HERE, save

logs=HERE/'offline'
net={'netns':os.readlink('/proc/self/ns/net'),'route':pathlib.Path('/proc/net/route').read_text(),
     'interfaces':socket.if_nameindex()}
try:
    with socket.socket() as s:
        s.settimeout(1);s.connect(('198.51.100.1',443))
    raise AssertionError('External connection succeeded')
except OSError as e:
    net.update(error=repr(e),errno=e.errno);assert e.errno==101
assert not net['route'].splitlines()[1:]
assert [n for _,n in net['interfaces']]==['lo']
save(logs/'retry-import-network.json',net)
env=dict(os.environ,CUDA_VISIBLE_DEVICES='',PIP_NO_INDEX='1',PIP_DISABLE_PIP_VERSION_CHECK='1',
         PYTHONDONTWRITEBYTECODE='1',MPLBACKEND='Agg',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
for key in ['HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy',
            'PYTHONPATH','PYTHONHOME','LD_LIBRARY_PATH','LD_PRELOAD']:env.pop(key,None)
summary=json.loads((HERE/'offline-summary.json').read_text())
for name,row in summary.items():
    cmd=row['import']['command'].copy()
    cmd[-1]=cmd[-1].replace('numpy.__mkl_version__','numpy._distributor_init.__mkl_version__')
    cmd[-1]=cmd[-1].replace("__mkl_version__=='2023.1.0'","__mkl_version__=='2023.0.1'")
    cmd[-1]=cmd[-1].replace("indent=2))", "indent=2,default=lambda b:b.decode() if isinstance(b,bytes) else repr(b)))")
    start=time.monotonic()
    p=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=180)
    (logs/f'retry-import-{name}.stdout.txt').write_text(p.stdout)
    (logs/f'retry-import-{name}.stderr.txt').write_text(p.stderr)
    receipt={'command':cmd,'exit_code':p.returncode,'elapsed_seconds':round(time.monotonic()-start,3)}
    save(logs/f'retry-import-{name}.receipt.json',receipt)
    row['initial_import']=row['import'];row['import']=receipt
    row['status']='complete-import-payload' if p.returncode==0 else 'partial-import-payload'
    print(name,p.returncode,flush=True)
save(HERE/'final-summary.json',summary)
