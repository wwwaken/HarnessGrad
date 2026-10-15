# TriviaQA metadata membership, scorer mapping, and execution-receipt search — w-trivia2

**Outcome: metadata review completed; execution-receipt outcome UNKNOWN; no withdrawal proposed.**
The declared schema lacks HumanAnswers and verification/domain flags. Published declarations disagree
about configuration membership and validation counts. No repeated inventory members were exposed.
Official scorer keys and its numeric denominator cannot be recovered from these declarations alone.
Evidence is enumerated below; no closure or production authorization follows.

## Evidence convention and boundary

`F` means the existing directory `tests/fixtures/hg_trivia2/`. A citation such as
`F/inventory.json:26` expands to that full in-repository path. Every request name below
has a full URL, observed HTTP status (or unobserved status), raw-body SHA-256,
verbatim excerpt, and body/receipt locator in `F/response-catalog.md`.
`views/*.json` are indented parsed views of exact `responses/*.body` bytes,
verified by `F/analyze.py:137`. JSON body hashes are of received bytes, not upstream
execution attestations. Requests use verified HTTPS, with transport failures preserved;
the acquisition commands and exact output are in `registry/w-trivia2-validation.txt`.

FOUND means the cited bytes/declaration/source were retrieved or inspected. ABSENT is
limited to an explicitly enumerated inventory or endpoint. UNKNOWN means the record
was not observable, was not searched, or requires information outside this review.
The inventory analysis consumes the exact revision's 150 tree entries, 142 sibling file
declarations, all twelve `dataset_info` schemas/split lists, and all eight `configs`
file-route declarations (`F/inventory.json:2`, `F/analyze.py:49`). It does not read
Parquet footers or payloads. These are **declared schemas and counts**, not measured
row coverage or verified on-disk schemas.

No question, answer, alias or gold payload row was read, printed, exported or summarized.
No scorer, acquired loader/converter, benchmark, model or GPU was executed. The fetched
pinned Hub card's example code fences are empty (`F/responses/hub-card-proxy-retry.body:854`).
The project's sample filenames appear only as metadata or documentation; sample bodies
were not fetched (`F/views/project-tree.json:75`,
`F/responses/project-readme-proxy.body:22`). Existing v2 and scorer/source identities
are read-only evidence (`data/datasets/triviaqa.py:91`, `F/source-identities.json:2`).
The bounded first-five custody packet remains governed by
`registry/dataset-blockers.json:1000`; its payload and packet were not used to answer
this metadata-only review.

## Part 1. Source-only membership and metadata review

### 1. HumanAnswers

**FOUND — answer declaration.** The pinned revision declares `answer` as a struct with
`aliases`, `normalized_aliases`, `matched_wiki_entity_name`,
`normalized_matched_wiki_entity_name`, `normalized_value`, `type`, and `value`.
For `rc.nocontext`, the verbatim declarations include `"name": "answer"`,
`"struct": [`, and `"name": "normalized_aliases"`, `"sequence": "string"`
(`F/views/hub-revision-final.json:257`). All twelve declared schemas have these
same field names (`F/inventory.json:88`). Acquisition:
`F/response-catalog.md:99` (HTTP 200, exact revision URL and digest).

**ABSENT — declared export schema and named membership only.** Neither `HumanAnswers`
nor `human_answers` is a declared field in any of the twelve schemas; there is no
HumanAnswers configuration, directory or split in the eight exported route/directory
inventories. Scope: all `cardData.dataset_info[*].features` recursively, all
`cardData.configs[*].config_name`, all their split routes, and all 150 exact-revision tree
paths. Reproduce with `python3 tests/fixtures/hg_trivia2/analyze.py --check`;
the normalized field-name absence is recorded at `F/inventory.json:390`, and complete
configuration/split names at `F/inventory.json:11` and `:398`.

