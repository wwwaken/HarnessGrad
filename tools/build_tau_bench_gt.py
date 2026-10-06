#!/usr/bin/env python3
"""Stage the tau-bench dataset's committed assets from the upstream checkout.

    python3 tools/build_tau_bench_gt.py                 # regenerate everything
    python3 tools/build_tau_bench_gt.py --checkout DIR  # use another clone
    python3 tools/build_tau_bench_gt.py --check         # fail if anything drifted

It reads a checkout of `sierra-research/tau-bench` (default
`/mnt/20t/xubuqiang/datasets/tau-bench`, override with `--checkout` or
`HG_TAU_BENCH`) and writes, under `data/tau_bench/`:

    gt/<task_id>.json     one task's ground truth: domain, user id, instruction
                          and the action sequence. This is the answer, and it is
                          **copied into the container only after the agent stops**
                          (as a `VERIFY.inputs` entry), never into the image.
    db/<domain>.json      the clean domain database, i.e. the initial state the
                          agent is handed as `/app/db.json`.
    policy/<domain>.txt   the wiki plus the rules, i.e. the policy `tau policy`
                          prints and the agent is told to follow.
    lib/tau_bench/        the upstream tool classes (verbatim, tasks removed) plus
                          `envs/hash.py`, which is `to_hashable`/`consistent_hash`
                          extracted **verbatim** from `tau_bench/envs/base.py`.
                          The same tree is installed in the image (`/opt/tau/lib`)
                          and copied in as a verifier input, so the replay hashes
                          exactly what tau-bench hashes and cannot be edited by the
                          agent it is grading.
    PROVENANCE.json       checkout path, upstream commit, and a sha256 per staged
                          file, so the assets can be re-derived from a checkout.

Why the staging and not a `pip install` of tau-bench
----------------------------------------------------
`tau_bench/__init__.py` imports the agent and the LLM user simulator, and the
checkout carries `tasks*.py` -- the answers -- in every domain package. Installing
the package into the image would put the answers one `cat` away from the agent.
Only the tool implementations, the data, the wiki and the rules travel, and
nothing that imports the rest: the tool modules are written against stdlib plus
`tau_bench.envs.tool`, which is 12 lines of ABC.

Hash-function provenance
------------------------
`envs/hash.py` is not a reimplementation. The source region from `ToHashable =`
through the end of `consistent_hash` is copied byte-for-byte out of
`tau_bench/envs/base.py` (the import of `sha256` and of the typing names, which
sit above that region in the original, is added back). The sha256 of the file it
was cut from is recorded in the module's header and in `PROVENANCE.json`, so a
reviewer can tell at a glance which upstream revision the reward is comparing.
`base.py` itself cannot be imported as-is: it pulls `tau_bench.envs.user`, which
imports `litellm`, and a check that needs an LLM client to compute a database
hash is a check that can fail for reasons that have nothing to do with the task.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / "data" / "tau_bench"
GT_DIR = OUT / "gt"
DB_DIR = OUT / "db"
POLICY_DIR = OUT / "policy"
LIB_DIR = OUT / "lib"

DEFAULT_CHECKOUT = "/mnt/20t/xubuqiang/datasets/tau-bench"

#: The task split each domain's own `env.py` uses. Retail's `MockRetailDomainEnv`
#: imports `tasks_test.TASKS_TEST` for `task_split="test"`; airline only knows
#: `tasks_test.TASKS`. The legacy `tasks.py` files hold a different, larger,
#: older set (185 retail / 76 airline) and are deliberately not used: they are
#: not what the environment scored.
DOMAINS = {
    "retail": ("tasks_test", "TASKS_TEST"),
    "airline": ("tasks_test", "TASKS"),
}

#: The database tables each domain's `data.load_data()` returns.
DATA_TABLES = {
    "retail": {"orders": "orders.json", "products": "products.json",
               "users": "users.json"},
    "airline": {"flights": "flights.json", "reservations": "reservations.json",
                "users": "users.json"},
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_module(name: str, path: Path):
    """Load a single file as a module without importing its package.

    The upstream `tasks_test.py` / `rules.py` / `data/__init__.py` are self
    contained given `tau_bench.types` (for the task files); importing them through
    the real package would pull `tau_bench/__init__.py`, the LLM agent and
    litellm, none of which are needed to read a task list.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _install_stub_types() -> None:
    """A `tau_bench.types` with Task/Action and no dependencies.

    The upstream task files are `Task(annotator=..., user_id=..., instruction=...,
    actions=[Action(name=..., kwargs=...)])` and nothing else; the real models are
    pydantic, which is not needed to read them. Fields the stub does not know are
    kept, because `annotator` and `outputs` are read back.
    """
    pkg = types.ModuleType("tau_bench")
    pkg.__path__ = []  # type: ignore[attr-defined]
    types_mod = types.ModuleType("tau_bench.types")

    class Action:
        def __init__(self, name: str, kwargs: dict):
            self.name = name
            self.kwargs = kwargs

    class Task:
        def __init__(self, **fields):
            self.__dict__.update(fields)
            self.__dict__.setdefault("outputs", [])

    types_mod.Action = Action  # type: ignore[attr-defined]
    types_mod.Task = Task  # type: ignore[attr-defined]
    sys.modules["tau_bench"] = pkg
    sys.modules["tau_bench.types"] = types_mod


