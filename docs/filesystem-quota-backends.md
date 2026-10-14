# Filesystem quota operator and backend implementation checklist

## Status, ownership and completion boundary

**Status: documented blocker. This change completes documentation only.** Host
provisioning, quota allocation, effective-kernel observers, Docker storage bounds,
production runner integration and verified cleanup remain external/runtime work.
No checklist item below is marked complete by this document or its schema.

For a concise administrator handoff separating read-only inspection, approved
maintenance and post-change verification, use the
[safe administrator checklist](task-222-quota-administrator-checklist.md).

The historical source audit at revision
`10e983fc5fcb006c5afdbce1ef851dad71e953f2` found no complete, connected byte-and-inode
backend for native bwrap/files tasks, Docker exec or harness/method workspaces.
Its evidence is retained in the appendix; it is not a current host capability
report. This conversion also checks the source contract in
[runner admission](runner-admission-contract.md): it validates supplied facts,
does not install quotas, and requires a read-only actor root. A supported writable
Docker upper layer would still need a separately reviewed admission extension.

| Owner | Deliverable | Completion evidence required later |
| --- | --- | --- |
| Host operator (external) | Supported kernel/filesystem, project-quota metadata and enabled enforcement; bounded allocator parent | Fresh `host_provisioning` records and operator change receipt |
| Backend implementer (pending code + runtime) | Allocator, ownership ledger, namespace observer, daemon/snapshotter integration and cleanup | Reviewed code, synthetic refusal tests, then separately authorized finite runtime validation |
| Runner/lifecycle implementer (pending code) | Gate every writer before preparation/start, checkpoint and lease-release integration | Reviewed call-site changes and lifecycle receipts bound to backend evidence |
| Runtime reviewer (external validation) | Confirm actual applied limits, coverage, snapshot bounds and absence | Trusted immutable records; synthetic tests and configuration declarations are insufficient |

The [JSON Schema](filesystem-quota-evidence.schema.json) is a **proposed metadata
sidecar format**, not a detector, allocator, runtime receipt or new production API.
It is not consumed by existing runners. Shape validation cannot establish trusted
observations or grant production authorization. No mounts, quota operations, host
configuration inspection, Docker/model/H0 execution or task-payload reads are
part of this documentation change.

## Operator and implementation checklist

Each unchecked item is an acceptance requirement for later work. Stop at a missing
prerequisite; persist blocked/unknown evidence and retain ownership. Host changes
need their own authorized provisioning procedure; no administration commands are
prescribed or executed here.

### 1. Inventory and frozen policy — backend + runtime reviewer

- [ ] Freeze fresh run/trial/manifest identities, source/split/model/harness hashes,
  the quota policy, allowed paths, per-phase resources/deadlines and ownership
  intent. The enclosing diagnostic/pilot receipt also needs metric identity,
  eligible/selected/task/trial coverage, invalid/unmeasured counts, endpoint binding
  and comparability notes; this quota sidecar does not replace it.
- [ ] Inventory actual writable surfaces for **every writer and phase**: host
  preparation, actor, verifier, method, snapshot/daemon, export and evidence writer.
  Cover task/setup/output, workspace and `.git`, base copies, method workspaces,
  trajectories, staging/extraction, verdicts, caches, logs, evidence, `/tmp`, HOME,
  TMPDIR, `.state`, hidden-tree/root scaffolding, shared memory, device filesystems,
  image volumes and additional mounts. Disable unused surfaces or bound them.
- [ ] Allocate independently owned scopes with both positive limits. A mount on a
  different filesystem needs its own verified scope. Shared user quotas, a shared
  daemon pool or aliases to one project do not provide independent per-run bounds.
  Inventory aliases even if read-only; the current runner contract requires
  distinct scope IDs for each writable surface and cannot admit shared aliases.
- [ ] State byte units as **allocated storage**, with quota blocks or tmpfs allocation
  granularity, and inode units as backend-accounted inodes/slots, including overhead.
  Apparent sparse-file lengths and exported logical bytes need separate policies.
  Reflinks/shared extents and snapshot copies need backend-specific accounting.
