# Filesystem byte/inode quota backend audit — Codex 168

## Decision and scope

At source revision `10e983fc5fcb006c5afdbce1ef851dad71e953f2`, the platform
has **no complete, connected byte-and-inode enforcement backend** for native
bwrap/files tasks, Docker exec tasks, or harness/method workspaces. These modes
remain unsupported for admission requiring filesystem quotas. No capability
detector was added: there is no implemented backend for those modes whose
effective limits it could verify.

This is a source audit, not a determination of the running host's kernel,
filesystem features, mount options, daemon storage driver, or existing quotas.
No host configuration, mount table, Docker daemon, quota interface, dataset, model
endpoint, H0, or benchmark was inspected or executed. Source hashes are recorded
in [the audit inventory](../filesystem-quota-codex168-source-evidence.json).

There **is** a narrower implementation: the cached inert Docker control command
requests a read-only root and `/tmp` tmpfs with both `size=16m` and
`nr_inodes=4096`. Its inspect validator checks those options. The artifact-runtime
helper likewise constructs bounded tmpfs options for `/tmp` and
`/control-output`. Linux tmpfs provides concrete kernel allocation limits when
these options are applied, but these control/helper paths do not supply quotas
to the three audited modes. This audit did not establish their live application.

## Source evidence

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

## Exact OS and backend work still required

### Disk-backed native tasks and workspaces

Provide a trusted host allocation service with one supported filesystem backend:

- **XFS project quotas:** a kernel with XFS and quota support, a backing filesystem
  mounted with project quota enforcement (`prjquota` / `pquota`), and positive
  kernel **block hard** and **inode hard** limits per project. Accounting enabled
  without enforcement is insufficient.
- **ext4 project quotas:** a kernel with ext4 project quota support, filesystem
  `quota` and `project` features / project quota metadata, and enabled project
  quota enforcement (`prjquota`). Verify the actual kernel/filesystem combination
  supports both hard-limit dimensions; its filesystem name alone is insufficient.

Administrative filesystem preparation and enforcement activation belong to a
separate OS provisioning change. Nothing in this audit performs that work.

The allocation service must create a fresh scope before **any** staging/copy/Git
write, assign a unique project ID and project-inheritance flag to the root, and
ensure every existing descendant belongs to that project. Query the assignment,
inheritance and effective hard limits through the filesystem's supported ioctl
and quota interfaces. Convert block units explicitly and refuse policy values
that cannot be represented exactly; a larger rounded limit must not silently
match a smaller requested byte ceiling. A directory name or free-space reading
cannot replace these queries.

Apply this to task/setup/output directories, harness `.git` storage, method base
copies, method workspaces and trajectories, host staging, verdicts, exports,
runtime caches, logs and evidence wherever writes are permitted. Additional
mounts need separately verified scopes; directory inheritance does not cover
another mounted filesystem. Do not use one shared user's quota as independent
per-run isolation. Prevent actor changes to project assignments, mounts or quota
enforcement, including capabilities that allow quota override.

Wire allocation and observation into `driver.py` before workspace creation,
`ckpt/git_state.py` before copies/extraction, method workspace allocation before
round staging, and `eval/runner.py` before task preparation. Kernel enforcement
must cover the host processes doing the preparation too, not only the later
sandbox. Retain scope ownership across checkpoints and crashes until cleanup is
verified; do not recycle a project ID while any owned object remains.

### Native bwrap scratch and implicit writable filesystems

For ephemeral scratch, a trusted service can provision tmpfs with explicit
positive `size=<bytes>` **and** `nr_inodes=<count>`, then bind that bounded storage
into the namespace. Alternatively extend the bwrap integration only after
verifying the pinned bwrap/kernel combination can apply and report both limits.
The existing bare `--tmpfs` arguments provide no such per-run policy. A bwrap
byte-size option alone would leave the inode requirement open.

