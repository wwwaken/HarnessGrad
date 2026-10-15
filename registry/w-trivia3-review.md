# TriviaQA payload-free key and metadata audit — w-trivia3

**Result: `rc.nocontext` validation has 17,944 stored rows; two measured `rc`
validation shards contain 8,972 rows but only 8,202 distinct QuestionIds. The
official numeric denominator and export-to-official key mapping remain UNKNOWN.**
The measurements are at `tests/fixtures/hg_trivia3/observations.json:134`, `:470`,
`:622`; replay command: `python3 tests/fixtures/hg_trivia3/verify_evidence.py`.
No closure, withdrawal, scorer run, or production authorization is proposed.

## Evidence scope, commands, and identities

`F` below expands to `tests/fixtures/hg_trivia3/`; all shortened F citations use
that existing in-repository directory. `P` expands to
`tests/fixtures/hg_trivia2/`. FOUND means retrieved/observed; ABSENT is limited to
an enumerated scope; UNKNOWN means unobserved, incomplete, or not searched.

The starting obligation is `registry/dataset-blockers.json:905`. This audit
builds on the completed metadata review at `registry/w-trivia2-review.md:42`,
`:76`, `:152`, `:175`, `:216`. It does not repeat its execution-receipt search.
The predecessor loader, filenames, counts and declared object identities are
not used to infer input membership or executed conversion behavior.

Acquisition command **A**: `python3 -u tests/fixtures/hg_trivia3/audit_keys.py`.
It was run three times during transport debugging. The first attempted all
no-context splits plus validation; later passes narrowed to validation and reused
only hash-checked successful byte ranges (not an old benchmark run ID).
The attempt scopes/results/errors are `F/partial-attempt-summary.json:1`,
`F/validation-attempt2-summary.json:1`, `F/key-audit-summary.json:1`. These are
incomplete acquisitions, not successful full audits or benchmark receipts. After handoff, A is historical only: preserve these receipts; replay V without network access.
The final invocation's exact stdout is retained in
`/mnt/20t/xubuqiang/hg-work/trivia3/attempt3-output.txt` and hash-bound by
`F/external-evidence-manifest.json:1`.

Replay command **V**: `python3 tests/fixtures/hg_trivia3/verify_evidence.py`.
It verifies range body digests, HTTP 206 Content-Range and redirect revision/LFS
bindings, reconstructs each complete identity inventory from only approved
column bytes, and recomputes set intersections. It does not import a dataset
loader or evaluator. Exact command/output is `registry/w-trivia3-validation.txt`.

Each GET URL is exactly
`https://huggingface.co/datasets/mandarjoshi/trivia_qa/resolve/0f7faf33a3908546c6fd5b73a660e0f8ff173c2f/<path>`
(early requests append `?hg_trivia3_range=<start>-<end>`).
Every observed URL, Range, Content-Range, status, UTC acquisition time, redirect
`X-Repo-Commit`, `X-Linked-ETag` and byte digest is in the external
`ranges/<path-with-__>/http-receipts.json` files enumerated at
`F/observations.json:4`; their exact SHA-256 digests are committed there.
The external manifest hash-binds every retained file. These are verified HTTPS
range observations bound to the requested immutable revision and declared LFS
identity, **not recomputed full-file LFS digests or conversion attestations**
(`F/audit_keys.py:82`, `F/verify_evidence.py:35`).

Only physical `question_id`, `question_source`, nested `filename` and nested
`doc_source` column chunks were allowed. `question`, text/title/context/URL and
all `answer.*` data pages were never read. Footers can contain statistics for
other columns: those bytes remain external, their values were not inspected or
emitted into git; only schema names and row counts were used. This boundary is
enforced/rechecked in `F/audit_keys.py:24`, `F/verify_evidence.py:44`.
No original JSON archive or HumanAnswers value was ingested. The retained
first-five packet, v2 identity and historical receipts were not used or edited.

## 1. HumanAnswers: which keys carry it?

