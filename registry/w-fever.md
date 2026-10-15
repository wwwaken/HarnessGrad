# w-fever: preserve exported evidence conjunctions and name both metrics

The synthetic two-sentence witness changes from strict score **1.0 before** to **0.0 after** when only the first required sentence is supplied. These are synthetic scorer results, not FEVER benchmark measurements; the exact baseline/current-code command and output are in `registry/w-fever-validation.txt:137`. The existing operator decision already selects `fever_exported_row_conjunctive_strict_at_5` (`registry/dataset-blockers.json:801`; `registry/w-fevobj-receipts.md:23`), so this implements that decision and records classification Macro-F1 components separately (`data/datasets/fever.py:43`).

## Retained source: FOUND, ABSENT, UNKNOWN

- **FOUND:** `/mnt/20t/xubuqiang/datasets/fever/valid.jsonl` has 15,935 flat-evidence rows, 9,525 non-NEI rows, and 1,400 non-NEI rows with multiple sentences; no nested evidence-group rows. This is a structure-only read, not scoring (`registry/w-fever-validation.txt:81`). The retained converter text loops over original groups and writes one flat sentence list per exported row (`registry/w-fevconv-receipts.md:374`; `registry/w-fevconv-receipts.md:390`). The historical correspondence record reports all 9,525 non-NEI rows matching complete original groups, including ordered equality; that record is cited, not independently reauthenticated here (`registry/w-fevconv-receipts.md:535`; `registry/w-fevconv-receipts.md:536`).
- **ABSENT within the enumerated readable JSON scope:** `shared_task_dev` filenames and grouped FEVER records in all regular files reached by `os.walk(..., followlinks=False)` under exactly `tests/fixtures/` (2,601 files) and `/mnt/20t/xubuqiang/datasets/fever/` (one file). The recursive JSON/document/JSONL search, exact command, and output are in `registry/w-fever-validation.txt:48`. A matching fixture object is schema metadata with dictionary-valued claim/label/evidence, not grouped claim data (clarification command and output at `registry/w-fever-validation.txt:418`). Filename search output is separately retained at `registry/w-fever-validation.txt:38`.
- **UNKNOWN:** grouped sources outside those two roots, Git history/object payloads, and the contents of the 91 fixture files that did not decode as UTF-8. No global absence or provenance claim follows from this search (`registry/w-fever-validation.txt:48`; explicit unverified scope at `registry/w-fever-validation.txt:23`).

## Reconstruction and the exact shared-scorer hunk

For a flat exported list `E = [[page, line, sentence], ...]`, wrap the entire list as `[E]`. Do not split it into `[[e] for e in E]`. The existing triple reader converts the line to `int`; page spelling, sentence content, row identity, and source order are left intact. Already nested groups retain their alternative-group structure (`data/scaffolds/qa/evidence_scorers.py:156`; synthetic flat/nested controls at `tests/quality/test_fever_w_fever.py:16` and `tests/quality/test_fever_w_fever.py:29`). The projection is owned by the shared scorer's flat-shape branch; the adapter's gold still carries the original row evidence (`data/datasets/fever.py:89`).

This cannot recover annotation IDs, missing alternative groups, or original-claim weighting (`data/datasets/fever.py:9`). The prior source record reports 51 absent alternative groups across 42 original IDs and 15,935 exported rows versus 9,835 distinct original IDs (`registry/w-fevconv-receipts.md:542`; `registry/w-fevconv-receipts.md:545`; `registry/w-fevconv-receipts.md:546`). Those are retained historical observations, not fresh counts from an original-dev payload. Groups exceeding five distinct pairs remain unable to pass at five predictions; the synthetic six-pair regression checks that behavior (`tests/quality/test_fever_w_fever.py:44`). No filtering or new source is introduced by the patch (`registry/w-fever-validation.txt:337`).

**Only one hunk touches the concurrently edited shared file** `data/scaffolds/qa/evidence_scorers.py`: zero-context header `@@ -159,3 +159,3 @@` (normal-context header `@@ -156,9 +156,9 @@`). It replaces two comment lines and `groups = [[item] for item in groups]` with two comment lines and `groups = [groups]`. Exact hunk/output: `registry/w-fever-validation.txt:337`. No HotpotQA lines change in that diff.

## Reward and secondary metric

The reward identifier is `fever_exported_row_conjunctive_strict_at_5`, following the recorded operator choice rather than choosing a new experiment objective (`registry/w-fevobj-receipts.md:23`; `data/datasets/fever.py:37`). For one valid exported-row prediction, with uppercase-only label comparison and `P5` the ordered prediction prefix:

```text
R_i = 1[label_i == prediction_i] *
      1[label_i == NOT ENOUGH INFO OR G_i is a subset of P5_i]
```

Here `G_i` is the whole flat row's exported group. General nested input uses “at least one complete group is contained in P5.” Missing predicted evidence for non-NEI gives reward 0, even for a correct label; correctly labelled NEI remains exempt (`data/scaffolds/qa/evidence_scorers.py:150`; `data/scaffolds/qa/evidence_scorers.py:162`; `data/datasets/fever.py:46`). The operator's future reporting convention averages measured trials within tasks and weights measured exported rows equally; invalid/unmeasured outcomes are not ordinary zeros (`registry/w-fevobj-receipts.md:23`). The implementation computes the binary item reward; this task adds no run aggregator.

The separate classification metric requested for this version is three-label Macro-F1. Per-task `official.classification` carries uppercase gold/predicted labels, the fixed three labels, and per-label TP/FP/FN counts (`data/datasets/fever.py:51`). Aggregate those counts over the declared measured population first:

```text
F1_c = 2 TP_c / (2 TP_c + FP_c + FN_c), or 0 when the denominator is 0
Macro-F1 = (F1_SUPPORTS + F1_REFUTES + F1_NOT_ENOUGH_INFO) / 3
```

The zero-denominator convention and aggregate requirement are explicit in the adapter docstring (`data/datasets/fever.py:12`). No per-task F1 is substituted for this aggregate. The synthetic four-item label example gives Macro-F1 `7/9`, versus accuracy `3/4`, and a right label without required evidence still contributes classification TP while its strict reward is 0 (`tests/quality/test_fever_w_fever.py:57`; `tests/quality/test_fever_w_fever.py:78`). The paper attribution is supplied by the assignment and was not independently checked; this is explicitly unverified in `registry/w-fever-validation.txt:28`.

Both metric records survive the actual standalone QA verifier's evidence writer on an authored synthetic claim (`tests/quality/test_fever_w_fever.py:95`; passing run at `registry/w-fever-validation.txt:298`). The adapter docstring, goal, and download note now name the chosen metric and evidence requirement (`data/datasets/fever.py:1`; `data/datasets/fever.py:90`; `data/datasets/fever.py:113`). The prompt still supplies only the claim and submission instructions; there is no supplied evidence corpus. This patch does not establish retrieval readiness or make label-only non-NEI answers strictly correct (`data/datasets/fever.py:19`; `data/datasets/fever.py:90`).

## Validation and integration boundary

No pre-existing `tests/quality/*fever*` file was found in the baseline Git-tree discovery (exact command and output at `registry/w-fever-validation.txt:442`); FEVER coverage was in the shared QA evidence suite and two tests selected from `test_dataset_refusals.py`. Baseline: **11 + 2 + 77 = 90 passed**, zero failures, 19 deselected (`registry/w-fever-validation.txt:101`). Final: **21 + 2 + 77 = 100 passed**, zero failures, 19 deselected; the extra ten are the new synthetic FEVER regressions (`registry/w-fever-validation.txt:298`; `tests/quality/test_fever_w_fever.py:16`). Blocker and closure counts remain 77. Two intermediate runs each had one new-test expectation failure; both exact outputs and corrections are preserved (`registry/w-fever-validation.txt:155`; `registry/w-fever-validation.txt:222`). All four owned `/tmp/fever-*-tests` roots were removed in their wrappers' `finally` blocks (the same four test ledger sections).

Required command `python3 tools/check_dataset_blockers.py` returned exactly (`registry/w-fever-validation.txt:404`):

```json
{"valid": true, "datasets": 28, "shared_blockers": 0, "historical_records": 11, "production_authorized": false}
```

FEVER remains closed under reading A as recorded at `registry/dataset-blockers.json:801`; this work proposes no blocker or journal change. The protected-path diff is empty (`registry/w-fever-validation.txt:411`). Only the two report paths specifically requested by this assignment are added under `registry/`; the source/test changes are listed in the validation byte inventory. No model/GPU/server/network fetch, FEVER dataset execution, diagnostic, pilot, historical receipt edit, or old-run resumption was performed; the ledger contains source reads and synthetic tests, and explicitly lists unverified scope (`registry/w-fever-validation.txt:6`; `registry/w-fever-validation.txt:23`). Parent review and merge remain separate.

**Most important uncertainty for review:** full original-group recovery is not established by this patch. The reconstruction relies on the retained historical correspondence and cannot restore omitted alternatives or original claim weights. Review the exported-row projection without promoting it to original-FEVER aggregate parity (`data/datasets/fever.py:9`; `registry/w-fevconv-receipts.md:535`; `registry/w-fevconv-receipts.md:545`).