- [ ] Reserve bounded space for immutable metadata/failure evidence before starting
  a writer; quota exhaustion must not silently erase its failure/cleanup receipt.

### 2. XFS project quotas — external operator, then backend implementer

- [ ] Operator: provision a kernel with XFS quota support and an XFS backing mount
  with project quotas enabled (`prjquota` / `pquota`). Verify **accounting and block
  and inode hard-limit enforcement**, not only the filesystem name or mount flags.
  Supply kernel release, filesystem UUID/device, mount and namespace identities,
  effective options, supported quota interface and administrative change ID.
- [ ] Operator: bound the allocator's parent/control storage. An empty scope root
  must be created under an already bounded parent; administrative initialization
  must not leave an unbounded staging window.
- [ ] Backend: persist intent/lease before allocation; create a fresh unique project
  on that filesystem; configure paired hard limits on the reserved ID before
  assigning the project ID and inheritance flag to its root.
  Verify all existing descendants, ownership and nested mounts before data writes.
  Observe assignment via filesystem inode ioctls and limits/enforcement via the
  supported kernel quota interface. A registry file alone is insufficient.
- [ ] Backend: set positive **block hard** and **inode hard** limits, then independently
  read them back. Record the API's quota-unit size and raw hard values. Require
  `hard_blocks * quota_unit_bytes == effective.bytes == requested.bytes` and
  `hard_inodes == effective.inodes == requested.inodes`. Reject unrepresentable
  policies rather than rounding up or silently changing a frozen ceiling.
- [ ] Backend: prevent project reassignment, quota override, mount replacement and
  writes outside the owned scope by every relevant actor/host writer. Reobserve
  identity/limits after namespace construction and before the first data write.
- [ ] Reviewer: require verified `host_provisioning`, `project_scope` and
  `writable_inventory` records. Configuration or a supplied `enforced=true` does
  not satisfy this gate.

### 3. ext4 project quotas — external operator, then backend implementer

- [ ] Operator: provision a kernel/filesystem combination supporting ext4 project
  quotas, with `quota` and `project` features, project quota metadata and enabled
  enforcement (`prjquota`). Confirm both block and inode hard-limit support on the
  actual combination. Feature names or filesystem type alone are insufficient.
- [ ] Operator: record verified metadata/features, kernel release, UUID/device,
  effective mount identity/options, accounting/enforcement state and change ID.
  Filesystem preparation, feature activation and mount changes are external work.
- [ ] Backend: satisfy **all** XFS allocator/ownership/inheritance, readback, exact
  conversion, bounded-parent, override prevention and cleanup requirements using
  ext4's supported interfaces. Do not assume XFS tools, quota units or Docker
  `overlay2` size support transfer to ext4.
- [ ] Reviewer: require the same three record kinds, identifying `ext4` explicitly;
  reject disabled metadata/enforcement, read permission failures, shared projects,
  mismatched descendants and missing dimensions.

### 4. tmpfs byte/inode bounds — backend + namespace observer

- [ ] Trusted provisioner: create dedicated tmpfs scopes with explicit positive
  `size=<bytes>` **and** `nr_inodes=<count>` before scratch use. Either bind already
  bounded storage into bwrap or prove the pinned bwrap/kernel integration supports
  both applied limits. Bare `--tmpfs` and a byte-only option leave the gate open.
- [ ] Observer: inspect the final consumer mount namespace, filesystem/mount identity
  and effective kernel byte/inode limits; requested Docker/bwrap options alone are
  insufficient. Record allocation-unit size and effective options. Refuse page/block
  rounding that makes effective limits differ from the frozen policy.
- [ ] Cover `/tmp`, `.state`, HOME/TMPDIR, hidden-tree tmpfs, writable namespace
  scaffolding, verifier output, `/dev/shm` and image volumes wherever present.
  Host binds require project quotas or deliberately bounded tmpfs allocations too.
