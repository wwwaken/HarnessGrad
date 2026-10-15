# w-fevconv — FEVER producing conversion and metric comparability

**ABSENT, bounded search:** no record of the execution that produced the installed `valid.jsonl` was retrieved in the enumerated scopes below. This is a local search result, not proof that no producer or upstream record exists. **FOUND, source conclusion:** converting a conjunction to singleton alternatives changes the pinned FEVER strict predicate for partial evidence. There are 1,400 exposed installed non-NEI rows, including all 1,395 rows previously identified as containing an original-insufficient singleton; 31 exported conjunctions exceed five distinct pairs. The precise predicates and observation limits appear below. Search outputs and commands are preserved in `registry/w-fevconv-validation.txt` (sections `Reproduction programs`, `Observed search outputs`, and `Exact shell-command ledger`). No scorer was executed by this worker.

## 1. Producing-conversion execution provenance

### FOUND — retained custody and correspondence

The existing record establishes installed/export custody, 15,935 row/task digests, the imposed 10,559-train / 5,376-eval inventory, and first-five selected-input custody (`registry/dataset-blockers.json:348`; `tests/fixtures/hg_wsel/fever.json:1`). None is reopened by this proposal. The historical w-jc2 observations are reproduced verbatim in appendix O: installed SHA-256 registry/w-fevconv-receipts.md:522 (O:5); original public dev SHA-256 registry/w-fevconv-receipts.md:524 (O:7); all 15,935 claim/label/verifiable agreements and 9,525 complete-group matches registry/w-fevconv-receipts.md:528 (O:11); normalization registry/w-fevconv-receipts.md:548 (O:31); 51 absent original alternative groups for 42 represented non-NEI IDs registry/w-fevconv-receipts.md:545 (O:28). These are prior observations, not a new original-dev audit. The installed digest and structural counts were independently reread using `python3 /mnt/20t/xubuqiang/hg-work/fevconv/parse-installed.py`; its complete output is in validation.

### FOUND — readable declarations and source custody, not producing receipts

Pinned scorer: `sheffieldnlp/fever-scorer@4801615100fbf6327f8e99b5dbaefe5dd890e869`, upstream path `src/fever/scorer.py`. Read with `git show 030a2e4389e2cf049a98741d27ca5875b6829f58:tests/fixtures/hg_e1_review/fever-upstream-scorer.py`; exact bytes are in appendix S, with acquisition URL/revision in appendix CS. SHA-256 `fa12eaab2c88208f990948fc5d533ad4f91a6b8f48640f29317d1f00ab410ac9`, Git blob `ecae63dcd900f84c498ad0f2e5d7dd06e305e329` (exact command/output: validation `source-packet.stdout`). The registry records empty tags/releases and setup `0.0.0`; no named release is claimed (`registry/dataset-blockers.json:348`).

Readable producer source: `copenlu/fever-adversarial-attacks@aaa126ec4f3cf7163f69b82a0a0976d2579a04a6`, upstream path `scripts/create_nli_dataset.py`. Read with `git show 030a2e4389e2cf049a98741d27ca5875b6829f58:tests/fixtures/hg_e1_review/fever-create-nli-dataset.py`; exact bytes are appendix C, acquisition URL/revision appendix CC. SHA-256 `09054c04a53eb5f3f035d94fd2fe8a271a57bf69c5768eadd0535497f8cec884`, Git blob `7a82da41e51c9d41ec259f67f9230f7c3f2917e5` (validation `source-packet.stdout`). This revision is the inspected source revision, **not** the authenticated producing revision.

README commands reference an example training input/output, not the installed validation blob (registry/w-fevconv-receipts.md:817 (R:41), registry/w-fevconv-receipts.md:819 (R:43)). The README declares Papelo retrieval and merge (registry/w-fevconv-receipts.md:821 (R:45), registry/w-fevconv-receipts.md:824 (R:48), registry/w-fevconv-receipts.md:826 (R:50), registry/w-fevconv-receipts.md:828 (R:52)); it supplies no observed interpreter/environment or hash-bound NEI execution receipt. Extraction skips NEI (registry/w-fevconv-receipts.md:372 (C:54)), loops over original groups (registry/w-fevconv-receipts.md:374 (C:56)), normalizes page names (registry/w-fevconv-receipts.md:378 (C:60)), can omit a missing sentence (registry/w-fevconv-receipts.md:381 (C:63)), discards a group on a missing page (registry/w-fevconv-receipts.md:383 (C:65)), and copies original fields before replacing evidence (registry/w-fevconv-receipts.md:390 (C:72)). These branches are possible decisions; their historical execution is UNKNOWN.

Two additional readable source bodies were recovered from the prior worker's already-recorded tool output at `/home/xubuqiang/.codex/sessions/2026/10/15/rollout-2026-10-15T13-16-26-01a13dfd-82c2-7762-8d0b-e89bba2ef504.jsonl:71`, without rerunning that command. `source-packet.py` strips the original displayed line-number prefixes and recomputes bytes/blob hashes. The merge source (`scripts/merge_nli_files.py`, appendix M) reproduces blob `2191816140b9ec0738a305eb09b8f16f58d497dd`; the NEI source (`scripts/aggregate_papelo_nei.py`, appendix N) reproduces blob `dc75b530850d36bb9c706c9a4ca9d7305c91a6e0`. Both agree with the prior pinned-tree observations (registry/w-fevconv-receipts.md:564 (O:47), registry/w-fevconv-receipts.md:570 (O:53); exact reconstruction/hashes in validation `source-packet.stdout`). Merge filters `annotation != "N/A"` (registry/w-fevconv-receipts.md:422 (M:24), registry/w-fevconv-receipts.md:430 (M:32)), then seeds/shuffles (registry/w-fevconv-receipts.md:443 (M:45)); NEI aggregation uses the first retrieved sentence (registry/w-fevconv-receipts.md:501 (N:49)). This recovers declarations, not execution. No ID-assignment or validation partition receipt follows from these source files.

### ABSENT — enumerated local execution-record search

For this finding, a **producing receipt** must record the execution producing the bound installed/export bytes and identify its executable revision/invocation/environment and input/output linkage. A README command, an acquisition receipt, a local audit, a selected export, or a matching source blob does not qualify. No qualifying record was retrieved. Each required field is searched-ABSENT as an authenticated field of that producing execution: converter revision; invocation; interpreter/environment; ID assignment; split/filter/omission decisions; NEI input receipt. Their actual historical values remain UNKNOWN.

The exact search expression was:

```text
fever|copenlu|create_nli_dataset|aggregate_papelo_nei|merge_nli_files|ae61c5b6cb11eafcc7d6c33069c68dd5c848f91f|5da0ccc0ccf77f974611de13f8aac6f78c6bba6293912835099eb6029baa85d9
```

`python3 /mnt/20t/xubuqiang/hg-work/fevconv/search.py` enumerated every regular file under the following explicit roots with `os.walk` (without following directory symlinks), wrote `scope-files.jsonl`, and ran `rg -l -i --hidden --no-ignore --glob '!.git/**' <expression> <root>` on each existing root. Counts are exact observed enumeration counts; session files were changing during work, so the task's earlier 722-file figure is not treated as this scan's count. All walk-error lists and rg stderr were empty. Files inside archives/object stores were additionally decoded below; raw rg absence alone is not archive-content absence.

| Scope root | Enumerated regular files | Bytes | Matching files / rg exit |
|---|---:|---:|---:|
| `/home/xubuqiang/.codex/sessions` | 732 | 3051047665 | 313 / 0 |
| `/home/xubuqiang/.codex/archived_sessions` | 5 | 417303 | 1 / 0 |
| `/home/xubuqiang/.codex/history.jsonl` | 1 | 3314721 | 0 / 1 |
| `/home/xubuqiang/.bash_history` | 1 | 74693 | 0 / 1 |
| `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive` | 168 | 1554930 | 1 / 0 |
| `/mnt/20t/xubuqiang/Study/hg-backup-20261014` | 3527 | 25305309 | 0 / 1 |
| `/mnt/20t/xubuqiang/Study/hg-backup-20261014-pre-rewrite` | 3690 | 26459081 | 0 / 1 |
| `/mnt/20t/xubuqiang/Study/hg-logs` | 6 | 100998 | 0 / 1 |
| `/mnt/20t/xubuqiang/harnessgrad_work` | 112 | 238140 | 0 / 1 |
| `/mnt/20t/xubuqiang/Study/harnessgrad_work` | 5626 | 44684992 | 0 / 1 |
| `/mnt/20t/xubuqiang/Study/harnessgrad_cli` | 1 | 3820 | 0 / 1 |
| `/mnt/20t/xubuqiang/Study/HarnessGrad-real-work-20261117` | 32 | 76477 | 0 / 1 |
| `/mnt/20t/xubuqiang/Study/HarnessGrad-real-work-20261117c` | 33 | 104375 | 0 / 1 |
| `/mnt/20t/xubuqiang/hg-wt/w-fevconv/runs` | 0 | 0 | 0 / path absent |
| `/mnt/20t/xubuqiang/hg-wt/w-fevconv/runs_discarded_20260929-004559` | 0 | 0 | 0 / path absent |
| `/mnt/20t/xubuqiang/hg-wt/w-fevconv/.harnessgrad-state` | 0 | 0 | 0 / path absent |
| `/mnt/20t/xubuqiang/hg-wt/w-fevconv/tests/fixtures` | 613 | 4525830 | 20 / 0 |
| `/mnt/20t/xubuqiang/hg-census` | 64859 | 420364891 | 10 / 0 |

