# Installed SpreadsheetBench Verified-400 structural eligibility — w-spreadelig

FOUND: **394 of 400 rows are structurally gradable without a run; six are not in that class**: one is retained only by the explicit official-range-zero compatibility policy, and five have concrete installed structural problems. The policy-inclusive candidate denominator is **395**, with all **400 released rows** still accounted for. These are structural candidate counts, never measured coverage or unconditional execution eligibility (`tests/fixtures/hg_spreadelig/summary.json:16`, `tests/fixtures/hg_spreadelig/summary.json:788`; exact audit and verification stdout in `registry/w-spreadelig-validation.txt`).

The blocker's first obligation is authenticated row-level eligibility; its coverage/runtime obligations remain separate (`registry/dataset-blockers.json:692`). Protected inputs are unchanged; only the eight worker evidence/report/proposal files are submitted for parent review (exact protected-file diff command and final staged-path check in `registry/w-spreadelig-validation.txt`).

## Closed classification vocabulary

| Class | One-sentence definition | Count |
|---|---|---:|
| `structurally_gradable` | The unique loader-selected pair opens with installed openpyxl in formula and cached-value modes, and every checker-interpreted golden reference expands to at least one addressable cell on an existing sheet. | 394 |
| `range_zero_policy_only` | The unique readable pair has exactly the previously audited `283-32` two-component `A:G` parser `ValueError`, so only the explicit compatibility zero is retained if execution reaches that branch. | 1 |
| `not_gradable_as_installed` | At least one installed workbook load, reference addressing, sheet lookup, variant-uniqueness or nonempty-expansion requirement fails, with the observed reason retained per row. | 5 |

Counts and all 400 ordered decisions are reproduced by the exact `audit.py`/`verify.py` commands in the validation log. Every object in `tests/fixtures/hg_spreadelig/eligibility.jsonl` binds its task ID, zero-based metadata index, canonical parsed-row digest, complete metadata digest, selected workbook paths/digests, reference probes, class and reason. JSONL line = metadata index + 1 (`tests/fixtures/hg_spreadelig/audit.py:253`; verifier checks the ordering). No workbook values, formula text, expected answers or scores are exported.

## Five structural problems and the compatibility row

| Task | Observation and interpretation | Evidence |
|---|---|---|
| `73-45` | `'Sheet1'!BD2:308` is accepted by the shipped parser as columns 56 through 0, then generates **zero cells**; this is structurally empty, not a `ValueError` and not the range-zero class. Whether a comparator would publish a vacuous pass was not tested. | `tests/fixtures/hg_spreadelig/eligibility.jsonl:36`, `data/datasets/spreadsheetbench/verify/check.py:119`, `data/datasets/spreadsheetbench/verify/check.py:137` |
| `130-9` | A quoted sheet name containing commas is split by the checker's literal comma separator into three components: `b2b` and ` sez` are invalid cell references and ` de` is not a sheet, although the actual sheet `b2b, sez, de` exists. | `tests/fixtures/hg_spreadelig/eligibility.jsonl:47`, `data/datasets/spreadsheetbench/verify/check.py:180`, `data/datasets/spreadsheetbench/verify/check.py:200` |
| `51090` | Both installed workbooks refuse both formula-mode and cached-value loads with underlying `ValueError: Value must be either numerical or a string containing a wildcard`; XML/ZIP readability is separate from openpyxl semantic loading. | `tests/fixtures/hg_spreadelig/eligibility.jsonl:193` |
| `54590` | Both installed workbooks have the same two-mode openpyxl load refusal and retained exception chains. | `tests/fixtures/hg_spreadelig/eligibility.jsonl:207` |
| `36764` | Both installed workbooks have the same two-mode openpyxl load refusal and retained exception chains. | `tests/fixtures/hg_spreadelig/eligibility.jsonl:262` |
| `283-32` | Both named sheets exist in both readable workbooks, but both `A:G` components raise exactly the audited `ValueError`; cell enumeration/addressability stays null, and no zero was measured here. | `tests/fixtures/hg_spreadelig/eligibility.jsonl:18`, `registry/w-metriccmp-sources/spreadsheetbench-prior-audit.txt:10`, `data/datasets/spreadsheetbench/verify/check.py:184` |

All 400 task folders contain exactly the two chosen `.xlsx` members; **794 of 800** workbooks open in both openpyxl modes, while all 800 ZIP/XML structures are readable. The inventory retains both workbook identities even on refusal (`tests/fixtures/hg_spreadelig/summary.json:43`; exact audit stdout in validation). The init workbook lacks an answer sheet in `178-22`, `395-36`, `402-43`; these rows stay structurally gradable because their golden references are valid and creating a result sheet is possible, while result-sheet behavior is a future execution question (`tests/fixtures/hg_spreadelig/eligibility.jsonl:58`, `tests/fixtures/hg_spreadelig/eligibility.jsonl:94`, `tests/fixtures/hg_spreadelig/eligibility.jsonl:97`; checker result-sheet mismatch at `data/datasets/spreadsheetbench/verify/check.py:151`).

