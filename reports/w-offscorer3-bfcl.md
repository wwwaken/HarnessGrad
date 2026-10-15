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
