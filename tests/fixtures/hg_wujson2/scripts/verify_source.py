"""Compare every source archive blob and reconstructed tree with B6 custody."""
import hashlib
import json
from pathlib import Path
import tarfile

packet = Path(__file__).resolve().parents[1]
custody = packet.parent / 'hg_wujson/deployment-v6/custody'
archive = next((packet / 'acquired').glob('ultrajson-*.tar.gz'))
tree = json.loads((custody / 'source-tree.json').read_text())
commit = json.loads((custody / 'source-commit.json').read_text())
with tarfile.open(archive) as t:
    root = t.getmembers()[0].name + '/'
    files = {m.name[len(root):]: t.extractfile(m).read() for m in t.getmembers() if m.isfile()}
entries = {e['path']: e for e in tree['tree']}
blobs = {p: e for p, e in entries.items() if e['type'] == 'blob'}
checks = []
for path, e in sorted(blobs.items()):
    data = files.get(path)
    sha = None if data is None else hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    checks.append({'path': path, 'mode': e['mode'], 'expected_git_blob': e['sha'],
                   'actual_git_blob': sha, 'sha256': None if data is None else hashlib.sha256(data).hexdigest(),
                   'matches': sha == e['sha']})

def rebuild(directory):
    parts = []
    for p, e in entries.items():
        parent, _, name = p.rpartition('/')
        if parent != directory:
            continue
        digest = rebuild(p) if e['type'] == 'tree' else bytes.fromhex(next(c['actual_git_blob'] for c in checks if c['path'] == p))
        parts.append((name.encode() + (b'/' if e['type'] == 'tree' else b''),
                      (b'40000' if e['type'] == 'tree' else e['mode'].encode()) + b' ' + name.encode() + b'\0' + digest))
    data = b''.join(data for _, data in sorted(parts))
    return hashlib.sha1(b'tree ' + str(len(data)).encode() + b'\0' + data).digest()

result = {
    'archive': archive.name, 'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
    'commit': commit['sha'], 'commit_verification_scope': 'preserved GitHub API verification assertion; no independent signature re-verification',
    'expected_root_tree': commit['tree']['sha'], 'reconstructed_root_tree': rebuild('').hex(),
    'extra_archive_files': sorted(set(files) - set(blobs)), 'blob_count': len(checks), 'blobs': checks,
}
result['passed'] = all(c['matches'] for c in checks) and not result['extra_archive_files'] and result['expected_root_tree'] == result['reconstructed_root_tree']
(packet / 'source-verification.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k:v for k,v in result.items() if k != 'blobs'}, indent=2))
assert result['passed']
