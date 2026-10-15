# ScienceWorld adapter fidelity audit

Scope: `data/datasets/scienceworld.py` + `data/datasets/scienceworld/` at `b466b1e4`.
Source of truth: Wang et al., *ScienceWorld: Is your Agent Smarter than a 5th Grader?*
(arXiv [2203.07540](https://ar5iv.labs.arxiv.org/html/2203.07540)). Read-only audit; no
commit. Measured against the provisioned `scienceworld` 1.2.3 + staged JRE 17, and the
partial run at `/mnt/20t/xubuqiang/hg-census/runs/scienceworld-qwen-t1-train` (195 tasks).

## 1. Reward identity — the environment's own score, fraction-scaled (no-action)

**Paper.** Each subtask has method-agnostic required goals plus 2–15 optional subgoals;
meeting them "increases the agent's score", and "Scores for all tasks are normalized to
between 0 and 1" (§B.1). Table 2 reports those 0–1 numbers. Episodes end on success, on
failure, or "after reaching a maximum number of steps (we used 100 in all experiments)".

**Ours.** The Python layer has no `get_score`; `step()` returns
`score = int(round(100 * self.server.getScore()))`, and the check divides once:

- `verify/check.py:206` — `reward = max(0, min(score, 100)) / 100.0`
- `verify/check.py:181-188` — replays `actions[:args.budget]`, `score = int(info.get("score", 0))`, breaks on `done`
- `eval/verification/verifier.py:788-800` — `score = float(raw)` from the reward file, `verdict = {... "score": score}`; `eval/run/runner.py:1371` — `score = sum(scores) / len(scores)`

Measured: a real episode reports an **int** (`score=0` after one step) and the regenerated
gold path of `boil/21` reaches **100**. So `0.01/0.06/0.22/0.39/0.75/1.0` are integer
scores `1/6/22/39/75/100 / 100`. The per-task maximum is always 100 because `getScore()` is
normalized to [0,1] and multiplied by 100; `max(0, …)` mirrors `random_agent.py`'s clipping
of negative scores (the check's docstring quotes it). **No thresholding, no shaping.**

**Severity: no-action.**

## 2. Step budget 1000 vs the paper's 100 (must-fix)

**Paper:** `100` steps, and the evaluation "run 1 episode on each of its test variations".

**Ours:** `lib/scw_env.py:46` — `STEP_BUDGET = 1000`; `lib/scw_env.py:135` —
`ScienceWorldEnv("", server, envStepLimit=step_budget)`; `check.py:181` caps at the same
number. The in-code rationale is that the longest archived test path is 796 moves, so 1000
"keeps every test path available instead of turning a correct long oracle into a false zero".

**Differs:** a 10x budget on a metric that rewards reaching subgoals over time inflates
every score. **Fix:** `STEP_BUDGET = 100` and document that the oracle then fails long
paths (16.7% of archive paths exceed 100 per the test's own note). **Changes scores:
yes, downward.** It is required for any comparison with Table 2.

## 3. Pool is the paper's `test` fold — but one task type is missing, and the doc says the wrong one

**Paper:** 30 tasks, 7200 variations, split 50/25/25 per subtask, test = 1744 by the archive.

**Ours:** `test_fold()` (`scienceworld.py:173-206`) loads `test_fold.json` (1744 records,
archive sha pinned), 29 distinct task types. Identity is faithful: the fold's
`task-N-…` names are the archive's own and `infer_task` maps them to the package's names
(verified: `task-9-mendellian-genetics-(known-plant) → mendelian-genetics-known-plant`).

**Differs:** mapping the fold's 29 names onto the package's enumerated 30
(`get_task_names()`, measured: 7207 variations) leaves exactly one unmatched:
**`measure-melting-point-unknown-substance` (300 variations; paper Table 2 row 2-3)**, the
300-variation gap `7207 - 6907`. The docstring instead claims the missing task is
`identify-life-stages-2` (`scienceworld.py:49`, echoed in
`tests/quality/test_scienceworld_dataset.py`), which is **false** — that task is present
(4 test variations, `task-7-identify-life-stages-2/6..9`). Cause is upstream: the released
`goldpaths-all.zip` has no paths for 2-3, and the adapter uses it as the task set.

**Severity: should-fix** (coverage claim is wrong; overall macro average can only cover
29/30 types). **Fix:** correct the docstring, and if all 30 types are wanted, add 2-3's
test variations by the same 50/25/25 rule (≈75) from the environment. **Changes scores:**
yes at the margin.

## 4. Aggregation: variation-weighted micro vs the paper's task-type macro (must-fix for comparability)

**Paper:** the Average row is an unweighted mean over the 30 subtask rows — "DRRN achieving
an average score of 0.17 across all 30 subtasks"; recomputing the Random-Valid column gives
0.0307 ≈ 0.03.

**Ours:** `eval/run/runner.py:1371` — `score = sum(scores) / len(scores)`, i.e. every
*variation* counts once. `inclined-plane-friction-(named-surfaces)` is 348/1744 = **20%** of
our pool but 1/30 = 3.3% of the paper's average. Measured on the 195 completed tasks: micro
mean `0.0846`, macro over the 8 observed types `0.0419` — a 2x gap from weighting alone.

**Severity: must-fix for any "comparable to the paper" claim.** **Fix:** report per-type
means and macro-average them (or compare Table 2's per-type rows), and record that this is a
different functional from the platform's `score`. **Changes scores: yes.**

## 5. The declared split studies the official test fold (should-fix)

`scienceworld.py:113` declares `OFFICIAL_EVAL = None`, which `registry.py:219-249` reads as
"every task in the pool is the benchmark's evaluation set" (`eval_ids = list(ids)`). Yet
`_is_eval` (`scienceworld.py:447-456`, `sha256(id)[0] % 3 == 0`) and `_split()`
(`465-476`) put 1175/1744 of that same test fold on the `train` side. The partial run is
`side: train, split_source: declared` — 1175 hash-selected **test** variations, whose traces
a method may read. That number is neither the paper's test average nor a clean train run.
**Fix:** treat `--split official --side eval` (all 1744) as the report run; if a train side
is wanted, it must not be the benchmark's held-out set. **Changes scores: yes** (different
task set).

## 6. Action / observation fidelity (disclosure)

Agent sees official text: `cli/scw:47-60` `_replay` calls `scw_env.load_task` and prints
`env.step()`'s observation / `env.look()`. The task description is the environment's own
`env.get_task_description()` (`cli/scw:108-112`), but it is **not** in the goal: `_goal`
(`scienceworld.py:232-272`) only points at `scw_task.json`/`scw task`, despite its docstring
claiming it is rendered. The paper gives the agent `d`; ours makes it one tool call away
(recoverable, but a prompt difference). The official admissible-action list
(`info['valid']`) is **not** exposed by the CLI. The paper's Random-Valid/DRRN/KG-A2C rows
*do* use that aid; CALM/BC/TDT do not. Our agent is unaided like the latter.
**Fix:** none required; state the aid status and consider putting the description in the
goal. **Changes scores:** only via the extra tool call.

Minor: `test_fold()`'s docstring says the file carries "the 22 that are too long"
(`scienceworld.py:179`); measured count over budget is **0**. `cli/scw` header still says
"100 steps". Task simplifications are `""` (full environment), matching the paper's main
results — the paper's simplification axis is 5 simplifications / `easy` mode, not
"fast/verbose".

## Plain answer: is a finished run comparable to a paper number?

**Not as the current run is configured.** The mean of the `--split declared --side train`
run (1175 of 1744 test variations, `score_kind: training`) is a variation-weighted average
of a hash subset of the test fold with a 1000-move budget; the paper reports a 30-task
**macro** average on **all** test variations with a **100-step** budget (Table 2, "Average"
row: 0.03/0.17/0.11/0.05/0.08/0.08; per-type columns are the finer comparison).

**To make it comparable:** (a) run `--split official --side eval` — the whole 1744-task
pool; (b) set `STEP_BUDGET = 100`; (c) macro-average over the 30 task types (add
`measure-melting-point-unknown-substance` or declare 29/30); (d) report our agent as
valid-action-aided or not. With (a)–(c) per-type scores are directly comparable to Table 2's
columns and the macro average to its Average row; without (b) the numbers are inflated.
