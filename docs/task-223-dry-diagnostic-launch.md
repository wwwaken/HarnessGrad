# Task 223 — dry template for a future fresh diagnostic

Status: **planning only; launch blocked; no task selected; no execution authorized by this document**.
Reviewed 2026-10-14 in `/tmp/hg-codex-223` at base
`82459cfa6d16c323ca40f21db2daf597921aedb3`.

This review reads source and documentation only. It does not enumerate a dataset,
select a task, reserve a run ID or directory, inspect a backend, contact an endpoint,
run a scorer, or execute a model/H0. All future-run facts remain unknown. This
template is deliberately incomplete and must never be submitted as policy evidence
or represented as a diagnostic receipt.

## Current contract and launch blockers

| Reviewed source | Current behavior and implication |
| --- | --- |
| [Operating rules](../AGENTS.md), [driver](../driver.py), [selection](../eval/metrics.py), [staged policy](../eval/diagnostic_policy.py) | First diagnostic is one task and one trial after dataset gates pass. Staged runs require `trials=1`, `jobs=1`, `rounds=0`; the driver forces `improver="none"`. Selection ranks unique eligible IDs by SHA-256 of each ID, with ID as tie-breaker, before setup/H0. No selection is performed here. |
| `driver.main`, `save_policy_receipt` | Requires context bound to dataset/side, passing dataset gates and the configured live local agent endpoint. It copies supplied hashes/limits; it does not independently verify their provenance or enforcement. Dataset loaders precede narrowing, so early selection alone does not establish selected-only/privacy closure. |
| [Diagnostic schema](../eval/diagnostic_receipt.schema.json), `validate_receipt` | Schema `harnessgrad.diagnostic-receipt.v2` checks shape; Python additionally recomputes coverage/score, replays lifecycle and binds scope/outcomes/digests. A real diagnostic needs a positive eligible count and exactly one selected task with an explicit outcome. Empty selection in this document cannot be a valid receipt. |
| [Lifecycle](../eval/lifecycle_receipt.py), [admission contract](runner-admission-contract.md) | Immutable sequence: `scope → admit → execute → quiesce → score → seal → cleanup`. Supplied hashes bind facts but do not authenticate observers or grant production authorization. `production_authorized` stays `false`. |
| `driver.save_policy_receipt`, train/eval publication callbacks | The current driver always supplies unknown cleanup/snapshot and no lifecycle, even if a lifecycle is placed in the policy-evidence file. Otherwise measured scores become unmeasured/null; staged curve publication is refused. A trusted producer and its integration remain a launch blocker. |
| [Run metadata writer](../harnessgrad/records.py), driver metadata call | `run_meta.json` records declared context and planned coverage, separately from final receipt evidence. No operational `runs/` directory or `run_meta.json` was available in this worktree. This review covers the current writer contract, not a live run elsewhere. |

The [Codex 193 audit](../reports/staged-receipt-audit-codex193-report.md) and
[Codex 177 lifecycle review](../reports/lifecycle-codex177-report.md) provide historical
findings; the behavior above was rechecked against current source. Their synthetic
successes are not production evidence. No dataset is declared ready here.

## Copyable planning envelope

The keys under `receipt_fields` use the exact diagnostic field names. The outer
envelope and `planned_target` are documentation fields, not an accepted runtime
schema. Nulls mean unknown, and observed zeros count only the empty dry selection;
they are neither failures nor benchmark scores. Do not save this as
`staged_plan.json`, `diagnostic_receipt.json` or `run_meta.json`.

