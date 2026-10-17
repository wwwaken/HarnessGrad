"""Start a dataset's host-side environment for ONE task, and stop it again.

This is the runner-side half of the tool relay. A dataset that has an interaction environment
declares it in its `SETUP` with a `tool_relay` key::

    "tool_relay": {
        "program": "<absolute path to the dataset's relay program>",
        "content": "<the environment's own bytes, e.g. a game file>",
        # or "content_path": "<a file the runner copies here at start>"
        "budget":  50,               # optional
    }

`_setup` builds that declaration per task because the content is per task. It is **not** part of
`SETUP["files"]`, so it is never materialised into the agent's working directory: it goes to a
`0700` directory this module owns, outside the work root, and the only reader is the relay
process started here. The agent gets the socket (`eval/containers/tool_route.py` mounts it
read-only at `/run/harnessgrad-tool/tool.sock`) and can ask, never read.

**Two failure modes, and why they are not a zero.** A relay that never came up, died mid-episode,
or left no receipt means the task was not measured: the agent may have been calling into a hole.
`ToolRelay.fault()` reports that, and the runner turns it into `_invalid(..., stage="tool relay")`
rather than letting a truncated episode be scored as a bad answer. A tool call that the
*environment* rejected is a different thing entirely: it is a normal measured step, and it never
appears as a fault here.
"""
from __future__ import annotations

import json
import os
import shutil
import socket as socket_mod
import subprocess
import sys
import tempfile
import time
from pathlib import Path

#: Fixed destination the sandbox mounts the socket at. Kept in step with
#: `eval/containers/tool_route.py`, which publishes it; a dataset never chooses this.
TOOL_SOCKET = "/run/harnessgrad-tool/tool.sock"

#: How long a relay may take to bind before the task is called unmeasured.
READY_TIMEOUT_S = 60.0


class ToolRelay:
    """One task's environment process. Use as a context manager."""

    def __init__(self, path: Path, directory: Path, proc: subprocess.Popen,
                 receipt_path: Path, log_path: Path):
        self.path = path
        self.directory = directory
        self.proc = proc
        self.receipt_path = receipt_path
        self.log_path = log_path
        self.faults: list[str] = []
        self.receipt: dict | None = None

    def __enter__(self) -> "ToolRelay":
        return self

    def __exit__(self, *exc_info) -> None:
        self.stop()

    def stop(self) -> None:
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                try:
                    self.proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.faults.append("relay did not exit after SIGKILL")
        code = self.proc.returncode
        # SIGTERM is how this module stops a healthy relay, so 0 and -15 are both normal.
        if code not in (0, -15):
            self.faults.append(f"relay exited {code}: {self._tail()}")
        try:
            self.receipt = json.loads(self.receipt_path.read_text())
        except (OSError, ValueError):
            self.faults.append("relay wrote no receipt, so its call count is unknown")

    def _tail(self, limit: int = 800) -> str:
        try:
            return self.log_path.read_text(errors="replace")[-limit:]
        except OSError:
            return "(no log)"

    def fault(self) -> str | None:
        """`None` when the episode was measured against a live environment."""
        return "; ".join(self.faults) if self.faults else None

    def cleanup(self) -> None:
        shutil.rmtree(self.directory, ignore_errors=True)


def declaration(setup: dict | None) -> dict | None:
    return (setup or {}).get("tool_relay")


def start(setup: dict | None, *, ready_timeout_s: float = READY_TIMEOUT_S) -> ToolRelay | None:
    """Start the relay `setup` declares, or return `None` for a task that needs none.

    A declared relay that cannot start raises `RuntimeError` rather than returning `None`:
    "this dataset needs an environment" and "this dataset has none" must not be the same
    answer, because the first one silently rewards an agent that was never measured.
    """
    decl = declaration(setup)
    if not decl:
        return None
    program = Path(decl["program"])
    if not program.is_file():
        raise RuntimeError(f"tool relay program is missing: {program}")

    directory = Path(tempfile.mkdtemp(prefix="hg-toolrelay-"))
    os.chmod(directory, 0o700)
    state = directory / "state"
    state.mkdir(mode=0o700)
    # The staged file keeps the name the environment expects. TextWorld guesses the world
    # format from the extension, so a file called `environment` is not a `.tw-pddl` and the
    # relay dies at startup -- which the runner then reports as an unmeasured task.
    payload = state / decl.get("filename", "environment")
    if "content" in decl:
        payload.write_text(decl["content"], encoding="utf-8")
    else:
        # `content_path` is for a dataset whose `SETUP` must not read the file: it hands the
        # path and the runner copies it here, so the relay still gets a private copy and the
        # agent still gets nothing.
        payload.write_text(Path(decl["content_path"]).read_text(), encoding="utf-8")
    os.chmod(payload, 0o600)
    sock = directory / "tool.sock"
    receipt_path = directory / "receipt.json"
    log_path = directory / "relay.log"

    # A dataset may need its own interpreter: AgentDojo's environment imports the task suite and
    # the attacks, which live in the dataset's provisioned runtime and not in the driver's python.
    argv = [str(decl.get("python") or sys.executable), str(program), "--socket", str(sock),
            "--receipt", str(receipt_path)]
    # The program names its own input flag; `content_flag` defaults to `--game` because that
    # is what the first migrated dataset uses, and a second dataset states its own.
    argv += [decl.get("content_flag", "--game"), str(payload)]
    for flag, key in (("--budget", "budget"), ("--deadline-s", "deadline_s"),
                      ("--max-calls", "max_calls")):
        if decl.get(key) is not None:
            argv += [flag, str(decl[key])]

    log = log_path.open("w")
    try:
        proc = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL, start_new_session=True)
    finally:
        log.close()

    handle = ToolRelay(sock, directory, proc, receipt_path, log_path)
    deadline = time.monotonic() + ready_timeout_s
    while True:
        if proc.poll() is not None:
            handle.faults.append(f"relay exited during startup: {handle._tail()}")
            raise RuntimeError(handle.fault())
        if sock.exists():
            probe = socket_mod.socket(socket_mod.AF_UNIX, socket_mod.SOCK_STREAM)
            probe.settimeout(2.0)
            try:
                probe.connect(str(sock))
                return handle
            except OSError:
                pass
            finally:
                probe.close()
        if time.monotonic() > deadline:
            handle.stop()
            handle.faults.append(f"relay did not accept a connection within {ready_timeout_s}s")
            raise RuntimeError(handle.fault())
        time.sleep(0.05)
