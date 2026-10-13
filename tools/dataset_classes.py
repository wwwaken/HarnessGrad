#!/usr/bin/env python3
"""Classify the published datasets, deriving everything a program can decide.

Why a program and not a table someone maintains
-----------------------------------------------
A classification rots the moment it is a hand-written list beside code that can contradict
it. So the axes split into three kinds, and only the middle one is a judgement:

1. **Derived** -- read out of the adapter and the agent-facing CLI. The environment kind, the
   verifier kind, the action surface (the verbs the shipped CLI exposes), the task counts and
   the split sizes. If any of these changed, re-running this tool produces the new answer;
   nothing has to be remembered. The decisive one is `interaction`: a dataset whose CLI
   exposes a `do`-style verb makes the agent act repeatedly and observe each result, and one
   whose CLI only submits an artefact cannot. That is a fact about the shipped program, so it
   is derived rather than declared -- a declared "this is a closed loop" flag would be the
   first field to go stale.

2. **Judged** -- the capability axis, and nothing else: one `(demand, surface)` pair per
   published dataset, declared once in `CAPABILITY`. There is no program that can decide
   whether `chessbench_puzzles` is "reasoning" or "games", and pretending otherwise buys a
   rule nobody follows. What a program *can* enforce is that the vocabulary stays closed and
   total, so this tool refuses a published dataset with no entry or an entry outside the
   vocabulary, and it refuses a demand thin enough to be a private name for one dataset.

   The axis has two levels because one flat list mixed four different kinds of statement.
   `demand` is what the task asks of the Harness, which is the level a transfer claim is
   phrased on ("improvements move within evidence and not to environment"). `surface` is
   where that demand is exercised, which is what tooling is chosen from. The flat list had
   `code_generation`, `text_to_sql`, `spreadsheet` and `terminal` as four top-level peers --
   four surfaces of two demands -- and `tool_calling` beside `tool_dialogue`, which restated
   an axis the derivation below already owns.

3. **Measured** -- cost, difficulty and headroom. Only a run knows these; they live in the
   curve points and in `tools/task_difficulty.py`'s per-dataset JSON, never in this file.

Usage:

    python3 tools/dataset_classes.py                # the table
    python3 tools/dataset_classes.py --json         # the same, for another program
    python3 tools/dataset_classes.py --demand reasoning
    python3 tools/dataset_classes.py --surface terminal
    python3 tools/dataset_classes.py --adversarial
    python3 tools/dataset_classes.py --interaction closed_loop
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data import registry  # noqa: E402

#: Level 1 of the judged axis: the demand the task places on the Harness. Closed, and printed
#: in this order. A demand names something the Harness must provide, which is why a transfer
#: claim can be stated over it: the Harness either carries external evidence across steps or
#: it does not, and that is a property of the artefact under improvement rather than of a
#: benchmark's subject matter.
DEMANDS = ("evidence", "reasoning", "tool_use", "artifact", "environment")

#: Level 2 of the judged axis: the surface the demand is exercised on. Kept because a SQL task
#: and a spreadsheet task stress different tools even though both deliver an artefact, but a
#: surface is a leaf, so a surface with one member is a fact about coverage rather than a
#: defect in the taxonomy.
#:
#: The judged entry for a dataset is its single `(demand, surface)` pair. One mapping rather
#: than two so the levels cannot drift apart: there is no way to add a dataset to a demand and
#: forget its surface, which a second dict keyed by the same names would allow.
CAPABILITY: dict[str, tuple[str, str]] = {
    "alfworld": ("environment", "embodied_text"),
    "agentdojo": ("tool_use", "tool_dialogue"),
    "bfcl_v3": ("tool_use", "tool_calling"),
    "chessbench_puzzles": ("reasoning", "planning_and_search"),
    "ds1000": ("artifact", "code_generation"),
    "gsm8k": ("reasoning", "reasoning"),
    "reasoning_gym": ("reasoning", "reasoning"),
    "jericho": ("environment", "interactive_fiction"),
    "musique": ("evidence", "information_seeking"),
    "twowikimultihopqa": ("evidence", "information_seeking"),
    "livecodebench": ("artifact", "code_generation"),
    "appworld": ("tool_use", "tool_dialogue"),
    "bird_minidev": ("artifact", "text_to_sql"),
    "physicsquestions": ("reasoning", "reasoning"),
    "scienceworld": ("environment", "science_simulation"),
    "sportsunderstanding": ("reasoning", "reasoning"),
    "spreadsheetbench": ("artifact", "spreadsheet"),
    "strategyqa": ("reasoning", "reasoning"),
    "tau_bench": ("tool_use", "tool_dialogue"),
    "terminal_bench": ("environment", "terminal"),
    "triviaqa": ("evidence", "information_seeking"),
    "gaia": ("evidence", "information_seeking"),
    # Refused datasets still have an entry: the classification is about what the benchmark
    # measures, and a refusal is a statement about this platform's contract, not about it.
    "api_bank": ("tool_use", "tool_calling"),
    "fever": ("evidence", "information_seeking"),
    "hotpotqa": ("evidence", "information_seeking"),
    "nestful": ("tool_use", "tool_calling"),
    "sotuqa": ("evidence", "information_seeking"),
    "tau2_bench": ("tool_use", "tool_dialogue"),
}

#: A condition, not a capability, and therefore not a level of the judged axis. `agentdojo`
#: runs bank, email and travel tool dialogues with an injected adversary, so its demand and
#: surface are the ordinary ones and what distinguishes it is the threat model. Carrying it as
#: its own demand would have said nothing about what the Harness must provide, while occupying
#: a top-level bucket with a single member: a demand named after the dataset it contains.
#:
#: As a flag it composes, and the claim it supports is the sharper one -- an improvement that
#: survives the ordinary dialogue may still fail here, which is a transfer result rather than
#: a category.
ADVERSARIAL = frozenset({"agentdojo"})

#: A CLI verb that means "act, then observe the result". Its presence is the difference
#: between a dataset a scaffold can iterate inside and one it can only answer once.
#:
#: The vocabulary is closed and each entry names where it came from: `alf`, `scw` and `jer`
#: expose `do "<action>"`, and `dojo` exposes `call '<json>'`. A dataset that ships a *new*
#: action verb therefore fails the check below rather than being silently misclassified --
#: which is what happened to `agentdojo` when this list held only `do`.
ACT_VERBS = ("do", "call")

#: The judged value, declared, and asserted equal to the derived one by `classify_all()`.
#: Two independent sources that must agree: if a shipped CLI changes its surface, or someone
#: edits this map, the tool stops and someone looks. A single source would have hidden the
#: `agentdojo` mistake above; the derived side is what caught it.
EXPECTED_INTERACTION = {
    "agentdojo": "closed_loop",
    "alfworld": "closed_loop",
    "bfcl_v3": "single_shot",
    "chessbench_puzzles": "single_shot",
    "ds1000": "single_shot",
    "fever": "single_shot",
    "hotpotqa": "single_shot",
    "gsm8k": "single_shot",
    "jericho": "closed_loop",
    "musique": "single_shot",
    "reasoning_gym": "single_shot",
    "twowikimultihopqa": "single_shot",
    "livecodebench": "single_shot",
    "bird_minidev": "single_shot",
    "physicsquestions": "single_shot",
    "scienceworld": "closed_loop",
    "sportsunderstanding": "single_shot",
    "spreadsheetbench": "single_shot",
    "strategyqa": "single_shot",
    "tau_bench": "closed_loop",
    "terminal_bench": "closed_loop",
    "appworld": "closed_loop",
    "triviaqa": "single_shot",
    "gaia": "closed_loop",
}

#: How few datasets make a demand a private name for one benchmark rather than a category.
#: Enforced below so the flat list's failure mode -- thirteen buckets, seven of them holding
#: one dataset each -- cannot come back one dataset at a time.
MIN_MEMBERS_PER_DEMAND = 2

_ACT_PATTERN = re.compile(
    r"^\s*(?:python3\s+\S+\s+)?(?:" + "|".join(ACT_VERBS) + r")\b", re.M)

#: How a shipped CLI declares its verb set. Both spellings are declarations *in the program*,
#: which is why they are read instead of the prose in the module docstring: `dojo` documents
#: "tools, call, and submit" in a sentence and lists them in `choices`, and the sentence is not
#: a thing a program can rely on.
_VERB_PATTERNS = (
    re.compile(r"choices\s*=\s*\[([^\]]*)\]"),
    re.compile(r"""command\s*==\s*["']([a-z_]+)["']"""),
)


