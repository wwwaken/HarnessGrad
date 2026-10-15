# Bounded official execution coverage extension - w-offscorer3

Official execution evidence is limited to the exact components, authored inputs and offline profiles documented here.

**`scorer-offline-closure` remains open. S1, S3, S4 and S6 remain PARTIAL. No dataset blocker closes, and no gate or production scorer changes.**

Baseline: `9f78bcd`, registered `/tmp/hg-offscorer3`, branch `wg-offscorer3`, review 2026-10-15. Read first: `AGENTS.md`, `reports/w-offscorer-equivalence.md`, `reports/w-offscorer2-coverage.md`; also reviewed BFCL's existing source packet, topology survey and Terminal-Bench's prior real execution report. The previous packets' method is followed: authentic unchanged official source execution separate from actual unchanged local scorers; common authored inputs; raw outputs and exceptions retained; per-input counts; recomputed identities and SHA-256 manifests. The candidate set was confirmed by inspecting actual routes and available source/runtime custody, including Tau-Bench and ALFWorld beyond the suggested first candidates.

## New measured scope

This packet adds some bounded official **component** execution for each of the seven previously wholly uncovered candidates. “Component” is essential: BFCL and ChessBench complete imports fail, and AppWorld uses its official generic evaluator with an explicitly authored task predicate. Terminal-Bench remains **partially covered** by its earlier real `bash /tests/test.sh` execution for `openssl-selfsigned-cert` in `reports/w-net-receipts.md`; no new Terminal-Bench execution is claimed. Its historical measurement/publication restrictions remain unchanged. No run receipt is opened or modified here.

| Dataset | Actual official execution | Same-input result and boundaries |
| --- | --- | --- |
| `gaia` | Full unchanged pinned `question_scorer` module | 20/20 numeric agree; 3 upstream-accepted gold sentinels refused locally; no call exceptions |
| `tau_bench` | Full unchanged Env module, actual terminal step and reward replay on authored retail state | 9/10 numeric agree; 1 output-replay divergence; 1 unfinished/classification boundary |
| `bfcl_v3` | Unchanged AST-selected Python prompting parser and undotted Simple checker | 11/16 numeric agree; 5 raw full-call/name-only contract divergences; 7 official parser/checker exceptions; complete imports fail `tree_sitter` |
| `livecodebench` | Full upstream evaluation module, real runner children and pass@1 aggregation | 10/10 numeric agree; 2 local-unmeasured malformed-test boundaries; 12 strict-profile IPC failures retained before isolated-network retry |
| `chessbench_puzzles` | Unchanged AST-selected `evaluate_puzzle_from_board` | 6/10 strict numeric agree; 4 divergences; 5 input/supplier exceptions; complete import fails `absl` |
| `alfworld` | Full installed `evaluate_dagger`, actual TextWorld/PDDL on an authored game | 5/5 numeric agree, including positive wins; empty-trace upstream reduction exception vs local zero |
| `appworld` | Installed generic evaluator and real runtime on an authored task/predicate | 6/6 numeric generic-workflow comparisons agree; released task-specific scorers remain unexecuted |

At that component-only scope, the derived inventory is 15 prior plus 7 newly exercised datasets, totaling 22; Terminal-Bench remains separately partial. The root `tests/fixtures/hg_woffscorer3/coverage-summary.json` derives coverage and counts from actual component comparison/raw files. Counts from different metrics, caller policies or failed profiles are not pooled into an agreement rate. The earlier nine QA components and six w-offscorer2 components keep their existing execution/provenance limitations; this packet does not upgrade them.

## Exact still-uncovered set and closure boundary

Within the named remaining set, no candidate is left wholly without **some** official component execution after this packet, except that Terminal-Bench receives no new execution and retains its prior single-task evidence. This does **not** mean complete official routes are covered. The explicit still-uncovered full-route set is **`appworld`, `bfcl_v3`, `chessbench_puzzles`, `terminal_bench`**: AppWorld's released task predicates, BFCL's full parser/checker/handler graph, ChessBench's complete engine/module graph and Terminal-Bench's remaining task scorers have not been executed here. AppWorld's authored predicate is never described as an official released task evaluator. If coverage requires an executed released task-specific predicate, AppWorld remains uncovered at that scope.

Other new coverage is narrow too: Tau-Bench covers authored retail state/tools only, ALFWorld an authored PDDL game only, GAIA normalization/caller controls only, and LiveCodeBench authored stdio/call tests only. All datasets retain broader task/family/input coverage gaps. Complete upstream imports are not substituted for source-function evidence or vice versa. Local Git objects, retained public acquisition receipts and installed distribution/image bytes identify the executed source at their respective scopes; no new remote source attestation or complete transitive image/ABI closure is inferred.

