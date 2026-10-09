#!/usr/bin/env python3
"""Host-side web search/fetch gateway for network-isolated task containers.

The ``web`` environment declaration is used instead of ``services`` because this is a
platform capability with host-side provider credentials, not a task-owned sidecar image.
The gateway is intentionally small and uses urllib so its host process needs no extra
package.  ``WebGateway`` is embedded by the runner and the CLI is useful for direct use.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DEFAULT_SEARXNG_URL = "http://127.0.0.1:8888"
# The platform's existing host egress chain. This is deliberately the same hop used by
# checks (`docs/egress.md`), rather than a second proxy invented for web tasks.
DEFAULT_WEB_PROXY = "http://172.17.0.1:17890"
MAX_FETCH_BYTES = 2_000_000
TIMEOUT_S = 30


class ProviderError(RuntimeError):
    """A provider failed; ``status`` and ``bytes`` still belong in the record."""

    def __init__(self, message: str, *, status: int = 0, bytes_: int = 0):
        super().__init__(message)
        self.status = status
        self.bytes = bytes_


def _json_request(url: str, payload: dict | None = None, headers: dict | None = None,
                  timeout: float = TIMEOUT_S) -> tuple[int, bytes]:
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=headers or {},
                                 method="POST" if data is not None else "GET")
    try:
        with _urlopen(req, timeout=timeout) as resp:
            return int(resp.status), resp.read()
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read()


def _urlopen(req: urllib.request.Request, *, timeout: float = TIMEOUT_S):
    """Open through the platform egress forwarder for non-local destinations."""
    host = urllib.parse.urlparse(req.full_url).hostname or ""
    if host in {"127.0.0.1", "localhost", "::1"}:
        return urllib.request.build_opener(urllib.request.ProxyHandler({})).open(
            req, timeout=timeout)
    proxy = os.environ.get("HG_WEB_PROXY", DEFAULT_WEB_PROXY)
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    return opener.open(req, timeout=timeout)


def parse_searxng(payload: dict, num: int = 10) -> list[dict]:
    return [{"title": str(r.get("title", "")), "url": str(r.get("url", "")),
             "snippet": str(r.get("content", r.get("snippet", "")))}
            for r in (payload.get("results") or [])[:num]
            if r.get("url")]


def parse_serper(payload: dict, num: int = 10) -> list[dict]:
    return [{"title": str(r.get("title", "")), "url": str(r.get("link", "")),
             "snippet": str(r.get("snippet", ""))}
            for r in (payload.get("organic") or [])[:num]
            if r.get("link")]


def parse_fetched(status: int, url: str, body: bytes) -> dict:
    text = body.decode("utf-8", errors="replace")
    return {"url": url, "status": status, "text": text, "bytes": len(body)}


def selected_providers() -> tuple[str, str, str | None]:
    search = os.environ.get("HG_WEB_SEARCH", "searxng").lower()
    fetch = os.environ.get("HG_WEB_FETCH", "http").lower()
    if search not in {"searxng", "serper", "google", "none"}:
        raise ValueError(f"unknown HG_WEB_SEARCH provider {search!r}")
    if fetch not in {"http", "crawl4ai", "jina"}:
        raise ValueError(f"unknown HG_WEB_FETCH provider {fetch!r}")
    missing = {"serper": ["SERPER_API_KEY"],
               "google": ["GOOGLE_API_KEY", "GOOGLE_CSE_ID"],
               "jina": ["JINA_API_KEY"]}
    required = missing.get(search, []) + missing.get(fetch, [])
    absent = [name for name in required if not os.environ.get(name)]
    if absent:
        provider = search if search in missing and not os.environ.get(missing[search][0]) else fetch
        raise ValueError(f"{provider} provider selected but required key(s) absent: {', '.join(absent)}")
    if fetch == "crawl4ai":
        try:
            import crawl4ai  # noqa: F401
        except ImportError as exc:
            raise ValueError("crawl4ai provider selected but crawl4ai is not installed") from exc
    endpoint = os.environ.get("HG_WEB_SEARXNG_URL", DEFAULT_SEARXNG_URL) if search == "searxng" else None
    return search, fetch, endpoint


class WebGateway:
    def __init__(self, *, bind_host: str = "127.0.0.1", port: int = 0,
                 record_path: str | Path | None = None,
                 enable_search: bool = True, enable_fetch: bool = True):
        self.bind_host, self.port = bind_host, port
        self.record_path = Path(record_path) if record_path else None
        self.search, self.fetch, self.searxng_url = selected_providers()
        self.enable_search, self.enable_fetch = enable_search, enable_fetch
        self._lock = threading.Lock()
        gateway = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                return

            def _send(self, status: int, obj: dict):
                data = json.dumps(obj, ensure_ascii=False).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers(); self.wfile.write(data)

            def _body(self):
                n = int(self.headers.get("Content-Length", "0"))
                return json.loads(self.rfile.read(n) or b"{}")

            def do_GET(self):
                if self.path == "/health":
                    self._send(200, {"ok": True, "search": gateway.search, "fetch": gateway.fetch})
                else:
                    self._send(404, {"error": "not found"})

            def do_POST(self):
                try:
                    payload = self._body()
                    if self.path == "/search":
                        if not gateway.enable_search:
                            self._send(404, {"error": "search was not declared for this task"}); return
                        result = gateway.search_request(str(payload["query"]), int(payload.get("num", 10)))
                    elif self.path == "/fetch":
                        if not gateway.enable_fetch:
                            self._send(404, {"error": "fetch was not declared for this task"}); return
                        result = gateway.fetch_request(str(payload["url"]), payload.get("query"))
                    else:
                        self._send(404, {"error": "not found"}); return
                    self._send(200, result)
                except (KeyError, ValueError, urllib.error.URLError, ProviderError) as exc:
                    self._send(502, {"error": str(exc)})
                except Exception as exc:  # provider failures must be visible to the task
                    self._send(502, {"error": f"{type(exc).__name__}: {exc}"})

        self.server = ThreadingHTTPServer((bind_host, port), Handler)
        self.port = self.server.server_address[1]
        self._thread = None

    @property
    def url(self) -> str:
        return f"http://{self.bind_host}:{self.port}"

    def _record(self, kind: str, target: str, status: int, bytes_: int):
        if not self.record_path: return
        row = {"timestamp": time.time(), "kind": kind, "url": target,
               "provider": self.search if kind == "search" else self.fetch,
               "status": status, "bytes": bytes_}
        self.record_path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock, self.record_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    def search_request(self, query: str, num: int) -> dict:
        num = max(1, min(int(num), 50))
        status, body, results = 0, b"", []
        try:
            if self.search == "none":
                status = 200
            elif self.search == "searxng":
                status, body = _json_request(
                    (self.searxng_url or DEFAULT_SEARXNG_URL).rstrip("/") + "/search?" +
                    urllib.parse.urlencode({"q": query, "format": "json"}))
                if status >= 400:
                    raise ProviderError(f"searxng returned HTTP {status}", status=status,
                                        bytes_=len(body))
                results = parse_searxng(json.loads(body), num)
            elif self.search == "serper":
                status, body = _json_request(
                    "https://google.serper.dev/search", {"q": query, "num": num},
                    {"X-API-KEY": os.environ["SERPER_API_KEY"],
                     "Content-Type": "application/json"})
                if status >= 400:
                    raise ProviderError(f"serper returned HTTP {status}", status=status,
                                        bytes_=len(body))
                results = parse_serper(json.loads(body), num)
            else:
                url = "https://www.googleapis.com/customsearch/v1?" + urllib.parse.urlencode({
                    "key": os.environ["GOOGLE_API_KEY"], "cx": os.environ["GOOGLE_CSE_ID"],
                    "q": query, "num": num})
                status, body = _json_request(url)
                if status >= 400:
                    raise ProviderError(f"google returned HTTP {status}", status=status,
                                        bytes_=len(body))
                payload = json.loads(body)
                results = parse_serper({"organic": [
                    {"title": x.get("title"), "link": x.get("link"),
                     "snippet": x.get("snippet")} for x in payload.get("items", [])]}, num)
            return {"results": results}
        except ProviderError:
            raise
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            raise ProviderError(f"{self.search} provider failed: {exc}", status=status,
                                bytes_=len(body)) from exc
        finally:
            self._record("search", query, status, len(body))

    def fetch_request(self, url: str, query: str | None = None) -> dict:
        status, body, target = 0, b"", url
        try:
            scheme = urllib.parse.urlparse(url).scheme.lower()
            if scheme not in {"http", "https"}:
                raise ProviderError(f"fetch URL must use http or https, got {scheme or 'none'}")
            if self.fetch == "http":
                req = urllib.request.Request(url, headers={"User-Agent": "HarnessGrad web gateway"})
                with _urlopen(req, timeout=TIMEOUT_S) as resp:
                    status, body = int(resp.status), resp.read(MAX_FETCH_BYTES + 1)
            elif self.fetch == "jina":
                req = urllib.request.Request("https://r.jina.ai/" + url,
                    headers={"Authorization": "Bearer " + os.environ["JINA_API_KEY"]})
                with _urlopen(req, timeout=TIMEOUT_S) as resp:
                    status, body = int(resp.status), resp.read(MAX_FETCH_BYTES + 1)
            else:
                from crawl4ai import AsyncWebCrawler

                async def crawl():
                    async with AsyncWebCrawler() as crawler:
                        return await crawler.arun(url=url)

                result = asyncio.run(crawl())
                status = 200
                body = (result.markdown or result.cleaned_html or "").encode("utf-8")
            body = body[:MAX_FETCH_BYTES]
            return parse_fetched(status, target, body)
        except urllib.error.HTTPError as exc:
            status, body = int(exc.code), exc.read(MAX_FETCH_BYTES)
            return parse_fetched(status, target, body)
        except ProviderError:
            raise
        except (OSError, ValueError, RuntimeError) as exc:
            raise ProviderError(f"{self.fetch} provider failed: {exc}", status=status,
                                bytes_=len(body)) from exc
        finally:
            self._record("fetch", url, status, len(body))

    def start(self):
        self._thread = threading.Thread(target=self.server.serve_forever, daemon=True); self._thread.start(); return self

    def stop(self):
        self.server.shutdown(); self.server.server_close()
        if self._thread: self._thread.join(timeout=5)


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--bind", default="127.0.0.1"); ap.add_argument("--port", type=int, default=8787); ap.add_argument("--record"); args = ap.parse_args(argv)
    try: gateway = WebGateway(bind_host=args.bind, port=args.port, record_path=args.record).start()
    except ValueError as exc: print(str(exc), file=sys.stderr); return 2
    print(gateway.url, flush=True)
    try:
        while True: time.sleep(3600)
    except KeyboardInterrupt: gateway.stop()
    return 0

if __name__ == "__main__": raise SystemExit(main())
