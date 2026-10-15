# Rescore measurement — the metric-identity fixes are score-neutral on every surviving run

Parent record, 2026-10-16 (goal rounds 8-9). **No model, no GPU, no dataset run, no network.** The scorer is
replayed over the per-task submissions and gold the platform already recorded, which is the calculation the
objective's own reference note invites: *"most scorer fixes can be recomputed rather than re-run."*

## What was measured

The plan (`/mnt/20t/xubuqiang/hg-work/eval-fidelity-plan.md:80`, `:198-199`) listed one open precondition
before any rescore could be claimed: *"whether every dataset's trace carries a re-parseable submission. One
cheap probe per dataset; until then the RESCORE/RERUN split in §2 is a plan, not a fact."* That probe is done
and the rescore ran.

Method: for each archived verdict, take the submission and gold that `evidence` records and call the
adapter's scorer exactly as `data/scaffolds/qa/verify/check.py:251-260` does - `score_prediction(structured,
gold)` when a structured `prediction.json` was present and the adapter is `EVIDENCE_AWARE`, otherwise
`score(prediction, gold)`. Verdicts are **multi-trial**, so each trial's own submission is rescored and the
results averaged, which is what the archived `score` is. Script: `registry/rescore-census-verdicts.py`
(auto-discovers every rescorable run from the `scorer_module` the scaffold recorded).

**Harness validation, and why it is the load-bearing step:** the archived scores were produced by the
*pre-fix* scorer, so a faithful harness must reproduce them in a pre-fix tree. It does, exactly - and the
post-fix tree reproduces them **identically**:

| tree | rescorable verdicts | agree | disagree |
| --- | ---: | ---: | ---: |
| **pre-fix** (scorers reverted to their pre-fix commits) | 4,578 | **4,578** | **0** |
| **post-fix** (HEAD) | 4,578 | **4,578** | **0** |

**Result: the two trees are indistinguishable over 4,578 archived verdicts in 10 runs.** The
metric-identity fixes change **not one** of them.

| dataset | runs | verdicts | pre-fix | post-fix |
| --- | ---: | ---: | ---: | ---: |
| `gsm8k` | 3 (`-qwen-t1-40`, `-t3-eval-full`, `-t3-train-resume-4367`) | 4,465 | 4465/4465 | 4465/4465 |
| `physicsquestions` | 3 (`-eval`, `-probe`, `-train`) | 65 | 65/65 | 65/65 |
| `fever` | 1 (`probe2-fever`) | 12 | 12/12 | 12/12 |
| `reasoning_gym` | 1 (`probe2-reasoning_gym`) | 12 | 12/12 | 12/12 |
| `triviaqa` | 1 (`probe2-triviaqa`) | 12 | 12/12 | 12/12 |
| `twowikimultihopqa` | 1 (`probe2-twowikimultihopqa`) | 12 | 12/12 | 12/12 |

`reasoning_gym` and `triviaqa` were classified **LABEL/DISCLOSURE, no metric change**, so their agreement is
a *positive control*: the harness agrees where nothing was supposed to change, which is what makes the
zero-delta on the five changed datasets meaningful rather than an artefact of a scorer that never disagrees.

## Why each fix is latent here - measured, not assumed

A fix that changes no score has to be explained, or it looks like the fix did nothing. In each case the
repaired code path was never exercised by these submissions:

| dataset | what the fix changed | why it cannot fire here |
| --- | --- | --- |
| `gsm8k` | prefer the number at the **first `####`** marker in the prediction over the last number | **0 of 3,957** trial-level predictions contain `####` |
| `physicsquestions` | strip trailing periods from the **prediction** as well as the reference | **0 of 53** predictions end in `.` |
| `twowikimultihopqa` | declare `EVIDENCE_AWARE` so the shared path scores Sup/Evi/Joint, and refuse the pair schema | **0 of 12** verdicts used a structured `prediction.json`; all 12 were plain text |
| `fever` | treat one flat exported row as **one conjunctive group** rather than as separate sufficient groups | only **1 of 12** golds carries more than one group, so at most one task could differ - and it does not |

## What this does and does not establish

**Does establish:** on every run we still hold, the fixes are **score-neutral**. The disclosure obligation
attached to those datasets - "earlier figures must not be reused as `<new metric name>`" - is therefore a
**labelling** obligation in practice, not an observed numeric change. That is stronger than the
qualification alone could support, because it is measured rather than inferred from the diff.

**Does not establish:** that the fixes are inert in general. They are **latent**: a future submission that
puts a `####` in its answer, or ends a prediction with a period, or uses the structured channel, or has a
multi-group gold, will be scored differently - correctly. The runs here simply contain no such submission.

**Scope of the evidence, stated plainly:** `gsm8k` dominates it - 4,465 of the 4,578 verdicts, across three
runs including a full eval run and a 3,106-task train resume - so GSM8K's neutrality is strong. The other
five datasets contribute 113 verdicts between them, all from probes, and their neutrality is real for those
tasks and must not be extended to the full pools.

## Coverage: 837 verdicts cannot be rescored, and 813 of them are one dataset

