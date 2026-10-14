#!/usr/bin/env python3
"""Independent, read-only image custody audit. No containers, pulls, or models."""
import ast
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tomllib

REPO = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent

def dump(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def command(label, args):
    p = subprocess.run(args, cwd=REPO, capture_output=True)
    (OUT / (label + '.stdout.txt')).write_bytes(p.stdout)
    (OUT / (label + '.stderr.txt')).write_bytes(p.stderr)
    dump(label + '.command.json', {'argv': args, 'cwd': str(REPO), 'returncode': p.returncode})
    return p

# Read literal default values from current adapter source, without importing any adapter.
refs = []
source = []
for dataset, filename, names in [
    ('gaia', 'gaia.py', ['IMAGE']),
    ('tau_bench', 'tau_bench.py', ['IMAGE']),
    ('appworld', 'appworld.py', ['IMAGE', 'SERVICE_IMAGE', 'VERIFIER_IMAGE']),
]:
    path = REPO / 'data/datasets' / filename
    raw = path.read_bytes()
    source.append({'path': str(path), 'sha256': sha(raw)})
    tree = ast.parse(raw)
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        matches = [t.id for t in node.targets if isinstance(t, ast.Name) and t.id in names]
        if not matches:
            continue
        if not isinstance(node.value, ast.Call) or len(node.value.args) != 2:
            raise RuntimeError(f'Unexpected image assignment at {path}:{node.lineno}')
        env_key, default = (ast.literal_eval(x) for x in node.value.args)
        refs.append({'dataset': dataset, 'role': matches[0], 'reference': default,
                     'environment_key': env_key, 'path': str(path), 'line': node.lineno,
                     'pin': 'digest' if '@sha256:' in default else 'movable-tag'})

root_source = REPO / 'data/datasets/terminal_bench.py'
source.append({'path': str(root_source), 'sha256': sha(root_source.read_bytes())})
root = None
for node in ast.parse(root_source.read_bytes()).body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'ROOT' for t in node.targets):
        root = Path(ast.literal_eval(node.value.args[0].args[1]))
        break
if root is None:
    raise RuntimeError('Could not extract Terminal-Bench configured default root')
# Match documented adapter layout selection, counting actual TOML files ourselves.
for candidate in [root, root / 'tasks']:
    tasks = sorted(p for p in candidate.glob('*/task.toml') if p.parent.is_dir())
    if tasks:
        break
if not tasks:
    raise RuntimeError(f'No task TOMLs in {root}')
for path in tasks:
    raw = path.read_bytes()
    parsed = tomllib.loads(raw.decode())
    ref = parsed['environment']['docker_image']
    line = next(i for i, s in enumerate(raw.decode().splitlines(), 1) if s.strip().startswith('docker_image'))
    refs.append({'dataset': 'terminal_bench', 'role': path.parent.name, 'reference': ref,
                 'path': str(path), 'line': line, 'sha256': sha(raw),
                 'pin': 'digest' if '@sha256:' in ref else 'movable-tag'})
dump('configured-references.json', refs)
dump('source-hashes.json', source)
keys = ['HG_GAIA_IMAGE', 'HG_TAU_IMAGE', 'HG_APPWORLD_IMAGE', 'HG_APPWORLD_SERVICE_IMAGE',
        'HG_APPWORLD_VERIFIER_IMAGE', 'HG_TERMINAL_BENCH', 'HG_TB_TASKS']
dump('environment.json', {k: os.environ.get(k) for k in keys})

fmt = '{"Id":{{json .Id}},"RepoDigests":{{json .RepoDigests}},"RepoTags":{{json .RepoTags}},"Size":{{json .Size}}}'
inspections = []
for i, ref in enumerate(refs):
    label = f'inspect-{i:03d}-{ref["dataset"]}-{ref["role"].lower()}'
    p = command(label, ['docker', 'image', 'inspect', '--format', fmt, ref['reference']])
    row = dict(ref, command_file=label + '.command.json', returncode=p.returncode)
    if p.returncode == 0:
        row['observed'] = json.loads(p.stdout)
    else:
        row['stderr'] = p.stderr.decode(errors='replace')
    inspections.append(row)
dump('current-inspections.json', inspections)