```json
{
  "document_kind": "task-223-dry-diagnostic-template",
  "execution_authorized": false,
  "planned_target": {
    "tasks": 1,
    "trials": 1,
    "jobs": 1,
    "rounds": 0,
    "max_total_h0_concurrency": 3
  },
  "receipt_fields": {
    "schema": "harnessgrad.diagnostic-receipt.v2",
    "run_id": null,
    "stage": "diagnostic",
    "trials": 1,
    "jobs": 1,
    "eligible_task_ids_sha256": null,
    "selected_task_ids": [],
    "context": {
      "dataset": null,
      "side": null,
      "metric": {
        "name": null,
        "scorer_sha256": null
      },
      "hashes": {
        "source": null,
        "split": null,
        "manifest": null,
        "model": null,
        "harness": null
      },
      "endpoint": null,
      "limits": {
        "resource": null,
        "budget": null
      },
      "gates": {
        "status": "unknown",
        "receipt_sha256": null,
        "detail": "No dataset chosen or production gates verified in Task 223."
      },
      "comparability_notes": [
        "Dry planning only; no selected task, trial, score or comparable measurement.",
        "Future diagnostic scope and all provenance, metric and enforcement evidence are pending."
      ]
    },
    "coverage": {
      "eligible_tasks": null,
      "selected_tasks": 0,
      "expected_trials": 0,
      "measured_tasks": 0,
      "invalid_tasks": 0,
      "unmeasured_tasks": 0,
      "measured_trials": 0,
      "invalid_trials": 0,
      "unmeasured_trials": 0
    },
    "outcomes": [],
    "score": null,
    "cleanup": {
      "status": "unknown",
      "receipt_sha256": null,
      "detail": "No execution or allocations; no cleanup observation or receipt collected."
    },
    "snapshot": {
      "status": "unknown",
      "receipt_sha256": null,
      "detail": "No execution; no snapshot/export completion observed."
    },
    "lifecycle": null
  }
}
```

## Exact future receipt fields and evidence

| Field path | Required future value or binding |
| --- | --- |
| `schema`, `run_id`, `stage`, `trials`, `jobs` | v2 schema above; a fresh single-directory-component ID; `diagnostic`, integer `1`, integer `1`. `rounds=0` is a driver argument, not a top-level diagnostic receipt field. Preserve every previous/incomplete run ID. |
| `context.dataset`, `context.side` | Nonempty adapter identity and `train` or `eval`, matching the driver arguments. Resolve the split before selection; eval also needs its source run/round provenance. |
| `context.metric.name`, `context.metric.scorer_sha256` | Exact metric/scorer version identity and SHA-256 of the pinned scorer closure. Supporting evidence must define score range/direction, aggregation, denominator, normalization and official-versus-local semantics. These descriptive details are evidence obligations, not additional schema-required metric keys. |
| `context.hashes.source` | SHA-256 bound to the exact dataset source/revision and acquired artifact inventory; retain the inventory and hashing recipe. |
| `context.hashes.split` | SHA-256 of the exact resolved split, tied to `split_source`; reconcile with `run_meta.split_sha`. `data.registry.split_sha` hashes JSON with sorted side members and sorted keys; it does not use compact receipt serialization. |
| `context.hashes.manifest` | SHA-256 of the frozen manifest, including policies and ownership intent; same value as `lifecycle.binding.manifest_sha256`. |
| `context.hashes.model` | SHA-256 bound to the exact model artifacts/revision and effective inference configuration, with a reproducible inventory. A model name alone is insufficient. |
| `context.hashes.harness` | SHA-256 of the exact harness content/configuration being measured, with its hashing recipe and checkpoint linkage. A Git commit label alone is insufficient. |
| `eligible_task_ids_sha256`, `selected_task_ids` | `eligible_digest` hashes the sorted unique full eligible ID pool using canonical receipt serialization. Later selection must equal `diagnostic_task_set(eligible)` and contain exactly one ID. Do not narrow the eligible pool using `--tasks` without recording that restriction and its denominator/comparability effect. No IDs or pool digest are chosen here. |
| `context.endpoint` | Exactly one of `http://127.0.0.1:8001/v1` (GPU0) or `http://127.0.0.1:8002/v1` (GPU1), matching effective agent configuration for the entire run. No endpoint is bound here. No paid endpoint. |
| `context.limits.resource`, `context.limits.budget` | Each is a nonempty flat map of named, finite, nonnegative numeric limits, or explicitly null while unknown. Names/units and mapping to enforced policies must be documented. The diagnostic schema fixes these two container names, not their inner keys; declarations alone prove no enforcement. See the checklist below for backend fields. |
| `context.gates`, `cleanup`, `snapshot` | Each requires the summary fields `status`, `receipt_sha256`, `detail`: status `passed`, `failed` or `unknown`; SHA-256 or null; nonblank detail. `passed` requires an actual hash. These are three separate evidence summaries. |
| `context.comparability_notes` | Nonempty list of nonblank strings. Record subset/denominator, split and seed, scorer deviations/version, model/configuration, harness/platform, endpoint/contention, sandbox/runtime, limits and missing evidence; explicitly identify incompatible historical results. A one-task/one-trial diagnostic does not estimate full-dataset performance or trial variance. |
| `coverage` | All nine keys in the template are required. Future `eligible_tasks=N>0`, `selected_tasks=1`, `expected_trials=1`. For both tasks and trials, `measured + invalid + unmeasured = 1`. Initial selected-but-unrun plan has unmeasured counts `1`, measured/invalid `0`; this empty dry template has no such trial. |
| `outcomes` | One row with exact fields `task_id`, `trial` (integer `1`), `status`, `score`, `reason`. `measured` requires finite numeric score and null reason; `invalid`/`unmeasured` require null score and nonblank reason. Missing results are unmeasured. Cached results are not fresh measurements. |
| `score` | Mean of measured outcome scores; null when none. Timeouts, provider/scorer/runtime/snapshot/cleanup failures must not become ordinary zero scores. A genuine measured zero still needs the full publication contract. |

