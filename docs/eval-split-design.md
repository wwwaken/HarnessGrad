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

## 6. Open items

* The same measurement has not been run for the other multi-hop adapters
  (`hotpotqa`, `2wiki`), where the group key would have to come from the corpus
  rather than the id. Whether their leakage magnitude is comparable is unknown.
* Whether the 34 hop-spanning components should be split by hop count is undecided;
  partitioning by component keeps them together, which is the conservative choice.
