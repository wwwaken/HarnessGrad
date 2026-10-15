# ALFWorld fidelity fixes — w-alfworld

FOUND: this worker's starting commit was `38a302e5c5edb9d1b26b0e642a40301f013f5cad`
on registered worktree `/mnt/20t/xubuqiang/hg-wt/w-alfworld`, branch
`wg-w-alfworld` (exact `git rev-parse HEAD && git worktree list --porcelain`
output: `registry/w-alfworld-validation.txt:34`). The changes below are source
fixes with synthetic controls, not a new measurement or pilot authorization.

FOUND: the shared episode cap is now **50**; adapter, CLI, replay and environment
defaults still derive from that one value (`data/datasets/alfworld/lib/gym_env.py:41`,
`data/datasets/alfworld.py:160`, `data/datasets/alfworld/cli/alf:154`). The local
upstream file `/mnt/20t/xubuqiang/datasets/alfworld/_src/repo/configs/eval_config.yaml:133`
reads verbatim `    max_nb_steps_per_episode: 50                            # terminate after this many steps`.
The exact read and output are in `registry/w-alfworld-validation.txt:4048`.
UNKNOWN: the paper itself and the local upstream checkout's revision were not
verified; the paper quotation, “we set the max number of steps per episode to be
50”, was supplied in the task. Comments that described the old 30-step protocol or
claimed its timing were updated (`data/datasets/alfworld/lib/gym_env.py:33`,
`data/datasets/alfworld.py:539`, `data/datasets/alfworld/cli/alf:29`).

The budget change can only raise a score, or leave it unchanged, when task coverage
and the existing action prefix are held fixed: success is a win at **any** step, so
extra permitted steps cannot erase an earlier win (`data/datasets/alfworld/lib/gym_env.py:105`,
`data/datasets/alfworld/verify/check.py:191`). Previously collected ALFWorld means
are therefore lower bounds under this budget correction, **not comparable 50-step
numbers**. This is a statement about the cap alone, not a prediction for a stochastic
rerun or the changed declared split; neither was executed.

FOUND: the evidence now distinguishes these observations
(`data/datasets/alfworld/verify/check.py:181`,
`tests/quality/test_alfworld_fidelity.py:86`):

| Observation | `budget_reached` | `budget_exhausted` |
| --- | --- | --- |
| Stops below cap without a win | false | false |
| Uses the cap without any win, including TextWorld `done=true` | true | true |
| Wins on the last permitted step | true | false |
| Ends early, even with extra actions in the log | false | false |

`budget_reached` means `actions_replayed >= budget`; the existing boolean
`budget_exhausted` means cap reached **and** no replayed win. `episode_done` still
records TextWorld's last `done`, and `actions_not_replayed` still records the
unreplayed suffix (`data/datasets/alfworld/verify/check.py:199`). This keeps a
terminal cap signal separate from task success; it makes no counterfactual claim
that additional steps would have solved the game. Reward and return-code logic are
unchanged (`data/datasets/alfworld/verify/check.py:191`,
`data/datasets/alfworld/verify/check.py:230`).

ABSENT: no downstream consumer of this ALFWorld evidence boolean was found in the
enumerated source scope `data/datasets/alfworld`, `tests/quality`, `eval`,
`harnessgrad`, `tools`, restricted to `*.py`, using
`rg -n 'budget_exhausted|budget_reached' ... --glob '*.py'`.
The exact command and observed matches are in
`registry/w-alfworld-validation.txt:3556`: the ALFWorld matches are its assignment,
evidence write and explanation branch; other matches use the separate harness
termination/failure-class string. That search does not establish anything about
external consumers. The existing field name/type and unfinished-at-cap meaning
are preserved, while its false negatives are corrected; it is not broadened to
all unfinished episodes.

FOUND: the declared split now hashes `task_id.split("__trial_")[0]`
(`data/datasets/alfworld.py:523`). Reading each retained `run_meta.json` and executing
the actual revised `_is_eval` function over those IDs gives the following counts;
this is offline metadata analysis, not replay or a rewrite of a frozen split
(`registry/w-alfworld-validation.txt:5110`):

| Retained directory under `/mnt/20t/xubuqiang/hg-census/runs/` | Old train/eval | Revised train/eval | Groups crossing sides, old → revised |
| --- | --- | --- | --- |
| `alfworld-qwen-t1-train` | 81 / 53 | 82 / 52 | 30 → 0 |
| `alfworld-qwen-t1-train2` | 81 / 53 | 82 / 52 | 30 → 0 |
| `alfworld-qwen-t1-eval2` | 81 / 53 | 82 / 52 | 30 → 0 |

Each manifest contains the same 134 unique task IDs across 47 game groups; 67 IDs
change sides. Repeat and reversed-order checks agree on these IDs
(`registry/w-alfworld-validation.txt:5110`). Synthetic controls additionally check
three trials per game, adding an unrelated game, both split sides, a task ID without
a trial suffix, and the `HG_ALFWORLD_SPLIT=none` override
(`tests/quality/test_alfworld_fidelity.py:156`). The declared split has changed and
historical train/eval means cannot be compared directly with its replacement.

