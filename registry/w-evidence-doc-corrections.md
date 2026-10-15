# Exact document corrections — w-evidence

2026-10-16. Proposed replacements only. The operator’s files were read, never written. The assigned worktree’s `docs/eval-split-design.md` ends at line 272 and has no §5c.1; the exact before block below comes from the operator’s current file and is retained in `registry/w-evidence-external-sources.md` with original line numbers. Re-check the before block immediately before applying; do not overwrite intervening operator edits.

## ALFWorld — docs/eval-split-design.md §5c.1

Source: `/mnt/20t/xubuqiang/Study/HarnessGrad/docs/eval-split-design.md:314`. **Before, verbatim:**

```markdown
* **alfworld — 134 rows, 47 distinct games.** Row ids end in `__trial_<n>` and repeat a
  game across trials; the group key is `task_id.split("__trial_")[0]`. Only 47 distinct
  games are present, 46 rows are duplicate instances, **99% of rows sit in a duplicated
  instance**, and **30 instances span both platform sides** under a naive random cut.
  Which unit is correct — 134 rows or 47 games — is an open question for the adapter
  owner, and it is a 2.85x dilution either way.
```

**After, exact replacement:**

```markdown
* **alfworld — 134 evaluated episodes, clustered in 47 task directories.** The
  134 `valid_unseen` game files are the paper's whole unseen evaluation set, not a
  2.85x-diluted sample. Each `__trial_<n>` game file is an evaluated episode with its
  own initial state; the benchmark point estimate remains the mean over all 134
  episodes. The 47 task-directory groups matter for dependence and uncertainty:
  group by `task_id.split("__trial_")[0]` when constructing a study/eval split and
  use group-aware error bars. They do not justify dividing the success rate by
  134/47 or replacing the benchmark's episode mean with a 47-group macro mean.
  The archived 0.4254 was measured under a historical 30-action budget; the adapter
  now uses the paper's 50 (`data/datasets/alfworld/lib/gym_env.py:41-44`, commit
  `cdb43ac4`), so the protocol difference is repaired in code but the archived number
  was not re-measured and must not be read as a 50-action result.
```

**Parent amendment 2026-10-16.** The sentence above read "The historical 30-action budget also differs
from the paper's 50; removing the dilution claim does not repair that protocol difference." That was
correct when written and is now incomplete: `STEP_BUDGET` is **50** on `main`
(`data/datasets/alfworld/lib/gym_env.py:44`, landed by `cdb43ac4`), and `verify/check.py:184-185` now
separates `budget_reached` from `budget_exhausted` instead of labelling truncation as exhaustion. So the
protocol gap is closed **in the code** while the archived figure predates it — the distinction a reader
needs is "archived number, old instrument" versus "current code, paper budget", not "we still differ".
Nothing else in this correction changes, and the 47-group/2.85x point is unaffected.

Evidence/limits: local source identifies the complete 134-game valid_unseen set (`data/datasets/alfworld.py:10-17`); the archive inventory independently counts 134 per-task records (`registry/w-evidence-archive-observed.json:18`, alfworld entry). The 47 clusters, distinct-state interpretation and paper 50-action protocol are inherited from the retrieved handoff (`/mnt/20t/xubuqiang/Study/HarnessGrad/docs/paper-fidelity-audit-handoff.md:231-255`), not remeasured from game payload here. Do not carry forward the former 46/99%/30 grouping numbers as new observations; that calculation was not reproduced. This correction leaves the episode success rate unchanged and corrects its interpretation; a budget change requires a new result.

## MuSiQue — label the archived 0.3064

**Required insertion alongside every use of that figure, exact text:**

> MuSiQue 0.3064 is the archived mean local joint F1, computed per task as Answer F1 × Support F1. It is not Answer F1 and is not an official MuSiQue scalar metric. The separate official Answer F1, Answer EM and Support F1 columns require retained component evidence; the scalar alone cannot reconstruct them. This is a diagnostic union of historical runs, not a newly measured comparable benchmark result.

The current scalar formula is directly observed at `data/datasets/musique.py:106-111`; official-component separation is at `docs/musique-output-contract.md:26-38`. The association of 0.3064 with that historical formula is inherited from the handoff (`/mnt/20t/xubuqiang/Study/HarnessGrad/docs/paper-fidelity-audit-handoff.md:172-174`), not a full replay: existing archive verdicts are missing and census verdict coverage is partial (`registry/w-evidence-archive.md:1`).

A bounded search of the worktree’s docs/registry Markdown excluding this worker’s own files did not retrieve a literal “0.3064 is Answer F1” sentence (exact command/output in validation). Do not invent one or replace the historical pre-repair Answer-F1 sentence at `docs/adapter-integration-journal.md:361`, which describes an earlier scorer. The concrete existing figure record is the external archive README:

Source: `/mnt/20t/xubuqiang/HarnessGrad_experiments_result/musique/loop_qwen3.5-9b-local/README.md:38`. **Before, verbatim:**

```markdown
| hop | tasks | mean | =0 | =1 | interior | Σp(1−p) | density | median s |
```

**After, exact replacement:**

```markdown
| hop | tasks | mean local joint F1 | =0 | =1 | interior | Σp(1−p) | density | median s |
```

Insert the qualification paragraph above immediately before this table; leave every numerical cell unchanged. This also labels all hop rows consistently. The operator can use the same qualification if adding 0.3064 to eval-split-design.md; it is not currently present there in the retrieved version.

**Parent verification of the figure, 2026-10-16.** The table's three hop rows are `mean` = 0.3272 (688
tasks), 0.3077 (1251) and 0.2730 (478); those task counts sum to **2417**, which is exactly the archived
per-task record count (`registry/w-evidence-archive-observed.json`). The task-weighted mean of the three
rows is `(688x0.3272 + 1251x0.3077 + 478x0.2730) / 2417` = **0.306388**, i.e. **0.3064**. So the figure the
label is for is the **task-weighted overall mean across hops**, and it is **not** any row of that table -
the unweighted mean of the three rows would be 0.3026, which is a different number. When applying the
relabel, do not attach the qualification to a hop row as if 0.3064 were one of them.

## Do not extend the MuSiQue formula sentence to 2Wiki

**Parent addition 2026-10-16.** Any wording produced alongside the MuSiQue label must **not** be shared with
2WikiMultihopQA, because the two are different formulas. MuSiQue's reward is `answer_f1 × support_f1`
(`data/datasets/musique.py:106`). 2Wiki's is **not** a product of component F1s: it multiplies the three
channel precisions (`joint_prec = answer_prec × sp_prec × evi_prec`) and the three recalls, then takes
their **harmonic mean**, with `joint_em` the product of the three EMs
(`data/datasets/twowikimultihopqa.py:476-482`); that module's own docstring states Joint F1 "is their
harmonic mean, **not** the product of the three component F1s" (`:28-29`). Fidelity handoff §3.4
previously read "MuSiQue's and 2Wiki's reward is joint F1 (answer F1 × support F1)", which is right for
MuSiQue and wrong for 2Wiki; the handoff has been corrected in place. Calling a 2Wiki figure "joint F1" is
correct; calling it "answer F1 × support F1" is not. If a 2Wiki label is needed, use: *joint F1 = harmonic
mean of the three-channel joint precision and joint recall, where each channel's precision and recall are
multiplied across answer/support/evidence.*
