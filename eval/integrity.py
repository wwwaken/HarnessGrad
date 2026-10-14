"""Checks that keep a run from silently invalidating itself.

Two things must hold for a measurement to mean anything, and the operating system
enforces neither. Both were measured on this platform rather than assumed, by
running a harness whose entrypoint probes its own surroundings and reports what it
found:

    up1/driver.py, up2/driver.py            absent      (the `..` climb is closed)
    abs /…/HarnessGrad/.env                 READABLE
    abs /…/HarnessGrad/driver.py            READABLE
    abs /…/HarnessGrad/eval/metrics.py      READABLE
    write /…/HarnessGrad/_probe             WROTE

  1. **The harness cannot reach the platform by accident.** The workspace used to
     be `runs/<id>/workspace`, inside the platform tree and two `..` from the
     driver, the scorer and `.env`. It now lives outside; the relative climb is
     gone and a run refuses to start if the two ever overlap again.

  2. **The method cannot rewrite the platform.** The platform's whole claim is
     that scoring is its own -- a method that edits the scorer is not being
     measured, it is marking its own paper. Same for the harness, which is
     arbitrary code the platform did not write.

Neither can be made *impossible* without a real sandbox (container, user
namespace, bind mount), and the measurement above shows what that costs: an
absolute path still reaches everything, because the subject runs as the same user.
So the second half is detection, and it is where the guarantee actually lives --
the platform hashes its own files around every method call and every evaluation
and **fails the run, naming the paths**, if anything moved.

Three claims, three statuses, kept apart on purpose:

    the harness cannot reach the platform by `..`     enforced (workspace moved)
    the harness cannot reach the platform at all       detected (hashes, per run)
    the method cannot reach the platform at all        detected (hashes, per call)

Read the numbers above before trusting a score from a harness you did not write.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

#: What counts as the platform: everything a run reads to decide what a number
#: means. `.env` is here because it holds the credentials the measurement is paid
#: for, and `docs/` because it is the written contract an adapter is written
#: against.
#:
#: `harnessgrad/` is where the platform's implementation lives now -- the entrypoint
#: `driver.py` wires it up. It is the referee in the most literal sense (it decides what a
#: round is, what a curve point contains and which failures are the platform's own), so it
#: is hashed like the rest. A move that left it out would have put the whole scoring path
#: outside the check while the tuple still looked complete.
#:
#: `base_harness/` is deliberately **not** here. It is a candidate, not a referee:
#: every run copies it into a workspace first, and the copy is what gets edited.
#: Listing it would flag the one write the platform exists to make. A run's
#: workspaces live outside the platform root entirely, so no legitimate write
#: lands in the paths below.
PLATFORM = ("driver.py", "harnessgrad", "eval", "ckpt", "data", "tools", "methods",
            "tests", "docs", "improvers", "INTERFACE.md", ".env")

#: Top-level entries that are deliberately **not** hashed, each with its reason.
#:
#: The list above is hand-written, and a hand-written list of "everything that matters"
#: is a list that goes stale the moment the tree grows. `improvers/` was added while this
#: comment was being written and was **not** covered: it holds the default `skill.md`
#: handed to the improver and the registry that decides *which* improver runs -- both
#: referee-side, both editable by a method without the check firing. That is the
#: platform's central claim, so the gap matters.
#:
#: The fix is not a longer list, it is a check: every top-level entry must be either in
#: `PLATFORM` or in here with a written reason
#: (`tests/quality/test_integrity.py::test_every_top_level_entry_is_classified`).
#: Adding a directory then forces a decision instead of silently widening the hole.
NOT_PLATFORM = {
    "base_harness": "a **candidate**, not a referee: each run copies it into a workspace "
                    "and the copy is what a method edits, so hashing it would flag the "
                    "one write the platform exists to make",
    "current_harness": "output of `tools/export_harnesses.py`, derived from runs; "
                       "nothing a run reads",
    "legacy": "unmaintained historical record (see `legacy/README.md`); not a supported "
              "route and not imported or read at run time",
    "install.sh": "provisions a machine (`bubblewrap`, `git`, `python3`); it does not "
                  "decide what a number means",
    "README.md": "the front door for a human, not something a run reads",
    "DOWNLOADS.md": "**generated** by `tools/datasets.py --write` from each loader's "
                    "`downloads()`; it changes whenever a dataset is added and decides "
                    "nothing a run reads (the loaders do). Hashing it would invalidate "
                    "every past run's certification for a reason that cannot change a "
                    "number -- the same argument as `web/`",
    "LICENSE": "the licence text; hashing it would change nothing about a measurement",
    ".env.example": "the template for `.env`; it holds placeholders, and `.env` itself "
                    "(which holds the credentials) is hashed",
    ".harnessgrad-state": "runtime state written by `tools/harnessgrad.sh` (pid files, "
                          "a log); generated, like `runs/`",
    ".pytest_cache": "pytest's own cache; generated by running the tests",
    "web": "the frontend SPA (`web/`): a **human** reads it, a run does not. It is built "
           "from `runs/` through a read API and its build output changes on every build, "
           "so hashing it would fail a run for a reason that cannot change a number. "
           "`harnessgrad/api/` -- the server the SPA talks to -- *is* platform, because a "
           "run's reader can be misled by it",
    "reports": "audit, evidence and review output that used to sit in the repository root "
               "and was moved here so the root stays navigable. It is written by humans and "
               "review sessions after a measurement, never read by a run; hashing it would "
               "fail a certification because someone added a report",
    "AGENTS.md": "operating rules for the agents and humans who work *on* the platform -- "
                 "review discipline, pilot policy, prohibited shortcuts. It governs how the "
                 "platform is changed, not what a number means, and no run reads it",
}

#: Where those names live, resolved from this file rather than from the working
#: directory: `driver.py` runs from the platform root, but the tests do not.
PLATFORM_ROOT = Path(__file__).resolve().parents[1]


def _digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot(root: Path) -> dict[str, str]:
    """Content digest of every platform file. Small: tens of files, kilobytes."""
    out: dict[str, str] = {}
    for name in PLATFORM:
        target = root / name
        if target.is_file():
            out[name] = _digest(target)
        elif target.is_dir():
            for p in sorted(target.rglob("*")):
                if p.is_file() and "__pycache__" not in p.parts \
                        and not p.name.endswith(".pyc"):
                    out[str(p.relative_to(root))] = _digest(p)
    return out


def diff(before: dict[str, str], after: dict[str, str]) -> dict[str, list[str]]:
    """What changed: added, removed, modified."""
    b, a = set(before), set(after)
    return {
        "added": sorted(a - b),
        "removed": sorted(b - a),
        "modified": sorted(k for k in b & a if before[k] != after[k]),
    }


def content_sha(root: Path) -> str:
    """One digest for the whole platform: what decided what this run's numbers mean.

    **A run's numbers are only comparable with another run's if the two ran the same
    platform, and until now nothing on disk said which platform that was.** Measured
    2026-10-05: 82 run directories, and not one recorded the content of the code that
    produced it -- so a reader could not tell a curve measured before a fix from one
    measured after, and an experiment invalidated mid-flight (a platform file edited while
    the driver ran) was indistinguishable from a valid one. `git rev-parse HEAD` is not
    enough: it says nothing about an uncommitted edit, which is exactly the case that
    produced the invalid run.

    Domain-separated by field so a rename cannot collide with a content change: the same
    property `ckpt.git_state.content_sha` gives a harness, applied to the referee.
    """
    snap = snapshot(root)
    h = hashlib.sha256()
    for name in sorted(snap):
        h.update(name.encode("utf-8"))
        h.update(b"\0")
        h.update(snap[name].encode("ascii"))
        h.update(b"\0")
    return h.hexdigest()


def workspace_is_outside_platform(workspace: Path, root: Path) -> bool:
    """A workspace nested in the platform is reachable from the harness by `..`.

    This is the cheap half of isolation and the half that actually holds: a
    subprocess cannot walk out of a directory tree it was never placed inside.
    """
    try:
        workspace.resolve().relative_to(root.resolve())
    except ValueError:
        return True
    return False
