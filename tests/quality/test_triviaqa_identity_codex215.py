"""Identity in materialized verifier evidence, using fabricated answers only."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from tests.quality.test_triviaqa_official_scorer import (
    ROOT,
    no_network,  # noqa: F401 - autouse fixture
    triviaqa,  # noqa: F401 - payload-free adapter fixture
)


@pytest.mark.parametrize("channel,prediction,expected", [
    ("text", "Invented Blue Town", 1),
    ("text", "wrong", 0),
    ("structured", "Invented Blue Town", 1),
    ("structured", "wrong", 0),
    ("text", "", 0),
    ("missing", None, 0),
])
def test_materialized_verifier_preserves_scorer_identity(
        triviaqa, tmp_path, channel, prediction, expected):
    gold = triviaqa._gold({"answer": {
        "value": "Invented Blue Town", "normalized_aliases": ["invented blue town"]}})
    # `63606f42` made the QA scaffold bind the spec to the selected task identity
    # (`data/scaffolds/qa/base.py:339-341`), so a hand-built record must carry one.
    # Fabricated like the answer: this test is about scorer identity surviving
    # materialization, and no dataset row is read.
    spec = triviaqa._SPEC.verifier({"task_id": "triviaqa/test/0", "gold": gold})
    for entry in spec["inputs"]:
        target = tmp_path / entry["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        if "content" in entry:
            target.write_text(entry["content"], encoding="utf-8")
        else:
            source = Path(entry["from"])
            assert source.resolve().is_relative_to(ROOT)
            shutil.copyfile(source, target)
    if channel == "structured":
        (tmp_path / "prediction.json").write_text(json.dumps({
            "schema_version": 1, "answer": prediction}), encoding="utf-8")
        (tmp_path / "answer.txt").write_text("legacy answer must lose precedence")
    elif channel == "text":
        (tmp_path / "answer.txt").write_text(prediction, encoding="utf-8")

    # Import the actual copied scaffold/adapter in a fresh interpreter. Suppress
    # pool construction before adapter import; any attempted payload/network read
    # fails. No cached production adapter or replacement scorer enters the child.
    code = r'''
import pathlib, runpy, socket, sys
def forbidden(*args, **kwargs):
    raise AssertionError("payload reads and network are forbidden")
socket.socket.connect = forbidden
socket.socket.connect_ex = forbidden
socket.create_connection = forbidden
workdir = pathlib.Path.cwd()
sys.path.insert(0, str(workdir))
from data.scaffolds.qa import base
assert pathlib.Path(base.__file__).resolve().is_relative_to(workdir)
base.parquet_rows = forbidden
base.QASpec.records = lambda self: []
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
'''
    result = subprocess.run(
        [sys.executable, "-I", "-S", "-B", "-c", code, *spec["argv"][1:]],
        cwd=tmp_path, capture_output=True, text=True, timeout=20)
    assert result.returncode == (0 if expected else 1), result.stdout + result.stderr
    evidence_path = tmp_path / spec["evidence_file"].lstrip("/")
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["measured"] is True
    assert evidence["reward"] == expected
    assert float((tmp_path / spec["reward_file"].lstrip("/")).read_text()) == expected
    assert evidence["official"]["scorer_identity"] == triviaqa.SCORER_IDENTITY == (
        "triviaqa-alias-max-em-upstream-normalization-all-aliases-v2")
    assert evidence["official"]["reference"] == triviaqa.SCORER_REFERENCE
    assert evidence["scorer_module"] == "data.datasets.triviaqa"
    adapter = tmp_path / "data/datasets/triviaqa.py"
    assert adapter.read_bytes() == (ROOT / "data/datasets/triviaqa.py").read_bytes()
    assert hashlib.sha256(adapter.read_bytes()).hexdigest() != (
        evidence["official"]["reference"]["source_sha256"])
