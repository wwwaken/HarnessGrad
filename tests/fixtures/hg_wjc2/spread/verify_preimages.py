#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
manifest=json.loads((ROOT/"encoded-preimages.json").read_text())
for item in manifest:
    j=json.loads((ROOT/"responses"/item["stored_name"]).read_text());b=j["raw"].encode()
    assert len(b)==item["bytes"]==j["bytes"]
    assert hashlib.sha256(b).hexdigest()==item["sha256"]==j["sha256"]
for receipt in (ROOT/"responses").glob("*.receipt.json"):
    r=json.loads(receipt.read_text())
    if "sha256" not in r:
        assert "error" in r
        continue
    f=receipt.with_name(receipt.name.removesuffix(".receipt.json")+".body")
    b=f.read_bytes() if f.exists() else json.loads(f.with_name(f.name+".json").read_text())["raw"].encode()
    assert len(b)==r["bytes"]
    assert hashlib.sha256(b).hexdigest()==r["sha256"]
print("Lossless wrappers and received response-body digests verified")
