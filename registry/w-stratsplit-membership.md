# w-stratsplit: original split recovered; installed pool is Train

**FOUND — published memberships and installed partition binding.** All 2,290
installed rows belong to original Train; zero belong to original Test; zero
installed rows are unaccounted for. The author's published **unofficial**
train/dev files cover 2,061/229 installed rows. This is established by exact
question/answer multiset comparison, including multiplicity, rather than by
matching counts (`tests/fixtures/hg_stratsplit/binding-summary.json:2`, `:9`,
`:15`; `tests/fixtures/hg_stratsplit/analyze.py`, the `Counter` assertions).

**Proposed disposition:** the remaining source-definition half of “original
scorer/split definition” is **satisfied**, subject to parent review of the
authority bridge below. It is **not** a proven-unobtainable limit candidate.
The scorer was already acquired (`registry/w-stratqa-receipts.md:3`). This
finding establishes a mismatch: the installed pool lacks all 490 original Test
members. It does not establish original-benchmark comparability. The parent
decides blocker closure; this worker changes no blocker, withdrawal, adapter,
journal or execution authorization. The proposal is
`registry/proposals/w-stratsplit.json:1`; checks are in
`registry/w-stratsplit-validation.txt`.

## Authority bridge

**FOUND — complete pinned distribution.** GET
`https://storage.googleapis.com/ai2i/strategyqa/data/strategyqa_dataset.zip?generation=1610016136750122`
returned HTTP 200, 3,434,332 bytes, SHA-256
`4911d85eb6721a93bed7645419df77e721808b32b9785dee14ad80e6249e0a90`.
The observed generation header and exact acquisition command are in
`tests/fixtures/hg_stratsplit/dataset-zip.receipt.json:1`. Each of its four
members was read completely; ZIP CRCs and locally computed member SHA-256s
are checked (`tests/fixtures/hg_stratsplit/analyze.py`, ZIP loop;
`tests/fixtures/hg_stratsplit/zip-members.json:1`).

**FOUND — independent official Test ID authority.** At
`allenai/strategyqa-evaluator@49b88ed2b2f1b57385c13e8a0699dee1d227f83e`,
the README says verbatim:

