"""The proposal applier must refuse anything that would silently drop an obligation.

`tools/apply_blocker_proposal.py` is the parent-side integration step for the
`registry/proposals/*.json` fragments that workers emit. Its whole value is the refusal path:
twice during this phase a hand-applied proposal dropped obligations that the blocker's own
`next_action` had carried, and a third time a proposal was applied while the focused tests were
failing. These tests exercise the refusals against a copy of the live registry, so they cannot
damage it.
"""
import copy
import json
from pathlib import Path

import pytest

import tools.apply_blocker_proposal as applier

ROOT = Path(__file__).resolve().parents[2]
LIVE = ROOT / "registry" / "dataset-blockers.json"


@pytest.fixture
def registry(tmp_path):
    """A private copy of the live registry plus a writer for proposal documents."""
    document = json.loads(LIVE.read_text(encoding="utf-8"))
    target = tmp_path / "registry.json"
    target.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def write(name, payload):
        path = tmp_path / name
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    return target, write


def a_blocker(document, dataset="fever", blocker_id="dataset-journal-gap"):
    for row in document["datasets"]:
        if row["dataset"] == dataset:
            for item in row["blockers"]:
                if item["id"] == blocker_id:
                    return item
    raise AssertionError(f"{dataset}/{blocker_id} is not an open blocker")


def test_valid_single_record_proposal_is_applied(registry, capsys):
    target, write = registry
    document = json.loads(target.read_text(encoding="utf-8"))
    old = a_blocker(document)["next_action"]
    proposal = write("ok.json", {
        "dataset": "fever", "blocker": "dataset-journal-gap",
        "observed_append": "TEST-APPEND-MARKER.",
        "next_action_replacement": old + " TEST-REPLACEMENT-MARKER.",
    })
    assert applier.main([str(proposal), "--dataset", "fever",
                         "--blocker", "dataset-journal-gap", "--registry", str(target),
                         "--apply"]) == 0
    updated = a_blocker(json.loads(target.read_text(encoding="utf-8")))
    assert "TEST-REPLACEMENT-MARKER." in updated["next_action"]
    assert "TEST-APPEND-MARKER." in updated["observed"]
    assert '"valid": true' in capsys.readouterr().out


def test_dry_run_writes_nothing(registry):
    target, write = registry
    before = target.read_text(encoding="utf-8")
    document = json.loads(before)
    proposal = write("dry.json", {
        "dataset": "fever", "blocker": "dataset-journal-gap",
        "next_action_replacement": a_blocker(document)["next_action"] + " EXTRA.",
    })
    assert applier.main([str(proposal), "--dataset", "fever",
                         "--blocker", "dataset-journal-gap", "--registry", str(target)]) == 0
    assert target.read_text(encoding="utf-8") == before


def test_refuses_a_quoted_clause_that_is_not_present(registry, capsys):
    target, write = registry
    document = json.loads(target.read_text(encoding="utf-8"))
    old = a_blocker(document)["next_action"]
    proposal = write("badquote.json", {
        "changes": [{"dataset": "fever", "blocker": "dataset-journal-gap",
                     "quoted_clause": "this sentence is not in the registry at all",
                     "replacement": old + " X."}],
    })
    assert applier.main([str(proposal), "--dataset", "fever",
                         "--blocker", "dataset-journal-gap", "--registry", str(target)]) == 1
    assert "REFUSED" in capsys.readouterr().err


def test_refuses_a_replacement_that_drops_an_obligation(registry, capsys):
    target, write = registry
    proposal = write("short.json", {
        "dataset": "fever", "blocker": "dataset-journal-gap",
        "next_action_replacement": "Keep working on fever.",
    })
    captured = capsys.readouterr()
    assert applier.main([str(proposal), "--dataset", "fever",
                         "--blocker", "dataset-journal-gap", "--registry", str(target)]) == 1
    err = capsys.readouterr().err
    assert "not carried by the replacement" in err
    assert "next_action" in err
    assert captured.out == ""
    # The override exists, but only after the dropped sentences have been printed for review.
    assert applier.main([str(proposal), "--dataset", "fever", "--blocker", "dataset-journal-gap",
                         "--registry", str(target), "--force"]) == 0


def test_refuses_divergent_replacements_in_a_changes_list(registry, capsys):
    target, write = registry
    document = json.loads(target.read_text(encoding="utf-8"))
    old = a_blocker(document)["next_action"]
    proposal = write("divergent.json", {
        "changes": [
            {"dataset": "fever", "blocker": "dataset-journal-gap",
             "quoted_clause": "Retain", "replacement": old + " A."},
            {"dataset": "fever", "blocker": "dataset-journal-gap",
             "quoted_clause": "Retain", "replacement": old + " B."},
        ],
    })
    assert applier.main([str(proposal), "--dataset", "fever",
                         "--blocker", "dataset-journal-gap", "--registry", str(target)]) == 1
    assert "distinct replacement strings" in capsys.readouterr().err


