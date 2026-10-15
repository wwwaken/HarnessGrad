"""Re-fetch captured exact wheel URLs outside git, independently recheck every byte.

Usage: python3 refetch.py /tmp/NEW-DIRECTORY (must not exist).
This does not re-resolve, alter constraints, or contact any model endpoint.
"""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument('destination',type=Path)
parser.add_argument('--filename',action='append',help='Optional bounded subset; default re-fetches the complete captured set plus pip tooling.')
args = parser.parse_args()
here = Path(__file__).resolve().parent
root = here.parents[2]
destination = args.destination.resolve()
assert not destination.is_relative_to(root) and not destination.exists()
destination.mkdir(parents=True)
records = json.loads((here/'artifacts.json').read_text())['artifacts']
records += [json.loads((here/'tool.json').read_text())['artifact']]
if args.filename:
    assert set(args.filename)<={r['filename'] for r in records}
    records=[r for r in records if r['filename'] in args.filename]
for record in records:
    path = destination/record['filename']
    size = 0
    with urllib.request.urlopen(record['url'],timeout=45) as response,path.open('xb') as stream:
        while block := response.read(1024*1024):
            size += len(block)
            assert size<=record['bytes'],record['filename']
            stream.write(block)
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream,'sha256').hexdigest()
    assert size==record['bytes'] and digest==record['sha256'],record['filename']
    print(digest,size,path.name,flush=True)
