"""AppWorld: the refusal, re-derived from the pinned bundle instead of asserted.

The first version of this file ended with `assert 732 == 732` -- a tautology, and the only
thing on disk that mentioned the number. This file replaces it with the measurement the
refusal is actually about: decrypt the pinned bundle (the password and salt are upstream's
public constants, transcribed in the adapter) and count the tasks, then read one task
directory to show what *is* shipped (the state test, the initial world, the instruction) and
what is not (a solution program).

It also deliberately does **not** keep the old file's transcription of the task/scenario
percentage average. That would be a transcription with no pinned source to compare against,
which is a self-test wearing a citation -- and unlike `data/qa/evidence_scorers.py`, whose
transcriptions prove that a metric *cannot* be computed, AppWorld's metric is present and
runnable in the release. What is missing is the oracle, and the decryption test is the
evidence for that claim.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import data.appworld as dataset  # noqa: E402

BUNDLE = dataset.DATASET_ROOT / "_src" / "data-0.1.0.bundle"


@pytest.fixture(scope="module")
def archive():
    if not BUNDLE.is_file():
        pytest.skip("appworld: fetch the declared official bundle")
    pytest.importorskip("cryptography", reason="the bundle is AES-encrypted")
    return dataset.bundle_zip()


def test_the_bundle_is_the_declared_one():
    declared = dataset.downloads()[0]["sha256"]
    assert hashlib.sha256(BUNDLE.read_bytes()).hexdigest() == declared


def test_the_release_contains_732_tasks(archive):
    """The number the refusal rests on, re-derived: one `ground_truth/evaluation.py` per task."""
    ids = dataset.task_ids()
    assert len(ids) == dataset.TASKS_IN_RELEASE == 732
    assert len(set(ids)) == len(ids)
    assert all(len(task_id.split("_")) == 2 for task_id in ids), ids[:3]
    assert len(archive.namelist()) == 14696


def test_a_task_ships_its_state_test_and_no_solution(archive):
    """`ground_truth/evaluation.py` is the metric; the solution is only a line count."""
    task = dataset.task_ids()[0]
    prefix = f"data/tasks/{task}/"
    members = [name[len(prefix):] for name in archive.namelist() if name.startswith(prefix)]
    assert "specs.json" in members
    assert "ground_truth/evaluation.py" in members
    assert any(name.startswith("dbs/") and name.endswith(".jsonl") for name in members)
    # No program anywhere in the task: the only .py is the state test itself.
    programs = [name for name in members if name.endswith(".py")]
    assert programs == ["ground_truth/evaluation.py"], programs

    meta = json.loads(archive.read(prefix + "ground_truth/metadata.json"))
    assert meta["num_solution_code_lines"] > 0, "a solution was generated and is not released"
    spec = json.loads(archive.read(prefix + "specs.json"))
    assert spec["instruction"].strip()

    # And the state test is not self-contained: it needs the pinned package installed.
    evaluation = archive.read(prefix + "ground_truth/evaluation.py").decode()
    assert "from appworld.evaluator import TestTracker" in evaluation
    assert "from appworld.apps" in evaluation


def test_the_refusal_names_the_oracle_and_the_pool():
    """Both measurements are quoted in the reason, and the 750 comes with its source.

    A refusal has to say what is missing (the oracle) *and* why a nearby number is not the
    benchmark's (the pool is 732 of 750). The paper's claim is cited in the module docstring
    rather than trusted, because the first version of this refusal quoted a task count from
    documentation that nothing on disk could confirm.
    """
    reason = dataset.REFUSED
    assert "no reference solution" in reason and "authored" in reason
    assert str(dataset.TASKS_IN_RELEASE) in reason and str(dataset.PUBLISHED_SUITE) in reason
    module_doc = (ROOT / "data" / "appworld.py").read_text()
    assert "2407.18901" in module_doc, "the 750 needs its citation, not a recollection"
    assert dataset.PUBLISHED_SUITE - dataset.TASKS_IN_RELEASE == 18