- [ ] Ensure the actor cannot remount, replace or enlarge the scope. Keep memory,
  swap, CPU, PID and time limits independently enforced: tmpfs size is an allocation
  bound, not a memory-resource contract or an apparent-file-length cap. Inode/slot
  accounting can include directories and extended attributes, not just file count.
- [ ] Reviewer: require `tmpfs_scope` plus final `writable_inventory`; lifetime starts
  before staging and ends only after writers, mounts and references are gone.

### 5. Workspace, staging and host writes — allocator + runner implementer

- [ ] Gate `driver.py` before workspace initialization; `ckpt/git_state.py` before
  staging/copy/extraction/materialization; method loops before base/workspace copies;
  `eval/runner.py` before task setup, scratch, HOME/TMPDIR and verifier output writes.
  These are required integration points, not implemented changes.
- [ ] Route all destinations, Git objects/worktrees, archives, temporary copy trees,
  trajectories, cache fills, logs and export/evidence writes to allocated scopes.
  Apply limits to the host preparation processes as well as the later actor.
- [ ] Before any preparation/data write, persist the frozen policy and trusted
  allocation evidence. `first_write_at` means first staging/data write; bounded
  empty-root initialization is recorded by the allocator before `activated_at`.
  Existing scaffolding must already be accounted for under the new project.
- [ ] Keep project/mount identities and lease ownership across checkpoints, crashes
  and interrupted allocation. Never reuse an old run ID or overwrite incomplete
  evidence. Restored/changed namespaces need fresh observations before writes.
- [ ] Fail closed on unsupported storage, observation errors, stale evidence,
  missing limits or incomplete writable coverage; no score or H0 authorization.

### 6. Docker writable layers, snapshot storage and export — external runtime work

- [ ] Observer: establish the **actual** daemon identity/version, classic driver or
  containerd snapshotter, backing filesystem/mounts, writable upper directory,
  volumes and mount inventory. The [historical storage note](moving-docker-data-root.md)
  is not fresh evidence. Unknown driver/snapshotter combinations remain blocked.
- [ ] Choose and freeze a supported execution design. A writable upper layer needs
  a driver/snapshotter-aware allocator and trusted paired hard-limit readback **before
  create/copy/start**. Coordinate IDs with driver-owned projects; never retag a
  live upper directory independently of its lifecycle. Classic `overlay2`'s
  `storage-opt size` relies on suitable XFS project quotas and proves no independent
  inode hard limit; do not assume it applies to a containerd snapshotter.
- [ ] A read-only-root design instead needs independent paired bounds on every
  writable mount and explicit artifact-only state transfer. Docker commit excludes
  bind/tmpfs contents. This is a runtime/state-export redesign, not a quota flag.
- [ ] Writable upper roots remain unsupported by current `admit_runtime`, which
  insists on a read-only root. Backend evidence alone cannot change that contract.
  Review and implement the admission extension before that execution design.
- [ ] Allocate independently enforced daemon/content, destination snapshot, temporary
  unpack/copy, logs and export scopes. If shared content-addressed storage or a driver
  cannot enforce run ownership and paired growth bounds, block that design rather
  than presenting free capacity as per-run enforcement. Moving the data root is
  provisioning, not a quota backend. Bound daemon/helper resources and teardown
  deadlines separately; actor cgroups do not bound daemon snapshot writes.
- [ ] Quiesce **all** writers and observe stop/exit/OOM state. Take byte+inode
  preflight with concurrent-work reservations on the exact destination device,
  plus enforced destination/temporary growth bounds and snapshot-worker resources.
  No generic copy multiplier establishes peak storage. Existing snapshot preflight
  remains `preflight_only=true`, `quota_enforced=false`.
- [ ] Persist distinct preflight and completion records: operation exit/OOM/timeout,
  final immutable image/artifact identity, observed allocated bytes/inodes and owned
  resources. Failure, timeout, unknown size, missing cleanup or snapshot evidence
  stays invalid/unmeasured, never an ordinary zero score.

