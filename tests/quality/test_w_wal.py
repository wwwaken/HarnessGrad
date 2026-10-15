"""Authored SQLite WAL dependency loss and native-input fail-closed regressions."""
import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("w_wal_control", ROOT / "tests/fixtures/hg_wwal/control.py")
control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(control)


@pytest.mark.parametrize("source_kind", ["live", "materialized", "closed"])
def test_bound_bird_refuses_wal_before_scoring(tmp_path, source_kind):
    with control.live_database(tmp_path / "live") as (database, db):
        root = database.parent
        if source_kind == "materialized":
            root = tmp_path / "main-only"
            root.mkdir()
            shutil.copy2(database, root / database.name)
            shutil.copy2(database.parent / "gold.sql", root / "gold.sql")
        elif source_kind == "closed":
            db.close()
        result = control.score(root, tmp_path / "result", bound=True)
        assert result["returncode"] == 3, result
        assert result["reward_text"] is None, result
        assert result["evidence"]["measured"] is False
        assert result["evidence"]["scorer_input"]["verified"] is False
        assert "SQLite WAL" in result["evidence"]["error"]


def test_generic_export_still_requires_explicit_sidecar_contract(tmp_path):
    # Characterised limitation, not an equivalence assertion or a platform admission.
    with control.live_database(tmp_path / "live") as (database, db):
        main = tmp_path / "main"
        projection = control.project(database.parent, main, ["database.sqlite", "gold.sql"])
        assert projection["verified_before_any_sqlite_probe"]
        assert control.sha(database) == control.sha(main / database.name)
        assert control.rows(database) == [("base",), ("wal-only",)]
        assert control.rows(main / database.name) == [("base",)]
        full = tmp_path / "full"
        control.project(database.parent, full, ["database.sqlite", "database.sqlite-wal",
                                                "database.sqlite-shm", "gold.sql"])
        assert control.rows(full / database.name) == control.rows(database)


def test_rollback_mode_database_still_measures_and_authenticates(tmp_path):
    with control.live_database(tmp_path / "live") as (database, db):
        db.close()
        connection = sqlite3.connect(database)
        assert connection.execute("pragma journal_mode=DELETE").fetchone() == ("delete",)
        connection.close()
        result = control.score(database.parent, tmp_path / "result", bound=True)
        assert result["returncode"] == 0
        assert result["reward_text"] == "0\n"
        assert result["evidence"]["measured"] is True
        assert result["evidence"]["scorer_input"]["verified"] is True


@pytest.mark.parametrize("name", ["database.sqlite", "database.db", "opaque.bin"])
def test_wal_detection_uses_consumed_bytes_and_never_calls_score(tmp_path, name):
    with control.live_database(tmp_path / "live", name) as (database, db):
        binding = control.bound_spec(database.parent, name)["scorer_input"]
        args = SimpleNamespace(task_id=binding["task_id"], scorer_input_sha256=binding["sha256"],
                               scorer_input_files=json.dumps(binding["files"]),
                               evidence_file=str(tmp_path / "evidence.json"))
        calls = []
        code = control.scorer_input.run_bound(
            args, {name: database, "gold.sql": database.parent / "gold.sql"},
            lambda *a: calls.append(a))
        assert code == 3
        assert calls == []
        assert "SQLite WAL" in json.loads(Path(args.evidence_file).read_text())["error"]


def test_non_sqlite_native_input_keeps_exact_bytes_and_cleans_private_copy(tmp_path):
    source = tmp_path / "payload.json"
    source.write_text('{"example":"authored"}\n')
    spec = control.scorer_input.bind({"inputs": [{"path": source.name, "from": str(source)}], "argv": []},
                                    "w-wal-authored", [source.name])
    binding = spec["scorer_input"]
    args = SimpleNamespace(task_id=binding["task_id"], scorer_input_sha256=binding["sha256"],
                           scorer_input_files=json.dumps(binding["files"]),
                           evidence_file=str(tmp_path / "evidence.json"))
    copies = []
    def consume(paths, receipt):
        assert receipt["verified"] is True
        copies.append(paths[source.name])
        assert paths[source.name].read_bytes() == source.read_bytes()
        return 7
    assert control.scorer_input.run_bound(args, {source.name: source}, consume) == 7
    assert not copies[0].exists()
