# Offline official scorer execution and controlled comparisons - w-offscorer

**Disposition: `scorer-offline-closure` remains open. No dataset blocker is closed.**
Official execution evidence is bounded to the scored components and input domains listed below.

Baseline: `fdfdbce` in the registered `/tmp/hg-offscorer` worktree; review date
2026-10-15. Read first and built on: `reports/w-clo-actor-closures.md`,
`tests/fixtures/hg_wclo_actor/`, `reports/w-shared-topology-survey.md`, and
`reports/e1-fever-physics-bird-review.md` / `tests/fixtures/hg_e1_review/`.
The earlier actor byte closures established inventory, not official execution.
The E1 packet already acquired FEVER's scorer and BIG-bench's metric source.
This packet executes those sources and adds public-source scoring controls for
GSM8K, StrategyQA, HotpotQA, TriviaQA, MuSiQue-Ans and 2WikiMultiHopQA.

## Coverage and limits

Official scorer function execution: **nine QA datasets**. All controls are authored
synthetic input sets; this is neither benchmark-task execution nor a measured
accuracy estimate. Source-function execution is narrower than a successful complete
upstream module import; the table and BIG-bench findings preserve that distinction.
Different metrics, channels and representations are not combined into an aggregate
agreement rate. Every per-input value/count below comes from the raw command outputs.

All component-relative paths below resolve under `tests/fixtures/hg_woffscorer/`
and the named component directory. Source copies, authored inputs, official and local
outputs, comparison files, acquisition receipts and all commands are retained there.
The root `SHA256SUMS` covers the full fixture packet. The complete validation command
log and checker output are `reports/w-offscorer-validation.txt`.

| Dataset | Actual official execution | Controlled comparison result |
| --- | --- | --- |
| `fever` | complete unmodified module; strict predicate + full API | 16/17 strict; 1 flat-gold projection difference; 3 full singleton API errors |
| `physicsquestions` | unchanged official functions selected from AST; full import failed | 8/12 agree; 4 differ; same strings/accepted targets |
| `sportsunderstanding` | unchanged official functions selected from AST; full import failed | 7/12 agree; 5 differ; paired channel outcomes; not equivalence |
| `gsm8k` | complete unmodified official scorer module | 6/16 raw outcomes agree; 10 differ |
| `strategyqa` | complete unmodified official scorer module | 5/12 raw outcomes agree; 7 differ; Boolean semantic projection 4/4 agrees, separate from raw inputs |
| `hotpotqa` | complete unmodified upstream evaluator | 12/13 numeric input comparisons agree; 1 differ; 0 nonnumeric |
| `triviaqa` | complete unmodified upstream evaluator | 10/10 numeric input comparisons agree; 0 differ; 1 nonnumeric |
| `musique` | complete unmodified upstream evaluator | 12/12 numeric input comparisons agree; 0 differ; 0 nonnumeric; platform reward differs from answer-F1 on 4 inputs |
| `twowikimultihopqa` | complete unmodified upstream evaluator | 13/13 numeric input comparisons agree; 0 differ; 0 nonnumeric |

All nine now have **bounded offline official scoring-component execution evidence**.
No new official execution evidence is supplied here for the other surveyed QA-command
routes `bfcl_v3`, `chessbench_puzzles` or `reasoning_gym`. Nor is new evidence supplied
for the seven native actor-workdir routes or the four snapshot-service routes. Existing
ALFWorld/Terminal-Bench/Chess observations and all historical/incomplete receipts keep
their original classifications. This report does not overwrite or generalize them.

## Offline execution and local scorer custody

Each successful scorer runs through `offline_exec.py`, which closes inherited socket
fds above stderr, installs a kernel seccomp EPERM filter for socket APIs and
`io_uring_setup`, and actively probes denied IPv4/IPv6/UNIX socket creation before
importing scoring code. Each invocation retains actual interpreter/libseccomp digests,
CPU/fd limits and `production_runtime_observation:false`; the outer timeout bounds
wall time. Acquisition commands are separate network-enabled public-source requests.
No model, GPU, endpoint, task runner, production verifier or container is run.

The original production adapter score functions and shared scorer sources remain
unchanged; `local-source-pins.json` recomputes their baseline byte identities. For
native PyArrow readers a Python audit hook alone cannot exclude data reads. Corrected
GSM8K, HotpotQA and TriviaQA imports therefore temporarily refuse only dataset row
construction, restore the fixture-only substitution before scoring, and assert empty
record caches. The earlier import attempts and their limitations are preserved in
`numeric_boolean/preserved-first-attempt/` and
`public_qa/historical-import-attempts/`, not represented as clean payload-exclusion
receipts. FEVER and BIG-bench CSV reads were refused by the Python audit hook. No
released task is scored in either the original or corrected controlled calls. This
fixture mechanism does not claim production filesystem isolation or trusted custody.

The following component sections contain exact source revisions and recomputed digests,
commands, per-input comparisons, measured divergence/error counts and domain caveats.


<!-- Component: FEVER -->

## FEVER

Executed the complete unmodified `sheffieldnlp/fever-scorer` module at
`4801615100fbf6327f8e99b5dbaefe5dd890e869`, upstream `src/fever/scorer.py`.
Recomputed source SHA-256:
`fa12eaab2c88208f990948fc5d533ad4f91a6b8f48640f29317d1f00ab410ac9`.
`fever/official_scorer.py` is byte-identical to the prior authenticated contents
response `tests/fixtures/hg_e1_review/fever-scorer-source-api.body`; execution
rechecks decoded bytes, Git blob and the source-revision receipt. `six`'s actual
version/path/hash is in `fever/official.json`.

Exact reproduction from the repository root:

```sh
bash tests/fixtures/hg_woffscorer/fever/commands.sh
```

That script records the exact `timeout 150s env ... python3 .../offline_exec.py
.../fever/run.py official|local|compare` commands. Full outputs are
`fever/official.json`, `fever/local.json` and `fever/comparison.json`; the three
`*-offline.txt` files record kernel socket-denial probes and dataset-read denial.
Official calls are `is_strictly_correct(instance, max_evidence=5)` and
`fever_score([instance])`, plus `fever_score(all_controlled_instances)`.
The local entry is the unchanged `data.datasets.fever.score_prediction`.

