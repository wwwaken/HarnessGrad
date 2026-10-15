"""Tiny authored SQLite controls; never import adapters or released task records."""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from data.scaffolds import scorer_input
from eval.admission import artifact_admission as artifacts
from eval.observe.tracing import _materialize


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


@contextlib.contextmanager
def live_database(root, name="database.sqlite"):
    root.mkdir()
    database = root / name
    db = sqlite3.connect(database)
    try:
        assert db.execute("pragma journal_mode=WAL").fetchone() == ("wal",)
        db.execute("pragma wal_autocheckpoint=0")
        db.execute("create table t(value text)")
        db.execute("insert into t values ('base')")
        db.commit()
        assert db.execute("pragma wal_checkpoint(TRUNCATE)").fetchone() == (0, 0, 0)
        db.execute("insert into t values ('wal-only')")
        db.commit()
        (root / "gold.sql").write_text("select value from t")
        yield database, db
    finally:
        db.close()


def inventory(root):
    return {p.name: {"bytes": p.stat().st_size, "sha256": sha(p)}
            for p in sorted(root.iterdir()) if p.is_file()}


def rows(database):
    # Not immutable=1: that would deliberately ignore an existing WAL.
    db = sqlite3.connect(f"{database.as_uri()}?mode=ro", uri=True)
    try:
        return db.execute("select value from t order by value").fetchall()
    finally:
        db.close()


def bound_spec(root, name="database.sqlite"):
    return scorer_input.bind({"inputs": [
        {"path": name, "from": str(root / name)},
        {"path": "gold.sql", "from": str(root / "gold.sql")}], "argv": []},
        "w-wal-authored", [name, "gold.sql"])


def score(root, out, *, bound=False):
    out.mkdir()
    pred = out / "answer.sql"
    pred.write_text("select value from t where value='base'")
    path = ROOT / "data/datasets/bird_minidev/verify/check.py"
    spec = importlib.util.spec_from_file_location("wwal_bird_check", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    argv = [str(path), "--db", "database.sqlite" if bound else str(root / "database.sqlite"),
            "--gold", "gold.sql" if bound else str(root / "gold.sql"), "--pred", str(pred),
            "--reward-file", str(out / "reward.txt"), "--evidence-file", str(out / "evidence.json")]
    if bound:
        argv += bound_spec(root)["argv"]
    stdout, stderr = io.StringIO(), io.StringIO()
    old_argv, old_cwd = sys.argv, Path.cwd()
    try:
        sys.argv = argv
        import os
        os.chdir(root)
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = module.main()
    finally:
        sys.argv = old_argv
        import os
        os.chdir(old_cwd)
    (out / "stdout.txt").write_text(stdout.getvalue())
    (out / "stderr.txt").write_text(stderr.getvalue())
    result = {"argv": argv, "returncode": code,
              "evidence": json.loads((out / "evidence.json").read_text()),
              "reward_text": (out / "reward.txt").read_text() if (out / "reward.txt").exists() else None}
    dump(out / "result.json", result)
    return result


def project(source, destination, names):
    contract = json.loads((ROOT / "tests/fixtures/hg_wpristine/task-contract.json").read_text())
    contract["task_id"] = "w-wal-authored"
    contract["source_sha256"] = hashlib.sha256(b"authored two-row WAL counterexample").hexdigest()
    contract["export"] = {"files": [{"path": n, "max_bytes": 1048576} for n in names],
                          "max_bytes": 4194304, "max_inodes": 32}
    raw = json.dumps(contract, sort_keys=True).encode()
    pin = hashlib.sha256(raw).hexdigest()
    binding = artifacts.execution_identity(contract["task_id"], "w-wal-" + uuid.uuid4().hex, "1")
    run_id = "w-wal-export-" + uuid.uuid4().hex
    receipt = artifacts.export_state(source, destination, raw, pin, run_id=run_id, execution_binding=binding)
    artifacts.verify_state_export(destination, receipt, raw, pin, run_id=run_id, execution_binding=binding)
    return {"contract": contract, "receipt": receipt, "verified_before_any_sqlite_probe": True}


def collect(output):
    output.mkdir()  # Never overwrite an earlier attempt.
    with tempfile.TemporaryDirectory(prefix="hg-w-wal-") as tmp:
        scratch = Path(tmp)
        with live_database(scratch / "live") as (database, db):
            live = database.parent
            before = inventory(live)
            shutil.copytree(live, output / "full-raw-before-close")
            pre = score(live, output / "unbound-live")
            native = score(live, output / "bound-live", bound=True)
            main = scratch / "main-only"
            projection = project(live, main, ["database.sqlite", "gold.sql"])
            # Preserve pristine selected bytes before a SQLite open creates sidecars.
            shutil.copytree(main, output / "main-only-before-probe")
            exported = score(main, output / "unbound-main-only")
            _materialize(scratch / "materialized", [
                {"path": "database.sqlite", "from": str(database)},
                {"path": "gold.sql", "from": str(live / "gold.sql")}], ROOT)
            materialized = score(scratch / "materialized", output / "bound-materialized", bound=True)
            full = scratch / "full-export"
            full_projection = project(live, full, ["database.sqlite", "database.sqlite-wal",
                                                   "database.sqlite-shm", "gold.sql"])
            full_score = score(full, output / "unbound-full-export")
            result = {"sqlite_runtime": sqlite3.sqlite_version, "python": sys.version,
                      "source_before": before, "source_after": inventory(live),
                      "live_rows": rows(database), "main_only_rows": rows(main / "database.sqlite"),
                      "full_export_rows": rows(full / "database.sqlite"),
                      "main_only_projection": projection, "full_projection": full_projection,
                      "unbound_live": pre, "bound_live": native, "unbound_main_only": exported,
                      "bound_materialized": materialized, "unbound_full_export": full_score}
        result["closed_wal_header"] = list(database.read_bytes()[18:20])
        result["bound_closed_wal"] = score(live, output / "bound-closed-wal", bound=True)
        db = sqlite3.connect(database)
        result["explicit_external_preparation_mode"] = db.execute("pragma journal_mode=DELETE").fetchone()
        db.close()
        result["delete_header"] = list(database.read_bytes()[18:20])
        result["bound_delete"] = score(live, output / "bound-delete", bound=True)
        result["scratch"] = tmp
    result["scratch_removed"] = not Path(result["scratch"]).exists()
    dump(output / "observations.json", result)
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    collect(parser.parse_args().output.resolve())
