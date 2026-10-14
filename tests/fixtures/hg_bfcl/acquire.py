#!/usr/bin/env python3
"""Public-source custody only. Never import upstream code or inspect task members."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PROXY = os.environ.get('HG_EGRESS_PROXY', 'http://172.17.0.1:17890')

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda: f.read(1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()

def get(name, url):
    body = OUT / 'responses' / (name + '.body')
    headers = body.with_suffix('.headers')
    receipt = body.with_suffix('.receipt.json')
    if any(p.exists() for p in (body, headers, receipt)):
        raise RuntimeError('Refuse to overwrite custody response: ' + name)
    body.parent.mkdir(exist_ok=True)
    args = ['curl', '--proxy', PROXY, '--noproxy', '', '--silent', '--show-error',
            '--connect-timeout', '20', '--max-time', '240', '--max-redirs', '0',
            '--header', 'User-Agent: HarnessGrad-w-bfcl-public-custody/1',
            '--header', 'Accept: application/octet-stream' if name == 'archive' else 'Accept: application/json',
            '--dump-header', str(headers.relative_to(ROOT)), '--output', str(body.relative_to(ROOT)),
            '--write-out', '%{http_code}', url]
    start = dt.datetime.now(dt.timezone.utc).isoformat()
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    record = dict(url=url, method='GET', command=args, proxy=PROXY,
                  started_at_utc=start, completed_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                  curl_exit_code=result.returncode, http_status=result.stdout,
                  stderr=result.stderr, production_authorized=False)
    for key, path in [('body', body), ('headers', headers)]:
        if path.exists():
            record[key] = dict(path=str(path.relative_to(ROOT)), bytes=path.stat().st_size,
                               sha256=digest(path))
    receipt.write_text(json.dumps(record, indent=2) + '\n')
    print(name, result.returncode, result.stdout, record.get('body'), flush=True)
    if result.returncode or result.stdout != '200':
        raise RuntimeError('Acquisition failed; preserved response: ' + name)
    return body

def main():
    doc = json.loads((ROOT / 'docs/dataset-blockers.json').read_text())
    initial = next(d for d in doc['datasets'] if d['dataset'] == 'bfcl_v3')
    (OUT / 'starting-blocker.json').write_text(json.dumps(initial, indent=2) + '\n')
    tag = json.loads(get('tag', 'https://api.github.com/repos/ShishirPatil/gorilla/git/ref/tags/v1.3').read_text())
    assert tag['object']['type'] == 'commit', 'Resolve annotated tag explicitly before proceeding'
    commit = tag['object']['sha']
    get('release', 'https://api.github.com/repos/ShishirPatil/gorilla/releases/tags/v1.3')
    get('commit', 'https://api.github.com/repos/ShishirPatil/gorilla/git/commits/' + commit)
    get('license-blob', 'https://api.github.com/repos/ShishirPatil/gorilla/git/blobs/' +
        next(f['git_blob_sha1'] for f in json.loads((ROOT / 'tests/fixtures/e3_bfcl_source/inventory.json').read_text())['files'] if f['original_path'] == 'LICENSE'))
    get('archive', 'https://codeload.github.com/ShishirPatil/gorilla/tar.gz/refs/tags/v1.3')

if __name__ == '__main__':
    main()
