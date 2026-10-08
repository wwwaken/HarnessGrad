"""AppWorld release, released oracle, log replay, and control arms."""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import data.appworld as dataset  # noqa: E402

BUNDLE = dataset.DATASET_ROOT / "_src" / "data-0.1.0.bundle"
CONTROL_TASK = "e85d92a_1"


def test_bundle_digest_and_release_count():
    assert hashlib.sha256(BUNDLE.read_bytes()).hexdigest() == dataset.downloads()[0]["sha256"]
    assert len(dataset.task_ids()) == dataset.TASKS_IN_RELEASE == 732


def test_declared_split_files_cover_every_task():
    splits = dataset.split_ids()
    assert {key: len(value) for key, value in splits.items()} == dataset.SPLIT_SIZES
    union = set().union(*splits.values())
    assert len(union) == 732 == len(dataset.task_ids())
    assert union == set(dataset.task_ids())
    assert set(dataset.SPLIT["train"]) == set(splits["train"] + splits["dev"])
    assert set(dataset.SPLIT["eval"]) == set(splits["test_normal"] + splits["test_challenge"])


def test_pool_contains_compact_metadata_and_db_digests():
    rows = dataset._pool()
    assert len(rows) == 732
    assert all({"task_id", "split", "difficulty", "num_api_calls", "num_apps", "instruction", "dbs"} <= set(row) for row in rows)
    assert len({row["dbs"] for row in rows}) > 1


def test_released_reference_coverage_is_computed():
    assert dataset.ORACLE_SOURCE == "released"
    assert "TestTracker" in dataset.ORACLE_VALIDATED_BY
    assert dataset.ORACLE_COVERAGE.startswith("147 of 732")
    assert "requester" in dataset.oracle_files({"task_id": CONTROL_TASK})["reference.py"]
    with pytest.raises(ValueError, match="no released reference"):
        dataset.oracle_files({"task_id": "92fe421_3"})


def test_check_separates_measured_zero_from_unmeasured(tmp_path):
    check = ROOT / "data/appworld/verify/check.py"
    missing = tmp_path / "missing.jsonl"
    reward = tmp_path / "reward"
    evidence = tmp_path / "evidence"
    proc = subprocess.run([sys.executable, str(check), "--task-id", CONTROL_TASK, "--log", str(missing), "--reward-file", str(reward), "--evidence-file", str(evidence)], cwd=tmp_path)
    assert proc.returncode == 3 and not reward.exists()
    assert json.loads(evidence.read_text())["measured"] is False

    empty = tmp_path / "empty.jsonl"
    empty.write_text("")
    appworld_env = dict(__import__("os").environ, APPWORLD_ROOT=str(dataset.UNPACKED))
    proc = subprocess.run(["/mnt/20t/xubuqiang/venvs/appworld/bin/python", str(check), "--task-id", CONTROL_TASK, "--log", str(empty), "--reward-file", str(reward), "--evidence-file", str(evidence)], cwd=tmp_path, env=appworld_env)
    assert proc.returncode == 0
    assert reward.read_text().strip() == "0.0"
    assert json.loads(evidence.read_text())["measured"] is True


@pytest.mark.parametrize("arm,expected", [("--oracle", "1.0"), ("--noop", "0.0")])
def test_by_hand_control_arms(arm, expected):
    proc = subprocess.run([sys.executable, "data/appworld/control.py", arm, "--task-id", CONTROL_TASK], cwd=ROOT, capture_output=True, text=True, timeout=300)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert f"reward  {expected}" in proc.stdout


@pytest.mark.parametrize("arm,expected", [("--oracle", "1.0"), ("--noop", "0.0")])
def test_platform_control_arms(arm, expected):
    proc = subprocess.run([sys.executable, "data/appworld/control.py", arm, "--task-id", CONTROL_TASK, "--platform", "--no-sandbox"], cwd=ROOT, capture_output=True, text=True, timeout=900)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert f"score    {expected}" in proc.stdout
