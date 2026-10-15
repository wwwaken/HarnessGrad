# Rescore measurement — the metric-identity fixes are score-neutral on every surviving run

Parent record, 2026-10-16 (goal round 8). **No model, no GPU, no dataset run, no network.** The scorer is
replayed over the per-task submissions and gold the platform already recorded, which is the calculation the
objective's own reference note invites: *"most scorer fixes can be recomputed rather than re-run."*

## What was measured

The plan (`/mnt/20t/xubuqiang/hg-work/eval-fidelity-plan.md:80`, `:198-199`) listed one open precondition
before any rescore could be claimed: *"whether every dataset's trace carries a re-parseable submission. One
cheap probe per dataset; until then the RESCORE/RERUN split in §2 is a plan, not a fact."* That probe is
now done, and the rescore ran.

Method: for each archived verdict, take the submission and gold that `evidence` records, and call the
adapter's scorer exactly as `data/scaffolds/qa/verify/check.py:251-260` does - `score_prediction(structured,
gold)` when a structured `prediction.json` was present and the adapter is `EVIDENCE_AWARE`, otherwise
`score(prediction, gold)`. Verdicts are **multi-trial**, so each trial's own submission is rescored and the
results averaged, which is what the archived `score` is.

**Harness validation, and why it is the load-bearing step:** the archived scores were produced by the
*pre-fix* scorer, so a faithful harness must reproduce them in the pre-fix tree. It does, exactly:

| tree | gsm8k | physicsquestions | 2Wiki | fever |
| --- | --- | --- | --- | --- |
| **pre-fix** (scorers reverted to their pre-fix commits) | 1319 / 1319 | 16 / 16 and 37 / 37 | 11 / 12 | 12 / 12 |
| **post-fix** (HEAD) | 1319 / 1319 | 16 / 16 and 37 / 37 | 11 / 12 | 12 / 12 |

The single 2Wiki line is not a disagreement: the archived value is **rounded to six decimals**
(`0.142857`) while the recomputation is exact (`0.142857142857…`). That is the receipt's own formatting, and
it appears identically in both trees.

**Result: the two trees are indistinguishable.** 1,396 archived verdicts across five runs, and the
metric-identity fixes change **not one of them**.

## Why each fix is latent here - measured, not assumed

A fix that changes no score has to be explained, or it looks like the fix did nothing. In each case the
repaired code path was simply never exercised by these submissions:

| dataset | what the fix changed | why it cannot fire here |
| --- | --- | --- |
| `gsm8k` | prefer the number at the **first `####`** marker in the prediction over the last number | **0 of 3,957** trial-level predictions contain `####` |
| `physicsquestions` | strip trailing periods from the **prediction** as well as the reference | **0 of 53** predictions end in `.` |
| `twowikimultihopqa` | declare `EVIDENCE_AWARE` so the shared path scores Sup/Evi/Joint, and refuse the pair schema | **0 of 12** verdicts used a structured `prediction.json`; all 12 were plain text |
| `fever` | treat one flat exported row as **one conjunctive group** rather than as separate sufficient groups | only **1 of 12** golds carries more than one group, so at most one task could differ - and it does not |

## What this does and does not establish

**Does establish:** on every run we still hold, the fixes are **score-neutral**. The disclosure obligation
attached to those datasets - "earlier figures must not be reused as `<new metric name>`" - is therefore a
**labelling** obligation in practice, not an observed numeric change. That is a stronger position than the
qualification alone could support, because it is now measured rather than inferred from the diff.

**Does not establish:** that the fixes are inert in general. They are **latent**: a future submission that
puts a `####` in its answer, or ends a prediction with a period, or uses the structured channel, or has a
multi-group gold, will be scored differently from before - correctly. The runs here simply contain no such
submission.

**Scope of the evidence, stated plainly:** `gsm8k` is a **full eval run** (1,319 tasks x 3 trials), so its
neutrality is strong. The other four are **probes**: 16 + 37 PhysicsQuestions, 12 2Wiki, 12 FEVER. Their
neutrality is real for those tasks and should not be extended to the full pools.

## Coverage: which datasets could not be rescored, and why

| dataset | verdicts | why not |
| --- | ---: | --- |
| `bfcl_v3` | 12 | **gold is redacted by design** - `data/scaffolds/qa/verify/check.py:144` redacts for `bfcl_v3`, so the archived evidence contains `{"redacted": true}` and the scorer cannot be replayed |
| `livecodebench` | 12 | verdict evidence holds only `reward` and `why`; the "submission" is a solution artifact, not a recorded string |
| `spreadsheetbench` | 12 | same - the submission is a workbook |
| `ds1000` | 12 | holds `official` and `why` but no recorded prediction or gold |
| `hotpotqa` | - | **no census run exists** for it |
| `alfworld`, `agentdojo`, `scienceworld` | - | classified **RERUN**, not RESCORE (`eval-fidelity-plan.md:116-117`): the instrument changed, not only the scorer |
| `sportsunderstanding` | - | no archived run at all (the plan already recorded "never run") |
| `bird_minidev` | - | its census run has no `verdicts/` directory |

## Reproduce

```bash
# post-fix
cd /mnt/20t/xubuqiang/Study/HarnessGrad && python3 /mnt/20t/xubuqiang/hg-work/rescore/rescore.py

# pre-fix: a detached worktree with only the scorers reverted, tests untouched
git worktree add --detach /tmp/wr HEAD
cd /tmp/wr
git checkout 74f47680^ -- data/datasets/gsm8k.py data/datasets/physicsquestions.py
git checkout 6b0c78ea^ -- data/datasets/twowikimultihopqa.py
git checkout 28e5dc67^ -- data/datasets/fever.py data/scaffolds/qa/evidence_scorers.py
python3 /mnt/20t/xubuqiang/hg-work/rescore/rescore.py
```

Two traps worth recording, because the first run of this produced a meaningless result and looked
plausible: the archived reward is the verdict's **`score`** (there is no top-level `reward` key), so reading
`verdict['reward']` silently compares nothing and reports 100% disagreement; and the verdict is a **mean
over trials**, so a single-sample rescore disagrees with every multi-trial task - which is how the first
attempt "found" 37 GSM8K changes that do not exist. **Both errors pointed at the fixes rather than at the
harness**, which is exactly the shape this phase keeps finding: a proxy read as a result.
