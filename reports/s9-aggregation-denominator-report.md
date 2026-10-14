# Stage B part 2: aggregation denominators (s9)

Base: `80c3707`. Worktree: `/tmp/hg-s9`. Classification: **(c), an undocumented
accident in the platform helper contracts**, not a proven numeric bug and not an
upstream requirement to silently omit missing MuSiQue predictions. Existing numeric
behavior is preserved.

## Mechanism and call chains

MuSiQue per item:

```text
score_prediction -> _score -> compute_f1 / compute_exact / compute_support
                         -> reward = answer_f1 * support_f1
score(text)        -> _score (empty support in default mode)
legacy mode       -> reward = answer_f1
aggregate(results) -> ordered per-field accumulation / len(results)
```

`aggregate` returns the unrounded mean of per-item rewards; it never multiplies
corpus means. Only answer_f1, answer_em and support_f1 are rounded to three decimals.
Its input contains scored results and no separate gold inventory. An omitted item
therefore disappears from its denominator. Empty inputs and mixed modes are refused.
The joint reward is a platform policy, not an official MuSiQue column.

2WikiMultihopQA per item and corpus:

```text
score -> score_prediction -> _prediction_metrics
                         -> update_answer / update_sp / update_evi
                         -> joint precision/recall -> joint_f1 reward
score(text) -> score_answer_only -> _one_question -> update_answer -> answer F1
evaluate_predictions(predictions, golds)
  -> _prediction_metrics for every gold ID (missing predictions use empty channels)
  -> ordered sums / len(golds) * 100 -> round once to two decimals
```

The corpus helper returns all 16 percentage metrics, including joint_f1, rather
than a verdict with a `reward` field. Missing rows/channels contribute zero;
extra prediction IDs do not enter the sums or denominator. Per-item rewards are
fractions and are not the rounded corpus percentages.

The actual platform execution path for both adapters is separate:

```text
QASpec.verifier -> materialized data/qa/verify/check.py::main
  -> adapter.score / score_prediction -> write_reward (existing :g serialization)
  -> eval.verifier._verify/_verify_inner -> verdict.score
  -> eval.runner._evaluate -> arithmetic mean of measured trial scores per task
  -> harnessgrad.records._scored -> measured task IDs only
  -> records._curve_point -> eval.metrics.mean -> recorded run score
```

Neither adapter corpus helper is called by the driver. The run score uses measured
tasks, excluding invalid/unmeasured tasks; absent benchmark predictions and failed
platform measurements have different meanings. Trials retain their existing runner
mean, and all existing accumulation order, scaling, rounding and serialization stay
in place.

## Upstream evidence and classification

MuSiQue transcribes components from StonyBrookNLP/musique at
`922ac98f19a201998dbdae6d7f2887a5258dbdeb`:

- [evaluate_v1.0.py](https://github.com/StonyBrookNLP/musique/blob/922ac98f19a201998dbdae6d7f2887a5258dbdeb/evaluate_v1.0.py#L29)
  asserts equal prediction/gold line counts (lines 29–31) and matching IDs in order
  (lines 37–39). Lines 58–60 invoke metrics on answerable gold rows; all rows in this
  adapter's Ans pool are answerable. Lines 83–85 round the three official means.
- [metrics/answer.py](https://github.com/StonyBrookNLP/musique/blob/922ac98f19a201998dbdae6d7f2887a5258dbdeb/metrics/answer.py)
  and [metrics/support.py](https://github.com/StonyBrookNLP/musique/blob/922ac98f19a201998dbdae6d7f2887a5258dbdeb/metrics/support.py)
  increment `_count` on each scored call and divide totals by `_count` in `get_metric`.

2Wiki transcribes
[2wikimultihop_evaluate_v1.1.py](https://github.com/Alab-NII/2wikimultihop/blob/209e761834d1ce055856fc11072c0a5aab47601d/2wikimultihop_evaluate_v1.1.py#L259)
at `209e761834d1ce055856fc11072c0a5aab47601d`. It iterates gold rows, skips missing
prediction channels without incrementing their metrics, then uses `N = len(gold)`
(line 259) and `round(metrics[k] / N * 100, 2)` (line 262).

Both canonical codeload archives were fetched into ignored worktree scratch, and
their SHA-256 digests matched the adapters' pins:

| Source | SHA-256 |
| --- | --- |
| MuSiQue archive | `c1cc3d121e3f623f9925857559030d48c136142ee2c9cdb52214bb6134c02272` |
| MuSiQue evaluate_v1.0.py | `f5fe66ae61dbea5172cba9d428d9924a5811f3457edc945fc1d81369c30e74b7` |
| 2Wiki archive | `01c0b699569cce142614d5d7a0e1f4864031aeaf035394af3084cc2c1d97dc3c` |
| 2Wiki evaluator | `7c09ee2ec98c7ecb57df79eb68dba22eb381ab58d50e730dfcefafb4dda31458` |

The three existing MuSiQue metric fixture files matched canonical archive bytes.
The complete 2Wiki transcription region matched the pinned evaluator, and the
existing structured test independently pins that region's digest.

Consequently **(c)**: with complete MuSiQue input the scored-call count equals the
answerable gold count. Upstream rejects an omitted row; it does not require a
smaller denominator. MuSiQue's permissive result-list helper and 2Wiki's complete
gold-inventory helper exposed different contracts without a common declaration.
Changing either current numeric behavior would violate this task's preservation
constraint, so neither behavior was changed.

## Changes and guards

`data/aggregation_policies.json` now declares each adapter's aggregation and
denominator explicitly. Each of the 28 published adapters declares `run_reward` as
`arithmetic_mean / measured_tasks`. The three platform fixtures also declare it for
compatibility. MuSiQue separately declares `corpus_metrics` as
`ordered_macro_mean / provided_results`; 2Wiki declares
`ordered_macro_mean / gold_rows`.

`data.aggregation.aggregation_policy` validates these declarations without importing
adapters. `aggregation_denominator` selects the declared count and refuses missing
counts. Both corpus helpers read that accessor inside their actual division paths.
Lazy imports preserve the existing isolated per-item verifier bundle without
modifying `data/qa/base.py`.

Both the training driver and eval-side entrypoint now carry the dataset name in
sampling metadata. Recorded run/train rewards pass it to `eval.metrics.mean`, which
reads the adapter's declared denominator. Generic means without a dataset retain
their existing behavior (including confidence-interval calculations).

The new focused guard AST-reads publication declarations even if imports would fail,
requires policies for every published adapter, discovers corpus helpers, and rejects
new undeclared or dynamic publication declarations. The excluded adapter is covered
by name without opening/importing its source. Runtime mutation tests demonstrate
that every published run policy and both corpus policies are live: changing the
denominator to a count unavailable to that caller causes refusal, rather than a
number from a hard-coded denominator. A recorded-curve test checks the live path
and exclusion of an invalid task. The referenced
`tests/quality/test_qa_control_expectations.py` was absent at this base; no file from
Stage B part 1 was edited.

## Before/after evidence

`tests/fixtures/aggregation_s9_before.json` was captured before implementation from
fabricated inputs on the unmodified base. The same inputs were recomputed after
implementation: all item verdicts, official fields, corpus outputs and five common
run-score inputs for every published dataset name were identical, without tolerance.
These are arithmetic/scorer unit controls, not benchmark measurements or pilots.

| Synthetic case | Before | After |
| --- | ---: | ---: |
| MuSiQue, three provided results | 0.48148148148148145 | 0.48148148148148145 |
| MuSiQue, only first result provided | 1.0 | 1.0 |
| MuSiQue legacy mean | 0.5555555555555555 | 0.5555555555555555 |
| 2Wiki complete, Joint F1 (%) | 100.0 | 100.0 |
| 2Wiki missing row, Joint F1 (%) | 50.0 | 50.0 |
| 2Wiki missing channels, Joint F1 (%) | 50.0 | 50.0 |
| 2Wiki no predictions, Joint F1 (%) | 0.0 | 0.0 |
| 2Wiki partial answer / two golds, Joint F1 (%) | 33.33 | 33.33 |

The common run inputs `[]`, `[1]`, `[1,0]`, `[1,0,1/3]`, `[0.1,0.2,0.3]`
yielded `[0.0,1.0,0.5,0.4444444444444444,0.19999999999999998]` before and after for
each of the 28 dataset names. No other adapter scorer was imported or executed.
The full before and after capture files also had identical bytes, SHA-256
`d7ab601e446d0a4eb24fde6bffe97fbc026669c43b84b7407224106e0040ee55`.

## Focused validation

Only these test files were run, each with
`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python -m pytest -q`:

| Test file | --basetemp | Result |
| --- | --- | --- |
| tests/quality/test_aggregation_policies.py | /mnt/20t/xubuqiang/.hg-pytest/s9/aggregation-policies | 41 passed |
| tests/quality/test_musique_official_scorer.py | /mnt/20t/xubuqiang/.hg-pytest/s9/musique-official-scorer | 106 passed |
| tests/quality/test_twowikimultihopqa_structured.py | /mnt/20t/xubuqiang/.hg-pytest/s9/twowiki-structured | 43 passed |

Initial attempts failed during pytest temporary-directory setup because the requested
parent directory did not exist; creating that parent resolved the errors. No full
suite, released task data, model endpoint, GPU, pilot or excluded adapter execution
was used.
