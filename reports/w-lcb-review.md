# LiveCodeBench metadata catalog and row custody review - w-lcb

**`livecodebench / row-attestation` remains external and open.** No upstream
problem IDs, row ranks or authenticated row/pool/split/statement binding were
obtained. Coverage is **0 upstream IDs against 1,055 locally declared problems**;
the upstream total itself remains unestablished by metadata acquired here.
All six pinned shard identities are linked to the adapter's declarations,
building on B6. The unchanged three-candidate inert selection is reproducible.

This review started at `6b41bd6068326050a745e91c19c2902f86d05414` in registered
worktree `/tmp/hg-lcb`, branch `wg-lcb`. It read the full blocker, task-198 and
task-207 packets, B6 and E2 provenance reviews and fixtures, `reports/LCB_GATE.md`,
`tools/lcb740_identity.py`, `tools/launch_lcb740_candidate.py`, and local
adapter/preparation/split source before acquisition. Prior acquisitions were
reused and rehashed; no repeated Hub card/tree/builder download was needed.

The operator explicitly withdrew independent reviewer/approver gates in this
task and `docs/independent-review-deferred.md`. Task-207's separate sign-off
requirements are superseded for this review. Missing evidence below concerns
real completeness and custody, not a missing human signature. The historical
packets, strict admission code and inert receipts are preserved; no admission
function or launcher was invoked and no positive custody record was created.

## Catalog coverage actually obtained

Pinned dataset: `livecodebench/code_generation_lite`, revision
`0fe84c3912ea0c4d4a78037083943e8f0c4dd505`, configuration `release_v6`.

| Evidence | Actual coverage and limit |
| --- | --- |
| Inherited authoritative Hub revision/tree | Ten files and one directory; all six shards have LFS identities. No separately advertised ID-only catalog or local custody sidecar among these paths. |
| Pinned builder | `release_v6` orders `test.jsonl`, `test2.jsonl`, `test3.jsonl`, `test4.jsonl`, `test5.jsonl`, `test6.jsonl`; produces the upstream `test` split, with increasing keys in shard/line order. No per-shard row counts or ID catalog in the source. |
| Upstream problem catalog/count/rank acquired | **0 IDs; total unknown; ranks unavailable; no complete or partial authoritative problem catalog obtained.** |
| Local declarations | 1,055 problems; historical preparation documentation gives shard counts 400/111/101/101/167/175. These are local historical claims, not newly measured upstream metadata. |
| Preserved candidate metadata | Three inferred pairs: `/83` → `2955`, `/740` → `abc360_a`, `/807` → `abc371_a`. These are not authenticated upstream coverage. |

Authoritative remote identities and preserved raw responses:

- Revision metadata URL:
  `https://huggingface.co/api/datasets/livecodebench/code_generation_lite/revision/0fe84c3912ea0c4d4a78037083943e8f0c4dd505?blobs=true`.
  Raw: `reports/b6-blocker-evidence/lcb-hub-proxy-revision/hop-0.body:1`;
  recomputed SHA-256 `501d60839cc3f592b476d5d79b1093f29ade0144fb3318f1b261d3ece274e4d4`.
- Recursive tree URL:
  `https://huggingface.co/api/datasets/livecodebench/code_generation_lite/tree/0fe84c3912ea0c4d4a78037083943e8f0c4dd505?recursive=true&expand=false&limit=1000`.
  Raw: `reports/b6-blocker-evidence/lcb-hub-proxy-tree/hop-0.body:1`;
  recomputed SHA-256 `91b24116907e1c5e5ed962fa90afe8583a36e97148e0ef6ed8369df21b27dee8`.
- Builder URL:
  `https://huggingface.co/datasets/livecodebench/code_generation_lite/resolve/0fe84c3912ea0c4d4a78037083943e8f0c4dd505/code_generation_lite.py`.
  Raw: `reports/b6-blocker-evidence/lcb-hub-proxy-builder/hop-1.body:48`, `:139`, `:152`;
  recomputed SHA-256 `973e37989fed0f069c8246776e918d0d96600d64a3730cd6242dd76bccf2f7bb`.
  Its recomputed Git blob SHA-1 `c71eaf4560b476b6f5c21a5732b10457ce543321`
  matches the pinned revision metadata. The code was parsed, never executed.

