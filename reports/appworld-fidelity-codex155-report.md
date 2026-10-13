# AppWorld fidelity and reusable reporting — Codex 155

2026-10-14. Workspace: `/tmp/hg-codex-155`, isolated worktree based on `8fcdcb8`.

## Delivered

- Preserved the task reward: `1.0` / `0.0` from official `TestTracker.success` (TGC). Added metric identity, task ID and declared source split to measured and unmeasured verifier evidence.
- Added `eval/appworld_reporting.py`: pure reporting from a selected manifest and trusted receipts, without importing the dataset adapter or opening dataset/gold files.
- Added scenario SGC as the conjunction of all three variants (`<scenario>_1`, `_2`, `_3`) within each trial, averaged over measured scenario trials. Partial selections, missing/invalid cells and ambiguous compacted trial histories withhold SGC rather than assigning a zero. TGC remains available from measured task cells.
- Retained `train`, `dev`, `test_normal` (Test-N) and `test_challenge` (Test-C) provenance and separate split summaries. The existing train/eval task partition and scalar scoring are unchanged.
- Added the trusted adapter's `reporting_manifest(selected_ids)`. It projects only selected public IDs, scenario/variant IDs and source splits; instructions, difficulty, databases, solutions and evaluator data are excluded. It is separate from actor tasks and SETUP.
- Preserved scorer evidence in saved single/multiple-trial verdicts. Selected invalid tasks now also get saved receipts with `score: null` and their invalid reason. Full evidence stays in trusted verdict records; generated reports project only success, metric, coverage and public provenance.
- Added `tools/report_appworld.py` to read selected saved verdicts and write a fresh JSON report. It ignores unselected files, refuses duplicate or contradictory cells, and refuses to overwrite an existing output.
- Corrected the runtime prompt and CLI help: an action executes an entire persistent Python snippet, including multiple API calls, assignments, loops and conditionals. Fabricated service tests verify unchanged snippet forwarding, multiple calls per action, printed outputs and persistent variables.

## Reuse

Supply a trusted selected manifest as a JSON list of `{task_id, source_split}` rows (or the adapter's projected manifest), and a saved round verdict directory:

```sh
python tools/report_appworld.py \
  --manifest selected.json \
  --verdicts runs/RUN/verdicts/round-0 \
  --trials 1 \
  --out fresh-appworld-report.json
```

This command postprocesses receipts; it does not execute tasks. Reports contain TGC/SGC definitions and fraction scale, a stable manifest hash, task/scenario/trial denominators, invalid/missing/unmeasured counts, split summaries and comparability notes. A null metric means no eligible measured cells, not a measured zero.

## Validation

Python 3.12.4. Final focused command:

```sh
TMPDIR="$PWD/.pytest_cache/appworld-fidelity/tmp" \
HARNESSGRAD_WORK_ROOT="$PWD/.pytest_cache/appworld-fidelity/work" \
python -m pytest -q \
  tests/quality/test_appworld_reporting.py \
  tests/quality/test_appworld_actor_protocol.py \
  tests/quality/test_appworld_service_diagnosis.py \
  tests/quality/test_trials_and_unmeasured.py::test_a_named_trial_that_failed_is_readable_on_disk \
  tests/quality/test_trials_and_unmeasured.py::test_the_runner_keeps_every_trial_s_trace_and_verdict \
  tests/quality/test_identity_and_verdicts.py::test_a_verdict_file_carries_the_tally_not_only_the_sentence \
  --basetemp="$PWD/.pytest_cache/appworld-fidelity/pytest"
```

Result: **44 passed in 3.24s**. `git diff --check` passed.

Checks include split-specific TGC/SGC arithmetic, same-trial aggregation, partial/missing/invalid coverage, compacted trial ambiguity, manifest projection and hashing, gold-field exclusion from generated reports, selected-only CLI reads, overwrite refusal, fake tracker reward/provenance, missing-log evidence, saved trial evidence, saved invalid receipts and existing generic tally persistence.

An initial fabricated verifier test failed because its `Path.is_dir` mock also affected output directory creation. The mock was narrowed to the external AppWorld data probe; subsequent focused runs passed.

## Limits and journal

Only fabricated inputs, fake AppWorld trackers, stubbed runners and a fabricated local HTTP service were used. No model calls, H0, heldout access, smoke runs, Docker execution, real dataset imports, official scorer execution, dataset preparation or GPU endpoints were used. All temporary work was directed inside this worktree.

The selected manifest supplies declared split provenance; this postprocessor does not independently validate it against a release bundle. The three-variant grouping is explicit and incompatible ID formats are refused. Historical receipts lacking TGC metric evidence stay unmeasured. Compacted partial histories retain TGC but cannot establish same-trial SGC. Reports do not certify full official split coverage, runtime readiness, cleanup, resource budgets or run comparability.

Journal: inspected code-only adapter/runtime/recording contracts; implemented projection, evidence persistence, report helper and CLI; corrected the prompt; reviewed the diff; ran the focused fabricated tests; recorded these limits. No production H0 authorization is claimed. The patch is committed in this isolated worktree for parent review and merge.
