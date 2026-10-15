# Offline scorer admission API

`eval.admission.scorer_admission` is the public facade for task-independent sealed scorer
bundles and task-bound artifact runtime admission. It validates local bytes and
supplied observations without creating or executing a runtime. Existing
`eval.admission.scorer_bundle` and `eval.admission.artifact_admission` entry points and successful
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
backend obligations. Dataset-specific production evidence remains unverified.

The opt-in pristine execution path additionally records `source_observation`:
bounded allowlisted-file metadata and SHA-256 probes before export and after
scorer cleanup, with the export bytes compared to the first probe. A detected
difference or unavailable final probe prevents a measured score. Its statuses
are `no_change_observed`, `difference_observed`, and `probe_unavailable`;
`quiescence_established` is always false. These are endpoint observations of
selected regular files, not continuous monitoring, a filesystem-wide snapshot,
or same-UID writer exclusion. In particular, a transient directory substitution
can restore the original file inodes before the final probe and evade detection.
Trusted source custody remains required. `execution_binding` records the task
contract and generated runtime/export UUID, whether a selected task was checked,
and explicitly missing outer-run/trial inputs (`outer_run_trial_binding` is
`not_provided`). Those inputs still need an execution-enforced backend contract.

For optional backend composition, ordinary-user access, lifecycle progression and
preflight refusal handling, see the [scorer backend and lifecycle API](scorer-backend-lifecycle-api.md).

## Per-bundle isolation (option B)

The pristine contract is an isolation class, not a global execution requirement.
The verifier reads `VERIFY[task_id]["scorer_bundle"]["isolation_class"]`.
Terminal-Bench and AppWorld declare `snapshot-service`, preserving their snapshot,
dependency-install network, service network and recording mounts. Existing native
commands and answer checks keep working; their executed classes are
`actor-workdir` and `in-process`. A missing declaration is recorded as `unknown`
separately from the class established by the executed route. A missing observation
also stays `unknown`. Neither becomes pristine by default.

For reusable sealed bundles, `harnessgrad.scorer-bundle.v2` adds the required
`isolation_class` field to the v1 fields. It accepts `pristine-offline` and
`snapshot-service`; pristine still requires a pinned image and `network="none"`.
The declaration participates in the bundle digest. V1 manifests, receipts and
strict offline admission helpers retain their existing semantics. A v2
snapshot-service declaration cannot enter an artifact-only runtime check.

An opt-in pristine command verifier declares:

```python
"scorer_bundle": {
    "isolation_class": "pristine-offline",
    "manifest": "/platform/scorer/bundle.json",
    "manifest_sha256": "<independently stored manifest SHA-256>",
    "root": "/platform/scorer/closure",
    "artifact_contract": "/platform/contracts/task.json",
    "artifact_contract_sha256": "<independently stored task contract SHA-256>",
}
```

The verifier's `argv` must equal the sealed scorer command. This backend supports
the exit-status (`exit0`) score protocol; reward-file and service checks retain
their existing backends. It verifies manifest and local closure bytes, binds the
task contract to the selected task and bundle, exports only bounded data-allowlisted
files, and creates a stopped Docker runtime with two read-only binds at
`/control-input` and `/control-scorer`. Writable scratch/output is contract-bounded
tmpfs. It inspects this instance and rechecks both projections before starting it;
an unexpected image, network or mount refuses execution. The stopped result and
container removal receipt accompany the verdict. Timeout, inspection, export and
cleanup failures remain unmeasured with null score. A completed failing check is
a measured zero. Existing runner policy admission remains in force.

`scorer_isolation_class` accompanies verdict, saved per-trial verdict, progress
score and curve point. `scorer_isolation_declared` retains the declaration beside
the observed class; pristine verdicts additionally carry
`scorer_isolation_evidence` (bundle/export/runtime/cleanup). Curve points include
`per_task_scorer_isolation`. Cache keys include explicit bundle declarations, and
cached trial classes are rechecked. Aggregation and curve writing refuse mixed
classes; cross-run comparisons require matching known classes and otherwise
name the reason, with no score/test-rate delta. Historical records remain readable
but their absent class cannot support a valid comparison.

These are topology and local integrity claims. Trusted pins, platform ownership,
quiescence through export, complete transitive image/ABI closure, official scorer
provenance, dataset-specific equivalence, trusted resource observation and live
cleanup evidence remain separate obligations. Synthetic controls are described in
[the option-B review](../reports/sb-option-b-review.md); they do not authorize H0.

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
