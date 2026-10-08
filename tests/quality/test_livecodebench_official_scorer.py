"""LiveCodeBench: the refusal, and the two measurements that make it precise.

The first version of this file was decoration: it re-typed `estimate_pass_at_k` inside the
test and asserted it against literals, so it proved that the *test* could compute pass@k --
not that the adapter could, and not that either matched upstream. It also read an absolute
path with no skip. This file does the two things the refusal actually rests on:

* **the transcription is upstream's bytes**, compared against `pass_k_utils.py` inside the
  pinned source archive rather than against a copy of itself, and exercised by calling the
  upstream function loaded from that archive;
* **the tests are available**, which is the fact that separates "the release ships no
  solution" from "the metric cannot be computed". The private cases decode offline with
  stdlib `base64` + `zlib` + `pickle`, through a decode step that is a function in the
  adapter, exercised here on a real row.

Together they are the argument `REFUSED` makes: gate 1 has no oracle here, and it is *not*
because the check is unreachable.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tarfile
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import data.livecodebench as dataset  # noqa: E402

ADAPTER = ROOT / "data" / "livecodebench.py"
ARCHIVE = dataset.DATASET_ROOT / "_src" / "upstream.tar.gz"
SHARD = dataset.DATASET_ROOT / "_src" / "test6.jsonl"
MEMBER = (f"LiveCodeBench-{dataset.UPSTREAM_COMMIT}"
          "/lcb_runner/evaluation/pass_k_utils.py")

#: The released row schema, pinned: a solution would have to appear as a key here, and the
#: refusal is the claim that none does.
ROW_FIELDS = {"question_id", "question_title", "question_content", "platform", "contest_id",
              "contest_date", "difficulty", "starter_code", "public_test_cases",
              "private_test_cases", "metadata"}


def _upstream_source() -> str:
    if not ARCHIVE.is_file():
        pytest.skip("livecodebench: fetch the declared official source archive")
    with tarfile.open(ARCHIVE) as tar:
        return tar.extractfile(MEMBER).read().decode()


@pytest.fixture(scope="module")
def upstream():
    """Upstream's module, loaded from the pinned archive -- the second implementation the
    differential tests compare against, so a transcription bug cannot pass by agreeing with
    itself."""
    source = _upstream_source()
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as handle:
        handle.write(source)
        path = handle.name
    spec = importlib.util.spec_from_file_location("lcb_upstream_pass_k_utils", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def first_row() -> dict:
    if not SHARD.is_file():
        pytest.skip("livecodebench: fetch the declared shards")
    with SHARD.open(encoding="utf-8") as handle:
        return json.loads(handle.readline())


def test_the_pinned_archive_is_the_declared_one():
    assert hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() == dataset.SOURCE_SHA256


def test_the_transcription_is_upstreams_bytes():
    """Counted as a substring of the adapter, so an edit cannot hide -- including the one
    this file's first version made, moving `import numpy` inside the two functions, which
    no value-level comparison would have noticed."""
    upstream_source = _upstream_source()
    region = upstream_source[upstream_source.index("def estimate_pass_at_k("):
                             upstream_source.index("def extract_instance_results(")]
    assert ADAPTER.read_text().count(region) == 1


@pytest.mark.parametrize("n,c,k", [(1, 1, 1), (2, 1, 1), (5, 0, 1), (5, 5, 1), (10, 3, 5),
                                   (100, 1, 10), (1, 0, 1)])
def test_pass_at_k_differential(n, c, k, upstream):
    assert dataset.estimate_pass_at_k(n, [c], k)[0] == pytest.approx(
        upstream.estimate_pass_at_k(n, [c], k)[0])


def test_the_aggregate_is_upstreams(upstream):
    """`compute_metrics_from_results` over a hand-built result table, both sides -- including
    the `detail` map, which is where a re-implementation would silently differ, and the
    `(total >= k).all()` filter, which drops a k that no task has enough samples for. The
    first version of this test asked for `pass@5` on three generations and got a KeyError
    from the *adapter* -- which is upstream's behaviour, and the differential is what made
    that legible instead of looking like a bug."""
    results = {"a": [[1, 1], [0, 0], [1, 0]], "b": [[1, 1], [1, 1], [1, 0]]}
    ours = dataset.compute_metrics_from_results(results, k_list=[1, 3])
    theirs = upstream.compute_metrics_from_results(results, k_list=[1, 3])
    assert set(ours) == set(theirs) == {"pass@1", "pass@3", "detail"}
    assert ours["pass@1"] == pytest.approx(theirs["pass@1"])
    assert ours["pass@3"] == pytest.approx(theirs["pass@3"])
    assert ours["detail"] == theirs["detail"]
    # The default k_list is upstream's, and so is the filter that empties it:
    for side in (dataset.compute_metrics_from_results(results),
                 upstream.compute_metrics_from_results(results)):
        assert set(side) == {"pass@1", "detail"}


def test_the_private_tests_decode_offline_with_the_released_step(first_row):
    """The decisive fact: `private_test_cases` is base64+zlib+pickle and stdlib decodes it.

    A refusal that says "no oracle" is credible; one that says "unreproducible" would not
    be, and this test is what keeps the two apart.
    """
    raw = first_row["private_test_cases"]
    with pytest.raises(ValueError):
        json.loads(raw)          # the branch upstream wraps in `except`
    cases = dataset.decode_private_test_cases(raw)
    assert cases
    assert all({"input", "output", "testtype"} <= set(case) for case in cases)
    public = dataset.decode_private_test_cases(first_row["public_test_cases"])
    assert public and all({"input", "output"} <= set(case) for case in public)


def test_the_released_rows_carry_no_reference_solution(first_row):
    """Why the refusal is about the *oracle* and not about the metric."""
    assert set(first_row) == ROW_FIELDS
    assert not any("solution" in field or "reference" in field for field in ROW_FIELDS)
