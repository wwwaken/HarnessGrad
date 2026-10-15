#!/usr/bin/env python3
"""Acquire only the two named public metadata objects; retain every attempt."""
import concurrent.futures
import datetime
import hashlib
import json
from pathlib import Path
import shlex
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent
LIMIT = 900_000


class RedirectRecorder(urllib.request.HTTPRedirectHandler):
    def __init__(self):
        self.rows = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        body = fp.read(LIMIT + 1)
        if len(body) > LIMIT:
            raise ValueError("redirect response exceeds metadata cap")
        self.rows.append(dict(url=req.full_url, status=code, location=newurl,
                              headers=list(headers.items()), body_hex=body.hex(),
                              bytes=len(body), sha256=hashlib.sha256(body).hexdigest()))
        if not newurl.startswith("https://"):
            raise ValueError("HTTPS downgrade refused")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(item):
    name, url, proxy = item
    assert url.startswith("https://huggingface.co/")
    assert ("/tree/ad8321607bcad0e534c243ec8c108a5787cea6c8" in url
            or "/1776db7e9abab525eae8e59c5015e3589dfe371b/fever_gold_evidence.py" in url)
    target = ROOT / (name + ".request.json")
    body_target = ROOT / (name + ".body")
    assert not target.exists() and not body_target.exists(), "Never overwrite receipts"
    redirects = RedirectRecorder()
    headers = {"User-Agent": "HarnessGrad-fevobj-provenance/1",
               "Accept-Encoding": "identity",
               "Host": urllib.parse.urlsplit(url).netloc, "Connection": "close"}
    row = dict(name=name, url=url, method="GET", proxy=proxy or None,
               command=shlex.join(["python3", *sys.argv]),
               timeout_seconds=25, response_cap_bytes=LIMIT, request_headers=headers,
               tls_verification="ssl.create_default_context(): CA and hostname verification",
               started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
               redirects=redirects.rows, status=None, bytes=None, sha256=None, body=None)
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({"http": proxy, "https": proxy} if proxy else {}),
        urllib.request.HTTPSHandler(context=ssl.create_default_context()), redirects)
    try:
        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            response = opener.open(req, timeout=25)
        except urllib.error.HTTPError as exc:
            response = exc
        with response:
            row.update(status=response.code, final_url=response.geturl(),
                       response_headers=list(response.headers.items()))
            body = response.read(LIMIT + 1)
        if len(body) > LIMIT:
            raise ValueError("response exceeds metadata cap; incomplete response not retained")
        body_target.write_bytes(body)
        row.update(bytes=len(body), sha256=hashlib.sha256(body).hexdigest(),
                   body=str(body_target.relative_to(ROOT)))
    except Exception as exc:
        row["error"] = type(exc).__name__ + ": " + str(exc)
    row["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    target.write_text(json.dumps(row, indent=2, ensure_ascii=False) + "\n")
    return {key: row.get(key) for key in ("name", "status", "bytes", "sha256", "error")}


if __name__ == "__main__":
    plan = json.loads(Path(sys.argv[1]).read_text())
    assert len({item[0] for item in plan}) == len(plan)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for result in pool.map(fetch, plan):
            print(json.dumps(result), flush=True)