Total unique matching files: 345 (`search.stdout`). Session JSON objects were decoded by `inspect-sessions.py` to retain actual call/output roles and `file:line` locations in `session-hits.jsonl`; broad matching context is not classified as execution. Concrete converter-name calls retrieved the scripts or authored/checksummed audit files: acquisition `/home/xubuqiang/.codex/sessions/2026/10/15/rollout-2026-10-15T01-50-24-01a13b89-6d3d-76d1-81e5-159483b0da8b.jsonl:309`; merge/NEI acquisition `/home/xubuqiang/.codex/sessions/2026/10/15/rollout-2026-10-15T13-16-26-01a13dfd-82c2-7762-8d0b-e89bba2ef504.jsonl:55`; source display at that same file's line 71. None records producing `valid.jsonl`. History and shell history yielded zero matching files (scope table). Remaining non-session matches were inventories/source/selection records and unrelated FEVER references; census matches were in Musique traces (`candidate-files.txt`, exact inventory in validation).

Because run directories are absent in the assigned worktree, their existing main-checkout counterparts were additionally searched **read-only** with `GIT_OPTIONAL_LOCKS=0 python3 /mnt/20t/xubuqiang/hg-work/fevconv/main-readonly-search.py`; no main-checkout file was modified:

| Explicit read-only root | Files | Bytes | Matching files / rg exit |
|---|---:|---:|---:|
| `/mnt/20t/xubuqiang/Study/HarnessGrad/runs` | 11886 | 1669692534 | 2 / 0 |
| `/mnt/20t/xubuqiang/Study/HarnessGrad/runs_discarded_20260929-004559` | 987 | 2393498 | 0 / 1 |
| `/mnt/20t/xubuqiang/Study/HarnessGrad/.harnessgrad-state` | 3 | 15 | 0 / 1 |

The two matches are `runs/loop-flash-base/round0_traces/mteb-retrieve.jsonl` and `runs/loop-flash-base/progress/round-0/traces/mteb-retrieve.trial1.jsonl` beneath that exact read-only root, not producing-conversion receipts (`main-readonly-search/candidate-files.txt`). The only `.tar.gz` enumerated there, `runs/local-screen-1/export/local-screen-1-traces.tar.gz`, was decoded in memory: 20 members, zero matching members (`embedded-search.stdout`). The evidence archive's two ZIPs were decoded: `codex/104/receipt/appworld-actor-protocol/receipt.zip`, 18 members; `codex/105/receipt/loop-robustness/receipt.zip`, 30 members; zero matching members in both (`backup-search.stdout`).

Repository history was searched **from this worktree**, without ref mutation:

```text
git log --all --format=fuller --name-only
git log --all --format='%H %s' -Sfever_gold_evidence --
git log --all --format='%H %s' -Screate_nli_dataset --
git log --all --format='%H %s' -Smerge_nli_files --
git log --all --format='%H %s' -Saggregate_papelo_nei --
git log --all --format='%H %s' -Soriginal_id --
git log --all --format='%H %s' -Svalid.jsonl --
git stash list
git reflog --all --format='%H %gd %gs'
git cat-file --batch-all-objects --batch-check
```

Exact outputs are recorded by `git-search.py` / `git-search.stdout` and the validation ledger: log 91,932 lines; pickaxe counts 17, 5, 8, 8, 20, 67 lines respectively; stash empty; reflog 109 lines. All 23,773 enumerated objects comprised 17,492 blobs, 5,561 trees, 720 commits. `git cat-file --batch` decoded all 18,212 blobs/commits; 847 objects matched (839 blobs / 8 commits). The retrieved FEVER records include source acquisition and correspondence, not a producing execution receipt. Historical packets cited with `git show <revision>:<path>` are deliberately revision-qualified because those paths were removed from the current tree; the exact relevant content is copied into this existing report's appendices.

Both backup object stores were decoded with `git --git-dir=<enumerated-backup>/dot-git cat-file --batch-all-objects --batch-check` and `--batch`: `hg-backup-20261014` had 2,151 blobs / 1,670 trees / 387 commits, 112 matching objects; `hg-backup-20261014-pre-rewrite` had 2,230 blobs / 1,725 trees / 406 commits, 125 matching objects. No producing-conversion receipt was retrieved (`backup-search.py` and exact `backup-search.stdout`; hit contents retained in scratch). All 145 embedded `.git` directories enumerated inside the named work/archive directories and read-only run roots were separately decoded: 1,033 objects, zero matching objects, zero errors (`embedded-search.py`, `embedded-git-results.json`, `embedded-search.stdout`). This avoids treating compressed Git objects as searchable plaintext.

### UNKNOWN — search limits and historical execution

This result covers the named file/object/member inventories and expression, not the whole machine or undocumented credentials/accounts. Unfollowed directory symlink targets, deleted files/objects, unenumerated directories, upstream private logs, and records using none of the search terms are UNKNOWN. Active transcripts can grow after enumeration. No historical producing interpreter, UUID-style export-ID algorithm, chosen validation split, missing-group decision, Wikipedia input or Papelo NEI input receipt is authenticated. Identical bytes and plausible ancestry do not turn any declaration into an execution receipt (source behavior above; prior `producer_revision_bound_to_export: null` registry/w-fevconv-receipts.md:656 (O:139)).

## 2. Flat conjunction versus singleton alternatives — source analysis only

### FOUND — exact predicates and representation boundary

The producer emits one row for each original group, storing its available sentence triples in a flat list (registry/w-fevconv-receipts.md:374 (C:56), registry/w-fevconv-receipts.md:375 (C:57), registry/w-fevconv-receipts.md:382 (C:64), registry/w-fevconv-receipts.md:390 (C:72), registry/w-fevconv-receipts.md:391 (C:73), registry/w-fevconv-receipts.md:392 (C:74)). Its conjunction meaning is the original group. The current local converter explicitly makes `groups = [[item] for item in groups]` when the flat-list branch matches (`data/scaffolds/qa/evidence_scorers.py:158`–`:164`, at base `eada00fc072d7006fb08cf7f4a750dbaa1437174`). It converts triple line numbers with `int()` and compares page/line membership in the first five predictions (`data/scaffolds/qa/evidence_scorers.py:156`–`:166`). This source conversion is the singleton behavior being compared; it is not the producer's documented conjunction conversion.

The pinned upstream scorer requires lists of `(string, int)` predictions (registry/w-fevconv-receipts.md:163 (S:3), registry/w-fevconv-receipts.md:174 (S:14), registry/w-fevconv-receipts.md:178 (S:18)), compares uppercase labels (registry/w-fevconv-receipts.md:182 (S:22)), extracts `[e[2], e[3]]` from each **nested group of four-field records** (registry/w-fevconv-receipts.md:197 (S:37), registry/w-fevconv-receipts.md:199 (S:39)), requires every sentence of one group inside the prediction prefix (registry/w-fevconv-receipts.md:201 (S:41)), and exempts correctly labelled NEI (registry/w-fevconv-receipts.md:205 (S:45)). `fever_score` defaults to five pairs (registry/w-fevconv-receipts.md:266 (S:106)) and passes that bound into strictness (registry/w-fevconv-receipts.md:292 (S:132)). Calling `is_strictly_correct` alone with its default `None` does not impose five (registry/w-fevconv-receipts.md:186 (S:26), registry/w-fevconv-receipts.md:193 (S:33)). This analysis uses the headline wrapper's five-pair default, not an invented helper default.

Flat triples cannot be passed directly to that upstream implementation as though it understood their shape: it indexes annotation-style nested records (registry/w-fevconv-receipts.md:199 (S:39)). For a valid source comparison, translate each pair `(page, int(line))` into `[null, null, page, int(line)]`; either place all records in **one group** (conjunction) or put each record in its **own group** (singletons). No translation or scorer was executed here. Pair normalization for the structural inventory is NFC-page / integer-line as in w-jc2 (registry/w-fevconv-receipts.md:548 (O:31)); raw arbitrary page normalization equivalence is not claimed.

Let `G` be the distinct normalized pairs of one exported non-NEI row, and `P5` the first five predicted pairs, with correct label and well-formed supplied predictions. Substituting the two groupings into the pinned source gives:

