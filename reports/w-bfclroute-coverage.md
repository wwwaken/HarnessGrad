# BFCL and ChessBench complete module route reachability - w-bfclroute

**Complete official routes remain unreachable offline: 0/2 requested dataset routes demonstrated; 0/43 primary controlled inputs have an official numeric return. No blocker closes.**

`scorer-offline-closure` remains open; **S1/S3/S4/S5/S6 remain PARTIAL**. Every dataset blocker, status, next_action, admission, refusal and historical record is unchanged; `production_authorized=false` remains unchanged. These are authored scorer/import controls, not a benchmark scoring run, dataset accuracy, H0 authorization or model execution.

Baseline `bf917b3b237e352ac46373fdba501d35004c7911`; registered worktree `/tmp/hg-bfclroute`, branch `wg-bfclroute`. Read `AGENTS.md`, both requested reports, both adapters in full and the prior raw scripts/results. A read-only child independently reviewed the source routes; root reviewed its findings against the numbered source. The earlier packet selected AST functions because full BFCL imports failed on `tree_sitter` and ChessBench on `absl`. This packet attempts actual complete modules with standard `importlib`, preserves failures and does **not** select AST bodies, patch dependencies, construct fake modules, or replace any scorer.

All packet-relative names below resolve under `tests/fixtures/hg_wbfclroute/`. `source-lines.txt` retains numbered original source; `source-entrypoints.json` and `source-imports.json` inventory definitions/imports statically. AST parsing only produces those inventories; it is never used to execute selected code.

## Exact official and local entrypoints

Let **B** be `tests/fixtures/hg_wbfclroute/source/bfcl/` and **C** be `tests/fixtures/hg_wbfclroute/source/chess/searchless_chess/`. These are literal repository paths; every following relative file resolves under the stated prefix, with original archive-member and retained-source identity in `identity.json`.

