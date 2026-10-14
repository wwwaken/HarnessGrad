"""Retain every real stopped-network probe until exact Env permits attribution.

No inspected observation is edited. No container is started. Fresh IDs and exclusive
receipt writes preserve every attempt, including any reordered-Env confounder.
"""
import hashlib
import json
import os
from pathlib import Path
import sys
import uuid

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from eval.admission import artifact_admission as artifacts
from eval.admission.pilot_admission import AdmissionError
from eval.containers import container


def save(path, value):
    with path.open("x") as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write("\n")


def main():
    run = Path(sys.argv[1]).resolve()
    change = sys.argv[2] if len(sys.argv) > 2 else "network"
    assert change in ("network", "mount")
    output = run / (change + "-followup")
    output.mkdir(exist_ok=False)
    (output / "probe-executed.py").write_bytes(Path(__file__).read_bytes())
    main_calls = json.loads((run / "evidence/docker-calls.json").read_text())
    create = next(c["argv"][1:] for c in main_calls if c["argv"][1] == "create")
    raw = (run / "platform/contracts/task.json").read_bytes()
    pin = hashlib.sha256(raw).hexdigest()
    summary = []
    for attempt in range(1, 13):
        name = f"hg-wprifix-{change}-{uuid.uuid4().hex}"
        probe = output / f"attempt-{attempt:02d}"
        probe.mkdir()
        exported = artifacts.export_state(run / "actor", probe / "input", raw, pin, run_id=name)
        save(probe / "export.json", exported)
        command = list(create)
        command[command.index("--name") + 1] = name
        if change == "network":
            command[command.index("--network") + 1] = "bridge"
        else:
            extra = probe / "extra"
            extra.mkdir()
            command[1:1] = ["--mount", f"type=bind,src={extra},dst=/unexpected,readonly"]
        for i, arg in enumerate(command):
            if "dst=/control-input" in arg:
                command[i] = f"type=bind,src={probe / 'input'},dst=/control-input,readonly"
        calls = []

        def docker(*args):
            result = container.docker(*args, timeout=30)
            calls.append(dict(argv=list(result.args), returncode=result.returncode,
                              stdout=result.stdout, stderr=result.stderr))
            return result

        record = dict(attempt=attempt, run_id=name, change=change, started=False, score=None)
        try:
            docker(*command).check_returncode()
            inspected = docker("inspect", name)
            inspected.check_returncode()
            info = json.loads(inspected.stdout)[0]
            save(probe / "inspect.json", info)
            # Exact order is required; never normalize or repair an observation.
            record["exact_environment"] = info["Config"]["Env"] == artifacts.SCORER_ENV
            record["network"] = info["HostConfig"]["NetworkMode"]
            try:
                admitted = artifacts.require_artifact_runtime(info, raw, pin,
                    artifact_root=probe / "input", closure_root=run / "platform/scorer/closure",
                    export_receipt=exported, run_id=name)
                record.update(refused=False, admission=admitted)
            except AdmissionError as exc:
                record.update(refused=True, reason=str(exc), exception=type(exc).__name__)
        finally:
            removed = docker("rm", "--force", name)
            record["removed"] = removed.returncode == 0
            absent = docker("inspect", name)
            record["post_removal_inspect_returncode"] = absent.returncode
            save(probe / "commands.json", calls)
            save(probe / "result.json", record)
        summary.append(record)
        if (record.get("exact_environment") and record.get("refused")
                and (change == "network" or record.get("reason") == "artifact-only read-only mounts required")):
            break
    save(output / "summary.json", summary)
    print(json.dumps(dict(output=str(output), attempts=summary), indent=2))


if __name__ == "__main__":
    main()
