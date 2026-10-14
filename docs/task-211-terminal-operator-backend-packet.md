# Terminal admission: operator and backend handoff — Task 211

Scope: this packet covers Terminal admission under the
[optional strict formal-deployment profile](filesystem-quota-backends.md#scope-optional-formal-deployment-enhancement).
Project quotas and dedicated volumes are not prerequisites for ordinary local
execution. The requirements below apply to claiming the profile's enforced bounds
and admitting its gated diagnostics; this clarification changes no runtime gate
or evidence requirement.

**Disposition: BLOCKED / documented requirements.** Host provisioning, paired
quota enforcement, trusted observations, Terminal scorer closure/export and
production lifecycle integration remain open. This packet supplies no runtime
receipt, benchmark score or diagnostic authorization. All acceptance items below
are pending unless a later, independently reviewed receipt proves them.

Prepared in `/tmp/hg-codex-211` against revision
`65b0f2a5bf95fdafd218ca54198843c27b9fffbe`. Scope is documentation and repository
source review only: no host changes or live configuration inspection, mounts,
Docker/container execution, model/H0 calls, task payloads or benchmark runs.

## Evidence basis and limits

| Input | Supported conclusion | Evidence boundary |
| --- | --- | --- |
| [Quota source audit, Codex 168](../reports/filesystem-quota-codex168-report.md) | No complete connected paired byte/inode quota backend was found at its audited revision. | Source-only historical finding; no claim that the current host has or lacks quota support. Its 252 passing tests were synthetic, not enforcement evidence. |
| [Operator/backend requirements, Codex 191](filesystem-quota-backends.md) and [proposed sidecar schema](filesystem-quota-evidence.schema.json) | Defines provisioning, allocation, observation, snapshot and cleanup acceptance requirements. | Documentation/schema only; no implemented observer or semantic validator. |
| [Historical host storage note](moving-docker-data-root.md) | Reports `overlayfs` with `io.containerd.snapshotter.v1` on 2026-10-06; Docker metadata and containerd image storage occupy different roots. | Old observation, not fresh host/quota evidence. The first move attempt was incomplete; this packet does not adopt or execute its migration procedure. |
| [Terminal admission report](../reports/report.md) and [current library](../eval/pilot_admission.py) | Cooperative reservations and synthetic runtime/ownership refusals exist; `benchmark_blockers` retains three gates per inherited task plus quota and official-execution blockers. | The report's 199 tests and six cached-image claims are historical. No task/image availability or dependency behavior was reverified here. |
| [Scorer audit](../reports/scorer-closure-codex170-report.md) and [current facade contract](scorer-admission-contract.md) | Declared bundle integrity, export and supplied runtime facts can be checked separately. | No proof of complete dependencies, official origin, production invocation or observer authenticity. Claims that task scripts fetch packages remain inherited and unverified. |
| [Staged receipt audit](../reports/staged-receipt-audit-codex193-report.md) and [driver writer](../driver.py) | The current staged writer supplies unknown cleanup/snapshot and omits lifecycle evidence. | Source observation reconfirmed for this packet; the driver cannot presently produce a valid measured diagnostic through that path. |

Fresh host facts are **unknown**: filesystem features/enforcement, current daemon
and snapshotter identity, effective limits, scorer readiness and cleanup. Do not
convert the absence of evidence into an observed failure or a passing declaration.
The [review record](task-211-terminal-operator-backend-review.md) pins consulted
repository files and records documentation validation separately.

## Owners, dependencies and required return package

| Gate | Owner | Required return evidence | Stop condition |
| --- | --- | --- | --- |
| Q1 — quota filesystem | Host operator | Approved provisioning/change receipt; fresh filesystem/kernel/mount identities and paired enforcement readback. | Unsupported or unknown block/inode enforcement. |
| Q2 — bounded allocation | Backend implementer | Durable intent/lease, independent scopes, paired limit/assignment observations before staging; complete writer inventory. | Any first write before enforcement, uncovered surface or shared/reused allocation. |
| T1 — containerd storage design | Backend/runtime implementer | Actual storage topology, supported read-only-root or reviewed writable-root design, bounded daemon/content/temp/export growth and worker resources. | Unknown snapshotter support, unbounded storage or incompatible admission contract. |
| S1 — scorer closure/export | Scorer custodian + backend | Independently pinned official source, offline runtime/dependencies, selected artifact contract and quiesced export; pristine runtime observation. | Missing dependency, input semantics, source custody, trusted runtime or export evidence. |
| O1 — observations/integration | Observer + runner implementers | Protected fresh records, digest resolution and semantic validation; launch gates before host preparation and actor/scorer writes. | Supplied booleans, replayed observations or unwired production path. |
| C1 — cleanup | Lifecycle/backend owner | Exact absence and quota-lifetime receipts, ownership reconciliation, atomic release or retained quarantine. | Partial/unknown cleanup; keep reservations and IDs held. |
| D1 — staged diagnostic | Independent runtime reviewer | All prerequisite evidence, actual official invocation, full lifecycle and one-task/one-trial receipt; separate expansion review. | Any gate open, invalid/unmeasured result or missing receipt linkage. |

Q1 precedes project allocation; Q2, T1, S1 and O1 must all close before a Terminal
diagnostic. C1 needs a reviewed recovery path before launch and actual completion
evidence afterward. Return immutable metadata, externally stored digests, owner and
review identities, unresolved items and comparability notes together. No gate is
closed by this packet, by a capacity ledger or by a synthetic control.

## Quota filesystem and writable inventory for the strict profile

For this profile's disk-backed writers, use independently owned **XFS or ext4
project-quota storage with both block and inode hard-limit enforcement**. Dedicated
tmpfs scopes need both effective byte and inode limits. A filesystem name, large
free capacity, shared user quota, relocated data root or storage-size option alone
is insufficient.
XFS and ext4 are alternatives. A dedicated volume is optional; existing storage
needs the same verified backend support and evidence to qualify for this profile.

| Storage | Operator prerequisite | Backend acceptance evidence |
| --- | --- | --- |
| XFS project quotas | Supported kernel and mount with project quotas (`prjquota` / `pquota`); verify accounting and both hard-limit dimensions. | Unique project ID, inheritance and complete descendant assignment; exact kernel limit readback on the same filesystem; bounded allocation parent. |
| ext4 project quotas | Supported kernel/filesystem with `quota` and `project` features, project metadata and enabled enforcement (`prjquota`). | Same ownership, assignment, exact readback and lifecycle requirements, using ext4-supported interfaces; no assumed XFS tool/driver compatibility. |
| Dedicated tmpfs | Supported namespace/provisioner applying positive `size` and `nr_inodes` before use. | Final consumer mount identity and actual limits; allocation granularity, remount prevention and complete lifetime cleanup. Bare tmpfs is insufficient. |

Freeze positive limits before allocation. Bytes mean **allocated storage**, with
recorded quota/allocation units; apparent file lengths and logical export bytes
are separate quantities. Require
`hard_blocks * quota_unit_bytes == effective.bytes == requested.bytes` and
`hard_inodes == effective.inodes == requested.inodes`. Reject ceilings that cannot
be represented exactly; do not silently round upward. Account for directories,
metadata, sparse files, shared extents and snapshot behavior as supported by the
actual backend. Logical export checks do not enforce filesystem allocation.

Persist ownership intent first. Initialize each empty scope under an already
bounded parent, apply hard limits and inheritance before data staging, then verify
the full assignment and final namespace before the first consumer write. Prevent
project reassignment, remounts and writes outside the observed scopes. A separate
mount/device requires its own independently enforced scope. Resolve aliases by
actual filesystem/project/generation; renamed scope IDs do not create isolation.

The writable inventory must cover **every phase and writer**, including host
preparation, actor, method, scorer, daemon/snapshot helper, export and receipt writer:

- Task/setup/output, workspace, `.git`, base/method copies and trajectories.
- Staging, extraction, caches, verdicts, logs, exports and protected evidence.
- HOME/TMPDIR, `/tmp`, `.state`, hidden trees, namespace scaffolding, `/dev/shm`,
  volumes and additional mounts; disable unused writable surfaces.
- Daemon content/snapshots, unpack/copy temporary space and all destination scopes.

Allocate protected, bounded failure-evidence capacity before starting any writer.
Required integration includes `driver.py` before workspace initialization,
`ckpt/git_state.py` before staging/materialization, method workspace copies and
`eval/runner.py` before setup/scratch/verifier writes. Admission only at actor
start leaves earlier host writes uncovered. These are pending integration work.

## Containerd snapshotter limits and execution design

Establish fresh daemon ID/version/config digest, Docker storage mode/driver,
snapshotter name, containerd namespace/root and actual content/snapshot/upper
filesystem identities. Record immutable image/container/snapshot identities and
their lease ownership. Deduplicate free capacity by device across Docker,
containerd, workspace and evidence paths. Historical root sizes prove no ceiling.

| Design or observation | Acceptance boundary |
| --- | --- |
| Classic `overlay2` with `storage-opt size` | Depends on suitable XFS project quotas; the size option supplies no independent inode hard-limit proof. It cannot be assumed to work for containerd snapshotters or ext4. |
| Writable containerd snapshot upper | Requires supported snapshotter-aware per-run allocation, paired effective readback and driver-coordinated project ownership before create/copy/start. Unknown support remains blocked. Do not retag a live driver-owned upper. |
| Read-only root with bounded mounts | Compatible direction for current `admit_runtime`, provided all writable mounts are independently bounded and state is transferred through a reviewed artifact contract. Terminal's existing container-state semantics are not automatically compatible. |
| Writable-root admission | Current `eval.runner_admission.admit_runtime` refuses it even if storage evidence is valid. Requires a separately reviewed contract and production implementation change. |
| Shared content store or daemon pool | Free space/reservations are insufficient. Require enforceable run ownership and paired growth bounds for relevant writes, or keep this design blocked. |
| Docker commit | Excludes bind/tmpfs data and cannot establish artifact-only scorer inputs. Actor snapshots cannot supply the trusted scorer shell/toolchain. Retained snapshots still require bounds and cleanup. |

Current runner admission also supports only `network=none`. Any actor access to a
live local model endpoint needs a separately reviewed relay/topology contract and
trusted observations; the existing contract grants no connectivity exception.
The scorer remains independently isolated with network none.

Bound daemon/content, destination snapshot, unpack/copy temporary space, logging
and export separately; document actual scope mappings and charge shared extents
without inventing independent capacity. Actor cgroups do not constrain daemon
writes. Freeze CPU, memory, swap, PID, wall-time and teardown bounds for each
helper/daemon phase and collect actual resource observations.

Before snapshot/export, quiesce **all** writers and record exit/OOM/timeout state.
Preflight both bytes and inodes on the actual destination device, with concurrent
reservations and enforced destination/temp growth ceilings. No generic copy-size
multiplier proves peak usage. Preserve separate immutable preflight and completion
records, operation outcome, final artifact identity and allocated byte/inode usage.
Legacy snapshot admission remains `preflight_only=true`, `quota_enforced=false`.
Unknown size, failed operation or missing completion/cleanup evidence prevents a
valid measurement. Artifact export also needs completion evidence under the
current lifecycle contract; it cannot silently mark snapshot evidence unnecessary.

## Terminal scorer closure and artifact-only export

For each later selected task, the scorer custodian must establish official source
revision/content custody, exact entrypoint, metric/protocol and required state
semantics. No task payload or task-specific contract is supplied here. The inherited
six-task scope is not a newly approved eligible pool. Its three gates per task
(dependency closure, trusted runtime, export contract) and unconditional quota and
official-execution blockers remain in the admission library; setting declaration
booleans true cannot remove them.

Required scorer return package:

- Independently pinned bundle and task-contract bytes, official source/metric
  evidence, immutable pristine image identity, full runtime/ABI, interpreter,
  packages, shared libraries and data dependency inventory with hashes. A closed
  declared dependency graph proves local declared integrity, not completeness.
- Offline availability for every required dependency and asset. Dedicated observed
  `network=none`, no attachments and no install/fetch fallback during scoring;
  source-custody preparation is distinct from runtime execution.
- Exact selected artifact allowlist, per-file and aggregate logical byte limits,
  inode accounting including directories, and paired allocation bounds on source,
  destination and temporary export scopes. Export only quiesced declared data to a
  fresh platform-owned destination; reject links, special files, executable state,
  unexpected projected files and observed source mutation under the existing
  contract. Read only declared source paths; do not inventory the actor tree to
  discover exports.
- Separate trusted scorer inputs and protected gold/reference custody. Current
  pristine runtime accepts read-only `/control-input` and `/control-scorer` only;
  any additional trusted-input projection requires an explicit reviewed contract
  or a task-specific trusted closure. Never add a mount by declaration alone.
- Fresh pristine scorer observation with `State.Status="created"` and
  `State.Running=false`; an exited/stopped runtime is not accepted. Bind exact
  command, image, environment allowlist, read-only root/mounts, network and bounded
  scratch/output; separate CPU/memory/swap/PID/deadline and ownership evidence.
  Keep checked bytes and runtime boundaries unchanged through invocation.
- Actual official scorer invocation receipt with run/trial/task, independent pins,
  export digest, runtime identity, metric, exit/OOM/timeout, resources and cleanup.
  Process exit alone is not a score; missing or malformed reports stay unmeasured.

Recheck bundle bytes, export inventory/content and supplied runtime facts with
`eval.scorer_admission` immediately before use. Pins must remain outside actor
state. The facade does not launch the scorer, establish official provenance,
discover dependencies or authenticate observations. If a selected task's state
cannot be represented by the current bounded data-only contract, block that task
pending a reviewed semantic extension; do not substitute the actor snapshot or
claim equivalent official scoring without evidence.

## Observer fields, trust and contract projections

The [quota sidecar specification](filesystem-quota-backends.md) and its
[closed schema](filesystem-quota-evidence.schema.json) remain authoritative for
exact shapes. This packet adds collection requirements, not fields to those
closed objects. Required envelope fields are:

| Field group | Required fields / collection meaning |
| --- | --- |
| Identity | `schema`, `kind`, fresh `record_id`; `binding` with `adapter_id`, `run_id`, `trial_id`, `manifest_sha256`. |
| Provenance | `source_revision`, `source_sha256`, `split_sha256`, `harness_sha256`, `policy_sha256`, `ownership_intent_sha256`, `model_sha256`, `endpoint_binding`, `model_bound`. Model/endpoint are null only for a frozen model-free lifecycle. |
| Observer | `observer_id`, `implementation_sha256`, `boot_id`, UTC `observed_at`, monotonic positive `sequence`, `privilege_boundary_sha256`, `raw_observation_sha256`. Collector is independent of actor output. |
| Phase | `lifecycle.phase`, `allocation_generation`, positive `deadline_ms`; provisioning/allocation/prestage/prestart/snapshot_preflight/snapshot_complete/cleanup as appropriate. |
| Result | `result.status` = verified/blocked/unknown; `result.reason=null` for verified, otherwise a fixed schema reason code. `measured=false`, `production_authorized=false`; matching kind-specific `facts`, nullable only as specified for unavailable/refused collection. |

Collect all seven kinds at their required boundaries: `host_provisioning`,
`project_scope`, `tmpfs_scope`, `writable_inventory`, `docker_storage`, `snapshot`
and `cleanup`. Kind-specific facts include kernel enforcement/raw units,
project/inheritance/descendant scans, requested/effective/usage values, final
writer/mount inventory, actual storage topology, quiescence, operation completion
and owned absence. Record filesystem type/UUID/device, mount ID/namespace/root,
mount point and root inode, bound to boot and allocation generation.

Keep auxiliary containerd namespace/root and scorer/invocation metadata in a
separately pinned protected inventory referenced by the existing evidence chain;
do not inject extra keys into the closed quota or admission records. Such metadata
has no automatically implemented consumer or validation in this packet.

Protect immutable records/raw metadata and resolve every referenced digest to
verified bytes. Check trust, strict sequence progression, same boot/filesystem,
exact limit arithmetic, complete writer coverage and matching intent/generation.
Reobserve after reboot, remount, namespace rebuild or identity/policy change.
Hashes alone prove neither freshness nor authenticity. Use metadata allowlists;
exclude task text, answers, logs, environment contents and credentials.

Quota sidecars are capped at 64 KiB; existing admission receipts at 16 KiB. Fail on
overflow; do not truncate. Apply schema format checks and the specified semantic
checks separately; the semantic validator remains unimplemented. Project verified
surface facts into existing runtime observations as
`{bytes, inodes, backend, scope_id, evidence_sha256}`; retain extra backend evidence
outside the closed API. Current runner cleanup handles five object kinds; the
sidecar's project/tmpfs/reservation checks are additional obligations before release.
Quota record and diagnostic/review digests use their respective documented
canonicalization functions; they are not interchangeable serialization rules.

## Cleanup, crash recovery and lease decision

Persist generation-bound ownership intent before every allocation, including
failed/timeout creates, snapshots, exports, temporary scopes and reservations.
Reconcile interrupted intents and discover objects only in the bound owned
namespace. Verify exact identity/ownership before removal; unrelated objects are
untouched. An unrecorded owned object prevents release until reconciled.

After stopping writers, require finite-deadline removal, detached mount aliases,
closed handles and independent exact absence observations. Include namespace
queries for **all eight** sidecar kinds: container, network, snapshot, volume,
workspace, project_scope, tmpfs_scope and reservation, even when none were planned.
Successful removal or an empty path is insufficient; query errors remain unknown.
Record reservation/lease release eligibility, then atomically apply release and
confirm the final reservation namespace; retained active reservations cannot be
reported absent. The reservation/cleanup transaction is pending backend work.

| Scope | Evidence required before reuse/release |
| --- | --- |
| Project quota | Exact original project/filesystem/generation, no descendants, writers, mounts, open-unlinked objects or pending deletion; kernel usage zero bytes and zero inodes. |
| tmpfs | Original mount/superblock lifetime destroyed with all namespace/bind aliases and references gone. Unqueryable destroyed-mount counters may be null with independent destruction evidence; never invent zeros. |
| Containers/snapshots/volumes/exports/workspaces | Exact owned identities absent and complete owned namespace empty, including interrupted allocations; retained historical objects stay explicitly owned/quarantined. |
| Ledger and reservations | Apply release atomically only after every mandatory cleanup check passes; otherwise quarantine and retain capacity and quota IDs. |

Recovery appends fresh observations without overwriting old/incomplete records.
Timeout, daemon/query failure or uncertain counters retain quarantine; age cannot
convert uncertainty to success. A later successful cleanup cannot repair an
invalid or unmeasured diagnostic.

## Staged diagnostic receipt and review gate

This is a **future receipt checklist**, not a launch plan or fabricated receipt.
Current state: no run ID, selected task, metric, endpoint, measured result or
runtime receipt has been allocated by Task 211. All dataset gates, selected-only
privacy/provenance, supported quota/runtime/scorer integration and cleanup recovery
must pass first. Storage support alone does not authorize H0.

The backend/runner must first fix the evidenced writer gap:
`driver.py:save_policy_receipt` supplies unknown cleanup/snapshot and no lifecycle.
No operator declaration or externally edited JSON can turn that into observed
evidence. Review production integration and the trusted writer before execution.

For a later authorized diagnostic, freeze a nonempty eligible ID pool and its
digest, then select exactly one task by the existing deterministic ID-only rule
before task execution. Use a fresh run ID and **one task, one trial, jobs=1,
rounds=0**. Bind one endpoint for the entire run, either
`http://127.0.0.1:8001/v1` or `http://127.0.0.1:8002/v1`; independently enforce total
H0 concurrency `<=3`. Use no method tuning or paid endpoint. No such run is
authorized or performed by this packet.

| Receipt section | Required eventual contents |
| --- | --- |
| Schema and scope | `harnessgrad.diagnostic-receipt.v2`, fresh `run_id`, `stage=diagnostic`, `trials=1`, `jobs=1`, exact `selected_task_ids`, `eligible_task_ids_sha256`; record `rounds=0` in the frozen plan. |
| Context | `dataset`, `side`, official `metric.name` and `metric.scorer_sha256`; source/split/manifest/model/harness hashes in `context.hashes`; exact endpoint; `limits.resource`, `limits.budget`; gate status/hash/detail and comparability notes. Pins must identify actual bytes used. |
| Limits and budget evidence | Per-phase CPU/memory/swap/PID/deadline/teardown, allocated byte/inode ceilings and snapshot/export maxima/reserves; model request/token/time caps, global concurrency lease, protected evidence allowance and actual usage. Numeric policy maps alone are not enforcement receipts. |
| Coverage | Eligible/selected tasks and expected trials; measured/invalid/unmeasured counts for both tasks and trials. Every selected trial appears explicitly. No eligible count or task IDs are asserted by this packet. |
| Outcomes and score | Each selected task has `trial=1`, status, explicit score and reason. Invalid/unmeasured rows have `score=null` and a reason; measured rows require a finite official metric and `reason=null`. Real measured zero is allowed only after successful measurement evidence. |
| Cleanup and snapshot | Distinct summary status/hash/detail referencing actual completion/absence evidence, not preflight or removal commands. Failed/unknown status prevents a valid measured diagnostic. |
| Lifecycle | Complete scope-bound `harnessgrad.lifecycle-receipt.v1` replay: scope → admit → execute → quiesce → score → seal → cleanup; bind outcomes, snapshot completion/worker/preflight and cleanup hashes. `publication_ready` does not imply production authorization. |
| Comparability | Dataset release/split and metric protocol, exact harness/model and selected scope; quota/storage/scorer/runtime differences, historical omissions and invalid/unmeasured denominators. Do not compare infrastructure failures as zero scores. |

Use both the JSON Schema and Python semantic/replay validation, with protected
eligible metadata and referenced records available to the reviewer. JSON shape
alone cannot authenticate observers, recompute selection or authorize expansion.
Preserve the pre-execution plan, incomplete outcomes, operation failures and
cleanup/recovery records under the original immutable run ID; never resume or
overwrite it, even for a retry.

Expansion requires a **separate approved review bound to the exact valid measured
diagnostic receipt**, matching the current eligible pool, context/pins, endpoint
and enforced limits. Require one measured trial, zero invalid and zero unmeasured,
passed gates/cleanup/snapshot and complete verified lifecycle. Reviewer identity
and authority need independent custody; a review string/hash does not prove them.
Only then may a fresh temporary rerun select
`min(30, ceil(10% * eligible))` tasks before execution, with `trials=1`, `jobs=1`.
The historical 50-task/three-trial protocol is not the fallback. If any prerequisite
is unknown, return the blocked packet with preserved evidence and open owners.
