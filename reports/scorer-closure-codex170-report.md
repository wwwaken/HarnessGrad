# Generic scorer closure and isolation audit — Codex 170

Generic production scoring does **not** enforce complete offline dependency closure,
an independently identified trusted scorer runtime, artifact-only state export, or
official scorer invocation. Image pinning and verifier input rematerialization are
useful existing controls, but they do not close these four gates.

This change adds a reusable, task-independent content-addressed scorer bundle
manifest and local closure validator. It shares the existing artifact validator's
implementation. It does not change production execution or authorize any H0 run.

## Scope and evidence

- Worktree: `/tmp/hg-codex-170`, detached HEAD; base commit
  `10e983fc5fcb006c5afdbce1ef851dad71e953f2`.
- Inspected source code only. No provisioned dataset, heldout, archive or benchmark
  payload reads; no dataset imports, model/H0, Docker, downloads or network requests.
- Executed only synthetic local-file tests. Tests refuse subprocess execution and
  socket creation. All temporary test files stay under this worktree.
- Findings below are source observations. Runtime isolation, upstream equivalence
  and successful official scoring remain unmeasured. Historical comments claiming
  that all Terminal-Bench test scripts install packages were not independently
  verified against task payloads in this audit.
- The primary integration journal remains for the reviewing parent to update after
  its diff review and merge. No main-branch changes were made.

## Enforcement observed

| Gate | Production enforcement | Source evidence and remaining boundary |
| --- | --- | --- |
| Pinned offline dependencies | **Absent generically.** Native checks use the host toolchain. Exec checks use image contents. No generic transitive dependency lock or local bundle validation is called before scoring. | `eval/sandbox.py:180` exposes host runtime directories/interpreter read-only; `eval/verifier.py:540` selects the environment or optional verifier image. GAIA's Dockerfile installs unversioned apt/pip packages; AppWorld pins its primary package but has `uvicorn<1` and no full transitive hash lock. Those build declarations do not establish offline closure. |
| Network closure | **Absent generically.** Exec checks inherit a service/task network; native verifier sandbox calls omit network isolation. | `eval/verifier.py:545`; `eval/verifier.py:565`; `eval/sandbox.py:198` implements `--unshare-net` only when passed `network="none"`. `eval/container_state.py:214` selects the task network when present. An internal task network is not a dedicated network-none scorer boundary. Unsandboxed native scoring remains a supported branch at `eval/verifier.py:571`. |
| Scorer image identity | **Partial.** Dataset/service images resolve to local content addresses before run startup; stateless exec `run()` rejects unpinned images. There is no independent bundle-to-observed-scorer-image binding. | `driver.py:767`; `harnessgrad/environments.py:57`; `eval/container.py:306`; `eval/container.py:598`. `_resolve_envs` resolves environment/service specs, not separate verifier specs. An optional `spec.image` must already be pinned to pass `run()`. Container-state scoring instead uses the actor-produced snapshot at `eval/verifier.py:271`; its identity does not establish pristine trusted scorer provenance. Native checks have no equivalent immutable runtime identity. |
| Separate artifact export | **Absent in production.** Stateless exec mounts the complete actor task tree read-only; native checks rematerialize trusted inputs in the same task tree; container-state checks inherit the full snapshot. | `eval/verifier.py:489`; `eval/verifier.py:540`; `eval/container_state.py:191`. Fresh exec/snapshot verdict directories prevent reuse of actor reward files, but separate verdict storage is not artifact-only input export. |
| Trusted verifier isolation | **Partial.** Rematerialized check inputs, minimized explicitly supplied environments, fresh exec processes/containers and read-only stateless task mounts exist. Container-state checks still inherit actor filesystem/toolchain state. | `eval/verifier.py:31`; `eval/verifier.py:44`; `eval/verifier.py:394`; `eval/container.py:585`. `eval/container.py:758` creates snapshot runtimes without the pristine runtime contract's read-only root, sealed scorer command or dedicated scorer mounts. No observed lifecycle binding to the closure/export receipts exists. |
| Official scorer invocation | **Adapter-specific; absent as a generic admission requirement.** The verifier registry accepts a command and input paths, with no official-source/entrypoint identity requirement. | `data/registry.py:643`. GAIA calls `question_scorer` at `data/gaia/verify/check.py:99`; Reasoning Gym calls `score_answer` at `data/reasoning_gym.py:115`; AppWorld calls `world.evaluate()` at `data/appworld/verify/check.py:56`. SpreadsheetBench explicitly transcribes its evaluator. QA contracts invoke each local adapter's scoring function. None of these source observations prove fresh official execution here. |

The existing `eval/artifact_admission.py` already validates caller-pinned task
contracts, exact local file closures, bounded data-only exports, and a supplied
pristine runtime observation. `require_artifact_runtime` checks image ID, command,
environment, network-none, read-only mounts and hard tmpfs byte/inode limits. It
explicitly does not launch a scorer. A call-site search in `eval`, `data` and
`tools` found no production integration of these export/runtime gates. The new
bundle validator also remains an explicit library/CLI capability, not an automatic
runner admission gate.

## Implementation

`eval/scorer_bundle.py` defines `harnessgrad.scorer-bundle.v1` with exactly:

- `schema`, `source_sha256`, a bare `runtime_image_id` (`sha256:` plus 64 lowercase
  hex digits), `network` (only `none`), and `scorer`.
- `scorer`: `entrypoint`, ordered `argv`, and `files`.
- Each file: canonical relative `path`, SHA-256, byte length, `role`
  (`scorer`, `runtime`, `dependency`), and an explicit `requires` list.

