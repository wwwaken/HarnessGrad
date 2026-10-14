"""The onboarding pages must not drift away from the code they describe.

`docs/dataset-onboarding.md` is the procedure a new author follows, and
`docs/dataset-first-day.md` is the reconnaissance that comes before it. Both are prose, so
nothing stops them from describing a tool that was renamed, a flag that was removed, or a
contract kind that no longer exists -- and a page that is *nearly* right is worse than none,
because it is followed.

These tests read the pages and check the parts a program can decide:

* every download kind, environment kind and verifier kind in `data/dataset.schema.json` is
  named on the procedure page, spelled the way the schema spells it;
* every `python3 <path>` command on **either** page points at a file that exists, and every
  `--flag` in it appears in the source of the file it is passed to;
* the first-day page still carries the routing rule it exists for: measure before writing,
  three outcomes, and the two refusal kinds.

What they deliberately do not check is the judgement: whether a lesson is true, or whether
a gate is the right gate. That is `docs/dataset-onboarding-skill.md`'s job, and
`tests/quality/test_dataset_controls.py` enforces the shape over every published dataset.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import dataset_lint  # noqa: E402

PAGE = ROOT / "docs" / "dataset-onboarding.md"
FIRST_DAY = ROOT / "docs" / "dataset-first-day.md"

#: Commands on the pages that are illustrative rather than runnable, because they carry a
#: placeholder for the dataset name. Their flags are checked against a real control script
#: instead -- see `test_the_generic_control_commands_use_real_flags`.
_PLACEHOLDER = re.compile(r"[<>\u2026]")

#: `python3 -m <module>` and `python3 -c "<code>"` are interpreter invocations, not paths.
_INTERPRETER_FLAGS = ("-m", "-c")


def _read(path: Path) -> str:
    assert path.is_file(), f"{path} is missing; it is part of the deliverable"
    return path.read_text(encoding="utf-8")


def _page() -> str:
    return _read(PAGE)


def _first_day() -> str:
    return _read(FIRST_DAY)


def _pages() -> list[tuple[str, str]]:
    return [("dataset-onboarding.md", _page()), ("dataset-first-day.md", _first_day())]


def _fenced_lines(text: str) -> list[str]:
    """Every line inside a ``` block."""
    out, inside = [], False
    for line in text.splitlines():
        if line.startswith("```"):
            inside = not inside
            continue
        if inside:
            out.append(line)
    return out


def _commands(text: str) -> list[list[str]]:
    """`python3 <path> …` invocations from the fenced blocks, tokenised."""
    out = []
    for line in _fenced_lines(text):
        line = line.split("#", 1)[0].strip()
        if not line.startswith("python3 "):
            continue
        out.append(line.split())
    return out


def test_the_page_names_every_kind_the_schema_declares():
    """A kind the schema has and the page omits is a shape a reader will not know about."""
    schema = dataset_lint.load_schema()
    text = _page()
    kinds = {
        "download": schema["download"]["kinds"],
        "env": schema["env"]["kinds"],
        "verify": schema["verify"]["kinds"],
    }
    missing = {
        group: [k for k in names if f"`{k}`" not in text]
        for group, names in kinds.items()
    }
    assert not any(missing.values()), f"the page does not name: {missing}"


def test_the_page_spells_every_kind_the_way_the_schema_does():
    """The reverse direction: a near-miss spelling sends a reader looking for machinery.

    This is checked as *near-miss spellings of real kinds* rather than as "every backticked
    word must be a kind" -- the latter is unsound, because the page legitimately backticks
    schema *field* names such as `file` (a required field of an `hf-file` entry) and
    `dst`/`repo`/`url`. An earlier version of this test flagged `file` as an invented kind;
    the test was wrong, not the page.
    """
    schema = dataset_lint.load_schema()
    kinds = (list(schema["download"]["kinds"]) + list(schema["env"]["kinds"])
             + list(schema["verify"]["kinds"]))
    text = _page()
    near_misses = []
    for kind in kinds:
        if "-" in kind:
            near_misses += [f"`{kind.replace('-', '_')}`", f"`{kind.replace('-', ' ')}`"]
        if kind == "files":
            near_misses += ["`file` environment", "`file` env"]
    present = [spelling for spelling in near_misses if spelling in text]
    assert not present, f"the page misspells kinds: {present}"


