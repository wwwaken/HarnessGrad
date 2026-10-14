# Bounded official execution coverage extension - w-offscorer2

Official execution evidence is limited to the exact components, inputs and profiles documented here.

**Disposition: `scorer-offline-closure` remains open. S1, S3, S4 and S6 remain partial.
No shared or dataset blocker is closed, and no gate, adapter or shared scorer changes.**

Baseline: `9dab533`, registered `/tmp/hg-offscorer2` worktree, review 2026-10-15.
The method follows `reports/w-offscorer-equivalence.md` and
`tests/fixtures/hg_woffscorer/`: preserve actual upstream bytes, recompute identities,
execute independent upstream/local paths on common bounded inputs, retain raw outputs,
and count exceptions and classification differences separately from numeric outcomes.
The current topology survey and all six candidate adapters/checkers were inspected;
the candidate list is confirmed at the route/component scope below.

## Coverage and measured outcomes

This packet adds bounded official execution for six candidates. The prior packet's
nine QA components (fever, physicsquestions, sportsunderstanding, gsm8k, strategyqa,
hotpotqa, triviaqa, musique, twowikimultihopqa) and the previously recorded real
Terminal-Bench task keep their existing evidence and limitations. No prior receipt
is rewritten or upgraded. These controls are not benchmark accuracy or H0 trials.

All comparison counts below derive from raw fixture outputs. Different components,
representations and caller profiles are not combined into one agreement rate.

| Dataset | Actual upstream execution | Measured controlled comparison |
| --- | --- | --- |
| `reasoning_gym` | Full installed package import; direct methods for three admitted families | 24/24 numeric agree; 0 numeric divergences; 3 malformed inputs each raise official/local KeyError |
| `bird_minidev` | Unchanged AST-selected SQLite EX functions; full official import fails (`psycopg2`) | 9 agree, 2 numeric divergences, 1 upstream zero/local-unmeasured classification among 12 inputs |
| `ds1000` | Complete upstream execution runner; unchanged selected official test composition; full test module import on authored gzip | 9/9 agree; strict socket-denial failure retained; successful path permits local UNIX IPC |
| `spreadsheetbench` | Full upstream evaluation module and CLI; same authored workbook bytes | Direct 15/15 numeric agree plus 4 nonnumeric boundaries; strict caller 16/16 agree plus 3 unmeasured; separate formula workflow 1 divergence (official 0/local recalculated 1) |
| `jericho` | Full installed package/native Frotz runtime; fresh replay including labelled study positive | 5/5 agree; 0 divergences; 0 final unmeasured |
| `scienceworld` | Full installed package/JVM runtime; fresh loopback-isolated replay; zero-score traces only | 4/4 agree; 0 divergences; 0 final unmeasured |

The first four components use wholly authored entries, SQLite worlds, code contexts
or workbooks. The world controls use explicitly selected **study** game/task content:
four authored Jericho traces plus one labelled reference-derived study walkthrough,
and four authored ScienceWorld traces. Reference-derived inputs are not called
synthetic predictions. No released heldout task is scored, and no model, GPU,
endpoint, production verifier, pilot or benchmark task runner is invoked.

## Exact remaining coverage and closure boundary

The assessment's list of fourteen without evidence **from the earlier packet** is
narrowed by the six newly covered components above. No new execution is supplied
here for `alfworld`, `appworld`, `bfcl_v3`, `chessbench_puzzles`, `gaia`,
`livecodebench`, `tau_bench`, or `terminal_bench`. This is a statement of packet
coverage, not proof that their scorers are unavailable. These eight were not
executed by w-offscorer2. Terminal-Bench already has genuine execution evidence
for its one real `openssl-selfsigned-cert` task in `reports/w-net-receipts.md`;
that evidence remains bounded and is not generalized to its other tasks. Other
historical native controls retain their original classifications.

The candidate six are also only partially covered: Reasoning Gym's other families,
BIRD's full module and non-SQLite/other metrics, DS-1000 benchmark aggregation and
released task/library breadth, SpreadsheetBench's upstream formula-opening workflow
and original three-variant release, other Jericho games, and positive-score/other
ScienceWorld tasks remain outside these controls. Installed Jericho/ScienceWorld
version+byte identities do not authenticate a published source revision. Pinned
BIRD/DS archives reuse existing adapter source pins without new remote attestation.
These provenance and execution limits alone prevent treating S4 as satisfied.

S1 dataset-specific pinned closures, S3 complete transitive image/ABI dependencies,
S4 official provenance/execution and S6 valid live controls remain partial. This task adds no
production runtime, private-input/export equivalence or resource/lifecycle admission.
Both shared next_actions/statuses and every dataset record/reference stay unchanged.
Only the shared `scorer-offline-closure.observed` and one additive evidence locator
are updated. Historical reports are preserved as dated assessments.

## Commands, raw evidence and integrity

All new controlled inputs, source copies, official/local outputs, raw failures,
commands and comparison files are under `tests/fixtures/hg_woffscorer2/`. The root
`SHA256SUMS` covers the whole packet, including nested manifests; `coverage-summary.json`
is derived from actual component comparisons. `local-source-pins.json` freshly hashes
23 unchanged production adapter/helper/check files against baseline `9dab533`.

Exact executed scoring commands, original execution working directories, scorer
identities and freshly recomputed digests appear in the component sections below.
Every command is bounded and offline at the declared profile: strict seccomp socket
denial, DS-1000's explicit local UNIX IPC exception, or a new network namespace with
only loopback for ScienceWorld/LibreOffice IPC. Native subprocesses inherit those
boundaries. Earlier runtime failures and fixture mistakes remain preserved, with no
score substituted for failed measurement. Root validation and checker/test output
are `reports/w-offscorer2-validation.txt`.

Final validation checks all 236 packet files and 23 unchanged production source
files; the registry checker is valid and all 54 focused registry tests pass.
The full whitespace check reports only verbatim upstream source whitespace;
the check excluding those exact source copies passes. No scorer body is cleaned
or rewritten to make a formatting check pass.

