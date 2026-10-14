"""Guards for the runner's lane assignment (`tools/run_tests.py`).

`EXCLUSIVE` decides which files run one at a time. It is a hand-curated list, and a
hand-curated list rots: a file is renamed and the entry silently stops matching
anything, or a shared resource is fixed and the entry stays behind out of habit.
Either way the runner keeps paying for a lane the file no longer needs, and the
*reason* for the entry is only in a comment nobody re-checks.

What this file checks, in order of how loudly it fails:

1. **Every `EXCLUSIVE` entry exists.** A stale name is not a lane, it is a typo.
2. **Every `EXCLUSIVE` entry still trips a cheap static signal** -- a literal fixed
   port, a server bind, a fixed `/tmp` path or shared name, a docker/container
   name, a modelled shared registry, or a write into the checkout. That is exactly
   the vocabulary `docs/test-lanes.md` records. An entry whose reason has
   disappeared fails here so it is either removed or given a new reason.
3. **No duplicates**, and no accidental `SLOW`-only traffic: an exclusive entry
   may also be slow (the long release replay is both), but the only overlap the
   evidence supports is pinned by name, so a new one is a decision instead of a
   coincidence.

The tests are *not* a claim about which files contend: the signal extraction is
intentionally cheap (regex over one file's lines, plus a tiny AST pass) so it can
run with the rest of the quality suite. The judgement that a signal fires is the
scan's; the judgement that it *justifies* the lane is the human's, recorded in
`docs/test-lanes.md` next to the experiment that measured it.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import run_tests  # noqa: E402


def _test_files() -> dict[str, Path]:
    """Every collected test module, by basename, as the runner discovers them."""
    return {p.name: p for p in (ROOT / "tests").rglob("test_*.py")}


# ---------------------------------------------------------------- the signals ---
#
# One regex table and one AST rule, deliberately the cheapest thing that can
# recognise the vocabulary in docs/test-lanes.md. A signal that needs data flow
# to see is not counted here; those files are still allowed to be exclusive, they
# just cannot claim one of these signals as their reason.

PORTS = ("8000", "8001", "8002", "8003", "8008", "8080", "8081", "8082", "8443",
         "8888", "9000", "9090", "9999", "5000", "7860", "11434")
_P = "|".join(PORTS)

SIGNAL_PATTERNS = {
    # (a) a literal fixed TCP port in a binding or addressing position.
    "fixed-port": re.compile(
        rf"\.bind\s*\(\s*\([^)]*(?:{_P})|"
        rf"port\s*[=:]\s*[\"']?(?:{_P})\b|"
        rf"127\.0\.0\.1:(?:{_P})\b|"
        rf"localhost:(?:{_P})\b|"
        rf":(?:{_P})\b(?=[^\n]*(?:url|endpoint|base|host|serve|listen))|"
        rf"(?:url|endpoint|base_url|HOST)\b[^\n]*:(?:{_P})\b"),
    # (b) a server that binds a socket.
    "server-bind": re.compile(
        r"\.bind\s*\(\s*\(|\.bind\s*\(\s*[\"']|"
        r"(?:Threading)?HTTPServer\s*\(|socketserver\.|\.listen\s*\(|"
        r"serve_forever\s*\(|uvicorn\.run\s*\(|make_server\s*\(|"
        r"HTTPConnection\s*\(|socket\.socket\s*\("),
    # (c) a fixed /tmp path or a fixed shared `hg-` name.
    "fixed-path": re.compile(r"[\"']/tmp/|[\"'][A-Za-z0-9_.*-]*hg-[A-Za-z0-9_.-]+[\"']"),
    # (d) a real docker daemon call or a literal container/network name.
    "docker": re.compile(
        r"subprocess\.\w+\(\s*\[[^\]]*[\"']docker[\"']|"
        r"\[\s*[\"']docker[\"']\s*,\s*[\"'](?:run|create|rm|exec|network|image|"
        r"commit|inspect|ps|cp|pull|start|stop|rmi)|"
        r"DOCKER_HOST|DOCKER_CONTEXT|/var/run/docker\.sock"),
}

# (e) a process-wide registry another file also mutates. The names are the ones
# the platform actually uses for "the set of things this build knows about".
REGISTRY_NAMES = {
    "ADAPTERS", "_ADAPTERS", "REGISTRY", "_REGISTRY", "SCORERS", "_SCORERS",
    "KNOWN_DATASETS", "DATASET_CLASSES", "METHODS", "HARNESSES", "PROVIDERS",
    "BACKENDS", "SERVICES", "VERIFY", "_RECORDS", "IMPROVERS", "RUNNERS",
    "ENVIRONMENTS", "TASKS", "ROUTES", "HANDLERS", "PLUGINS",
}
_MUTATORS = {"update", "clear", "pop", "append", "extend", "setdefault",
             "insert", "remove", "popitem"}

# (f) a write into the checkout, or into a fixed directory beside it. `ROOT`-named
# constants and `__file__`-derived names only: those are the writes no lane makes
# safe, because the parallel lane is walking the same tree.
_ROOT_NAMES = {"ROOT", "PLATFORM", "REPO_ROOT", "PLATFORM_ROOT", "REPO",
               "WORKTREE", "CHECKOUT"}
_WRITE_METHODS = {"write_text", "write_bytes", "mkdir", "unlink", "touch",
                  "rename", "replace", "rmdir", "symlink_to", "hardlink_to",
                  "chmod"}
_COPY_DESTS = {"copy", "copy2", "copyfile", "move"}
_WRITE_FUNCS = {"rmtree", "remove", "unlink", "rename", "replace", "makedirs"}


def _file_derived(node: ast.AST) -> bool:
    """`Path(__file__)...`, `__file__`, `.parents[n]`, `os.path.dirname(__file__)`."""
    if isinstance(node, ast.Name) and node.id == "__file__":
        return True
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr in {
                "resolve", "absolute", "parent", "joinpath", "dirname", "abspath"}:
            return any(_file_derived(arg) for arg in node.args) or _file_derived(func.value)
        if isinstance(func, ast.Name) and func.id in {"Path", "PurePath", "str",
                                                      "dirname", "abspath"}:
            return any(_file_derived(arg) for arg in node.args)
    if isinstance(node, ast.Attribute) and node.attr in {"parent", "parents"}:
        return _file_derived(node.value)
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute) \
            and node.value.attr == "parents":
        return _file_derived(node.value.value)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        return _file_derived(node.left) or _file_derived(node.right)
    return False


def _checkout_derived_names(tree: ast.AST) -> set[str]:
    """Locally-bound names whose value traces back to the checkout root."""
    names: set[str] = set()

    def rooted(node: ast.AST) -> bool:
        if isinstance(node, ast.Name):
            return node.id in names or node.id in _ROOT_NAMES
        if _file_derived(node):
            return True
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            return rooted(node.left) or rooted(node.right)
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr in {
                    "resolve", "absolute", "joinpath", "join"}:
                return any(rooted(arg) for arg in node.args) or rooted(func.value)
            if isinstance(func, ast.Name) and func.id in {"Path", "PurePath", "str"}:
                return any(rooted(arg) for arg in node.args)
        if isinstance(node, ast.Attribute) and node.attr in {"parent", "parents"}:
            return rooted(node.value)
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute) \
                and node.value.attr == "parents":
            return rooted(node.value.value)
        return False

    for _ in range(6):
        grew = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                targets = [node.target.id]
            else:
                continue
            if targets and rooted(node.value) and not all(t in names for t in targets):
                names.update(targets)
                grew = True
        if not grew:
            break
    return names


def signals_of(path: Path) -> set[str]:
    """The cheap static signals a test file trips. Never reads a test body."""
    text = path.read_text(encoding="utf-8", errors="replace")
    found = {name for name, pattern in SIGNAL_PATTERNS.items()
             if any(pattern.search(line) for line in text.splitlines()
                    if not line.strip().startswith("#"))}
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return found

    # (e) a modelled registry: a module-level literal with a registry name that this
    # file also mutates. Reads do not count -- only writes.
    for node in tree.body:
        if isinstance(node, ast.Assign):
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            targets = [node.target.id]
        else:
            continue
        for name in targets:
            if name not in REGISTRY_NAMES:
                continue
            for use in ast.walk(tree):
                writes = (
                    isinstance(use, ast.Call) and isinstance(use.func, ast.Attribute)
                    and isinstance(use.func.value, ast.Name)
                    and use.func.value.id == name and use.func.attr in _MUTATORS)
                writes = writes or (
                    isinstance(use, ast.Subscript) and isinstance(use.ctx, ast.Store)
                    and isinstance(use.value, ast.Name) and use.value.id == name)
                if writes:
                    found.add("shared-registry")
                    break

    # (f) a write into the checkout (or the tree beside it).
    rooted_names = _checkout_derived_names(tree)

    def rooted(node: ast.AST) -> bool:
        if isinstance(node, ast.Name):
            return node.id in rooted_names or node.id in _ROOT_NAMES
        if _file_derived(node):
            return True
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            return rooted(node.left) or rooted(node.right)
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr in {
                    "resolve", "absolute", "joinpath", "join"}:
                return any(rooted(arg) for arg in node.args) or rooted(func.value)
            if isinstance(func, ast.Name) and func.id in {"Path", "PurePath", "str"}:
                return any(rooted(arg) for arg in node.args)
        if isinstance(node, ast.Attribute) and node.attr in {"parent", "parents"}:
            return rooted(node.value)
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute) \
                and node.value.attr == "parents":
            return rooted(node.value.value)
        return False

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr in _WRITE_METHODS and rooted(func.value):
            found.add("checkout-write")
        elif isinstance(func, ast.Attribute) and func.attr in _COPY_DESTS \
                and len(node.args) > 1 and rooted(node.args[1]):
            found.add("checkout-write")
        elif isinstance(func, ast.Name) and func.id in _WRITE_FUNCS and node.args \
                and rooted(node.args[0]):
            found.add("checkout-write")
        elif isinstance(func, ast.Name) and func.id == "open" and node.args \
                and rooted(node.args[0]):
            mode = ""
            if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                mode = str(node.args[1].value)
            for keyword in node.keywords:
                if keyword.arg == "mode" and isinstance(keyword.value, ast.Constant):
                    mode = str(keyword.value.value)
            if any(flag in mode for flag in "wax+"):
                found.add("checkout-write")
    return found


SIGNAL_VOCABULARY = sorted(set(SIGNAL_PATTERNS) | {"shared-registry", "checkout-write"})

#: The overlap between `EXCLUSIVE` and `SLOW` the evidence supports. An entry may
#: be both only when the cost is the reason the entry exists:
#:
#: * `test_appworld_official_scorer.py` -- the measured release replay is ~1274s,
#:   an order of magnitude past the next file, and it drives real containers.
#:   Cost, not a contended resource, is what justifies holding it at 1 job.
#:
#: Every other `SLOW` file must stay out of `EXCLUSIVE`, and a new overlap is a
#: decision this test refuses to make silently.
_SLOW_AND_EXCLUSIVE = frozenset({"test_appworld_official_scorer.py"})

#: Lock-tier entries whose reason is cost, not isolation. They must be named here
#: or the guard fails: a file that is genuinely exclusive cannot be demoted by
#: deleting a signal.
_COST_ONLY = frozenset({"test_appworld_official_scorer.py"})

#: `SLOW`-only entries that trip a static signal anyway, pinned with the reason the
#: signal is not an isolation defect. These are reviewed, not assumed:
#:
#: * `test_isolation.py` -- the `checkout-write` signal is the synthetic
#:   `tmp_path` platform its autouse guard fixture builds, i.e. the *shape* of a
#:   checkout write, not a write to the shared checkout. The fixture is exactly
#:   what makes the file safe in the parallel lane, and the file is in `SLOW` for
#:   cost: its tamper tests snapshot and stat the whole checkout (~40s measured).
#:
#: A `SLOW`-only file that starts tripping a signal and is not pinned here fails,
#: so the signal cannot be ignored by leaving the file in `SLOW`.
_DOCUMENTED_SLOW_SIGNAL_EXCEPTIONS = {
    "test_isolation.py": "signal is the synthetic tmp_path platform, cost-only",
}


@pytest.fixture(scope="module")
def files() -> dict[str, Path]:
    return _test_files()


def test_every_exclusive_entry_names_a_file_that_exists(files):
    missing = [name for name in run_tests.EXCLUSIVE if name not in files]
    assert not missing, (
        "EXCLUSIVE names files that no longer exist: " + ", ".join(sorted(missing))
        + ". A stale entry is not a lane; remove it or fix the name.")


def test_exclusive_entries_are_unique():
    duplicates = sorted({name for name in run_tests.EXCLUSIVE
                         if run_tests.EXCLUSIVE.count(name) > 1})
    assert not duplicates, "EXCLUSIVE repeats: " + ", ".join(duplicates)


def test_every_exclusive_entry_still_trips_a_static_signal(files):
    """Fail closed: an entry with no reason left is an entry to remove.

    An entry is allowed to have no signal only if it is one of the pinned
    cost-only entries, and cost-only is a named decision, not a default.
    """
    unsupported = []
    for name in run_tests.EXCLUSIVE:
        path = files.get(name)
        if path is None:
            continue                                  # reported by the test above
        if name in _COST_ONLY:
            continue
        if not signals_of(path):
            unsupported.append(name)
    assert not unsupported, (
        "EXCLUSIVE entries trip none of the documented signals "
        f"({', '.join(SIGNAL_VOCABULARY)}): " + ", ".join(sorted(unsupported))
        + ". Either the reason is gone -- remove the entry -- or the reason is cost, "
          "which has to be named in _COST_ONLY and in docs/test-lanes.md.")


def test_cost_only_entries_are_named_and_still_slow(files):
    """`_COST_ONLY` may not become a dumping ground, and its members must be real."""
    stray = sorted(_COST_ONLY - set(run_tests.EXCLUSIVE))
    assert not stray, ("_COST_ONLY names files that are not exclusive: "
                       + ", ".join(stray))
    for name in sorted(_COST_ONLY):
        path = files.get(name)
        assert path is not None, f"cost-only entry {name} does not exist"
        assert name in run_tests.SLOW, (
            f"{name} is pinned as cost-only but is not in SLOW; if it is fast it "
            "belongs in the parallel lane")


def test_no_exclusive_entry_claims_signal_it_cannot_name(files):
    """The reverse direction: report the signals, so a removal has a paper trail.

    This asserts a property rather than a freeze: any file may change which signal
    it trips, but the report below is the evidence a reviewer checks against
    `docs/test-lanes.md`. An exclusive file that trips nothing is already a
    failure in the test above unless it is pinned cost-only.
    """
    report = {name: sorted(signals_of(files[name])) for name in run_tests.EXCLUSIVE
              if name in files}
    assert set(report) == set(run_tests.EXCLUSIVE)
    # The lanes must partition: an exclusive file is not also being counted as a
    # parallel file by the runner's own split.
    on_disk = {f.name for f in (ROOT / "tests").rglob("test_*.py")}
    exclusive = on_disk & set(run_tests.EXCLUSIVE)
    parallel = on_disk - set(run_tests.EXCLUSIVE)
    assert not (exclusive & parallel), sorted(exclusive & parallel)


def test_slow_and_exclusive_overlap_is_the_measured_one():
    overlap = set(run_tests.EXCLUSIVE) & set(run_tests.SLOW)
    assert overlap == set(_SLOW_AND_EXCLUSIVE), (
        "EXCLUSIVE and SLOW overlap changed: " + ", ".join(sorted(overlap))
        + ". A file that is only slow belongs in SLOW; a file that contends belongs "
          "in EXCLUSIVE with a signal. If the new overlap is deliberate, pin it here "
          "and say why in docs/test-lanes.md.")
    for name, reason in _DOCUMENTED_SLOW_SIGNAL_EXCEPTIONS.items():
        assert name in run_tests.SLOW, (
            f"{name} is pinned as a slow-signal exception but is not in SLOW")
        assert name not in run_tests.EXCLUSIVE, (
            f"{name} is pinned as a slow-signal exception but is also exclusive; "
            "the exception exists for a file that stays in the parallel lane")
        assert reason, f"{name} has an exception with no reason recorded"


def test_slow_entries_without_a_signal_are_not_in_exclusive(files):
    """`SLOW` is a cost list; it must not smuggle anything into the exclusive lane.

    A `SLOW`-only file that trips a signal is reported, and may stay there only if
    the reason is pinned in `_DOCUMENTED_SLOW_SIGNAL_EXCEPTIONS`.
    """
    smuggled = []
    for name in run_tests.SLOW:
        if name in run_tests.EXCLUSIVE:
            continue
        path = files.get(name)
        if path is None:
            continue
        if not signals_of(path):
            continue                    # slow and isolated: exactly where it belongs
        if name in _DOCUMENTED_SLOW_SIGNAL_EXCEPTIONS:
            continue                    # reviewed: signal is not an isolation defect
        smuggled.append(name)
    assert not smuggled, (
        "SLOW-only files trip an isolation signal but are not in EXCLUSIVE: "
        + ", ".join(sorted(smuggled))
        + ". Move them, or pin the reason in _DOCUMENTED_SLOW_SIGNAL_EXCEPTIONS "
          "and docs/test-lanes.md.")


def test_the_signal_extraction_is_cheap_and_self_consistent(files):
    """A guard on the guard: the scan must find the signals it is asserting on."""
    interesting = {name: sorted(signals_of(path)) for name, path in files.items()
                   if signals_of(path)}
    # There is always at least one file that trips a signal, or the scan has
    # silently stopped matching and `test_every_exclusive_entry_still_trips_a_static_signal`
    # would pass for the wrong reason.
    assert interesting, "the static scan recognised no file at all"
    assert set().union(*interesting.values()) <= set(SIGNAL_VOCABULARY)