def test_refuses_an_unknown_blocker(registry, capsys):
    target, write = registry
    proposal = write("unknown.json", {
        "dataset": "fever", "blocker": "no-such-blocker",
        "next_action_replacement": "x",
    })
    assert applier.main([str(proposal), "--dataset", "fever",
                         "--blocker", "no-such-blocker", "--registry", str(target)]) == 1
    assert "no open blocker" in capsys.readouterr().err


def test_identical_replacement_is_refused(registry, capsys):
    target, write = registry
    document = json.loads(target.read_text(encoding="utf-8"))
    proposal = write("same.json", {
        "dataset": "fever", "blocker": "dataset-journal-gap",
        "next_action_replacement": a_blocker(document)["next_action"],
    })
    assert applier.main([str(proposal), "--dataset", "fever",
                         "--blocker", "dataset-journal-gap", "--registry", str(target)]) == 1
    assert "identical to the current value" in capsys.readouterr().err


def test_observed_append_is_idempotent(registry, capsys):
    target, write = registry
    document = json.loads(target.read_text(encoding="utf-8"))
    old_action = a_blocker(document)["next_action"]
    marker = "IDEMPOTENT-MARKER."
    first = write("first.json", {"dataset": "fever", "blocker": "dataset-journal-gap",
                                 "observed_append": marker,
                                 "next_action_replacement": old_action + " A."})
    assert applier.main([str(first), "--dataset", "fever", "--blocker", "dataset-journal-gap",
                         "--registry", str(target), "--apply"]) == 0
    after_first = a_blocker(json.loads(target.read_text(encoding="utf-8")))
    assert after_first["observed"].count(marker) == 1
    second = write("second.json", {"dataset": "fever", "blocker": "dataset-journal-gap",
                                   "observed_append": marker,
                                   "next_action_replacement": after_first["next_action"] + " B."})
    assert applier.main([str(second), "--dataset", "fever", "--blocker", "dataset-journal-gap",
                         "--registry", str(target), "--apply"]) == 0
    assert "no-op" in capsys.readouterr().out
    assert a_blocker(json.loads(target.read_text(encoding="utf-8")))["observed"].count(marker) == 1


def test_a_broken_registry_is_restored(registry, capsys, tmp_path):
    """If the write would leave the registry invalid, the original bytes come back."""
    target, write = registry
    document = json.loads(target.read_text(encoding="utf-8"))
    before = target.read_text(encoding="utf-8")
    # A proposal that is clean by the applier's own checks but corrupts the registry on write is
    # simulated by pointing the checker at a registry whose statuses the checker rejects.
    broken = tmp_path / "broken.json"
    mutated = copy.deepcopy(document)
    a_blocker(mutated)["status"] = "not-a-real-status"
    broken.write_text(json.dumps(mutated, indent=2), encoding="utf-8")
    original = broken.read_text(encoding="utf-8")
    proposal = write("ok2.json", {"dataset": "fever", "blocker": "dataset-journal-gap",
                                  "next_action_replacement": a_blocker(mutated)["next_action"] + " A."})
    assert applier.main([str(proposal), "--dataset", "fever", "--blocker", "dataset-journal-gap",
                         "--registry", str(broken), "--force", "--apply"]) == 1
    assert broken.read_text(encoding="utf-8") == original
    assert "restored" in capsys.readouterr().err


def test_acknowledge_phrases_allow_named_drops_but_only_named_ones(registry, capsys):
    target, write = registry
    document = json.loads(target.read_text(encoding="utf-8"))
    old = a_blocker(document)["next_action"]
    # Drop exactly one sentence, and name it.
    first = applier.sentences(old)[0]
    proposal = write("named.json", {
        "dataset": "fever", "blocker": "dataset-journal-gap",
        "next_action_replacement": old.replace(first + " ", ""),
    })
    base = [str(proposal), "--dataset", "fever", "--blocker", "dataset-journal-gap",
            "--registry", str(target), "--min-coverage", "0.99"]
    # A phrase that does not name the dropped sentence must not unlock it.
    assert applier.main(base + ["--acknowledge", "something else entirely"]) == 1
    assert "not carried by the replacement" in capsys.readouterr().err
    # Naming it does.
    assert applier.main(base + ["--acknowledge", first[:60]]) == 0
    assert "dry run" in capsys.readouterr().out


def test_forced_apply_warns_about_unacknowledged_drops(registry, capsys):
    target, write = registry
    proposal = write("forced.json", {
        "dataset": "fever", "blocker": "dataset-journal-gap",
        "next_action_replacement": "Keep working on fever.",
    })
    assert applier.main([str(proposal), "--dataset", "fever", "--blocker", "dataset-journal-gap",
                         "--registry", str(target), "--force"]) == 0
    captured = capsys.readouterr()
    assert "WARNING" in captured.err
    assert "uncovered sentence(s) applied without acknowledgement" in captured.err
