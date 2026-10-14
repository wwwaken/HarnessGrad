"""Guards for dataset-scoped test selection (`tools/test_scope.py`).

The selection rule is derived from filenames, so it self-maintains for the common
case. What it cannot do by itself is notice two things that matter, and those are
what this file checks:

1. **A dataset with no dedicated test.** If `test_<name>_*.py` never appears, that
   dataset has no adapter-level coverage at all -- a real gap, not a scoping detail.
   It is reported rather than silently selecting "core only".
2. **A dataset-specific file that is not named after its dataset.** Those are the
   `EXTRA` entries, and each one is a human decision. A stale entry (file renamed or
   deleted) would silently drop coverage from a selection, so the path must exist.

The selection must also not double-count: a platform test that merely *mentions* a
dataset is core. That rule is asserted directly, because getting it wrong is how a
"run one dataset" command quietly pulls in the whole suite.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import test_scope  # noqa: E402


@pytest.fixture(scope="module")
def names():
    return test_scope.published()


@pytest.fixture(scope="module")
def mapping(names):
    return test_scope.scope_map(names)


#: Datasets with no dedicated adapter test file at all. Measured, not assumed:
#: they are reached only indirectly by the cross-dataset contract tests
#: (`test_dataset_controls.py`, `test_dataset_refusals.py`, `test_bigbench_official_scorers.py`).
#: Pinned so the gap can only shrink: a new dataset that ships without a test fails
#: here, and adding a test means deleting its name from this tuple.
#:
#: This list is the reason the scoping helper reports a gap instead of quietly
#: returning "core only" -- a selection with no adapter test looks identical to a
#: selection whose adapter tests all pass.
NO_DEDICATED_TEST = (
    "api_bank", "fever", "hotpotqa", "physicsquestions", "sotuqa",
    "sportsunderstanding", "strategyqa", "tau2_bench", "tau_bench", "terminal_bench",
)


def test_no_new_dataset_arrives_without_a_dedicated_test(names, mapping):
    without = tuple(sorted(n for n in names if not mapping[n]))
    added = sorted(set(without) - set(NO_DEDICATED_TEST))
    assert not added, (
        f"dataset(s) with no dedicated test file: {added}. Add a "
        "`test_<dataset>_*.py` (or an EXTRA entry naming the file), or add the name "
        "to NO_DEDICATED_TEST with a reason -- do not let it pass silently.")
    fixed = sorted(set(NO_DEDICATED_TEST) - set(without))
    assert not fixed, (
        f"{fixed} now has a dedicated test file; remove it from NO_DEDICATED_TEST so "
        "the recorded gap stays accurate")


def test_extra_entries_point_at_real_files():
    for fname in test_scope.EXTRA:
        assert (ROOT / "tests" / "quality" / fname).is_file(), (
            f"EXTRA names {fname}, which does not exist; a stale entry silently "
            "removes a file from every selection that should contain it")


def test_registry_wide_entries_point_at_real_files():
    for fname in test_scope.REGISTRY_WIDE:
        assert (ROOT / "tests" / "quality" / fname).is_file(), fname


def test_registry_wide_files_are_not_also_dataset_scoped(mapping):
    for fname in test_scope.REGISTRY_WIDE:
        holders = [d for d, files in mapping.items()
                   if d not in ("core", "registry") and fname in files]
        assert not holders, (
            f"{fname} checks the dataset layer across all datasets, so it must not be "
            f"selected for individual datasets; it was attributed to {holders}")


def test_a_platform_test_that_merely_mentions_a_dataset_is_core(mapping):
    # These use one dataset as a fixture while testing platform behaviour. If any of
    # them became dataset-scoped, `--dataset terminal_bench` would start running the
    # runner's own contract tests, and every other dataset would inherit them too.
    for fname in ("test_trials_and_unmeasured.py", "test_verifier.py",
                  "test_task_id_paths.py", "test_import_direction.py"):
        assert fname in mapping["core"], f"{fname} should be a core platform test"
        for d, files in mapping.items():
            if d in ("core", "registry"):
                continue
            assert fname not in files, f"{fname} must not be scoped to {d}"


def test_selection_for_one_dataset_excludes_another(names, mapping):
    chosen = set(test_scope.select(names, ["gsm8k"]))
    assert "test_gsm8k_dataset.py" in chosen
    assert "test_appworld_official_scorer.py" not in chosen, (
        "a gsm8k run must not pay for the AppWorld replay suite")
    assert not chosen & mapping["appworld"]
    assert not chosen & mapping["registry"], "registry-wide is opt-in"


def test_selection_always_contains_core(names, mapping):
    chosen = set(test_scope.select(names, ["gsm8k"]))
    assert mapping["core"] <= chosen, "a platform regression still matters"


def test_unknown_dataset_is_refused(names):
    with pytest.raises(KeyError):
        test_scope.select(names, ["not_a_dataset"])