| Audit question | Observed identity/key set and source/command | Verdict |
| --- | --- | --- |
| Declared HumanAnswers fields | Prior complete scope: all twelve declared schemas, eight config routes and 150 pinned tree paths; `registry/w-trivia2-review.md:53`. | **ABSENT within declarations**, as already established. |
| Stored dedicated HumanAnswers field | Every physical column path in the thirteen retrieved footers, listed individually in `F/observations.json:104`; A retrieves and V checks this exact scope. `human_answer_field_present=false` in each. | **ABSENT in these thirteen shard schemas**; not a whole-export schema measurement. No row in these shards can carry a dedicated physical HumanAnswers column. |
| Which consumed-input QuestionIds have HumanAnswers present/nonempty? | No consumed-input incidence inventory observed; only export identity columns were read (A/V). The predecessor source limitation remains `registry/w-trivia2-review.md:62`. | **UNKNOWN**, not an empty key set. Export omission cannot answer input incidence. |
| Preserved under normalized aliases / redundant after official normalization? | No per-input-key normalized containment/preservation attestations. Official source reads both lists at `tests/fixtures/triviaqa_upstream/evaluation/triviaqa_evaluation.py:76`; A/V never decode either list. | **UNKNOWN**. No answer-value or sample-based inference. |

Settlement needs the consumed input's immutable key-only incidence inventory,
including absent/present-empty/present-nonempty states, linked to export shard
and row ordinal, plus upstream-computed per-key normalization-containment and
preservation booleans. Do not publish aliases, answer text, or guessable hashes
of individual answer strings. The present export schemas cannot retroactively
provide those input states (`registry/w-trivia2-review.md:71`).

## 2. Twelve declarations versus eight exported configurations

This is a declaration/route reconciliation, not evidence of twelve materialized
datasets. The enumeration below transcribes the prior pinned inventory; no new
tree/schema search was performed. Inputs: `P/views/hub-revision-final.json:71`
(`cardData.dataset_info`; routes at :1477), `P/inventory.json:11`;
prior derivation `registry/w-trivia2-review.md:103`. Machine-readable enumeration:
`F/declarations.json:1`. Exact extraction command: `python3 tests/fixtures/hg_trivia3/enumerate_declarations.py`; output is in the validation file.
Routes/directories are the eight observed exported configs, **not Domain labels**.

| dataset_info declaration (all twelve) | train / validation / test declaration | Route and directory in pinned inventory | Verdict |
| --- | --- | --- | --- |
| rc | 138384 / 17944 / 17210 | rc | FOUND export config |
| rc.nocontext | 138384 / 17944 / 17210 | rc.nocontext | FOUND export config |
| rc.web | 76496 / 9951 / 9509 | rc.web | FOUND export config |
| rc.web.nocontext | 76496 / 9951 / 9509 | rc.web.nocontext | FOUND export config |
| rc.wikipedia | 61888 / 7993 / 7701 | rc.wikipedia | FOUND export config |
| rc.wikipedia.nocontext | 61888 / 7993 / 7701 | rc.wikipedia.nocontext | FOUND export config |
| unfiltered | 87622 / 11313 / 10832 | unfiltered | FOUND export config |
| unfiltered.nocontext | 87622 / 11313 / 10832 | unfiltered.nocontext | FOUND export config |
| unfiltered.web | unspecified / unspecified / unspecified | ABSENT from eight routes/directories | declaration only |
| unfiltered.web.nocontext | unspecified / unspecified / unspecified | ABSENT from eight routes/directories | declaration only |
| unfiltered.wikipedia | unspecified / unspecified / unspecified | ABSENT from eight routes/directories | declaration only |
| unfiltered.wikipedia.nocontext | unspecified / unspecified / unspecified | ABSENT from eight routes/directories | declaration only |

**Supported:** eight exported config routes, twelve metadata declarations.
**Unresolved:** why the four extra declarations exist, their intended members,
and whether they describe any consumed input. No zero counts are substituted;
the older zero-count declaration is a different observation
(`registry/w-trivia2-review.md:111`). No naming-based Web/Wikipedia membership
claim follows.

## 3. Prose 18,669 versus structured 17,944 validation rows