| Route | Complete-module entrypoints and behavior, file+line |
| --- | --- |
| BFCL module command / dispatch | `B/bfcl_eval/eval_checker/eval_runner.py:474` `main`; script entry `:512`; category expansion `:488`; catalogue membership `:494`; `runner` `:502` / definition `:349`; configured handler `:382` / `get_handler:29`; `evaluate_task:410` called at `:390`. |
| BFCL Python Simple | `eval_runner.py:420` Python language default; prompts loaded `:432`; references `:442`; Simple dispatch `:457` to `ast_file_runner:246`; `handler.decode_ast:270`; actual output-format check `:287`; official `ast_checker:307`; accuracy denominator `:332`. All these files are under `B/bfcl_eval/eval_checker/`. |
| BFCL irrelevance | `B/bfcl_eval/eval_checker/eval_runner.py:434` calls `relevance_file_runner:171`; decoder `:188`; empty detection `:191`; decode exceptions `:195` intentionally count as no tool, with success choice `:202`. This route is distinct from Simple; a top-level import failure occurs before this policy and cannot count as a correct irrelevant answer. |
| BFCL actual prompting handler | `B/bfcl_eval/constants/model_config.py:1492` catalogue key `Qwen/Qwen3-0.6B` maps `QwenHandler` at `:1498`; `B/bfcl_eval/model_handler/local_inference/qwen.py:5` inherits OSS; `base_oss_handler.py:25` constructor creates OpenAI client at `:40`; decoder `:55` calls `B/bfcl_eval/model_handler/utils.py:695` `default_decode_ast_prompting`, then Python `ast_parse:241`. Generation is a separate method `base_oss_handler.py:63`, never called. The chosen historical catalogue key only defines a controlled response grammar; no model with that name is run, and it does not establish a mapping for `qwen3.5-9b-local`. |
| BFCL checker and eager catalogue/parser graph | `B/bfcl_eval/eval_checker/ast_eval/ast_checker.py:1` imports the entire model catalogue, which imports handlers at `B/bfcl_eval/constants/model_config.py:4` through `:70`. Shared `B/bfcl_eval/model_handler/utils.py:13` / `:14` import Java/JS parsers. Their `java_parser.py:1` and `js_parser.py:1` import `tree_sitter`; language/parser initialization is at `:4` / `:6`. Type converters are imported at `ast_checker.py:6` / `:7`. |
| BFCL paths / aggregation | `B/bfcl_eval/constants/eval_config.py:11` sets `PACKAGE_ROOT`; `:25` / `:27` set prompt/reference paths. `BFCL_PROJECT_ROOT:17` only redirects output/project state; mkdir sites `:34` / `:35`. Complete runner aggregation at `B/bfcl_eval/eval_checker/eval_runner.py:403` / `:405` reaches helper `get_category_score:148`, whose missing-category fallback `eval_runner_helper.py:155` reads other category files. Only two authored categories would not demonstrate the full leaderboard aggregate, even after dependencies were provisioned. |
| ChessBench full module | `C/src/puzzles.py:22` / `:23` import `absl.app/flags`; `:24`-`:27` import chess/engine/PGN/pandas; `:29` / `:30` import full engine constants/interface. `evaluate_puzzle_from_board:74` requests supplied solver moves at `:86`, with official unchecked push at `:91` / `:93`. |
| ChessBench pandas-row caller | `C/src/puzzles.py:58` `evaluate_puzzle_from_pandas_row`; PGN parsed at `:63`; initial board is **PGN end board** at `:66`; board evaluator called at `:67`. This differs from the adapter's directly supplied FEN interface. If import succeeded, supplementary row calls would use a declared setup-FEN PGN, without released rows. |
| ChessBench script / engine graph | `C/src/puzzles.py:97` `main`; CSV read with bounded `nrows` at `:105`; authentic `ENGINE_BUILDERS[_AGENT.value]()` at `:106`; row scoring `:109`; `app.run(main):119`. `C/src/engines/constants.py:24` imports JAX and `:27`-`:33` imports tokenizer/training/transformer/neural/Stockfish/Lc0. `C/src/training_utils.py:22`-`:28` imports chex, grain, haiku, jax, optax, orbax. Thus a supplied scripted prediction engine cannot avoid the complete module's eager ML imports. CLI native/model engine construction, binaries/checkpoints and whole CSV execution are not executed. |
| Actual local BFCL | `data/datasets/bfcl_v3.py:217` `score`: name-only normalization `:223`, multiset comparison `:225`, explicit diagnostic metric `:230`. Raw full-call text and projected name-only gold are retained per input. No claim of full-call metric equivalence. |
| Actual local ChessBench | `data/datasets/chessbench_puzzles.py:309` `score` calls strict legal `score_strict:297` and separate unchecked diagnostic `score_upstream:185`. Strict stepwise legality is checked at `:245`; the adapter explicitly labels its sequence contract different from interactive official puzzle accuracy. |

The retained BFCL projection is the prior Simple/irrelevance code-only scorer graph, not every category's dynamic tool runtime or package CLI generation graph. `eval_runner.py` is itself the official script/module scoring entry. No missing generation or multi-turn runtime is claimed installed or executed.

## Source bytes and offline runtime

`prepare.py` compares every BFCL source member against both its prior retained original and exact preserved archive member, and compares every Chess source member against its pinned archive. Only allowlisted code/license/spec/requirements bodies are opened; no task, answer, result, CSV, checkpoint or released solution member is read. Standard import resolution uses fresh private scratch package directories containing exact unmodified source, with no custom finder. Preparation imports the local adapters without populating their record caches.