def test_every_command_on_the_pages_points_at_a_file_that_exists():
    missing = []
    for name, text in _pages():
        for argv in _commands(text):
            if argv[1] in _INTERPRETER_FLAGS or _PLACEHOLDER.search(argv[1]):
                continue
            if not (ROOT / argv[1]).exists():
                missing.append(f"{name}: {argv[1]}")
    assert not missing, f"a page tells a reader to run files that do not exist: {missing}"


def test_every_flag_on_the_pages_is_a_flag_of_the_file_it_is_passed_to():
    wrong = []
    for name, text in _pages():
        for argv in _commands(text):
            target = argv[1]
            if _PLACEHOLDER.search(target) or target in _INTERPRETER_FLAGS:
                continue
            path = ROOT / target
            if not path.is_file() or path.suffix != ".py":
                continue
            source = path.read_text(encoding="utf-8")
            for flag in (a for a in argv[2:] if a.startswith("--")):
                if f'"{flag}"' not in source:
                    wrong.append(f"{name}: {target} {flag}")
    assert not wrong, f"a page uses flags the tools do not define: {wrong}"


def test_the_generic_control_commands_use_real_flags():
    """The page's `data/datasets/<name>/control.py --oracle …` lines carry a placeholder, so the
    flags are checked against the two control entry points that exist."""
    text = _page()
    for script in ("data/scaffolds/qa/control.py", "data/datasets/jericho/control.py"):
        source = (ROOT / script).read_text(encoding="utf-8")
        for flag in ("--oracle", "--noop", "--platform"):
            assert f'"{flag}"' in source, f"{script} does not define {flag}"
            assert flag in text, f"the page does not document {flag}"


def test_the_page_states_the_five_gates():
    """The bar is five named gates; a page that drops one is a page that hides a gate."""
    text = _page().lower()
    for phrase in ("oracle", "do-nothing", "verbatim", 'kind = "dataset"',
                   "task_difficulty"):
        assert phrase.lower() in text, f"the page no longer mentions {phrase!r}"


def test_the_page_defers_to_the_programs():
    """The precedence rule is the whole reason the page can be short."""
    text = _page()
    assert "the program is right" in text
    assert "dataset.schema.json" in text and "dataset_lint.py" in text


# --------------------------------------------------- the first-day page ---


def test_the_first_day_page_keeps_the_measure_before_writing_rule():
    """The whole reason the page exists: no adapter until the gold has been scored."""
    text = _first_day().lower()
    assert "do not write `data/datasets/<name>.py` until" in text
    assert "run the gold through the official scorer" in text
    # It must say why, with the two datasets that went opposite ways.
    assert "nestful" in text and "ds1000" in text


def test_the_first_day_page_states_all_three_outcomes_and_the_two_refusal_kinds():
    text = _first_day()
    for outcome in ("**runnable**", "**runnable, with a measured exclusion**", "**refused**"):
        assert outcome in text, f"the first-day page no longer names {outcome}"
    for kind in ("`contract_gap`", "`unreproducible`"):
        assert kind in text, f"the first-day page no longer names the refusal kind {kind}"


def test_the_first_day_page_carries_the_measured_environment_fact():
    """The sandbox measurement is the one that decides heavy-dependency designs."""
    text = _first_day()
    assert "work root" in text and "VERIFY.inputs" in text
    assert "eval/containers/sandbox.py" in text, "the measurement must name the mechanism it measured"


def test_the_two_pages_point_at_each_other():
    """A procedure nobody can find, and a reconnaissance nobody reads, are both wasted."""
    assert "dataset-first-day.md" in _page()
    assert "dataset-onboarding.md" in _first_day()
