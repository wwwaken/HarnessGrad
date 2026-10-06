#!/usr/bin/env python3
"""Declarative provisioning: what each dataset needs, and whether it is here.

The design this implements
--------------------------
A dataset's loader is the authority on what the dataset needs. So the needs are
expressed *in the loader*, as a `downloads()` function, and this tool only reads it:

    python3 tools/datasets.py --list      what every dataset asks for
    python3 tools/datasets.py --check     which of those are present locally
    python3 tools/datasets.py --write     regenerate DOWNLOADS.md from the loaders

**DOWNLOADS.md is generated and must never be hand-edited.** A second copy of a
provisioning list in a document forks, and the fork shows up as "someone followed the
docs and got different bytes" -- which is why the renderer is this tool and the
authority is the loader.

The split the whole feature rests on: **data lands under
`/mnt/20t/xubuqiang/datasets/<name>/` and never in git; code -- how to load and how to
score -- stays in git.** A dataset whose `downloads()` names a `dst` inside the platform
tree is refused by `tools/dataset_lint.py` for exactly that reason.

A version must be pinned: a release tag, a commit sha or an exact package version. A
branch name is not a version and is refused by the lint; `--check` cannot verify a
moving target even if one were allowed.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "DOWNLOADS.md"
SCHEMA_PATH = ROOT / "data" / "dataset.schema.json"

sys.path.insert(0, str(ROOT))
import data.registry as registry  # noqa: E402


def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text())


def datasets_with_downloads() -> list[tuple[str, list[dict]]]:
    """Every published dataset that declares `downloads()`, in name order."""
    out = []
    for name in registry.published():
        module = importlib.import_module(f"data.{name}")
        fn = getattr(module, "downloads", None)
        if callable(fn):
            out.append((name, list(fn() or [])))
    return out


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dataset_root(module) -> Path:
    """Where this dataset's bytes live, for resolving a relative `dst`.

    A relative `dst` is relative to the dataset root, not to the platform -- that is
    the split the whole feature rests on. The root is read from the loader, in the same
    order the rest of the tooling does: an explicit `provision_status()['root']`, then a
    `DATASET_ROOT`/`ROOT` attribute, and only then the platform directory (which is
    right for a dataset whose content really is committed).
    """
    status = getattr(module, "provision_status", None)
    if callable(status):
        try:
            root = status().get("root")
            if root:
                return Path(root)
        except Exception:  # noqa: BLE001 - a broken status is reported elsewhere
            pass
    for attribute in ("DATASET_ROOT", "ROOT"):
        value = getattr(module, attribute, None)
        if value:
            return Path(value)
    return ROOT


def check_entry(entry: dict, base: Path) -> dict:
    """Is one download present? Never raises: a provisioning tool that dies on the first
    missing byte cannot report the other nine."""
    kind = entry.get("kind")
    result = {"name": entry.get("name"), "kind": kind, "version": entry.get("version"),
              "present": False, "detail": ""}
    if kind == "pip":
        package = entry.get("package")
        try:
            installed = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            result["detail"] = f"{package} is not installed"
            return result
        if installed == str(entry.get("version")):
            result.update(present=True, detail=f"{package}=={installed}")
        else:
            result["detail"] = (f"{package}=={installed} is installed, but the dataset "
                                f"pins {entry.get('version')}")
        return result

    dst = entry.get("dst")
    if not dst:
        result["detail"] = "no `dst` to check"
        return result
    path = Path(str(dst))
    if not path.is_absolute():
        path = base / path
    if not path.exists():
        result["detail"] = f"missing: {path}"
        return result
    expected = entry.get("sha256")
    if expected and path.is_file():
        actual = _sha256(path)
        if actual != expected:
            result["detail"] = f"{path} exists but sha256 {actual[:12]}... != {expected[:12]}..."
            return result
        result.update(present=True, detail=f"{path} (sha256 ok)")
        return result
    result.update(present=True, detail=f"{path} exists")
    return result


def check_dataset(name: str, downloads: list[dict]) -> dict:
    module = importlib.import_module(f"data.{name}")
    base = dataset_root(module)
    entries = [check_entry(entry, base) for entry in downloads]
    status = {}
    fn = getattr(module, "provision_status", None)
    if callable(fn):
        try:
            status = fn()
        except Exception as exc:  # noqa: BLE001
            status = {"error": f"{type(exc).__name__}: {exc}"}
    return {"dataset": name, "entries": entries, "status": status,
            "present": all(e["present"] for e in entries) if entries else False}


def render_index(rows: list[dict]) -> str:
    """DOWNLOADS.md, from the loaders. See the module docstring for why it is generated."""
    lines = [
        "<!-- GENERATED BY tools/datasets.py --write. DO NOT EDIT BY HAND. -->",
        "",
        "# Dataset downloads",
        "",
        "The authority for every line below is the named dataset's own `downloads()`",
        "function; this file is rendered from it by `python3 tools/datasets.py --write`.",
        "Editing this file changes a copy, not the loader -- and a copy forks. Data lands",
        "under `/mnt/20t/xubuqiang/datasets/<name>/` and is never committed; the code that",
        "loads and scores it stays in git.",
        "",
        "`python3 tools/datasets.py --check` reports which of these are present locally.",
        "",
    ]
    for row in rows:
        name = row["dataset"]
        lines.append(f"## `{name}`")
        lines.append("")
        if not row["entries"]:
            lines.append("_Declares no downloads._")
            lines.append("")
            continue
        for entry in row["entries"]:
            size = entry.get("size") or "size not stated"
            lines.append(f"### {entry.get('name')} ({entry['kind']}, {entry.get('version')})")
            lines.append("")
            lines.append(f"- **Version (pinned):** `{entry.get('version')}`")
            lines.append(f"- **Size:** {size}")
            if entry.get("url"):
                lines.append(f"- **URL:** {entry['url']}")
            if entry.get("repo"):
                lines.append(f"- **Repo:** `{entry['repo']}`")
            if entry.get("file"):
                lines.append(f"- **File:** `{entry['file']}`")
            if entry.get("package"):
                lines.append(f"- **Package:** `{entry['package']}=={entry.get('version')}`")
            if entry.get("dst"):
                lines.append(f"- **Destination:** `{entry['dst']}`")
            if entry.get("sha256"):
                lines.append(f"- **sha256:** `{entry['sha256']}`")
            lines.append("")
            lines.append(f"> {entry.get('note', '').strip()}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--list", action="store_true", help="print each dataset's needs")
    mode.add_argument("--check", action="store_true",
                      help="report which datasets are present locally")
    mode.add_argument("--write", action="store_true",
                      help="regenerate DOWNLOADS.md from the loaders")
    parser.add_argument("--dataset", action="append", help="only this dataset")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    rows = datasets_with_downloads()
    if args.dataset:
        rows = [r for r in rows if r[0] in set(args.dataset)]

    if args.write:
        INDEX.write_text(render_index([{"dataset": n, "entries": e} for n, e in rows]))
        print(f"wrote {INDEX.relative_to(ROOT)} ({len(rows)} dataset(s))")
        return 0

    if args.check:
        checked = [check_dataset(name, entries) for name, entries in rows]
        if args.json:
            print(json.dumps({"schema_version": _schema()["schema_version"],
                              "datasets": checked}, indent=1, sort_keys=True))
            return 0
        failed = 0
        for row in checked:
            mark = "ok  " if row["present"] else "MISS"
            if not row["present"]:
                failed += 1
            status = row["status"]
            extra = ""
            if status and status.get("tasks") is not None:
                extra = f" ({status.get('tasks')} task(s) loadable)"
            print(f"{mark} {row['dataset']}{extra}")
            for entry in row["entries"]:
                flag = "  ok " if entry["present"] else "  -- "
                print(f"{flag} [{entry['kind']}] {entry['name']} @ {entry['version']}"
                      f" -- {entry['detail']}")
        return 1 if failed else 0

    # Default and --list: what each dataset asks for.
    if args.json:
        print(json.dumps([{"dataset": n, "downloads": e} for n, e in rows],
                         indent=1, sort_keys=True))
        return 0
    for name, entries in rows:
        print(f"{name}: {len(entries)} item(s)")
        for entry in entries:
            print(f"  [{entry['kind']}] {entry['name']} @ {entry['version']} "
                  f"({entry.get('size', '?')})")
            if entry.get("url"):
                print(f"      {entry['url']}")
            print(f"      {entry.get('note', '').strip()}")
    if not rows:
        print("no published dataset declares downloads()")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