### 7. Cleanup, crash recovery and lease release — trusted backend

- [ ] Persist an allocation intent before every object/scope/reservation is created,
  including failed create attempts. Bind identity and allocation generation to the
  lease; verify ownership before removal. Inspect only the owned namespace.
- [ ] Stop writers, detach all mount aliases, close handles and remove owned objects
  within a finite deadline. A successful remove command is not an absence receipt.
  Observe exact owned IDs and full namespace absence, including unrecorded objects
  after interrupted allocation and all kinds even when no objects were planned.
- [ ] Project scopes: verify no descendants, pending deletions, open unlinked objects
  or remaining mounts/writers, and kernel project usage of **zero bytes and zero
  inodes** after removing the root. Keep the project ID/lease quarantined while
  counters or ownership are uncertain; do not recycle solely because a path is gone.
- [ ] Tmpfs scopes: prove destruction of the original mount/superblock lifetime,
  including namespace/bind aliases and references. The actor namespace disappearing
  alone is insufficient. Do not invent zero counters when a destroyed mount cannot
  be queried; record nullable counters with independent destruction evidence.
- [ ] Release quota IDs and reservations **atomically** only after verified cleanup
  and all mandatory absence checks. Timeouts, query errors or partial removal mean
  quarantine and retained reservations. Recovery repeats observations with a fresh
  sequence/record; age never converts uncertainty to success.

## Exact evidence schema and collection contract

[filesystem-quota-evidence.schema.json](filesystem-quota-evidence.schema.json)
uses JSON Schema Draft 2020-12. Every listed object field is required, objects are
closed (`additionalProperties=false`), and each record contains exactly one
`kind` with its matching `facts`. Only explicitly nullable fields admit `null`.
No task text, answers, logs, environment, credentials or arbitrary attachments are
allowed. Paths/identifiers are allowlisted metadata from trusted allocation plans,
not actor-supplied strings or task-derived filenames. Preserve only redacted,
metadata-only raw observations in protected storage; hashes reference those bytes.

### Envelope — required on every record

| Field | Exact meaning |
| --- | --- |
| `schema`, `kind`, `record_id` | Constant `harnessgrad.filesystem-quota-evidence.v1`; one of the seven kinds below; fresh immutable record ID |
| `binding` | Exactly `adapter_id`, `run_id`, `trial_id`, `manifest_sha256`; identical to the consuming lifecycle/runner binding |
| `provenance` | Exactly `source_revision`, `source_sha256`, `split_sha256`, `harness_sha256`, `policy_sha256`, `ownership_intent_sha256`, `model_sha256`, `endpoint_binding`, `model_bound`; model/endpoint are null iff the frozen lifecycle is model-free |
| `observer` | Exactly `observer_id`, `implementation_sha256`, `boot_id`, UTC `observed_at`, positive monotonic `sequence`, `privilege_boundary_sha256`, `raw_observation_sha256`; identifies the independent trusted collector and protected metadata observation |
| `lifecycle` | Exactly `phase`, `allocation_generation`, positive `deadline_ms`; phase is provisioning/allocation/prestage/prestart/snapshot_preflight/snapshot_complete/cleanup |
| `result` | Exactly `status` and `reason`; status verified/blocked/unknown; verified requires null reason, otherwise a fixed schema reason code |
| `measured`, `production_authorized` | Both always `false`; quota observations contain no scores and cannot authorize a pilot |
| `facts` | Matching closed object below, or null only for blocked/unknown collection; partial non-null facts still must satisfy the kind's shape |

