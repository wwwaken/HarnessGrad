"""Known mount-contract regressions using inert trees; no backend execution.

These assertions review the existing prevention plan, not kernel enforcement.
The separate Codex 181 suite covers fatal detection and unknown attribution.
"""
from __future__ import annotations

import builtins
from pathlib import Path
import socket
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from eval import sandbox  # noqa: E402
from harnessgrad import methods  # noqa: E402


@pytest.fixture(autouse=True)
def synthetic_only(monkeypatch):
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        assert name != "data" and not name.startswith("data."), "adapter imports forbidden"
        return original_import(name, *args, **kwargs)

    def denied(*args, **kwargs):
        pytest.fail("network/backend/subprocess execution forbidden")

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    monkeypatch.setattr(socket, "socket", denied)
    monkeypatch.setattr(subprocess, "Popen", denied)
    monkeypatch.setattr(sandbox, "_bwrap", lambda: "/synthetic/bwrap")
    monkeypatch.setattr(sandbox, "RUNTIME", ())
    monkeypatch.setattr(sandbox, "DNS", ())
    monkeypatch.setattr(sandbox, "interpreter_prefix", lambda: None)


@pytest.fixture
def layout(tmp_path):
    platform = tmp_path / "platform"
    program = platform / "methods" / "fabricated" / "run.py"
    program.parent.mkdir(parents=True)
    program.write_text("# inert method fixture\n")
    work_root = tmp_path / "work"
    repo = work_root / "run" / "workspace"
    repo.mkdir(parents=True)
    task = tmp_path / "task"
    task.mkdir()
    return platform, work_root, repo, task, program


def mount_events(command):
    """Read mount options from a generated plan; never launch the command."""
    result = []
    index = 1
    while command[index] != "--":
        option = command[index]
        if option in {"--bind", "--ro-bind"}:
            result.append((option, command[index + 1], command[index + 2]))
            index += 3
        elif option == "--tmpfs":
            result.append((option, None, command[index + 1]))
            index += 2
        elif option in {"--proc", "--dev", "--setenv"}:
            index += 3
        else:
            index += 1
    return result


@pytest.mark.parametrize("verification", [False, True])
def test_native_plan_hides_platform_and_freezes_source(layout, verification):
    platform, work_root, repo, task, _ = layout
    verdict = task / "verdict"
    verdict.mkdir()
    command = sandbox.command(
        ["inert-entrypoint"], platform=platform, work_root=work_root,
        repo=repo, task_dir=task, env={},
        task_dir_writable=not verification,
        writable_paths=(verdict,) if verification else ())
    events = mount_events(command)
    hide = events.index(("--tmpfs", None, str(platform)))
    assert not any(target == str(platform) for _, _, target in events[hide + 1:])
    assert ("--ro-bind", str(repo), str(repo)) in events[hide + 1:]
    assert ("--ro-bind", str(work_root), str(work_root)) in events[hide + 1:]
    assert not any(option == "--bind" and Path(target).is_relative_to(platform)
                   for option, _, target in events)
    task_events = [event for event in events if event[2] == str(task)]
    assert task_events[-1][0] == ("--ro-bind" if verification else "--bind")
    if verification:
        assert events.index(("--bind", str(verdict), str(verdict))) > events.index(
            ("--ro-bind", str(task), str(task)))


def test_method_plan_restores_only_readonly_program_paths(layout, monkeypatch):
    platform, work_root, repo, task, program = layout
    monkeypatch.setattr(methods, "PLATFORM_ROOT", platform)
    monkeypatch.setenv("HARNESSGRAD_WORK_ROOT", str(work_root))
    argv = ["inert-interpreter", str(program)]
    plan = methods._method_sandbox_plan(repo, argv, task, readonly=(repo,))
    assert plan["repo"] == repo
    assert plan["platform"] == platform
    events = mount_events(sandbox.command(argv, env={}, **plan))
    hide = events.index(("--tmpfs", None, str(platform)))
    restored = [(option, target) for option, _, target in events[hide + 1:]
                if Path(target).is_relative_to(platform)]
    assert restored == [("--ro-bind", str(platform / "methods")),
                        ("--ro-bind", str(program.parent))]


def test_unavailable_sandbox_refuses_before_any_process(layout, monkeypatch):
    platform, work_root, repo, task, _ = layout

    def unavailable():
        raise sandbox.SandboxUnavailable("synthetic unavailable backend")

    monkeypatch.setattr(sandbox, "_bwrap", unavailable)
    with pytest.raises(sandbox.SandboxUnavailable, match="synthetic unavailable"):
        sandbox.run(["inert-entrypoint"], platform=platform, work_root=work_root,
                    repo=repo, task_dir=task, env={}, timeout_s=1)
    monkeypatch.setattr(methods, "_method_env", lambda *args: {})
    monkeypatch.setattr(methods, "_method_sandbox_plan", lambda *args: {
        "platform": platform, "work_root": work_root, "repo": repo, "task_dir": task})
    reply = methods._call_entrypoint(repo, ["inert-entrypoint"], {}, timeout_s=1)
    assert "refusing to run the method: sandbox unavailable" in reply["_error"]
