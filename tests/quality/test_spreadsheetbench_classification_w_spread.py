"""Synthetic checker/admission regressions; no dataset payload or external runtime."""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys

import openpyxl
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from eval.run import runner
from eval.verification import verifier


def _module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CASES = [
    ("unparseable-range", None, "not a cell range"),
    ("golden-load", None, "workbook load failed"),
    ("result-load", None, "workbook load failed"),
    ("formula-probe-load", None, "formula detection"),
    ("comparator-exception", None, "synthetic comparator failure"),
    ("formula-no-runtime", None, "no LibreOffice"),
    ("recalc-timeout", None, "LibreOffice timed out"),
    ("recalc-exit", None, "LibreOffice exited 7"),
    ("recalc-no-output", None, "LibreOffice produced no file"),
    ("recalc-launch", None, "LibreOffice recalculation"),
    ("recalc-copy", None, "LibreOffice recalculation"),
    ("golden-sheet-absent", None, "comparison"),
    ("mismatch", 0.0, "value difference"),
    ("result-sheet-absent", 0.0, "not found in the result"),
    ("result-absent", 0.0, "no such file exists"),
    ("match", 1.0, "reference values"),
]


@pytest.fixture(params=CASES, ids=[c[0] for c in CASES])
def scenario(request, monkeypatch, tmp_path):
    case, score, reason = request.param
    check = _module("spreadsheet_check_w_spread",
                    ROOT / "data/datasets/spreadsheetbench/verify/check.py")
    # Import the adapter against an empty synthetic root, never the installed mirror.
    monkeypatch.setenv("HG_SPREADSHEETBENCH_DATA", str(tmp_path / "empty-data"))
    adapter = _module("spreadsheet_adapter_w_spread", ROOT / "data/datasets/spreadsheetbench.py")
    work = tmp_path / "work"
    work.mkdir()
    golden = tmp_path / "reference.xlsx"
    wb = openpyxl.Workbook()
    wb.active.title = "S"
    wb.active["A1"] = 1
    wb.save(golden)
    if case == "mismatch":
        wb.active["A1"] = 2
    elif case.startswith("recalc-") or case == "formula-no-runtime":
        wb.active["A1"] = "=1"
    if case == "result-sheet-absent":
        wb.active.title = "Other"
    if case != "result-absent":
        wb.save(work / "result.xlsx")
    wb.close()
    if case == "golden-load":
        golden.write_bytes(b"synthetic unreadable workbook")
    if case == "result-load":
        (work / "result.xlsx").write_bytes(b"synthetic unreadable workbook")
    position = ("S!A:G" if case == "unparseable-range" else
                "Absent!A1" if case == "golden-sheet-absent" else "S!A1")
    record = {"task_id": "synthetic-spread", "golden_path": golden,
              "instruction_type": "", "answer_position": position}
    spec = adapter._verifier(record)
    (work / "task.json").write_text(json.dumps(record, default=str))
    (work / "golden.xlsx").write_bytes(golden.read_bytes())
    if case == "formula-probe-load":
        load = openpyxl.load_workbook

        def probe_load(*args, **kwargs):
            if kwargs.get("data_only") is False:
                raise OSError("synthetic formula probe load failure")
            return load(*args, **kwargs)

        monkeypatch.setattr(openpyxl, "load_workbook", probe_load)
    if case == "comparator-exception":
        def broken_compare(*args, **kwargs):
            raise RuntimeError("synthetic comparator failure")
        monkeypatch.setattr(check, "compare_workbooks", broken_compare)
    monkeypatch.setattr(check, "soffice_path",
                        lambda: None if case == "formula-no-runtime" else "synthetic-soffice")

    def denied(*args, **kwargs):
        pytest.fail("unexpected external runtime launch")

    monkeypatch.setattr(verifier.sandbox_mod, "run", denied)
    monkeypatch.setattr(verifier.container_mod, "run", denied)
    monkeypatch.setattr(verifier.container_mod, "create", denied)

    def invoke(argv):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                code = check.main(argv)
            except Exception:
                # Match check.py's __main__ crash exit, so pre-fix missing evidence is tested.
                code = 4
        return subprocess.CompletedProcess(["synthetic-check"], code,
                                           stdout.getvalue(), stderr.getvalue())

    def synthetic_process(cmd, **kwargs):
        if cmd[0] == "synthetic-soffice":
            if case == "recalc-timeout":
                raise subprocess.TimeoutExpired(cmd, 180)
            if case == "recalc-launch":
                raise OSError("synthetic LibreOffice launch failure")
            if case == "recalc-copy":
                # A produced but unreadable conversion makes the move fail locally.
                outdir = Path(cmd[cmd.index("--outdir") + 1])
                (outdir / "result.xlsx").symlink_to(outdir / "absent-conversion")
                monkeypatch.setattr(check.shutil, "move", denied_move)
                # is_file must pass before the deliberately failed move.
                (outdir / "absent-conversion").write_bytes(b"synthetic conversion")
            return subprocess.CompletedProcess(cmd, 7 if case == "recalc-exit" else 0,
                                               "", "synthetic recalculation stderr")
        assert cmd[:2] == ["python3", "check.py"], cmd
        assert (Path(kwargs["cwd"]) / "check.py").read_bytes() == (
            ROOT / "data/datasets/spreadsheetbench/verify/check.py").read_bytes()
        argv = list(cmd[2:])
        argv[argv.index("--workdir") + 1] = str(kwargs["cwd"])
        for flag in ("--reward-file", "--evidence-file"):
            i = argv.index(flag) + 1
            argv[i] = str(Path(kwargs["cwd"]) / argv[i])
        return invoke(argv)

    def denied_move(*args, **kwargs):
        raise OSError("synthetic conversion copy failure")

    monkeypatch.setattr(verifier.subprocess, "run", synthetic_process)
    return check, work, spec, score, reason, invoke


