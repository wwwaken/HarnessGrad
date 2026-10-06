#!/usr/bin/env python3
"""`tau` -- the command line the agent uses to act on the tau-bench database.

The task environment is a tau-bench domain: a JSON database, the domain's tool
implementations, and a policy. There is no chat: the agent acts by calling tools,
and this is the only way to call one. It is a single self-contained file so it can
also be run as `python3 /usr/local/bin/tau_cli.py` if the `tau` shim is missing.

    tau list                       print the tools and their argument schemas
    tau call <tool_name> '<json>'  invoke a tool against the database and print
                                   its observation (or `Error: ...`)
    tau policy                     print the policy the task must be handled under
    tau show                       print the current database as JSON

`tau call` reads `/app/db.json`, invokes the tool on the parsed database, writes
the (possibly mutated) database back to the same file, and prints what the tool
returned. Read-only tools persist an unchanged database, which is harmless. If the
tool raises, its exception is caught and printed as `Error: ...` -- exactly what
`tau_bench.envs.base.Env.step` does -- and the database is still saved, because a
tool may have mutated part of it before failing.

Every call is appended to `/app/tau_calls.jsonl` as evidence of what was done.
That file is the agent's own, so it is evidence and never the grade: the verifier
compares database hashes, not action logs.

Where things live (override with the matching environment variable):
    /app/db.json          TAU_DB            the database; the task's mutable state
    /opt/tau/lib          TAU_LIB           `tau_bench` tool classes (read-only)
    /opt/tau/policy       TAU_POLICY_DIR    `<domain>.txt`, printed by `tau policy`
    /app/tau_calls.jsonl  TAU_CALL_LOG      append-only log of `tau call`s
"""
from __future__ import annotations

import importlib
import json
import os
import sys
import tempfile
from pathlib import Path

LIB = Path(os.environ.get("TAU_LIB", "/opt/tau/lib"))
WORKDIR = Path(os.environ.get("TAU_WORKDIR", "/app"))
DB_PATH = Path(os.environ.get("TAU_DB", str(WORKDIR / "db.json")))
POLICY_DIR = Path(os.environ.get("TAU_POLICY_DIR", "/opt/tau/policy"))
CALL_LOG = Path(os.environ.get("TAU_CALL_LOG", str(WORKDIR / "tau_calls.jsonl")))

#: A database table that only one domain has is how the domain is recognised when
#: `--domain` is not given. The two sets are the keys of
#: `tau_bench.envs.<domain>.data.load_data()`.
DOMAIN_TABLES = {
    "retail": ("orders", "products", "users"),
    "airline": ("flights", "reservations", "users"),
}

#: Actions that end the conversation. Kept in step with each domain's
#: `Mock*DomainEnv.terminate_tools`; they never touch the database.
TERMINATE_TOOLS = ("transfer_to_human_agents",)


def _fail(message: str, code: int = 2) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(code)


def detect_domain(data: dict) -> str:
    keys = set(data)
    for domain, tables in DOMAIN_TABLES.items():
        if set(tables) <= keys:
            return domain
    _fail(f"cannot tell the domain from the database keys {sorted(keys)}; "
          f"pass --domain retail|airline")


def load_db() -> dict:
    if not DB_PATH.is_file():
        _fail(f"no database at {DB_PATH}")
    try:
        data = json.loads(DB_PATH.read_text())
    except ValueError as exc:
        _fail(f"{DB_PATH} is not valid JSON: {exc}")
    if not isinstance(data, dict):
        _fail(f"{DB_PATH} holds a {type(data).__name__}, expected a JSON object")
    return data


