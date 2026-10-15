"""Authored controls for recalculating a frozen SpreadsheetBench artifact."""
from __future__ import annotations

import errno
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

import openpyxl
import pytest


ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("expected", [1, 2], ids=["match", "mismatch"])
def test_formula_result_is_compared_without_writing_frozen_task(
        tmp_path, monkeypatch, capsys, expected):
    spec = importlib.util.spec_from_file_location(
        "spreadsheetbench_readonly_w_sbfix2",
        ROOT / "data/datasets/spreadsheetbench/verify/check.py")
    check = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(check)
    work = tmp_path / "frozen-task"
    work.mkdir()
    wb = openpyxl.Workbook()
    wb.active["A1"] = "=1"
    wb.save(work / "result.xlsx")
    wb.active["A1"] = expected
    wb.save(work / "golden.xlsx")
    wb.close()
    (work / "task.json").write_text(json.dumps({
        "task_id": "sbfix2-authored", "answer_position": "Sheet!A1"}))
    (work / "answer.txt").write_text("result.xlsx\n")
    frozen = {p.name: p.read_bytes() for p in work.iterdir()}
    move = shutil.move
    attempted_writes = []
    scratch_paths = []

    def readonly_move(source, destination, *args, **kwargs):
        # A chmod is insufficient when tests run with DAC override privileges. Model
        # the actual read-only mount error at the old publication write instead.
        if Path(destination).resolve().is_relative_to(work.resolve()):
            attempted_writes.append(str(destination))
            raise OSError(errno.EROFS, "Read-only file system", str(destination))
        return move(source, destination, *args, **kwargs)

    def converted_with_fresh_cache(cmd, **kwargs):
        assert cmd[0] == "synthetic-soffice"
        source = Path(cmd[-1])
        assert not source.is_relative_to(work)
        scratch_paths.append(source.parent.parent)
        outdir = Path(cmd[cmd.index("--outdir") + 1])
        with zipfile.ZipFile(source) as src, zipfile.ZipFile(
                outdir / source.name, "w") as dst:
            for entry in src.infolist():
                content = src.read(entry)
                if entry.filename == "xl/worksheets/sheet1.xml":
                    assert b"<ns0:v" not in content and b"<v>" not in content
                    content = content.replace(b"</ns0:f>", b"</ns0:f><ns0:v>1</ns0:v>")
                dst.writestr(entry, content)
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(check.shutil, "move", readonly_move)
    monkeypatch.setattr(check, "soffice_path", lambda: "synthetic-soffice")
    monkeypatch.setattr(check.subprocess, "run", converted_with_fresh_cache)
    code = check.main(["--workdir", str(work),
                       "--reward-file", str(tmp_path / "reward.txt"),
                       "--evidence-file", str(tmp_path / "evidence.json")])
    output = capsys.readouterr()
    assert code == (0 if expected == 1 else 1), output.err
    evidence = json.loads((tmp_path / "evidence.json").read_text())
    assert evidence["measured"] is True and evidence["recalculated"] is True
    assert evidence["reward"] == (1.0 if expected == 1 else 0.0)
    assert (tmp_path / "reward.txt").read_text() == ("1\n" if expected == 1 else "0\n")
    assert attempted_writes == []
    assert {p.name: p.read_bytes() for p in work.iterdir()} == frozen
    assert scratch_paths and all(not p.exists() for p in scratch_paths)
