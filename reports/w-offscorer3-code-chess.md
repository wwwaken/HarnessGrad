# LiveCodeBench and ChessBench bounded official execution - w-offscorer3-code-chess

**S4 gains bounded official scorer execution evidence for `livecodebench` and `chessbench_puzzles`. `scorer-offline-closure` remains open; S1, S3, S4 and S6 remain partial, and no dataset blocker is closed.**

All packet-relative paths below resolve under `tests/fixtures/hg_woffscorer3/code_chess/`. Read first: `AGENTS.md`, `reports/w-offscorer-equivalence.md`, and `reports/w-offscorer2-coverage.md`. The same method is used: copy already-pinned scorer bytes, execute actual upstream code separately from unchanged production local scorers on identical authored inputs, preserve every raw return/error, and derive per-input counts. No released tasks, model, GPU, endpoint, benchmark runner, `runs/` path or frozen receipt is used. `execution-scope.json` records the limits and comparability scope.

## Reproduction and custody

Exact command from the repository root:

```bash
bash -x tests/fixtures/hg_woffscorer3/code_chess/commands.sh > tests/fixtures/hg_woffscorer3/code_chess/commands-output.txt 2> tests/fixtures/hg_woffscorer3/code_chess/commands-exact.txt
```

`commands.sh` and `commands-exact.txt` retain every expanded invocation. The scoring commands are:

```bash
export PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 JAX_PLATFORMS=cpu
timeout 150s python3 tests/fixtures/hg_woffscorer3/code_chess/offline_exec.py tests/fixtures/hg_woffscorer3/code_chess/execute.py chess-official > tests/fixtures/hg_woffscorer3/code_chess/chess-official.json 2> tests/fixtures/hg_woffscorer3/code_chess/chess-official-offline.txt
timeout 150s python3 tests/fixtures/hg_woffscorer3/code_chess/offline_exec.py tests/fixtures/hg_woffscorer3/code_chess/execute.py chess-local > tests/fixtures/hg_woffscorer3/code_chess/chess-local.json 2> tests/fixtures/hg_woffscorer3/code_chess/chess-local-offline.txt
timeout 150s python3 tests/fixtures/hg_woffscorer3/code_chess/offline_exec.py tests/fixtures/hg_woffscorer3/code_chess/execute.py lcb-official > tests/fixtures/hg_woffscorer3/code_chess/lcb-official-strict-probe.json 2> tests/fixtures/hg_woffscorer3/code_chess/lcb-official-strict-probe-offline.txt
export HG_WOFFSCORER3_PARENT_NETNS
HG_WOFFSCORER3_PARENT_NETNS=$(readlink /proc/self/ns/net)
timeout 150s bwrap --unshare-net --die-with-parent --ro-bind / / --bind /tmp /tmp --proc /proc --dev /dev python3 tests/fixtures/hg_woffscorer3/code_chess/namespace_exec.py tests/fixtures/hg_woffscorer3/code_chess/execute.py lcb-official > tests/fixtures/hg_woffscorer3/code_chess/lcb-official.json 2> tests/fixtures/hg_woffscorer3/code_chess/lcb-official-offline.txt
timeout 150s python3 tests/fixtures/hg_woffscorer3/code_chess/offline_exec.py tests/fixtures/hg_woffscorer3/code_chess/execute.py lcb-local > tests/fixtures/hg_woffscorer3/code_chess/lcb-local.json 2> tests/fixtures/hg_woffscorer3/code_chess/lcb-local-offline.txt
python3 tests/fixtures/hg_woffscorer3/code_chess/compare.py > tests/fixtures/hg_woffscorer3/code_chess/comparison.json
```

