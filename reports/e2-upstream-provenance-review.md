# E2: public upstream provenance acquisition

**Zero full blocker closures. Both owned blockers remain external.** Public
metadata acquisition and local consistency checks cannot supply the outstanding
authenticated custody and independent human decisions. No positive attestation,
review approval, production admission or benchmark measurement is issued.

Workspace: `/tmp/hg-e2`, registered detached worktree at
`13fa17c451eb0cb44adcf5126fa25ccd345c47c8`. All writes stay in this worktree and the permitted
documentation/fixture paths. No adapter, driver, runtime or evaluator changes.
No whole-suite run, dataset payload access, model, GPU or endpoint calls.

## Requirements read before acquisition (verbatim)

The user quoted the earlier requirements retained in
`reports/b6-blocker-evidence/original-five-blockers.json:15` and `:84`.
B6 already narrowed those requirements. The actual current registry requests
were read first and saved unchanged in
`tests/fixtures/upstream_provenance_e2/starting-blockers.json:22` and `:47`.

### livecodebench / row-attestation

> Use the existing task-207 custody/reviewer procedure to obtain a genuine metadata-only complete catalog/rank and authenticated row/pool/split/statement linkage, plus separate independent approval. Compare against the preserved inert selection without payload reads. Exact upstream release/builder/shard metadata is now acquired; it cannot establish the local sorted-row mapping or manufacture reviewer approval.

### twowikimultihopqa / hub-data-provenance

> Obtain metadata-only original-release archive/file digest custody, explicit dataset/alias rights and completeness/ID-coverage attestation, and independently authenticated selected-manifest linkage to the pinned raw artifacts. Canonical Hub artifact identity and intended evaluator-version documentation are acquired; do not substitute builder-converted rows or infer original release equivalence. Keep payload and production execution outside this review.

## Existing checked-in work: what it establishes

- **B6** already acquired canonical HTTPS Hub metadata/tree and builders at the
  pinned LCB and 2Wiki revisions. It matched all six LCB shard LFS digests and
  the 2Wiki raw dev/alias hashes. It distinguished upstream shard order from
  local sorted IDs. It also distinguished builder-generated 2Wiki rows from
  the raw JSON/alias route.
  These are existing acquisitions, not new discoveries here:
  `reports/b6-dataset-blocker-review.md:44`, `:187`, `:289`.
- **Task 206 / task 197** establish the pinned original evaluator sources and
  Apache-2.0 code license; task 206 explicitly leaves Hub/data rights and custody
  open: `docs/task-206-twowiki-provenance-review.md:15`, `:50`;
  `tests/fixtures/twowikimultihopqa_upstream_codex197/README.md:12`.
  The later B6 evidence supersedes task 206's missing-Hub-identity observation.
- **Task 207** supplies an unissued target template and a separate custodian /
  independent-review protocol, not a record, trusted key, signature or approval:
  `docs/task-207-livecodebench-operator-packet.md:3`, `:38`, `:50`, `:56`, `:64`.
  Its prohibition on network applies to its future offline verification commands;
  this task separately authorizes public metadata acquisition. Those admission
  commands and the statement-reading identity entry point are not run here.
- B6's copies of historical 2Wiki split/selection metadata have local byte custody,
  explicitly **not independent authentication**:
  `reports/b6-blocker-evidence/preserved-receipts/custody.json:3`.
  Earlier receipts and the inert selection remain unchanged.

The verifier rechecks 17 inherited file digests. Their exact paths, byte counts
and SHA-256 values are in `tests/fixtures/upstream_provenance_e2/comparison.json`.
The inherited canonical Hub metadata SHA-256 values are LCB
`501d60839cc3f592b476d5d79b1093f29ade0144fb3318f1b261d3ece274e4d4` and 2Wiki
`6340521cf170fac8e82785cd21a5e9941306ea6ee54963438b6555561b09d21a`.

## LiveCodeBench: acquired evidence and limits

New canonical Hub history returns the pinned revision and two commits titled
“add v6”: `819a13a5c0347c1bd2f5600a35bc9ac9695d461b` and
`503416f80ac447d31f252d8434023786ce45dd0c`. The raw history is
`tests/fixtures/upstream_provenance_e2/lcb-pinned-history/hop-0.body:1`.
Commit titles support release-history documentation only; this API does not
supply a signed complete ID catalog or local row/pool/split custody envelope.

The refs response has `tags=[]`, `converts=[]` and `main` pointing at the pinned
revision: `tests/fixtures/upstream_provenance_e2/lcb-refs/hop-0.body:1`.
This describes the observed refs, not an assertion that no attestation exists
elsewhere. B6's complete pinned path inventory contains the card, builder, image
and six shards, with no separately advertised ID-only catalog or custody sidecar:
`reports/b6-blocker-evidence/lcb-hub-proxy-tree/hop-0.body:1`.
No catalog is reconstructed from shards or a viewer/rows endpoint.

