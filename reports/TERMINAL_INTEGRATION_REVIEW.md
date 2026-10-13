# Terminal artifact admission integration review — Codex 161

**Finding: `eval/artifact_admission.py` is an offline contract library. The
production Terminal-Bench driver/runner/verifier path does not enforce it.**

Reviewed `main` and this isolated worktree at
`10e983fc5fcb006c5afdbce1ef851dad71e953f2` on 2026-10-14. The reviewed production
files match that revision of `main`. This report is the only committed change.
Production integration remains blocked; synthetic success grants no H0 admission.

## Observed production path

| Boundary | Source evidence at the reviewed revision | Actual behavior |
| --- | --- | --- |
| Staged driver policy | `driver.py:368`, `driver.py:382` | Checks supplied diagnostic/pilot context and passing gate status. Does not invoke the artifact library. Other sampling policies do not enter this staged branch. |
| Dataset loading | `driver.py:436`, `driver.py:491`, `driver.py:496`; `data/registry.py:85` | Imports the adapter and loads tasks, setup/verifier tables and environment declarations. |
| Terminal declarations | `data/terminal_bench.py:185`, `data/terminal_bench.py:232`, `data/terminal_bench.py:282` | Declares `kind=exec`, `state=container`, an image tag and the task network. The verifier runs `bash /tests/test.sh` with checkout `tests/` copied in. No artifact contract bytes, independent contract pin, sealed scorer bundle or bounded state allowlist is provided. |
| Image preflight | `driver.py:767`; `harnessgrad/environments.py:62` | Resolves task/service image digests. A pinned task image does not pin an independent scorer closure or pristine grader runtime. |
| H0 and task dispatch | `driver.py:1062`; `eval/runner.py:877`, `eval/runner.py:150` | Calls `evaluate`, then `run_one`, then `_run_one_container_state` for Terminal's environment. There is no artifact admission call before dispatch. |
| State transfer | `eval/container_state.py:190`, `eval/container_state.py:191` | Stops the actor container and commits its complete filesystem to a snapshot. Does not call `export_state` or verify a data-only projection. |
| Verification | `eval/container_state.py:213`; `eval/verifier.py:271`, `eval/verifier.py:276`, `eval/verifier.py:278`, `eval/verifier.py:293` | Creates the grader from the actor snapshot, inherits the task's internal network, copies verifier inputs, starts the container and executes the declared command. There is no closure check or created-runtime inspection gate before start. |
| Runtime and cleanup | `eval/container.py:758`, `eval/container.py:882`; `eval/container_state.py:244` | `create` supplies CPU/memory/PID flags but no read-only root or hard byte/inode quota contract. Snapshot admission is byte-capacity preflight (`preflight_only=true`, `quota_enforced=false`). Teardown removes owned objects in `finally`, without an artifact-bound cleanup/absence receipt. |

Source searches for `artifact_admission`, `harnessgrad.artifact-scorer.v1`,
`require_artifact_runtime`, `verify_scorer_closure` and `export_state` across
`driver.py`, `eval/`, `harnessgrad/` and `tools/` found only library definitions and
internal calls in `eval/artifact_admission.py`. The synthetic suite imports that
library directly; it does not establish production enforcement.

`eval/pilot_admission.py:153` separately reports missing dependency closure,
trusted runtime and state export evidence unconditionally. Its scope is the cached
synthetic control boundary, not the driver path. Its blocker list therefore does
not prevent the production driver from using the snapshot verifier.
`harnessgrad/trusted_runner.py:394` accepts an injected runner and invokes it; the
offline facade does not supply the missing Terminal adapter or admission wiring.

## Exact integration blockers

The immediate blocker is an absent trusted Terminal artifact adapter: no current
production input supplies the pinned declaration, local closure, bounded state
projection and pristine runtime observation required by the library. Calling the
library with the existing verifier/environment tables cannot satisfy its API or
its trust boundary.

