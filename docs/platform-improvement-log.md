# Platform Improvement Log

This index tracks reusable platform capabilities learned while onboarding datasets. Dataset entries belong in `docs/adapter-integration-journal.md`; this file records the capability that future adapters should reuse.

The source-only [dataset blocker registry](dataset-blockers.md) indexes current
work separately from historical outcomes. Historical pilot sizes below are
records of earlier protocols; current planning follows AGENTS.md's one-task
diagnostic and separately reviewed 30-task/one-trial temporary-rerun cap.

## How to use this log

Every platform improvement must record:

- the failure or repeated need that motivated it;
- the shared contract it adds or changes;
- the datasets that exposed it;
- tests or controls that validate it;
- rollout status: `planned`, `isolated`, `merged`, or `deferred`;
- the commit that introduced it.

Do not merge a dataset-specific runner when a shared lifecycle, evidence envelope, resource policy or endpoint contract can express the need.

## Capability index

| Capability | First evidence | Current state | Reuse rule |
|---|---|---|---|
| Dataset-specific oracle/noop controls | QA, ALFWorld, Bird, DS1000 | merged | Run oracle and noop before H0; keep measured zero separate from unreachable scorer |
| Declared split and split digest | GSM8K, QA family | merged | Record `split_source` and `split_sha`; never call imposed splits official |
| Structured evidence envelope | FEVER, HotpotQA, Bird, GAIA planning | merged/under review | Evidence can say measured, unmeasured or invalid; missing evidence is not score zero |
| Deterministic capped pilot selection | ScienceWorld integrity failure | merged in `d10b387` | Default new pilot is `min(50, ceil(10% * eligible side))` before task execution |
| Trial-aware score and spread | H0 QA pilots | merged | Record every trial, mean and spread; do not confuse mean-of-trials with pass@k/Pass^k |
| Fresh task workspace and stale verdict cleanup | QA, ALFWorld, Terminal planning | merged/under review | Each attempt owns fresh state, verdict paths and cleanup evidence |
| Platform integrity boundary | ScienceWorld v4 | isolated patch | Hide platform before execution; read-only platform mounts; fail closed on writes |
| Invalid/unmeasured classification | Hotpot timeouts, Bird SQL, runtime review | isolated patch | Verifier timeout, missing reward, malformed evidence and scorer crash do not become ordinary zero |
| GPU/endpoint registry | GPU0/GPU1 imbalance | isolated patch | Bind run/role to endpoint/GPU UUID; allocate new runs least-loaded; keep old runs sticky |
| Endpoint/budget request correlation | allocator recovery review | isolated repair | Persist budget request and endpoint attempt IDs; reconcile idempotently |
| GPU utilization evidence window | GPU1 idle question | isolated design | Use fresh multi-sample windows, request counters and attribution; one zero sample is unknown |
| Shared runtime lifecycle | AppWorld/GAIA/tau/Jericho/Terminal | planning | `SCOPE_CHECK -> ADMIT -> RESTORE -> READY -> EXECUTE -> QUIESCE -> SCORE -> SEAL -> CLEANUP` |
| Resource and disk admission | Terminal-Bench/Docker root | planning | Reserve CPU, RAM, process, disk, inodes and evidence space before launch |
| Runner enforcement and cleanup receipt contracts | Terminal-Bench quota gap / GAIA snapshot failure | isolated | Require actual byte/inode limits, phase resource bounds and exact owned absence; synthetic passing receipts grant no H0 authorization |
| Public/reference coverage boundary | LiveCodeBench/AppWorld/GAIA | planning | Authored references are coverage facts, not official gold; public-only train policy stays explicit |

## Detailed records

### C-001 — Deterministic capped pilots

- Trigger: ScienceWorld completed a large 10% pilot before platform integrity failure was discovered.
- Contract: select by SHA-256 task ID rank before setup/image admission/H0; choose `min(50, ceil(10% * eligible side))`.
- Validation: boundary checks for 1, 9, 50, 118, 492 and 6913 eligible tasks; GSM8K tests still pass.
- Commit: `d10b387 platform: cap early pilots and parse GSM8K decimals`.
- Status: `merged`.

### C-002 — Decimal-aware GSM8K scoring

- Trigger: upstream integer-only extraction maps `3.5` to `5` and `18.0` to `0`, contradicting the task contract.
- Contract: use a decimal-aware extractor; record scorer identity as `decimal-aware-extract`; retain old archive identities unchanged.
- Validation: 18 focused scorer/evidence tests passed.
- Commit: `d10b387 platform: cap early pilots and parse GSM8K decimals`.
- Status: `merged`.

### C-003 — Platform integrity prevention

- Trigger: ScienceWorld v4 completed 354/354 but emitted `harness modified the platform`.
- Contract: prevent writes before execution through platform hiding/read-only mounts; detect and invalidate any remaining change; keep `base_harness` as subject code, not platform code.
- Validation: 52 isolated tests passed in `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/81`; patch apply checks passed; no production rollout yet.
- Candidate: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/81/patch.diff`.
- Status: `isolated`.

### C-004 — Measurement validity

- Trigger: Hotpot timeouts, Bird database failures, missing verifier evidence and scorer/runtime failures.
- Contract: separate `valid score`, `unmeasured`, `invalid`, `timeout` and `cleanup failure`; only a trusted verifier can produce a numeric zero.
- Validation: runtime prototype and adversarial review; known production gaps remain in host/exec/snapshot paths.
- Candidate: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/75/patch.diff` plus `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/71/prototype.patch`.
- Status: `isolated`.

