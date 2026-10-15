"""Archive the initial packet only after checking every copied byte."""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

p = Path(__file__).resolve().parent
old = p / "preserved-initial-evidence"
rows = {str(f.relative_to(old)): hashlib.sha256(f.read_bytes()).hexdigest()
        for f in sorted(old.rglob("*")) if f.is_file()}
archive = p / "preserved-initial-evidence.zip"
with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED, strict_timestamps=False) as out:
    for name in rows:
        out.write(old / name, name)
with zipfile.ZipFile(archive) as inp:
    assert set(inp.namelist()) == set(rows)
    assert all(hashlib.sha256(inp.read(n)).hexdigest() == pin for n, pin in rows.items())
receipt = {"archive": archive.name, "members": len(rows),
           "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(), "verified_member_sha256": rows,
           "metadata_note": "ZIP clamps pre-1980 timestamps; original observed metadata remains in inventories.json"}
(p / "preservation.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
shutil.rmtree(old)
print(json.dumps({k: v for k, v in receipt.items() if k != "verified_member_sha256"}, indent=2))