| Dataset | Archive bytes read | Recomputed archive SHA-256 | Revision binding | Staged code/license/spec members |
| --- | ---: | --- | --- | ---: |
| `bfcl_v3` | 44552456 | `57854157e82aed5723a1458d2a4ac426e3256959ded4a20ddc4d627c22edb7fe` | `ea13468e4423454d0c213704fb87cf7cb3990433` | 83 |
| `chessbench_puzzles` | 2253771 | `9cf0832b04024a9e0a6edb59f0dee62aeadee3b9b97799b9a7521b2221f7d39a` | `90ae0e6b121673fc3079aaeffa047580bb600c0a` | 20 |

BFCL reuses preserved public tag/commit/archive custody; Chess revision remains the adapter pin plus matching archive member root, not a newly fetched remote attestation. `identity.json` records every exact source path/member, byte count and newly recomputed hash; raw preparation output is `prepare.stdout.txt`. Runtime module and unchanged adapter hashes are in each raw JSON output. Complete transitive wheel/image/ABI/provenance custody remains unmet.

Exact top-level commands are in `preparation-commands.txt`. `commands.json` and `ordered-import.command.json` preserve exact subprocess argv/cwd/environment, exits and raw stream filenames. For example, the actual primary BFCL child is `timeout 150s <recorded-python> <packet>/offline_exec.py <packet>/execute.py bfcl-official`. All scoring/import children run serially with CPU 120 seconds, wall 150 seconds, NOFILE 256, empty CUDA visibility, one OpenBLAS/OMP thread and JAX CPU configuration. No GPU/device/model/endpoint call occurs. No RSS, process or filesystem-quota enforcement is claimed by this fixture.

The unchanged prior seccomp wrapper closes inherited sockets and denies socket APIs plus `io_uring_setup` before imports. Every guarded raw stderr starts with measured IPv4/IPv6/UNIX EPERM probes, interpreter/libseccomp paths/hashes and limits, and ends with the dataset-read audit receipt. The supplemental Python audit hook excludes external dataset payload reads; it is not a native filesystem sandbox. Fresh code-only scratch is removed after each process, with pre-cleanup inventory and post-cleanup absence in raw JSON; validation rechecks absence. No production cleanup/admission claim follows. The only external dataset-directory read is preparation of the pinned Chess **source archive**, before scorer execution; no released puzzle data is opened.

## Actual complete-module reachability

`import-00.stdout.txt` through `import-17.stdout.txt` each retain a fresh-process complete import attempt, actual exception/traceback, loaded source hashes and passive Python call trace. The primary BFCL, Chess board and Chess row files separately retain each input's failed import, so imports are not inferred from older receipts. Collector exit 0 means it successfully captured the outcome; it does not mean the official module imported or the scorer ran.

