# Fidelity phase acceptance record — what was fixed, and the test that proves it

Parent record, 2026-10-16. This file exists because the goal's acceptance criteria ask for
**fail-before/pass-after evidence per fix**. That evidence was scattered across eleven workers'
validation files; this consolidates it, and for every must-fix it is **first-hand parent
evidence**, not a quotation of a worker's report.

Reproduce the fail-before half with the method in the last section. Pass-after aggregate:

```
$ TMPDIR=/tmp python3 -m pytest -q -p no:randomly \
    tests/quality/test_w_metricfix.py \
    tests/quality/test_verifier_reward_absence_w_verifierfix.py \
    tests/quality/test_spreadsheetbench_readonly_w_sbfix2.py \
    tests/quality/test_spreadsheetbench_classification_w_spread2.py \
    tests/quality/test_services.py \
    tests/quality/test_bfcl_adaptfid1.py tests/quality/test_twowiki_adaptfid1.py \
    tests/quality/test_agentdojo_bridge.py tests/quality/test_ds1000_scratch_cleanup_w_scratch.py \
    tests/quality/test_hotpot_timeout_admission_w_hotpot.py tests/quality/test_scienceworld_dataset.py \
    tests/quality/test_alfworld_dataset.py tests/quality/test_alfworld_fidelity.py \
    tests/quality/test_tau_bench_recording_w_taubench.py tests/quality/test_fever_w_fever.py
230 passed, 3 skipped in 254.65s (0:04:14)
```

## Range B — the must-fixes, each with a measured fail-before

Every row below was produced by reverting the fix commit in a throwaway worktree **while keeping its
regression test**, so the only difference from `main` is the fix.

| item | fix commit | regression test | fail-before (fix absent) | pass-after |
| --- | --- | --- | --- | --- |
| **B5** prediction `"7 km."` judged wrong though the prompt allows a period | `74f47680` | `test_w_metricfix.py::test_physics_trailing_period_on_prediction` | **FAILED** | passes |
| **B6** `"not plausible"` scored 1.0 against gold `plausible` | `74f47680` | `test_w_metricfix.py::test_sports_negation_selects_complement` | **FAILED** | passes |
| **B7** a missing reward file became a silent `0.0` | `c7018165` | `test_verifier_reward_absence_w_verifierfix.py::test_missing_snapshot_reward_is_invalid[0]` and `[3]` | **2 failed, 4 passed** | all pass |

**B7's fail-before is the clearest demonstration of the defect**, so it is quoted in full. With the fix
reverted, the test's own assertion fires and the captured stdout shows the wrong score:

```
>       assert verdict.get("unmeasured"), "a missing reward is unmeasured, never a zero"
E       AssertionError: a missing reward is unmeasured, never a zero
E       assert None
E        +  where None = ...get('unmeasured')
E        +    where ... = {'detail': 'the check wrote no /verifier/reward.txt; exit 3, stdout check starting | stderr check dependency unavailable',
                          'kind': 'command', 'passed': False, 'scorer_isolation_class': 'snapshot-service', ...}.get
--- Captured stdout call ---
{"exit_code": 3, "invalid": {}, "per_task": {"synthetic-task": 0.0}, "verdict": {... "passed": false ...}}
```

`per_task: {"synthetic-task": 0.0}` **is** the bug: no reward file was written and the run published a
zero. After the fix the same synthetic input yields `unmeasured` and keeps `detail` and the check's
stdout.

## Range C — the remaining fidelity fixes, and one that failed hardest

All of these are covered by the 230-passed set above. `74f47680` also carries **C8** and **C9**:

```
FAILED tests/quality/test_w_metricfix.py::test_gsm8k_first_marker_overrides_later_number          # C8
FAILED tests/quality/test_w_metricfix.py::test_livecodebench_correct_child_can_finish_after_600_seconds  # C9
4 failed in 0.09s
```

C9's fail-before names the clamp exactly, and the captured stdout names the wrong measurement:

```
E         Differing items:
E         {'join_budget_s': 600} != {'join_budget_s': 726}
E         {'reward': 0.0} != {'reward': 1.0}
E         {'killed': True} != {'killed': False}
E         {'passed': 0} != {'passed': 103}
--- Captured stdout call ---
reward 0: global timeout after 600s: the solution did not finish on 103 tests
```

The synthetic-input reproduction for all four `w-metricfix` cases is committed and runnable:

```
$ python3 tests/quality/test_w_metricfix.py --workdir /tmp/hg-demo
{"case": "physics", "reward": 1.0}
{"affirmative_gold_reward": 0.0, "case": "sports", "reward": 1.0}
{"case": "gsm8k", "filter": "decimal-aware-extract", "flexible_extract": "20", "reward": 1.0,
 "scored_extraction": "strict_match", "scored_value": "18", "strict_match": "18"}
reward 1: all 103 released tests passed
{"case": "livecodebench", "join_budget_s": 726, "killed": false, "passed": 103, "reward": 1.0}
```

Note the second line: `"not plausible"` against gold `"not plausible"` scores 1.0, and the same
prediction against gold `"plausible"` scores **0.0** — both directions of the B6 fix in one run.

