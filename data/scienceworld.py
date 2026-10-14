r"""ScienceWorld as a dataset: an interactive science-lab environment whose reward is the
JVM's own goal score. INTERFACE.md §2.5.9.

    python3 tools/datasets.py --fetch --dataset scienceworld
    python3 data/scienceworld/control.py --oracle
    python3 data/scienceworld/control.py --oracle --platform
    driver.py --dataset scienceworld ...

Where the tasks come from
-------------------------
`allenai/ScienceWorld`, the `scienceworld` package pinned at **1.2.3**. The wheel is the
whole environment: `setup.py` declares `package_data={'scienceworld': [JAR_FILE, ...]}`
and ships `scienceworld.jar` (7.5 MB), `tasks.json` and `object_type_ids.tsv`, so there is
**no separate data download** -- the pip pin carries everything, and the run needs a JVM
(see `lib/scw_env.py` and the JRE entry in `downloads()`).

The task set is the benchmark's own test fold
---------------------------------------------
Measured by enumeration through the package's API (`get_task_names()` and
`get_max_variations()`): **30 task types, 7,207 variations in total**, from
`inclined-plane-friction-named-surfaces` (1386) down to `identify-life-stages-2` (10) and
`boil` (30). That number is a **generation limit, not an evaluation protocol**: it is how
many worlds the environment can build, not the set anybody scores on.

The evaluation protocol is in the repository's own `goldpaths/goldpaths-all.zip`, which
marks every reference solution with a `train` / `dev` / `test` fold:

    measured over the archive: 6,907 paths
      train 3,442   dev 1,721   test 1,744
      test paths span all 29 task types that have gold paths

This adapter returns **the `test` fold**, one task per variation. That is a choice, and it is
named here rather than implied: the archive does not ship with the package, so "the official
test split" is a decision to read it and follow it. The alternative -- every variation the
environment can generate -- mixes the folds the benchmark separated and inflates the task
count with worlds the evaluation never uses.

**The fold's identity is transcribed into git, not fetched.** `raw.githubusercontent.com` is
blocked on this host and a branch URL is not a pin, so the archive itself cannot be
provisioned reproducibly; `data/scienceworld/test_fold.json` carries the 1,744
`(task_name, variation)` pairs and each path's length, with the archive's sha256 recorded
beside them, and a test rebuilds the file from the archive and fails if the two disagree.
Only the *identity* of the tasks is needed at run time: the gold action sequences are
regenerated from the environment's own API, which is what makes the oracle control test the
**environment** rather than a stored answer.

The adapter keeps the complete `test` fold because the shared move budget is now 1,000 and the longest recorded path is 796. `test_fold.json` still carries every path length, and `test_fold()` re-applies the budget filter on every load. The current budget therefore excludes no recorded test path.

One discrepancy remains visible in the numbers: the package enumerates **30** task names and the archive has gold paths for **29**. The task without a gold path (`identify-life-stages-2`, 10 variations) is not in the test fold and this adapter does not return it.

The variation indices in the archive are the package's own (verified: the API's
`load(task, variationIdx, ...)` on a test-fold index reproduces that fold's path
character for character -- `tests/quality/test_scienceworld_dataset.py` pins the comparison
on real entries), so the fold and the environment agree about what a task *is*.

The metric, and what is deliberately not added
----------------------------------------------
`reward = max(0, score) / 100.0`, where `score` is the **last** `info['score']` the
environment reported, an integer 0-100. That is what the environment's own evaluation loop
records (`examples/random_agent.py`: `score = info['score']`, appended per episode; its
summary clips negatives before averaging, which is where `max(0, ...)` comes from). The
integer score is carried in the evidence beside the fraction, and the goal-met predicate is
`score == 100`.

`scw done` exists because a harness needs a way to stop; it is recorded and it is **not** a
gate, because ScienceWorld has no such requirement (`docs/dataset-onboarding-skill.md` §2).

Two decisions a reader should know about
----------------------------------------
* **No simplifications.** `simplificationStr` is empty, so the worlds are the full ones.
  The paper also reports an "easy" preset (`teleportAction`, `openDoors`,
  `selfWateringFlowerPots`, `noElectricalAction`), which is a *different* task set with a
  different score; mixing the two in one curve is the error this note exists to prevent.
* **A 1,000-move budget.** The environment's constructor default is 100, but the adapter
  uses 1,000 so every recorded test reference path fits without a false zero or truncation.
  The episode stops when the goal is met or the budget is spent. `STEP_BUDGET` is declared
  once in `lib/scw_env.py` and imported by the CLI, check and control, so the three cannot
  drift apart.

The leak boundary
-----------------
`load(..., generateGoldPath=True)` and `get_gold_action_sequence()` make the reference
solution reachable **through the environment object**. The agent's CLI never sets the flag
and never calls the accessor: it exposes `look`, `do`, `inventory`, `task` and `done`, and
each command builds its world with `generate_gold=False` (the default in `load_task`). So
the gold path is reachable only through an API the agent's process does not call, which is
the proof §12 asks for -- and it is a *stronger* position than ALFWorld's, where the answer
had to be stripped out of a file the agent receives.
"""
from __future__ import annotations

