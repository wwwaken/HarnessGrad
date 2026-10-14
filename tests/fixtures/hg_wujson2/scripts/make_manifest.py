"""Hash all packet files, excluding this manifest's own bytes."""
import hashlib
from pathlib import Path

packet = Path(__file__).resolve().parents[1]
repo = packet.parents[2]
manifest = packet / 'SHA256SUMS'
paths = sorted(p for p in packet.rglob('*') if p.is_file() and p != manifest)
manifest.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.relative_to(repo).as_posix() + '\n' for p in paths))
print(f'SHA256SUMS: {len(paths)} files; {sum(p.stat().st_size for p in paths)} bytes')
