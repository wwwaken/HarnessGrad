# Offline runner admission contract

`eval.admission.runner_admission` provides reusable checks for adapter runtime, snapshot and
cleanup observations. It performs no execution or discovery. The supplied facts
must come from a trusted backend observer, independently of actor output and adapter
declarations. A passing synthetic contract is not a production H0 authorization.

Runtime admission remains the strict contract used by gated runtime paths. The
[quota deployment enhancement](filesystem-quota-backends.md#scope-optional-formal-deployment-enhancement)
is optional for ordinary local execution: project quotas and a dedicated volume
are not general installation prerequisites. `admit_runtime` still requires all its
facts below. Snapshot and cleanup admission instead use the operator's
[2026-10-15 decision](enforcement-proof-decision.md): check available facts best-effort,
retain uncertainty, and refuse known failures. They do not prove infallible bounds,
exact absence or atomic lease closure. A local run without verified enforcement cannot
claim this contract's byte/inode guarantees.

For local feedback without quota administration, the
[Task 237 ordinary-run receipt proposal](task-237-ordinary-run-receipt.md) records
quota uncertainty, sandbox choice and local metric identity under explicit
non-production labels. It adds no runtime implementation or exception to runtime
admission; ordinary receipts cannot satisfy that gate.

## API and receipts

All three functions take `(binding, policy, observed)` and return a JSON-compatible
receipt, or raise `AdmissionError` with a bounded `receipt` and fixed `code`.
Bindings contain exactly `adapter_id`, fresh `run_id`, fresh `trial_id` and
`manifest_sha256` (64 lowercase hex digits). Every observation repeats the binding.
Runtime observations require an `evidence_sha256`; snapshot/cleanup evidence hashes
may be omitted or null, with that uncertainty recorded. Invalid supplied hashes
still refuse. A mismatch refuses stale or cross-run facts.
The manifest must freeze source, split, harness, phase, limits and owned namespace.
Use a distinct trial binding/manifest for each worker or lifecycle phase; these
stateless functions cannot detect replay within an identical binding.

Evidence hashes authenticate no origin. The proposed external verifier, signing
roles and challenge/allocation binding are reviewed in
[task 233](task-233-quota-readback-authentication.md), including the distinct-worker
binding mismatch with nested lifecycle snapshot checks. That proposal is not
implemented and does not change binding or input-integrity checks.

Receipts record the stage, binding, status, `measured=false` and
`production_authorized=false`. Passing receipts include canonical policy and
observation SHA-256 hashes and normalized evidence. Refusal receipts contain a
reason without echoing unchecked data. Persist the original frozen policy beside
refusals so requested limits remain auditable. These receipts contain no score.

The maximum serialized receipt is 16 KiB, each identity/path is at most 256 UTF-8
bytes, quantities are signed 64-bit nonnegative integers, filesystem inventories
have at most 32 surfaces, and ownership inventories have at most 64 resources.
Additional fields (including logs, environment variables, payloads and credentials)
are rejected. An oversized valid receipt is refused without truncating evidence.

## Runtime, network and filesystem enforcement

`admit_runtime` accepts a policy with exactly `resources`, `network` and
`filesystems`. Resource keys are `cpu_millis`, `memory_bytes`, `swap_bytes`, `pids`
and `timeout_ms`; all are positive except swap, which may be zero. Observations
must contain matching actual values, `resource_backend` equal to `cgroup-v1` or
`cgroup-v2`, and `timeout_backend` equal to `host-supervisor`. The supervisor must
bound execution and teardown; cgroups alone do not enforce a wall-time deadline.

This contract supports `network=none` only: the observed network must be `none`
with `attachments=[]`. A command flag alone is insufficient. Backends must inspect
the namespace and every attached interface before execution, and prevent changes
after that observation. Live-model relays and service networks need a separate
contract; this gate grants no exception for them.

The root must be read-only. `filesystems` maps every canonical absolute writable
surface (for example `/work`) to positive `bytes` and `inodes` limits. Observed
surfaces must match exactly. Each observed surface adds an enforced `backend`
(`tmpfs` or `project-quota`), a distinct `scope_id`, and its own `evidence_sha256`.
The observer must verify the mount/project identity and effective hard limits on
both dimensions, accounting for all writable binds, volumes, scratch, exports,
logs and evidence storage. Writable roots and unsupported backends remain blocked.

Reservations, free-space observations, a disk-size flag, `enforced=true`, or a
declared quota are insufficient. Kernel/mount enforcement is an independent gate.
These checks do not install a filesystem quota. A backend lacking reliable byte
and inode enforcement must keep the adapter blocked. Do not fill a disk or create
large numbers of files as an admission probe; these tests use fabricated facts.

The [Codex 168 source audit](filesystem-quota-backends.md) found no complete quota
backend connected to native bwrap/files, Docker exec or workspaces. Bounded tmpfs
in the separate inert control/helper paths does not close those gaps. The audit
lists the OS provisioning, allocator, effective-limit observer and runner wiring
required; it makes no live host capability claim.

## Best-effort snapshot preflight

`admit_snapshot` requires positive `max_bytes`, `max_inodes`, `reserve_bytes`,
`reserve_inodes` and `timeout_ms`. Available observations provide nonnegative
writable/free byte and inode counts, the applied deadline and a trusted `device_id`.
Omitted/null facts are unknown and their field paths appear in `evidence.uncertainties`;
all snapshot receipts that pass carry `evidence.best_effort=true`, even with complete
preflight observations. Unknown quantities remain null, including derived required
capacity when writable size is unknown.

Known facts still refuse on a running worker, nonzero exit, OOM, deadline mismatch,
excess writable size or insufficient free space. With size known, free space must
cover size plus reserve; with size unknown, free space below the reserve still
refuses. Exact equality passes. Receipts retain observed, maximum, reserve,
required and deadline quantities without claiming that missing checks passed.

This is snapshot preflight. The trusted snapshot worker also needs its own runtime
resource admission. Continue applying capacity reservations and backend-specific
bounds on commit/export growth best-effort, retaining gaps rather than requiring
proof of bounded peak usage. Docker daemon resources are not bounded by the actor's
cgroup. No generic multiplier proves commit peak usage.
Record commit exit/OOM/timeout, final image identity and size, and owned-image
cleanup separately. Real failures remain failures; missing completion/score evidence
is not a measured zero. These admission receipts themselves always stay unmeasured.

The existing `eval.containers.container.snapshot_admission` remains byte-only preflight. It
now rejects malformed limits, negative/invalid size observations, invalid Docker
roots and query failures, and records byte limits and inspection/commit deadlines.
Its receipt explicitly says `preflight_only=true`, `quota_enforced=false`. It
does not verify inode limits, quiescence, daemon resource limits or complete cleanup.

## Cleanup and lease release

`admit_cleanup` takes `owned` resources and positive `timeout_ms`. Each ownership
record is `{kind, id}`; supported kinds are `container`, `network`, `snapshot`,
`volume` and `workspace`. Observed `objects` identify resources with `kind` and `id`.
Known identity components must match the policy, and complete identities cannot be
duplicated. Missing/null identity components record uncertainty; partial identities
do not count as checked owned objects. Known
`absent` values must be true; false still refuses release. Missing object rows,
omitted/null absence facts or evidence hashes record uncertainty instead of refusing.
Namespace coverage may be partial: omitted/null kinds, `remaining` values and
hashes record uncertainty, while any known nonempty namespace still refuses.
This retains checks for observed unrecorded allocations and interrupted intents.

The backend must persist ownership intent before allocation, validate ownership
before removal and query only the bound owned namespace. Continue deleting resources
and updating the ledger using the existing mechanisms; no proof of exact absence or
atomic closure is required by this API. Actual removal failures and deadline
mismatches still refuse. A successful remove without complete absence observations
can proceed with uncertainty retained. The receipt records observed object counts,
only namespace kinds with observed empty `remaining` lists, the observed deadline
(null when unknown), policy limits, `best_effort=true` and uncertainty field paths.
This module does not delete resources or update a ledger. Passing receipts request
`lease_action=release`, including with uncertainty; refusals request
`lease_action=quarantine`. Persist uncertainty with the receipt; release is not proof
that nothing remains or that the ledger update was atomic.

## Synthetic validation

`eval.admission.lifecycle_receipt` composes these checks into immutable lifecycle checkpoints:
`scope → admit → execute → quiesce → score → seal → cleanup`. Runtime and cleanup
transitions recheck supplied `policy`/`observed` facts through this module. Seal
requires snapshot completion, artifact identity, snapshot-worker runtime admission,
and snapshot preflight; preflight alone never suffices. Failed/unknown stages may
only advance to cleanup, and successful cleanup cannot restore measurement validity.
See [the lifecycle review](../reports/lifecycle-codex177-report.md) for bindings, publication
rules, failure persistence and remaining backend obligations. The
[scorer backend and lifecycle API](scorer-backend-lifecycle-api.md) documents optional
composition, ordinary-user access and the distinction between missing scorer and
resource observations.

`tests/quality/test_runner_admission.py` denies real subprocesses and sockets and
uses fabricated observations and a fake Docker client. Existing reservation and
cleanup regressions in `test_cached_pilot_admission.py` remain independent coverage
of persistent quarantine/capacity behavior. Neither suite needs benchmark payloads,
heldout content, images, models, providers, GPUs or an available Docker daemon.