```text
conjunction strict pass  <=> G is a subset of P5
singleton strict pass    <=> G intersects P5
strict disagreement      <=> 0 < |G intersect P5| < |G|
```

The equivalence follows directly from the outer group loop and inner `all` (registry/w-fevconv-receipts.md:197 (S:37), registry/w-fevconv-receipts.md:201 (S:41)). Therefore singleton conversion cannot decrease this row's strict predicate relative to its **same exported group**; it can increase it when the label is correct and evidence is a nonempty proper subset. Wrong labels fail both (registry/w-fevconv-receipts.md:190 (S:30), registry/w-fevconv-receipts.md:210 (S:50)); correctly labelled NEI passes both (registry/w-fevconv-receipts.md:205 (S:45)). Pairs after position five cannot repair an incomplete prefix (registry/w-fevconv-receipts.md:201 (S:41), registry/w-fevconv-receipts.md:266 (S:106)). If `|G| > 5`, the conjunction cannot pass at this bound, whereas a singleton can pass with one hit. Duplicate predictions consume positions; they cannot supply more than five distinct pairs. The installed non-NEI rows contain no duplicate gold pairs (exact parsing output below).

For the other returned metrics, label accuracy is unchanged (registry/w-fevconv-receipts.md:290 (S:130), registry/w-fevconv-receipts.md:306 (S:146)). Evidence precision uses the union of pairs, so changing only grouping leaves it unchanged (registry/w-fevconv-receipts.md:213 (S:53), registry/w-fevconv-receipts.md:218 (S:58), registry/w-fevconv-receipts.md:225 (S:65)). Complete-group recall changes under the same nonempty-proper-subset condition even if the label is wrong (registry/w-fevconv-receipts.md:229 (S:69), registry/w-fevconv-receipts.md:231 (S:71), registry/w-fevconv-receipts.md:240 (S:80), registry/w-fevconv-receipts.md:243 (S:83)). F1 can consequently change when the aggregate formula is defined (registry/w-fevconv-receipts.md:308 (S:148), registry/w-fevconv-receipts.md:309 (S:149), registry/w-fevconv-receipts.md:311 (S:151)); the source has an unguarded division when `pr + rec == 0`, so an undefined/error result is not a zero. The conclusion concerns strict correctness and source-defined metrics, not a new observed aggregate score. Group-per-row conversion also changes original-claim weighting/denominator: an original claim with several exported groups becomes several rows (registry/w-fevconv-receipts.md:374 (C:56), registry/w-fevconv-receipts.md:392 (C:74); prior 15,935 rows versus 9,835 distinct original IDs registry/w-fevconv-receipts.md:542 (O:25)). Grouping equivalence alone would not establish original-dev aggregate comparability.

### FOUND — precisely which installed rows are exposed

The exact command `python3 /mnt/20t/xubuqiang/hg-work/fevconv/parse-installed.py` only parsed installed bytes, recomputed their known SHA-256, and counted pair-set sizes; it did not import or call a scorer. Output: 15,935 rows; 9,525 non-NEI / 6,410 NEI; 8,125 non-NEI rows with one distinct pair; **1,400 with more than one**, including 1,369 with 2–5 and **31 with 6–25**. Exact size distribution:

```text
size:  1    2    3   4   5   6  7  8  9 10 12 15 25
rows: 8125 1186 134 33  16  10  6  8  1  3  1  1  1
```

There were zero non-NEI duplicate-pair rows, zero missing pair fields, and all non-NEI line fields were strings, so the integer conversion matters. Full exact output and reproduction program are in validation. An exact row identifier rule is: `label != "NOT ENOUGH INFO" and len({(NFC(e[0]), int(e[1])) for e in row["evidence"]}) > 1`. Appendix I enumerates all 1,400 one-based installed line numbers; the task index is line minus one. Thus 8,125 single-pair non-NEI and 6,410 NEI rows (14,535 total) are not exposed to this **same-exported-group** strictness difference. Exposure means a possible prediction-dependent difference, not that any recorded prediction took that branch.

All **1,395** established original-insufficient-singleton rows are in that 1,400-row set (registry/w-fevconv-receipts.md:537 (O:20), registry/w-fevconv-receipts.md:538 (O:21)); each contains at least one exported pair `p` for which **no** original complete group is a subset of `{p}`. Predicting only that pair with the correct label gives a singleton pass, an exported-conjunction fail, and an original-complete-group fail by registry/w-fevconv-receipts.md:201 (S:41). This strengthens the witness beyond mere exported-group comparison. The remaining five multisentence rows still differ from their own conjunction, but every one of their singleton pairs satisfies some original complete group under the established normalized mapping (difference between the prior 1,400 / 1,395 predicates registry/w-fevconv-receipts.md:537 (O:20), registry/w-fevconv-receipts.md:538 (O:21); audit definition registry/w-fevconv-receipts.md:778 (A:110)). That does not mean the full original-gold and exported-singleton predicates are equivalent for arbitrary predictions: the original can have alternative groups not present in this row. This worker did not independently reconstruct all 1,395 original-ID membership flags or their intersection with the 31 overlong rows; it relies on the established w-jc2 mapping/count and records that limit rather than inventing an ID list.

### FOUND — minimal checkable witness

Installed line **20**, task `fever/validation/19`, original ID **10947**, has label SUPPORTS and pairs `("Fist_of_Legend", 2)` and `("Fist_of_Fury", 0)` (current installed parsing output in validation; historical verbatim example registry/w-fevconv-receipts.md:669 (E:3), registry/w-fevconv-receipts.md:676 (E:10), registry/w-fevconv-receipts.md:689 (E:23)). Take a well-formed prediction with `predicted_label="SUPPORTS"` and `predicted_evidence=[["Fist_of_Fury",0]]`. The single prefix pair is within five. The conjunction requires both pairs and therefore fails; singleton conversion has a one-record group matching it and therefore passes (registry/w-fevconv-receipts.md:190 (S:30), registry/w-fevconv-receipts.md:197 (S:37), registry/w-fevconv-receipts.md:201 (S:41)). The original alternatives reproduced in appendix E contain either `Fist_of_Legend` alone or both pairs, so none is contained in this singleton (registry/w-fevconv-receipts.md:699 (E:33), registry/w-fevconv-receipts.md:749 (E:83)). This is substitution into readable source, not observed scorer execution or a reported score.

The independently parsed first-five selection has: lines 1–3 non-NEI with one pair each; lines 4–5 NEI (exact command/output in validation; current selection record `tests/fixtures/hg_wsel/fever.json:1`). It does not exercise this conjunction-breaking branch. It provides no full-pool comparability claim.

### UNKNOWN — historical scoring, original alternatives and runtime

Whether the historical installed export was ever scored under this exact pinned scorer with any given prediction/gold projection remains UNKNOWN. A historical source packet contains **authored synthetic** controls, not released task measurements: `git show 466cb42bbeae0b80ea7643efe53d19590046e161:tests/fixtures/hg_woffscorer/fever/make_inputs.py` explicitly says it never reads a released task row (registry/w-fevconv-receipts.md:786 (H:1)) and constructs synthetic pages (registry/w-fevconv-receipts.md:792 (H:7)). Those records do not attest scoring of the installed export. No such execution was performed or inferred here.

The 51 absent original groups / 42 IDs remain an omission-provenance limit (registry/w-fevconv-receipts.md:545 (O:28)). Comparing each exported group to its singleton projection is one-directional; comparing the export to **all** original alternative groups can differ in either direction, because predictions may satisfy an original alternative absent from the row (registry/w-fevconv-receipts.md:197 (S:37), registry/w-fevconv-receipts.md:201 (S:41)). No actual score delta, held-out result, full original-gold metric equivalence, producing receipt, authenticated NEI retrieval inputs, pristine runtime or diagnostic authorization is established by this report.

## 3. Parent proposal and validation boundary

`registry/proposals/w-fevconv.json` proposes a searched-absent standing limit for the producing-execution receipt, without asserting global impossibility or automatic withdrawal. It leaves metric semantics as concrete remaining work: explicitly choose/name a conjunctive row metric or restore complete original-group scoring with declared original-claim weighting, then review the selected input under that choice. The proposed next action drops export/installed/selected re-binding and does not re-impose `scorer-offline-closure` or `artifact-only-state-export`: their operator withdrawal is recorded at `registry/withdrawn-requirements.md:18` and `:44` (commit `73a5ab222ab0411651785403931f9ad557dace0f`), with retained limits at `:21` and `:56`. The active registry and journal were not edited.

Baseline checker observation, exact command `python3 tools/check_dataset_blockers.py`:

```json
{"valid": false, "error": "bfcl_v3: missing evidence tests/fixtures/hg_bfcl/README.md"}
```

Four existing registry evidence paths were absent from the unchanged base. To complete local validation, exact historical bytes from `31486f6b41a3a8202dde6602e79edf1062813065` were restored locally as ignored files: BFCL README/inventory, Trivia README, w-prov README. No restored file is staged or committed; hashes, commands and sizes appear in validation `restore-checker.stdout`. The repeated checker output was:

```json
{"valid": true, "datasets": 28, "shared_blockers": 0, "historical_records": 11, "production_authorized": false}
```

This pass depends on those local evidence files; these three deliverables cannot repair their absence in another clean worktree. This is an inherited checkout limitation, unrelated to the FEVER-only report/proposal. No new production/source/test logic was changed and no scorer/model/GPU/API or historical run was executed.

## Appendices — exact readable source and prior observations

Line prefixes such as `S041` denote original source line 41; the text after the prefix is verbatim, except appendix R which preserves the original lossless JSON-quoted line preimages (including line terminators). `registry/w-fevconv-receipts.md:201 (S:41)` citations in the analysis resolve to this report's actual file line containing that source line. This keeps citations readable after historical packets were untracked. Source retrieval commands, hashes and exact outputs are in validation.

### Appendix S

```text
S001 |import six
S002 |
S003 |def check_predicted_evidence_format(instance):
S004 |    if 'predicted_evidence' in instance.keys() and len(instance['predicted_evidence']):
S005 |        assert all(isinstance(prediction, list)
S006 |                   for prediction in instance["predicted_evidence"]), \
S007 |            "Predicted evidence must be a list of (page,line) lists"
S008 |
S009 |        assert all(len(prediction) == 2
S010 |                   for prediction in instance["predicted_evidence"]), \
S011 |            "Predicted evidence must be a list of (page,line) lists"
S012 |
S013 |        assert all(isinstance(prediction[0], six.string_types)
S014 |                    for prediction in instance["predicted_evidence"]), \
S015 |            "Predicted evidence must be a list of (page<string>,line<int>) lists"
S016 |
S017 |        assert all(isinstance(prediction[1], int)
S018 |                   for prediction in instance["predicted_evidence"]), \
S019 |            "Predicted evidence must be a list of (page<string>,line<int>) lists"
S020 |
S021 |
S022 |def is_correct_label(instance):
S023 |    return instance["label"].upper() == instance["predicted_label"].upper()
S024 |
S025 |
S026 |def is_strictly_correct(instance, max_evidence=None):
S027 |    #Strict evidence matching is only for NEI class
S028 |    check_predicted_evidence_format(instance)
S029 |
S030 |    if instance["label"].upper() != "NOT ENOUGH INFO" and is_correct_label(instance):
S031 |        assert 'predicted_evidence' in instance, "Predicted evidence must be provided for strict scoring"
S032 |
S033 |        if max_evidence is None:
S034 |            max_evidence = len(instance["predicted_evidence"])
S035 |
S036 |
S037 |        for evience_group in instance["evidence"]:
S038 |            #Filter out the annotation ids. We just want the evidence page and line number
S039 |            actual_sentences = [[e[2], e[3]] for e in evience_group]
S040 |            #Only return true if an entire group of actual sentences is in the predicted sentences
S041 |            if all([actual_sent in instance["predicted_evidence"][:max_evidence] for actual_sent in actual_sentences]):
S042 |                return True
S043 |
S044 |    #If the class is NEI, we don't score the evidence retrieval component
S045 |    elif instance["label"].upper() == "NOT ENOUGH INFO" and is_correct_label(instance):
S046 |        return True
S047 |
S048 |    return False
S049 |
S050 |
S051 |def evidence_macro_precision(instance, max_evidence=None):
S052 |    this_precision = 0.0
S053 |    this_precision_hits = 0.0
S054 |
S055 |    if instance["label"].upper() != "NOT ENOUGH INFO":
S056 |        all_evi = [[e[2], e[3]] for eg in instance["evidence"] for e in eg if e[3] is not None]
S057 |
S058 |        predicted_evidence = instance["predicted_evidence"] if max_evidence is None else \
S059 |                                                                        instance["predicted_evidence"][:max_evidence]
S060 |
S061 |        for prediction in predicted_evidence:
S062 |            if prediction in all_evi:
S063 |                this_precision += 1.0
S064 |            this_precision_hits += 1.0
S065 |
S066 |        return (this_precision / this_precision_hits) if this_precision_hits > 0 else 1.0, 1.0
S067 |
S068 |    return 0.0, 0.0
S069 |
S070 |def evidence_macro_recall(instance, max_evidence=None):
S071 |    # We only want to score F1/Precision/Recall of recalled evidence for NEI claims
S072 |    if instance["label"].upper() != "NOT ENOUGH INFO":
S073 |        # If there's no evidence to predict, return 1
S074 |        if len(instance["evidence"]) == 0 or all([len(eg) == 0 for eg in instance]):
S075 |           return 1.0, 1.0
S076 |
S077 |        predicted_evidence = instance["predicted_evidence"] if max_evidence is None else \
S078 |                                                                        instance["predicted_evidence"][:max_evidence]
S079 |
S080 |        for evidence_group in instance["evidence"]:
S081 |            evidence = [[e[2], e[3]] for e in evidence_group]
S082 |            if all([item in predicted_evidence for item in evidence]):
S083 |                # We only want to score complete groups of evidence. Incomplete groups are worthless.
S084 |                return 1.0, 1.0
S085 |        return 0.0, 1.0
S086 |    return 0.0, 0.0
S087 |
S088 |
S089 |# Micro is not used. This code is just included to demostrate our model of macro/micro
S090 |def evidence_micro_precision(instance):
S091 |    this_precision = 0
S092 |    this_precision_hits = 0
S093 |
S094 |    # We only want to score Macro F1/Precision/Recall of recalled evidence for NEI claims
S095 |    if instance["label"].upper() != "NOT ENOUGH INFO":
S096 |        all_evi = [[e[2], e[3]] for eg in instance["evidence"] for e in eg if e[3] is not None]
S097 |
S098 |        for prediction in instance["predicted_evidence"]:
S099 |            if prediction in all_evi:
S100 |                this_precision += 1.0
S101 |            this_precision_hits += 1.0
S102 |
S103 |    return this_precision, this_precision_hits
S104 |
S105 |
S106 |def fever_score(predictions,actual=None, max_evidence=5):
S107 |    correct = 0
S108 |    strict = 0
S109 |
S110 |    macro_precision = 0
S111 |    macro_precision_hits = 0
S112 |
S113 |    macro_recall = 0
S114 |    macro_recall_hits = 0
S115 |
S116 |    for idx,instance in enumerate(predictions):
S117 |        assert 'predicted_evidence' in instance.keys(), 'evidence must be provided for the prediction'
S118 |
S119 |        #If it's a blind test set, we need to copy in the values from the actual data
S120 |        if 'evidence' not in instance or 'label' not in instance:
S121 |            assert actual is not None, 'in blind evaluation mode, actual data must be provided'
S122 |            assert len(actual) == len(predictions), 'actual data and predicted data length must match'
S123 |            assert 'evidence' in actual[idx].keys(), 'evidence must be provided for the actual evidence'
S124 |            instance['evidence'] = actual[idx]['evidence']
S125 |            instance['label'] = actual[idx]['label']
S126 |
S127 |        assert 'evidence' in instance.keys(), 'gold evidence must be provided'
S128 |
S129 |        if is_correct_label(instance):
S130 |            correct += 1.0
S131 |
S132 |            if is_strictly_correct(instance, max_evidence):
S133 |                strict+=1.0
S134 |
S135 |        macro_prec = evidence_macro_precision(instance, max_evidence)
S136 |        macro_precision += macro_prec[0]
S137 |        macro_precision_hits += macro_prec[1]
S138 |
S139 |        macro_rec = evidence_macro_recall(instance, max_evidence)
S140 |        macro_recall += macro_rec[0]
S141 |        macro_recall_hits += macro_rec[1]
S142 |
S143 |    total = len(predictions)
S144 |
S145 |    strict_score = strict / total
S146 |    acc_score = correct / total
S147 |
S148 |    pr = (macro_precision / macro_precision_hits) if macro_precision_hits > 0 else 1.0
S149 |    rec = (macro_recall / macro_recall_hits) if macro_recall_hits > 0 else 0.0
S150 |
S151 |    f1 = 2.0 * pr * rec / (pr + rec)
S152 |
S153 |    return strict_score, acc_score, pr, rec, f1
```

### Appendix C

