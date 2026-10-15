"""Wrapper scratch lifecycle only; authored inputs, no benchmark or model."""
from __future__ import annotations

import json
from pathlib import Path
import runpy
import subprocess
import sys

import pytest


CHECK = Path(__file__).resolve().parents[2] / "data/datasets/ds1000/verify/check.py"


@pytest.mark.parametrize("outcome", ["pass", "fail", "timeout", "spawn-error", "setup-error"])
def test_wrapper_removes_only_its_scratch_on_return_or_exception(tmp_path, monkeypatch, outcome):
    check = runpy.run_path(str(CHECK))
    work = tmp_path / "task"
    work.mkdir()
    scratch_root = tmp_path / "scratch"
    scratch_root.mkdir()
    sentinel = scratch_root / "unrelated"
    sentinel.write_text("keep")
    (work / "context.json").write_text(json.dumps({
        "code_context": "def test_execution(code):\n    exec(code)\n"}))
    (work / "solution.py").write_text("assert False\n" if outcome == "fail" else "assert True\n")
    # A dependency stub tests wrapper plumbing; the evidence packet separately runs
    # the actual pinned upstream execution.py against authored arithmetic.
    if outcome != "setup-error":
        (work / "execution.py").write_text(
            "def check_correctness(program, timeout):\n"
            "    try:\n"
            "        exec(program, {})\n"
            "        return {'passed': True, 'result': 'passed'}\n"
            "    except AssertionError:\n"
            "        return {'passed': False, 'result': 'failed'}\n")
    monkeypatch.chdir(work)
    monkeypatch.setattr(sys, "argv", [str(CHECK)])
    monkeypatch.setattr(check["tempfile"], "tempdir", str(scratch_root))
    real_run = subprocess.run
    created = []

    def run_runner(argv, **kwargs):
        scratch = Path(kwargs["cwd"])
        created.append(scratch)
        assert scratch.parent == scratch_root
        assert {p.name for p in scratch.iterdir()} == {
            "execution.py", "run_ds1000.py", "program.json"}
        assert json.loads((scratch / "program.json").read_text()).endswith("test_execution(code)\n")
        assert kwargs["timeout"] == 130
        if outcome == "timeout":
            raise subprocess.TimeoutExpired(argv, kwargs["timeout"])
        if outcome == "spawn-error":
            raise OSError("authored spawn failure")
        return real_run(argv, **kwargs)

    monkeypatch.setattr(check["subprocess"], "run", run_runner)
    error = {"timeout": subprocess.TimeoutExpired, "spawn-error": OSError,
             "setup-error": FileNotFoundError}.get(outcome)
    if error:
        with pytest.raises(error):
            check["main"]()
        assert not (work / "verifier/reward.txt").exists()
    else:
        assert check["main"]() == 0
        expected = float(outcome == "pass")
        assert float((work / "verifier/reward.txt").read_text()) == expected
        evidence = json.loads((work / "verifier/evidence.json").read_text())
        assert evidence["measured"] is True
        assert evidence["reward"] == expected
    if outcome != "setup-error":
        assert len(created) == 1
        assert not created[0].exists()
    assert list(scratch_root.iterdir()) == [sentinel]
    assert sentinel.read_text() == "keep"