> The file `predictions_dummy.json` is a valid dummy submission file for the
> [StrategyQA leaderboard](https://leaderboard.allenai.org/strategyqa). It contains
> predictions for 490 questions. If you submit it, you'll get this dummy score:

(`tests/fixtures/hg_stratsplit/evaluator-README.md:31`). The retrieved blob
`9a27dcde87984ac6ee7cd0fc0e9c3ce80ecc5148` reproduces its pinned tree entry:
97,022 decoded bytes, SHA-256
`62d72bb17f84df2fb56cb8245c06458b2f45325af3f20e7db5b3b46b3470e4fe`
(`tests/fixtures/hg_stratsplit/git-bindings.json:26`). Its **complete key set
equals the ZIP Test qid set**, without extra/missing IDs. The code checks
`dummy_ids == test_ids` and both sets have 490 unique IDs
(`tests/fixtures/hg_stratsplit/analyze.py:102`; successful command/output in
validation). Only keys were used, not prediction values or scores. The official
code README links this evaluator (`tests/fixtures/hg_stratsplit/author-README.md:148`).

**FOUND — exact author train/dev membership authority.** At
`eladsegal/strategyqa@1ba1e97452e189569357876f2854b01357ffbe37`,
`data/strategyqa/train.json` and `dev.json` were retrieved by pinned Git blobs,
decoded and authenticated against the complete recursive tree and commit/tree
binding (`tests/fixtures/hg_stratsplit/git-bindings.json:2`, `:8`;
`tests/fixtures/hg_stratsplit/repo-commit.body:1`, `repo-tree.body:1`). Verbatim:

> To train our baseline models, we created a 90%/10% random split of the official train set to get an *unofficial* train/dev split: `data/strategyqa/[train/dev].json`.

Two trailing upstream spaces are omitted (`tests/fixtures/hg_stratsplit/author-README.md:43`).
These files contain 2,061/229 unique, disjoint IDs, and their **combined exact
question/Boolean-answer multiset equals the ZIP Train member**. The checks are
in `tests/fixtures/hg_stratsplit/analyze.py:105` and its successful validation
output. This links ZIP Train content to files the author explicitly identifies
as a subdivision of official Train, independently of paper counts.

**FOUND — final publication corroboration.** The ACL PDF returned HTTP 200,
635,125 bytes, SHA-256
`bfa000a0bc7c065f62918b61267032bba4edc196a4e67927c92b9bf6baa0e1de`
(`tests/fixtures/hg_stratsplit/paper-pdf.receipt.json:1`). `pdftotext -layout`
reveals “annotator-based data split”, Table 4's Train/Test 2290/490, and the
statement that the question-writer sets are disjoint. Exact layout-preserving
excerpts and full extracted-text digest are retained
(`tests/fixtures/hg_stratsplit/paper-split-excerpts.txt:6`, `:15`, `:33`). These
counts corroborate membership bytes; they do not generate IDs.

The landing page still returns 403. Its direct endorsement hyperlink to this
GCS object remains **UNKNOWN** (`tests/fixtures/hg_stratsplit/official-page.receipt.json:1`).
The authority bridge instead combines exact official-evaluator Test IDs with
exact author-declared official-Train subdivision content. This is the most
important review target: rejecting that bridge would leave direct landing-page
endorsement unresolved, while the observed membership/content equalities stand.

## Full ZIP member inventory

All entries below are FOUND and fully read. Compressed sizes, CRCs, record counts
and key signatures are also retained in `tests/fixtures/hg_stratsplit/zip-members.json:1`.

| Exact name | Uncompressed bytes | SHA-256 |
|---|---:|---|
| `strategyqa_test.json` | 64207 | `268bec2605a45830ae7f1f3861d5ee2a4a10f4aeaca0358a076760b2eff3ed25` |
| `strategyqa_train.json` | 4281955 | `728e28b7d6bdfe6da3a0a5f8c5923113a79063d199e960cfcc9f8a3ab34cd92c` |
| `strategyqa_train_filtered.json` | 681610 | `5c207a051a4753c930f446591d232520b7db854b19c9da873650643bb03b0362` |
| `strategyqa_train_paragraphs.json` | 7748648 | `e664979065b2eabfb5412b968c82d532d099e3ad86c9e3de5d3065a016edf96b` |

Test's 490 records have exactly `qid,question` keys, no answer field. Train has
2,290 records; filtered Train has 2,821; the paragraph map has 9,251 keys
(`tests/fixtures/hg_stratsplit/zip-members.json:9`, `:21`, `:33`, `:45`). The
latter two files are inventory findings, not installed partitions.
**ABSENT within exactly these four member names:** dev, README, split-definition
or generator member. This does not mean membership is absent: Train/Test qids
are present inside their data files.

## Installed mapping and coverage

`tests/fixtures/hg_stratsplit/membership-ids.json:1` retains the source IDs.
ZIP Train and author train/dev use **different ID namespaces**, with zero qid
intersection despite identical question/answer multisets
(`tests/fixtures/hg_stratsplit/binding-summary.json:33`). No ID translation is
guessed. Exact question text joins the sources, with source Boolean answers
checked against CSV `Yes`/`No`. All installed inputs have exactly the prefix
`Answer with 'Yes' or 'No': ` removed before matching; no other normalization
or fuzzy matching occurs (`tests/fixtures/hg_stratsplit/analyze.py`, CSV checks).

The installed CSV has 200,453 bytes and SHA-256
`c1fd0c271bf98741b68ac1ea3d167c5ccf2ed46da66645d5fc0ed6222e45f055`
(`tests/fixtures/hg_stratsplit/binding-summary.json:2`). Its loader and local
task naming are `data/datasets/strategyqa.py:108`, `:177` and
`data/scaffolds/qa/base.py:242`, `:252`.
`tests/fixtures/hg_stratsplit/installed-row-binding.tsv:1` binds every ordered
CSV row to `strategyqa/test/<zero-based-index>`, canonical parsed-row SHA-256,
prefix-removed question SHA-256, source candidate qids, original partition,
author unofficial partition and imposed side. It exports no answer text.
TSV: 491,438 bytes, SHA-256
`3015ba7fd809b6a8d85af3b4c91dc61a087dba38efb9c26dde118410729dbfd2`
(`tests/fixtures/hg_stratsplit/binding-summary.json:45`).

| Source partition | Source IDs | Installed rows covered | Source members missing from installed pool |
|---|---:|---:|---:|
| Original Train | 2290 | 2290 | 0 |
| Original Test | 490 | 0 | 490 |
| Author unofficial train, within original Train | 2061 | 2061 | 0 |
| Author unofficial dev, within original Train | 229 | 229 | 0 |

Arithmetic: 2,290 + 0 + 0 unaccounted = 2,290 installed; 2,061 + 229 = 2,290
for the unofficial division. Sources: `tests/fixtures/hg_stratsplit/binding-summary.json:9`,
`:15`, and multiset/uniqueness assertions in `analyze.py` in that directory.

**UNKNOWN exact ID assignments for two rows:** indices 42 and 1987 have equal
question/answer content and each matches two IDs in each source namespace.
Both candidates are original Train and unofficial train: partition ambiguity
is zero. The TSV retains both IDs and invents no occurrence-order tie-break.
The other 2,288 rows have one candidate per namespace
(`tests/fixtures/hg_stratsplit/binding-summary.json:36`; exact multiplicity and
duplicate-label command/output in validation).

The imposed 1520/770 split is independently reproduced from the current local
pure `is_eval` predicate, AST-extracted without importing the adapter/harness
(`tests/fixtures/hg_stratsplit/analyze.py`, local predicate extraction;
`data/scaffolds/qa/base.py:123`). Its cross-tab is:

| Author unofficial partition | Platform train | Platform eval | Total |
|---|---:|---:|---:|
| train | 1372 | 689 | 2061 |
| dev | 148 | 81 | 229 |
| Total | 1520 | 770 | 2290 |

All cells are original Train (`tests/fixtures/hg_stratsplit/binding-summary.json:19`,
`:23`). No original membership was inferred from the imposed hash split.
The brief's `registry/w-journalcov-review.md` and `tests/fixtures/hg_wjc2` are
**ABSENT at those exact paths in this checkout**; this packet binds to the
observed CSV/current source directly (`tests/fixtures/hg_stratsplit/binding-summary.json:53`;
exact `Path.exists()` commands/output in validation).

## Attempts and exact search limits

`tests/fixtures/hg_stratsplit/attempts.jsonl:1` has one line per request: 20 HTTPS
requests and the local CSV read. Every line gives exact URL/path, command,
status, response-body SHA-256/bytes and raw fixture path. A null status, digest
or byte count means no response was observed. Receipts retain headers and
errors; the exact outputs are in `registry/w-stratsplit-validation.txt`.
The capture verifies TLS, requests identity encoding, caps each body at 15 MB,
and refuses overwrite (`tests/fixtures/hg_stratsplit/capture.py:20`).

**FOUND:** complete current `ai2i` GCS bucket listing restricted to `strategyqa/`,
`max-keys=1000`, `IsTruncated=false`, all 36 objects enumerated
(`tests/fixtures/hg_stratsplit/gcs-objects.json:1`, `gcs-prefix.receipt.json:1`).
**ABSENT within those 36 exact object keys:** separate dev, README, split script
or ID-list object. The exact guessed `strategyqa/README.md` URL returns 404
(`tests/fixtures/hg_stratsplit/ai2i-readme-candidate.receipt.json:1`). Model/corpus
objects were listed, not downloaded or searched internally; other prefixes,
object versions and buckets are **UNKNOWN**. Exact listing command/output is
in validation; the object-key enumeration is `gcs-objects.json`.

**FOUND:** pinned author repo complete tree, 81 blobs
(`tests/fixtures/hg_stratsplit/repo-files.json:1`). **ABSENT in these path names:**
case-insensitive `split|random|seed` matches. The exact predicate
`[r['path'] for r in tree['tree'] if any(k in r['path'].lower() for k in ['split','random','seed'])]`
returns `[]` in validation. This is only a filename search. Other code bodies,
branches/tags/history and author-published generators elsewhere remain
**UNKNOWN**. No unavailable sampling rule was reconstructed; actual membership
files suffice for the partition definition.

**FOUND:** final paper PDF/text and ACL record. **ABSENT within the ACL record's
enumerated links containing `2021.tacl-1.21`:** a supplementary/appendix download.
The exact HTMLParser command and all matching links are recorded in validation.
This does not cover publisher supplements or unlinked arXiv source material.
The PDF text was searched with
`rg -n -i -C 3 'split|annotator|Train|Test|appendix|supplement' tests/fixtures/hg_stratsplit/paper-text.txt`;
its exact output is in validation. Prose percentages/counts were not converted
into membership IDs.

**UNKNOWN:** paper-linked landing-page content (four variants return 403), the
candidate `ai2.org` page (DNS error), unlinked Drive releases, private materials,
web archives, other author websites and leaderboard runtime internals. The
guessed `https://strategyqa.github.io/` root is 404 only at that URL. Receipts:
`tests/fixtures/hg_stratsplit/official-page.receipt.json:1`,
`official-page-slash.receipt.json:1`, `official-www.receipt.json:1`,
`official-moved.receipt.json:1`, `ai2-current.receipt.json:1`,
`project-github-pages.receipt.json:1`, all within that directory. No global
unobtainability claim is made.

## Retention, replay and verification

Raw bodies are preserved at the ledger's fixture paths as ignored symlinks to
persistent bytes under `/mnt/20t/xubuqiang/hg-work/stratsplit/`. Dataset payloads
and PDF bytes are not committed. The commit contains receipts, scripts,
metadata, member digests, IDs and answer-free row mapping, each under 1 MB.
Machine-local storage paths are explicit in the receipts. Replay on another
machine uses the logged URLs/commands, fresh output paths and body hashes.
Immutable GCS generation/Git blob identifiers are used for dataset content;
ordinary website bodies need not remain byte-identical.

Offline recomputation command: `python3 tests/fixtures/hg_stratsplit/analyze.py`
after acquiring the logged bodies and running the logged `pdftotext -layout`
command. It checks all response digests, commit/tree/blob bindings, ZIP member
CRCs/digests, exact official Test IDs, content multisets, per-row matches and
coverage. The required command `python3 tools/check_dataset_blockers.py`
returned exactly:

```json
{"valid": true, "datasets": 28, "shared_blockers": 0, "historical_records": 11, "production_authorized": false}
```

Exact output and size inventory: `registry/w-stratsplit-validation.txt`.
No dataset, benchmark, scorer, model, GPU, dependency installation or old run
was executed. No official Test gold was acquired. No score is asserted; local
normalized whole-answer EM remains distinct from original Accuracy
(`registry/w-stratqa-receipts.md:3`).
