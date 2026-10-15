# w-bfclcontain: expression execution finding and fabricated differential

**FOUND: the generic prompting decoder is uncontained.** A fabricated argument
`fabricated_echo(value=__bfclcontain_probe__()+0)` invoked the harness's harmless
in-memory probe and decoded its return value as `7`. The probe event is
`["entered"]`; an inert decoder would have recorded `[]`.
See `tests/fixtures/hg_bfclcontain/observations.jsonl:28` and
`tests/fixtures/bfcl_ast_source/candidate-codex195/files/berkeley-function-call-leaderboard/bfcl_eval/model_handler/utils.py:302`.
This is a finding handoff, **not containment closure**. Further execution-path
probes stop at this finding; no acquired source or production adapter workaround
is included (`tests/fixtures/hg_bfclcontain/control.py:164`,
`registry/w-bfclcontain-validation.txt:1`).

**FOUND: the bounded differential reproduces 19 fabricated cases**, comprising
6 mutual accepts, 5 mutual rejects and 8 platform accepts/upstream rejects.
The exact cases, complete synthetic schemas/references, platform answer text,
both verdicts and outcomes are in
`tests/fixtures/hg_bfclcontain/observations.jsonl:1` through its first 19 records;
the summary is `tests/fixtures/hg_bfclcontain/observations.jsonl:29`.
These are direct function controls, not an official scorer entrypoint, dataset
run or measured benchmark result (`tests/fixtures/hg_bfclcontain/control.py:122`).

## Scope and evidence states

FOUND means the cited source or observed execution was retrieved. ABSENT is
limited to the enumerated scope and named search below. UNKNOWN is an untested
property or unobserved binding, never an assertion of safety. The per-site
review separates source retrieval from dynamic control coverage
(`tests/fixtures/hg_bfclcontain/boundary-review.jsonl:1`).

The search scope is **every `.py` below**
`tests/fixtures/bfcl_ast_source/`,
`tests/fixtures/external_provenance_b5/bfcl/`, and `data/scaffolds/qa/`, plus
`data/datasets/bfcl_v3.py`, the extensionless `data/scaffolds/qa/cli/qa`, and
`data/__init__.py`, `data/scaffolds/__init__.py`, `data/datasets/__init__.py`.
The exact 62 paths, observed sizes and SHA-256 values are enumerated in
`tests/fixtures/hg_bfclcontain/source-inventory.json:1`.
Reproduce the AST search with `inventory()` in
`tests/fixtures/hg_bfclcontain/control.py:42`; the exact command/output are in
`registry/w-bfclcontain-validation.txt:1`.
It finds 37 lexically named sink statements, including `ast.parse` because it
compiles model text to an AST. Their exact source expressions, enclosing functions
and file:line identities are `tests/fixtures/hg_bfclcontain/sinks.jsonl:1`.
Every one has a corresponding reachability/boundary review in
`tests/fixtures/hg_bfclcontain/boundary-review.jsonl:1`.

**ABSENT in that enumerated lexical call search:** explicit Python `exec` and
`compile` calls; pickle/yaml loader calls; `os.system`/`os.popen` shell calls;
sink calls in the platform's BFCL module and retained AST checker itself.
The regex `re.compile` calls are not Python expression compilation. The retained
server/control subprocess statements pass argument vectors without `shell=True`
(`tests/fixtures/hg_bfclcontain/sinks.jsonl:10`,
`tests/fixtures/hg_bfclcontain/sinks.jsonl:36`).
This is not a whole-machine search or proof against arbitrary reflective aliases,
unacquired dependencies, hostile objects or primitives invoked inside unrestricted
eval. Those properties are UNKNOWN; the confirmed eval path already defeats a
general containment claim (`tests/fixtures/hg_bfclcontain/observations.jsonl:28`).

The prior handler report was read as a handoff, not re-derived: served name,
chosen handler branch and response encoding remain **UNKNOWN**
(`registry/w-bfclmem-handler.md:9`). Its QwenFC source is outside the two
authoritative upstream source roots specified for this task, so this work neither
imports it nor turns its reported JSON-only branch into a deployed containment
claim (`registry/w-bfclmem-handler.md:15`,
`tests/fixtures/hg_bfclcontain/control.py:29`). The runtime-custody and
attestation frontiers are retained, not reopened
(`registry/w-bfclrt-custody.md:3`, `registry/w-bfclattest-validation.txt:1`).

