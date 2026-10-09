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

2. **Judged** -- the capability domain, and nothing else. There is no program that can decide
   whether `chessbench_puzzles` is "planning" or "games", and pretending otherwise buys a rule
   nobody follows. So it is declared once, here, in `CAPABILITY`, and this tool is its reader:
   it refuses a published dataset with no domain and a domain outside the vocabulary, which is
   what keeps the list total as datasets are added.

3. **Measured** -- cost, difficulty and headroom. Only a run knows these; they live in the
   curve points and in `tools/task_difficulty.py`'s per-dataset JSON, never in this file.

Usage:

    python3 tools/dataset_classes.py                # the table
    python3 tools/dataset_classes.py --json         # the same, for another program
    python3 tools/dataset_classes.py --domain planning
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

#: The judged axis: one domain per published dataset. The vocabulary is closed on purpose --
#: an open one grows a synonym per author and stops being usable for selection.
CAPABILITY = {
    "alfworld": "embodied_text",
    "agentdojo": "agent_security",
    "bfcl_v3": "tool_calling",
    "chessbench_puzzles": "planning_and_search",
    "ds1000": "code_generation",
    "gsm8k": "reasoning",
    "reasoning_gym": "reasoning",
    "jericho": "interactive_fiction",
    "musique": "information_seeking",
    "twowikimultihopqa": "information_seeking",
    "livecodebench": "code_generation",
    "appworld": "tool_dialogue",
    "bird_minidev": "text_to_sql",
    "physicsquestions": "reasoning",
    "scienceworld": "science_simulation",
    "sportsunderstanding": "reasoning",
    "spreadsheetbench": "spreadsheet",
    "strategyqa": "reasoning",
    "tau_bench": "tool_dialogue",
    "terminal_bench": "terminal",
    "triviaqa": "information_seeking",
    "gaia": "information_seeking",
    # Refused datasets still have a domain: the classification is about what the benchmark
    # measures, and a refusal is a statement about this platform's contract, not about it.
    "api_bank": "tool_calling",
    "fever": "information_seeking",
    "hotpotqa": "information_seeking",
    "nestful": "tool_calling",
    "sotuqa": "information_seeking",
    "tau2_bench": "tool_dialogue",
}

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
    row = {
        "dataset": name,
        "domain": CAPABILITY.get(name),
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
    surface = []
    acts = False
    for script in scripts:
        verbs = _declared_verbs(script)
        if not verbs:
            raise SystemExit(
                f"{name}: {script} declares no verb set that this tool can read. Its CLI uses "
                f"a spelling not covered by _VERB_PATTERNS, so the interaction axis cannot be "
                f"derived for it. Add the spelling (and decide which of its verbs mean "
                f"'act') rather than defaulting the dataset to single_shot.")
        surface.append(f"{script.name}[{','.join(sorted(verbs))}]")
        if verbs & set(ACT_VERBS):
            acts = True
    row["action_surface"] = surface
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
            f"{row['env_kinds']}, action surface {surface}) but EXPECTED_INTERACTION says "
            f"{declared!r}. Neither side is overwritten automatically: decide which is right, "
            f"then fix the other.")
    return row


def classify_all() -> list[dict]:
    rows = [classify(name) for name in registry.published()]
    unknown = [r["dataset"] for r in rows if r["domain"] not in set(CAPABILITY.values())]
    if unknown:
        raise SystemExit(
            f"these published datasets have no capability domain (or one outside the "
            f"vocabulary): {unknown}. Add them to CAPABILITY in {Path(__file__).name}.")
    missing = sorted(set(CAPABILITY) - {r['dataset'] for r in rows})
    if missing:
        raise SystemExit(f"CAPABILITY names datasets that are not published: {missing}")
    return rows


def _table(rows: list[dict]) -> str:
    head = (f"{'dataset':20s} {'domain':20s} {'interaction':12s} {'env':8s} "
            f"{'verify':9s} {'tasks':>6s} {'train':>6s} {'eval':>6s}")
    out = [head, "-" * len(head)]
    for r in rows:
        env = ",".join(r["env_kinds"]) or "-"
        ver = ",".join(r["verifier_kinds"]) or "-"
        out.append(f"{r['dataset']:20s} {str(r['domain']):20s} {str(r['interaction']):12s} "
                   f"{env:8s} {ver:9s} {r['tasks']:>6d} {r['train']:>6d} {r['eval']:>6d}")
    closed = [r["dataset"] for r in rows if r["interaction"] == "closed_loop"]
    once = [r["dataset"] for r in rows if r["interaction"] == "single_shot"]
    out += [
        "",
        f"closed_loop ({len(closed)}): {', '.join(closed)}",
        f"single_shot ({len(once)}): {', '.join(once)}",
        "",
        "domains:",
    ]
    for domain in sorted({r["domain"] for r in rows}):
        names = [r["dataset"] for r in rows if r["domain"] == domain]
        out.append(f"  {domain:20s} {len(names):2d}  {', '.join(names)}")
    return "\n".join(out)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--domain", help="only this capability domain")
    parser.add_argument("--interaction", choices=["closed_loop", "single_shot"])
    parser.add_argument("--runnable-only", action="store_true",
                        help="drop the datasets that refuse")
    args = parser.parse_args(argv)

    rows = classify_all()
    if args.domain:
        rows = [r for r in rows if r["domain"] == args.domain]
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