**UNKNOWN — original absence, preservation, and redundancy.** No declared substitute
configuration/split establishes that HumanAnswers were empty, already represented by
normalized aliases, or preserved in another field. The candidate predecessor source
copies `answer["NormalizedAliases"]` and emits seven answer fields, without
HumanAnswers (`F/responses/predecessor-source-attempt2.body:237`), but that is source
behavior rather than evidence of execution or upstream answer values. The official
scorer explicitly combines `NormalizedAliases` with normalized optional `HumanAnswers`
(`tests/fixtures/triviaqa_upstream/evaluation/triviaqa_evaluation.py:76`). Consequently
the adapter docstring's claim “no human answers at all” (`data/datasets/triviaqa.py:132`)
is stronger than this metadata establishes. Settlement requires an authoritative
payload-free audit/receipt of the consumed input's HumanAnswers incidence, preservation
and normalized-set containment, or an independently authorized row comparison; neither
was performed here.

### 2. Domain / VerifiedEval / source membership

**FOUND — export inventory.** Eight directories and eight file routes exist, each with
train/validation/test. The following are structured metadata declarations, not distinct
question counts (`F/inventory.json:11`, `:26`, `:398`):

| Exported configuration/subtree | train | validation | test |
| --- | ---: | ---: | ---: |
| rc | 138384 | 17944 | 17210 |
| rc.nocontext | 138384 | 17944 | 17210 |
| rc.web | 76496 | 9951 | 9509 |
| rc.web.nocontext | 76496 | 9951 | 9509 |
| rc.wikipedia | 61888 | 7993 | 7701 |
| rc.wikipedia.nocontext | 61888 | 7993 | 7701 |
| unfiltered | 87622 | 11313 | 10832 |
| unfiltered.nocontext | 87622 | 11313 | 10832 |

The sibling file inventory agrees exactly with the tree's 142 files, and every one of
140 Parquet declarations is assigned once by the eight configs' routes
(`F/inventory.json:610`, `:615`). Current public viewer `/info` and `/splits`
also list these eight configs and their 24 splits (`F/inventory.json:637`,
`F/views/viewer-splits.json:2`); these are mutable service observations, not immutable
execution receipts. URLs/statuses/digests:
`F/response-catalog.md:103`,
`F/response-catalog.md:131`,
`F/response-catalog.md:135`.

**FOUND — two published disagreements, preserved.** The same pinned revision's
`dataset_info` lists twelve configs, adding `unfiltered.web`,
`unfiltered.web.nocontext`, `unfiltered.wikipedia`, and
`unfiltered.wikipedia.nocontext`. Those four each declare split names but no
`num_examples`; their counts are unknown, not zero
(`F/views/hub-revision-final.json:1025`, `:1125`, `F/inventory.json:20`, `:67`).
They have no exported directory, sibling files or file routes in the enumerated
tree/config/sibling scope. This is a twelve-declaration versus eight-export mismatch,
not four observed extra datasets. The historical `dataset_infos.json` instead records
zero counts for those four (`tests/fixtures/triviaqa_hub_codex225/historical_loader/dataset_infos.json:1`;
its exact observed identity is `F/source-identities.json:26`), a different declaration
that must not fill the pinned card's missing counts. The pinned card's prose table
states verbatim `|rc                  |138384|     18669|17210|` and
`|rc.nocontext        |138384|     18669|17210|`
(`F/responses/hub-card-proxy-retry.body:996`), whereas structured metadata says
`"num_examples": 17944` for their validation splits
(`F/views/hub-revision-final.json:180`, `:299`). Its prose table also lists only four
configurations (`F/responses/hub-card-proxy-retry.body:994`). No count was silently
corrected. Card URL/status/digest: `F/response-catalog.md:62`.

**FOUND — candidate source intentions, not executed membership.** The predecessor
declares eight builder configs and `self.sources = ["web", "wikipedia"] if source == "all" else [source]`
(`F/responses/predecessor-source-attempt2.body:132`, `:143`). It maps validation to
`"dev.json"` and unfiltered to `unfiltered-web-*` filenames (`:84`, `:91`), and says
verbatim `# there is no unfiltered version for the wikipedia subset` (`:115`).
The declared web+wikipedia counts sum to rc for each split, and context/no-context
counts match (`F/inventory.json:626`, `:631`). Arithmetic and source intentions do
not prove member identity, uniqueness, coverage, or which input was executed.
Source URL/status/digest: `F/response-catalog.md:111`.

