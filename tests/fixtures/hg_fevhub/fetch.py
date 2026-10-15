#!/usr/bin/env python3
"""Retain public HTTPS metadata; never retrieve export payloads or disable TLS."""
import concurrent.futures
import datetime
import hashlib
import json
import os
from pathlib import Path
import ssl
import sys
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent
SCRATCH = Path('/mnt/20t/xubuqiang/hg-work/fevhub')
PROXY = os.environ.get('FEVHUB_PROXY', 'http://172.17.0.1:17890')

class RedirectRecorder(urllib.request.HTTPRedirectHandler):
    def __init__(self):
        self.redirects = []
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        body = fp.read()
        self.redirects.append({'url': req.full_url, 'status': code, 'location': newurl,
                               'headers': list(headers.items()), 'body_hex': body.hex(),
                               'body_sha256': hashlib.sha256(body).hexdigest()})
        if not newurl.startswith('https://'):
            raise ValueError('HTTPS downgrade refused')
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def fetch(item):
    name, url = item
    assert url.startswith('https://')
    assert not url.endswith(('valid.jsonl', 'train.jsonl', '.parquet', '.zip', '.tar.gz'))
    redirects = RedirectRecorder()
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY} if PROXY else {}),
        urllib.request.HTTPSHandler(context=ssl.create_default_context()), redirects)
    row = {'name': name, 'url': url, 'method': 'GET', 'proxy': PROXY or None,
           'tls_verification': 'ssl.create_default_context(): CA and hostname verification',
           'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'request_headers': {'User-Agent': 'HarnessGrad-fevhub-provenance/1', 'Accept-Encoding': 'identity'},
           'redirects': redirects.redirects}
    try:
        req = urllib.request.Request(url, headers=row['request_headers'])
        try:
            response = opener.open(req, timeout=25)
        except urllib.error.HTTPError as e:
            response = e
        with response:
            row.update(status=response.code, final_url=response.geturl(), headers=list(response.headers.items()))
            content_type = response.headers.get('Content-Type', '')
            body = response.read(8_000_001)
        if len(body) > 8_000_000:
            raise ValueError('metadata response exceeds 8 MB cap; not a complete response')
        row.update(bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
        if len(body) < 1_000_000 and 'application/pdf' not in content_type:
            target = ROOT / (name + '.body')
            target.write_bytes(body)
            row['body'] = str(target.relative_to(ROOT))
        else:
            target = SCRATCH / (name + '.body')
            target.write_bytes(body)
            row['body_external'] = str(target)
            (ROOT / (name + '.pointer.json')).write_text(json.dumps({'path': str(target), 'bytes': len(body), 'sha256': row['sha256']}, indent=2)+'\n')
    except Exception as e:
        row['error'] = type(e).__name__ + ': ' + str(e)
        row.setdefault('status', None)
    row['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (ROOT / (name + '.request.json')).write_text(json.dumps(row, indent=2, ensure_ascii=False)+'\n')
    return {k: row.get(k) for k in ('name','status','bytes','sha256','error')}

if __name__ == '__main__':
    plan = json.loads(Path(sys.argv[1]).read_text())
    assert len({x[0] for x in plan}) == len(plan)
    assert all(not (ROOT/(x[0]+'.request.json')).exists() for x in plan), 'Never overwrite receipts'
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(fetch, plan):
            print(json.dumps(result), flush=True)