Inventory the final namespace, including `/tmp`, `.state`, hidden-tree tmpfs,
root scaffolding, verifier-output binds and writable device/shared-memory mounts
where present. Make unused surfaces read-only or cover them with verified limits.
Keep the actor unable to remount, replace or increase limits. Verify final mount
identity and both effective mount limits from the actor's mount namespace through
a trusted observer before actor execution. Host task binds still require the
disk-backed backend above, or a deliberate bounded-tmpfs task allocation.

### Docker exec and snapshot storage

First establish the **actual** daemon storage driver, snapshotter, backing mounts
and upper-layer paths. [The historical storage note](moving-docker-data-root.md)
reports a containerd image store (`overlayfs`,
`io.containerd.snapshotter.v1`) and ext4 storage; those are historical claims,
not fresh observations or quota evidence. Do not infer classic `overlay2` support
or XFS from them.

Docker's classic `overlay2` `storage-opt size` facility depends on an appropriate
XFS backing filesystem with project quotas. A byte-size setting alone does not
establish an independently configured inode hard limit, and must not be assumed
to apply to a containerd snapshotter. The platform source configures neither facility.

To retain a writable exec root, implement a supported daemon/snapshotter quota
allocator and trusted observer for the actual writable upper layer, with paired
kernel block/inode hard limits, project assignment/inheritance, per-container
ownership and protection against actor overrides. Integrate it before container
copies/start and retain ownership through stop, commit and cleanup. Snapshotter
project ID allocation must coordinate with any existing driver-managed IDs.

An alternative is a deliberate read-only-root execution design with all permitted
writes on independently bounded tmpfs or project-quota mounts and artifact-only
state transfer. This changes container-state semantics: Docker commit does not
capture mounted tmpfs/bind contents. It is a runtime redesign, not a quota flag.
Add explicit paired limits for `.state`, HOME/TMPDIR and other writable mounts in
either design; inventory image-declared volumes and extra mounts as well.

Commit/export creates writes outside the actor's upper layer and cgroup. Provide
separate enforced scopes and resource limits for daemon/containerd content,
snapshot destinations, temporary unpack/copy data, logs and exported evidence.
Moving Docker's data root or increasing its free space does not install a quota.
Snapshot preflight alone must continue to report no enforcement.

### Trusted observation and fail-closed admission

After the backend exists, add a **read-only** capability detector that never
mounts, assigns IDs, sets quotas or starts workloads. It must consume trusted
mount-namespace/filesystem/project/quota observations, bind them to the exact
run/trial/source/policy and owned scope, and verify both effective positive hard
limits plus enforcement state and complete writable-surface coverage. Docker
configuration / requested mount options alone are weaker than effective kernel
evidence; retain that distinction in receipts.

Unknown storage drivers, unsupported filesystems, disabled enforcement,
permission failures, missing dimensions, shared scopes, stale identities,
unrepresentable limits and incomplete inventories must return unsupported/blocked,
`measured=false`, without a score or production authorization. Route those
observations to the existing runner admission contract **before** staging or
execution. The current production runners do not call that contract; its
fail-closed behavior must not be attributed to those runners.

Synthetic detector tests should inject these cases and verify that no observation
or declaration can promote an unsupported backend. Any later OS enforcement
validation is a separate, explicitly authorized step on small dedicated storage
with finite bounds and verified cleanup. This audit provides no live enforcement
validation or production H0 authorization.

## Validation of existing contracts

The existing synthetic runner-admission and artifact-runtime suites passed:
**252 passed**. Their autouse guards prohibit real subprocess and socket execution;
Docker observations are fabricated and disk usage is mocked. All test temporary
files were confined to this worktree and removed afterwards. These tests validate
contract refusals and bounded artifact handling, not installed quotas.

See [the task report](../filesystem-quota-codex168-report.md) for the exact command
and [captured output](../filesystem-quota-codex168-test-result.txt).
