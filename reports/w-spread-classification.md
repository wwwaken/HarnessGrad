# SpreadsheetBench classification repair - w-spread

Base: `bd9a6a75b4b98ce0c889a25bd1376db6df652b48`, isolated registered worktree
`/tmp/hg-spread`, branch `wg-spread`. Read `AGENTS.md`, HotpotQA precedent
`2a456b7` (verifier/runner diff), and
`tests/quality/test_hotpot_timeout_admission_w_hotpot.py` before implementation.

## Classification repaired; blocker remains open

Comparator/load failures now raise into the checker's explicit `measured=false`
evidence/exit-3 path, with the failing phase and exception named, and no reward
file. Formula detection and the complete LibreOffice operation (including temp
setup, process launch, conversion move and temporary-directory cleanup) share
that path. Completed value mismatches and absent result sheets still score
measured zero; a matching workbook still scores one. An absent submitted artifact
still follows the existing explicit measured-zero contract.

Only the checker changes production behavior. The adapter's command/reward/evidence
contract remains intact. No gate, refusal or admission rule was relaxed.

## Sites traced (before and after)

All `before` locations below refer to the base commit; `after` locations refer to
this worktree's final files.

- **Workbook comparator loader:**
  `data/datasets/spreadsheetbench/verify/check.py`, before 164-168, after 168-172.
  Both golden and result `load_workbook(data_only=True)` exceptions formerly
  returned `(False, str(e))`, indistinguishable from a real mismatch. They now
  raise `RuntimeError("workbook load failed: ...")` with the original cause.
- **Unparseable range:** same file, before 174-188, after 178-193. The comment
  promised unmeasured but the exception handler returned `False`; it now raises
  `ValueError` identifying the task's `answer_position` and parser failure.
- **Reference-sheet error masked by missing result sheet:** same file, before
  141-143, after 143-146. Reference sheet lookup now precedes the result-sheet
  mismatch return. A nonexistent sheet in the golden metadata cannot become a
  measured zero just because the result lacks that sheet too. A valid golden
  sheet absent only from the result remains a measured mismatch.
- **Result disappearance at comparator entry:** same file, before 162-163,
  after 165-167. The comparator now raises a named `FileNotFoundError` instead
  of returning `False`. This differs from the deliberate absent-submission
  branch in `main()`, before 335-344, after 341-350, which remains measured zero.
- **Formula probe loader:** same file, before 247-260, after 252-266. An
  unreadable result formerly became `False` (apparently formula-free), reaching
  the comparator's false/zero path. A probe-only failure could even produce a
  measured success if the later data-only loads succeeded. It now raises a
  workbook-load/formula-detection reason; no inferred formula-free success.
- **LibreOffice subprocess and conversion:** same file, before 224-244 and
  348-365, after 229-249 and 352-379. Timeout (180 seconds), nonzero exit and
  missing output already returned failure and were unmeasured. Unexpected
  process-launch, scratch/profile, file-move or cleanup exceptions escaped to
  the script's exit-4 crash handler without explicit unmeasured evidence. The
  full operation now falls inside the guarded phase, preserving the existing
  handled failure cases and naming unexpected ones `LibreOffice recalculation`.
- **Common score sink:** same file, before 369-388, after 370-388. Any normal
  `False` result wrote `measured=true`, `score=reward=0`; now loader/parser/tool
  failures cannot reach that sink. Already-raised comparison errors continue
  to be unmeasured, with a more precise phase/type reason.
- **Adapter and admission:** `data/datasets/spreadsheetbench.py:222-254,357-366`
  declares `kind=command`, stages trusted check/golden/task inputs, uses the
  files environment, and supplies reward/evidence paths and a 300-second timeout.
  It has no second comparator or score conversion to fix.
  `eval/verification/verifier.py:646-665` reads `measured=false` evidence when
  there is no reward and sets `unmeasured` to the error. Its generic in-memory
  verdict retains a numeric fallback, but `eval/run/runner.py:1102-1111,1121-1127`
  excludes that verdict before scores/cache admission and persists `invalid`
  instead. No verifier/runner change is necessary. Synthetic integration below
  checks the persisted record rather than trusting the fallback field.

## Synthetic fails-before / passes-after

`tests/quality/test_spreadsheetbench_classification_w_spread.py:29-46` names
16 cases; each runs through the checker and through the adapter's actual verifier
spec plus production verifier/runner persistence/aggregation code (32 assertions
as parametrized test cases). The fixture imports the adapter against an empty
synthetic data root, creates authored workbooks, and intercepts every subprocess;
no LibreOffice, container, sandbox, harness, model or endpoint starts.

Before changing production code, the new file produced **14 failed, 18 passed**.
The failures were the range, corrupt golden, corrupt result, formula-probe-only
load failure, LibreOffice launch, conversion move and invalid golden sheet,
each at checker and persistence level. The same file after the fix produced
**32 passed**. A completed numeric mismatch remains measured `0.0`, cached and
persisted complete; failed checks have no reward and persist an invalid reason
with no score, trial scores or complete marker, and no cache admission
(`tests/quality/test_spreadsheetbench_classification_w_spread.py:150-194`).

