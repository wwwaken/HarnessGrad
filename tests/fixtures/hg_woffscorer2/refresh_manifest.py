#!/usr/bin/env python3
"""Hash every packet file, including raw observations; do not rerun scorers."""
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
files = sorted(p for p in HERE.rglob('*') if p.is_file()
               and '__pycache__' not in p.parts and p != HERE / 'SHA256SUMS')
(HERE / 'SHA256SUMS').write_text(''.join(
    f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(HERE)}\n' for p in files))
print(f'SHA256SUMS files={len(files)}')
