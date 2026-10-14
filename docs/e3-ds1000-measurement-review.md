# DS1000 archive measurement review — e3

Reviewed only repository metadata in `/tmp/hg-e3`. Source review is complete;
**archive acceptance is still blocked**. This review supplies reproducible local
search and source custody, but no original pilot receipt. Leave
`ds1000/host-slice-archive-review` at **measurement** and retain
`ds1000-v4-pending-review`, `effect=null`.

## Controlling next_action, read before review

> Keep archive acceptance blocked pending original selected-ID/split/host-pool provenance, original trial outcomes and timeout/error/lifecycle records; reconcile measured, invalid and unmeasured counts before considering append or comparison. Preserve ds1000-v4-pending-review with effect=null. Neither host oracle-sweep coverage nor timeout limits certify the pilot's 183 planned measurements.

The exact registry object and registry SHA-256 at read time are retained in
`tests/fixtures/e3_ds1000_review/metadata-provenance-snapshot.json`.

## What the prior review already establishes

`reports/measurement-coverage-hg-b3-review.md:124` separates the claimed
926/1000 host availability and 74 exclusions from the 61 selected platform
train-side tasks ×3, or **183 planned task-trials**. At `:141` it identifies
120/130-second configured checker deadlines and a synthetic timeout that writes
`measured=true` and reward zero. At `:150` it explicitly leaves selected IDs,
original trials, timeout/error records and archive acceptance unresolved. The
external oracle sweep and historical archive references were not opened in that
review (`:45`). This follow-up does not turn those source findings into receipt
verification.

## What this review checked

The acquisition snapshot records repository HEAD
`13fa17c451eb0cb44adcf5126fa25ccd345c47c8`, all exact command argv, exit codes,
stdout/stderr paths and SHA-256s, the explicit 566-file metadata content-search
scope, and whole-file source hashes. Raw command outputs and source-line excerpts
are checked in under `tests/fixtures/e3_ds1000_review/`; `SHA256SUMS` covers all
23 acquisition files. This is metadata evidence, without released task bodies.

The two `rg --no-ignore -n --only-matching -i` searches use explicit tracked
metadata paths from `git ls-files`, so ignore rules do not hide journal or registry
matches. They cover docs, reports, fixture metadata, the named DS1000 adapter and
checker, split helper, and related test sources. Exact run/record/score/sweep-name
hits are preserved in `original-run-exact-identity-search.stdout.txt`; host/pilot
claim hits are preserved in `pool-exact-claim-search.stdout.txt`. Tracked and
current file inventories are retained. A separate `git log --all --format=
--name-only` query covers DS1000/oracle-sweep/run-name paths in local refs; it is a
filename-history search, not an enumeration of every historical file body.

No original selected manifest, per-trial outcome ledger, timeout/error/lifecycle
record or oracle-sweep receipt was located in this scope. Exact pilot identity
hits are journal summaries, registry/history/readiness copies, the inherited
review and historical test-failure output, rather than original pilot records.
`docs/task-243-diagnostic-readiness.json:388` supplies an assessment and repeats
the pending-review record at `:412`; it does not add receipt custody. No path
outside this checkout was opened and no network, model, dataset, scorer, pilot or
whole-suite execution occurred. No historical receipt was edited.

## Established with source citations

- **Historical claims only:** `docs/adapter-integration-journal.md:317` says
  final curve pending review; `:318` gives 61 train-side tasks and 3 trials from
  the 926/1000 host slice; `:320` reports `ds1000-h0-10pct-v4` and
  `0.2076502732`; `:322` requires sample/trial/timeout verification; `:323` says
  unappended. The nominal 183 is not a verified measured-trial denominator.
- **Frozen exclusion metadata is obtainable:** `data/datasets/ds1000.py:90`
  through `:102` has 27 distinct released-row indices in 12 cause groups. AST
  literal extraction, without importing the adapter, records those exact
  indices/causes in the acquisition snapshot. At `:16` the adapter claims 47
  TensorFlow-import rows; at `:39` it places the original per-row oracle sweep
  outside git. Current source contains no complete original 926-ID host manifest
  or the 47 TensorFlow row IDs. The 27-row table is source metadata, not acquired
  proof of the historical sweep results.
- **Pool and split meaning:** `data/datasets/ds1000.py:57` identifies offered
  rows as a subset of the official simplified evaluation pool. At `:160` the
  train/eval division is platform-imposed; `data/scaffolds/qa/base.py:131` gives
  SHA-256 first-byte modulo 3 as the current split rule. Current rule bytes
  establish semantics, without certifying original 61-ID selection, host
  membership, split binding or representative coverage. Source/data pins at
  `data/datasets/ds1000.py:73` are declarations, not a historical run binding.
- **Oracle-sweep test is conditional:**
  `tests/quality/test_ds1000_official_scorer.py:152` checks the frozen table against
  the external sweep only when provisioned; `:154` skips when that receipt is
  absent. Expected 953 attempted/926 passed/27 failed counts (`:157`) are test
  assertions, not newly inspected original outcomes. This test was not run.
- **Timeout values are limits:** `data/datasets/ds1000/verify/check.py:41`
  configures 120 seconds inside and `:54` configures 130 outside. A serialized
  failing result maps to reward zero at `:55` and `measured=true` at `:62`.
  `tests/quality/test_measurement_coverage_hg_b3.py:130` supplies the synthetic
  `timed out` response; its assertions at `:143` demonstrate the flag limitation,
  not an original timeout count. No new runtime claim is made.
- **Historical custody stays pending:**
  `tests/fixtures/dataset_blockers/history-codex178.json:118` preserves the
  record/run IDs, `:120` pending-review and `:121` null effect. At `:131` it
  explicitly labels the external archive report as a citation, unopened during
  the earlier review. It is unchanged here.

## What remains and status

Obtain the original selected IDs with original split and 926-ID host-pool
provenance; bind each selected ID to all original trial outcomes, timeout/error
and lifecycle records, scorer/source/model/harness identities, endpoint and
cleanup evidence. Reconcile measured, invalid and unmeasured tasks/trials against
183 planned task-trials and the exact score denominator before any append or
comparison. Counts remain unknown rather than zero. The source review and
negative search custody are complete; the required original evidence was not
obtained. **Status remains measurement; archive effect remains null.**
