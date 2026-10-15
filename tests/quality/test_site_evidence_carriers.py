"""Every `/site/...` external reference must have a readable carrier in the fixture.

`tools/check_dataset_blockers.py` accepts `external-reference` evidence on an absolute
path and deliberately does not check that the path exists, so a registry can cite
review documents that no longer exist anywhere. That is exactly what happened: 32 of
36 cited `/site/...` paths had no readable carrier after `reports/` and `docs/` were
deleted, and only `tests/fixtures/hg_migration_site/` (which had itself been reaped)
could resolve them. This pins the invariant that the carriers are present and that
each one is byte-identical to the commit it was recovered from.

The fixture's `PROVENANCE.json` records, per carrier, the `/site/...` reference, the
exact source path, the source commit and the SHA-256 of the recovered bytes. These
tests read only that recorded provenance plus the resolver convention at
`tests/quality/conftest.py:24`; they do not re-derive or re-authenticate the citation.
"""
import hashlib
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "registry" / "dataset-blockers.json"
WITHDRAWALS = ROOT / "registry" / "withdrawn-requirements.md"
CARRIERS = ROOT / "tests" / "fixtures" / "hg_migration_site"
PROVENANCE = CARRIERS / "PROVENANCE.json"

REFERENCE = re.compile(r"/site/[A-Za-z0-9._/@+-]+")


def _references():
    text = REGISTRY.read_text(encoding="utf-8") + WITHDRAWALS.read_text(encoding="utf-8")
    return sorted(set(REFERENCE.findall(text)))


def test_every_cited_site_reference_resolves_to_a_carrier():
    references = _references()
    assert references, "no /site/ reference found: the citation scheme changed"
    absent = [r for r in references
              if not (CARRIERS / r[len("/site/"):]).is_file()]
    assert absent == [], f"cited /site/ references without a carrier: {absent}"


def test_provenance_covers_every_reference_and_every_carrier():
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    recorded = {item["reference"] for item in provenance}
    # PROVENANCE.json records the whole restored packet, which is a superset of what the
    # registry and the withdrawal record cite today: the packet also carries the sources
    # that the focused tests, the disposition plan and the journal cite.
    assert set(_references()) <= recorded, "a cited /site/ reference has no provenance entry"
    on_disk = {"/site/" + str(p.relative_to(CARRIERS)) for p in CARRIERS.rglob("*")
               if p.is_file() and p.name != "PROVENANCE.json"}
    assert recorded == on_disk, "carrier files and PROVENANCE.json entries disagree"


def test_each_carrier_is_byte_identical_to_its_recorded_recovery():
    for item in json.loads(PROVENANCE.read_text(encoding="utf-8")):
        path = CARRIERS / item["reference"][len("/site/"):]
        data = path.read_bytes()
        assert len(data) == item["bytes"], item["reference"]
        assert hashlib.sha256(data).hexdigest() == item["sha256"], item["reference"]
        assert item["source_commit"], item["reference"]
        assert item["source_path"].startswith(("reports/", "docs/")), item["reference"]


def test_carrier_packet_stays_small_text():
    """The fixture is evidence, not a payload store: keep it under 4 MB and text-only."""
    total = 0
    for path in CARRIERS.rglob("*"):
        if not path.is_file():
            continue
        data = path.read_bytes()
        total += len(data)
        assert len(data) < 1_048_576, f"{path} exceeds the 1 MB committed-file limit"
        data.decode("utf-8")
    assert total < 4_000_000, f"carrier packet grew to {total} bytes"
