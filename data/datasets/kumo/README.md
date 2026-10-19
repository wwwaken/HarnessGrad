# KUMO native adapter

Coverage: **5,290 of 5,300** released standard cases (5,040 easy, 250 hard).
Source: `linhaowei1/kumo@576748764f7d72634654d0784944a485eca9047c`.
Downloaded sparse source: 5,846 files, 127,892,007 bytes; no historical model results.
The default data root is the workspace sibling `datasets/kumo`; override with `HG_KUMO_DATA`.
Data, private answers, books and audit artifacts stay outside this repository.

## Provisioning

```sh
python3 data/datasets/kumo/prepare.py --fetch
python3 tools/datasets.py --check --dataset kumo
python3 tools/dataset_lint.py --dataset kumo
```

`--fetch` uses a pinned sparse Git checkout, then audits every candidate twice and
creates `prepared-v1`. With an existing checkout, omit `--fetch`. Preparation refuses
to overwrite an existing prepared directory. Source blobs are checked against Git;
public/private files are bound to a pinned manifest. The adapter verifies public
bytes; the KUMO relay and verifier each check the selected private case.
`source-files.json` also supports the generic downloader's per-file SHA256 checks.
No extra Python dependencies or model calls are needed for preparation/scoring.
Older prepared materials include the VanillaAgent prompt. Preserve the old
`prepared-v1` directory and rerun preparation to obtain the current public files
and manifest; private cases, task selection and scoring remain unchanged.

## Metric and protocol

The metric is `kumo.official.consistency_accuracy.v1`: upstream
`env/engine.py::Environment.evaluate_answer` is vendored verbatim with its license.
It accepts a candidate iff its rules are consistent with **all** released observations,
including inclusive numeric intervals. No judge model is used.

This differs from Harbor's exact gold-string score. The full repeated audit found
5,255 uniquely accepted golds, 35 cases with multiple accepted candidates, and 10
cases for which no candidate is consistent. The 35 ambiguous cases are retained
with the official predicate. The 10 excluded easy cases are:

- FungalEnv/36
- MythicalCreatureEnv/9, /14
- QuantumEnv/3, /15, /36
- SorcererEnv/0, /5, /7, /40

Exclusion is recomputed from the official predicate, not the handwritten list.
Per-row evidence and source digests are in `official-audit.json`.
MedicalOOD is outside the standard 5,300-case suite (its extra file is truncated
and lacks corresponding books).

Protocol `kumo.query50.v1` follows Harbor's limit of **50 accepted action queries**,
including repeated actions. Invalid actions do not spend that budget. This differs
from upstream VanillaAgent's limit of 50 model turns; scores are not directly
comparable across those protocols. The transport separately limits each run to
**256 total service calls**, including `stats` and invalid queries. Calls beyond
that limit are refused even when action queries remain; the relay reports this
as a transport fault, so the run is unmeasured. Local `show` and `submit` commands
do not consume service calls. The adapter declares a deterministic hash split
using the existing platform rule (3,515 train / 1,775 eval). This is an adapter policy,
not an official upstream split; `OFFICIAL_EVAL` remains unset. The diagnostic selects
only train. Other datasets' split handling is unchanged.

## Execution and isolation

The actor gets the selected public book, candidate/action lists and `kumo.py`:
`show`, `do`, `stats`, `submit`. A private host-side Unix relay answers actions.
Public materials omit the upstream VanillaAgent system prompt. The harness
chooses its prompts, query order, batching, reasoning and completion procedure.
The verifier reads only the final `answer.txt`, which must contain one candidate
verbatim. `submit` is an optional file-writing helper; it does not terminate the
harness or prevent the harness from subsequently overwriting the answer.
The shared transport limits total calls, and a lock preserves the episode budget
across reconnects. No private answer, rules or unqueried observation table is mounted
in the actor sandbox. Only the selected private case is read by the relay.

The relay enforces the 50-query budget in host memory. After actor exit, the
standard command verifier scores only the final answer against the pinned private
case using the official predicate. It neither consumes nor trusts actor-produced
query recordings. No trusted episode is exported through a new runner field.
Relay startup/transport failures use the existing unmeasured path. Shared runner and
relay code are unchanged from before KUMO integration. This retains the existing
lifecycle limitations: the runner does not remove relay staging directories, startup
failures can leave staging, and explicit `cleanup()` ignores deletion errors. These
are shared platform issues, not fixed or claimed as resolved by this adapter.

