"""tau-bench as a dataset: retail to study, airline to be scored on. INTERFACE.md §2.5.9.

    python tools/build_tau_bench_gt.py      # regenerate the committed assets
    driver.py --dataset tau_bench ...

Where the tasks come from
-------------------------
`sierra-research/tau-bench`. The task set is the one each domain's own environment
scores: retail `tasks_test.TASKS_TEST` (115) and airline `tasks_test.TASKS` (50).
The checkout's legacy `tasks.py` files hold a larger, older set (185 / 76) and are
deliberately not used -- `MockRetailDomainEnv`/`MockAirlineDomainEnv` do not read
them either. `tools/build_tau_bench_gt.py` copies each task's ground truth, the
clean database, the policy and the tool implementations into `data/tau_bench/`;
this module only reads those committed assets, so it does not need the checkout on
the machine that runs the dataset.

What a task is
--------------
Tau-bench's task is a *database transaction*, not a conversation: the reward is
`tau_bench.envs.base.Env.calculate_reward()`, which hashes the environment database
after the agent's actions, replays the ground-truth actions on a clean database and
requires the two hashes to be equal -- and it computes that reward only when the
episode is `done`, and additionally requires the agent to have said every string in
the task's `outputs`. The environment here reproduces all three parts:

    the domain's tool implementations, the clean database, the wiki + rules

and the agent's only way to act is the `tau` CLI
(`list` / `call` / `policy` / `say` / `done`). It is one container image
(`harnessgrad/tau-bench:20261006`) for both domains, with `state: "container"`
because the mutated database is the state.

Why SQL/args and not an LLM user simulator
------------------------------------------
There is no scripted user strategy upstream -- only `UserStrategy.HUMAN` and
`UserStrategy.LLM` -- and running an LLM in the environment would make the reward
depend on a second model. It does not have to: the reward compares database states,
and the ground-truth `respond`/read-only steps never touch the database. The user id
is therefore given to the agent in the goal, which removes the need for a simulator
while changing nothing the reward measures. Read-only lookups do not move the hash
either, so an agent that skips the authentication calls is not penalised for it.

How `calculate_reward` is reproduced
------------------------------------
* **Database state.** `verify/check.py` hashes `/app/db.json` with the hash
  functions extracted verbatim from `tau_bench/envs/base.py` and compares it with the
  hash of a clean database after the ground-truth actions are replayed through the
  same tool classes. Terminating actions are not replayed, exactly as upstream:
  `calculate_reward` skips every ground-truth action whose name is in
  `terminate_tools` (`transfer_to_human_agents`), because it does not touch the
  database.
* **Done is required.** Upstream calls `calculate_reward()` only when `Env.step`
  sets `done`. There is no user simulator here that could send `###STOP###`, so
  `tau done` records the agent's declaration in `/app/tau_calls.jsonl` and the check
  requires it: no `done`, reward `0`, however good the database looks.
* **`outputs` is required.** For every string in the task's `outputs`, upstream
  requires some respond content to contain it
  (`output.lower() in content.lower().replace(",", "")`). There is no interactive
  user here, so `tau say '<text>'` records an utterance in the same log and the
  check applies that rule to the recorded says; one missing string is reward `0`.

The split
---------
`train` is retail, `eval` is airline: two different domains, disjoint and covering.
Tau-bench's own retail test set is an exam and declares no train/eval split, so this
one is imposed here and is stated loudly. Both sides are narrowed by the exclusion
below.

Tasks that cannot discriminate
------------------------------
Replaying all 165 ground truths with `measured_no_op_tasks()` shows 31 whose final
database is byte-identical to the clean one. Five of those carry an `outputs`
requirement, and are kept: `say` + `done` still make them discriminate. The other 26
carry none, so after the done gate an agent that calls `tau done` immediately is a
full-credit solution and the task measures nothing about the database work. They are
listed in `EXCLUDED_TASKS` and `load()` never returns them. They cannot merely be
left off `SPLIT`: `data/registry.py` requires every returned task to be on exactly
one side, so an excluded task has to be absent from `load()` entirely. Their
ground-truth files stay in `gt/` -- only the adapter stops returning them.

Counts: 165 staged, 26 excluded, **139 returned** -- `train` 108 retail, `eval` 31
airline. A score on the eval side is a score on 31 of tau-bench's 50 airline test
tasks, not on the retail set the method studied.
"""


from __future__ import annotations


#: See `data/registry.py:KIND_DATASET`. A fixture is platform test material and is
#: deliberately not offered as a choice in the Launch form.
KIND = "dataset"

import json
import os
import sys
from pathlib import Path

#: The committed assets, written by `tools/build_tau_bench_gt.py`. Kept beside this
#: module: `data/tau_bench.py` is the adapter, `data/tau_bench/` is its content.
ASSETS = Path(__file__).resolve().parent / "tau_bench"

