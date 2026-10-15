"""Recompute hashes after execution without trusting prior manifests."""
from pathlib import Path
import hashlib
F=Path(__file__).resolve().parent
manifest=F/'SHA256SUMS'
files=[p for p in sorted(F.rglob('*')) if p.is_file() and p!=manifest]
manifest.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(F))+'\n' for p in files))
print(f'computed SHA-256 for {len(files)} packet files')
