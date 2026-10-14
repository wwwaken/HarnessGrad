"""Verify acquired evidence offline without importing adapters or upstream code.

Run: PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/hg_e1_review/verify.py
"""
import ast
import base64
import csv
import hashlib
import io
import json
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def literal(path, name):
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign):
            if any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
                return ast.literal_eval(node.value)
    raise AssertionError(f"missing literal {name}")


def verify():
    checksums = (ROOT / "SHA256SUMS").read_text().splitlines()
    for line in checksums:
        expected, name = line.split("  ", 1)
        assert digest((ROOT / name).read_bytes()) == expected, name

    successes, failures = [], []
    for path in sorted(ROOT.glob("*.receipt.json")):
        receipt = json.loads(path.read_text())
        raw = (ROOT / receipt["body"]).read_bytes()
        assert digest(raw) == receipt["sha256"]
        assert len(raw) == receipt["bytes"]
        (successes if receipt["status"] == 200 else failures).append(path.name)

    decoded = {}
    for name, output in [
        ("fever-scorer-source-api", "fever-upstream-scorer.py"),
        ("fever-scorer-setup-api", "fever-upstream-setup.py"),
        ("bigbench-task-api", "bigbench-physics-task.json"),
        ("bigbench-metrics-api", "bigbench-task-metrics.py"),
        ("bigbench-json-task-api", "bigbench-json-task.py"),
        ("fever-conversion-source-api", "fever-create-nli-dataset.py"),
        ("fever-conversion-reader-api", "fever-conversion-datareader.py"),
    ]:
        payload = json.loads((ROOT / f"{name}.body").read_text())
        raw = base64.b64decode(payload["content"])
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        assert hashlib.sha1(blob).hexdigest() == payload["sha"]
        assert raw == (ROOT / output).read_bytes()
        decoded[output] = {"sha256": digest(raw), "git_blob_sha1": payload["sha"]}

    hub = json.loads((ROOT / "fever-hub-proxy-revision.body").read_text())
    assert hub["sha"] == literal(REPO / "data/datasets/fever.py", "REVISION")
    hub_tree = json.loads((ROOT / "fever-hub-proxy-tree.body").read_text())
    hub_paths = {item["path"]: item for item in hub_tree}
    assert set(hub_paths) == {item["rfilename"] for item in hub["siblings"]}
    readme = (ROOT / "fever-hub-proxy-readme.body").read_bytes()
    assert hashlib.sha1(b"blob " + str(len(readme)).encode() + b"\0" + readme).hexdigest() == hub_paths["README.md"]["oid"]
    conversion_commit = json.loads((ROOT / "fever-conversion-head.body").read_text())
    conversion_tree = json.loads((ROOT / "fever-conversion-tree.body").read_text())
    assert conversion_commit["commit"]["tree"]["sha"] == conversion_tree["sha"]
    assert conversion_tree["truncated"] is False
    for source, path in [("fever-conversion-source-api", "scripts/create_nli_dataset.py"),
                         ("fever-conversion-reader-api", "datareader.py")]:
        payload = json.loads((ROOT / f"{source}.body").read_text())
        assert any(item["path"] == path and item["sha"] == payload["sha"] for item in conversion_tree["tree"])

    adapter = REPO / "data/datasets/physicsquestions.py"
    archive = (ROOT / "rewoo-archive.body").read_bytes()
    assert digest(archive) == literal(adapter, "REWOO_SHA256")
    commit = json.loads((ROOT / "rewoo-commit.body").read_text())["sha"]
    assert commit == literal(adapter, "REWOO_COMMIT")
    with tarfile.open(fileobj=io.BytesIO(archive)) as handle:
        member = f"ReWOO-{commit}/data/bigbench/physics_question.csv"
        raw_csv = handle.extractfile(member).read()
        assert raw_csv == (ROOT / "rewoo-physics.csv").read_bytes()
    rows = list(csv.DictReader(io.StringIO(raw_csv.decode())))
    task = json.loads((ROOT / "bigbench-physics-task.json").read_text())
    nonblank = [example for example in task["examples"] if example["input"].strip()]
    assert len(rows) == len(nonblank) == literal(adapter, "N_TOTAL") == 53
    # Compare ordered rows, not an input-keyed dict: the source repeats an input.
    for row, example in zip(rows, nonblank):
        assert row["input"] == example["input"]
        assert row["target"].startswith("Can be one of ")
        assert ast.literal_eval(row["target"][len("Can be one of "):]) == example["target"]
    assert len(task["examples"]) == 54
    assert task["preferred_score"] == "exact_str_match"

    return {
        "valid": True,
        "checksummed_files": len(checksums),
        "successful_http_responses": successes,
        "preserved_failed_requests": failures,
        "decoded_sources": decoded,
        "fever": {"hub_revision": hub["sha"],
                  "valid_export_git_blob_sha1_from_metadata": hub_paths["valid.jsonl"]["oid"],
                  "valid_export_bytes_from_metadata": hub_paths["valid.jsonl"]["size"],
                  "hub_readme_matches_revision_tree": True,
                  "referenced_conversion_source_revision": conversion_commit["sha"],
                  "conversion_source_to_hub_export_binding_verified": False,
                  "original_evidence_group_preservation_verified": False},
        "physics": {"archive_sha256_matches_declaration": True,
                    "csv_member_sha256": digest(raw_csv), "csv_rows": len(rows),
                    "bigbench_examples": len(task["examples"]),
                    "ordered_input_and_target_list_matches": len(nonblank),
                    "bigbench_revision": json.loads((ROOT / "bigbench-head.body").read_text())["sha"],
                    "installed_source_or_selected_manifest_verified": False},
        "bird_original_metadata_present_in_packet": False,
        "production_runtime_or_measurement_verified": False,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
