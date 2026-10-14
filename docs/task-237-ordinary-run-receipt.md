# Task 237 — ordinary-run receipt semantics

Status: **proposed documentation contract; no runtime integration or execution**.
Reviewed in `/tmp/hg-codex-237` at base
`0930d99cc882c5a049c98f9123e9427470e7e818`.

An ordinary run can provide useful local feedback without provisioning filesystem
quotas or claiming formal benchmark evidence. Its receipt must say what was
observed, what remains unknown, and which metric was computed. Quota availability,
sandbox availability, measurement validity and production authorization are
independent facts.

This proposal adds no driver mode, command-line switch, receipt writer or admission
exception. The [companion schema](task-237-ordinary-run-receipt.schema.json) and
[contract tests](../tests/quality/test_ordinary_run_receipt_codex237.py) describe a
future ordinary-run sidecar. Existing `run_meta.json` and `curve.jsonl` are not
silently upgraded to this format. No test or run was executed for Task 237.

## Running as an ordinary user

Ordinary use means an existing non-staged local workflow with the user's existing
permissions, dependencies and a supported sandbox. It does not require the user to
install project quotas, change mounts, configure the Docker daemon, enroll an
observer or obtain root merely to record local feedback. Those provisioning steps
belong to the separate formal runtime contract. This design does not promise that
every dataset or sandbox works on every unprivileged host.

Keep the requested sandbox: if it cannot start, record the failure and stop that
attempt. Do not silently change sandbox choice to make an ordinary run proceed.
Recording an existing choice is not permission to disable required isolation.
Dataset/privacy, scorer, integrity, resource and execution policies still apply;
an ordinary label does not make a refused dataset runnable. Dependencies requiring
administrator setup remain unavailable until a supported environment exists.

For a host already supporting the ordinary workflow, the absence of a complete
filesystem-quota backend is recorded as `false` or `"unknown"`, rather than asking
the user to administer the host or pretending that quotas passed. A known ordinary
measurement may still be displayed locally with the required non-production
label. Formal diagnostic/pilot admission remains blocked wherever its gates are
not satisfied. Task 237 itself authorizes and performs no execution.

## Receipt identity and use

The proposed filename is `ordinary_run_receipt.json`, with schema discriminator
`harnessgrad.ordinary-run-receipt.v1` and `run_kind="ordinary"`. Create a fresh run
ID; preserve incomplete receipts and corrections as separate immutable artifacts.
Never overwrite, resume, rename or wrap an ordinary receipt to impersonate a
staged receipt. Hashes bind bytes; they do not authenticate the observer.

Every receipt, displayed score, export and plotted series must retain this exact
label and the following explicit flags:

> NON-PRODUCTION ORDINARY RUN — NOT FORMAL BENCHMARK EVIDENCE

- `evidence_class="non-production"`.
- `production_authorized=false`, `formal_benchmark_evidence=false` and
  `publication_ready=false`, including when every local measurement succeeds.
- `record_origin="illustrative"` for authored examples/tests, or `"observed"` only
  for an actual ordinary run. Examples never become observed evidence by passing
  schema validation.

`publication_ready=false` prohibits formal benchmark publication; a clearly
labelled local diagnostic display is allowed by this proposed contract. Neither
the schema nor these flags constitutes an authorization mechanism. Existing
`harnessgrad.store.certify` checks readability/platform identity/integrity; its
`valid` or `certified` result is not production authorization, quota attestation,
official metric equivalence or formal benchmark eligibility.

Formal consumers must require their own supported schema, trusted observations,
dataset gates, complete lifecycle evidence and separate review. In particular,
[diagnostic v2](../eval/diagnostic_receipt.schema.json) and
[staged policy](../eval/policy/diagnostic_policy.py) do not accept this schema. Even fully
known ordinary provenance or a successful local zero does not authorize H0,
pilot expansion, a leaderboard submission or merging into a formal result table.
A future formal attempt needs fresh identities, gate review and execution under
the applicable contract; it cannot retroactively relabel an ordinary attempt.

## Filesystem quota and sandbox facts

`filesystem_quota.enforced` describes **complete per-run byte and inode hard-limit
coverage for every writer and writable surface**, including preparation, actor,
verifier, workspace, temporary storage, logs, snapshot/export and evidence writes.

| Value | Meaning | Consequence |
| --- | --- | --- |
| `false` | At least one required surface/dimension is known to lack enforcement, or the selected ordinary backend explicitly provides none. | Local use may continue under applicable ordinary policies; no complete quota claim. A concrete reason is required. |
| `"unknown"` | Inventory, backend observation, effective limits or evidence is missing, unreadable or stale. | Preserve uncertainty and the reason. Neither known enforcement nor known absence is established. |

This v1 proposal represents ordinary paths without verified complete quota
coverage; it cannot express `true`. A later supported enforcement claim needs a
separately reviewed contract and fresh evidence, and still cannot itself grant
production authorization. A requested limit, quota flag, available disk capacity,
snapshot preflight, cgroup memory bound or sandbox success proves neither byte
nor inode quota enforcement. Known partial coverage is `false`; incomplete
knowledge with no established gap is `"unknown"`. Do not coerce `null`, missing,
`0`, `"false"` or `"unknown"` through a truthiness test.

