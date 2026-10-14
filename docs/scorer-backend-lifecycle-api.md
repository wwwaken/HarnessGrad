# Optional scorer backend and lifecycle API

This contract covers `eval.scorer_backend` and `eval.lifecycle_receipt`.
They are local Python validators, with no HTTP service, provisioning callbacks,
backend selection, administrator role or production execution route. Backend
integration is optional; every argument of `check_backend` is still required.
Installing or selecting a backend does not establish that its observations exist.

## Ordinary-user contract

Ordinary users must be able to import these APIs and check readable, caller-owned
fixture projections without root, sudo, a Docker socket, privileged groups or host
configuration changes. The APIs do not install cgroups, mount filesystems, set
quotas, authenticate an observer or collect runtime facts. Synthetic tests require
none of those capabilities.

A future execution integration must obtain enforcement and observations through
an independently trusted, already provisioned backend. Host provisioning belongs
to the operator, outside an ordinary user's run. Effective limits and observation
access may be unavailable on a rootless or delegated deployment. Report that
capability as unavailable and keep work unmeasured; do not prompt the user to
elevate privileges, substitute declared limits for readback, or fall back to an
unchecked local scorer. Rootless compatibility of a real backend is unverified.

When the optional backend is disabled, do not allocate resources, read datasets
or synthesize passing evidence. If a caller requests preflight with unavailable
evidence, pass the documented `None` inputs and retain the resulting refusal.
There is no `enabled`, `admin`, `rootless` or `authorized` input in the current API.
Any future configuration wrapper needs its own contract and tests.

## Scorer preflight

`check_backend(...)` takes these explicit, keyword-only inputs:

| Inputs | Trusted caller responsibility |
| --- | --- |
| `binding`, `scope_sha256` | Freeze adapter/run/trial/manifest identity and the pre-execution plan independently of incoming receipts. |
| `lifecycle_receipt` | Supply a replay-valid, passed `quiesce` checkpoint with that complete binding and scope. `None` means unavailable. |
| `bundle_raw`, `bundle_sha256` | Supply exact sealed scorer manifest bytes and an independently stored pin. |
| `contract_raw`, `contract_sha256` | Supply exact task contract bytes and its separate pin. |
| `closure_root`, `artifact_root` | Supply readable, platform-owned scorer and selected-only export projections; preserve their checked bytes through use. |
| `export_receipt` | Supply the task/contract/run-bound export receipt, or `None`. Keep the actor stopped and separately bind export to trial and quiescence. |
| `info` | Supply a fresh pristine runtime inspection in the existing artifact-admission shape, or `None`. |
| `runtime_policy`, `runtime_policy_sha256` | Supply the independently pinned resource/network/filesystem policy; policy may be `None` when unavailable. |
| `runtime_observed` | Supply independently observed effective enforcement for the same instance as `info`, or `None`. |

The check replays lifecycle first, validates resources second and scorer admission
third. Resource filesystems must exactly match the task contract's quota surfaces.
The runner gate accepts observed `cgroup-v1`/`cgroup-v2`, `host-supervisor`, isolated
network and enforced byte/inode quotas. Labels alone do not prove enforcement.
See [runner admission](runner-admission-contract.md) and
[scorer admission](scorer-admission-contract.md) for their closed input schemas.

The check reads only the supplied local projections. It does not export state,
invoke a scorer or backend, advance lifecycle, collect observations, persist
receipts, remove resources or update leases. It verifies projection bytes on each
call; a prior preflight receipt is not an accepted replacement for evidence.

A successful `harnessgrad.scorer-backend-receipt.v1` has `stage="preflight"` and
`status="passed"`. It records the binding, scope, lifecycle/export digests and
nested scorer/resource receipts. `measured`, `production_authorized`,
`execution_authorized` and `publication_ready` all remain `false`. No score is
returned. A pass establishes supplied-evidence consistency only.

## Missing observations and refusals

`ScorerBackendError` extends `scorer_admission.AdmissionError`; use `.code` and
`.receipt` to persist the fixed, sanitized reason. The receipt has the same false
flags as success, a failing `stage` (`lifecycle`, `resources` or `scorer`), and no
input evidence or score. Omitted keyword arguments raise normal Python
`TypeError`; optional integration does not mean optional trust inputs.

