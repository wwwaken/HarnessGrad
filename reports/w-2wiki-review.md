# twowikimultihopqa / hub-data-provenance — w-2wiki

**OPEN: external.** This review adds real documentation-byte custody and an
explicit account of contradictory public claims. It obtains neither an original
data-release content digest nor an explicit original dataset/alias grant nor an
authenticated selected-row linkage. No human approval is required: the operator's
withdrawal in `docs/independent-review-deferred.md:3` supersedes the earlier E2
report's reviewer/custodian sign-off paragraph. Substantive missing evidence is
the reason this blocker stays open.

Reviewed on 2026-10-15 Asia/Shanghai, in registered `/tmp/hg-2wiki` (`wg-2wiki`),
from `2c82417955798e6f00474bcbf49a80c4811d8df1`. All new HTTP acquisitions used
canonical `HG_EGRESS_PROXY=http://172.17.0.1:17890` with ordinary certificate
validation. Every entity, parsed-header serialization, URL, status and time is
preserved under `tests/fixtures/hg_2wiki/`; every acquired byte has a recomputed
SHA-256 in `SHA256SUMS` and the receipts. HTTPS origin custody is established;
publisher signatures are not claimed. No benchmark, model, GPU, endpoint,
payload retrieval, conversion or scorer execution occurred. runs/ and frozen
receipts were untouched; references below use existing repository metadata.

## Original-release digest custody

B6 already authenticated the Hub's advertised identities, and E2 already acquired
exact-revision upload history, empty release/tag inventories and a zero-result
license-issue search. Those requests and the already passing local historical
split checks were not repeated. The pinned official README identifies the
December 8, 2020 release and original Dropbox share
`9fwhnzektzv4wh5/data_ids.zip`, with `id_aliases.json` and evaluator v1.1:
`reports/b6-blocker-evidence/twowiki-upstream-readme/README.upstream.md:6`, `:12`.

The new **GET of that exact share's HTML page** returns HTTP 200, an error title
and `edison_page_name=shared_link_disabled`:
`tests/fixtures/hg_2wiki/original-share-page/hop-0.body:7`, `:34`;
request/status/MIME/size/digests are in its `receipt.json:4`.
Its 92,113 bytes hash to
`e252567be77af87a9bf912845110adb7c5031e691ba0e2172a97a93ab4343789`.
**That is an HTML error-page digest, not an archive or archive-member digest.**
No attributable archive content hash or member digest mapping was obtained.

The later share's historical HEAD advertises a 259,216,602-byte `data_ids.zip`
attachment with opaque ETag `1607522485443626d`:
`tests/fixtures/upstream_provenance_e2/twowiki-later-download-followup-head/hop-0.headers:4`, `:7`, `:19`.
It was not queried again and is not substituted for the pinned original release.
An opaque ETag, a size, a HEAD empty-body hash and the adapter's separately
pinned evaluator-source archive hash cannot supply a data-release digest.

The inherited Hub response still advertises these raw objects at
`f4f0d7e4ae275d9281e90c46c93e66d6cdda3674`:

| Raw object | Advertised bytes | Advertised LFS SHA-256 |
| --- | ---: | --- |
| `data/dev.json` | 57,614,142 | `79f77ae104088ea8e25b1a65dbece768d45771194663bc5660ec9a98070dadf5` |
| `data/id_aliases.json` | 17,501,406 | `f08ffcb6c2cefca9bdbe86b4248d6ad7a7743762d3f7264c14ff0bae85726fb6` |

Source: `reports/b6-blocker-evidence/twowiki-hub-proxy-revision/hop-0.body:1`;
adapter declarations: `data/datasets/twowikimultihopqa.py:94`.
This review recomputes SHA-256 of the **metadata response bytes**, not of those
unretrieved dataset objects. Original-release archive/member equality remains
unestablished.

## What the rights responses actually say

The new upstream GitHub `/license?ref=main` response identifies Apache-2.0 and
LICENSE blob `342ce459a34de236d05b2be3f01e5f08f6c712e8`:
`tests/fixtures/hg_2wiki/current-repository-license/hop-0.body:1`.
Its decoded 11,337 bytes recompute to
`b8c1d7752e71597a45121774b6be93df38a81e1b748be15c063c0759f11e00ea`
and exactly match task 197's pinned license. The decoded blob's Git SHA-1 also
matches the API identity. The current query is mutable; that does not make the
returned bytes or blob identity ambiguous.

