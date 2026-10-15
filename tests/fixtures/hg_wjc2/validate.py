"""Capture real commands/output; do not rewrite any inherited evidence packet."""
from pathlib import Path
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
report = ROOT / "reports/w-jc2-validation.txt"
commands = [
    ["python3", "tools/check_dataset_blockers.py"],
    ["python3", str(HERE.relative_to(ROOT) / "bind_inputs.py"), "--check"],
    ["python3", "tests/fixtures/hg_wjc2/fever/audit.py", "--check"],
    ["python3", "tests/fixtures/hg_wjc2/gym/verify.py"],
    ["python3", "tests/fixtures/hg_wjc2/spread/audit.py", "--check"],
    ["python3", "tests/fixtures/hg_wjc2/spread/verify_preimages.py"],
    ["python3", "tests/fixtures/hg_wjournalcov/audit.py", "--check"],
    ["python3", str(HERE.relative_to(ROOT) / "check_scope.py")],
    ["python3", "-c", "import json,pathlib; p=pathlib.Path('tests/fixtures/hg_wjc2/source-links.json'); x=json.loads(p.read_text()); assert all(pathlib.Path(v['path']).read_text().splitlines()[v['line']-1]==v['verbatim'] for v in x); print(json.dumps({'source_anchors_valid':True,'anchors':x},indent=2))"],
    ["sha256sum", "-c", "tests/fixtures/hg_wjc2/SHA256SUMS"],
    ["sha256sum", "reports/w-jc2-review.md", "docs/dataset-blockers.json",
     "docs/adapter-integration-journal.md"],
    ["git", "diff", "--check"],
    ["git", "diff", "--cached", "--check"],
    ["git", "status", "--short"],
]

failed = []
with report.open("w") as out:
    out.write("w-jc2 final parent validation; raw subprocess stdout/stderr follow.\n")
    for i, argv in enumerate(commands):
        result = subprocess.run(argv, cwd=ROOT, capture_output=True,
                                env={**__import__('os').environ, "PYTHONDONTWRITEBYTECODE": "1"})
        out.write("\nARGV " + json.dumps(argv) + "\nSTDOUT\n")
        out.write(result.stdout.decode(errors="replace"))
        out.write("\nSTDERR\n" + result.stderr.decode(errors="replace"))
        out.write("\nEXIT " + str(result.returncode) + "\n")
        out.flush()
        print(i, result.returncode, " ".join(argv[:4]), flush=True)
        if result.returncode:
            failed.append(i)
    captured = json.loads((HERE / "focused-tests.command.json").read_text())
    out.write("\nFOCUSED TESTS (captured after final registry observation edit)\nARGV " + json.dumps(captured["argv"]) + "\nSTDOUT\n")
    out.write((HERE / "focused-tests.stdout.txt").read_text())
    out.write("\nSTDERR\n" + (HERE / "focused-tests.stderr.txt").read_text())
    out.write("\nEXIT " + str(captured["returncode"]) + "\n")
    if captured["returncode"]:
        failed.append("focused-tests")
    out.write("\n" + json.dumps({"failed_command_indices": failed, "valid": not failed}) + "\n")
sys.exit(bool(failed))