Identifiers are nonempty printable ASCII tokens up to 256 bytes; bounded descriptive
text/paths use printable ASCII. Paths must additionally be canonical absolute paths
(no `//`, `.` or `..` components) under trusted owned roots. SHA-256 values are 64
lowercase hex digits; `source_revision` is the pinned 40-digit Git revision. Times
are valid UTC ISO-8601 with `Z`. Integer quantities exclude booleans and lie in
`[0, 2^63-1]`, with positive limits/deadlines; project IDs are `[1, 2^32-1]` and exit
codes signed 32-bit. Decode quantities as integers, rejecting float encodings
(such as `1.0`) even where JSON Schema treats them as integral numbers. Schema
format checks must be enabled. Arrays have explicit
bounds, including at most 32 surfaces and 64 ownership objects. A serialized sidecar
record is capped at 64 KiB; existing projected admission receipts retain their
16 KiB cap and must fail rather than truncate. The JSON Schema checks structure;
canonical paths, byte caps, identity uniqueness, trust and cross-field arithmetic
below require an additional backend semantic validator (not implemented here).

Digest input is also fixed: `policy_sha256` hashes the canonical frozen policy
JSON using the serialization below; `manifest_sha256` and `split_sha256` hash the
exact frozen manifest/split-metadata bytes. `source_sha256`, `harness_sha256` and
`model_sha256` hash exact immutable inventory-manifest bytes listing the respective
source, executable/runtime closure or model/tokenizer members and their digests.
`source_revision` must match that source inventory. Ownership-intent digests hash
exact append-only ledger checkpoint bytes for the allocation generation. Observer
implementation/privilege-boundary digests reference exact pinned implementation
inventory and trusted privilege-policy bytes. No inventory may include task text;
verify member hashes separately rather than treating the manifest hash as proof of
its claims. Record digests and raw-observation digests use the rules below.

### Kind-specific facts — exact field sets are in the schema

| Kind / collection point | Required evidence and interpretation |
| --- | --- |
| `host_provisioning` / provisioning | Operator change/administrator IDs, kernel release, filesystem identity, enabled features/effective mount options, verified project metadata, quota interface and accounting/block/inode enforcement flags. Must be XFS or ext4 for a verified project backend. This is external host work. |
| `project_scope` / allocation, prestage or prestart | Scope and lease IDs, filesystem, provisioning-record digest, project ID/inheritance, complete descendant assignment scan, requested/effective paired limits, usage, raw hard blocks/inodes and quota-unit bytes, enforcement flags, override protection, activation/first-write times. |
| `tmpfs_scope` / allocation, prestage or prestart | Scope and lease IDs, tmpfs filesystem/mount identity, requested/effective paired limits, usage/allocation unit, effective mount options, remount protection and activation/first-write times. |
| `writable_inventory` / prestage or prestart | Inventory ID, actor-root read-only fact, writer IDs, every surface's path/role/access/writer/mount/namespace/filesystem identity and enforcement reference, completeness/unmatched count, inventory lock and its evidence. Read-only surfaces have null scope/reference; writable surfaces require both. |
| `docker_storage` / prestage or prestart | Actual daemon/config/driver/snapshotter, immutable container/image IDs, chosen strategy, root/upper identity and enforcement reference, driver project-ID ownership digest, writable inventory, separate daemon/content/destination/temp/log/export scopes and daemon resource receipt. Classic mode has null snapshotter; artifact-only mode has null writable-upper fields. |
| `snapshot` / snapshot_preflight or snapshot_complete | Container/storage evidence, all-writer quiescence, maxima/reserves/deadline, byte+inode capacity/reservation lease, worker resource receipt, bounded destination, operation state/exit/OOM/timeout/times, final image/artifact/allocated size and ownership inventory digest. Preflight and completion are separate immutable records. |
| `cleanup` / cleanup | Lease/intent, exact generation-bound owned objects/removal/absence facts, namespace absence for all eight kinds, scope lifetime/usage/destruction observations, intent coverage and release/quarantine decision. Additional quota kinds extend sidecar evidence, not the existing cleanup API. |

`filesystem` identifies exactly `filesystem_type`, `filesystem_uuid`,
`device_major_minor`, `mount_id`, `mount_namespace_id`, `mount_root`, `mount_point`
and `root_inode`. Disk UUIDs are required for XFS/ext4 and null for tmpfs. Mount IDs
and inode numbers are meaningful only with namespace, filesystem, boot and
allocation-generation identities; neither a path nor an ID alone prevents reuse.