```text
C001 |"""
C002 |Create FEVER NLI dataset, where for each line in the original FEVER dataset
C003 |with N number of evidence annotations, we create N instances with the
C004 |original fields and evidence - list of sentences # [Wikipedia URL, sentence ID, sentence]
C005 |from the wiki dump.
C006 |
C007 |'NOT ENOUGH INFO' instances are discarded as they do not have any evidence annotations.
C008 |"""
C009 |import argparse
C010 |import json
C011 |import os
C012 |import unicodedata
C013 |from tqdm import tqdm
C014 |
C015 |
C016 |if __name__ == "__main__":
C017 |    parser = argparse.ArgumentParser()
C018 |    parser.add_argument("--wiki_dir",
C019 |                        help="Path to the wiki pages dump",
C020 |                        required=True, type=str)
C021 |    parser.add_argument("--dataset_dirs",
C022 |                        help="Paths to the dataset splits",
C023 |                        required=True, type=str, nargs='+')
C024 |    parser.add_argument("--output_paths",
C025 |                        help="Paths to serialize the datasets",
C026 |                        required=True, type=str, nargs='+')
C027 |    args = parser.parse_args()
C028 |
C029 |    wiki_docs = {}  # wiki_id: [wiki lines]
C030 |
C031 |    for file in tqdm(os.scandir(args.wiki_dir), desc='Reading wiki pages...', leave=True):
C032 |        # {"id": "", "text": "", "lines": ""}
C033 |        # "lines": "0\tThe following are the football -LRB-
C034 |        # soccer -RRB- events of the year 1928 throughout the world .\n1\t"
C035 |        with open(file) as out:
C036 |            for doc in out:
C037 |                doc = json.loads(doc)
C038 |                doc_lines = {}
C039 |                for doc_line in doc['lines'].split('\n'):
C040 |                    cols = doc_line.split('\t')
C041 |                    if len(cols) > 1:
C042 |                        try:
C043 |                            doc_lines[int(cols[0])] = cols[1]
C044 |                        except Exception as e:
C045 |                            # print(cols)
C046 |                            pass
C047 |                wiki_docs[doc['id']] = doc_lines
C048 |
C049 |    for old_dir, new_dir in zip(args.dataset_dirs, args.output_paths):
C050 |        output_writer = open(new_dir, 'w')
C051 |        with open(old_dir) as out:
C052 |            for line in tqdm(out, desc=f'Processing dataset...{old_dir}', leave=True):
C053 |                line = json.loads(line)
C054 |                if line['label'] == 'NOT ENOUGH INFO':
C055 |                    continue
C056 |                for ann in line['evidence']:
C057 |                    sentences = []
C058 |                    for ann_sent in ann:  # [Annotation ID, Evidence ID, Wikipedia URL, sentence ID]
C059 |                        if ann_sent[2]:
C060 |                            wiki_url = unicodedata.normalize('NFC', ann_sent[2])
C061 |                            # [Wikipedia URL, sentence ID, sentence]
C062 |                            if wiki_url in wiki_docs:
C063 |                                sentence = wiki_docs[wiki_url].get(ann_sent[3], '')
C064 |                                if sentence != '':
C065 |                                    sentences.append([wiki_url, ann_sent[3], sentence])
C066 |                            else:
C067 |                                sentences = []
C068 |                                break
C069 |
C070 |                    if len(sentences) == 0:
C071 |                        continue
C072 |                    nli_line = line.copy()
C073 |                    nli_line['evidence'] = sentences
C074 |                    output_writer.write(json.dumps(nli_line) + '\n')
C075 |        output_writer.close()
```

### Appendix M

```text
M001 |"""Add 'NOT ENOUGH INFO' instances generated with the Papelo system."""
M002 |import argparse
M003 |import json
M004 |import random
M005 |
M006 |if __name__ == "__main__":
M007 |    orig_files = 'data/adv_sr_nli.jsonl'
M008 |    nei_files = 'data/adv_nei_nli.jsonl'
M009 |    parser = argparse.ArgumentParser()
M010 |    parser.add_argument("--sr_file",
M011 |                        help="Path to the file with support/refute evidence-claim pairs",
M012 |                        required=True, type=str)
M013 |    parser.add_argument("--nei_file",
M014 |                        help="Path to the file with NEI evidence-claim pairs",
M015 |                        required=True, type=str)
M016 |    parser.add_argument("--output_path",
M017 |                        help="Paths to output file",
M018 |                        required=True, type=str)
M019 |    args = parser.parse_args()
M020 |
M021 |    orig_lines = []
M022 |    for c in open(args.sr_file).readlines():
M023 |        json_line = json.loads(c)
M024 |        if json_line['label'].upper() in ['SUPPORTS', 'REFUTES'] and json_line['annotation'] != "N/A":
M025 |            orig_lines.append(c.strip())
M026 |
M027 |    nei_lines = open(args.nei_file).readlines()
M028 |
M029 |    nei_lines_cleaned = []
M030 |    for line in nei_lines:
M031 |        line_json = json.loads(line)
M032 |        if line_json['label'].upper() == 'NOT ENOUGH INFO' and line_json['annotation']!= "N/A":
M033 |            line_json['label'] = 'NOT ENOUGH INFO'
M034 |            nei_lines_cleaned.append(json.dumps(line_json))
M035 |
M036 |    labels_orig = {}
M037 |    for line in orig_lines + nei_lines_cleaned:
M038 |        label = json.loads(line)['label']
M039 |        labels_orig[label] = labels_orig.get(label, 0) + 1
M040 |
M041 |    print(labels_orig)
M042 |    print(len(orig_lines)+len(nei_lines_cleaned))
M043 |
M044 |    final_lines = orig_lines + nei_lines_cleaned
M045 |    random.seed(42)
M046 |    random.shuffle(final_lines)
M047 |
M048 |    with open(args.output_path, 'w') as out:
M049 |        out.write('\n'.join(final_lines))
```

### Appendix N

```text
N001 |"""
N002 |Add 'NOT ENOUGH INFO' instances generated with the Papelo system.
N003 |"""
N004 |import argparse
N005 |import json
N006 |import os
N007 |import unicodedata
N008 |from tqdm import tqdm
N009 |
N010 |
N011 |if __name__ == "__main__":
N012 |    parser = argparse.ArgumentParser()
N013 |    parser.add_argument("--wiki_dir",
N014 |                        help="Path to the wiki pages dump",
N015 |                        required=True, type=str)
N016 |    parser.add_argument("--dataset_dirs",
N017 |                        help="Paths to the dataset splits",
N018 |                        required=True, type=str, nargs='+')
N019 |    parser.add_argument("--output_paths",
N020 |                        help="Paths to serialize the datasets",
N021 |                        required=True, type=str, nargs='+')
N022 |    args = parser.parse_args()
N023 |
N024 |    wiki_docs = {}  # wiki_id: [wiki lines]
N025 |
N026 |    for file in tqdm(os.scandir(args.wiki_dir), desc='Reading wiki pages...', leave=True):
N027 |        # {"id": "", "text": "", "lines": ""}
N028 |        # "lines": "0\tThe following are the football -LRB- soccer
N029 |        # -RRB- events of the year 1928 throughout the world .\n1\t"
N030 |        with open(file) as out:
N031 |            for doc in out:
N032 |                doc = json.loads(doc)
N033 |                doc_lines = [doc_line.split('\t')[1] for doc_line in doc['lines'].split('\n')
N034 |                             if len(doc_line.split('\t')) > 1]
N035 |                wiki_docs[doc['id']] = doc_lines
N036 |
N037 |    for papelo_path, new_path in zip(args.dataset_dirs, args.output_paths):
N038 |        """
N039 |        {"id": 56204, "verifiable": "NOT VERIFIABLE", "label": "NOT ENOUGH INFO",
N040 |        "claim": "Keith Urban is a person who sings.",
N041 |        "evidence": [[[176603, null, null, null], [178904, null, null, null], [313935, null, null, null]]],
N042 |        "predicted_pages": ["Keith_Urban_-LRB-1999_album-RRB-", "Days_Go_By"],
N043 |        "predicted_sentences": [["Keith_Urban_-LRB-1999_album-RRB-", 0], ["Days_Go_By", 0]]}
N044 |        """
N045 |        output_writer = open(new_path, 'w')
N046 |        with open(papelo_path) as out:
N047 |            for line in tqdm(out, desc='Processing dataset...', leave=True):
N048 |                line = json.loads(line)
N049 |                for predicted_sent in line['predicted_sentences'][:1]:
N050 |                    wiki_url = unicodedata.normalize('NFC', predicted_sent[0])
N051 |                    sent_id = predicted_sent[1]
N052 |                    if len(wiki_docs[wiki_url]) > sent_id:
N053 |                        sentence = wiki_docs[wiki_url][sent_id]
N054 |                        sentences = [[wiki_url, sent_id, sentence]]
N055 |                        nli_line = line.copy()
N056 |                        nli_line['evidence'] = sentences
N057 |                        del nli_line['predicted_pages']
N058 |                        del nli_line['predicted_sentences']
N059 |                        output_writer.write(json.dumps(nli_line) + '\n')
N060 |        output_writer.close()
```

### Appendix O

