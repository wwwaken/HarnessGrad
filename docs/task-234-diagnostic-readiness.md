# Task 234 — diagnostic readiness at current HEAD

**No dataset is ready for a justified first model diagnostic on either GPU.**
The source inventory contains **28 datasets: 24 blocked, 4 explicitly excluded,
0 ready**. Of the 24 blocked datasets, 23 reference all eight registry shared
blockers; AgentDojo has a separate production-route gate. These are source-review
dispositions, not measured benchmark failures or observations of GPU availability.

Reviewed HEAD: `61e7f82245c76e7c833740216940d1fcaf3b76be`; tree:
`d74461cdd2e3cd6a06f76d2b5b09160f1883dd20`. Initial worktree was clean.
Work stayed in `/tmp/hg-codex-234`, on 2026-10-14. The companion
[metadata snapshot](task-234-diagnostic-readiness.json) records exact registry
blocker IDs, taxonomy, stage distinctions and SHA-256 pins of reviewed inputs.
This report evaluates that pinned HEAD; its own documentation commit is not a
new runtime observation. Re-review after any relevant source or policy change.

Only repository source, public code-provenance metadata and documentation were
reviewed. No adapters/task pools were imported; no benchmark payload, heldout,
external receipt or dataset root was opened. No model, H0, endpoint, GPU, Docker,
host-quota query, backend mutation, official scorer or benchmark control ran.
No task was selected, run ID reserved, policy evidence supplied or score created.

## What changed, and what did not

| Current evidence | Recomputed disposition |
| --- | --- |
| [TriviaQA review 215](../reports/triviaqa-review-codex215-report.md), merged normalization/all-alias fixes | Evaluator acquisition is closed. Current metric identity is `triviaqa-alias-max-em-upstream-normalization-all-aliases-v2`; do not invent v3 or retain the obsolete acquisition gate. `hub-export-scorer-linkage` remains external. Export-to-loader/scorer, selected question identity and denominator need independent metadata/code binding; deployed scorer/harness and shared runtime evidence remain missing. Per-row alias-max EM is not full upstream grouping/F1 or leaderboard equivalence. |
| [2Wiki review 206](task-206-twowiki-provenance-review.md), [registry audit 216](task-216-twowiki-registry-audit.md) | Independent original v1.0/v1.1 evaluator source acquisition is closed. `ujson-native-offline-closure` and `hub-data-provenance` remain external. An installed extension plus synthetic execution is not wheel/installation-origin, loader/transitive or deployment closure. `recovery-comparability` concerns old mixed Answer F1/Joint F1 receipts, not a requirement to rerun the old pilot before the first new diagnostic. |
| [GAIA packet 210](gaia-operator-packet-codex210.md), [review 219](gaia-contract-review-codex219.md) | All operator deliveries remain pending. The full scorer-revision discrepancy, source custody/lock, NumPy/Python/native closure, selected validation/attachment/gold projection, actor/pristine-verifier identities, supported services-network admission, quotas, export, snapshot and cleanup are unresolved. Task-202/212 inputs are unavailable as recorded; their reconciliation is pending, not inferred from another packet. The dry preflight always blocks execution and does not validate runtime receipts. |
| [Terminal packet 211](task-211-terminal-operator-backend-packet.md), [review 220](task-220-terminal-packet-review.md) | Q1/Q2/T1/S1/O1/C1/D1 remain open. Pristine scorer state must be exactly `State.Status="created"`, `State.Running=false`; stopped/exited is insufficient. `benchmark_blockers` unconditionally retains three gates per task (dependency, trusted runtime, export), plus paired quotas and official execution. Six cached images are historical availability claims, not admitted eligible tasks. |
| [Quota source audit 168](../reports/filesystem-quota-codex168-report.md), [backend specification](filesystem-quota-backends.md), [administrator checklist 222](task-222-quota-administrator-checklist.md) | No complete connected paired byte/inode backend is established. Audit 168 explicitly did not inspect host state; checklist 222 performed no host inspection and leaves every action pending. Current host capability is **unknown**, not proven unsupported or enforced. No fresh host provisioning, project/tmpfs, writer-inventory, storage or cleanup receipt is supplied at this HEAD. Relocation, free capacity and reservation ledgers do not close the gate. |
| [Scorer backend review 221](../reports/scorer-backend-review-codex221-report.md), current `eval/admission/scorer_backend.py` | A standalone preflight now composes lifecycle/resource/scorer/export checks. A contradictory policy pin stays blocked even without runtime observation. This supersedes any absolute claim that the validators have no compositional caller. It does not provide a production driver/runner caller, observer, official invocation, same-instance/freshness proof, snapshot completion or cleanup. Passing flags remain unmeasured and unauthorized. |
| [Dry template 223](task-223-dry-diagnostic-launch.md), current `driver.save_policy_receipt` | Still supplies unknown cleanup/snapshot and omits lifecycle. Even provisional measured outcomes are withheld as unmeasured/null; staged curve publication is refused. An externally edited policy file cannot supply the missing producer. This is an independent first-diagnostic blocker across staged routes. |

