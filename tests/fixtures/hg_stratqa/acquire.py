"""Bounded HTTPS source capture; never imports or executes downloaded content."""
import hashlib
import json
from pathlib import Path
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent
LIMIT = 950_000


def acquire(name, url, byte_range=None):
    if not name.replace("-", "").replace("_", "").isalnum():
        raise ValueError("Unsafe capture name")
    receipt_path = ROOT / (name + ".receipt.json")
    body_path = ROOT / (name + ".body")
    if receipt_path.exists() or body_path.exists():
        raise FileExistsError("Never overwrite a capture")
    hops = []

    class Redirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            hops.append({"url": req.full_url, "status": code,
                         "headers": list(headers.items()), "location": newurl})
            if urllib.parse.urlsplit(newurl).scheme != "https":
                raise ValueError("Refuse non-HTTPS redirect")
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    if urllib.parse.urlsplit(url).scheme != "https":
        raise ValueError("HTTPS required")
    result = {"url": url, "method": "GET", "tls": "ssl.create_default_context()",
              "request_headers": {"User-Agent": "HarnessGrad-source-audit/1.0",
                                  "Accept-Encoding": "identity"},
              "max_response_bytes": LIMIT, "redirects": hops}
    if byte_range is not None:
        result["request_headers"]["Range"] = byte_range
    request = urllib.request.Request(url, headers=result["request_headers"])
    opener = urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ssl.create_default_context()), Redirect())
    try:
        try:
            response = opener.open(request, timeout=35)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            result.update(final_url=response.geturl(), status=response.status,
                          response_headers=list(response.headers.items()))
            raw = response.read(LIMIT + 1)
            complete = len(raw) <= LIMIT
            raw = raw[:LIMIT]
            body_path.write_bytes(raw)
            result.update(body_path=body_path.relative_to(ROOT.parents[2]).as_posix(),
                          body_bytes=len(raw), body_sha256=hashlib.sha256(raw).hexdigest(),
                          complete=complete)
    except Exception as error:
        result.update(status=None, error=type(error).__name__ + ": " + str(error))
    receipt_path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"capture": name, **result}, sort_keys=True))


if __name__ == "__main__":
    acquire(*sys.argv[1:])
