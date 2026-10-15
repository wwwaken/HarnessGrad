"""Inert byte/row/source audit. No adapter imports, selection, scoring or runs.

Capture stdout verbatim as audit-output.json. --check rederives observations and
inventories from current local bytes and checks the permitted registry delta.
Row hashes are canonical parsed JSON, never raw CSV-line or selected-gold hashes.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
NAMES = ("fever", "physicsquestions", "reasoning_gym", "sportsunderstanding",
         "spreadsheetbench", "strategyqa")
DATA = Path("/mnt/20t/xubuqiang/datasets")
FILES = {}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode()


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    label = str(path.relative_to(REPO)) if path.is_relative_to(REPO) else str(path)
    FILES[label] = {"bytes": len(raw), "sha256": digest(raw)}
    return raw


def literal(path, name):
    for node in ast.parse(read(path)).body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError((path, name))


def split_inventory(ids):
    evaluation = [t for t in ids if hashlib.sha256(t.encode()).digest()[0] % 3 == 0]
    eval_set = set(evaluation)
    train = [t for t in ids if t not in eval_set]
    split_raw = json.dumps({"train": sorted(train), "eval": sorted(evaluation)},
                           sort_keys=True).encode()
    return {"source": "hash", "train": train, "eval": evaluation,
            "split_sha256": digest(split_raw), "official_eval": None}


def derive():
    result = {}
    inventories = {}
    sources = [REPO / "data/datasets" / (n + ".py") for n in NAMES]
    sources += [REPO / p for p in (
        "data/scaffolds/qa/base.py", "data/scaffolds/qa/read.py",
        "data/scaffolds/qa/verify/check.py", "data/scaffolds/qa/evidence_scorers.py",
        "data/scaffolds/registry.py", "data/scaffolds/scorer_input.py",
        "data/datasets/spreadsheetbench/verify/check.py",
        "data/datasets/reasoning_gym/prepare.py")]
    source_lines = []
    for path in sources:
        raw = read(path)
        source_lines.append(f"FILE {path.relative_to(REPO)} sha256={digest(raw)}")
        # JSON-quoted lines preserve source whitespace without creating trailing
        # whitespace in the numbered evidence wrapper (including empty lines).
        source_lines.extend(f"{i}: {json.dumps(line, ensure_ascii=False)}"
                            for i, line in enumerate(raw.decode().splitlines(), 1))
    reports = ["reports/w-clo-actor-closures.md", "reports/w-offscorer2-coverage.md",
               "reports/e1-fever-physics-bird-review.md", "reports/w-offscorer-equivalence.md",
               "reports/w-spread2-reconciliation.md", "reports/w-tbi-receipts.md",
               "reports/w-tbi2-receipts.md", "reports/w-resolver2-payloads.md",
               "reports/w-prov-validation.txt", "tests/fixtures/hg_wprov/README.md"]
    # Preserve the discovery result: no imaginary w-prov-*.md report is cited.
    prov_reports = sorted(str(p.relative_to(REPO)) for p in (REPO / "reports").glob("w-prov-*.md"))
    for rel in reports + prov_reports:
        read(REPO / rel)
    for name in NAMES:
        adapter = REPO / "data/datasets" / (name + ".py")
        if name == "spreadsheetbench":
            continue
        if name == "fever":
            path = DATA / name / literal(adapter, "VALID")
            pool_split = "validation"
        elif name == "reasoning_gym":
            path = DATA / name / literal(adapter, "POOL")
            pool_split = "eval"
        else:
            path = DATA / name / literal(adapter, "CSV_PATH")
            pool_split = "test"
        raw = read(path)
        rows = ([json.loads(line) for line in raw.decode().splitlines() if line.strip()]
                if name in {"fever", "reasoning_gym"}
                else list(csv.DictReader(io.StringIO(raw.decode(), newline=""))))
        if name == "physicsquestions":
            rows = [r for r in rows if str(r.get("input") or "").strip()]
        ids = [f"{name}/{pool_split}/{i}" for i in range(len(rows))]
        division = split_inventory(ids)
        eval_set = set(division["eval"])
        mapping = [{"task_id": tid, "loaded_position": i,
                    "parsed_row_sha256": digest(canonical(row)),
                    "declared_side": "eval" if tid in eval_set else "train"}
                   for i, (tid, row) in enumerate(zip(ids, rows))]
        detail = {"source_path": str(path), "source_bytes": len(raw),
                  "source_sha256": digest(raw), "source_pool_split": pool_split,
                  "loaded_rows": len(rows), "declared_train": len(division["train"]),
                  "declared_eval": len(division["eval"]),
                  "declared_split_sha256": division["split_sha256"]}
        if name != "fever":
            old = REPO / "tests/fixtures/hg_wprov"
            prior = json.loads(read(old / "manifests" / (name + ".json")))
            installed = old / "installed" / (name + (".jsonl" if name == "reasoning_gym" else ".csv"))
            assert read(installed) == raw
            for item, previous in zip(mapping, prior["loaded_rows"], strict=True):
                assert all(item[k] == previous[k] for k in item)
            assert division == prior["declared_split"]
            assert prior["selected_manifest"] is None
            detail["preserved_wprov_bytes_rows_split_match"] = True
        if name == "reasoning_gym":
            assert digest(raw) == literal(adapter, "POOL_SHA256")
            counts = Counter(r["family"] for r in rows)
            families = literal(REPO / "data/datasets/reasoning_gym/prepare.py", "FAMILIES")
            size = literal(adapter, "PER_FAMILY")
            assert [(r["family"], r["index"]) for r in rows] == [
                (f, i) for f in families for i in range(size)]
            assert all(str(r["entry"].get("answer", "")).strip() for r in rows)
            assert all(r["question"] == str(r["entry"]["question"]).strip() for r in rows)
            detail.update(families=len(counts), per_family_counts=dict(sorted(counts.items())),
                          declared_pool_digest_matches=True, behavioral_eligibility_established=False)
        if name == "fever":
            old = json.loads(read(REPO / "tests/fixtures/hg_wclo_actor/gold/fever.json"))
            detail["matches_prior_local_gold_byte_observation"] = (
                old["artifacts"][0]["sha256"] == digest(raw))
            detail["label_counts"] = dict(sorted(Counter(str(r.get("label")) for r in rows).items()))
            detail["nonempty_claims"] = sum(bool(str(r.get("claim", "")).strip()) for r in rows)
            detail["rows_with_id_field"] = sum("id" in r for r in rows)
            detail["raw_evidence_container_counts"] = dict(sorted(Counter(
                type(r.get("evidence")).__name__ for r in rows).items()))
            detail["upstream_id_group_correspondence_authenticated"] = False
            tree = json.loads(read(REPO / "tests/fixtures/hg_e1_review/fever-hub-proxy-tree.body"))
            revision = json.loads(read(REPO / "tests/fixtures/hg_e1_review/fever-hub-proxy-revision.body"))
            member = next(item for item in tree if item["path"] == literal(adapter, "VALID"))
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            detail["installed_git_blob_sha1"] = blob
            detail["authenticated_tree_member"] = member
            detail["authenticated_hub_revision"] = revision["sha"]
            assert revision["sha"] == literal(adapter, "REVISION")
            detail["installed_matches_authenticated_tree_blob_and_size"] = (
                blob == member["oid"] and len(raw) == member["size"])
        inventories[name] = {"dataset": name, "row_hash_encoding":
            "UTF-8 json.dumps(ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)",
            "rows": mapping, "declared_split": division, "official_mode_eval_ids": ids,
            "scope": "Static loader inventory; not behavioral/gradable/admission eligibility or a selection."}
        result[name] = detail

    name = "spreadsheetbench"
    adapter = REPO / "data/datasets/spreadsheetbench.py"
    root = DATA / name
    release_dir = literal(adapter, "RELEASE_DIR")
    tasks_json = release_dir + "/dataset.json"  # TASKS_JSON's source f-string, inertly expanded.
    assert 'TASKS_JSON = f"{RELEASE_DIR}/dataset.json"' in read(adapter).decode()
    metadata_path = root / tasks_json
    metadata = read(metadata_path)
    rows = json.loads(metadata)
    assert len(rows) == literal(adapter, "N_TASKS")
    archive_path = root / "_src" / literal(adapter, "TARBALL")
    archive_raw = read(archive_path)
    assert digest(archive_raw) == literal(adapter, "TARBALL_SHA256")
    patterns = literal(adapter, "_WORKBOOK_PATTERNS")
    mapping = []
    with tarfile.open(fileobj=io.BytesIO(archive_raw), mode="r:gz") as archive:
        assert archive.extractfile(tasks_json).read() == metadata
        for i, row in enumerate(rows):
            tid = str(row["id"])
            folder = root / release_dir / str(row["spreadsheet_path"])
            item = {"task_id": tid, "loaded_position": i, "parsed_row_sha256": digest(canonical(row)),
                    "declared_side": "eval" if hashlib.sha256(tid.encode()).digest()[0] % 3 == 0 else "train"}
            assert str(row["answer_position"]).strip()
            for kind in ("init", "golden"):
                candidates = [folder / p.format(id=tid) for p in patterns[kind]]
                path = next((p for p in candidates if p.is_file()), None)
                if path is None:
                    for pattern in patterns[kind][2:]:
                        matches = sorted(folder.glob(pattern))
                        if matches:
                            path = matches[0]
                            break
                assert path is not None, (tid, kind)
                raw = read(path)
                member = str(path.relative_to(root))
                archived = archive.extractfile(member).read()
                assert archived == raw, member
                item[kind] = {"path": str(path), "archive_member": member,
                              "bytes": len(raw), "sha256": digest(raw), "archive_equal": True}
            mapping.append(item)
    ids = [r["task_id"] for r in mapping]
    assert len(set(ids)) == len(ids)
    division = split_inventory(ids)
    inventories[name] = {"dataset": name, "rows": mapping, "declared_split": division,
        "official_mode_eval_ids": ids, "all_eval_override": "HG_SPREADSHEETBENCH_SPLIT=none",
        "scope": "Default-path metadata/init/golden bytes only; no workbook load, cells, formula or gradability test."}
    result[name] = {"source_path": str(metadata_path), "source_bytes": len(metadata),
        "source_sha256": digest(metadata), "source_pool_split": "verified_400",
        "loaded_rows": len(rows), "declared_train": len(division["train"]),
        "declared_eval": len(division["eval"]), "declared_split_sha256": division["split_sha256"],
        "archive_path": str(archive_path), "archive_sha256": digest(archive_raw),
        "archive_matches_adapter_pin": True, "metadata_archive_equal": True,
        "workbook_members_compared": sum(len([r["init"], r["golden"]]) for r in mapping),
        "all_workbook_members_archive_equal": all(r[k]["archive_equal"] for r in mapping for k in ("init", "golden")),
        "independent_upstream_authentication_established": False,
        "gradable_eligibility_established": False}
    for name in NAMES:
        result[name].update(run_id=None, selected_manifest=None, selected_only_export=None,
            chosen_split_mode=None, chosen_side=None, selected_tasks=None, expected_trials=None,
            measured_trials=None, invalid_trials=None, unmeasured_trials=None,
            production_authorized=False)
    summary = {"datasets": result, "w_prov_markdown_report_matches": prov_reports,
        "selection_authority": "No independent run-specific manifest, fresh run ID, split mode or side supplied. Inventory is not authorization.",
        "environment_observations": {k: os.environ.get(k) for k in (
            "HG_SPREADSHEETBENCH_DATA", "HG_SPREADSHEETBENCH_SPLIT", "HG_QA_SPLIT")},
        "scope": "Read-only host/default-path observation and inert source derivation; no upstream/scorer/adapter execution, network, model, endpoint, run or filesystem export."}
    return summary, inventories, "\n".join(source_lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    summary, inventories, lines = derive()
    outputs = {"observations.json": json.dumps(summary, indent=2) + "\n",
               "source-lines.txt": lines,
               "file-hashes.json": json.dumps(FILES, sort_keys=True, indent=2) + "\n"}
    outputs.update({n + "-inventory.json": json.dumps(value, indent=2) + "\n"
                    for n, value in inventories.items()})
    for rel, raw in outputs.items():
        if args.check:
            assert (HERE / rel).read_text() == raw, rel
        else:
            path = HERE / rel
            assert not path.exists(), path
            path.write_text(raw)
    if args.check:
        baseline = json.loads((HERE / "registry-before.json").read_text())
        current = json.loads((REPO / "docs/dataset-blockers.json").read_text())
        for document in (baseline, current):
            for row in document["datasets"]:
                if row["dataset"] in NAMES:
                    for blocker in row["blockers"]:
                        blocker.pop("observed")
        assert baseline == current, "Registry delta escaped the six observed fields"
    print(json.dumps({"valid": True, "observations": summary,
                      "hashed_files": len(FILES), "closed_blockers": []}, indent=2))


if __name__ == "__main__":
    main()