import os
from pathlib import Path

#: See `data/registry.py:KIND_DATASET`.
KIND = "dataset"

#: The oracle control submits the benchmark's own released reference; see
#: `data/dataset.schema.json` (`module.oracle_about`) for what the other value means.
ORACLE_SOURCE = "released"


#: The benchmark's own evaluation set, within this adapter's pool: **every task here belongs
#: to it**. The pool is the benchmark's own test fold: all 1,744 recorded paths fit the
#: adapter-owned 1,000-move budget. The train and dev folds exist upstream and are not loaded here.
#:
#: `None` is the accurate value only because nothing in the pool is study material -- it does
#: not claim the pool is the whole of the benchmark's evaluation set (see `ds1000`, which is a
#: measured subset). `--split official --side eval` is the comparable run: the whole pool, with
#: no study material in it. `--split declared` keeps this adapter's own division.
OFFICIAL_EVAL = None

import importlib.util
import json

#: Where the JRE is staged. Outside the platform tree on purpose: it is runtime, not code,
#: it is 136 MB unpacked, and `tools/datasets.py` provisions it. `HG_SCIENCEWORLD_DATA`
#: overrides it so a reader can point at another copy.
DATASET_ROOT = Path(os.environ.get("HG_SCIENCEWORLD_DATA",
                                   "/mnt/20t/xubuqiang/datasets/scienceworld"))

ASSETS = Path(__file__).resolve().parent / "scienceworld"
CLI_DIR = ASSETS / "cli"
LIB_DIR = ASSETS / "lib"
VERIFY_DIR = ASSETS / "verify"