| Required input/enforcement | Missing production implementation |
| --- | --- |
| Independently pinned task/source/scorer declaration | A platform-owned per-task metadata source must supply contract bytes and an independently trusted SHA-256, bind task/source/image identity to the selected run and persist that provenance. Neither caller gate booleans nor a digest computed from caller-supplied bytes establishes the trusted pin. |
| Verified local offline closure | `verify_scorer_closure` (`eval/artifact_admission.py:177`) needs an exact local bundle with pinned runtime/scorer/dependency files and a closed dependency graph. Terminal supplies only an unsealed `tests/` path. The library explicitly requires independent evidence of official scorer completeness and runtime ABI compatibility; declared file hashes alone cannot establish either. |
| Bounded data-only state projection | `export_state` (`eval/artifact_admission.py:212`) needs a quiesced local source, explicit file allowlist, byte/inode bounds and an exclusive platform-owned destination. Terminal state is inside a stopped container; no trusted bounded container-to-projection backend exists on this path. Whole-image commit and best-effort trace/answer copying do not implement this contract. |
| Pristine created scorer runtime | `require_artifact_runtime` (`eval/artifact_admission.py:326`) requires the pinned pristine image, sealed runtime/entrypoint command, exact environment, `network=none`, read-only root, only read-only `/control-input` and `/control-scorer` binds, and bounded tmpfs writes. The snapshot-based grader, inherited network and writable verdict bind conflict with that contract. `container.create` also starts from `sleep infinity`; this is not the contract's scorer entrypoint. A separate trusted creation/inspection/start boundary is necessary. |
| Effective limits and lifecycle evidence | The artifact runtime checker does not establish CPU/memory/PID ownership limits or cleanup by itself. Production needs fresh backend observations, actor filesystem byte/inode enforcement, bounded export/snapshot work, run/trial binding and verified owned-object absence. Cooperative reservations and snapshot capacity checks do not close these gaps. |

There is also a loader-order blocker for a payload-free preflight:
`data/terminal_bench.py:282` initializes its tables using `_all()` at import;
`_load_one` reads `task.toml`, `instruction.md` and the Dockerfile before the
driver's side/task selection. `HG_TB_TASKS` can narrow `_all()`, but the driver does
not establish that filter from its selected side/tasks before importing the
adapter. Importing this module to obtain preflight metadata would already read
payloads. A separate metadata-only selection/provenance source is needed before
`datasets.load_split` and before model/provider/runtime work.

## Integration decision

Use the requested report fallback. No production preflight was wired because the
current adapter lacks every artifact input and the runtime path is structurally
incompatible. An optional offline check would leave the production route
unenforced; accepting synthetic receipts or asserted gate booleans would falsely
admit it. Replacing the loader and grader backend requires independently acquired
task-specific evidence and work outside this payload-free review.

The concrete admission boundary to implement later is a mandatory metadata-only
Terminal check before dataset import, backed by platform-pinned selected-task
contracts and local closure checks. Actual grader admission additionally requires
the bounded projection and freshly inspected pristine runtime immediately before
start, with failures recorded as blocked/unmeasured rather than zero scores.
Direct `run_one` dispatch and cached evaluation results must enforce the same
binding so driver-only checks cannot be omitted by other callers. These are
integration requirements, not a claim that the current code implements them.

## Validation and limits

Executed only the existing synthetic artifact contract suite:

```text
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q \
  -p no:cacheprovider \
  --basetemp=/tmp/hg-codex-161/.terminal-integration-pytest-codex161 \
  tests/quality/test_terminal_artifact_admission.py
52 passed in 0.21s
```

The suite refuses `subprocess.run`, `subprocess.Popen` and socket construction.
Its fixtures contain only authored synthetic metadata/data. It verifies sealed
local closure, bounded export, receipt checking and supplied runtime observations;
it includes rejection of snapshot images, networked/writable runtime observations
and missing byte/inode limits. This confirms the offline contract's tested
behavior, not an official scorer run or production admission.

No Docker command, download, model call, H0, heldout access or benchmark task
payload read was performed. The Terminal adapter was read as source, never
imported. Historical task counts and dependency-install behavior described in
source comments were not independently verified. No measured benchmark score or
production cleanup receipt was produced. Test temporary files were confined to
this worktree and removed after validation.