`limits.resource` and `limits.budget` record requested values with units in their
keys, or null if unavailable. They are declarations, not effective observations.
For quotas, record both requested `bytes` and `inodes` independently as positive
integers or null; these fields never establish enforcement. No disk-fill, inode
exhaustion or privileged probe is needed or prescribed to populate an ordinary
receipt. See the [formal backend requirements](filesystem-quota-backends.md).

Record `sandbox.host` and `sandbox.task` separately. Each has `requested`,
`effective`, nullable `plan_version` and a nonblank explanation in `detail`.
Values are `bwrap`, `container`, `none` or `unknown`. For example, host-side bwrap
and a container task boundary can coexist; neither implies the other was active.
An effective value requires a current observation for that boundary. Configuration
alone supplies only the requested value; absent effective evidence is `unknown`.
For a known requested choice, the effective value must match or remain unknown;
a failed request cannot become a successful different boundary in the same receipt.
Legacy metadata that lacks a boundary is unknown, not automatically `none` or
active. Plan version, image identity and evidence limitations belong in the
receipt's provenance and comparability notes. No sandbox choice establishes quotas
or production authorization, and different boundaries are not silently comparable.

## Measurement, lifecycle and coverage

Each selected `(task_id, trial)` has exactly one outcome; trials are numbered
`1..trials`. Persist missing attempts as unmeasured with a reason. Reject duplicate,
unselected or out-of-plan rows rather than counting them twice. The entire frozen
selection is retained, including tasks that never started.

| Outcome | Required score/reason | Meaning |
| --- | --- | --- |
| `measured` | Finite number, including a genuine `0`; `reason=null`. | Execution and the named local scorer completed with a usable metric result. |
| `invalid` | `score=null`; nonblank reason. | A known integrity, execution or measurement-contract violation invalidated the attempt, such as an observed timeout or runtime failure. |
| `unmeasured` | `score=null`; nonblank reason. | No usable measurement: not started, missing verdict, provider/scorer unavailable, unknown completion, or cached evidence without a fresh trial. |

An ordinary `measured` outcome is local evidence only. A process exit code or a
boolean pass flag cannot substitute for the scorer's metric result. A failed
answer with a successfully completed valid scorer can be a measured zero; a
provider, scorer, timeout, snapshot or cleanup failure cannot. Preserve original
failure stage and reason; do not resolve a known invalid state into unmeasured
just because a later stage lacks evidence.

`coverage` records eligible tasks (nullable only when unknown), selected task
count, expected task-trials and the disjoint measured/invalid/unmeasured trial
counts. Selected count equals the number of unique selected IDs; expected count
equals selected count times planned trials; the three outcome counts sum to
expected. A known eligible count must be at least selected count. Unknown
eligibility is explained in comparability notes. This proposal does not change
staged task selection or trial/concurrency policy.

`cleanup` and `snapshot` each contain `status` and `detail`. Status is `passed`,
`failed` or `unknown`; snapshot alone also permits `not_required`, with an explicit
reason when no snapshot/export operation was planned. A command returning success
without observing owned-resource absence is not passed cleanup. An unattempted or
failed snapshot cannot be disguised as not required. These are local summaries,
not substitutes for formal runner/lifecycle attestations.

The top-level status and aggregate `score` follow this order:

1. Any invalid outcome or failed cleanup/snapshot makes the receipt `invalid`.
2. Otherwise, any unmeasured outcome or unknown cleanup/snapshot makes it
   `unmeasured`.
3. Otherwise it is locally `measured`, with cleanup passed and snapshot passed or
   genuinely not required. Its score is the arithmetic mean over **all planned
   task-trials**. This v1 contract supports only that aggregation.

For invalid/unmeasured receipts the aggregate score is null. Original measured
outcome rows can be retained for debugging, under the same non-production label,
but must not be promoted to a successful aggregate. There is no measured-subset
mean, failure-to-zero conversion or success inferred from cleanup alone. Known
missing quotas by themselves are not invalid ordinary measurements; they remain a
separate explicit limitation that prevents formal use.

Scores and numeric declarations must be finite JSON numbers, excluding booleans,
NaN and infinities. Counts, trial indices, quota quantities and plan versions use
integer encodings, excluding booleans and float encodings such as `1.0` even where
JSON Schema treats the latter as integral. Metric-specific ranges remain part of
the named scorer's contract; a generic receipt must not assume every metric is a
fraction in `[0, 1]`.

## Metric identity, provenance and comparison

`metric` is required on every receipt, even when its score is null. Its identity
includes `id`, `name`, `scorer_sha256`, `unit`, `direction`, `aggregation` and
`official_equivalence`. Use a versioned local ID rather than a generic `accuracy`
label. The ID's definition specifies range, normalization, denominator, task/trial
unit and scorer version. `unit` distinguishes fractions from percentages;
`direction` is higher/lower; aggregation is
`arithmetic_mean_all_planned_task_trials`. The scorer hash is a 64-character
lowercase SHA-256 when available, otherwise null with a comparability explanation.
Unknown scorer provenance is never replaced by a model name or an example hash.
If the metric definition itself is unavailable, no usable score exists: retain a
versioned unresolved metric ID and unmeasured outcomes, describing the gap.