| Actual official module | Fresh import outcome |
| --- | --- |
| `bfcl_eval.eval_checker.eval_runner` (`import-00.stdout.txt`) | `ModuleNotFoundError: No module named 'tree_sitter'` |
| `bfcl_eval.eval_checker.ast_eval.ast_checker` (`import-01.stdout.txt`) | `ModuleNotFoundError: No module named 'tree_sitter'` |
| `bfcl_eval.model_handler.utils` (`import-02.stdout.txt`) | `ModuleNotFoundError: No module named 'tree_sitter'` |
| `bfcl_eval.model_handler.local_inference.qwen` (`import-03.stdout.txt`) | `ModuleNotFoundError: No module named 'tree_sitter'` |
| `bfcl_eval.constants.model_config` (`import-04.stdout.txt`) | `ModuleNotFoundError: No module named 'tree_sitter'` |
| `bfcl_eval.model_handler.parser.java_parser` (`import-05.stdout.txt`) | `ModuleNotFoundError: No module named 'tree_sitter'` |
| `bfcl_eval.model_handler.parser.js_parser` (`import-06.stdout.txt`) | `ModuleNotFoundError: No module named 'tree_sitter'` |
| `bfcl_eval.eval_checker.ast_eval.type_convertor.java_type_converter` (`import-07.stdout.txt`) | imports complete module; no scorer invocation |
| `bfcl_eval.eval_checker.ast_eval.type_convertor.js_type_converter` (`import-08.stdout.txt`) | imports complete module; no scorer invocation |
| `bfcl_eval.eval_checker.eval_runner_helper` (`import-09.stdout.txt`) | `ModuleNotFoundError: No module named 'tree_sitter'` |
| `searchless_chess.src.puzzles` (`import-10.stdout.txt`) | `ModuleNotFoundError: No module named 'absl'` |
| `searchless_chess.src.engines.constants` (`import-11.stdout.txt`) | `ModuleNotFoundError: No module named 'jax'` |
| `searchless_chess.src.engines.engine` (`import-12.stdout.txt`) | imports complete module; no scorer invocation |
| `searchless_chess.src.engines.stockfish_engine` (`import-13.stdout.txt`) | `AttributeError: module 'chess' has no attribute 'engine'` |
| `searchless_chess.src.engines.lc0_engine` (`import-14.stdout.txt`) | imports complete module; no scorer invocation |
| `searchless_chess.src.engines.neural_engines` (`import-15.stdout.txt`) | `ModuleNotFoundError: No module named 'haiku'` |
| `searchless_chess.src.training_utils` (`import-16.stdout.txt`) | `ModuleNotFoundError: No module named 'chex'` |
| `searchless_chess.src.utils` (`import-17.stdout.txt`) | imports complete module; no scorer invocation |
| `searchless_chess.src.engines.stockfish_engine` (`ordered-import.stdout.txt`) | imports complete module; no scorer invocation |

There are **19 import probes: 6 successful module imports, 13 failed imports**. These are probe counts, not an overall module-graph coverage fraction or scorer-equivalence evidence. `stockfish_engine` first fails with `AttributeError: module 'chess' has no attribute 'engine'` when imported alone: its annotations rely on the caller having imported `chess.engine`. A separate preserved `ordered-import` probe imports the real `chess.engine`, matching `puzzles.py:25`, then the complete Stockfish module imports successfully. No engine constructor or binary is called; the original failure remains preserved. No upstream byte or annotation is patched.

The primary failures are verbatim:

```text
ModuleNotFoundError: No module named 'tree_sitter'
ModuleNotFoundError: No module named 'absl'
```

BFCL traceback chain: `eval_runner.py:16` → `ast_checker.py:1` → `model_config.py:4` → `claude.py:10` → shared `model_handler/utils.py:13` → `parser/java_parser.py:1`. Chess fails immediately at `puzzles.py:22`. Additional independently probed branches fail on `jax`, `haiku` and `chex`; these are real exceptions, but unexecuted deeper ML dependencies are not claimed resolved.

`environment.stdout.txt` records distribution metadata, including absence of the three native Tree-sitter packages and `absl-py`; upstream BFCL declarations at `B/pyproject.toml:26`-`:28` require Tree-sitter 0.21.3, Java grammar 0.21.0 and JavaScript grammar 0.21.4. Chess requirements are `C/requirements.txt`, including the eager ML graph. `pip-cache-list.stdout.txt` preserves the local wheel cache inventory. The prior retained wheelhouse is inventoried verbatim by filename in the environment JSON. Two seccomp-confined pip resolution probes use `--no-index --no-cache-dir --no-deps --find-links=<retained-wheelhouse>` with fresh destination directories and do not install anything. Their exits are 1 and raw stderr retains:

```text
ERROR: Could not find a version that satisfies the requirement tree_sitter==0.21.3 (from versions: none)
ERROR: No matching distribution found for tree_sitter==0.21.3
ERROR: Could not find a version that satisfies the requirement absl-py (from versions: none)
ERROR: No matching distribution found for absl-py
```

This is unavailability in the current interpreter/cache/retained wheelhouse only, not a claim that no compatible artifact exists elsewhere. Offline scope forbids fetching dependencies here. No dependency shim, dummy model catalogue or selected-function fallback is used.