def _declared_verbs(source: Path) -> set[str]:
    """The verbs a CLI declares in its own argument handling.

    An empty set is a hard failure rather than a default: a third spelling means a human has
    to look, and a silent `single_shot` is exactly the mistake this axis already made once.
    """
    text = source.read_text(encoding="utf-8", errors="replace")
    verbs: set[str] = set()
    for pattern in _VERB_PATTERNS:
        for match in pattern.finditer(text):
            verbs |= {v.strip().strip("\"'") for v in match.group(1).split(",") if v.strip()}
    return {v for v in verbs if v}


def _first(mapping):
    return mapping[list(mapping)[0]] if isinstance(mapping, dict) and mapping else None


def _cli_scripts(module, task_id: str) -> list[Path]:
    """The agent-facing programs a dataset ships.

    The rule is the layout convention this repository actually follows, not a file extension
    and not the executable bit -- measured: `data/qa/cli/qa` is mode 0600 while
    `data/alfworld/cli/alf` is 0711, so the bit cannot decide, and `dojo.py` carries a `.py`
    extension while `alf` does not, so neither can a suffix. Every agent-facing program here
    lives under a `cli/` directory or is materialized under a `bin/` directory.
    """
    out = []
    for entry in (module.SETUP.get(task_id) or {}).get("files", []):
        rel = entry.get("path", "")
        source = entry.get("from")
        if not source:
            continue
        if "bin" in Path(rel).parts or "cli" in Path(source).parts:
            path = Path(source)
            if path.is_file():
                out.append(path)
    return out