The seccomp guard is byte-identical to the prior `hg_woffscorer2/reasoning_gym/offline_exec.py`. It denies socket APIs for IPv4/IPv6/UNIX and `io_uring_setup`, closes inherited socket fds, and actively verifies EPERM. Every local LCB checker subprocess independently installs the same guard/audit hook; its raw stderr is preserved per input. Successful official LCB calls need `multiprocessing.Manager` UNIX IPC and instead run in a fresh bubblewrap network namespace, with only `lo`, no IPv4 routes, and a recorded external ENETUNREACH probe. It permits local IPC; it is not a socketless profile. Both guards impose CPU and file-descriptor limits and record actual interpreter identity; namespace receipts also hash bwrap. Dataset-read audit denial lists are empty. Python audit hooks are supplemental and do not establish a production filesystem sandbox.

`source-identity.json` freshly hashes existing archives, retained archive members and production sources. Archive assertions run in `prepare.py`; `verify.py` rechecks copies and unchanged production identities. No new public acquisition or independent authentication of archive revision is claimed. `SHA256SUMS` covers the full fixture packet, including historical mistakes and raw outputs. Validation command/output is `reports/w-offscorer3-code-chess-validation.txt`.

## LiveCodeBench

Actual complete upstream modules: `lcb_runner/evaluation/compute_code_generation_metrics.py`, `testing_util.py`, and `pass_k_utils.py`, from adapter-pinned `LiveCodeBench@28fef95ea8c9f7a547c8329f2cd3d32b92c1fa24`. Existing `upstream.tar.gz` recomputed SHA-256: `56c7c42aee979def86b69547ecd6d5a877a0e4940af8923bf4325ca0defecbaf`. The complete evaluation package initializer and its dependencies import unchanged; no AST selection or substituted module is used.

| Official scorer file | Recomputed SHA-256 |
| --- | --- |
| `compute_code_generation_metrics.py` | `073f388cc78bf0eb0ad35eaeb8bb509c0a3664963e5305d2be13d6b6eb6f3d21` |
| `testing_util.py` | `b7cb6a8a69807bb868150a61742e25d7bb5328bbe01d514471b6ec43c9fa9ed2` |
| `pass_k_utils.py` | `6af3ee55d40f96fa06fa511bd5e43d94b19604750e82454b4b3c1f45c5199010` |

The official side calls actual upstream `check_correctness(sample, generation, timeout=6, debug=False)`, which launches actual `run_test` in its own child, then actual `compute_metrics_from_results({"task": [results]}, k_list=[1])`. The local side separately executes unchanged `data/datasets/livecodebench/verify/check.py` via its real CLI and the same upstream executor/aggregation bytes materialized in fresh scratch. Local `tests.json` and `solution.py` are asserted byte-identical to the official argument strings. Local rewards/evidence, subprocess argv/cwd/stdout/stderr/exit, and cleanup are retained in `lcb-local.json`. Official raw per-test returns, metadata and captured output are retained in `lcb-official.json`.

Twelve authored inputs cover stdio, call-based evaluation, partial correctness, empty/missing method, syntax/runtime failure, a six-second per-test timeout, and empty/mismatched test payload boundaries. No benchmark input is used. **10 numeric comparisons: 10 agreements, 0 numeric divergences; 2 local unmeasured inputs.** Numeric agreement is about binary pass@1; the blank solution's per-test return differs (`[-4]` upstream versus `[]` local early measured zero), so per-test equivalence is not claimed. Timing metadata is naturally different.

<!-- LCB table generated from comparison.json -->