These are **17 authored synthetic scorer inputs**, with zero released task rows.
Prediction label/evidence pairs are identical, with the API key `answer` mapped to
`predicted_label`. Fourteen controls use exactly the same canonical grouped gold.
Three additional controls deliberately serialize one canonical conjunctive group
into the adapter's flat mirror representation. The canonical gold, local gold,
projection label and prediction are all present together in `fever/inputs.json`.
These latter controls test a gold projection, not equality of the two gold schemas.

The strict predicate has **16 agreements / 1 divergence / 0 predicate errors**.
Canonical grouped controls agree **14/14**; flat projection controls agree **2/3**.
The measured `mirror_flat_partial` divergence is upstream strict `false` versus
local reward `1.0`: upstream requires both synthetic sentences while the local
flat branch treats each as independently sufficient. This confirms a synthetic
projection failure; it does not count corrupted released mirror rows.

The full upstream `fever_score([instance])` raises **three `ZeroDivisionError`s**
(`wrong_evidence`, `required_sixth_pair`, `mirror_flat_wrong`) when its auxiliary
precision and recall are both zero. Their raw tracebacks are retained; no score is
substituted for those failures. The strict predicate still returns normally for
these inputs. The combined controlled-input aggregation returns normally and is
retained, but is not a benchmark measurement.

<!-- The parent report appends the machine-derived per-input table below. -->

| Synthetic input | Official strict predicate | Local reward | Agreement | Full singleton API error |
| --- | ---: | ---: | --- | --- |
| `conjunction_complete` | `true` | 1.0 | yes | none |
| `conjunction_partial` | `false` | 0.0 | yes | none |
| `wrong_evidence` | `false` | 0.0 | yes | ZeroDivisionError |
| `alternate_group` | `true` | 1.0 | yes | none |
| `required_sixth_pair` | `false` | 0.0 | yes | ZeroDivisionError |
| `required_fifth_pair` | `true` | 1.0 | yes | none |
| `nei_empty` | `true` | 1.0 | yes | none |
| `nei_wrong_label` | `false` | 0.0 | yes | none |
| `wrong_label` | `false` | 0.0 | yes | none |
| `lowercase_label` | `true` | 1.0 | yes | none |
| `punctuated_label` | `false` | 0.0 | yes | none |
| `padded_label` | `false` | 0.0 | yes | none |
| `empty_prediction_evidence` | `false` | 0.0 | yes | none |
| `mirror_flat_partial` | `false` | 1.0 | **no** | none |
| `mirror_flat_complete` | `true` | 1.0 | yes | none |
| `mirror_flat_wrong` | `false` | 0.0 | yes | ZeroDivisionError |
| `refutes_complete` | `true` | 1.0 | yes | none |

<!-- Component: BIG-bench -->

# BIG-bench official metric function controls: Physics Questions and Sports Understanding

These are bounded synthetic scorer controls. They execute no benchmark task, model, GPU, endpoint or production harness. Physics uses the same accepted-target list and generated string for both scorers. Sports uses paired candidate log-probability vectors and generated strings in each controlled row; these are distinct output channels, so paired outcome agreement is not scorer equivalence.

## Source custody and execution profile

Official source: `google/BIG-bench@092b196c1f8f14a54bbc62f24759d43bde46dd3b`, `bigbench/api/task_metrics.py`. Recomputed SHA-256: `0d210ed501882ee38742f689b5e4bbc363a7481ef39dc8ee9959bfbc39903e73`. The exact full source copy is `official-task-metrics.py`; the prior authenticated source API response is `tests/fixtures/hg_e1_review/bigbench-metrics-api.body`. `verify.py` decodes that response and checks the Git blob plus byte identity.

Sports official task metadata was additionally acquired from the same revision: `sports-task.json`, recomputed SHA-256 `925617612d19ca02d7b13bfb263300cc13701dca8851151a77be8ce986feadab`, Git blob `406204f3540173ffc7a0ae1152a960c5af7628ff`. Raw API response and acquisition receipt are retained. It declares `preferred_score: multiple_choice_grade` and that sole metric. No released example is used as a control.

The full module import was genuinely attempted offline and failed: installed `datasets==4.5.0` has no `load_metric`. Dependency preflight also records absent T5/TensorFlow-related modules. Raw exception/traceback: `full-module-import-output.json`. This failure is preserved, never treated as a score.

The successful execution is explicitly **unchanged official metric FUNCTION execution**, through AST selection/compile of the exact named function definitions and the upstream `argmax` helper, using actual NumPy. No function body is changed or manually reimplemented; unused imports and unrelated metric definitions are not executed. This does not establish full-module import, full upstream task-runner processing/regex behavior, BLEU, complete transitive dependency closure, or production runtime custody.

| Official function | Original lines | Recomputed selected-source SHA-256 |
| --- | --- | --- |
| `measure_multiple_choice_grade` | 28–43 | `657fc5a248ff3a06ac42f3ce8314b7caae2b8520fed998bd8838f1d8b15fa4bb` |
| `exact_str_match_fn` | 267–279 | `e55780af886ed4607580c7c4ba2a5a9f5d3235ee42c1fb9ddaec4dd76e483c77` |
| `argmax` | 554–560 | `a2039dc6db78843f099ead0181a5594cae31c99494dadc652f8b888c75de80fe` |

Execution globals, NumPy version/path/digest and complete source digest are in `official-source-identity.json`. Existing adapters are imported unchanged and their `score` functions called directly. Local adapter hashes are in `local-output.json`. Generic verifier quote/answer preprocessing is outside these controls.

All execution commands use `offline_exec.py`: kernel seccomp denies all socket entry points and `io_uring_setup`, closes inherited sockets, and verifies AF_INET/AF_INET6/AF_UNIX denial. No network is available during source-function, local scorer, or full-module-probe execution. Source acquisition is a separate earlier network operation. Guard receipts retain interpreter/libseccomp digests, CPU/file-descriptor limits and `production_runtime_observation:false`.

Adapter import eager gold reads were denied before file content could be read; `local-offline-receipt.txt` lists both blocked CSV opens, and `local-output.json` records their intentional import `load_error`. No adapter `load()` is called. This keeps execution confined to the controlled input bytes.

## Physics Questions per-input comparison

Measured controls: **12 inputs, 8 agreeing outcomes, 4 different outcomes**. These counts describe synthetic controls only.