The terms define Licensor as the copyright owner or authorized entity (`LICENSE.decoded:12`),
define Work by the copyright notice attached to it (`:35`), and grant reproduction,
derivative-work, sublicensing and distribution rights subject to conditions
(`:66`). Redistribution requires the license, changed-file notices, retained
attribution and applicable NOTICE content (`:89`). These paths are relative to
`tests/fixtures/hg_2wiki/current-repository-license/`.
Nothing in this response identifies the external December ZIP, `dev.json` or
`id_aliases.json` as the licensed Work, or states their third-party conditions.
This is not a finding that Apache cannot license data; it is missing scope and
authority evidence for these particular external files.

The exact-revision witness mirror card **does explicitly assert**:
“The original 2WikiMultihopQA is released under the Apache License 2.0” and
“This redistribution keeps the same license”:
`tests/fixtures/hg_2wiki/witness-card/hop-1.body:124`.
This is a mirror publisher's statement, not an original rights-holder statement
for the raw dev/alias objects. The card's fields omit aliases (`:61`), and its
referenced `./LICENSE` is absent from the pinned sibling inventory:
`reports/b6-blocker-evidence/twowiki-hub-proxy-witness/hop-0.body:1`.
The freshly obtained card reconstructs the inventory's Git blob
`8ab0f8f05cceb25e55e793f42e05b6135eae3e87`, so the claim has real byte custody.
It does not establish the missing original dataset/alias grant.

The publisher PDF says “This work is licensed under a Creative Commons
Attribution 4.0 International License”:
`tests/fixtures/hg_2wiki/publisher-paper/extracted.txt:50` (PDF p. 1).
It describes using Wikipedia summaries and Wikidata statements (`:162`), but
does not explicitly extend that paper notice to the December ZIP or alias file.
Neither the paper notice nor the mirror assertion supplies that missing scope.

## Completeness and ID coverage actually established

The newly acquired original paper, DOI/Anthology identity
`2020.coling-main.580`, claims **192,606 examples** in Table 1 (PDF p. 6):
154,878 train-medium, 12,576 train-hard, 12,576 dev and 12,576 test.
It says train-medium and train-hard form training data, giving a derived total
of **167,454 training examples**:
`tests/fixtures/hg_2wiki/publisher-paper/extracted.txt:244`, `:258`.
The PDF SHA-256 is
`e5e15d11dbf116a2d58437e7435ae4ce118dfc5373e3568e1c7d1cbdf0a0387d`;
text extraction is reproducibly checked against those raw PDF bytes.
These are author-reported example counts, **not an enumerated unique-ID count or
an attestation for the later ID-enriched files**.

The witness card's front matter advertises 167,454 / 12,576 / 12,576 examples
(`tests/fixtures/hg_2wiki/witness-card/hop-1.body:28`), matching the existing Hub
metadata and the paper's aggregate counts. Its prose table instead says
**113,284 / 12,981 / 12,995** (`:65`), while claiming no examples were added or
removed (`:111`). This internal contradiction prevents treating that statement
as a reliable completeness attestation. It does not establish that the payload
is incomplete; the payload was not inspected.

The pinned original README claims `_id` is unique per sample (`README.upstream.md:42`)
and describes where answer/evidence IDs were added (`:7`), but gives no distinct
entity-ID inventory, alias count, missing/duplicate-ID report, per-file coverage
denominators or digest-bound release manifest. Paths in this sentence are under
`reports/b6-blocker-evidence/twowiki-upstream-readme/`.
The adapter's historical 10,603 answer-ID rows / 203,297 alias-entry note at
`data/datasets/twowikimultihopqa.py:638` remains an inherited declaration, **not
newly authenticated coverage**. Unique raw IDs, answer-ID and evidence-endpoint
resolution coverage, missing aliases, duplicate alias keys and alias completeness
remain unknown in this metadata review. No alias list or coverage number is
invented.

## Selected-manifest linkage: file and line