The command must name a declared runtime under `/control-scorer/` and then the
declared scorer entrypoint under that same mount. All graph edges must resolve
locally; every file must be reachable from the entrypoint. The validator checks
the exact tree inventory, sizes and hashes, rejects symlinks/hardlinks/special
files, and detects observable file changes during reads. It never discovers imports,
installs packages, inspects images or executes the declared command.

APIs:

- `seal_bundle(manifest)` validates and emits deterministic JSON bytes plus their
  SHA-256. JSON object key order is canonical; list order remains significant.
- `load_bundle(raw, expected_sha256)` verifies an externally supplied manifest pin
  and rejects malformed declarations and duplicate JSON object keys.
- `verify_bundle(root, raw, expected_sha256)` checks local declared bytes and emits
  `harnessgrad.scorer-bundle-receipt.v1` with scope
  `local_declared_closure_integrity`. `declared_network` describes the manifest,
  not an observed runtime. It returns no task score or admission status.
- `require_contract_bundle(contract_raw, contract_sha256, bundle_raw,
  bundle_sha256)` requires a separately pinned legacy task contract to match the
  bundle's source, runtime and scorer declarations. Different tasks retain separate
  export/quota contracts while sharing one bundle identity.
- `python3 -m eval.scorer_bundle --root <local-bundle-directory> --manifest
  <local-manifest-file> --sha256 <trusted-manifest-pin>` prints the scoped receipt.
  Invalid admission returns exit 2 and a sanitized JSON failure, without printing
  manifest/scorer data. It performs no scorer execution.

`eval/artifact_admission.py` now shares `validate_scorer_spec` and
`verify_scorer_files` with the new module. Its existing task contract schema and
receipt format stay compatible; existing export/runtime controls use the same file
validation implementation.

The caller must protect the pin independently of actor state, establish source
provenance, keep the bundle platform-owned and quiesced through execution, and
bind real observations to its receipt. Hashing a declared graph cannot show that
undeclared imports, shared libraries, data assets or image ABI dependencies are
absent. Neither a source hash nor the declared entrypoint proves official origin.

## Precise unresolved cross-adapter gates

| Execution family | Required closure before a valid diagnostic |
| --- | --- |
| Native/files, including shared QA and package scorers | Inventory a selected-only scorer projection and a trusted runtime including required packages/data/shared libraries. Pin their bytes independently of the host Python environment. Supply an explicit network-none verifier policy. Export only the bounded prediction/action/data allowlist to a separate platform destination; place trusted scorer code and gold in separate trusted projections. Observe and bind namespace, command, limits and lifecycle to the exact manifest. |
| Stateless exec, including GAIA and spreadsheet/code checks | Materialize the offline bundle and record the actual pristine scorer image ID/ABI. Require the verifier override image to resolve separately from the actor image. Mount only the verified data export and trusted scorer inputs, with a dedicated network-none boundary. Validate the created runtime against both bundle and task contract immediately before invocation. |
| Container-state, including Terminal-Bench | Stop and establish actor quiescence, export declared task artifacts, then use a pristine scorer runtime instead of the actor snapshot's runtime/toolchain. Resolve task-specific verifier dependencies offline; the current network/install behavior cannot be treated as closed. Existing snapshot cleanup is still needed for retained historical artifacts, but cannot substitute for trusted scorer isolation. |
| Service-backed checks, including AppWorld-style replay | Pin trusted replay/evaluator code and all required state/data/runtime assets. Export a bounded selected action log or data projection, rather than inheriting the actor/service filesystem or shared network. Establish a separate trusted replay topology with explicit local-only connectivity where services are required; an adapter needing service connectivity cannot satisfy the current single-container network-none contract without additional topology evidence. |
| Every official scorer | Independently establish source revision/content provenance and the exact official entrypoint/metric/protocol. Produce a real offline invocation receipt bound to manifest, actual runtime, task/export identity, timeout/resource budgets and cleanup. Keep failures, unmeasured tasks and invalid receipts separate from measured zero scores. Synthetic integrity controls do not prove scorer equivalence or permit a pilot. |

These gates need adapter-specific evidence and execution integration. No generic
boolean such as `offline_verified` or `official_verified` can replace them.

The existing pristine artifact runtime contract accepts exactly two read-only
projections: `/control-input` and `/control-scorer`. Reusing one code bundle across
tasks that need private gold/reference data also requires an explicit separately
pinned trusted-input projection and mount contract, or a task-specific trusted
closure. The new reusable bundle does not implicitly add or admit such a mount.

## Validation and review

Command (pytest scratch must be outside the platform because driver-based tests
use `tmp_path` as a harness work root):

```bash
mkdir -p .scratch/scorer-bundle-codex170
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  TMPDIR=/tmp/hg-codex-170/.scratch/scorer-bundle-codex170 \
  python3 -m pytest -q \
  tests/quality/test_scorer_bundle_codex170.py \
  tests/quality/test_terminal_artifact_admission.py \
  --basetemp=/tmp/harnessgrad-pytest-scorer-bundle-codex170-pytest \
  -o cache_dir=.scratch/scorer-bundle-codex170/pytest-cache
```

Result: exit 0, **84 passed in 0.24s**. No skips, dataset scoring or measured
benchmark result. Coverage includes deterministic identity, external pin mismatch,
graph closure, unsupported declarations, duplicate JSON keys, malformed shapes,
exact local bytes/inventory, link rejection, multiple task bindings, contract
mismatches, scoped CLI receipts, and existing export/quota/runtime regressions.
`git diff --check` passed. Reviewed the extraction diff and new files for unrelated
changes. Broader benchmark/scorer suites were not run because this scope excludes
dataset/runtime access.

Delivery: the accompanying detached-worktree commit contains the validator,
shared-core extraction, unique synthetic test file, this report and the local
HTML overview. Parent review and merge remain separate.
