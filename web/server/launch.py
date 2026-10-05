"""``GET /api/launch/options``: what the Launch form may offer, and from where.

Five sources, each read as the driver would read it:

* harnesses -- ``base_harness/*/harness.json``;
* datasets  -- ``data/*.py`` modules that declare a top-level ``load()``;
* improvers -- ``improvers/improvers.json`` (names plus the default);
* flags     -- ``driver.py --help``;
* environment -- ``.env`` plus the process environment.

**A secret's value is never returned.**  The redaction is name-based first
(``KEY``, ``TOKEN``, ``SECRET``, ``PASSWORD``, ``PASSPHRASE``, ``CREDENTIAL``)
and value-shaped second (anything that looks like a provider key), so a variable
added to ``.env`` tomorrow is redacted without a code change.  A redacted field
still reports ``set`` and ``secret`` so the form can say "a credential is
present" without ever seeing it.
"""
from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

#: Substrings that make a variable's value unreturnable, case-insensitive.
SECRET_HINTS = ("KEY", "TOKEN", "SECRET", "PASSWORD", "PASSPHRASE", "CREDENTIAL")
#: Value shapes that are credentials whatever the variable is called.
_SECRET_VALUE_RE = re.compile(r"^(sk-|ghp_|gho_|ghs_|xox[baprs]-|AKIA|ASIA|AIza)")

#: The CLI flag each environment variable backs, where one exists.  Everything
#: else is documented by `driver.py --help` under "configuration", which is to
#: say it is environment-only and has no flag.
_FLAG_FOR = {
    "HG_IMPROVER": "--improver",
    "HG_IMPROVER_MODEL": "--improver-model",
    "HG_IMPROVER_EFFORT": "--improver-effort",
    "HG_METHOD_TIMEOUT_S": "--method-timeout (mode B; this bounds one call)",
    "HG_RUN_ROOT": "--runs-root",
}

_NO_FLAG = "(no flag; environment only)"

#: `--sampling` is a free-form string in the driver (`below_X`, `random_N`); the
#: help text names the shape and these are the values the platform records.
SAMPLINGS = ["all", "below_0.5", "above_0.5", "random_10"]

_HELP_CACHE: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# .env and driver.py --help
# ---------------------------------------------------------------------------

def parse_env_file(repo: Path) -> dict[str, str]:
    """``.env`` as a name -> value map.  Quoted values are unquoted; nothing else.

    This reads the file the driver folds into a run's environment.  Values are
    kept here so the caller can decide which ones may be returned; the caller
    must ask `is_secret()` before putting one in a response.
    """
    path = repo / ".env"
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    values: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        name, _, value = stripped.partition("=")
        name, value = name.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if name:
            values[name] = value
    return values


def is_secret(name: str, value: str | None) -> bool:
    """Whether this variable's value must never leave the process."""
    upper = name.upper()
    if any(hint in upper for hint in SECRET_HINTS):
        return True
    if value and _SECRET_VALUE_RE.match(value):
        return True
    return False


def driver_help(repo: Path) -> dict[str, Any]:
    """``python3 -B driver.py --help``, cached for the process lifetime.

    ``-B`` / ``PYTHONDONTWRITEBYTECODE=1`` keep the probe from leaving
    ``__pycache__`` anywhere in the platform tree: the API is an observer.
    """
    global _HELP_CACHE
    if _HELP_CACHE is not None:
        return _HELP_CACHE
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result: dict[str, Any] = {"text": "", "returncode": None, "error": None}
    try:
        proc = subprocess.run(
            [sys.executable, "-B", str(repo / "driver.py"), "--help"],
            cwd=str(repo), capture_output=True, text=True, timeout=60, env=env,
        )
        result["text"] = proc.stdout or proc.stderr
        result["returncode"] = proc.returncode
    except (OSError, subprocess.SubprocessError) as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    _HELP_CACHE = result
    return result


def parse_help(text: str) -> dict[str, Any]:
    """Split ``--help`` into ``flag_help`` and the declared environment variables.

    The output has two relevant sections.  ``options:`` lists flags; each entry
    begins with exactly two spaces and a non-space, and its description continues
    on lines indented further.  ``configuration ...:`` lists ``NAME=default``
    with a one-line note.  Everything is parsed textually -- no argparse import,
    no executing the driver -- so a driver that is broken still yields options.
    """
    flags: dict[str, str] = {}
    envs: list[tuple[str, str | None, str]] = []
    section: str | None = None
    current_flag: str | None = None
    current_env: int | None = None

    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if stripped == "options:":
            section, current_flag, current_env = "options", None, None
            continue
        if stripped.startswith("configuration") and stripped.endswith(":"):
            section, current_flag, current_env = "config", None, None
            continue

        if section == "options":
            if re.match(r"^  \S", line):
                body = line[2:]
                parts = re.split(r"\s{2,}", body, maxsplit=1)
                head = parts[0]
                description = parts[1].strip() if len(parts) > 1 else ""
                long_flags = re.findall(r"--[A-Za-z0-9][A-Za-z0-9-]*", head)
                current_flag = long_flags[0] if long_flags else head.split()[0]
                flags[current_flag] = description
            elif current_flag and line.startswith("    "):
                extra = stripped
                if extra:
                    flags[current_flag] = (flags[current_flag] + " " + extra).strip()
        elif section == "config":
            match = re.match(
                r"^  (?P<name>[A-Z][A-Z0-9_]*)(?:=(?P<default>\S*))?"
                r"(?:\s{2,}(?P<note>.*))?$", line)
            if match:
                envs.append((match.group("name"), match.group("default"),
                             (match.group("note") or "").strip()))
                current_env = len(envs) - 1
            elif current_env is not None and line.startswith("    ") and stripped:
                name, default, note = envs[current_env]
                envs[current_env] = (name, default, (note + " " + stripped).strip())

    choices = {
        "modes": re.findall(r"--mode \{([^}]*)\}", text),
        "sides": re.findall(r"--side \{([^}]*)\}", text),
    }
    return {"flags": flags, "envs": envs, "choices": choices}


