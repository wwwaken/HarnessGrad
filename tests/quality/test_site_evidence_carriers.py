"""Every evidence document the registry cites must have a readable carrier.

`tools/check_dataset_blockers.py` accepts `external-reference` evidence on an absolute
path and deliberately does not check that the path exists, so a registry can cite review
documents that no longer exist anywhere. That is exactly what happened twice: 32 of 36
cited `/site/...` paths had no readable carrier after `reports/` and `docs/` were
deleted, and the registry's own `observed` prose pointed at `reports/w-jc2-review.md` and
`reports/w-journalcov-review.md`, which no longer existed either.

`tests/fixtures/hg_migration_site/PROVENANCE.json` records, per document, the exact
`reference` string as it appears in the registry, the `carrier` path that holds the
bytes, where it was recovered from (`source_path`), the `source_commit`, and the byte
count and SHA-256 of the recovered bytes. These tests check that recorded provenance and
the resolver convention at `tests/quality/conftest.py:24`; they do not re-authenticate
the underlying observation, and a present carrier is not a claim that the citation is
correct.
"""
import hashlib
import json
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "registry" / "dataset-blockers.json"
WITHDRAWALS = ROOT / "registry" / "withdrawn-requirements.md"
PACKET = ROOT / "tests" / "fixtures" / "hg_migration_site"
PROVENANCE = PACKET / "PROVENANCE.json"

# `/site/...` is a placeholder absolute root resolved by the conftest fixture; the other
# two forms are ordinary repo-relative citations written into `observed`/`next_action`.
SITE_REFERENCE = re.compile(r"/site/[A-Za-z0-9._/@+-]+")
REPO_REFERENCE = re.compile(r"(?<![\w/])((?:reports|docs)/[A-Za-z0-9._/@+-]+)")


def _provenance():
    return json.loads(PROVENANCE.read_text(encoding="utf-8"))


def _known(path, by_reference):
    """True when `path` is an in-repo file or a recorded carrier reference."""
    if (ROOT / path).is_file():
        return True
    item = by_reference.get(path)
    return bool(item) and (ROOT / item["carrier"]).is_file()


def _cited_references():
    """Cited document paths, with sentence punctuation trimmed off the end.

    Prose writes `... see reports/w-jc2-review.md.` and `... docs/w-shared-verifier-review.md.`
    so a naive match keeps the full stop. A trailing `.,;:)` is dropped only while the
    shorter form is a known document, which keeps real extensions like `.md`/`.json` intact.
    """
    text = REGISTRY.read_text(encoding="utf-8") + WITHDRAWALS.read_text(encoding="utf-8")
    by_reference = {item["reference"]: item for item in _provenance()}
    references = set(SITE_REFERENCE.findall(text))
    for raw in REPO_REFERENCE.findall(text):
        path = raw
        while path and path[-1] in ".,;:)" and _known(path[:-1], by_reference):
            path = path[:-1]
        references.add(path)
    return sorted(references)


def test_every_cited_document_resolves_to_a_carrier():
    references = _cited_references()
    assert references, "no evidence reference found: the citation scheme changed"
    by_reference = {item["reference"]: item for item in _provenance()}
    unresolved = [r for r in references if not _known(r, by_reference)]
    assert unresolved == [], f"cited documents with no readable carrier: {unresolved}"


def test_provenance_covers_every_carrier_and_records_its_recovery():
    provenance = _provenance()
    by_reference = {item["reference"]: item for item in provenance}
    assert len(by_reference) == len(provenance), "duplicate reference in PROVENANCE.json"
    # Every citation whose path is not present in the repo must be recorded, and the
    # packet's files must be described exactly (no undocumented carrier, no stale entry).
    missing = [r for r in _cited_references() if not (ROOT / r).is_file()]
    assert set(missing) <= set(by_reference), "a cited document has no provenance entry"
    packet_carriers = {str(p.relative_to(ROOT)) for p in PACKET.rglob("*")
                       if p.is_file() and p.name != "PROVENANCE.json"}
    recorded_packet = {item["carrier"] for item in provenance
                       if item["carrier"].startswith("tests/fixtures/hg_migration_site/")}
    assert recorded_packet == packet_carriers, "packet files and PROVENANCE.json disagree"
    for item in provenance:
        assert item["source_commit"], item["reference"]
        assert item["source_path"].startswith(("reports/", "docs/")), item["reference"]


def test_each_carrier_is_byte_identical_to_its_recorded_recovery():
    for item in _provenance():
        data = (ROOT / item["carrier"]).read_bytes()
        assert len(data) == item["bytes"], item["reference"]
        assert hashlib.sha256(data).hexdigest() == item["sha256"], item["reference"]


def test_packet_stays_small_text():
    """The packet is evidence, not a payload store: keep it under 4 MB and text-only."""
    total = 0
    for path in PACKET.rglob("*"):
        if not path.is_file():
            continue
        data = path.read_bytes()
        total += len(data)
        assert len(data) < 1_048_576, f"{path} exceeds the 1 MB committed-file limit"
        data.decode("utf-8")
    assert total < 4_000_000, f"carrier packet grew to {total} bytes"


def test_every_carrier_is_tracked_in_git():
    """A carrier that exists on disk but was never committed is not a carrier.

    `.gitignore:289` narrowed `/docs/*` to a name whitelist and silently dropped three of the
    restored documents from `git add -A`. The byte-identity test above reads the working tree,
    so it still passed in the worktree while `main` shipped provenance entries pointing at
    files that were not in the commit. Ask git directly instead.
    """
    for item in _provenance():
        result = subprocess.run(["git", "ls-files", "--error-unmatch", "--", item["carrier"]],
                                cwd=ROOT, capture_output=True, text=True)
        assert result.returncode == 0, f"{item['carrier']} is not tracked in git"
        result = subprocess.run(["git", "check-ignore", "-q", "--", item["carrier"]],
                                cwd=ROOT, capture_output=True, text=True)
        assert result.returncode != 0, f"{item['carrier']} is gitignored"
