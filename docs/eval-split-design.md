# Eval-split design: what cross-validation can and cannot fix

This document records the split construction for the `score(N)` study, and why
cross-validation is **not** the instrument for the main claim. It exists because the
report's methodology section has to state how train/valid/eval were carved, and the
answer is dataset-specific rather than generic.

## 1. The three jobs, kept separate

Three different problems get conflated under "how do we split". They have three
different fixes, and only one of them is cross-validation.

| Job | What it protects | Correct instrument | CV's role |
| --- | --- | --- | --- |
| **Leakage** — a test task is reconstructible from a train task | the *point estimate* | **grouping** the split | none (see §3) |
| **Axis consistency** — every point on the `score(N)` curve is scored the same way | the *shape* of the curve | one **frozen** eval slice, same `split_sha` throughout | **anti-role**: rotating folds breaks it (§4) |
| **Variance** — how much of the gap is sampling noise | the *error bars* | repeated, group-disjoint fold assignments | this is the only legitimate use (§5) |

## 2. Measured leakage structure — MuSiQue dev

MuSiQue question ids encode their constituent single-hop questions
(`2hop__460946_294723`), and `question_decomposition` lists each source id, answer
and `paragraph_support_idx`. So the reuse graph is recoverable exactly, without
heuristics.

| Quantity | Value |
| --- | ---: |
| Tasks | 2417 |
| Distinct source single-hop questions | 2768 |
| Source questions reused by ≥2 tasks | 915 (33.1%) |
| Tasks sharing ≥1 source question with another task | 2173 (**89.9%**) |
| Task pairs sharing ≥1 source question | 22 889 (0.78% of all pairs) |
| **Connected components** over that relation | **544** |
| Largest component | 58 tasks (2.4%) |
| Singleton components | 244 |
| Components spanning >1 hop count | 34 |

The 0.78% figure is the misleading one. Converted to an actual split, a random
100-task eval slice leaves every eval task with about **18 train neighbours that
share a constituent question**; the number is stable at 17–19 for eval sizes 60–200.

### 2.1 The channel is shallow and diffuse, not duplication

| Overlap (shared sources ÷ union) | Pairs |
| --- | ---: |
| 0.1 | 1 089 |
| 0.2 | 3 471 |
| 0.3 | 2 902 |
| 0.4 | 503 |
| 0.5 | 3 831 |
| 0.6 | 1 819 |
| 0.8 | 6 |
| 1.0 (near-duplicate tasks) | **28** |

Literal near-duplicates are rare: only 28 task pairs (56 tasks) have an identical
source-question set — these are genuine reorderings such as
`3hop2__87184_90327_76291` versus `3hop2__90327_87184_76291`. The dominant channel is
the **shallow shared hop** (12 349 pairs at overlap 0.2–0.6). This matters for two
reasons:

* Grouping costs almost no data. The dataset is not a pile of clones, so cutting by
  group does not gut the corpus.
* But the confound is *pervasive*. It is not a handful of bad items to delete; it is
  90% of the corpus sharing one intermediate fact with something else. It cannot be
  cleaned item-wise, only partitioned group-wise.

This is the same mechanism that inflates capability claims on multi-hop data
generally: the constituent fact is memorised, so only the composition step remains
to be learned, and R1's staircase measures less than it appears to.

## 3. Why CV does not fix leakage

Plain k-fold splits the *tasks*, so each fold's test side still contains the leaked
neighbours of that fold's train side. Every fold is inflated in the same direction,
so averaging them reproduces the bias rather than cancelling it — and does so with
smaller variance, which makes the biased number look *more* trustworthy than a single
split would. Cross-validation estimates the variance of an estimator; it does not
redefine the unit of independence.

Group k-fold does fix it, but the grouping is what fixes it. CV is then just a way to
repeat the correction, not the correction itself.

The required group definition is the **transitive closure** of the shared-source
relation. If `A ~ s1 ~ B` and `B ~ s2 ~ C`, then `A`, `B` and `C` must land in one
group; a non-transitive grouping still lets leakage walk along a chain.

## 4. Why CV structurally conflicts with `score(N)`

The platform's rule is that two points belong on one axis only when `split_sha`
agrees. Rotating folds changes `split_sha` by construction, so point `N=8` and point
`N=64` would be scored on different eval sets. The curve would then move for two
reasons at once — more training data, and a different test set — and neither is
separable after the fact.

The `score(N)` curve therefore requires **one frozen eval slice for the entire
sweep**, not an averaged one.

## 5. The decision