## First diagnostic, its completion, and expansion are different gates

**Before the first diagnostic:** close the selected dataset's applicable source,
privacy, scorer, runtime and resource requirements. Obtain independently reviewed
selected-only source/split/eligible-ID custody and controls, then freeze exactly
one deterministically selected task from a nonempty eligible pool. Freeze the
metric/scorer, actual source/split/manifest/model/harness hashes, one endpoint,
finite enforced resource/budget limits and fresh ownership/run identity. Use
`sampling=diagnostic`, one task, `trials=1`, `jobs=1`, `rounds=0`, `improver=none`;
independently establish total H0 concurrency `<=3`. Review supported observation,
scorer/export, bounded snapshot and failure/cleanup paths and their production
receipt writer before launch. A prior model diagnostic is **not** required here.

**During and after that diagnostic:** collect actual execution/quiescence,
official metric invocation, artifact linkage, bounded export/snapshot completion
and exact owned cleanup evidence. These final facts cannot exist before their
operations. They must flow through the trusted producer and lifecycle
`scope → admit → execute → quiesce → score → seal → cleanup`. Require diagnostic-v2
schema **and** semantic/replay validation, consistent scope/outcome/summary hashes,
all selected outcomes and eligible/selected/task/trial coverage. Passing gates,
snapshot and cleanup are necessary before publishing any measured score. Failures
remain invalid/unmeasured with null score; an ordinary measured zero is valid
only when measurement succeeds. Later cleanup does not repair a failed trial.

**Before expansion:** obtain a *separate* approved reviewer/time/digest record
bound to the entire valid measured first diagnostic. `require_review` requires
one measured trial, zero invalid/unmeasured, matching eligible pool/digest and
selection, dataset/side, metric, all five hashes, scorer hash, endpoint, limits
and gates, plus successful lifecycle/snapshot/cleanup and a fresh expansion ID.
Unknown pins/limits cannot authorize expansion. Only then may a temporary rerun
preselect `min(30, ceil(0.10 * eligible))` tasks, one trial, one job, zero rounds.
Never use historical 50×3 or 9×3 as a new launch protocol.

The context validator permits explicit nulls for incomplete planning/failure and
model-free records. That structural allowance is not evidence of a launchable
model diagnostic. Model-free records use null model/endpoint plus an explanation;
they cannot satisfy model-diagnostic expansion review. Similarly, a structurally
passing lifecycle still has `production_authorized=false` and authenticates no
observer. No completed future diagnostic receipt is demanded *before* that
diagnostic; a viable reviewed production path to produce it is demanded.

**Historical comparability is separate:** old curves need matching metric,
source/split/selection, denominator, trial protocol, harness/model, runtime and
limits before comparison. A new local metric may be clearly scoped without
claiming leaderboard or old-curve equivalence. Preserve all 11 registry historical
records and null effects; this audit does not open or authenticate their external
receipts. Completed historical generations are not justification for duplicate
GPU work. A prior successful/nonzero task is not a universal first-diagnostic
requirement: AppWorld retains its explicit successful-task *expansion* gate.

## Exact shared requirements still open

The following applies to each of the 23 rows marked **S** below. Registry status
labels classify remaining work; they are not readiness or stage labels.

