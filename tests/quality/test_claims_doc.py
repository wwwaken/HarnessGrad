"""`docs/claims.md`: the research register has to stay falsifiable and stay separate.

The register exists because two kinds of statement were being mixed, and the mixture is what
makes a paper unreadable: a claim about **how harnesses learn** and a claim about **how a
dataset is plumbed** both look like "a thing we found out". The scope rule is written at the
top of the file; this test is what keeps it from eroding, because prose rules erode.

Two invariants, and the second is the one that matters:

* **structure** -- every `R<n>` carries an attribution, a claim, why it would matter, a
  confirmation condition, a **refutation** condition, its confounds, an experiment, and a
  status from a closed vocabulary. A claim without a refutation condition is not a claim;
  it is a hope. `R1`–`R12` without the `Refuted if` line would still read well, which is
  exactly why the checker has to be the one that objects.
* **separation** -- the scope rule and the "what is deliberately not here" section are
  present, so a future edit cannot quietly move the JRE-unpacking fix back in beside them.

`_parse` is exercised against a synthetic register in the second half, so a checker that
silently stopped checking would fail here rather than pass quietly.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

CLAIMS = ROOT / "docs" / "claims.md"

#: `docs/claims.md` is **internal to the group**: it carries the claims, their prior-art
#: verdicts and the paper split, so it lives in `.gitignore` and is never pushed. A clone
#: therefore has no copy, and this module skips rather than fails -- what it guards is for
#: us, not for someone using the platform. Locally the file is always present, so the skip
#: is invisible to the group's own suite.
if not CLAIMS.is_file():
    pytest.skip("docs/claims.md is internal (see .gitignore) and absent from this clone",
                allow_module_level=True)

#: Everything a claim must say. The list is the contract; adding a field to one claim and
#: not the others is the failure mode this catches.
FIELDS = ("Raised by", "Claim", "Why it would matter", "Confirmed if", "Refuted if",
          "Confounds", "Experiment", "Prior art", "Status")

#: A closed vocabulary, so "partially tested, probably fine" cannot be written.
STATUSES = ("untested", "upstream-only", "measured")

#: The prior-art verdict, checked the same way. Twelve papers were read; a claim either has
#: been measured by someone else (`pre-empted`), is contradicted by other measurements
#: (`contested`), has a piece of it measured (`partial`), or has nothing (`open`).
#: "related work probably exists" is not one of the four.
PRIOR_STATES = ("pre-empted", "contested", "partial", "open")


def _parse(text: str) -> dict[str, dict]:
    """`{claim id: {"title":…, "fields": {label: body}, "raw":…}}` for every `## R<n> — …`."""
    out: dict[str, dict] = {}
    heads = list(re.finditer(r"^## (R\d+) — (.*)$", text, re.M))
    for index, head in enumerate(heads):
        end = heads[index + 1].start() if index + 1 < len(heads) else len(text)
        body = text[head.end():end]
        fields = {}
        for label in FIELDS:
            found = re.search(rf"^\*\*{re.escape(label)}\.?\*\*((?:.|\n)*?)(?=\n\*\*|\n## |\Z)",
                              body, re.M)
            fields[label] = found.group(1).strip() if found else ""
        out[head.group(1)] = {"title": head.group(2).strip(), "fields": fields,
                             "raw": body}
    return out


def _problems(claims: dict[str, dict]) -> list[str]:
    """Every structural defect, as text. Used on the real file and on the probe below."""
    bad = []
    for cid, claim in claims.items():
        for label in FIELDS:
            if not claim["fields"][label]:
                bad.append(f"{cid}: missing **{label}.**")
        status = claim["fields"]["Status"].split(",")[0].split("—")[0].strip().rstrip(".")
        if status and status not in STATUSES:
            bad.append(f"{cid}: status {status!r} is outside {STATUSES}")
        # The verdict is the first bold word of the field, so the state is machine-readable
        # rather than buried in prose that a reader has to interpret.
        raw = (claim["fields"]["Prior art"].strip().removeprefix("**")
               .split("**")[0].strip())
        # The state is the **first word**: the rest of the line is the verdict's detail
        # ("pre-empted in its weak form", "open, and against current practice").
        state = raw.split(",")[0].split()[0] if raw else ""
        if state not in PRIOR_STATES:
            bad.append(f"{cid}: prior-art state {state!r} is outside {PRIOR_STATES}")
    return bad


def test_the_register_parses_at_all():
    claims = _parse(CLAIMS.read_text())
    assert len(claims) >= 12, sorted(claims)
    assert list(claims) == [f"R{n}" for n in range(1, len(claims) + 1)], list(claims)


def test_every_claim_is_structurally_complete_and_falsifiable():
    claims = _parse(CLAIMS.read_text())
    assert not _problems(claims), "\n".join(_problems(claims))


def test_the_refutation_condition_is_not_a_restatement_of_the_confirmation():
    """A `Refuted if` that repeats `Confirmed if` would pass the field check and say nothing."""
    for cid, claim in _parse(CLAIMS.read_text()).items():
        confirmed = claim["fields"]["Confirmed if"]
        refuted = claim["fields"]["Refuted if"]
        assert refuted != confirmed, cid
        assert len(refuted) > 40, f"{cid}: the refutation condition is a stub"


def test_the_user_s_claims_keep_their_original_wording():
    """Attribution is a field, so it is checkable: their seven, quoted, not paraphrased."""
    text = CLAIMS.read_text()
    for cid in ("R1", "R2", "R3", "R4", "R5", "R6", "R7"):
        block = _parse(text)[cid]["raw"]
        assert "user, verbatim" in block, cid
        assert re.search(r"[\u4e00-\u9fff]", block), f"{cid}: the quoted wording is missing"


def test_the_scope_rule_and_the_exclusion_section_are_both_present():
    text = CLAIMS.read_text()
    assert "A claim belongs here only if it is about the learning process" in text
    assert "What is deliberately not here" in text
    # The exclusion section must actually name where the engineering conclusions live, or a
    # reader cannot follow them and will re-add them here.
    tail = text.split("## What is deliberately not here", 1)[1]
    assert "docs/dataset-onboarding-skill.md" in tail


def test_the_prior_art_section_names_its_sources_and_says_what_is_left():
    """A prior-art pass that does not name papers, or does not say what survives it, is a mood."""
    text = CLAIMS.read_text()
    assert "## Prior art" in text
    assert text.count("arxiv.org/abs/26") >= 8, "the check read twelve papers; name them"
    assert "**still ours**" in text, "the instrument table must state what remains ours"


def test_a_claim_whose_prior_art_is_open_says_so_explicitly():
    """`open` is the state that licenses spending compute; it must not be the silent default."""
    claims = _parse(CLAIMS.read_text())
    open_claims = [cid for cid, c in claims.items()
                   if "open" in c["fields"]["Prior art"].split("—")[0]]
    assert len(open_claims) >= 5, open_claims
    for cid in open_claims:
        assert claims[cid]["fields"]["Experiment"], cid


def test_the_measurement_prerequisites_are_not_dressed_up_as_claims():
    """`P1`/`P2` are instruments; `M1`–`M5` are settled results. Neither is an `R<n>`."""
    text = CLAIMS.read_text()
    assert "## Open measurement prerequisites" in text
    assert "## Already settled" in text
    for instrument in ("| P1 |", "| P2 |"):
        assert instrument in text, instrument
    for settled in ("| M1 |", "| M2 |", "| M3 |", "| M4 |", "| M5 |"):
        assert settled in text, settled


# --------------------------------------------------------------- teeth ---

PROBE = """## R1 — a claim with no refutation condition

**Raised by.** someone.

**Claim.** Something is true.

**Why it would matter.** It would.

**Confirmed if.** It looks true.

**Confounds.** None worth naming.

**Experiment.** Look at it.

**Prior art.** **open** — nothing found.

**Status.** untested.
"""


def test_the_checker_rejects_a_claim_with_no_refutation_condition():
    """The probe is the proof the checker works: without this it could pass for years."""
    problems = _problems(_parse(PROBE))
    assert any("Refuted if" in problem for problem in problems), problems


def test_the_checker_rejects_a_status_outside_the_vocabulary():
    probe = PROBE.replace("**Status.** untested.", "**Status.** partially tested, probably fine.")
    assert any("outside" in problem for problem in _problems(_parse(probe)))


def test_the_checker_accepts_a_well_formed_claim():
    """The other half of the teeth: the probe above must fail for the *field*, not for noise."""
    probe = PROBE.replace(
        "**Confirmed if.** It looks true.",
        "**Confirmed if.** It looks true.\n\n**Refuted if.** It looks false.")
    probe = probe.replace("**Confounds.** None worth naming.",
                          "**Confounds.** The instrument could be the thing moving.")
    assert _problems(_parse(probe)) == []


if __name__ == "__main__":                                  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
