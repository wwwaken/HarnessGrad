"""Reading what a task's run left behind: its trace, and the phase report.

Split out of `eval/runner.py` (stage 4). These four functions are the only place that
reads a trace back, and they were three different concerns of one 1,938-line module:
`_last_identity` and `_last_usage` parse the *last* record of each kind, `_materialize`
puts the harness's own fixture tree in place before it runs, and `_write_progress` writes
the per-task report a reader sees while a round is in flight.

The seam is real rather than cosmetic: nothing here knows what a task *is*, what a
verifier is, or how a score is computed. It moves bytes between the harness's directory and
the platform's, and it reads JSON lines. `eval/runner.py` imports it; it imports nothing
from the runner.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path


def task_file(dest: Path, name: str) -> Path:
    """`dest / name`, with the directories `name` implies created.

    A task id **contains slashes by design** -- `data/qa/base.py`'s is
    `<dataset>/<split>/<n>`, and the comment there says so out loud -- so every file named
    after a task is a *nested* path. `dest.mkdir()` is not enough: it creates
    `verdicts/round-0/` and leaves `verdicts/round-0/gsm8k/train/` missing.

    Measured, and it is the whole reason this function exists: the first real run of a QA
    dataset (`gsm8k`, ids `gsm8k/train/0`) died with
    `FileNotFoundError: .../verdicts/round-0/gsm8k/train/0.json`, and the same task's
    progress record was lost to a warning nobody read (`.../progress/round-0/gsm8k/train/
    0.json`). Every writer of a task-named file goes through here, so the next id shape
    with a slash in it does not have to find all five sites again.
    """
    path = dest / name
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

def _last_identity(trace: str) -> dict | None:
    """The harness's own statement of what ran it, if it made one.

    A harness reads its model configuration from wherever it likes -- our `HG_AGENT_*`
    convention, a CLI's own config file, a flag. The platform only knows the first of
    those, so left to itself it would record `HG_AGENT_MODEL` for a harness that
    ignored it. **This project has already shipped that bug once**: a curve point said
    `agent_model: mock` while a live model answered every task.

    So the harness may declare it, and when it does the declaration is what goes on
    the record -- see `INTERFACE.md` §3. A declaration that disagrees with the
    platform's own environment is not resolved silently in either direction; both
    values are recorded.

    Shape, one JSON object per line in the trace:

        {"harness_identity": {"agent_model": "...", "agent_backend": "...",
                              "harness": "claude-code 2.0.1"}}
    """
    found = None
    for line in trace.splitlines():
        line = line.strip()
        if not line or "harness_identity" not in line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict) and isinstance(event.get("harness_identity"), dict):
            found = event["harness_identity"]      # last one wins
    return found
def _last_usage(trace: str) -> dict | None:
    """The `usage` block a harness wrote into its trace, if it wrote one.

    Last one wins: a harness may report usage incrementally as it goes, and the final
    line is the total. Absent means absent -- a harness that reports nothing gets no
    token count rather than a zero, because a zero that means "not reported" is
    indistinguishable from a real zero and would silently disable a cost rule.
    """
    found = None
    for line in trace.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict) and isinstance(record.get("usage"), dict):
            found = record["usage"]
    return found
def _clear_tree(target: Path) -> None:
    """Remove a directory tree that may be **read-only**, so `copytree` can re-write it.

    Measured, and it is a platform bug rather than a dataset's: `_materialize` runs twice
    per task and its whole promise is that the second run **overwrites** what the first
    wrote. `shutil.copytree(..., dirs_exist_ok=True)` cannot do that for a source whose
    files are read-only -- Java runtimes are shipped with `r--r--r--` for legal files --
    and it fails with `[Errno 13] Permission denied` on every one of them. The failure
    looks like the dataset's, exactly like the ALFWorld namespace fork did
    (`docs/dataset-onboarding-skill.md` §1); the fix belongs here because the next dataset
    with a read-only input would hit it too.

    `chmod` first (a directory that cannot be traversed cannot be emptied), then remove.
    """
    if not target.exists():
        return
    for root, dirs, _files in os.walk(target):
        os.chmod(root, 0o755)
        for name in dirs:
            os.chmod(Path(root) / name, 0o755)
    shutil.rmtree(target, ignore_errors=True)


def _materialize(workdir: Path, entries, platform_root: Path,
                 base: Path | None = None) -> list[str]:
    """Write a dataset's files into `workdir`. Returns the relative paths written.

    Used twice per task, and the two uses are the point of the whole design:

    * **before** the harness runs, to set the task up;
    * **again before verification**, to overwrite anything the harness changed. A task
      whose grade is "run these tests" must not be gradeable by editing the tests, and
      re-writing them is the only way that holds when the harness was free to write
      into the same directory.

    Paths are refused rather than clamped if they escape `workdir`: a `../` silently
    turning into `.` would set up a task whose inputs are not where the dataset said.
    """
    written: list[str] = []
    for entry in entries or []:
        rel = str(entry.get("path") or "")
        if not rel:
            continue
        target = (workdir / rel).resolve()
        if not str(target).startswith(str(workdir.resolve()) + os.sep) \
                and target != workdir.resolve():
            raise ValueError(f"setup path {rel!r} escapes the working directory")
        if "content" in entry and entry["content"] is not None:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(str(entry["content"]))
        elif "from" in entry:
            source = Path(str(entry["from"]))
            if not source.is_absolute():
                source = (base or platform_root) / source
            if not source.exists():
                raise ValueError(f"setup source {source} does not exist")
            if source.is_dir():
                _clear_tree(target)
                shutil.copytree(source, target, dirs_exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
        else:
            continue
        written.append(rel)
    return written
def _write_progress(progress_dir, round_no: int, tid: str,
                    measured: list[dict], unmeasured: dict | None,
                    *, diagnostic: dict | None = None) -> None:
    """Write one task's result the moment it exists, not at the end of the round.

    **Measured, twice, and the second time cost two hours.** A round's results were
    written only after `evaluate` returned -- every trial, every verdict, every trace --
    so a run that was killed lost all of it. Measured: `loop-terminal_bench-41133` and
    `local-floor-5/6` died to the tamper check and discarded their measurements; and
    `screen-all-1` (51 tasks x 3 trials, 2h05m, five containers still running) was killed
    by the environment at 22:42 and left **two files**: `run_meta.json` and a header line.
    Three separate losses from one design choice, and the choice was "the record is the
    thing you write at the end".

    So each task writes itself here as soon as its last trial finishes:

        <run>/progress/round-<N>/<task>.json      score, per-trial scores, verdict,
                                                  the check's test tally, wall clock
        <run>/progress/round-<N>/<task>.trial<i>.jsonl   that trial's trace

    A separate `progress/` directory rather than the final `round<N>_traces/` and
    `verdicts/`: a partial round must not look like a complete one. The end-of-round
    savers remain the authoritative record; these are what survives a kill.

    Never raises. A progress write that fails must not turn a measured task into a
    failed one -- the same rule the teardown helpers follow, for the same reason.
    """
    if progress_dir is None:
        return
    try:
        dest = Path(progress_dir) / "progress" / f"round-{round_no}"
        dest.mkdir(parents=True, exist_ok=True)
        if unmeasured is not None:
            record = {"task_id": tid, "round": round_no, "invalid": unmeasured}
            if diagnostic is not None:
                record["harness_output"] = {
                    "exit_code": diagnostic.get("exit_code"),
                    "stderr": (diagnostic.get("stderr") or "")[-8000:],
                    "harness_runtime": diagnostic.get("harness_runtime"),
                    "model_gateway": diagnostic.get("model_gateway"),
                }
                body = diagnostic.get("trace")
                if body:
                    traces = dest / "traces"
                    traces.mkdir(exist_ok=True)
                    task_file(traces, f"{tid}.invalid.jsonl").write_text(
                        body, encoding="utf-8")
            task_file(dest, f"{tid}.json").write_text(json.dumps(
                record,
                indent=1, ensure_ascii=False), encoding="utf-8")
            return
        scores = [float((r.get("verdict") or {}).get(
            "score", 1.0 if (r.get("verdict") or {}).get("passed") else 0.0))
            for r in measured]
        last = (measured[-1].get("verdict") or {}) if measured else {}
        wall = None
        for line in str((measured[-1] if measured else {}).get("trace") or "").splitlines():
            if '"wall_clock_s"' in line:
                try:
                    wall = json.loads(line)["wall_clock_s"].get("total")
                except (ValueError, AttributeError):
                    pass
        task_file(dest, f"{tid}.json").write_text(json.dumps({
            "task_id": tid, "round": round_no,
            "score": sum(scores) / len(scores) if scores else None,
            "trial_scores": scores, "n_trials": len(scores),
            "passed": last.get("passed"), "kind": last.get("kind"),
            "detail": last.get("detail"),
            "tests": last.get("tests"),
            "wall_clock_s": wall,
            "complete": True,
        }, indent=1, ensure_ascii=False), encoding="utf-8")
        traces = dest / "traces"
        traces.mkdir(exist_ok=True)
        for index, result in enumerate(measured, start=1):
            body = result.get("trace")
            if body:
                task_file(traces, f"{tid}.trial{index}.jsonl").write_text(
                    body, encoding="utf-8")
    except (OSError, ValueError, TypeError) as exc:                      # noqa: BLE001
        print(f"warning: could not write the progress record for {tid}: {exc}",
              file=sys.stderr)
