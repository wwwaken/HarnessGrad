"""Opt-in synthetic GSM8K fixture; never opens a provisioned dataset."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def synthetic_gsm8k():
    """Build an isolated adapter using three synthetic test and five train rows.

    Split names exercise the adapter contract; these are authored unit-test data,
    not released questions or benchmark measurements.
    """
    sys.path.insert(0, str(ROOT))
    from data.scaffolds.qa import base

    answers = {
        "test": ("18", "3.5", "-3.25"),
        "train": ("42", "1250", "-3", "7000", "18.0"),
    }
    tables = {
        split: [
            {"question": f"Synthetic {split} question {i}: compute a value.",
             "answer": f"Synthetic solution for {split} row {i}.\n#### {answer}"}
            for i, answer in enumerate(values)
        ]
        for split, values in answers.items()
    }
    reads = []

    def synthetic_rows(path):
        split = Path(path).name.split("-", 1)[0]
        assert split in tables, path
        reads.append(split)
        return tables[split]

    spec = importlib.util.spec_from_file_location(
        "gsm8k_synthetic_contract", ROOT / "data" / "gsm8k.py")
    module = importlib.util.module_from_spec(spec)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(base, "parquet_rows", synthetic_rows)
        spec.loader.exec_module(module)
    assert reads == ["test", "train"]
    assert module._LOAD_ERROR is None
    # Keep any later table rebuild confined to the same synthetic rows.
    module._SPEC._rows = lambda: tables
    return module
