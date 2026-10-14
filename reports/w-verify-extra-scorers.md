# Independent extra scorer verification - w-verify

Checked six dataset claims by calling the actual adapter sources and preserved official source copies with an independently written harness. No old comparison-output JSON or old execution scripts were used as results. New authored controls establish each mechanism first; the original synthetic input rows are a separate exact-count crosscheck. Official API files were constructed afresh from those rows. The source-copy byte identities and read-only origins are in `tests/fixtures/hg_wverify/extra-scorers/source-copy-identities.json`.

Execute the twelve exact-count and new-control commands with:

```sh
bash tests/fixtures/hg_wverify/extra-scorers/commands.sh
```

Each exact shell invocation, output locator, and exit code is also preserved in `tests/fixtures/hg_wverify/extra-scorers/execution-commands.json`. No model, GPU, endpoint or network execution occurred. Every scorer command ran under a kernel seccomp socket-denial wrapper; the adjacent `.offline.txt` records IPv4/IPv6/UNIX EPERM probes. Adapter import temporarily refused `QASpec.records`, restored the original function before scoring, and asserted zero cached released records. Adapter/scorer production bytes were unchanged.

| Checked claim | Verdict | Exact command | Fresh raw observations |
| --- | --- | --- | --- |
| StrategyQA 7 raw-contract differences in 12; Boolean projection 4/4 | REPRODUCED | `bash tests/fixtures/hg_wverify/extra-scorers/commands.sh` (StrategyQA outputs) | Crosscheck: agree=5, diverge=7, numeric=12, Boolean projected agree=4/4. Own controls: agree=3, diverge=4 in 7, projected agree=4/4. |
| Sports Understanding 5 paired-channel differences in 12 | REPRODUCED | `bash tests/fixtures/hg_wverify/extra-scorers/commands.sh` (Sports outputs) | Crosscheck: agree=7, diverge=5, numeric=12. Own controls: agree=1, diverge=3 in 4. Actual unchanged official metric functions compiled from AST; no full-module-import claim. |
| FEVER one flat-gold conjunction divergence; three full singleton API exceptions | REPRODUCED | `bash tests/fixtures/hg_wverify/extra-scorers/commands.sh` (FEVER outputs) | Crosscheck: strict agree=16, diverge=1 in 17; singleton errors=3, all `ZeroDivisionError`. Own controls: strict agree=3, diverge=1 in 4; singleton errors=1. |
| HotpotQA one empty-support boundary divergence | REPRODUCED | `bash tests/fixtures/hg_wverify/extra-scorers/commands.sh` (HotpotQA outputs) | Crosscheck: agree=12, diverge=1 in 13; own controls: agree=3, diverge=1 in 4. Both-empty official SP-EM/Joint-EM=1/1; local=0/0. |
| TriviaQA numeric agreement with one upstream exception | REPRODUCED | `bash tests/fixtures/hg_wverify/extra-scorers/commands.sh` (TriviaQA outputs) | Crosscheck: numeric=10, agree=10, diverge=0, nonnumeric=1; own controls: numeric=3, agree=3, nonnumeric=1. Empty alias list upstream `ValueError: max() iterable argument is empty`; local reward=0. |
| MuSiQue common metrics agree on 12 inputs | REPRODUCED | `bash tests/fixtures/hg_wverify/extra-scorers/commands.sh` (MuSiQue outputs) | Crosscheck: agree=12, diverge=0, numeric=12; own controls agree=5/5. Compares answer F1, answer EM, support F1 at official three-decimal rounding. |
| MuSiQue four reward-policy differences | REPRODUCED, with precision caveat | `timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= python3 tests/fixtures/hg_wverify/extra-scorers/offline_exec.py tests/fixtures/hg_wverify/extra-scorers/musique_precision_and_aggregate.py` | Independently executed upstream unrounded `AnswerMetric` vs local reward: four differences. Literal rounded upstream evaluator column vs unrounded local reward: five differences, including partial-answer 0.667 vs 0.6666666666666666. |
| MuSiQue aggregate common metrics agree | REPRODUCED | `timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= python3 tests/fixtures/hg_wverify/extra-scorers/offline_exec.py tests/fixtures/hg_wverify/extra-scorers/musique_precision_and_aggregate.py` | Crosscheck aggregate upstream=local `{answer_f1:0.889, answer_em:0.833, support_f1:0.789}`; own aggregate upstream=local `{answer_f1:1.0, answer_em:1.0, support_f1:0.493}`. |

Raw per-input results and tracebacks: `*-authored.stdout.json`, `*-crosscheck.stdout.json`; the compact fresh-output projection is `derived-summary.json`. For StrategyQA the raw Boolean and Yes/No contracts differ; only the separately projected Boolean panel tests semantic conversion. Sports compares candidate ranking with generated text, two different channels. FEVER's flat-gold input serializes a conjunctive evidence group into the adapter's different representation. These limitations reproduce the report's caveats and do not establish scorer equivalence on released datasets.

The MuSiQue precision caveat is real but is not a fifth reward-policy change. The original report explicitly describes its four differences as policy differences and its table labels the answer F1 as a raw component. Independently executed upstream raw component calls reproduce four. The initial independent runner's `reward_policy_differences` field is preserved unmodified at five: that field compares the upstream evaluator's rounded return to the unrounded reward. `musique-precision-aggregate.stdout.json` records both definitions and the extra rounding-only row. No discrepancy was erased or old evidence changed.

Not checked in this subtask: production runtime/offline closure, released-data accuracy, source reacquisition/authentication against a remote upstream, and complete BIG-bench module/task-runner import. These are outside the requested local quantitative controls.

Reproduced: all six requested comparison mechanisms/counts and MuSiQue aggregate. Refuted: none of these claims under their stated component/policy definitions. Could not check: remote authenticity and production/released-data generalization.