**ABSENT — membership/verification declarations.** Across all twelve declared schemas,
`Domain`, `VerifiedEval`, `QuestionPartOfVerifiedEval`, and
`DocPartOfVerifiedEval` are absent (`F/inventory.json:390`). The declared
`question_source` and `entity_pages.doc_source` are strings rather than enumerated
Domain or verification flags (`F/views/hub-revision-final.json:203`, `:211`). The
exact-revision inventory contains only root `.gitattributes`, `README.md`, and Parquet
files; it has no separate row-ID/source-membership list or verified subset sidecar
(`F/inventory.json:622`, `F/responses/hub-tree-final.body:1`). Reproduce both named
scope searches with `python3 tests/fixtures/hg_trivia2/analyze.py --check`.

**UNKNOWN — actual members and official filtering.** Source-specific names and counts
cannot establish which exported IDs belong to original Web/Wikipedia or verified eval.
The official helper requires top-level `Domain` and `VerifiedEval`, conditionally
question verification and Web document verification flags
(`tests/fixtures/triviaqa_upstream/utils/dataset_utils.py:8`, `:30`, `:40`). A
published immutable, payload-free list binding original source/verification flags and
scorer keys to exported IDs would settle this without answer rows. Such a list was
not exposed in the named export inventory; project archives and row IDs were not read.

### 3. Duplicates at the inventory level

**ABSENT — repeated metadata members, within the enumerated scope.** No duplicate tree
paths, sibling paths, config names, per-config split names, schema field paths, raw
JSON object keys, or multiply assigned Parquet paths were exposed. No file Git blob
OID, declared LFS OID, or directory OID repeats within the exact-revision inventory
(`F/inventory.json:603`, `:644`). Scope and exact command are the `analyze.py --check`
inventory search above, covering all 150 entries/all 142 siblings/all twelve schema
declarations/all eight route maps, plus raw JSON object keys in the tree, revision,
and viewer-info responses. Grouping is by full path or declared content identity;
common split labels across different configurations are not duplicate full paths.

**UNKNOWN — row/key duplicates and cross-config overlap.** No question-ID/member list
is present in the inspected metadata, so duplicate question IDs, repeated scorer keys,
cross-source/cross-config overlap, writer deduplication, and answer agreement between
repeated keys remain unobserved (`F/inventory.json:641`). Equal counts do not prove
equal members. The official dictionary construction would overwrite repeated Wikipedia
QuestionId or Web question-document keys (`tests/fixtures/triviaqa_upstream/utils/dataset_utils.py:9`,
`:22`). The candidate loader yields filename-plus-question-ID keys
(`F/responses/predecessor-source-attempt2.body:327`); this cannot attest actual writer
behavior. A payload-free key inventory/deduplication audit with an export binding
would settle incidence; no row-based duplicate detection was attempted.

### 4. Scorer-key mapping

**FOUND — established pinned source, inspected rather than executed.**
Official source identity is the existing pin
`mandarjoshi90/triviaqa@ca43b5820b107f3970cf4b7d67f7db7a98117b79`,
`evaluation/triviaqa_evaluation.py`, SHA-256
`51785a3bc2e02a8f1ebf9db3aa18834c6a5daa5089ee5d435c99e0babf4be682`
(`tests/fixtures/triviaqa_upstream/provenance.json:4`, `:19`,
`F/source-identities.json:8`). The local v2 identity and reference are unchanged
(`data/datasets/triviaqa.py:91`). Mapping follows the source, not canonical-value
inference:

| Consumer | Declared export field / required key | Source and result |
| --- | --- | --- |
| Local adapter `_gold` | `row.answer.normalized_aliases` → internal `gold.accepted`; optional `answer.human_answers`/`HumanAnswers` are supported by code but absent from all declarations | `data/datasets/triviaqa.py:137`, `:259`, `:268`; schema `F/views/hub-revision-final.json:257`. |
| Local `score` | Reads internal `gold.accepted`, not raw `answer.value` or `answer.aliases` | `data/datasets/triviaqa.py:162`; `gold.value` is diagnostic text (`:173`). `_gold` derives that label from `answer.value` (`:261`), which is not the comparison alias set. |
| Official answer extraction | Reads each `datum['Answer']`; required answer key `NormalizedAliases`; optional `HumanAnswers` | `tests/fixtures/triviaqa_upstream/utils/dataset_utils.py:9`, `:22`; `tests/fixtures/triviaqa_upstream/evaluation/triviaqa_evaluation.py:77`. Raw lowercase Hub `answer.normalized_aliases` cannot be passed unchanged to this function. |
| Official Wikipedia key | Required original `Domain == 'Wikipedia'`, `Data`, `QuestionId`, `Answer`; prediction dictionary indexed by QuestionId | `tests/fixtures/triviaqa_upstream/utils/dataset_utils.py:8`; `tests/fixtures/triviaqa_upstream/evaluation/triviaqa_evaluation.py:107`, `:118`. Hub `question_id` supplies a candidate name mapping only, not a verified unique official key inventory. |
| Official Web key | For non-Wikipedia Domain, each EntityPages/SearchResults page requires `Filename`; key is `'{}--{}'.format(qid, doc_name)` | `tests/fixtures/triviaqa_upstream/utils/dataset_utils.py:14`, `:19`. Hub nested `filename` names exist, but Domain is missing and actual no-context documents are unobserved. |
| Official CLI/filter envelope | Requires `VerifiedEval`, `Domain`, `Data`, `Version`; when VerifiedEval is true, requires question flags and, for Web, document flags | `tests/fixtures/triviaqa_upstream/utils/dataset_utils.py:40`, `:43`, `:30`; `tests/fixtures/triviaqa_upstream/evaluation/triviaqa_evaluation.py:149`. Export declarations provide no such envelope or flags (`F/inventory.json:390`). |

In the table, abbreviated `evaluation/triviaqa_evaluation.py` means
`tests/fixtures/triviaqa_upstream/evaluation/triviaqa_evaluation.py`.
The comparison functions do not consume export `answer.aliases`, `normalized_value`,
`matched_wiki_entity_name`, `normalized_matched_wiki_entity_name`, or `type`;
the official alias function reads only NormalizedAliases and optional HumanAnswers
(`tests/fixtures/triviaqa_upstream/evaluation/triviaqa_evaluation.py:76`). They do not
grade `question`, `question_source`, document text/title/url/rank/description, or the
canonical `value`; Web filenames and question IDs instead participate in key construction
(`tests/fixtures/triviaqa_upstream/utils/dataset_utils.py:19`). The local adapter
projects only `question` and `answer`, so it cannot reconstruct official Web document
keys from its current projection (`data/datasets/triviaqa.py:195`, `:240`).

**UNKNOWN — full compatibility.** Renaming lowercase fields could satisfy some
structural reads, but does not restore omitted human answers, Domain/verification
selection, document-key grouping, or unique-key correspondence. Whether canonical
values belong to accepted aliases is a row-level property and was not verified.
Schema presence alone does not verify per-row nonempty aliases; local `_gold` rejects
an empty accepted list (`data/datasets/triviaqa.py:262`). No scorer-key equivalence or
official leaderboard equivalence is claimed.

### 5. Denominator and multiple-alias aggregation

**FOUND — official algorithm.** `evaluate_triviaqa` defaults `qid_list` to
`ground_truth.keys()`; its denominator is `len(qid_list)`, not number of prediction
entries, raw export rows, or aliases. Each key contributes max EM over the alias set
and independently max F1; totals are multiplied by 100 and divided by this denominator
(`tests/fixtures/triviaqa_upstream/evaluation/triviaqa_evaluation.py:53`, `:104`,
`:120`, `:129`). Missing predictions remain in the requested-key denominator and
contribute zero (`:107`). An explicitly supplied qid_list determines its own length;
the function does not deduplicate that list (`:106`). The default key dictionary
collapses repeated original keys by overwrite, and verified filtering happens before
that construction (`tests/fixtures/triviaqa_upstream/utils/dataset_utils.py:9`, `:22`, `:40`).
Human answers add normalized alternatives, not extra denominator terms
(`tests/fixtures/triviaqa_upstream/evaluation/triviaqa_evaluation.py:77`). Empty ground-truth lists make the official
`max` fail; local alias max returns zero and the local gold builder refuses an empty
accepted set (`tests/fixtures/triviaqa_upstream/evaluation/triviaqa_evaluation.py:58`, `data/datasets/triviaqa.py:155`, `:262`).