| Input ID | Official return | Local reward | Agreement | Controlled condition |
| --- | ---: | ---: | --- | --- |
| `p01-exact` | 1.0 | 1.0 | true | Exact accepted spelling |
| `p02-alternative` | 1.0 | 1.0 | true | Other exact accepted spelling |
| `p03-prediction-whitespace` | 0.0 | 1.0 | false | Only prediction surrounding whitespace differs |
| `p04-reference-period-removed` | 0.0 | 1.0 | false | Reference has terminal period; prediction lacks it |
| `p05-reference-period-preserved` | 1.0 | 0.0 | false | Exact period-bearing official target |
| `p06-reference-whitespace` | 0.0 | 1.0 | false | Only reference surrounding whitespace differs |
| `p07-prediction-period-added` | 0.0 | 0.0 | true | Only prediction has terminal period |
| `p08-case-difference` | 0.0 | 0.0 | true | Case differs |
| `p09-numeric-nearness` | 0.0 | 0.0 | true | Numerically nearby unlisted spelling |
| `p10-explanation` | 0.0 | 0.0 | true | Extra prose |
| `p11-empty` | 1.0 | 1.0 | true | Empty strings are metric-boundary synthetic control |
| `p12-quoted` | 0.0 | 0.0 | true | Direct scorer called without generic verifier quote processing |

Measured normalization divergences: surrounding prediction whitespace and surrounding reference whitespace score official 0/local 1; a period-bearing reference with a periodless prediction scores official 0/local 1; an exact period-bearing target/prediction scores official 1/local 0. A period added only to a periodless prediction scores 0 for both. The local normalization is asymmetric: it strips whitespace on both sides and periods only on the reference. No numerical tolerance is present. The quoted-answer control calls direct scorers, so the generic QA verifier quote unwrapping does not intervene.

## Sports Understanding per-input paired-channel comparison

The official function selects `choice[argmax(log_prob)]` and returns the corresponding `target_scores` value. It never reads generated text. The local adapter matches a generated text label as a word, case-insensitively, and refuses two-label answers. That source-level distinction is confirmed by executing the actual upstream function and tie breaker. The deliberately decoupled rows demonstrate why these channels cannot be interchanged.

Measured controls: **12 inputs, 7 agreeing outcomes, 5 different outcomes**. These counts describe synthetic controls only.

| Input ID | Official return | Local reward | Agreement | Controlled condition |
| --- | ---: | ---: | --- | --- |
| `s01-aligned-plausible` | 1.0 | 1.0 | true | Candidate winner and text agree |
| `s02-aligned-implausible` | 1.0 | 1.0 | true | Candidate winner and text agree |
| `s03-aligned-wrong` | 0.0 | 0.0 | true | Both channels choose wrong label |
| `s04-capitalized` | 1.0 | 1.0 | true | Text normalization; candidate winner aligned |
| `s05-both-labels` | 1.0 | 0.0 | false | Candidate winner correct; generated text names both labels |
| `s06-empty-text` | 1.0 | 0.0 | false | Candidate winner correct; empty generated text |
| `s07-wrong-vector-correct-text` | 0.0 | 1.0 | false | Deliberately decoupled channels |
| `s08-correct-vector-wrong-text` | 1.0 | 0.0 | false | Deliberately decoupled channels |
| `s09-negation` | 1.0 | 1.0 | true | Word rule does not understand negation |
| `s10-vector-tie` | 1.0 | 1.0 | true | Actual upstream hash tie breaker is executed |
| `s11-word-boundary` | 1.0 | 0.0 | false | Correct candidate ranking; generated text does not name label as word |
| `s12-text-case-whitespace` | 1.0 | 1.0 | true | Candidate winner and normalized generated text agree |

Sports differing outcomes are the correct candidate ranking with both-label text, empty text, wrong-label text or a non-word label prefix, and the wrong candidate ranking with correct-label text. The tied vector runs the official deterministic SHA-256 tie breaker and selects `plausible` here; this is an observed function return, not a replacement tie policy. The local negation control scores `not implausible` correct for `implausible`, demonstrating literal word matching rather than semantic interpretation.

## Exact commands and raw output

The exact command log is `commands.txt` (cwd `/tmp/hg-offscorer-bigbench`). Acquisition output is `sports-task-acquisition.json`. Official per-input/aggregate raw returns: `official-output.json`; local complete raw return dictionaries: `local-output.json`; paired comparison/counts: `comparison.json`.

```sh
python3 tests/fixtures/hg_woffscorer/bigbench/acquire_sports.py
timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= python3 tests/fixtures/hg_woffscorer/offline_exec.py tests/fixtures/hg_woffscorer/bigbench/import_probe.py > tests/fixtures/hg_woffscorer/bigbench/full-module-import-output.json 2> tests/fixtures/hg_woffscorer/bigbench/full-module-import-offline-receipt.txt
timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= python3 tests/fixtures/hg_woffscorer/offline_exec.py tests/fixtures/hg_woffscorer/bigbench/run.py official > tests/fixtures/hg_woffscorer/bigbench/official-output.json 2> tests/fixtures/hg_woffscorer/bigbench/official-offline-receipt.txt
timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= python3 tests/fixtures/hg_woffscorer/offline_exec.py tests/fixtures/hg_woffscorer/bigbench/run.py local > tests/fixtures/hg_woffscorer/bigbench/local-output.json 2> tests/fixtures/hg_woffscorer/bigbench/local-offline-receipt.txt
timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= python3 tests/fixtures/hg_woffscorer/offline_exec.py tests/fixtures/hg_woffscorer/bigbench/run.py compare > tests/fixtures/hg_woffscorer/bigbench/comparison.json 2> tests/fixtures/hg_woffscorer/bigbench/compare-offline-receipt.txt
PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/hg_woffscorer/bigbench/verify.py > tests/fixtures/hg_woffscorer/bigbench/verification-output.json
python3 tools/check_dataset_blockers.py > tests/fixtures/hg_woffscorer/bigbench/registry-validation.json
```

## Remaining unmet obligations

Both datasets now have pinned, bounded, offline official metric **function** execution evidence. Neither gains successful full official module/task-runner execution or complete transitive image/ABI closure. Production trusted class-specific lifecycle/resource/cleanup and valid live controls remain unmet. Source/function controls do not authorize H0 or close any shared or dataset blocker. Registry and journal are left for parent integration.

<!-- Component: Numeric / Boolean -->

# GSM8K and StrategyQA official execution evidence (w-offscorer fragment)

All controlled inputs are authored in `tests/fixtures/hg_woffscorer/numeric_boolean/inputs.json`; no released questions or model outputs are scored. Official Python modules are acquired without modification from fixed public GitHub revisions, with the API Git blob hash checked and SHA-256 recomputed. `acquisition-with-contract.json` records every acquired byte path, revision and digest. Network acquisition is separate from execution.

