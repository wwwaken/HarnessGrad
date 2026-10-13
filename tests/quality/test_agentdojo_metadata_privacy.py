"""Metadata-only privacy checks; no task payloads or verifier execution."""
from __future__ import annotations

import builtins
import importlib
from pathlib import Path

import pytest


@pytest.mark.parametrize("name", ["ENV", "SETUP", "VERIFY"])
def test_metadata_maps_need_no_dataset_reads(name, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("metadata inspection attempted a dataset read")

    # Keep the guard scoped to the metadata request so pytest can report normally.
    with monkeypatch.context() as guard:
        guard.setattr(builtins, "open", forbidden)
        for method in ("open", "read_text", "read_bytes"):
            guard.setattr(Path, method, forbidden)
        module = importlib.import_module("data.agentdojo")
        for hook in ("records", "load", "control_task", "oracle_files"):
            guard.setattr(module, hook, forbidden)
        metadata = getattr(module, name)

    assert set(metadata) == {
        f"agentdojo/{index}" for index in range(module.TASK_COUNT)
    }