Recheck integrity and scope without replaying worlds or candidate code:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/hg_woffscorer2/verify.py
PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/hg_woffscorer2/bird_ds/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/hg_woffscorer2/spreadsheetbench/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/hg_woffscorer2/worlds/verify.py
python3 tools/check_dataset_blockers.py
```

The following sections embed the reviewed component reports, including every
per-input outcome and the exact exceptions/divergences. Their component-specific
coverage statements refer only to that component; the table above is the combined
new scope. Original execution paths in raw receipts remain historical paths after
integration; reproduction scripts and validators derive the current checkout root.


<!-- Reviewed component: reasoning-gym -->

# Reasoning Gym controlled official execution - w-offscorer2

The complete installed `reasoning-gym==0.1.25` package imports offline. Direct upstream
`create_dataset(family, seed=20261008, size=20).score_answer(answer, entry)` is compared
with unchanged `data.datasets.reasoning_gym.score` on the same authored predictions
and entries. No generated item (`dataset[index]`) or released pool row is accessed.
Scope: `chain_sum`, `letter_counting`, `word_sorting`, three admitted families only;
this does not execute every admitted family or establish family eligibility.

Upstream `open-thought/reasoning-gym`, tag `v0.1.25`, commit
`21e6d2a9a581b3e11aafe711abfd37402f8482d5`. `run.py` recomputes the published wheel
SHA-256 `7f17a3eddb13c015d7d4a755ed576a061df889faf9468bcc2cca334ebe9e0435`,
checks it against preserved PyPI release JSON, then rehashes all 200 actual installed
package members and checks byte equality with that wheel and Git blob equality with
the preserved nontruncated tree. Prior provenance responses are in
`tests/fixtures/hg_wprov/reasoning_gym/responses/`; their newly recomputed digests,
all installed member paths/digests and selected callable identities are retained in
both `official.json` and `local.json`. The package manifest hash includes actual
installed paths; it is an observation, not a portable dependency closure.

Recomputed source-file hashes:

| Method | Source | SHA-256 |
| --- | --- | --- |
| `chain_sum` | `reasoning_gym.arithmetic.chain_sum.ChainSumDataset.score_answer` | `7e811214e9e31aa67eeb5490a0cf8eb275fceab609c4523bb38ceec9f8dbcb9f` |
| `letter_counting` | `reasoning_gym.dataset.ProceduralDataset.score_answer` | `480caacca5b12865e13bac68937687a799977e040ace5ae0496e71c1d77971e6` |
| `word_sorting` | `reasoning_gym.algorithmic.word_sorting.WordSortingDataset.score_answer` | `32d554acf0613b0cec4236a806165bebb426420a851a9e5468943a0cb8deff41` |

`chain_sum` also calls unchanged `reasoning_gym.utils.compute_decimal_reward`;
its containing file is part of the freshly verified package member manifest.
`letter_counting` inherits `ProceduralDataset.score_answer`.

Exact executed command, repository-root cwd:

```sh
bash tests/fixtures/hg_woffscorer2/reasoning_gym/commands.sh
```

The checked-in script expands to each of `official`, `local`, `compare`:

```sh
timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 tests/fixtures/hg_woffscorer2/reasoning_gym/offline_exec.py tests/fixtures/hg_woffscorer2/reasoning_gym/run.py official > tests/fixtures/hg_woffscorer2/reasoning_gym/official.json 2> tests/fixtures/hg_woffscorer2/reasoning_gym/official-offline.txt
```

The other two invocations replace `official` with `local` / `compare` in both
argument and output basenames. `offline_exec.py` is copied byte-for-byte from
`tests/fixtures/hg_wverify/scorers/offline_exec.py`; its kernel seccomp filter denies
all socket APIs and io_uring_setup before importing scorers, with real IPv4/IPv6/UNIX
EPERM probes in all three `*-offline.txt` receipts. Limits are wall 150 s, CPU 120 s,
file descriptors 256. The local adapter import attempts one Python open of
`/mnt/20t/xubuqiang/datasets/reasoning_gym/pool.jsonl`; the audit hook denies it
before any content read, and the adapter catches that import-time provisioning
failure. Its record cache is asserted empty before and after direct scoring.
`local-offline.txt` preserves that denied open; official/compare denial lists are
empty. No native table reader or adapter `load()` call is invoked. This is a
fixture guard, not a production verifier/runtime observation.

Measured: **27 authored inputs; 24 numeric comparisons; 24 agreements; 0 numeric
divergences; 3 official and 3 local errors on the same 3 malformed inputs.**
The nullable predictions are explicit API-boundary controls. Malformed entries are
deliberate invalid-schema probes, excluded from numeric agreement counts. Raw
tracebacks remain in both outputs. Partial substring credit (including `1000.1`
against `1000`) is an observed upstream return and adapter agreement, not an accuracy
claim. No exceptions are converted to zeros.

All component paths below resolve under `tests/fixtures/hg_woffscorer2/reasoning_gym/`:
`inputs.json`, full `official.json` / `local.json`, and `compare.json`.

| Input | Prediction | Official | Local | Outcome |
| --- | --- | --- | --- | --- |
| `chain_sum-01` | `"1000"` | 1.0 | 1.0 | agree |
| `chain_sum-02` | `"+01,000.00"` | 1.0 | 1.0 | agree |
| `chain_sum-03` | `"1000.1"` | 0.6666666666666666 | 0.6666666666666666 | agree |
| `chain_sum-04` | `"value=1000"` | 0.4 | 0.4 | agree |
| `chain_sum-05` | `""` | 0.0 | 0.0 | agree |
| `chain_sum-06` | `null` | 0.0 | 0.0 | agree |
| `chain_sum-07` | `"wrong"` | 0.0 | 0.0 | agree |
| `chain_sum-08` | `" 1000 "` | 1.0 | 1.0 | agree |
| `letter_counting-01` | `"42"` | 1.0 | 1.0 | agree |
| `letter_counting-02` | `"042"` | 0.6666666666666666 | 0.6666666666666666 | agree |
| `letter_counting-03` | `"x42"` | 0.6666666666666666 | 0.6666666666666666 | agree |
| `letter_counting-04` | `"42x"` | 0.6666666666666666 | 0.6666666666666666 | agree |
| `letter_counting-05` | `" 42 "` | 0.5 | 0.5 | agree |
| `letter_counting-06` | `""` | 0.0 | 0.0 | agree |
| `letter_counting-07` | `"wrong"` | 0.0 | 0.0 | agree |
| `letter_counting-08` | `null` | 0.0 | 0.0 | agree |
| `word_sorting-01` | `"alpha, beta, gamma"` | 1.0 | 1.0 | agree |
| `word_sorting-02` | `"gamma, beta, alpha"` | 0.3333333333333333 | 0.3333333333333333 | agree |
| `word_sorting-03` | `"alpha, gamma, beta"` | 0.3333333333333333 | 0.3333333333333333 | agree |
| `word_sorting-04` | `" alpha , beta,gamma"` | 1.0 | 1.0 | agree |
| `word_sorting-05` | `""` | 0.0 | 0.0 | agree |
| `word_sorting-06` | `null` | 0.0 | 0.0 | agree |
| `word_sorting-07` | `"wrong"` | 0.0 | 0.0 | agree |
| `word_sorting-08` | `"alpha, alpha, alpha"` | 0.3333333333333333 | 0.3333333333333333 | agree |
| `chain_sum-malformed-entry` | `"x"` | KeyError | KeyError | error; unscored |
| `letter_counting-malformed-entry` | `"x"` | KeyError | KeyError | error; unscored |
| `word_sorting-malformed-entry` | `"x"` | KeyError | KeyError | error; unscored |

The malformed `chain_sum` / `letter_counting` entries each raise `KeyError('answer')`;
`word_sorting` raises `KeyError('metadata')`, independently in official and local
calls. These six exceptions constitute three nonnumeric inputs. No divergence was
measured in the numeric domain covered. No claims extend to the other families,
all dependency ABIs, selected private input custody, exported state equivalence or
live harness execution. Shared and dataset blockers remain open.


<!-- Reviewed component: bird-ds -->

# BIRD Mini-Dev and DS-1000 bounded upstream execution - w-offscorer2

Disposition: `scorer-offline-closure` remains open; S1, S3, S4 and S6 remain partial.
No dataset blocker is closed and no H0, model, GPU, endpoint or released benchmark task is executed.
The topology survey correctly identifies both routes as native actor-workdir checks; DS-1000 additionally launches the official execution runner child.

All component-relative paths below are under `tests/fixtures/hg_woffscorer2/bird_ds/`.
`inputs.json` contains authored synthetic SQL worlds, contexts and candidate code.
`source-identity.json` records independently recomputed hashes of the existing adapter-pinned local official codeload archives and exact retained archive members; no new remote attestation or network acquisition was performed.
The adapters and production checkers are unchanged. Both comparisons invoke the real unchanged local `verify/check.py` in a fresh synthetic work directory.

## Reproduction and exact commands

The actual working directory was the registered `/tmp/hg-offscorer2-sqlds` worktree. Run from any repository root containing the packet:

```sh
bash tests/fixtures/hg_woffscorer2/bird_ds/commands.sh
python3 tests/fixtures/hg_woffscorer2/bird_ds/validate.py
```

The first command performs local archive custody, scorer executions, comparison and the registry checker. Its exact commands are preserved verbatim in `commands.sh`:

```sh
#!/usr/bin/env bash
set -euo pipefail
# Invoke from repository root. Acquisition uses local archives only, not network.
packet=tests/fixtures/hg_woffscorer2/bird_ds
export PYTHONDONTWRITEBYTECODE=1
export CUDA_VISIBLE_DEVICES=
python3 "$packet/prepare.py" > "$packet/preparation-output.json"
timeout 150s python3 "$packet/offline_exec.py" "$packet/execute.py" bird-official > "$packet/bird-official.json" 2> "$packet/bird-official-offline.txt"
timeout 150s python3 "$packet/offline_exec.py" "$packet/execute.py" bird-local > "$packet/bird-local.json" 2> "$packet/bird-local-offline.txt"
timeout 150s python3 "$packet/offline_exec.py" "$packet/execute.py" ds-strict-probe > "$packet/ds-strict-probe.json" 2> "$packet/ds-strict-probe-offline.txt"
timeout 150s python3 "$packet/offline_exec.py" --unix-ipc "$packet/execute.py" ds-official > "$packet/ds-official.json" 2> "$packet/ds-official-offline.txt"
timeout 150s python3 "$packet/offline_exec.py" --unix-ipc "$packet/execute.py" ds-local > "$packet/ds-local.json" 2> "$packet/ds-local-offline.txt"
timeout 150s python3 "$packet/offline_exec.py" "$packet/compare.py" > "$packet/comparison.json" 2> "$packet/comparison-offline.txt"
python3 tools/check_dataset_blockers.py > "$packet/registry-validation.json"
```

`prepare.py` hashes archive bytes with `hashlib.sha256(...).hexdigest()` and asserts equality to the pinned adapter constants before extraction. `validate.py` recomputes all retained source and production-checker digests, derives comparison statuses independently, checks identical initial database bytes, verifies guard probes/cleanup and validates the SHA-256 manifest. `validation.txt` preserves the validation command and checker output.

## Official source identity

- `bird_minidev` revision: `abd11b6db92a1c9f809b32f7564c7c71b34d67f0`. Archive: `/mnt/20t/xubuqiang/datasets/bird_minidev/_src/evaluation.tar.gz`. Recomputed SHA-256: `e70bcf57ed7dcc1ab4a55e38a14fa12d8bf7ff0cc2e66db673e4d55b16f5050b`.
  - Upstream member `mini_dev-abd11b6db92a1c9f809b32f7564c7c71b34d67f0/evaluation/evaluation_ex.py`; retained `source/bird_minidev/evaluation_ex.py`; recomputed SHA-256 `da1bbcd4530be83692d7c650c814ea9704bb710d0c953eb75d02ccb38233cf89`.
  - Upstream member `mini_dev-abd11b6db92a1c9f809b32f7564c7c71b34d67f0/evaluation/evaluation_utils.py`; retained `source/bird_minidev/evaluation_utils.py`; recomputed SHA-256 `f6943d249caac5aeaef9bce21d43dbf29dcef85a0c965a76df032a9542f308bf`.
- `ds1000` revision: `b39aab71`. Archive: `/mnt/20t/xubuqiang/datasets/ds1000/_src/ds1000-repo.tar.gz`. Recomputed SHA-256: `b14f1a2b0fb20ef55f0693019122f22c82b03ef6647faabf0e6e8ae1272a1dc0`.
  - Upstream member `DS-1000-b39aab71/test_ds1000.py`; retained `source/ds1000/official_test_ds1000.py`; recomputed SHA-256 `32ebe279eefa2d3cb1d633a82b43954ea813567e2fca28a9f6d777ce7f04d50c`.
  - Upstream member `DS-1000-b39aab71/execution.py`; retained `source/ds1000/execution.py`; recomputed SHA-256 `fab0beb2a5c3300f4540c2225ffc013881e5770fed388ad20d4620ae040cd311`.

## BIRD Mini-Dev execution scope and findings

The full unchanged official `evaluation_ex.py` import was attempted offline and failed with `ModuleNotFoundError: No module named 'psycopg2'` in `evaluation_utils.py`. The original full-import traceback is retained in `bird-official.json`; this is not represented as successful full-module import.

The successful bounded path executes the unchanged upstream AST-selected `calculate_ex`, `execute_model`, `connect_db` and `execute_sql` definitions, with real installed `func_timeout` and stdlib SQLite. Each call is `execute_model(prediction, gold, fresh_database, input_index, 30.0, "SQLite")`. Bodies are not edited or reimplemented. Other SQL dialects, Soft-F1, R-VES and full dataset/CLI aggregation are uncovered. The selected function hashes/line positions and actual dependency identities are retained in `bird-official.json`.

| Selected upstream function | Recomputed selected-source SHA-256 |
| --- | --- |
| `connect_db` | `da85ab94f6ea0baebe7537ceaffc2ebb1aee6ea058450f7cfd743763b6b450d8` |
| `execute_sql` | `5a50a8737043603024004dd150b93bd56fa4345f5f780cc0f3fcb56a1ad97071` |
| `calculate_ex` | `a93d78d74252e7961f6811407fef01517b541cf6791c656522f4208b9b5e756e` |
| `execute_model` | `9a1a675dd56be80e534b7ffc381caef265eab61cfc928abb1fc9e2f7d924bc66` |

Every official/local pair starts from an independently rebuilt database; `initial_database_sha256` matches for every paired input. Temporary worlds are removed and the per-record cleanup observations are retained. Mutations occur only within the authored temporary database.

Measured: **12 controls, 9 numeric agreements, 2 numeric divergences, 1 local-unmeasured outcome, 0 uncaught official per-input exceptions**. The full-import exception above is separate.

| Input | Official EX | Local reward | Classification |
| --- | ---: | ---: | --- |
| `exact` | 1 | 1.0 | agree |
| `order` | 1 | 1.0 | agree |
| `duplicates` | 1 | 1.0 | agree |
| `wrong_subset` | 0 | 0.0 | agree |
| `empty_result` | 1 | 1.0 | agree |
| `null` | 1 | 1.0 | agree |
| `wrong_column_order` | 0 | 0.0 | agree |
| `bad_prediction` | 0 | 0.0 | agree |
| `blank_nonempty_gold` | 0 | 0.0 | agree |
| `blank_empty_gold` | 1 | 0.0 | diverge |
| `bad_gold` | 0 | none | local_unmeasured |
| `mutation_delete` | 1 | 0.0 | diverge |

- `blank_empty_gold`: upstream executes an empty prediction as an empty result, compares it to the empty gold result and returns 1. The local check intentionally classifies a blank answer as measured 0.
- `mutation_delete`: upstream runs `DELETE FROM numbers` first and then gold `SELECT`, so both fetched result sets are empty and EX is 1. The local check executes gold first and retains the original rows, then runs `DELETE`; its reward is 0. This is a measured order/mutation divergence.
- `bad_gold`: upstream `execute_model` catches the SQL failure and returns EX 0. The local check exits 3, writes `measured:false`, and writes no reward. This is an unmeasured classification difference, never a numeric zero or numeric agreement.
- `bad_prediction`: local evidence reports `OperationalError: no such column: missing`; upstream's exception-catching scorer returns EX 0. The values agree; the caught SQL failure is preserved as a finding.

Raw official results: `bird-official.json`; complete subprocess outputs, return codes/rewards/evidence: `bird-local.json`; per-input comparisons: `comparison.json`.

## DS-1000 execution scope and findings

`execution.py` imports and executes in full, unchanged. The complete upstream `test_ds1000.py` also imports successfully against an authored temporary `data/ds1000.jsonl.gz`; it loads only the controlled contexts and metadata. Its dataset-wide process-pool evaluation function is not called. The upstream `test_program` assignment is selected unchanged from its AST and executed against the same candidate/context pairs; each composed program is then passed sequentially to the complete unchanged `execution.check_correctness(program, timeout=120, completion_id=input_index)`. Program bytes, their hashes, raw runner results and completion IDs are retained. This proves complete official execution-runner use and bounded official construction execution, not execution of the complete benchmark aggregation function.

Recomputed selected-construction source SHA-256: `d2cc26d7569b7604f37264c75ce458c0a1a24eaaa88d2c52d1de9911d9409df3`.

Measured: **9 controls, 9 numeric agreements, 0 numeric divergences, 0 unmeasured controls and 0 uncaught per-input official exceptions**.

| Input | Official pass score | Local reward | Raw official runner result |
| --- | ---: | ---: | --- |
| `correct` | 1 | 1.0 | `passed` |
| `incorrect` | 0 | 0.0 | `failed: ` |
| `syntax_error` | 0 | 0.0 | `failed: invalid syntax (<string>, line 1)` |
| `runtime_error` | 0 | 0.0 | `failed: controlled failure` |
| `empty` | 0 | 0.0 | `failed: 'answer'` |
| `string_pass` | 1 | 1.0 | `passed` |
| `string_fail` | 0 | 0.0 | `failed: ` |
| `marker_without_helper` | 0 | 0.0 | `failed: name 'test_string' is not defined` |
| `system_exit` | 0 | 0.0 | `failed: controlled exit` |

The assertion, syntax, runtime, empty-answer and `SystemExit` failures are raw upstream runner outcomes, not fabricated zeros. `marker_without_helper` confirms that both constructions use the literal substring `test_string(` even when it occurs only in a comment, producing the measured `name 'test_string' is not defined` failure. No production code is changed to smooth over this finding. The successful controls exercise both plain execution and the conditional string test.

### Offline guard limitation and strict failure

The initial strict socket-denial probe genuinely fails: `multiprocessing.Manager()` raises parent `EOFError`; its child traceback shows `PermissionError: [Errno 1] Operation not permitted` while creating AF_UNIX IPC. `ds-strict-probe.json` and `ds-strict-probe-offline.txt` preserve both tracebacks; no score is substituted for this failed runtime attempt.

Successful DS scorer calls therefore use the fixture-only `--unix-ipc` guard mode: kernel seccomp denies all socket/socketpair domains except AF_UNIX and denies `io_uring_setup`, with inherited socket descriptors above stderr closed. IPv4 and IPv6 socket creation probes fail with EPERM; AF_UNIX is explicitly permitted for upstream local multiprocessing. The guard is inherited across exec/fork. This is offline execution with an explicit local-IPC exception, not an assertion of blanket socket denial or production isolation. Authored candidates contain no network/IPC operations. BIRD and comparison calls retain the strict mode that denies AF_UNIX too.

Every guard receipt preserves interpreter/libseccomp identities, CPU/file-descriptor limits, explicit `production_runtime_observation:false`, socket probes and an empty denied-external-dataset-read list. Outer calls are bounded by `timeout 150s`; execution is sequential. Local DS scratch directories are confined with `TMPDIR` to the fresh synthetic world and removed with it. No run receipts, frozen receipts or production adapter/scorer files are modified.

Raw official results: `ds-official.json`; complete local outputs: `ds-local.json`; all comparisons: `comparison.json`. This packet covers no released DS rows, numerical libraries' task breadth, timeout control or transitive dependency/ABI closure.

## Exact new coverage and remaining scope

This component newly covers **`bird_minidev` (unchanged upstream SQLite EX execution functions)** and **`ds1000` (complete upstream execution runner plus selected unchanged test composition)**.
No new official execution evidence is supplied by this component for `alfworld`, `appworld`, `bfcl_v3`, `chessbench_puzzles`, `gaia`, `jericho`, `livecodebench`, `reasoning_gym`, `scienceworld`, `spreadsheetbench`, `tau_bench` or `terminal_bench`. Other w-offscorer2 components may independently narrow that list. Existing Terminal-Bench evidence remains separately bounded to its previously recorded real task. This component narrows only S4; all shared/dataset blocker states remain unchanged here.


<!-- Reviewed component: spreadsheet -->

# SpreadsheetBench bounded official execution - w-offscorer2

`spreadsheetbench` now has bounded **complete upstream module and official CLI execution** on authored workbook controls. This packet narrows only S4; `scorer-offline-closure` remains open and no dataset blocker is closed. It establishes no production H0 authorization or benchmark accuracy.

## Source identity and scope

Executed the unmodified `RUCKBReasoning/SpreadsheetBench` source `evaluation/evaluation.py` at revision `e2758ac01c6c52efc746bf0d53b2fd01dbc42dd2`. Its lossless bytes were decoded from the already-local GitHub contents response at `reports/w-spread2-evidence/official-source-response.json`; the response is preserved again in `source/official-source-response.json`. The source copy is `source/official-evaluation.py`, recomputed SHA-256 `4ae77cee8df01d1f34684fceab972810d696886533d33be2e89373de6b4d3de3`, and recomputed Git blob SHA-1 `d8109e9509f06fc67e9458fbbd4d494e086e48fc`. The API receipt's immutable URL and blob are checked by `prepare.py`. There is no new acquisition or network request, and no independent authenticity beyond that inherited source receipt is claimed.

The pinned `verified_400` mirror identity is separately recomputed: adapter-declared Hub revision `ab0b742b0fc95b946f212d80ac7771b5531272e4`, archive SHA-256 `10ef893dd29cb13ab97143ea787e68cdc9574a13873ab9a54e50b31dc03fc949`, metadata SHA-256 `bcecaa89a005bd4e3bbe98da150a86e8062c27f262e575d5e47bd9861b3525e7`. The installed metadata is byte-identical to its archive member. These are mirror inventory identities, **not released-task scoring evidence**. No released instruction or workbook was scored. All paths and recomputed identities are in `source-identity.json`.

All fixture-relative paths in this report resolve under `tests/fixtures/hg_woffscorer2/spreadsheetbench/`. `SHA256SUMS` covers controlled input bytes, source copies, runners and raw outputs. `inputs.json` authors `19` input definitions and `inputs/<id>/` preserves actual golden/result XLSX bytes and task metadata. The full upstream module imports normally with unchanged imports; no AST selection or module substitute was needed. Runtime versions and module digests are retained in `official.json`: openpyxl 3.1.2, NumPy 1.26.4, tqdm 4.66.4.

The local source is unchanged `data/datasets/spreadsheetbench/verify/check.py`, SHA-256 `9ec684b333d4d4ca648c76fe6991085a8c4d046f9a620566a945bf0cbcb7bd19`; adapter `data/datasets/spreadsheetbench.py`, SHA-256 `8fdfad8f320bce041555ca3b4c8b769b79d07ad971af78f314852eb5f9799505`. Official and local `compare_workbooks` consume **the same on-disk files, instruction_type and answer_position**. A separate upstream CLI profile builds its required three workbook copies per authored row, using identical bytes, while the local `main` profile uses a fresh copy once per row. This is a caller-policy comparison, not a claim that the one-pair mirror and three-variant original release are equivalent.

## Exact commands and offline enforcement

From the repository root, the complete packet was generated with:

```sh
bash tests/fixtures/hg_woffscorer2/spreadsheetbench/commands.sh
```

The exact expanded commands from that script are:

```sh
export PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=
python3 tests/fixtures/hg_woffscorer2/spreadsheetbench/prepare.py > tests/fixtures/hg_woffscorer2/spreadsheetbench/preparation.stdout.json
timeout 150s python3 tests/fixtures/hg_woffscorer2/spreadsheetbench/offline_exec.py tests/fixtures/hg_woffscorer2/spreadsheetbench/execute.py official > tests/fixtures/hg_woffscorer2/spreadsheetbench/official.json 2> tests/fixtures/hg_woffscorer2/spreadsheetbench/official.offline.txt
timeout 150s python3 tests/fixtures/hg_woffscorer2/spreadsheetbench/offline_exec.py tests/fixtures/hg_woffscorer2/spreadsheetbench/execute.py local > tests/fixtures/hg_woffscorer2/spreadsheetbench/local.json 2> tests/fixtures/hg_woffscorer2/spreadsheetbench/local.offline.txt
timeout 150s python3 tests/fixtures/hg_woffscorer2/spreadsheetbench/offline_exec.py tests/fixtures/hg_woffscorer2/spreadsheetbench/execute.py official-cli > tests/fixtures/hg_woffscorer2/spreadsheetbench/official-cli.json 2> tests/fixtures/hg_woffscorer2/spreadsheetbench/official-cli.offline.txt
timeout 150s python3 tests/fixtures/hg_woffscorer2/spreadsheetbench/offline_exec.py tests/fixtures/hg_woffscorer2/spreadsheetbench/execute.py local-main > tests/fixtures/hg_woffscorer2/spreadsheetbench/local-main.json 2> tests/fixtures/hg_woffscorer2/spreadsheetbench/local-main.offline.txt
bash tests/fixtures/hg_woffscorer2/spreadsheetbench/formula-netns-command.sh
python3 tests/fixtures/hg_woffscorer2/spreadsheetbench/compare.py > tests/fixtures/hg_woffscorer2/spreadsheetbench/comparison.stdout.json
```

`prepare.py` verifies already-local mirror inventory before scoring; it does not run a scorer. The four initial scorer invocations run through an unchanged copy of the prior `hg_woffscorer/offline_exec.py` guard (recomputed digest in source identity), which denies IPv4/IPv6/UNIX socket syscalls and io_uring at the kernel, closes inherited socket descriptors, and actively verifies denial. Its 120 CPU-second / 256-FD limits and interpreter/libseccomp digests are in all four `*.offline.txt` receipts; each outer command has a 150-second wall bound. Receipts record no attempted external dataset payload reads and `production_runtime_observation:false`. This fixture custody is not production filesystem/ABI/runtime closure. No model, GPU, endpoint, benchmark runner, historical run ID or frozen receipt is used.

The full upstream CLI child actually executed this exact command (also preserved in `official-cli.json`):

```sh
/mnt/8t/xubuqiang/anaconda3/bin/python3 /tmp/hg-offscorer2-spread/tests/fixtures/hg_woffscorer2/spreadsheetbench/source/official-evaluation.py --dataset controlled --setting control --model no-model-executed
```

Its recorded working directory was `/tmp/hg-woffscorer2-spread-cli-valyalw4/evaluation`. The fixture built only authored `../data/controlled/` files and retained exact raw CLI JSON in `official-cli-metrics.raw.json`, as well as the child stdout/stderr and exit status in `official-cli.json`. The temporary tree was removed on normal exit.

## Per-input results

Direct boolean outcomes: **15 numeric comparisons; 15 agreements, 0 numeric divergences; 4 nonnumeric inputs**. Official comparator exceptions: **2**. Local comparator exceptions: **3**. Exception/return differences are findings, not filled-in zeros.

Full upstream CLI exited **0**, executing **57 synthetic workbook-copy evaluations** (19 authored controls, three identical copies each). Caller-profile numeric outcomes agree **16/16**, with **0 numeric divergences** and **3 local unmeasured controls**. This does not combine the function-level and caller-policy counts.

| Authored input | Official comparator | Local comparator | Direct outcome | Official CLI three copies | Local full check |
| --- | --- | --- | --- | --- | --- |
| `exact-number` | 1 | 1 | agree | `[1, 1, 1]` | 1.0 |
| `numeric-string` | 1 | 1 | agree | `[1, 1, 1]` | 1.0 |
| `rounding-same` | 1 | 1 | agree | `[1, 1, 1]` | 1.0 |
| `rounding-different` | 0 | 0 | agree | `[0, 0, 0]` | 0.0 |
| `wrong-text` | 0 | 0 | agree | `[0, 0, 0]` | 0.0 |
| `blank-empty` | 1 | 1 | agree | `[1, 1, 1]` | 1.0 |
| `case-sensitive` | 0 | 0 | agree | `[0, 0, 0]` | 0.0 |
| `datetime-serial` | 1 | 1 | agree | `[1, 1, 1]` | 1.0 |
| `time-minute` | 1 | 1 | agree | `[1, 1, 1]` | 1.0 |
| `style-ignored` | 1 | 1 | agree | `[1, 1, 1]` | 1.0 |
| `first-sheet-default` | 1 | 1 | agree | `[1, 1, 1]` | 1.0 |
| `multi-range-wrong` | 0 | 0 | agree | `[0, 0, 0]` | 0.0 |
| `missing-result-sheet` | 0 | 0 | agree | `[0, 0, 0]` | 0.0 |
| `invalid-gold-sheet` | KeyError | KeyError | nonnumeric boundary | `[0, 0, 0]` | unmeasured (exit 3; no reward) |
| `malformed-column-only-range` | ValueError | 0 | nonnumeric boundary | `[0, 0, 0]` | 0.0 |
| `reversed-empty-range` | 1 | 1 | agree | `[1, 1, 1]` | 1.0 |
| `missing-artifact` | 0 | FileNotFoundError | nonnumeric boundary | `[0, 0, 0]` | 0.0 |
| `corrupt-artifact` | 0 | RuntimeError | nonnumeric boundary | `[0, 0, 0]` | unmeasured (exit 3; no reward) |
| `uncached-formula` | 0 | 0 | agree | `[0, 0, 0]` | unmeasured (exit 3; no reward) |

Raw tuple returns, printed output, exception messages and tracebacks are preserved in `official.json` / `local.json`; raw local evidence and its actual main arguments are in `local-main.json`. `comparison.json` contains joined per-input outcomes and machine-derived counts.

## Measured findings and remaining limits

- `malformed-column-only-range`: upstream direct `compare_workbooks` raises `ValueError: invalid literal for int() with base 10: ''`; local direct comparator returns false with its explicit official-equivalent-range-zero message. The actual upstream CLI catches the exception and emits `[0,0,0]`; local main produces measured zero. This is a caller-level compatibility result, not evidence that any cells were compared.
- `invalid-gold-sheet`: both direct comparators raise `KeyError: 'Worksheet Other does not exist.'`; upstream CLI swallows it into `[0,0,0]`, while local main records `measured:false`, exit 3 and no reward. This classification difference remains explicit.
- `missing-artifact`: official direct returns false (`File not exist`); local direct raises `FileNotFoundError`. The actual full callers both record zero for the absent authored result artifact.
- `corrupt-artifact`: official direct returns false (`File is not a zip file`); local direct raises `RuntimeError`. Official CLI produces `[0,0,0]`, while the local full check fails formula detection, records `measured:false`, exit 3 and no reward. This is not a numeric agreement.
- `uncached-formula`: both direct data-only comparators see `None` and return false. Upstream CLI also emits `[0,0,0]`; it does not recalculate workbooks. Local main attempts the documented installed LibreOffice path and fails under this strict no-socket profile: `LibreOffice exited 1: Warning: failed to launch javaldx - java may not function correctly` followed by `ERROR 4 forking process`. Its raw evidence has `recalculated:false`, `measured:false`, exit 3 and no reward. This initial profile does not establish production failure; the local-IPC retry below resolves the bounded offline conversion question. Upstream `evaluation/open_spreadsheet.py` was not available in this packet and was **not executed**. Official formula-recalculation workflow evidence remains uncovered.
- `reversed-empty-range`: both complete comparators and full callers accept the reversed range despite different authored A1 values, because it enumerates no cells. This observed vacuous pass is reported, not presented as semantic correctness.
- Compared return **booleans** agree for numeric controls. Diagnostic message strings differ (upstream often returns an empty string; local retains a mismatch reason); the comparison does not claim message-byte equality. Style changes are ignored by both scorers, matching the commented-out upstream fill/font checks. The actual data-only workbook read and the authored rounding, numeric-string, datetime, time, sheet and multi-range paths all ran.

## Separate formula retry with offline local IPC

The exact same authored `uncached-formula` input was copied fresh and passed through unchanged local `main` under a fresh **network namespace**, allowing LibreOffice's local UNIX IPC. This bounded retry is separate from, and does not overwrite, the strict deny-all-sockets failure above. Exact command:

```sh
export PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=
export HG_WOFFSCORER2_HOST_NETNS
HG_WOFFSCORER2_HOST_NETNS=$(readlink /proc/self/ns/net)
timeout 150s bwrap --unshare-net --die-with-parent --ro-bind / / --bind /tmp /tmp --proc /proc --dev /dev python3 tests/fixtures/hg_woffscorer2/spreadsheetbench/formula_netns_guard.py > tests/fixtures/hg_woffscorer2/spreadsheetbench/local-formula-netns.json 2> tests/fixtures/hg_woffscorer2/spreadsheetbench/local-formula-netns.offline.txt
```

`formula-netns-command.sh` retains this command. The receipt records distinct host/scorer network namespaces, only loopback in `/proc/net/dev`, no IPv4 routes, IPv6 routes on loopback only, bwrap/interpreter hashes and the same CPU/FD limits. No network interface connects it to the host network. A dataset-payload-read audit found no attempted external payload read. This is a different isolation profile from denying all socket syscalls; local IPC is allowed. It remains a controlled fixture, not production runtime custody.

Measured result: **1 numeric workflow comparison; 0 agreements, 1 divergence**. Actual official data-only comparator/CLI result is **0** on the uncached `=1+2` workbook; local full check now returns **1**, exit **0**, `recalculated:true`, `measured:true`. Its actual LibreOffice subprocess argv is captured by a read-only Python audit observer in `local-formula-netns.json`; the converted workbook bytes are retained in `formula-recalculated.xlsx` with a recomputed digest in that output. The original common input workbook is unchanged. This comparison measures **recalculation workflow policy**, not divergence in `compare_cell_value` or a successful upstream `open_spreadsheet.py` execution. `comparison.json:formula_netns_profile` retains the separate counts.

Coverage supplied by this fragment is **SpreadsheetBench only**, bounded to its exact official evaluation module/CLI controls. It does not establish original three-variant dataset release provenance, complete transitive dependencies, the complete upstream formula-opening workflow, platform-selected gold export or trusted actor runtime isolation. Other datasets are outside this fragment. S1, S3, S4 and S6 remain partial; neither the shared blocker nor a dataset blocker is closed.

Validation: `reports/w-offscorer2-spreadsheet-validation.txt` retains fixture validation, SHA-256 verification and blocker-checker output. The upstream source preserves its original trailing whitespace to remain byte-identical; diff whitespace validation excludes only that copied upstream file.


<!-- Reviewed component: worlds -->

# Jericho and ScienceWorld bounded upstream execution - w-offscorer2-worlds

**S4 gains bounded installed-upstream execution evidence for Jericho and ScienceWorld. The shared blocker remains open; no dataset blocker is closed.**

This packet lives under `tests/fixtures/hg_woffscorer2/worlds/`. It confirms the topology survey's native actor-workdir routes: Jericho's verifier rebuilds Frotz and replays action strings, and ScienceWorld's verifier rebuilds the JVM world and replays action strings. The official side imports each complete, unchanged installed upstream package and directly calls its runtime APIs. The local side imports the unchanged production `verify/check.py` and calls `main(argv)` on separate fresh worlds. It is not two local-verifier calls labelled official.

## Commands and offline boundary

Exact replay from the repository root:

```bash
bash -x tests/fixtures/hg_woffscorer2/worlds/commands.sh > tests/fixtures/hg_woffscorer2/worlds/commands-output.txt 2> tests/fixtures/hg_woffscorer2/worlds/commands-exact.txt
PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/hg_woffscorer2/worlds/verify.py > tests/fixtures/hg_woffscorer2/worlds/verification.json
python3 tools/check_dataset_blockers.py
```

`commands-exact.txt` retains the actual expanded timeout/env/bwrap/interpreter/script invocations, including the fresh scratch root. Official and local raw returns are `jericho-official.json`, `jericho-local.json`, `scienceworld-official.json` and `scienceworld-local.json`; `comparison.json` retains per-input results and counts. Inputs are `inputs.json`; all SHA-256 values are freshly recomputed by `prepare.py` and checked by `verify.py`, not copied from historical manifests.

Jericho uses the existing `tests/fixtures/hg_wverify/scorers/offline_exec.py` kernel seccomp guard. It denies all sockets and io_uring_setup, closes inherited socket descriptors, probes IPv4/IPv6/UNIX denial, and keeps complete guard receipts in `jericho-*-offline.txt`. The selected ROM is copied before scoring so external dataset payload reads are unnecessary.

ScienceWorld requires Python/JVM loopback IPC. Its exact `bwrap --unshare-net` commands establish a fresh network namespace with only `lo`, no IPv4 routes, and no inherited socket descriptors; `namespace_exec.py` checks a different namespace from the parent and records external-connect ENETUNREACH. The JVM stays inside that namespace. This is offline execution with local IPC, **not socketless execution**. Full device/route observations are preserved in `scienceworld-*-offline.txt`. Root mounts are read-only, with private writable `/tmp` and a fresh external scratch root. No model, GPU, endpoint or task runner executes.

Each dataset/mode command has a wall timeout and CPU/file-descriptor limits recorded in receipts. Cases execute sequentially, one fresh world per case per side. `execution-scope.json` records counts and bounds. This is a controlled scorer packet, not a pilot, eligible-task census, benchmark accuracy measurement, or production-runtime custody observation. No released evaluation task is played: selected Jericho `acorncourt` is outside the declared hash-eval split; ScienceWorld variation zero is absent from the checked-in canonical `task-3-find-non-living-thing` test-fold entries. The ScienceWorld full world uses no simplifications and never generates a gold path.

## Installed upstream identity and provenance limits

The identity pins are installed distribution versions plus freshly hashed installed Python/native/JAR bytes and package METADATA/WHEEL/RECORD. `identities.json` preserves absolute paths, sizes and every digest, alongside byte-identical Python source copies under `official-source/`. This does **not** authenticate a public source commit, independently validate wheel acquisition, or infer an upstream Git revision; `upstream_git_revision` is null. Jericho's reference-bearing `game_info.py` is hashed but deliberately not copied wholesale. Complete package imports read the installed package metadata in a trusted fixture process; this is not a selected-only production filesystem-isolation claim.

| Component | Identity | Recomputed SHA-256 |
| --- | --- | --- |
| `jericho/jericho.py` | installed `jericho==3.3.1` | `94f2e745cfd96deffaa95f7ea24b6be34a6ef29a2bc5c4b2bce891c1315353f8` |
| `jericho/libfrotz.so` | installed `jericho==3.3.1` | `1ade244682f43e1695489b22288e894a1d8b497c9785a7190991d7626e3996e0` |
| `scienceworld/scienceworld.py` | installed `scienceworld==1.2.3` | `23a37a2e9ed8e43d8c5e27d8660ea344d38a544abcd8c7e6af40071c7832ce68` |
| `scienceworld/scienceworld.jar` | installed `scienceworld==1.2.3` | `f4e1fdce0cdabe1bab7128a7e78ea820210d9db3c28d7272bcbbc3f3a1c5f0d7` |
| JRE `java` | staged Temurin release bytes, see `identities.json` | `f5aed21d3a0b0f4b05d3a3f9fe71263916d5bc0d47b53aa52a3340b90f0b4805` |
| JRE `libjvm.so` | staged Temurin release bytes, see `identities.json` | `11e5d09f442e42bddc4619b6eed829eaf3952158a5f77c797a58d558fae21738` |
| JRE `release` | staged Temurin release bytes, see `identities.json` | `a23a26314d44357bfbcee8358e63ffc117c42e6b6580bb0d27ccfef2c5d53983` |
| study ROM `acorncourt.z5` | selected local BYU-PCCL suite bytes | `7b13c904bf7608fa0de902ce7ecd5fcd0e026f293fc67baa87b99a35a3190c9e` |

The actual ScienceWorld JAR manifest is preserved verbatim in `identities.json`, including implementation/specification version. Its scoring code is the local installed JAR, not a fixture substitute. Local check/library hashes are in that same identity file and remain unchanged.

## Per-input measured results

Jericho upstream calls are `FrotzEnv(rom, seed=4)`, `reset()`, `get_max_score()`, `get_score()` and `step(action)`. Its maximum is a native return. The empty trace score is read by actual `get_score()`, not supplied by the verifier's empty-log initialization. ScienceWorld upstream calls are `ScienceWorldEnv('', None, envStepLimit=8)`, `load(..., generateGoldPath=False)`, `server.getScore()` and `step(action)`. ScienceWorld's 100-point scale is the unchanged upstream wrapper's `int(round(100 * getScore()))` unit convention, not an independently queried maximum. Empty traces read actual JVM `getScore()`; nonempty traces retain complete upstream `info` values and observations. Fractions are transparent unit conversions of those actual returns, compared to local reward.

The four authored Jericho traces are kept distinct from the positive, reference-derived study control. `acquire_study_reference.py` calls upstream `get_walkthrough()` only for selected non-heldout `acorncourt`; its exact returned actions and seed are `reference-selection.json`, and raw kernel-offline acquisition output is retained. This is a labelled study oracle control, not an authored trace or an accuracy measurement.

| Dataset/input | Official score | Scale/maximum | Official fraction | Local score/reward | Agreement |
| --- | ---: | ---: | ---: | --- | --- |
| `jericho/j-empty` | 0 | 30 | 0.0 | 0 / 0.0 | True |
| `jericho/j-look` | 0 | 30 | 0.0 | 0 / 0.0 | True |
| `jericho/j-impossible-command` | 0 | 30 | 0.0 | 0 / 0.0 | True |
| `jericho/j-get-ball` | 0 | 30 | 0.0 | 0 / 0.0 | True |
| `jericho/j-study-reference-full` | 30 | 30 | 1.0 | 30 / 1.0 | True |
| `scienceworld/s-empty` | 0 | 100 | 0.0 | 0 / 0.0 | True |
| `scienceworld/s-look` | 0 | 100 | 0.0 | 0 / 0.0 | True |
| `scienceworld/s-impossible-command` | 0 | 100 | 0.0 | 0 / 0.0 | True |
| `scienceworld/s-focus` | 0 | 100 | 0.0 | 0 / 0.0 | True |

`jericho`: **5 measured input comparisons, 5 agreements, 0 divergences, 0 unmeasured** in the final packet.

`scienceworld`: **4 measured input comparisons, 4 agreements, 0 divergences, 0 unmeasured** in the final packet.

Jericho's study positive control reaches the actual native maximum; raw per-step awards remain preserved. ScienceWorld controls all return zero and establish only fresh-world zero-score/invalid-action replay, not successful-task or positive-score execution. Neither sample establishes general scorer equivalence or coverage of other games/tasks.

## Preserved failures and corrected fixture mistakes

`preserved-first-attempt/` keeps the original inputs, scripts, identity, expanded commands and raw outputs. All four direct upstream ScienceWorld cases raised `FileNotFoundError: [Errno 2] No such file or directory: 'java'`: the fixture set JAVA_HOME but py4j's launch path also needed PATH to contain the JRE bin directory. The unchanged local helper already sets both, so its four first-attempt calls measured zero. Four ignored upstream destructor `AttributeError`s about absent `_gateway` are preserved in the same stderr. These are import/launch failures, not scores. The fixture-only PATH correction produced the later genuine JVM results; no production source changed.

The first-attempt fixture also assigned zero to empty official traces rather than querying upstream state. That was a fixture error and its apparent empty-trace agreement is not used as official evidence. Later execution reads native/JVM state explicitly; `preserved-second-attempt/` retains that corrected initial packet before the labelled study-positive control was added. Historical outputs are never smoothed into final scores.

## Cleanup and remaining scope

Official ScienceWorld child processes are closed and awaited; per-case termination/return-code observations are in `scienceworld-official-offline.txt`. The unchanged local verifier closes its world; local `child_cleanup` records and post-execution selected-child `/proc` observations are in `scienceworld-local.json` and `verification.json`. `cleanup.json` records removal of the final fresh scratch root. This bounded fixture cleanup evidence does not establish production snapshot ownership or trusted lifecycle closure.

Covered here: installed upstream Jericho and ScienceWorld scoring-runtime execution on the exact listed traces. This packet alone supplies no new execution evidence for ALFWorld, AppWorld, BFCL, BIRD, ChessBench, DS1000, GAIA, LiveCodeBench, Reasoning Gym, SpreadsheetBench, Tau-Bench or Terminal-Bench. Parent integration may incorporate separate packets. S1, S3, S4 and S6 remain partial, and no blocker or gate is closed.