Every scorer invocation uses the shared kernel seccomp socket-denial guard, CPU/time and descriptor limits; `*-offline.txt` contain IPv4/IPv6/Unix EPERM probes and interpreter/libseccomp identities. No model, GPU, endpoint, task runner, container, benchmark-task execution or `runs/` access occurred. Torch is imported only because the unmodified OpenAI source defines a Dataset class; no model or CUDA operation is called. These are bounded scorer controls, not portable image/ABI closure or trusted production lifecycle/resource/cleanup evidence.

The actual local adapter modules are imported and their unchanged `score()` functions executed. Their scaffold eagerly attempts dataset loading: the CSV attempt is denied by the Python audit hook; the PyArrow reader is explicitly refused by a fixture-only `base.parquet_rows` override during import, restored before `score()`. This avoids native parquet reads that bypass Python's `open` audit hook. An initial GSM8K local import failed the no-records assertion after eager table loading and emitted no score; its original runner and raw stdout/stderr are retained in `preserved-first-attempt/`. That failure is not counted as an incorrect answer. No dataset records from that failed import were printed or scored.

## GSM8K

Official identity: `openai/grade-school-math@3101c7d5072418e28b9008a6636bde82a006892c`, `grade_school_math/dataset.py::extract_answer/is_correct`; SHA-256 `c22b81bccaaebfd1123be296e8b3c3dca3ddc704c46b70bf4a50603bb627e197`. It selects the first `####` regex match, strips commas and compares strings exactly. Raw output: `tests/fixtures/hg_woffscorer/numeric_boolean/gsm8k-official.json`.

Local identity: `data/datasets/gsm8k.py::score`, SHA-256 `628dbf064bd7aa965d31b669247f3fae291de897dd17ad8c71b49c2614e630bb`; raw output: `tests/fixtures/hg_woffscorer/numeric_boolean/gsm8k-local.json`. The same completion string and canonical marked gold are passed to both routes; only the gold's schema is projected through the actual local `_gold()` function.

Measured on 16 authored completion strings: **6 agreements, 10 divergences**, with no per-case scorer errors. The official source rejects unmarked answers and preserves leading zeros/decimal spelling; the adapter accepts numeric representations within its strict `<1e-6` tolerance. Official first-marker extraction also differs from local last-number extraction, including extra numbers after a correct marker. No equivalence or test@N selection claim follows from these controls.

| Input | Completion | Canonical gold | Official correct | Local correct | Agreement |
| --- | --- | --- | --- | --- | --- |
| g01 | `"#### 18"` | `"#### 18"` | True | True | True |
| g02 | `"18"` | `"#### 18"` | False | True | False |
| g03 | `"The answer is 18"` | `"#### 18"` | False | True | False |
| g04 | `"#### 18.0"` | `"#### 18"` | False | True | False |
| g05 | `"#### 1,250"` | `"#### 1250"` | True | True | True |
| g06 | `"#### 018"` | `"#### 18"` | False | True | False |
| g07 | `"#### 18\n#### 7"` | `"#### 18"` | True | False | False |
| g08 | `"#### 7\n#### 18"` | `"#### 18"` | False | True | False |
| g09 | `"#### 18\nAdditional number: 99"` | `"#### 18"` | True | False | False |
| g10 | `"#### 18.0000005"` | `"#### 18"` | False | True | False |
| g11 | `"#### 18.000002"` | `"#### 18"` | False | False | True |
| g12 | `"No numerical answer"` | `"#### 18"` | False | False | True |
| g13 | `"#### -3.25"` | `"#### -3.25"` | True | True | True |
| g14 | `"#### 17"` | `"#### 18"` | False | False | True |
| g15 | `"#### 1e3"` | `"#### 1"` | True | False | False |
| g16 | `"#### $18"` | `"#### 18"` | False | True | False |

## StrategyQA

Official identity: `allenai/strategyqa-evaluator@49b88ed2b2f1b57385c13e8a0699dee1d227f83e`, unmodified `evaluator/eval.py::AnswerEvaluator`; SHA-256 `68c0edcd2fd26daf2cec368302d9f564cbf351288aa4a2c265f47bdc00704044`. The full official module and CLI execute offline with its unmodified `sari.py` dependency (SHA-256 `2aaef3836a9d8f3f501efb859c36359c408015f833b4db2e4efeef8aa8e271b4`) and installed NumPy. The paper repository README links this official evaluator; the retained official paper reader annotates `answer: Optional[bool]` (`source/strategyqa/paper-code-reader.py:116`).

Local identity: `data/datasets/strategyqa.py::score`, SHA-256 `eaad45dfb944241fad84eb575882560ffcf7243de40c9d34fd0766a40c16a50a`; its metric is normalized whole-string Yes/No EM from ReWOO's vendor evaluator, distinct from official Boolean equality. ReWOO's paid LLM judge was not invoked. Raw official/local results are `strategyqa-official.json` and `strategyqa-local.json` in this directory.

The table below passes the same raw prediction value to both scorers. Canonical gold is Boolean for the official contract and is projected to its semantic Yes/No label for the local adapter. **These are incompatible output classes; raw-contract probes are not a common-domain scoring-equivalence statistic.** On four valid official Boolean controls, two verdicts agree and two diverge because the local text adapter does not interpret raw Boolean values as Yes/No. On eight adapter text probes, three verdicts agree and five diverge; all eight are out of the official Boolean prediction contract. The official evaluator's acceptance of a JSON string does not make it a valid Boolean answer. The combined descriptive count is 5 agreements/7 divergences over these two panels only; it must not be reported as benchmark accuracy or equivalent scorers.

| Input | Panel | Raw prediction | Canonical gold | Official correct | Local correct | Agreement |
| --- | --- | --- | --- | --- | --- | --- |
| s01 | valid_official_boolean | `true` | `true` | True | False | False |
| s02 | valid_official_boolean | `false` | `false` | True | False | False |
| s03 | valid_official_boolean | `true` | `false` | False | False | True |
| s04 | valid_official_boolean | `false` | `true` | False | False | True |
| s05 | adapter_text_official_out_of_contract | `"Yes"` | `true` | False | True | False |
| s06 | adapter_text_official_out_of_contract | `"No"` | `false` | False | True | False |
| s07 | adapter_text_official_out_of_contract | `"YES!"` | `true` | False | True | False |
| s08 | adapter_text_official_out_of_contract | `"  no\n"` | `false` | False | True | False |
| s09 | adapter_text_official_out_of_contract | `"a yes"` | `true` | False | True | False |
| s10 | adapter_text_official_out_of_contract | `"Yes, because this is true"` | `true` | False | False | True |
| s11 | adapter_text_official_out_of_contract | `"No"` | `true` | False | False | True |
| s12 | adapter_text_official_out_of_contract | `""` | `false` | False | False | True |