def _extract_hash_module(base_path: Path) -> str:
    """`to_hashable` + `consistent_hash`, verbatim from `envs/base.py`."""
    source = base_path.read_text()
    start = source.index("ToHashable = Union[")
    end = source.index("class Env")
    block = source[start:end].rstrip()
    digest = hashlib.sha256(base_path.read_bytes()).hexdigest()
    header = (
        '"""The database hash tau-bench scores with -- extracted, not rewritten.\n'
        "\n"
        "The block below is copied verbatim from `tau_bench/envs/base.py` in the\n"
        "upstream checkout (everything from `ToHashable =` up to `class Env`), with the\n"
        "`sha256` and `typing` names it uses added back because they are imported above\n"
        "that region in the original. `Env.get_data_hash()` is exactly\n"
        "`consistent_hash(to_hashable(self.data))`, which is what the verifier calls.\n"
        "\n"
        "    source   tau_bench/envs/base.py\n"
        f"    sha256   {digest}\n"
        '"""\n'
        "from hashlib import sha256\n"
        "from typing import Dict, List, Set, Tuple, Union\n"
        "\n"
    )
    return header + block + "\n"


def _load_tasks(checkout: Path, domain: str) -> list:
    module_name, attr = DOMAINS[domain]
    path = checkout / "tau_bench" / "envs" / domain / f"{module_name}.py"
    if not path.is_file():
        raise SystemExit(f"no task file at {path}; is --checkout right?")
    mod = _load_module(f"tb_{domain}_{module_name}", path)
    return list(getattr(mod, attr))


def _load_db(checkout: Path, domain: str) -> dict:
    """The clean database, read through the upstream `data.load_data()`."""
    data_init = checkout / "tau_bench" / "envs" / domain / "data" / "__init__.py"
    if data_init.is_file():
        mod = _load_module(f"tb_{domain}_data", data_init)
        return mod.load_data()
    folder = data_init.parent
    return {table: json.loads((folder / fname).read_text())
            for table, fname in DATA_TABLES[domain].items()}


def _load_policy(checkout: Path, domain: str) -> str:
    folder = checkout / "tau_bench" / "envs" / domain
    wiki = (folder / "wiki.md").read_text()
    rules = _load_module(f"tb_{domain}_rules", folder / "rules.py").RULES
    text = wiki.rstrip() + "\n"
    if rules:
        text += "\n# Rules\n\n" + "".join(f"- {rule}\n" for rule in rules)
        text += ("\n(The rules above are the upstream `rules.py` list; the wiki\n"
                 "above it is `wiki.md`.)\n")
    else:
        text += ("\n# Rules\n\n(Upstream `rules.py` declares no additional rules "
                 "for this domain.)\n")
    return text


def _stage_lib(checkout: Path, domain: str) -> None:
    envs = checkout / "tau_bench" / "envs"
    lib_pkg = LIB_DIR / "tau_bench"
    lib_envs = lib_pkg / "envs"
    lib_tools = lib_envs / domain / "tools"
    lib_tools.mkdir(parents=True, exist_ok=True)
    for package in (lib_pkg, lib_envs, lib_envs / domain):
        (package / "__init__.py").write_text("")

    written = []
    tool_base = lib_envs / "tool.py"
    shutil.copy2(envs / "tool.py", tool_base)
    written.append(tool_base)

    src_tools = envs / domain / "tools"
    for src in sorted(src_tools.glob("*.py")):
        dst = lib_tools / src.name
        shutil.copy2(src, dst)
        written.append(dst)

    hash_path = lib_envs / "hash.py"
    hash_path.write_text(_extract_hash_module(envs / "base.py"))
    written.append(hash_path)

    # No bytecode in the committed tree: a stale `.pyc` is a second copy of a tool
    # module that nothing regenerates, and the `COPY lib` into the image would carry
    # it along with whatever the host interpreter happened to produce.
    for cache in LIB_DIR.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)


