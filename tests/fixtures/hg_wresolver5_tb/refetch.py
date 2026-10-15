"""Re-fetch recorded exact wheels to an external directory and independently verify them."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request
from common import HERE, ROOT
parser=argparse.ArgumentParser();parser.add_argument('destination',type=Path);args=parser.parse_args()
destination=args.destination.resolve()
assert destination!=ROOT and ROOT not in destination.parents, 'Payloads must remain outside repository'
destination.mkdir(parents=True,exist_ok=True)
for a in json.loads((HERE/'inputs.json').read_text())['artifacts']:
    path=destination/a['filename']
    assert not path.exists(),'Use a fresh destination; never overwrite an artifact'
    with urllib.request.urlopen(a['url'],timeout=45) as response,path.open('xb') as stream:
        assert response.status==200
        count=0
        while chunk:=response.read(65536):
            count+=len(chunk);assert count<=16*1024*1024
            stream.write(chunk)
    with path.open('rb') as stream:actual=hashlib.file_digest(stream,'sha256').hexdigest()
    assert path.stat().st_size==a['bytes'] and actual==a['sha256']
    print(json.dumps({'filename':a['filename'],'bytes':count,'sha256':actual,'url':a['url'],'verified':True}),flush=True)