A separate **fixture-only semantic projection** maps true/false prediction values to Yes/No before the unchanged local scorer. It yields four agreements and zero divergences against the four valid official Boolean controls. `strategyqa-local-projected.json` records both canonical and passed prediction values. This demonstrates agreement after an explicit channel conversion, not equivalence of current generated-text scoring with official Boolean scoring.

| Input | Canonical Boolean | Local passed string | Official correct | Local correct | Agreement |
| --- | --- | --- | --- | --- | --- |
| s01 | `true` | `"Yes"` | True | True | True |
| s02 | `false` | `"No"` | True | True | True |
| s03 | `true` | `"Yes"` | False | False | True |
| s04 | `false` | `"No"` | False | False | True |

The unmodified official CLI reports `Accuracy: 0.5` on the four Boolean controls and `Accuracy: 0.0` on the eight explicitly invalid text probes. Full raw command output and metrics are retained in `strategyqa-valid_official_boolean-cli-stdout.txt`, `strategyqa-valid_official_boolean-cli-metrics.json`, `strategyqa-adapter_text_official_out_of_contract-cli-stdout.txt` and `strategyqa-adapter_text_official_out_of_contract-cli-metrics.json`. The CLI's `SARI: 0.0` and `Recall@10: 0.0` are wrapper defaults for unrequested metrics, not measured decomposition/retrieval scores.

## Exact commands (repository root)

The following commands were run in `/tmp/hg-offscorer-numeric`; they are also retained verbatim in `commands.txt`. `acquisition.json` preserves the first seven-file acquisition receipt; `acquisition-with-contract.json` adds the paper reader source and is the current acquisition receipt.

```sh
python3 tests/fixtures/hg_woffscorer/numeric_boolean/acquire.py > tests/fixtures/hg_woffscorer/numeric_boolean/acquisition-with-contract.json
timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= python3 tests/fixtures/hg_woffscorer/offline_exec.py tests/fixtures/hg_woffscorer/numeric_boolean/execute.py gsm8k official > tests/fixtures/hg_woffscorer/numeric_boolean/gsm8k-official.json 2> tests/fixtures/hg_woffscorer/numeric_boolean/gsm8k-official-offline.txt
timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= python3 tests/fixtures/hg_woffscorer/offline_exec.py tests/fixtures/hg_woffscorer/numeric_boolean/execute.py gsm8k local > tests/fixtures/hg_woffscorer/numeric_boolean/gsm8k-local.json 2> tests/fixtures/hg_woffscorer/numeric_boolean/gsm8k-local-offline.txt
timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= python3 tests/fixtures/hg_woffscorer/offline_exec.py tests/fixtures/hg_woffscorer/numeric_boolean/execute.py strategyqa official > tests/fixtures/hg_woffscorer/numeric_boolean/strategyqa-official.json 2> tests/fixtures/hg_woffscorer/numeric_boolean/strategyqa-official-offline.txt
timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= python3 tests/fixtures/hg_woffscorer/offline_exec.py tests/fixtures/hg_woffscorer/numeric_boolean/execute.py strategyqa local > tests/fixtures/hg_woffscorer/numeric_boolean/strategyqa-local.json 2> tests/fixtures/hg_woffscorer/numeric_boolean/strategyqa-local-offline.txt
timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= python3 tests/fixtures/hg_woffscorer/offline_exec.py tests/fixtures/hg_woffscorer/numeric_boolean/execute.py strategyqa local --canonical-boolean-projection > tests/fixtures/hg_woffscorer/numeric_boolean/strategyqa-local-projected.json 2> tests/fixtures/hg_woffscorer/numeric_boolean/strategyqa-local-projected-offline.txt
python3 tests/fixtures/hg_woffscorer/numeric_boolean/prepare_cli_inputs.py
timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= python3 tests/fixtures/hg_woffscorer/offline_exec.py tests/fixtures/hg_woffscorer/numeric_boolean/source/strategyqa/eval.py --golds_file tests/fixtures/hg_woffscorer/numeric_boolean/strategyqa-valid_official_boolean-golds.json --predictions_file tests/fixtures/hg_woffscorer/numeric_boolean/strategyqa-valid_official_boolean-predictions.json --metrics_output_file tests/fixtures/hg_woffscorer/numeric_boolean/strategyqa-valid_official_boolean-cli-metrics.json > tests/fixtures/hg_woffscorer/numeric_boolean/strategyqa-valid_official_boolean-cli-stdout.txt 2> tests/fixtures/hg_woffscorer/numeric_boolean/strategyqa-valid_official_boolean-cli-offline.txt
timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= python3 tests/fixtures/hg_woffscorer/offline_exec.py tests/fixtures/hg_woffscorer/numeric_boolean/source/strategyqa/eval.py --golds_file tests/fixtures/hg_woffscorer/numeric_boolean/strategyqa-adapter_text_official_out_of_contract-golds.json --predictions_file tests/fixtures/hg_woffscorer/numeric_boolean/strategyqa-adapter_text_official_out_of_contract-predictions.json --metrics_output_file tests/fixtures/hg_woffscorer/numeric_boolean/strategyqa-adapter_text_official_out_of_contract-cli-metrics.json > tests/fixtures/hg_woffscorer/numeric_boolean/strategyqa-adapter_text_official_out_of_contract-cli-stdout.txt 2> tests/fixtures/hg_woffscorer/numeric_boolean/strategyqa-adapter_text_official_out_of_contract-cli-offline.txt
python3 tests/fixtures/hg_woffscorer/numeric_boolean/compare.py > tests/fixtures/hg_woffscorer/numeric_boolean/comparison.json
python3 tests/fixtures/hg_woffscorer/numeric_boolean/validate.py
python3 tools/check_dataset_blockers.py
```

`comparison.json` contains machine-readable per-input verdicts and panel counts. `validate.py` verifies acquired source hashes/Git blobs, local scorer hashes, input alignment, derived counts, raw CLI metrics and offline receipts. Parent integration provides the full SHA-256 manifest.

