#!/usr/bin/env python3
"""The ALFWorld controls: does the check actually reach 1, and actually reach 0?

A dataset whose oracle also scores 0 has an unreachable check, and every harness score
on it is meaningless. A dataset whose do-nothing control scores 1 has a check that
cannot fail. Both are quiet: they produce a plausible number in the right place. So
both are run and both are asserted here, and the same two runs are what the brief asks
a reader to be able to reproduce.

Two ways to run each control
----------------------------
`--oracle`/`--noop` drive the CLI by hand and run the check directly. This needs
nothing but `pip install alfworld textworld` plus the extracted data, and it is the
"no Docker" path.

`--platform` runs the same episode through the platform's own `eval.run.runner.run_one`
with an oracle control harness (`data/datasets/alfworld/oracle_harness/`). That exercises
`SETUP` -> harness -> `VERIFY` end to end on a `files` environment, with the mount
namespace **on** by default -- which is also what proves the adapter's `VERIFY` works
with the platform's isolation in place. `--no-sandbox` exists for a machine without
`bwrap`. It needs no Docker either way.

The oracle is ALFWorld's own: the `walkthrough` array inside the extracted
`game.tw-pddl`, which is the reference solution the 0.4.2 asset shipped. Verified: all
134 valid_unseen walkthroughs satisfy their game (see docs/dataset-onboarding-skill.md).
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import data.datasets.alfworld as alfworld  # noqa: E402


def _record(task_id: str | None) -> dict:
    records = alfworld._RECORDS
    if not records:
        raise SystemExit("no ALFWorld tasks; provision the data first "
                         "(python3 tools/datasets.py --list)")
    if task_id is None:
        # A task on the eval side, so the control exercises what a score is taken on.
        task_id = alfworld.SPLIT["eval"][0]
    for record in records:
        if record["task_id"] == task_id:
            return record
    raise SystemExit(f"unknown task id {task_id!r}")


def _walkthrough(record: dict) -> list[str]:
    """The reference solution, read from the *unstripped* game file on disk."""
    gamedata = json.loads(Path(record["game_path"]).read_text())
    actions = list(gamedata.get("walkthrough") or [])
    if not actions:
        raise SystemExit(f"{record['task_id']} ships no walkthrough to replay")
    return actions


def materialize(record: dict, workdir: Path) -> None:
    """Put the task where `SETUP` would: the stripped game, the CLI, its library."""
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / alfworld.GAME_IN_WORKDIR).write_text(record["stripped_game"])
    shutil.copy2(alfworld.LIB_DIR / "gym_env.py", workdir / "gym_env.py")
    shutil.copy2(alfworld.CLI_DIR / "alf", workdir / "alf")
    (workdir / "alf").chmod(0o755)


def drive(workdir: Path, actions: list[str], *, budget: int) -> None:
    """Act through the CLI exactly as an agent would, stopping at the budget."""
    for action in actions[:budget]:
        subprocess.run([sys.executable, "alf", "do", action], cwd=workdir,
                       check=True, capture_output=True, text=True)
    subprocess.run([sys.executable, "alf", "done"], cwd=workdir,
                   check=True, capture_output=True, text=True)


def run_check(workdir: Path, record: dict, *, budget: int) -> tuple[int, str]:
    """Run the check the way the platform's verifier does, and read its verdict.

    The check's inputs are written here **again**, exactly as `VERIFY.inputs` are
    re-materialized after the harness stops. That is what makes the grade independent of
    anything the agent did to `<workdir>/check.py`, `<workdir>/gym_env.py` or
    `<workdir>/game.tw-pddl`, and it is why this function does not simply trust the
    copies `materialize()` wrote.
    """
    shutil.copy2(alfworld.VERIFY_DIR / "check.py", workdir / "check.py")
    shutil.copy2(alfworld.LIB_DIR / "gym_env.py", workdir / "gym_env.py")
    (workdir / alfworld.GAME_IN_WORKDIR).write_text(record["stripped_game"])
    argv = [sys.executable, "check.py",
            "--workdir", ".",
            "--game", alfworld.GAME_IN_WORKDIR,
            "--log", alfworld.LOG_IN_WORKDIR,
            "--reward-file", alfworld.REWARD_REL,
            "--evidence-file", alfworld.EVIDENCE_REL,
            "--budget", str(budget)]
    proc = subprocess.run(argv, cwd=workdir, capture_output=True, text=True)
    reward_path = workdir / alfworld.REWARD_REL
    reward = int(reward_path.read_text().strip()) if reward_path.is_file() else -1
    evidence_path = workdir / alfworld.EVIDENCE_REL
    evidence = (json.loads(evidence_path.read_text())
                if evidence_path.is_file() else {})
    verdict = {
        "returncode": proc.returncode,
        "reward": reward,
        "why": evidence.get("why"),
        "won_at_step": evidence.get("won_at_step"),
        "actions_replayed": evidence.get("actions_replayed"),
        "official_game_points": evidence.get("official_game_points"),
        "stdout": proc.stdout.strip(),
    }
    return reward, json.dumps(verdict, indent=1, sort_keys=True)


def run_local(record: dict, *, oracle: bool, workdir: Path, budget: int) -> int:
    materialize(record, workdir)
    if oracle:
        drive(workdir, _walkthrough(record), budget=budget)
    reward, detail = run_check(workdir, record, budget=budget)
    print(f"task    {record['task_id']}")
    print(f"mode    {'oracle' if oracle else 'do-nothing'}")
    print(f"reward  {reward}")
    print(detail)
    expected = 1 if oracle else 0
    if reward != expected:
        print(f"CONTROL FAILED: expected reward {expected}, got {reward}", file=sys.stderr)
        return 1
    return 0


def run_platform(record: dict, *, oracle: bool, workdir: Path,
                 sandbox: bool = True) -> int:
    """The same episode through `eval.run.runner.run_one`, with no Docker and no model.

    The control harness (`data/datasets/alfworld/oracle_harness/`) replays `.oracle/actions.json`
    through the CLI and otherwise does nothing, which is exactly what a harness control
    should be: a fixed program that runs what the dataset hands it.

    The harness is **copied into the work root** before the run, because a real run
    copies its harness there too, and because the sandbox refuses to run when the
    subject's tree is inside the platform it must hide. With the sandbox on, this
    control also proves that the adapter's `VERIFY` works with the namespace in place --
    including the writable verdict directory the reward-file contract needs.
    """
    from eval.run.runner import run_one

    tid = record["task_id"]
    task = next(t for t in alfworld.load()[0] if t["task_id"] == tid)
    setup = {"files": list(alfworld.SETUP[tid]["files"])}
    if oracle:
        setup["files"].append({"path": ".oracle/actions.json",
                               "content": json.dumps(_walkthrough(record))})
    work_root = workdir / "work"
    harness = work_root / "oracle_harness"
    shutil.copytree(ROOT / "data" / "datasets" / "alfworld" / "oracle_harness", harness,
                    dirs_exist_ok=True)
    # The platform reads this to decide what the sandbox may reveal; a real run sets it
    # to a directory outside the platform root.
    os.environ["HARNESSGRAD_WORK_ROOT"] = str(work_root)
    result = run_one(
        repo=harness,
        task=task,
        setup=setup,
        verifier=alfworld.VERIFY[tid],
        env=alfworld.ENV[tid],
        sandbox=sandbox,
        run_id="alfworld-control",
        run_seed="0",
    )
    verdict = result.get("verdict") or {}
    print(f"task     {tid}")
    print(f"mode     {'oracle' if oracle else 'do-nothing'} (platform run_one, "
          f"sandbox={sandbox})")
    print(f"exit     {result.get('exit_code')}")
    print(f"score    {verdict.get('score')}  passed {verdict.get('passed')}")
    print(f"detail   {verdict.get('detail')}")
    if verdict.get("evidence"):
        print(f"evidence {json.dumps(verdict['evidence'].get('why'), ensure_ascii=False)}")
    expected = 1.0 if oracle else 0.0
    score = verdict.get("score")
    if score is None:
        # No score is not a zero. The platform refused the task, the scorer failed, or
        # the run produced nothing -- each is unmeasured, and an unmeasured do-nothing
        # arm must never be counted as a passing control. Treating `None` as 0.0 here
        # did exactly that: it turned a refusal into "the noop arm behaved".
        print(f"CONTROL UNMEASURED: no score for {tid}", file=sys.stderr)
        return 2
    if float(score) != expected:
        print(f"CONTROL FAILED: expected score {expected}, got {score}",
              file=sys.stderr)
        return 1
    return 0


def main(argv) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--oracle", action="store_true",
                      help="replay ALFWorld's own walkthrough, expect reward 1")
    mode.add_argument("--noop", action="store_true",
                      help="do nothing, expect reward 0")
    parser.add_argument("--platform", action="store_true",
                        help="run through eval.runner.run_one instead of by hand")
    parser.add_argument("--no-sandbox", action="store_true",
                        help="with --platform, run without the mount namespace (the "
                             "weaker mode; the default is the namespace on)")
    parser.add_argument("--task-id", default=None)
    parser.add_argument("--workdir", default=None,
                        help="where to work; default is a fresh temporary directory")
    parser.add_argument("--keep", action="store_true",
                        help="with --workdir, do not delete it first")
    parser.add_argument("--budget", type=int, default=alfworld.STEP_BUDGET)
    args = parser.parse_args(argv)

    record = _record(args.task_id)
    if args.workdir:
        workdir = Path(args.workdir)
        if workdir.exists() and not args.keep:
            shutil.rmtree(workdir)
        workdir.mkdir(parents=True, exist_ok=True)
        cleanup = False
    else:
        workdir = Path(tempfile.mkdtemp(prefix="alfworld-control-"))
        cleanup = True
    try:
        if args.platform:
            return run_platform(record, oracle=args.oracle, workdir=workdir,
                                sandbox=not args.no_sandbox)
        return run_local(record, oracle=args.oracle, workdir=workdir,
                         budget=args.budget)
    finally:
        if cleanup:
            shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
