# w-bfclguard: scoped decoder reachability and an unwired preflight

**FOUND:** the current platform BFCL name scorer and shared verifier completed
four fabricated scoring controls without importing the retained decoder or
entering any function with its source filename. **ABSENT over the enumerated AST
scope:** a named import/call/loading/process-invocation reference to the retained
decoder. **UNKNOWN:** general runtime unreachability through computed loaders,
generated code, process argv, dependencies or code outside that scope. This is
not a claim that every possible platform execution cannot reach the decoder
(`tests/fixtures/hg_bfclguard/dynamic-observation.json:1`,
`tests/fixtures/hg_bfclguard/summary.json:1`,
`tests/fixtures/hg_bfclguard/reachability.py:92`).

The existing unsafe finding remains FOUND, not closed: the earlier in-memory
probe entered and returned 7 at the retained BinOp eval. That observation is the
handoff used here, not a newly invented execution receipt
(`registry/w-bfclcontain.md:3`,
`tests/fixtures/hg_bfclcontain/observations.jsonl:28`). The source observed in this
work hashes to
`153bb33a9515ea2d6ee6a1387faaa464c7be4fe9c6a9f88cc17ad23a1cc306d2`;
the new test pins that exact file and confirms its two resolver eval branches
are BinOp and Lambda (`tests/quality/test_bfclguard_reachability.py:30`).

## 1. Enumerated AST graph and its limits

The exact scope is `driver.py`, every `.py` recursively below `eval/`, `data/`,
`tools/`, `harnessgrad/`, `ckpt/`, `methods/`, and extensionless files in those
directories whose first line is a Python shebang. `__pycache__` is excluded.
The observed inventory contains 317 files: 308 `.py` files and nine such scripts.
Each file's path, module identity, observed bytes and SHA-256 are recorded,
one file per line, with zero-based ID equal to line number minus one
(`tests/fixtures/hg_bfclguard/reachability.py:23`,
`tests/fixtures/hg_bfclguard/sources.jsonl:1`,
`tests/fixtures/hg_bfclguard/summary.json:1`; the count command and output are in
`registry/w-bfclguard-validation.txt:1`). No scoped file was omitted after a parse
error: an error propagates from `ast.parse`
(`tests/fixtures/hg_bfclguard/reachability.py:111`).

Every source is conservatively treated as an entry point, rather than guessing
which CLI or imported function an operator might select. `closures.jsonl`
enumerates **every** such entry and its transitive reachable source IDs;
`sources.jsonl` maps those IDs back to modules and paths. For example, entry 25
is the BFCL module, entry 140 is the shared check, and entry 147 is the driver
(`tests/fixtures/hg_bfclguard/sources.jsonl:26`,
`tests/fixtures/hg_bfclguard/sources.jsonl:141`,
`tests/fixtures/hg_bfclguard/sources.jsonl:148`,
`tests/fixtures/hg_bfclguard/closures.jsonl:26`,
`tests/fixtures/hg_bfclguard/closures.jsonl:141`,
`tests/fixtures/hg_bfclguard/closures.jsonl:148`).

The graph walks all AST nodes, including function-local and conditional imports,
resolves relative imports and known `from package import child` candidates,
includes parent-package initialization for imports and for module entries, and
adds literal absolute dynamic-import/run-module edges. It conservatively adds
script-local and `methods/` candidates for unqualified names. There are 2,115
graph records, including synthetic initializer records; this count is not a count
of executed imports (`tests/fixtures/hg_bfclguard/reachability.py:127`,
`tests/fixtures/hg_bfclguard/reachability.py:149`,
`tests/fixtures/hg_bfclguard/reachability.py:160`,
`tests/fixtures/hg_bfclguard/edges.jsonl:1`,
`tests/fixtures/hg_bfclguard/summary.json:1`).

The separate mechanism inventory records exact file, line, expression, alias-
resolved callee and resolution state for 134 recognized loader/execution/process
call nodes. Seven have literal module arguments; 127 remain UNKNOWN to this
analyzer. These are syntactic call candidates, including subprocess helper calls,
not 134 observed process launches. Alias recognition covers imports and simple
assignments, not arbitrary reflection. Source IDs in all artifacts share the
same inventory (`tests/fixtures/hg_bfclguard/reachability.py:57`,
`tests/fixtures/hg_bfclguard/reachability.py:92`,
`tests/fixtures/hg_bfclguard/reachability.py:175`,
`tests/fixtures/hg_bfclguard/mechanisms.jsonl:1`,
`tests/fixtures/hg_bfclguard/summary.json:1`).

