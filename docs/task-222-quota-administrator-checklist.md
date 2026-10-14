# Safe quota administrator checklist — Task 222

**Docs only; all actions below remain pending.** No host inspection or changes,
model/H0 calls, or runtime validation were performed for this checklist.

This checklist applies when an operator chooses the
[optional formal-deployment quota enhancement](filesystem-quota-backends.md#scope-optional-formal-deployment-enhancement).
Ordinary local execution requires neither project quotas nor a dedicated volume.
The checks below are requirements for claiming the strict profile's enforced
byte/inode bounds; they do not add an installation step for every user. Existing
gated diagnostics/pilots still need their required evidence and review.

Review basis: the [quota source audit](../reports/filesystem-quota-codex168-report.md)
at `10e983fc5fcb006c5afdbce1ef851dad71e953f2` found no complete connected
byte-and-inode backend; it did **not** inspect host quota capabilities. The
[2026-10-06 storage note](moving-docker-data-root.md) reports containerd-backed
storage and an incomplete migration attempt, not current quota evidence or an
approved migration procedure. The [backend requirements](filesystem-quota-backends.md)
and [proposed evidence schema](filesystem-quota-evidence.schema.json) define
acceptance requirements; schema validity alone proves neither enforcement nor
production readiness.

For proposed signer roles, authenticated readback, per-allocation binding and the
challenge/consumption sequence, see the
[task-233 authentication review](task-233-quota-readback-authentication.md).
It implements no verifier and completes no checklist item; a root change receipt
cannot replace fresh trial enforcement observations.

## Read-only inspection — administrator / trusted observer

- [ ] Record observation time, observer and boot identity, kernel release, and each
  relevant filesystem UUID/type, device major:minor, mount/namespace identity,
  root inode and effective mount options. Use metadata-only query/report modes;
  permission failures remain unknown. Do not mount, repair or activate features.
- [ ] Inspect project metadata, accounting, and **both block and inode hard-limit
  enforcement** through supported read-only interfaces. XFS needs project quotas;
  ext4 needs supported `quota`/`project` features, project metadata and enforcement.
  Filesystem names, mount flags and free capacity alone are insufficient.
- [ ] Map actual Docker/containerd driver, snapshotter, content/snapshot roots and
  backing filesystems; inventory host preparation, workspace/`.git`, scratch,
  HOME/TMPDIR, shared memory, binds/volumes, verifier, daemon, snapshot/export,
  logs and evidence writers. Observe existing state without starting workloads.
- [ ] Preserve protected, allowlisted metadata and unresolved gaps. Exclude task
  payloads, credentials, environment dumps and unrestricted logs. Inspection is
  not permission to provision or a complete `host_provisioning` receipt.

## Provisioning — separate approved maintenance / backup procedure

- [ ] Before mutations, require an administrator-owned change ID, exact target
  device/UUID and ownership review, impact/dependency inventory, maintenance
  window, quiescence of affected writers, verified restorable data/configuration
  backups, and a recovery/rollback plan with stop conditions and console access.
- [ ] Treat filesystem feature/metadata changes, enforcement activation, mount or
  boot changes, kernel changes, daemon restarts/storage migration, project-ID
  assignment and limit setting as mutations, never read-only discovery. Follow a
  filesystem/version-specific reviewed procedure; respect offline prerequisites.
- [ ] This checklist does not prescribe formatting. If a separate plan requires
  filesystem recreation, **stop** until explicit destructive-operation approval,
  independently verified target identity, confirmed absence of live mounts/users,
  and a tested restore plan exist. Never format live root or daemon storage;
  prefer dedicated empty storage if that approved plan calls for new storage.
  A dedicated volume is an optional provisioning choice. No destructive commands
  are supplied here.
- [ ] Plan independently owned paired byte/inode scopes under an already bounded
  allocator parent, durable ownership intents/leases, positive frozen limits and
  protected failure-evidence capacity before staging. Include daemon, temporary
  snapshot/export and all host writers. Moving storage or setting a Docker size
  option does not establish paired per-run enforcement.

## Post-change verification — fresh evidence / independent review

- [ ] Reobserve boot, filesystem, mount/namespace and daemon identities after the
  change and any required restart; verify persistence and affected-service health
  against the approved plan. Preserve before/after metadata and the change receipt.
- [ ] Read back actual accounting and paired hard limits, unique project ownership,
  inheritance and complete descendant assignment. Require zero mismatches and
  uncovered mounts; activation must precede staging. Require
  `hard_blocks * quota_unit_bytes == effective.bytes == requested.bytes` and
  `hard_inodes == effective.inodes == requested.inodes`. Reject rounding or missing
  dimensions. Dedicated tmpfs needs effective byte **and** inode bounds too.
- [ ] Verify every writer's final namespace and enforced scope, including daemon
  and snapshot/export destinations. Unknown driver support or uncovered storage
  remains blocked. Current runner admission requires a read-only actor root;
  a host provisioning receipt cannot close backend/runner integration gaps.
- [ ] Any write-based enforcement check needs separate authorization and a dedicated
  disposable scope under an already bounded parent, fixed byte/inode/time/resource
  ceilings and verified cleanup. Never fill shared storage; no task/model/H0 work.
  Read-only observations alone cannot establish actual refusal behavior.
- [ ] Validate fresh metadata-only records against Draft 2020-12 with format checks
  **and** the backend document's trust, freshness, digest, identity, arithmetic and
  coverage rules. Bind records to real run/trial/manifest, source/split/harness,
  policy/ownership, observer and lifecycle identities; never invent missing IDs,
  hashes or change receipts. For a genuinely model-free lifecycle, use
  `model_bound=false` and null model/endpoint fields. Keep `measured=false` and
  `production_authorized=false`.
- [ ] Return `host_provisioning`, project/tmpfs scope and writable-inventory evidence;
  include Docker/storage and separate snapshot preflight/completion records where
  applicable. Record gaps as `blocked`/`unknown` with schema reason codes; retain
  partial and old records. Missing required envelope fields stay an incomplete
  inspection worksheet, not a fabricated schema-valid receipt.
- [ ] Verify owned-scope cleanup before atomic lease release: no writers, mounts,
  handles, descendants or pending deletion; project usage zero bytes **and** inodes;
  tmpfs original lifetime destroyed with aliases gone. Destroyed tmpfs counters may
  be null, never invented zeros. Require complete owned-object/namespace absence;
  quarantine IDs and retain reservations on uncertainty. Passing a finite check
  does not authorize production H0.