Run with the native filesystem sandbox (the default); privacy is not promised
for an explicitly unsandboxed run. Network is inherited to support a configured
HTTP or HTTPS model endpoint. Egress restrictions, filesystem quotas and prevention
of online answer lookup are not claimed. This is an integration adapter, not a
production benchmark admission.

## Validation

```sh
python3 data/datasets/kumo/control.py --oracle
python3 data/datasets/kumo/control.py --noop
python3 data/datasets/kumo/control.py --oracle --platform
python3 data/datasets/kumo/control.py --noop --platform
python3 tools/run_tests.py --dataset kumo --with-registry --jobs 8
```

Controls use the mock backend and require scores 1/0. Tests cover vendored scorer
identity/differential behavior, full provisioned audit, cross-connection budgets,
private data isolation, scoring independent of forged recordings, and source mismatch
rejection. Test fixtures clean their own relay staging; that is not evidence of
automatic cleanup by the runner.

The control entry point and its scripted `oracle_harness/` live beside the adapter's
CLI and verifier, following ALFWorld/Jericho. The platform oracle makes one real
relay query and submits the staged released answer through `kumo.py`; no shared
oracle source is rewritten. The local arm reuses the shared command-control helpers.

There is no KUMO-specific API diagnostic command. Real model runs use the existing
platform runner/driver and base harness. Historical diagnostic artifacts are retained
outside the repository; they are integration evidence, not aggregate benchmark results.

## Recorded real API smoke

At commit `b8899205`, on 2026-10-17, the user-authorized `.env` API trial on the preselected train task
`CookingEnv/42` completed with **score 0**, 12 model calls, three action queries,
42,300 input / 1,141 output tokens, and 163.102 seconds. The actor exited normally,
the official verifier measured the answer, and both relay and work root were cleaned.
The wrong answer was retained without a score-based rerun. Evidence lives outside git
at `datasets/kumo/diagnostic-20261017-02`; the preceding zero-attempt configuration
failure is also retained. See the integration journal and `validation.json` for scope.

## Minimal integration revision — 2026-10-18 (historical: `5ab95cab`)

The former shared hash fields, trusted-recording injection, result fields, global
relay admission changes, classifier fallback and download-summary rendering have
been removed. KUMO uses the existing `files`, `tool_relay` and `command` contracts.
The only shared runtime changes retained are relay process/directory cleanup on
success and failure, with cleanup failures propagated. Control orchestration lives
in `tools/kumo_control.py`; only the relay's shared-transport import needs a new
file-specific dependency exception.

The 2026-10-17 API result and `validation.json` are historical evidence for the
previous implementation; this revision is validated with controls and regression
tests, with no new API calls. See `validation-minimal-20261018.json`.


## Shared runtime restored — 2026-10-18

This supersedes the retained lifecycle changes described in the preceding revision.
`eval/run/runner.py` and `eval/run/tool_relay.py` are restored byte-for-byte to
`89626402` (before KUMO). There are no shared execution/interface behavior changes
from this integration. Existing datasets keep their original cleanup and exception
behavior. KUMO inherits the lifecycle limitations documented above. The earlier
`validation-minimal-20261018.json` describes `5ab95cab`, not this revision. No new
API run was made. Current checks are in `validation-compatible-20261018.json`.


## Dataset-local controls — 2026-10-18

The control entry point is now `data/datasets/kumo/control.py`, with its own
`oracle_harness/`, matching existing interactive datasets. The former
`tools/kumo_control.py` and `tools/kumo_diagnostic.py` entry points are removed.
The dependency guard names the control's three exact execution imports, as it does
for other dataset-local controls. This changes no shared execution interfaces.

After shared runtime restoration at `02c93b5f`, the user-requested real test with
`Ling-3.1-flash` completed CookingEnv/42: answer `Stewing`, official score 1,
7 model calls, 6 queries, 18,594 input / 1,477 output tokens, 20.938 seconds.
One action parse error recovered. Evidence remains at workspace
`datasets/kumo/diagnostic-restored-20261018T015854683418Z/assessment.json`.
The prior `Ling-3.0-flash` test is also retained; it exercised queries but did not
submit an answer and is not counted as a complete answer-submission test.
The external validation launcher cleaned each run's temporary root after checking
for surviving processes; this does not change the baseline runner's cleanup behavior.
No additional API requests are needed for this layout change.
