#!/usr/bin/env python3
"""DS-1000 official command check.

This is the released `test_ds1000.py` construction copied into the verification namespace:
`code_context + code=<candidate> + test_execution(code)`, plus `test_string(code)` only
when the context declares that helper. `execution.py` is re-materialized as VERIFY.input
and runs the candidate in its own child process with the upstream 120-second timeout.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
import tempfile


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reward-file", default="verifier/reward.txt")
    ap.add_argument("--evidence-file", default="verifier/evidence.json")
    args = ap.parse_args()
    work = pathlib.Path.cwd()
    task = json.loads((work / "context.json").read_text(encoding="utf-8"))
    solution = work / "solution.py"
    candidate = solution.read_text(encoding="utf-8") if solution.is_file() else ""
    program = (task["code_context"] + "\n" + f"code = {candidate!r}\n"
               + "test_execution(code)\n"
               + ("test_string(code)\n" if "test_string(" in task["code_context"] else ""))
    # Keep this checker dependency-free: execution.py is a VERIFY input, and the candidate
    # program is passed via a temporary JSON file so the child can import the official runner.
    scratch = pathlib.Path(tempfile.mkdtemp(prefix="ds1000-check-"))
    runner = scratch / "run_ds1000.py"
    (scratch / "execution.py").write_text((work / "execution.py").read_text(encoding="utf-8"), encoding="utf-8")
    runner.write_text(
        "import json, sys\n"
        "from execution import check_correctness\n"
        "program=json.loads(open(sys.argv[1]).read())\n"
        "print(json.dumps(check_correctness(program, timeout=120)))\n",
        encoding="utf-8")
    payload = scratch / "program.json"
    payload.write_text(json.dumps(program), encoding="utf-8")
    # 14 official Matplotlib rows call `sns.load_dataset(...)`. seaborn resolves that from
    # `$SEABORN_DATA/<name>.csv`; the four CSVs are a VERIFY input, so the official code
    # path runs offline instead of fetching from GitHub mid-check.
    import os
    env = dict(os.environ)
    env["SEABORN_DATA"] = str(work / "seaborn-data")
    for noisy in ("MPLBACKEND",):
        env.setdefault(noisy, "Agg")
    proc = subprocess.run([sys.executable, str(runner), str(payload)], cwd=scratch,
                          capture_output=True, text=True, timeout=130, env=env)
    result = json.loads(proc.stdout.strip().splitlines()[-1]) if proc.returncode == 0 and proc.stdout.strip() else {"passed": False, "result": proc.stderr[-500:]}
    reward = 1.0 if result.get("passed") else 0.0
    out = work / args.reward_file
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(f"{reward:g}\n")
    ev = work / args.evidence_file
    ev.parent.mkdir(parents=True, exist_ok=True)
    ev.write_text(json.dumps({"measured": True, "reward": reward,
                              "official": {"metric": "DS-1000 test_execution plus conditional test_string",
                                            "result": result.get("result")},
                              "why": result.get("result", "")}, sort_keys=True) + "\n")
    print(f"reward {reward:g}: {result.get('result', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
