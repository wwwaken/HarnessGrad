# w-isolationmix: retain unmeasured rounds without mixing measured topologies

**Decision A.** Exclude explicitly unmeasured points from the curve's isolation
aggregate, while preserving them in the record. `common_class` still rejects
known/unknown mixtures and different known classes; `require_comparable` still
rejects unknown observations (`eval/verification/isolation.py:20`,
`eval/verification/isolation.py:33`). The production change is confined to
`harnessgrad/records.py:618`; the original strict pins remain at
`tests/quality/test_runtime_observations_w_obs.py:33` and
`tests/quality/test_scorer_isolation_option_b.py:316`.

Required property: **two scores produced by different known topologies never
share one aggregate; a scoreless point never blocks a record from being written.**
The direct control asserts refusal before file creation, followed by successful
writing of a known/unmeasured/known history
(`tests/quality/test_isolation_aggregate_w_isolationmix.py:116`). Its observed
message is `scorer isolation class mismatch: in-process, snapshot-service`
(`reports/w-isolationmix-evidence/aggregate-controls.txt:1`).

## FOUND: the candidate is an unmeasured event, not an unknown measured state

The original saved curves contain only H0; no candidate row reached the file
(`reports/w-isolationmix-evidence/before-bad-candidate.curve.jsonl:1`,
`reports/w-isolationmix-evidence/before-breaks-python.curve.jsonl:1`). The baseline
trace ends in the known/unknown mismatch before writing
(`reports/w-isolationmix-evidence/candidate-before.txt:59`).

To observe the rejected point without bypassing the guard, a fresh mock-driver
run loaded the original records module from the observed baseline revision
`2525a653efd3383c25601109ab22c22129664b53` into memory, captured each writer input
in memory, then called the original writer unchanged. Snapshots were persisted
only after the run, and the throwaway run root was removed
(`reports/w-isolationmix-evidence/capture_before.py:38`,
`reports/w-isolationmix-evidence/capture_before.py:44`,
`reports/w-isolationmix-evidence/capture_before.py:65`,
`reports/w-isolationmix-evidence/before-capture-summary.txt:1`). The input snapshot
is explicitly **not** the original writer's successfully persisted curve.

The captured original candidate row has `measured_by_platform: false`,
`n_scored: 0`, `per_task: {}`, `scorer_isolation_class: "unknown"`, and a named
invalid-manifest problem
(`reports/w-isolationmix-evidence/before-attempted-bad-candidate.curve.jsonl:2`).
The original guard still raised, and its persisted file still contains only H0
(`reports/w-isolationmix-evidence/before-capture-summary.txt:5`,
`reports/w-isolationmix-evidence/before-capture-persisted.curve.jsonl:1`). Thus B
would discard the candidate-rejection event the existing tests explicitly ask
to retain (`tests/quality/test_candidate_apply.py:259`,
`tests/quality/test_candidate_apply.py:762`); C would unnecessarily weaken the
score-aggregation guard (`eval/verification/isolation.py:27`).

After the fix, both actual `runs/<fixture-run-id>/curve.jsonl` copies retain H0
and the rejected candidate. The invalid-manifest and compile-error rows both
have `measured_by_platform: false`, `n_scored: 0`, `per_task: {}`, unknown class,
and their distinct named problems
(`reports/w-isolationmix-evidence/after-bad-candidate.curve.jsonl:2`,
`reports/w-isolationmix-evidence/after-breaks-python.curve.jsonl:2`). The tests
now additionally require successful driver completion and zero measured task
coverage; their previous assertions are retained
(`tests/quality/test_candidate_apply.py:258`,
`tests/quality/test_candidate_apply.py:264`,
`tests/quality/test_candidate_apply.py:770`).

The score field on these unmeasured rows is the existing numeric `0.0`
placeholder, **not a platform measurement**: empty scores produce zero through
`mean`, and the point records `n_scored: 0`
(`eval/run/metrics.py:40`, `harnessgrad/records.py:211`,
`harnessgrad/records.py:278`). This patch preserves that representation because
the record schema rejects a null required score field
(`harnessgrad/store/schema.py:153`). The guard excludes a point if its score is
explicitly null, its platform-measurement flag is explicitly false, or its
scored-task count is zero. A real zero score still participates. Missing legacy
fields do not prove nonmeasurement and therefore remain in the strict guard
(`harnessgrad/records.py:618`,
`tests/quality/test_isolation_aggregate_w_isolationmix.py:16`,
`tests/quality/test_isolation_aggregate_w_isolationmix.py:50`).

## FOUND: complete audit of the requested aggregate boundaries

Scope command: `rg -n 'common_class\(' harnessgrad eval
tests/quality/test_runtime_observations_w_obs.py
tests/quality/test_scorer_isolation_option_b.py`. Its exact output is retained in
`reports/w-isolationmix-validation.txt:306`.

