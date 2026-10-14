#!/usr/bin/env python3
"""Build `src/fixtures/data/` from the real run tree, read-only.

The read API does not exist yet, so the UI develops against fixtures. This script is the
**only** thing that produces them, and it is checked in so the fixtures can be rebuilt and
audited rather than trusted:

    python3 scripts/build_fixtures.py            # from web/, or anywhere

What it copies:

* a **curated** list of run directories -- not the whole 90-run tree -- covering every
  badge the Experiments screen can render (certified / valid-not-certified / invalid /
  no curve at all);
* two full **bundles** (`ds-dgm`, `ds-rrsi`): every point, every verdict, and every saved
  round patch. They are the Compare screen's demo pair, and they are the platform's own
  headline case -- both keep `score = 0.1` at round 0 and both *change which task passes*;
* two **task pages** (`ds-dgm` round 0, `cobol-modernization` and `fix-git`) with the
  verdict on disk and the full parsed trace.

What it deliberately does **not** do: write anything outside `web/`, read `.env` values
for secret-looking keys, or commit the millions of bytes under `runs/`.

Two derived values, both marked in the fixture README:

* `verdict.tests` -- the per-test tally. No verdict on disk carries it yet (the stage-0
  field was added after every recorded run), so it is parsed out of the verdict's own
  `detail` string, which is where `eval/run/runner.py:_test_report_failures` got it.
* `point.test_rate` / `point.per_task_test_rate` -- computed from those tallies by the
  same formula as `eval/run/runner.py:test_rate_of` (`passed / (passed + failed)`).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent
REPO = WEB.parent
RUNS = REPO / "runs"
OUT = WEB / "src" / "fixtures" / "data"

# Runs shown in the Experiments table. Chosen for coverage, not for score.
CURATED_RUNS = [
    "ds-dgm",              # valid, not certified; the flagship compare run
    "ds-rrsi",             # valid, not certified; the other half of the compare pair
    "codex-local-dgm",     # valid, not certified
    "v10-dgm",             # valid, not certified
    "handfix-1",           # valid, not certified
    "smoke-a-noimprover",  # certified
    "smoke-b-noimprover",  # certified
    "smoke-testrate",      # valid; the run stage 0 was verified against
    "smoke-a",             # INVALID: measured_by_platform is not true
    "smoke-b",             # INVALID: measured_by_platform is not true
    "codex-task-dgm",      # INVALID: no curve.jsonl -- nothing measured
    "v8-rrsi",             # INVALID: no curve.jsonl
    "noise-1",             # valid, one point
    "B2-noop",             # valid, one point
]

# The Compare screen's two runs, copied whole.
BUNDLE_RUNS = ["ds-dgm", "ds-rrsi"]

# Task pages with a full trace. Two, as asked; both are small enough to ship verbatim.
TASK_PAGES = [
    ("ds-dgm", 0, "cobol-modernization"),
    ("ds-dgm", 0, "fix-git"),
]

# Trace strings are cut here. The harness's own `output_limit` is 4000 and its context
# budget is 60000, so a cut at 6000 never removes something the harness could have seen;
# the marker left behind says how much was dropped.
TRACE_STRING_LIMIT = 6000
# Verdict `detail` is trimmed inside bundles (the featured task pages keep it whole).
BUNDLE_DETAIL_LIMIT = 1200

# `.env` keys that must never have their value copied into a fixture.
SECRET_HINTS = ("KEY", "TOKEN", "SECRET", "PASSWORD")
# Non-secret env vars whose value it is safe and useful to show in the Launch form.
SAFE_ENV_VALUES = {
    "HG_AGENT_BACKEND",
    "HG_AGENT_MODEL",
    "HG_METHOD_MODEL",
    "HG_AGENT_TIMEOUT_S",
    "HG_AGENT_RETRIES",
    "HG_METHOD_TIMEOUT_S",
}

_TALLY_RE = re.compile(r"check_report [^(]*\(([^)]*)\)")


def read_json(path: Path):
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def certify(runs: list[str]) -> dict[str, dict]:
    """`harnessgrad/store/schema.py:certify()` for each run, via the platform's own CLI.

    Calling `tools/validate_run.py --json` instead of reimplementing `certify()` here is
    the point: the fixture then cannot drift from the authority the UI is claiming to
    render.
    """
    cmd = [sys.executable, str(REPO / "tools" / "validate_run.py"),
           *[f"runs/{run}" for run in runs], "--json"]
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    # Exit 1 means "at least one run is not valid", which is exactly the state the
    # Experiments screen exists to show. It is not an error here.
    if proc.returncode not in (0, 1):
        raise SystemExit(f"validate_run.py failed ({proc.returncode}):\n{proc.stderr}")
    rows = json.loads(proc.stdout)
    return {row["run_id"]: row for row in rows}


def slim_env(env: dict | None) -> dict:
    """Drop the per-task image lists: real, huge, and not read by any screen.

    What survives is what `docs/refactor_references.md` §7 calls the platform's advantage
    over the projects it studied: the pinned `image_digest`, the placement, and the
    harness runtime source.
    """
    if not isinstance(env, dict):
        return {}
    keep = ("kind", "image_digest", "network", "placement", "services", "model",
            "seed", "model_gateway")
    out = {k: env[k] for k in keep if k in env}
    runtime = env.get("harness_runtime")
    if isinstance(runtime, list):
        out["harness_runtime"] = [
            {k: r.get(k) for k in ("source", "python", "install", "install_sha256",
                                   "built_from_image")}
            for r in runtime if isinstance(r, dict)
        ]
    variants = env.get("variants")
    if isinstance(variants, list):
        out["variants_count"] = len(variants)
    return out


def slim_point(point: dict) -> dict:
    point = dict(point)
    # `split` restates the whole task list on every point; the run's meta carries it once.
    point.pop("split", None)
    if isinstance(point.get("env"), dict):
        point["env"] = slim_env(point["env"])
    # The candidate-code blob is a static analysis report with no screen yet.
    point.pop("candidate_code", None)
    return point


def tally_from_detail(detail: str) -> dict | None:
    """The CTRF tally, recovered from the verdict's own summary line."""
    match = _TALLY_RE.search(detail or "")
    if not match:
        return None
    passed = failed = skipped = 0
    for number, word in re.findall(r"(\d+)\s+(passed|failed|skipped|pending)", match.group(1)):
        value = int(number)
        if word == "passed":
            passed = value
        elif word == "failed":
            failed = value
        else:
            skipped += value
    if passed + failed == 0 and skipped == 0:
        return None
    tally = {"passed": passed, "failed": failed}
    if skipped:
        tally["skipped"] = skipped
    return tally


