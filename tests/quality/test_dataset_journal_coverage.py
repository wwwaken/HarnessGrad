"""Source-only coverage guard: registry entries must point at tracked reviews.

Like test_test_lanes.py, discover entries from the hand-maintained registry and
check their evidence rather than assuming that an adapter path is a review.
No dataset module, pool, external receipt, network or runtime is consulted.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[2]

# Explicit pre-existing debt outside b1's fever/physicsquestions/reasoning_gym scope.
# Strict xfail makes a resolved gap fail until its stale exception is removed.
# Never add a new dataset here just to make an omitted review pass.
_KNOWN_JOURNAL_GAPS = frozenset({
    "sportsunderstanding", "spreadsheetbench", "strategyqa",
})


def _journal_entries():
    registry = json.loads((ROOT / "docs/dataset-blockers.json").read_text(encoding="utf-8"))
    return [(row["dataset"], blocker)
            for row in registry["datasets"]
            for blocker in row["blockers"]
            if blocker["family"] == "journal-coverage"]


@pytest.fixture(scope="module")
def tracked_reviews():
    # Git metadata only: no adapter imports, payload reads or benchmark execution.
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", "docs/dataset-reviews"],
        cwd=ROOT, check=True, capture_output=True)
    return set(result.stdout.decode("utf-8").split("\0"))


@pytest.mark.parametrize("dataset,blocker", [
    pytest.param(dataset, blocker, id=dataset,
                 marks=pytest.mark.xfail(
                     strict=True, reason="pre-existing out-of-scope journal review gap")
                 if dataset in _KNOWN_JOURNAL_GAPS else ())
    for dataset, blocker in _journal_entries()
])
def test_every_journal_coverage_entry_points_at_a_checked_in_review(
        dataset, blocker, tracked_reviews):
    reviews = [item for item in blocker["evidence"]
               if item["kind"] == "repository"
               and item["path"] == f"docs/dataset-reviews/{dataset}.md"]
    assert reviews, (
        f"{dataset}: journal-coverage needs a checked-in docs/dataset-reviews/*.md "
        "review reference; pointing at the adapter does not close journal coverage")
    for review in reviews:
        relative = Path(review["path"])
        assert not relative.is_absolute() and ".." not in relative.parts, dataset
        path = ROOT / relative
        assert path.resolve().is_relative_to(ROOT.resolve()), dataset
        assert path.is_file(), f"{dataset}: missing review {relative}"
        assert relative.as_posix() in tracked_reviews, (
            f"{dataset}: review {relative} exists locally but is not tracked by Git")
        assert review["locator"] and review["locator"] in path.read_text(encoding="utf-8"), (
            f"{dataset}: stale or empty review locator in {relative}")