## Deliverable 1: expression boundary

The actual prompting path is OSSHandler.decode_ast ->
default_decode_ast_prompting -> ast_parse -> resolve_ast_call ->
resolve_ast_by_type. A keyword binary expression reaches ordinary eval without
first restricting its operands. A nested Call with keywords, or a list/dict/tuple,
can recursively re-enter the resolver; quoted strings take the Constant branch.
Sources:
`tests/fixtures/external_provenance_b5/bfcl/files/berkeley-function-call-leaderboard/bfcl_eval/model_handler/local_inference/base_oss_handler.py:54`,
`tests/fixtures/bfcl_ast_source/candidate-codex195/files/berkeley-function-call-leaderboard/bfcl_eval/model_handler/utils.py:695`,
`tests/fixtures/bfcl_ast_source/candidate-codex195/files/berkeley-function-call-leaderboard/bfcl_eval/model_handler/utils.py:263`,
`tests/fixtures/bfcl_ast_source/candidate-codex195/files/berkeley-function-call-leaderboard/bfcl_eval/model_handler/utils.py:280`.
The runner's decode exception handler runs after any side effects; it does not
contain evaluation
(`tests/fixtures/bfcl_ast_source/candidate-codex195/files/berkeley-function-call-leaderboard/bfcl_eval/eval_checker/eval_runner.py:268`).

All 37 sink sites are individually enumerated in the machine-readable review;
the following groups explain their source-level relationships. No group without
a distinguishing control is declared dynamically contained.

| Sites in boundary-review.jsonl | Payload reachability and boundary |
|---|---|
| 21, 26 | `convert_value` / `_convert_value` feed value strings to literal_eval. Direct code-string controls returned the string without calling the probe. No callers of these helpers were found in the enumerated acquired source; production reachability and resource bounds remain UNKNOWN. |
| 22, 27 | The same helpers select and call `getattr(builtins, type_str)` without an allowlist. A model-controlled type selector would be unsafe; the acquired scope supplies no observed caller binding that selector to a model string. No dynamic control after the finding; containment UNKNOWN. |
| 23 | ast.parse compiles fabricated prompting text into an AST. It does not execute at this statement; the downstream resolver is unsafe. No size/depth/CPU/memory bound in this method. |
| 24 | Binary-expression eval is reachable and **observed UNCONTAINED**. The canary distinguishes execution from a happy-path parse or an exception. |
| 25 | Lambda branch contains eval, but first indexes `value.body[0].value`; a normal Lambda body is an expression. Successful eval reachability/control UNKNOWN; not claimed contained. |
| 28–29 | Multi-turn getattr selectors come from public ground-truth instance attributes, not prediction names. No Simple AST call path. Object/property behavior and runtime containment UNKNOWN. |
| 30–31 | Multi-turn import/getattr uses the fixed class/module mapping and caller-provided involved_classes before iterating call strings. Prediction fields do not directly select these imports. Real module custody UNKNOWN. |
| 32 | Multi-turn string eval follows method rewriting and a short denied-name list. Direct call-string entry exists in source; it is outside Simple AST. No additional dynamic probe after the BinOp finding; containment UNKNOWN. |
| 33 | Cohere literal_eval consumes execution-result strings, potentially model-influenced through tool execution. Outside Simple AST; no site-specific control or resource proof, hence UNKNOWN. |
| 34 | OpenAI handler getattr uses literal `tool_calls` on an SDK object. Call-name text does not choose the attribute. SDK/runtime behavior UNKNOWN. |
| 35 | Arch response parsing evals tagged bodies that remain strings after JSON decode fails. Source-reachable alternative handler; no dynamic control after the finding. Does not establish local handler selection; containment UNKNOWN. |
| 36–37 | Server argv derives from run/model configuration before responses; no response-to-shell path at these statements. No process was launched and runtime containment remains UNKNOWN. |
| 1–14 | Shared QA control import derives from the CLI dataset selector; getattr names are literals. Subprocess calls use argv and pass oracle text as one argument. Prediction text does not select an import, attribute or shell program. No control/dataset run performed. |
| 15 | Oracle harness passes its staged answer as a single CLI argument, without shell=True. Not executed. |
| 16–20 | Shared verifier import derives from regex-validated CLI dataset name and fixed prefix; getattr names are literals. It passes answer data to the already-selected scorer. This bounds selector flow in source, not materialized-module/search-path custody. |

