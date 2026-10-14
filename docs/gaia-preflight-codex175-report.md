# GAIA source-safe dry preflight — Codex 175

**Production admission remains blocked.** A metadata-only review can close source
identity, declaration comparison and refusal-boundary checks. It cannot establish
selected-only dataset access, an enforced runtime, an official measured score,
snapshot lifecycle or verified cleanup. The new CLI has no execution path and
returns exit **2** for every review, including matching source/runtime identities.

## Scope and observed evidence

Work was confined to the detached worktree `/tmp/hg-codex-175`, based on main's
commit `e7acaa1126c4c63c8ddc338bd9a7f4988f43ffdf`, tree
`4d06f74e9c86d273327e549adb59ed45a6378baa`. Main's existing
`eval.gaia_snapshot_attestation.collect_source` collected 796 committed entries;
its canonical source identity is
`815a0ad7d16507ec3ce6d9cdfa62c7d5d2ce99abc74591ed18449a0e0fc4cebd`.
That collection describes the base commit, not this delivery's eventual candidate
or a historical run checkout.

Only repository source, documentation, Git metadata and authored synthetic tests
were inspected. No provisioned dataset, parquet, pool header/row, attachment,
heldout payload, token, model configuration/artifact or H0 receipt was opened.
No Docker, model, H0, network, download, image build or benchmark control ran.
No tasks were selected or executed; real eligible/selected/task/trial coverage
and invalid/unmeasured task counts were not observed. This report is not a
diagnostic or pilot receipt. There is no model/endpoint binding to claim.

The journal's V2/V3 and earlier lifecycle entries are historical claims and
external evidence pointers, not validated receipts. The referenced
`GAIA_LIFECYCLE_WIRING.md` is absent from this checkout. Its claims were not
adopted as current observations; the findings below come from the current code.

## Gate reassessment

| Gate | What source/metadata can close | What remains before execution |
| --- | --- | --- |
| Dry-review privacy boundary | **Closed for this CLI:** no task, adapter-data, receipt-file or arbitrary file-path input; no execution dispatch. Fresh-import and entrypoint guards passed. | This says nothing about the production adapter's reads. |
| Frozen source identity and compatibility | **Available:** complete Git tree modes/OIDs, full commit/tree identity, clean candidate HEAD check, every changed path and conservative runtime change classification. | Hold the candidate fixed from before adapter import through sealing; independently pin ignored/external inputs. The collector holds no lock. |
| Release/split/scorer declarations | **Source declaration established:** validation revision, expected 165 rows, pool/parquet/scorer hashes; wrapper invokes official `question_scorer`, and placeholder gold is unmeasured. | Independently authenticate release/scorer custody and actual selected bytes. Declared hashes and row counts are not observations of provisioned data or actual eligible tasks. |
| Eligible/selected identity and counts | **Can close with authenticated metadata only:** custodian-supplied ID-only inventory, split rule, counts and preselected manifest hash, tied to the pinned release/pool. No such evidence was supplied or validated here. | Selected task/attachment materialization and proof that no other row/gold/annotator solution was read require a selected-only reader and controls. |
| Runtime identity schema/comparison | **Available conditionally:** strict inline `gaia-runtime.v1` bindings can be compared without inspecting their external objects. Default invocation makes no runtime comparison. | Actual images, dependency closure, selection and policies need independent custody/observations. Equal arbitrary valid hashes cannot close provenance or enforcement. |
| Runner refusal | **Closed as a refusal boundary:** the real hook blocks GAIA's exec/container/network/resource/deadline fields; early dispatch and cached-success regressions pass. | A trusted observer and reviewed production admission integration are absent. Caller declarations, offline passing contracts and cached success cannot override it. |
| Web/network/resource enforcement | Source shows `services` network and web search/fetch declarations, CPU/memory and deadlines. | Fresh backend observations of cgroups/swap/PIDs/deadlines, actor gateway topology/policy and verifier isolation. Shared `admit_runtime` accepts only `network=none`, so it cannot admit GAIA's actor topology as written. |
| Byte/inode quotas | Source identifies the gap; snapshot preflight explicitly reports `quota_enforced=false`. | Supported OS/daemon storage backend with paired hard limits and complete writable-surface coverage, including snapshot/export/evidence writes. Free-space checks/reservations are insufficient. |
| Trusted verifier and offline closure | Source shows fresh reward storage and re-copied verifier inputs; the task-independent scorer bundle validator is available. | Pristine separately pinned verifier, sealed official scorer/dependencies/selected gold, network-none enforcement and fresh offline execution. Current container-state verifier uses the actor snapshot/toolchain and actor network. |
| Artifact-only export | The existing artifact library describes bounded data export and trusted-runtime checks; it is not wired into GAIA's scoring path. | Export only approved answer data into a platform-owned sealed projection, then score in the pristine verifier. Re-copying check inputs into an actor snapshot is insufficient. |
| Snapshot lifecycle | Source ordering is stop → capacity check/commit → immutable snapshot ID → verifier; snapshot failures are invalid/no-score. | Real stopped/exit/OOM observations, bounded worker/deadline, byte/inode headroom/device observations and successful snapshot identity. Synthetic calls are not lifecycle evidence. |
| Owned cleanup | Source shows removal attempts in teardown. | Complete exact-owned inventory and independently verified object/namespace absence; quarantine unresolved ownership. Best-effort removal does not prove absence. |
| Official oracle/noop and receipt review | Source declares released-answer oracle and official metric; error/placeholder behavior is inspectable. | Fresh selected controls, measured oracle=1/noop=0, invalid/unmeasured handling, sealed coherent identities and independent receipt review. No existing result was reused. |