All SHA-256 fields use 64 lowercase hexadecimal characters when known. Never
substitute zero-filled/example hashes or use this review's Git base as run evidence.
The schema permits some null provenance fields; launch readiness still needs real
pins and trusted evidence, and expansion explicitly rejects unknown hashes/limits.

Canonical receipt hashing is SHA-256 over UTF-8 JSON with sorted keys, compact
separators and `allow_nan=False` (`receipt_digest`). `scope_digest` binds exactly
`stage`, `eligible_task_ids_sha256`, `selected_task_ids`, and the full `context`.
Run/manifest binding is checked separately through lifecycle. Retain the objects and
hash recipes, not just digests; different serialization recipes are not interchangeable.

## Lifecycle, resource and cleanup checklist for the future operator

Every box below is pending. This is a future review checklist, not launch approval.

- [ ] Close selected-only/privacy and source/split provenance gates; pin the official
  scorer/dependency closure and any offline/network requirements; verify trusted
  runtime/verifier and artifact-only state export. Preserve `demand × surface`
  capability taxonomy separately from harness `exercises` coverage.
- [ ] Integrate a trusted lifecycle producer with actual runner observations and
  receipt publication. A field added to policy evidence, a synthetic fixture, an
  exit code, or a passing schema check cannot supply this integration. Resolve the
  current runtime gate's `network="none"` contract versus any required local-model
  relay/service network using an applicable supported contract before launch.
- [ ] Freeze a fresh ID, one endpoint, manifest and scope before execution. Verify
  both receipt directory and workspace parent are fresh; preserve conflicts and
  incomplete evidence. Acquire independent global ownership/concurrency evidence:
  total H0 concurrency `<=3`, this run `jobs=1`. The driver has no global lease.
- [ ] Record concrete resource/budget limits and units. Runtime admission policy
  has exact keys `resources`, `network`, `filesystems`; `resources` has
  `cpu_millis`, `memory_bytes`, `swap_bytes`, `pids`, `timeout_ms` (positive integers
  except swap may be zero). Each writable canonical path maps to `bytes`, `inodes`.
  Account for workspace, scratch, logs, exports and evidence storage.
