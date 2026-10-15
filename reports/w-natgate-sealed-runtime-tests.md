# w-natgate: verifier test route repairs

## Result and route choices

**FOUND:** ALFWorld's changed file passes **8 tests in 14.68s**. The sealed sandbox
case took **12.19s**; the generic re-materialization case took **1.58s**. Exact command,
output, and the complete measured verdict are in
`reports/w-natgate-sealed-runtime-tests-validation.txt` under `alfworld-pytest.txt`.
The supplied before-count, **2 failed, 6 passed**, is parent-provided evidence; I did
not rerun the unchanged file to reproduce it.

- `test_the_check_re_materializes_its_inputs`: **generic-route strip**. Deep-copy the
  dataset spec and remove only `native_runtime`; preserve all inputs and the
  scorer-input binding, and supply the independent selected `task_id`. The original
  measured-zero, failed-pass, and no-actions evidence assertions remain; added checks
  compare both overwritten rogue files with their trusted sources and require a
  verified consumed-input receipt. This isolates mutable-input mechanics from sealed
  admission (`tests/quality/test_alfworld_dataset.py:146`, `:150`, `:152`, `:154`,
  `:159`, `:160`). The source comment names the hp3/hp4/hostpin sealed-route controls
  (`tests/quality/test_alfworld_dataset.py:148`).
- `test_the_sandboxed_check_can_still_write_its_verdict`: **real sealed sandbox**.
  Retain the binding and real dataset inputs, supply `task_id`, and assert the
  admitted runtime's verified flag and exact spec SHA-256, in addition to the
  verified consumed input, writable reward/evidence files, and unchanged artifact
  (`tests/quality/test_alfworld_dataset.py:196`, `:198`, `:202`, `:205`, `:206`, `:210`).
  The checked-out starting revision already used `sandbox=True` here; its defect
  included the missing selected-task argument, rather than a literal false flag
  (validation: `git show HEAD:tests/quality/test_alfworld_dataset.py` starting-revision
  excerpt). No skip or parametrization was added or removed (review the test diff).

**FOUND:** The selected-task guard rejects a bound spec without `task_id`
(`eval/verification/verifier.py:526`). The native wrapper first rejects
`sandbox=False` (`eval/verification/verifier.py:474`); stripping only the native
binding would therefore leave the first test blocked by the independent input guard.

## Measured sealed verdict

The complete, unedited JSON emitted by the sandboxed test is pasted in the validation
file; its observed runtime receipt contains:

```json
{"dataset": "alfworld", "files": 2581, "identity": {"executable": "/mnt/8t/xubuqiang/anaconda3/bin/python3.12", "kernel": "6.8.0-136-generic", "machine": "x86_64", "soabi": "cpython-312-x86_64-linux-gnu", "sqlite": "3.45.3", "version": "3.12.4 | packaged by Anaconda, Inc. | (main, Jun 18 2024, 15:12:24) [GCC 11.2.0]"}, "mechanism": "sealed-memfd-private-root-v1", "sha256": "8bf87ee279e407b7a5eda8b2dc5ee85ad297d04bbc29ddf496338a4adeebd6dc", "verified": true}
```

The observed verdict has `score: 0.0`, `passed: false`, `evidence.measured: true`,
`evidence.scorer_input.verified: true`, and the explanation
`the log holds no actions, so the goal cannot have been satisfied`
(validation: `alfworld-pytest.txt`, captured stdout). This is an empty-action-log
verifier unit control, not a pilot, model run, or production H0 authorization.

## Complete relevant sandbox=False survey

**FOUND scope:** recursively search `tests/quality/` with
`rg -n 'sandbox\s*=\s*False' tests/quality/`. Full exact output and the enumerated
19-file inventory are pasted in the validation file. The inventory's dataset-name
intersection is only a screening aid; the following dispositions use the actual
specs and assertions at each cited site. Paths in this table are relative to
`tests/quality/`; every relevant hit has its own row. No other editable stale
dataset-bound call was identified in this enumerated search scope.