Every `requested`/`effective` pair is exactly `{bytes, inodes}`; usage is
`{allocated_bytes, inodes}`. Project scans record completeness, object/mismatch/
uncovered nested-mount counts and a digest. Scope references always resolve to a complete
verified project/tmpfs record, not to a requested option or admission declaration.
A `docker_storage` record describes the actual driver/mount topology; an unknown
combination emits blocked/unknown with a fixed reason instead of a fabricated ID.

Cleanup object and namespace kinds are exactly `container`, `network`, `snapshot`,
`volume`, `workspace`, `project_scope`, `tmpfs_scope`, `reservation`. Namespace rows
carry `remaining_ids`, `query_complete` and evidence digest, including empty kinds.
Objects carry `kind`, `id`, `allocation_generation`, `removal_state`, nullable
`absent` and evidence digest. Scope rows reference the original enforcement record
and retain writer/mount/handle/destruction state, nullable usage/descendant/deletion
facts and project-ID reuse decision. Missing queries remain null/unknown, not zero.

### Mandatory semantic checks — independent of schema validity

1. **Trust, immutability and freshness.** Persist frozen policy/intent first, then
   observer records in storage the actor cannot modify. Hash records using UTF-8
   `json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
   allow_nan=False)` without a trailing newline; record digests are external, never
   self-hashed fields. Hash raw metadata bytes exactly as stored. Resolve and verify
   every referenced digest, policy, source lock, ownership generation, lease and
   binding. Provisioning evidence must identify the same host/boot/filesystem as its
   scope. Track strictly increasing observer sequences per observer/boot/binding;
   time alone cannot prevent replay. Reject stale records after reboot, remount,
   reassignment, namespace rebuild, policy change or unlocked inventory. Reobserve
   changed phases; do not reuse one trial's observations for another trial.
2. **Limits and first write.** Both effective limits must exactly equal policy and
   be positive. Project records must satisfy the raw-block conversion above;
   tmpfs bytes must be exactly representable at the recorded allocation granularity.
   Require actual accounting and both enforcement flags, correct project/inheritance,
   complete zero-mismatch assignment scan and `uncovered_mount_count=0`. Actor
   override/remount flags must be false. Usage must fit the effective limits and
   include allocation overhead. Activation precedes the first staging/data write;
   null `first_write_at` means no such write yet, not an unknown timestamp.
3. **Complete writer coverage.** Inventory must be complete/locked with zero unmatched
   writable surfaces. Each writable path/writer/mount resolves to its observed
   enforced scope in the final namespace. Scope IDs and filesystem/project/generation tuples
   distinguish allocations; mount IDs may recur for different paths on one mount. Duplicate aliases/shared scopes cannot be promoted to distinct
   isolation by renaming IDs. Prevent new mounts or escaped paths after observation.
   `read_only_actor_root=false` blocks current runtime admission, even when the
   storage observation itself is valid. Non-Docker runs omit Docker/snapshot records;
   they still require inventory and cleanup of all allocated scopes.
4. **Snapshot phases.** Container/storage/ownership identities must match. Require
   `running=false`, `exit_code=0`, `oom_killed=false`, `active_writer_count=0` and
   no later writes. Preflight requires each writable count within its maximum,
   free capacity at least writable count plus reserve, and exclusive reservation
   covering that same requirement after concurrent commitments. Destination and
   temporary scopes must enforce paired growth ceilings independently of these
   counts. Limits/deadline and worker/daemon resource receipts must match policy.
   Preflight operation is `not_started` with all operation outcome fields null.
   Completion requires `succeeded`, zero exit, no OOM/timeout, non-null ordered
   start/end times within deadline, immutable image/artifact identity and non-null
   byte/inode observations within policy and destination limits. Any failed/unknown
   operation remains blocked/unmeasured; preflight alone is never completion.