These are source-origin bindings through preserved canonical HTTPS acquisitions,
not publisher-signature verification. Shard LFS values are **advertised object
digests**, matched byte-for-byte to source declarations; shard payloads were not
read or freshly hashed. Full values and every inherited response-chain digest
are in `tests/fixtures/hg_lcb/review.json`.

## New public metadata acquisition and refusal

All requests used canonical proxy `http://172.17.0.1:17890`, default TLS
certificate validation and `Accept-Encoding: identity`. Exact URLs, UTC times,
statuses, lengths and independently recomputed body/header SHA-256 values are
preserved under `tests/fixtures/hg_lcb/`; `SHA256SUMS` covers every fixture file.

| Acquisition directory | HTTP | Complete entity bytes | Result |
| --- | --- | --- | --- |
| `viewer-openapi` | 302 | 110 | Redirect to official public API documentation; no automatic redirect follow. |
| `viewer-openapi-contract` | 200 | 312,494 | Official dataset-viewer OpenAPI contract, separately acquired from its documented GitHub target. |
| `viewer-splits` | 501 | 284 | Viewer rejects the dataset's arbitrary-Python loader. |
| `viewer-size` | 404 | 22 | `{"error":"Not found."}` for `release_v6`. |
| `viewer-info` | 404 | 22 | Same missing-config metadata response. |

`tests/fixtures/hg_lcb/viewer-splits/response.body:1` says:

> The dataset viewer doesn't support this dataset because it runs arbitrary Python code.

Its exact body SHA-256 is
`54ea6de885b7fdb7ed4f8f1ab0094e4d367222b76c3ac4924135898b3b86f154`.
The complete 284-byte response also suggests a Parquet conversion. No conversion
was attempted: it would require reading dataset payloads and would not by
itself authenticate the historical local transformation.

The preserved OpenAPI JSON's `/paths/~1splits/get/parameters`, corresponding
`/size` and `/info` parameters, and `/rows` and `/filter` parameters document
**no `revision` parameter**. `/rows` and `/filter` also document **no column
projection**. The revision query sent in these availability probes therefore
cannot authenticate the pinned revision; these errors are current service
observations only. No row/filter request was sent, and no projection or release
pin was assumed from undocumented parameters. The OpenAPI came from mutable
`main`; its exact body is preserved, not represented as release-time evidence.

Within the inspected pinned tree and public viewer interface, no usable
metadata-only catalog source was obtained. This is a scoped evidence gap,
not a claim that no catalog can exist anywhere.

## Row, pool, split and statement linkage

| Link | Local file and line | Remote identity / finding |
| --- | --- | --- |
| Release pin and six shard object identities | `data/datasets/livecodebench.py:75`, `:93`, `:361` | Canonical revision/tree raw responses above match all six `_FILES` declarations, despite the adapter's download host being `hf-mirror.com`. |
| `test.jsonl` / `test2.jsonl` / `test3.jsonl` | `data/datasets/livecodebench.py:94`, `:95`, `:96` | Corresponding `siblings[].lfs.sha256` and tree `lfs.oid` at the exact remote revision match. |
| `test4.jsonl` / `test5.jsonl` / `test6.jsonl` | `data/datasets/livecodebench.py:97`, `:98`, `:99` | Same authenticated-source metadata match; full values in `review.json`. |
| Upstream order and split | `data/datasets/livecodebench/prepare.py:66`, `:107` | Pinned builder raw `:48`, `:144`, `:153` defines six ordered shards and upstream `test`; local preparation then transforms ordering. |
| Unique sorted local pool | `data/datasets/livecodebench/prepare.py:116`, `:121`, `:146`, `:154` | Rejects duplicate IDs, sorts all unique question IDs, writes one header then body rows. No upstream ID catalog proves this union or `/740` rank. |
| Zero-based local row addressing | `data/datasets/livecodebench.py:190`, `:204`, `:209`, `:285` | Skips header; enumerates body records; `/740` would mean body ordinal 741 / JSONL line 742 if the declared format holds. No acquired upstream identity binds that physical row to `abc360_a`. |
| Declared pool digest | `data/datasets/livecodebench.py:81`; `tools/lcb740_identity.py:14` | `bbf2bf826856156656568f568e4026f7702f90b5da22a880b733b755a69f4256` agrees with task-207/inert declarations. No acquired metadata receipt binds the catalog/transformation to those pool bytes. |
| Imposed split | `data/datasets/livecodebench.py:289`, `:298`; `data/scaffolds/registry.py:161`, `:174`, `:185` | Original task ID hash puts `/740` in local `train`. Upstream publishes `test`; there is no upstream train equivalence. |
| Statement identity | `data/datasets/livecodebench/prepare.py:88`; `data/datasets/livecodebench.py:229`; `tools/lcb740_identity.py:16`, `:17` | Pool copies upstream `question_content`; adapter wraps it in delivery text. The prior launch names `https://atcoder.jp/contests/abc360/tasks/abc360_a?lang=en` and an excerpt digest. No acquired upstream metadata binds that excerpt to this pinned pool row. |

