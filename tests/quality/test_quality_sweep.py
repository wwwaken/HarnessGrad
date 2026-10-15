"""The sweep tool must not be able to report a clean run it did not perform.

`tools/quality_sweep.py` exists because a chunked sweep hid seven red files in `main` on 2026-10-15: a
pytest collection error aborts a whole batch and the batch summary still reads clean. The properties
pinned here are the ones that make its report worth reading - every selected file produces a *recorded*
outcome even when it cannot be launched, a red file fails the run, a timeout is recorded as a timeout,
and a subset run says out loud that it is not a coverage measurement.

The tool is not pointed at the real suite here (that takes minutes and drives real sandboxes); the parts
that would launch pytest are replaced, and the real discovery is checked on its own.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def sweep():
    spec = importlib.util.spec_from_file_location("quality_sweep", ROOT / "tools" / "quality_sweep.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _ok(path: Path) -> dict:
    return {"file": str(path.relative_to(ROOT)), "returncode": 0, "timed_out": False,
            "seconds": 0.0, "summary": "1 passed", "failures": []}


def test_discovery_covers_the_real_suite(sweep):
    found = sweep.discover()
    assert len(found) > 100, (
        f"only {len(found)} quality files discovered: the glob or the directory moved, and a sweep that "
        f"finds nothing passes for the wrong reason")
    assert all(p.name.startswith("test_") and p.suffix == ".py" for p in found)
    assert (ROOT / "tests/quality/test_verifier.py") in found


def test_a_launch_failure_is_a_recorded_result_not_a_gap(sweep, monkeypatch, tmp_path):
    """`run_one` must never raise: if it could drop an entry, the coverage check compares a list with
    itself and stops being able to fail."""
    def boom(*args, **kwargs):
        raise OSError("synthetic launch failure")

    monkeypatch.setattr(sweep.subprocess, "run", boom)
    result = sweep.run_one(ROOT / "tests/quality/test_verifier.py", 5, tmp_path)
    assert result["returncode"] == 1
    assert result["timed_out"] is False
    assert "OSError" in result["summary"]
    assert result["file"] == "tests/quality/test_verifier.py"


def test_a_timeout_is_recorded_as_a_timeout(sweep, monkeypatch, tmp_path):
    def times_out(*args, **kwargs):
        raise sweep.subprocess.TimeoutExpired(cmd="pytest", timeout=5, output="partial output")

    monkeypatch.setattr(sweep.subprocess, "run", times_out)
    result = sweep.run_one(ROOT / "tests/quality/test_verifier.py", 5, tmp_path)
    assert result["returncode"] == 124 and result["timed_out"] is True


def test_a_file_that_could_not_be_launched_is_counted_red(sweep, monkeypatch, capsys):
    """The failure mode the tool exists for: the file is not silently absent from the report."""
    selected = sweep.discover()[:3]
    monkeypatch.setattr(sweep, "discover", lambda: selected)
    monkeypatch.setattr(sweep, "run_one", lambda p, t, r: (
        {"file": str(p.relative_to(ROOT)), "returncode": 1, "timed_out": False, "seconds": 0.0,
         "summary": "OSError: synthetic launch failure", "failures": []}
        if p == selected[1] else _ok(p)))
    assert sweep.main([]) == 1
    out = capsys.readouterr().out
    assert "ran 3 of 3 selected files" in out
    assert "1 red" in out and selected[1].name in out


def test_a_subset_run_is_not_dressed_up_as_coverage(sweep, monkeypatch, capsys):
    monkeypatch.setattr(sweep, "run_one", lambda p, t, r: _ok(p))
    assert sweep.main(["--only", "test_verifier.py"]) == 0
    captured = capsys.readouterr()
    assert "NOT evidence that the suite is green" in captured.err
    assert "1 of 1 selected files" in captured.out
    assert f"{len(sweep.discover())} exist" in captured.out


def test_every_discovered_file_appears_in_the_report(sweep, monkeypatch, capsys):
    """The coverage invariant, on the real list: every discovered file is selected by default."""
    monkeypatch.setattr(sweep, "run_one", lambda p, t, r: _ok(p))
    assert sweep.main([]) == 0
    out = capsys.readouterr().out
    total = len(sweep.discover())
    assert f"ran {total} of {total} selected files ({total} exist)" in out


def test_the_json_report_names_the_coverage(sweep, monkeypatch, tmp_path):
    report = tmp_path / "sweep.json"
    monkeypatch.setattr(sweep, "run_one", lambda p, t, r: _ok(p))
    assert sweep.main(["--only", "test_verifier.py", "--json", str(report)]) == 0
    payload = json.loads(report.read_text())
    assert payload["discovered"] > 100 and payload["selected"] == 1 and payload["ran"] == 1
    assert payload["missing"] == [] and payload["interrupted"] is False
