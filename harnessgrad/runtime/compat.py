"""Compatibility adapter for the historical one-shot method contract.

The adapter is intentionally observational.  It invokes an old entrypoint once,
preserves its single JSON response, and writes a protocol event stream beside
the legacy trajectory.  Missing phase semantics are marked ``custom`` /
``unverified`` and ``unobserved``; no event is inferred from ``changed``.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from .events import ArtifactKind, Evidence, EventRecorder, ImplementationMode, Lifecycle, Owner, Scope, Stage, StageID, artifact, sha256_bytes


@dataclass(frozen=True)
class LegacyRun:
    response: dict[str, Any]
    stdout: str
    stderr: str
    returncode: int
    trajectory: Any | None
    events: tuple[dict[str, Any], ...]


def _read_json(path: str | Path | None) -> Any | None:
    if not path: return None
    try: return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError): return None


class LegacyCompatibilityWrapper:
    """Run a legacy method and emit typed sidecar events."""

    def __init__(self, entrypoint: Sequence[str], *, timeout: float = 3600,
                 event_stream: str | Path | None = None, env: Mapping[str, str] | None = None) -> None:
        if not entrypoint: raise ValueError("entrypoint is empty")
        self.entrypoint, self.timeout = list(entrypoint), timeout
        self.event_stream, self.env = event_stream, dict(env or {})

    def run(self, request: Mapping[str, Any]) -> LegacyRun:
        req = dict(request)
        run_id = str(req.get("run_id") or "legacy-run")
        session_id = str(req.get("session_id") or "legacy-session")
        owner = Owner("method", str(req.get("method_id") or "legacy-method"))
        recorder = EventRecorder(run_id, session_id, producer=Owner("recorder", "compatibility-wrapper"), stream=self.event_stream)
        recorder.bootstrap(profile_opt_in="legacy.compatibility.v1", evidence_mode="declared_traces",
            stage_modes={stage.value: "custom" for stage in StageID},
            task_set_sha=req.get("task_set_sha") or sha256_bytes(json.dumps(req.get("task_ids", []), sort_keys=True)),
            budget={"unit": "generations", "limit": 1})
        request_bytes = json.dumps(req, sort_keys=True, ensure_ascii=False).encode()
        legacy_art = artifact("legacy-response-" + run_id, ArtifactKind.LEGACY_RESPONSE,
            request_bytes, producer=Owner("recorder", "compatibility-wrapper"), visibility="public_record",
            content_kind="none")
        scope = Scope(run_id, session_id, str(req.get("iteration_id") or "iteration-0"), str(req.get("branch_id") or "main"))
        response_art = None; stdout = stderr = ""; returncode = 1
        try:
            env = os.environ.copy(); env.update(self.env)
            proc = subprocess.run(self.entrypoint, input=json.dumps(req), text=True,
                                  capture_output=True, timeout=self.timeout, env=env,
                                  cwd=req.get("cwd") or None, check=False)
            stdout, stderr, returncode = proc.stdout, proc.stderr, proc.returncode
            try: response = json.loads(stdout) if stdout.strip() else {}
            except ValueError: response = {"legacy_parse_error": True}
        except subprocess.TimeoutExpired as exc:
            stdout, stderr, returncode = exc.stdout or "", exc.stderr or "", 124
            response = {"legacy_timeout": True}
        trajectory_path = req.get("trajectory_out")
        trajectory = _read_json(trajectory_path)
        response_bytes = json.dumps({"response": response, "stdout": stdout, "stderr": stderr,
                                     "returncode": returncode}, sort_keys=True, ensure_ascii=False).encode()
        response_art = artifact("legacy-response-data-" + run_id, ArtifactKind.LEGACY_RESPONSE, response_bytes,
            producer=Owner("recorder", "compatibility-wrapper"), visibility="public_record", parents=(legacy_art.artifact_id,), content_kind="none")
        recorder.record(scope=scope, stage=Stage(StageID.PROPOSE_CHANGES, "legacy-proposal", ImplementationMode.CUSTOM),
            payload={"payload_kind": "proposal", "candidate_ids": [], "artifact_kind": "none", "hypothesis": "legacy output is not a typed proposal"},
            owner=owner, producer=owner, implementation={"module": "legacy.compatibility", "compliance": "unverified", "fidelity": "unknown"},
            evidence=Evidence.UNOBSERVED, input_artifacts=[legacy_art], output_artifacts=[response_art], artifacts=[legacy_art, response_art],
            reason="legacy_entrypoint_boundary", claims={"legacy_changed": response.get("changed"), "legacy_steps": response.get("steps")})
        # An old response cannot establish selection or deployment.  Empty result
        # events make the missing semantic boundary explicit for downstream readers.
        for stage in (StageID.SELECT_CONTEXT, StageID.EXECUTE, StageID.ORGANIZE_FEEDBACK,
                      StageID.BUILD_VALIDATE, StageID.EVALUATE_CANDIDATES, StageID.SELECT_DEPLOY, StageID.STOP_CONTINUE):
            recorder.record(scope=scope, stage=Stage(stage, f"legacy-{stage.value}", ImplementationMode.CUSTOM),
                payload={"payload_kind": "empty_result", "reason": "legacy_unobserved"},
                owner=owner, producer=Owner("recorder", "compatibility-wrapper"),
                implementation={"module": "legacy.compatibility", "compliance": "unverified", "fidelity": "unknown"},
                evidence=Evidence.UNOBSERVED, reason="legacy_unobserved", claims={"legacy_boundary": True})
        return LegacyRun(response, stdout, stderr, returncode, trajectory, recorder.events)


def run_legacy(entrypoint: Sequence[str], request: Mapping[str, Any], **kwargs: Any) -> LegacyRun:
    return LegacyCompatibilityWrapper(entrypoint, **kwargs).run(request)