| item | what it is | test file |
| --- | --- | --- |
| **C10** | BFCL: a line with no identifier-shaped call is not a predicted function | `test_bfcl_adaptfid1.py` |
| **C11** | 2Wiki: declare evidence-awareness / refuse the pair schema | `test_twowiki_adaptfid1.py` |
| **C12** | AgentDojo: registered attack, no in-goal defence warning, derived `TASK_COUNT` | `test_agentdojo_bridge.py` |
| **C13** | DS-1000: `context.json` out of actor `SETUP`, kept in `VERIFY.inputs` | `test_ds1000_scratch_cleanup_w_scratch.py` |
| **C14** | HotpotQA: reward is answer F1, EM in evidence, no joint figure published | `test_hotpot_timeout_admission_w_hotpot.py` |
| **C15** | ScienceWorld: `STEP_BUDGET` 100, separate observed-type macro, 29/30 declared | `test_scienceworld_dataset.py` |
| **C16** | ALFWorld: budget 50, `budget_reached` vs `budget_exhausted`, split by `__trial_` | `test_alfworld_dataset.py`, `test_alfworld_fidelity.py` |
| **17a** | τ-bench: grade the service-owned recording, accept the terminate tool as done, stop at done | `test_tau_bench_recording_w_taubench.py` |
| **17b** | FEVER: preserve the exported row's conjunctive evidence group, name the metric | `test_fever_w_fever.py` |

## Range A — the live defects on `main`

**A1, SpreadsheetBench recalculating a read-only task tree.** Fix `f5af0f78`; test
`test_spreadsheetbench_readonly_w_sbfix2.py::test_formula_result_is_compared_without_writing_frozen_task`.
Fail-before, fix reverted and test kept:

```
FAILED tests/quality/test_spreadsheetbench_readonly_w_sbfix2.py::test_formula_result_is_compared_without_writing_frozen_task[match]
FAILED tests/quality/test_spreadsheetbench_readonly_w_sbfix2.py::test_formula_result_is_compared_without_writing_frozen_task[mismatch]
2 failed, 10 warnings in 0.36s
```

The regression test does not string-match the message; it raises the **actual** error the old code hit -
`OSError(errno.EROFS, "Read-only file system", ...)` (`:45-48`) - which is `[Errno 30]`, and asserts the
frozen task tree's bytes are unchanged and scratch is empty afterwards.

**A2, a relative bind source rejected by Docker.** Fix `5e5441cc` (the operator's cherry-pick of
`b2f19e26`). Two tests, both green in the 230-passed set, and both named for the behaviour:

* `test_services.py::test_a_recording_mount_is_absolute_even_when_the_run_tree_is_relative` - its docstring
  quotes the failure verbatim (`invalid mount path: 'runs/<run-id>/recordings/...'`, `:308`) and it asserts
  the mount source is the **resolved** path (`:316`) with the reason stated (`:318`).
* `test_services.py::test_the_service_and_check_recording_mounts_are_absolute_before_docker_sees_them` -
  asserts both audiences get an absolute `src` and `running.recordings["orders"].is_absolute()` (`:342`,
  `:344`).

`tests/quality/test_services.py` alone: **45 passed in 70.95s** (parent run).

## Range D — the evidence landing

| item | landed where | status |
| --- | --- | --- |
| **18** dated qualification sentences for affected records | `registry/blocker-closure-assessment.md` "Metric-identity qualification" section + `review.notes[22]` | done; **no status changed, no closure reopened**. The registry has no closed-blocker records to attach to - 7 `datasets[*].blockers` entries, all open |
| **19** `docs/eval-split-design.md` §5c.1 + MuSiQue 0.3064 | `registry/w-evidence-doc-corrections.md`, amended twice by the parent | exact before/after produced; **the file is operator-dirty and was not edited**. Before-block re-verified verbatim against the operator's file |
| **20** the disclosure table | `registry/w-evidence-disclosure.md` | 28 rows; the `--trials N` vs `pass@k`/`test@N`/`pass^k` platform decision is stated once in the preamble as one decision reported six times |
| **21** fold scripts must keep `verdicts/` | `registry/w-evidence-archive.md` | parent-reproduced: all four archives hold **0** verdict files; three AgentDojo fold sources are absent from the census and four more source runs hold zero verdicts, so the census is a partial substitute only. The change helps **future folds only** |
| **22** the `exec` admission gate is a planning fact | journal round 5 + the disclosure preamble | recorded as a design fact, not a defect |

## Range E — the three open blockers

| dataset | blocker | state |
| --- | --- | --- |
| `bfcl_v3` | `simple-ast-contract` | preflight gate decision recorded (stays unwired, by decision, with the obligation carried in `next_action`); official scorer execution **not** run and still needs authorization |
| `triviaqa` | `hub-export-scorer-linkage` | PENDING-UPSTREAM; nothing fabricated |
| `appworld` | `successful-task-evidence` | awaiting the operator; no re-run. Its two Docker admission failures are both fixed (`a9e78d8` overlay, `5e5441cc` relative mount) |

All three have their qualification appended to their own `observed` field, and their closure options are
set out with exact registry text in `registry/w-decisionpack.md`. **No blocker was downgraded or closed.**

## How to reproduce the fail-before half

```bash
git worktree add --detach /tmp/fb HEAD
cd /tmp/fb
git revert --no-commit <fix-sha>          # stages the revert; `git diff` will look EMPTY here
git checkout HEAD -- <the regression test>  # each fix commit ADDED its test, so the revert deletes it
python3 -m pytest -q <the regression test>
```

Two traps worth recording, because the first run of this produced a useless result: `git revert
--no-commit` **stages** its changes, so a plain `git diff --stat` prints nothing (use `git diff --cached`);
and every fix commit in this phase added its own regression test, so reverting the commit deletes the test
and pytest reports `ERROR: file or directory not found` instead of a failure. Restoring the test from
`HEAD` after the revert is what makes the run meaningful - the only thing missing is then the fix.

*Not verified here:* the fail-before half for C10-C16 and item 17 (their workers' validation files record
it; I verified only the pass-after side for those), and anything requiring execution - no dataset, model,
GPU or network was used to produce this record.