The newly acquired pinned card has Git blob SHA-1
`37908db28f9e16ad36a1c6dfb5c30201cc325f99`, checked against B6's existing
canonical revision metadata. Its changelog ends at v5 even though B6's builder
maps v6; the card is not a complete release catalog. Its `license: cc` is
unspecified, not a clearance: `tests/fixtures/upstream_provenance_e2/lcb-pinned-card/hop-1.body:2`, `:20`.

### Compare against preserved inert selection

The preserved inert file SHA-256 remains
`683d0a0e689b4579ffd8f61a3e672299c8e944014efcc9cffa75e99af3512d38`.
Its selected entry says `livecodebench/740`, `abc360_a`, `train`, with
`FILENAME_INFERRED_NOT_POOL_ATTESTED`:
`docs/evidence/lcb740/prior-selection.inert.json:92`.
Its source says revision `0fe84c3912ea0c4d4a78037083943e8f0c4dd505`, declared
pool SHA-256 `bbf2bf826856156656568f568e4026f7702f90b5da22a880b733b755a69f4256`
and inferred split SHA-256
`af97cfb379d5af4ae2437e6fda50d4a15199f0d001b0dda64625304a85c9f187`:
`docs/evidence/lcb740/prior-selection.inert.json:146`.

Those declarations and the preserved launch's statement digest match every
corresponding task-207 template field. The metadata-only ranking of the three
eligible IDs selects `/740`; the original-ID hash rule places it in train.
This verifies existing declaration/selection consistency, not the physical pool
row, catalog completeness, statement bytes or fresh pool hash. Local pool code
sorts unique IDs (`data/datasets/livecodebench/prepare.py:101`, `:121`), so an
upstream ordinal cannot prove the local index. The comparison is explicitly
non-attesting in `tests/fixtures/upstream_provenance_e2/comparison.json`.

**Still required — human custody and independent review:** the actual pool
custodian must substantiate a complete unique ID catalog, rank 740 and authenticated
pool/split/statement linkage and issue the exact record plus separately signed
envelope. A reviewer independent of the producer and this agent must authenticate
the custodian/key through a trusted channel, review every claim and supply the
separately signed approved exact-byte digest (task 207 lines 38–69). No custodian
was contacted, no such record/key/signature was received, and no approved digest
is manufactured. This blocker remains `external` with `row_attested=false` and
`pool_freshly_verified_here=false`.

## 2Wiki: acquired evidence and limits

Canonical exact-revision Hub history contains only an initial commit and
“Upload folder using huggingface_hub” at the pinned revision. It provides no
original archive digest, member linkage, alias coverage or rights statement:
`tests/fixtures/upstream_provenance_e2/twowiki-pinned-history/hop-0.body:1`.
The GitHub Releases and Tags API responses are each `[]`:
`tests/fixtures/upstream_provenance_e2/twowiki-releases/hop-0.body:1` and
`twowiki-tags/hop-0.body:1`. A repository-scoped issue search for `license`
returns zero items and `incomplete_results=false`:
`tests/fixtures/upstream_provenance_e2/twowiki-license-issues/hop-0.body:1`.
This is a bounded search observation, not proof that no terms exist anywhere.

B6's pinned original README names the December ID-enriched release and alias-aware
v1.1 evaluator (`reports/b6-blocker-evidence/twowiki-upstream-readme/README.upstream.md:6`).
Its old Dropbox share ID differs from the later mutable README's link
(`reports/b6-blocker-evidence/twowiki-upstream-current-readme/hop-0.body:16`).
HEAD on the original link, including `dl=1`, returns HTML metadata with no archive
digest. HTTP 200 therefore does not prove an archive is still downloadable:
`tests/fixtures/upstream_provenance_e2/twowiki-original-download-head/hop-0.headers:44`.

The later link redirects to a different Dropbox shared-file route. A `dl=1`
HEAD follows to an advertised attachment named `data_ids.zip`, length
**259,216,602 bytes**, opaque ETag **1607522485443626d**:
`tests/fixtures/upstream_provenance_e2/twowiki-later-download-followup-head/hop-0.headers:4`, `:7`, `:19`.
Neither this ETag nor the zero-byte HEAD entity's SHA-256 is an archive digest.
There is no archive SHA-256 or member hash response. The first download attempt's
unrecognized CDN-host refusal is retained; a separately named HEAD followup uses
the exact saved redirect and keeps every prior receipt. No archive GET occurs.
Do not substitute this later endpoint for the pinned December release.

The already acquired Hub metadata advertises dev SHA-256
`79f77ae104088ea8e25b1a65dbece768d45771194663bc5660ec9a98070dadf5`
and aliases SHA-256
`f08ffcb6c2cefca9bdbe86b4248d6ad7a7743762d3f7264c14ff0bae85726fb6`;
these match adapter declarations (`data/datasets/twowikimultihopqa.py:94`).
The existing builder yields validation from dev, omits answer/evidence IDs and
loads no aliases (`reports/b6-blocker-evidence/twowiki-hub-proxy-loader/hop-1.body:90`, `:119`).
It does not authenticate the raw route's completeness or license.

