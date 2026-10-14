"""Verify this evidence packet offline. Does not import adapters or upstream code."""
import hashlib
import json
from pathlib import Path

import build_custody

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]


def verify():
    listed = {}
    for line in (ROOT / "SHA256SUMS").read_text().splitlines():
        expected, name = line.split("  ", 1)
        assert name not in listed
        path = ROOT / name
        assert path.resolve().is_relative_to(ROOT.resolve()) and not path.is_symlink()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, name
        listed[name] = expected
    actual = {str(p.relative_to(ROOT)) for p in ROOT.rglob("*")
              if p.is_file() and p != ROOT / "SHA256SUMS" and "__pycache__" not in p.parts}
    # Nested packets may carry their own manifests; those manifests are themselves
    # included in the root manifest, alongside all raw bytes and derived files.
    assert actual == set(listed), (actual - set(listed), set(listed) - actual)
    source = json.loads((ROOT / "source-receipt.json").read_text())
    for name, item in source["files"].items():
        raw = (ROOT / item["snapshot"]).read_bytes()
        assert len(raw) == item["bytes"]
        assert hashlib.sha256(raw).hexdigest() == item["sha256"]
        assert raw == (REPO / name).read_bytes(), f"source changed: {name}"
    manifests, summary = build_custody.derive()
    for name, member in build_custody.MEMBERS.items():
        assert (ROOT / "installed" / (name + ".csv")).read_bytes() == (
            ROOT / "rewoo" / ("installed-" + member)).read_bytes()
        assert (ROOT / "rewoo" / ("adapter-" + name + ".py")).read_bytes() == (
            REPO / "data/datasets" / (name + ".py")).read_bytes()
    for name, value in manifests.items():
        assert json.loads((ROOT / "manifests" / (name + ".json")).read_text()) == value
        assert value["selected_manifest"] is None
    assert json.loads((ROOT / "custody-summary.json").read_text()) == summary
    before = json.loads((ROOT / "starting-blockers.json").read_text())
    after = {d["dataset"]: d for d in json.loads((REPO / "docs/dataset-blockers.json").read_text())["datasets"]}
    for dataset in before:
        name = dataset["dataset"]
        current = after[name]
        assert {k: v for k, v in dataset.items() if k != "blockers"} == {
            k: v for k, v in current.items() if k != "blockers"}
        assert len(dataset["blockers"]) == len(current["blockers"]) == 1
        for key in ("id", "family", "status"):
            assert dataset["blockers"][0][key] == current["blockers"][0][key]
        assert current["blockers"][0]["status"] == "measurement"
    return {"valid": True, "checksummed_files": len(listed),
            "source_files_bound": len(source["files"]),
            "row_manifests_reproduced": {name: value["loaded_rows"] for name, value in summary.items()},
            "selected_manifests_verified": 0, "blockers_closed": 0,
            "production_authorized": False,
            "scope": "point-in-time host bytes and source-derived structural custody; no runtime measurement"}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
