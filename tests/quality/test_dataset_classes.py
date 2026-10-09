"""The dataset classification must stay total, and its two sides must agree.

`tools/dataset_classes.py` splits the classification into three kinds of axis on purpose:

* **derived** from the adapter and the shipped CLI (environment, verifier, interaction,
  counts) -- so it cannot go stale while nobody is looking;
* **judged**, and only the capability domain is judged: it is declared once in `CAPABILITY`,
  and the tool refuses a published dataset without one;
* **measured** elsewhere (cost, difficulty, headroom), never in that file.

The interaction axis is the one that earns its keep: it is the difference between a dataset a
scaffold can iterate inside and one it can only answer once. It is derived *and* declared, and
these tests hold the two sides together. That is not ceremony -- the first version derived it
from a single verb (`do`) and silently called `agentdojo` a single-shot dataset, because
`dojo` spells its action verb `call`.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import dataset_classes  # noqa: E402
from data import registry  # noqa: E402


def _rows() -> list[dict]:
    return dataset_classes.classify_all()


def test_every_published_dataset_is_classified_exactly_once():
    rows = _rows()
    names = [row["dataset"] for row in rows]
    assert sorted(names) == sorted(registry.published())
    assert len(names) == len(set(names))


def test_the_capability_vocabulary_is_closed_and_total():
    rows = _rows()
    vocabulary = set(dataset_classes.CAPABILITY.values())
    for row in rows:
        assert row["domain"] in vocabulary, row
    declared = set(dataset_classes.CAPABILITY)
    assert declared == set(registry.published()), (
        "CAPABILITY must name exactly the published datasets; the tool raises otherwise, so "
        "this assertion documents the property rather than reimplementing it")
    # A vocabulary with one member per dataset would classify nothing.
    assert len(vocabulary) < len(rows)


def test_the_derived_interaction_agrees_with_the_declared_one():
    rows = _rows()
    for row in rows:
        if row["refused"]:
            assert row["interaction"] == "n/a (refused)"
            continue
        assert row["interaction"] == dataset_classes.EXPECTED_INTERACTION[row["dataset"]], row


def test_the_cross_check_actually_fires():
    """Two sides that can never disagree are one side with extra steps."""
    original = dict(dataset_classes.EXPECTED_INTERACTION)
    try:
        dataset_classes.EXPECTED_INTERACTION["agentdojo"] = "single_shot"
        with pytest.raises(SystemExit) as excinfo:
            dataset_classes.classify_all()
        assert "agentdojo" in str(excinfo.value)
        assert "agentdojo" in str(excinfo.value)
    finally:
        dataset_classes.EXPECTED_INTERACTION.clear()
        dataset_classes.EXPECTED_INTERACTION.update(original)
    assert dataset_classes.classify_all()  # restored


def test_a_container_environment_is_always_a_closed_loop():
    for row in _rows():
        if "exec" in row["env_kinds"]:
            assert row["interaction"] == "closed_loop", row


def test_every_closed_loop_dataset_ships_a_program_or_is_a_container():
    """The derivation reads a shipped program; a `files` closed loop with none means it read
    nothing. An `exec` dataset is the other case on purpose: the agent gets a shell, so there
    is no CLI to ship and the container itself is the interface."""
    for row in _rows():
        if row["interaction"] != "closed_loop" or "exec" in row["env_kinds"]:
            continue
        assert row["action_surface"], row


def test_every_shipped_program_declares_a_readable_verb_set():
    """The failure mode this replaced: a new spelling silently yielding `single_shot`."""
    for name in registry.published():
        module = registry.importlib.import_module(f"data.{name}")
        if getattr(module, "REFUSED", None):
            continue
        task_id = module.load()[0][0]["task_id"]
        for script in dataset_classes._cli_scripts(module, task_id):
            verbs = dataset_classes._declared_verbs(script)
            assert verbs, (f"{script} declares no verb set this tool can read; a third "
                           f"spelling has to be added deliberately")


def test_an_unreadable_verb_set_is_reported_not_defaulted(tmp_path):
    """A CLI spelled some third way must be loud, not quietly classified."""
    weird = tmp_path / "weird_cli"
    weird.write_text("#!/usr/bin/env python3\nimport sys\nmode = sys.argv[1]\n"
                     "if mode in {'alpha', 'beta'}:\n    pass\n")
    assert dataset_classes._declared_verbs(weird) == set()


def test_the_json_view_is_machine_readable():
    proc = subprocess.run([sys.executable, "tools/dataset_classes.py", "--json"],
                          cwd=ROOT, capture_output=True, text=True, timeout=300)
    assert proc.returncode == 0, proc.stderr[-400:]
    rows = json.loads(proc.stdout)
    assert len(rows) == len(registry.published())
    assert all({"dataset", "domain", "interaction", "tasks"} <= set(row) for row in rows)


def test_the_filters_select_what_they_say():
    proc = subprocess.run([sys.executable, "tools/dataset_classes.py", "--json",
                           "--interaction", "closed_loop", "--runnable-only"],
                          cwd=ROOT, capture_output=True, text=True, timeout=300)
    rows = json.loads(proc.stdout)
    assert rows and all(row["interaction"] == "closed_loop" and not row["refused"]
                        for row in rows)
    # Pinned as an exact set on purpose: the closed-loop datasets have an exec environment.
    assert {row["dataset"] for row in rows} == {
        "agentdojo", "alfworld", "appworld", "gaia", "jericho", "scienceworld",
        "tau_bench", "terminal_bench"}
