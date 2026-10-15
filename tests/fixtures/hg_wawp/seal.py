"""Seal every retained packet member except the manifest itself."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parent
members = [p for p in sorted(root.rglob('*')) if p.is_file() and p.name != 'SHA256SUMS']
(root/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+
                           str(p.relative_to(root))+'\n' for p in members))
print(f'Sealed {len(members)} files with SHA-256')