```text
O001 |{
O002 |  "scope": "full installed valid.jsonl versus public original dev; no admitted selection or run",
O003 |  "installed_path": "/mnt/20t/xubuqiang/datasets/fever/valid.jsonl",
O004 |  "installed_bytes": 6471611,
O005 |  "installed_sha256": "5da0ccc0ccf77f974611de13f8aac6f78c6bba6293912835099eb6029baa85d9",
O006 |  "installed_git_blob_sha1": "ae61c5b6cb11eafcc7d6c33069c68dd5c848f91f",
O007 |  "original_body_sha256": "e89865bfe1b4dd054e03dd57d7241a6fde24862905f31117cf0cd719f7c78df7",
O008 |  "original_body_md5": "4eecc1018b3d2bd46089ca36d886f439",
O009 |  "official_download_and_linked_zenodo_bytes_equal": true,
O010 |  "counts": {
O011 |    "installed_rows": 15935,
O012 |    "original_id_present": 15935,
O013 |    "original_id_matches": 15935,
O014 |    "claim_matches": 15935,
O015 |    "label_matches": 15935,
O016 |    "verifiable_matches": 15935,
O017 |    "non_nei_rows": 9525,
O018 |    "non_nei_complete_group_set_equal_rows": 9525,
O019 |    "non_nei_complete_group_ordered_equal_rows": 9525,
O020 |    "non_nei_multisentence_rows": 1400,
O021 |    "non_nei_rows_with_original_insufficient_singleton": 1395,
O022 |    "original_insufficient_export_singleton_occurrences": 3046,
O023 |    "nei_rows": 6410,
O024 |    "original_release_rows": 19998,
O025 |    "installed_unique_original_ids": 9835,
O026 |    "installed_unique_non_nei_original_ids": 6551,
O027 |    "original_non_nei_distinct_groups_for_represented_ids": 9575,
O028 |    "original_groups_absent_from_valid_for_represented_non_nei_ids": 51,
O029 |    "represented_non_nei_ids_with_groups_absent_from_valid": 42
O030 |  },
O031 |  "normalization": "page Unicode NFC; line int; group pair-set equality and ordered equality reported separately",
O032 |  "inventory_sha256": "aaea48decd7e67f10b7db4512cf9b15f32ee9f49c338c6dd1a187f78097daf55",
O033 |  "inventory_gzip_sha256": "b3d77808ce7a5d2644bffbf5c3096ff81b17da4f21dfe5319862067bfe5511a5",
O034 |  "source_sha256": {
O035 |    "data/datasets/fever.py": "7c0cd67c7d82d9c71f2bde4c52e564f279930f6fc7f62aae4cdda5b7c27afcd0",
O036 |    "data/scaffolds/qa/evidence_scorers.py": "a962f23e0c0f704b31294902ddaae3facee0e7496dfc43041bf973a912043729",
O037 |    "tests/fixtures/hg_e1_review/fever-create-nli-dataset.py": "09054c04a53eb5f3f035d94fd2fe8a271a57bf69c5768eadd0535497f8cec884",
O038 |    "tests/fixtures/hg_e1_review/fever-hub-proxy-tree.body": "120d602345fb2b5114cd28473d99b691a0f5a9e7505ff38c4ed49bbfa8dd9c75"
O039 |  },
O040 |  "producer_blobs": {
O041 |    "producer-readme": {
O042 |      "tree_path": "README.md",
O043 |      "git_blob_sha1": "fdef54595fb47675cf5db2328dc92601b0f02cd5",
O044 |      "sha256": "374052abccfd55c67e5d1a94f3c05b82de4426f2ce1c5e9efdd9c5daa7164a34",
O045 |      "matches_preserved_pinned_tree": true
O046 |    },
O047 |    "producer-merge": {
O048 |      "tree_path": "scripts/merge_nli_files.py",
O049 |      "git_blob_sha1": "2191816140b9ec0738a305eb09b8f16f58d497dd",
O050 |      "sha256": "960f0540bb4c1e1c80027c88f256906b3c5d2124d5629e1fea0fdd7f32e36cfd",
O051 |      "matches_preserved_pinned_tree": true
O052 |    },
O053 |    "producer-nei": {
O054 |      "tree_path": "scripts/aggregate_papelo_nei.py",
O055 |      "git_blob_sha1": "dc75b530850d36bb9c706c9a4ca9d7305c91a6e0",
O056 |      "sha256": "cf9d2d241577666b8cd7a52d041d3b09863d24dce8c503e3ce98c36f471a69fd",
O057 |      "matches_preserved_pinned_tree": true
O058 |    }
O059 |  },
O060 |  "acquisitions": [
O061 |    {
O062 |      "receipt": "fever-dev.receipt.json",
O063 |      "status": 200,
O064 |      "body_bytes": 4349935,
O065 |      "body_sha256": "e89865bfe1b4dd054e03dd57d7241a6fde24862905f31117cf0cd719f7c78df7",
O066 |      "error": null
O067 |    },
O068 |    {
O069 |      "receipt": "fever-download-page.receipt.json",
O070 |      "status": 200,
O071 |      "body_bytes": 17217,
O072 |      "body_sha256": "215843ee560afbcdcc6df00f6451cb62445c98bce7178821eb8da93f2a4ca723",
O073 |      "error": null
O074 |    },
O075 |    {
O076 |      "receipt": "hub-commits-retry.receipt.json",
O077 |      "status": null,
O078 |      "body_bytes": 0,
O079 |      "body_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
O080 |      "error": "URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1000)>"
O081 |    },
O082 |    {
O083 |      "receipt": "hub-commits.receipt.json",
O084 |      "status": null,
O085 |      "body_bytes": 0,
O086 |      "body_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
O087 |      "error": "URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1000)>"
O088 |    },
O089 |    {
O090 |      "receipt": "original-zenodo.receipt.json",
O091 |      "status": 200,
O092 |      "body_bytes": 4349935,
O093 |      "body_sha256": "e89865bfe1b4dd054e03dd57d7241a6fde24862905f31117cf0cd719f7c78df7",
O094 |      "error": null
O095 |    },
O096 |    {
O097 |      "receipt": "producer-issue5-comments.receipt.json",
O098 |      "status": 200,
O099 |      "body_bytes": 2035,
O100 |      "body_sha256": "b724d4363060b976e1f6c818a952522a708ab3438ad82505825c2ed0328139ba",
O101 |      "error": null
O102 |    },
O103 |    {
O104 |      "receipt": "producer-issue5-retry.receipt.json",
O105 |      "status": 200,
O106 |      "body_bytes": 3563,
O107 |      "body_sha256": "9ebb7cad63b68d518fe071a14d347f6a27c7715ac522edd6453059fb1b48310a",
O108 |      "error": null
O109 |    },
O110 |    {
O111 |      "receipt": "producer-issue5.receipt.json",
O112 |      "status": null,
O113 |      "body_bytes": 0,
O114 |      "body_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
O115 |      "error": "URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1000)>"
O116 |    },
O117 |    {
O118 |      "receipt": "producer-merge.receipt.json",
O119 |      "status": 200,
O120 |      "body_bytes": 1806,
O121 |      "body_sha256": "960f0540bb4c1e1c80027c88f256906b3c5d2124d5629e1fea0fdd7f32e36cfd",
O122 |      "error": null
O123 |    },
O124 |    {
O125 |      "receipt": "producer-nei.receipt.json",
O126 |      "status": 200,
O127 |      "body_bytes": 2780,
O128 |      "body_sha256": "cf9d2d241577666b8cd7a52d041d3b09863d24dce8c503e3ce98c36f471a69fd",
O129 |      "error": null
O130 |    },
O131 |    {
O132 |      "receipt": "producer-readme.receipt.json",
O133 |      "status": 200,
O134 |      "body_bytes": 6786,
O135 |      "body_sha256": "374052abccfd55c67e5d1a94f3c05b82de4426f2ce1c5e9efdd9c5daa7164a34",
O136 |      "error": null
O137 |    }
O138 |  ],
O139 |  "producer_revision_bound_to_export": null,
O140 |  "selected_manifest": null,
O141 |  "run_id": null,
O142 |  "scorer_executed": false,
O143 |  "blocker_closed": false
O144 |}
```

### Appendix E

