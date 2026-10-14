"""Check the verification packet, unchanged registry, and allowed diff scope."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
baseline = json.loads((HERE / "baseline.json").read_text())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


checker = subprocess.run(["python3", "tools/check_dataset_blockers.py"], cwd=ROOT, capture_output=True, text=True)
print("$ PYTHONDONTWRITEBYTECODE=1 python3 tools/check_dataset_blockers.py")
print(checker.stdout, end="")
print(checker.stderr, end="")
assert checker.returncode == 0
assert json.loads(checker.stdout)["valid"] is True
registry = ROOT / "docs/dataset-blockers.json"
actual = sha(registry.read_bytes())
assert actual == baseline["sha256"]["docs/dataset-blockers.json"]
assert not git("diff", baseline["head"], "--", "docs/dataset-blockers.json")
print("registry_before_sha256=" + actual)
print("registry_after_sha256=" + actual)
print("registry_unchanged=true")

journal = (ROOT / "docs/adapter-integration-journal.md").read_bytes()
assert sha(journal[:baseline["journal_bytes"]]) == baseline["sha256"]["docs/adapter-integration-journal.md"]
assert len(journal) > baseline["journal_bytes"]
print("journal_append_only=true")

names = set(git("diff", "--name-only", baseline["head"]).splitlines())
names.update(git("ls-files", "--others", "--exclude-standard").splitlines())
assert all(p.startswith(("reports/", "tests/fixtures/hg_wverify/")) or p == "docs/adapter-integration-journal.md" for p in names)
frozen = ["reports/w-offscorer-equivalence.md", "tests/fixtures/hg_woffscorer/", "reports/w-img-abi-custody.md",
          "tests/fixtures/hg_wimg/", "reports/w-net-receipts.md", "reports/w-net-evidence/", "data/", "eval/"]
assert not git("diff", baseline["head"], "--", *frozen)
print("allowed_diff_scope=true")
print("frozen_evidence_adapters_and_runtime_unchanged=true")

sources = json.loads((HERE / "scorers/source-custody.json").read_text())
for row in sources:
    if "copy" in row:
        assert sha((ROOT / row["copy"]).read_bytes()) == row["sha256"]
    else:
        assert sha((ROOT / row["source"]).read_bytes()) == row["sha256"] == row["original_worker_source_sha256"]
print("primary_scorer_source_pins_match=true")
for row in json.loads((HERE / "extra-scorers/source-copy-identities.json").read_text()):
    assert sha((HERE / "extra-scorers" / row["copy"]).read_bytes()) == row["sha256"]
print("additional_official_source_copy_pins_match=true")

primary = json.loads((HERE / "scorers/output.json").read_text())
assert all(n == 0 for n in primary["identity"]["cached_dataset_records"].values())
extra = json.loads((HERE / "extra-scorers/parent-review.json").read_text())
assert extra["all_original_summaries_reproduced"] is True
precision = json.loads((HERE / "extra-scorers/parent-musique-precision-aggregate.stdout.json").read_text())
assert precision["released_records_loaded"] == 0
assert precision["panels"]["crosscheck"]["aggregate_common_metrics_equal"] is True
print("parent_reviewed_scorer_replays=true")
print("released_dataset_records_loaded=0")

manifest = HERE / "SHA256SUMS"
entries = []
for line in manifest.read_text().splitlines():
    expected, path = line.split("  ", 1)
    assert sha((ROOT / path).read_bytes()) == expected, path
    entries.append(path)
actual_paths = sorted(str(p.relative_to(ROOT)) for p in HERE.rglob("*") if p.is_file() and p != manifest)
assert sorted(entries) == actual_paths
print("fixture_manifest_files=" + str(len(entries)))
print("fixture_manifest_complete=true")
print("PASS: registry valid and unchanged; frozen artifacts unchanged; journal append-only; packet hashes valid")