def save_db(data: dict) -> None:
    """Atomic: a tool call must never leave a half-written database behind."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".db-", dir=str(DB_PATH.parent))
    try:
        with os.fdopen(fd, "w") as handle:
            json.dump(data, handle, ensure_ascii=False, separators=(",", ":"))
        os.replace(tmp, DB_PATH)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def tools_for(domain: str) -> dict:
    if str(LIB) not in sys.path:
        sys.path.insert(0, str(LIB))
    try:
        module = importlib.import_module(f"tau_bench.envs.{domain}.tools")
    except ImportError as exc:
        _fail(f"cannot load the {domain} tools from {LIB}: {exc}")
    return {cls.get_info()["function"]["name"]: cls for cls in module.ALL_TOOLS}


def _log_call(domain: str, name: str, arguments, observation: str) -> None:
    """Append-only; a log that cannot be written must not fail the call."""
    try:
        CALL_LOG.parent.mkdir(parents=True, exist_ok=True)
        with CALL_LOG.open("a") as handle:
            handle.write(json.dumps({"domain": domain, "name": name,
                                     "arguments": arguments,
                                     "observation_chars": len(observation)},
                                    ensure_ascii=False) + "\n")
    except OSError:
        pass


def cmd_list(argv: list) -> int:
    domain = _domain()
    tools = tools_for(domain)
    infos = [tools[name].get_info() for name in tools]
    print(f"# {domain} tools ({len(infos)}); call one with "
          f"tau call <name> '<json-arguments>'")
    print(json.dumps(infos, indent=2, ensure_ascii=False))
    return 0


def cmd_policy(argv: list) -> int:
    domain = _domain()
    path = POLICY_DIR / f"{domain}.txt"
    if not path.is_file():
        _fail(f"no policy for {domain} at {path}")
    sys.stdout.write(path.read_text())
    return 0


def cmd_show(argv: list) -> int:
    print(json.dumps(load_db(), indent=1, ensure_ascii=False))
    return 0


def cmd_call(argv: list) -> int:
    # `tau call <tool> <json>`; the JSON is one shell argument, but join the rest so an
    # unquoted-but-space-separated JSON body still works.
    if len(argv) < 2:
        _fail("usage: tau call <tool_name> '<json-arguments>'")
    name, raw = argv[0], " ".join(argv[1:])
    if raw.strip() in ("", "-"):
        raw = sys.stdin.read()
    try:
        arguments = json.loads(raw)
    except ValueError as exc:
        _fail(f"arguments for {name} are not valid JSON: {exc}")
    if not isinstance(arguments, dict):
        _fail(f"arguments for {name} must be a JSON object, got "
              f"{type(arguments).__name__}")

    data = load_db()
    domain = _domain(data)
    tools = tools_for(domain)
    if name not in tools:
        print(f"Error: unknown tool {name!r}; available: "
              + ", ".join(sorted(tools)))
        return 1
    try:
        observation = tools[name].invoke(data, **arguments)
    except Exception as exc:  # noqa: BLE001 - mirrors Env.step's blanket catch
        observation = f"Error: {exc}"
    save_db(data)
    _log_call(domain, name, arguments, str(observation))
    print(observation if isinstance(observation, str)
          else json.dumps(observation, ensure_ascii=False))
    return 0


def _extract_domain(argv: list) -> list:
    """Pull a global `--domain X` / `--domain=X` out of `argv` into TAU_DOMAIN."""
    rest = []
    i = 0
    while i < len(argv):
        item = argv[i]
        if item == "--domain":
            if i + 1 >= len(argv):
                _fail("--domain needs a value")
            os.environ["TAU_DOMAIN"] = argv[i + 1]
            i += 2
            continue
        if item.startswith("--domain="):
            os.environ["TAU_DOMAIN"] = item.split("=", 1)[1]
            i += 1
            continue
        rest.append(item)
        i += 1
    return rest


def _domain(data: dict | None = None) -> str:
    """`--domain`/`TAU_DOMAIN`, else the domain inferred from the database."""
    explicit = os.environ.get("TAU_DOMAIN") or ""
    if explicit:
        if explicit not in DOMAIN_TABLES:
            _fail(f"unknown domain {explicit!r}; expected retail or airline")
        return explicit
    return detect_domain(load_db() if data is None else data)


USAGE = """tau -- act on the tau-bench database

  tau list                        list tools and their argument schemas
  tau call <tool_name> '<json>'   call a tool and print its observation
  tau policy                      print the policy to follow
  tau show                        print the current database

The database is /app/db.json; `tau call` writes it back after every call.
Adding --domain retail|airline anywhere overrides domain detection.
"""


def main(argv: list) -> int:
    argv = _extract_domain(list(argv))
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(USAGE)
        return 0
    command, rest = argv[0], argv[1:]
    handlers = {"list": cmd_list, "call": cmd_call, "policy": cmd_policy,
                "show": cmd_show}
    if command not in handlers:
        print(f"Error: unknown command {command!r}", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        return 2
    return handlers[command](rest)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