def classify(name: str) -> dict:
    module = registry.importlib.import_module(f"data.{name}")
    refused = getattr(module, "REFUSED", None)
    demand, surface = CAPABILITY.get(name, (None, None))
    row = {
        "dataset": name,
        "demand": demand,
        "surface": surface,
        "adversarial": name in ADVERSARIAL,
        "refused": bool(refused),
        "env_kinds": sorted({v.get("kind") for v in module.ENV.values()}) if getattr(module, "ENV", None) else [],
        # A refusal declares no tasks on purpose, so the contract axes are inapplicable.
        "verifier_kinds": [],
        "interaction": None,
        "action_surface": [],
        "tasks": 0,
        "train": 0,
        "eval": 0,
    }
    if refused:
        row["interaction"] = "n/a (refused)"
        return row
    tasks = module.load()[0]
    task_id = tasks[0]["task_id"]
    row["verifier_kinds"] = sorted({v["kind"] for v in module.VERIFY.values()})
    scripts = _cli_scripts(module, task_id)
    surface_names = []
    acts = False
    for script in scripts:
        verbs = _declared_verbs(script)
        if not verbs:
            raise SystemExit(
                f"{name}: {script} declares no verb set that this tool can read. Its CLI uses "
                f"a spelling not covered by _VERB_PATTERNS, so the interaction axis cannot be "
                f"derived for it. Add the spelling (and decide which of its verbs mean "
                f"'act') rather than defaulting the dataset to single_shot.")
        surface_names.append(f"{script.name}[{','.join(sorted(verbs))}]")
        if verbs & set(ACT_VERBS):
            acts = True
    row["action_surface"] = surface_names
    if "exec" in row["env_kinds"]:
        row["interaction"] = "closed_loop"
    elif acts:
        row["interaction"] = "closed_loop"
    else:
        row["interaction"] = "single_shot"
    row["tasks"] = len(tasks)
    row["train"] = len(module.SPLIT["train"])
    row["eval"] = len(module.SPLIT["eval"])
    declared = EXPECTED_INTERACTION.get(name)
    if declared != row["interaction"]:
        raise SystemExit(
            f"{name}: the shipped program says {row['interaction']!r} (env "
            f"{row['env_kinds']}, action surface {surface_names}) but EXPECTED_INTERACTION "
            f"says {declared!r}. Neither side is overwritten automatically: decide which is "
            f"right, then fix the other.")
    return row