## Per-input official versus local outcomes

`inputs.json` predeclares all authored input bytes before execution. BFCL reuses the prior 23 authored Simple controls and adds five authored irrelevance controls. Chess reuses the prior 15 authored boundary controls. No prior scores are copied as current measurements. Each side receives identical prediction text; comparison joins IDs and verifies the common input SHA-256. BFCL local gold is the explicit function-name projection; Chess receives the same FEN/reference moves. Actual local `score` functions are imported and called unchanged; task-loading caches stay empty.

The planned BFCL invocation uses real `eval_runner.main` on a single authored JSONL input and a historical prompting handler key. Its complete-module import fails before any input file is materialized or handler is constructed; `main_entered=false` on every input. Both Chess callers fail before board/PGN construction or prediction-supplier invocation; `scorer_entered=false`. The passive call trace confirms no scoring/runner body entry. Every official `score` remains JSON `null`, never a synthetic zero.

**BFCL: S = `ModuleNotFoundError: No module named 'tree_sitter'`, unmeasured at full-runner import.**

| Authored input | Category | Official full route | Actual local reward | Numeric comparison |
| --- | --- | --- | ---: | --- |
| `valid_full_call` | simple | S | 0.0 | unavailable |
| `accepted_width_alternative` | simple | S | 0.0 | unavailable |
| `string_normalization` | simple | S | 0.0 | unavailable |
| `fenced_call` | simple | S | 0.0 | unavailable |
| `wrong_function` | simple | S | 0.0 | unavailable |
| `wrong_width` | simple | S | 0.0 | unavailable |
| `wrong_color` | simple | S | 0.0 | unavailable |
| `wrong_type` | simple | S | 0.0 | unavailable |
| `missing_required` | simple | S | 0.0 | unavailable |
| `unexpected_argument` | simple | S | 0.0 | unavailable |
| `duplicate_calls` | simple | S | 0.0 | unavailable |
| `empty_call_list` | simple | S | 0.0 | unavailable |
| `bare_local_contract` | simple | S | 1.0 | unavailable |
| `none_local_contract` | simple | S | 0.0 | unavailable |
| `malformed_syntax` | simple | S | 0.0 | unavailable |
| `literal_binop` | simple | S | 0.0 | unavailable |
| `variable_argument` | simple | S | 0.0 | unavailable |
| `negative_integer` | simple | S | 0.0 | unavailable |
| `unary_plus` | simple | S | 0.0 | unavailable |
| `positional_args` | simple | S | 0.0 | unavailable |
| `empty_response` | simple | S | 0.0 | unavailable |
| `invalid_schema_type` | simple | S | 0.0 | unavailable |
| `empty_reference` | simple | S | 0.0 | unavailable |
| `irrelevance-none` | irrelevance | S | 1.0 | unavailable |
| `irrelevance-empty-list` | irrelevance | S | 0.0 | unavailable |
| `irrelevance-full-call` | irrelevance | S | 0.0 | unavailable |
| `irrelevance-bare-name` | irrelevance | S | 0.0 | unavailable |
| `irrelevance-empty` | irrelevance | S | 1.0 | unavailable |

**ChessBench: A = `ModuleNotFoundError: No module named 'absl'`, unmeasured at full-puzzles import.** The board and row columns are separate attempted caller routes over the same 15 primary inputs; the row attempts are supplementary and do not add 15 distinct inputs to the denominator.

