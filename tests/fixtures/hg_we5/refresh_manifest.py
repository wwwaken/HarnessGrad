"""Seal this owned packet; does not modify any earlier receipt."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parent
members = [p for p in sorted(root.rglob("*")) if p.is_file() and p.name != "SHA256SUMS"]
assert not any("__pycache__" in p.parts for p in members)
(root / "SHA256SUMS").write_text("".join(
    f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(root)}\n" for p in members))
print(f"sealed {len(members)} packet members")