5. **Cleanup release.** Cover every planned and discovered generation-bound identity,
   including interrupted intents; no duplicates/replacements. All eight namespaces
   must be present once, queried completely, with empty remaining IDs. All objects
   must have proven absence; already absent objects may be `not_attempted` only with
   fresh trusted absence evidence. All scopes require gone writers, detached mounts,
   closed handles and verified destruction. Project scopes additionally require
   zero kernel bytes/inodes, zero descendants, no pending deletion and reusable ID.
   Destroyed tmpfs counters may be null, but destruction must prove the original
   lifetime gone and `project_id_reusable=false`. `lease_action=release` is permitted
   only for a verified record satisfying every check and intent coverage. Verified
   cleanup requests release; blocked/unknown cleanup requests quarantine. Apply release atomically in the ledger only after this verification.
6. **Refusal and persistence.** Missing queries, unsupported backend, malformed or
   stale identities, missing dimensions, representability/inventory/resource gaps,
   timeout, snapshot failure or incomplete cleanup produce blocked/unknown with a
   fixed reason and retain leases/reservations. Preserve valid partial metadata and
   prior records; successful later cleanup cannot repair an invalid measurement.
   Malformed untrusted data are not echoed into refusal receipts.

These checks describe required backend behavior. No semantic validator or observer
implementation is supplied by this documentation change.

## Integration with current contracts and validation handoff

- [ ] Project each verified consumer surface into the existing runtime observation as
  exactly `{bytes, inodes, backend, scope_id, evidence_sha256}` (`backend` is
  `project-quota` or `tmpfs`; evidence hash is the scope sidecar digest). Supply the
  existing resource/network/root facts separately. Do not send extended sidecar keys
  to closed `admit_runtime` objects or claim its hash check verifies kernel evidence.
- [ ] Enforce allocation/admission before host staging, not only before actor start.
  A complete trusted backend and production runner wiring remain unverified by
  this change; runtime integration is a pending implementation item. A future read-only capability
  detector may observe only: never provision, mount, assign IDs, set limits or start
  a workload. Put those mutations in the separate trusted allocator/operator path.
- [ ] Project snapshot preflight into `admit_snapshot`'s existing shape; retain
  completion and backend growth/resource evidence separately for lifecycle sealing.
  Keep the byte-only legacy `snapshot_admission` explicitly non-enforcing.
- [ ] Project the five supported object kinds into `admit_cleanup`; separately
  require sidecar project/tmpfs/reservation checks before atomic lease release.
  The existing module neither deletes resources nor updates the ownership ledger.
- [ ] Implement offline synthetic refusal coverage for disabled enforcement, missing
  units/dimensions, rounding, shared/reused IDs, mismatched descendants, incomplete
  inventories, stale namespaces, unknown drivers, unbounded snapshots and uncertain
  cleanup. Synthetic observations validate contracts only.
- [ ] Only after separate authorization, validate actual enforcement on small,
  dedicated finite storage with no task payload/model/H0, fixed resource budgets
  and verified cleanup. Record identities, actual byte/inode refusal observations,
  normal behavior below bounds and lifecycle failures. This future runtime step is
  **external validation**, not performed here, and is not production H0 admission.

## Historical source-audit appendix (preserved evidence)

The following findings and test count belong to Codex 168's historical revision,
not this checklist conversion or a live host. Source hashes remain in
[the audit inventory](../filesystem-quota-codex168-source-evidence.json).

### Historical source evidence

The inert Docker control requested a read-only root and `/tmp` with `size=16m`
and `nr_inodes=4096`; artifact-runtime helpers built paired tmpfs options too.
Those narrower paths did not provide a complete task/workspace backend, and
the historical audit did not establish live application of their limits.

