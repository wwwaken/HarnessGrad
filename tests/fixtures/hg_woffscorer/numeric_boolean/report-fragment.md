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
