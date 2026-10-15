"""Enforce the user-requested largest-new-file bound on the actual staged index."""
import json
from pathlib import Path
import subprocess
paths=subprocess.check_output(['git','diff','--cached','--name-only','--diff-filter=A','-z']).decode().split('\0')
files=[]
for path in paths:
    if not path:continue
    assert path.startswith(('tests/fixtures/hg_wresolver5_tb/','reports/w-resolver5-tb-'))
    size=int(subprocess.check_output(['git','cat-file','-s',':'+path]))
    assert size<1024*1024,(path,size)
    assert Path(path).suffix not in {'.whl','.conda','.deb','.gz','.bz2','.zip','.body'}
    files.append((size,path))
assert files
print(json.dumps({'valid':True,'largest_added_file_bytes':max(files)[0],
    'largest_added_file':max(files)[1],'largest_added_file_limit_bytes':1024*1024,
    'staged_added_files':len(files),'staged_added_bytes':sum(s for s,p in files)},indent=2))