| Observation | Exact source / command | Scope and verdict |
| --- | --- | --- |
| `\|rc                  \|138384\|     18669\|17210\|` and `\|rc.nocontext        \|138384\|     18669\|17210\|` | P/responses/hub-card-proxy-retry.body:996; immutable URL/digest at P/response-catalog.md:62; `sed -n '994,1000p' tests/fixtures/hg_trivia2/responses/hub-card-proxy-retry.body` | FOUND prose declaration. |
| Both structured validation counts are 17944 | P/views/hub-revision-final.json:180, :299; F/declarations.json:1; extraction command in validation file | FOUND structured declaration. |
| Sole `rc.nocontext/validation-00000-of-00001.parquet` footer: 17944 rows | A/V, F/observations.json:134; corresponding raw tail/footer and Range bindings in external receipt | **17,944 corroborated as stored row count**; **18,669 contradicted for this exact export split**. Difference is 725 by subtraction; no missing-member identity inferred. |
| `rc` validation shards 00002 and 00003: 4486 rows each | A/V, F/observations.json:246 | Only 2/4 rc shards measured. **Full rc row total still uncorroborated by footer enumeration here**; do not transfer the no-context observation by equal counts. |
| Official selected unique-key count | No complete original Domain/VerifiedEval key inventory; official construction at tests/fixtures/triviaqa_upstream/utils/dataset_utils.py:7 | **UNKNOWN**; neither prose nor structured row count is an established official denominator. |

## 4. Actual source and verification membership

| Audit question | Observed key set / source / command | Verdict |
| --- | --- | --- |
| question_source members | Complete source-string frequencies for each of four measured key shards at F/observations.json:483, :513, :538, :572; A/V. These are quiz-site strings, e.g. the fourteen distinct strings enumerated for unfiltered.nocontext validation. Exact per-key assignments are in the hash-bound external JSONL inventories. | **FOUND exported question_source assignments for this scope**. A quiz source string is not original Domain. |
| Document source and filename members | Nested filename/doc_source columns in three context shards; observed entity-page doc_source labels are Search and TagMe (F/observations.json:479, :509, :568); approved paths and exact inventory digests at F/key-audit-summary.json:1 and F/observations.json:495. | **FOUND exported document identifiers** for measured shards. Their source labels do not establish original Domain or filtering. |
| Original Domain / VerifiedEval and question/document verification flags | Prior declaration absence at registry/w-trivia2-review.md:133; additionally no domain/verified physical field among all columns in thirteen enumerated footers (A/V, F/observations.json:104). | **ABSENT fields within enumerated schemas; actual input membership UNKNOWN**. No unverified/false default assigned. |
| rc versus source-specific member equality; context/no-context equality | Only four complete key shards, listed in next table; no complete paired rc/rc.web/rc.wikipedia/no-context member inventories. | **UNKNOWN**. Shared QuestionId observations below do not establish source partition or equality. |

## 5. Row identities, QuestionId duplicates, and candidate scorer keys

Each external JSONL line binds shard ordinal to QuestionId and available document
identifiers; inventories are rebuilt from range bytes by V. No full content-row
equality or answer agreement was measured. `A`/`B` below are two shards of the
same `rc` validation split, not inferred cross-source rows.

| Measured identity/key set | Stored rows | Distinct QuestionIds | Candidate QuestionId--Filename occurrences / distinct | Source and verdict |
| --- | ---: | ---: | ---: | --- |
| A: rc/validation-00002-of-00004.parquet | 4486 | 4486 | 12837 / 12837 | F/observations.json:470; A/V; within-shard duplicates ABSENT in these keys. |
| B: rc/validation-00003-of-00004.parquet | 4486 | 4486 | 7810 / 7810 | F/observations.json:501; A/V; within-shard duplicates ABSENT in these keys. |
| unfiltered.nocontext/validation-00000-of-00001.parquet | 11313 | 11313 | not read / not read | F/observations.json:529; A/V; entire split's QuestionIds unique. Zero in candidate-key summary means no filename columns read, not zero official Web keys. |
| unfiltered/validation-00003-of-00007.parquet | 1616 | 1616 | 19017 / 19017 | F/observations.json:560; A/V; within-shard duplicates ABSENT in these keys. |
| A union B | 8972 | 8202 | 20647 occurrences / 19308 distinct | **FOUND 770 shared QuestionIds and 1339 shared candidate QuestionId--Filename keys** (A/V, F/observations.json:584). Uniqueness is contradicted for both candidate key rules on this measured rc slice. This does not prove duplicate full rows, original official Domain membership or answer agreement. |
| unfiltered shard versus complete unfiltered.nocontext split | 1616 measured context IDs | all 1616 present in no-context set | no official key claim | F/observations.json:615; **FOUND subset by QuestionId only**, not answer preservation or full member equality. |