S4 is narrowed, not satisfied. S1 pinned execution-selected closures, S3 complete transitive dependencies, S4 official provenance/execution and S6 valid live controls remain PARTIAL. No production runtime admission, private selected-input/export equivalence, resource/lifecycle guarantee, pilot expansion, benchmark accuracy or production authorization follows. All dataset records, historical records, blocker statuses and next_actions remain unchanged; the sole registry change is additive shared `observed` detail and its verbatim evidence locator.

## Commands, integrity and review

Each reviewed component section below includes official identity/recomputed hashes, exact execution commands, every per-input result, divergence/exception and limits. Full scripts, controlled inputs, raw stdout/stderr, official/local results, preserved failed attempts and source copies are under `tests/fixtures/hg_woffscorer3/`. The root `SHA256SUMS` covers the complete packet including nested manifests; unchanged production source pins are in `local-source-pins.json`. The validation log `reports/w-offscorer3-validation.txt` records exact parent verification, focused registry tests, whitespace and checker commands/output. Source copies retain original bytes, including upstream whitespace.

Final parent validation: all 267 root manifest members and 91 unchanged production source pins pass, all component validators pass, the registry remains valid with production authorization false, and all 54 focused registry regressions pass. The complete whitespace output is retained reversibly as JSON-escaped text; only verbatim upstream source/inspection whitespace is excluded from the passing owned-change check.

All scoring is bounded and offline: kernel seccomp socket denial, an isolated network namespace for upstream LiveCodeBench's local IPC, or network-disabled AppWorld containers with released task data hidden. Each profile retains real probes/receipts and explicit custody limits. The component reports distinguish fixtures' corrected mistakes and runtime failures from numeric zero scores. No benchmark scoring run, model, GPU, endpoint, production H0, `runs/` mutation or frozen receipt mutation occurs. Parent reviewed each isolated child's diff and ran its focused packet validator before integration into this worktree; no agent commits to main.


<!-- Reviewed component: gaia-tau -->

# GAIA and Tau-Bench bounded official execution - w-offscorer3

Both complete upstream scoring modules import and execute under kernel-enforced socket denial. No shared or dataset blocker closes. These are authored scorer controls, not benchmark accuracy, production verifier admission or H0 runs.

All component-relative paths resolve under `tests/fixtures/hg_woffscorer3/gaia_tau/`.

## Source custody and exact commands

GAIA executes the complete unchanged `gaia-benchmark/leaderboard` `scorer.py`, adapter-pinned revision `9f133d71362ecb0a1c7ff6b4dcfc2a6b9f8ffd1e`, fresh SHA-256 `0d44c07f3046eec521697c22e3eaca8719cc81e422a8eaf32695c5f22bdac6e2`. Tau-Bench executes complete unchanged `tau_bench.envs.base.Env` at locally checked-out Git commit `59a200c6d575d595120f1cb70fea53cef0632f6b`, `base.py` fresh SHA-256 `1ad0402073f0ac9ca6b527efa0706e2aa8836dd2e5c1d453ed414ecb768c6d21`. Its complete `types.py`, `user.py`, `tool.py` and two actual upstream retail tools are retained, with every copied member checked against that commit's Git object. `identities.json` records all recomputed hashes and local verifier pins. Neither identity asserts a new remote provenance attestation; GAIA reuses the adapter pin and Tau-Bench authenticates local Git-object equality only.

Exact executed commands, repository-root cwd:

```sh
bash -x tests/fixtures/hg_woffscorer3/gaia_tau/commands.sh > tests/fixtures/hg_woffscorer3/gaia_tau/commands.stdout.txt 2> tests/fixtures/hg_woffscorer3/gaia_tau/commands.exact.txt
PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/hg_woffscorer3/gaia_tau/verify.py > tests/fixtures/hg_woffscorer3/gaia_tau/verification.json
```

The script records expanded commands in `commands.exact.txt`, including a separate full Tau-Bench import probe and each `timeout 150s python3 .../offline_exec.py .../run.py gaia|tau official|local` command. The unmodified prior guard denies socket syscalls and io_uring, closes inherited socket fds, actively tests IPv4/IPv6/UNIX EPERM and imposes CPU 120 s / FD 256 limits. `*.offline.txt` receipts include actual interpreter/libseccomp hashes and no external dataset-payload read attempts. Source staging occurs before the guard and copies only scoring code, never released task records. Native filesystem exclusion is not claimed by the Python audit hook. `production_runtime_observation` is false. No model, endpoint, GPU, task runner, benchmark run or frozen receipt is used.

`run.py` records actual loaded scorer/dependency paths and hashes, full raw returns, print/warning output, argv, evidence and errors in `gaia-official.json`, `gaia-local.json`, `tau-official.json`, `tau-local.json`. Both sides bind the same input-file digest. `comparison.json` is joined by input ID; `verify.py` independently recomputes it and checks cleanup, guard probes and source bytes. The first packet before adding the final Tau-Bench boundary control is preserved under `preserved-initial/`; it contains no failed scoring attempt. Normal case directories are temporary outside the repository and all were removed.

## GAIA comparison