```text
E001 |[
E002 |  {
E003 |    "installed_line": 20,
E004 |    "export_id": "c54ca9623d1faf64622629d5f3310ad0",
E005 |    "original_id": 10947,
E006 |    "original_line": 1278,
E007 |    "installed_row_sha256": "fba12d8d247ba6c33c3cbd50a24197e0455f4e5fb27df4f888cdd827b9e0e766",
E008 |    "original_row_sha256": "42c9376e8b2f90a62fe7a7bca111ddcdc6aee3f198c8c1bb1d2db71ffd1e6512",
E009 |    "label": "SUPPORTS",
E010 |    "export_pair_count": 2,
E011 |    "original_group_indices_set_equal": [
E012 |      1,
E013 |      3,
E014 |      4,
E015 |      5
E016 |    ],
E017 |    "original_group_indices_ordered_equal": [
E018 |      1,
E019 |      3,
E020 |      4,
E021 |      5
E022 |    ],
E023 |    "export_pairs": [
E024 |      [
E025 |        "Fist_of_Legend",
E026 |        2
E027 |      ],
E028 |      [
E029 |        "Fist_of_Fury",
E030 |        0
E031 |      ]
E032 |    ],
E033 |    "original_group_pairs": [
E034 |      [
E035 |        [
E036 |          "Fist_of_Legend",
E037 |          2
E038 |        ]
E039 |      ],
E040 |      [
E041 |        [
E042 |          "Fist_of_Legend",
E043 |          2
E044 |        ],
E045 |        [
E046 |          "Fist_of_Fury",
E047 |          0
E048 |        ]
E049 |      ],
E050 |      [
E051 |        [
E052 |          "Fist_of_Legend",
E053 |          2
E054 |        ]
E055 |      ],
E056 |      [
E057 |        [
E058 |          "Fist_of_Legend",
E059 |          2
E060 |        ],
E061 |        [
E062 |          "Fist_of_Fury",
E063 |          0
E064 |        ]
E065 |      ],
E066 |      [
E067 |        [
E068 |          "Fist_of_Legend",
E069 |          2
E070 |        ],
E071 |        [
E072 |          "Fist_of_Fury",
E073 |          0
E074 |        ]
E075 |      ],
E076 |      [
E077 |        [
E078 |          "Fist_of_Legend",
E079 |          2
E080 |        ],
E081 |        [
E082 |          "Fist_of_Fury",
E083 |          0
E084 |        ]
E085 |      ]
E086 |    ],
E087 |    "original_insufficient_singletons": [
E088 |      [
E089 |        "Fist_of_Fury",
E090 |        0
E091 |      ]
E092 |    ]
E093 |  },
E094 |  {
E095 |    "installed_line": 27,
```

### Appendix A

```text
A099 |                  'original_group_indices_ordered_equal': ordered_indices}
A100 |        inventory.append(record)
A101 |        if row['label'] == 'NOT ENOUGH INFO':
A102 |            counts['nei_rows'] += 1
A103 |            continue
A104 |        seen_non_nei_ids.add(source['id'])
A105 |        counts['non_nei_rows'] += 1
A106 |        counts['non_nei_complete_group_set_equal_rows'] += bool(exact_set_indices)
A107 |        counts['non_nei_complete_group_ordered_equal_rows'] += bool(ordered_indices)
A108 |        counts['non_nei_multisentence_rows'] += len(as_set) > 1
A109 |        seen_groups[source['id']].add(as_set)
A110 |        singleton_invalid = [list(pair) for pair in sorted(as_set)
A111 |                             if not any(pair_set(g) <= {pair} for g in groups)]
A112 |        counts['non_nei_rows_with_original_insufficient_singleton'] += bool(singleton_invalid)
```

### Appendix H

```text
H001 |"""Author synthetic FEVER scorer probes; never read a released task row."""
H002 |import json
H003 |from pathlib import Path
H004 |
H005 |HERE = Path(__file__).resolve().parent
H006 |A = [0, 0, "Synthetic_Page_A", 1]
H007 |B = [0, 1, "Synthetic_Page_B", 2]
H008 |C = [1, 2, "Synthetic_Page_C", 3]
H009 |AB = [[A, B]]
H010 |pa, pb, pc = [[e[2], e[3]] for e in (A, B, C)]
H011 |rows = []
H012 |
H013 |
H014 |def add(name, predicted, pairs, *, label="SUPPORTS", evidence=AB, flat=False):
H015 |    local_evidence = evidence
H016 |    if flat:
H017 |        assert len(evidence) == 1
H018 |        local_evidence = [[e[2], e[3], "authored synthetic sentence"] for e in evidence[0]]
H019 |    rows.append({"id": name, "synthetic": True,
H020 |                 "projection": "flat-mirror from one conjunctive group" if flat else "canonical grouped gold",
```

### Appendix R

```text
R035 |"# Dataset Preparation\n"
R036 |"The data used for training a fact checking model can be found at [HuggingFace fever_gold_evidence dataset](https://huggingface.co/datasets/copenlu/fever_gold_evidence)\n"
R037 |"\n"
R038 |"1. We join each claim with its gold evidence sentences from the Wikipedia pages. \n"
R039 |"This is done for SUPPORTS and REFUTES classes as NEI do not have evidence.<br>\n"
R040 |"`export PYTHONPATH=./`<br>\n"
R041 |"`python scripts/create_nli_dataset.py --dataset_dirs data/paper_train.jsonl --wiki_dir data/wiki-pages/wiki-pages/ --output_paths data/train_sr_nli.jsonl`\n"
R042 |"\n"
R043 |"Where paper_train.jsonl is an example path to a FEVER's dataset file in jsonl format, and wiki-pages is an example path to the Wikipedia dump from the FEVER dataset.\n"
R044 |"\n"
R045 |"2. We then collect evidence sentences for the NEI class using the Papelo system from FEVER'2018 \n"
R046 |"and merge the outputs of the system for the NEI class with the gold evidence sentences collected in the previous step.<br>\n"
R047 |"`PYTHONPATH=fever2018-retrieval/src`<br>\n"
R048 |"`python fever2018-retrieval/src/scripts/retrieval/ir.py --db data/fever/fever.db --model data/index/fever-tfidf-ngram\\=2-hash\\=16777216-tokenizer\\=simple.npz --in-file data/fever-data/train_nei.jsonl --out-file data/fever/train_nei.sentences.p5.s5.jsonl --max-page 2 --max-sent 2`\n"
R049 |"<br><br>\n"
R050 |"`python scripts/aggregate_papelo_nei.py --dataset_dirs data/fever/train_nei.sentences.p5.s5.jsonl --wiki_dir data/wiki-pages/wiki-pages/ --output_paths data/train_nei_nli.jsonl`\n"
R051 |"<br><br>\n"
R052 |"`python scripts/merge_nli_files.py --sr_file data/train_sr_nli.jsonl --nei_file data/train_nei_nli.jsonl --output_path data/train_nli.jsonl`\n"
R053 |"\n"
```

### Appendix CS

```text
CS001 |{
CS002 |  "url": "https://api.github.com/repos/sheffieldnlp/fever-scorer/contents/src/fever/scorer.py?ref=4801615100fbf6327f8e99b5dbaefe5dd890e869",
CS003 |  "requested_at_utc": "2026-10-14T17:54:09.667853+00:00",
CS004 |  "method": "GET",
CS005 |  "timeout_s": 25,
CS006 |  "status": 200,
CS007 |  "final_url": "https://api.github.com/repos/sheffieldnlp/fever-scorer/contents/src/fever/scorer.py?ref=4801615100fbf6327f8e99b5dbaefe5dd890e869",
CS008 |  "headers": {
```

### Appendix CC

```text
CC001 |{
CC002 |  "url": "https://api.github.com/repos/copenlu/fever-adversarial-attacks/contents/scripts/create_nli_dataset.py?ref=aaa126ec4f3cf7163f69b82a0a0976d2579a04a6",
CC003 |  "requested_at_utc": "2026-10-14T18:03:53.522115+00:00",
CC004 |  "method": "GET",
CC005 |  "timeout_s": 25,
CC006 |  "status": 200,
CC007 |  "final_url": "https://api.github.com/repos/copenlu/fever-adversarial-attacks/contents/scripts/create_nli_dataset.py?ref=aaa126ec4f3cf7163f69b82a0a0976d2579a04a6",
CC008 |  "headers": {
```

### Appendix I — all exposed one-based installed lines

