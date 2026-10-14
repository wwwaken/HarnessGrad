#!/usr/bin/env python3
"""Verify evidence bytes and allowed source/registry scope, without scoring tasks."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BASE = "fdfdbce"


def load(path):
    return json.loads(path.read_text())


def original(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=REPO)


def main():
    paths = set()
    for line in (HERE / "SHA256SUMS").read_text().splitlines():
        expected, name = line.split("  ", 1)
        path = HERE / name
        assert path.is_file() and not path.is_symlink(), name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, name
        assert name not in paths, name
        paths.add(name)
    actual = {str(p.relative_to(HERE)) for p in HERE.rglob("*")
              if p.is_file() and "__pycache__" not in p.parts and p != HERE / "SHA256SUMS"}
    assert paths == actual, {"unlisted": sorted(actual-paths), "missing": sorted(paths-actual)}

    previous = json.loads(original("docs/dataset-blockers.json"))
    current = load(REPO / "docs/dataset-blockers.json")
    assert current["datasets"] == previous["datasets"], "dataset blockers changed"
    assert {k: v for k, v in current.items() if k != "shared_blockers"} == {
        k: v for k, v in previous.items() if k != "shared_blockers"}
    changes = []
    for before, after in zip(previous["shared_blockers"], current["shared_blockers"], strict=True):
        assert before["id"] == after["id"]
        if before != after:
            assert before["id"] == "scorer-offline-closure"
            assert {k:v for k,v in before.items() if k not in {"observed", "evidence"}} == {
                k:v for k,v in after.items() if k not in {"observed", "evidence"}}
            assert after["evidence"][:len(before["evidence"])] == before["evidence"]
            for evidence in after["evidence"]:
                if evidence["kind"] == "repository":
                    assert evidence["locator"] in (REPO / evidence["path"]).read_text(), evidence
            changes.append(after["id"])
    assert changes == ["scorer-offline-closure"], changes
    journal = (REPO / "docs/adapter-integration-journal.md").read_bytes()
    assert journal.startswith(original("docs/adapter-integration-journal.md"))
    assert journal.count(b"## Offline official scorer execution and bounded equivalence - 2026-10-15 - w-offscorer") == 1
    allowed = {"docs/dataset-blockers.json", "docs/adapter-integration-journal.md",
               "reports/w-offscorer-equivalence.md", "reports/w-offscorer-validation.txt"}
    changed = subprocess.check_output(["git", "diff", BASE, "--name-only"], cwd=REPO, text=True).splitlines()
    assert all(p in allowed or p.startswith("tests/fixtures/hg_woffscorer/") for p in changed), changed
    source_pins = load(HERE / "local-source-pins.json")
    for name, expected in source_pins["sha256"].items():
        path = REPO / name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, name
        assert path.read_bytes() == original(name), name
    fever = load(HERE / "fever/comparison.json")
    assert fever["controlled_inputs"] == len(fever["cases"])
    assert fever["agreements"] == sum(c["agreement"] is True for c in fever["cases"])
    assert fever["divergences"] == sum(c["agreement"] is False for c in fever["cases"])
    assert fever["predicate_errors"] == sum(not c["comparable_predicate"] for c in fever["cases"])
    assert fever["singleton_fever_score_errors"] == sum(bool(c["official_fever_score_error"]) for c in fever["cases"])
    for name in ("official", "local", "comparison"):
        assert load(HERE / f"fever/{name}.json")["inputs_sha256"] == hashlib.sha256((HERE / "fever/inputs.json").read_bytes()).hexdigest()
    for path in HERE.rglob("*-offline.txt"):
        receipt = json.loads(path.read_text().splitlines()[0])
        assert all(p["result"] == "denied" and p["errno"] == 1 for p in receipt["socket_probes"].values()), path
        assert receipt["production_runtime_observation"] is False, path
    print(json.dumps({"verified_fixture_files": len(paths), "local_source_pins": len(source_pins["sha256"]),
                      "registry_changes": changes, "dataset_blocker_changes": 0,
                      "production_source_changes": 0, "journal_append_only": True,
                      "benchmark_tasks_executed": 0, "production_authorized": False}, indent=2))


if __name__ == "__main__":
    main()
