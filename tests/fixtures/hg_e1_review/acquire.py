"""Acquire public source evidence; preserve every response, including failures.

Run from the worktree: python3 tests/fixtures/hg_e1_review/acquire.py NAME URL
Bodies are kept as received after HTTP transport decoding. No downloaded code runs.
"""
import hashlib
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def acquire(name, url, proxy=None):
    root = Path(__file__).resolve().parent
    receipt_path = root / f"{name}.receipt.json"
    if receipt_path.exists():
        raise SystemExit(f"Refusing to overwrite {receipt_path}")
    request = urllib.request.Request(url, headers={"User-Agent": "HarnessGrad-source-review", "Accept": "application/json"})
    receipt = {"url": url, "requested_at_utc": datetime.now(timezone.utc).isoformat(),
               "method": "GET", "timeout_s": 25}
    if proxy is not None:
        assert proxy == "http://127.0.0.1:17891", "only the existing recorded public egress route"
        receipt["transport_proxy"] = proxy
    body = b""
    try:
        opener = (urllib.request.build_opener(urllib.request.ProxyHandler({"https": proxy}))
                  if proxy else urllib.request.build_opener())
        with opener.open(request, timeout=25) as response:
            body = response.read(20_000_001)
            if len(body) > 20_000_000:
                raise ValueError("response exceeds review evidence limit")
            receipt.update(status=response.status, final_url=response.url,
                           headers=dict(response.headers), error=None)
    except urllib.error.HTTPError as error:
        body = error.read()
        receipt.update(status=error.code, final_url=error.url,
                       headers=dict(error.headers), error=str(error))
    except Exception as error:
        receipt.update(status=None, error=f"{type(error).__name__}: {error}")
    destination = root / f"{name}.body"
    destination.write_bytes(body)
    receipt.update(body=destination.name, bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({key: receipt[key] for key in ("url", "status", "bytes", "sha256", "error")}))


if __name__ == "__main__":
    acquire(*sys.argv[1:])