GT_DIR = ASSETS / "gt"
DB_DIR = ASSETS / "db"
LIB_DIR = ASSETS / "lib"
CHECK_SCRIPT = ASSETS / "verify" / "check.py"
PROVENANCE = ASSETS / "PROVENANCE.json"

#: The image. Built once from `data/tau_bench/Dockerfile`; the platform does not
#: build or pull during a run (INTERFACE.md §2.5.5), so this must already be local.
IMAGE = os.environ.get("HG_TAU_IMAGE", "harnessgrad/tau-bench:20261006")

WORKDIR = "/app"

#: Where the check's **inputs** are staged inside its container. Top level on purpose --
#: see the note in `_verifier`. The outputs stay in the reward file's directory.
GT_IN_CONTAINER = "/tau-gt.json"
CLEAN_DB_IN_CONTAINER = "/tau-clean-db.json"
CHECK_IN_CONTAINER = "/tau-check.py"
LIB_IN_CONTAINER = "/tau-lib"
REWARD_FILE = "/verifier/reward.txt"
EVIDENCE_FILE = "/verifier/evidence.json"
AGENT_TIMEOUT_S = 900
VERIFY_TIMEOUT_S = 900

#: The order the two domains are listed in, and which side of the split each is on.
#: `train = retail, eval = airline` is the brief and is not derived from anything --
#: the registry checks only that the sides are disjoint and cover every task.
DOMAIN_ORDER = ("retail", "airline")
TRAIN_DOMAINS = ("retail",)
EVAL_DOMAINS = ("airline",)

#: Ground-truth actions upstream does not replay; they do not touch the database.
#: `Mock{Retail,Airline}DomainEnv.terminate_tools`.
TERMINATE_TOOLS = ("transfer_to_human_agents",)

#: Tasks whose ground-truth replay leaves the database unchanged **and** which carry
#: no `outputs` requirement. Such a task cannot discriminate: the database hash
#: already matches before the agent does anything, the done gate is satisfied by an
#: immediate `tau done`, and there is no output to say. They are removed from what
#: `load()` returns -- not merely from `SPLIT`, because `data/registry.py` requires
#: every returned task to be on exactly one side -- while their ground-truth files
#: stay in `gt/` for audit. 7 retail, 19 airline.
#:
#: The list is a measurement, not a guess, and it is kept explicit so `load()` does
#: no replay work. To regenerate it after `tools/build_tau_bench_gt.py` reruns:
#:
#:     python3 -c "import data.tau_bench as t; print(t.measured_no_op_tasks())"
#:
#: which replays every ground truth through the staged tools and keeps the tasks
#: whose `consistent_hash(to_hashable(db))` is unchanged and whose `outputs` is
#: empty -- exactly the comparison `verify/check.py` makes. The 5 no-op tasks that
#: *do* carry `outputs` (airline_044, retail_024, retail_062, retail_067,
#: retail_068) are deliberately not here: `say` + `done` still make them measure.
EXCLUDED_TASKS = (
    "airline_012", "airline_013", "airline_015", "airline_017", "airline_018",
    "airline_021", "airline_024", "airline_029", "airline_035", "airline_036",
    "airline_037", "airline_038", "airline_039", "airline_040", "airline_041",
    "airline_042", "airline_047", "airline_048", "airline_049",
    "retail_010", "retail_012", "retail_025", "retail_050", "retail_057",
    "retail_065", "retail_106",
)

#: One environment for every task: same image, same writable workdir, no network.
#: The tool implementations and the clean database are in the image; the task's own
#: copy of the database is copied into `/app` by `SETUP`, so the agent mutates a file
#: in its writable state rather than a read-only image path.
ENV_BASE: dict = {
    "kind": "exec",
    "image": IMAGE,
    "workdir": WORKDIR,
    "state": "container",
    "network": "none",
    "cpus": 2,
    "memory_mb": 4096,
    "placement": "inside",
    "services": [],
    "agent_timeout_s": AGENT_TIMEOUT_S,
    "verify_timeout_s": VERIFY_TIMEOUT_S,
}
DEFAULT_ENV = ENV_BASE


def _read_gt() -> list[dict]:
    if not GT_DIR.is_dir():
        raise ValueError(
            f"no tau-bench ground truth under {GT_DIR}. Generate it with:\n"
            f"    python tools/build_tau_bench_gt.py")
    records = []
    for path in sorted(GT_DIR.glob("*.json")):
        records.append(json.loads(path.read_text()))
    if not records:
        raise ValueError(f"{GT_DIR} is empty; run tools/build_tau_bench_gt.py")
    records.sort(key=lambda r: (DOMAIN_ORDER.index(r["domain"]), r["index"]))
    return records