**ABSENT over that complete syntactic enumeration:** an Import/ImportFrom
target naming `bfcl_eval`, `model_handler` or the three named decoder functions;
a recognized importlib/exec/compile/eval/runpy/process call expression mentioning
those targets; or a Name/Attribute node referring to those targets. The only two
target-bearing AST references are data strings at `data/datasets/bfcl_v3.py:103`
and `data/datasets/bfcl_v3.py:539`. The earlier grep's one hit was therefore
incomplete even as a text inventory (`tests/fixtures/hg_bfclguard/references.jsonl:1`,
`tests/fixtures/hg_bfclguard/references.jsonl:2`,
`tests/fixtures/hg_bfclguard/summary.json:1`,
`tests/quality/test_bfclguard_reachability.py:51`).

The exact missing witness for a **named** path would be an AST import edge such
as `from bfcl_eval.model_handler.utils import default_decode_ast_prompting`,
a call to a decoder identifier, or a loading/execution/process Call whose
expression identifies that module/source. Tests inject each form, including
aliased importlib and file loading, exec, runpy and subprocess argv, and assert
detection. A multi-hop fabricated graph also verifies relative imports,
initializers, literal dynamic loading and transitive entry closure
(`tests/quality/test_bfclguard_reachability.py:66`,
`tests/quality/test_bfclguard_reachability.py:89`,
`tests/quality/test_bfclguard_reachability.py:106`).

**UNKNOWN, not ABSENT:** computed import names/file paths, indirect callable
aliases, arbitrary `sys.path`/meta-path/module substitution, star re-export
semantics, generated strings later executed as code, runtime subprocess argv or
their child imports, native/third-party code, and non-Python scripts. The graph
does not perform dataflow or execute any of these. A concrete example is the
shared check's `__import__(module_name, fromlist=["score"])`, recorded UNKNOWN
instead of silently dropped; registry imports, computed run_path and the native
runtime's process plan are also explicitly inventoried
(`tests/fixtures/hg_bfclguard/mechanisms.jsonl:54`,
`tests/fixtures/hg_bfclguard/mechanisms.jsonl:55`,
`tests/fixtures/hg_bfclguard/mechanisms.jsonl:76`,
`tests/fixtures/hg_bfclguard/mechanisms.jsonl:79`,
`tests/fixtures/hg_bfclguard/reachability.py:175`).

Everything under `tests/` is outside graph traversal. One explicit scoped import
leaves the scope: `tools/check_triviaqa_provenance.py:9` imports a test helper.
It is reported as an outbound edge and is not followed. Thus even static
whole-repository transitive closure is UNKNOWN here; the result is deliberately
limited to the named platform scope and recognized resolution rules
(`tools/check_triviaqa_provenance.py:9`,
`tests/fixtures/hg_bfclguard/summary.json:1`,
`tests/fixtures/hg_bfclguard/reachability.py:193`).

Reproduce the AST inventory/graph with
`python3 -I -S -B tests/fixtures/hg_bfclguard/reachability.py`; its exact stdout
is in `registry/w-bfclguard-validation.txt:1`. The quality test recomputes and
compares all artifacts and the summary, so a stale report fails
(`tests/quality/test_bfclguard_reachability.py:51`).

## 2. Actual BFCL scoring route and dynamic negative control

The shared verifier reads answer data, validates the dataset selector, builds
`data.datasets.<name>`, imports it and retrieves `score`; its call uses the
structured answer when present or unwrapped plain text otherwise. For the
fabricated BFCL controls it calls the adapter's real score function; it does not
call a retained BFCL handler (`data/scaffolds/qa/verify/check.py:189`,
`data/scaffolds/qa/verify/check.py:222`,
`data/scaffolds/qa/verify/check.py:235`,
`data/scaffolds/qa/verify/check.py:251`,
`tests/fixtures/hg_bfclguard/dynamic-observation.json:1`).

