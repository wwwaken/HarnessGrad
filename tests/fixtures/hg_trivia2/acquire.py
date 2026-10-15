"""Fetch only explicitly enumerated small public source/metadata responses.

Never call rows/first-rows/search/filter endpoints or fetch Parquet/archives.
Each response is bounded to 950,000 bytes; bodies and HTTP evidence are retained.
Usage: python3 tests/fixtures/hg_trivia2/acquire.py PLAN.json
PLAN is a JSON list of {name, url}. Run only on a fresh name, not over receipts.
"""
import concurrent.futures
import datetime
import hashlib
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
LIMIT = 950_000


def fetch(item):
    name, url = item['name'], item['url']
    assert '/' not in name and '..' not in name
    dest = ROOT / 'responses' / (name + '.body')
    receipt_path = dest.with_suffix('.receipt.json')
    assert not dest.exists() and not receipt_path.exists(), name
    record = dict(item, method='GET', requested_at_utc=datetime.datetime.now(
        datetime.timezone.utc).isoformat(), tls_verification='Python default verified HTTPS',
        response_limit_bytes=LIMIT, https_proxy=os.environ.get('HTTPS_PROXY'))
    request = urllib.request.Request(url, headers={
        'User-Agent': 'HarnessGrad-metadata-only-w-trivia2/1',
        'Accept': 'application/json, text/plain, text/html;q=0.5',
    })
    try:
        try:
            response = urllib.request.urlopen(request, timeout=35)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            record.update(status=response.status, final_url=response.url,
                          headers=list(response.headers.items()))
            body = response.read(LIMIT + 1)
            if len(body) > LIMIT:
                raise ValueError('response exceeded metadata byte limit; not retained')
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(body)
        record.update(bytes=len(body), sha256=hashlib.sha256(body).hexdigest(),
                      body=str(dest.relative_to(ROOT)))
        try:
            obj = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            pass
        else:
            view = ROOT / 'views' / (name + '.json')
            view.parent.mkdir(parents=True, exist_ok=True)
            view.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
            record['view'] = str(view.relative_to(ROOT))
    except Exception as error:
        record['error'] = type(error).__name__ + ': ' + str(error)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(record, indent=2) + '\n')
    return {key: record.get(key) for key in ['name', 'status', 'bytes', 'sha256', 'error']}


if __name__ == '__main__':
    plan = json.loads(pathlib.Path(sys.argv[1]).read_text())
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=int(os.environ.get('HG_TRIVIA2_FETCH_WORKERS', '4'))) as pool:
        for result in pool.map(fetch, plan):
            print(json.dumps(result, sort_keys=True), flush=True)