**FOUND — local metric limit.** v2 returns per-task 0/1 reward based on max normalized
EM across every entry of `gold.accepted`, without an alias cap in the comparison
(`data/datasets/triviaqa.py:157`, `:162`, `:269`). Its `accepted[:20]` is output
diagnostic text only (`:171`). This source has no corpus-level denominator or F1
aggregation; a run aggregation would require a measured task/trial receipt outside
this review. The declared rc.nocontext validation count is 17,944
(`F/inventory.json:34`), with the conflicting prose count retained above. Neither
count is automatically the denominator of the official evaluator or a measured run.

**UNKNOWN — numeric official denominator and headline equivalence.** A Wikipedia
denominator needs the selected/filtered distinct QuestionId keys; a Web denominator
needs distinct selected question-document keys. Combining declared 9,951 Web and
7,993 Wikipedia validation **rows** to 17,944 does not measure those keys
(`F/inventory.json:626`, `tests/fixtures/triviaqa_upstream/utils/dataset_utils.py:17`).
Settlement requires an immutable, payload-free inventory of the original selected
Domain/VerifiedEval/filtered keys, its export-ID mapping, duplicate policy, and exact
requested qid_list, or a separately authorized row audit. No such inventory was
exposed in the searched export metadata. No denominator was inferred from the
bounded operator first-five eval selection, and no scorer was executed.

## Part 2. Enumerated authoritative execution-receipt search

The search targets a receipt binding **the pinned export** to the code actually
executed, source/license hashes, runtime/writer versions, and consumed input
revision/hashes. The list below is its scope, not a claim about every upstream
service. All response bodies cited here are retained under F. Exact GETs are in
`F/plan-1.json` through `F/plan-10-history-retry.json` (including the separately named
Hub/GitHub plans), with failures retained under fresh request names; commands/output
are in validation. No mutable pointer, opaque ETag, file listing, identical blob,
converter name or plausible ancestry is treated as an execution receipt.