"Cells present" is recorded in two senses: an addressable Excel cell, including a legal implicit blank, and a literal OOXML `<c r=...>` member. Each target stores `explicit_ooxml_cells`, `implicit_cells` and `merged_placeholders`; absent serialization does not invalidate an addressable blank, consistent with the checker's `None`/empty semantics (`tests/fixtures/hg_spreadelig/audit.py:53`; `data/datasets/spreadsheetbench/verify/check.py:86`). Invalid/empty references remain failed or unknown, never invented cells.

## Formula, array and metadata flags

FOUND: installed input formulas imply a possible runtime path, not successful evaluation. The detector scans **any sheet** for a **string** starting `=`; it does not branch on instruction type or explicitly reject array objects (`data/datasets/spreadsheetbench/verify/check.py:258`, `data/datasets/spreadsheetbench/verify/check.py:163`, `data/datasets/spreadsheetbench/verify/check.py:364`). The audit separately records string formulas, non-string formula cells, raw OOXML formula kinds, and an unchanged-workbook routing flag (`tests/fixtures/hg_spreadelig/audit.py:53`; `tests/fixtures/hg_spreadelig/summary.json:761`).

| Unchanged workbook structural routing | Init rows | Golden rows |
|---|---:|---:|
| String formula; engine would be required | 132 | 167 |
| String formula plus array object; engine would be required | 20 | 54 |
| Array object only; current string detector would bypass it | 7 | 69 |
| No formula observed | 238 | 107 |
| Workbook load refusal; formula route UNKNOWN | 3 | 3 |

These mutually exclusive route counts are in the exact final audit stdout and `tests/fixtures/hg_spreadelig/summary.json:761`. Golden routing is hypothetical only: the checker actually recalculates submitted results, not golden inputs (`data/datasets/spreadsheetbench/verify/check.py:367`, `data/datasets/spreadsheetbench/verify/check.py:383`). Any future submission can add/remove formulas, so actual routing, array conversion/refusal, cached-value freshness, formula correctness and comparator success stay **UNKNOWN** for every row. Array flags do not silently become exclusions or runtime approvals. Raw XML array markers are available even for workbooks whose openpyxl loads fail (inventory `xml_formula_types`).

FOUND: the metadata carries verbatim `exclude` annotations on `56225` (`ignore, initial file already passes verification`) and `56274` (`golden has data validation dropdown set to a completely different value`), and 17 instructions mention `array` (`tests/fixtures/hg_spreadelig/eligibility.jsonl:338`, `tests/fixtures/hg_spreadelig/eligibility.jsonl:339`; `tests/fixtures/hg_spreadelig/summary.json:46`). These are explicit source flags, not newly verified scoring claims. Both flagged rows satisfy structural checks; the adapter's projection ignores `exclude` and retains both (`data/datasets/spreadsheetbench.py:115`). Whether either annotation should change a separately authorized study population is **UNKNOWN** and must be resolved explicitly by its manifest owner. No deduced score or silent denominator subtraction follows.

## Authentication and analysis commands

FOUND: installed metadata is 306,533 bytes, SHA-256 `bcecaa89a005bd4e3bbe98da150a86e8062c27f262e575d5e47bd9861b3525e7`; installed archive is 14,958,255 bytes, SHA-256 `10ef893dd29cb13ab97143ea787e68cdc9574a13873ab9a54e50b31dc03fc949` (`tests/fixtures/hg_spreadelig/summary.json:4`, `tests/fixtures/hg_spreadelig/summary.json:9`; final audit asserts these exact pins). Complete metadata and all **800** freshly hashed workbook byte buffers match the pinned local archive members; digest/path/member-equality fields are per row, and the independent verifier rehashes installed files (validation commands/output). OOXML/openpyxl probes use those same hashed byte buffers (`tests/fixtures/hg_spreadelig/audit.py:53`).

Independent canonical-release authentication is **reused**, not rediscovered: `reports/w-jc2-review.md:215` binds upstream commit `49b73a94775fb489063f60ca1865e3a650079a79`, archive SHA-256 above, blob `b6baaf0f23ef5adc1cd22078f4eeb3102b4a7c72`, and all 800 default-loader members (`reports/w-jc2-review.md:230`). Prior row/split inventory is reused from `reports/w-journalcov-review.md:39`. The two exact paths `tests/fixtures/hg_wjc2` and `tests/fixtures/hg_wjournalcov` are ABSENT in this assigned checkout, so their underlying upstream response packet was **not revalidated** here (exact scoped discovery in validation). Local archive equality freshly bridges this inventory to the retained authenticated archive identity; no new independent upstream acquisition is claimed.

