# Producing a harness-evolution result

This page is the protocol for the one measurement this repository has never produced: an H0 → H1
improvement that survives comparison with a control. It is written because the machinery for it
exists and the *procedure* did not, and because two limits of that machinery are structural
rather than incidental and have to be known **before** a run is launched, not discovered from a
receipt afterwards.

It is not a plan for a paper and it authorizes nothing. A run still needs the operator's
authorization, an applicable split side, and a fresh run ID.

## 1. What has to be true before a delta means anything

Measured, 2026-10-05, on `terminal_bench` with `trials=3`, `jobs=4`, **five tasks**:

| run | edits | H0 → max |
| --- | --- | --- |
| `B2-noop` | **none** (`editable_surface_touched: []`) | 0.267 → 0.467 |
| `B2-rrsi` | **none** | 0.200 → 0.467 |
| `B2-llm` | `agent.py` | 0.267 → **0.000** |

The control arm moved **+0.2 with no edit at all**. On five tasks one task is worth 0.2, so that
band and one task are the same size and no improvement smaller than a task flip can be seen. The
same holds across the corpus: 96 runs have a curve, **8** have `max > H0`, and every one of the
eight is inside the band — `tau-a-r10` moved +0.018 (less than one task), `strong-model-1` used
**two** tasks, `flash-three-*` used three, and the two largest movers are the no-edit controls.

Two consequences, and neither is optional:

* **A control arm at the same configuration, in the same session.** Without it the method arm's
  movement is indistinguishable from what happens when nothing is edited. This is the one thing
  the platform's own records already prove is necessary.
* **Enough tasks that one task is small.** `full-a` used 51 and is the only run in the corpus at
  a scale where a two-task move does not dominate the number.

## 2. What each path can and cannot produce

Two limits are structural. Both were verified this round by running the code, not by reading it.

**The staged path cannot turn the significance guard on.** `staged_task_set`
(`eval/policy/diagnostic_policy.py:101-102`) refuses anything but `trials=1, jobs=1`:

    staged diagnostics and temporary pilots require trials=1, jobs=1

and the capability-floor guard is only available when both sides carry a spread
(`harnessgrad/policies.py:112`):

    "ci_available": bool(candidate_std and baseline_std)

With `trials=1` there is no spread, so `ci_available` is `False` and the guard the platform
already implements cannot fire. This is by design — a diagnostic is one task one trial — but it
means a staged run can never be the significance-guarded one.

**The staged path also withholds its score.** `_require_publication`
(`eval/policy/diagnostic_policy.py:160-170`) needs `gates.status == "passed"` plus `cleanup` and
`snapshot` receipts, and no dataset has a lifecycle receipt to bind. Measured: all three staged
diagnostics on disk (`aime`, `appworld`, `scienceworld`) report `score: None`,
`measured_tasks: 0`, `outcome: unmeasured, reason: policy_enforcement_not_observed`.

**The unstaged path publishes and grants nothing.** `driver.save_policy_receipt` returns `True`
immediately when `not staged`, which is how all 96 historical curves got their numbers. It
carries no production or H0 authorization, and that has to be said in the record rather than
implied by silence.

So the choice for the first evolution result is: run **unstaged**, record it as provisional, and
accept that the number is not production-authorized; or build the missing runtime-observation
producer first (`docs/runtime-observation-brief.md`) so a staged run can publish. The second is
the honest long path and it blocks everything else in the meantime.

## 3. The protocol

```sh
# 0. A files-environment dataset, not a container one: `aime` (60 tasks) or `gsm8k` rather
#    than `terminal_bench`, which needs Docker per task and costs an order of magnitude more.
#    Measured: one aime task ran end to end in 44.3 s with both GPUs saturated.

# 1. Calibrate the band. One arm, no method, the exact configuration the experiment will use.
python3 driver.py --harness loop --dataset <name> --split official --side eval \
  --sampling all --trials 3 --jobs <n> --rounds 0 --improver none \
  --run-id <fresh>-calib --runs-root <runs>

# 2. The same configuration again, unchanged. The difference between step 1 and step 2 IS the
#    band; if it is not smaller than the effect being claimed, stop and raise the task count.

# 3. The method arm, same tasks, same --trials, same side, no `--from-run`.
python3 driver.py --harness loop --dataset <name> --split official --side eval \
  --sampling all --trials 3 --jobs <n> --rounds <n> --improver <name> \
  --run-id <fresh>-method --runs-root <runs>

# 4. Read the two curves together. `score`, `score_std`, `n_trials`,
#    `editable_surface_touched` and `editable_surface_components` are all on the point.
```

`--side eval` with `--split official` scores the benchmark's own evaluation set. Fix the task set
for the whole experiment (`--tasks` or a `--split` file) so round 0 is not a different draw from
the rounds that follow.

## 4. What counts as a result

A round is an improvement only when **all** of these hold, and the third is what most of the
corpus fails:

1. its score is above the control arm's band from step 1-2, not merely above H0;
2. `score_std` is present and `ci_available` is `true`, so the platform's own guard could have
   fired — a `true` here means the comparison was available, not that it passed;
3. `editable_surface_touched` is non-empty **and** `editable_surface_components` names a
   component. A touched path reported as `unattributed` is an honest reading, but it is not a
   claim about a component;
4. it is monotone across rounds or, if it is not, the reversal is reported rather than dropped —
   `v9-dgm` went 0.1 → 0.2 → 0.1 and neither end of that is a result.

A null result that satisfies 1-4 is worth more than a positive one that does not. The corpus
already contains 88 flat curves and 8 false positives; one more of either adds nothing.

## 5. What is still weak

* **Attribution is close to meaningless on the base harness.** `base_harness/loop` is a single
  `agent.py`, so a `components` map would claim that one file as context *and* control *and*
  verification. The reading works and is tested, but a claim like "context handling improved"
  needs a harness whose files separate along the components first.
* **A clean decline is still a round with no child.** The `_ask_cli` fix makes a *crashed*
  improver an outage instead of a fabricated `no_change`; a round where the improver genuinely
  declines stays a no-child round, which is a fact about the method rather than about the
  platform.
* **The candidate preflight is a guarantee, not a new check.** `eval/run/candidate.py` already
  re-validates every candidate before measurement without executing it;
  `tests/quality/test_candidate_apply.py` now pins the non-execution property, which previously
  held only by an argument.
