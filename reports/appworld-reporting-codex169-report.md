# AppWorld report ergonomics and receipt integration — Codex 169

Scope: `/tmp/hg-codex-169`, base `10e983f`. Reviewed reporting code and current
writer contracts. All test events/results are fabricated. No real AppWorld task
payload, run receipt, smoke, H0, model, service or container was accessed/executed.

## Determination

`tools/report_appworld.py` can report measured TGC and same-trial SGC from saved
`verdicts/round-N/<selected-task-id>.json` files and a public selected manifest,
without importing the adapter. It cannot recover measured TGC/SGC from the current
progress receipts or consume `events.jsonl`. Test-N/Test-C are declared source
splits from the manifest, independent of a run's train/eval side.

Observed integration gaps:

- `eval.tracing._write_progress` retains generic score, trial scores, final
  passed/kind/detail/test tally and completion state, but drops both final and
  per-trial scorer evidence. Passing its directory through `--verdicts` is
  syntactically possible; generic successes still produce null TGC/SGC. With
  multiple trials this also cannot reconstruct trial coverage from `trial_scores`.
- `eval.progress.Reporter` / `eval.console.Console` emit task/phase/beat events,
  generic task scores and round context, but no scorer metric/success evidence or
  explicit trial identity. The CLI has no `--events` input. Event completion,
  `passed`, a generic zero/one, or a round mean cannot establish TGC. Pairing event
  occurrence counts would not establish same-trial SGC.
- `harnessgrad.records._save_verdicts` preserves final scorer evidence and
  available multi-trial evidence. Historical incomplete trial lists are compacted;
  the reporter excludes their scenario conjunctions as `unaligned_trials`.
  Task-level invalid records do not identify every affected trial. Original trial
  positions cannot be recovered retrospectively.
- A manifest's source split is declared, not authenticated against release data.
  Supplied evidence split/task contradictions are rejected; absence of these
  evidence fields is allowed. The tool does not attest full official split coverage.
  It trusts the supplied round directory and does not validate common embedded
  round, run, model or harness identity across its selected receipt files.
- The report includes metric identity, normalized public-manifest hash and
  selected/task/trial coverage, but is not a staged diagnostic receipt. It does not
  bind source/model/harness hashes, endpoint, eligible pool, budgets, cleanup or
  snapshot lifecycle, and cannot authorize expansion. Its aggregate
  `unmeasured_task_trials` must not be copied as the disjoint unmeasured count in
  `eval.diagnostic_policy` receipts.

## Focused change

Report schema version 2 distinguishes four task/trial statuses:

- `measured`: trusted evidence declares the AppWorld TGC metric, `measured=true`
  and a Boolean `success`, with no invalid/unmeasured override. A measured failure
  remains zero.
- `invalid`: explicit invalid receipt or malformed claimed measurement evidence.
- `unmeasured`: a present receipt lacks evidence, declares `measured=false`, or
  carries an explicit unmeasured flag.
- `missing`: no receipt for the selected task/trial cell.

`receipts_from_verdicts` now preserves invalid and unmeasured flags separately,
including per-trial invalid flags. Previously all present non-measurements were
classified invalid. `recorded_unmeasured_task_trials` is the disjoint count of
present unmeasured cells; `unmeasured_task_trials` retains its aggregate meaning:
invalid + recorded unmeasured + missing. Only measured cells enter fractions.
The CLI help now explains the receipt directory, planned trial count, evidence
limits and fresh-output requirement.

No runner/writer format was changed. Current live progress/events remain
insufficient measurement inputs. A future integration needs selected public
metadata, explicit original trial IDs and minimal scorer evidence persisted at the
trusted writer, plus separate lifecycle/provenance binding. It must not derive
scorer evidence from generic scores or import the adapter to fill missing facts.
Live files are written non-atomically today; a future reader also needs an explicit
partial-write policy. This review did not test concurrent writes.

## Fabricated integration validation

New unique test file:
`tests/quality/test_appworld_receipt_integration_codex169.py`.
It exercises current Console/Reporter, progress writer, saved-verdict writer and
the CLI, with guarded CLI subprocesses that reject dataset/adapter imports,
dataset file access, networking and downstream execution.

The tests verify measured successes/failures, Test-N/Test-C labels, opposing
variant successes across trials (positive task means but scenario SGC zero),
compacted-history SGC refusal, missing/invalid/unmeasured separation, explicit
nonmeasurement overrides, source-split contradictions, selected-only reads,
private-field omission, existing-output preservation, help text and current
progress/event limitations. Fixtures do not represent benchmark measurements.

Validation command (pytest temporary files must stay outside the platform because
driver-based tests use `tmp_path` as a harness work root):

```sh
python3 -m pytest -q \
  tests/quality/test_appworld_receipt_integration_codex169.py \
  tests/quality/test_appworld_reporting.py \
  --basetemp=/tmp/harnessgrad-pytest-codex169-pytest-tmp-codex169
```

Result: **30 passed in 0.96s**. `git diff --check` passed. The test scratch directory
was removed after validation; no fabricated run artifacts are retained as measured
receipts. Parent review and merge remain pending.