The two ends are preserved, but the connecting attestation is absent:

| Evidence end | File and line | What it establishes |
| --- | --- | --- |
| Pinned raw dev/alias object identities | `reports/b6-blocker-evidence/twowiki-hub-proxy-revision/hop-0.body:1` | Hub-advertised object SHA-256 and revision |
| Original ordered 50 selected IDs and compact-JSON SHA-256 `c9abd185c059bbc2ef3f8e1ca3ade5e275258c234fb7ad4a5b1512b8b60f1a19` | `tests/fixtures/upstream_provenance_e2/comparison.json:373`, `:429` | Prior local selection, with binding explicitly false at `:431` |
| Recovery two selected IDs `/1589`, `/2501` and compact-JSON SHA-256 `d083aef36aa69942821871272277fdd162a6112a1e204c8007cae342952dedfb` | `tests/fixtures/upstream_provenance_e2/comparison.json:433`, `:440` | Prior local selection, with binding explicitly false at `:442` |
| Shared historical split | `reports/b6-blocker-evidence/preserved-receipts/twowiki-original-run-meta.json:12695` | Local split hash `161b79332301a152d9ff53ffff073b2f9b307054bc510764068fb48a89bc17b4` |
| Meaning of task suffix | `data/scaffolds/qa/base.py:241`, `:247`, `:252` | Task ID uses source row position, not upstream `_id` |
| Raw JSON loading and gold's upstream ID | `data/datasets/twowikimultihopqa.py:546`, `:587` | Source code checks unique `_id` and retains it separately |

E2 already established the 8,335-train / 4,241-eval split and that both selected
lists are unique subsets of train. That prior finding is reused; its ordered
list hashes and inherited source bytes are verified here without replaying runs.
A valid ordinal range or matching selected-list hash cannot authenticate which
raw row occupied each position. The inspected public documentation/Hub inventory
contains no digest-bound ordered `_id` index, selected-row metadata proof or
dev/alias-to-selection mapping. The mirror's schema-conversion claim (`witness-card/hop-1.body:55`)
does not supply an ordinal map or alias bindings. **No selected manifest was
authenticated against raw artifacts in this review.** This is a missing
reproducible binding, not a missing second person's approval.

## Raw response identities and disposition

All paths in this table are relative to `tests/fixtures/hg_2wiki/`.

| Acquired raw response | Bytes | Recomputed SHA-256 |
| --- | ---: | --- |
| `original-share-page/hop-0.body` — HTML error | 92,113 | `e252567be77af87a9bf912845110adb7c5031e691ba0e2172a97a93ab4343789` |
| `publisher-paper/hop-0.body` — paper PDF | 639,331 | `e5e15d11dbf116a2d58437e7435ae4ce118dfc5373e3568e1c7d1cbdf0a0387d` |
| `current-repository-license/hop-0.body` — GitHub JSON | 16,565 | `6af990b37c81a5ffa57461e080149261733253ee01ea8284e8a55bc36d5cdf18` |
| `witness-card/hop-0.body` — redirect entity | 301 | `3afbd10244358de0df03f8de8edf98ccbbd26869c5d345f7ae88c6c66f374410` |
| `witness-card/hop-1.body` — exact-revision card | 5,462 | `1f5b8791e8fede7128e3245f0fbaf2dc663f24caf27dbe5f87165ff1f8f51450` |

**Still missing:** original data-release content digest and member mapping to
the pinned raw Hub objects; explicit applicable original dataset/alias rights;
digest-bound completeness and ID/alias coverage; and authenticated selected
ordinal-to-raw-artifact linkage. The public sources inspected did not supply
these. Neither absence of a paper digest for data nor the mirror's counts can
be repaired by inference. Registry status stays `external`; no gate is weakened,
deleted or downgraded. The next action is clarified to distinguish real custody
from withdrawn human approval. Exact commands and validation output are in
`reports/w-2wiki-validation.txt`.

Validation passed: all fixture digests, inherited metadata identities, decoded
license/card Git blobs, paper extraction and registry/journal scope; 54 existing
source-only registry tests (3.17s); registry checker valid=true with 28 datasets,
2 shared blockers, 11 historical records and production_authorized=false.
