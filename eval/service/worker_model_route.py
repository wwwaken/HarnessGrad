"""One fixed chat-completions HTTP operation over a private worker Unix socket.

Unlike a generic TCP tunnel, requests cannot select another route or protocol.
Streaming bodies are forwarded without buffering the episode or changing budgets.
"""
import http.client
import hashlib
from http.server import BaseHTTPRequestHandler
import os
from pathlib import Path
import shutil
import socketserver
import tempfile
import threading
from urllib.parse import urlsplit


class ModelRoute:
    def __init__(self, base_url, *, timeout_s):
        url = urlsplit(base_url)
        if (url.scheme != 'http' or not url.hostname or url.username or url.password
                or url.query or url.fragment):
            raise ValueError('worker model requires an explicit plain HTTP endpoint')
        self.endpoint_sha256 = hashlib.sha256(base_url.encode()).hexdigest()
        self.target = (url.hostname, url.port or 80)
        self.url_path = url.path.rstrip('/')
        self.operation = self.url_path + '/chat/completions'
        self.timeout_s = timeout_s
        self.faults = []; self.calls = 0; self.connections = set(); self.clients = set(); self.lock = threading.Lock(); self.stopped = False
        self.directory = None; self.server = None; self.thread = None

    def start(self):
        owner = self
        class Server(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
            daemon_threads = True
            def get_request(self):
                client, address = super().get_request()
                client.settimeout(min(30, owner.timeout_s))
                with owner.lock:
                    if owner.stopped or len(owner.clients) >= 16:
                        client.close()
                        owner.faults.append('model connection limit')
                        raise OSError('route closed or full')
                    owner.clients.add(client)
                return client, address
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args): pass
            def finish(self):
                try: super().finish()
                finally:
                    with owner.lock: owner.clients.discard(self.request)
            def do_POST(self):
                if (self.path != owner.operation or self.headers.get('Transfer-Encoding')
                        or len(self.headers.get_all('Content-Length', [])) != 1):
                    owner.faults.append('unauthorized operation or framing')
                    self.send_error(403); return
                try:
                    size = int(self.headers['Content-Length'])
                    if not 0 < size <= 16 << 20: raise ValueError('model request byte limit')
                    self.connection.settimeout(owner.timeout_s)
                    body = self.rfile.read(size)
                    if len(body) != size: raise ValueError('short model request')
                    conn = http.client.HTTPConnection(*owner.target, timeout=owner.timeout_s)
                    with owner.lock:
                        owner.calls += 1; owner.connections.add(conn)
                    try:
                        headers = {'Content-Type': 'application/json', 'Connection': 'close'}
                        if self.headers.get('Authorization'): headers['Authorization'] = self.headers['Authorization']
                        conn.request('POST', owner.operation, body=body, headers=headers)
                        reply = conn.getresponse()
                        if reply.status != 200:
                            owner.faults.append('provider HTTP failure'); self.send_error(502); return
                        self.send_response(200)
                        self.send_header('Content-Type', reply.getheader('Content-Type', 'application/json'))
                        self.send_header('Connection', 'close'); self.end_headers()
                        total = 0
                        while chunk := reply.read1(65536):
                            total += len(chunk)
                            if total > 64 << 20: raise ValueError('model response byte limit')
                            self.wfile.write(chunk); self.wfile.flush()
                    finally:
                        conn.close()
                        with owner.lock: owner.connections.discard(conn)
                except (OSError, ValueError, http.client.HTTPException):
                    owner.faults.append('model transport failure')
                    self.close_connection = True
            def do_GET(self):
                owner.faults.append('unauthorized operation'); self.send_error(403)
            do_CONNECT = do_GET
            do_PUT = do_GET
            do_DELETE = do_GET
            do_HEAD = do_GET
            do_OPTIONS = do_GET
            do_PATCH = do_GET
        try:
            self.directory = Path(tempfile.mkdtemp(prefix='hg-worker-model-'))
            self.path = self.directory / 'model.sock'
            self.server = Server(str(self.path), Handler)
            os.chmod(self.path, 0o666)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True); self.thread.start()
            return self
        except BaseException:
            self.stop(); raise

    def report(self):
        return {'operation': 'POST ' + self.operation, 'endpoint_sha256': self.endpoint_sha256, 'transport': 'unix+isolated-loopback',
                'calls': self.calls, 'faults': list(self.faults),
                'limits': {'connections': 16, 'request_bytes': 16 << 20, 'response_bytes': 64 << 20},
                'cleanup': {'complete': self.stopped and not self.connections and not self.clients}}

    def stop(self):
        with self.lock:
            self.stopped = True
            for client in self.clients:
                try: client.shutdown(2)
                except OSError: pass
                client.close()
            for conn in self.connections:
                if conn.sock:
                    try: conn.sock.shutdown(2)
                    except OSError: pass
                conn.close()
        if self.thread:
            self.server.shutdown(); self.thread.join(timeout=5)
        if self.server: self.server.server_close()
        if self.directory: shutil.rmtree(self.directory)
        # Closing sockets wakes all handlers; a short bounded join records lag.
        import time
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            with self.lock:
                if not self.connections and not self.clients: break
            time.sleep(.01)