def _check_judged_axis(rows: list[dict]) -> None:
    """The judged axis has to stay closed, total, and coarse enough to be a taxonomy.

    Every refusal here is a statement about the vocabulary, so it names the dataset and what
    to add to `CAPABILITY`. Silence is what this replaces: the flat list grew two singleton
    buckets per new benchmark because nothing objected.
    """
    unknown = [r["dataset"] for r in rows
               if not r["demand"] or not r["surface"] or r["demand"] not in DEMANDS]
    if unknown:
        raise SystemExit(
            f"these published datasets have no judged entry, or a demand outside the "
            f"vocabulary: {unknown}. Add them to CAPABILITY in {Path(__file__).name}.")
    missing = sorted(set(CAPABILITY) - {r["dataset"] for r in rows})
    if missing:
        raise SystemExit(f"CAPABILITY names datasets that are not published: {missing}")

    # A surface belongs to exactly one demand, or it is not a leaf and the levels overlap.
    owners: dict[str, set[str]] = {}
    for demand, surface in CAPABILITY.values():
        owners.setdefault(surface, set()).add(demand)
    shared = {s: sorted(d) for s, d in owners.items() if len(d) > 1}
    if shared:
        raise SystemExit(
            f"these surfaces appear under more than one demand: {shared}. A surface is a leaf, "
            f"so either merge the demands or split the surface.")

    # And a demand has to be a category rather than a private name for one dataset.
    counts = {d: sum(1 for r in rows if r["demand"] == d) for d in DEMANDS}
    unused = [d for d in DEMANDS if counts[d] == 0]
    if unused:
        raise SystemExit(f"these demands have no datasets: {unused}. Drop them from DEMANDS.")
    thin = {d: n for d, n in counts.items() if n < MIN_MEMBERS_PER_DEMAND}
    if thin:
        raise SystemExit(
            f"these demands hold fewer than {MIN_MEMBERS_PER_DEMAND} datasets: {thin}. The "
            f"flat vocabulary this replaced ended with seven one-dataset buckets; a new "
            f"benchmark either belongs to an existing demand or the demand is wrong.")


def classify_all() -> list[dict]:
    rows = [classify(name) for name in registry.published()]
    _check_judged_axis(rows)
    return rows


def _table(rows: list[dict]) -> str:
    head = (f"{'dataset':20s} {'demand':11s} {'surface':20s} {'interaction':12s} "
            f"{'env':8s} {'verify':9s} {'tasks':>6s} {'train':>6s} {'eval':>6s}")
    out = [head, "-" * len(head)]
    for r in rows:
        env = ",".join(r["env_kinds"]) or "-"
        ver = ",".join(r["verifier_kinds"]) or "-"
        mark = " *" if r["adversarial"] else ""
        out.append(f"{r['dataset']:20s} {str(r['demand']):11s} {str(r['surface']):20s} "
                   f"{str(r['interaction']):12s} {env:8s} {ver:9s} "
                   f"{r['tasks']:>6d} {r['train']:>6d} {r['eval']:>6d}{mark}")
    closed = [r["dataset"] for r in rows if r["interaction"] == "closed_loop"]
    once = [r["dataset"] for r in rows if r["interaction"] == "single_shot"]
    out += [
        "",
        f"closed_loop ({len(closed)}): {', '.join(closed)}",
        f"single_shot ({len(once)}): {', '.join(once)}",
        "",
        "demands:",
    ]
    for demand in DEMANDS:
        names = [r["dataset"] for r in rows if r["demand"] == demand]
        if not names:
            continue
        surfaces = []
        for surface in dict.fromkeys(r["surface"] for r in rows if r["demand"] == demand):
            n = sum(1 for r in rows if r["surface"] == surface)
            surfaces.append((n, surface))
        surfaces.sort(key=lambda item: (-item[0], item[1]))
        out.append(f"  {demand:12s} {len(names):2d}  "
                   f"[{', '.join(f'{s} {n}' for n, s in surfaces)}]")
    adversarial = [r["dataset"] for r in rows if r["adversarial"]]
    out.append(f"  {'adversarial':12s} {len(adversarial):2d}  {', '.join(adversarial) or '-'}"
               f"   (* in the table above; a condition, not a demand)")
    return "\n".join(out)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--demand", choices=DEMANDS, help="only this demand")
    parser.add_argument("--surface", help="only this surface")
    parser.add_argument("--adversarial", action="store_true",
                        help="only datasets carrying an injected adversary")
    parser.add_argument("--interaction", choices=["closed_loop", "single_shot"])
    parser.add_argument("--runnable-only", action="store_true",
                        help="drop the datasets that refuse")
    args = parser.parse_args(argv)

    rows = classify_all()
    if args.demand:
        rows = [r for r in rows if r["demand"] == args.demand]
    if args.surface:
        rows = [r for r in rows if r["surface"] == args.surface]
    if args.adversarial:
        rows = [r for r in rows if r["adversarial"]]
    if args.interaction:
        rows = [r for r in rows if r["interaction"] == args.interaction]
    if args.runnable_only:
        rows = [r for r in rows if not r["refused"]]
    if args.json:
        print(json.dumps(rows, indent=1, sort_keys=True))
    else:
        print(_table(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
