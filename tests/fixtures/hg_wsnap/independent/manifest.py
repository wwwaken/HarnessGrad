#!/usr/bin/env python3
"""Generate/check exhaustive retained-member SHA256SUMS; never hash absent bytes."""
import hashlib
import json
from pathlib import Path
import sys

PACKET = Path(__file__).resolve().parent.parent
MANIFEST = PACKET / 'SHA256SUMS'
HEADER = '''# SHA-256 of retained regular packet files only; paths are relative to this directory.
# Every retained packet file except SHA256SUMS is listed. This is not an image archive.
# NOT REHASHABLE: original four docker-save archives and nine unique layer payloads
# (27 image-layer references); see independent/packet-audit.json for their inventory.
# Historical snapshot manifest/config/layers are absent; archived inspect is metadata only.
# The intermediate VOLUME base was inspected, not exported for byte verification.
# Original temporary startup-before and writer-comparison files were deleted; their
# reported values survive only as observations. Fresh independent file copies are retained.
# The fresh independent save archive and layer payloads were also deleted after hashing;
# fresh-metadata/recomputed.json records those computations, not retained payload bytes.
# Retained manifest/config JSON bytes can be rehashed; missing image bytes cannot.
'''


def members():
    for path in sorted(PACKET.rglob('*')):
        assert not path.is_symlink(), path
        if path.is_file() and path != MANIFEST:
            yield path


paths = list(members())
rows = {str(p.relative_to(PACKET)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
if sys.argv[1:] == ['--write']:
    MANIFEST.write_text(HEADER + ''.join(f'{digest}  {name}\n' for name, digest in rows.items()))
    print(json.dumps({'written': True, 'retained_members': len(rows), 'missing_payloads_covered': False}, sort_keys=True))
else:
    actual = {}
    for line in MANIFEST.read_text().splitlines():
        if line.startswith('#') or not line:
            continue
        digest, name = line.split('  ', 1)
        assert name not in actual, name
        actual[name] = digest
    assert actual == rows, 'manifest membership or bytes differ'
    print(json.dumps({'valid': True, 'retained_members': len(rows), 'excluded': 'SHA256SUMS',
                      'missing_payloads_rechecked': False}, sort_keys=True))
