# w-scienceworld: 100 steps and explicit task-type macro export

FOUND — the default is now 100, following the task-provided paper quotation
"we used 100 in all experiments" (`data/datasets/scienceworld/lib/scw_env.py:42`).
Long oracle paths truncate at 100. The complete 1,744-task fold remains eligible;
299 archived paths exceed 100, the longest is 796, and none exceed the previous 1,000.
The old budget filter was removed so changing the execution budget does not select an
easier task pool (`data/datasets/scienceworld.py:194`;
`registry/w-scienceworld-validation.txt:84`). `fold_excluded()` remains a compatibility
accessor returning no exclusions, while `fold_over_budget()` reports the affected paths
(`data/datasets/scienceworld.py:225`). The CLI header now describes a budgeted step and
names the shared default (`data/datasets/scienceworld/cli/scw:5`).

FOUND — the existing declared corpus-metric route can express the required macro, so no
platform metrics/runner change was needed. ScienceWorld declares `ordered_macro_mean`
with `provided_results`, where each provided result is one observed task-type mean
(`data/aggregation_policies.json:23`; `data/datasets/scienceworld.py:264`). The existing
run reward stays micro, like the other corpus adapters. The denominator reader chooses a
count, not a grouping; the adapter groups measured variations by the fold's `task_name`
first (`data/scaffolds/aggregation.py:33`; `data/datasets/scienceworld.py:254`).

FOUND — `aggregate(per_task, step_budget=...)` reports micro, macro over observed task
types, per-type means/counts, measured/unmeasured variation coverage, observed/released/
paper type counts, missing type, comparability and the truncation limit in one result
(`data/datasets/scienceworld.py:239`). Empty measurements return null means; unknown IDs,
nonfinite/out-of-range rewards and malformed source budgets fail closed. Unmeasured types
never receive invented zeroes (`tests/quality/test_aggregation_policies.py:225`;
`tests/quality/test_aggregation_policies.py:242`). The source run's budget defaults to
unknown, independently of today's configured default; historical 1,000-step scores are
not relabeled as 100-step scores (`tests/quality/test_aggregation_policies.py:233`).

Export a JSON curve point containing its measured `per_task` mapping with:

```sh
python3 -m data.datasets.scienceworld --aggregate point.json --step-budget 100
```

This is the implemented export interface, not a claim that a real point was processed
(`data/datasets/scienceworld.py:605`; synthetic CLI control:
`tests/quality/test_aggregation_policies.py:274`). Supply 100 only for a source run known
to have used 100; omit the option if unobserved. The parent must use this export when
reporting the paper-facing macro: ordinary curve `score` remains micro
(`harnessgrad/records.py:211`). The synthetic unequal-group control reports micro 0.25
and macro 0.5, with no benchmark execution (`tests/quality/test_aggregation_policies.py:193`).

FOUND — `task-7-identify-life-stages-2` is present at variations 6, 7, 8 and 9. The
corrected docstring/test name `measure-melting-point-unknown-substance` as the missing
type (`data/datasets/scienceworld.py:52`; `tests/quality/test_scienceworld_dataset.py:93`).
ABSENT — that missing-name substring has zero matches in the enumerated `tasks` list of
`data/datasets/scienceworld/test_fold.json`; the exact command and output are recorded
in `registry/w-scienceworld-validation.txt:80`. Installed 1.2.3 static task metadata,
after explicit prefix/parenthesis/spelling normalization, has 30 types versus 29 in the
committed fold, with exactly that missing type (`registry/w-scienceworld-validation.txt:125`).
A complete released-fold macro is therefore over 29/30 task types; a partial result is over
only its observed types. The paper's full 30-type Average stays null in this export
(`tests/quality/test_aggregation_policies.py:215`). The user supplied the 300-variation
upstream gap; it was not independently enumerated through the JVM in this task
(`registry/w-scienceworld-validation.txt:198`).

FOUND — changing the shared library required refreshing its sealed-runtime digest and
size plus the independent manifest pin. Only that library entry changed in the native
manifest; `check.py` was not edited (`data/runtimes/scienceworld-native.json:7052`;
`data/runtimes/__init__.py:7`; unchanged-file diff command:
`registry/w-scienceworld-validation.txt:69`). The new manifest SHA-256 is
`78ed5155efaf2d990128070bbe4f8a1af80116bb12c25d27bbc1819a54901081`.
The unchanged verifier SHA-256 is
`1acecbf19c1bb96b95e796fa2dff20b8d73e208b06f42c24214e0b06bce03a3e`.
Observed byte/pin checks and the enumerated registry literal searches are recorded in
`registry/w-scienceworld-validation.txt:162`; no registry state or journal was changed.
A new static unit control pins this dependency (`tests/quality/test_scienceworld_dataset.py:151`).

FOUND — requested unit-suite scope before: 69 passed, 1 skipped, 5 deselected; final:
91 passed, 1 skipped, 5 deselected. All five live-environment tests were deliberately
excluded to obey the no-rerun instruction, and the archive comparison skipped because
its two enumerated candidate paths are absent. Exact invocations/output, intermediate
checks and scratch cleanup are in `registry/w-scienceworld-validation.txt:19` and
`registry/w-scienceworld-validation.txt:50`. The checker output is:

```json
{"valid": true, "datasets": 28, "shared_blockers": 0, "historical_records": 11, "production_authorized": false}
```

Evidence: `registry/w-scienceworld-validation.txt:171`. This change does not edit blocker
registry state. Static/unit success is not production authorization.

UNKNOWN — the original paper/archive, the supplied 195-task retained-run micro 0.0846
versus macro 0.0419, actual JVM truncation/scoring at step 100, and full-run behavior were
not independently verified. No benchmark, GPU, model, network or full-run execution was
performed; the complete non-verification list is
`registry/w-scienceworld-validation.txt:198`. Most important review target: ensure the
planned result publication actually uses the explicit macro export, records its source
budget and labels its observed coverage/29-of-30 limit; the platform curve headline is
still the micro mean (`harnessgrad/records.py:211`; `data/datasets/scienceworld.py:288`).