```text
20,27,51,56,62,82,84,96,120,125,165,187,189,196,198,201,206,211,218,226
254,264,266,278,281,288,290,293,294,300,302,305,306,313,314,340,357,403,421,463
482,486,488,502,516,526,534,553,562,563,583,600,610,613,622,626,649,678,679,682
698,708,714,715,717,725,744,750,766,787,790,791,801,803,814,825,828,829,850,860
864,865,874,876,877,879,880,891,895,910,913,928,930,945,947,953,961,987,988,998
1008,1017,1040,1045,1049,1065,1088,1092,1095,1101,1131,1134,1148,1156,1162,1174,1200,1213,1229,1251
1269,1277,1285,1288,1301,1310,1313,1327,1373,1382,1388,1389,1400,1430,1444,1470,1478,1486,1512,1514
1550,1586,1587,1604,1621,1634,1677,1685,1709,1717,1718,1728,1746,1759,1760,1780,1799,1821,1830,1831
1853,1866,1893,1901,1907,1916,1923,1925,1947,1951,1974,1977,1995,1996,2010,2016,2024,2048,2049,2051
2063,2065,2084,2115,2125,2163,2165,2167,2191,2196,2201,2205,2213,2220,2237,2251,2264,2284,2293,2316
2340,2346,2353,2355,2357,2376,2383,2395,2404,2406,2443,2448,2449,2478,2487,2506,2523,2547,2569,2597
2610,2620,2624,2637,2643,2652,2673,2681,2718,2725,2750,2755,2759,2774,2787,2799,2804,2806,2809,2820
2850,2851,2863,2864,2876,2878,2884,2898,2907,2913,2917,2964,2967,2973,2977,2981,2994,2995,3026,3028
3043,3050,3070,3077,3099,3101,3102,3111,3132,3136,3138,3161,3173,3175,3176,3179,3192,3204,3227,3228
3229,3234,3239,3247,3254,3274,3287,3294,3298,3302,3308,3312,3314,3334,3353,3382,3394,3397,3418,3438
3471,3476,3478,3481,3490,3491,3522,3531,3558,3567,3577,3579,3591,3600,3605,3612,3614,3620,3640,3646
3655,3664,3665,3668,3672,3692,3711,3721,3735,3739,3742,3750,3757,3764,3769,3792,3831,3832,3879,3904
3907,3908,3930,3931,3938,3947,3951,3957,3969,4003,4008,4026,4027,4033,4044,4048,4055,4074,4076,4099
4112,4116,4155,4161,4163,4164,4183,4191,4202,4224,4234,4238,4247,4254,4269,4277,4279,4294,4302,4330
4342,4357,4359,4366,4371,4391,4404,4405,4424,4427,4431,4472,4491,4496,4499,4511,4528,4535,4552,4569
4585,4592,4622,4624,4626,4645,4652,4659,4688,4706,4708,4709,4752,4760,4763,4767,4782,4784,4801,4803
4805,4807,4811,4832,4834,4863,4900,4904,4910,4926,4928,4937,4939,4940,4946,4952,4968,4974,4984,5005
5016,5019,5022,5032,5043,5056,5068,5076,5087,5090,5097,5100,5103,5111,5115,5124,5130,5143,5147,5148
5154,5155,5156,5194,5198,5211,5212,5229,5242,5257,5261,5282,5286,5290,5302,5310,5317,5353,5363,5377
5378,5384,5392,5394,5409,5413,5414,5420,5425,5427,5453,5472,5477,5485,5488,5503,5511,5512,5530,5557
5563,5571,5573,5583,5594,5597,5610,5613,5617,5621,5636,5650,5693,5700,5713,5722,5723,5733,5737,5751
5761,5778,5784,5788,5812,5814,5815,5816,5822,5824,5835,5836,5851,5877,5880,5884,5891,5910,5912,5916
5920,5950,5965,5976,5992,6016,6039,6055,6059,6065,6070,6091,6105,6107,6117,6118,6152,6158,6173,6181
6191,6196,6201,6229,6247,6251,6257,6288,6297,6353,6362,6365,6374,6381,6397,6399,6416,6420,6430,6446
6447,6453,6459,6461,6483,6501,6508,6547,6562,6566,6580,6581,6596,6625,6628,6633,6650,6651,6674,6687
6714,6717,6733,6735,6760,6771,6782,6783,6787,6793,6804,6806,6824,6826,6830,6835,6838,6857,6858,6864
6868,6880,6900,6932,6936,6953,6987,7019,7031,7046,7066,7079,7085,7100,7104,7105,7106,7108,7109,7127
7148,7150,7153,7163,7164,7185,7187,7198,7210,7211,7238,7249,7265,7271,7285,7305,7317,7325,7348,7349
7358,7364,7371,7375,7377,7410,7415,7422,7425,7431,7434,7437,7439,7447,7455,7477,7499,7500,7511,7534
7537,7550,7572,7575,7579,7584,7591,7599,7619,7646,7650,7662,7663,7665,7677,7687,7691,7711,7719,7737
7773,7796,7797,7805,7810,7815,7838,7846,7875,7905,7923,7930,7931,7933,7934,7936,7956,7967,7972,7988
7990,8002,8013,8031,8041,8071,8086,8104,8127,8137,8139,8146,8155,8158,8179,8182,8193,8197,8211,8216
8231,8234,8235,8266,8280,8284,8286,8291,8295,8307,8318,8356,8384,8389,8394,8418,8419,8434,8435,8439
8453,8468,8498,8520,8523,8546,8582,8603,8628,8651,8660,8674,8697,8721,8725,8726,8743,8749,8760,8762
8769,8775,8776,8781,8806,8850,8868,8882,8883,8889,8909,8933,8944,8953,8954,8976,8993,8999,9029,9052
9058,9083,9089,9092,9093,9101,9104,9114,9120,9128,9150,9154,9158,9160,9164,9182,9216,9217,9222,9228
9234,9262,9266,9286,9302,9308,9311,9322,9325,9352,9371,9386,9399,9400,9424,9429,9454,9456,9461,9462
9463,9470,9472,9483,9491,9498,9505,9515,9516,9544,9569,9588,9599,9602,9611,9627,9672,9680,9742,9769
9773,9779,9795,9799,9801,9804,9818,9819,9823,9848,9897,9904,9919,9944,9948,9961,9979,9980,9996,10011
10014,10032,10063,10065,10086,10099,10101,10110,10125,10132,10143,10155,10159,10161,10183,10195,10208,10214,10221,10237
10243,10245,10250,10268,10307,10314,10320,10327,10331,10333,10342,10347,10354,10355,10366,10380,10382,10387,10393,10418
10434,10447,10448,10455,10466,10474,10478,10479,10483,10492,10493,10516,10520,10523,10528,10536,10551,10553,10554,10557
10560,10564,10569,10604,10606,10622,10624,10647,10662,10663,10670,10675,10689,10691,10708,10709,10741,10764,10766,10803
10805,10809,10815,10829,10831,10838,10852,10859,10860,10889,10901,10906,10933,10949,10958,10959,10962,10966,10967,10969
10970,10981,10990,10998,11003,11010,11013,11028,11031,11058,11060,11074,11075,11080,11090,11095,11111,11122,11153,11154
11159,11167,11173,11185,11205,11208,11226,11231,11262,11285,11298,11299,11307,11316,11318,11341,11349,11359,11360,11376
11377,11402,11425,11429,11448,11453,11462,11471,11476,11479,11488,11504,11522,11524,11544,11553,11594,11616,11640,11645
11653,11679,11686,11695,11731,11737,11756,11781,11805,11840,11850,11853,11881,11882,11884,11904,11927,11950,11955,11957
11976,11977,11978,11979,11983,11994,12005,12046,12047,12062,12070,12081,12088,12089,12098,12126,12129,12144,12147,12154
12167,12186,12195,12217,12222,12265,12276,12292,12294,12295,12307,12334,12353,12362,12387,12390,12407,12426,12448,12454
12465,12466,12469,12474,12478,12480,12487,12489,12504,12506,12512,12518,12533,12538,12543,12558,12564,12571,12587,12611
12639,12642,12655,12656,12657,12660,12687,12691,12726,12739,12748,12749,12751,12758,12768,12773,12793,12818,12842,12866
12870,12876,12883,12886,12891,12894,12899,12938,12974,12982,12985,12986,12987,12993,12994,12997,13034,13045,13072,13104
13129,13155,13157,13170,13172,13173,13175,13188,13195,13205,13206,13229,13232,13244,13262,13277,13278,13286,13319,13342
13347,13348,13395,13396,13413,13429,13451,13457,13475,13486,13502,13517,13518,13555,13558,13572,13604,13616,13669,13693
13706,13714,13720,13726,13728,13743,13754,13766,13772,13776,13781,13791,13796,13804,13806,13811,13812,13818,13825,13854
13857,13867,13890,13907,13910,13932,13962,13971,13987,13998,14009,14025,14044,14074,14097,14113,14155,14177,14178,14190
14202,14210,14211,14214,14218,14223,14226,14243,14251,14261,14293,14301,14303,14312,14313,14327,14437,14438,14455,14464
14467,14473,14482,14485,14488,14500,14506,14512,14523,14540,14543,14545,14565,14567,14575,14580,14588,14600,14609,14612
14642,14643,14661,14665,14667,14670,14700,14707,14723,14749,14750,14751,14754,14759,14778,14795,14802,14803,14811,14816
14822,14827,14842,14862,14878,14882,14886,14892,14925,14926,14934,14954,14966,14970,14989,14992,14994,15016,15020,15031
15045,15053,15065,15068,15082,15085,15094,15096,15102,15106,15107,15114,15129,15154,15157,15162,15192,15194,15211,15228
15241,15250,15258,15321,15328,15336,15342,15351,15375,15376,15389,15390,15404,15417,15418,15425,15429,15440,15444,15460
15526,15532,15545,15552,15558,15572,15573,15576,15577,15578,15581,15591,15602,15611,15616,15626,15630,15642,15655,15656
15666,15667,15669,15678,15701,15703,15705,15718,15722,15760,15773,15775,15795,15799,15839,15854,15863,15870,15884,15896
```

The 31 rows with more than five distinct pairs (one-based installed lines):

```text
84,2673,4946,5100,5420,5613,6501,7163,7579,7990,8041,8286,8628,9262,10709,10764,11360,12154,13172,13286,13669,13781,13962,14822,14827,14886,14970,15096,15129,15228,15884
```
