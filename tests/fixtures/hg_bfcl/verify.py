#!/usr/bin/env python3
"""Offline byte/identity and syntax audit; no upstream imports or task reads.

--write writes the derived inventory and manifests. Default verifies them.
The raw archive is opaque custody evidence except the 83 allowlisted source,
license and dependency-spec members; no task/result/answer member is opened.
"""
import ast
import base64
import hashlib
import json
from pathlib import Path
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
WRITE = sys.argv[1:] == ['--write']
assert not sys.argv[1:] or WRITE

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def git_hash(kind, raw):
    return hashlib.sha1(kind.encode() + b' ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()

def identity(path):
    raw = path.read_bytes()
    return dict(path=str(path.relative_to(ROOT)), bytes=len(raw), sha256=sha(raw))

def publish(name, raw):
    target = HERE / name
    if WRITE:
        target.write_bytes(raw)
    else:
        assert target.read_bytes() == raw, name

def response(name):
    receipt = json.loads((HERE / 'responses' / (name + '.receipt.json')).read_bytes())
    assert receipt['http_status'] == '200' and receipt['curl_exit_code'] == 0
    for field in ('body', 'headers'):
        assert identity(ROOT / receipt[field]['path']) == receipt[field]
    return (ROOT / receipt['body']['path']).read_bytes()

tag = json.loads(response('tag'))
release = json.loads(response('release'))
commit = json.loads(response('commit'))
license_blob = json.loads(response('license-blob'))
archive = response('archive')
assert tag['object']['type'] == 'commit' and tag['object']['sha'] == commit['sha']
assert release['tag_name'] == 'v1.3' and 'Leaderboard V3' in release['body']
v = commit['verification']
header, message = v['payload'].split('\n\n', 1)
signed = (header + '\ngpgsig ' + v['signature'].replace('\n', '\n ') + '\n\n' + message).encode()
assert git_hash('commit', signed) == commit['sha']
# Reuse the original untruncated B5 response, verifying all tree object hashes.
tree_path = ROOT / 'tests/fixtures/external_provenance_b5/responses/bfcl-tree.body'
tree = json.loads(tree_path.read_bytes())
assert tree['truncated'] is False and tree['sha'] == commit['sha']
root_tree_path = tree_path.with_name('bfcl-root-tree.body')
root_tree = json.loads(root_tree_path.read_bytes())
assert root_tree['truncated'] is False and root_tree['sha'] == commit['tree']['sha']
entries = {e['path']: e for e in tree['tree']}
parents = {}
for e in tree['tree']:
    parents.setdefault(str(Path(e['path']).parent), []).append(e)
for parent, children in parents.items():
    ordered = sorted(children, key=lambda e: Path(e['path']).name + ('/' if e['type'] == 'tree' else ''))
    raw = b''.join(e['mode'].lstrip('0').encode() + b' ' + Path(e['path']).name.encode() + b'\0' + bytes.fromhex(e['sha']) for e in ordered)
    assert git_hash('tree', raw) == (root_tree['sha'] if parent == '.' else entries[parent]['sha'])
prior_path = ROOT / 'tests/fixtures/e3_bfcl_source/inventory.json'
prior = json.loads(prior_path.read_bytes())
assert prior['commit'] == commit['sha'] and prior['root_tree'] == root_tree['sha']
# Compare with the adapter's declared archive pin without importing its code.
adapter_path = ROOT / 'data/datasets/bfcl_v3.py'
adapter = ast.parse(adapter_path.read_bytes())
pins = {n.targets[0].id: ast.literal_eval(n.value) for n in adapter.body
        if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
        and n.targets[0].id in {'REPO_TAG', 'TARBALL_URL', 'TARBALL_SHA256'}}
assert pins['REPO_TAG'] == release['tag_name'] and sha(archive) == pins['TARBALL_SHA256']
allowed = {'gorilla-1.3/' + f['original_path']: f for f in prior['files']}
assert len(allowed) == 83
files = []
imports = []
evaluation_calls = []
seen = set()
with tarfile.open(HERE / 'responses/archive.body', 'r:gz') as tf:
    pax_headers = tf.pax_headers
    for member in tf:
        if member.name not in allowed:
            continue
        assert member.isfile() and member.name not in seen
        seen.add(member.name)
        old = allowed[member.name]
        with tf.extractfile(member) as stream:
            raw = stream.read()
        local = ROOT / old['path']
        assert raw == local.read_bytes()
        blob = git_hash('blob', raw)
        entry = entries[old['original_path']]
        assert blob == old['git_blob_sha1'] == entry['sha']
        assert member.size == len(raw) == old['bytes'] == entry['size']
        assert sha(raw) == old['sha256']
        row = dict(original_path=old['original_path'], **identity(local),
                   archive_member=member.name, archive_member_bytes=member.size,
                   archive_member_sha256=sha(raw), git_blob_sha1=blob)
        files.append(row)
        if old['original_path'] == 'LICENSE':
            lic = base64.b64decode(license_blob['content'])
            assert lic == raw and git_hash('blob', lic) == license_blob['sha'] == blob
            publish('LICENSE.upstream', raw)
        if local.suffix == '.py':
            parsed = ast.parse(raw, filename=old['original_path'])
            for node in ast.walk(parsed):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    modules = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or '']
                    for module in modules:
                        imports.append(dict(path=old['path'], line=node.lineno, module=module))
                if isinstance(node, ast.Call):
                    call = ast.unparse(node.func)
                    if call in {'eval', 'exec', 'ast.literal_eval', 'importlib.import_module'}:
                        evaluation_calls.append(dict(path=old['path'], line=node.lineno, call=call))
assert seen == set(allowed)
if 'comment' in pax_headers:
    assert pax_headers['comment'] == commit['sha']
result = dict(schema='harnessgrad.w-bfcl-public-custody.v1',
              scope='Static code review and public-source custody; no upstream execution or task member access',
              commit=commit['sha'], root_tree=root_tree['sha'], tag=tag['ref'],
              archive=identity(HERE / 'responses/archive.body'), archive_pax_headers=pax_headers,
              archive_matches_adapter_pin=True, reconstructed_tree_objects=len(parents),
              reused_evidence=[identity(tree_path), identity(root_tree_path), identity(prior_path), identity(adapter_path)],
              files=sorted(files, key=lambda f: f['original_path']),
              imports=sorted(imports, key=lambda r: (r['path'], r['line'], r['module'])),
              evaluation_calls=sorted(evaluation_calls, key=lambda r: (r['path'], r['line'])),
              signature_cryptographically_verified=False,
              runtime_closure=False, official_scorer_executed=False,
              measured=False, production_authorized=False)
publish('inventory.json', (json.dumps(result, indent=2) + '\n').encode())
paths = sorted(p for p in HERE.rglob('*') if p.is_file() and p.name != 'SHA256SUMS' and '__pycache__' not in p.parts)
sums = ''.join(sha(p.read_bytes()) + '  ' + str(p.relative_to(HERE)) + '\n' for p in paths)
publish('SHA256SUMS', sums.encode())
print('PASS: five raw HTTP bodies/headers; reconstructed commit and %d trees; 83/83 archive/source/blob bindings; 81 Python syntax trees; SHA256SUMS.' % len(parents))
print('Archive SHA-256: ' + sha(archive))
print('Official scorer executed=false; runtime closure=false; measured=false; production_authorized=false.')
