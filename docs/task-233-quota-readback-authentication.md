# Quota readback authentication and allocation binding — Task 233

**Proposal only; runtime gates remain blocked.** Review base:
`61e7f82245c76e7c833740216940d1fcaf3b76be`, in `/tmp/hg-codex-233`.
This review uses repository contracts only. No host inspection, provisioning,
keys/signatures, quota receipts, workload, model/H0 call or enforcement probe was
performed or produced. Authentication objects below are proposed contracts,
not implemented schemas or accepted APIs. Existing schemas and runtime code
remain unchanged.

Scope: this proposal supports the
[optional formal-deployment quota enhancement](filesystem-quota-backends.md#scope-optional-formal-deployment-enhancement).
Ordinary local execution requires neither project quotas nor a dedicated volume.
The authentication and allocation requirements below apply when claiming the
strict profile's guarantees; all existing gated admission requirements remain.

Authenticate an administrator's readback with an enrolled, host-scoped observer
signature over exact metadata and its collection context. Admission additionally
requires fresh independent observations joining the real allocation to its durable
lease, frozen trial policy and final writer namespaces. A root provisioning receipt
establishes prerequisites at one time; it cannot establish a later trial's project
assignment, effective limits or coverage.

## Findings from the supplied contracts

| Source | Established contract | Authentication or binding gap |
| --- | --- | --- |
| [Quota schema](filesystem-quota-evidence.schema.json), `$defs.observer`, `host_provisioning`, `project_scope` | Observer/boot/implementation/raw-observation hashes; administrator/change IDs; scope-to-provisioning digest; run/trial/manifest and allocation generation | No signature, key, host identity, challenge, trusted enrollment or replay database. An administrator ID is a claim; a hash checks bytes, not origin. |
| [Backend requirements](filesystem-quota-backends.md), mandatory semantic checks | Protected immutable metadata, independent observer, exact arithmetic, matching host/boot/filesystem, increasing sequences, complete coverage and cleanup | These are requirements for a future semantic validator. Protected storage and submitted sequence fields alone do not authenticate a report. |
| [Task-222 checklist](task-222-quota-administrator-checklist.md) | Inspection, separately approved maintenance and fresh post-change readback are distinct; incomplete observations stay worksheets | Does not specify enrollment, signer roles, signed bytes or a run-specific challenge/consumption protocol. |
| [Runner contract](runner-admission-contract.md), [implementation](../eval/runner_admission.py), `_observation` / `admit_runtime` | Exact four-field binding and paired limits; distinct scope IDs; closed projected observations | Checks evidence-hash syntax and supplied facts. Does not resolve sidecars, verify signatures, query the kernel or remember consumed observations. |
| [Lifecycle implementation](../eval/lifecycle_receipt.py), `_gate`, `_attestation`, `validate_lifecycle_receipt` | Replays ordered stages/facts, hashes events, binds scoring/sealing/snapshot/cleanup | Explicitly states that digests do not authenticate origin. The name `attestation` does not imply a signature. No collector, freshness service or lease update. |

Quota sidecars and admission receipts retain `measured=false` and
`production_authorized=false`. Lifecycle structural publication readiness is also
not production approval. This proposal closes none of those runtime boundaries.

## Root provisioning versus fresh enforcement evidence

| Evidence | Subject and lifetime | Proposed signers | What it establishes |
| --- | --- | --- | --- |
| Root provisioning/change receipt | Real approved maintenance on an identified host/filesystem; preserved historically across runs | `administrator-change` and independent `host-observer` post-change readback | Change provenance and observed host prerequisites. No trial allocation, writer coverage or refusal behavior. |
| Fresh trial enforcement observations | One real binding, generation, lease, phase and challenge | `host-observer` before staging; `namespace-observer` in final consumer namespaces | Actual kernel accounting/enforcement flags, paired hard limits, assignment, topology and coverage at observation time, protected against subsequent changes. |
| Finite behavioral validation | Separately authorized disposable validation lifecycle, fixed ceilings and verified cleanup | Trusted observers and independent `runtime-reviewer` | Observed behavior below bounds and actual byte/inode refusal outcomes for that tested backend. No automatic transfer to other allocations or production approval. |

Behavioral validation is future external work; no commands or probes are specified
here. Read-only kernel readback establishes effective configuration, not observed
write refusal. A valid signature authenticates the statement, not the completeness
or truth of its claims without the trust and semantic checks below.

The existing `host_provisioning` sidecar is **run-bound**, despite describing host
prerequisites: its mandatory `binding` and `provenance` cannot be null. Preserve
the historical, run-independent maintenance receipt outside that schema. For each
consuming trial, collect a new `host_provisioning` record with real binding and
current boot/filesystem facts, referencing the real change ID. Never copy an old
record and replace its binding. Unknown change receipts/IDs remain incomplete
inspection evidence and block; inventing a change ID or dummy trial is not an
encoding solution.

The maintenance receipt may name an earlier boot; that is historical context,
not current-boot admission. Its authenticated change history must identify the
same host/filesystem. The fresh run-bound provisioning record and scope records
must name the same current boot. A genuinely model-free lifecycle uses
`model_bound=false` and null model/endpoint fields, with real remaining identities.

Tmpfs scopes have no `host_provisioning_record_sha256` and cannot use the XFS/ext4
`host_provisioning` facts shape. Authenticate their host/boot and dedicated mount
lifetime directly; do not manufacture project-provisioning evidence for tmpfs.

## Observer roles and trust enrollment

These are separately authorized logical roles. For this proposal, allocation
mutator and readback signer must be different principals/keys. An administrator
signing a typed report supplies attribution, not independent readback. One
protected collector may hold both observer roles only if the frozen trust policy
authorizes both and it actually observes both host and consumer namespaces.

| Role | Authority and signature | Required separation |
| --- | --- | --- |
| `controller` | Freeze scope, sign phase challenges, maintain durable one-use challenge state | Outside actor/adapter control; cannot substitute its own kernel claims for an observer. |
| `administrator-change` | Sign the real maintenance change record and allowlisted before/after metadata | Root provisioning authority; its signature is not trial admission. |
| `allocator` | Sign durable ownership intent and actual allocation/lease mapping | Own mutation path/ledger; cannot self-certify readback or release on removal-command success. |
| `host-observer` | Independently query host kernel quota state, effective limits, assignment and host preparation scopes | Query-only authority in this role; no provisioning or actor-submitted signing input. |
| `namespace-observer` | Observe final consumer mounts/writers, effective scopes, read-only root and locked writable inventory | Resolve actual namespaces/objects; requested mount options are not observations. |
| `lifecycle-supervisor` | Sign checkpoints, execution/quiescence and snapshot outcomes; control writer handoff | Verify observer signatures and all semantics before permitting a writer. |
| `cleanup-observer` | Sign fresh object absence, usage/destruction and namespace queries | Independent of removal mutator; cannot release allocator leases. |
| `runtime-reviewer` | Sign scope-limited review of authenticated evidence and later bounded validation | Separate from allocation/provisioning signer; no inferred production approval. |

Before acceptance, the verifier needs an independently approved, versioned
trust-policy checkpoint. Each enrollment binds principal, Ed25519 public key,
permitted roles, stable `host_id`, observer IDs, implementation/privilege-policy
digests, validity interval and revocation state. `key_id` is lowercase SHA-256 of
the raw 32-byte Ed25519 public key. Keys supplied only in an evidence packet are
not trust anchors. The controller pins the host's current approved boot identity
through trusted enrollment; a submitted `boot_id` cannot authenticate itself.

Keep keys, evidence and replay/lease ledgers outside actor/adapter access. The
collector must construct its own statements from allowlisted metadata queries,
not sign actor-submitted JSON. Preserve only protected redacted metadata, with
collection implementation and redaction policy pinned; raw hashes name those
exact preserved bytes. Check both the request's frozen trust-policy revision and
current revocation state. Unknown, expired, revoked or wrong-host/role keys cannot
authorize a new transition. Preserve historical verification decisions/checkpoints;
claimed signing time alone is insufficient. Rotation needs separate enrollment;
re-signing old metadata does not make an observation fresh.

This design trusts the administrator, collector and host kernel for their duties.
Host root can control software collectors and local keys; separate keys on that
host do not establish independence from compromised root. An implementation hash
identifies claimed code, not proof it ran. If that trust assumption is unsuitable,
independently anchored platform/boot attestation and protected collection/key
custody need separate review. Administrator-signed readback alone stays blocked.

## Exact proposed signature contract

Do not extend closed v1 quota, runner or lifecycle objects. Store them unchanged
and add an external `harnessgrad.quota-auth.v1` envelope containing exactly
`schema`, `payload`, `signatures`. The following is a wire-contract proposal,
not a receipt instance, generated signature or implemented validator.

Let `C(x)` be UTF-8
`json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
allow_nan=False)`, without trailing newline, matching quota record serialization.
Reject duplicate member names before parsing, floats, non-finite numbers, booleans
as integers and unknown fields. Apply existing metadata/time/integer bounds.
Cap each envelope at 64 KiB and each reference array at 128 entries. Require
exactly two distinct enrolled signatures for `maintenance`, and exactly one for
each other type, sorted by `key_id`. Store larger evidence separately under its
own bounds; never truncate it or embed unrestricted logs.

Each signature entry contains exactly `protected` and `signature_b64u`.
`protected` contains exactly `algorithm` (constant `Ed25519`), `key_id`,
`principal_id`, `role`. Sign these bytes; `||` denotes concatenation and `U64BE`
an unsigned eight-byte big-endian length:

```text
UTF8("harnessgrad.quota-auth.v1") || 0x00 ||
U64BE(length(C(protected))) || C(protected) || C(payload)
```

`signature_b64u` is the 64-byte signature in unpadded base64url (86 characters).
Verify with the enrolled key and its allowed principal/role/host context; no
algorithm negotiation or packet-provided replacement trust policy. Domain and
signed `statement_type` limit purpose. Full statement references are
`SHA256(C(envelope))`, including signatures; quota references remain
`SHA256(C(record))`. Raw metadata hashes cover exact stored bytes. No object
contains its own hash. Runner and lifecycle digests retain their own modules'
serializers; do not assume these serialization schemes are interchangeable.

Every payload has exactly these common fields:

| Fields | Meaning |
| --- | --- |
| `statement_id`, `statement_type` | Fresh immutable ID; one of the seven types below. |
| `host_id`, `boot_id`, `issued_at`, `not_after` | Enrolled host, approved observed boot, UTC issue/expiry; expiry follows issuance within frozen freshness policy. |
| `binding`, `allocation_generation`, `phase` | Existing exact binding, actual generation, existing quota phase; all null only for historical `maintenance`. |
| `challenge_sha256` | Controller challenge digest; null only for `maintenance`, `intent` and the `challenge` itself. |
| `previous_checkpoint_sha256` | Most recent accepted phase checkpoint, equal to the challenge's pinned predecessor; null only for maintenance or before the first checkpoint exists. |
| `measured`, `production_authorized`, `body` | Both flags false; closed type-specific body below. |

The type determines the exact body fields and required signer set:

| Type / required role | Exact body and interpretation |
| --- | --- |
| `maintenance` / `administrator-change` and `host-observer` co-sign the same payload | `change_id`, `administrator_id`, `change_record_sha256`, `before_metadata_sha256`, `after_metadata_sha256`, `filesystems`. Sign after real independent post-change readback; historical completion only. |
| `intent` / `allocator` | `ownership_intent_sha256`, `ledger_checkpoint_sha256`, `planned_inventory_sha256`, `bounded_parent_record_sha256`. Persist intent/reservations before signing; certify only a plan, never allocation success. Phase is `allocation`. |
| `challenge` / `controller` | `request_id`, `purpose`, `nonce`, `scope_sha256`, `policy_sha256`, `ownership_intent_sha256`, `expected_inventory_sha256`, `trust_policy_sha256`, `allocation_statement_sha256`. Nonce is 32 fresh random bytes encoded as 64 lowercase hex characters, not generated here. Allocation-statement hash is null only for initial allocation; durable request state fixes all expectations. |
| `allocation` / `allocator` | `ownership_intent_sha256`, `ledger_checkpoint_sha256`, `scopes`. Each row is exactly `scope_id`, `allocator_lease_id`, `allocation_key`, `bounded_parent_record_sha256`. Sign after real allocation and ledger commit; certifies mapping, not enforcement. |
| `observation` / phase-appropriate host, namespace or cleanup observer | `allocation_statement_sha256`, `maintenance_statement_sha256`, `records`, `namespace_mapping_sha256`, `inventory_lock_sha256`. Each record row is exactly `kind`, `record_sha256`, `raw_observation_sha256`, `observer_id`, `sequence`. Maintenance hash required for project scopes, null for pure tmpfs. Namespace mapping/lock hashes required for writer admission, null only where inapplicable to allocation/provisioning or destruction. |
| `checkpoint` / `lifecycle-supervisor` | `accepted_statements`, `projection_sha256`, `admission_receipt_sha256`, `lifecycle_receipt_sha256`, `lifecycle_stage`, `ledger_checkpoint_sha256`, `decision`. Decision is `accept`, `blocked` or `unknown`. Not-yet-created receipts/projections and their lifecycle stage are null; an accepted writer handoff requires actual projection, admission receipt and ledger checkpoint. A non-null stage must equal the referenced lifecycle receipt's state. |
| `review` / `runtime-reviewer` | `checkpoint_statement_sha256`, `evidence_index_sha256`, `trust_policy_sha256`, `decision`, `unresolved_reason_codes`. Decision is `accepted_for_stated_scope`, `blocked` or `unknown`; reasons use the quota schema enumeration. No production approval. |

`accepted_statements` is a duplicate-free array of statement SHA-256 digests;
`records` and `scopes` have no duplicate identities. `filesystems` uses the existing
eight-field filesystem shape. The evidence index resolves all sidecars, raw
metadata, policy/provenance inventories, lease checkpoints and statements by hash;
it contains no task content. Verify every referenced digest and required signature
before accepting a checkpoint. Other fields/nulls/attachments are refused. The
intent is signed before the scope digest is computed, preventing cyclic references.
The maintenance administrator signature's principal must equal `administrator_id`;
the observer co-signer must be a different enrolled principal.

Challenge `purpose` is exactly one of `allocation`, `prestage_admission`,
`prestart_admission`, `execute`, `quiesce`, `score`, `snapshot_preflight`,
`snapshot_complete`, `seal`, `cleanup`. Pin the expected responding statement
types/roles and next lifecycle stage in durable request state. Admission purposes
use matching quota phases; execution/quiescence/scoring checkpoints retain phase
`prestart` as their writer context, sealing uses `snapshot_complete`. Other
purposes use their same-named quota phase. This introduces no quota phase or
lifecycle stage. Distinct purposes have distinct challenges even in the same phase.

For writer admission, `host-observer` signs host/prestage records and
`namespace-observer` signs final prestart records; if both collections are needed,
use separate observation statements under the same phase challenge. Snapshot
phases require supervisor-signed operation checkpoints plus host/namespace
observations for every applicable destination and worker. `cleanup-observer`
alone signs cleanup observations. Record observer IDs, boot, implementation,
privilege-policy digest and sequences must match the signing principal's enrollment.
Every observation's binding/generation and pinned predecessor must equal its
challenge; actual record `observed_at` must be inside that challenge's window.

## Binding to the actual allocation

Project `allocation_key` has exactly `backend=project-quota`, `filesystem`,
`project_id`, `root_handle_metadata_sha256`. Tmpfs `allocation_key` has exactly
`backend=tmpfs`, `filesystem`, `mount_lifetime_id`, `root_handle_metadata_sha256`.
`filesystem` is the existing eight-field identity shape. Protected root-handle
metadata identifies the opened object, namespace and root inode, not merely a
pathname resolved later. `mount_lifetime_id` is the allocator's durable fresh
lifetime token checked against retained mount/object references, not a renamed
reusable kernel mount ID.

The verifier must join and compare:

- Enrolled host/current boot and authenticated observer implementation/boundary.
- Exact adapter/run/trial/manifest, scope/provenance/policy/ownership digest,
  current generation and active allocator lease.
- Allocator-signed actual scope/root/project or tmpfs lifetime, current ledger
  checkpoint and independently observed kernel/filesystem identity.
- Every writer's final namespace/mount/root inode and enforcement-record digest,
  complete locked inventory, zero unmatched writable surfaces and distinct scopes.
- Accounting, both hard-limit enforcement dimensions, inheritance, complete
  zero-mismatch descendant/nested-mount scan and usage including overhead.
- `hard_blocks * quota_unit_bytes == effective.bytes == requested.bytes` and
  `hard_inodes == effective.inodes == requested.inodes`; exactly representable
  tmpfs byte/inode bounds and override/remount prevention for all writers.

Host provisioning and consumer namespaces can have different mount IDs/paths.
The signed namespace-map digest resolves an explicit observed map between host
scope and each consumer mount: same host/boot/filesystem and underlying
root/project or tmpfs lifetime. Compare namespace-local IDs within that namespace;
do not require equal mount IDs across namespaces or treat equal UUIDs alone as
the same allocated subtree. Missing mapping, unlocked topology or uncertain held
object identity blocks admission. Renaming a shared project cannot make it unique.

## Collection and consumption sequence

1. **Enroll and preserve maintenance evidence.** Verify real change provenance and
   independently read back post-change host state before co-signing `maintenance`.
   Preserve history. Reboot/remount/configuration changes require renewed host
   observation; maintenance history alone never opens a writer gate.
2. **Freeze scope and intent.** Choose real binding, fresh generation, manifests,
   provenance, policy, writer plan, deadlines and trust revision. Persist and sign
   intent/reservations under an already bounded parent. Then freeze `scope_sha256`
   over the scope index including signed intent and trust-policy digest. No scope
   identity or requested limit is presented as an observed allocation.
3. **Challenge and allocate.** Persist the signed allocation-phase challenge, then
   create only reserved empty scopes under the bounded parent, apply paired
   ceilings/inheritance and commit actual lease/mapping. Sign `allocation`.
   Verify that response, persist an allocation-only checkpoint and consume the
   allocation challenge atomically with its ledger result; this grants no writer
   permission. Allocation retries recover that same outcome rather than allocate
   again. The next challenge pins this checkpoint and actual allocation digest.
   No staging/data writer runs; empty-root initialization overhead is accounted
   for. Interrupted intents retain ownership for quarantine/cleanup.
4. **Challenge fresh host readback before staging.** A new `prestage` challenge
   names the actual allocation statement. Independently collect fresh run-bound
   `host_provisioning`, project/tmpfs scopes, host writer inventory and applicable
   daemon/storage evidence; sign record/raw hashes. The provisioning record retains
   schema phase `provisioning`; its external observation answers this prestage
   challenge. All sidecars share the consuming binding/generation. Verify the join
   above and retain the allocator/topology lock.
5. **Consume permission, then stage.** Verify signatures, raw hashes, semantics,
   deadlines and limits; obtain passing runtime/resource admission for each host
   preparation writer. Persist a signed checkpoint binding exact projection and
   admission digests. Atomically consume the challenge and record writer permission
   with the active lease before allowing a first data write. Record actual
   activation/first-write times; null `first_write_at` means no data write yet,
   never unknown. Bounded initialization is distinguished from staging/data writes.
6. **Reobserve final consumer namespaces.** Before actor/verifier/method start,
   issue a fresh `prestart` challenge; collect fresh scopes/inventory and applicable
   storage records in actual namespaces. Recheck assignment after staging, aliases
   and nested mounts, paired bounds and topology lock. Verify namespace-observer
   signatures, consume that challenge and persist actor admission/lifecycle
   checkpoint before start. Prestage evidence cannot substitute for this readback.
7. **Observe execution, quiescence and snapshot work.** Persist authenticated
   supervisor outcomes at the actual lifecycle stages. Issue/consume a fresh
   purpose-specific challenge for each supervised execution, quiescence, scoring
   and sealing checkpoint, with the exact expected predecessor and stage. Before
   snapshot/export,
   prove all writers stopped; obtain a fresh preflight challenge, enforced
   destination/temporary bounds, concurrent reservation and worker/daemon resource
   admission. Collect separate `snapshot_complete` operation/artifact evidence
   under another challenge. Preflight is never completion; legacy byte-only
   preflight is never quota enforcement. Seal only identical scored/sealed
   outcomes and the actual authenticated artifact. Resolve the worker-binding
   contract issue below before production integration.
8. **Observe cleanup, then release.** After removal attempts, issue a new cleanup
   challenge. Independently verify all generation-bound objects, eight sidecar
   namespaces, writer/mount/handle destruction and project zero-usage/reuse rules.
   Destroyed tmpfs counters may be null. Verify five-kind `admit_cleanup` projection
   and additional sidecar checks. Only a verified durable checkpoint and ledger
   compare-and-swap may release the exact lease/reservations. Uncertainty quarantines.

Afterward the independent reviewer signs the terminal checkpoint/evidence index
for its stated scope, referencing the original challenge/predecessor as an audit
context. Review of a consumed challenge creates no new execution permission and
adds no lifecycle stage. Unresolved gaps remain blocked/unknown.

Persist pending/consumed/failed challenges, predecessor checkpoints and observer
sequence high-water marks per observer/boot/binding in a protected durable ledger.
Require an unused nonce for the expected phase/generation, collection after
challenge issuance and before expiry, and frozen collection/admission deadlines.
Use frozen bounded clock skew plus supervisor monotonic deadlines; wall time alone
is insufficient. Require strictly increasing record sequences. Co-signing one
record does not create extra sequence numbers.

Challenge consumption, checkpoint persistence and writer permission must form a
recoverable transaction/compare-and-swap; concurrent callers cannot consume one
request twice or skip its expected lifecycle stage. After a crash, recover the
existing permit and actual writer state,
not another start. Revalidating an archive is audit, not a new permission. Lost
durable freshness/order state blocks writes and quarantines allocations.

Retain mutation exclusion from readback through startup and throughout the scope
lifetime except through trusted lifecycle operations. Reboot, mount/namespace
replacement, project reassignment, policy/lease change or topology unlock invalidates
outstanding permission and requires fresh challenge/observation. Preserve old and
failed records. Missing required fields remain incomplete worksheets; record
bounded blocked/unknown evidence without invented values. Later cleanup cannot
restore measurement validity or turn invalid/unmeasured work into a zero score.

## Runner and lifecycle handoff

The new verifier must run **before** current pure contract functions. After trust
and semantic validation, project each writable surface to exactly
`{bytes, inodes, backend, scope_id, evidence_sha256}`, with the quota record digest
as surface evidence. First freeze an evidence index over validated input records,
statements and trust decisions, excluding the projected observation and derived
checkpoint. Use that index digest as observation-level `evidence_sha256`, then
hash the full policy/observation projection in the signed checkpoint. This order
avoids self-referential hashes. Resource/network/root facts still need independent
trusted observations. No relaxation of `network=none`, read-only actor root or
other gates is proposed. External signed checkpoints bind projection, quota/raw
hashes, admission receipt and actual lifecycle checkpoint, without adding keys to
closed v1 objects.

The main actor lifecycle retains its binding through
`scope → admit → execute → quiesce → score → seal → cleanup`. Quota phases and
challenges do not add, skip or repeat lifecycle stages. Restaging/recovery requires
fresh evidence and permitted lifecycle handling, never a consumed permission.

**Worker-binding mismatch requires an explicit contract decision.** The runner
document requests distinct trial bindings/manifests for workers or phases;
`eval.lifecycle_receipt._gate` always supplies the enclosing binding, including
snapshot worker runtime/preflight observations. Nesting a child-bound worker
receipt cannot satisfy both. Proposed future resolution: separately admit
preparation/snapshot workers using fresh child bindings; freeze an authenticated
parent/child scope/allocation map and extend lifecycle snapshot validation to
verify child bindings, policy/resources, destination scopes, actual artifact and
signed map. Parent score/seal and cleanup remain bound to the main trial. This
needs separate contract/code review and tests; current functions do not implement
it. Relabeling child facts with a parent binding or silently changing the lifecycle
binding is not a documentary workaround.

Scope sidecars allow only allocation/prestage/prestart phases. Collect fresh
worker scope records at supported phases and reference them through the external
snapshot index. Do not invent `snapshot_preflight` as a project/tmpfs record phase.
The proposed mapping and future lifecycle integration must resolve all worker
references; an external index alone is not accepted by existing code.

## Refusal and later completion criteria

Refuse unsigned/unknown-key/wrong-role statements, unresolved raw metadata, changed
digests, stale boot/challenges/sequences, allocation/lease/namespace mismatches,
incomplete inventory, missing dimensions, rounding, unknown backends, unsupported
writable roots, unbounded daemon/snapshot growth and incomplete cleanup. Map
authentication/shape failures to existing `invalid_evidence`, stale inputs to
`stale_evidence`, identity/ownership failures to their existing reason codes and
query failures to `observation_error`. Preserve bounded metadata without echoing
unchecked input; no new implemented reason codes are presumed.

Later review must establish protected enrollment/key custody, independent actual
collection, durable freshness/lease transactions, signature/semantic validator,
pre-staging runner wiring, worker-binding integration, snapshot growth bounds and
cleanup lifecycle. Offline contracts cannot establish live enforcement. Separately
authorized finite validation and independent review remain required. This document
authorizes no host change, trial, pilot or production H0.

## Documentation validation

Checks: source/schema fields and phases, role/signature/binding walkthrough, local
Markdown links, unchanged runtime/schema bytes and `git diff --check`. No runtime
tests or host queries are needed for this documentation change. The
[local reading companion](task-233-quota-readback-overview.html) summarizes roles
and sequence; this Markdown document defines the proposal.
