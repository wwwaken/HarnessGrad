"""Opt-in pinned, artifact-only scorer execution. Never used for snapshot checks.

The Docker observer checks the stopped instance, rather than trusting a declaration
or launch flags. This does not prove transitive image/ABI closure or official origin.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import time
import uuid

from eval.admission import artifact_admission as artifacts
from eval.admission import scorer_bundle as bundles
from eval.admission.pilot_admission import AdmissionError, LOG_CONFIG
from eval.containers import container
from eval.verification.isolation import record_class


def _platform_path(value, actor: Path) -> Path:
    path = Path(value)
    artifacts._root(path)
    path = path.resolve(strict=True)
    if path == actor.resolve() or actor.resolve() in path.parents:
        raise AdmissionError("scorer declarations and closure must be outside actor state")
    return path


def verify(workdir: Path, spec: dict, *, timeout_s: int, task_id: str | None = None) -> dict:
    bundle = spec["scorer_bundle"]
    name = "hg-pristine-" + uuid.uuid4().hex
    actual = "unknown"
    evidence = {}
    attempted = False
    verdict = {"kind": "command", "passed": False, "score": None}
    deadline = time.monotonic() + timeout_s

    def docker(*args):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise subprocess.TimeoutExpired(args, timeout_s)
        return container.docker(*args, timeout=remaining)
    # Exclusive platform-owned storage, never a projection inside actor state.
    with tempfile.TemporaryDirectory(prefix="hg-pristine-") as scratch:
        try:
            raw = _platform_path(bundle["manifest"], workdir).read_bytes()
            pin = bundle["manifest_sha256"]
            root = _platform_path(bundle["root"], workdir)
            manifest = bundles.load_bundle(raw, pin)
            if manifest.get("isolation_class") != "pristine-offline":
                raise AdmissionError("pristine runtime requires explicit pristine-offline bundle")
            if spec.get("argv") != manifest["scorer"]["argv"]:
                raise AdmissionError("verifier command differs from sealed scorer command")
            evidence["bundle"] = bundles.verify_bundle(root, raw, pin)
            contract_raw = _platform_path(bundle["artifact_contract"], workdir).read_bytes()
            contract_pin = bundle["artifact_contract_sha256"]
            contract = bundles.require_contract_bundle(contract_raw, contract_pin, raw, pin)
            if task_id is not None and contract["task_id"] != task_id:
                raise AdmissionError("artifact contract task differs from selected task")
            artifact_root = Path(scratch) / "input"
            exported = artifacts.export_state(workdir, artifact_root, contract_raw, contract_pin,
                                              run_id=name)
            evidence["export"] = exported
            argv = manifest["scorer"]["argv"]
            cmd = ["create", "--pull=never", "--name", name, "--network", "none",
                   "--read-only", "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
                   "--ipc", "private", "--log-driver", LOG_CONFIG["Type"], "--pids-limit", "128",
                   "--memory", "512m", "--cpus", "1", "--workdir", "/tmp",
                   "--entrypoint", argv[0]]
            for env in artifacts.SCORER_ENV:
                cmd += ["--env", env]
            for key, value in LOG_CONFIG["Config"].items():
                cmd += ["--log-opt", f"{key}={value}"]
            for path, options in artifacts.runtime_tmpfs(contract_raw, contract_pin).items():
                cmd += ["--tmpfs", f"{path}:{options}"]
            for source, target in ((artifact_root, "/control-input"), (root, "/control-scorer")):
                if "," in str(source):
                    raise AdmissionError("projection path cannot contain mount option separators")
                cmd += ["--mount", f"type=bind,src={source},dst={target},readonly"]
            cmd += [manifest["runtime_image_id"], *argv[1:]]
            attempted = True
            created = docker(*cmd)
            if created.returncode:
                raise AdmissionError("pristine scorer creation failed")
            inspected = docker("inspect", name)
            if inspected.returncode:
                raise AdmissionError("pristine scorer inspection failed")
            info = json.loads(inspected.stdout)[0]
            evidence["runtime"] = artifacts.require_artifact_runtime(
                info, contract_raw, contract_pin, artifact_root=artifact_root, closure_root=root,
                export_receipt=exported, run_id=name)
            # The client may forward a failing check's exit code. The stopped
            # container's state distinguishes that measured zero from a launch error.
            docker("start", "--attach", name)
            stopped = docker("inspect", name)
            if stopped.returncode:
                raise AdmissionError("pristine scorer result inspection failed")
            state = json.loads(stopped.stdout)[0]["State"]
            if (state["Running"] is not False or state["Status"] != "exited"
                    or state.get("OOMKilled") or state.get("Error")):
                raise AdmissionError("pristine scorer did not finish normally")
            actual = "pristine-offline"
            # This backend's output protocol is the sealed command's exit status.
            # Reward-file and service semantics remain on their existing backend.
            verdict.update(passed=state["ExitCode"] == 0, score=float(state["ExitCode"] == 0),
                           detail=f"sealed scorer exit {state['ExitCode']}")
        except (AdmissionError, OSError, ValueError, KeyError, TypeError, IndexError,
                subprocess.TimeoutExpired) as exc:
            verdict["unmeasured"] = f"pristine scorer unavailable: {exc}"
        finally:
            if attempted:
                try:
                    removed = container.docker("rm", "--force", name, timeout=30)
                    evidence["cleanup"] = {"container": name, "removed": removed.returncode == 0}
                except (OSError, subprocess.TimeoutExpired):
                    evidence["cleanup"] = {"container": name, "removed": False}
                if not evidence["cleanup"]["removed"]:
                    verdict.update(passed=False, score=None, unmeasured="pristine scorer cleanup failed")
    verdict["scorer_isolation_evidence"] = evidence
    return record_class(verdict, spec, actual)
