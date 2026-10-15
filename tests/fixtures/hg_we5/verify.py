#!/usr/bin/env python3
"""Reconcile saved raw scorer returns, actual projected bytes and source pins."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from eval.admission import artifact_admission as artifacts


def load(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fields(result):
    e = result["evidence"]
    return {"measured": e.get("measured"), "reward_text": result["reward_text"],
            "reward": e.get("reward"), "correct": e.get("correct"), "official": e.get("official"),
            "returncode": result["returncode"]}


def raw_result(path):
    result = load(path / "result.json")
    assert load(path / "process.json")["returncode"] == 0
    assert result == json.loads((path / "stdout.txt").read_text())
    assert result["evidence"] == load(path / "scorer-output/evidence.json")
    reward = path / "scorer-output/reward.txt"
    assert result["reward_text"] == (reward.read_text() if reward.exists() else None)
    if result["evidence"]["measured"]:
        assert float(result["reward_text"]) == result["evidence"]["reward"]
    else:
        assert result["reward_text"] is None
    return result


def check_pair(packet, case):
    out = packet / case["id"]
    contract = load(out / "contract.json")
    raw = json.dumps(contract, sort_keys=True).encode()
    pin = hashlib.sha256(raw).hexdigest()
    receipt = load(out / "export-receipt.json")
    assert receipt["task_id"] == case["task_id"]
    assert receipt["source_sha256"] == hashlib.sha256(json.dumps(case, sort_keys=True).encode()).hexdigest()
    artifacts.verify_state_export(out / "exported", receipt, raw, pin, run_id=receipt["run_id"],
                                execution_binding=receipt["execution_binding"])
    names = [r["path"] for r in receipt["files"]]
    for row in receipt["files"]:
        assert sha(out / "source" / row["path"]) == row["sha256"]
        assert (out / "source" / row["path"]).read_bytes() == (out / "exported" / row["path"]).read_bytes()
    assert (out / "source/unselected.txt").is_file() and not (out / "exported/unselected.txt").exists()
    inventories = load(out / "inventories.json")
    before = {r["path"]: r for r in inventories["pre"]}
    after = {r["path"]: r for r in inventories["exported_after_scoring"]}
    assert inventories["pre"] == inventories["source_after_scoring"]
    for name in names:
        assert before[name]["sha256"] == after[name]["sha256"]
        assert before[name]["inode"] != after[name]["inode"]
        assert before[name]["mode"] == "0o600" and after[name]["mode"] == "0o640"
        assert before[name]["mtime_ns"] != after[name]["mtime_ns"]
    for stage in ("pre", "post"):
        result = raw_result(out / stage)
        request = load(out / stage / "request.json")
        reads = {r["path"] for r in result["state_reads"]}
        assert all(str(Path(request["state"]) / n) in reads for n in names)
        assert str(Path(request["state"]) / "unselected.txt") not in reads
        if case["kind"] == "qa":
            native = load(out / "private/authored-verifier.json")
            assert native["scorer_input"]["sha256"] == sha(out / "private/gold.json")
            assert native["scorer_input"]["task_id"] == case["task_id"]
            assert native["scorer_input"]["sha256"] == request["gold_sha256"]
            assert result["evidence"]["scorer_input"]["verified"] is True
            assert result["evidence"]["scorer_input"]["sha256"] == request["gold_sha256"]
        comp = load(out / "comparison.json")
        assert fields(result) == comp[stage]
    assert comp["pre"] == comp["post"] and comp["equivalent"] is True
    refusal = load(out / "tamper-refusal.json")
    assert refusal["scorer_called"] is False and refusal["error"] == "state projection seal mismatch"
    assert refusal["original_sha256"] != refusal["mutated_sha256"]
    return comp


def validate(packet=HERE / "evidence", *, seals=True):
    if seals:
        entries = (HERE / "SHA256SUMS").read_text().splitlines()
        for entry in entries:
            pin, rel = entry.split("  ", 1)
            assert sha(HERE / rel) == pin, rel
    for rel, pin in load(packet / "source-pins.json").items():
        assert sha(ROOT / rel) == pin, rel
    for rel, pin in load(HERE / "execution-source-pins.json").items():
        assert sha(ROOT / rel) == pin, rel
    cases = load(packet / "cases.json")
    pairs = [check_pair(packet, c) for c in cases]
    summary = load(packet / "summary.json")
    assert summary["pairs"] == pairs
    assert summary["paired_cases"] == len(cases)
    assert summary["equivalent_pairs"] == len(pairs)
    datasets = sorted({c["dataset"] for c in cases})
    assert summary["datasets"] == datasets
    for dataset in datasets:
        assert {p["pre"]["reward"] for p in pairs if p["dataset"] == dataset} == {0.0, 1.0}
    assert summary["positive_pairs"] == sum(p["pre"]["reward"] == 1.0 for p in pairs)
    assert summary["negative_pairs"] == sum(p["pre"]["reward"] == 0.0 for p in pairs)
    assert summary["scratch_removed"] and not Path(summary["scratch"]).exists()
    assert not summary["production_authorized"] and not summary["general_equivalence_established"]
    assert not summary["production_pristine_dataset_equivalence_established"]
    incomplete = []
    for path in sorted(packet.glob("*/incomplete-comparison.json")):
        result = load(path)
        assert fields(raw_result(path.parent / "incomplete")) == result["incomplete"]
        incomplete.append(result)
    for folder in (packet / "gsm8k-positive/foreign-private", packet / "spreadsheetbench-positive/outside-pointer"):
        result = raw_result(folder)
        assert result["returncode"] == 3 and not result["evidence"]["measured"]
    wal = load(packet / "sqlite-wal-dependency/observations.json")
    assert wal["pre"]["reward"] == wal["checkpointed"]["reward"] == 0.0
    assert wal["main_only"]["reward"] == 1.0
    assert wal["pre"] == fields(raw_result(packet / "sqlite-wal-dependency/pre"))
    assert wal["main_only"] == fields(raw_result(packet / "sqlite-wal-dependency/post-main-only"))
    assert wal["checkpointed"] == fields(raw_result(packet / "sqlite-wal-dependency/post-checkpointed"))
    for r in wal["live_private_before_copy"]:
        assert sha(packet / "sqlite-wal-dependency/live-private-before-close" / r["path"]) == r["sha256"]
    for r in wal["main_only_receipt"]["files"]:
        assert sha(packet / "sqlite-wal-dependency/main-only" / r["path"]) == r["sha256"]
    for r in wal["closed_private"]:
        assert sha(packet / "sqlite-wal-dependency/live-private-after-close" / r["path"]) == r["sha256"]
    for label, rootname in (("contract", "main-only"), ("checkpointed_contract", "checkpointed")):
        raw = json.dumps(wal[label], sort_keys=True).encode()
        receipt = wal["main_only_receipt" if rootname == "main-only" else "checkpointed_receipt"]
        pin = hashlib.sha256(raw).hexdigest()
        assert receipt["contract_sha256"] == pin
        assert receipt["task_id"] == wal[label]["task_id"]
        assert receipt["execution_binding"]["task_id"] == receipt["task_id"]
        assert receipt["execution_binding"]["outer_run_id"] == summary["outer_id"]
        assert receipt["bytes"] == sum(r["bytes"] for r in receipt["files"])
        for r in receipt["files"]:
            path = packet / "sqlite-wal-dependency" / rootname / r["path"]
            assert path.stat().st_size == r["bytes"] and sha(path) == r["sha256"]
        if rootname == "checkpointed":
            artifacts.verify_state_export(packet / "sqlite-wal-dependency" / rootname, receipt,
                raw, pin, run_id=receipt["run_id"], execution_binding=receipt["execution_binding"])
        else:
            # The final parent row probe opens this WAL-mode database and creates
            # new SHM/empty-WAL files after the real scorer/export check. Preserve
            # and identify them, rather than mislabel this archived post-probe tree
            # as an untouched exact-allowlist runtime projection.
            assert (packet / "sqlite-wal-dependency/main-only/db.sqlite-wal").stat().st_size == 0
            assert (packet / "sqlite-wal-dependency/main-only/db.sqlite-shm").is_file()
    assert wal["checkpointed"] == wal["pre"]
    assert wal["live_rows"] != wal["main_only_rows"]
    preservation = load(HERE / "preservation.json")
    assert sha(HERE / preservation["archive"]) == preservation["sha256"]
    with zipfile.ZipFile(HERE / preservation["archive"]) as archive:
        assert len(archive.namelist()) == preservation["members"]
        for name, pin in preservation["verified_member_sha256"].items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == pin
    guard = next(json.loads(line) for line in (HERE / "commands.stderr.txt").read_text().splitlines()
                 if line.startswith('{"cpu_limit_seconds"'))
    assert all(p["result"] == "denied" for p in guard["socket_probes"].values())
    assert '{"blocked_external_dataset_reads": []}' in (HERE / "commands.stderr.txt").read_text()
    return {"valid": True, "paired_cases": len(pairs), "datasets": datasets,
            "selected_tamper_refusals": len(pairs), "incomplete_projection_controls": len(incomplete),
            "incomplete_projection_score_changes": sum(r["full"]["reward"] != r["incomplete"]["reward"] for r in incomplete),
            "wal_main_only_score_changed": True, "wal_checkpointed_score_preserved": True,
            "manifest_members": len(entries) if seals else None, "production_authorized": False}


if __name__ == "__main__":
    print(json.dumps(validate(seals="--no-seals" not in sys.argv), indent=2, sort_keys=True))
