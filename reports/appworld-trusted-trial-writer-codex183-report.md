# AppWorld trusted trial evidence writer — Codex 183

Scope: isolated `/tmp/hg-codex-183`, base `d21d79d`. Saved-verdict persistence
and reporting only, with fabricated dictionaries and public synthetic manifests.
No real AppWorld payload, historical run receipt, adapter execution, scorer,
service, container, model, H0 or main-branch work was performed.

## Closure

The registry's `trusted-trial-evidence-writer` code blocker is closed for the
saved-verdict/report path. Removed only that active blocker from
`docs/dataset-blockers.json`; the successful-task measurement gate, all shared
blockers, historical records and `production_authorized=false` remain intact.
The journal and registry guide record the bounded closure.

`harnessgrad.records._saved_verdict` projects both final and per-trial verdicts
through one pure helper. Supplied evidence retains scorer metric identity,
Boolean measured/success facts, task ID and declared source split exactly.
Original one-based `trial` identities supplied on verdicts or scorer evidence
survive unchanged; explicit unaligned markers remain effective. No identity is
assigned from a compacted list's position. Every newly written anonymous trial
has `trial_aligned=false`, including anonymous single-verdict records. Thus
shortening report coverage to match survivor count cannot fabricate SGC.
Measured TGC remains available for anonymous cells, with scenario SGC excluded.

The writer persists only selected tasks present in scores, final verdicts,
trial histories or invalid/unmeasured mappings. Evidence-only and flag-only
receipts survive without a generic task score; wholly absent tasks remain
missing. Final-trial flags stay inside their trial when a history exists,
while result-level invalid/unmeasured flags apply to the task. False flags are
retained. Explicit empty histories and malformed evidence are retained for
reporter refusal instead of being silently replaced with absent evidence.

Generic `passed`, task scores, trial scores and their means do not supply
scorer metric, measured/success evidence, source split or original identity.
Diagnostic trial scores now retain only supplied scores; absent/None scores
stay null rather than being inferred from `passed`. This also permits writing
invalid/unmeasured trials carrying an explicit null score.

## Synthetic validation

New unique suite:
`tests/quality/test_appworld_trusted_trial_writer_codex183.py`. It guards the
exercised writer/report path against dataset imports/reads, external file reads,
networking and runtime subprocess execution. Existing guarded report CLI tests
also deny dataset/runtime access and check selected-only reads and private-field
omission. No generated dictionary is a benchmark result.

Coverage includes evidence-only/final/history persistence, Test-N/Test-C facts,
sparse and reordered original IDs, measured success and measured zero despite
conflicting generic values, task/trial flags, unknown scores, missing coverage,
compacted-history refusal even when report coverage equals survivor count,
malformed evidence and empty-history refusal, and input immutability. Existing
writer tests cover nested task paths and scorer tallies. Synthetic fixtures that
expect aligned SGC now supply original trial IDs; the generic trial-score fixture
supplies its explicit diagnostic scores.

Validation command (pytest scratch must be outside the platform because
driver-based tests use `tmp_path` as a harness work root):

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q \
  -p no:cacheprovider \
  tests/quality/test_appworld_trusted_trial_writer_codex183.py \
  tests/quality/test_appworld_saved_verdict_adapter_codex172.py \
  tests/quality/test_appworld_receipt_integration_codex169.py \
  tests/quality/test_appworld_reporting.py \
  tests/quality/test_trials_and_unmeasured.py::test_a_named_trial_that_failed_is_readable_on_disk \
  tests/quality/test_identity_and_verdicts.py::test_a_verdict_file_carries_the_tally_not_only_the_sentence \
  tests/quality/test_task_id_paths.py::test_a_verdict_for_a_nested_id_is_written \
  tests/quality/test_dataset_blockers.py \
  -k 'not trusted_adapter and not verifier_keeps and not missing_log' \
  --basetemp=/tmp/harnessgrad-pytest-codex183-pytest-tmp-codex183
PYTHONDONTWRITEBYTECODE=1 python3 tools/check_dataset_blockers.py
git diff --check
```

Final validation results are recorded below after execution. The original
writer failed eight of nine targeted regression probes for dropped
evidence-only/flag-only records, unselected output and discarded malformed
evidence. Four scorer/adapter tests are deliberately deselected to keep this
validation within the saved-verdict/reporting scope.

## Remaining limits

This patch preserves trusted input; it does not authenticate scorer origin or
create missing evidence. Current runner histories may lack original trial IDs;
the writer cannot recover them and now keeps those cells unaligned. Legacy
saved files are not rewritten; the adapter's historical complete-anonymous
ordering compatibility remains, subject to explicit unaligned markers.

Progress/events remain insufficient measurement inputs and are unchanged.
Production provenance, common source/split/manifest/model/harness identities,
endpoint binding, eligible coverage, budgets, quota enforcement, runtime,
snapshot and cleanup evidence remain separate requirements. This source-only
closure does not authorize a diagnostic, pilot or H0. Parent review/merge is
separate from the focused commit in this isolated worktree.