def _git_commit(checkout: Path) -> str:
    import subprocess
    try:
        proc = subprocess.run(["git", "-C", str(checkout), "rev-parse", "HEAD"],
                              capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return ""
    return proc.stdout.strip() if proc.returncode == 0 else ""


def build(checkout: Path) -> dict:
    checks = []
    if not (checkout / "tau_bench").is_dir():
        raise SystemExit(f"{checkout} is not a tau-bench checkout")
    for name, path in (("base.py", checkout / "tau_bench/envs/base.py"),
                       ("tool.py", checkout / "tau_bench/envs/tool.py")):
        if not path.is_file():
            raise SystemExit(f"missing {name} at {path}")

    # Only the generated trees are cleared; `image/` and `verify/` are hand-written.
    for directory in (GT_DIR, DB_DIR, POLICY_DIR, LIB_DIR):
        if directory.exists():
            shutil.rmtree(directory)
        directory.mkdir(parents=True)

    _install_stub_types()

    counts = {}
    for domain in DOMAINS:
        tasks = _load_tasks(checkout, domain)
        counts[domain] = len(tasks)
        for index, task in enumerate(tasks):
            tid = f"{domain}_{index:03d}"
            actions = [{"name": action.name, "arguments": action.kwargs}
                       for action in task.actions]
            record = {
                "task_id": tid,
                "domain": domain,
                "index": index,
                "user_id": task.user_id,
                "instruction": task.instruction,
                "actions": actions,
                "outputs": list(getattr(task, "outputs", []) or []),
            }
            (GT_DIR / f"{tid}.json").write_text(
                json.dumps(record, indent=1, sort_keys=True, ensure_ascii=False) + "\n")

        db = _load_db(checkout, domain)
        (DB_DIR / f"{domain}.json").write_text(
            json.dumps(db, separators=(",", ":"), ensure_ascii=False, sort_keys=True))
        (POLICY_DIR / f"{domain}.txt").write_text(_load_policy(checkout, domain))
        _stage_lib(checkout, domain)

    staged = sorted(p for directory in (GT_DIR, DB_DIR, POLICY_DIR, LIB_DIR)
                    for p in directory.rglob("*")
                    if p.is_file() and "__pycache__" not in p.parts)
    provenance = {
        "checkout": str(checkout),
        "checkout_commit": _git_commit(checkout),
        "generated_by": "tools/build_tau_bench_gt.py",
        "task_files": {d: f"tau_bench/envs/{d}/{DOMAINS[d][0]}.py" for d in DOMAINS},
        "task_counts": counts,
        "base_py_sha256": _sha256(checkout / "tau_bench/envs/base.py"),
        "files": {str(p.relative_to(OUT)): _sha256(p) for p in staged},
    }
    (OUT / "PROVENANCE.json").write_text(
        json.dumps(provenance, indent=1, sort_keys=True) + "\n")
    return provenance


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--checkout", default=os.environ.get("HG_TAU_BENCH",
                                                             DEFAULT_CHECKOUT))
    parser.add_argument("--check", action="store_true",
                        help="verify the committed assets match a fresh build")
    args = parser.parse_args()
    checkout = Path(args.checkout).resolve()

    before = None
    if args.check:
        try:
            before = json.loads((OUT / "PROVENANCE.json").read_text())
        except (OSError, ValueError):
            print("no PROVENANCE.json to check against", file=sys.stderr)
            return 2

    provenance = build(checkout)
    counts = provenance["task_counts"]
    print(f"tau-bench assets -> {OUT}")
    for domain, n in sorted(counts.items()):
        print(f"  {domain:8s} {n:4d} tasks, db {DB_DIR / (domain + '.json')}")
    print(f"  checkout {provenance['checkout']} @ "
          f"{provenance['checkout_commit'] or '(no git)'}")
    print(f"  staged {len(provenance['files'])} files")

    if args.check and before is not None:
        # Re-read what is on disk now; `before` was the pre-build record. Since
        # `build` just rewrote everything, compare the fresh record to the old one.
        if before.get("files") != provenance.get("files") or \
                before.get("task_counts") != provenance.get("task_counts"):
            print("assets drifted; see PROVENANCE.json", file=sys.stderr)
            return 1
        print("  --check: assets match")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
