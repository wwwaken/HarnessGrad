# TriviaQA retained-evidence reconciliation — w-trivia4

Question 2 is decided as a declaration/route mismatch. Questions 1, 3 and 4
remain unknown at the whole-input/export level, with bounded findings below
(`tests/fixtures/hg_trivia4/summary.json:4`). In particular, **725 is an arithmetic
difference, not an explained membership difference**
(`tests/fixtures/hg_trivia4/summary.json:133`).

`P` means `tests/fixtures/hg_trivia2/`, `K` means `tests/fixtures/hg_trivia3/`,
and `R` means `tests/fixtures/hg_trivia4/`; every abbreviated citation expands
to that existing repository path. FOUND identifies observed evidence; ABSENT
is limited to a named enumerated scope; UNKNOWN means the required observation
is unavailable here. A section's final verdict applies to its full question,
not to every narrower finding in the section.

The baseline is `registry/dataset-blockers.json:740`. Its immutable upstream
build/export **EXECUTION** clause stays **PENDING-UPSTREAM**. The completed
execution-receipt search is inherited from `registry/w-trivia2-review.md:253`,
not rerun. No `next_action` change or status change is proposed: retain its
execution binding, source/license hashes, runtime/writer versions, consumed
input identities, bounded-search caveat, all unresolved payload-free audit
obligations, inference prohibitions, first-five custody, v2/historical
identities, withdrawn-gate wording and no-production-authorization boundary
(`registry/dataset-blockers.json:740`).

Evidence replay commands, with exact output in `registry/w-trivia4-validation.txt`:
`python3 tests/fixtures/hg_trivia3/verify_evidence.py` authenticates retained
approved ranges offline; `python3 tests/fixtures/hg_trivia4/reconcile.py`
recomputes key-set cardinalities from hash-checked retained JSONL and checks
this worker's summary. The former passed with 13 footers/four key inventories;
the latter records `section_verdicts` and byte-identical custody
(`R/summary.json:4`, `R/summary.json:439`). Neither command executes a dataset
or scorer; read boundaries are `K/verify_evidence.py:51` and `R/reconcile.py:1`.

## 1. HumanAnswers incidence, preservation, redundancy and conflict

Start from the completed metadata finding rather than repeat its inventory
search: all twelve declared schemas lack `HumanAnswers`/`human_answers`
(`registry/w-trivia2-review.md:53`). The retained physical-schema audit adds
ABSENT dedicated HumanAnswers fields in exactly the thirteen shard footers
enumerated at `R/summary.json:20`, inherited from `K/observations.json:104`.
This is schema absence within that scope, not an input-incidence count.

| Required row-level count over installed/exported rows | Retained result | Evidence and limitation |
| --- | --- | --- |
| Consumed-input HumanAnswers present / absent / present-empty / nonempty | UNKNOWN in every category | Only exported IDs, source labels and filenames are available in the four complete key inventories; no consumed-input incidence inventory is established (`K/verify_evidence.py:110`, `R/summary.json:247`). |
| Preserved / truncated / deduplicated-away copies | UNKNOWN in every category | Physical field omission does not identify copies inside other answer fields; answer columns were not decoded (`registry/w-trivia3-review.md:52`, `:67`). |
| Redundant normalized copies / conflicting copies | UNKNOWN in both categories | Keys and duplicate incidence do not establish answer equality or normalized containment; no per-key preservation/containment attestations are retained in this audit (`registry/w-trivia3-review.md:68`, `:146`). |

All seven aggregate placeholders in `R/summary.json:10` are JSON `null`
(UNKNOWN), not zero. A repeated QuestionId or candidate document key is not
evidence of redundant or conflicting answers. Official source concatenates
`NormalizedAliases` with normalized optional `HumanAnswers`; it does not
deduplicate them in `get_ground_truths`
(`tests/fixtures/triviaqa_upstream/evaluation/triviaqa_evaluation.py:76`).
Neither that source rule nor a converter's omission proves what the consumed
input contained (`registry/w-trivia2-review.md:62`).

