"""One bounded HTTP request, run only as a trusted broker child (stdlib, no retries)."""
import json
import sys
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):
        raise RuntimeError('redirect refused')

try:
    request=json.load(sys.stdin)
    with build_opener(ProxyHandler({}),NoRedirect()).open(
            Request(request['url'],data=request['body'].encode(),headers=request['headers']),
            timeout=request['timeout']) as response:
        raw=response.read(8*1024*1024+1)
    if len(raw)>8*1024*1024:raise ValueError('response too large')
    sys.stdout.buffer.write(raw)
except Exception as exc:
    # Provider bodies/URLs/headers may contain secrets. Only the failure class leaves.
    sys.stderr.write(type(exc).__name__)
    sys.exit(1)
