#!/usr/bin/env python3
"""Acquire only the explicitly listed public provenance responses; never payloads.

Existing response names are immutable: reruns refuse to overwrite them.
Redirect responses are retained, not automatically followed. TLS uses the
Python default certificate/hostname verification. No credentials are sent.
"""
import concurrent.futures
import datetime
import hashlib
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request

HERE = Path(__file__).resolve().parent
REV = "0f7faf33a3908546c6fd5b73a660e0f8ff173c2f"
PRE = "d63a76f01c8226449f76b437dd512cf8b17adf5d"
API = "https://huggingface.co/api/datasets/mandarjoshi/trivia_qa"
RAW = "https://huggingface.co/datasets/mandarjoshi/trivia_qa/raw"
QUERY = "?recursive=false&expand=false"
REQUESTS = {
    "hub-revision": f"{API}/revision/{REV}",
    "hub-root-tree": f"{API}/tree/{REV}{QUERY}",
    "hub-selected-tree": f"{API}/tree/{REV}/rc.nocontext{QUERY}",
    "hub-commits": f"{API}/commits/{REV}",
    "hub-discussion-8": f"{API}/discussions/8",
    "hub-predecessor-tree": f"{API}/tree/{PRE}{QUERY}",
    "hub-input-tree": f"{API}/tree/{PRE}/data{QUERY}",
    "hub-predecessor-loader": f"{RAW}/{PRE}/trivia_qa.py",
    "hub-recursive-tree": f"{API}/tree/{REV}?recursive=true&expand=false",
    "hub-initial-commits": f"{API}/commits/6baa09772e6ddf7e7b5d629ea64f1a8c1df21c3c",
    "hub-added-selected-tree": f"{API}/tree/279d93a6e999c93dc992e1a705389e350ba7f706/rc.nocontext{QUERY}",
    "upstream-scorer": "https://raw.githubusercontent.com/mandarjoshi90/triviaqa/ca43b5820b107f3970cf4b7d67f7db7a98117b79/evaluation/triviaqa_evaluation.py",
    "upstream-license": "https://raw.githubusercontent.com/mandarjoshi90/triviaqa/ca43b5820b107f3970cf4b7d67f7db7a98117b79/LICENSE",
}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def acquire(name):
    url = REQUESTS[name]
    directory = HERE / "responses"
    directory.mkdir(exist_ok=True)
    receipt_path = directory / f"{name}.receipt.json"
    body_path = directory / f"{name}.body"
    headers_path = directory / f"{name}.headers"
    if any(p.exists() for p in (receipt_path, body_path, headers_path)):
        raise FileExistsError(f"refuse overwrite: {name}")
    proxy = os.environ.get("HG_EGRESS_PROXY", "http://172.17.0.1:17890")
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({"http": proxy, "https": proxy}), NoRedirect())
    request_headers = {"User-Agent": "HarnessGrad-w-trivia-provenance/1", "Accept-Encoding": "identity"}
    receipt = {"url": url, "method": "GET", "proxy": proxy,
               "request_headers": request_headers, "started_at_utc": now(),
               "tls_verification": "default CA and hostname verification; no override",
               "redirects_followed": False}
    try:
        try:
            response = opener.open(urllib.request.Request(url, headers=request_headers), timeout=45)
        except urllib.error.HTTPError as exc:
            response = exc
        with response:
            body = response.read()
            headers = response.headers.as_bytes()
            body_path.write_bytes(body)
            headers_path.write_bytes(headers)
            receipt.update(status=response.code, response_url=response.geturl(),
                           body=body_path.name, size_bytes=len(body),
                           sha256=hashlib.sha256(body).hexdigest(),
                           headers=headers_path.name,
                           headers_sha256=hashlib.sha256(headers).hexdigest())
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        receipt.update(error_type=type(exc).__name__, error=str(exc))
    receipt["finished_at_utc"] = now()
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(name, receipt.get("status", receipt.get("error")), receipt.get("sha256", "no response"), flush=True)


if __name__ == "__main__":
    names = sys.argv[1:] or list(REQUESTS)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(acquire, names))