`official_equivalence` is `unverified` or `different`. An ordinary score must not
claim official equivalence based on its name, a plausible scale, an imported
package or passing synthetic tests. AppWorld task and scenario completion, for
example, have different denominators; a fraction and a percentage also cannot be
silently combined. Metrics requiring a different aggregation need a future
reviewed extension, not a misleading arithmetic-mean label.

Record dataset/side, source/split/manifest/model/harness hashes, platform hash,
one endpoint binding or null for model-free/unknown, requested resource/budget
limits, and nonempty comparability notes. Unknown hashes are explicit nulls, not
fabricated all-zero values. Notes distinguish model-free from an unknown model,
and include selection, seeds, trials, metric/scorer differences, sandbox, quota
coverage, missing lifecycle facts and incomplete provenance. Hash recipes and
artifact inventories must be preserved when hashes are supplied. No task payload,
private answer, credential or unrestricted log belongs in this metadata sidecar.

Even local comparisons require matching metric definition/unit/aggregation,
selection, split, trials, scorer, model, harness/platform, sandbox and relevant
resource conditions, or an explicit account of differences. Unknown identity
blocks a comparability claim; two null hashes are not evidence of equality.
Reports and charts must keep ordinary results separate from formal evidence,
retain coverage and limitation labels, and never treat omitted trials as zero.

## Illustrative receipt — no run occurred

All IDs below are authored examples. Null provenance and unknown observations
are intentional. The one planned example cell is unmeasured; no score, endpoint
call, runtime resource or cleanup observation is claimed.

```json
{
  "schema": "harnessgrad.ordinary-run-receipt.v1",
  "run_kind": "ordinary",
  "evidence_class": "non-production",
  "label": "NON-PRODUCTION ORDINARY RUN — NOT FORMAL BENCHMARK EVIDENCE",
  "record_origin": "illustrative",
  "production_authorized": false,
  "formal_benchmark_evidence": false,
  "publication_ready": false,
  "run_id": "illustrative-task-237-no-run",
  "dataset": "illustrative-local-dataset",
  "side": "train",
  "trials": 1,
  "selected_task_ids": ["illustrative-cell"],
  "metric": {
    "id": "illustrative.local-completion.v1",
    "name": "Illustrative local completion; range 0..1; one task-trial per cell",
    "scorer_sha256": null,
    "unit": "fraction",
    "direction": "higher",
    "aggregation": "arithmetic_mean_all_planned_task_trials",
    "official_equivalence": "unverified"
  },
  "hashes": {
    "source": null, "split": null, "manifest": null,
    "model": null, "harness": null, "platform": null
  },
  "endpoint": null,
  "limits": {"resource": null, "budget": null},
  "filesystem_quota": {
    "enforced": "unknown",
    "requested": {"bytes": null, "inodes": null},
    "detail": "No backend inventory or enforcement observation; no run occurred."
  },
  "sandbox": {
    "host": {"requested": "unknown", "effective": "unknown", "plan_version": null,
             "detail": "No host sandbox selected or observed."},
    "task": {"requested": "unknown", "effective": "unknown", "plan_version": null,
             "detail": "No task boundary selected or observed."}
  },
  "coverage": {
    "eligible_tasks": null, "selected_tasks": 1, "expected_task_trials": 1,
    "measured_trials": 0, "invalid_trials": 0, "unmeasured_trials": 1
  },
  "outcomes": [
    {"task_id": "illustrative-cell", "trial": 1, "status": "unmeasured",
     "score": null, "reason": "Authored documentation example; no execution."}
  ],
  "cleanup": {"status": "unknown", "detail": "No resources or absence observations."},
  "snapshot": {"status": "not_required", "detail": "No snapshot or export planned."},
  "status": "unmeasured",
  "score": null,
  "comparability_notes": [
    "Illustrative only: no eligible pool, source, split, manifest, scorer or runtime observations.",
    "No model is used: model hash and endpoint are null; harness/platform hashes are unknown.",
    "No seed or execution; one illustrative selected cell/trial; sandbox and quota coverage unknown.",
    "No cleanup evidence; no official equivalence or cross-run comparability established."
  ]
}
```

## Validation and implementation boundary

The JSON Schema checks shape, closed fields, explicit flags and basic state
constraints. Semantic contract tests additionally check complete unique
task/trial coverage, counts, failure precedence, numeric encodings and aggregate
arithmetic. Production readers/writers must implement those
semantic checks in a separate reviewed change; neither schema validation nor the
test-only oracle supplies observations, enforces quotas or labels existing UI.

The tests exercise authored data only and import no driver, scorer, adapter or
runtime. They also check that an ordinary discriminator is rejected by the existing
staged schema. They were **authored but not executed** for this task, as requested.
Source/diff review is not a passing test receipt. No benchmark, provider, model,
GPU, Docker, host probe, admin change or runtime cleanup was performed.