Each table row's exact original file:line, expression, source retrieval state and
dynamic-control state are retained in
`tests/fixtures/hg_bfclcontain/boundary-review.jsonl:1`.
In particular, the Arch extraction fallback is visible at
`tests/fixtures/external_provenance_b5/bfcl/files/berkeley-function-call-leaderboard/bfcl_eval/model_handler/local_inference/arch.py:193`;
the verifier's selector validation precedes its import at
`data/scaffolds/qa/verify/check.py:222`; the fixed BFCL verifier argv comes from
`data/scaffolds/qa/base.py:345` and `data/datasets/bfcl_v3.py:530`.

Nine controls record the exact payload, output, probe-event list, and expected
unsafe observation (`tests/fixtures/hg_bfclcontain/observations.jsonl:20`):

- Three raw-call texts sent to the platform score function: expression-shaped
  function name, quoted code argument and nested call. They were rejected with no
  probe event. This tests the platform's actual text boundary, separately from the
  differential's explicit call-to-name projection.
- The same three texts sent to the original prompting decoder: respectively an
  empty extracted function name, a retained string, and nested dictionary/string
  data, with no probe event. These inputs alone would be falsely reassuring.
- A nonliteral code string sent to each literal_eval helper: retained unchanged,
  no probe event.
- The decisive binary-expression argument: returned `7`, **probe entered**.

For **each** control, the unsafe observation is `probe_events contains entered`;
the test asserts the entire expected output **and** the event list. The final
control positively records the unsafe observation. The probe performs only an
in-memory list append and returns 7; no file/process/network payload was used
(`tests/fixtures/hg_bfclcontain/control.py:156`,
`tests/quality/test_bfclcontain_differential.py:41`).
Passing tests preserve this finding; they do not certify containment.

## Deliverable 2: fabricated full-call differential contract

**Authority:** the unchanged platform functions are authoritative for the existing
name-only diagnostic; the retained upstream format predicate and AST checker are
authoritative for the bounded decoded Python Simple full-call decision. Neither
side is authoritative for unknown serving/handler/encoding or an official-run
receipt. Full-call correctness is not defined by name-only equality
(`data/datasets/bfcl_v3.py:217`,
`tests/fixtures/external_provenance_b5/bfcl/files/berkeley-function-call-leaderboard/bfcl_eval/utils.py:140`,
`tests/fixtures/bfcl_ast_source/retry-codex227/files/berkeley-function-call-leaderboard/bfcl_eval/eval_checker/ast_eval/ast_checker.py:30`).

The harness compiles exact original AST function nodes with original line numbers,
not copies of their behavior. It selects the four platform functions, the upstream
format predicate, and the checker's functions/type constants. It supplies real
stdlib ast/re/builtins only; no replacement checker helpers, handler, model map or
Java/JS converters are invented. Module imports/initializers and the official
runner are deliberately not executed. This is a **test-only source slice**, not
full-package import/runtime closure or a passing technical source gate
(`tests/fixtures/hg_bfclcontain/control.py:71`).

Inputs are fabricated decoded call sets plus their complete fabricated raw schemas
and acceptable-value references. Language is Python, category is Simple, and
trusted schema names have no dots. This makes convert_func_name return before
model-map lookup; the obvious `UNBOUND-FABRICATED-NO-MODEL-MAP` sentinel is not a
serving alias. Dotted schema names fail loudly before comparison, rather than
inventing underscore_to_dot (`tests/fixtures/hg_bfclcontain/control.py:129`,
`tests/quality/test_bfclcontain_differential.py:68`,
`tests/fixtures/bfcl_ast_source/retry-codex227/files/berkeley-function-call-leaderboard/bfcl_eval/eval_checker/ast_eval/ast_checker.py:75`).

