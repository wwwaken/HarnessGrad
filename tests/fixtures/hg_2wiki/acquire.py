"""Acquire bounded public documentation only; never download benchmark artifacts.

Each named attempt is append-only. Redirects and HTTP failures are preserved.
Use the canonical HG_EGRESS_PROXY and normal certificate validation.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
from urllib.error import HTTPError
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

ROOT = Path(__file__).resolve().parent
LIMIT = 4 * 1024 * 1024
PROXY = os.environ.get("HG_EGRESS_PROXY", "http://172.17.0.1:17890")
REQUESTS = {
    "original-share-page": "https://www.dropbox.com/s/9fwhnzektzv4wh5/data_ids.zip?dl=0",
    "publisher-paper": "https://aclanthology.org/2020.coling-main.580.pdf",
    "current-repository-license": "https://api.github.com/repos/Alab-NII/2wikimultihop/license?ref=main",
    "witness-card": "https://huggingface.co/datasets/framolfese/2WikiMultihopQA/resolve/fe713bfbd1afbca1a65246741a75890405d56a3a/README.md",
}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def allowed(url):
    p = urlsplit(url)
    if p.scheme != "https" or p.username or p.password:
        return False
    if p.hostname == "www.dropbox.com":
        return p.path == "/s/9fwhnzektzv4wh5/data_ids.zip" and p.query == "dl=0"
    if p.hostname == "aclanthology.org":
        return p.path == "/2020.coling-main.580.pdf"
    if p.hostname == "api.github.com":
        return p.path == "/repos/Alab-NII/2wikimultihop/license"
    return p.hostname == "huggingface.co" and p.path.endswith("/README.md") and (
        p.path.startswith("/datasets/framolfese/2WikiMultihopQA/resolve/")
        or p.path.startswith("/api/resolve-cache/datasets/framolfese/2WikiMultihopQA/")
    )


def acquire(name):
    directory = ROOT / name
    directory.mkdir()  # Deliberately refuses to overwrite any acquisition.
    url = REQUESTS[name]
    receipts = []
    opener = build_opener(ProxyHandler({"https": PROXY}), NoRedirect)
    for hop in range(5):
        receipt = dict(method="GET", url=url, started_at_utc=datetime.now(timezone.utc).isoformat(),
                       transport_proxy=PROXY, tls_certificate_validation=True,
                       publisher_signature_verified=False)
        if not allowed(url):
            receipt["error"] = "Refused URL outside documentation allowlist"
            receipts.append(receipt)
            break
        try:
            try:
                response = opener.open(Request(url, headers={
                    "User-Agent": "HarnessGrad-metadata-custody-review",
                    "Accept-Encoding": "identity",
                }), timeout=25)
            except HTTPError as error:
                response = error
            with response:
                headers = response.headers.as_bytes()
                (directory / f"hop-{hop}.headers").write_bytes(headers)
                receipt.update(status=response.code,
                               headers_sha256=hashlib.sha256(headers).hexdigest(),
                               headers_representation="HTTPMessage.as_bytes; parsed response headers")
                mime = response.headers.get_content_type()
                # Dropbox must return HTML documentation, never an archive or preview payload.
                if urlsplit(url).hostname == "www.dropbox.com" and mime != "text/html":
                    receipt["error"] = "Refused non-HTML Dropbox response before reading body"
                    receipts.append(receipt)
                    break
                body = response.read(LIMIT + 1)
                (directory / f"hop-{hop}.body").write_bytes(body)
                receipt.update(bytes=len(body), sha256=hashlib.sha256(body).hexdigest(),
                               complete=len(body) <= LIMIT, content_type=mime)
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
    return {"name": name, "hops": [{k: r[k] for k in ("status", "bytes", "sha256", "error") if k in r}
                                     for r in receipts]}


if __name__ == "__main__":
    names = sys.argv[1:] or list(REQUESTS)
    with ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(acquire, names):
            print(json.dumps(result), flush=True)