| dataset | runs | verdicts | why not |
| --- | ---: | ---: | --- |
| **`musique`** | **7** | **813** | **its gold is redacted**: the adapter declares `REDACT_EVIDENCE`, so `data/scaffolds/qa/verify/check.py:236-240` replaces the gold with `{"redacted": true}` in every evidence path. This is the dataset classified **LABEL-only**, so the one dataset whose finding was purely about the metric's *name* is also the one whose evidence cannot be replayed - which is why w-evidence had to corroborate `0.3064` from the current scorer rather than from historical verdicts |
| `bfcl_v3` | 1 | 12 | gold redacted by design (`data/scaffolds/qa/verify/check.py:144`, dataset set) |
| `chessbench_puzzles` | 1 | 12 | gold redacted (adapter-declared, same path) |
| `livecodebench` | 1 | 12 | **RERUN by nature**: the fix is a **timeout** (the 600 s clamp), and the child killed at 600 s recorded no per-test outcomes - no amount of rescoring recorded bytes recovers a run that needed more wall time. Its evidence does carry `per_test`, `tests` and `metric`; what is missing is a completed execution, not a string |
| `ds1000` | 1 | 12 | **RERUN by nature**: the fix moved `context.json` out of the agent's `SETUP`, so the archived run answered a *different task*; rescoring would grade a submission against inputs it never saw |
| `spreadsheetbench` | 1 | 12 | the fix changed **where** the workbook is recalculated; a wave-1 probe that already ran after the fix has no pre-fix score to revise, and the submission is a workbook, not a string |
| `hotpotqa` | - | - | **no census run exists** |
| `alfworld`, `agentdojo`, `scienceworld`, `jericho`, `bird_minidev` | - | - | `alfworld`/`agentdojo`/`scienceworld` are classified **RERUN** (`eval-fidelity-plan.md:116-117`: the instrument changed, not only the scorer); the other two have no verdicts with a recorded prediction |
| `sportsunderstanding` | - | - | no archived run at all (the plan already recorded "never run") |

### The musique redaction is deliberate - and its cost is now measured

I checked whether the 813 lost verdicts are an oversight before recording them as a limitation. They are
not: `REDACT_EVIDENCE = True` (`data/datasets/musique.py:29`) was added by `ce7f3f4b` ("restore MuSiQue and
2Wiki evaluation fidelity", 2026-10-13) together with `EVIDENCE_AWARE` and the joint-F1 policy, and the
mechanism is documented in this repository's own output contract - *"MuSiQue verifier evidence redacts gold
before prediction parsing, including invalid-artifact paths"* (`docs/musique-output-contract.md:52-53`), in
the paragraph that also says gold "live[s] only in trusted `VERIFY.inputs`". The two peer adapters that
redact give their reasons inline and both are about **private** data (`bfcl_v3.py:76` "avoid echoing
trusted BFCL gold"; `chessbench_puzzles.py:34` "the complete private reference").

MuSiQue's gold is **public** - it is the dataset w-evidence re-derived from a public mirror. So this
redaction is a **defence-in-depth consistency choice rather than a privacy requirement**, and its measured
cost is that the single dataset whose finding is **LABEL-only** - the one where replaying the archive would
have been most informative, because the claim is about the metric's *name* rather than its value - is the
one whose evidence can never be replayed. Recording the trade, not a recommendation: removing the redaction
would restore 813 verdicts to rescorability and would also start echoing a public gold into evidence, which
is a custody decision for the operator. No inline comment states musique's *motive*, unlike its two peers;
that is the only documentation gap here, and it is small.

## Reproduce

```bash
# post-fix
cd /mnt/20t/xubuqiang/Study/HarnessGrad && python3 registry/rescore-census-verdicts.py

# pre-fix: a detached worktree with only the scorers reverted, tests untouched
git worktree add --detach /tmp/wr HEAD
cd /tmp/wr
git checkout 74f47680^ -- data/datasets/gsm8k.py data/datasets/physicsquestions.py
git checkout 6b0c78ea^ -- data/datasets/twowikimultihopqa.py
git checkout 28e5dc67^ -- data/datasets/fever.py data/scaffolds/qa/evidence_scorers.py
python3 /mnt/20t/xubuqiang/Study/HarnessGrad/registry/rescore-census-verdicts.py   # absolute path
cd - && git worktree remove --force /tmp/wr
```

**Use the absolute path in the pre-fix step.** The worktree is checked out at `HEAD`, so a relative
`registry/rescore-census-verdicts.py` runs *that* tree's copy - which is how the first attempt at this
silently measured the older 1,396-verdict version and looked like a complete result.

## Three traps, all of which produced a plausible wrong answer

Each of these pointed at the fixes rather than at the harness, and each is the same shape this phase keeps
finding - **a proxy read as a result**:

* **The archived reward is the verdict's `score`**; there is no top-level `reward` key. Reading
  `verdict['reward']` compares nothing and reported **0 of 1,319 agreement**.
* **A verdict is a mean over trials.** Rescoring one sample per task "found" **37 GSM8K changes** that do
  not exist; rescoring per trial and averaging reproduces the archive exactly.
* **The receipt rounds official metrics to six decimals.** Comparing at `1e-12` reported a 2Wiki
  disagreement (`0.142857` vs `0.142857142857…`) that is formatting, not scoring. The comparison tolerance
  is `1e-6`, which is the precision the receipts actually carry.