| Enumerated authoritative scope | FOUND / ABSENT / UNKNOWN and evidence |
| --- | --- |
| Hub `/refs`: all returned branches/tags/converts | **FOUND** `main`, `script`, `refs/convert/parquet`; **ABSENT** tags in this response (`"tags": []`). Verbatim ref `"ref": "refs/convert/parquet"`, target `bd67746ffd85804fdc6b2ec5b00222ea26f8117e` (`F/views/hub-refs-proxy-retry.json:2`, `:18`); URL/200/digest `F/response-catalog.md:96`. Target pointers alone do not attest execution. |
| Pinned export revision, all 150 recursive tree entries, card YAML/schema/count/file-route metadata | **FOUND** declarations and eight directories; **ABSENT** a standalone execution/build/job/attestation file within these 142 files: root files are README/.gitattributes and the other 140 are Parquet (`F/inventory.json:5`, `:622`). Exact inventory command is `python3 tests/fixtures/hg_trivia2/analyze.py --check`. URLs/200/digests `F/response-catalog.md:99`, `F/response-catalog.md:103`, `F/response-catalog.md:62`. No runtime/writer/executed-input binding appears in these inspected declarations. |
| Exact pinned `/raw/.../dataset_infos.json` and predecessor same path | **ABSENT at these two exact URLs**, HTTP 404 body verbatim `Entry not found`; `F/response-catalog.md:66`, `F/response-catalog.md:92`. This does not mean dataset_info is absent from the card; it is present there. |
| Main export history at pinned revision, conversion history at PR's last commit, all PR #8 events | **FOUND** 17 main-history entries, 27 conversion-history entries, and PR events; no pagination Link supplied by these responses (receipts). Verbatim titles `"title": "Convert dataset to Parquet (#8)"` and `"title": "Delete data folder"`; PR's comment is `"raw": "Convert dataset to Parquet."` (`F/views/hub-history-proxy-retry.json:4`, `F/views/hub-conversion-history.json:4`, `F/views/hub-pr8-success.json:66`). **ABSENT** execution-receipt link/runtime/writer/input attestation in these inspected messages/comment/events. URLs/200/digests `F/response-catalog.md:79`, `F/response-catalog.md:65`, `F/response-catalog.md:90`. This extends the prior review's bounded search without re-proving ancestry. |
| Export-path and loading-script path-history routes `/commits/<pin>/rc.nocontext` and `/commits/<pin>/trivia_qa.py` | **FOUND** HTTP 404 error `"error":"Sorry, we can't find the page you are looking for."`; **UNKNOWN** path-specific API history because these exact routes do not expose it. `F/response-catalog.md:70`, `F/response-catalog.md:86`. General main/conversion histories and historical root listings are inspected separately; unsupported routes are not an absent-history claim. |
| Root snapshots at every distinct commit returned by the main/conversion histories (28 named revisions) | **FOUND/UNKNOWN per request** in `F/history-root-inventory.json:1`; individual failures do not negate a successful retry or the separately retrieved recursive listing at the same revision. Exact scope is `F/plan-9-history-roots.json:1`, failed-root retries `F/plan-10-history-retry.json:1`. Loader and dataset-info path/OID changes can be inspected in returned roots; failed roots remain UNKNOWN. Root listings are not path-specific commit diffs or execution receipts. Old subtree contents/payloads were not fetched. |
| Predecessor recursive tree/source and initial-conversion recursive tree | **FOUND** predecessor source and tree; source import `import datasets`, builder label `datasets.Version("1.2.0")` (`F/responses/predecessor-source-attempt2.body:24`, `:129`); source/tree URL/200/digests `F/response-catalog.md:111`, `F/response-catalog.md:112`. The initial-conversion recursive tree was retrieved (HTTP 200; `F/response-catalog.md:107`); this is output/source presence, not execution attestation. Unpinned library import/builder label cannot identify an installed runtime/writer. |
| Generated ref pinned to observed `bd67746...`: revision, recursive tree, returned history | **FOUND** generated file inventory and history; verbatim title `"title": "Update parquet files"`, author name `"user": "parquet-converter"` (`F/views/generated-history-attempt5.json:4`, `:8`). Revision/tree/history URLs/200/digests `F/response-catalog.md:74`, `F/response-catalog.md:12`, `F/response-catalog.md:11`. **ABSENT** an execution receipt in these inspected returned records. No code digest/runtime/writer/input identity binding this generated ref to the 2024 pinned export was recovered. Current generated files are a separate observed revision; no replacement export was inferred. |
| datasets-server `/info`, `/splits`, `/is-valid` for this named dataset | **FOUND** schema/split/validity metadata; `/info` says `"pending":[],"failed":[],"partial":false`, not a historical build receipt. `F/response-catalog.md:131`, `F/response-catalog.md:135`, `F/response-catalog.md:138`. **ABSENT** historical executed converter/runtime/writer/input linkage in these returned bodies; current state flags cannot certify the old export's execution. |
| datasets-server `/status` and `/pending-jobs`; Hub `/api/jobs/mandarjoshi` | **FOUND** 404 `Not Found` for the two viewer routes, and 401 `{"error":"Invalid username or password."}` for Hub Jobs. **UNKNOWN** job/build records behind authentication or an undiscovered supported historical-build endpoint. `F/response-catalog.md:136`, `F/response-catalog.md:134`, `F/response-catalog.md:82`. Unauthorized/unsupported endpoints are not proof no job exists. |
| Original GitHub project pinned/current recursive file trees; converter and aggregation script histories | **FOUND** pinned/current tree listings (`"truncated": false`), `utils/convert_to_squad_format.py` source and its 2 history entries, `evaluation/triviaqa_evaluation.py`'s 3 history entries, `utils/dataset_utils.py`'s 2 history entries; no pagination Link supplied. `F/response-catalog.md:130`, `F/response-catalog.md:121`, `F/response-catalog.md:117`, `F/response-catalog.md:119`, `F/response-catalog.md:114`, `F/response-catalog.md:123`. Converter source calls `convert_to_squad_format(args.triviaqa_file, args.squad_file)` (`F/decoded/project-converter.py:110`); it is a SQuAD converter, not proof of the Hub Parquet builder. **ABSENT** a Hub execution receipt in these named returned listings/source/history records. |
| Original GitHub project `/releases?per_page=100`, `/tags?per_page=100`, `/git/matching-refs/tags/`, `/actions/runs?per_page=100`, `/actions/artifacts?per_page=100` | **ABSENT within these public endpoint lists**: verbatim `[]`, `[]`, `[]`, `{"total_count":0,"workflow_runs":[]}`, `{"total_count":0,"artifacts":[]}` (HTTP 200; no pagination Link). `F/response-catalog.md:127`, `F/response-catalog.md:129`, `F/response-catalog.md:128`, `F/response-catalog.md:113`, `F/response-catalog.md:116`. Empty current public lists cannot establish whether private/deleted/expired artifacts ever existed. |
| Original project pinned/current README; official ACL 2017 paper BibTeX and artifact-page anchor inventory | **FOUND** README paper/download links and paper record DOI `10.18653/v1/P17-1147` (`F/responses/project-readme-proxy.body:5`, `:8`, `:32`; `F/responses/paper-record.body:15`). URLs/200/digests `F/response-catalog.md:125`, `F/response-catalog.md:124`, `F/response-catalog.md:110`, `F/response-catalog.md:109`. **ABSENT** an export-execution receipt/link in these inspected README/BibTeX records and all 46 extracted artifact-page anchor URLs (`F/paper-link-inventory.json:1`; reproduce `python3 tests/fixtures/hg_trivia2/build_evidence.py`). Paper PDF, arXiv body, project homepage body, and payload-linked archives were not inspected and remain UNKNOWN. |
| Original project `/triviaqa/data/` index | **FOUND** HTTP 403 body excerpt `<title>403 Forbidden</title>`; **UNKNOWN** index contents/artifacts. `F/response-catalog.md:122`. No archive, row body, supplementary paper payload or private maintainer artifact was downloaded. |

