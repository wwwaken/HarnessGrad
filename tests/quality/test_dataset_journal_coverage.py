"""Source-only coverage guard: tracked registry entries must cite exact site reviews.

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

# Empty since 2026-10-15: the b2 three (sportsunderstanding, spreadsheetbench, strategyqa)
# now carry their own docs/dataset-reviews/<dataset>.md, extracted verbatim from the combined
# docs/dataset-source-reviews-b2.md and cited as `/site/dataset-reviews/<dataset>.md`. The
# exception set is kept so that any *new* journal-coverage dataset with no per-dataset review
# has an explicit place to be recorded rather than silently passing; never add a dataset here
# just to make an omitted review pass.
_KNOWN_JOURNAL_GAPS = frozenset()


def _journal_entries():
    registry = json.loads((ROOT / "registry/dataset-blockers.json").read_text(encoding="utf-8"))
    return [(row["dataset"], blocker)
            for row in registry["datasets"]
            for blocker in row["blockers"]
            if blocker["family"] == "journal-coverage"]


@pytest.fixture(scope="module")
def tracked_registry():
    # Git metadata only: no adapter imports, payload reads or benchmark execution.
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", "registry/dataset-blockers.json"],
        cwd=ROOT, check=True, capture_output=True)
    return set(result.stdout.decode("utf-8").split("\0"))


@pytest.mark.parametrize("dataset,blocker", [
    pytest.param(dataset, blocker, id=dataset,
                 marks=pytest.mark.xfail(
                     strict=True, reason="pre-existing out-of-scope journal review gap")
                 if dataset in _KNOWN_JOURNAL_GAPS else ())
    for dataset, blocker in _journal_entries()
])
def test_every_journal_coverage_entry_points_at_its_migrated_review(
        dataset, blocker, tracked_registry):
    titles = {"fever": "FEVER", "physicsquestions": "Physics Questions",
              "reasoning_gym": "Reasoning Gym"}
    reviews = [item for item in blocker["evidence"]
               if item == {"kind": "external-reference",
                           "path": f"/site/dataset-reviews/{dataset}.md",
                           "locator": f"# {titles.get(dataset, dataset)} source-only journal review"}]
    assert reviews, (
        f"{dataset}: journal-coverage needs its exact /site/dataset-reviews/*.md "
        "review reference; pointing at the adapter does not close journal coverage")
    assert "registry/dataset-blockers.json" in tracked_registry, (
        f"{dataset}: the migrated review citation must be tracked by Git")


@pytest.mark.parametrize("dataset,blocker", _journal_entries())
def test_archived_dataset_review_locator(dataset, blocker, site_archive):
    reference = f"/site/dataset-reviews/{dataset}.md"
    # The three b2 gaps deliberately remain strict xfails in the citation guard.
    # An optional archive does not repair an absent citation.
    path = site_archive(reference)
    relative = path.relative_to(ROOT)
    assert not relative.is_absolute() and ".." not in relative.parts, dataset
    assert path.resolve().is_relative_to(ROOT.resolve()), dataset
    assert path.is_file(), f"{dataset}: missing review {relative}"
    review = next(item for item in blocker["evidence"] if item["path"] == reference)
    assert review["locator"] and review["locator"] in path.read_text(encoding="utf-8"), (
        f"{dataset}: stale or empty review locator in {relative}")
