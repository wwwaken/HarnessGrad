"""Public metadata only; preserve every HTTP entity, without replacing attempts.

No dataset rows, statements, tests, shards, converted parquet or model calls.
The OpenAPI contract must be reviewed before adding any projected-row request.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

HERE = Path(__file__).resolve().parent
REVISION = '0fe84c3912ea0c4d4a78037083943e8f0c4dd505'
DATASET = 'livecodebench/code_generation_lite'
QUERY = urlencode(dict(dataset=DATASET, revision=REVISION))
CONFIG_QUERY = QUERY + '&config=release_v6'
REQUESTS = {
    'viewer-openapi-contract': 'https://raw.githubusercontent.com/huggingface/dataset-viewer/main/docs/source/openapi.json',
    'viewer-openapi': 'https://datasets-server.huggingface.co/openapi.json',
    'viewer-splits': 'https://datasets-server.huggingface.co/splits?' + QUERY,
    'viewer-size': 'https://datasets-server.huggingface.co/size?' + CONFIG_QUERY,
    'viewer-info': 'https://datasets-server.huggingface.co/info?' + CONFIG_QUERY,
}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def acquire(name):
    url = REQUESTS[name]
    directory = HERE / name
    directory.mkdir()  # Fail rather than overwrite a prior response.
    proxy = os.environ.get('HG_EGRESS_PROXY', 'http://172.17.0.1:17890')
    receipt = dict(url=url, method='GET', started_at_utc=datetime.now(timezone.utc).isoformat(),
                   proxy=proxy, tls_certificate_validation=True, publisher_signature_verified=False,
                   request_headers={'Accept-Encoding': 'identity', 'User-Agent': 'HarnessGrad-w-lcb-metadata-review'})
    opener = build_opener(ProxyHandler({'https': proxy}), NoRedirect)
    try:
        try:
            response = opener.open(Request(url, headers=receipt['request_headers']), timeout=25)
        except HTTPError as error:
            response = error
        with response:
            headers = response.headers.as_bytes()
            (directory / 'response.headers').write_bytes(headers)
            limit = 4 * 1024 * 1024
            body = response.read(limit + 1)
            (directory / 'response.body').write_bytes(body)
            receipt.update(status=response.code, bytes=len(body), complete=len(body) <= limit,
                           sha256=hashlib.sha256(body).hexdigest(),
                           headers_sha256=hashlib.sha256(headers).hexdigest(),
                           headers_representation='HTTPMessage.as_bytes; parsed headers, not wire octets')
    except Exception as error:
        receipt['error'] = f'{type(error).__name__}: {error}'
    (directory / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return dict(name=name, **receipt)


if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=4) as executor:
        for result in executor.map(acquire, sys.argv[1:] or REQUESTS):
            print(json.dumps(result), flush=True)