#: Read once at import. `load()` is called more than once per run and the content is
#: immutable, so re-reading 165 files per call would be work with no effect.
#: `_ALL_GT` is everything on disk (the excluded tasks' files are kept); `_GT` is what
#: this dataset returns. The excluded ids are validated against the files rather than
#: recomputed: regenerating the list is a documented manual step (see above).
_ALL_GT: list[dict] = _read_gt()
_unknown_excluded = set(EXCLUDED_TASKS) - {record["task_id"] for record in _ALL_GT}
if _unknown_excluded:
    raise ValueError(
        f"tau_bench: EXCLUDED_TASKS names task(s) with no ground truth: "
        f"{sorted(_unknown_excluded)}; regenerate it with measured_no_op_tasks()")
_GT: list[dict] = [record for record in _ALL_GT
                   if record["task_id"] not in EXCLUDED_TASKS]
_BY_ID: dict[str, dict] = {record["task_id"]: record for record in _GT}


def _goal(record: dict) -> str:
    """The instruction, with a clearly-labelled preamble naming only the interface.

    Nothing here hints at the answer. It states the user id (which the reward makes
    free -- see the module docstring), the policy is readable with `tau policy`, and
    the CLI is how the task is acted on.
    """
    domain = record["domain"]
    return (
        f"# Task\n"
        f"\n"
        f"You are the {domain} customer-service agent. The user is not simulated: the\n"
        f"conversation has already happened, and your job is to carry out the database\n"
        f"work it calls for by calling the domain's tools.\n"
        f"\n"
        f"## How to act\n"
        f"\n"
        f"- You act on the database by calling tools through the `tau` command.\n"
        f"- You are acting for the user whose id is `{record['user_id']}`.\n"
        f"- Read the policy you must follow first: `tau policy`.\n"
        f"- List the available tools and their argument schemas: `tau list`.\n"
        f"- Call one tool at a time and read its observation:\n"
        f"      tau call <tool_name> '<json-arguments>'\n"
        f"- There is no interactive user here. Anything you need to tell the user goes\n"
        f"  through:\n"
        f"      tau say '<text>'\n"
        f"  and no reply will come back.\n"
        f"- When the task is finished, call `tau done`. The task is not treated as\n"
        f"  finished until you do, and it is not scored before then.\n"
        f"- The database is `/app/db.json` in your working directory. `tau call` reads\n"
        f"  it, applies the tool and writes it back, so a tool call survives the\n"
        f"  command; keep the file valid JSON if you touch it by any other means.\n"
        f"- Every fact about the database (ids, prices, availability, balances) must\n"
        f"  come from a tool observation. Do not invent values.\n"
        f"\n"
        f"## The user's request\n"
        f"\n"
        f"{record['instruction'].strip()}\n"
    )


def _db_path(domain: str) -> Path:
    return DB_DIR / f"{domain}.json"


def measured_no_op_tasks() -> list[str]:
    """Recompute `EXCLUDED_TASKS` by replaying every ground truth. Manual step only.

    Deliberately not called by `load()`: `load()` reads committed assets, and a
    replay at import time would make the task list depend on the checkout's tools at
    the moment of import. Run:

        python3 -c "import data.tau_bench as t; print(t.measured_no_op_tasks())"

    For each task: replay its non-terminating ground-truth actions through the staged
    tool classes on a fresh copy of the clean database, then keep the task when
    `consistent_hash(to_hashable(db))` is unchanged **and** `outputs` is empty --
    the same hash comparison and the same non-discriminating condition the check and
    the module docstring describe.
    """
    import importlib
    if str(LIB_DIR) not in sys.path:
        sys.path.insert(0, str(LIB_DIR))
    from tau_bench.envs.hash import consistent_hash, to_hashable

    def hash_of(value) -> str:
        return consistent_hash(to_hashable(value))

    tools_by_domain: dict[str, dict] = {}
    for domain in DOMAIN_ORDER:
        module = importlib.import_module(f"tau_bench.envs.{domain}.tools")
        tools_by_domain[domain] = {cls.get_info()["function"]["name"]: cls
                                   for cls in module.ALL_TOOLS}

    no_op = []
    for record in _ALL_GT:
        domain = record["domain"]
        db = json.loads(_db_path(domain).read_text())
        before = hash_of(db)
        for action in record["actions"]:
            if action.get("name") in TERMINATE_TOOLS:
                continue
            tool = tools_by_domain[domain].get(action["name"])
            if tool is None:
                continue
            try:
                tool.invoke(db, **action.get("arguments", {}))
            except Exception:  # noqa: BLE001 - a refused action is not a hash change
                pass
        if hash_of(db) == before and not (record.get("outputs") or []):
            no_op.append(record["task_id"])
    return no_op