Official calls `question_scorer(answer, gold)` directly. Local imports unchanged `data/datasets/gaia/verify/check.py` and calls its real `main()` with the same authored answer bytes written to a file and the same gold serialized in JSON. Local whitespace stripping and placeholder/missing-answer policy are part of the caller being compared. For the labelled missing-file control the common canonical prediction is empty string; only the local filesystem channel omits the file.

Measured GAIA: **23 inputs; 20 numeric comparisons; 20 agreements; 0 numeric divergences; 3 nonnumeric/classification boundaries**. No official or local Python call exception occurred.

| Authored input | Official return | Local reward | Comparison |
| --- | ---: | ---: | --- |
| `number-exact` | 1.0 | 1.0 | agree |
| `currency-comma` | 1.0 | 1.0 | agree |
| `percent-unscaled` | 1.0 | 1.0 | agree |
| `number-wrong` | 0.0 | 0.0 | agree |
| `number-invalid` | 0.0 | 0.0 | agree |
| `float-inf-invalid` | 1.0 | 1.0 | agree |
| `float-nan` | 0.0 | 0.0 | agree |
| `text-case-space` | 1.0 | 1.0 | agree |
| `text-wrong` | 0.0 | 0.0 | agree |
| `text-internal-newline` | 1.0 | 1.0 | agree |
| `list-separator` | 1.0 | 1.0 | agree |
| `list-order` | 0.0 | 0.0 | agree |
| `list-punctuation` | 0.0 | 0.0 | agree |
| `list-numeric` | 1.0 | 1.0 | agree |
| `list-length` | 0.0 | 0.0 | agree |
| `list-empty-item` | 1.0 | 1.0 | agree |
| `list-space` | 1.0 | 1.0 | agree |
| `blank-answer` | 0.0 | 0.0 | agree |
| `whitespace-answer` | 0.0 | 0.0 | agree |
| `empty-gold` | 1.0 | unmeasured | nonnumeric/classification |
| `placeholder-gold` | 1.0 | unmeasured | nonnumeric/classification |
| `punctuation-empty` | 1.0 | unmeasured | nonnumeric/classification |
| `missing-answer` | 0.0 | 0.0 | agree |

Findings: empty gold, placeholder `?` and punctuation-versus-empty-gold are accepted by upstream's string normalization; local exits 3 with `measured:false` and no reward. These are refusal boundaries, not numeric disagreements or filled-in zeros. On `float-inf-invalid`, upstream maps invalid numeric text to infinity and consequently accepts it against authored gold `inf`; local agrees. `nan` does not equal itself, percentages are stripped without rescaling, list order/punctuation are significant, and list-length mismatch emits the preserved upstream warning. This describes actual controlled returns, not eligibility of those gold values in GAIA.

## Tau-Bench comparison

Official imports the complete unchanged Env and constructs it on a wholly authored retail database/task using actual upstream `ModifyUserAddress` and `TransferToHumanAgents`. It uses upstream `HumanUserSimulationEnv`; fixture stdin supplies the literal `continue` only when the labelled ground-truth-respond boundary requests it. No user simulator, Env method, tool body or dependency is stubbed. Authored current database and utterance `Action`s represent the identical recorded local database/log. A real upstream `step(transfer_to_human_agents)` triggers `calculate_reward`; the unfinished control instead executes an unknown nonterminal action. Local invokes unchanged `data/datasets/tau_bench/verify/check.py:main(argv)` with the committed upstream tool/hash library and the same authored database, gold actions, utterances and done state. No released retail/airline task or committed missing clean database is needed for these synthetic controls. Airline and released task breadth remain uncovered.

Measured Tau-Bench: **11 inputs; 10 numeric comparisons; 9 agreements; 1 numeric divergences; 1 nonnumeric/classification boundaries**. No official or local Python call exception occurred.

| Authored input | Official return | Local reward | Comparison |
| --- | ---: | ---: | --- |
| `address-correct` | 1.0 | 1.0 | agree |
| `address-wrong` | 0.0 | 0.0 | agree |
| `output-present` | 1.0 | 1.0 | agree |
| `output-missing` | 0.0 | 0.0 | agree |
| `output-case` | 1.0 | 1.0 | agree |
| `output-comma-asymmetric` | 0.0 | 0.0 | agree |
| `unfinished` | 0.0 | 0.0 | nonnumeric/classification |
| `unknown-ground-truth-tool` | 1.0 | 1.0 | agree |
| `ground-truth-tool-error-noop` | 1.0 | 1.0 | agree |
| `terminate-skip` | 1.0 | 1.0 | agree |
| `ground-truth-respond-output` | 1.0 | 0.0 | diverge |