The observation at line 495 is correct but describes **record construction**:
gold function names are normalized there. The actual comparison is
`sorted(got) == sorted(want)` at line 225, with both lists passed through
`bare_name`. This is list equality after sorting, so duplicate multiplicity is
retained, despite the metric's existing "set equality" label. `bare_name` only
splits a string on the final dot; prediction parsing only splits/strips lines
and applies a no-tool regex. On these string/dict inputs no call expression is
parsed, compiled or evaluated: argument text remains characters in a compared
string (`data/datasets/bfcl_v3.py:491`, `data/datasets/bfcl_v3.py:173`,
`data/datasets/bfcl_v3.py:199`, `data/datasets/bfcl_v3.py:217`). This does not
assert full-call correctness or official BFCL metric equivalence
(`data/datasets/bfcl_v3.py:230`).

The fresh `python3 -I -S -B` dynamic control imports the real platform modules,
calls `bfcl_v3.score` and `check.main` for each of four fabricated inputs, and
asserts the full observed outputs. A bare dotted name passes; BinOp-shaped,
nested-call and quoted-code full-call strings fail this name metric. The check
uses fabricated gold bytes bound to a fabricated task ID and their observed
digest. These are direct function controls, not dataset trials or official
scores (`tests/fixtures/hg_bfclguard/controls.py:149`,
`tests/fixtures/hg_bfclguard/controls.py:153`,
`tests/fixtures/hg_bfclguard/controls.py:168`,
`tests/fixtures/hg_bfclguard/dynamic-observation.json:1`).

Before import and after each case, the control asserts no retained package name
or source-file alias in `sys.modules`. An import finder, audit hook and profile
hook separately detect retained imports, code execution using its filename and
entry into any function under `/bfcl_eval/model_handler/` (which precedes its
eval sink). All three tripwires have positive synthetic controls; swallowed
exceptions still leave a failing event list. The scoring observations contain
`retained_sys_modules: []` and `sink_events: []`; source-row loading state stays
empty. The hooks also refuse network/process/GPU/dataset-path operations during
these calls. They are test instrumentation, not production isolation
(`tests/fixtures/hg_bfclguard/controls.py:69`,
`tests/fixtures/hg_bfclguard/controls.py:109`,
`tests/fixtures/hg_bfclguard/controls.py:115`,
`tests/fixtures/hg_bfclguard/controls.py:186`,
`tests/fixtures/hg_bfclguard/dynamic-observation.json:1`).

**Correction to the requested premise:** `test_import_direction.py` does not
forbid platform imports from `tests`. Its rule selector has no such case, and a
new control verifies that both a static tests import and a direct decoder import
produce no policy error; its extractor also ignores a dynamic import of the
exact retained path. Its source scope excludes `ckpt/`, `methods/` and
extensionless scripts. It would not have caught this decoder import as a
tests-boundary violation. No change/proposal to that guard is made
(`tests/quality/test_import_direction.py:17`,
`tests/quality/test_import_direction.py:135`,
`tests/quality/test_bfclguard_reachability.py:115`).

## 3. Test-only, unwired preflight gate

The gate lives solely in `tests/fixtures/hg_bfclguard/gate.py`. No current
platform-side full-call decoder call site was identified by the scoped analysis
or exercised BFCL route, so inserting this gate in the name scorer/shared check
would not contain an upstream official decode. It remains **UNWIRED**; no
production insertion or registry status change is proposed
(`tests/fixtures/hg_bfclguard/gate.py:1`,
`tests/fixtures/hg_bfclguard/summary.json:1`,
`tests/fixtures/hg_bfclguard/dynamic-observation.json:1`).

The seam validates the same immutable text before invoking its supplied decoder.
It mirrors the retained Python prompting normalization, permits dotted top-level
call names and keyword literal arguments, and refuses unsupported language,
syntax, positional/unpacked arguments and nonliteral value nodes. Limits are
65,536 characters, 4,096 AST nodes and depth 64; parsing happens before the
node/depth check, so these are not an OS CPU/memory sandbox
(`tests/fixtures/hg_bfclguard/gate.py:12`,
`tests/fixtures/hg_bfclguard/gate.py:21`,
`tests/fixtures/hg_bfclguard/gate.py:82`,
`tests/fixtures/bfcl_ast_source/candidate-codex195/files/berkeley-function-call-leaderboard/bfcl_eval/model_handler/utils.py:242`,
`tests/fixtures/bfcl_ast_source/candidate-codex195/files/berkeley-function-call-leaderboard/bfcl_eval/model_handler/utils.py:695`).