UNKNOWN — deciding every row needs an immutable input/export correspondence
audit: consumed-input identity, source record/ordinal and QuestionId/document
identity mapped to export shard/ordinal, per-record HumanAnswers presence and
list cardinality, preservation/truncation/deduplication results, normalized
containment and precisely defined redundancy/conflict counts. The prior
settling-artifact contract is `registry/w-trivia3-review.md:161`. Those
answer-derived attestations cannot be reconstructed from the retained key
inventories; reading answers or acquiring payloads is outside this task.

## 2. Twelve metadata declarations versus eight exported configurations

Reuse the exact prior enumeration (`K/declarations.json:1`,
`registry/w-trivia3-review.md:77`); `R/reconcile.py:28` projects its declared
names and non-null route declarations without repeating the schema/tree scan.
The exported column below refers to routes/directories, not original Domain
membership (`registry/w-trivia2-review.md:76`).

| Metadata declaration — all twelve | Exported config route/directory |
| --- | --- |
| `rc` | `rc` |
| `rc.nocontext` | `rc.nocontext` |
| `rc.web` | `rc.web` |
| `rc.web.nocontext` | `rc.web.nocontext` |
| `rc.wikipedia` | `rc.wikipedia` |
| `rc.wikipedia.nocontext` | `rc.wikipedia.nocontext` |
| `unfiltered` | `unfiltered` |
| `unfiltered.nocontext` | `unfiltered.nocontext` |
| `unfiltered.web` | ABSENT in prior enumerated route/directory inventory |
| `unfiltered.web.nocontext` | ABSENT in prior enumerated route/directory inventory |
| `unfiltered.wikipedia` | ABSENT in prior enumerated route/directory inventory |
| `unfiltered.wikipedia.nocontext` | ABSENT in prior enumerated route/directory inventory |

FOUND exact set differences: declaration-only = the four `unfiltered.*`
names in the last four rows; export-route-only = empty set. Recomputed sets
are `R/summary.json:100`. The prior absence scope is all twelve
`dataset_info` declarations, eight config route maps, 150 tree entries and
142 sibling-file declarations (`registry/w-trivia2-review.md:20`, `:103`).
The four extra declarations have unspecified pinned-card counts, not zero;
historical zero declarations must not replace them
(`registry/w-trivia2-review.md:107`). Why the four extra declarations exist
and their intended members remain unknown; no claim of twelve materialized datasets
claim follows from the mismatch (`registry/w-trivia3-review.md:102`).

DECIDED — twelve declarations, eight exported config names, exactly four
declaration-only names as enumerated, and zero export-route-only names;
artefacts `K/declarations.json:1`, `R/summary.json:100`; reproducible command
`python3 tests/fixtures/hg_trivia4/reconcile.py` (exact output in validation).

## 3. Prose 18669 versus structured 17944 validation counts

FOUND primary retained source for **both numbers**: the exact-revision Hub
README at
`https://huggingface.co/datasets/mandarjoshi/trivia_qa/raw/0f7faf33a3908546c6fd5b73a660e0f8ff173c2f/README.md`.
Its retained HTTP-200 observation, 26,668 bytes and body digest are
`P/response-catalog.md:62`; this task makes no new network request.

* Prose primary source: `P/responses/hub-card-proxy-retry.body:994`
  labels the columns `train`, `validation`, `test`; lines 996 and 997 say
  verbatim `|rc                  |138384|     18669|17210|` and
  `|rc.nocontext        |138384|     18669|17210|`.
* Structured primary source in the **same retained card**:
  `P/responses/hub-card-proxy-retry.body:80` says `- name: validation`,
  followed at line 82 by `num_examples: 17944`; the second configuration
  repeats these at lines 140 and 142. The parsed revision response separately
  declares 17944 at `P/views/hub-revision-final.json:180` and `:299`.
* Historical `dataset_infos.json` also declares validation 17944 for `rc`
  and `rc.nocontext` (`tests/fixtures/triviaqa_hub_codex225/historical_loader/dataset_infos.json:1`;
  exact extraction command/output in validation). It gives no membership
  reconciliation and does not identify executed input or conversion.
* The sole `rc.nocontext` validation shard's measured footer contains 17944
  stored rows (`K/observations.json:134`; offline replay command above).
  Only two of four `rc` validation shards have retained measured footers;
  their 4486+4486 does not measure the full `rc` total
  (`registry/w-trivia3-review.md:115`).

