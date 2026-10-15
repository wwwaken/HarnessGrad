"""Read-only public acquisition; preserve successes/failures, decoded response bytes."""
import gzip
import hashlib
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def acquire(name, url):
    destination = ROOT / (name + '.body.gz')
    receipt_path = ROOT / (name + '.receipt.json')
    if destination.exists() or receipt_path.exists():
        raise SystemExit('Refusing existing acquisition name')
    receipt = {'url': url, 'requested_at_utc': datetime.now(timezone.utc).isoformat(),
               'proxy': 'http://127.0.0.1:17891', 'method': 'GET', 'timeout_s': 35}
    opener = urllib.request.build_opener(urllib.request.ProxyHandler(
        {'http': receipt['proxy'], 'https': receipt['proxy']}))
    request = urllib.request.Request(url, headers={'User-Agent': 'HarnessGrad-source-review'})
    body = b''
    try:
        with opener.open(request, timeout=receipt['timeout_s']) as response:
            body = response.read(25_000_001)
            if len(body) > 25_000_000:
                raise ValueError('response exceeds acquisition limit')
            receipt.update(status=response.status, final_url=response.url,
                           headers=dict(response.headers), error=None)
    except urllib.error.HTTPError as error:
        body = error.read()
        receipt.update(status=error.code, final_url=error.url,
                       headers=dict(error.headers), error=str(error))
    except Exception as error:
        receipt.update(status=None, error=f'{type(error).__name__}: {error}')
    destination.write_bytes(gzip.compress(body, mtime=0))
    receipt.update(body_gzip=destination.name, body_bytes=len(body),
                   body_sha256=hashlib.sha256(body).hexdigest(),
                   gzip_sha256=hashlib.sha256(destination.read_bytes()).hexdigest())
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, sort_keys=True))


if __name__ == '__main__':
    acquire(*sys.argv[1:])