The statement digest
`072b9614bc27ae5fb47d3a7fc90de200c15208722a145d6291985967cb50c14f`
is a **historically declared digest of an English excerpt plus delivery/provenance**,
not raw HTML or a newly hashed statement. Its scope is preserved in
`docs/evidence/lcb740/prior-launch.json:10`. No statement bytes were read.

As an additional metadata check, applying the existing split rule to the
**declared** namespace `livecodebench/0` through `livecodebench/1054` gives
663 train / 392 eval. Canonical serialization from `registry.split_sha` yields
`af97cfb379d5af4ae2437e6fda50d4a15199f0d001b0dda64625304a85c9f187`,
matching the inert selection and task-207 target. This is conditional on that
ordinal universe; it does not attest its actual pool membership or question-ID
mapping. No pool or full historical split receipt was freshly verified.

## Comparison with the preserved inert selection

Recomputed SHA-256 of `docs/evidence/lcb740/prior-selection.inert.json` remains
`683d0a0e689b4579ffd8f61a3e672299c8e944014efcc9cffa75e99af3512d38`.
No original receipt changed. Its `:13` holds three inferred candidate pairs;
`:92` selects `/740` → `abc360_a`; `:146` holds source declarations.

The task-207 template matches the inert selection's task ID, zero-based index,
question ID, revision, declared pool digest, inferred split digest, side and
prior launch's statement digest. These also agree with the current identity
constants. A template match establishes declaration consistency only.

Recomputing ascending `(SHA256(UTF8("livecodebench" + NUL + task_id)), task_id)`
produces `/740`, `/83`, `/807`, exactly matching `:124`. Selecting
`min(30, ceil(10% * 3)) = 1` retains `/740`. Every candidate's original-ID hash
places it in train. The full rank digests are in `review.json` and the unchanged
inert file. These selection ranks are distinct from sorted question-ID pool ranks.
The preserved mapping remains `FILENAME_INFERRED_NOT_POOL_ATTESTED` and the
selection remains `active=false`. This review retains `row_attested=false` and
`pool_freshly_verified_here=false`.

## Finding: requirements still unmet

1. **Complete pinned ID catalog and rank:** no authoritative metadata-only list
   of problem IDs with exact total, per-shard membership/order and completeness
   provenance; therefore sorted unique rank 740 is not established.
2. **Local pool custody:** no reproducible metadata provenance binds that full
   catalog and the actual frozen preparation to the declared pool SHA-256 or
   authenticates `/740` → `abc360_a` (nor the two other inferred candidate pairs).
3. **Split and statement custody:** the conditional split and declared excerpt
   digest agree locally, but no acquired evidence binds the actual pool rows to
   the historical full split and public statement identity/transformation.

The next action is genuinely incomplete, so the blocker retains family
`source-provenance`, status `external`. A complete official metadata catalog
plus reproducible existing local pool/split/statement custody could satisfy the
remaining work; a separate reviewer, human approval or signature is **not** a
required gate. No benchmark, model, GPU, container, endpoint or launcher was run;
no `runs/` or frozen receipt was modified. Validation commands and checker output
are in `reports/w-lcb-validation.txt`; offline reproduction is documented in
`tests/fixtures/hg_lcb/README.md`.
