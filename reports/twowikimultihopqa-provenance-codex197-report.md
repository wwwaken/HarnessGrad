# Task 197: 2WikiMultihopQA evaluator provenance

**Authoritative code acquired; source gate closed for the pinned fixture.**
Production scorer wiring, model/H0 execution and benchmark-data access are
unchanged. Fresh-environment offline dependency closure remains open.

## Source, revision and license

The original repository is
[Alab-NII/2wikimultihop](https://github.com/Alab-NII/2wikimultihop).
The acquired revision is
[`209e761834d1ce055856fc11072c0a5aab47601d`](https://github.com/Alab-NII/2wikimultihop/commit/209e761834d1ce055856fc11072c0a5aab47601d),
authored by Xanh Ho on 2020-12-08. Its root tree is
`545a956af257f0c79c68c39a358086de7cbf243b`.

Exact original files and metadata are in
[`tests/fixtures/twowikimultihopqa_upstream_codex197`](tests/fixtures/twowikimultihopqa_upstream_codex197/README.md):

- `2wikimultihop_evaluate.py`, the original canonical-answer evaluator:
  SHA-256 `854b03c487608286d6381379eb32e46d9b845493527d1fe1951d0bf4ec923a40`.
- `2wikimultihop_evaluate_v1.1.py`, the alias-aware evaluator:
  SHA-256 `7c09ee2ec98c7ecb57df79eb68dba22eb381ab58d50e730dfcefafb4dda31458`.
  This matches the existing adapter's declared evaluator pin. The transcribed
  function region also matches exactly when the adapter is read as text.
- Exact upstream `LICENSE` (Apache-2.0) and `requirements.txt`; original
  HotpotQA attribution is preserved. No `NOTICE` is present in the pinned root
  tree. Dataset licensing was not evaluated.
- Original commit/root-tree API responses and a `provenance.json` receipt with
  original paths, per-file sizes, SHA-256/Git blob pins, URLs, acquisition time,
  dependency evidence and trust boundaries.

Acquisition used explicit GitHub Git blob API requests. Each decoded original
file matched its tree's Git blob SHA-1; the root tree object was reconstructed
and its SHA-1 verified. Offline tests pin both code and metadata independently
of self-declared receipt hashes. The commit is unsigned; observed origin rests
on GitHub HTTPS metadata, and parent review is still required. An initial raw
host request failed with a connection reset and saved no payload. The previously
declared complete archive was not fetched or revalidated.

No README, baseline source, prediction example, dataset archive, task/answer,
alias table, train/dev/test/heldout payload or model was fetched or opened.
Public root-tree path/blob metadata and PyPI dependency metadata were inspected.

## Answer F1 and Joint F1

The metric definitions come directly from the pinned evaluators, rather than
from a mirror scorer or an inferred leaderboard label. `f1` is answer F1;
`joint_f1` is a separate field. The fixture README explains all sixteen fields
and the precise normalization, alias, evidence and aggregation rules.

Answer F1 is the normalized-token multiset precision/recall harmonic mean.
v1.1 independently maximizes answer EM, F1, precision and recall over the
canonical answer plus aliases/demonyms. Joint precision is the product of
answer/supporting-fact/evidence precision; Joint recall is the corresponding
recall product. Joint F1 is the harmonic mean of those two products, not the
product of the component F1s. Joint EM multiplies the three EM components.

Every gold ID remains in the denominator. Missing channel predictions contribute
zero and disable Joint for that ID; extra prediction IDs are ignored. All
sixteen fields are accumulated in gold-file order, divided by the number of
gold rows, multiplied by 100 and rounded once to two decimals. These missing-ID
rules do not convert malformed inputs, empty gold, missing dependencies or
runtime exceptions into ordinary measured zeros.

Observed fabricated-input examples distinguish the rules: all three component
F1s can be 66.67 while Joint F1 is 33.33; a perfect answer with a missing
support/evidence channel has answer F1=100 and Joint F1=0. Two v1.1 quirks also
matter: independent answer-alias maxima can give answer F1=80 but Joint F1=100;
multiple valid evidence alternatives for one gold group can give evidence
recall=200 and Evi/Joint F1=133.33. The fixture preserves these behaviors. No
clamping, scorer correction or production rewiring was performed.

## Dependency findings and custodian handoff

AST inspection establishes a self-contained evaluator with standard-library
imports and only one external runtime import, `ujson`. The upstream manifest
does not pin it. `spacy`, `tqdm`, `torch==1.1.0` and `joblib` appear in the
manifest but are absent from both evaluator import graphs.

The full unchanged programs were exercised using the existing real
`ujson==5.10.0`, which declares no transitive Python runtime dependencies. The
receipt records CPython 3.12.4/Linux x86_64, pytest 7.4.4, the installed native
module digest and BSD-3-Clause license-file fingerprint. `readelf` identifies
direct native dependencies on `libstdc++.so.6`, `libgcc_s.so.1` and `libc.so.6`.
Their loader/transitive closure was not attested.

PyPI metadata pins a compatible CPython 3.12 Linux wheel to SHA-256
`f8ccb77b3e40b151e20519c6ae6d89bfe3f4c14e8e210d910287f778368bb3d1`
and the sdist to
`b3cd8f3c5d8c7738257f1018880444f7b7d9b66232c64649f562d7ba86ad4bc1`.
Neither artifact was downloaded or installed, and the existing native extension
was not linked to the published wheel. The required custodian handoff is the
pinned compatible wheel plus its license notices, an installation-origin receipt,
and a supported Python/native-runtime image receipt, followed by a fresh offline
import/synthetic run. An sdist build would require additional build closure.
This remaining request concerns deployable dependencies; the original evaluator
source no longer requires custodian acquisition.

## Verification and limits

[`tests/quality/test_twowikimultihopqa_provenance_codex197.py`](tests/quality/test_twowikimultihopqa_provenance_codex197.py)
passed **38 tests** on fabricated inputs in 0.24 seconds. Exact command and
output are in
[`twowikimultihopqa-provenance-codex197-test-result.txt`](twowikimultihopqa-provenance-codex197-test-result.txt).
Coverage includes commit/tree/blob linkage, source/license drift, missing
license, dependency/import pins, the unchanged adapter transcription region,
both original evaluator versions, token counts/sentinels, channel omissions,
gold denominators, aliases/demonyms, empty-set rules and the two v1.1 quirks.

Tests block sockets and restrict evaluator opens to generated synthetic files.
They never import the dataset adapter or construct a pool. There is no skipped
upstream gate, local replacement implementation or substituted JSON dependency.
The old data-backed scorer suite was not run under the no-data restriction.

These are finite source-integrity and synthetic semantics checks, not complete
validation of platform wrappers, trusted input transport, real dataset identity,
alias completeness or leaderboard comparability. No endpoint, model, H0,
diagnostic or pilot was used and no benchmark score/coverage receipt is claimed.
The unique task scratch directory was removed after preserving the test result.

The original pinned Python files retain upstream trailing whitespace and final
blank lines. A full staged whitespace check reports those unchanged upstream
bytes; the authored test/docs/receipt/result files pass the focused whitespace
check. Normalizing the original files would invalidate their provenance pins.
