"""Read-only access to a HarnessGrad ``runs/`` tree.

Everything here is a *reader*.  No function opens a file for writing, creates a
directory, moves or deletes anything; the API is an observer of a tree that a
long-running driver is still appending to.

Two consequences follow from that, and both are deliberate:

* ``certify()`` comes from ``harnessgrad/store/schema.py`` -- the authority -- and
  is imported rather than reimplemented, because a second copy of "what a curve
  point is" would drift from the first.
* Every read tolerates a half-written file.  A ``curve.jsonl`` line that is not
  yet complete JSON, a ``run_meta.json`` captured mid-write, a trace file whose
  last line lost the race: each becomes a **problem string** on the response, not
  an exception.  The runs being served are being written while they are served.

The three-state rule from ``schema.py`` is preserved: a field that is absent, a
field that is explicitly ``null`` ("the platform looked and found nothing") and a
field that is ``0`` are three different facts, and nothing here collapses them.
"""
from __future__ import annotations

import datetime as _dt
import json
import re
import sys
from pathlib import Path
from typing import Any

# The platform's schema is the authority for what a run directory *is*.  Resolve
# the repository root from this file (``web/server/readapi.py`` -> repo) so the
# server can be started from any working directory without writing anything.
REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from harnessgrad.store.schema import certify as _certify  # noqa: E402
from harnessgrad.store.schema import read_curve  # noqa: E402

#: A single path component: a run id or a task id.  The first character may not
#: be a dot, so ``.`` and ``..`` are refused by construction; ``..`` is refused
#: again explicitly below, and ``/`` can never match.
_COMPONENT_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9._-]*$")
_ROUND_DIR_RE = re.compile(r"^round-(\d+)$")
_DIFF_STAT_RE = re.compile(r"^round-(\d+)\.json$")


# ---------------------------------------------------------------------------
# Guards and primitive reads
# ---------------------------------------------------------------------------

def is_safe_component(name: str) -> bool:
    """Is ``name`` safe to join onto a directory as a single component?

    Rejects empty strings, ``.``/``..``, anything containing ``/`` or ``\\`` and
    anything starting with a dot.  This is the directory-traversal guard: the
    raw URL component is tested *before* any path is built.
    """
    if not isinstance(name, str) or not name:
        return False
    if ".." in name or "/" in name or "\\" in name:
        return False
    return bool(_COMPONENT_RE.match(name))


def _read_text(path: Path) -> str | None:
    """File text, or ``None`` when it cannot be read.

    ``errors="replace"`` is load-bearing: a writer appending multi-byte UTF-8 can
    be caught between the bytes, and a ``UnicodeDecodeError`` here would turn a
    live run into a 500.  A replaced character makes the enclosing JSON line fail
    to parse, which is reported as a problem -- the honest outcome.
    """
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def read_json(path: Path) -> tuple[Any, str | None]:
    """``(value, error)`` for a JSON file.  Never raises on a bad or partial file."""
    text = _read_text(path)
    if text is None:
        return None, f"cannot read {path.name}"
    try:
        return json.loads(text), None
    except json.JSONDecodeError as exc:
        return None, f"{path.name} is not JSON: {exc}"


def read_jsonl(path: Path) -> tuple[list[Any], list[str]]:
    """One object per line, in file order, plus a problem per unparseable line.

    A trailing half-written line is skipped with a problem; the events before it
    are still returned, so a task mid-write still renders the steps it has.
    """
    text = _read_text(path)
    if text is None:
        return [], [f"cannot read {path.name}"]
    events: list[Any] = []
    problems: list[str] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as exc:
            problems.append(f"{path.name} line {number} is not JSON: {exc}")
    return events, problems


