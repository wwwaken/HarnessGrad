"""Retain source responses without executing upstream code or exposing answers."""
import hashlib
import json
from pathlib import Path
import shlex
import ssl
import sys
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent
STORE = Path('/mnt/20t/xubuqiang/hg-work/stratsplit')
LIMIT = 15_000_000

def capture(name, url):
    receipt = ROOT / (name + '.receipt.json')
    body = ROOT / (name + '.body')
    target = STORE / (name + '.body')
    assert not receipt.exists() and not body.exists() and not target.exists()
    hops = []
    class HTTPSRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            assert newurl.startswith('https://')
            hops.append({'url': req.full_url, 'status': code, 'location': newurl})
            return super().redirect_request(req, fp, code, msg, headers, newurl)
    assert url.startswith('https://')
    headers = {'User-Agent': 'HarnessGrad-stratsplit-source-audit/1.0',
               'Accept-Encoding': 'identity'}
    record = {'url': url, 'command': shlex.join(
        ['python3', 'tests/fixtures/hg_stratsplit/capture.py', name, url]),
        'request_headers': headers, 'redirects': hops, 'limit_bytes': LIMIT}
    opener = urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ssl.create_default_context()), HTTPSRedirect())
    try:
        try:
            response = opener.open(urllib.request.Request(url, headers=headers), timeout=40)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            record.update(status=response.status, final_url=response.geturl(),
                          headers=list(response.headers.items()))
            raw = response.read(LIMIT + 1)
            record['complete'] = len(raw) <= LIMIT
            target.write_bytes(raw)
            body.symlink_to(target)
            record.update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                          raw_fixture=str(body.relative_to(ROOT.parents[2])),
                          persistent_body=str(target))
    except Exception as error:
        record.update(status=None, error=type(error).__name__ + ': ' + str(error))
    receipt.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, sort_keys=True))

if __name__ == '__main__':
    capture(*sys.argv[1:])
