"""Write exact offline validation commands and combined outputs to the owned report."""
from datetime import datetime, timezone
import os
from pathlib import Path
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / "reports/w-prov-validation.txt"
COMMANDS = [
    ["python3", "tests/fixtures/hg_wprov/verify.py"],
    ["python3", "tests/fixtures/hg_wprov/build_custody.py", "--check"],
    ["python3", "tests/fixtures/hg_wprov/rewoo/verify.py"],
    ["python3", "tests/fixtures/hg_wprov/reasoning_gym/verify.py"],
    ["python3", "tests/fixtures/hg_wprov/check_registry_scope.py"],
    ["python3", "tools/check_dataset_blockers.py"],
    ["python3", "-m", "pytest", "tests/quality/test_dataset_blockers.py", "-q",
     "--basetemp=/tmp/harnessgrad-pytest-w-prov"],
    ["git", "-c", "core.whitespace=-blank-at-eof,cr-at-eol", "diff", "--check",
     "0b470b6dd6e1935a20016cf42b3e78d510c8d85c"],
]
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
REPORT.parent.mkdir(exist_ok=True)
failed = False
with REPORT.open("w") as output:
    output.write("w-prov independent parent validation\n")
    output.write("UTC: " + datetime.now(timezone.utc).isoformat() + "\n")
    output.write("cwd: " + str(ROOT) + "\n")
    output.write("Offline evidence checks only; no regeneration/scoring/model/GPU/pilot.\n")
    output.write("Whitespace check preserves raw response header endings and CRLF evidence bytes.\n")
    output.write("Historical bounded regeneration commands/stdout/stderr, including failed attempts, "
                 "are preserved in tests/fixtures/hg_wprov/reasoning_gym/.\n\n")
    for command in COMMANDS:
        output.write("$ PYTHONDONTWRITEBYTECODE=1 " + shlex.join(command) + "\n")
        output.flush()
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True)
        output.write(result.stdout)
        if result.stdout and not result.stdout.endswith("\n"):
            output.write("\n")
        output.write("[exit " + str(result.returncode) + "]\n\n")
        failed |= result.returncode != 0
    # Preserve the completed provenance attempt's output without rerunning the
    # generator. Its expected mismatch is a finding, not a passing seed proof.
    import json
    directory = ROOT / "tests/fixtures/hg_wprov/reasoning_gym"
    raw_stdout = (directory / "attempt-5.stdout.txt").read_text()
    receipt = json.loads(raw_stdout)
    output.write("HISTORICAL COMPLETED PROVENANCE ATTEMPT (not rerun by validation)\n")
    output.write("$ " + receipt["command"] + "\n")
    output.write("Exact script: tests/fixtures/hg_wprov/reasoning_gym/attempt-5-script.py\n")
    output.write("[stdout]\n" + raw_stdout)
    output.write("[stderr]\n" + (directory / "attempt-5.stderr.txt").read_text())
    output.write("[exit 1: whole-pool equality false; retained provenance gap]\n\n")
    output.write("ALL CHECKS PASSED\n" if not failed else "VALIDATION HAS FAILURES\n")
print(str(REPORT))
raise SystemExit(1 if failed else 0)
