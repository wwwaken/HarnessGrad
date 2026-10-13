# GSM8K scorer provenance and aggregation

The current adapter metric is **decimal-aware-extract**. `data/gsm8k.py` selects the
last signed integer or decimal in the answer, strips commas and dollar signs, and
compares it with the reference using `abs(float(got) - float(want)) < 1e-6`.
Its behavior remains unchanged by this provenance repair. For example, `18.0`
matches `18`, and `-3.25` remains one signed decimal. Missing or unparseable answers
are measured zeros when trusted gold and the scorer are available.

## What the original fixture establishes

The independent fixture is
[`integer_extractor.json`](../tests/fixtures/gsm8k_original/integer_extractor.json).
It pins the inherited regex `(-?[$]?\d[\d,]*)`, last-match selection and comma/dollar
stripping from repository commit `f7ab62143108e120914b5ead34ed339d0c785ee9`, before
the decimal change in `d10b387cc476f4d4ebf04b5a8451453969592db5`.
The fixture and its source file have SHA-256 digests documented in the
[fixture README](../tests/fixtures/gsm8k_original/README.md). Focused tests check the
fixture digest and literal integer-only pattern without borrowing the adapter regex.
Changing a scorer requires a new fixture and identity; preserve these original bytes.

The original test claimed a verbatim lm-evaluation-harness transcription without
pinning an upstream revision. That historical attribution remains unverified.
This fixture establishes the inherited repository behavior only. In particular,
the original integer extractor returns `0` for `18.0`, `5` for `3.5`, and `25` for
`-3.25`; the current adapter returns the complete decimal in each case. Agreement
on integer examples does not establish upstream equivalence.

For a verifiable upstream comparison, lm-evaluation-harness revision
`6d2abda4fd171e68a8789330c4149e37c1ca0bda` (v0.4.8) has a
[different flexible regex](https://github.com/EleutherAI/lm-evaluation-harness/blob/6d2abda4fd171e68a8789330c4149e37c1ca0bda/lm_eval/tasks/gsm8k/gsm8k.yaml)
and uses
[normalized string exact match](https://github.com/EleutherAI/lm-evaluation-harness/blob/6d2abda4fd171e68a8789330c4149e37c1ca0bda/lm_eval/api/metrics.py),
which differs from this adapter's numeric tolerance. Neither source is presented
as the origin of the integer fixture.

## Evidence and compatibility

The legacy function names `official_flexible` and `official_strict`, and the evidence
container `official`, remain for compatibility. `official.filter` identifies the
scored metric as `decimal-aware-extract`; `official.flexible_extract` contains the
decimal-aware extracted value. The `strict_match` field contains the adapter's
last strict-marker extraction and does not affect reward. These legacy names do
not certify equivalence to an official upstream scorer.

Preserve old receipts under their recorded scorer identities. Do not reinterpret
an old `flexible-extract` score as a decimal-aware score. Comparisons must record
scorer/source hashes, dataset revision and split, selected manifest, model and
harness hashes, budgets, aggregation protocol, measured task/trial coverage and
invalid/unmeasured counts. Explain intended differences; a shared dataset name
or split alone does not establish comparability across scorer identities.

## Trial-mean versus test@N

`eval/runner.py::evaluate` implements repeated-trial averaging. For a task with
measured rewards `r_1, ..., r_N`, its score is `(r_1 + ... + r_N) / N`. The run score
averages these task means across measured tasks. Thus binary rewards `[1, 0, 0]`
produce a task mean of `1/3`. Increasing `--trials` measures repeatability; it adds
no selection or reranking step.

In the [original GSM8K verifier protocol](https://arxiv.org/abs/2110.14168), test@N
samples N candidate solutions for a problem, ranks them with a verifier, selects
one candidate, then grades that selected answer. Averaging the resulting per-problem
verdicts produces test@N. The same three hypothetical rewards do not determine a
test@3 verdict: the verifier's selection could earn either 0 or 1. This is also
distinct from oracle any-success/pass@N, which would count any correct candidate.

**test@N is not implemented.** `--trials N` must not be labelled test@N. A future
implementation would need an explicit candidate-generation protocol, verifier
identity and ranking/selection rule, budgets and receipts, and a separate metric
identity. No runtime, selector, verifier model or aggregation code is added here.

For incomplete evaluations, report requested and measured coverage separately.
Invalid, unmeasured, scorer/provider/timeout/cleanup failures are not ordinary
incorrect-answer zeros; a partial trial mean does not establish the planned full
protocol. Synthetic unit-test examples are not benchmark measurements or H0
authorization.

## Validation scope

The focused scorer and dataset tests use authored synthetic rows and answers.
Verifier subprocesses run the copied scorer with an empty table reader, so neither
released split is read. No model, H0, heldout evaluation, or archived receipt is
executed or changed by these checks.