# The preserved raw_utf8 bytes, NOT their precomputed_digest or matches, are the hash source.
manifest_path = REPO / 'tests/fixtures/hg_wimg/capture/manifest-read/start.stdout.txt'
manifest_raw = manifest_path.read_bytes()
archive = json.loads(manifest_raw)
blobs = {}
checks = []
for expected, entry in sorted(archive.items()):
    raw = entry['raw_utf8'].encode('utf-8')
    computed = 'sha256:' + sha(raw)
    blobs[expected] = json.loads(raw)
    blob_dir = OUT / 'preserved-raw-manifests'
    blob_dir.mkdir(exist_ok=True)
    (blob_dir / (expected.split(':', 1)[1] + '.json')).write_bytes(raw)
    checks.append({'expected': expected, 'computed': computed, 'match': expected == computed, 'bytes': len(raw)})
dump('manifest-rehash.json', {'source': str(manifest_path), 'source_sha256': sha(manifest_raw), 'checks': checks})

def configs(digest, seen=None):
    seen = set() if seen is None else seen
    if digest in seen or digest not in blobs:
        return []
    seen.add(digest)
    obj = blobs[digest]
    if 'config' in obj:
        return [obj['config']['digest']]
    result = []
    for child in obj.get('manifests', []):
        platform = child.get('platform', {})
        if platform.get('architecture') == 'unknown':
            continue
        result.extend(configs(child['digest'], seen))
    return result

bindings = []
for row in inspections:
    if row['returncode']:
        continue
    digests = row['observed'].get('RepoDigests') or []
    roots = sorted({x.split('@', 1)[1] for x in digests})
    for root_digest in roots:
        known = root_digest in blobs
        root_hash = 'sha256:' + sha(archive[root_digest]['raw_utf8'].encode()) if known else None
        candidate_configs = configs(root_digest)
        bindings.append({'reference': row['reference'], 'repo_digest': root_digest,
                         'captured_root_available': known, 'computed_root_digest': root_hash,
                         'root_hash_matches': root_hash == root_digest,
                         'runnable_manifest_configs': candidate_configs,
                         'fresh_inspect_image_id': row['observed']['Id'],
                         'fresh_image_id_matches_root_or_config': row['observed']['Id'] == root_digest or row['observed']['Id'] in candidate_configs})
dump('manifest-fresh-inspect-bindings.json', bindings)
# Record the access boundary, using read-only requests only.
command('direct-store-permission', ['ls', '-ld', '/var/lib/containerd/io.containerd.content.v1.content/blobs/sha256', '/var/lib/docker/containerd/daemon/io.containerd.content.v1.content/blobs/sha256'])
command('direct-store-sudo', ['sudo', '-n', 'ctr', '--address', '/run/containerd/containerd.sock', '--namespace', 'moby', 'images', 'list'])

present = [x for x in inspections if not x['returncode']]
missing = [x for x in inspections if x['returncode']]
summary = {
    'captured_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'reference_count': len(refs), 'unique_reference_count': len({x['reference'] for x in refs}),
    'references_by_dataset': dict(collections.Counter(x['dataset'] for x in refs)),
    'present_count': len(present), 'missing_count': len(missing),
    'missing_references': [x['reference'] for x in missing],
    'missing_errors': [x['stderr'].strip() for x in missing],
    'present_with_repo_digests': sum(bool(x['observed'].get('RepoDigests')) for x in present),
    'terminal_bench_tags': sum(x['dataset'] == 'terminal_bench' and x['pin'] == 'movable-tag' for x in refs),
    'terminal_bench_present': sum(x['dataset'] == 'terminal_bench' for x in present),
    'terminal_bench_missing': sum(x['dataset'] == 'terminal_bench' for x in missing),
    'appworld_digest_pins': sum(x['dataset'] == 'appworld' and x['pin'] == 'digest' for x in refs),
    'preserved_manifest_count': len(checks),
    'preserved_manifest_hash_matches': sum(x['match'] for x in checks),
    'fresh_present_reference_bindings': len(bindings),
    'root_digest_hash_matches': sum(x['root_hash_matches'] for x in bindings),
    'fresh_image_id_bindings': sum(x['fresh_image_id_matches_root_or_config'] for x in bindings),
}
dump('summary.json', summary)
print(json.dumps(summary, indent=2, sort_keys=True))
