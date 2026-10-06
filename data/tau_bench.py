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
requires the two hashes to be equal. So the environment here is:

    the domain's tool implementations, the clean database, the wiki + rules

and the agent's only way to act is the `tau` CLI (list / call / policy). It is one
container image (`harnessgrad/tau-bench:20261006`) for both domains, with
`state: "container"` because the mutated database is the state.

Why SQL/args and not an LLM user simulator
------------------------------------------
There is no scripted user strategy upstream -- only `UserStrategy.HUMAN` and
`UserStrategy.LLM` -- and running an LLM in the environment would make the reward
depend on a second model. It does not have to: the reward compares database states,
and the ground-truth `respond`/read-only steps never touch the database. The user id
is therefore given to the agent in the goal, which removes the need for a simulator
while changing nothing the reward measures. Read-only lookups do not move the hash
either, so an agent that skips the authentication calls is not penalised for it.

Two deliberate differences from `calculate_reward`
--------------------------------------------------
* **`outputs` is ignored.** `calculate_reward` also requires the final `respond`
  message to contain some literal strings. That check is about the conversation, and
  there is no conversation here (no `respond` action, no user), so the reward is the
  database-hash comparison alone -- the part of tau-bench's rule this environment can
  actually measure. `VERIFY` therefore never awards a fraction of a point for prose.
* **Terminating actions are not replayed**, exactly as upstream: `calculate_reward`
  replays every ground-truth action whose name is not in `terminate_tools`
  (`transfer_to_human_agents`), because it does not touch the database.

The split
---------
`train` is retail, `eval` is airline: 115 and 50 tasks, disjoint and covering, two
different domains. Tau-bench's own retail test set is an exam and declares no
train/eval split, so this one is imposed here and is stated loudly: a score on the
eval side is a score on tau-bench's airline test set (all 50 of it), not on the
retail set the method studied.
"""
from __future__ import annotations

import json
import os
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
_GT: list[dict] = _read_gt()
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
        f"- You are acting for the user whose id is `{record['user_id']}`.\n"
        f"- Read the policy you must follow first: `tau policy`.\n"
        f"- List the available tools and their argument schemas: `tau list`.\n"
        f"- Call one tool at a time and read its observation:\n"
        f"      tau call <tool_name> '<json-arguments>'\n"
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
        "argv": ["python3", "/verifier/check.py"],
        "inputs": [
            {"dst": "/verifier/gt.json", "from": str(GT_DIR / f"{tid}.json")},
            {"dst": "/verifier/clean_db.json",
             "from": str(_db_path(record["domain"]))},
            {"dst": "/verifier/check.py", "from": str(CHECK_SCRIPT)},
            {"dst": "/verifier/lib", "from": str(LIB_DIR)},
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
