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


def test_the_release_declares_its_own_division(archive):
    """`data/datasets/*.txt` is the release's own split table -- and it says 732, not 750.

    This is what settles the count question the first version of the refusal got half wrong:
    nothing is withheld from the bundle, each of the 732 tasks appears in exactly one split,
    and the four files sum to the number of task directories.
    """
    splits = dataset.split_ids()
    assert {name: len(ids) for name, ids in splits.items()} == dataset.SPLIT_SIZES
    union = set().union(*splits.values())
    assert len(union) == sum(len(ids) for ids in splits.values()) == 732
    assert union == set(dataset.task_ids())
    for name, ids in splits.items():
        assert len(set(ids)) == len(ids), name


def test_the_paper_count_is_an_earlier_build():
    """The whole of "732 vs 750": the difference is in train and dev, and it is six scenarios.

    The paper reports 250 scenarios x 3 tasks = 750 with splits 105/60/168/417
    (arXiv 2407.18901v2). The release kept every test task and dropped 18 from train+dev --
    105 -> 90 and 60 -> 57 is 15 + 3, which is six whole scenarios at three tasks each.
    """
    paper, release = dataset.PAPER_SPLITS, dataset.SPLIT_SIZES
    assert paper["test_normal"] == release["test_normal"] == 168
    assert paper["test_challenge"] == release["test_challenge"] == 417
    assert paper["train"] - release["train"] == 15
    assert paper["dev"] - release["dev"] == 3
    assert sum(paper.values()) - sum(release.values()) == 18
    assert (paper["train"] - release["train"]) + (paper["dev"] - release["dev"]) == 18
    assert 18 % 3 == 0 and 18 // 3 == 6, "the delta is whole scenarios of three tasks"
    doc = (ROOT / "data" / "appworld.py").read_text()
    assert "2407.18901" in doc, "the paper's 750 needs its citation, not a recollection"


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


def test_the_refusal_names_the_oracle_and_settles_the_pool():
    """The reason is now about one thing: the oracle, which the platform has since decided to
    author. The pool is *not* a ground for refusing -- the release states its own 732 across
    four splits, so a run can say which one it scored -- and the reason must not say otherwise,
    because that claim was wrong for a full round."""
    reason = dataset.REFUSED
    assert "no reference solution" in reason and "authored" in reason
    assert "declares its own 732" in reason
    assert str(dataset.TASKS_IN_RELEASE) in reason
    assert "not comparable" not in reason
    doc = (ROOT / "data" / "appworld.py").read_text()
    assert "2407.18901" in doc, "the paper's 750 needs its citation, not a recollection"