FOUND: retained receipts corroborate the old cap. Over exactly the three directories
above and the glob `round*_traces/*.jsonl`, the train2 traces contain 28 lines with
`step 30/30` and 16 with `budget of 30 actions is spent`; eval2 contains 14 and 8
respectively. These are **matching line counts**, not counts of distinct episodes
(`registry/w-alfworld-validation.txt:5083`). Concrete examples are
`/mnt/20t/xubuqiang/hg-census/runs/alfworld-qwen-t1-train2/round0_traces/pick_and_place_simple-Vase-None-Safe-219__trial_T20190908_205221_748352.jsonl:64`
and the same file at line 67. Recorded aggregate means are 37/81 =
`0.4567901234567901` for train2 and 20/53 = `0.37735849056603776` for eval2,
as reported by each `curve.jsonl:1`; exact paths, summaries and observed file
hashes are in `registry/w-alfworld-validation.txt:5367`. These values were read,
not recomputed by running episodes or newly certified as valid measurements.

ABSENT: `curve.jsonl` and `round0_traces/.sides.json` do not exist in the enumerated
directory `alfworld-qwen-t1-train`; paths matching recursive `*evidence*` are absent
in all three enumerated run directories (exact command/output:
`registry/w-alfworld-validation.txt:5367`). UNKNOWN: the old per-episode scorer flags
were not observed, so the historical frequency of false `budget_exhausted` labels
is not asserted. The flag defect is demonstrated by synthetic controls, including
an exact-cap loss with TextWorld `done=true` (`tests/quality/test_alfworld_fidelity.py:86`;
before-fix failures: `registry/w-alfworld-validation.txt:4752`).

FOUND: custody pins need parent integration before sealed execution. Although the
registry search below is empty, `data/runtimes/alfworld-native.json:15397` pins
`/scorer/check.py`, and `data/runtimes/alfworld-native.json:15421` pins
`/scorer/gym_env.py`. Their observed old and replacement values are:

| Source | Old SHA-256 | New SHA-256 | Old → new bytes |
| --- | --- | --- | --- |
| `data/datasets/alfworld/verify/check.py` | `c4978ec4af63cf1df8cdacf8000f182307a6a2281f513791a7d6f7a46b56b741` | `a121abd799b28649771ac7197a903d23d66229029fc9abaf1d0178716efd6f7c` | 11201 → 11470 |
| `data/datasets/alfworld/lib/gym_env.py` | `46dfb6b0574c8ed391e30162c0d54ce6cd7e6030cf545ad867effaef6561e448` | `284a32de3d2cf5a7cbc449f1a71dcf41a61b9272c4091f458f7900f6a504a2f3` | 7174 → 7229 |

The unchanged manifest SHA-256 is
`8bf87ee279e407b7a5eda8b2dc5ee85ad297d04bbc29ddf496338a4adeebd6dc`, also independently
pinned at `data/runtimes/__init__.py:17`. Both current source hashes differ from its
pins (exact command/output: `registry/w-alfworld-validation.txt:5340`). The parent
must review refreshed source custody pins and the resulting independent manifest
pin; this worker did not modify either runtime file. UNKNOWN: sealed execution with
those refreshed pins and the 50-step cap has not been verified. This is the most
important remaining review target.

ABSENT: the exact scorer path, its legacy `data/alfworld/verify/check.py` spelling,
and its old SHA-256 have no hits across the 114 enumerated existing registry files,
excluding only these two worker deliverables. The exact Python search, complete
filename enumeration and empty outputs are in
`registry/w-alfworld-validation.txt:5340`. No registry index or proposal was changed.

FOUND: validation before → after was **6 passed → 6 passed** for dataset source/data
checks (2 real-environment tests deselected), **2 passed → 2 passed** for control-file
and metric-test declarations (24 tests deselected), **7 passed → 7 passed** for layout,
and **15 failed / 1 passed → 16 passed** for the new synthetic fidelity suite
(`registry/w-alfworld-validation.txt:4519`,
`registry/w-alfworld-validation.txt:4752`,
`registry/w-alfworld-validation.txt:5147`). The control selector deliberately avoids
all oracle/noop dataset executions. Synthetic controls exercise the real CLI log
boundary, replay loop and scorer with fabricated environments and inputs
(`tests/quality/test_alfworld_fidelity.py:48`,
`tests/quality/test_alfworld_fidelity.py:119`). Exact commands and outputs, including
temporary `/tmp/alfworld-*` creation and immediate removal, are in the validation
transcript. No production H0 authorization follows from these controls.

FOUND: `python3 tools/check_dataset_blockers.py` returned exactly
`{"valid": true, "datasets": 28, "shared_blockers": 0, "historical_records": 11, "production_authorized": false}`
(`registry/w-alfworld-validation.txt:5104`). The registry index and journal were not
edited; the passing checker does not test the stale runtime custody pins.
The validation transcript also lists explicit non-verifications and the byte sizes
of all files included in the commit.
