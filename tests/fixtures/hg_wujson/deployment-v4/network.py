"""Observe container interfaces/routes and a denied connection to a reserved IP."""
import errno
import json
from pathlib import Path
import socket

interfaces = sorted(p.name for p in Path('/sys/class/net').iterdir())
routes = Path('/proc/net/route').read_text()
assert interfaces == ['lo'], interfaces
assert len(routes.splitlines()) == 1, routes
with socket.socket() as sock:
    sock.settimeout(2)
    result = sock.connect_ex(('203.0.113.1', 443))
assert result == errno.ENETUNREACH, result
print(json.dumps({'interfaces': interfaces, 'ipv4_routes': routes,
                  'reserved_documentation_ip': '203.0.113.1',
                  'connect_ex_errno': result, 'errno_name': errno.errorcode[result],
                  'passed': True}, indent=2))