def test_checker_classifies_failures_and_completed_comparisons(scenario):
    check, work, spec, score, reason, invoke = scenario
    proc = invoke(["--workdir", str(work), "--reward-file", str(work / "reward.txt"),
                   "--evidence-file", str(work / "evidence.json")])
    evidence = json.loads((work / "evidence.json").read_text())
    if score is None:
        assert proc.returncode == 3
        assert evidence["measured"] is False
        assert reason in evidence["error"]
        assert not {"score", "reward", "correct"}.intersection(evidence)
        assert not (work / "reward.txt").exists()
    else:
        assert proc.returncode == (0 if score else 1)
        assert evidence["measured"] is True
        assert evidence["score"] == evidence["reward"] == score
        assert reason in evidence["why"]
        assert float((work / "reward.txt").read_text()) == score


def test_classification_survives_verifier_persistence_and_aggregation(
        scenario, monkeypatch, tmp_path):
    check, work, spec, score, reason, invoke = scenario
    verdict = verifier._verify(work, spec, "", sandbox=False, timeout_s=300,
                               env={"kind": "files"})
    monkeypatch.setattr(runner, "run_one", lambda *a, **k: {
        "verdict": verdict, "trace": "synthetic trace\n", "exit_code": 0, "stderr": ""})
    cache = {}
    result = runner._evaluate(
        tmp_path, [{"task_id": "synthetic-spread"}], {}, cache=cache,
        trials=1, jobs=1, progress_dir=tmp_path, round_no=0)
    persisted = json.loads((tmp_path / "progress/round-0/synthetic-spread.json").read_text())
    if score is None:
        assert reason in verdict["unmeasured"]
        assert result["per_task"] == result["per_task_trials"] == {}
        assert result["trial_verdicts"] == result["verdicts"] == {}
        assert result["invalid"]["synthetic-spread"]["stage"] == "check"
        assert reason in persisted["invalid"]["detail"]
        assert not {"score", "trial_scores", "complete"}.intersection(persisted)
        assert cache == {}
    else:
        assert "unmeasured" not in verdict
        assert result["per_task"] == {"synthetic-spread": score}
        assert result["invalid"] == {}
        assert persisted["complete"] is True and persisted["score"] == score
        assert len(cache) == 1