| File:line | Dataset or actual call | Disposition and reason |
| --- | --- | --- |
| `test_alfworld_dataset.py:153` | ALFWorld | **Fixed: strip** from a deep copy at `:150`; preserves real inputs and independently selected task while testing generic re-materialization. |
| `test_jericho_runtime_boundaries.py:143` | Synthetic Python sleep command | **Fine unchanged**: inline spec starts at `:142`, contains no native binding, and tests the host timeout. No stripping occurs. |
| `test_jericho_runtime_boundaries.py:156` | Synthetic runner task | **Fine unchanged**: tests refusal of unsandboxed `env.network=none` at `:157` / `:158`; no dataset verifier is supplied. No stripping occurs. |
| `test_measurement_coverage_hg_b3.py:92` | Synthetic timeout, in a file also mentioning ALFWorld/BIRD | **Fine unchanged**: inline `synthetic-check` spec at `:91`, not an adapter spec; timeout aggregation is the assertion. |
| `test_native_runtime_hp3.py:62` | ALFWorld / Jericho | **Fine unchanged**: this is intentionally the sealed-route sandbox-refusal negative control; asserts unmeasured and `sandbox` at `:63`. The BIRD mention at `:32` is a separate admission-only manifest fixture. |
| `test_native_runtime_hp4.py:66` | ScienceWorld / ChessBench | **Fine unchanged**: deliberately tests that retaining a sealed pin with no sandbox is refused (`:67`). |
| `test_native_runtime_hostpin.py:41` | BIRD | **Fine unchanged**: `test_pin_cannot_be_bypassed_by_no_sandbox` explicitly requires sandbox refusal (`:40`, `:42`). |
| `test_chessbench_stepwise_runner.py:253` | ChessBench stepwise task | **Fine unchanged, protected**: verifies stepwise admission refuses no-sandbox before launch (`:254`, `:255`). |
| `test_chessbench_stepwise_runner.py:308` | ChessBench stepwise evaluation | **Fine unchanged, protected**: refuses even with populated cache; requires no cache reuse, no measured tasks, and stepwise-admission invalidity (`:310`, `:311`). |
| `test_task_bound_native_inputs_w_tbi2.py:315` | ALFWorld / BIRD / Jericho / ScienceWorld cases | **Owner action: strip** in a deep copy for generic dispatch. Current bound call can satisfy the negative assertion at the earlier runtime gate, before the mocked consumption receipt is examined (`:314`, `:316`). Protected; untouched. |
| `test_task_bound_native_inputs_w_tbi2.py:323` | Same four native cases | **Owner action: strip** for a meaningful selected-task mismatch control. The current native gate can refuse before task identity is examined (`:322`, `:324`, `:326`). Protected; untouched. |
| `test_task_bound_native_inputs_w_tbi2.py:332` | Same four native cases | **Owner action: strip** for the missing-selected-task control; otherwise native admission can mask the intended refusal (`:331`, `:333`, `:335`). Protected; untouched. |
| `test_task_bound_native_inputs_w_tbi2.py:358` | Same four native cases, three modes | **Owner action: strip**: generic staging/check spies must execute. This file removes runtime directories only (`:341`, `:344`), not `native_runtime`; the process interceptor at `:357` is bypassed. Three ALFWorld modes reproduced as failures; other dataset modes not run. Protected; untouched. |
| `test_task_bound_scorer_inputs_w_tbi.py:130` | ChessBench case | **Owner action: strip** for the selected-task mismatch test; earlier native refusal can mask the intended identity check (`:129`, `:132`, `:134`). Protected; untouched. |
| `test_task_bound_scorer_inputs_w_tbi.py:152` | ChessBench case, receipt faults | **Owner action: strip** for the generic consumption-receipt test; current native gate can hide whether the mocked receipt is rejected (`:150`, `:154`). Protected; untouched. |
| `test_task_bound_scorer_inputs_w_tbi.py:164` | ChessBench matching receipt | **Owner action: strip** to reach the mocked generic verifier; reproduced failure reports `native runtime requires sandbox=True` at the reward-preservation assertion (`:166`). Protected; untouched. |
| `test_task_bound_scorer_inputs_w_tbi.py:173` | ChessBench missing selected task | **Owner action: strip** for the intended selected-task guard instead of a runtime-gate refusal (`:172`, `:174`, `:176`). Protected; untouched. |
| `test_task_bound_scorer_inputs_w_tbi.py:199` | ChessBench materialization modes | **Owner action: strip** from the existing deep copy (`:182`); the generic process/check spy at `:198` must be reached, while keeping actual scorer-input binding. Protected; not executed here. |