Combined local synthetic validation: **53 passed, 4 deselected**, including the
Hotpot timeout precedent, submission controls, and synthetic official-comparator
unit tests. The four tests that inspect/compare actual released workbooks were
explicitly deselected. Updated the inherited direct-comparator assertions for
file loss and unparseable ranges to expect exceptions; the released-range test
was updated for consistency but was not executed. Exact commands, raw regression
output and checker output: `reports/w-spread-validation.txt`.

## Gradable eligibility: defined conditions, authenticated row set not established

The source pins the **declared** mirror to KAKA22/SpreadsheetBench revision
`ab0b742b0fc95b946f212d80ac7771b5531272e4` and tarball SHA-256
`10ef893dd29cb13ab97143ea787e68cdc9574a13873ab9a54e50b31dc03fc949`
(`data/datasets/spreadsheetbench.py:77-87,257-276`). These declarations are not
fresh authentication of installed files, mirror equivalence or official scorer
custody. No installed payload was inspected or hashed in this task.

The loader requires 400 metadata rows, resolvable initial/golden workbook paths,
and a nonempty answer position (`data/datasets/spreadsheetbench.py:105-139`).
Its deterministic filename/glob fallback (`:142-168`) tolerates release naming
variants. A failure raises for the pool, not a per-row eligibility exclusion.
It does not load the workbooks or validate the named ranges/sheets, so **400
loaded rows does not imply 400 gradable rows**. `provision_status()` checks
presence and binary lookup, not authenticity or successful scoring (`:319-339`).

For a declared pool P, the default declared hash eval side is
`E_hash = {id in P: sha256(id.encode()).digest()[0] % 3 == 0}`
(`data/datasets/spreadsheetbench.py:352-354,367-372`). Setting
`HG_SPREADSHEETBENCH_SPLIT=none` makes `E_all = P`; `OFFICIAL_EVAL=None`
(`:64-71`) also makes `--split official --side eval` include the entire loaded
pool (`data/scaffolds/registry.py:218-248`). None of these split choices validates
gradability or filters bad ranges. The source-known `283-32` range `Sheet3'!A:G`
is unreadable by the parser (`check.py:178-193`); it cannot be claimed gradable.
Its SHA-256 first byte is 191, so it is outside default hash **eval** but inside
hash train and either all-eval option. This is a calculation on an ID cited in
source, not an installed-data audit or score.

A defensible pre-execution gradable set G must bind authenticated source rows,
the chosen split/side and exact initial/reference/metadata/scorer bytes; the input
workbook must be usable, the golden workbook loadable, and every named answer
range/cell/sheet valid and comparable under the pinned evaluator. Nonempty
comparisons and trustworthy reference cached values also need review; the
transcribed range parser alone is not a full eligibility validator. Formula
submissions additionally require the provisioned offline LibreOffice/runtime
and a successful recalculation before comparison. Trial-specific tool/load
failure is then recorded unmeasured, not a zero and not a retrospectively hidden
eligibility exclusion. Legitimate mismatch remains zero regardless of difficulty.

This task **cannot certify G, enumerate which installed rows meet it, or claim
399 gradable tasks**. It establishes source conditions and synthetic failure
classification only. Authenticated row-level eligibility and eligible/selected/
task/trial/invalid/unmeasured coverage remain open; no preselection manifest or
benchmark execution was created. Split membership must be intersected with a
reviewed G, with exclusions and coverage retained explicitly.

Scores are binary named-cell comparisons on the **one supplied variant**.
The paper's three-variant soft/hard aggregates remain distinct
(`data/datasets/spreadsheetbench.py:20-48,274-276`). This fix changes failure
admission, not that metric or its comparability.

## Remaining next_action clauses and registry disposition

`spreadsheetbench / dataset-journal-gap` remains `measurement`, OPEN. Updated
only its observation, evidence and next action to record the classification
repair and retain the remaining work:

- Establish authenticated row-level gradable eligibility and coverage.
- Independently authenticate installed/mirror data and scorer custody.
- Establish formula/LibreOffice offline runtime closure, including transitive
  dependencies/ABI, actual formula/cache behavior and relevant resources.
- Meet both referenced shared gates: `scorer-offline-closure` (pinned complete
  closures, official provenance/execution and trusted class-specific lifecycle,
  resource/cleanup/live controls) and `artifact-only-state-export` (authoritative
  per-task export/private-input contracts, ownership/quiescence/trial binding,
  scoring equivalence and live lifecycle/cleanup under the declared class).
- Obtain separate diagnostic authorization after those requirements; keep the
  single-variant metric distinct and never promote the repaired local control
  into production evidence.

Historical records, runs, frozen receipts and archives are untouched. No new
benchmark task, model, GPU, endpoint or paid service was used. The registry's
production authorization remains false; no blocker is removed or downgraded.
