"""Recheck old inventory bytes separately from its stale whole-registry baseline.

The original audit and its refusal remain unchanged and preserved. This caller
does not authorize a run, change evidence or replace that validator's result.
"""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
prior = ROOT / "tests/fixtures/hg_wjournalcov"
spec = importlib.util.spec_from_file_location("prior_inventory_audit", prior / "audit.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
summary, inventories, lines = module.derive()
outputs = {"observations.json": json.dumps(summary, indent=2) + "\n",
           "source-lines.txt": lines,
           "file-hashes.json": json.dumps(module.FILES, sort_keys=True, indent=2) + "\n"}
outputs.update({n + "-inventory.json": json.dumps(value, indent=2) + "\n"
                for n, value in inventories.items()})
for name, value in outputs.items():
    assert (prior / name).read_text() == value, name
print(json.dumps({"current_bytes_equal_prior_inventory": True,
                  "derived_files_compared": sorted(outputs),
                  "datasets": sorted(inventories),
                  "inherited_registry_check": "failed: retained older baseline predates parent merges",
                  "replacement_registry_scope_check": "hg_wjc2/check_scope.py against exact starting HEAD",
                  "production_authorized": False}, indent=2))
