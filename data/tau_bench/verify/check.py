#!/usr/bin/env python3
"""The tau-bench check: replay the ground truth and compare database hashes.

This runs **inside a snapshot of the agent's container**, after the agent stopped,
with its inputs copied in by the platform only at that point. It is deliberately
not a test of the agent's transcript: tau-bench's own scoring rule is a comparison
of database states, so that is what is compared here.

    1. read the agent's database from the workdir (`/app/db.json`);
    2. import the domain's tool classes from `/verifier/lib` -- a host-staged copy
       of the upstream implementations, so the replay cannot be steered by anything
       the agent edited inside the container;
    3. replay the ground-truth actions on a **clean** database, through those same
       tool classes, skipping terminating actions exactly as
       `tau_bench.envs.base.Env.calculate_reward` does;
    4. hash both with `consistent_hash(to_hashable(...))` -- the functions
       extracted verbatim from `tau_bench/envs/base.py` -- and write `1` to the
       reward file iff they are equal, `0` otherwise.

Evidence
--------
It also writes an evidence JSON naming *why*: whether the whole-database hash
matched, which top-level table differs, how many ground-truth actions there were
and how many replayed, any replay errors -- both exceptions and the `Error: ...`
strings a tool *returns* when it refuses an action -- whether the ground truth
changes the database at all (a ground-truth replay that is a no-op means a no-op
agent passes, so it is worth saying out loud), and how many `tau call`s the agent
logged (`/app/tau_calls.jsonl`, which is the agent's own file and therefore
evidence, not the grade).

Failure modes are kept apart on purpose
---------------------------------------
* The agent's database missing or unparseable is the agent's state: reward `0`,
  with the reason in the evidence.
* This check's own inputs missing (ground truth, clean database, tool library) is
  not a measurement: no reward file is written, so the platform reports the task
  as unmeasured rather than as a zero the agent earned.

Inputs (paths overridable with the matching flag or environment variable):
    /verifier/gt.json         TAU_GT           ground truth for this task
    /verifier/clean_db.json   TAU_CLEAN_DB     the clean database
    /verifier/lib             TAU_LIB          tau-bench tools + hash functions
    /app/db.json              TAU_DB           the agent's database
    /verifier/reward.txt      TAU_REWARD       1 or 0
    /verifier/evidence.json   TAU_EVIDENCE     why
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from collections import Counter
from pathlib import Path

VERIFIER_DIR = Path("/verifier")
DEFAULTS = {
    "gt": VERIFIER_DIR / "gt.json",
    "clean_db": VERIFIER_DIR / "clean_db.json",
    "lib": VERIFIER_DIR / "lib",
    "db": Path(os.environ.get("TAU_WORKDIR", "/app")) / "db.json",
    "reward": VERIFIER_DIR / "reward.txt",
    "evidence": VERIFIER_DIR / "evidence.json",
    "call_log": Path(os.environ.get("TAU_WORKDIR", "/app")) / "tau_calls.jsonl",
}

#: `Mock*DomainEnv.terminate_tools` in the upstream environment. `calculate_reward`
#: does not replay them, and neither does this: they do not touch the database.
TERMINATE_TOOLS = ("transfer_to_human_agents",)


def _env_path(flag_value, env_name: str, default: Path) -> Path:
    if flag_value:
        return Path(flag_value)
    override = os.environ.get(env_name)
    return Path(override) if override else default


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name, env_name in (("gt", "TAU_GT"), ("clean_db", "TAU_CLEAN_DB"),
                           ("lib", "TAU_LIB"), ("db", "TAU_DB"),
                           ("reward", "TAU_REWARD"), ("evidence", "TAU_EVIDENCE"),
                           ("call_log", "TAU_CALL_LOG")):
        parser.add_argument(f"--{name.replace('_', '-')}", default=None,
                            help=f"default: {DEFAULTS[name]} (${env_name})")
    args = parser.parse_args(argv)
    return {key: _env_path(getattr(args, key),
                           "TAU_" + key.upper(), DEFAULTS[key]) for key in DEFAULTS}


def hash_of(value) -> str:
    from tau_bench.envs.hash import consistent_hash, to_hashable
    return consistent_hash(to_hashable(value))


def write_reward(path: Path, score: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{score}\n")


def write_evidence(path: Path, evidence: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(evidence, indent=1, sort_keys=True,
                                   ensure_ascii=False) + "\n")
    except OSError as exc:  # evidence is for a reader, not for the score
        print(f"could not write evidence: {exc}", file=sys.stderr)


def import_tools(lib: Path, domain: str) -> dict:
    if str(lib) not in sys.path:
        sys.path.insert(0, str(lib))
    import importlib
    module = importlib.import_module(f"tau_bench.envs.{domain}.tools")
    return {cls.get_info()["function"]["name"]: cls for cls in module.ALL_TOOLS}


def agent_call_log(path: Path):
    """(count, {tool: count}) from the agent's own log, or (None, {}) if absent."""
    if not path.is_file():
        return None, {}
    counts: Counter = Counter()
    total = 0
    for line in path.read_text(errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        total += 1
        try:
            counts[json.loads(line).get("name", "?")] += 1
        except ValueError:
            counts["<unparseable>"] += 1
    return total, dict(counts)


def section_comparison(agent_db, gt_db) -> dict:
    sections = {}
    for key in sorted(set(agent_db) | set(gt_db)):
        in_agent, in_gt = key in agent_db, key in gt_db
        if in_agent and in_gt:
            matched = hash_of(agent_db[key]) == hash_of(gt_db[key])
        else:
            matched = False
        sections[key] = {"matched": matched, "in_agent": in_agent,
                         "in_ground_truth": in_gt}
    return sections


def main(argv) -> int:
    paths = parse_args(argv)
    evidence: dict = {"gt_file": str(paths["gt"]),
                      "clean_db_file": str(paths["clean_db"]),
                      "agent_db_file": str(paths["db"]),
                      "tool_lib": str(paths["lib"])}

    # ---- this check's own inputs: missing means the task was not measured. ----
    try:
        gt = json.loads(paths["gt"].read_text())
    except (OSError, ValueError) as exc:
        evidence["error"] = f"ground truth unavailable: {exc}"
        write_evidence(paths["evidence"], evidence)
        print(f"check cannot run: {evidence['error']}", file=sys.stderr)
        return 3

    domain = gt["domain"]
    actions = gt["actions"]
    evidence.update(task_id=gt.get("task_id"), domain=domain,
                    user_id=gt.get("user_id"),
                    ground_truth_actions=len(actions))

    try:
        clean_db = json.loads(paths["clean_db"].read_text())
    except (OSError, ValueError) as exc:
        evidence["error"] = f"clean database unavailable: {exc}"
        write_evidence(paths["evidence"], evidence)
        print(f"check cannot run: {evidence['error']}", file=sys.stderr)
        return 3

    try:
        tools = import_tools(paths["lib"], domain)
    except Exception as exc:  # noqa: BLE001 - the library is the check's own input
        evidence["error"] = f"cannot import the {domain} tools: {exc}"
        write_evidence(paths["evidence"], evidence)
        print(f"check cannot run: {evidence['error']}", file=sys.stderr)
        return 3

    # ---- replay the ground truth on the clean database ----
    clean_hash = hash_of(clean_db)
    replayed, skipped, errors, tool_errors = 0, [], [], []
    for action in actions:
        name = action.get("name")
        if name in TERMINATE_TOOLS:
            skipped.append(name)
            continue
        tool = tools.get(name)
        if tool is None:
            errors.append(f"unknown ground-truth tool {name!r}")
            continue
        try:
            observation = tool.invoke(clean_db, **action.get("arguments", {}))
            # A tool reports a refused action by *returning* `Error: ...`, not by
            # raising; recorded because it is how a ground truth that never changes
            # the database (so a no-op agent scores) is told apart from a real one.
            if isinstance(observation, str) and observation.startswith("Error:"):
                tool_errors.append(f"{name}: {observation}")
        except Exception as exc:  # noqa: BLE001 - mirrors Env.step
            errors.append(f"{name}: {type(exc).__name__}: {exc}")
        replayed += 1

    evidence.update(replayed_actions=replayed, skipped_terminate_actions=skipped,
                    replay_errors=errors, replay_tool_errors=tool_errors,
                    clean_data_hash=clean_hash,
                    ground_truth_db_keys=sorted(clean_db))
    gt_hash = hash_of(clean_db)
    evidence["ground_truth_data_hash"] = gt_hash
    evidence["ground_truth_changes_database"] = gt_hash != clean_hash

    # ---- the agent's database, which is the state being graded ----
    try:
        raw = paths["db"].read_bytes()
        agent_db = json.loads(raw)
        if not isinstance(agent_db, dict):
            raise ValueError(f"database is a {type(agent_db).__name__}, "
                             f"expected a JSON object")
    except (OSError, ValueError) as exc:
        evidence.update(reward=0, database_hash_matched=False,
                        agent_db_error=str(exc), agent_db_keys=[])
        total, counts = agent_call_log(paths["call_log"])
        evidence.update(agent_tool_calls=total, agent_tool_call_counts=counts)
        write_reward(paths["reward"], 0)
        write_evidence(paths["evidence"], evidence)
        print(f"reward 0: the agent's database could not be read: {exc}")
        return 0

    agent_hash = hash_of(agent_db)
    matched = agent_hash == gt_hash
    evidence.update(reward=int(matched), database_hash_matched=matched,
                    agent_data_hash=agent_hash, agent_db_bytes=len(raw),
                    agent_db_keys=sorted(agent_db),
                    sections=section_comparison(agent_db, clean_db))
    total, counts = agent_call_log(paths["call_log"])
    evidence.update(agent_tool_calls=total, agent_tool_call_counts=counts)

    write_reward(paths["reward"], int(matched))
    write_evidence(paths["evidence"], evidence)

    if matched:
        print(f"reward 1: database hash matches the ground truth "
              f"({gt_hash[:12]}..., {replayed} actions replayed)")
    else:
        differing = [k for k, v in evidence["sections"].items() if not v["matched"]]
        print(f"reward 0: database hash differs (agent {agent_hash[:12]}... vs "
              f"ground truth {gt_hash[:12]}...); differing tables: {differing}; "
              f"replay errors: {errors}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001 - a crash must not look like a measured zero
        traceback.print_exc()
        raise SystemExit(4)
