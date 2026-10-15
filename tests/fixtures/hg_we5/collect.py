#!/usr/bin/env python3
"""Fresh bounded offline paired export controls; output directory must not exist."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import uuid
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from eval.admission import artifact_admission as artifacts
from eval.admission.pilot_admission import AdmissionError


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def state_view(root):
    return [{"path": str(p.relative_to(root)), "bytes": p.stat().st_size,
             "sha256": digest(p.read_bytes()), "mode": oct(p.stat().st_mode & 0o777),
             "inode": p.stat().st_ino, "uid": p.stat().st_uid, "gid": p.stat().st_gid,
             "mtime_ns": p.stat().st_mtime_ns}
            for p in sorted(root.rglob("*")) if p.is_file()]


def contract_for(case, names):
    # Reuse the real sealed control's declaration, whose closure bytes are rehashed
    # below. ONLY export_state/verify_state_export consume this derived contract.
    # The local dataset scorer does not execute under this control's sealed bundle.
    contract = json.loads((ROOT / "tests/fixtures/hg_wpristine/task-contract.json").read_text())
    contract.update(task_id=case["task_id"], source_sha256=digest(json.dumps(case, sort_keys=True).encode()))
    contract["export"] = {"files": [{"path": n, "max_bytes": 1048576} for n in names],
                          "max_bytes": 4194304, "max_inodes": 32}
    raw = json.dumps(contract, sort_keys=True).encode()
    return raw, digest(raw)


def project(source, destination, case, names, outer):
    raw, pin = contract_for(case, names)
    run = "w-e5-export-" + uuid.uuid4().hex
    binding = artifacts.execution_identity(case["task_id"], outer, "1")
    receipt = artifacts.export_state(source, destination, raw, pin, run_id=run, execution_binding=binding)
    artifacts.verify_state_export(destination, receipt, raw, pin, run_id=run, execution_binding=binding)
    return raw, pin, receipt, binding


def invoke(state, private, case, out, packet):
    request = dict(case, state=str(state), private=str(private), output=str(out / "scorer-output"))
    if case["kind"] == "qa":
        request["gold_sha256"] = case.get("expected_gold_sha256", digest((private / "gold.json").read_bytes()))
    out.mkdir()
    write_json(out / "request.json", request)
    argv = [sys.executable, str(HERE / "worker.py"), str(out / "request.json")]
    proc = subprocess.run(argv, capture_output=True, text=True, timeout=30,
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "CUDA_VISIBLE_DEVICES": ""})
    (out / "stdout.txt").write_text(proc.stdout)
    (out / "stderr.txt").write_text(proc.stderr)
    write_json(out / "process.json", {"argv": argv, "returncode": proc.returncode})
    if proc.returncode:
        raise RuntimeError(f"worker failed: {out.relative_to(packet)}; raw stderr retained")
    result = json.loads(proc.stdout)
    write_json(out / "result.json", result)
    return result


def semantic(result):
    e = result["evidence"]
    return {"measured": e.get("measured"), "reward_text": result["reward_text"],
            "reward": e.get("reward"), "correct": e.get("correct"),
            "official": e.get("official"), "returncode": result["returncode"]}


def qa_cases():
    cases = [
        ("gsm8k", {"answer": "18"}, "  '#### 18'\n", "#### 17\n", None),
        ("strategyqa", {"answer": "yes"}, " `Yes` \n", "No\n", None),
        ("triviaqa", {"value": "Crimson City", "accepted": ["crimson city", "red town"]},
         '"The red_town"\n', "blue town\n", None),
        ("fever", {"answer": "SUPPORTS", "evidence": [["Authored Page", 0, "authored sentence"]]},
         "REFUTES\n", "REFUTES\n", {"schema_version": 1, "answer": "SUPPORTS", "predicted_evidence": [["Authored Page", 0]]}),
        ("hotpotqa", {"answer": "red town", "supporting_facts": [["Authored Page", 0]]},
         "wrong fallback\n", "wrong fallback\n", {"schema_version": 1, "answer": "red town", "predicted_evidence": [["Authored Page", 0]]}),
        ("musique", {"id": "authored", "answer": "red town", "aliases": [], "supporting_facts": [["Authored Page", 0]]},
         "wrong fallback\n", "wrong fallback\n", {"schema_version": 1, "answer": "red town", "predicted_evidence": [["Authored Page", 0]]}),
        ("twowikimultihopqa", {"id": "authored", "type": "synthetic", "answer": "red town", "aliases": [],
                              "supporting_facts": [["Authored Page", 0]], "evidences": [["S", "born in", "O"]],
                              "evidences_id": [], "evidence_aliases": {}},
         json.dumps({"schema_version": 1, "answer": "red town", "supporting_facts": [["Authored Page", 0]], "evidence": [["S", "born in", "O"]]}),
         json.dumps({"schema_version": 1, "answer": "red town", "supporting_facts": [["Authored Page", 0]], "evidence": []}), None),
    ]
    result = []
    for dataset, gold, good, bad, structured in cases:
        for variant in ("positive", "negative"):
            case = {"id": dataset + "-" + variant, "dataset": dataset, "kind": "qa",
                    "task_id": "w-e5-" + dataset, "gold": gold,
                    "files": {"answer.txt": good if variant == "positive" else bad}}
            if structured:
                prediction = copy.deepcopy(structured)
                if variant == "negative":
                    prediction["predicted_evidence"] = []
                case["files"]["prediction.json"] = json.dumps(prediction)
            result.append(case)
    return result


def prepare(case, state, private):
    state.mkdir()
    private.mkdir()
    for name, value in case.get("files", {}).items():
        path = state / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)
    # Deliberately different modes, timestamps, path and inodes survive only as observations.
    (state / "unselected.txt").write_text("Unselected authored decoy, not a scorer input.\n")
    if case["kind"] == "qa":
        from data.scaffolds.qa import base
        with patch.object(base.QASpec, "records", return_value=[]):
            adapter = importlib.import_module("data.datasets." + case["dataset"])
        spec = adapter._SPEC.verifier({"task_id": case["task_id"], "gold": case["gold"]})
        staged = next(item for item in spec["inputs"] if item["path"] == "gold.json")
        (private / "gold.json").write_text(staged["content"], encoding="utf-8")
        write_json(private / "authored-verifier.json", spec)
    elif case["kind"] == "sql":
        db = sqlite3.connect(private / "db.sqlite")
        db.execute("create table t(value text)")
        db.executemany("insert into t values (?)", [("red",), ("blue",), ("blue",)])
        db.commit()
        db.close()
        (private / "gold.sql").write_text("select value from t\n")
    else:
        from openpyxl import Workbook
        for root, name, a1, a2 in ((state, "nested/result.xlsx", 3.141 if case["variant"] == "positive" else 9, "unchanged"),
                                    (private, "golden.xlsx", 3.14, "unchanged")):
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            wb = Workbook()
            wb.active.title = "Sheet1"
            wb.active["A1"], wb.active["A2"] = a1, a2
            wb.save(path)
            wb.close()
        write_json(private / "task.json", {"task_id": case["task_id"], "answer_position": "Sheet1!A1:A2", "instruction_type": "synthetic"})
    for path in state.rglob("*"):
        if path.is_file():
            path.chmod(0o600)
            os.utime(path, ns=(1_000_000_000, 1_000_000_000))


def wal_counterexample(scratch, packet, outer):
    """A genuine committed SQLite sidecar dependency, using actual BIRD EX."""
    root = scratch / "wal"
    root.mkdir()
    private, state = root / "live-private", root / "state"
    private.mkdir()
    state.mkdir()
    db = sqlite3.connect(private / "db.sqlite")
    journal_mode = db.execute("pragma journal_mode=WAL").fetchone()
    db.execute("pragma wal_autocheckpoint=0")
    db.execute("create table t(value text)")
    db.execute("insert into t values ('base')")
    db.commit()
    checkpoint = db.execute("pragma wal_checkpoint(TRUNCATE)").fetchall()
    db.execute("insert into t values ('wal-only')")
    db.commit()
    (private / "gold.sql").write_text("select value from t")
    (state / "answer.sql").write_text("select value from t where value='base'")
    case = {"id": "sqlite-wal-dependency", "dataset": "bird_minidev", "kind": "sql", "task_id": "w-e5-wal"}
    out = packet / case["id"]
    out.mkdir()
    try:
        live = invoke(state, private, case, out / "pre", packet)
        before = state_view(private)
        # Preserve actual live sidecar bytes before closing/checkpointing the writer.
        shutil.copytree(private, out / "live-private-before-close")
        raw, pin, receipt, binding = project(private, root / "main-only", case, ["db.sqlite", "gold.sql"], outer)
        post = invoke(state, root / "main-only", case, out / "post-main-only", packet)
        # A stopped writer and an actual checkpoint define a different, explicitly
        # bounded input transformation. No live DB snapshot consistency is inferred.
        rows_live = db.execute("select value from t").fetchall()
        db.close()
        closed = state_view(private)
        raw2, pin2, receipt2, binding2 = project(private, root / "checkpointed", case, ["db.sqlite", "gold.sql"], outer)
        good = invoke(state, root / "checkpointed", case, out / "post-checkpointed", packet)
        with sqlite3.connect(root / "main-only/db.sqlite") as lost:
            rows_main = lost.execute("select value from t").fetchall()
        write_json(out / "observations.json", {"journal_mode": journal_mode, "checkpoint_before_insert": checkpoint,
                   "live_private_before_copy": before, "closed_private": closed, "live_rows": rows_live,
                   "main_only_rows": rows_main, "main_only_receipt": receipt,
                   "checkpointed_receipt": receipt2, "contract": json.loads(raw), "checkpointed_contract": json.loads(raw2),
                   "pre": semantic(live), "main_only": semantic(post), "checkpointed": semantic(good)})
        for name, source in (("live-private-after-close", private), ("main-only", root / "main-only"), ("checkpointed", root / "checkpointed")):
            shutil.copytree(source, out / name)
        assert semantic(live)["reward"] == 0.0 and semantic(post)["reward"] == 1.0
        assert semantic(live) == semantic(good)
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    packet = args.output.resolve()
    packet.mkdir()  # Exclusive: preserve every earlier successful/incomplete packet.
    outer = "w-e5-" + uuid.uuid4().hex
    cases = qa_cases()
    for kind, dataset, files in (("sql", "bird_minidev", {"answer.sql": "select value from t order by value desc"}),
                                 ("workbook", "spreadsheetbench", {"answer.txt": "nested/result.xlsx\n"})):
        for variant in ("positive", "negative"):
            f = dict(files)
            if kind == "sql" and variant == "negative":
                f["answer.sql"] = "select value from t where value='red'"
            cases.append({"id": dataset + "-" + variant, "task_id": "w-e5-" + dataset,
                          "dataset": dataset, "kind": kind, "variant": variant, "files": f})
    write_json(packet / "cases.json", cases)
    template = ROOT / "tests/fixtures/hg_wpristine/task-contract.json"
    pins = {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in [
        ROOT / "eval/admission/artifact_admission.py", ROOT / "eval/verification/pristine.py",
        ROOT / "data/scaffolds/qa/base.py", ROOT / "data/scaffolds/qa/prediction.py",
        ROOT / "data/scaffolds/qa/evidence_scorers.py", ROOT / "data/scaffolds/qa/verify/check.py", template,
        *[ROOT / "data/datasets" / (name + ".py") for name in sorted({c["dataset"] for c in cases})],
        ROOT / "data/datasets/bird_minidev/verify/check.py", ROOT / "data/datasets/spreadsheetbench/verify/check.py",
        *sorted((ROOT / "tests/fixtures/hg_wpristine/closure").iterdir())]}
    write_json(packet / "source-pins.json", pins)
    artifacts.verify_scorer_closure(ROOT / "tests/fixtures/hg_wpristine/closure", template.read_bytes(), digest(template.read_bytes()))
    results = []
    with tempfile.TemporaryDirectory(prefix="hg-we5-") as temp:
        scratch = Path(temp)
        for case in cases:
            root = scratch / case["id"]
            root.mkdir()
            state, private, exported = root / "state", root / "private", root / "exported"
            prepare(case, state, private)
            out = packet / case["id"]
            out.mkdir()
            pre_inventory = state_view(state)
            pre = invoke(state, private, case, out / "pre", packet)
            names = sorted(case["files"])
            if case["kind"] == "workbook":
                names.append("nested/result.xlsx")
            raw, pin, receipt, binding = project(state, exported, case, names, outer)
            post = invoke(exported, private, case, out / "post", packet)
            write_json(out / "contract.json", json.loads(raw))
            write_json(out / "export-receipt.json", receipt)
            write_json(out / "inventories.json", {"pre": pre_inventory, "source_after_scoring": state_view(state),
                       "exported_after_scoring": state_view(exported), "private": state_view(private)})
            # Recheck after scoring; our covered scorers do not mutate selected bytes.
            artifacts.verify_state_export(exported, receipt, raw, pin, run_id=receipt["run_id"], execution_binding=binding)
            for name, source in (("source", state), ("exported", exported), ("private", private)):
                shutil.copytree(source, out / name)
            pair = {"id": case["id"], "dataset": case["dataset"], "kind": case["kind"],
                    "pre": semantic(pre), "post": semantic(post), "equivalent": semantic(pre) == semantic(post)}
            write_json(out / "comparison.json", pair)
            results.append(pair)
            assert pair["equivalent"] and pre["evidence"]["measured"] is True
            # Same-length selected-content mutation: production integrity check must
            # refuse BEFORE scoring. Never pass a refused projection to a scorer.
            selected = exported / names[0]
            original = selected.read_bytes()
            selected.write_bytes(bytes([original[0] ^ 1]) + original[1:])
            try:
                artifacts.verify_state_export(exported, receipt, raw, pin, run_id=receipt["run_id"], execution_binding=binding)
            except AdmissionError as exc:
                write_json(out / "tamper-refusal.json", {"error": str(exc), "scorer_called": False,
                           "original_sha256": digest(original), "mutated_sha256": digest(selected.read_bytes())})
            else:
                raise AssertionError("content mutation accepted")
            # Fresh incomplete contract, not bypassed integrity: demonstrates why an
            # authoritative scorer dependency declaration is necessary.
            if "prediction.json" in names or case["kind"] == "workbook":
                omitted = "prediction.json" if "prediction.json" in names else "nested/result.xlsx"
                small = [n for n in names if n != omitted]
                _, _, omitted_receipt, _ = project(state, root / "incomplete", case, small, outer)
                incomplete = invoke(root / "incomplete", private, case, out / "incomplete", packet)
                write_json(out / "incomplete-comparison.json", {"omitted": omitted, "receipt": omitted_receipt,
                           "full": semantic(pre), "incomplete": semantic(incomplete)})
            if case["id"] == "gsm8k-positive":
                old_gold = digest((private / "gold.json").read_bytes())
                (private / "gold.json").write_text('{"answer":"17"}\n')
                bad_private = invoke(state, private, dict(case, expected_gold_sha256=old_gold), out / "foreign-private", packet)
                assert bad_private["reward_text"] is None and bad_private["evidence"]["measured"] is False
            if case["id"] == "spreadsheetbench-positive":
                (state / "answer.txt").write_text("../outside.xlsx\n")
                bad_pointer = invoke(state, private, case, out / "outside-pointer", packet)
                assert bad_pointer["reward_text"] is None and bad_pointer["evidence"]["measured"] is False
        wal_counterexample(scratch, packet, outer)
    write_json(packet / "summary.json", {"outer_id": outer, "paired_cases": len(results),
               "equivalent_pairs": sum(p["equivalent"] for p in results), "datasets": sorted({p["dataset"] for p in results}),
               "positive_pairs": sum(p["pre"]["reward"] == 1.0 for p in results),
               "negative_pairs": sum(p["pre"]["reward"] == 0.0 for p in results),
               "scratch": str(scratch), "scratch_removed": not scratch.exists(), "pairs": results,
               "production_pristine_dataset_equivalence_established": False,
               "general_equivalence_established": False, "production_authorized": False})
    print((packet / "summary.json").read_text())


if __name__ == "__main__":
    main()