Official-scorer execution evidence now exists for **GSM8K and StrategyQA**, limited to the source paths/metrics and controlled input contracts described above. This fragment makes no statement that other datasets were executed. Portable transitive image/ABI closure, trusted class-specific lifecycle/resource/cleanup observations and valid live controls remain unmet; no blocker is closed and no pilot is authorized.

<!-- Component: Public QA -->

## Additional QA-family official execution evidence

All inputs below are named synthetic controls, created by `python3 tests/fixtures/hg_woffscorer/public_qa/prepare_inputs.py`; no benchmark tasks or models were executed. Each official command imports the acquired source unchanged and invokes its complete evaluator on the same per-input files used to construct local scorer arguments. HotpotQA and 2Wiki execute `eval`; TriviaQA executes `evaluate_triviaqa`; MuSiQue executes `evaluate`. The comparator retains raw stdout, returned dictionaries, and exceptions.

Execution commands ran from `/tmp/hg-offscorer-public` (registered branch `wg-offscorer-public`, starting commit `fdfdbce`). Kernel seccomp refuses socket APIs and io_uring_setup; each stderr receipt proves IPv4, IPv6, and UNIX socket creation returned EPERM. The actual installed `ujson` extension is used by HotpotQA and 2Wiki and its recomputed digest is in each official output under `imported_source_and_extension_files`. No dependency replacement or scorer-source rewriting was applied.

The local execution fixture temporarily refuses `QASpec.records` only while importing an adapter, restores it before scoring, and asserts `_SPEC._records` remains empty before and after scoring. Scorer functions and production files remain unchanged. The refusal and cache state are recorded in each corrected local output. This fixture import isolation is not evidence of production verifier admission, lifecycle, ABI closure, or cleanup.

**Preserved initial-import limitation:** earlier local attempts used Python file-open audit guards alone. HotpotQA and TriviaQA eager imports could read released parquet pools through native PyArrow I/O, which that audit does not intercept; the initial receipts do not establish payload exclusion. 2Wiki’s initial Python `dev.json` open was denied, and MuSiQue import was lazy. Those initial attempts and the pre-suppression execution script are preserved in `tests/fixtures/hg_woffscorer/public_qa/historical-import-attempts/` and are excluded from the clean comparison evidence. Their scores used only the named synthetic arguments; no benchmark task or model execution occurred. Corrected local outputs below use the row-loading refusal.

Raw output and comparison locators: `tests/fixtures/hg_woffscorer/public_qa/outputs/<dataset>/{official,local}.stdout.json`, matching `.offline-receipt.txt` files, `tests/fixtures/hg_woffscorer/public_qa/comparison.json`, and `tests/fixtures/hg_woffscorer/public_qa/execution-commands.json`. `comparison-summary.stdout.json` is generated by `python3 tests/fixtures/hg_woffscorer/public_qa/compare.py`.

In the tables, O means the executed upstream evaluator and L means the actual local adapter. Equality is asserted only for the columns listed and at the official evaluator’s scale and rounding. Missing channels are passed as missing upstream fields and missing local fields; MuSiQue upstream’s required list receives `[]` for the local omitted support channel, with this contract translation visible in prepared inputs.

### hotpotqa

Official repository: https://github.com/hotpotqa/hotpot; revision `fa3a36370899e1d85822de61e58c85ea19993154`. Executed scorer: `tests/fixtures/hg_woffscorer/public_qa/source/hotpotqa/hotpot_evaluate_v1.py`; recomputed SHA-256 `d35fc91a6db21d791dbdda11daf3856e9359f5701d54e3eefba20d88fecc02c0`. Local adapter: `data/datasets/hotpotqa.py`; recomputed SHA-256 `1946c6cf56db9124cf1b8d4fed61eed43c61d2a4ff85f181ac8b2739946db6e1`.

Acquisition: `python3 tests/fixtures/hg_woffscorer/public_qa/acquire.py > tests/fixtures/hg_woffscorer/public_qa/acquisition.stdout.json`. GitHub commit/tree/blob responses are preserved in `tests/fixtures/hg_woffscorer/public_qa/acquisition/`. `verify.py` reconstructs the signed Git commit identity, tree identity, and scorer blob identity from these responses; source SHA-256 is recomputed separately. The selected upstream tree contains no root `LICENSE`; no SPDX claim is made.

Exact executed commands:

```sh
timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= python3 tests/fixtures/hg_woffscorer/offline_exec.py tests/fixtures/hg_woffscorer/public_qa/execute.py official hotpotqa > tests/fixtures/hg_woffscorer/public_qa/outputs/hotpotqa/official.stdout.json 2> tests/fixtures/hg_woffscorer/public_qa/outputs/hotpotqa/official.offline-receipt.txt
timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= python3 tests/fixtures/hg_woffscorer/offline_exec.py tests/fixtures/hg_woffscorer/public_qa/execute.py local hotpotqa > tests/fixtures/hg_woffscorer/public_qa/outputs/hotpotqa/local.stdout.json 2> tests/fixtures/hg_woffscorer/public_qa/outputs/hotpotqa/local.offline-receipt.txt
```

Measured comparison: 13 numeric inputs; 12 agree and 1 diverge; 0 nonnumeric input(s). 78 metric cells compared; 2 differ.

Compared columns: (EM,F1,SP-EM,SP-F1,Joint-EM,Joint-F1), fractions.

| Input | Official / local common metrics |
|---|---|
| exact | O=L=(1,1,1,1,1,1) |
| case-punctuation-articles | O=L=(1,1,1,1,1,1) |
| partial-answer | O=L=(0,0.666666666667,1,1,0,0.666666666667) |
| wrong-answer | O=L=(0,0,1,1,0,0) |
| yes-no-mismatch | O=L=(0,0,1,1,0,0) |
| yes-token-overlap-rejected | O=L=(0,0,1,1,0,0) |
| partial-support | O=L=(1,1,0,0.666666666667,0,0.666666666667) |
| extra-support | O=L=(1,1,0,0.8,0,0.8) |
| duplicate-support | O=L=(1,1,1,1,1,1) |
| wrong-title-case | O=L=(1,1,0,0.5,0,0.5) |
| missing-support | O=L=(1,1,0,0,0,0) |
| submitted-empty-support | O=L=(1,1,0,0,0,0) |
| both-empty-support-boundary | O=(1,1,1,0,1,0); L=(1,1,0,0,0,0) |