Task capability remains `demand × surface`; harness `exercises` remain a separate
axis. This review creates no flattened dataset category or coverage claims.

## Exact source findings that prevent a backend-free closure

`data.gaia.__getattr__` builds all ENV/SPLIT/SETUP/VERIFY entries through `rows()`;
`load()` and `_row_for()` also use the full pool. GAIA has no selected-only
`control_task` hook. `data.command_control.pick` calls `load()` even with an
explicit task ID. Its platform arm also uses a fixed `<dataset>-control` run ID
and defaults a missing verdict to zero for its exit decision. Therefore neither
`--task-id` nor a successful noop exit establishes selected-only measured control.

`data/gaia/prepare.py` reads both validation and test parquets; parquet filenames
containing “metadata” do not make their question/gold/annotator contents safe
preflight inputs. `prepare.py --check` hashes the entire pool and reads its header.
Existing official-scorer tests can open those external files and execute controls;
they were excluded from this validation.

`eval.container_state` passes the actor snapshot and network to
`eval.verifier._verify_container_state`, which creates the verifier from that
snapshot. Fresh reward/evidence storage prevents stale reward reuse, but does not
replace an actor-controlled interpreter/dependency tree with a trusted one.
The Dockerfile uses a mutable base and unversioned apt/pip packages; its source
cannot establish a complete immutable scorer ABI/dependency closure.

`eval.runner._refuse_unobserved_policies` has no positive observation override.
`run_one` calls it before harness-manifest/storage access; `_evaluate` calls it
before cache lookup. Direct backend/verifier calls remain outside that boundary,
and driver image checks can occur earlier. The CLI calls only the refusal helper,
never `driver`, the control loader, `run_one`, `_evaluate`, or a verifier.

## Delivered CLI and its limits

From a **clean committed checkout**, use full commit hashes:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B -m eval.gaia_preflight \
  --reference-commit e7acaa1126c4c63c8ddc338bd9a7f4988f43ffdf \
  --candidate-commit <full-candidate-HEAD>