The platform input is the explicit newline-joined function-name projection of each
fabricated call set; the upstream input retains the **whole** call/schema/reference.
The real upstream format predicate rejects malformed multi-key calls before the
checker. Unexpected exceptions are test failures, never zero verdicts or skipped
cases (`tests/fixtures/hg_bfclcontain/control.py:132`).

The 19 cases cover exact/wrong value, wrong type, missing required/extra parameters,
wrong function, namespace erasure, duplicate/empty calls, multi-key format rejection,
optional omission with/without the empty alternative, int-to-float, bool-versus-int,
list order, string normalization, inert code strings, expression-shaped names and
dictionary alternatives (`tests/fixtures/hg_bfclcontain/cases.json:1`).
Checker source defines required/extra/optional handling and value/type routing at
`tests/fixtures/bfcl_ast_source/retry-codex227/files/berkeley-function-call-leaderboard/bfcl_eval/eval_checker/ast_eval/ast_checker.py:333`;
string/list rules are at
`tests/fixtures/bfcl_ast_source/retry-codex227/files/berkeley-function-call-leaderboard/bfcl_eval/eval_checker/ast_eval/ast_checker.py:166`.

**Meaning of disagreements:** the eight platform-accept/upstream-reject cases are
known metric gaps, explicitly pinned individually. They must not be silently
turned into equal verdicts. Any change from a case's recorded pair, error detail
or complete output fails the test; source drift also fails. Mutual agreement on
these finite cases is not benchmark equivalence
(`tests/quality/test_bfclcontain_differential.py:34`,
`tests/fixtures/hg_bfclcontain/observations.jsonl:2`).

Standalone reproduction requires only stdlib (`python3 -I -S -B
tests/fixtures/hg_bfclcontain/control.py`). During source-slice initialization and
comparisons, an audit tripwire rejects file/device opens, imports, sockets,
subprocesses, process launch and ctypes. Swallowing its exception still fails the
outer assertion. Six tripwire tests emit audit events directly, including a GPU
device open, dataset open and official-runner import; they do not perform those
operations. This is dependency detection for these controls, **not a production
sandbox** or proof of resource containment
(`tests/fixtures/hg_bfclcontain/control.py:99`,
`tests/quality/test_bfclcontain_differential.py:58`).

## Remaining obligations

**Technical source gate: still blocked.** No independently approved receipt pin
was supplied. The unchanged gate still refuses without one, before source reads;
locally observed source hashes are integrity observations, not approval. The
explicit command returned exit 2 and the fixed blocked JSON
(`tests/quality/test_bfcl_ast_source_contract.py:80`,
`registry/w-bfclcontain-validation.txt:1`). No guard is weakened or declared stale.

**UNKNOWN / not verified:** actual served model identity, config/handler branch,
raw response encoding and handler decode; dotted-schema model-map behavior;
Java/JavaScript and other categories; positional/raw syntax coverage beyond the
listed boundary controls; arbitrary malformed objects, exhaustive nesting,
input/output size and CPU/memory limits; filesystem/process/network isolation,
quota/export/snapshot/cleanup of a real run; source/index custody approval;
full-package official scorer import/execution, aggregation and denominator;
the runtime worker's compiled-build frontier. No task, released reference or
selected/held-out row was read for these controls
(`tests/fixtures/hg_bfclcontain/control.py:122`,
`tests/fixtures/hg_bfclcontain/cases.json:1`,
`registry/w-bfclcontain-validation.txt:1`).

A later authorized run must supply the actual serving/config/handler/encoding
binding, independent source/index/runtime identities and complete trusted selected
schemas/reference alternatives; validate the **same** fabricated contract through
its actual decode/checker route; and record official metric/input/runtime/source/
receipt identities and resource/cleanup evidence. Production currently reduces
references to names; this task does not implement or assert a full-call integration
(`data/datasets/bfcl_v3.py:491`, `data/datasets/bfcl_v3.py:504`,
`registry/w-bfclmem-handler.md:9`).
The unsafe expression finding and failed technical gate remain obligations, so no
replacement next_action or status proposal is made. The blocker remains external
and open on actual official scorer execution; the blocker checker still returns
valid=true and production_authorized=false
(`registry/w-bfclcontain-validation.txt:1`).
