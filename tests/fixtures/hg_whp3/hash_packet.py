"""Index the final evidence selection, excluding self-referential check outputs."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
paths = sorted(p for p in OUT.rglob('*') if p.is_file()
               and '__pycache__' not in p.parts
               and p.name != 'SHA256SUMS'
               and not p.name.startswith('packet-hash-'))
(OUT / 'SHA256SUMS').write_text(''.join(
    hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + str(p.relative_to(ROOT)) + '\n'
    for p in paths))
print(json.dumps({'selected_files': len(paths), 'index': str((OUT / 'SHA256SUMS').relative_to(ROOT)),
                  'excluded': ['SHA256SUMS', '__pycache__/', 'packet-hash-* command/stdout/stderr']}))
