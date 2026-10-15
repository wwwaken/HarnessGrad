"""Retrieve only version-tagged licence candidates; never guess a resolved revision."""
import base64
import json
from pathlib import Path
from collect import command, digest, write_rows

HERE = Path(__file__).parent


def get(key, url):
    folder = HERE / 'publisher'
    folder.mkdir(exist_ok=True)
    body, headers = folder / (key + '.raw'), folder / (key + '.headers')
    result = command(['curl', '--silent', '--show-error', '--location', '--max-time', '40',
        '--dump-header', str(headers), '--output', str(body), '--write-out', '%{http_code}', url])
    received_body_file = body.exists()
    if not received_body_file:
        body.write_bytes(b'')
    data = body.read_bytes()
    status = int(result['stdout']) if result['stdout'].isdigit() else None
    return {'url': url, 'response': str(body), 'headers': str(headers), **digest(data),
            'received_body_file': received_body_file,
            'headers_identity': digest(headers.read_bytes()), **result, 'status': status,
            'state': 'FOUND' if status == 200 else 'ABSENT' if status == 404 else 'UNKNOWN'}


def main():
    records = []
    # These are enumerated candidate tag spellings, not assumed observed objects.
    for repository, tag, key, license_name in [
        ('huggingface/tokenizers', 'v0.23.3', 'tokenizers-0.23.3', 'LICENSE'),
        ('openssl/openssl', 'openssl-4.0.3', 'openssl-4.0.3', 'LICENSE.txt'),
    ]:
        ref = get(key + '-ref', f'https://api.github.com/repos/{repository}/git/ref/tags/{tag}')
        records.append(ref)
        if ref['status'] != 200:
            continue
        obj = json.loads(Path(ref['response']).read_bytes())['object']
        while obj['type'] == 'tag':
            tag_record = get(key + '-tag-' + obj['sha'], obj['url'])
            records.append(tag_record)
            if tag_record['status'] != 200:
                obj = None
                break
            obj = json.loads(Path(tag_record['response']).read_bytes())['object']
        if obj is None or obj['type'] != 'commit':
            continue
        record = get(key + '-license-api', f"https://api.github.com/repos/{repository}/contents/{license_name}?ref={obj['sha']}")
        record.update({'repository': repository, 'tag': tag, 'observed_commit': obj['sha'],
            'scope': 'producer version-tag text; not a text packaged inside the selected wheel',
            'tag_signature_verification': 'UNKNOWN not performed'})
        if record['status'] == 200:
            response = json.loads(Path(record['response']).read_bytes())
            if response.get('encoding') == 'base64':
                data = base64.b64decode(response['content'])
                target = HERE / 'publisher' / (key + '-LICENSE.txt')
                target.write_bytes(data)
                record['license_text'] = {'path': str(target), **digest(data),
                    'git_blob_observed': response['sha'],
                    'git_blob_recomputed': __import__('hashlib').sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()}
        records.append(record)
    write_rows(HERE / 'publisher.jsonl', records)
    print(json.dumps({'requests': len(records), 'statuses': [r['status'] for r in records],
        'version_tag_licenses_found': sum('observed_commit' in r and r['status'] == 200 for r in records)}, sort_keys=True))


if __name__ == '__main__':
    main()