| Authored input | Official per-test | Official pass@1 | Local per-test | Local reward | Comparison |
| --- | --- | ---: | --- | ---: | --- |
| `stdio-pass` | `[True, True, True]` | 1.0 | `[True, True, True]` | 1.0 | agree |
| `stdio-wrong-first` | `[-2]` | 0.0 | `[-2]` | 0.0 | agree |
| `stdio-partial` | `[True, -2]` | 0.0 | `[True, -2]` | 0.0 | agree |
| `stdio-timeout` | `[-3]` | 0.0 | `[-3]` | 0.0 | agree |
| `stdio-runtime` | `[-4]` | 0.0 | `[-4]` | 0.0 | agree |
| `stdio-syntax` | `[-4]` | 0.0 | `[-4]` | 0.0 | agree |
| `stdio-empty` | `[-4]` | 0.0 | `[]` | 0.0 | agree |
| `call-pass` | `[True, True, True]` | 1.0 | `[True, True, True]` | 1.0 | agree |
| `call-wrong` | `[False]` | 0.0 | `[False]` | 0.0 | agree |
| `call-missing-method` | `[-4]` | 0.0 | `[-4]` | 0.0 | agree |
| `empty-tests` | `[]` | 1.0 | `None` | unmeasured | nonnumeric |
| `mismatched-tests` | `[True]` | 1.0 | `None` | unmeasured | nonnumeric |

`empty-tests` yields upstream `[]`, pass@1 **1**, due to vacuous aggregation; `mismatched-tests` yields `[True]`, pass@1 **1**, because upstream zips the unequal lists. The local wrapper refuses these with exit **3**, `measured:false` and no reward. These are classification findings, never converted to numeric agreements or zeros. `stdio-empty` is zero on both reward channels but local skips the executor; its per-test difference stays visible. The timeout sentinel is actual upstream **-3**, retained as a measured candidate failure on both sides; it is not an environment timeout.

The strict socket-denial probe imports the full upstream module but all **12** official calls raise parent `EOFError`; captured child tracebacks show `PermissionError: [Errno 1] Operation not permitted` on AF_UNIX socket creation inside `multiprocessing.Manager`. `lcb-official-strict-probe.json` preserves each error and traceback; no score is supplied for the failed profile. The successful isolated-namespace retry is distinct. The official successful process reports no active multiprocessing children on completion. Local fresh scratch removal is checked both in the raw output and independently by `verify.py`.

## ChessBench puzzles

Existing pinned `google-deepmind/searchless_chess@90ae0e6b121673fc3079aaeffa047580bb600c0a` archive SHA-256: `9cf0832b04024a9e0a6edb59f0dee62aeadee3b9b97799b9a7521b2221f7d39a`. Its actual `src/puzzles.py` SHA-256: `f8e5e1d6c41450924d6f62a0813b3c20b21facef1c160b623762f7cd135ea634`. The full unchanged module import was actually attempted and failed with **`ModuleNotFoundError: No module named 'absl'`**. `chess-official.json` retains that complete traceback; complete module execution is not claimed.

Following the prior packets' explicit AST method, the unchanged `evaluate_puzzle_from_board` function is selected and executed with its source locations retained, using actual `python-chess==1.11.2`. The exact selected source is `source/chess-selected-evaluate_puzzle_from_board.py`, SHA-256 `5d6b4f54aa5bfdd7557682955cbcf1485f8ff90e546326247163755136ed2ce0`. Only annotation resolution is postponed at compile time; the scorer body is unmodified. A scripted engine supplies authored UCI strings sequentially when upstream requests a move, and preserves the actual requested board FEN per call. Missing strings raise actual `StopIteration`; malformed UCI parsing raises the actual exception. This controlled engine shim supplies predictions, not scoring behavior.

The local side independently imports unchanged `data.datasets.chessbench_puzzles` and calls actual `score(prediction, gold)` on the same FEN, reference moves and prediction tokens. Both official and local gold/prediction fields are retained per input. The adapter's dataset record cache stays empty; no CSV is opened. The local reward is the documented **strict legal offline sequence** metric, while its `official.upstream` channel is a diagnostic. Neither is presented as interactive official puzzle accuracy or Elo.

Fifteen authored inputs yield **10 numeric strict-reward comparisons: 6 agreements, 4 divergences; 5 official-side exceptions**. Separately, the local upstream diagnostic agrees on **9/10** numeric official outcomes, diverging on the empty reference. The latter comparison is not combined with strict-reward counts.