| Supplied evidence | Result with otherwise valid preceding inputs |
| --- | --- |
| `lifecycle_receipt=None` | `unknown`, `lifecycle_evidence_unavailable` |
| Valid lifecycle that has not passed quiescence, including unknown quiescence | `blocked`, `lifecycle_contract_refused` |
| `runtime_policy=None`, or `runtime_observed=None` with a matching policy pin | `unknown`, `resources_evidence_unavailable` |
| Supplied policy pin mismatch, even with no runtime observation | `blocked`, `resources_contract_refused` |
| Empty/incomplete resource observation, or unsupported enforcement backend | `blocked`, `resources_contract_refused` |
| Missing/incomplete export or pristine runtime inspection | `unknown`, `scorer_evidence_unavailable` |
| Unavailable local projection or projection file I/O | `unknown`, `scorer_evidence_unavailable` |
| Observed projection changes, inconsistent pins/identities or runtime boundary mismatch | `blocked`, at the validating stage |

This is a sequential check, not an aggregate diagnosis. An earlier refusal can
prevent inspection of later inputs. Missing fields do not uniformly map to
`unknown`: the resource validator conservatively blocks incomplete dictionaries,
while scorer observation gaps remain unknown. Both outcomes withhold measurement
and authorization. Do not turn either into a zero score, a pass or a retry using
fabricated observations. In particular, `running=false` without an observed
pristine `created` state is insufficient.

## Lifecycle API and failure handling

| Function | Meaning |
| --- | --- |
| `start_lifecycle(binding, scope_sha256)` | Return a new frozen `scope` checkpoint with no events. |
| `transition(receipt, stage, evidence)` | Replay the input and return an independent new checkpoint. |
| `validate_lifecycle_receipt(receipt)` | Replay event evidence; return `None` or raise on inconsistency. |
| `require_scope(receipt, *, run_id, manifest_sha256, scope_sha256)` | Validate and compare independently expected scope pins, including incomplete checkpoints. |
| `require_publication(receipt, *, run_id, manifest_sha256, scope_sha256, outcomes_sha256, cleanup_sha256, snapshot_sha256)` | Validate the completed lifecycle against this exact sealed publication. |
| `digest(value)` | Hash canonical JSON; this does not authenticate its origin. |

Successful progression is `scope → admit → execute → quiesce → score → seal →
cleanup`. Admission and cleanup use `{policy, observed}` runner evidence.
Execution, quiescence, scoring and sealing use exact lifecycle attestations:
`schema`, `binding`, `stage`, `status`, `receipt_sha256`, `facts` and bounded
`detail`. Passed attestations require stage-specific facts. Failed/unknown
attestations require empty `facts`; they may have a null receipt hash.

A scorer preflight receipt is neither a score attestation nor a lifecycle event.
If preflight refuses at a passed quiesce checkpoint, trusted orchestration must
persist its sanitized refusal and record an explicit `score` attestation with
`status="unknown"` for unavailable evidence, or `status="failed"` for a blocked
check, empty `facts`, and the refusal digest/detail. Then attempt cleanup using
independently collected cleanup observations. The pure APIs do not perform these
steps automatically. A malformed transition raises without changing the input;
preserve that failure separately instead of inventing a passing event.

After a failed/unknown stage, only cleanup may follow. Successful cleanup
preserves the earlier unsuccessful status and `publication_ready=false`.
Unproven cleanup yields a quarantine refusal and cannot release a lease; applying
that action atomically remains a backend obligation. Cleanup is terminal and
retries need a fresh run ID. Ordinary passed progression cannot skip from quiesce
straight to cleanup.

Seal requires matching outcome digests, completed snapshot artifact identity,
exit/OOM/timeout facts, snapshot preflight and snapshot-worker runtime evidence.
Only successful cleanup after seal makes `publication_ready=true`. That flag
means structural publication readiness; `production_authorized` remains `false`
even on the completed lifecycle. These functions never grant production H0
authorization or establish official scorer execution.

## Integration work still required

Before any real backend is connected, define and test its observer/instance and
export/trial associations, freshness, trusted storage, durable checkpoint and
ownership-intent persistence, deadlines, exact quota readback, snapshot completion
and cleanup/quarantine. Evidence digests prove none of those properties by
themselves. The current common binding also applies to nested snapshot-worker
facts; a distinct-worker binding proposal needs an explicit versioned contract,
as noted in the runner-admission documentation.

The offline suites exercise API semantics using authored fixture bytes and
fabricated observations. Task 241 adds privilege-operation guards, incomplete
resource observations and preflight-refusal-to-cleanup composition. Future
backend tests must separately cover disabled/missing optional dependencies without
allocation, permission-denied observation collection, same-instance provenance,
interrupted checkpoint persistence and uncertain cleanup. Those tests and a
separate measured diagnostic review are prerequisites, not evidence supplied by
the synthetic checks here.
