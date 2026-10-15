"""Pinned build-only tools required by the obtained sdists; never scorer versions."""
import json
import pathlib
import obtain

HERE=pathlib.Path(__file__).resolve().parent
m=json.loads((HERE/'manifest.json').read_text())
obtain.PAYLOADS=pathlib.Path(m['payload_directory'])
# Explicit build-tool choices, checked against live versioned PyPI responses.
for key,version in [('cmake','3.29.6'),('setuptools-scm','8.1.0'),('cppy','1.2.1'),('pkgconfig','1.5.5')]:
    k,r=obtain.obtain((key,{'name':key,'version':version,'role':'sdist-build-only'}))
    m['artifacts'][k]=r
    print(k,r['status'],r.get('filename',r.get('reason')),flush=True)
(HERE/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
