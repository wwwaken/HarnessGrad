"""Refresh synthetic-evidence byte manifests, deepest first; never access runs/."""
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
for directory in [p.parent for p in sorted(HERE.rglob('SHA256SUMS'), key=lambda p: -len(p.parts)) if p.parent != HERE] + [HERE]:
    files = [p for p in sorted(directory.rglob('*')) if p.is_file()
             and p != directory / 'SHA256SUMS' and '__pycache__' not in p.parts]
    assert not any(p.is_symlink() for p in files)
    (directory / 'SHA256SUMS').write_text(''.join(
        f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(directory)}\n' for p in files))
    print(f'{directory.relative_to(HERE)}/SHA256SUMS: {len(files)} files')
