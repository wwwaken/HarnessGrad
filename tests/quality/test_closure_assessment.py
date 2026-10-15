"""The closure assessment must not drift away from the registry it describes.

`registry/blocker-closure-assessment.md` is a decision document: it enumerates every open blocker,
classifies each obligation, and states which blockers are closure candidates. A document like that goes
stale silently, so these tests pin the correspondence between it and `registry/dataset-blockers.json`
without asserting anything about the *judgements* it makes.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "registry" / "dataset-blockers.json"
ASSESSMENT = ROOT / "registry" / "blocker-closure-assessment.md"

# A summary-table row looks like: | `dataset / blocker-id` | status | disposition | classes |
ROW = re.compile(r"^\|\s*`([a-z0-9_]+) / ([a-z0-9-]+)`\s*\|", re.MULTILINE)


def _registry_blockers():
    document = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return {(row["dataset"], blocker["id"])
            for row in document["datasets"] for blocker in row["blockers"]}


def test_assessment_describes_exactly_the_open_blockers():
    described = set(ROW.findall(ASSESSMENT.read_text(encoding="utf-8")))
    assert described, "no summary rows parsed: the assessment table format changed"
    assert described == _registry_blockers(), (
        "the closure assessment and the registry disagree about which blockers are open")


def test_assessment_marks_the_four_permanent_refusals_as_refused():
    text = ASSESSMENT.read_text(encoding="utf-8")
    refusals = {pair for pair in _registry_blockers() if pair[1] == "retain-contract-refusal"}
    assert len(refusals) == 4, refusals
    for dataset, blocker in refusals:
        row = re.search(rf"^\|\s*`{dataset} / {blocker}`.*$", text, re.MULTILINE)
        assert row and "REFUSED" in row.group(0), dataset


def test_assessment_states_that_nothing_was_closed_by_a_source_only_review():
    text = ASSESSMENT.read_text(encoding="utf-8")
    assert "that closure waived no verification step" in text
    assert "no measured score is asserted anywhere" in text