```

The JSON report preserves both complete collected source manifests, canonical
source hashes, changed paths, review-only exclusions, source compatibility,
`checkout_lock=not-held`, `ignored_inputs=not-inspected`, the real runner refusal
receipt and remaining gates. Source comparison without runtime bindings is
explicitly `source_compatible_only`; runtime compatibility is `not-performed`.

Optional `--reference-runtime` and `--candidate-runtime` must both supply inline
JSON with exactly the existing compatibility tool's runtime schema. No JSON file,
stdin, `@file`, arbitrary repo, task/selection, receipt path, backend, output path
or execution option is accepted. Bindings reject duplicate keys, nonfinite values,
oversize/malformed JSON, mutable image tags, missing fields and non-validation
splits. Their provenance is always `caller-declared-not-authenticated`.

The required runtime identity fields are:

- `schema`, `dataset_revision`, `split=validation`;
- SHA-256 fields `pool_sha256`, `split_sha256`, `selection_sha256`,
  `scorer_sha256`, `harness_sha256`, `dependencies_sha256`, `web_policy_sha256`,
  `export_contract_sha256`, `quota_policy_sha256`;
- exact `image_id` and `verifier_image_id` (`sha256:<64 hex>`);
- positive integer `container_plan`, `snapshot_max_bytes`, `snapshot_reserve_bytes`;
- `limits` with positive integer `cpus`, `memory_mb`, `pids`.

These fields identify supplied declarations; they neither collect enforcement
observations nor authenticate external evidence. The fixed GAIA policy probe
contains only field names/kinds and `None` limit values, with an authored dummy
task identifier. It never resolves GAIA task attributes. A source-AST regression
checks that the projection matches GAIA's current declaration presence.

Every review returns exit 2 and `execution_status=blocked`, `measured=false`,
`production_authorized=false`, `lifecycle_authorized=false`,
`evidence_reusable=false`, `receipt_validation=not-performed`, with no score.
Even an all-matching compatibility attestation retains these flags. Metadata
errors and a missing/changed refusal hook return sanitized failure JSON without
echoing argument values or traceback contents. `--help` only prints usage.

No existing runtime source/hook was edited and no compatibility exemption was
added. The new CLI, tests and this report are conservatively runtime-affecting
paths under the existing tool; earlier evidence requires comparison against the
final candidate and fresh controls rather than automatic reuse.

## External prerequisites, in closure order

1. **Trusted metadata custody:** an independently authenticated validation-only
   inventory/selection record for `gaia-benchmark/GAIA` revision
   `682dd723ee1e1697e00360edccf2366dc8418dd9`, with pool/source/split/selected hashes,
   eligible/selected counts and approved IDs. Do not supply question/gold/annotator
   payloads to this preflight. Establish attachment digests and exclusion custody
   through the data owner. The declared 165 rows are not an observed eligible count.
2. **Selected-only materialization:** a reviewed indexed/selected reader and control
   interface that refuses before any nonselected reads, pins selected row and
   attachment bytes, excludes annotator solution data, and keeps gold outside
   agent setup. Changing the shared picker alone does not fix GAIA's lazy full-pool
   SETUP/VERIFY/ENV/SPLIT construction or `oracle_files` lookup.
3. **Source/runtime custody and lock:** hold one clean candidate before adapter
   import through sealing; pin ignored/external inputs, effective policies,
   no-model harness and independent actor/verifier image IDs. Existing metadata
   collection supplies no coherent execution lock or historical checkout proof.
4. **Official offline scorer closure:** independently establish the reviewed
   scorer bytes/revision provenance (declared leaderboard revision
   `9f133d71362ecb0a1c7ff6b4dcfc2a6b9f8ffd1e`, scorer SHA-256
   `0d44c07f3046eec521697c22e3eaca8719cc81e422a8eaf32695c5f22bdac6e2`).
   The adapter's download URL uses `resolve/main`; that URL does not authenticate
   the claimed revision. Supply a complete sealed interpreter/package/native ABI
   closure including numpy and selected trusted gold. The reusable bundle's
   two-mount artifact contract needs an explicit trusted-gold projection contract
   or a coherent task-specific trusted closure; no mount is implicitly admitted.
5. **Pristine verifier/export integration:** implement an answer-only bounded,
   data-only export to independent platform storage and a pristine verifier that
   consumes that sealed export plus trusted scorer/gold. Validate real image,
   command, environment, read-only mounts and `network=none` before official
   invocation. Do not inherit actor snapshot execution state.
6. **Supported enforced backend and trusted observers:** establish the actual
   Docker/containerd snapshotter and backing filesystem; provide complete paired
   hard byte/inode scopes for actor writable storage, scratch/mounts and
   snapshot/export/log/evidence destinations. Observe effective CPU/memory/swap,
   PID/deadline and storage enforcement before staging/writes. Add a reviewed
   actor `services`/web topology policy and observer, because the current shared
   runtime contract supports only network-none. Independently isolate the scorer.
   Then wire trusted observations into production admission without allowing
   adapter/caller evidence to bypass the existing refusal boundary. Merely
   supplying a valid offline contract cannot unblock it.
7. **Measured lifecycle/cleanup controls:** with finite limits and fresh ownership
   IDs, observe actor stop/exit/OOM state, writable bytes/inodes, free/reserve
   bytes/inodes, device identity, snapshot-worker limits/deadline and immutable
   successful snapshot identity. Verify exact owned actors/verifiers/gateways,
   networks, volumes, snapshot images/tags and workspaces absent in all relevant
   namespaces. Retain/quarantine ownership on ambiguity, including commit timeout
   before a returned image ID. Current removal helpers cannot generate this proof.
8. **Fresh selected oracle/noop receipts and separate review:** implement a receipt
   path that preserves invalid/unmeasured classifications, uses fresh run IDs and
   records independently measured oracle=1/noop=0 under the real official scorer.
   Seal metric identity, eligible/selected/task/trial coverage, invalid/unmeasured
   counts, source/split/manifest/model/harness hashes, limits/budgets, endpoint
   binding (explicitly N/A for no-model controls), lifecycle/cleanup and
   comparability. Preserve historical/incomplete receipts. Only after all gates
   close can a separately authorized one-task/one-trial, jobs=1 diagnostic be
   considered. Expansion requires a separate review of its valid measured
   receipt; temporary reruns use `min(30, ceil(10% * eligible))`, trials=1, jobs=1.

These are evidence and implementation prerequisites, not commands to run an
unadmitted backend or bypass the refusal. Nothing in this delivery authorizes
the controls, a diagnostic, a pilot or H0.

## Validation and delivery

```bash
mkdir -p .pytest_cache/gaia-codex175
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  TMPDIR=/tmp/hg-codex-175/.pytest_cache/gaia-codex175 \
  python3 -m pytest -q \
  tests/quality/test_gaia_preflight_codex175.py \
  tests/quality/test_gaia_snapshot_attestation.py \
  tests/quality/test_shared_admission_wiring_codex163.py \
  --basetemp=/tmp/harnessgrad-pytest-codex175-gaia-codex175-pytest -p no:cacheprovider
```

**155 passed in 0.60s**, exit 0, no skips. The new tests use authored source/runtime
identities and guards against payload readers, Docker, model/network/backend,
host disk inspection and execution/scoring entrypoints. A fresh guarded Python
subprocess checks module-import side effects; the existing suites supply only
synthetic Git/backend observations. Test scratch remains inside this worktree.
These are regression results, not real dataset or backend evidence.

Parent review/merge remains separate. Main, driver, runner, adapter, snapshot and
verifier implementation files were left unchanged. The existing source comparison
will flag this delivery's added files as requiring fresh measured controls.
