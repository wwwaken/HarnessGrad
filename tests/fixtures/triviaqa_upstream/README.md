# TriviaQA upstream-fixture acquisition contract

Status: **unacquired / provenance blocked**. This directory contains no upstream
scorer, scorer commit pin, source digest, or acquisition receipt. No network
acquisition was attempted. The former test reference was a second local
transcription, which cannot establish upstream identity. Claims of “verbatim” in
`data/triviaqa.py` remain unverified; this docs/tests change does not repair or
certify the production scorer.

The dataset pin `mandarjoshi/trivia_qa` on HuggingFace at
`0f7faf33a3908546c6fd5b73a660e0f8ff173c2f` pins the parquet export, **not** the
GitHub evaluator. An adapter hash or a hash of the former test transcription is
also not an upstream source pin.

## Material required to close the source gate

An acquisition owner must supply independently obtained material from
`https://github.com/mandarjoshi/TriviaQA`, with an immutable full Git commit ID.
For an offline acquisition, use an already supplied checkout or archive; the tests
never fetch missing files. Keep the following under this directory:

1. `evaluation/triviaqa_evaluation.py`: the entire original file at that commit,
   with its original bytes, encoding, line endings, comments and imports. Do not
   copy functions out of the adapter, reconstruct code from memory, or apply
   formatting, Python-version conversion or normalization fixes to the fixture.
2. The original license/notice file(s) from the same source revision, preserving
   upstream relative paths. Record the actual license path; its name and licensing
   terms have not been verified here. If redistribution cannot be established,
   stop rather than adding an invented license or a substituted implementation.
3. `provenance.json`, using the schema below. Compute SHA-256 from every original
   file's raw bytes and its Git blob SHA-1 from `blob <byte-length>\0<bytes>`.
   Review the commit-to-file linkage against the supplied checkout's commit tree,
   or an independently verified commit-specific archive. Record that evidence
   and the reviewer, rather than treating a matching self-declared hash as proof
   of origin. Preserve the acquisition material's identity in `origin`.
4. If later full-evaluator work needs helper modules, acquire their exact bytes,
   license coverage and pins at the same revision too. Record every helper in
   `files`; do not fill dependency gaps with stubs or unrelated packages. This
   component gate supplies only standard-library `re` and `string` and does not
   import the full script.

Receipt schema (deliberately invalid until populated from acquired material;
**do not install this example as a completed receipt**):

```json
{
  "schema_version": 1,
  "repository": "https://github.com/mandarjoshi/TriviaQA",
  "commit": null,
  "source_path": "evaluation/triviaqa_evaluation.py",
  "license_path": null,
  "acquisition": {
    "method": "local_git_checkout",
    "origin": null,
    "acquired_at_utc": null,
    "reviewed_by": null,
    "commit_link_evidence": null
  },
  "files": {
    "evaluation/triviaqa_evaluation.py": {
      "sha256": null,
      "git_blob_sha1": null
    }
  }
}
```

`method` is `local_git_checkout` or `upstream_archive`. `commit` is a lowercase
40-hex GitHub commit ID, separate from the Hub dataset revision. Acquisition
fields are nonempty strings; record time in UTC. Each `files` entry contains a
64-hex SHA-256 and a 40-hex Git blob SHA-1. Add the acquired license path to
`files` and set `license_path` to it. Paths must be canonical, relative, and stay
within this directory. Missing files, pins, attestation or license fail the gate;
any source/license/helper digest mismatch fails before evaluator code executes.
Mechanical validation cannot authenticate an acquisition attestation. A reviewer
must establish the claimed origin and commit linkage before accepting the fixture.

## What the tests establish

`tests/quality/test_triviaqa_official_scorer.py` has one mandatory gate,
`test_em_components_match_pinned_upstream_fixture`. It validates the receipt and
all file hashes, then extracts the four EM-related function definitions from the
original source AST without rewriting their bodies. It compares normalization,
capitalized JSON keys, the Hub lowercase-key translation, alias reduction and
scalar rewards on fabricated inputs. Underscores, punctuation, articles, Unicode
and empty predictions are included to expose possible transcription drift.
Missing functions, incompatible syntax or unresolved dependencies fail; they do
not trigger a local reference fallback. Agreement is a finite component check,
not byte identity of the adapter or an end-to-end official evaluation.

All other tests are explicitly local regressions or acquisition-contract tests.
Integrity-test files are inert text marked `SYNTHETIC`, and contain no invented
upstream function bodies. Their simulated receipt tests hash enforcement only.
The adapter's import-time pool construction is suppressed before import, released
payload reads are forbidden, and socket connection attempts fail. No train,
validation, test, heldout, model, GPU endpoint or H0 run is accessed.

Run the full gate from the repository root, keeping temporary output here:

```sh
mkdir -p .scratch/triviaqa-provenance
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q tests/quality/test_triviaqa_official_scorer.py --basetemp=.scratch/triviaqa-provenance/pytest
```

Until acquisition, this command must exit nonzero with the missing-fixture
failure. To check contract enforcement and current local behavior separately:

```sh
mkdir -p .scratch/triviaqa-provenance
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q tests/quality/test_triviaqa_official_scorer.py -k 'not test_em_components_match_pinned_upstream_fixture' --basetemp=.scratch/triviaqa-provenance/pytest-local
```

The second command excludes the provenance gate and cannot certify upstream
equivalence or authorize production H0. A passing acquired-fixture gate still
requires separate review of the following comparison boundaries.

## Evaluation scope and comparison boundaries

- **`rc.nocontext`**: the adapter reads question/answer columns from this Hub
  configuration and supplies no retrieved documents. It is not the full `rc`
  reading-comprehension setting. Tool use by a harness is a separate variable;
  the absence of supplied context alone does not prove a model-only experiment.
- **`validation`**: the adapter declares validation as its scored split and an
  even-stride 2,000-row train sample as its study side. The repository reports
  17,944 validation rows and blinded test gold at the dataset revision; these are
  inherited dataset claims, not measurements made by these synthetic tests. A
  validation number is not a test leaderboard number. No test/heldout payload is
  opened to confirm the claim; fabricated empty aliases test rejection instead.
- **EM only**: current reward is a 0/1 exact match maximized over accepted aliases,
  with no token F1. Comparing just the canonical `value` is a different rule.
  The adapter reads both key spellings, coerces values to strings, permits an
  empty reduction to return zero, and caps accepted aliases at 200; `_gold`
  rejects empty aliases. These adaptations are not established as verbatim
  upstream behavior. The file's `official` result key is a legacy label, not
  provenance evidence. Do not add F1 or claim a complete official score without
  independently pinned source, dependencies and differential evidence.
- **Grouping and denominator**: task identity is a split/file-row position
  (`triviaqa/validation/<index>`), not a `QuestionId`/document key. The adapter's
  `COLUMNS` omit question/document IDs and its gold drops grouping metadata. EM
  components alone cannot prove equivalence to an upstream file evaluator's ID
  construction, question/document grouping, duplicate handling, domain or
  verified-subset selection, missing-prediction policy, denominator, or scale.
  Those upstream rules remain **unverified pending source acquisition**. For an
  illustrative policy difference, two correct rows for question A and one wrong
  row for question B give a row mean of 2/3, but a unique-question mean of 1/2.
  That example is not an assertion about the missing upstream algorithm.

Any future comparison must identify the dataset config/revision/split, selected
row and trial coverage, grouping unit, denominator/scale, EM metric, source and
adapter hashes, and invalid/unmeasured counts. Source acquisition and synthetic
agreement are preflight evidence only; this change creates no benchmark score
and grants no model/H0 authorization.