1. **Freeze a group-disjoint eval slice.** Materialise `groups.json` from the
   connected components, then hold out whole groups until the slice reaches the
   target size. At ~4.4 tasks per group, 100 tasks is about 23 of 544 groups, so the
   remainder of the corpus is untouched. Record the resulting `split_sha`; the whole
   `N`-sweep shares it.
2. **Freeze a separate valid slice**, built the same way and disjoint from eval. It
   is used to choose configurations and checkpoints and is never an input to a
   reported number.
3. **Use CV only for variance.** Pre-register a small number (≈3) of *group-disjoint*
   fold assignments, run the full frozen pipeline under each, and report the spread
   across slices. This upgrades the existing per-point `ci95` from "within one slice"
   to "across slices". Each fold is an independent point with its own `split_sha`.
   Never select the fold, harness or checkpoint that scores best — that converts the
   slices from evidence back into a training set.
4. **Keep cross-dataset transfer (R4) on a separate axis.** No fold assignment
   addresses it; it is a different test with a different instrument.

The split mechanism already supports this: `--split declared|default|official|<file.json>`
records `split_source` and `split_sha`, so a committed `groups.json` is the only new
artifact required.

## 5b. Sizing: a floor, not a ratio

A fixed ratio cannot work here, because the eligible counts are bimodal. Measured by
enumerating each adapter's rows:

| Dataset | Eligible | 10% eval | Resolvable at 10% |
| --- | ---: | ---: | ---: |
| fever | 15 935 | 1 594 | 2.2 pp |
| twowikimultihopqa | 12 576 | 1 258 | 2.4 pp |
| chessbench_puzzles | 10 000 | 1 000 | 2.7 pp |
| gsm8k | 8 792 | 879 | 2.9 pp |
| hotpotqa | 7 405 | 740 | 3.2 pp |
| musique | 2 417 | 242 | 5.2 pp |
| strategyqa | 2 290 | 229 | 5.4 pp |
| reasoning_gym | 1 780 | 178 | 6.1 pp |
| scienceworld | 1 666 | 167 | 6.3 pp |
| bfcl_v3 | 1 040 | 104 | 8.0 pp |
| sportsunderstanding | 1 000 | 100 | 8.2 pp |
| appworld | 750 | 75 | 9.4 pp |
| bird_minidev | 500 | 50 | 11.6 pp |
| spreadsheetbench | 400 | 40 | 12.9 pp |
| tau2_bench | 278 | 28 | 15.4 pp |
| sotuqa | 74 | 7 | 30.8 pp |
| jericho | 56 | 6 | 33.3 pp |
| physicsquestions | 53 | 5 | 36.4 pp |

(Counts are unverified for `chessbench_puzzles`, whose eligible split is `test`, and
for `gsm8k`, where `train:7473 + test:1319` were summed; `bfcl_v3`'s 1040 is
`simple:400 + _answers:400 + irrelevance:240` and may overlap. `triviaqa` is large but
was not enumerated.)

### Required eval size

Per-task score sd `sigma ~= 0.291`, back-solved from the M2 measurement (sd 1.30
tasks over 20 tasks = 6.5 pp). Required `n` for a two-sided test at alpha 0.05 and
power 0.8 is `n = (2.802 * sigma / d)^2`:

| Step to resolve | Eval tasks needed |
| --- | ---: |
| 20 pp | 17 |
| 15 pp | 29 |
| 10 pp | 66 |
| 8 pp | 104 |
| 5 pp | 265 |
| 3 pp | 737 |

### The rule

```
eval  = clamp(ceil(0.10 * eligible),  EVAL_FLOOR = 150, EVAL_CAP = 500)
valid = clamp(ceil(0.10 * eligible),  VALID_FLOOR = 50,  VALID_CAP = 150)
train = eligible - eval - valid          # and whole groups only
```

* **Floor 150** — 10 pp needs 66 tasks and 8 pp needs 104, so 150 leaves margin and
  resolves about 6.7 pp. Below it, do not emit a point.
* **Cap 500** — 500 tasks already resolves 3.6 pp, and the sweep is about 12 `N`
  points x 3 trials x 2 harnesses, so 500 already means ~36k task-runs per dataset.
  Taking 10% of `fever` would be 3.2x that for no gain.
* **Valid 50–150** — valid only selects checkpoints and does not need a tenth of the
  corpus. What it does not take, train keeps.

Note that the current mechanism is not 10%: `data/qa/base.py::is_eval` takes a
deterministic **third** (`sha256(id)[0] % 3 == 0`). Moving to this rule cuts eval by
3.3x and raises MuSiQue's floor from 2.9 pp to 5.2 pp, in exchange for 23 pp more
train for the `N`-sweep. That is a deliberate trade of resolution for train range,
not a strict improvement.