| Exact registry ID / work status | Requirement before first diagnostic | Completion / expansion distinction |
| --- | --- | --- |
| `runtime-observations` / runtime | Independently trusted, fresh run/trial/phase-bound effective cgroup/resource/deadline, read-only-root, network and mount observations; production launch integration. Unsupported topology stays blocked. | Preserve observer/same-instance authenticity and enforcement through use; dictionaries and hashes alone do not prove it. |
| `paired-filesystem-quotas` / runtime | Enforce positive exact allocated-byte **and inode** bounds before any staging/write, independently scoped across every writer, including workspaces, scratch, verifier, daemon, exports/snapshots, logs and evidence. Current host state remains unknown. | Require kernel readback, identity/freshness/coverage and owned-scope cleanup; the proposed sidecar schema has no connected collector/semantic implementation. |
| `scorer-offline-closure` / code-solvable | Independently pin complete official/local metric source, dependencies/ABI and pristine offline runtime; connect current bundle/backend preflight into production. | Declared closure integrity does not establish completeness or actual official invocation. |
| `pristine-verifier` / runtime | Independently identify/admit a fresh trusted verifier, protected gold and read-only trusted inputs, distinct from actor runtime/snapshot. | Actual invocation must remain bound to those bytes/runtime; an actor toolchain is insufficient. |
| `artifact-only-state-export` / code-solvable | Review and wire an explicit bounded data-only task artifact contract, quiescence and fresh platform-owned export path. | Observe actual export/seal and scorer input linkage after quiescence; whole actor trees/snapshots do not close this gate. |
| `official-scorer-identity` / measurement | Freeze honest metric/version/aggregation/denominator and independently authenticated source/runtime/scorer pins; establish a usable verified scoring route and required no-model controls. | Record fresh official invocation and actual deployed hashes in the diagnostic. Upstream file hashes alone cannot substitute for adapter/harness identity. |
| `snapshot-owned-cleanup` / runtime | Review/integrate bounded snapshot/export worker, all-writer quiescence, paired capacity/reservation/enforcement, durable ownership intent, exact absence/atomic lease release or quarantine and failure recovery. Reconcile relevant interrupted ownership before reallocation. | Actual completion/absence receipts are produced afterward; preflight, removal exit codes or later cleanup cannot substitute for successful measurement lifecycle. |
| `pilot-guidance-conflict` / code-solvable | Keep the chosen plan explicitly under current AGENTS/staged 1×1 rules; retain historical descriptions. The platform log already has an overriding current-policy preamble, though its old table/contract wording remains indexed. | This documentation issue is not a missing prior-diagnostic requirement. Resolve any ambiguity before expansion; never infer 50×3 authorization. Registry remains conservatively unchanged. |

Two cross-cutting gaps additionally affect staged readiness: **L**, the missing
trusted lifecycle producer/driver wiring; and **P**, authenticated eligible
selection/provenance, frozen metric/content pins, endpoint/budget/ownership and
current dataset control review. Early staged selection is not selected-only
loading: current driver loaders run before narrowing. S is the exact registry
reference set; L/P express current source/operating-rule obligations, not new
registry fields. For AgentDojo, keep its specialized gate without silently adding
the eight shared references it does not declare.

## All 28 dataset dispositions

Every **blocked** row also lacks a complete reviewed new-run evidence package.
“Comparison” entries below are not automatically additional pre-first-run gates.
Resolve the chosen metric's own semantics before launch even when historical
equivalence is unnecessary. Exact observed findings, actions, taxonomy and evidence
locators are retained in the companion JSON.