All 15 inspected source/review/protected-file identities are recorded in `tests/fixtures/hg_spreadelig/source-identities.json:1` and exact `sha256sum` stdout in validation.

Parser identity: `parse_cell_range` at `data/datasets/spreadsheetbench/verify/check.py:119`, with naming helpers at `data/datasets/spreadsheetbench/verify/check.py:102`, `data/datasets/spreadsheetbench/verify/check.py:111`, `data/datasets/spreadsheetbench/verify/check.py:137`; colon preflight at `data/datasets/spreadsheetbench/verify/check.py:188`, sheet/range handling at `data/datasets/spreadsheetbench/verify/check.py:200`. The AST allowlist extracts only these four primitives and adapter `_find_workbook` (`data/datasets/spreadsheetbench.py:151`), leaving module top-level code, comparisons, scorer and runtime unexecuted (`tests/fixtures/hg_spreadelig/audit.py:153`).

FOUND local checker SHA-256 is `e7131a2649a89d818a73b6b83e1b66892e41b93c53a7fee8330749146ad3ee46`, matching the inherited runtime report (`registry/w-spreadrt-runtime.md:56`) but **different from the task prompt's `5c247413ec7fe636cd6d417bc7d9bd76c1c7e8944cceae58635c7add10ba737d`**. This inventory binds observed worktree bytes only; applicability to the unobserved alternate checker is UNKNOWN and must be reviewed before reuse. No alternate checkout was read or changed. Adapter SHA-256, interpreter and openpyxl 3.1.2 identities are in `tests/fixtures/hg_spreadelig/summary.json:34` and `tests/fixtures/hg_spreadelig/summary.json:38`; exact `sha256sum` output is in validation.

Exact analysis passes, run from the assigned worktree:

```sh
TMPDIR=/tmp/spreadelig-tmp PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/hg_spreadelig/audit.py --out tests/fixtures/hg_spreadelig
TMPDIR=/tmp/spreadelig-tmp PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/hg_spreadelig/verify.py
python3 tools/check_dataset_blockers.py
```

The same audit command ran three times while refining structural fields: pass 1 established initial counts, pass 2 added separate load modes/exception chains/routing, pass 3 added literal OOXML cell-presence counts. All three exact stdout streams, final consistency output, and checker output are preserved in validation; only final inventory is authoritative. There was no dataset scorer invocation in any pass.

## Denominators and limits

FOUND default imposed split inventory remains **291 train / 109 eval**, with structural classes **286 / 108**, range-zero **1 / 0**, and not-gradable **4 / 1** respectively (`tests/fixtures/hg_spreadelig/summary.json:777`; exact audit stdout). This does not choose a run split/side or replace the already retained first-five mixed-side packet (`registry/dataset-blockers.json:692`).

A future diagnostic must report the **400 released** rows, **394 structurally gradable**, **1 policy-only zero** and **5 structural problems**, then bind its separately authorized selection and chosen split/side to this inventory. Under unchanged inputs and this structural criterion the policy-inclusive candidate pool is **395** (hash train **287**, hash eval **108**), and any different population needs its own explicit filter and counts. A run retaining structural-problem rows must show them as such and report resulting invalid/unmeasured execution evidence separately; no score is inferred here, including for the empty-expansion case. The malformed `283-32` is retained if selected/reached, and must not be silently repaired or removed (`data/datasets/spreadsheetbench/verify/check.py:184`; `registry/w-metriccmp-comparability.md:458`). Metadata exclusion flags, formula/array runtime qualification and checker-pin mismatch remain visible qualifications, so 395 is **not** a claim that 395 rows will be measurable.

This inventory is **not measured coverage, not a score, not a diagnostic, and does not authorize one**. `measured`, selected/trial/invalid/unmeasured coverage and run ID are null; execution eligibility is UNKNOWN, rather than zero failures or 400 measured tasks (`tests/fixtures/hg_spreadelig/summary.json:829`, `tests/fixtures/hg_spreadelig/verify.py:36`). It supplies structural/ineligible-task evidence only. Completed comparisons, transformation behavior on real cell values, formula correctness/cache freshness, actual scorer execution, submitted workbook behavior, selection/export/runtime admission, cleanup/snapshot execution and diagnostic comparability remain UNKNOWN. No model, GPU, endpoint, benchmark, `soffice`, `check.py` CLI or comparator was invoked (allowlisted audit code and exact commands in validation). The adopted metric remains the one-released-variant named-cell metric, distinct from three-variant soft/hard aggregates (`registry/w-metriccmp-comparability.md:475`). Withdrawn shared gates are not reinstated; the existing next action's remaining obligations and parent integration authority are preserved (`registry/dataset-blockers.json:692`).
