"""Bounded public metadata/code acquisition; retain each HTTP hop unchanged.

Run from this worktree: python3 reports/b6-blocker-evidence/acquire.py NAME URL
Never use for benchmark payloads. No credentials, retries or response rewriting.
"""
import hashlib
import json
from pathlib import Path
import sys
from datetime import datetime, timezone
from urllib.error import HTTPError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

ROOT = Path(__file__).resolve().parent
LIMIT = 2 * 1024 * 1024


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def acquire(name, url, proxy=None):
    directory = ROOT / name
    directory.mkdir()  # Refuse overwrite of an earlier acquisition.
    receipts = []
    if proxy is not None:
        assert proxy == "http://127.0.0.1:17891", "only the existing recorded egress route"
    opener = build_opener(ProxyHandler({"https": proxy} if proxy else {}), NoRedirect)
    for hop in range(6):
        parsed = urlparse(url)
        assert parsed.scheme == "https" and parsed.hostname in {
            "huggingface.co", "api.github.com", "raw.githubusercontent.com",
            "dns.google", "cloudflare-dns.com", "1.1.1.1", "dns.alidns.com",
            "hf.co", "www.huggingface.co", "hf-mirror.com"
        }
        assert not parsed.username and not parsed.password
        assert not any(s in parsed.path for s in (
            "/rows", "/first-rows", ".parquet", ".jsonl", "/dev.json",
            "/train.json", "/id_aliases.json", "/prediction_format.json"
        )), "payload URL refused"
        receipt = {"url": url, "started_at_utc": datetime.now(timezone.utc).isoformat()}
        if proxy:
            receipt["transport_proxy"] = proxy
        try:
            try:
                response = opener.open(Request(url, headers={
                    "User-Agent": "HarnessGrad-public-metadata-review",
                    "Accept-Encoding": "identity",
                    "Accept": "application/dns-json" if "dns-query" in url else "*/*",
                }), timeout=18)
            except HTTPError as error:
                response = error
            with response:
                body = response.read(LIMIT + 1)
                body_path = directory / f"hop-{hop}.body"
                body_path.write_bytes(body)
                header_bytes = response.headers.as_bytes()
                (directory / f"hop-{hop}.headers").write_bytes(header_bytes)
                receipt.update(status=response.code, bytes=len(body),
                               sha256=hashlib.sha256(body).hexdigest(),
                               headers_sha256=hashlib.sha256(header_bytes).hexdigest(),
                               complete=len(body) <= LIMIT)
                location = response.headers.get("Location")
        except Exception as error:
            receipt["error"] = f"{type(error).__name__}: {error}"
            receipts.append(receipt)
            break
        receipts.append(receipt)
        if receipt["complete"] and receipt["status"] in (301, 302, 303, 307, 308) and location:
            url = urljoin(url, location)
        else:
            break
    (directory / "receipt.json").write_text(json.dumps(receipts, indent=2) + "\n")
    print(json.dumps({"name": name, "receipts": receipts}))


if __name__ == "__main__":
    acquire(*sys.argv[1:])
