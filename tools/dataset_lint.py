#!/usr/bin/env python3
"""Lint a dataset adapter against the machine-checkable half of the contract.

Why this exists
---------------
`docs/dataset-onboarding-skill.md` records the judgement lessons -- the ones that need
a person. This is the other half: the invariants a program can decide, so that a new
dataset which violates one turns the quality suite red instead of producing a plausible
number. The rules come from `data/dataset.schema.json`, which is data, not code, because
the two tools that read it (`tools/datasets.py`, which renders DOWNLOADS.md) and this
one must agree about what a valid `downloads()` is.

What it checks (see the schema for the exact spelling)
------------------------------------------------------
    KIND declared and one of the known kinds
    load() callable and returning tasks with `task_id` + `goal`
    ENV/SETUP/VERIFY cover every task id (delegated to data/registry.py, so there is
        one answer to "is this environment/verifier valid", not two)
    VERIFY.inputs `dst` values are TOP LEVEL absolute paths
    a `command` verifier declares `reward_file`, and it is absolute
    downloads() present, non-empty, each entry well-formed, each version PINNED
    the dataset's data root is outside the platform tree

Usage
-----
    python3 tools/dataset_lint.py                  # every published dataset
    python3 tools/dataset_lint.py --dataset alpaca # one
    python3 tools/dataset_lint.py --json
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data" / "dataset.schema.json"

sys.path.insert(0, str(ROOT))
import data.registry as registry  # noqa: E402


class Result:
    """What linting one dataset found. `unprovisioned` is not a failure.

    A dataset whose bytes are not on this machine is not a broken dataset: it is one
    whose provisioning has not run. Lumping that in with a malformed `VERIFY` would
    make the suite red on every machine that has not downloaded 100 GB, which is how a
    check gets turned off. The split is deliberate and it is the caller's job to say so.
    """

    def __init__(self, name: str):
        self.name = name
        self.errors: list[str] = []
        self.unprovisioned: str | None = None

    def error(self, message: str) -> None:
        self.errors.append(message)

    @property
    def ok(self) -> bool:
        return not self.errors

    def as_dict(self) -> dict:
        return {"dataset": self.name, "ok": self.ok, "errors": self.errors,
                "unprovisioned": self.unprovisioned}


def load_schema(path: Path = SCHEMA_PATH) -> dict:
    return json.loads(path.read_text())


def _is_top_level(dst: str) -> bool:
    """`/foo` is top level; `/a/b` is not.

    The platform copies a verifier's inputs in **before** it creates the reward file's
    directory, so a nested `dst` has no parent to be copied into -- measured, and it
    cost a whole run (see `data/tau_bench.py:_verifier`). A top-level destination has
    `/` for a parent, which always exists.
    """
    return PurePosixPath(str(dst)).parent == PurePosixPath("/")


def _outside_platform(path: Path, root: Path) -> bool:
    p = path.resolve()
    return p != root.resolve() and root.resolve() not in p.parents


def lint_downloads(downloads, schema: dict, result: Result) -> None:
    spec = schema["download"]
    if not isinstance(downloads, list) or not downloads:
        result.error("downloads() must return a non-empty list")
        return
    for index, entry in enumerate(downloads):
        where = f"downloads()[{index}]"
        if not isinstance(entry, dict):
            result.error(f"{where} must be a dict")
            continue
        kind = entry.get("kind")
        if kind not in spec["kinds"]:
            result.error(f"{where} has kind {kind!r}; known kinds are {spec['kinds']}")
            continue
        required = list(spec["common_required"]) + list(
            spec["by_kind"].get(kind, {}).get("required", []))
        missing = [key for key in required if not entry.get(key)]
        if missing:
            result.error(f"{where} ({entry.get('name')!r}) is missing {missing}")
        version = str(entry.get("version", "")).strip()
        if version.lower() in spec["version_forbidden"]:
            result.error(f"{where} ({entry.get('name')!r}) is not pinned: version="
                         f"{entry.get('version')!r}; a branch name is not a version")
        note = str(entry.get("note") or "")
        if len(note) < spec["note_min_chars"]:
            result.error(f"{where} ({entry.get('name')!r}) has no plain-language note "
                         f"({len(note)} chars; the schema asks for at least "
                         f"{spec['note_min_chars']})")
        dst = entry.get("dst")
        if dst:
            p = Path(str(dst))
            target = p if p.is_absolute() else ROOT / p
            if p.is_absolute() and not _outside_platform(target, ROOT):
                result.error(f"{where} writes to {dst!r}, which is inside the platform "
                             f"tree; dataset bytes must live outside it")


def lint_tasks(tasks, scorable, schema: dict, result: Result) -> set[str]:
    spec = schema["task"]
    if not isinstance(tasks, list):
        result.error("load() must return tasks as a list")
        return set()
    if not isinstance(scorable, dict):
        result.error("load() must return scorable as a dict")
    ids: list[str] = []
    for task in tasks:
        if not isinstance(task, dict):
            result.error("every task must be a dict")
            continue
        missing = [key for key in spec["required"] if not task.get(key)]
        if missing:
            result.error(f"task {task.get('task_id')!r} is missing {missing}")
        tid = task.get("task_id")
        if isinstance(tid, str) and tid:
            ids.append(tid)
    duplicates = sorted({t for t in ids if ids.count(t) > 1})
    if duplicates:
        result.error(f"duplicate task_id(s): {duplicates}")
    return set(ids)


def lint_verify(verifiers, task_ids: set[str], schema: dict, result: Result) -> None:
    spec = schema["verify"]
    if verifiers is None:
        return
    known = set(verifiers)
    unknown = known - task_ids
    absent = task_ids - known
    if unknown:
        result.error(f"VERIFY names unknown task(s) {sorted(unknown)}")
    if absent:
        result.error(f"task(s) {sorted(absent)} have no VERIFY entry")
    for tid, verifier in sorted(verifiers.items()):
        if not isinstance(verifier, dict):
            result.error(f"VERIFY[{tid!r}] must be a dict")
            continue
        kind = verifier.get("kind")
        if kind not in spec["kinds"]:
            result.error(f"VERIFY[{tid!r}] has kind {kind!r}; known kinds are "
                         f"{spec['kinds']}")
            continue
        if kind != "command":
            continue
        for key in spec["command_required"]:
            if not verifier.get(key):
                result.error(f"VERIFY[{tid!r}] is a command verifier without `{key}`")
        for key in spec["absolute_paths"]:
            value = verifier.get(key)
            if value and not str(value).startswith("/"):
                result.error(f"VERIFY[{tid!r}][{key!r}] must be absolute, got {value!r}")
        for index, entry in enumerate(verifier.get("inputs") or []):
            where = f"VERIFY[{tid!r}].inputs[{index}]"
            if not isinstance(entry, dict):
                result.error(f"{where} must be a dict")
                continue
            target = entry.get("dst") or entry.get("path")
            if not target:
                result.error(f"{where} has neither `path` nor `dst`")
                continue
            if "content" not in entry and "from" not in entry:
                result.error(f"{where} ({target!r}) has neither `content` nor `from`")
            if entry.get("dst"):
                if not str(entry["dst"]).startswith("/"):
                    result.error(f"{where} `dst` must be absolute, got "
                                 f"{entry['dst']!r}")
                elif spec["dst_must_be_top_level"] and not _is_top_level(entry["dst"]):
                    result.error(
                        f"{where} `dst`={entry['dst']!r} is nested. The platform copies "
                        f"inputs in before it creates the reward directory, so a nested "
                        f"destination has no parent; use a top-level path such as "
                        f"/{PurePosixPath(str(entry['dst'])).name}")


def lint_split(split, task_ids: set[str], schema: dict, result: Result) -> None:
    if split is None:
        return
    spec = schema["split"]
    if not isinstance(split, dict):
        result.error("SPLIT must be a dict or absent")
        return
    unknown_sides = set(split) - set(spec["sides"])
    if unknown_sides:
        result.error(f"SPLIT has unknown side(s) {sorted(unknown_sides)}")
    sides = {side: list(split.get(side, [])) for side in spec["sides"]}
    for side, members in sides.items():
        missing = set(members) - task_ids
        if missing:
            result.error(f"SPLIT[{side!r}] names unknown task(s) {sorted(missing)}")
    overlap = set(sides["train"]) & set(sides["eval"])
    if overlap:
        result.error(f"task(s) {sorted(overlap)} are on both sides of SPLIT")
    covered = set(sides["train"]) | set(sides["eval"])
    if covered != task_ids:
        result.error(f"task(s) {sorted(task_ids - covered)} are on neither side of SPLIT")
    if spec["no_empty_side"]:
        empty = [side for side, members in sides.items() if not members]
        if empty:
            result.error(f"SPLIT has an empty side: {empty}")


def lint_paths(module, schema: dict, result: Result) -> None:
    spec = schema["paths"]
    if not spec["must_be_outside_platform"]:
        return
    for attribute in spec["data_root_attributes"]:
        value = getattr(module, attribute, None)
        if value is None:
            continue
        try:
            path = Path(value)
        except TypeError:
            continue
        if not path.is_absolute():
            continue
        if not _outside_platform(path, ROOT):
            result.error(f"{attribute}={str(path)!r} is inside the platform tree; "
                         f"dataset bytes must live outside it (see "
                         f"data/dataset.schema.json:paths)")


def lint_dataset(name: str, schema: dict, *, require_data: bool = True) -> Result:
    result = Result(name)
    try:
        module = importlib.import_module(f"data.{name}")
    except Exception as exc:  # noqa: BLE001 - a module that will not import is a finding
        result.error(f"will not import: {type(exc).__name__}: {exc}")
        return result

    kind = getattr(module, schema["module"]["kind_attribute"], None)
    if kind not in schema["module"]["kinds"]:
        result.error(f"KIND must be one of {schema['module']['kinds']}, got {kind!r}")

    for callable_name in schema["module"]["required_callables"]:
        if not callable(getattr(module, callable_name, None)):
            result.error(f"`{callable_name}()` is missing or not callable")

    lint_paths(module, schema, result)

    downloads = getattr(module, "downloads", None)
    if callable(downloads):
        try:
            lint_downloads(downloads(), schema, result)
        except Exception as exc:  # noqa: BLE001
            result.error(f"downloads() raised {type(exc).__name__}: {exc}")

    # The dynamic half needs the data. `provision_status()` is a dataset's own answer to
    # "are my bytes here"; a module without one is assumed provisioned and `load()`
    # decides.
    status = getattr(module, "provision_status", None)
    if callable(status):
        try:
            if not status().get("present"):
                result.unprovisioned = f"no data at {status().get('split_dir') or status().get('root')}"
                return result
        except Exception as exc:  # noqa: BLE001
            result.error(f"provision_status() raised {type(exc).__name__}: {exc}")
            return result

    try:
        tasks, scorable = registry.load(name)
    except Exception as exc:  # noqa: BLE001
        if require_data:
            result.error(f"load() raised {type(exc).__name__}: {exc}")
        else:
            result.unprovisioned = f"{type(exc).__name__}: {exc}"
        return result

    task_ids = lint_tasks(tasks, scorable, schema, result)
    lint_split(getattr(module, "SPLIT", None), task_ids, schema, result)

    # The contract checks the platform already owns are delegated, not re-implemented:
    # two answers to "is this ENV/VERIFY valid" is exactly the fork this repository is
    # built to avoid.
    try:
        _, setups, verifiers = registry.load_tasks(name)
    except Exception as exc:  # noqa: BLE001
        result.error(f"registry.load_tasks: {type(exc).__name__}: {exc}")
        # Still lint the declared VERIFY directly. The platform's validator stops at the
        # first structural problem, and a lint that reports one violation per run makes
        # the next reader fix one thing and run it again -- so the broken-copy test below
        # would have to be run eleven times to see eleven rules fire.
        verifiers = {tid: dict(spec) for tid, spec in
                     (getattr(module, "VERIFY", None) or {}).items()
                     if isinstance(spec, dict)}
        setups = dict(getattr(module, "SETUP", None) or {})
    try:
        registry.load_envs(name)
    except Exception as exc:  # noqa: BLE001
        result.error(f"registry.load_envs: {type(exc).__name__}: {exc}")

    known = {t["task_id"] for t in tasks}
    unknown_setup = set(setups) - known
    if unknown_setup:
        result.error(f"SETUP names unknown task(s) {sorted(unknown_setup)}")
    lint_verify(verifiers, known, schema, result)
    return result


def published_datasets() -> list[str]:
    return list(registry.published())


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dataset", action="append",
                        help="lint only this dataset; repeatable")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--allow-unprovisioned", action="store_true",
                        help="a dataset whose data is absent is reported, not failed")
    args = parser.parse_args(argv)
    schema = load_schema()
    names = args.dataset or published_datasets()

    results = [lint_dataset(name, schema,
                            require_data=not args.allow_unprovisioned)
               for name in names]
    if args.json:
        print(json.dumps([r.as_dict() for r in results], indent=1, sort_keys=True))
    else:
        for result in results:
            if result.unprovisioned:
                print(f"SKIP {result.name}: not provisioned ({result.unprovisioned})")
            elif result.ok:
                print(f"ok   {result.name}")
            else:
                print(f"FAIL {result.name}")
                for error in result.errors:
                    print(f"     - {error}")
    return 1 if any(not r.ok for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