### C-005 — Endpoint/GPU allocation

- Trigger: both long-running drivers were bound to GPU0/8001 while GPU1/8002 sat unused.
- Contract: registry identity includes endpoint URL, GPU UUID, host, run and role; bindings are sticky; new runs use least-loaded/round-robin allocation; health and usage remain evidence-based.
- Validation: 78 allocator tests and 36 observability tests passed; no live migration performed.
- Candidates: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/72/endpoint_registry.patch`, `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/78/observability.schema.json`.
- Status: `isolated`.

### C-006 — Budget and endpoint recovery

- Trigger: repeated reconcile could release one reservation twice; endpoint IDs did not correlate with budget attempts.
- Contract: terminal reconciliation is idempotent for matching evidence; conflicting evidence is rejected; unknown execution preserves reservations; request/attempt IDs persist across restart.
- Validation: 105 offline tests passed.
- Candidate: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/83/patch.diff`.
- Status: `isolated`.

### C-007 — Shared runtime lifecycle

- Trigger: AppWorld, GAIA, tau-bench, Jericho and Terminal-Bench each exposed similar reset, service, network, scorer and cleanup risks.
- Contract: one platform lifecycle and seven controls, with adapter data limited to declarations and fixtures.
- Validation: 18 document checks, 42 synthetic shared-control tests; real runtime gates remain open.
- Reference: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/74/launch-gate-checklist.md`, `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/80/schedule.md`.
- Status: `planned`.

### C-008 — Offline runner enforcement and bounded receipts

- Trigger: the cached-pilot reservation ledger does not enforce writable disk/inode quotas; GAIA snapshot failure exposed missing snapshot/resource closure.
- Contract: `eval.runner_admission` checks trusted observations against frozen runtime, no-network, byte/inode, snapshot and cleanup policies. Receipts bind adapter/run/trial/manifest, retain policy/observation hashes and stay at most 16 KiB. Cleanup uncertainty requests quarantine and capacity retention.
- Known-fault repair: byte-only Docker snapshot preflight now refuses malformed/nonpositive limits, negative sizes, unknown roots and query failures; receipts expose maxima, reserves, deadlines and `quota_enforced=false`.
- Validation: fabricated facts and fake Docker only; focused command and results in `runner-admission-codex-158-report.md`.
- Reuse: [runner admission contract](runner-admission-contract.md); backend observer/enforcement, atomic lease integration, snapshot worker limits and complete owned cleanup still require independent verification.
- Status: `isolated`; no production runner wiring or filesystem quota installation; no Docker/model/H0/heldout execution.
- Commit: accompanying `platform: add offline runner quota and cleanup admission contracts` commit.

### C-009 — Filesystem quota backend source audit — Codex 168

- Trigger: distinguish enforceable byte/inode quotas from capacity observations and supplied admission facts.
- Finding: no complete backend is connected to bwrap/files, Docker exec or harness/method workspaces. Bounded tmpfs exists only in separate control/helper paths; no live kernel enforcement was inspected.
- Contract: [backend audit](filesystem-quota-backends.md) specifies XFS/ext4 project hard quotas, bounded tmpfs, driver/snapshotter integration, pre-staging allocation, trusted read-only effective-limit observations, fail-closed runner wiring and verified scope cleanup.
- Validation: 252 existing synthetic runner/artifact contract tests passed, with real subprocess/network execution denied; [report](../filesystem-quota-codex168-report.md), [source hashes](../filesystem-quota-codex168-source-evidence.json) and [output](../filesystem-quota-codex168-test-result.txt).
- Status: `documented_blocker`; documentation only, no detector or runtime source change; no mounts, quota operations, Docker daemon queries, model/H0 or benchmark. Production quota enforcement remains unsupported.

### C-010 — Source-only blocker registry and historical preservation — Codex 178

- Trigger: blocker evidence is spread across the adapter journal and source audits, while later repairs can obscure incomplete historical runs.
- Contract: [registry](dataset-blockers.json) keeps `demand x surface` separate from `exercises`, expands shared blocker references, and records explicit work status/evidence/action for every publishable declaration. A separately pinned baseline preserves 11 historical incomplete/partial/pending-review records with null effects.
- Datasets: all 28 declared datasets, including refused adapters and explicit gaps for datasets without specific journal entries.
- Validation: `tools/check_dataset_blockers.py` passes; **45** focused source-only tests cover totality, axis separation, evidence locators, historical deletion/reclassification/rescoring, duplicate run IDs and forbidden adapter/external/runtime access.
- Status: `isolated`; docs/index validation only. No production gate or execution authorization follows; external receipts remain unverified journal citations.
- Commit: accompanying focused blocker-registry docs/code/tests commit; parent review/merge pending.

## Commit discipline

Use small commits with a capability-oriented subject, for example:

```text
platform: cap early pilots before H0 execution
runtime: separate verifier timeout from measured zero
runtime: prevent harness writes to platform checkout
allocator: bind runs to GPU endpoint identities
adapter: add LiveCodeBench covered-train manifest
```

Each commit should update the relevant journal entry or add one. The commit body should include:

```text
Trigger:
Evidence:
Shared contract:
Validation:
Remaining gates:
```

A dataset result is not complete until the journal entry, manifest hash, run ID, archive status and validation command agree.