- [ ] Independently observe runtime `binding`, `evidence_sha256`, `resources`,
  `resource_backend`, `timeout_backend`, `network`, `attachments`, `read_only_root`,
  `filesystems`. Resource backend must be `cgroup-v1`/`cgroup-v2`, deadline backend
  `host-supervisor`, root read-only, and each filesystem observation must include
  matching `bytes`, `inodes`, enforced `backend` (`tmpfs`/`project-quota`), distinct
  `scope_id`, `evidence_sha256`. Configuration flags and capacity preflight do not
  prove byte/inode enforcement.
- [ ] Pin the budget profile and ledger mapping to `context.limits.budget`, including
  applicable wall-time, request/call/retry, prompt/output/total-token and context
  caps. Record `budget.configured`, `profile_hash`, `ledger_path`, `run_id`,
  `arm_id`, `dispatcher_run_id`, `scope`, `counters` when the dispatcher is bound.
  Its enforcement is `trusted_dispatch_only`; arbitrary harness network/provider
  calls are not covered. Keep orchestration trials/jobs separate from provider calls.
- [ ] Prepare lifecycle exact top-level keys: `schema` =
  `harnessgrad.lifecycle-receipt.v1`, `binding`, `scope_sha256`, `state`, `status`,
  `events`, `publication_ready`, `production_authorized`. Binding has exactly
  `adapter_id`, `run_id`, `trial_id`, `manifest_sha256`, identical across evidence.
  Starting `state="scope"`, `status="passed"` means only structural scope validity;
  `events=[]`, `publication_ready=false`, `production_authorized=false`.
- [ ] Persist each transition checkpoint in order. Events have `stage`, `status`,
  `evidence`, `receipt_sha256`; at most six events and 128 KiB serialized lifecycle.
  `admit` and `cleanup` recheck original `policy`/`observed` facts. Other successful
  stages use attestations with exact fields `schema` =
  `harnessgrad.lifecycle-attestation.v1`, `binding`, `stage`, `status`,
  `receipt_sha256`, `facts`, `detail`.
- [ ] Execution facts: `exit_code=0` (integer), `oom_killed=false`, `timed_out=false`.
  Quiesce facts add `running=false`. Score facts have `outcomes_sha256` over the
  normalized outcome rows. Seal facts have the same `outcomes_sha256` and nested
  `snapshot` attestation, with scorer inputs linked to the actual exported artifact.
- [ ] Snapshot completion facts have exactly `completed=true`, `artifact_sha256`,
  `exit_code=0`, `oom_killed=false`, `timed_out=false`, `preflight`, `runtime`.
  Preflight policy has `max_bytes`, `max_inodes`, `reserve_bytes`, `reserve_inodes`,
  `timeout_ms`; the observation has exactly `binding`, `evidence_sha256`, `writable_bytes`,
  `writable_inodes`, `free_bytes`, `free_inodes`, `running`, `exit_code`,
  `oom_killed`, `timeout_ms`, `device_id`. Require quiescence, capacity/reservations,
  worker runtime admission and actual completed bounded export. Preflight alone is
  insufficient; retain final artifact identity/size and owned-image cleanup evidence.
- [ ] Cleanup policy has `owned` and `timeout_ms`; each owned identity has `kind`,
  `id`, with intent persisted before allocation. Observation has `binding`,
  `evidence_sha256`, `objects`, `namespaces`, `timeout_ms`. Every exact object has
  `kind`, `id`, `absent=true`, `evidence_sha256`. `namespaces` covers `container`,
  `network`, `snapshot`, `volume`, `workspace`, each with `remaining=[]` and
  `evidence_sha256`, including kinds with no allocations. Successful removal alone
  does not prove absence. Unknown/refused cleanup retains quarantine/reservations.

Failed/unknown lifecycle stages may only attempt cleanup. A later successful cleanup
does not make a failed measurement publishable; cleanup is terminal and cannot resume
the run. Summary `cleanup.receipt_sha256` must equal the cleanup event's digest of
the checked admission receipt. Summary `snapshot.receipt_sha256` must equal the
digest of the nested completed snapshot attestation. An event's `receipt_sha256`
is the digest of checked evidence, distinct from an attestation's internal
`receipt_sha256` naming its supporting receipt.

