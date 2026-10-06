#!/usr/bin/env python3
"""The tau-bench check: replay the ground truth, compare database hashes, then
require the episode to be finished and the task's required outputs to have been said.

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
       extracted verbatim from `tau_bench/envs/base.py`;
    5. require the agent's log to contain a `done` record. Upstream only calls
       `calculate_reward` when the episode is `done`
       (`tau_bench/envs/base.py:step`), so an agent that never finishes is not
       scored, however good its database looks;
    6. require, for every string in the task's `outputs`, some recorded `say` whose
       content contains it -- the same test, `output.lower() in
       content.lower().replace(",", "")`, that upstream's
       `RewardOutputInfo` applies to the agent's respond actions.

The reward is `1` only when the hashes match **and** `done` was recorded **and**
every output was found; otherwise `0`.

Evidence
--------
It also writes an evidence JSON naming *why*: whether the whole-database hash
matched and which top-level table differs; `agent_declared_done`; the per-output
found/not-found map plus `r_outputs`, mirroring upstream's `RewardOutputInfo`;
how many ground-truth actions there were and how many replayed; any replay errors
-- both exceptions and the `Error: ...` strings a tool *returns* when it refuses
an action; whether the ground truth changes the database at all (a ground-truth
replay that is a no-op means a no-op agent passes the hash test, so it is worth
saying out loud); and the agent's own log (`/app/tau_calls.jsonl`), split into
tool calls, says and the done declaration.

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
    /app/tau_calls.jsonl      TAU_CALL_LOG     the agent's calls, says and done
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

#: `tau_bench.types.RESPOND_ACTION_NAME`. `tau say` logs its utterance under this
#: name with the text at `arguments["content"]`, which is the shape upstream's
#: `calculate_reward` reads when it checks a task's `outputs`.
RESPOND_ACTION_NAME = "respond"


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


def read_agent_log(path: Path) -> dict:
    """The agent's own log, split into tool calls, says and the done declaration.

    Returns counts and the say contents. It is the agent's file, so a missing or
    malformed one never raises: a malformed line counts as `<unparseable>` and is
    not evidence of anything, and no `done`/`say` record is found in it.
    """
    info = {"log_file": str(path), "log_present": path.is_file(),
            "agent_events": 0, "agent_tool_calls": None,
            "agent_tool_call_counts": {}, "agent_says": [], "agent_say_count": 0,
            "agent_declared_done": False}
    if not path.is_file():
        return info
    counts: Counter = Counter()
    total, says, done = 0, [], False
    for line in path.read_text(errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        total += 1
        try:
            record = json.loads(line)
        except ValueError:
            record = None
        if not isinstance(record, dict):
            counts["<unparseable>"] += 1
            continue
        kind, name = record.get("kind"), record.get("name", "?")
        if kind == "done" or name == "done":
            done = True
        elif kind == "say" or name == RESPOND_ACTION_NAME:
            arguments = record.get("arguments")
            content = arguments.get("content", "") if isinstance(arguments, dict) else ""
            says.append(str(content))
        else:
            counts[name] += 1
    info.update(agent_events=total, agent_tool_calls=sum(counts.values()),
                agent_tool_call_counts=dict(counts), agent_says=says,
                agent_say_count=len(says), agent_declared_done=done)
    return info


def check_outputs(outputs, says) -> tuple[dict, float]:
    """`tau_bench/envs/base.py:calculate_reward`'s outputs rule, applied to `says`.

    Verbatim upstream test, per output: `output.lower()` must appear in some
    respond content after `content.lower().replace(",", "")`. Note the comma
    removal applies to the content only, exactly as upstream wrote it. Returns
    `(found_by_output, r_outputs)`, mirroring upstream's `RewardOutputInfo`.
    """
    found = {}
    for output in outputs:
        found[output] = any(
            str(output).lower() in str(say).lower().replace(",", "")
            for say in says)
    return found, (1.0 if all(found.values()) else 0.0)


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
    outputs = list(gt.get("outputs") or [])
    evidence.update(task_id=gt.get("task_id"), domain=domain,
                    user_id=gt.get("user_id"),
                    ground_truth_actions=len(actions),
                    outputs_required=len(outputs))

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

    # ---- the agent's own log: evidence, and the `done`/`outputs` gates. ----
    log = read_agent_log(paths["call_log"])
    evidence.update(log)
    outputs_found, r_outputs = check_outputs(outputs, log["agent_says"])
    done = log["agent_declared_done"]
    evidence.update(outputs=outputs_found, r_outputs=r_outputs,
                    outputs_satisfied=(r_outputs == 1.0))

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
        write_reward(paths["reward"], 0)
        write_evidence(paths["evidence"], evidence)
        print(f"reward 0: the agent's database could not be read: {exc}")
        return 0

    agent_hash = hash_of(agent_db)
    matched = agent_hash == gt_hash
    reward = int(matched and done and r_outputs == 1.0)
    evidence.update(reward=reward, database_hash_matched=matched,
                    agent_data_hash=agent_hash, agent_db_bytes=len(raw),
                    agent_db_keys=sorted(agent_db),
                    sections=section_comparison(agent_db, clean_db))

    write_reward(paths["reward"], reward)
    write_evidence(paths["evidence"], evidence)

    if reward == 1:
        print(f"reward 1: database hash matches the ground truth "
              f"({gt_hash[:12]}..., {replayed} actions replayed), the agent "
              f"declared done, and all {len(outputs)} required output(s) were said")
        return 0

    reasons = []
    if not matched:
        differing = [k for k, v in evidence["sections"].items() if not v["matched"]]
        reasons.append(f"database hash differs (agent {agent_hash[:12]}... vs "
                       f"ground truth {gt_hash[:12]}...); differing tables: "
                       f"{differing}; replay errors: {errors}")
    if not done:
        reasons.append("the agent never declared done (no `tau done` in "
                       f"{paths['call_log']})")
    if r_outputs != 1.0:
        missing = [o for o, ok in outputs_found.items() if not ok]
        reasons.append(f"required output(s) not said: {missing}")
    print("reward 0: " + "; ".join(reasons))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001 - a crash must not look like a measured zero
        traceback.print_exc()
        raise SystemExit(4)
