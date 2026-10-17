"""Train-side `--resume`: continue the loop, never re-measure a round that exists.

The seam is easy to get wrong in one specific way: it rebuilds everything from the record
instead of from a measurement, so if the re-staged workspace does not reproduce the same
content address, the resumed loop would build on a tree the curve's scores do not belong
to. That invariant is asserted here, next to the refusals.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from driver import ResumeNothingToDo, ResumeRefused, _resume_train_state


def _run(tmp_path: Path, *, rounds: tuple[int, ...] = (0, 1), sha: str = "sha-a",
         with_state: bool = True, split_sha: str = "split-1",
         platform: str | None = "platform-1") -> Path:
    run_dir = tmp_path / "runs" / "rsi10-test-train"
    run_dir.mkdir(parents=True)
    points = []
    for r in rounds:
        points.append({"round": r, "score": 0.5,
                       "identity": {"harness_sha": sha if r == rounds[-1] else f"sha-{r}"},
                       "sampling": {"trials": 1, "task_ids": ["t1"]},
                       "per_task": {"t1": 0.5}})
    (run_dir / "curve.jsonl").write_text(
        "\n".join(json.dumps(p) for p in points) + "\n")
    meta = {"split_sha": split_sha}
    if platform:
        meta["platform_content_sha"] = platform
    (run_dir / "run_meta.json").write_text(json.dumps(meta))
    if with_state:
        state = run_dir / f"state_after_round{rounds[-1]}"
        state.mkdir()
        (state / "agent.py").write_text("print('candidate')\n")
    traces = run_dir / "round0_traces"
    traces.mkdir()
    (traces / "t1.jsonl").write_text(json.dumps({"step": 0}) + "\n")
    return run_dir


def _args(rounds: int = 3) -> SimpleNamespace:
    return SimpleNamespace(rounds=rounds)


def test_refuses_without_a_curve(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs" / "empty"
    run_dir.mkdir(parents=True)
    with pytest.raises(ResumeRefused) as exc:
        _resume_train_state(_args(), run_dir, None, tmp_path / "work")
    assert "nothing to continue" in str(exc.value)


def test_refuses_when_the_split_moved(tmp_path: Path) -> None:
    run_dir = _run(tmp_path, split_sha="split-OLD")
    class Split:
        pass
    import driver
    monkeypatched = driver.datasets.split_sha
    try:
        driver.datasets.split_sha = lambda _split: "split-NEW"
        with pytest.raises(ResumeRefused) as exc:
            _resume_train_state(_args(), run_dir, Split(), tmp_path / "work")
        assert "task set" in str(exc.value)
    finally:
        driver.datasets.split_sha = monkeypatched


def test_refuses_when_the_platform_changed(tmp_path: Path) -> None:
    run_dir = _run(tmp_path, platform="platform-OLD")
    import driver
    original = driver._platform_content_sha
    try:
        driver._platform_content_sha = lambda: "platform-NEW"
        with pytest.raises(ResumeRefused) as exc:
            _resume_train_state(_args(), run_dir, None, tmp_path / "work")
        assert "content changed" in str(exc.value)
    finally:
        driver._platform_content_sha = original


def test_refuses_without_the_last_state(tmp_path: Path) -> None:
    run_dir = _run(tmp_path, with_state=False, platform=None)
    with pytest.raises(ResumeRefused) as exc:
        _resume_train_state(_args(), run_dir, None, tmp_path / "work")
    assert "state_after_round" in str(exc.value)


def test_nothing_to_do_when_the_budget_is_already_measured(tmp_path: Path) -> None:
    run_dir = _run(tmp_path, rounds=(0, 1, 2), platform=None)
    with pytest.raises(ResumeNothingToDo) as exc:
        _resume_train_state(_args(rounds=2), run_dir, None, tmp_path / "work")
    assert "already measured" in str(exc.value)


def test_the_restaged_tree_keeps_the_recorded_content_address(tmp_path: Path) -> None:
    """Re-staging the saved state must reproduce the address the curve already names."""
    from ckpt.git_state import commit_state, stage_workspace

    run_dir = tmp_path / "runs" / "rsi10-test-train"
    run_dir.mkdir(parents=True)
    # Build a real harness state, so its content address is the thing under test.
    source = tmp_path / "source"
    source.mkdir()
    (source / "agent.py").write_text("print('state')\n")
    state = run_dir / "state_after_round1"
    stage_workspace(source, state)
    sha = commit_state(state, "round 1")
    (run_dir / "curve.jsonl").write_text("\n".join(
        json.dumps({"round": r, "score": 0.5, "identity": {"harness_sha": sha},
                    "sampling": {"trials": 1}, "per_task": {"t1": 0.5}})
        for r in (0, 1)) + "\n")
    (run_dir / "run_meta.json").write_text(json.dumps({"split_sha": None}))
    traces = run_dir / "round0_traces"
    traces.mkdir()
    (traces / "t1.jsonl").write_text("{}\n")

    got = _resume_train_state(_args(), run_dir, None, tmp_path / "work")
    assert got["last"] == 1
    assert got["recorded_sha"] == sha
    assert got["staged_sha"] == sha, (
        "re-staging the saved state must reproduce the content address the curve names")
    assert (tmp_path / "work" / "agent.py").read_text() == "print('state')\n"
