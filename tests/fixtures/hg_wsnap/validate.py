#!/usr/bin/env python3
"""Recheck retained evidence without Docker, imports of platform code, or network."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def digest(data):
    return 'sha256:'+hashlib.sha256(data).hexdigest()

def load(path):
    return json.loads(path.read_text())

def raw(n):
    return (HERE/'raw'/f'{n:03d}.stdout.txt').read_text()

s = load(HERE/'summary.json')
original_pins = load(HERE/'source-pins.json')
current_pins = load(HERE/'independent/current-source-pins.json')
assert {p['path'] for p in original_pins} == {p['path'] for p in current_pins}
for pin in current_pins:
    assert digest((ROOT/pin['path']).read_bytes()) == 'sha256:'+pin['sha256'], pin['path']
for pin in original_pins:
    archived = (HERE/'source'/pin['path']).read_bytes()
    current = (ROOT/pin['path']).read_bytes()
    assert digest(archived) == 'sha256:'+pin['sha256'], pin['path']
    if current != archived:
        assert pin['path'] == 'eval/verification/verifier.py'
        old_ast, new_ast = ast.parse(archived), ast.parse(current)
        for tree in (old_ast, new_ast):
            tree.body = [n for n in tree.body if not isinstance(n, ast.FunctionDef) or n.name != '_verify']
        assert ast.dump(old_ast, include_attributes=False) == ast.dump(new_ast, include_attributes=False)
commands = sorted((HERE/'raw').glob('*.command.json'))
assert len(commands) == 84
for path in commands:
    c = load(path)
    assert c['argv'] and c['timeout_s'] <= 1800
    if c['timeout_s'] > 180:
        assert c['argv'][:2] == ['docker', 'commit']
    assert path.with_name(path.name.replace('.command.json','.stdout.txt')).is_file()
    assert path.with_name(path.name.replace('.command.json','.stderr.txt')).is_file()
recomputed = {}
for folder in sorted((HERE/'image-metadata').iterdir()):
    result = load(folder/'recomputed.json')
    def blob(d):
        return (folder/'blobs/sha256'/d.split(':')[1]).read_bytes()
    assert digest(blob(result['image_id'])) == result['manifest_sha256'] == result['image_id']
    manifest = json.loads(blob(result['image_id']))
    assert digest(blob(result['config_sha256'])) == manifest['config']['digest'] == result['config_sha256']
    assert len(blob(result['config_sha256'])) == manifest['config']['size']
    config = json.loads(blob(result['config_sha256']))
    assert len(result['layers']) == len(manifest['layers']) == len(config['rootfs']['diff_ids'])
    for row, layer, diffid in zip(result['layers'], manifest['layers'], config['rootfs']['diff_ids'], strict=True):
        assert row['descriptor'] == layer
        assert row['blob_sha256'] == layer['digest']
        assert row['uncompressed_sha256'] == diffid
        member = result['all_archive_members']['blobs/sha256/'+layer['digest'].split(':')[1]]
        assert member['sha256'] == layer['digest'] and member['size'] == layer['size']
    # Layer bytes were streamed during capture and deleted: only metadata is independently rehashed here.
    assert result['layer_bytes_retained'] is False
    recomputed[folder.name] = result
assert raw(15).strip() == s['snapshot_id'] == recomputed['snapshot']['image_id']
assert s['snapshot_parent'] == s['base_id'] == recomputed['base']['image_id']
base_layers = [r['uncompressed_sha256'] for r in recomputed['base']['layers']]
assert [r['uncompressed_sha256'] for r in recomputed['snapshot']['layers']][:-1] == base_layers
for label in ('verifier_before_start','verifier_after_start'):
    assert s[label]['Image'] == s[label]['Config']['Image'] == s['snapshot_id']
assert s['actor_stopped']['Running'] is False and s['actor_stopped']['Pid'] == 0
assert s['retargeted_tag_id'] == s['base_id'] != s['snapshot_id']
assert raw(25).startswith('committed-root\nbind-excluded\ntmpfs-excluded\nno-docker-socket\n')
assert s['baseline_probe'] == raw(25)
assert raw(34).strip() == s['attack_snapshot_id'] == recomputed['startup-snapshot']['image_id']
for label in ('attack_verifier_before_start','attack_verifier_after_start'):
    assert s[label]['Image'] == s['attack_snapshot_id']
assert s['attack_before_start'] == 'committed-before-start\n'
assert raw(41) == s['attack_after_start'] and raw(41).startswith('rewritten-by-actor-startup\n')
assert s['base_volumes'] is None
assert raw(48) == s['volume_actor_write'] == 'actor-volume-output\n'
assert raw(58) == s['volume_verifier_read'] == 'actor-after-commit\n'
assert raw(52).strip() == s['volume_snapshot_id'] == recomputed['volume-snapshot']['image_id']
assert s['volume_actor_mounts'][0]['Name'] != s['volume_verifier_mounts'][0]['Name']
assert all(c['remove_returncode'] == 0 and c['absence_returncode'] == 1 for c in s['cleanup'])
assert len(s['cleanup']) == 12 and s['base_still_present'] == s['base_id']
old = HERE/'source/tests/fixtures/hg_wverify/net'
historical = json.loads(load(old/'snapshot-inspect-00072.json')['stdout'])[0]
verifier = json.loads(load(old/'container-inspect-00064.json')['stdout'])[0]
actor = json.loads(load(old/'container-inspect-00000.json')['stdout'])[0]
assert historical['Id'] == historical['Descriptor']['digest'] == verifier['Image'] == verifier['Config']['Image']
assert historical['Parent'] == actor['Image'] == s['base_id']
assert historical['RootFS']['Layers'][:-1] == base_layers
receipt = load(HERE/'source/reports/w-net-evidence/launch/snapshot-observation-receipt.json')
assert digest((old/'snapshot-inspect-00072.json').read_bytes()) == 'sha256:'+receipt['snapshots'][0]['source_sha256']
events = [json.loads(line) for line in (HERE/'source/reports/w-net-evidence/launch/docker-events.jsonl').read_text().splitlines()]
commits = [e for e in events if e['Action'] == 'commit' and e['Actor']['ID'] == actor['Id']]
assert len(commits) == 1
assert commits[0]['Actor']['Attributes']['imageID'] == historical['Id']
assert s['historical_inspect_returncode'] == 1
print(json.dumps({'valid': True, 'raw_commands': len(commands), 'source_pins': len(load(HERE/'source-pins.json')), 'metadata_roots_rehashed': len(recomputed), 'layer_bytes_rechecked_now': False, 'historical_binding_metadata_equal': True, 'tag_substitution_failed': True, 'startup_mutation_demonstrated': True, 'volume_output_loss_demonstrated': True, 'owned_objects_removed': len(s['cleanup'])}, sort_keys=True))