**Measured divergence:** `both-empty-support-boundary` supplies empty support gold and an explicitly submitted empty support prediction. Upstream returns SP-EM=1, Joint-EM=1; local returns SP-EM=0, Joint-EM=0. Both SP-F1 and Joint-F1 are zero. Local `hotpot_update_sp` raises `MissingEvidence` for a falsey list and the adapter maps it to all-zero support. This is an explicitly synthetic boundary; no claim is made that empty support gold occurs in the released HotpotQA split.

### triviaqa

Official repository: https://github.com/mandarjoshi90/triviaqa; revision `ca43b5820b107f3970cf4b7d67f7db7a98117b79`. Executed scorer: `tests/fixtures/hg_woffscorer/public_qa/source/triviaqa/evaluation/triviaqa_evaluation.py`; recomputed SHA-256 `51785a3bc2e02a8f1ebf9db3aa18834c6a5daa5089ee5d435c99e0babf4be682`. Local adapter: `data/datasets/triviaqa.py`; recomputed SHA-256 `c4c9e7121672f482abd5ec5527daa07d893f27bfbdcb7255841782332597413c`.

Source and helpers are copied byte-for-byte from the already acquired `tests/fixtures/triviaqa_upstream/` closure. `source-identities.json` records original provenance, SHA-256, and Git blob identity; verification checks copied bytes against that existing independently acquired source. Only per-row alias-max EM is implemented locally. Upstream F1 is retained as an auxiliary result, with no local F1 equivalence claim.

Exact executed commands:

```sh
timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= python3 tests/fixtures/hg_woffscorer/offline_exec.py tests/fixtures/hg_woffscorer/public_qa/execute.py official triviaqa > tests/fixtures/hg_woffscorer/public_qa/outputs/triviaqa/official.stdout.json 2> tests/fixtures/hg_woffscorer/public_qa/outputs/triviaqa/official.offline-receipt.txt
timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= python3 tests/fixtures/hg_woffscorer/offline_exec.py tests/fixtures/hg_woffscorer/public_qa/execute.py local triviaqa > tests/fixtures/hg_woffscorer/public_qa/outputs/triviaqa/local.stdout.json 2> tests/fixtures/hg_woffscorer/public_qa/outputs/triviaqa/local.offline-receipt.txt
```

Measured comparison: 10 numeric inputs; 10 agree and 0 diverge; 1 nonnumeric input(s). 10 metric cells compared; 0 differ.

Compared columns: alias-max EM, percent (local reward × 100).

| Input | Official / local common metrics |
|---|---|
| exact | O=L=(100) |
| later-alias | O=L=(100) |
| underscore-hyphen-article | O=L=(100) |
| smart-apostrophe | O=L=(100) |
| punctuation-becomes-space | O=L=(100) |
| partial-answer | O=L=(0) |
| wrong | O=L=(0) |
| empty-prediction | O=L=(0) |
| human-answer-alias | O=L=(100) |
| empty-normalized-text-boundary | O=L=(100) |
| empty-alias-set-error-boundary | upstream ValueError: max() iterable argument is empty; local=0 |

**Measured domain difference:** `empty-alias-set-error-boundary` raises upstream `ValueError: max() iterable argument is empty`, while local returns zero. The official aggregate over the deliberately mixed controls also raises this exception; it is retained as an error, not a fabricated official score or an ordinary numeric disagreement. Numeric EM agrees on all other controls. Upstream F1 is present in the raw output and comparison as `upstream_f1_auxiliary_local_unimplemented`.

### musique

Official repository: https://github.com/StonyBrookNLP/musique; revision `922ac98f19a201998dbdae6d7f2887a5258dbdeb`. Executed scorer: `tests/fixtures/hg_woffscorer/public_qa/source/musique/evaluate_v1.0.py`; recomputed SHA-256 `f5fe66ae61dbea5172cba9d428d9924a5811f3457edc945fc1d81369c30e74b7`. Local adapter: `data/datasets/musique.py`; recomputed SHA-256 `817af68df579bcf577c64a9613fa5b368424ee00dc4101f20ad00010c357e5f2`.

Source was copied directly from the already acquired pinned official archive `/mnt/20t/xubuqiang/datasets/musique/_src/musique.tar.gz`, recomputing its SHA-256 `c1cc3d121e3f623f9925857559030d48c136142ee2c9cdb52214bb6134c02272` first. Exact archive members, copied source SHA-256 and Git blob identities are in `tests/fixtures/hg_woffscorer/public_qa/source-identities.json`. No released dataset rows or global aliases were read by corrected execution; 2Wiki aliases are synthetic inline fixtures.

Exact executed commands:

```sh
timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= python3 tests/fixtures/hg_woffscorer/offline_exec.py tests/fixtures/hg_woffscorer/public_qa/execute.py official musique > tests/fixtures/hg_woffscorer/public_qa/outputs/musique/official.stdout.json 2> tests/fixtures/hg_woffscorer/public_qa/outputs/musique/official.offline-receipt.txt
timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= python3 tests/fixtures/hg_woffscorer/offline_exec.py tests/fixtures/hg_woffscorer/public_qa/execute.py local musique > tests/fixtures/hg_woffscorer/public_qa/outputs/musique/local.stdout.json 2> tests/fixtures/hg_woffscorer/public_qa/outputs/musique/local.offline-receipt.txt
```

Measured comparison: 12 numeric inputs; 12 agree and 0 diverge; 0 nonnumeric input(s). 36 metric cells compared; 0 differ.

Compared columns: (answer F1,answer EM,support F1), fractions at official 3-decimal rounding.

| Input | Official / local common metrics |
|---|---|
| exact | O=L=(1,1,1) |
| normalized-answer | O=L=(1,1,1) |
| alias-answer | O=L=(1,1,1) |
| partial-answer | O=L=(0.667,0,1) |
| wrong-answer | O=L=(0,0,1) |
| partial-support | O=L=(1,1,0.667) |
| support-title-ignored | O=L=(1,1,1) |
| extra-support | O=L=(1,1,0.8) |
| duplicate-support | O=L=(1,1,1) |
| missing-support | O=L=(1,1,0) |
| empty-support | O=L=(1,1,0) |
| both-empty-support-boundary | O=L=(1,1,1) |

Official common columns and their aggregate agree. The default platform reward is `answer_f1 * support_f1`, explicitly absent as an official MuSiQue metric. It differs from the upstream answer-F1 column on 4 inputs. These policy differences do not count as common-metric divergences:

| Input | Official answer F1 (raw component) | Local platform reward |
|---|---|---|
| partial-support | 1 | 0.666666666667 |
| extra-support | 1 | 0.8 |
| missing-support | 1 | 0 |
| empty-support | 1 | 0 |

The local structured default path was tested; the legacy answer-only path and MuSiQue-Full sufficiency evaluation were not tested. All synthetic upstream rows set `answerable=true`, matching the MuSiQue-Ans scorer domain.

### twowikimultihopqa

Official repository: https://github.com/Alab-NII/2wikimultihop; revision `209e761834d1ce055856fc11072c0a5aab47601d`. Executed scorer: `tests/fixtures/hg_woffscorer/public_qa/source/twowikimultihopqa/2wikimultihop_evaluate_v1.1.py`; recomputed SHA-256 `7c09ee2ec98c7ecb57df79eb68dba22eb381ab58d50e730dfcefafb4dda31458`. Local adapter: `data/datasets/twowikimultihopqa.py`; recomputed SHA-256 `55556cbb914e64bcdb644b5d96df6b89752a927c3b96a4b5d34f3dbbc3ceec21`.

Source was copied directly from the already acquired pinned official archive `/mnt/20t/xubuqiang/datasets/twowikimultihopqa/_src/2wikimultihop.tar.gz`, recomputing its SHA-256 `01c0b699569cce142614d5d7a0e1f4864031aeaf035394af3084cc2c1d97dc3c` first. Exact archive members, copied source SHA-256 and Git blob identities are in `tests/fixtures/hg_woffscorer/public_qa/source-identities.json`. No released dataset rows or global aliases were read by corrected execution; 2Wiki aliases are synthetic inline fixtures.

Exact executed commands:

```sh
timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= python3 tests/fixtures/hg_woffscorer/offline_exec.py tests/fixtures/hg_woffscorer/public_qa/execute.py official twowikimultihopqa > tests/fixtures/hg_woffscorer/public_qa/outputs/twowikimultihopqa/official.stdout.json 2> tests/fixtures/hg_woffscorer/public_qa/outputs/twowikimultihopqa/official.offline-receipt.txt
timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= python3 tests/fixtures/hg_woffscorer/offline_exec.py tests/fixtures/hg_woffscorer/public_qa/execute.py local twowikimultihopqa > tests/fixtures/hg_woffscorer/public_qa/outputs/twowikimultihopqa/local.stdout.json 2> tests/fixtures/hg_woffscorer/public_qa/outputs/twowikimultihopqa/local.offline-receipt.txt
```

Measured comparison: 13 numeric inputs; 13 agree and 0 diverge; 0 nonnumeric input(s). 208 metric cells compared; 0 differ.

Official percentages rounded to two decimals are compared with `round(local_fraction * 100, 2)`. Each tuple is `(EM,F1,precision,recall)`. This explicitly checks the published columns, not sub-rounding equality.

| Input | Answer | Support | Evidence | Joint |
|---|---|---|---|---|
| exact | O=L=(100,100,100,100) | O=L=(100,100,100,100) | O=L=(100,100,100,100) | O=L=(100,100,100,100) |
| normalized-answer | O=L=(100,100,100,100) | O=L=(100,100,100,100) | O=L=(100,100,100,100) | O=L=(100,100,100,100) |
| answer-alias | O=L=(100,100,100,100) | O=L=(100,100,100,100) | O=L=(100,100,100,100) | O=L=(100,100,100,100) |
| partial-answer | O=L=(0,66.67,100,50) | O=L=(100,100,100,100) | O=L=(100,100,100,100) | O=L=(0,66.67,100,50) |
| wrong-answer | O=L=(0,0,0,0) | O=L=(100,100,100,100) | O=L=(100,100,100,100) | O=L=(0,0,0,0) |
| partial-support | O=L=(100,100,100,100) | O=L=(0,66.67,100,50) | O=L=(100,100,100,100) | O=L=(0,66.67,100,50) |
| empty-support | O=L=(100,100,100,100) | O=L=(0,0,0,0) | O=L=(100,100,100,100) | O=L=(0,0,0,0) |
| duplicate-support | O=L=(100,100,100,100) | O=L=(100,100,100,100) | O=L=(100,100,100,100) | O=L=(100,100,100,100) |
| normalized-support-title | O=L=(100,100,100,100) | O=L=(0,50,50,50) | O=L=(100,100,100,100) | O=L=(0,50,50,50) |
| missing-support | O=L=(100,100,100,100) | O=L=(0,0,0,0) | O=L=(100,100,100,100) | O=L=(0,0,0,0) |
| missing-evidence | O=L=(100,100,100,100) | O=L=(100,100,100,100) | O=L=(0,0,0,0) | O=L=(0,0,0,0) |
| wrong-evidence | O=L=(100,100,100,100) | O=L=(100,100,100,100) | O=L=(0,0,0,0) | O=L=(0,0,0,0) |
| evidence-entity-alias | O=L=(100,100,100,100) | O=L=(100,100,100,100) | O=L=(100,100,100,100) | O=L=(100,100,100,100) |

All official v1.1 published columns and the aggregate agree for the structured path, including synthetic answer aliases, evidence entity aliases, normalized support titles, missing support/evidence channels, and partial answers/support. Legacy text scoring was not tested. This is controlled scoring evidence, not a provenance assertion for released dataset rows.

This adds bounded official-execution evidence for HotpotQA, TriviaQA, MuSiQue-Ans and 2WikiMultihopQA. No other dataset is covered by this fragment. Complete transitive image/ABI closure, trusted class-specific lifecycle/resource/cleanup observations, and valid live controls remain unmet; no shared or dataset blocker is closed.

## Shared blocker decision - remains open

The shared registry observation is sharpened only for `scorer-offline-closure`, with
an appended verbatim evidence locator into this report. Its status, next_action and
all dataset records, historical records and other shared blockers remain unchanged.
The journal is append-only. Production adapters/shared scorers, runs/, archives and
frozen evidence are untouched.

Still unmet: complete portable transitive scorer/runtime/image/ABI closure and byte
custody; successful full BIG-bench module/task-runner execution; complete matched
response processing and metric comparability; dataset source/selected-gold provenance
gates; trusted class-specific lifecycle/resource/cleanup observations; and valid live
controls before pilots. Snapshot/service connectivity must remain available where
required and only matching known production isolation classes may be compared. The
kernel-offline fixture receipts do not satisfy those production requirements.
