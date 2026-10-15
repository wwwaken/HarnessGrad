"""Offline reconciliation of retained metadata and payload-free identity inventories.

Never imports a loader/scorer, opens answer columns, or performs network requests.
Use --write only for this worker's summary; default checks it without mutation.
The prior verify_evidence.py separately authenticates approved range bytes.
"""
import collections
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIOR = ROOT / "tests/fixtures/hg_trivia3"


def load(path):
    return json.loads(path.read_text())


def build():
    observations = load(PRIOR / "observations.json")
    final_attempt = load(PRIOR / "key-audit-summary.json")
    declarations = load(PRIOR / "declarations.json")["declarations"]
    # Reuse the completed declaration review, rather than repeat its inventory scan.
    declared = [r["name"] for r in declarations]
    routed = [r["name"] for r in declarations if r["export_routes"] is not None]
    scope = load(HERE / "count-source-scope.json")
    source_files = []
    for name in scope:
        data = (ROOT / name).read_bytes()
        source_files.append({"path": name, "bytes": len(data),
                             "sha256": hashlib.sha256(data).hexdigest()})

    inventories, qsets, dsets = [], {}, {}
    for item in final_attempt["results"]:
        inv = item["identity_inventory"]
        data = Path(inv["path"]).read_bytes()
        assert len(data) == inv["bytes"]
        assert hashlib.sha256(data).hexdigest() == inv["sha256"]
        rows = [json.loads(line) for line in data.splitlines()]
        assert len(rows) == item["footer_row_count"]
        qids, keys = [], []
        empty_documents = 0
        for ordinal, row in enumerate(rows):
            assert set(row) <= {"shard_ordinal", "question_id", "question_source",
                                "entity_pages", "search_results"}
            assert row["shard_ordinal"] == ordinal
            qids.append(row["question_id"])
            filenames = []
            for group in ("entity_pages", "search_results"):
                nested = row.get(group, {})
                assert set(nested) <= {"filename", "doc_source"}
                filenames.extend(nested.get("filename", []))
            empty_documents += not filenames
            keys.extend(row["question_id"] + "--" + name for name in filenames)
        path = item["path"]
        qsets[path], dsets[path] = set(qids), set(keys)
        inventories.append({
            "path": path, "inventory": inv, "rows": len(rows),
            "distinct_question_ids": len(set(qids)),
            "question_id_duplicate_excess": len(qids) - len(set(qids)),
            "candidate_doc_key_occurrences": len(keys),
            "distinct_candidate_doc_keys": len(set(keys)),
            "candidate_doc_key_duplicate_excess": len(keys) - len(set(keys)),
            "rows_with_no_exported_filenames": empty_documents,
            "question_source_counts": dict(sorted(collections.Counter(
                row["question_source"] for row in rows).items())),
            "document_source_counts": dict(sorted(collections.Counter(
                source for row in rows for group in ("entity_pages", "search_results")
                for source in row.get(group, {}).get("doc_source", [])).items())),
        })
    pairs = []
    for a, b in itertools.combinations(sorted(qsets), 2):
        pairs.append({"a": a, "b": b,
                      "shared_question_ids": len(qsets[a] & qsets[b]),
                      "a_only_question_ids": len(qsets[a] - qsets[b]),
                      "b_only_question_ids": len(qsets[b] - qsets[a]),
                      "shared_candidate_doc_keys": len(dsets[a] & dsets[b]),
                      "a_only_candidate_doc_keys": len(dsets[a] - dsets[b]),
                      "b_only_candidate_doc_keys": len(dsets[b] - dsets[a])})
    for actual, prior in zip(pairs, observations["intersections"]):
        assert all(actual[k] == v for k, v in prior.items())
    a, b = sorted(p for p in qsets if p.startswith("rc/"))
    custody = "tests/fixtures/hg_wsel/triviaqa.json"
    custody_bytes = (ROOT / custody).read_bytes()
    committed_custody = subprocess.check_output(["git", "show", "HEAD:" + custody], cwd=ROOT)
    assert custody_bytes == committed_custody
    card = ROOT / scope[0]
    count_lines = [{"line": i, "text": text} for i, text in
                   enumerate(card.read_text().splitlines(), 1)
                   if "num_examples: 17944" in text or "|     18669|" in text]
    return {
        "revision": observations["revision"],
        "section_verdicts": {"1": "UNKNOWN", "2": "DECIDED", "3": "UNKNOWN", "4": "UNKNOWN"},
        "upstream_execution": "PENDING-UPSTREAM; no search performed",
        "human_answers": {
            "input_present_rows": None, "input_nonempty_rows": None,
            "preserved_rows": None, "truncated_rows": None,
            "deduplicated_rows": None, "redundant_rows": None,
            "conflicting_rows": None, "null_means": "UNKNOWN, not zero",
            "measured_footer_schema_scope": [
                {"path": r["path"], "rows": r["rows"],
                 "dedicated_human_answers_field": r["human_answer_field_present"],
                 "domain_or_verification_field": r["verification_or_domain_field_present"]}
                for r in observations["footers"]],
        },
        "configurations": {
            "declared": declared, "exported_routes": routed,
            "declaration_only": sorted(set(declared) - set(routed)),
            "route_only": sorted(set(routed) - set(declared)),
        },
        "validation_count_discrepancy": {
            "primary_retained_card": scope[0], "count_lines": count_lines,
            "prose": 18669, "structured": 17944, "arithmetic_difference": 18669 - 17944,
            "measured_rc_nocontext_validation_rows": next(
                r["rows"] for r in observations["footers"]
                if r["path"] == "rc.nocontext/validation-00000-of-00001.parquet"),
            "cause": "UNKNOWN", "prose_member_inventory": "UNKNOWN",
            "scope": source_files,
        },
        "complete_key_shards": inventories, "pairwise_sets": pairs,
        "two_rc_shards": {
            "rows": sum(r["rows"] for r in inventories if r["path"] in (a, b)),
            "distinct_question_ids": len(qsets[a] | qsets[b]),
            "question_id_duplicate_excess": len(qsets[a] & qsets[b]),
            "candidate_doc_key_occurrences": sum(
                r["candidate_doc_key_occurrences"] for r in inventories if r["path"] in (a, b)),
            "distinct_candidate_doc_keys": len(dsets[a] | dsets[b]),
            "candidate_doc_key_duplicate_excess": len(dsets[a] & dsets[b]),
        },
        "original_domain_verified_membership": "UNKNOWN",
        "official_export_key_mapping": "UNKNOWN", "official_numeric_denominator": "UNKNOWN",
        "full_row_duplicates_and_answer_agreement": "UNKNOWN",
        "custody": {"path": custody, "bytes": len(custody_bytes),
                    "sha256": hashlib.sha256(custody_bytes).hexdigest(),
                    "byte_identical_to_HEAD": True, "used_for_membership_audit": False},
    }


if __name__ == "__main__":
    result = build()
    encoded = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    target = HERE / "summary.json"
    if sys.argv[1:] == ["--write"]:
        target.write_text(encoded)
    else:
        assert not sys.argv[1:]
        assert target.read_text() == encoded
    print(json.dumps({"verified": True, "section_verdicts": result["section_verdicts"],
                      "source_scope_files": len(result["validation_count_discrepancy"]["scope"]),
                      "complete_key_shards": len(result["complete_key_shards"]),
                      "two_rc_shards": result["two_rc_shards"],
                      "official_numeric_denominator": "UNKNOWN",
                      "custody_byte_identical": True}, sort_keys=True))