def _setup(record: dict) -> dict:
    """`/app/db.json` -- the clean database, visible to the agent, which mutates it."""
    return {"files": [{"path": "db.json",
                       "from": str(_db_path(record["domain"]))}]}


def _verifier(record: dict) -> dict:
    """The check and everything it needs, copied in **after** the agent stops.

    The ground truth is an input rather than an image file: an image is built once,
    before any run, and a `VERIFY.inputs` entry is materialized only at verification
    time, so the answer is not on the filesystem the agent explored. The tool library
    and the clean database travel the same way, which also means the replay cannot be
    steered by anything the agent changed inside the container -- the snapshot supplies
    the agent's database and nothing else the check trusts.
    """
    tid = record["task_id"]
    return {
        "kind": "command",
        "argv": ["python3", CHECK_IN_CONTAINER],
        # **Top level, not `/verifier/...`, and that is not cosmetic.** The platform
        # copies these in *before* it starts the check's container, and it creates the
        # reward file's directory only *after* starting it (see `mkdir_in` in
        # `eval/verifier.py`). `docker cp <file> <ctr>:/a/b/c` therefore fails with
        # `Could not find the file /a/b` when the destination is nested and nothing has
        # made the parent yet. A top-level destination has `/` as its parent, which always
        # exists. Measured 2026-10-06: `/verifier/gt.json` failed the whole run with
        # `ContainerUnavailable: could not copy ... Could not find the file /verifier`.
        # The outputs stay under `/verifier` because by then the platform has created it.
        "inputs": [
            {"dst": GT_IN_CONTAINER, "from": str(GT_DIR / f"{tid}.json")},
            {"dst": CLEAN_DB_IN_CONTAINER,
             "from": str(_db_path(record["domain"]))},
            {"dst": CHECK_IN_CONTAINER, "from": str(CHECK_SCRIPT)},
            {"dst": LIB_IN_CONTAINER, "from": str(LIB_DIR)},
        ],
        "reward_file": REWARD_FILE,
        "evidence_file": EVIDENCE_FILE,
        "timeout_s": VERIFY_TIMEOUT_S,
    }


def load() -> tuple[list[dict], dict[str, str]]:
    """`(tasks, scorable)`. Every task is graded by its `VERIFY` entry, so the
    `scorable` map is present only because the interface asks for it."""
    tasks = [{"task_id": record["task_id"],
              "goal": _goal(record),
              "inputs": []}
             for record in _GT]
    return tasks, {record["task_id"]: "" for record in _GT}


ENV: dict[str, dict] = {record["task_id"]: dict(ENV_BASE) for record in _GT}
SETUP: dict[str, dict] = {record["task_id"]: _setup(record) for record in _GT}
VERIFY: dict[str, dict] = {record["task_id"]: _verifier(record) for record in _GT}

_ids_by_domain: dict[str, list[str]] = {domain: [] for domain in DOMAIN_ORDER}
for _record in _GT:
    _ids_by_domain[_record["domain"]].append(_record["task_id"])

SPLIT = {
    "train": [tid for domain in TRAIN_DOMAINS for tid in _ids_by_domain[domain]],
    "eval": [tid for domain in EVAL_DOMAINS for tid in _ids_by_domain[domain]],
}


def downloads() -> list[dict]:
    """What a reader must fetch to rebuild this dataset's committed assets.

    Tau-bench's ground truth is **committed** under `data/tau_bench/` -- the adapter
    reads that, not the checkout -- so this dataset runs on a machine with nothing
    fetched at all. The entry below describes the upstream source the committed bytes
    were derived from, pinned to the commit recorded in `PROVENANCE.json`, and
    `tools/build_tau_bench_gt.py` is what turns it back into `gt/`, `db/`, `policy/`
    and `lib/`. `tools/datasets.py --write` renders it into `DOWNLOADS.md` from here,
    so there is one list rather than a document that can drift from the loader.
    """
    try:
        commit = json.loads(PROVENANCE.read_text()).get("checkout_commit") or "unknown"
    except (OSError, ValueError):
        commit = "unknown"
    return [{
        "kind": "http",
        "name": "tau-bench checkout (regenerates the committed assets)",
        "version": commit,
        "url": f"https://github.com/sierra-research/tau-bench/archive/{commit}.tar.gz",
        "size": "~67 MB unpacked",
        "dst": "/mnt/20t/xubuqiang/datasets/tau-bench",
        "extract_to": ".",
        "note": "Only needed to REGENERATE `data/tau_bench/`: the adapter reads the "
                "committed assets, which are already in git. Pinned to the commit in "
                "PROVENANCE.json -- never a branch.",
    }]