**FOUND — Jericho answer:** its two literal false calls do **not** strip a native
binding. The timeout call builds its synthetic command inline at
`tests/quality/test_jericho_runtime_boundaries.py:142`; the isolation refusal passes
only a synthetic task and env, with no verifier, at `:156`. The file measured
**16 passed, 1 skipped in 0.33s**; its existing missing `hg_wsnap` snapshot fixture
causes the skip (validation: `jericho-pytest.txt`).

The remaining literal-hit files in the inventory are outside the five-dataset call
scope: AppWorld actor/service controls, synthetic pristine/trial controls,
SpreadsheetBench, demo isolation, and generic verifier controls. For reproducible
inspection, the validation includes the targeted source query and its output; for
example demo isolation loads `demo` (`tests/quality/test_isolation.py:266`), and
generic verifier runner tests load `verify_demo`
(`tests/quality/test_verifier.py:258`, `:279`).

**ABSENT within an explicit protected-file scope:** the literal-pattern search has
no hits in `test_chess3_diagnostic_actor.py`, `test_chessbench_selected_control.py`,
`test_chessbench_puzzles_strict_replay.py`, `test_alfworld_official_scorer.py`,
`test_livecodebench_official_scorer.py`, and `test_ds1000_official_scorer.py`.
The exact six-path `rg` command returns exit 1 with no output (validation: `checks.txt`).
The protected SpreadsheetBench file has a hit at `:202` but builds a
SpreadsheetBench spec (`tests/quality/test_spreadsheetbench_classification_w_spread2.py:87`),
outside these five datasets; it is unchanged.

## Required checks and integration limits

**FOUND:** the requested hp3/hp4/hostpin suite measured **26 passed, 4 skipped in
52.12s**. All four skips report the pre-existing missing
`tests/fixtures/hg_whp3` fixture guard at `tests/quality/test_native_runtime_hp3.py:83`.
The sealed ALFWorld control above ran successfully; these four fixture-dependent
controls did not run (validation: `native-controls-pytest.txt`).

**FOUND:** a focused, read-only test run of the protected files measured
**4 failed, 258 deselected in 1.82s**: the ChessBench matching-identity case failed
with the sandbox gate; the three ALFWorld real-materialization modes failed with an
empty interceptor-results list (validation: `protected-findings-pytest.txt`).
These require their owners' generic-route repairs before the parent can claim the
combined suite is green. The negative controls listed above also need review for
early-refusal masking, even when their current assertions pass.

**FOUND:** `python3 tools/check_dataset_blockers.py` returned exactly:

```json
{"valid": true, "datasets": 28, "shared_blockers": 0, "historical_records": 11, "production_authorized": false}
```

This test-only repair does not change the registry; the explicit protected-path
`git diff --exit-code` check was empty with exit 0, as was `git diff --check`
(validation: `checks.txt`). No registry proposal is warranted.

**UNKNOWN / not verified:** the full quality suite, the remaining protected-file
parametrizations, missing authored replay/snapshot fixtures, live released-task
replay beyond this empty-log ALFWorld control, GPU/model execution, production
authorization, and portability to another host. The most important integration
uncertainty is whether the owners repair the protected generic-dispatch tests
without leaving negative controls that pass at the wrong gate; measured examples
and static dispositions above give the parent concrete cases to review.
