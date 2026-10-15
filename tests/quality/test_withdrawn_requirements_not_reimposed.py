"""No active blocker may re-impose a requirement the operator withdrew.

The failure this pins is specific and happened repeatedly in this phase. When the operator withdrew
`scorer-offline-closure`, `artifact-only-state-export`, `pristine-verifier` and `runtime-observations`,
the dataset blockers' `observed` fields recorded the change but their `next_action` fields kept
conditioning closure and admission on those gates, so the active requirements contradicted the record.
Worker proposals then kept reintroducing the same phrasing. A blocker may *mention* a withdrawn
requirement only to say it is withdrawn and does not condition closure - never as work to do.

`registry/withdrawn-requirements.md` is the authority for what is withdrawn; this test reads it rather
than hardcoding the list, so a new withdrawal is covered automatically.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "registry" / "dataset-blockers.json"
WITHDRAWALS = ROOT / "registry" / "withdrawn-requirements.md"

# "## Shared requirement withdrawn: `scorer-offline-closure`" and "### `livecodebench / row-attestation`"
WITHDRAWN_SHARED = re.compile(r"^## Shared requirement withdrawn: `([a-z0-9-]+)`", re.MULTILINE)
WITHDRAWN_DATASET = re.compile(r"^### `([a-z0-9_]+) / ([a-z0-9-]+)`", re.MULTILINE)
SENTENCE = re.compile(r"(?<=[.;])\s+")

# A sentence naming a withdrawn requirement is acceptable only if it says so. These are the markers
# the applied registry text uses; a new phrasing has to be added here deliberately.
MARKERS = ("withdrawn", "withdrawals", "do not restore", "does not condition", "do not condition",
           "absent shared", "not re-impose", "reinstat")

# Phrases that only ever meant "these shared gates are still required".
GENERIC = ("all shared gates", "both shared gates", "remaining shared evidence",
           "all shared admission", "shared admission gates", "shared admission evidence")


def _withdrawn_names():
    text = WITHDRAWALS.read_text(encoding="utf-8")
    names = set(WITHDRAWN_SHARED.findall(text))
    names.update(f"{dataset}/{blocker}" for dataset, blocker in WITHDRAWN_DATASET.findall(text))
    assert names, "no withdrawn requirement parsed: the withdrawal record format changed"
    return names


def _shared_ids():
    return set(WITHDRAWN_SHARED.findall(WITHDRAWALS.read_text(encoding="utf-8")))


def _blockers():
    document = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return document, [(row["dataset"], blocker)
                      for row in document["datasets"] for blocker in row["blockers"]]


def test_withdrawn_shared_requirements_are_absent_from_the_active_shared_list():
    document, _ = _blockers()
    present = {item["id"] for item in document["shared_blockers"]}
    assert present & _shared_ids() == set(), "a withdrawn shared requirement is active again"


def test_no_active_next_action_names_a_withdrawn_requirement_as_work_to_do():
    _, blockers = _blockers()
    names = _withdrawn_names()
    offenders = []
    for dataset, blocker in blockers:
        for sentence in SENTENCE.split(blocker["next_action"]):
            named = [name for name in names if name in sentence]
            if named and not any(marker in sentence.lower() for marker in MARKERS):
                offenders.append((dataset, blocker["id"], named, sentence[:160]))
    assert offenders == [], f"withdrawn requirements re-imposed as obligations: {offenders}"


def test_no_active_next_action_requires_the_generic_shared_gates():
    _, blockers = _blockers()
    offenders = []
    for dataset, blocker in blockers:
        for sentence in SENTENCE.split(blocker["next_action"]):
            if any(phrase in sentence for phrase in GENERIC) and \
                    not any(marker in sentence.lower() for marker in MARKERS):
                offenders.append((dataset, blocker["id"], sentence[:160]))
    assert offenders == [], f"active blockers still require the shared gates: {offenders}"


def test_the_withdrawal_record_still_names_the_retained_boundary():
    """Withdrawal is a limit with evidence, not a deletion: the retained scope must stay readable."""
    text = WITHDRAWALS.read_text(encoding="utf-8")
    for marker in ("**Asked for:**", "**Searched:**", "**Result:**"):
        assert marker in text, f"the withdrawal record lost its {marker} evidence structure"
    assert "Retained future opt-in boundary" in text


# Any test module that names a withdrawn shared requirement must also read the record that says it
# was withdrawn. A module that pins the requirement as still active without looking at
# `registry/withdrawn-requirements.md` is exactly the failure this caught by hand:
# test_appworld_trusted_trial_writer_codex183.py asserted appworld's shared_blockers still equalled
# {scorer-offline-closure, artifact-only-state-export} and went red the moment they were withdrawn.
GUARD_DIR = ROOT / "tests" / "quality"


def test_only_tests_that_read_the_withdrawal_record_name_a_withdrawn_requirement():
    offenders = []
    for path in sorted(GUARD_DIR.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        named = sorted(name for name in _shared_ids() if name in text)
        if not named:
            continue
        reads_record = "withdrawn-requirements.md" in text
        if not reads_record:
            offenders.append((path.name, named))
    assert offenders == [], (
        "test modules name a withdrawn shared requirement without reading the withdrawal record: "
        f"{offenders}")


def test_only_tests_that_read_the_withdrawal_record_pin_a_withdrawn_blocker():
    """The same rule for dataset-level withdrawals.

    Three test sites pinned withdrawn blockers as still active and went red the moment the operator
    withdrew them - appworld's shared list, and `ujson-native-offline-closure` in two files. A module
    that names such a blocker must read the record explaining why it is gone.
    """
    withdrawn_ids = {blocker for _, blocker
                     in WITHDRAWN_DATASET.findall(WITHDRAWALS.read_text(encoding="utf-8"))}
    assert withdrawn_ids, "no dataset-level withdrawal parsed"
    offenders = []
    for path in sorted(GUARD_DIR.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        named = sorted(name for name in withdrawn_ids
                       if f'"{name}"' in text or f"'{name}'" in text)
        if named and "withdrawn-requirements.md" not in text:
            offenders.append((path.name, named))
    assert offenders == [], (
        "test modules pin a withdrawn dataset blocker without reading the withdrawal record: "
        f"{offenders}")