All six pairwise QuestionId and candidate-document-key intersections are
enumerated in `F/observations.json:584`. Cross-shard doc-key intersections are
measured, not inferred from row counts. Duplicate answer agreement, actual
writer behavior and full-export duplicate incidence remain UNKNOWN. The first
attempt's partially read train/test columns provide no complete key inventory;
they are not used as membership evidence (`F/partial-attempt-summary.json:1`).

## 6. Official key mapping, aggregation, and numeric denominator

| Question | Observed rule or key set / source / command | Verdict |
| --- | --- | --- |
| Official algorithmic key rule | Wikipedia: QuestionId dictionary; otherwise QuestionId--Filename across EntityPages and SearchResults. Verified filtering occurs first. Source-only prior review at registry/w-trivia2-review.md:187; tests/fixtures/triviaqa_upstream/utils/dataset_utils.py:7, :14, :26, :37. | **ESTABLISHED source rule**, inspected, never executed. |
| Export identities mapped to official filtered keys | Measured QuestionIds/filenames at F/observations.json:470; original Domain/VerifiedEval field absence in thirteen footers at :104; no original/export correspondence receipt was observed in this audit. | **STILL UNDETERMINED / UNKNOWN**. Candidate keys are not authenticated official membership. |
| Alias aggregation | Official `NormalizedAliases` plus normalized optional `HumanAnswers`; per-key max EM and separate max F1, then 100*sum/len(qid_list). Missing predictions retain denominator terms; default qid_list is ground_truth.keys(); supplied lists are not deduplicated. Source-only review registry/w-trivia2-review.md:216 and tests/fixtures/triviaqa_upstream/evaluation/triviaqa_evaluation.py:76, :102, :129. | **ESTABLISHED source algorithm**; no numeric result calculated. |
| Unique QuestionId denominator equal to rc raw rows | A/B: 8972 row occurrences versus 8202 distinct QuestionIds (A/V, F/observations.json:622). | **CONTRADICTED for measured slice**. Does not assign a full-split or official denominator. |
| Official numeric denominator for pinned export | No complete selected, filtered, source-bound official key inventory and requested qid_list (F/key-audit-summary.json:1; F/observations.json:627). | **STILL UNDETERMINED / UNKNOWN**. Neither 18669 nor 17944 is established as the official denominator. |

**Single settling artifact:** an immutable, producer-attested **input/export
membership-and-preservation audit packet**, bound to this export revision and
its shard identities, consumed input hashes and pinned official helper/scorer.
It must enumerate each input QuestionId/document identity, original Domain and
all verification flags, selected/filtered membership, export shard/row ordinal,
official key, duplicate/overwrite order, exact requested qid_list (or explicit
default), and per-key HumanAnswers incidence/normalization containment and
answer-preservation booleans without answer text. Canonical inventory digests
and observed counts must accompany the packet. This would settle mapping and
numeric denominator without guessing aliases or executing a scorer. It would
not itself prove which converter executed unless separately attested.

## Integration boundary

`registry/proposals/w-trivia3.json:1` proposes only evidence additions and remaining
payload-free obligations. The registry, withdrawn requirements, journal,
AGENTS.md, frozen receipts and local v2 code are unchanged; validation checks
the git diff. No dataset/benchmark/scorer/model/GPU execution or pilot occurred.
Required checker command/output and explicit unverified items are recorded in
`registry/w-trivia3-validation.txt:1`. External evidence is retained under the
assigned persistent scratch directory; no pytest or temporary SSD materialization
was needed.