These observations corroborate 17944 as this no-context export split's stored
row count, and contradict 18669 **as a stored row count for that exact split**.
They do not identify what was counted to produce the prose number. Both
declarations label validation; neither supplies a prose-side member/key
inventory that could be subtracted from the export inventory. The four
complete key inventories also do not include a complete `rc.nocontext`
validation QuestionId set (`K/key-audit-summary.json:4`). The sole footer
measures rows, not distinct question IDs or answers.

The local count-source search scope is **exactly the 17 paths** enumerated
in `R/count-source-scope.json:1`; sizes and measured digests bind this scope at
`R/summary.json:159`. It includes the pinned card and parsed metadata, viewer
declarations, retained project READMEs and converter source, predecessor and
historical loader/metadata, all three acquisition summaries, observations,
declarations, and both prior reviews. Reproduce the numeric occurrence search:

```sh
python3 -c 'import json,subprocess; from pathlib import Path; scope=json.loads(Path("tests/fixtures/hg_trivia4/count-source-scope.json").read_text()); print("Enumerated count-source scope:", *scope, sep="\n", flush=True); raise SystemExit(subprocess.run(["rg","-n","-o",r"\b(18669|17944|725)\b|18,669|17,944",*scope]).returncode)'
```

Exact output is retained in `registry/w-trivia4-validation.txt`. The search
finds 18669 in the primary card and prior reviews; the only literal 725
match is the prior review's subtraction (`registry/w-trivia3-review.md:115`).
This named count-source search is not a renewed upstream execution-receipt
search and is not a claim about all local files or unavailable upstream data.
The prior inventories expose only the measured key scope
(`K/observations.json:470`); a literal numeric search alone cannot prove no
other reconciliation exists.

UNKNOWN — 18669 − 17944 = 725 (`R/summary.json:155`) has no established
cause or decidable member-set difference in the searched retained evidence.
An immutable correction explaining how the prose count was produced, or its
counting rule and complete counted ID/key inventory bound to source/split
identities plus the complete corresponding export inventory, would decide
it. No such prose-side inventory is established here; payload acquisition,
new upstream searches and dataset execution are outside scope. Do not
substitute a questions-versus-answers, split-selection or deduplication story.

## 4. Domain/VerifiedEval/source membership, duplicates, official keys and denominator

FOUND bounded key measurements replayed offline from four hash-checked
inventories (`R/summary.json:247`); these are exported QuestionIds and
candidate `QuestionId--Filename` strings, not authenticated official keys.
The following table's figures are directly recomputed by
`python3 tests/fixtures/hg_trivia4/reconcile.py`.

| Measured validation identity scope | Rows | Distinct QuestionIds | Candidate document-key occurrences / distinct |
| --- | ---: | ---: | ---: |
| A = `rc/validation-00002-of-00004.parquet` | 4486 | 4486 | 12837 / 12837 |
| B = `rc/validation-00003-of-00004.parquet` | 4486 | 4486 | 7810 / 7810 |
| U = `unfiltered.nocontext/validation-00000-of-00001.parquet` | 11313 | 11313 | 0 / 0 in exported filename lists |
| C = `unfiltered/validation-00003-of-00007.parquet` | 1616 | 1616 | 19017 / 19017 |
| A and B together | 8972 | 8202 | 20647 / 19308 |

FOUND A∩B: 770 QuestionIds and 1339 candidate document keys. A\B and B\A
each contain 3716 QuestionIds; their exclusive document-key counts are 11498
and 6471 (`R/summary.json:365`). Thus repeated QuestionIds and repeated
candidate document keys exist in this measured `rc` slice. It does not
establish repeated full rows, answer equality/conflict, or upstream writer
deduplication. The four within-shard QuestionId duplicate-excess counts are
zero, and candidate document-key excess is zero within each shard
(`R/summary.json:247`).

FOUND C⊆U by QuestionId: 1616 shared, C\U = 0, U\C = 9697. A versus U:
4484 shared, A\U = 2, U\A = 6829. B versus U: 4479 shared, B\U = 7,
U\B = 6834 (`R/summary.json:377`, `:401`, `:415`). These are measured set
relationships between the enumerated partial scopes, not whole-config
source partition/equality. All six pairwise QuestionId/document-key
intersections and both directional differences are retained at
`R/summary.json:365`; no answer comparison follows.

