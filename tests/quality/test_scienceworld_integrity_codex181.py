"""Synthetic attribution regression; no ScienceWorld imports or execution.

Only fabricated bytes and a temporary Git index are used. Hash differences must
remain fatal, but neither guard can infer a writer or source tracking from them.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from eval.run.integrity import diff, snapshot  # noqa: E402
from harnessgrad import methods, records  # noqa: E402


@pytest.fixture
def fabricated_tree(tmp_path):
    root = tmp_path / "platform"
    (root / "eval").mkdir(parents=True)
    source = root / "eval" / "fabricated.py"
    source.write_text("# inert tracked fixture\n")
    subprocess.run(["git", "init", "-q", str(root)], check=True,
                   capture_output=True)
    subprocess.run(["git", "-C", str(root), "add", "--", "eval/fabricated.py"],
                   check=True, capture_output=True)
    note = root / "eval" / "task-output.txt"
    note.write_text("inert untracked fixture\n")
    tracked = subprocess.run(["git", "-C", str(root), "ls-files", "-z"],
                             check=True, capture_output=True).stdout.split(b"\0")
    assert b"eval/fabricated.py" in tracked
    assert b"eval/task-output.txt" not in tracked
    return root


def _mutation(root, case):
    if case == "user-source-edit":
        path = root / "eval" / "fabricated.py"
        path.write_text("# inert concurrent user edit\n")
        return "modified", "eval/fabricated.py"
    if case == "untracked-output-edit":
        path = root / "eval" / "task-output.txt"
        path.write_text("inert task output changed\n")
        return "modified", "eval/task-output.txt"
    if case == "untracked-task-add":
        path = root / "eval" / "task.json"
        path.write_text('{"task_id": "fabricated"}\n')
        return "added", "eval/task.json"
    path = root / "eval" / "fabricated.py"
    path.unlink()
    return "removed", "eval/fabricated.py"


@pytest.mark.parametrize("guard", ["evaluation", "method"])
@pytest.mark.parametrize("case", ["user-source-edit", "untracked-output-edit",
                                  "untracked-task-add", "source-remove"])
def test_mismatches_stop_without_writer_or_tracking_claim(
        fabricated_tree, monkeypatch, capsys, guard, case):
    root = fabricated_tree
    expected = []
    notes = []

    def local_change(*args, **kwargs):
        expected.append(_mutation(root, case))
        return {"synthetic_reply": True}

    if guard == "method":
        monkeypatch.setattr(methods, "PLATFORM_ROOT", root)
        # No method process is spawned: the test itself changes inert bytes.
        monkeypatch.setattr(methods, "_call_entrypoint", local_change)
        with pytest.raises(methods.PlatformTampered) as exc:
            methods._call_method(root.parent / "candidate", [], {}, timeout_s=1)
        output = capsys.readouterr().err
    else:
        before = snapshot(root)
        local_change()
        changes = diff(before, snapshot(root))
        monkeypatch.setattr(records, "console", SimpleNamespace(
            note=lambda message, **kwargs: notes.append((message, kwargs))))
        with pytest.raises(methods.PlatformTampered) as exc:
            records._require_untampered({"tampered": changes})
        assert len(notes) == 1
        assert notes[0][1]["level"] == "error"
        output = notes[0][0] + notes[0][1]["human"]

    kind, path = expected[0]
    assert exc.value.args[0][kind] == [path]
    assert path in output
    assert "Content snapshots do not identify the writer or source tracking" in output
    assert "Run integrity is unverified" in output
    assert "harness modified the platform" not in output
    assert "method modified the platform" not in output
    assert "Restore" not in output  # A user's edit must not be presumed unwanted.


@pytest.mark.parametrize("guard", ["evaluation", "method"])
def test_task_and_candidate_changes_outside_platform_are_not_mismatches(
        fabricated_tree, monkeypatch, guard):
    root = fabricated_tree

    def task_change(*args, **kwargs):
        (root.parent / "task.json").write_text('{"task_id": "fabricated"}\n')
        (root.parent / "candidate.py").write_text("# inert candidate edit\n")
        return {"synthetic_reply": True}

    if guard == "method":
        monkeypatch.setattr(methods, "PLATFORM_ROOT", root)
        monkeypatch.setattr(methods, "_call_entrypoint", task_change)
        assert methods._call_method(root.parent, [], {}, timeout_s=1) == {
            "synthetic_reply": True}
    else:
        before = snapshot(root)
        task_change()
        changes = diff(before, snapshot(root))
        assert not any(changes.values())
        records._require_untampered({"tampered": changes})


def test_candidate_tree_inside_fixture_remains_excluded(fabricated_tree):
    root = fabricated_tree
    before = snapshot(root)
    candidate = root / "base_harness" / "fabricated"
    candidate.mkdir(parents=True)
    (candidate / "agent.py").write_text("# inert candidate edit\n")
    assert not any(diff(before, snapshot(root)).values())


def test_untracked_explicit_environment_input_remains_protected(fabricated_tree):
    root = fabricated_tree
    before = snapshot(root)
    (root / ".env").write_text("FABRICATED_VALUE=fixture\n")
    assert diff(before, snapshot(root))["added"] == [".env"]