### Split and selected-manifest consistency

Reusing B6's preserved metadata only, canonical sorted split JSON reproduces
`161b79332301a152d9ff53ffff073b2f9b307054bc510764068fb48a89bc17b4`,
8,335 train IDs and 4,241 eval IDs. The original 50 and recovery 2 selected IDs
are unique subsets of the same preserved train partition. Their ordered selected
ID lists and compact-JSON SHA-256 values are recorded in
`tests/fixtures/upstream_provenance_e2/comparison.json`. This reuses the historical
selection; it is not a new pilot selection, independently issued manifest or
payload-to-row equivalence receipt. No score is recomputed or reinterpreted.

**Still required — authenticated custody and human rights decision:** the
original-release custodian must supply the archive digest and member digest
mapping to the exact Hub dev/alias artifacts, plus alias ID coverage/completeness
and evaluator-version linkage. The platform data custodian must substantiate the
full imposed split and ordered selected manifests against those artifacts without
payload delivery. The dataset/alias rights holder must provide explicit terms,
including applicable third-party conditions. A reviewer independent of this agent
must authenticate those issuers/receipts and decide whether the rights and custody
evidence satisfy this gate. The evaluator's Apache-2.0 code license is preserved
(SHA-256 `b8c1d7752e71597a45121774b6be93df38a81e1b748be15c063c0759f11e00ea`),
but it supplies no new dataset/alias rights decision. This blocker remains
`external`; no payload or production execution is admitted.

## Every new raw response SHA-256

Paths below are relative to `tests/fixtures/upstream_provenance_e2/`.
HEAD entities contain zero bytes. The repeated empty digest identifies those
empty entities only; the header digests and receipt digests are in `SHA256SUMS`.
Original entity bytes are unchanged. Header files are parsed-header
serializations, not original wire-format bytes. Every request uses ordinary
certificate-validated HTTPS through the preexisting B6 egress proxy. This is
observed origin evidence, not independently verified issuer signatures.

| Raw artifact | Result | SHA-256 |
| --- | --- | --- |
| `lcb-pinned-card/hop-0.body` | GET 307 | `a88533329cd2b7ea07e49c53982cccb2c8d0d83d1cfca1a92e40284385050474` |
| `lcb-pinned-card/hop-1.body` | GET 200 | `fbf0df23c9fb430778f037691bd191ece41d49373c0695151d87549b6f45d809` |
| `lcb-pinned-history/hop-0.body` | GET 200 | `cc74ef23ada8a009f211d1a6531330bd4491ac61e428bd0abd25984ee9f5cffa` |
| `lcb-refs/hop-0.body` | GET 200 | `9c9f407731dbc02775a9bc04f1f5a09827e302a5d54a919c59e6016ac0f10cb6` |
| `twowiki-later-archive-head/hop-0.body` | HEAD 302 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `twowiki-later-archive-head/hop-1.body` | HEAD 200 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `twowiki-later-download-followup-head/hop-0.body` | HEAD 200 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `twowiki-later-download-head/hop-0.body` | HEAD 302 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `twowiki-later-download-head/hop-1.body` | HEAD 302 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `twowiki-later-download-head/receipt.json` | Refused before response | `74ab2613045b43852ec52f871bed4ab9eec25a70bd1beac35eefded25ae5958f` (receipt) |
| `twowiki-license-issues/hop-0.body` | GET 200 | `c9938edecb99d754b2d039ac9eec320a94c769b6a6417921e2dcbef9e2fe01a0` |
| `twowiki-original-archive-head/hop-0.body` | HEAD 200 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `twowiki-original-download-head/hop-0.body` | HEAD 200 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `twowiki-pinned-history/hop-0.body` | GET 200 | `8eebb51231a4a4cfc4cb314c76ac4954a3237cd277777566a56dc0be8371dbf9` |
| `twowiki-releases/hop-0.body` | GET 200 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` |
| `twowiki-tags/hop-0.body` | GET 200 | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` |

## Validation and disposition

The fixture's offline verifier checks every received body/header digest and size,
all 17 inherited pins, exact card Git-blob linkage, refs/history declarations,
unchanged LCB inert/template identities, and historical 2Wiki split/selection
consistency. It also structurally compares the registry with the base: only the
two owned blockers' observations and appended evidence may differ. All statuses,
next actions, other blockers, shared blockers, taxonomy, historical records and
production authorization remain unchanged. No blocker is deleted.

Focused commands and final results are retained in
`reports/e2-upstream-provenance-validation.txt`. Registry checker must remain
`valid=true`. This base has **four** shared blockers; earlier task-206/B6 counts
of eight are historical observations, not this checkout's count.

No diagnostic/pilot runs occur. Benchmark metric, task/trial coverage, endpoint,
model/image hashes, cleanup and comparability receipts are not applicable to this
metadata review; they are not zero scores or production evidence. Existing run
receipts remain preserved. No runtime or snapshot resources are created. Parent
review/integration is separate from this worktree commit.
