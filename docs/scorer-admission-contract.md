# Offline scorer admission API

`eval.scorer_admission` is the public facade for task-independent sealed scorer
bundles and task-bound artifact runtime admission. It validates local bytes and
supplied observations without creating or executing a runtime. Existing
`eval.scorer_bundle` and `eval.artifact_admission` entry points and successful
receipt schemas remain available.

## Checks and trust inputs

`validate_bundle(*, closure_root, bundle_raw, bundle_sha256)` authenticates exact
manifest bytes against the caller's independent pin and checks the platform-owned
tree against the exact declared file inventory, sizes and hashes. Its evidence is
the existing `harnessgrad.scorer-bundle-receipt.v1` receipt with scope
`local_declared_closure_integrity`. It has no task or export/quota policy.

`admit_runtime(*, bundle_raw, bundle_sha256, contract_raw, contract_sha256,
closure_root, artifact_root, export_receipt, info, run_id)` requires every argument
explicitly. The bundle and task contract each need their own trusted pin. Their
source hash, image identity and scorer declaration must agree before any local
tree is read. Export allowlists and quotas remain governed by the task contract.
Missing `export_receipt` or `info` may be represented by `None`.

Runtime admission rechecks the scorer tree once, rechecks the bounded data-only
projection and its task/contract/run receipt binding, then validates the supplied
pristine runtime observation using the existing runtime checks. Successful
evidence contains `bundle`, `runtime` and `run_id`. The two nested receipts retain
their separate pins and scopes, including `inspected_runtime_contract` for runtime
facts. Every call verifies local bytes again; a prior passing receipt is never an
input that authorizes skipping verification.

Trusted callers must keep pins outside actor-controlled state, own both projection
trees, quiesce sources, collect complete fresh runtime observations, and preserve
the checked bytes and boundaries through use. The facade cannot establish official
source completeness, image ABI completeness, observer authenticity, freshness,
ownership, CPU/memory/PID/deadline enforcement or cleanup. Those remain independent
backend obligations. Production adapter integration remains unverified.

For optional backend composition, ordinary-user access, lifecycle progression and
preflight refusal handling, see the [scorer backend and lifecycle API](scorer-backend-lifecycle-api.md).

## Receipts and refusals

Both checks return a JSON-compatible `harnessgrad.scorer-admission.v1` receipt with
`stage` equal to `bundle` or `runtime`, `status="passed"`, `measured=false`,
`production_authorized=false`, and scoped `evidence`. Passing this contract does
not close independent production blockers or measure a benchmark score.

A refusal raises `ScorerAdmissionError`, a subclass of the existing
`AdmissionError`, with `.code` and `.receipt`. Receipts retain the same schema,
stage and false flags, omit evidence and scores, and contain a fixed `reason`:

- `status="blocked"`, reason `bundle_contract_refused` or
  `runtime_contract_refused`: invalid seals/declarations, inconsistent identities,
  observed integrity changes or runtime/export/quota mismatches.
- `status="unknown"`, reason `bundle_evidence_unavailable` or
  `runtime_evidence_unavailable`: unavailable projection roots or file I/O,
  missing/incomplete export evidence or incomplete runtime observations.

Refusals do not echo input bytes, environment data or paths. The chained exception
retains the underlying diagnostic. Caller programming errors, such as omitted
required keyword arguments, continue to raise normal Python errors.

## Construction and legacy compatibility

The facade also exposes the existing `seal_bundle`, `load_bundle`, `load_contract`,
`export_state`, `verify_state_export` and `runtime_tmpfs` helpers. They retain their
existing signatures and return shapes rather than producing facade receipts.
Unavailable evidence, including a failed partial-export cleanup, now raises
`EvidenceUnavailable`, which remains catchable as `AdmissionError`. The facade
exports both types. A partial export retained after cleanup failure remains unknown
and must not be mounted, reused or treated as successfully cleaned up.

Both sealed loaders now use one exact-byte JSON loader and reject duplicate JSON
keys at any depth. Task contract duplicate-key acceptance is intentionally removed.
Synthetic controls in `tests/quality/test_scorer_admission_codex173.py` exercise
the public surface, pin independence, policy separation, legacy receipt parity,
one closure check per runtime call, repeat verification and blocked/unknown states.
They use inert local files, fabricated observations and guards against subprocess
or socket use. They provide no Docker, H0, heldout or production integration evidence.