### The declaration this forces: `curve_eligible`

A dataset below the floor must not silently emit a noisy point. It should declare
that it does not carry the R1/R2 curve, exactly as `UNCOVERED_DEMANDS` and
`UNCOVERED_FUNCTIONS` declare gaps, while remaining usable for other claims
(transfer, coverage). Two independent conditions:

1. `eligible - eval - valid >= MIN_TRAIN` (about 300), so the curve has range.
2. `largest_component_ratio` is small enough that the floor is reachable without one
   group dominating the corpus.

Under those conditions the curve is carried by 13 datasets (`fever` through
`bird_minidev`). `spreadsheetbench` (400) and `tau2_bench` (278) can support a
single-point harness comparison (resolving ~13 pp) but not a sweep. `jericho` (56)
and `physicsquestions` (53) cannot support either.

Finally, eval size and `--trials` reduce different noises — eval size reduces
task-sampling noise, trials reduce run-to-run noise. Neither substitutes for the
other, and `--trials >= 3` remains required.

### Small datasets: a coverage problem, not a splitting problem

Small datasets come in two kinds, and pooling does not rescue either.

**Small but in a populated cell.** `physicsquestions` (53) sits in
`reasoning/reasoning` with 13 915 tasks, so it is 0.38% of its cell. Even a 50%
improvement in it moves the cell mean by 0.19 pp, far below the noise floor, and
`gsm8k`'s 8792 tasks would drown it. Pooling therefore helps the *cell* and not the
dataset. If the claim is cell-level the dataset contributes nothing measurable; if
the claim is dataset-level the dataset can never carry it. **Pooling is not worth
doing.**

**Small and alone in its cell.** Measured singleton cells:

| Cell | Dataset | Eligible |
| --- | --- | ---: |
| `artifact/spreadsheet` | spreadsheetbench | 400 |
| `artifact/text_to_sql` | bird_minidev | 500 |
| `environment/interactive_fiction` | jericho | **56** |
| `environment/embodied_text` | alfworld | not enumerated |
| `environment/terminal` | terminal_bench | not enumerated |
| `environment/science_simulation` | scienceworld | 1666 |
| `reasoning/planning_and_search` | chessbench_puzzles | 10 000 |

`chessbench_puzzles` and `scienceworld` are singletons *and* large, and carry a curve
normally. Singleton-ness and smallness are independent properties; only their
intersection is a problem.

The key consequence: **`jericho` at 56 tasks is not a splitting problem.** It is the
sole member of `environment/interactive_fiction`, which violates
`MIN_MEMBERS_PER_DEMAND = 2`. The platform already has a mechanism for that — the
two-way below-floor declaration. So its handling is a coverage declaration, not a new
split rule.

### Tiering

| Tier | Condition | Split | Supports |
| --- | --- | --- | --- |
| **A** `curve_eligible` | eligible ≥ 800 | `clamp(10%, 150, 500)`, whole groups | the R1/R2 curve |
| **B** `point_eligible` | 150 ≤ eligible < 800 | same rule, one frozen `N` only | single-point comparison (~9–13 pp) |
| **C** `illustrative` | eligible < 150, or singleton and < 800 | **no split, use all tasks** | existence, end-to-end, coverage — no number |

Singleton status stacks on top of the tier: a singleton cell also carries a
coverage-gap declaration regardless of its tier.

**Do not split a Tier C dataset.** Splitting `jericho` 40/8/8 yields 8 eval tasks and
a 29 pp resolution floor; that number demonstrates nothing and invites citation. All
56 tasks used for an end-to-end existence claim and for coverage of the
`interactive_fiction` surface is a defensible asset, where the split would convert a
usable asset into an unusable number.

If a number is genuinely needed for such a dataset, the only honest form is an
explicitly labelled **in-sample diagnostic**: no split, all tasks, vary `N`, reported
as mechanism sensitivity and declared not to be generalisation evidence. The platform
already distinguishes valid, unmeasured and diagnostic, so the label is available —
but it must not enter the R1 table.

## 6. Open items

* The same measurement has not been run for the other multi-hop adapters
  (`hotpotqa`, `2wiki`), where the group key would have to come from the corpus
  rather than the id. Whether their leakage magnitude is comparable is unknown.
* Whether the 34 hop-spanning components should be split by hop count is undecided;
  partitioning by component keeps them together, which is the conservative choice.