def certify_dir(run_dir: Path) -> dict:
    """``schema.certify()``, with a JSON-shaped fallback if it ever raises.

    ``certify()`` catches its own ``JSONDecodeError``, but it reads with the
    platform's default encoding and does not catch ``OSError`` or a
    ``UnicodeDecodeError``, so a genuinely half-written file could still raise.
    The API's contract is a body, not a traceback, so the failure becomes a
    problem on a certify-shaped dict instead.
    """
    try:
        return _certify(run_dir)
    except Exception as exc:  # noqa: BLE001 - the point is to convert any failure
        return {
            "run_id": run_dir.name,
            "points": 0,
            "rounds": [],
            "valid": False,
            "certified": False,
            "problems": [f"certify() could not read {run_dir.name}: "
                         f"{type(exc).__name__}: {exc}"],
            "notes": [],
            "tampered": [],
            "platform_content_sha": None,
            "final_score": None,
        }


def curve_of(run_dir: Path) -> tuple[list[dict], list[str]]:
    """``schema.read_curve()`` wrapped so a partial read can never raise."""
    try:
        return read_curve(run_dir)
    except Exception as exc:  # noqa: BLE001
        return [], [f"curve.jsonl could not be read: {type(exc).__name__}: {exc}"]


def _dir_mtime_iso(run_dir: Path) -> str | None:
    """The directory's mtime as an ISO-8601 UTC string.

    This is the timestamp of last resort for a run whose curve has no point yet
    (``runs/full-a`` while it is starting up).  It is a *proxy* for "when this
    run was last touched", and the summary says so in ``timestamp_source``.
    """
    try:
        mtime = run_dir.stat().st_mtime
    except OSError:
        return None
    return _dt.datetime.fromtimestamp(mtime, tz=_dt.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# run_meta.json
# ---------------------------------------------------------------------------

def read_meta(run_dir: Path) -> tuple[dict, str | None]:
    """``(meta, meta_error)``.  A missing `run_meta.json` is a state, not an error."""
    path = run_dir / "run_meta.json"
    if not path.is_file():
        return {}, ("no run_meta.json: the run's own account of itself is "
                    "missing")
    data, error = read_json(path)
    if error is not None:
        return {}, f"run_meta.json: {error}"
    if not isinstance(data, dict):
        return {}, f"run_meta.json is not a JSON object (got {type(data).__name__})"
    return data, None


def improver_name(meta: dict) -> str | None:
    """The improver the platform *resolved*, not the one the method's name implies.

    ``run_meta.improver`` is a resolved record on newer runs and a bare string on
    older ones; both are read, and ``None`` is returned when neither applies.
    """
    value = meta.get("improver") if isinstance(meta, dict) else None
    if isinstance(value, dict):
        name = value.get("name") or value.get("model")
        return name if isinstance(name, str) and name else None
    if isinstance(value, str) and value:
        return value
    return None


# ---------------------------------------------------------------------------
# GET /api/runs
# ---------------------------------------------------------------------------

def iter_run_names(runs_root: Path) -> list[str]:
    """Every subdirectory of ``runs/``, sorted.  Files are not runs.

    Directories are *not* filtered on having a ``run_meta.json`` or a
    ``curve.jsonl``: "unreadable" and "nothing measured yet" are states the
    Experiments screen renders, so they must come back as rows.
    """
    try:
        entries = sorted(runs_root.iterdir(), key=lambda p: p.name)
    except OSError:
        return []
    return [p.name for p in entries if p.is_dir()]


def run_summary(runs_root: Path, name: str) -> dict:
    """One row of ``GET /api/runs``.

    ``certify()`` returns no timestamp and none of the identity fields, so this
    joins them in.  The timestamp is the last curve point's ``timestamp_utc``
    when there is one, and otherwise the run directory's mtime;
    ``timestamp_source`` says which was used.
    """
    run_dir = runs_root / name
    certified = certify_dir(run_dir)
    meta, meta_error = read_meta(run_dir)
    points, _curve_problems = curve_of(run_dir)
    last: dict = points[-1] if points and isinstance(points[-1], dict) else {}

    from_curve = bool(last.get("timestamp_utc"))
    return {
        "certify": certified,
        "run_id": name,
        "agent_model": meta.get("agent_model"),
        "agent_backend": meta.get("agent_backend"),
        "harness": meta.get("harness"),
        "dataset": meta.get("dataset"),
        "improver": improver_name(meta),
        "mode": meta.get("mode"),
        "side": last.get("side"),
        "score_kind": last.get("score_kind"),
        # The last point's own score; `certify().final_score` is the same value
        # and is used when the curve could not be re-read here.
        "last_score": last.get("score") if points else certified.get("final_score"),
        "last_test_rate": last.get("test_rate"),
        "wall_clock_s": meta.get("wall_clock_s"),
        "timestamp_utc": last.get("timestamp_utc") or _dir_mtime_iso(run_dir),
        "timestamp_source": "curve" if from_curve else "run_meta_mtime",
        "meta_error": meta_error,
    }


def list_runs(runs_root: Path) -> list[dict]:
    """Every run directory as a summary row, in sorted order."""
    return [run_summary(runs_root, name) for name in iter_run_names(runs_root)]


# ---------------------------------------------------------------------------
# GET /api/runs/<id>
# ---------------------------------------------------------------------------

def read_verdicts(run_dir: Path) -> tuple[dict[str, dict[str, dict]], list[str]]:
    """``{round: {task_id: verdict}}`` from ``verdicts/round-<n>/<task>.json``."""
    root = run_dir / "verdicts"
    out: dict[str, dict[str, dict]] = {}
    problems: list[str] = []
    if not root.is_dir():
        return out, problems
    try:
        round_dirs = sorted(root.iterdir(), key=lambda p: p.name)
    except OSError as exc:
        return out, [f"cannot list verdicts/: {exc}"]
    for round_dir in round_dirs:
        match = _ROUND_DIR_RE.match(round_dir.name)
        if not match or not round_dir.is_dir():
            continue
        by_task: dict[str, dict] = {}
        for file in sorted(round_dir.glob("*.json")):
            data, error = read_json(file)
            if error is not None:
                problems.append(f"verdicts/{round_dir.name}/{file.name}: {error}")
                continue
            if isinstance(data, dict):
                by_task[file.stem] = data
            else:
                problems.append(
                    f"verdicts/{round_dir.name}/{file.name}: not a JSON object")
        out[match.group(1)] = by_task
    return out, problems


def read_diff_stats(run_dir: Path) -> tuple[dict[str, dict], list[str]]:
    """``{round: stat}`` from ``diffs/round-<n>.json`` (the patch is served alone)."""
    root = run_dir / "diffs"
    out: dict[str, dict] = {}
    problems: list[str] = []
    if not root.is_dir():
        return out, problems
    try:
        files = sorted(root.glob("round-*.json"))
    except OSError as exc:
        return out, [f"cannot list diffs/: {exc}"]
    for file in files:
        match = _DIFF_STAT_RE.match(file.name)
        if not match:
            continue
        data, error = read_json(file)
        if error is not None:
            problems.append(f"diffs/{file.name}: {error}")
            continue
        if isinstance(data, dict):
            out[match.group(1)] = data
        else:
            problems.append(f"diffs/{file.name}: not a JSON object")
    return out, problems


def run_bundle(runs_root: Path, run_id: str) -> dict:
    """``GET /api/runs/<id>``: meta, every point, every verdict, every diff stat.

    Traces are deliberately absent: a run's traces are tens of megabytes and the
    Task screen fetches one task at a time.  A run with no ``curve.jsonl`` is
    ``points: []`` plus a ``load_problems`` entry, never a 404.
    """
    run_dir = runs_root / run_id
    meta, meta_error = read_meta(run_dir)
    problems: list[str] = []
    if meta_error is not None:
        problems.append(meta_error)
    points, point_problems = curve_of(run_dir)
    problems.extend(point_problems)
    verdicts, verdict_problems = read_verdicts(run_dir)
    problems.extend(verdict_problems)
    diffs, diff_problems = read_diff_stats(run_dir)
    problems.extend(diff_problems)
    return {
        "run_id": run_id,
        "meta": meta,
        "points": points,
        "verdicts": verdicts,
        "diffs": diffs,
        "load_problems": problems,
    }


# ---------------------------------------------------------------------------
# GET /api/runs/<id>/rounds/<n>/diff
# ---------------------------------------------------------------------------

def round_diff(runs_root: Path, run_id: str, round_no: int) -> dict | None:
    """``{stat, patch}`` for a round, or ``None`` when no patch was saved.

    ``None`` is what the caller turns into a 404: round 0 has no diff by
    construction, and a round whose patch is still being written is the same
    absence.  The stat is read separately and may be ``None`` on its own (the
    patch is the thing that decides whether this round has a diff at all).
    """
    run_dir = runs_root / run_id
    stat, stat_error = read_json(run_dir / "diffs" / f"round-{round_no}.json")
    if not isinstance(stat, dict):
        stat = None
    patch = _read_text(run_dir / "diffs" / f"round-{round_no}.patch")
    if patch is None:
        return None
    return {
        "run_id": run_id,
        "round": round_no,
        "stat": stat,
        "stat_error": stat_error if stat is None else None,
        "patch": patch,
    }


# ---------------------------------------------------------------------------
# GET /api/runs/<id>/rounds/<n>/tasks/<task>
# ---------------------------------------------------------------------------

def task_diff(run_dir: Path, round_no: int) -> dict | None:
    """The round's stat **and** patch, for a task page's context panel."""
    stat, _stat_error = read_json(run_dir / "diffs" / f"round-{round_no}.json")
    patch = _read_text(run_dir / "diffs" / f"round-{round_no}.patch")
    if patch is None and not isinstance(stat, dict):
        return None
    if not isinstance(stat, dict):
        stat = {"round": round_no, "from": None, "to": None, "files": [],
                "added": None, "removed": None}
    return {**stat, "patch": patch or ""}


def task_page(runs_root: Path, run_id: str, round_no: int, task_id: str) -> dict:
    """``GET /api/runs/<id>/rounds/<n>/tasks/<task>``.

    ``verdict`` is ``None`` when the task was not scored in this round -- an
    absence, never a zero -- and that absence is explained in
    ``verdict_problems``.  A missing trace is a ``trace_problems`` entry with an
    empty list, not a 404: the task page still has its verdict, its round diff
    and its identity to show.
    """
    run_dir = runs_root / run_id
    verdict: dict | None = None
    verdict_problems: list[str] = []
    verdict_path = run_dir / "verdicts" / f"round-{round_no}" / f"{task_id}.json"
    if not verdict_path.is_file():
        verdict_problems.append(
            f"no verdict for `{task_id}` in round {round_no}: the task was not "
            f"scored in this round, or it is not part of this run's sampling")
    else:
        data, error = read_json(verdict_path)
        if error is not None:
            verdict_problems.append(f"verdicts/round-{round_no}/{task_id}.json: {error}")
        elif isinstance(data, dict):
            verdict = data
        else:
            verdict_problems.append(
                f"verdicts/round-{round_no}/{task_id}.json is not a JSON object")

    trace: list[Any] = []
    trace_problems: list[str] = []
    trace_path = run_dir / f"round{round_no}_traces" / f"{task_id}.jsonl"
    if not trace_path.is_file():
        trace_problems.append(f"no trace file: round{round_no}_traces/{task_id}.jsonl")
    else:
        trace, trace_problems = read_jsonl(trace_path)

    return {
        "run_id": run_id,
        "round": round_no,
        "task_id": task_id,
        "verdict": verdict,
        "verdict_problems": verdict_problems,
        "trace": trace,
        "trace_problems": trace_problems,
        "diff": task_diff(run_dir, round_no),
    }
