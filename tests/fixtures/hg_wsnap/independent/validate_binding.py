#!/usr/bin/env python3
"""Offline check of independent raw observations, including both accepted cases."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
runs = list(HERE.glob('w-snap2-*/summary.json'))
assert len(runs) == 1
RUN = runs[0].parent
s = json.loads(runs[0].read_bytes())


def raw(stem):
    return (RUN / (stem + '.stdout.txt')).read_bytes()


def metadata(stem):
    return json.loads(raw(stem))[0]


for c in s['commands']:
    stem = c['stem']
    command = json.loads((RUN / (stem + '.command.json')).read_bytes())
    assert command['returncode'] == c['returncode']
    assert command['argv'] and command['timeout_s'] <= 1800
    assert (RUN / (stem + '.stdout.txt')).is_file()
    assert (RUN / (stem + '.stderr.txt')).is_file()

snapshot = raw('014-helper-commit').decode().strip()
assert snapshot == s['expected_snapshot']
assert metadata('015-snapshot-inspect')['Id'] == snapshot
assert metadata('019-retargeted-inspect')['Id'] == s['base_id'] != snapshot
ordinary = metadata('021-ordinary-before-start')
assert ordinary['Image'] == ordinary['Config']['Image'] == snapshot
assert ordinary['Mounts'] == []
assert raw('023-ordinary-binding-observation') == b'committed-value\nbind-excluded\ntmpfs-excluded\nno-docker-socket\n'
assert metadata('010-stopped-actor')['State']['Running'] is False
assert metadata('010-stopped-actor')['State']['Pid'] == 0
assert (RUN / 'stopped-tick.txt').read_bytes() == (RUN / 'snapshot-tick.txt').read_bytes()

for stem in ('026-foreign-before-start', '028-foreign-after-start'):
    m = metadata(stem)
    assert m['Image'] == m['Config']['Image'] == s['base_id'] != snapshot
assert raw('029-helper-exec') == b'binding-value-absent\n/usr/bin/sleep\n'
assert s['foreign_identity_route']['returned']['passed'] is True
missing = json.loads((RUN / '032-unavailable-identity-refusal.command.json').read_bytes())
assert missing['returncode'] != 0 and '--pull=never' in missing['argv']
assert b'No such image' in (RUN / '032-unavailable-identity-refusal.stderr.txt').read_bytes()

changed = raw('039-helper-commit').decode().strip()
for stem in ('041-changed-before-start', '044-changed-after-start'):
    m = metadata(stem)
    assert m['Image'] == m['Config']['Image'] == changed
assert (RUN / 'changed-before-start.txt').read_bytes() == b'committed-before-start\n'
assert (RUN / 'changed-after-start.txt').read_bytes() == b'changed-during-start\n'
assert raw('046-helper-exec') == b'changed-during-start\n/usr/bin/sleep\n'
assert metadata('048-changed-image-still-same')['Id'] == changed
assert s['changed_filesystem_route']['passed'] is True

fresh = RUN / 'fresh-metadata'
manifest_bytes = (fresh / 'manifest.json').read_bytes()
config_bytes = (fresh / 'config.json').read_bytes()
manifest = json.loads(manifest_bytes)
assert 'sha256:' + hashlib.sha256(manifest_bytes).hexdigest() == snapshot
assert 'sha256:' + hashlib.sha256(config_bytes).hexdigest() == manifest['config']['digest'] != snapshot
for item in s['cleanup']:
    assert item['absence_rc'] == 1
# Removing the changed snapshot's last tag already removed that image. Its later
# explicit removal correctly reports absence; do not relabel the nonzero result.
assert metadata('069-base-still-present')['Id'] == s['base_id']
assert all(c['returncode'] == 1 for c in s['commands'] if c['label'].endswith('absence'))
print(json.dumps({'valid': True, 'raw_commands': len(s['commands']),
                  'foreign_existing_identity_refused': False,
                  'unavailable_identity_refused_without_pull': True,
                  'changed_filesystem_refused': False, 'image_identity_unchanged': True,
                  'tag_substitution_excluded': True, 'tested_mounts_excluded': True,
                  'retained_writer_bytes_equal': True, 'owned_object_absence_checks': len(s['cleanup']),
                  'fresh_manifest_config_rehashed': True, 'missing_payloads_rechecked_now': False}, sort_keys=True))
