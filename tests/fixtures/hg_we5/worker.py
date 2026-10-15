#!/usr/bin/env python3
"""Actual local scorer entrypoints on authored states; never load benchmark rows."""
from __future__ import annotations

import contextlib
import importlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


def main():
    request = json.loads(Path(sys.argv[1]).read_text())
    state, private = Path(request["state"]), Path(request["private"])
    output = Path(request["output"])
    output.mkdir()
    reads = []

    def audit(event, args):
        if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
            path = Path(os.fsdecode(args[0])).absolute()
            if path.is_relative_to(state) or path.is_relative_to(private):
                reads.append({"path": str(path), "mode": args[1], "flags": args[2]})

    sys.addaudithook(audit)
    os.chdir(state)
    reward, evidence = output / "reward.txt", output / "evidence.json"
    common = ["--reward-file", str(reward), "--evidence-file", str(evidence)]
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        if request["kind"] == "qa":
            from data.scaffolds.qa import base
            # Only import-time pool construction is suppressed. Real score functions,
            # validation, binding and entrypoint dispatch are unchanged.
            with patch.object(base.QASpec, "records", return_value=[]):
                adapter = importlib.import_module("data.datasets." + request["dataset"])
            from data.scaffolds.qa.verify.check import main as check
            argv = ["--dataset", request["dataset"], "--answer", "answer.txt",
                    "--prediction", "prediction.json", "--gold", str(private / "gold.json"),
                    "--task-id", request["task_id"], "--gold-sha256", request["gold_sha256"],
                    *common]
            native_spec = json.loads((private / "authored-verifier.json").read_text())
            if "--score-mode" in native_spec["argv"]:
                index = native_spec["argv"].index("--score-mode")
                argv += ["--score-mode", native_spec["argv"][index + 1]]
            if "--redact-gold" in native_spec["argv"]:
                argv.append("--redact-gold")
            code = check(argv)
        else:
            path = ROOT / "data/datasets" / request["dataset"] / "verify/check.py"
            spec = importlib.util.spec_from_file_location("actual_check", path)
            adapter = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(adapter)
            if request["kind"] == "sql":
                argv = ["--db", str(private / "db.sqlite"), "--gold", str(private / "gold.sql"),
                        "--pred", "answer.sql", *common]
                sys.argv = [str(path), *argv]
                code = adapter.main()
            else:
                argv = ["--workdir", str(state), "--golden", str(private / "golden.xlsx"),
                        "--task", str(private / "task.json"), *common]
                code = adapter.main(argv)
    result = {"argv": argv, "returncode": code, "stdout": stdout.getvalue(),
              "stderr": stderr.getvalue(), "evidence": json.loads(evidence.read_text()),
              "reward_text": reward.read_text() if reward.exists() else None,
              "state_reads": reads, "adapter_file": str(Path(adapter.__file__).resolve())}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