### Standing-limit argument

**UNKNOWN; the standing-limit withdrawal rule is not supported by this search.**
The enumerated accessible public records expose ancestry, declarations, a generated
ref, candidate source and paper/release metadata, but no immutable receipt binding
the pinned Hub export to executed code, source/license hashes, runtime/writer versions
and consumed input revision/hashes (table citations above). That supports absence
within the named inspected responses, not the universal claim that no further work
in this repository can obtain the receipt. Authenticated Hub job/build records,
unsupported historical-build/path-history interfaces, historical root snapshots still unavailable after the recursive-listing successes and retries, the denied original data index and uninspected original maintainer/job
artifacts remain UNKNOWN. A supported historical build/job endpoint or an original
immutable maintainer artifact carrying the complete binding, or authoritative evidence
that these records were never captured/are no longer recoverable, is still missing.
Re-running a converter now would not establish what ran then; matching a predecessor
blob, naming an author/converter, using an ETag/ref pointer, or comparing file inventories
would not substitute for this receipt. Therefore the proposal preserves the execution
obligation and sets `withdrawal_entry` to null.

## Integration proposal and validation

`registry/proposals/w-trivia2.json:1` is a proposal for parent review, not a registry
mutation. It retires the already completed general metadata review from next_action
while explicitly retaining the unestablished HumanAnswers preservation/redundancy,
source/verification/key/duplicate/denominator linkage and immutable execution receipt.
It preserves v2/historical identities and the operator's bound first-five eval-side
custody; it imposes no withdrawn shared gate or new production authorization.

`registry/w-trivia2-validation.txt` records acquisition commands/output, byte/view and
inventory integrity checks, exact blocker-checker output, owned diff checks, every
committed file's size, and unverified items. The checker output is
`{"valid": true, "datasets": 28, "shared_blockers": 0, "historical_records": 11, "production_authorized": false}`.
The review/proposal/fixture additions cannot change registry semantics because
`registry/dataset-blockers.json` was not edited; the parent must review and apply any
proposal separately. No frozen receipt, registry or journal was edited.