| Path / symbol | Existing behavior | Missing enforcement |
| --- | --- | --- |
| `eval/sandbox.py:command` | Read-only runtime/workspace binds; writable host task and verifier-output binds; bare tmpfs mounts for hidden trees, private `/tmp`, and `.state` | No task-bind project quota; no explicit paired byte/inode limits on tmpfs; no backend identity or kernel quota observer |
| `eval/separated_stdio.py:namespace_command` | Separate native namespace with bare `/tmp` tmpfs and writable `/work` or `/verdict` binds | Same missing host-bind enforcement and paired tmpfs limits |
| `eval/runner.py:run_one` | Creates task scratch, `.state`, HOME and TMPDIR; dispatches to sandbox or container functions | No quota provisioning/admission before those writes |
| `eval/container.py:command`, `_mounts` | Docker/files root is read-only; `/tmp` requests `size=512m`; task and `.state` are writable host binds | No explicit inode policy for `/tmp`; neither bind has a quota backend |
| `eval/container_state.py:_run_one_container_state` → `eval/container.py:create` | Docker exec/container-state root is writable; `create` passes CPU/memory/PID bounds; scratch and HOME are bare tmpfs; state is copied into the root and later committed | No byte/inode limits for the writable layer or tmpfs; no graph-driver/snapshotter quota integration |
| `driver.py:main` → `ckpt/git_state.py:stage_workspace`, `materialize` | Ordinary host mkdir/copy/git/archive operations; workspace-location isolation | No quota-aware allocator; no limit before staging, Git storage or extraction |
| `harnessgrad/loops/mode_a.py:_run_mode_a`, `harnessgrad/methods.py:_method_sandbox_plan` | Copies base workspace, creates method workspace, makes the enclosing scratch directory writable | No independent quota scope for these writable trees/trajectory output |
| `eval/pilot_admission.py:control_command`, `_runtime_envelope` | Explicit `size` and `nr_inodes` for control `/tmp`; read-only root and restricted mount plan | Limited control path; not a writable task/workspace backend or kernel project-quota observer |
| `eval/artifact_admission.py:runtime_tmpfs`, `require_artifact_runtime` | Bounded tmpfs options and validation of supplied Docker inspect facts; checks small allowlisted artifact exports | An option builder / supplied-observation contract, not exec-layer or workspace provisioning |
| `eval/runner_admission.py:admit_runtime` | Validates supplied `tmpfs` or `project-quota` facts, exact limits and distinct scope IDs | No implementation that allocates a project, queries effective kernel limits, or wires trusted observations into the runners |
| `eval/pilot_admission.py:filesystem_capacity`, `ReservationLedger` | `statvfs` free byte/inode readings and cooperative reservations | Observation/accounting only; cannot stop writes |
| `eval/container.py:snapshot_admission` | Size/free-byte preflight before commit; receipt says `preflight_only=true`, `quota_enforced=false` | No inode or growth enforcement; actor cgroups do not bound daemon snapshot storage |

The platform source search found no implementation of project ID assignment,
project-inheritance management, `quotactl`, project hard-limit queries or setters,
`xfs_quota` / `setquota` integration, or a Docker `storage-opt` quota path.
The accepted string `project-quota` in the admission contract is not an installed
backend. Synthetic facts with that string test the contract only.

`statvfs`, `shutil.disk_usage`, Docker size observations, traversal totals,
export-file size checks, free-space reserves, memory limits, read-only binds and
declared policy do **not** establish filesystem byte-and-inode quota enforcement.
Read-only binds remove a writable surface; they do not bound other writable
surfaces. Tmpfs `size` bounds allocated data, not aggregate apparent file lengths;
disk quota blocks are also allocation accounting. Policy and receipts must state
those units, especially for sparse files and block rounding.

### Historical validation of existing contracts

The existing synthetic runner-admission and artifact-runtime suites passed:
**252 passed**. Their autouse guards prohibit real subprocess and socket execution;
Docker observations are fabricated and disk usage is mocked. All test temporary
files were confined to this worktree and removed afterwards. These tests validate
contract refusals and bounded artifact handling, not installed quotas.

See [the task report](../filesystem-quota-codex168-report.md) for the exact command
and [captured output](../filesystem-quota-codex168-test-result.txt).