## Future metadata and final review checklist

- [ ] Re-review source after blocker fixes; choose the dataset/side, verify all gates,
  establish eligible coverage and only then freeze one deterministic task. Planned
  launch arguments must explicitly be `sampling=diagnostic`, `trials=1`, `jobs=1`,
  `rounds=0`, fresh `run_id`, evidence file and roots; keep `improver=none`. No shell
  launch command is supplied or executed by Task 223.
- [ ] Reconcile `run_meta.json` identity fields `run_id`, `mode`, `harness`, `dataset`,
  `sampling_policy`, `trials`, `jobs`, `workspace`, `work_root`, `platform_root`,
  `sandbox`, `config`, `budget`, `env`, `agent_model`, `agent_backend`,
  `framework_version`, `method_entrypoint`, `improver`, `platform`. Confirm effective
  endpoint/seed/arguments through redacted `config`, and `split`, `split_declared`,
  `split_source`, `split_sha`, `oracle_source`, `oracle_coverage`; verify eval source
  linkage when applicable. `platform` includes `content_sha`, `git_sha` when available,
  and `dirty`; it is separate from the five context provenance hashes.
- [ ] Reconcile the exact `run_meta.diagnostic_policy` keys: `receipt_schema`,
  `eligible_tasks`, `eligible_task_ids_sha256`, `selected_tasks`, `selected_task_ids`,
  `expected_trials`, `trials`, `jobs`, `evidence_sha256`, `context`.
  `evidence_sha256` binds the full supplied policy-evidence object. This block records
  the plan, not final measured/invalid/unmeasured coverage or lifecycle completion.
  `_write_run_meta` omits fields passed as null; metadata absence is not a pass.
- [ ] Preserve the exclusive initial `staged_plan.json` and separate final
  `diagnostic_receipt.json`. A post-plan exception may leave only the plan; direct
  exclusive writes are not crash-atomic/fsynced. Preserve partial files and progress
  artifacts, and record failure evidence separately without overwriting/resuming.
  Progress scores or `complete=true` cannot substitute for the final receipt.
- [ ] Before publication, check schema **and** `validate_receipt`, verify actual
  eligible pool/selection and independently authenticate evidence origin. Require
  passing gates, snapshot, cleanup and replayed lifecycle with exact scope/outcome
  hashes. Keep invalid/unmeasured counts and comparability notes visible. A completed
  structural lifecycle still has `production_authorized=false`.
- [ ] Before any expansion, obtain a separate review with exact fields
  `approved=true`, `reviewer`, `reviewed_at`, `receipt_sha256`, bound to the entire
  valid measured diagnostic. `require_review` also requires the same eligible pool,
  dataset/side, metric, five hashes, endpoint, limits and gates; all provenance/scorer
  hashes and both limit maps must be known, `measured_trials=1`,
  `invalid_trials=0`, `unmeasured_trials=0`, with a fresh expansion ID. Review
  comparability notes explicitly. Temporary blocked/incomplete reruns may then use
  `min(30, ceil(0.10 * eligible))`, `trials=1`, `jobs=1`, `rounds=0`. Do not revert
  to the historical 50-task cap/three-trial protocol or infer authorization here.

## Task 223 validation

Completed documentation-only checks on 2026-10-14:

- A standard-library-only `python3 -` checker parsed the embedded JSON, matched all
  14 top-level receipt keys and nested required keys against the schema, verified
  the empty dry-state invariants and intentional non-receipt state, checked all
  10 staged metadata-policy keys against the driver's AST, and resolved all 11 local
  links (including the journal entry). Passed.
- `git diff --check` passed. Final change scope is this Markdown document and its
  journal entry; no source/schema/runtime changes.
- A filename-only inventory including ignored files found no `run_meta.json` in
  this worktree. No external run store was inspected.

No runtime module, dataset loader, test suite, driver or endpoint was invoked.