| Dataset | First-diagnostic disposition and exact additional gate IDs | Expansion / historical comparison requirements |
| --- | --- | --- |
| `agentdojo` | **Blocked, specialized** — `production-route-admission`: independent selected-group manifest/custody and fresh non-scoring production-route verifier/lifecycle/cleanup evidence. Metadata/privacy source tests do not admit `run_one`. | Historical selected controls are not fresh route evidence; no adversarial execution is authorized by this review. |
| `alfworld` | **Blocked, S+L+P** — `current-runtime-review`: review current selected controls/runtime/identity, without demanding the future diagnostic's result in advance. | Preserve complete historical 9×3 generation; no redundant rerun without a new scientific protocol. |
| `api_bank` | **Excluded** — `retain-contract-refusal`; explicitly prohibited by operating rules. Missing dialogue-state metric contract remains. | Do not provision/run or substitute a metric. |
| `appworld` | **Blocked, S+L+P** — current selected-only/state-reset/service/gold/scorer route and controls need fresh admission. `successful-task-evidence` is not a requirement that the first new diagnostic score above zero. | Explicit successful measured task gate remains before expansion; healthy 16/32-step zeros do not close it. No task tuning or budget escalation; historical 9×3 is superseded. |
| `bfcl_v3` | **Blocked, S+L+P** — `release-index-custody`, `simple-ast-contract`: independently approve archive/tag/commit and selected index/release custody; acquire exact pinned parser/checker/dispatch/helper/license projection and derive full-call semantics with fabricated differential inputs. | Current function-name multiset is diagnostic-only, not official Simple AST/full-call accuracy. Source contract is still unacquired. |
| `bird_minidev` | **Blocked, S+L+P** — `sql-coverage-reconciliation`: establish selected SQL engine/schema/scorer reachability and coverage/error classification. | Reconcile V5 28/34 measured tasks and trial metadata; preserve V4 incomplete and V5's historical label/coverage limit. |
| `chessbench_puzzles` | **Blocked, S+L+P** — `trusted-stepwise-transport`, `interruption-closure`: production public-observation/official interactive scoring integration and actor isolation; termination/owned-resource uncertainty needs independent review. | Both interrupted IDs stay incomplete and immutable; fabricated transport is not official interactive accuracy. Old terminal scores are not prerequisites to a fresh diagnostic. |
| `ds1000` | **Blocked, S+L+P** — `host-slice-archive-review`: establish the intended source pool/host slice, selected controls and timeout outcome semantics. | Review old 61-task/926-of-1000 scope, selected trials/timeouts and archive before accepting any historical effect. |
| `fever` | **Blocked, S+L+P** — `dataset-journal-gap`: current scorer/provenance/privacy/runtime/control review is absent. | Missing entry proves no readiness; define any intended comparison separately. |
| `gaia` | **Blocked, S+L+P** — `frozen-lifecycle-receipt`: all packet deliveries listed above, immutable source lock, supported network/export route and task-202/212 reconciliation remain pending. | V2/V3 incomplete, trace/event coverage conflict and snapshot exit-137 cause remain unresolved; no aggregate. Selected validation is not full test leaderboard. |
| `gsm8k` | **Blocked, S+L+P** — `scorer-protocol-comparability`: pin decimal-aware scorer and define current trial-mean metric/denominator before execution. | Old integer scorer is distinct; trial-mean is not verifier-selected test@N, which remains unimplemented. Old-curve equivalence is not a first-diagnostic prerequisite. |
| `hotpotqa` | **Blocked, S+L+P** — `schema-timeout-measurement`: review repaired structured-evidence contract and timeout/invalid classification. | Stopped V4 94/1476 trials stays incomplete; no zero imputation or old full-size rerun. |
| `jericho` | **Blocked, S+L+P** — `independent-runtime-proof`: independently validate selected production runtime boundary/controls from a work root outside platform checkout. | Source projection/phase repairs and historical 16/16 controls are not current production-path proof. |
| `livecodebench` | **Blocked, S+L+P** — `row-attestation`, `smoke-scorer-comparability`: independent custodian approval of row/pool/split metadata, official wrapped-function scorer/source/runtime route. | Existing external-process smoke is not official wrapped-function execution; self-hashes do not authenticate row custody. |
| `musique` | **Blocked, S+L+P** — `joint-policy-comparability`: freeze labeled Answer/Support/local-joint metric, selected scope, source and denominator. | Historical 150/150 claim remains unverified externally; platform joint reward is not an official single leaderboard column. |
| `nestful` | **Excluded** — `retain-contract-refusal`; explicitly prohibited; released execution Win Rate not reproducible. | Do not substitute slot/sequence metrics or provision/run. |
| `physicsquestions` | **Blocked, S+L+P** — `dataset-journal-gap`. | Dataset-specific scorer/provenance/runtime/control review missing; no inferred pass. |
| `reasoning_gym` | **Blocked, S+L+P** — `dataset-journal-gap`. | Dataset-specific scorer/provenance/runtime/control review missing; no inferred pass. |
| `scienceworld` | **Blocked, S+L+P** — `prevent-platform-writes`: prevention source review is closed; independently verify live effective protected mounts and immutable platform provenance. | V4 stays incomplete, `effect=null`, writer unknown; diagnostic-only mean cannot become a valid effect. No unsandboxed substitute. |
| `sotuqa` | **Excluded** — `retain-contract-refusal`; explicitly prohibited; headline judge metric unavailable. | EM/F1 substitution is not permitted. |
| `sportsunderstanding` | **Blocked, S+L+P** — `dataset-journal-gap`. | Dataset-specific scorer/provenance/runtime/control review missing; no inferred pass. |
| `spreadsheetbench` | **Blocked, S+L+P** — `dataset-journal-gap`. | Dataset-specific scorer/provenance/runtime/control review missing; no inferred pass. |
| `strategyqa` | **Blocked, S+L+P** — `dataset-journal-gap`. | Dataset-specific scorer/provenance/runtime/control review missing; no inferred pass. |
| `tau2_bench` | **Excluded** — `retain-contract-refusal`; explicitly prohibited; independent user/judge assertions unavailable. | Do not supply required user actions from the actor or provision/run. |
| `tau_bench` | **Blocked, S+L+P** — `local-state-lifecycle`: selected service reset, database state and evaluator secrecy need independent current control/runtime evidence. | Local pool loadability proves no lifecycle or benchmark equivalence. |
| `terminal_bench` | **Blocked, S+L+P** — `cached-runtime-admission`: Q1/Q2/T1/S1/O1/C1 and the D1 production writer; exact per-task dependency/runtime/export gates, paired quota and official invocation remain. | Current six cached-image scope is historical, not an authenticated eligible pool; a standalone scorer preflight supplies no execution receipt. |
| `triviaqa` | **Blocked, S+L+P** — `hub-export-scorer-linkage`: independently pinned Hub export/loader/scorer/license/config/split, Domain/VerifiedEval selection and duplicate/question identity rules; preserve v2. | Resolve aggregation/missing-prediction denominator for chosen metric; full question/document grouping, F1 and upstream leaderboard equivalence need separate evidence. Old scorer identities are immutable. |
| `twowikimultihopqa` | **Blocked, S+L+P** — `ujson-native-offline-closure`, `hub-data-provenance`: pinned wheel/license/install-origin and Python/native closure; authenticated release/Hub/split/manifest/alias-artifact custody, rights and evaluator-version mapping. | `recovery-comparability`: review original/recovery mixed Answer F1/Joint F1, 48 scored tasks/two invalids separately. Preserve original null effect; no need to complete/reuse that old run before a new diagnostic. |