Findings: `ground-truth-respond-output` is a measured divergence, **official 1 / local 0**. During `calculate_reward`, upstream replays the authored ground-truth respond action and appends it to `self.actions`; its output scan therefore sees the replay's own `secret` although the original agent said nothing. The local verifier records unknown ground-truth tool `respond` in `replay_errors` and correctly finds no agent utterance. This is a deliberate invalid/atypical task-schema boundary, not a claim about released task prevalence. `unfinished` has upstream intermediate reward 0 with `done:false` and `reward_info:null`, versus local recorded measured zero: no upstream terminal reward was computed, so it is excluded from numeric scoring agreements. Unknown/refused ground-truth tools leave the authored database unchanged and both scorers accept the matching no-op state; upstream appended actions/final replayed database and local `unknown ground-truth tool` / `Error: user not found` diagnostics are retained. Output comma removal applies to agent content only in both paths. The skip-termination control executes the real upstream exclusion.

S4 gains bounded complete-module GAIA and Tau-Bench execution only. Complete remote provenance, transitive dependency/image/ABI custody, private selected-input/export equivalence, trusted production resource/lifecycle isolation and valid live controls remain outside this packet. S1, S3, S4 and S6 stay PARTIAL; no dataset blocker closes.

Dependency finalization finding: the full Tau-Bench import probe and official process each exit successfully but retain ignored `BaseEventLoop.__del__` tracebacks ending in `AttributeError: '_UnixSelectorEventLoop' object has no attribute '_ssock'`. These arise after importing the real litellm/asyncio graph under socket denial; no cause beyond that observed context is asserted. They are not scorer-call exceptions and do not replace the returned scores. `dependency-diagnostics.json` records counted occurrences and raw stderr hashes. The first read-only validator assumed the guard footer was the last stderr line and failed on these finalizer messages; its failure is preserved in `validator-first-failure.txt`, and the validator now locates the actual JSON footer without discarding the surrounding stderr.


<!-- Reviewed component: bfcl -->

# BFCL bounded official source-function execution - w-offscorer3

`bfcl_v3` now has bounded execution evidence for unchanged upstream Python
prompting parser and undotted Simple AST checker functions. The complete official
checker, parser module and OSS handler do **not** import in the installed runtime:
each measured import fails with `ModuleNotFoundError: No module named 'tree_sitter'`.
No BFCL or shared blocker closes; `scorer-offline-closure` S1, S3, S4 and S6 stay partial.

This component follows `reports/w-offscorer-equivalence.md` and
`reports/w-offscorer2-coverage.md`, after reading `reports/w-bfcl-review.md`.
Execution cwd: registered `/tmp/hg-offscorer3-bfcl`; baseline `9f78bcd`.
All fixture paths below are relative to `tests/fixtures/hg_woffscorer3/bfcl/`.
This packet executes wholly authored bounded inputs, with no released task/answer
row access, benchmark run, model, GPU, endpoint, provider request or container.
The existing production adapter and shared scorer files are unchanged.

## Official identity and source custody

Upstream `https://github.com/ShishirPatil/gorilla`, `refs/tags/v1.3`, commit
`ea13468e4423454d0c213704fb87cf7cb3990433`, root tree `b34aa53a73491f42dc69b8b18c92448d7c311f50`.
`run.py identity()` rehashes the existing raw `tests/fixtures/hg_bfcl/responses/archive.body`
as `57854157e82aed5723a1458d2a4ac426e3256959ded4a20ddc4d627c22edb7fe`, compares its PAX commit comment, and checks the retained tag and
commit response values. It reads only the existing custody inventory's exact
allowlisted code/license/spec members, checks all 83 members against actual
retained bytes and the archive, and recomputes their Git blobs and SHA-256 values.
Task/result/reference archive member bodies are never opened. The raw archive and
historical evidence remain unchanged. This repeats byte custody against preserved
public responses; no new remote provenance request occurs.

`official.json`, `local.json` and `import.json` contain the freshly recomputed
archive, inventory, raw metadata receipt and member identities. The executed source
copies are byte-identical to those retained upstream files:

| Exact source copy | Recomputed SHA-256 |
| --- | --- |
| `tests/fixtures/hg_woffscorer3/bfcl/official-source/ast_checker.py` | `58a8a1d8a42ec4f7e0f340a8bf11ab4035c54d38d933ae2621f22bbc7c8d1c9b` |
| `tests/fixtures/hg_woffscorer3/bfcl/official-source/utils.py` | `153bb33a9515ea2d6ee6a1387faaa464c7be4fe9c6a9f88cc17ad23a1cc306d2` |

Selected callable route:
`default_decode_ast_prompting(prediction, 'Python')` → `ast_parse` /
`resolve_ast_call` / `resolve_ast_by_type` →
`ast_checker(function, decoded, possible_answer, 'Python', 'simple', 'controlled-no-model')`.
The last argument is an unused label on these undotted controls, not a fabricated
catalogue entry. No `MODEL_CONFIG_MAPPING`, missing package or Java/JavaScript
converter is stubbed. `run.py` selects original function/constant AST nodes, then
compiles them with their original locations and unchanged bodies, with actual
stdlib `ast` and `re`. Selected names, source lines and source-segment digests are
in `official.json.selected_original_nodes`. The Python undotted Simple branches
use no omitted catalogue or converter globals. Dotted names, Java/JavaScript,
parallel/multiple categories, full handler construction, complete module imports,
provider SDK/native closure and local-model handler integration remain unexecuted.