# ---------------------------------------------------------------------------
# base_harness/, data/, improvers/
# ---------------------------------------------------------------------------

def harness_names(repo: Path) -> list[str]:
    """Directories under ``base_harness/`` that carry a ``harness.json``."""
    root = repo / "base_harness"
    try:
        return sorted(p.parent.name for p in root.glob("*/harness.json"))
    except OSError:
        return []


def declares_load(path: Path) -> bool:
    """Whether a module is a dataset: it declares a top-level, zero-argument ``load()``.

    Parsed with ``ast`` rather than imported: importing every dataset would
    execute it (and could need a container or a model endpoint) just to list a
    name.  The zero-argument test is what separates a dataset from
    ``data/registry.py``, whose ``load(name)`` is the loader the driver calls:
    it is infrastructure, not a task set.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError, ValueError):
        return False
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name != "load":
            continue
        args = node.args
        if (not args.args and not args.posonlyargs and not args.kwonlyargs
                and args.vararg is None and args.kwarg is None):
            return True
    return False


def dataset_names(repo: Path) -> list[str]:
    """``data/*.py`` modules that declare a top-level ``load()``."""
    root = repo / "data"
    try:
        return sorted(p.stem for p in root.glob("*.py") if declares_load(p))
    except OSError:
        return []


def improver_registry(repo: Path) -> tuple[list[str], str | None, str | None]:
    """``(names_with_default_first, default, error)`` from ``improvers.json``."""
    path = repo / "improvers" / "improvers.json"
    try:
        raw = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except OSError as exc:
        return [], None, f"cannot read improvers.json: {exc}"
    except json.JSONDecodeError as exc:
        return [], None, f"improvers.json is not JSON: {exc}"
    if not isinstance(raw, dict):
        return [], None, "improvers.json is not a JSON object"
    entries = raw.get("improvers")
    names = sorted(entries) if isinstance(entries, dict) else []
    default = raw.get("default")
    if isinstance(default, str) and default and default in names:
        names = [default] + [n for n in names if n != default]
    return names, (default if isinstance(default, str) else None), None


# ---------------------------------------------------------------------------
# The endpoint body
# ---------------------------------------------------------------------------

def _first_choice(choices: list[str], fallback: list[str]) -> list[str]:
    if not choices:
        return list(fallback)
    return [part.strip() for part in choices[0].split(",") if part.strip()]


def build_launch_options(repo: Path) -> dict[str, Any]:
    """The whole ``GET /api/launch/options`` body.

    The process environment wins over ``.env`` when both set a variable, because
    the process is the more recent statement of intent; ``.env`` is what a run
    started from this directory would actually fold in.  Either way a secret is
    reported as ``{set: true, secret: true, value: null}``.
    """
    help_info = driver_help(repo)
    parsed = parse_help(help_info.get("text") or "")
    env_file = parse_env_file(repo)

    help_envs = {name: (default, note) for name, default, note in parsed["envs"]}
    ordered = [name for name, _default, _note in parsed["envs"]]
    ordered += sorted(name for name in env_file if name not in help_envs)

    env_derived: list[dict[str, Any]] = []
    for name in ordered:
        from_env = os.environ.get(name)
        from_file = env_file.get(name)
        if from_env not in (None, ""):
            value = from_env
        elif from_file not in (None, ""):
            value = from_file
        else:
            value = None
        secret = is_secret(name, value)
        _default, note = help_envs.get(name, (None, ""))
        if not note:
            note = "Declared in `.env`; `driver.py --help` does not list a default."
        env_derived.append({
            "flag": _FLAG_FOR.get(name, _NO_FLAG),
            "env_var": name,
            "value": None if (secret or value is None) else value,
            "set": value is not None,
            "secret": secret,
            "note": note,
        })

    improvers, default_improver, improver_error = improver_registry(repo)
    options: dict[str, Any] = {
        "harnesses": harness_names(repo),
        "datasets": dataset_names(repo),
        "samplings": list(SAMPLINGS),
        "improvers": improvers,
        "default_improver": default_improver,
        "env_derived": env_derived,
        # Extra keys the SPA's `LaunchOptions` type reads; harmless to the
        # contract and the reason the built frontend works unchanged.
        "improver_names": improvers,
        "modes": _first_choice(parsed["choices"]["modes"], ["A", "B"]),
        "sides": _first_choice(parsed["choices"]["sides"], ["train", "eval"]),
        "flag_help": parsed["flags"],
    }
    if improver_error:
        options["problems"] = [improver_error]
    if help_info.get("error"):
        options["problems"] = options.get("problems", []) + [
            f"driver.py --help could not be read: {help_info['error']}"]
    return options