<!-- Chess table generated from comparison.json -->

| Authored input | Official return/reward | Local strict reward | Local upstream diagnostic | Comparison |
| --- | --- | ---: | ---: | --- |
| `reference-short` | 1.0 | 1.0 | 1.0 | agree |
| `reference-long` | 1.0 | 1.0 | 1.0 | agree |
| `trailing-ignored` | 1.0 | 1.0 | 1.0 | agree |
| `wrong-legal` | 0.0 | 0.0 | 0.0 | agree |
| `missing-solver` | StopIteration | 0.0 | 0.0 | nonnumeric |
| `missing-later` | StopIteration | 0.0 | 0.0 | nonnumeric |
| `malformed-solver` | InvalidMoveError | 0.0 | 0.0 | nonnumeric |
| `illegal-reference-setup` | 1.0 | 0.0 | 1.0 | diverge |
| `illegal-reference-solver` | 1.0 | 0.0 | 1.0 | diverge |
| `setup-only` | 1.0 | 0.0 | 1.0 | diverge |
| `empty-reference` | 1.0 | 0.0 | 0.0 | diverge |
| `invalid-fen` | ValueError | 0.0 | 0.0 | nonnumeric |
| `reference-mate` | 1.0 | 1.0 | 1.0 | agree |
| `alternate-mate` | 1.0 | 1.0 | 1.0 | agree |
| `immediate-mate-extra-reference` | StopIteration | 1.0 | 0.0 | nonnumeric |

Measured numeric strict divergences: illegal reference setup (`e2e5`), illegal expected solver move (`e7e4`), setup-only reference and empty reference all yield upstream **1** versus local strict **0**. The upstream function uses unchecked `Board.push` and accepts exhausted or empty move lists. Strict scoring deliberately enforces legality and at least one solver move. The local upstream diagnostic has its own `bool(moves)` guard, so it returns **0** on the empty reference despite official **1**. These are measured metric/input-domain differences; they do not establish corruption of any released puzzle.

The five official-side exceptions are: missing first solver / missing later solver / continuing an authored reference after immediate mate, each **`StopIteration`** in the scripted prediction supplier; malformed solver **`InvalidMoveError`**; invalid FEN **`ValueError`** before scorer entry. Local scoring returns **0** on the first four malformed/missing input boundaries, and **1** after its legal immediate checkmate ends play. These are not five ordinary upstream zero scores. The correct reference mate and separately authored alternate immediate mate both execute and agree positively. Valid trailing submitted tokens are ignored by both callers.

## Preserved fixture mistakes and limits

`preserved-first-attempt/` retains the original failed local cache assertion (it expected `None`; the real empty cache is `[]`) and the initial intended alternate-mate position, which did not actually mate. `preserved-second-attempt/` retains two additional fixture mistakes: authored call inputs ended with a newline, causing JSON decoding of an empty argument; and upstream stdout/stderr were replaced with `StringIO`, so `faulthandler.enable()` encountered `fileno` errors and returned **-4**. These apparent all-zero official results are not used as final evidence. The corrected fixture uses well-formed authored call inputs, real temporary capture files and a verified legal alternate mate. `preserved-third-attempt/` retains the first corrected packet before the additional timeout control and independent local subprocess guard were added. All changes are fixture-only; no production adapter or scorer changed.

Covered by this fragment: full upstream LiveCodeBench scoring-module/runtime execution and unchanged ChessBench official function execution at the exact stated scopes. Complete ChessBench module import remains failed. This fragment supplies no official-execution evidence for `alfworld`, `appworld`, `bfcl_v3`, `gaia` or `tau_bench`; parent integration may add separate packets. `terminal_bench` remains partially covered by the prior real official `bash /tests/test.sh` receipt in `reports/w-net-receipts.md`; this fragment does not expand it. S1, S3, S4 and S6 remain partial, and every blocker stays open.