## Exact commands and offline bounds

Executed from the repository root:

```sh
bash tests/fixtures/hg_woffscorer3/bfcl/commands.sh
```

The script issues this exact command for each `import`, `official`, `local`,
`compare` argument and corresponding output basenames:

```sh
timeout 150s env PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 tests/fixtures/hg_woffscorer3/bfcl/offline_exec.py tests/fixtures/hg_woffscorer3/bfcl/run.py official > tests/fixtures/hg_woffscorer3/bfcl/official.json 2> tests/fixtures/hg_woffscorer3/bfcl/official-offline.txt
```

The guard is byte-identical to the prior packet's strict `offline_exec.py`.
It closes inherited socket descriptors and denies socket APIs and io_uring_setup
with kernel seccomp EPERM before scorer imports. Every `*-offline.txt` records
actual denied IPv4, IPv6 and UNIX probes, interpreter/libseccomp digests, wall
command bounds, CPU 120 s and file-descriptor 256 limits. The supplemental Python
audit hook excludes external dataset payload opens; all four observed denied-open
lists are empty. The local import's `_RECORDS` cache is asserted empty before and
after calls; no row-loader substitution is needed. This guard is a controlled
fixture observation, not production filesystem/runtime admission.

`import.json` preserves all three actual full-import exceptions and full tracebacks.
A code-only import finder maps retained official package paths without modifying
source or substituting dependencies. Official import-time `result` and `score`
directories are redirected by `BFCL_PROJECT_ROOT` to a fresh temporary directory;
its actual contents and successful removal are recorded. No handler constructor
or generation method is invoked, and no network attempt is permitted.

## Identical raw inputs, measured results and limits

`inputs.json` contains 23 authored cases. Both independent scorers receive
**the exact same prediction strings** per input; the comparison checks byte-equal
strings and identifiers. The official schema and alternative-value references are
authored; the local `gold.functions` is their explicitly recorded name projection.
The final empty-reference case deliberately lacks a reference and is an API-boundary
probe. The local entry is unchanged `data.datasets.bfcl_v3.score(prediction, local_gold)`;
its freshly recomputed source digest in both outputs is `de8f7efb844c39fa79632d42171d537e488f055dae7b5e1bceb583368e3bce17`.

Raw full-call comparisons: **16 numeric, 11 agreements, 5 divergences;
7 official exceptions, 0 local exceptions; 7 nonnumeric inputs**.
No failed call is replaced by zero. These are distinct metric/response contracts:
upstream compares full calls including arguments, while the adapter deliberately
requires name-only lines. Therefore the counts measure these raw contract outcomes,
not metric equivalence or benchmark accuracy.

| Authored input | Official result or exception | Local reward | Numeric agreement |
| --- | ---: | ---: | --- |
| `valid_full_call` | 1.0 | 0.0 | no |
| `accepted_width_alternative` | 1.0 | 0.0 | no |
| `string_normalization` | 1.0 | 0.0 | no |
| `fenced_call` | 1.0 | 0.0 | no |
| `wrong_function` | 0.0 | 0.0 | yes |
| `wrong_width` | 0.0 | 0.0 | yes |
| `wrong_color` | 0.0 | 0.0 | yes |
| `wrong_type` | 0.0 | 0.0 | yes |
| `missing_required` | 0.0 | 0.0 | yes |
| `unexpected_argument` | 0.0 | 0.0 | yes |
| `duplicate_calls` | 0.0 | 0.0 | yes |
| `empty_call_list` | SyntaxError | 0.0 | nonnumeric |
| `bare_local_contract` | AttributeError | 1.0 | nonnumeric |
| `none_local_contract` | AttributeError | 0.0 | nonnumeric |
| `malformed_syntax` | SyntaxError | 0.0 | nonnumeric |
| `literal_binop` | 1.0 | 0.0 | no |
| `variable_argument` | 0.0 | 0.0 | yes |
| `negative_integer` | 0.0 | 0.0 | yes |
| `unary_plus` | 0.0 | 0.0 | yes |
| `positional_args` | 0.0 | 0.0 | yes |
| `empty_response` | SyntaxError | 0.0 | nonnumeric |
| `invalid_schema_type` | KeyError | 0.0 | nonnumeric |
| `empty_reference` | IndexError | 0.0 | nonnumeric |

The 5 divergences are `valid_full_call`, `accepted_width_alternative`,
`string_normalization`, `fenced_call`, `literal_binop`: official returns 1.0 while
local returns 0.0 on the same raw full call. Official accepted the optional argument
omission, alternative width, string punctuation normalization and authored `1+1`
expression; the name-only adapter treats that whole line as a different name.
`bare_local_contract` is the adapter's valid name-only answer (local 1.0), while
the official parser raises `AttributeError` on that same string. This is a separate
nonnumeric contract boundary, not an official score zero or numeric divergence.