| Authored input | Official board route | Official PGN-row route | Actual local strict reward | Local unchecked diagnostic |
| --- | --- | --- | ---: | ---: |
| `reference-short` | A | A | 1.0 | 1.0 |
| `reference-long` | A | A | 1.0 | 1.0 |
| `trailing-ignored` | A | A | 1.0 | 1.0 |
| `wrong-legal` | A | A | 0.0 | 0.0 |
| `missing-solver` | A | A | 0.0 | 0.0 |
| `missing-later` | A | A | 0.0 | 0.0 |
| `malformed-solver` | A | A | 0.0 | 0.0 |
| `illegal-reference-setup` | A | A | 0.0 | 1.0 |
| `illegal-reference-solver` | A | A | 0.0 | 1.0 |
| `setup-only` | A | A | 0.0 | 1.0 |
| `empty-reference` | A | A | 0.0 | 0.0 |
| `invalid-fen` | A | A | 0.0 | 0.0 |
| `reference-mate` | A | A | 1.0 | 1.0 |
| `alternate-mate` | A | A | 1.0 | 1.0 |
| `immediate-mate-extra-reference` | A | A | 1.0 | 0.0 |

| Measured accounting | BFCL | ChessBench primary board route |
| --- | ---: | ---: |
| Primary authored inputs | 28 | 15 |
| Official numeric returns | 0 | 0 |
| Official unmeasured import failures | 28 | 15 |
| Local numeric returns | 28 | 15 |
| Local unmeasured | 0 | 0 |
| Numeric pairs | 0 | 0 |
| Numeric agreements | 0 | 0 |
| Numeric divergences | 0 | 0 |

BFCL local outcomes: 3 ones / 25 zeros. Chess strict local outcomes: 6 ones / 9 zeros. These local counts do not certify official accuracy. All 43 primary official outcomes are unmeasured provisioning failures; the 15 supplementary row attempts add 15 unmeasured route attempts. This is 58 failed per-input import attempts with two primary missing-module causes, not 58 distinct dependency discoveries or zero scores. No scorer-body invalid-candidate verdict is produced by the official side. Numeric agreement and divergence rates are **undefined (0/0)**; zero numeric disagreements does not establish equivalence. The prior selected-function comparisons keep their earlier scope and are not added to this packet's complete-route counts.

## Coverage fraction and remaining unreachable work

Coverage is exactly **0/2 requested complete dataset module routes demonstrated**, with **0/28 BFCL** and **0/15 ChessBench primary** official numeric-return coverage, or **0/43** combined primary controls. Supplementary Chess PGN-row coverage is **0/15**. These denominators describe this bounded authored packet only; they are not released task counts, overall S4 coverage or a census of all callable module entrypoints. Successful standalone imports of converters/engine utility modules do not improve those fractions.

Unreachable here: complete BFCL Simple and irrelevance dispatch/handler/parser/checker execution; native Java/JS parser initialization; catalogue's transitive provider imports and compatibility; selected trusted full-call schemas/answers, local-model response grammar, whole-category source privacy integration, positional joins, expression-eval containment and leaderboard aggregation. Unreachable Chess work includes both complete-module board and PGN-row evaluation, engine catalogue/ML dependency closure, native engine binary/checkpoint custody and CLI engine/CSV execution. Model/GPU execution is outside authorization. Released puzzle breadth, task comparability, full portable source/runtime/ABI closure, production resource/lifecycle guarantees and valid live controls remain unmet.

`reports/w-awp-released-predicates.md` already addresses AppWorld's separate 3/732 scope. This packet supplies no AppWorld or Terminal-Bench execution. **S1/S3/S4/S5/S6 remain PARTIAL; `scorer-offline-closure` and every dataset blocker stay open.** Only additive shared registry observation/evidence and the journal entry are changed. `runs/`, frozen receipts, dataset payloads, production code/gates and existing evidence are untouched.

Validation commands/output: `reports/w-bfclroute-validation.txt`. `validate.py` independently rehashes source/archive/local bytes, derives comparison counts, validates socket-denial receipts, verifies no scorer entry on failed routes and removed scratch roots, and compares the registry against baseline allowing only this additive shared observation/evidence. `SHA256SUMS` covers the packet, including scripts and raw streams; it excludes only itself. Verbatim upstream whitespace is retained and excluded explicitly from the owned-text whitespace check.