**Filename scope correction.** The retained `U` receipt explicitly lists
filename columns among `read_column_paths` (`K/key-audit-summary.json:160`);
all 11313 reconstructed exported rows have no filenames. In C, one of 1616
rows has none (`R/summary.json:321`, `:353`). Therefore U's 0/0 above is an
observed empty *exported* filename-key set, not a count of original official
Web keys. This refines the prior table's wording “no filename columns read”
(`registry/w-trivia3-review.md:139`); it cannot restore original documents,
Domain, or verified selection. The offline reconstruction checks original
retained inventory equality (`K/verify_evidence.py:107`).

FOUND `question_source` quiz-source-string frequencies and per-row
assignments in these four inventories, and document-source labels `Search`
and `TagMe` in the three context shards (`R/summary.json:261`, `:292`,
`:321`, `:353`). Neither these strings nor config names determine original
Domain or VerifiedEval. ABSENT Domain/verification fields in the twelve
declared schemas and thirteen enumerated physical schemas is the prior
bounded finding (`registry/w-trivia2-review.md:133`, `R/summary.json:20`).
Actual original Domain, VerifiedEval, question/document verification flags,
complete source-specific membership and complete context/no-context equality
remain UNKNOWN (`registry/w-trivia3-review.md:125`).

FOUND **source algorithm**, inspected without execution:

* Original `Domain == 'Wikipedia'`: dictionary keyed by `QuestionId`;
  otherwise key by `QuestionId--Filename` over EntityPages and SearchResults;
  later duplicate dictionary assignments overwrite earlier ones
  (`tests/fixtures/triviaqa_upstream/utils/dataset_utils.py:7`, `:14`, `:17`).
* If `VerifiedEval` is true, retain questions with
  `QuestionPartOfVerifiedEval`; for original Web Domain, also retain pages
  with `DocPartOfVerifiedEval` before dictionary construction
  (`tests/fixtures/triviaqa_upstream/utils/dataset_utils.py:26`, `:37`).
* Accepted aliases are `NormalizedAliases` plus normalized optional
  `HumanAnswers`; EM and F1 each take their own per-key maximum. The default
  requested sequence is `ground_truth.keys()`; both totals divide by
  `len(qid_list)` and multiply by 100. Missing predictions keep denominator
  terms. An explicit supplied list is not deduplicated; extra unrequested
  predictions add no denominator terms
  (`tests/fixtures/triviaqa_upstream/evaluation/triviaqa_evaluation.py:76`,
  `:102`, `:120`, `:129`). HumanAnswers alternatives add no denominator
  terms; source inspection does not establish their preservation.

Key-only audits can decide membership, key multiplicity, source/verification
filter sets and numeric denominator **if** the original flags, complete key
mapping and exact requested `qid_list` are supplied. The current export IDs
do not carry that original-input mapping, so neither 8202 (partial union),
17944 (stored no-context rows) nor 18669 (prose) is an official denominator
(`R/summary.json:427`). Full-row equality, answer agreement, normalized
HumanAnswers redundancy and actual EM/F1 need payload-derived attestations
or separately authorized payload work; cardinalities alone cannot decide
them (`registry/w-trivia3-review.md:146`, `:161`).

The first-five custody packet is retained byte-identically, 7773 bytes,
SHA-256 `1ffd8cbd5319043f7120b05572682f6b170f860804c324e957d79600bb476c07`
(`R/summary.json:439`); only byte identity was checked, and its rows were not
used to establish any whole-export membership or denominator. It supplies
neither converter execution nor metadata-only provenance
(`registry/dataset-blockers.json:740`).

UNKNOWN — complete official source/verified membership, row-content duplicate
incidence, export-to-official key mapping and numeric denominator remain
unestablished. The immutable packet specified at
`registry/w-trivia3-review.md:161` would decide the key questions: input
identities/flags, selected/filter membership, export shard/ordinal,
official key and overwrite order, and exact `qid_list` or explicit default.
Payload-derived preservation/equality attestations must be supplied by an
authorized producer; reading answers, official scorer execution and fresh
payload/network acquisition are outside this task.