Taxonomy remains `demand × surface`, with `exercises` separately preserved for
every row in JSON. The four excluded declarations still count toward 28; Matrix
is also prohibited but is not one of these 28 source declarations.

## Can either GPU start a justified task now?

| Endpoint | Justified model diagnostic / pilot start at reviewed HEAD | Evidence limit |
| --- | --- | --- |
| GPU0 — `http://127.0.0.1:8001/v1` | **No** | No admitted dataset/current receipt path. Physical availability, service/model health, utilization and global leases were not inspected. |
| GPU1 — `http://127.0.0.1:8002/v1` | **No** | Same gates; moving the endpoint closes none. Physical availability and current concurrency remain unknown. |

This task authorizes metadata/source work only. Neither a necessary production
no-model control nor a GPU workload is justified by these packets; synthetic
metadata checks require no GPU and cannot be scheduled as benchmark utilization.
The justified next work is source integration of trusted observation/lifecycle/
scorer-export receipt production, independent quota capability evidence and
provenance handoffs. These are missing capabilities/evidence, not launch commands
or authorization to mutate the host. Do not fill idle capacity with duplicates.

## Validation and handoff

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_dataset_blockers.py`: exit 0,
  valid, **28 datasets / 8 shared blockers / 11 historical records**,
  `production_authorized=false`.
- Existing guarded source-only registry suite: **52 passed**, exit 0; no skips.
  Command: `env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/hg-codex-234/.scratch/task234-readiness python3 -B -m pytest -q -p no:cacheprovider --basetemp=/tmp/harnessgrad-pytest-task234-readiness-pytest tests/quality/test_dataset_blockers.py`.
  Its guards refuse adapters, external reads, sockets and subprocesses. No scorer
  differential or dataset/runtime suite was run for this metadata-only task.
- Companion JSON/report checks verify 28 exact unique rows, 24 blocked/4 excluded,
  23 complete shared-reference sets, separate AgentDojo route, closed obsolete
  source gates, current v2 identity, unchanged history, input pins, local links and
  the driver lifecycle gap. The validation receipt records actual results.
- Only task-234 documentation/metadata is delivered. Registry, production code,
  acquired fixtures, historical receipts and shared journal remain unchanged.
  Parent review/merge and shared-journal update remain separate.

See [validation receipt](task-234-readiness-validation.txt) for the captured
checks. Local scratch cleanup is test-file housekeeping only, not backend cleanup
or a diagnostic lifecycle receipt.
