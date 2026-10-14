#!/usr/bin/env python3
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows = []
for path in sorted(HERE.rglob("*")):
    if path.is_file() and path.name != "SHA256SUMS" and "__pycache__" not in path.parts:
        rows.append(hashlib.sha256(path.read_bytes()).hexdigest() + "  " + str(path.relative_to(HERE)))
(HERE / "SHA256SUMS").write_text("\n".join(rows) + "\n")
print(f"manifest_files={len(rows)}")
