"""Offline raw-packet reconciliation and fail-closed corruption controls."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil

import pytest

HERE = Path(__file__).resolve().parents[1] / "fixtures/hg_we5"
if not HERE.is_dir():
    pytest.skip("tests/fixtures/hg_we5 is internal (see .gitignore) and absent from this clone",
                allow_module_level=True)

spec = importlib.util.spec_from_file_location("we5_packet", HERE / "verify.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
CASES = json.loads((HERE / "evidence/cases.json").read_text())


def test_complete_packet_including_wal_and_retained_attempts():
    assert audit.validate()["valid"]


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_real_export_and_actual_local_scorer_pair(case):
    assert audit.check_pair(HERE / "evidence", case)["equivalent"]


@pytest.mark.parametrize("change", ["bytes", "missing_structured", "extra_file", "claimed_reward"])
def test_independent_reconciliation_rejects_changed_evidence(tmp_path, change):
    case = next(c for c in CASES if c["id"] == "hotpotqa-positive")
    out = tmp_path / case["id"]
    shutil.copytree(HERE / "evidence" / case["id"], out)
    if change == "bytes":
        (out / "exported/answer.txt").write_text("changed\n")
    elif change == "missing_structured":
        (out / "exported/prediction.json").unlink()
    elif change == "extra_file":
        (out / "exported/unselected.txt").write_text("unselected\n")
    else:
        path = out / "comparison.json"
        claimed = json.loads(path.read_text())
        claimed["pre"]["reward"] = claimed["post"]["reward"] = 0.0
        path.write_text(json.dumps(claimed))
    with pytest.raises((AssertionError, audit.artifacts.AdmissionError)):
        audit.check_pair(tmp_path, case)
