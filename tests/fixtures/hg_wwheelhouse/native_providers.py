"""Acquire only native providers explicitly loaded by Torch's import-time loader."""
import concurrent.futures
import hashlib
import importlib.metadata as md
import json
import pathlib
import obtain

HERE=pathlib.Path(__file__).resolve().parent
m=json.loads((HERE/'manifest.json').read_text())
obtain.PAYLOADS=pathlib.Path(m['payload_directory'])
source=pathlib.Path('/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/torch/__init__.py')
keys=['nvidia-cublas-cu12','nvidia-cudnn-cu12','nvidia-cuda-nvrtc-cu12','nvidia-cuda-runtime-cu12',
      'nvidia-cuda-cupti-cu12','nvidia-cufft-cu12','nvidia-curand-cu12','nvidia-nvjitlink-cu12',
      'nvidia-cusparse-cu12','nvidia-cusolver-cu12','nvidia-nccl-cu12','nvidia-nvtx-cu12']
records=[]
for key in keys:
    d=md.distribution(key)
    records.append((key,{'name':d.metadata['Name'],'version':d.version,'role':'torch-import-time-native-provider',
                        'installed_wheel':d.read_text('WHEEL'),'direct_url':d.read_text('direct_url.json')}))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for k,r in pool.map(obtain.obtain,records):
        r['source_witness']={'path':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                            'lines':'285, 289-325, 366','note':'ctypes.CDLL loader; cuda_libs names every required provider. No GPU operation is executed.'}
        m['artifacts'][k]=r
        (HERE/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
        print(k,r['version'],r['status'],r.get('filename',r.get('reason')),flush=True)