def _load_lib():
    """`lib/scw_env.py`, by file path.

    Not `from data.scienceworld.lib import scw_env`: the check imports this module inside
    the verification namespace, where `lib/` travels as plain files beside the CLI, and the
    module is deliberately importable without a package around it.
    """
    spec = importlib.util.spec_from_file_location("scienceworld_scw_env",
                                                  LIB_DIR / "scw_env.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_LIB = _load_lib()

#: Declared once, in the shared library, and imported by the CLI, the check and the control.
STEP_BUDGET = _LIB.STEP_BUDGET
LOG_IN_WORKDIR = _LIB.LOG_FILENAME
TASK_IN_WORKDIR = _LIB.TASK_FILENAME

#: The container contract's locations. On a `files` environment `eval/verification/verifier.py` resolves
#: the absolute spelling against the workdir; the check's `argv` carries the relative
#: spelling its own working directory understands.
REWARD_FILE = "/verifier/reward.txt"
EVIDENCE_FILE = "/verifier/evidence.json"
REWARD_REL = "verifier/reward.txt"
EVIDENCE_REL = "verifier/evidence.json"

#: The JRE inside the dataset root. The **unpacked** tree is what travels into a task: the
#: platform's `_materialize` copies a directory (`shutil.copytree`) and a tarball would have
#: to be extracted by something, which during verification means the check writing into a
#: read-only task tree -- measured, `[Errno 30] Read-only file system`. Copying the tree is
#: also cheap (0.1 s measured) and every JVM you can copy starts, symlinks and all.
JRE_STAGED = DATASET_ROOT / "jre" / _LIB.JRE_DIRNAME

#: The official evaluation split, transcribed into git. **Not a download**: the archive
#: it comes from is unreachable reproducibly here (see the module docstring), and only the
#: tasks' *identity* is needed -- the gold sequences are regenerated from the environment.
FOLD_FILE = ASSETS / "test_fold.json"

#: The fold this dataset is: the benchmark's own held-out evaluation set.
EVAL_FOLD = "test"


def test_fold() -> list[dict]:
    """The official `test` fold, after the budget filter. Read once per process.

    The file is a transcription of the repository's `goldpaths-all.zip` (see the module
    docstring for why it is in git rather than fetched), and it carries **every** test path
    with its length, including the 22 that are too long. The filter lives here so the
    exclusion is recomputed from the data on every load, and the raise below is the guard
    that keeps it honest: if the budget is ever lowered without updating the filter, the
    load fails loudly instead of silently scoring a correct oracle 0.
    """
    global _FOLD_CACHE
    if _FOLD_CACHE is not None:
        return _FOLD_CACHE
    if not FOLD_FILE.is_file():
        raise FileNotFoundError(f"no test-fold file at {FOLD_FILE}")
    payload = json.loads(FOLD_FILE.read_text())
    if payload.get("eval_fold") != EVAL_FOLD:
        raise ValueError(f"{FOLD_FILE} describes fold {payload.get('eval_fold')!r}, not "
                         f"{EVAL_FOLD!r}")
    records = []
    too_long = []
    for entry in payload["tasks"]:
        record = {"task_id": f"{entry['task_name']}/{entry['variation']}",
                  "task_name": str(entry["task_name"]),
                  "variation": int(entry["variation"]),
                  "gold_moves": int(entry["gold_moves"])}
        (too_long if record["gold_moves"] > STEP_BUDGET else records).append(record)
    if not records:
        raise ValueError(f"{FOLD_FILE} leaves no tasks inside the {STEP_BUDGET}-move "
                         f"budget")
    if len(records) + len(too_long) == 0:
        raise ValueError(f"{FOLD_FILE} has no tasks")
    _FOLD_CACHE = records
    return records


def fold_excluded() -> list[dict]:
    """The test-fold paths left out for exceeding the budget, with their lengths.

    Exposed so the control and the tests can *report* the exclusion rather than only
    document it, and so `provision_status` can show it.
    """
    payload = json.loads(FOLD_FILE.read_text())
    return [e for e in payload["tasks"] if int(e["gold_moves"]) > STEP_BUDGET]


_FOLD_CACHE: list[dict] | None = None


def _probe_dir() -> Path:
    """A temporary workdir for the enumeration, with the staged JRE already unpacked.

    `make_env` looks for the JVM in the workdir first and at the staged copy last, so the
    by-hand path needs no unpacking at all; this only exists because the signature wants a
    workdir.
    """
    return Path(os.environ.get("HG_SCIENCEWORLD_WORKDIR", "/tmp"))


def _goal(record: dict) -> str:
    """The instruction: the task's own description, plus the interface, and nothing else.

    The description is read from the environment (`get_task_description()`), which is the
    benchmark's own wording. Fetching it needs a JVM, so the *records* carry only the task
    identity and the goal is rendered when the task is listed. The preamble states the
    budget and how to act -- the two things the interface cannot tell the agent -- and it
    says nothing about how to solve the task.
    """
    return (
        f"# Task\n"
        f"\n"
        f"You are an agent in a science lab, described one location at a time, acting by\n"
        f"typing commands. This is ScienceWorld task `{record['task_name']}`, variation\n"
        f"`{record['variation']}`. Your task description is in `{TASK_IN_WORKDIR}` and can\n"
        f"also be printed with `python3 scw task`.\n"
        f"\n"
        f"## How to act\n"
        f"\n"
        f"- See where you are, what is there, and your current score:\n"
        f"      python3 scw look\n"
        f"- Take one action (any text command; the environment decides whether it is\n"
        f"  understood, and an action it does not understand still costs a move):\n"
        f"      python3 scw do \"pick up thermometer\"\n"
        f"- Look at the task description again:\n"
        f"      python3 scw task\n"
        f"- See what you are carrying:\n"
        f"      python3 scw inventory\n"
        f"- When the task is finished, say so:\n"
        f"      python3 scw done\n"
        f"- Every action is appended to `{LOG_IN_WORKDIR}` and costs one of your\n"
        f"  **{STEP_BUDGET}** moves.\n"
        f"\n"
        f"## How it is scored\n"
        f"\n"
        f"- Your actions are replayed from the beginning in a fresh environment running the\n"
        f"  same pinned JVM, and the environment's own goal score is read at the end: an\n"
        f"  integer 0-100. Reaching 100 means the task was solved.\n"
        f"- Partial credit is the score's own fraction; there is no judge.\n"
        f"- Nothing you print is read. Only the actions you take are.\n"
    )


def _setup(record: dict) -> dict:
    """What the agent receives before it starts.

    The CLI, its library and the JRE travel as `from` references into this repository; the
    task identity travels as **inline content**, so the world the agent builds is the one
    the dataset declared and not something it could have edited into a file. The JRE is the
    136 MB directory under `jre/`: it is copied in because the verification namespace cannot
    see the dataset root, and both the agent's CLI and the check need the same JVM.
    """
    return {"files": [
        {"path": TASK_IN_WORKDIR,
         "content": json.dumps({"task_name": record["task_name"],
                                "variation": record["variation"],
                                "simplifications": ""})},
        {"path": "scw_env.py", "from": str(LIB_DIR / "scw_env.py")},
        {"path": "scw", "from": str(CLI_DIR / "scw")},
        # The runtime, as a prepared tree. `lib/scw_env.py::java_home` finds it at
        # `<workdir>/jre/<dirname>` and sets JAVA_HOME/PATH from it; py4j then launches it
        # by absolute path (a relative one breaks, because py4j passes its own cwd).
        {"path": f"{_LIB.JRE_RELDIR}/{_LIB.JRE_DIRNAME}", "from": str(JRE_STAGED)},
    ]}


def _verifier(record: dict) -> dict:
    """The grade: the check, its trusted inputs, and where the verdict goes.

    `inputs` use `path` (relative to the workdir), not `dst`: on a `files` environment the
    platform materialises these into the workdir, and `dst` is a container path. The task
    file, the check, the shared library and the JRE are all re-materialised at verification
    time, so nothing the agent wrote to any of them is what runs.
    """
    return {
        "kind": "command",
        "argv": [
            "python3", "check.py",
            "--workdir", ".",
            "--task", TASK_IN_WORKDIR,
            "--log", LOG_IN_WORKDIR,
            "--reward-file", REWARD_REL,
            "--evidence-file", EVIDENCE_REL,
            "--budget", str(STEP_BUDGET),
        ],
        "inputs": [
            {"path": "check.py", "from": str(VERIFY_DIR / "check.py")},
            {"path": "scw_env.py", "from": str(LIB_DIR / "scw_env.py")},
            {"path": TASK_IN_WORKDIR,
             "content": json.dumps({"task_name": record["task_name"],
                                    "variation": record["variation"],
                                    "simplifications": ""})},
            {"path": f"{_LIB.JRE_RELDIR}/{_LIB.JRE_DIRNAME}", "from": str(JRE_STAGED)},
        ],
        "reward_file": REWARD_FILE,
        "evidence_file": EVIDENCE_FILE,
        "timeout_s": 900,
    }


def downloads() -> list[dict]:
    """Everything this dataset needs, with the traps written down beside it.

    Read by `tools/datasets.py`; the generated `DOWNLOADS.md` is rendered from this
    function, never from a hand-written table, so the two cannot disagree.
    """
    return [
        {
            "kind": "pip",
            "name": "scienceworld",
            "package": "scienceworld",
            "version": "1.2.3",
            "size": "~8 MB",
            "note": "The environment **is** the package: `setup.py` declares "
                    "`package_data={'scienceworld': [JAR_FILE, ...]}` and the wheel ships "
                    "`scienceworld.jar` (7.5 MB), `tasks.json` (4.8 KB) and "
                    "`object_type_ids.tsv`. There is therefore no separate data download. "
                    "Trap: the package is Python *around a JVM*; it does not run without "
                    "Java, which is why the JRE below is part of this dataset. Version "
                    "1.3.0 changes physics trajectories and gold paths (its README), so "
                    "the pin is 1.2.3 and scores are not comparable across it.",
        },
        {
            "kind": "http",
            "name": "Temurin JRE 17 (Adoptium)",
            "version": _LIB.JRE_VERSION,
            "url": _LIB.JRE_URL,
            "size": _LIB.JRE_SIZE,
            "sha256": _LIB.JRE_SHA256,
            "dst": "_src/" + _LIB.JRE_TARBALL,
            "extract_to": "jre",
            "note": "Trap: this machine has **no system `java` and no root**, so a runtime "
                    "is a provisioning step, and the release URL *is* the version. **JDK "
                    "17, not the newest**: the JAR is built in 2025 and a newer JDK may "
                    "refuse an older target in a way that does not name Java. Both sides "
                    "need it -- the check replays in a fresh environment, so the agent's CLI "
                    "and the check must resolve the same JVM; a JVM only one of them can "
                    "find is a check that fails for a reason nothing records.",
        },
    ]


def provision_status() -> dict:
    """What is present locally, for `tools/datasets.py --check`.

    Deliberately does not import `scienceworld` or start a JVM: this is the answer to "did
    the provisioning run", which has to work on a machine where it did not.
    """
    java = DATASET_ROOT / "jre" / _LIB.JRE_DIRNAME / "bin" / "java"
    tarball = DATASET_ROOT / "_src" / _LIB.JRE_TARBALL
    return {
        "root": str(DATASET_ROOT),
        "present": java.is_file() and tarball.is_file() and FOLD_FILE.is_file(),
        "split_dir": str(DATASET_ROOT),
        "java": str(java) if java.is_file() else None,
        "jre_unpacked": str(JRE_STAGED) if JRE_STAGED.is_dir() else None,
        "jre_tarball": str(tarball) if tarball.is_file() else None,
        "fold_file": str(FOLD_FILE) if FOLD_FILE.is_file() else None,
        "fold_excluded_over_budget": len(fold_excluded()) if FOLD_FILE.is_file() else None,
        "tasks": len(_RECORDS) if _RECORDS else None,
    }


#: Enumerated on first use, never at import: `data/registry.py::published` imports every
#: adapter, and the enumeration needs a JVM. `_LOAD_ERROR` carries the reason into `load()`,
#: so a machine without the runtime can still see the dataset in the chooser and read why
#: it will not run.
try:
    _RECORDS: list[dict] = []
    _LOAD_ERROR: str | None = None
except Exception as _exc:  # noqa: BLE001 - reported by load(), which is where it bites
    _RECORDS = []
    _LOAD_ERROR = f"{type(_exc).__name__}: {_exc}"


def _ensure() -> list[dict]:
    global _RECORDS, _LOAD_ERROR
    if _RECORDS:
        return _RECORDS
    if _LOAD_ERROR is not None:
        raise ValueError(f"scienceworld: cannot read the task set ({_LOAD_ERROR})")
    try:
        _RECORDS = test_fold()
    except Exception as exc:  # noqa: BLE001 - carried into load()
        _LOAD_ERROR = f"{type(exc).__name__}: {exc}"
        raise
    return _RECORDS


def load() -> tuple[list[dict], dict[str, str]]:
    """`(tasks, scorable)`. Every task is graded by its `VERIFY` entry, so the `scorable`
    map is present only because the interface asks for it."""
    try:
        records = _ensure()
    except Exception as exc:  # noqa: BLE001 - the reason is the point
        raise ValueError(
            f"scienceworld: cannot build the task list ({exc}). Provision the runtime "
            f"with `python3 tools/datasets.py --fetch --dataset scienceworld` and check "
            f"that `pip show scienceworld` reports 1.2.3.") from exc
    if not records:
        raise ValueError("scienceworld: the enumeration returned no tasks")
    tasks = [{"task_id": r["task_id"], "goal": _goal(r), "inputs": []} for r in records]
    return tasks, {r["task_id"]: "" for r in records}


def _is_eval(task_id: str) -> bool:
    """A deterministic third, by hash of the task id.

    Hashed rather than sliced off the sorted list so that adding or removing a task does
    not reshuffle which side every other task is on -- the same rule `data/alfworld.py` and
    `data/terminal_bench.py` use. The official `train`/`dev`/`test` folds exist in the
    repository's `goldpaths-all.zip` but are not in the package; see the module docstring.
    """
    import hashlib
    return hashlib.sha256(task_id.encode()).digest()[0] % 3 == 0


#: One environment for every task: the host, because the hard constraint of this exercise
#: is that nothing here needs Docker. `files` cannot carry resource or timeout fields
#: (`data/registry.py::_check_env` refuses them), so the platform's defaults apply.
DEFAULT_ENV: dict = {"kind": "files"}


def _split() -> dict:
    """The imposed train/eval split, computed without materialising the per-task dicts.

    Deriving it from the records would mean building 21,621 goal/verifier structures just
    to answer "which side is this task on", and `tools/dataset_lint.py` and the driver both
    read `SPLIT` before anything else. The identity is the same generator the records use,
    so the two cannot disagree.
    """
    train, eval_ = [], []
    for record in _ensure():
        (eval_ if _is_eval(record["task_id"]) else train).append(record["task_id"])
    return {"train": train, "eval": eval_}


class _Lazy:
    """`ENV`, `SETUP` and `VERIFY`, built on first use.

    Three dicts with one entry per task, and there are 7,207 tasks. Building them at import
    would make importing this adapter cost a JVM start plus 21,621 dict constructions -- the
    lesson the QA batch recorded in `docs/dataset-onboarding-skill.md` §15.7. The platform
    asks for them through module `__getattr__` below.
    """

    def __init__(self) -> None:
        self._cache: dict = {}

    def get(self, name: str):
        if name not in self._cache:
            records = _ensure()
            ids = [r["task_id"] for r in records]
            self._cache = {
                "ENV": {tid: {"kind": "files"} for tid in ids},
                "SETUP": {r["task_id"]: _setup(r) for r in records},
                "VERIFY": {r["task_id"]: _verifier(r) for r in records},
            }
        return self._cache[name]


_LAZY = _Lazy()

_split_mode = (os.environ.get("HG_SCIENCEWORLD_SPLIT") or "hash").lower()


def __getattr__(name: str):
    if name in ("ENV", "SETUP", "VERIFY"):
        return _LAZY.get(name)
    if name == "SPLIT":
        if _split_mode == "none":
            # Every task as eval, accepting the driver's warning -- ALFWorld's escape hatch,
            # for the same reason: the benchmark declares no division and the one here is
            # imposed, so wanting the whole set scored must be sayable without editing code.
            ids = [r["task_id"] for r in _ensure()]
            return {"train": [], "eval": ids}
        return _split()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["KIND", "DATASET_ROOT", "STEP_BUDGET", "load", "downloads",
           "provision_status", "DEFAULT_ENV"]
