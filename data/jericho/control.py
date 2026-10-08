#!/usr/bin/env python3
"""The Jericho controls: does the check actually reach 1, and actually reach 0?

    python3 data/jericho/control.py --oracle
    python3 data/jericho/control.py --noop
    python3 data/jericho/control.py --oracle --platform
    python3 data/jericho/control.py --noop   --platform

A dataset whose oracle scores 0 has an unreachable check, and every harness score on it is
meaningless. A dataset whose do-nothing control scores 1 has a check that cannot fail. Both
failures are quiet -- a plausible number lands in the right place -- so both are run and both
are asserted.

The oracle is Jericho's own: `FrotzEnv.get_walkthrough()` at the game's official seed, which is
the reference solution the benchmark's `game_info.py` ships. By default the control picks the
**shortest walkthrough on the eval side** of the split, because the control's runtime is a cost
the whole suite pays; `--task-id` runs any game for a reader who wants a specific one.

A note on what "reward 1" means here. The reward is `score / get_max_score()`, so 1 means the
game was finished. Measured over this suite, the walkthroughs reach the maximum for most games
but **not all** -- a few stop short -- and when the oracle picks an eval-side game whose
walkthrough does not reach the maximum, this control will fail. That is the control doing its
job: it is reporting that the reference solution does not finish that game, which is a fact
about the benchmark rather than about the check. `--task-id` exists for that case, and the
suite's own walkthrough scores are recorded by `tests/quality/test_jericho_dataset.py`.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

import data.jericho as jericho  # noqa: E402
import jer_env  # noqa: E402


def _record(task_id: str | None) -> dict:
    records = jericho._RECORDS
    if not records:
        raise SystemExit("no Jericho games; provision them with "
                         "`python3 tools/datasets.py --fetch --dataset jericho`")
    if task_id is None:
        eval_ids = set(jericho.SPLIT["eval"])
        task_id = min((r for r in records if r["task_id"] in eval_ids),
                      key=lambda r: len(r["walkthrough"]))["task_id"]
    for record in records:
        if record["task_id"] == task_id:
            return record
    raise SystemExit(f"unknown task id {task_id!r}")


def _copy_entry(entry: dict, workdir: Path) -> None:
    """One SETUP/VERIFY entry, the way the platform's `_materialize` does it."""
    target = workdir / entry["path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    if "content" in entry:
        target.write_text(entry["content"])
    else:
        shutil.copy2(entry["from"], target)
        if entry["path"] == "jer":
            target.chmod(0o755)


def materialize(record: dict, workdir: Path) -> None:
    """Put the task where `SETUP` would: the game identity, the ROM, the CLI, its library."""
    workdir.mkdir(parents=True, exist_ok=True)
    for entry in jericho.SETUP[record["task_id"]]["files"]:
        _copy_entry(entry, workdir)
    # The ROM is a `from` reference into the dataset root, which is not in the workdir; the
    # platform's SETUP does not ship it (only `VERIFY.inputs` does), so the control copies it
    # the way a real run would after verification materializes it.
    shutil.copy2(record["path"], workdir / record["rom"])


def drive(workdir: Path, actions: list[str]) -> int:
    """Act through the CLI exactly as an agent would. Returns how many commands ran."""
    ran = 0
    for action in actions:
        proc = subprocess.run([sys.executable, "jer", "do", action], cwd=workdir,
                              capture_output=True, text=True)
        if proc.returncode != 0:
            raise SystemExit(f"the CLI refused {action!r}: {proc.stderr[-400:]}")
        ran += 1
    subprocess.run([sys.executable, "jer", "done"], cwd=workdir, capture_output=True,
                   text=True)
    return ran


def run_check(module, record: dict, workdir: Path) -> tuple[float, str]:
    """Run the check the way the platform's verifier does, re-materializing its inputs."""
    verifier = module.VERIFY[record["task_id"]]
    for entry in verifier.get("inputs") or []:
        _copy_entry(entry, workdir)
    argv = [sys.executable, *verifier["argv"][1:]]
    proc = subprocess.run(argv, cwd=workdir, capture_output=True, text=True)
    reward_path = workdir / module.REWARD_REL
    reward = float(reward_path.read_text().strip()) if reward_path.is_file() else -1.0
    evidence_path = workdir / module.EVIDENCE_REL
    evidence = (json.loads(evidence_path.read_text())
                if evidence_path.is_file() else {})
    detail = {
        "returncode": proc.returncode,
        "reward": reward,
        "score": evidence.get("score"),
        "max_score": evidence.get("max_score"),
        "moves": evidence.get("moves"),
        "measured": evidence.get("measured"),
        "why": evidence.get("why") or evidence.get("error"),
        "stderr": proc.stderr[-400:],
    }
    return reward, json.dumps(detail, indent=1, sort_keys=True)


def run_local(module, record: dict, *, oracle: bool, workdir: Path) -> int:
    materialize(record, workdir)
    if oracle:
        drive(workdir, record["walkthrough"])
    reward, detail = run_check(module, record, workdir)
    print(f"task    {record['task_id']}  ({len(record['walkthrough'])} reference commands)")
    print(f"mode    {'oracle' if oracle else 'do-nothing'}")
    print(f"reward  {reward:g}")
    print(detail)
    expected = 1.0 if oracle else 0.0
    if reward != expected:
        print(f"CONTROL FAILED: expected reward {expected:g}, got {reward:g}",
              file=sys.stderr)
        return 1
    return 0


def run_platform(module, record: dict, *, oracle: bool, workdir: Path,
                 sandbox: bool = True) -> int:
    """The same episode through `eval.runner.run_one`, with no Docker and no model."""
    from eval.runner import run_one

    tid = record["task_id"]
    task = next(t for t in module.load()[0] if t["task_id"] == tid)
    setup = {"files": list(module.SETUP[tid]["files"])}
    if oracle:
        setup["files"].append({"path": ".oracle/actions.json",
                               "content": json.dumps(record["walkthrough"])})
    work_root = workdir / "work"
    harness = work_root / "oracle_harness"
    shutil.copytree(Path(__file__).resolve().parent / "oracle_harness", harness,
                    dirs_exist_ok=True)
    os.environ["HARNESSGRAD_WORK_ROOT"] = str(work_root)
    started = time.time()
    result = run_one(
        repo=harness,
        task=task,
        setup=setup,
        verifier=module.VERIFY[tid],
        env=module.ENV[tid],
        sandbox=sandbox,
        run_id="jericho-control",
        run_seed="0",
    )
    verdict = result.get("verdict") or {}
    print(f"task     {tid}")
    print(f"mode     {'oracle' if oracle else 'do-nothing'} (platform run_one, "
          f"sandbox={sandbox})")
    print(f"exit     {result.get('exit_code')}   wall {time.time() - started:.1f}s")
    print(f"score    {verdict.get('score')}  passed {verdict.get('passed')}")
    print(f"detail   {verdict.get('detail')}")
    if verdict.get("evidence"):
        print(f"evidence {json.dumps(verdict['evidence'].get('why'), ensure_ascii=False)}")
    expected = 1.0 if oracle else 0.0
    if float(verdict.get("score") or 0.0) != expected:
        print(f"CONTROL FAILED: expected score {expected:g}, got {verdict.get('score')}",
              file=sys.stderr)
        return 1
    return 0


def main(argv) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--oracle", action="store_true",
                      help="replay the game's own walkthrough; expect reward 1")
    mode.add_argument("--noop", action="store_true", help="do nothing; expect 0")
    parser.add_argument("--platform", action="store_true")
    parser.add_argument("--no-sandbox", action="store_true")
    parser.add_argument("--task-id", default=None)
    parser.add_argument("--workdir", default=None)
    parser.add_argument("--keep", action="store_true")
    args = parser.parse_args(argv)

    record = _record(args.task_id)
    if args.workdir:
        workdir = Path(args.workdir)
        if workdir.exists() and not args.keep:
            shutil.rmtree(workdir)
        workdir.mkdir(parents=True, exist_ok=True)
        cleanup = False
    else:
        workdir = Path(tempfile.mkdtemp(prefix="jericho-control-"))
        cleanup = True
    started = time.time()
    try:
        if args.platform:
            return run_platform(jericho, record, oracle=args.oracle, workdir=workdir,
                                sandbox=not args.no_sandbox)
        return run_local(jericho, record, oracle=args.oracle, workdir=workdir)
    finally:
        print(f"elapsed {time.time() - started:.1f}s")
        if cleanup:
            shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
