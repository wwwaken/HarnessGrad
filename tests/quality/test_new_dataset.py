"""The generator's promise: a scaffold that already passes the five gates.

`tools/new_dataset.py` is only worth having if the thing it generates works. A skeleton with
TODOs would be *less* useful than copying a working dataset, because it would look finished.
So the promise is exact -- generate, lint, oracle 1, noop 0, by hand and through the
platform -- and this file is what holds the tool to it.

The loop is run against throwaway names under `data/`, and the fixture removes every artefact
whether the test passes or fails. A scaffold left behind by a failing test would be a scaffold
that the next full-suite run lints as a published dataset.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import dataset_lint  # noqa: E402
import new_dataset  # noqa: E402
from data import registry  # noqa: E402

SOURCE = {
    "url": "https://example.invalid/scaffold-probe.tar.gz",
    "version": "v1.2.3",
    "size": "1 MB",
    "note": "A probe source used by tests/quality/test_new_dataset.py; never fetched, so "
            "it has no traps to record.",
}

KINDS = {
    "qa": {"module": "scaffold_probe_qa", "control": ["data/qa/control.py"],
           "control_args": ["--dataset", "scaffold_probe_qa"]},
    "command": {"module": "scaffold_probe_cmd", "control": ["data/scaffold_probe_cmd/control.py"],
                "control_args": []},
}


def _artifacts(name: str) -> list[Path]:
    return [ROOT / "data" / f"{name}.py", ROOT / "data" / name]


@pytest.fixture(params=sorted(KINDS))
def scaffold(request):
    """Generate the scaffold, hand it to the test, then remove every artefact."""
    kind = request.param
    name = KINDS[kind]["module"]
    for path in _artifacts(name):
        if path.is_dir():
            import shutil
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()
    new_dataset.generate(name, kind, SOURCE)
    try:
        yield kind, name
    finally:
        for path in _artifacts(name):
            if path.is_dir():
                import shutil
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()
        # The module may have been imported by the lint; a cached entry would shadow the
        # next generation of the same name.
        sys.modules.pop(f"data.{name}", None)


def _run(argv: list[str], *, timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *argv], cwd=ROOT, capture_output=True,
                          text=True, timeout=timeout)


def test_the_scaffold_is_not_a_published_dataset(scaffold):
    """`KIND = "fixture"` is what keeps a scaffold out of the chooser until it is real."""
    _, name = scaffold
    assert name not in registry.published()


def test_the_scaffold_passes_the_lint(scaffold):
    kind, name = scaffold
    result = dataset_lint.lint_dataset(name, dataset_lint.load_schema())
    assert result.ok, f"{kind} scaffold: " + "; ".join(result.errors)
    assert not result.unprovisioned, "the scaffold must be lintable, not skipped"


def test_the_scaffold_declares_pinned_provenance(scaffold):
    """A dataset must name where its bytes came from -- the lint refuses an empty list."""
    _, name = scaffold
    module = registry.importlib.import_module(f"data.{name}")
    entries = module.downloads()
    assert entries, "downloads() is empty; the contract requires provenance"
    for entry in entries:
        assert entry["version"] == SOURCE["version"]
        assert entry["url"] == SOURCE["url"]
        assert len(entry["note"]) >= 20


@pytest.mark.parametrize("arm,expected", [("--oracle", "1"), ("--noop", "0")])
def test_the_scaffold_controls_reach_the_expected_reward(scaffold, arm, expected):
    kind, name = scaffold
    argv = KINDS[kind]["control"] + KINDS[kind]["control_args"] + [arm]
    proc = _run(argv)
    assert proc.returncode == 0, f"{kind} {arm}: {proc.stdout[-800:]} {proc.stderr[-400:]}"
    # The two controls pad differently (`reward  1` vs `reward 1: matches`), so the number
    # is parsed rather than the spacing matched. `(?![\d.])` keeps `1` from matching the
    # `1` of `1.0`, which is what the platform arm reports.
    assert re.search(rf"reward\s+{re.escape(expected)}(?![\d.])", proc.stdout), \
        f"{kind} {arm} did not report reward {expected}: {proc.stdout[-800:]}"


@pytest.mark.parametrize("arm,expected", [("--oracle", "1.0"), ("--noop", "0.0")])
def test_the_scaffold_controls_pass_through_the_platform(scaffold, arm, expected):
    """The second half of gates 1 and 2: `SETUP -> harness -> VERIFY` via `run_one`."""
    kind, name = scaffold
    argv = KINDS[kind]["control"] + KINDS[kind]["control_args"] + [arm, "--platform"]
    proc = _run(argv)
    assert proc.returncode == 0, f"{kind} {arm} --platform: {proc.stdout[-800:]}"
    assert f"score    {expected}" in proc.stdout, \
        f"{kind} {arm} --platform reported {proc.stdout[-600:]}"


def test_the_generator_refuses_to_overwrite(scaffold):
    kind, name = scaffold
    with pytest.raises(SystemExit) as excinfo:
        new_dataset.generate(name, kind, SOURCE)
    assert "refusing to overwrite" in str(excinfo.value)


def test_the_generator_refuses_an_unpinned_source(tmp_path):
    """An unpinned scaffold teaches the wrong habit on its first line."""
    with pytest.raises(SystemExit) as excinfo:
        new_dataset.generate("scaffold_probe_unpinned", "qa",
                             {**SOURCE, "version": "main"})
    assert "branch, not a pin" in str(excinfo.value)
    assert not (ROOT / "data" / "scaffold_probe_unpinned.py").exists()


def test_the_generator_refuses_a_source_with_no_trap_recorded():
    with pytest.raises(SystemExit) as excinfo:
        new_dataset.generate("scaffold_probe_bare", "qa", {**SOURCE, "note": "todo"})
    assert "at least 20 characters" in str(excinfo.value)
    assert not (ROOT / "data" / "scaffold_probe_bare.py").exists()


def test_the_files_kind_says_why_it_is_not_generated_yet():
    """A refused shape must refuse *loudly*, naming the decision and where to read."""
    with pytest.raises(SystemExit) as excinfo:
        new_dataset.generate("scaffold_probe_files", "files", SOURCE)
    message = str(excinfo.value)
    assert "deliberately not implemented" in message
    assert "docs/survey/README.md" in message
    assert not (ROOT / "data" / "scaffold_probe_files.py").exists()
