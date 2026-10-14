"""Acquire only pinned BFCL Python import bodies; never approve or run them."""
import ast
import base64
import datetime
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OLD = ROOT / 'tests/fixtures/external_provenance_b5'
PREFIX = 'berkeley-function-call-leaderboard/'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def identity(path):
    raw = path.read_bytes()
    return dict(path=str(path.relative_to(ROOT)), bytes=len(raw), sha256=digest(raw))


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def acquire():
    (HERE / 'responses').mkdir(parents=True, exist_ok=True)
    tree_path = OLD / 'responses/bfcl-tree.body'
    tree = json.loads(tree_path.read_bytes())
    assert tree['truncated'] is False
    entries = {e['path']: e for e in tree['tree'] if e['type'] == 'blob'}
    previous = json.loads((OLD / 'inventory.json').read_bytes())['bfcl_v3']
    sources = {f['original_path']: ROOT / f['path'] for f in previous['files']}
    attempts = {}
    failures = []
    opener = urllib.request.build_opener(NoRedirect)

    def fetch(path):
        entry = entries[path]
        sha = entry['sha']
        if sha not in attempts:
            label = f'{len(attempts) + 1:02d}-{sha}'
            receipt_path = HERE / 'responses' / (label + '.json')
            body_path = HERE / 'responses' / (label + '.body')
            assert not receipt_path.exists() and not body_path.exists(), 'fresh bundle required'
            url = 'https://api.github.com/repos/ShishirPatil/gorilla/git/blobs/' + sha
            headers = {'User-Agent': 'HarnessGrad-code-only-e3/1', 'Accept': 'application/json'}
            receipt = dict(url=url, method='GET', request_headers=headers,
                           requested_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                           requested_for_original_path=path, pinned_blob_sha1=sha)
            response = None
            try:
                response = opener.open(urllib.request.Request(url, headers=headers), timeout=20)
            except urllib.error.HTTPError as exc:
                response = exc
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                receipt['transport_error'] = f'{type(exc).__name__}: {exc}'
            decoded = None
            if response is not None:
                with response:
                    raw = response.read(2 * 1024 * 1024 + 1)
                    assert len(raw) <= 2 * 1024 * 1024
                    receipt.update(status=response.status, response_headers=list(response.headers.items()))
                body_path.write_bytes(raw)
                receipt['response_body'] = identity(body_path)
                if receipt['status'] == 200:
                    item = json.loads(raw)
                    assert item['sha'] == sha and item['encoding'] == 'base64'
                    decoded = base64.b64decode(item['content'])
                    assert len(decoded) == item['size'] == entry['size']
                    assert hashlib.sha1(b'blob ' + str(len(decoded)).encode() + b'\0' + decoded).hexdigest() == sha
                    ast.parse(decoded)
                    receipt['decoded'] = dict(bytes=len(decoded), sha256=digest(decoded), git_blob_sha1=sha)
            receipt['completed_at_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
            attempts[sha] = (decoded, str(receipt_path.relative_to(ROOT)))
            print(path, receipt.get('status', receipt.get('transport_error')), flush=True)
        decoded, receipt_path = attempts[sha]
        if decoded is None:
            failures.append(dict(original_path=path, pinned_blob_sha1=sha, receipt=receipt_path))
            return
        target = HERE / 'files' / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(decoded)
        sources[path] = target

    def module_path(module):
        stem = PREFIX + module.replace('.', '/')
        for candidate in (stem + '.py', stem + '/__init__.py'):
            if candidate in entries:
                return candidate
        return None

    unresolved = set()
    processed = set()
    missing = {module_path(m) for m in previous['unacquired_imports']}
    assert None not in missing
    while True:
        required = set(missing)
        for path in sorted(sources):
            if not path.endswith('.py'):
                continue
            parent = Path(path).parent
            while str(parent).startswith(PREFIX + 'bfcl_eval'):
                initializer = str(parent / '__init__.py')
                if initializer in entries:
                    required.add(initializer)
                parent = parent.parent
            parsed = ast.parse(sources[path].read_bytes())
            for node in ast.walk(parsed):
                modules = []
                if isinstance(node, ast.Import):
                    modules = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom):
                    assert not node.level, (path, node.lineno, 'relative import needs review')
                    if node.module:
                        modules.append(node.module)
                        for alias in node.names:
                            if alias.name != '*' and module_path(node.module + '.' + alias.name):
                                modules.append(node.module + '.' + alias.name)
                for module in modules:
                    if module.startswith('bfcl_eval.'):
                        target = module_path(module)
                        if target:
                            required.add(target)
                        else:
                            unresolved.add((path, node.lineno, module))
        pending = required - set(sources) - processed
        if not pending:
            break
        for path in sorted(pending):
            processed.add(path)
            fetch(path)

    files = []
    for path, local in sorted(sources.items()):
        raw = local.read_bytes()
        sha = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        assert sha == entries[path]['sha'] and len(raw) == entries[path]['size']
        files.append(dict(original_path=path, **identity(local), git_blob_sha1=sha,
                          newly_acquired=local.is_relative_to(HERE),
                          expected_archive_member='gorilla-1.3/' + path,
                          archive_member_verified=False))
    manifest = dict(schema='harnessgrad.e3-bfcl-acquisition-candidate.v1',
                    repository='https://github.com/ShishirPatil/gorilla', tag='v1.3',
                    commit=previous['commit'], root_tree=previous['root_tree'],
                    reused_tree=identity(tree_path), reused_inventory=identity(OLD / 'inventory.json'),
                    files=files, failed_acquisitions=failures,
                    unresolved_static_modules=sorted(unresolved),
                    requests=len(attempts), status='blocked', measured=False,
                    custodian_approved=False, independent_review=None, approved_receipt_pin=None,
                    production_authorized=False, archive_member_custody=False,
                    runtime_closure=False,
                    dynamic_multi_turn_modules='Not traversed; requires branch-specific review')
    (HERE / 'inventory.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('requests', len(attempts), 'files', len(files), 'failed paths', len(failures),
          'unresolved modules', sorted(unresolved))


if __name__ == '__main__':
    acquire()