| Boundary | Can scoreless/unknown input reach it? Correct behavior and disposition |
| --- | --- |
| `harnessgrad/records.py:163`, `_curve_point` | An unmeasured candidate reaches it with empty scored task IDs: the aggregate is empty and returns unknown. Scored legacy tasks can have unknown classes and must still refuse mixed classes. Already correct: `_scored` selects only measured task IDs (`harnessgrad/records.py:124`, `harnessgrad/loops/mode_a.py:492`); the new empty-point control confirms excluded task classes do not enter (`tests/quality/test_isolation_aggregate_w_isolationmix.py:107`). |
| `harnessgrad/records.py:618`, `_write_curve` | Yes, both scored and unmeasured points share the history. Fixed: validate only participating measurements before opening the destination, then write every point with its normalized class and comparability flag (`harnessgrad/records.py:623`, `harnessgrad/records.py:628`). |
| `eval/observe/tracing.py:409`, `_write_progress` | Unmeasured input reaches the function but returns through its separate invalid-record branch before this aggregate (`eval/observe/tracing.py:387`, `eval/observe/tracing.py:407`). Empty measured input is safe; scored unknown topology stays strict. Already correct; the new runner control reads both progress branches (`tests/quality/test_isolation_aggregate_w_isolationmix.py:94`). |
| `eval/run/runner.py:1214`, cached trials | Normal cached entries carry scores (`eval/run/runner.py:1332`); unmeasured tasks return before caching (`eval/run/runner.py:1181`). Missing legacy verdict classes can reach this aggregate and must remain unknown/strict. Already correct; the new control also reuses a scored zero from cache (`tests/quality/test_isolation_aggregate_w_isolationmix.py:98`). |
| `eval/run/runner.py:1262`, fresh trials | Invalid/check-unmeasured results exit before `measured.append` and before aggregation (`eval/run/runner.py:1119`, `eval/run/runner.py:1162`, `eval/run/runner.py:1179`). Scored unknown topology can reach it and must remain strict. Already correct. |
| `eval/run/runner.py:1389`, tasks | Empty/no-measurement evaluations produce an empty class map; invalid and unrun tasks are skipped (`eval/run/runner.py:1204`, `eval/run/runner.py:1239`). Only scored cached/fresh tasks populate it (`eval/run/runner.py:1212`, `eval/run/runner.py:1268`). Already correct; a valid zero beside an unmeasured task still aggregates as in-process (`tests/quality/test_isolation_aggregate_w_isolationmix.py:75`). |
| `eval/verification/isolation.py:34`, `require_comparable` | Unknown observations, including scoreless records, can reach this explicit comparison boundary. Already correct: unknown and mixed classes still raise (`eval/verification/isolation.py:34`, `tests/quality/test_isolation_aggregate_w_isolationmix.py:46`). |

## FOUND: validation

| Command scope | Before | After | Evidence |
| --- | --- | --- | --- |
| `python3 -m pytest -q tests/quality/test_candidate_apply.py` with isolated basetemp/TMPDIR | 2 failed, 30 passed | 32 passed | `reports/w-isolationmix-evidence/candidate-before.txt:119`; `reports/w-isolationmix-evidence/candidate-after.txt:2` |
| `python3 -m pytest -q tests/quality/test_runtime_observations_w_obs.py tests/quality/test_scorer_isolation_option_b.py` with isolated basetemp/TMPDIR | 53 passed, 1 skipped | 53 passed, 1 skipped | `reports/w-isolationmix-evidence/isolation-pins-before.txt:2`; `reports/w-isolationmix-evidence/isolation-pins-after.txt:2` |
| New aggregate/recording controls, including direct property control | Development assumption failure retained separately | 28 passed | `reports/w-isolationmix-evidence/aggregate-controls-initial.txt:100`; `reports/w-isolationmix-evidence/aggregate-controls.txt:4` |
| `python3 tools/check_dataset_blockers.py` | Not rerun before implementation | `{"valid": true, "datasets": 28, "shared_blockers": 0, "historical_records": 11, "production_authorized": false}` | `reports/w-isolationmix-evidence/dataset-blockers.txt:1` |

The checker reports validity, while no registry or journal changes are proposed
by this curve-only patch. The protected-file diff check, exact test commands,
full observed outputs, file sizes and scratch cleanup are recorded in
`reports/w-isolationmix-validation.txt:320`,
`reports/w-isolationmix-validation.txt:387`.

## ABSENT within an enumerated scope

The two baseline fixture curve files contain only round 0: candidate rows are
ABSENT from those files, not from memory. The complete bytes are retained above;
the exact inspection command and its output are in
`reports/w-isolationmix-validation.txt:335`.
Changes to the two original isolation test files, isolation helper, tracing,
runner, registry, journal and AGENTS.md are ABSENT from the worktree diff under
the explicitly enumerated `git diff --exit-code -- ...` command in the
validation file (`reports/w-isolationmix-validation.txt:320`). No broader absence
claim is made.

## UNKNOWN / reviewer attack point

Downstream plotting/reporting consumers were not audited for their treatment of
the existing unmeasured `score: 0.0` placeholder. A reviewer should attack whether
those consumers honor measurement coverage; this patch only fixes recording
membership (`harnessgrad/records.py:618`). Arbitrarily contradictory foreign
records, live model/GPU behavior, real container isolation, production pilots
and the full repository test suite remain unverified. The retained mock run
identifies its backend explicitly
(`reports/w-isolationmix-evidence/before-capture-driver.txt:7`).
