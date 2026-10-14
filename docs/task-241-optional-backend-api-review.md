---
title: Task 241 — Optional backend API review
subtitle: Ordinary-user validation, explicit uncertainty, no production authorization
template: doc
theme: paper
lang: en
---

The current APIs can validate supplied evidence without administrator operations.
They do not implement an execution backend. Task 241 adds API documentation and
six synthetic checks; it changes no production code or receipt schemas.

## A Review findings

Reviewed base: `0930d99cc882c5a049c98f9123e9427470e7e818`.
Primary sources: `eval/scorer_backend.py`, `eval/lifecycle_receipt.py`, their
admission dependencies, and focused synthetic tests. The inherited task-221
report supplied context; current source and fresh tests established these results.

| Finding | Observed behavior | Integration consequence |
| --- | --- | --- |
| No administrator interface | Validators use supplied facts and readable projection bytes. They perform no provisioning or backend callbacks. | Keep ordinary-user validation available without sudo, daemon access or privileged groups. Actual rootless execution remains unverified. |
| Missing evidence stays unsuccessful | `None` observations remain unknown. Incomplete resource dictionaries remain blocked. Unknown quiescence cannot pass scorer preflight. | Preserve both refusal classes as unmeasured; never substitute declared facts or a zero score. |
| Preflight does not advance lifecycle | A refused check leaves the successful quiesce checkpoint unchanged. Passed progression cannot skip directly to cleanup. | Persist refusal, record an unknown/failed score attestation with empty facts, then attempt cleanup. |
| Publication differs from authorization | Complete lifecycle cleanup can enable structural publication; production authorization remains false. | A synthetic pass cannot authorize H0 execution or close production blockers. |
| Evidence associations remain external | Export lacks a trial/quiescence field; runtime inspection and enforcement lack a shared instance identity. | Define trusted associations, freshness and persistence before connecting an executor. |

This scoped contract review required no production implementation change.
The missing integration guide was the immediate documentation gap.

## B Delivered documentation and tests

[API contract](scorer-backend-lifecycle-api.md) documents all required preflight
inputs, trust ownership, return/refusal fields, stage order, lifecycle APIs,
ordinary-user behavior and unsuccessful cleanup handling. Existing scorer and
runner admission guides now link to it.

`tests/quality/test_optional_backend_api_codex241.py` adds six checks:

- One checks successful preflight and completed lifecycle with identity queries
  and privilege operations forbidden. Publication still leaves authorization false.
- Three check empty or incomplete resource observations stay blocked.
- Two compose unknown/blocked preflight refusal with explicit unsuccessful scoring
  and successful cleanup. Cleanup preserves uncertainty or failure.

The suite reuses authored local fixture bytes and fabricated observations.
Its imported guards forbid subprocesses and sockets.

Additional guards forbid identity queries, ownership changes and privilege changes. This verifies API
behavior; it does not prove host permissions, delegated enforcement or an actual
rootless runtime.

## C Tests needed before optional execution integration

| Needed contract or test | Current status |
| --- | --- |
| Disabled backend and missing optional dependencies cause no allocation, dataset access or fallback execution | No selection/configuration wrapper exists in these APIs; test the future wrapper. |
| Permission-denied observer access retains unknown/blocked status without prompting for privilege | Observation collection is external and unverified. |
| Export binds exact trial and quiescence; inspection and limits describe the same fresh runtime | Caller obligations; shared association fields are absent. |
| Frozen policy pins, ownership intents and checkpoints survive interruption atomically | Durable orchestration is external. |
| A delegated observer reads effective CPU/memory/PID/deadline and byte/inode enforcement | Supplied-value validation exists; actual enforcement remains unverified. |
| Snapshot completion and uncertain cleanup preserve reservations and quarantine | Pure lifecycle checks exist; deletion, namespace observation and ledger updates are external. |

Keep unavailable capabilities unmeasured. Operator provisioning belongs outside
the ordinary-user path. Any future executor needs separate integration review
and staged diagnostic evidence before expansion.

## D Validation and scope

Fresh validation returned **393 passed in 1.16s**, exit status zero:

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python -m pytest -q tests/quality/test_optional_backend_api_codex241.py tests/quality/test_scorer_backend_codex213.py tests/quality/test_lifecycle_receipt_codex177.py tests/quality/test_scorer_admission_codex173.py tests/quality/test_runner_admission.py --basetemp=/tmp/hg-codex-241/.pytest-tmp-codex241
```

`git diff --check` passed. Task-owned test fixture output stayed in the worktree;
cleanup removed it after validation. The task-241 HTML companion summarizes this report.

Work stayed in `/tmp/hg-codex-241`. No production execution, dataset reads,
model/provider requests, GPU calls, backend queries or host provisioning occurred.
This report and its tests grant no production authorization. Parent diff review,
merge and journal updates remain separate.
