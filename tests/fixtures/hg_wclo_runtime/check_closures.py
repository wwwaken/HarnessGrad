"""Validate inspected bytes and scope without importing adapters or invoking scorers."""
import argparse
import hashlib
import json
from pathlib import Path
import re

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--write", action="store_true", help="write literal locators and fixture SHA256SUMS")
parser.add_argument("--external", action="store_true", help="also hash external locally observed source/data files")
args = parser.parse_args()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


cache = {}
skipped = set()


def check_file(label, digest):
    path = Path(label)
    if path.is_absolute():
        if not path.is_relative_to(ROOT) and not args.external:
            skipped.add(label)
            return
    else:
        path = ROOT / path
    assert re.fullmatch(r"[0-9a-f]{64}", digest), f"bad SHA256: {label}"
    key = str(path)
    if key not in cache:
        assert path.is_file(), f"missing hash preimage: {label}"
        cache[key] = sha(path)
    assert cache[key] == digest, f"byte identity changed: {label}"


def walk(value, owner):
    if isinstance(value, dict):
        if isinstance(value.get("path"), str) and isinstance(value.get("sha256"), str):
            label = value["path"]
            if label.startswith("../"):
                label = str((owner.parent / label).resolve())
            check_file(label, value["sha256"])
        for key, child in value.items():
            # These paths are relative to stdlib_root, not the repository.
            if key != "stdlib_members":
                walk(child, owner)
    elif isinstance(value, list):
        for child in value:
            walk(child, owner)


registry = json.loads((ROOT / "docs/dataset-blockers.json").read_text())
scope = {r["dataset"] for r in registry["datasets"] if "scorer-offline-closure" in r["shared_blockers"]}
survey = (ROOT / "reports/w-shared-topology-survey.md").read_text()
survey_scope = set(re.findall(r"^\| `([a-z0-9_]+)` \|", survey, re.M))
assert scope == survey_scope, "registry/topology scope changed; review applicability"
records = [json.loads(p.read_text()) for p in sorted((OUT / "datasets").glob("*.json"))]
assert {r["dataset"] for r in records} == scope and len(records) == len(scope), "dataset record coverage/uniqueness"
snapshot = {"gaia", "tau_bench", "appworld", "terminal_bench"}
locators = []
for row in records:
    name = row["dataset"]
    assert row["isolation_class"] == ("snapshot-service" if name in snapshot else "actor-workdir"), name
    assert row["closure_status"] == "partial-byte-pins", f"unsupported completeness claim: {name}"
    for field in ("entrypoints", "gold_artifacts", "interpreter", "not_pinned"):
        assert row.get(field), f"missing {field}: {name}"
    assert isinstance(row.get("third_party_packages"), list), f"missing dependency surface: {name}"
    walk(row, OUT / "datasets" / f"{name}.json")
    # Alternate controllers and task-specific shell/test functions are separate
    # entrypoints too. Collect nested lists while removing repeated references.
    entries = {}
    def collect_entries(value):
        if isinstance(value, dict):
            if {"path", "line", "symbol", "sha256"} <= value.keys() and value["sha256"]:
                entries[(value["path"], value["line"], value["symbol"])] = value
            for child in value.values():
                collect_entries(child)
        elif isinstance(value, list):
            for child in value:
                collect_entries(child)
    collect_entries(row)
    for entry in entries.values():
        path = Path(entry["path"])
        if path.is_absolute() and not args.external:
            continue
        source = path if path.is_absolute() else ROOT / path
        lines = source.read_text().splitlines()
        line = entry["line"]
        assert isinstance(line, int) and 0 < line <= len(lines), f"entrypoint line: {name} {entry}"
        locator = lines[line - 1]
        assert locator.strip(), f"blank entrypoint line: {name} {entry}"
        # Store literal byte-derived text, not a paraphrased function description.
        locators.append({"dataset": name, "path": entry["path"], "line": line,
                         "symbol": entry["symbol"], "locator": locator})

for name in ("host-runtime.json", "native-abi-byte-pins.json", "import-byte-pins.json"):
    value = json.loads((OUT / name).read_text())
    walk(value, OUT / name)
    if name == "host-runtime.json" and args.external:
        interpreter = value["interpreter"]
        payload = "".join(f'{r["sha256"]}  {r["path"]}\n' for r in interpreter["stdlib_members"])
        assert hashlib.sha256(payload.encode()).hexdigest() == interpreter["stdlib_manifest_sha256"]
        for member in interpreter["stdlib_members"]:
            check_file(str(Path(interpreter["stdlib_root"]) / member["path"]), member["sha256"])

# Check all additional dataset-specific inventories too (the collection scripts
# contain no adapter imports). prior-evidence-audit deliberately contains absent files.
for path in sorted(OUT.glob("*.json")):
    if path.name not in {"prior-evidence-audit.json", "evidence-locators.json"}:
        walk(json.loads(path.read_text()), path)

locator_path = OUT / "evidence-locators.json"
if args.write:
    locator_path.write_text(json.dumps(locators, indent=2, sort_keys=True) + "\n")
else:
    saved = json.loads(locator_path.read_text())
    if not args.external:
        saved = [r for r in saved if not Path(r["path"]).is_absolute()]
    assert saved == locators, "stale entrypoint locator inventory"

files = sorted(p for p in OUT.rglob("*") if p.is_file() and p != OUT / "SHA256SUMS")
assert not any("__pycache__" in p.parts for p in files), "unexpected bytecode fixture"
manifest = "".join(f"{sha(p)}  {p.relative_to(OUT)}\n" for p in files)
if args.write:
    (OUT / "SHA256SUMS").write_text(manifest)
else:
    assert (OUT / "SHA256SUMS").read_text() == manifest, "fixture manifest coverage/hash mismatch"
print(json.dumps({"valid": True, "datasets": len(records), "actor_workdir": len(records) - len(snapshot),
                  "snapshot_service": len(snapshot), "entrypoint_locators": len(locators),
                  "byte_preimages_checked": len(cache), "external_preimages_skipped": len(skipped),
                  "fixture_files": len(files), "complete_offline_closures": 0, "benchmark_executions": 0}))
