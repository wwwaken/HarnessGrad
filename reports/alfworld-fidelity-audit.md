# ALFWorld adapter fidelity audit

Source of truth: `main` @ `b466b1e4`. Adapter: `data/datasets/alfworld.py` +
`data/datasets/alfworld/`. Data: `/mnt/20t/xubuqiang/datasets/alfworld`.
Run under audit: `HarnessGrad_experiments_result/alfworld/loop_qwen3.5-9b-local/`
(134/134 tasks, `full` pool, mean **0.4254**, 77 zeros / 57 ones / 0 interior).

Contract read first: `AGENTS.md`, `INTERFACE.md` §2.2 (check runs after the harness,
read-only artefacts, **exit code and score are independent**) and §2.5.7.

## 1. What `reward` is — official, binary, unreshaped

Paper: success is the ALFRED task goal — *all* goal conditions satisfied — reported as
"Success percentages"; partial credit is a separate metric, "goal-condition success
rates … given in parentheses" (Table 2). The paper's text setting fixes *"the max
number of steps per episode to be 50"*.

Ours is TextWorld's own PDDL goal flag, replayed from the action log:

- `data/datasets/alfworld/verify/check.py:188` — `reward = 1 if state["won"] else 0`
- `data/datasets/alfworld/verify/check.py:232` — `write_reward(args.reward_file, 0)`
- `data/datasets/alfworld/lib/gym_env.py:125` — `won = won or record["won"]`
- `lib/gym_env.py:71` — `textworld.EnvInfos(won=True, admissible_commands=True, extras=["gamefile"])`

`check.py:110-132` reimplements upstream's reduction
(`game_points = np.max(np.array(sequence_game_points), 0)`) and pins equality to a
verbatim copy in `tests/quality/test_alfworld_official_scorer.py`. No judge, no partial
credit, no reshaping — the paper's binary success metric. The harness's exit code is
never read (`INTERFACE.md` §2.2). **Severity: no-action.**

## 2. Is `valid_unseen` the right set? Yes — and the pool *is* the paper's split

Paper Table 1: `train 3,553 / seen 140 / unseen 134`, with per-type unseen
`24 / 18 / 31 / 23 / 21 / 17`. Our measured game-file breakdown is exactly that:

```
task_type (game files): look_at 18, pick_place 24, clean 31, cool 21, heat 23, pick_two 17
```

`data/datasets/alfworld.py:131` loads `("json_2.1.1","valid_unseen")`; `:115`
`OFFICIAL_EVAL = None`; the `full` run scored all 134. So the pool is **all of the
paper's unseen split**, not a subset. There are 255 `traj_data.json` under
`valid_unseen`; the extra ones are movable-receptacle/sliced/unsolvable and are
excluded by both the adapter (`:224`, `:234`, `:243`) and upstream
`collect_game_files` (`alfred_tw_env.py:162-186`).

**Differs:** the adapter additionally imposes a hash train/eval split
(`alfworld.py:522-549`, `_is_eval` → 53 eval / 81 train), keyed on the **full**
`task_id`, so 30 instances have trials on *both* sides. That is group leakage for the
*declared* split, and it is not a paper split. The `full` number under audit does not
use it. **Severity: should-fix** (key on `task_id.split("__trial_")[0]`). Does not
change 0.4254. Also note `README.md` in the archive wrongly says these numbers are
"not comparable to ALFWorld's published figures, which are computed on all of
valid_unseen" — the pool *is* all of valid_unseen.

## 3. 134 vs 47 — 134 is correct; the paper counts trials as games

`evaluate_dagger.py` batches over `env.reset()`, and the env's episode list is
`alfred_tw_env.py:186-187`:

```python
self.game_files.append(game_file_path)
...
print(f"Overall we have {len(self.game_files)} games in split={self.train_eval}")
self.num_games = len(self.game_files)
```

Every `game.tw-pddl` — i.e. every `__trial_` demonstration — is one evaluated
episode. Measured on disk: 134 game files in 47 task directories (41×3, 5×2, 1×1).
The three trials of `look_at_obj_in_light-AlarmClock-None-DeskLamp-308` have
**different `pddl_problem` hashes** (`b5747b4b0b71`, `a14df0386cab`, `dcff13c1b526`),
so they are distinct initial states, and their scores differed (0,1,0).

Therefore the official episode unit is the trial, and the paper's "134 games" *is*
our 134 rows. Our 134-row mean **does not over-count** relative to the paper.

What the 47 does affect is **independence**. Re-derived from the archived
`progress/round-0/*.json`:

| unit | n | mean | SE | 95% CI |
| --- | --- | --- | --- | --- |
| row (official protocol) | 134 | 0.4254 | 0.0427 | ±0.084 |
| game-macro (47 instances) | 47 | 0.4149 | 0.0529 | ±0.104 |

The point estimate moves 1.1 pp — within one SE — so there is **no dilution**. What
is wrong is the error bar: trials within a game are correlated, so the nominal row SE
understates uncertainty (design effect ≈1.5). **Severity: disclosure** on the point
estimate; **should-fix** on reporting (cluster by instance, or state the design
effect). Does not change 0.4254.

## 4. Interface fidelity — commands/observations match; the step cap does not

`gym_env.py:71-79` reproduces upstream `alfred_tw_env.py:250-274` exactly:
same `EnvInfos(won, admissible_commands, extras=["gamefile"])`, same
`[AlfredDemangler(shuffle=False), AlfredInfos]`, `shuffle=False` matching
`domain_randomization=False` on eval. Measured initial observation is the official one,
including `Your task is to: examine the alarmclock with the desklamp.` and the
admissible list (`go to desk 1`, `take …`, `heat …`, `clean …`, `examine …`).

**The step budget differs.** `lib/gym_env.py:43` — `STEP_BUDGET = 30`, justified only
as "The community/sibling-project protocol". The paper and the official config both say
50 (`configs/eval_config.yaml:133 max_nb_steps_per_episode: 50`, read by
`init_env`). This binds hard: **41 of 134 episodes (30.6%; 53% of all failures) used
exactly 30 actions** and ended with `episode ended without a win`. (Also,
`check.py:181`'s `budget_exhausted` heuristic is `len(actions) > len(replayed)`, so it
is `False` for these — the evidence mislabels cap-truncation.) **Severity: must-fix**
for comparability. Raising 30→50 can only raise the mean, so **0.4254 is a lower bound
under the paper's protocol**; already-collected scores would need a re-run.

## 5. Other differences

- `alf look` is free (`cli/alf:94`), whereas upstream `look` costs a step. It yields no
  new information. **disclosure.**
- `alf done` is not a gate (`check.py:24-30`); correct — ALFWorld has no such rule.
- The harness config that produced the run sets `max_steps: 32` (curve identity), so the
  agent has ~32 shell calls for up to 30 actions. **disclosure** — it can bind before
  the ALFWorld budget.
- `walkthrough` is stripped (`alfworld.py:195`, `:266-274`) — good, no solution leak.
- `valid_seen` is not loaded, so no in-distribution number is produced. **disclosure.**
- The paper averages success over three evaluation runs; ours is one trial. **disclosure.**

## Plain answer

**Yes.** `0.4254` is a task-success rate over **all 134 games of the paper's
`valid_unseen` (unseen) TextWorld split** — the same set and the same binary metric as
Table 1 / the TextWorld "unseen / All Tasks" column of Table 2 (35% for the trained
BUTLER::Brain). It is *not* comparable to the paper's embodied columns, and the
per-type shape is far from BUTLER's because our agent is an untrained LLM. The number
is a **lower bound**: our 30-step cap vs the paper's 50 truncates 41 episodes.
