#!/usr/bin/env python3
"""The HarnessGrad read API -- a small, dependency-free HTTP server.

    python3 web/server/serve.py --port 8791 --runs-root runs

Six endpoints under ``/api/`` and a static fallback to ``web/dist`` so the built
SPA works as one artifact:

    GET /api/health
    GET /api/runs
    GET /api/runs/<id>
    GET /api/runs/<id>/rounds/<n>/diff
    GET /api/runs/<id>/rounds/<n>/tasks/<task>
    GET /api/launch/options

**It is read-only.**  Nothing in this server opens a file under ``runs/`` for
writing, creates a directory, or deletes anything.  See ``README.md``.

Only the Python standard library is used: ``http.server``, ``json``, ``pathlib``.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import re
import sys
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

# Never leave a `.pyc` in the platform tree: this process is an observer, and a
# write anywhere under `harnessgrad/` would be a write the integrity check is
# designed to catch.  Must be set before the imports below.
sys.dont_write_bytecode = True

sys.path.insert(0, str(Path(__file__).resolve().parent))
import launch as launch_options  # noqa: E402
import readapi  # noqa: E402

REPO = readapi.REPO

#: The order matters only in that `runs/<id>` is checked after the two nested
#: routes; its `[^/]+` component can never match them anyway.
_ROUTES = (
    ("health", re.compile(r"^/api/health/?$")),
    ("launch", re.compile(r"^/api/launch/options/?$")),
    ("run_diff", re.compile(
        r"^/api/runs/(?P<run>[^/]+)/rounds/(?P<round>[^/]+)/diff/?$")),
    ("run_task", re.compile(
        r"^/api/runs/(?P<run>[^/]+)/rounds/(?P<round>[^/]+)/tasks/(?P<task>[^/]+)/?$")),
    ("run", re.compile(r"^/api/runs/(?P<run>[^/]+)/?$")),
    ("runs", re.compile(r"^/api/runs/?$")),
)


class ApiHandler(BaseHTTPRequestHandler):
    """Every response is JSON, including every error.  No tracebacks on the wire."""

    server_version = "HarnessGradReadAPI/1.0"
    protocol_version = "HTTP/1.1"

    # -- plumbing ----------------------------------------------------------

    def log_message(self, fmt: str, *args) -> None:  # noqa: A003 - stdlib name
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        # The tree is being written while it is served; a cached list would be a
        # lie the moment a round lands.  `no-store` also keeps an old 404 from
        # sticking after a run appears.
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        # Read-only and unauthenticated by design; this only lets the Vite dev
        # server (port 5273) point at the API during development.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, status: int, payload: object) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=1).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def _error(self, status: int, code: str, message: str, **extra: object) -> None:
        body = {"error": code, "status": status, "message": message}
        body.update(extra)
        self._json(status, body)

    # -- entry points ------------------------------------------------------

    def do_GET(self) -> None:  # noqa: N802 - stdlib name
        self._handle(head_only=False)

    def do_HEAD(self) -> None:  # noqa: N802 - stdlib name
        self._handle(head_only=True)

    def _handle(self, *, head_only: bool) -> None:
        try:
            path = unquote(urlsplit(self.path).path)
            if path.startswith("/api/") or path == "/api":
                self._dispatch_api(path)
            else:
                self._serve_spa(path)
        except (BrokenPipeError, ConnectionResetError):
            return  # the client left; nothing to report
        except Exception:  # noqa: BLE001 - the contract is a body, not a traceback
            traceback.print_exc()
            try:
                self._json(500, {
                    "error": "internal",
                    "status": 500,
                    "message": "the read API hit an unexpected error; "
                               "the traceback is on the server's stderr",
                })
            except Exception:  # noqa: BLE001 - the socket is already gone
                pass

    # -- /api --------------------------------------------------------------

    def _dispatch_api(self, path: str) -> None:
        # A `..` or `.` segment is refused before any path is built, so
        # `/api/runs/../driver.py` cannot reach the router's `run` component at
        # all -- and neither can a percent-encoded spelling of it.
        segments = [segment for segment in path.split("/") if segment]
        if any(segment in (".", "..") for segment in segments):
            self._error(400, "invalid-path",
                        "path traversal is refused: `..` and `.` are not path components",
                        path=path)
            return

        for name, pattern in _ROUTES:
            match = pattern.match(path)
            if match:
                self._route(name, match.groupdict())
                return
        self._error(404, "not-found", f"no such endpoint: {path}", path=path)

    def _route(self, name: str, params: dict[str, str]) -> None:
        runs_root: Path = self.server.runs_root  # type: ignore[attr-defined]
        if name == "health":
            self._json(200, {"ok": True, "runs": len(readapi.iter_run_names(runs_root))})
            return
        if name == "runs":
            self._json(200, readapi.list_runs(runs_root))
            return
        if name == "launch":
            self._json(200, launch_options.build_launch_options(REPO))
            return

        run_id = params.get("run", "")
        if not readapi.is_safe_component(run_id):
            self._error(400, "invalid-run-id",
                        f"`{run_id}` is not a usable run id: expected one path "
                        "component of letters, digits, `_`, `-` and `.`, with no `..`",
                        run_id=run_id)
            return
        run_dir = runs_root / run_id
        if not run_dir.is_dir():
            self._error(404, "run-not-found",
                        f"no directory runs/{run_id}", run_id=run_id)
            return

        if name == "run":
            self._json(200, readapi.run_bundle(runs_root, run_id))
            return

        round_raw = params.get("round", "")
        if not round_raw.isdigit():
            self._error(400, "invalid-round",
                        f"`{round_raw}` is not a round number", run_id=run_id,
                        round=round_raw)
            return
        round_no = int(round_raw)

        if name == "run_diff":
            body = readapi.round_diff(runs_root, run_id, round_no)
            if body is None:
                # Round 0 has no diff by construction; a round that has not been
                # measured yet has none either.  This is an absence, told apart
                # from an error by the status code.
                self._error(404, "diff-not-found",
                            f"no saved patch for round {round_no} of run `{run_id}`",
                            run_id=run_id, round=round_no)
                return
            self._json(200, body)
            return

        if name == "run_task":
            task_id = params.get("task", "")
            if not readapi.is_safe_component(task_id):
                self._error(400, "invalid-task-id",
                            f"`{task_id}` is not a usable task id", run_id=run_id,
                            round=round_no, task_id=task_id)
                return
            self._json(200, readapi.task_page(runs_root, run_id, round_no, task_id))
            return

        self._error(404, "not-found", f"no such endpoint: {self.path}")

    # -- static SPA --------------------------------------------------------

    def _serve_spa(self, path: str) -> None:
        dist: Path = self.server.web_dist  # type: ignore[attr-defined]
        if not dist.is_dir():
            self._error(404, "spa-not-built",
                        f"no SPA build at {dist}; run `pnpm build` in web/ or use "
                        "the /api/ endpoints", path=path)
            return

        index = dist / "index.html"
        relative = path.lstrip("/")
        candidate = dist / relative if relative else index
        try:
            resolved = candidate.resolve()
            roots = {dist.resolve(), index.resolve()}
            if resolved in roots or dist.resolve() in resolved.parents:
                if candidate.is_file():
                    self._send_file(candidate)
                    return
        except OSError:
            pass
        # A client-side route (`/runs/ds-dgm`) is not a file: hand back the shell.
        if index.is_file():
            self._send_file(index)
        else:
            self._error(404, "not-found", f"no such path: {path}", path=path)

    def _send_file(self, path: Path) -> None:
        try:
            body = path.read_bytes()
        except OSError as exc:
            self._error(404, "not-found", f"cannot read {path.name}: {exc}")
            return
        content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        if content_type.startswith("text/") or content_type in (
                "application/javascript", "application/json", "image/svg+xml"):
            content_type += "; charset=utf-8"
        self._send(200, body, content_type)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="serve.py",
        description="The HarnessGrad read API (read-only) plus the built SPA.")
    parser.add_argument("--port", type=int, default=8791)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--runs-root", default=str(REPO / "runs"),
                        help="the runs/ tree to read (never written)")
    parser.add_argument("--web-dist", default=str(REPO / "web" / "dist"),
                        help="the built SPA; served for every non-/api path")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    runs_root = Path(args.runs_root).expanduser().resolve()
    web_dist = Path(args.web_dist).expanduser().resolve()
    if not runs_root.is_dir():
        print(f"warning: --runs-root {runs_root} is not a directory", file=sys.stderr)

    httpd = ThreadingHTTPServer((args.host, args.port), ApiHandler)
    httpd.daemon_threads = True
    httpd.runs_root = runs_root      # type: ignore[attr-defined]
    httpd.web_dist = web_dist        # type: ignore[attr-defined]
    print(f"HarnessGrad read API on http://{args.host}:{args.port}", file=sys.stderr)
    print(f"  runs-root: {runs_root}", file=sys.stderr)
    print(f"  web-dist:  {web_dist}"
          f"{'' if web_dist.is_dir() else '  (not built: /api only)'}", file=sys.stderr)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