Measured input exceptions: `SyntaxError` for `empty_call_list`, `malformed_syntax`
and `empty_response`; `AttributeError` for `bare_local_contract` and
`none_local_contract`; `KeyError` for `invalid_schema_type`; `IndexError` for
`empty_reference`. The strict caller's full error-to-score behavior is not inferred
from these direct function exceptions. Raw traces remain in `official.json`.

Additional observed parser behaviors are retained in the raw decoded outputs:
`unary_plus` resolves authored `+2` to `-2` and returns official 0.0; its
`resolve_ast_by_type` unary branch negates the operand without distinguishing the
operator. `positional_args` decodes the function with an empty argument dictionary,
then fails required arguments (official 0.0). These measured behaviors remain
findings; neither parser is patched.

## Integrity, validation and coverage boundary

`SHA256SUMS` covers every component fixture file except itself. `verify.py` verifies
those bytes, reruns custody/member hashes and comparison derivation, checks unchanged
adapter bytes, requires the actual socket-denial receipts and retains exception
classification. The component command/checker output is
`reports/w-offscorer3-bfcl-validation.txt`. Exact validation commands:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/hg_woffscorer3/bfcl/verify.py
python3 tools/check_dataset_blockers.py
```

The full staged whitespace check flags only verbatim upstream trailing whitespace
in the two source copies. The check excluding `official-source/` passes; upstream
source bytes remain unchanged.

This extends only BFCL's bounded official **source-function** execution scope.
The full module/native/catalogue/handler route remains missing, and no production
H0, selected-only verifier or benchmark-comparability claim follows. This component
adds no execution for the other remaining datasets; the parent coverage report
records their reviewed outcomes and Terminal-Bench's existing partial real-task
execution separately.


<!-- Reviewed component: code-chess -->

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


<!-- Reviewed component: worlds -->

# ALFWorld and AppWorld official generic execution - w-offscorer3-worlds

S4 gains bounded offline execution of complete installed upstream ALFWorld evaluation and AppWorld generic evaluation/replay components. **S1, S3, S4 and S6 remain partial; no blocker is closed.** AppWorld's task-specific predicate in this packet is authored fixture code, **not a released official task evaluator**. This distinction limits its new evidence to authentic generic scoring machinery, rather than released task-scoring equivalence.

Packet root: `tests/fixtures/hg_woffscorer3/worlds/`. Baseline: `9f78bcd`; isolated registered worktree `/tmp/hg-offscorer3-worlds`. Previous method packets `reports/w-offscorer-equivalence.md` and `reports/w-offscorer2-coverage.md` were read first. Inputs are wholly authored; no released benchmark task, heldout input, oracle walkthrough, model, GPU, endpoint or production runner executes. Production adapters and scorers remain unchanged. These are scorer controls, not measured benchmark scores or H0 authorization.

## Commands, raw custody and boundaries

Exact final replay, executed at repository root:

```bash
bash -x tests/fixtures/hg_woffscorer3/worlds/commands.sh > tests/fixtures/hg_woffscorer3/worlds/commands-output.txt 2> tests/fixtures/hg_woffscorer3/worlds/commands-exact.txt
PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/hg_woffscorer3/worlds/verify.py
python3 tools/check_dataset_blockers.py
```

`commands.sh` and expanded `commands-exact.txt` retain every argument, bound, image identity and path. `alfworld-official.json` / `alfworld-local.json` preserve raw results, actual native observations, per-case stdout/stderr and exceptions. AppWorld official/local JSON retain child argv, exit codes, exact stdout/stderr, network receipts, native API responses and complete tracker/evidence values. `comparison.json` derives per-input joined outcomes and counts. `SHA256SUMS` is freshly computed across retained packet bytes; `verify.py` recomputes every listed hash and source/controlled-archive equality. Exact validation/checker output is `reports/w-offscorer3-worlds-validation.txt`.

ALFWorld uses an unchanged copy of the earlier kernel seccomp `offline_exec.py`, which closes inherited socket descriptors and actively tests AF_INET, AF_INET6 and AF_UNIX denial. Native Fast Downward inherits syscall denial. Guard receipts record interpreter/libseccomp hashes, 120 CPU seconds, 256 FDs and no attempted external dataset payload reads. Each side has a 150-second wall bound.

AppWorld runs in the already-local pinned verifier image with `--network none`, read-only root, bounded private `/tmp`, one CPU, 1 GiB memory, 128 pids, 120 CPU seconds, 256 FDs and a 150-second wall bound per side. All released `/appworld` data is hidden by a read-only empty tmpfs during scoring; only the fixture archive's authored task is loaded. The network receipt checks `lo` as the sole interface, no IPv4 routes, and a failed external IP connection. Local IPC is allowed for actual FastAPI/Starlette test-client activity; this is offline, not socketless. Every case uses a fresh child interpreter and fresh external `/tmp/hg-woffscorer3-appworld-*` root. Child exits are awaited, scratch deletion is recorded, and post-execution named-container inspection fails with `no such object` in each `appworld-*-cleanup.txt`, confirming automatic removal. These fixture receipts do not establish production trusted custody, quota, snapshot lifecycle or transitive image closure.

The preparation script builds SQLite schemas through actual `ModelCollection.load(..., create_db=True)` and adds only a synthetic user, supervisor and task. It copies public API docs, no task directory. Exact acquisition/preparation command (executed before final scoring):

```bash
docker run --rm --network none --read-only --tmpfs /tmp:rw,nosuid,size=256m --cpus 1 --memory 1g --pids-limit 128 --ulimit cpu=120:120 --ulimit nofile=256:256 -e PYTHONDONTWRITEBYTECODE=1 -e CUDA_VISIBLE_DEVICES= -e HG_IMAGE=sha256:f3cb916b9bdc297d4c73dd9646e9550befb7c6e23827d937b90a0640373e97ca --mount type=bind,src=/tmp/hg-offscorer3-worlds/tests/fixtures/hg_woffscorer3/worlds,dst=/output --entrypoint python sha256:f3cb916b9bdc297d4c73dd9646e9550befb7c6e23827d937b90a0640373e97ca /output/prepare_appworld.py > tests/fixtures/hg_woffscorer3/worlds/appworld-prepare.json 2> tests/fixtures/hg_woffscorer3/worlds/appworld-prepare.stderr.txt
```

## Installed official identities

Version+byte custody does not authenticate a published Git commit or wheel acquisition. `upstream_git_revision` is null. Complete installed modules genuinely import and execute; there is no AST-selected scorer or reimplemented official reduction here. Metadata/WHEEL/RECORD identities and selected exact source copies are retained in `*-identities.json` / `source/`. The AppWorld source-inspection text files preserve additional full original source reads; they are not used as replacement modules.

| Component | Actual installed identity | Recomputed source SHA-256 |
| --- | --- | --- |
| ALFWorld evaluator | `alfworld==0.4.2`, `agents/eval/evaluate_dagger.py` | `d85f9da274eaea9bb2129d55d630f2a3477a4572cdc368c04993ccf152745fcb` |
| ALFWorld domain | installed `data/alfred.pddl` | `f1473041ed01da514de1f87adfd7ef0804862361f83ccf63c75e43633b0eb280` |
| ALFWorld grammar | installed `data/alfred.twl2` | `c5b22f0f73309a7fd7c8e5b71de42ad4803b60766ab4a51cc2feb34162be036b` |
| Native PDDL runtime | installed `fast_downward/libdownward.so` | `eab180829afd721c7a0637d000348694acb75b322f56049b95a9495c8d9ca81b` |
| AppWorld generic evaluator | `appworld==0.1.3.post1`, image installed `evaluator.py` | `4e773fb91cdad3ad10deeacde2d0b1f717454be599e6758419e8e1bb88b75cba` |
| AppWorld runtime | image installed `environment.py` | `ad650588158727c4ebe72a080638ec0174c33af8a8b9e9b81f3d9bfda55d3fd9` |
| AppWorld task loader | image installed `task.py` | `6b74420e30579e27c36cf2ace41f743d3d5f0640af4d15cae13df0419b42d5ea` |

AppWorld image ID is `sha256:f3cb916b9bdc297d4c73dd9646e9550befb7c6e23827d937b90a0640373e97ca`; actual `docker image inspect` is retained. Current common authored AppWorld archive SHA-256 is `0ec0c7e565474d437edbd40050a9e0dbb0602629800e49f38e9c2f1e0057db43`. The archive contains only `hgcontrol_1` under `data/tasks/`; validator checks all member digests.

## ALFWorld measured comparisons

Official side invokes unchanged full `evaluate_dagger(env, ScriptedInput(...), num_games=1)`. The supplied agent is a deterministic action-list feeder with no neural model or inference; its observation/preprocessing methods pass strings through. The environment is actual installed TextWorld/PDDL with authentic `AlfredDemangler` and `AlfredInfos`. Authored PDDL problem asks the agent to hold one apple; installed domain/grammar are unchanged. Native reset, action responses, `won` and `done` flags are retained. Local side calls unchanged `data/datasets/alfworld/verify/check.py:main(argv)` with unchanged `gym_env.py`, rebuilding a fresh native world from the same game and actions.

Both sides share the maximum environment budget of four and exact action bytes. The upstream scripted-agent loop horizon is `min(len(actions), budget)`, because an exhausted input supplies no further action; local `main` receives budget four and replays only available actions. These caller configurations are not identical for short/empty traces. In particular, empty horizon zero is an explicit API boundary control, not an ordinary official episode or numeric divergence.

| Input | Official result | Local reward | Outcome |
| --- | --- | --- | --- |
| `take-win` | 1.0 | 1.0 | agree |
| `look-no-win` | 0.0 | 0.0 | agree |
| `invalid-no-win` | 0.0 | 0.0 | agree |
| `win-then-invalid` | 1.0 | 1.0 | agree |
| `budget-truncation` | 0.0 | 0.0 | agree |
| `empty` | `ValueError` | 0.0 | nonnumeric caller boundary |

**Six controlled inputs, five numeric comparisons, five numeric agreements, zero numeric divergences, one official exception, zero local unmeasured.** The exception is `zero-size array to reduction operation maximum which has no identity` at official `np.max(sequence_game_points)` with zero upstream loop steps. No score is filled in. `win-then-invalid` also exposes a legitimate execution-policy difference: upstream executes an additional step after `done` before its prior-done mask stops the loop; local stops at first done. Final binary outcomes agree on this input. Positive controls are actual native goal satisfaction, not fixture-supplied `won` flags. This covers authored single-goal replay and full evaluator reduction, not released ALFWorld tasks, six task-family breadth or general equivalence.

## AppWorld measured comparisons

Official side imports complete authentic AppWorld and directly invokes the authentic requester methods on a fresh `AppWorld`, then calls unchanged `appworld.evaluator.evaluate_task`. Local side executes a byte-identical copy of unchanged production `verify/check.py:main`, which replays the same URL/method/data calls through `world.execute` and obtains `world.evaluate`. The byte copy is verified against current production source. No fake world, requester, model collection or tracker stands in for upstream.

The input task has a **wholly authored `ground_truth/evaluation.py`**, calling actual official `test.answer` to compare its supervisor-task stored answer against authored target `42`. This executes generic official `evaluate_task`, ground-truth loader, `TestTracker`, answer normalization, API replay and TGC success plumbing. It **does not execute any released task's evaluation predicate**, prove original task-score correctness, authenticate released-task provenance, or close AppWorld S4.

| Input | Official generic TGC | Local replay TGC | Outcome |
| --- | --- | --- | --- |
| `correct-answer` | 1.0 | 1.0 | agree |
| `wrong-answer` | 0.0 | 0.0 | agree |
| `no-calls` | 0.0 | 0.0 | agree |
| `numeric-answer` | 1.0 | 1.0 | agree |
| `wrong-then-correct` | 1.0 | 1.0 | agree |
| `invalid-api` | 0.0 | 0.0 | agree |

**6 controlled inputs; 6 numeric comparisons; 6 agreements, 0 numeric divergences; 0 final official exceptions; 0 final local unmeasured.** Counts are common-input generic-workflow outcomes, not released-task scorer equivalence.

## Preserved fixture/import/execution failures

No failed receipt is substituted with zero or overwritten without a preserved copy.

- Host Python package discovery found no installed `appworld`; complete upstream import instead succeeds in the already-local pinned verifier image. This is an image-installed execution profile, not a new host dependency closure.
- `appworld-preserved-first-attempt/` retains six actual `TypeError: object of type 'NoneType' has no len()` failures in `GroundTruth.__init__` because authored minimal metadata omitted required count metadata. The fixture metadata was completed; no upstream code changed.
- `appworld-preserved-second-attempt/` retains the first successful correct-answer followed by five missing-DB-root failures: official cached home-path helpers retained the previous deleted scratch root in a shared process. Fresh child interpreters per case remove that fixture cross-case state; this is not a production cache-lifecycle diagnosis.
- `appworld-preserved-third-attempt/` retains six local unmeasured missing-task failures when unchanged local check detected installed `/appworld/data` and rebound away from the controlled root. Final scoring hides bundled `/appworld` entirely so the unchanged check respects its authored `APPWORLD_ROOT`; no original dataset is exposed.
- `appworld-preserved-fifth-attempt/` retains five local `io.UnsupportedOperation: fileno` failures at authentic `safety_guard.disable()` followed by an `AttributeError` when its still-patched `SystemExit` alias caught that exception. Fixture `StringIO` capture lacks the real file descriptor required by `faulthandler.enable`; final capture uses real `tempfile.TemporaryFile` descriptors. This fixes the capture harness and allows authentic upstream safety restoration; no safety function is disabled or replaced. The failed per-case scratch deletions remain explicit; automatic container removal removes their private tmpfs.
- `appworld-preserved-fourth-attempt/` retains five local child serialization failures (`TypeError: object supporting the buffer API required`) after genuine `world.execute` left safety patches affecting the fixture's late `Path.read_bytes` call. No-calls child completed normally. The fixture now computes digest bytes before upstream execute; this permits unchanged scoring and captures raw evidence without changing or disabling upstream safety behavior. The failed command log and child stderr are retained.

This packet adds no execution for BFCL, ChessBench, GAIA, LiveCodeBench or Tau-Bench; parent integration may include their independent packets. Terminal-Bench retains its **partial** existing one-task official `bash /tests/test.sh` evidence from `reports/w-net-receipts.md`, not broadened by these controls. AppWorld released task-specific evaluator execution remains outside this packet even if its generic workflow runs successfully. S1, S3, S4 and S6 remain partial.