def trimmed(text: str, limit: int) -> str:
    if not isinstance(text, str) or len(text) <= limit:
        return text
    return text[:limit] + f"\n… [truncated for the fixture: {len(text)} chars originally]"


def slim_verdict(verdict: dict, *, trim_detail: bool) -> dict:
    out = dict(verdict)
    detail = out.get("detail") or ""
    tally = tally_from_detail(detail)
    if tally:
        out["tests"] = tally
    if trim_detail:
        out["detail"] = trimmed(detail, BUNDLE_DETAIL_LIMIT)
    return out


def read_curve(run: str) -> list[dict]:
    path = RUNS / run / "curve.jsonl"
    if not path.is_file():
        return []
    points = []
    for line in path.read_text().splitlines():
        if line.strip():
            points.append(json.loads(line))
    return points


def read_verdicts(run: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    root = RUNS / run / "verdicts"
    if not root.is_dir():
        return out
    for round_dir in sorted(root.iterdir()):
        if not round_dir.is_dir():
            continue
        match = re.fullmatch(r"round-(\d+)", round_dir.name)
        if not match:
            continue
        by_task = {}
        for file in sorted(round_dir.glob("*.json")):
            data = read_json(file)
            if isinstance(data, dict):
                by_task[file.stem] = slim_verdict(data, trim_detail=True)
        out[match.group(1)] = by_task
    return out


def read_diffs(run: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    root = RUNS / run / "diffs"
    if not root.is_dir():
        return out
    for stat_file in sorted(root.glob("round-*.json")):
        stat = read_json(stat_file)
        if not isinstance(stat, dict):
            continue
        patch_file = stat_file.with_suffix(".patch")
        stat = dict(stat)
        stat["patch"] = patch_file.read_text() if patch_file.is_file() else ""
        out[str(stat.get("round"))] = stat
    return out


def read_trace(run: str, round_no: int, task: str) -> tuple[list[dict], list[str]]:
    path = RUNS / run / f"round{round_no}_traces" / f"{task}.jsonl"
    if not path.is_file():
        return [], [f"no trace file: {path.name}"]
    events, problems = [], []
    for n, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            problems.append(f"line {n} is not JSON: {exc}")
            continue
        for key in ("reply", "output", "command"):
            if isinstance(event.get(key), str):
                event[key] = trimmed(event[key], TRACE_STRING_LIMIT)
        events.append(event)
    return events, problems


def point_test_rate(verdicts: dict[str, dict]) -> float | None:
    """`eval/run/runner.py:test_rate_of`, applied to the recovered tallies."""
    rates = []
    for verdict in verdicts.values():
        tally = verdict.get("tests")
        if not isinstance(tally, dict):
            continue
        passed, failed = tally.get("passed"), tally.get("failed")
        if not isinstance(passed, int) or not isinstance(failed, int):
            continue
        ran = passed + failed
        if ran > 0:
            rates.append(passed / ran)
    return sum(rates) / len(rates) if rates else None


def enrich_points(points: list[dict], verdicts: dict[str, dict]) -> list[dict]:
    """Attach the stage-0 `test_rate` family, derived from the recovered tallies.

    This is an addition the fixture makes and the real record does not yet have; the
    README says so. Without it the second curve series would be empty on every screen and
    the reason stage 0 exists -- a binary score cannot resolve the effect -- would be
    invisible exactly where it matters.
    """
    out = []
    for point in points:
        point = slim_point(point)
        by_round = verdicts.get(str(point.get("round")), {})
        per_task = {}
        for task, verdict in by_round.items():
            tally = verdict.get("tests")
            if not isinstance(tally, dict):
                continue
            passed, failed = tally.get("passed"), tally.get("failed")
            if isinstance(passed, int) and isinstance(failed, int) and passed + failed > 0:
                per_task[task] = passed / (passed + failed)
        rate = point_test_rate(by_round)
        if rate is not None:
            point["test_rate"] = rate
            point["test_rate_n_tasks"] = len(per_task)
            point["per_task_test_rate"] = per_task
            point["tests_passed"] = sum(
                v["tests"]["passed"] for v in by_round.values()
                if isinstance(v.get("tests"), dict))
            point["tests_total"] = sum(
                v["tests"]["passed"] + v["tests"]["failed"] for v in by_round.values()
                if isinstance(v.get("tests"), dict))
        out.append(point)
    return out


def summarise(run: str, certify_row: dict) -> dict:
    meta = read_json(RUNS / run / "run_meta.json") or {}
    points = read_curve(run)
    last = points[-1] if points else {}
    improver = meta.get("improver")
    if isinstance(improver, dict):
        improver_name = improver.get("name") or improver.get("model")
    else:
        improver_name = improver
    verdicts = read_verdicts(run)
    last_verdicts = verdicts.get(str(last.get("round")), {})
    last_rate = point_test_rate(last_verdicts)
    if last_rate is None:
        last_rate = last.get("test_rate") if last.get("test_rate") is not None else None
    side = last.get("side")
    score_kind = last.get("score_kind")
    return {
        "run_id": certify_row.get("run_id") or run,
        "certify": certify_row,
        "agent_model": meta.get("agent_model"),
        "agent_backend": meta.get("agent_backend"),
        "harness": meta.get("harness"),
        "dataset": meta.get("dataset"),
        "improver": improver_name,
        "mode": meta.get("mode"),
        "side": side,
        "score_kind": score_kind,
        "last_score": certify_row.get("final_score", last.get("score")),
        "last_test_rate": last_rate,
        "wall_clock_s": meta.get("wall_clock_s"),
        "timestamp_utc": last.get("timestamp_utc"),
        "meta_error": None if meta else "no run_meta.json: the run's own account of itself is missing",
    }


def build_bundle(run: str) -> dict:
    meta = read_json(RUNS / run / "run_meta.json") or {}
    meta = dict(meta)
    if isinstance(meta.get("env"), dict):
        meta["env"] = slim_env(meta["env"])
    meta.pop("split", None)  # 89 task ids; the UI reads it per point's sampling instead
    verdicts = read_verdicts(run)
    points = enrich_points(read_curve(run), verdicts)
    problems = []
    if not meta:
        problems.append("no run_meta.json")
    if not points:
        problems.append("no curve.jsonl: nothing was measured")
    return {
        "run_id": run,
        "meta": meta,
        "points": points,
        "verdicts": verdicts,
        "diffs": read_diffs(run),
        "load_problems": problems,
    }


def build_task_page(run: str, round_no: int, task: str) -> dict:
    verdict_file = RUNS / run / "verdicts" / f"round-{round_no}" / f"{task}.json"
    raw = read_json(verdict_file)
    problems = []
    verdict = None
    if raw is None:
        problems.append(f"no verdict file: verdicts/round-{round_no}/{task}.json")
    else:
        verdict = slim_verdict(raw, trim_detail=False)
    trace, trace_problems = read_trace(run, round_no, task)
    diffs = read_diffs(run)
    diff = diffs.get(str(round_no))
    return {
        "run_id": run,
        "round": round_no,
        "task_id": task,
        "verdict": verdict,
        "verdict_problems": problems,
        "trace": trace,
        "trace_problems": trace_problems,
        "diff": diff,
    }


def parse_env_file() -> dict[str, str]:
    path = REPO / ".env"
    if not path.is_file():
        return {}
    values = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def build_launch_options() -> dict:
    harnesses = sorted(
        d.name for d in (REPO / "base_harness").iterdir()
        if (d / "harness.json").is_file()
    )
    datasets = sorted(
        p.stem for directory in (REPO / "data", REPO / "data/datasets")
        for p in directory.glob("*.py")
        if not p.stem.startswith(("registry", "verify_"))
        and not (directory.name == "datasets" and p.stem == "__init__")
    )
    improvers_raw = read_json(REPO / "improvers" / "improvers.json") or {}
    improver_names = sorted((improvers_raw.get("improvers") or {}).keys())
    if improvers_raw.get("default"):
        improver_names = [improvers_raw["default"]] + [
            n for n in improver_names if n != improvers_raw["default"]
        ]
    env_values = parse_env_file()

    def env_field(flag: str, var: str, note: str) -> dict:
        raw = env_values.get(var)
        secret = any(h in var for h in SECRET_HINTS)
        return {
            "flag": flag,
            "env_var": var,
            "value": raw if (raw and not secret and var in SAFE_ENV_VALUES) else None,
            "set": bool(raw),
            "secret": secret,
            "note": note,
        }

    return {
        "harnesses": harnesses,
        "datasets": datasets,
        "samplings": ["all", "below_0.5", "above_0.5", "random_10"],
        "improvers": improver_names,
        "modes": ["A", "B"],
        "sides": ["train", "eval"],
        "improver_names": improver_names,
        "env_derived": [
            env_field("--agent-model (no flag; harness-declared)", "HG_AGENT_MODEL",
                      "The model that solves the tasks. Read from the environment and "
                      "recorded on every point's `identity.agent_model`."),
            env_field("--agent-backend (no flag)", "HG_AGENT_BACKEND",
                      "How the agent model is reached (`openai`, `codex`, `mock`)."),
            env_field("--agent-timeout (no flag)", "HG_AGENT_TIMEOUT_S",
                      "Per-task agent timeout, unless the task's env variant overrides it."),
            env_field("--agent-retries (no flag)", "HG_AGENT_RETRIES",
                      "Retries per model call."),
            env_field("--improver", "HG_METHOD_MODEL",
                      "The improver's own model. `identity.improver` records what was "
                      "resolved, not what was asked for."),
            env_field("--improver", "DEEPSEEK_API_KEY",
                      "Credential for the improver endpoint. Never copied into a fixture."),
            env_field("--improver", "HG_METHOD_API_KEY",
                      "Credential for the improver endpoint. Never copied into a fixture."),
            env_field("--improver", "HG_METHOD_BASE_URL",
                      "The improver endpoint, when it is not the default."),
            env_field("--agent-model (no flag)", "HG_AGENT_API_KEY",
                      "Credential for the agent model. Never copied into a fixture."),
            env_field("--agent-model (no flag)", "HG_AGENT_BASE_URL",
                      "The agent endpoint, when it is not the default."),
            env_field("--no-sandbox", "HG_EGRESS_PROXY",
                      "Proxy used to reach model endpoints from inside a run."),
        ],
        "flag_help": {
            "--harness": "which base harness to start from",
            "--dataset": "the task set",
            "--sampling": "all | below_X | above_X | random_N (chosen on H0)",
            "--rounds": "how many states to measure",
            "--trials": "measure each task N times; the point carries n_trials and score_std",
            "--jobs": "measure up to N tasks concurrently",
            "--mode": "DEPRECATED and ignored: there is one engine",
            "--improver": "improvers/improvers.json name, or a path to an executable",
            "--improver-model": "override the improver's own model",
            "--method-entrypoint": "argv for the method's own runner",
            "--run-id": "the run directory name under runs/",
            "--tasks": "a comma-separated subset of task ids",
            "--side": "which side of the split this run is about",
            "--from-run": "--side eval: the train run whose harness state to measure",
            "--from-round": "--side eval: which round of that run (default: its last)",
            "--seed": "the environment's seed; recorded on every point",
            "--no-sandbox": "run the harness WITHOUT a mount namespace",
            "--work-root": "where harness working trees live; must be OUTSIDE the platform",
        },
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cert = certify(CURATED_RUNS)
    summaries = [summarise(run, cert[run]) for run in CURATED_RUNS if run in cert]
    missing = [run for run in CURATED_RUNS if run not in cert]
    if missing:
        print(f"warning: validate_run.py returned nothing for {missing}", file=sys.stderr)

    write = lambda name, data: (OUT / name).write_text(  # noqa: E731
        json.dumps(data, indent=1, ensure_ascii=False) + "\n")

    write("runs-index.json", summaries)
    for run in BUNDLE_RUNS:
        write(f"run-{run}.json", build_bundle(run))
    for run, round_no, task in TASK_PAGES:
        write(f"task-{run}-r{round_no}-{task}.json", build_task_page(run, round_no, task))
    write("launch-options.json", build_launch_options())

    for path in sorted(OUT.glob("*.json")):
        print(f"{path.relative_to(WEB)}: {path.stat().st_size:>9,} bytes")
    print(f"\n{len(summaries)} runs, {len(BUNDLE_RUNS)} bundles, {len(TASK_PAGES)} task pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
