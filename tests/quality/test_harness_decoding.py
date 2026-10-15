"""A harness must not die on a byte its own tool printed.

Measured 2026-10-15: one model-issued shell command emitted a non-UTF-8 byte, the harness's
`subprocess.run(..., text=True)` decoded it strictly, `UnicodeDecodeError` propagated out of the harness,
and the episode ended as a zero for a task nobody finished. Every runnable harness that runs a shell
command or an agent CLI had the same call, so the same crash was reachable from eight places.

This pins the property directly instead of trusting a grep: for every `subprocess` call in
`base_harness/` that asks for text, the call must also say what to do with undecodable bytes.

Scope, and why it stops here:

* `base_harness/` is what `driver.py --harness <name>` copies into a workspace, so it is the code the
  bug was in.
* `current_harness/` is **derived** - `tools/export_harnesses.py`'s output, a record of harnesses that
  already ran - and is deliberately not edited; a frozen record is not a place to fix a live bug.
* The same pattern exists in `eval/` (the platform decoding a check's or a CLI's output) and in
  `data/*/verify/check.py` (a check decoding its own tool's output). Those are the *referee* side:
  `data/*/verify/check.py` files are scored artefacts whose digests are recorded as custody in
  `registry/`, so changing them is a scorer-identity change and needs its own reviewed pass rather than
  a drive-by edit. `registry/known-red-tests.md` records the inventory.
"""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HARNESSES = ROOT / "base_harness"

#: Sites that ask for text without `errors=`, each with the reason it is left strict.
#: An entry that no longer matches makes the test fail, so this cannot rot into a blanket exemption.
EXCEPTIONS = {
    "dsh_agent/agent.py": (
        "the Node loader probe (`_LOADER_PROBE_JS`): its output is a single platform-authored JSON "
        "line that this function immediately `json.loads`, so a strict decode gives a readable "
        "platform error instead of a silently substituted byte inside JSON. It never carries task "
        "or tool output."
    ),
}


def _subprocess_text_calls(path: Path):
    """(lineno, has_errors) for every subprocess call in `path` that asks for text."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = getattr(func, "attr", None) or getattr(func, "id", None)
        if name not in ("run", "Popen", "check_output", "check_call", "call"):
            continue
        keywords = {kw.arg for kw in node.keywords if kw.arg}
        wants_text = any(
            (kw.arg == "text" and getattr(kw.value, "value", None) is True)
            or kw.arg in ("universal_newlines", "encoding")
            for kw in node.keywords
        )
        if wants_text:
            found.append((node.lineno, "errors" in keywords))
    return found


def test_every_text_subprocess_in_a_harness_says_how_to_decode():
    offenders, checked = [], 0
    for path in sorted(HARNESSES.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        relative = str(path.relative_to(HARNESSES))
        for lineno, has_errors in _subprocess_text_calls(path):
            checked += 1
            if not has_errors and relative not in EXCEPTIONS:
                offenders.append(f"{relative}:{lineno}")
    assert checked >= 8, (
        f"only {checked} text-mode subprocess calls found under base_harness/: the harness set or this "
        f"test's matcher changed, and a guard that matches nothing passes for the wrong reason")
    assert not offenders, (
        "these harness calls request text without `errors=`, so a command that prints one non-UTF-8 "
        "byte raises UnicodeDecodeError inside the harness and ends the episode as a zero:\n  "
        + "\n  ".join(offenders)
        + "\nAdd `errors=\"replace\"` (lossy on the offending byte, but the trace stays valid UTF-8) or "
          "record the site in EXCEPTIONS with the reason it must stay strict.")


def test_the_one_strict_exception_is_still_a_real_site():
    """An exemption for a call that no longer exists is how a guard quietly stops guarding."""
    assert EXCEPTIONS, "the exception list must not be emptied to make this file pass"
    for relative, reason in EXCEPTIONS.items():
        path = HARNESSES / relative
        assert path.is_file(), f"{relative} is exempted but does not exist"
        strict = [lineno for lineno, has_errors in _subprocess_text_calls(path) if not has_errors]
        assert strict, (
            f"{relative} is exempted from the decoding rule but every text-mode subprocess there now "
            f"passes `errors=`; remove the exemption")
        assert len(reason.strip()) >= 30, f"{relative}: the exemption needs a written reason"
