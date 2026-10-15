#!/usr/bin/env python3
"""Rehash retained original bytes; explicitly inventory unavailable payloads."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
PACKET = HERE.parent
ROOT = HERE.parents[3]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


pins = load(PACKET / 'source-pins.json')
source_rows = []
current_pins = []
for pin in pins:
    archived = (PACKET / 'source' / pin['path']).read_bytes()
    current = (ROOT / pin['path']).read_bytes()
    assert sha(archived) == pin['sha256']
    current_pins.append({'path': pin['path'], 'sha256': sha(current)})
    source_rows.append({'path': pin['path'], 'archived_sha256': sha(archived),
                        'current_sha256': sha(current), 'identical': current == archived})
    if current != archived:
        assert pin['path'] == 'eval/verification/verifier.py'
        a, b = ast.parse(archived), ast.parse(current)
        # The one changed function is the separate pristine/actor-workdir dispatch.
        a.body = [n for n in a.body if not isinstance(n, ast.FunctionDef) or n.name != '_verify']
        b.body = [n for n in b.body if not isinstance(n, ast.FunctionDef) or n.name != '_verify']
        assert ast.dump(a, include_attributes=False) == ast.dump(b, include_attributes=False)

# Compare every imported member directly to the prior committed object, independent
# of its report and of the new SHA256SUMS that will be generated later.
names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', 'b4017fe', '--',
                                 'tests/fixtures/hg_wsnap'], cwd=ROOT).decode().splitlines()
imported = []
for name in names:
    original = subprocess.check_output(['git', 'show', 'b4017fe:' + name], cwd=ROOT)
    present = (ROOT / name).read_bytes()
    # The validator is intentionally revised; all other original packet bytes remain.
    equal = original == present
    assert equal or name.endswith('/validate.py')
    imported.append({'path': name, 'original_sha256': sha(original),
                     'current_sha256': sha(present), 'identical': equal})

metadata = []
missing_layers = set()
for folder in sorted((PACKET / 'image-metadata').iterdir()):
    recomputed = load(folder / 'recomputed.json')
    blobdir = folder / 'blobs' / 'sha256'
    manifest_bytes = (blobdir / recomputed['image_id'].split(':')[1]).read_bytes()
    manifest = json.loads(manifest_bytes)
    manifest_hash = 'sha256:' + sha(manifest_bytes)
    config_bytes = (blobdir / manifest['config']['digest'].split(':')[1]).read_bytes()
    config_hash = 'sha256:' + sha(config_bytes)
    assert manifest_hash == recomputed['image_id'] == recomputed['manifest_sha256']
    assert config_hash == manifest['config']['digest'] == recomputed['config_sha256']
    assert config_hash != manifest_hash
    for layer in manifest['layers']:
        assert not (blobdir / layer['digest'].split(':')[1]).exists()
        missing_layers.add(layer['digest'])
    metadata.append({'label': folder.name, 'manifest_rehashed': manifest_hash,
                     'config_rehashed': config_hash, 'missing_layer_references': len(manifest['layers'])})

old = PACKET / 'source/tests/fixtures/hg_wverify/net'
snapshot = json.loads(load(old / 'snapshot-inspect-00072.json')['stdout'])[0]
actor = json.loads(load(old / 'container-inspect-00000.json')['stdout'])[0]
verifier = json.loads(load(old / 'container-inspect-00064.json')['stdout'])[0]
events = [json.loads(line) for line in (PACKET / 'source/reports/w-net-evidence/launch/docker-events.jsonl').read_text().splitlines()]
commits = [e for e in events if e['Action'] == 'commit' and e['Actor']['ID'] == actor['Id']]
assert len(commits) == 1
assert commits[0]['Actor']['Attributes']['imageID'] == snapshot['Id'] == snapshot['Descriptor']['digest'] == verifier['Image'] == verifier['Config']['Image']
assert actor['Image'] == snapshot['Parent']
receipt = load(PACKET / 'source/reports/w-net-evidence/launch/snapshot-observation-receipt.json')
assert sha((old / 'snapshot-inspect-00072.json').read_bytes()) == receipt['snapshots'][0]['source_sha256']

result = {'original_commit': 'b4017fe', 'original_packet_members': imported,
          'source_pins': source_rows, 'snapshot_route_ast_unchanged': True,
          'metadata': metadata, 'missing_original_layer_blobs': sorted(missing_layers),
          'missing_original_layer_reference_count': sum(m['missing_layer_references'] for m in metadata),
          'historical_chain': {'actor': actor['Id'], 'parent': actor['Image'],
                               'snapshot': snapshot['Id'], 'verifier': verifier['Id'],
                               'snapshot_inspect_bytes_sha256': sha((old / 'snapshot-inspect-00072.json').read_bytes())}}
(HERE / 'packet-audit.json').write_text(json.dumps(result, indent=2) + '\n')
(HERE / 'current-source-pins.json').write_text(json.dumps(current_pins, indent=2) + '\n')
print(json.dumps({'original_members_compared': len(imported),
                  'original_members_identical': sum(r['identical'] for r in imported),
                  'archived_source_pins_rehashed': len(source_rows),
                  'current_source_files_identical': sum(r['identical'] for r in source_rows),
                  'snapshot_route_ast_unchanged': True, 'manifest_config_pairs_rehashed': len(metadata),
                  'missing_unique_original_layer_blobs': len(missing_layers),
                  'missing_layer_references': result['missing_original_layer_reference_count'],
                  'historical_metadata_chain_equal': True}, sort_keys=True))