`bfclguard_binop_contains_call` names the existing finding's shape;
`bfclguard_call_in_argument` refuses any argument-descendant Call, including
inside container keys/values. All remaining BinOp nodes are also refused with
`bfclguard_binop_eval`, since even literal arithmetic selects upstream eval.
The literal allowlist excludes Lambda, the resolver's other eval branch. A
refusal is `{status: "unmeasured", measured: false, reason: <named reason>,
production_authorized: false}`, without a reward. An admission is never a score
or execution authorization (`tests/fixtures/hg_bfclguard/gate.py:17`,
`tests/fixtures/hg_bfclguard/gate.py:56`,
`tests/fixtures/hg_bfclguard/gate.py:67`,
`tests/quality/test_bfclguard_reachability.py:30`).

The controls use an inert spy, not the unsafe decoder. Each also runs the same
spy without the gate, positively observing one decoder entry; every refusal
observes zero guarded entries. This tests ordering before decoding and does not
repeat the original exploit investigation
(`tests/fixtures/hg_bfclguard/controls.py:40`,
`tests/fixtures/hg_bfclguard/gate-observations.jsonl:1`).

| Fabricated control | With gate | Without gate: observed spy / retained-source implication |
| --- | --- | --- |
| `fabricated_echo(value=__probe__())` | unmeasured, `bfclguard_call_in_argument`; no decoder entry | Spy entered once. The retained zero-keyword Call branch returns text; this shape alone is not the original execution finding (`tests/fixtures/hg_bfclguard/gate-observations.jsonl:1`; `tests/fixtures/bfcl_ast_source/candidate-codex195/files/berkeley-function-call-leaderboard/bfcl_eval/model_handler/utils.py:305`). |
| Ordinary literal dict/list, negative number, boolean and inert code string | passes, spy entered once | Spy entered once; argument nodes select literal/container branches, not either eval branch (`tests/fixtures/hg_bfclguard/gate-observations.jsonl:2`; `tests/fixtures/bfcl_ast_source/candidate-codex195/files/berkeley-function-call-leaderboard/bfcl_eval/model_handler/utils.py:280`; `tests/quality/test_bfclguard_reachability.py:30`). |
| `fabricated_echo(value=__bfclcontain_probe__()+0)` | unmeasured, `bfclguard_binop_contains_call`; no decoder entry | Spy entered once. The **prior** retained-decoder observation entered its in-memory probe and returned 7 (`tests/fixtures/hg_bfclguard/gate-observations.jsonl:3`, `tests/fixtures/hg_bfclcontain/observations.jsonl:28`). |
| Reversed BinOp, nested Call in a container, literal BinOp, Lambda, multiple ordinary calls, positional/unpacked arguments, subscript, malformed syntax | named refusals except ordinary multiple calls, which pass | Every bypass spy entered once; no upstream behavior for these additional cases is claimed dynamically verified (`tests/fixtures/hg_bfclguard/gate-observations.jsonl:4`, `tests/fixtures/hg_bfclguard/controls.py:24`). |

Additional language/character/node/depth-bound assertions run with the controls
(`tests/fixtures/hg_bfclguard/controls.py:63`). A future authorized integration
must validate the exact bytes immediately before its actual prompting decoder,
preserve refusals as unmeasured and retain all separate source/runtime/handler
and official-scorer gates; this fixture supplies no such integration
(`tests/fixtures/hg_bfclguard/gate.py:26`,
`tests/fixtures/hg_bfclguard/gate.py:82`, `registry/w-bfclcontain.md:204`,
`registry/w-bfclcontain.md:224`).

## Validation and remaining review target

FOUND: 14 new quality tests passed; the focused existing source-contract,
containment-differential and import-direction regression passed 75 tests, with
one publication-enumeration test deselected to avoid importing all adapters.
The unchanged differential regression intentionally still records the old
unsafe result. Exact commands/output, warnings, final byte sizes, cleanup and
explicit non-verification list are in `registry/w-bfclguard-validation.txt:1`.
The blocker checker returned
`{"valid": true, "datasets": 28, "shared_blockers": 0, "historical_records": 11, "production_authorized": false}`
(`registry/w-bfclguard-validation.txt:1`).

The most important uncertainty to attack is a **computed loader/generated
process route outside the static graph and four concrete scoring calls**. Neither
the static absence result nor the unwired gate closes that uncertainty or
authorizes official scoring (`tests/fixtures/hg_bfclguard/mechanisms.jsonl:54`,
`tests/fixtures/hg_bfclguard/mechanisms.jsonl:79`,
`tests/fixtures/hg_bfclguard/gate.py:1`).
