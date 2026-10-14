"""Copy the completed external run without changing any original receipt."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from eval.policy import diagnostic_policy as policy

RUN = Path(json.loads((OUT / "launch-output.txt").read_text().splitlines()[0])["run_dir"])


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    with (OUT / name).open("x") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")


result = json.loads((RUN / "task-result.json").read_text())
staged = json.loads((RUN / "diagnostic_receipt.json").read_text())
policy.validate_receipt(staged)
shutil.copytree(RUN, OUT / "execution")
inventory = []
for source in sorted(RUN.rglob("*")):
    if not source.is_file():
        continue
    relative = source.relative_to(RUN)
    copy = OUT / "execution" / relative
    assert source.read_bytes() == copy.read_bytes()
    inventory.append(dict(source=str(source), copy=str(copy.relative_to(ROOT)),
                          relative_path=str(relative), bytes=source.stat().st_size,
                          sha256=sha(source)))
write("artifact-inventory.json", inventory)
archive = OUT / "run-artifacts.tar.gz"
with tarfile.open(archive, "x:gz") as bundle:
    bundle.add(RUN, arcname=RUN.name)
with tarfile.open(archive) as bundle:
    for entry in inventory:
        data = bundle.extractfile(RUN.name + "/" + entry["relative_path"]).read()
        assert len(data) == entry["bytes"]
        assert hashlib.sha256(data).hexdigest() == entry["sha256"]
write("archive-sha256.json", dict(path=str(archive.relative_to(ROOT)),
                                 bytes=archive.stat().st_size, sha256=sha(archive)))
raw = json.loads((RUN / "raw-controller-outcomes.json").read_text())
write("raw-controller-summary.json", dict(
    source=str(RUN / "raw-controller-outcomes.json"),
    interpretation="Controller outcomes before policy publication gating; not a staged policy receipt.",
    **policy.measurement_summary(staged["selected_task_ids"], raw)))
write("integrity-audit.json", dict(
    original_copy_archive_files_checked=len(inventory),
    all_copies_and_archive_match=True,
    policy_manifest_matches=staged["context"]["hashes"]["manifest"] == sha(RUN / "launch/manifest.json"),
    launch_source_matches=sha(OUT / "launch.py") == sha(RUN / "launch/launch.py"),
    actor_trace_matches=result["trace"] == (RUN / "actor-trace.jsonl").read_text(),
    platform_diff=json.loads((RUN / "launch/platform-diff.json").read_text())))
print((OUT / "integrity-audit.json").read_text())
