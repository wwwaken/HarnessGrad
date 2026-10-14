# Codex 158 — offline runner admission and bounded receipts

Implemented reusable resource, no-network, filesystem-quota, snapshot and cleanup
admission contracts in `/tmp/hg-codex-158`. **402 focused offline tests passed.**
Actual filesystem quota installation remains blocked; no production authorization
is implied by this change or by the synthetic passing receipts.

## Scope and findings

- Base commit: `8fcdcb80b90f43ab1c76c1f572c5cf70a6504e11`; isolated existing Codex worktree; date `2026-10-14`.
- The existing reservation ledger is cooperative capacity accounting, not disk/inode enforcement. Cached images and quota declarations cannot close that gap.
- The existing Docker snapshot preflight accepted negative writable sizes, silently defaulted malformed limits, inferred a Docker root when the response was empty, and omitted its maximum/reserve/deadline settings from the receipt.
- Work used supplied source and fabricated metadata only. Docker invocations, model/provider calls, H0 trials, benchmark trials and heldout reads: **0**. No dataset payload or endpoint was opened. Old receipts and inherited `report.md` were preserved.

## Changes

- `eval/runner_admission.py`: three adapter-independent checks, `admit_runtime`, `admit_snapshot`, `admit_cleanup`, backed by strict JSON-shaped policies and trusted observations.
- Runtime gate: actual CPU/memory/swap/PID/deadline bounds; inspected no-network state; read-only root; complete writable surface inventory; effective byte **and** inode limits; distinct quota scopes. Reservation-only, declaration-only, writable binds without quota evidence and unsupported backends refuse admission.
- Snapshot gate: quiescence, zero exit/no OOM, writable byte/inode maxima, free byte/inode reserves and exact finite deadline. Normalized receipts retain maximum, reserve, required and observed quantities. Snapshot worker resource enforcement remains a separate runtime gate.
- Cleanup gate: exact inventory and absence evidence for containers, networks, snapshots, volumes and workspaces; all five owned namespaces must be checked, even with no expected allocations. Any uncertainty requests quarantine; a verified receipt requests release. This module performs no deletion or ledger mutation.
- Receipts bind adapter/run/trial/manifest, hash policy and observations, are capped at 16 KiB under standard single-line JSON serialization, reject extra/private payload fields, and contain no score. They always say `measured=false`, `production_authorized=false`.
- `eval/container.py`: fail-closed repair for invalid limits/sizes/roots and query exceptions, explicit byte bounds and inspection/commit deadlines, and `preflight_only=true`, `quota_enforced=false`. Valid defaults and the existing commit deadline are retained.
- Contract documentation: [docs/runner-admission-contract.md](../docs/runner-admission-contract.md). Platform log and adapter journal contain isolated-status follow-up entries.

## Validation and review

Final command (all paths beneath this worktree):

```sh
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q \
  tests/quality/test_runner_admission.py \
  tests/quality/test_cached_pilot_admission.py \
  tests/quality/test_container.py::test_snapshot_admission_rejects_writable_layer_before_commit \
  tests/quality/test_container.py::test_commit_exit_137_is_classified_as_oom \
  tests/quality/test_container.py::test_commit_disk_and_resource_errors_are_classified \
  --basetemp=/tmp/harnessgrad-pytest-codex158-test-tmp-final-admission --tb=short
```

Result: **402 passed in 5.36s**, comprising 200 new synthetic tests, 199 existing
persistent reservation/cleanup regressions and three existing snapshot failure
controls. New tests deny real subprocesses, sockets and Docker calls; all Docker
results are fakes. The cached admission suite also denies real execution. The three
selected existing snapshot tests mock every relevant Docker entry point.

An initial test run had a missing basetemp parent and an undersized receipt-limit
fixture; both test setup issues were corrected. The corrected interim suite passed
371 tests; final validation includes the additional policy/evidence regressions.
No failed test attempt was reported as a benchmark score or production gate.

Review covered the complete focused diff, refusal behavior, deterministic/input
immutable receipts, bounded output, stale binding rejection, distinct filesystem
quota scopes, byte/inode boundary equality, unknown cleanup retention, and backward
compatibility of valid snapshot settings. `git diff --check` passed. Temporary
pytest ledgers were removed after inspection; no runtime resources were allocated.

## Reviewable receipt examples

[runner-admission-codex-158-receipts.json](runner-admission-codex-158-receipts.json)
contains five explicitly synthetic examples. Bindings and manifest/evidence hashes
inside those examples are fabricated fixture values, not real provenance claims.

| Example | Status | Single-line receipt bytes |
|---|---|---:|
| Runtime | passed | 876 |
| Snapshot | passed | 883 |
| Cleanup | passed / release | 668 |
| Reservation-only filesystem quota | blocked | 381 |
| Owned snapshot still present | blocked / quarantine | 402 |

The samples exercise three contract stages and two refusals. Benchmark coverage,
eligible/selected tasks, task/trial coverage, score identity, model binding and
comparability to real pilots are **not applicable**; no evaluation was performed.

## Artifact integrity

SHA-256 over the final files:

| Artifact | SHA-256 |
|---|---|
| `eval/runner_admission.py` | `f9d9dee76e1e1a94366d1f486c122a100bb42755b4ec9d4a86c48b4941c1f663` |
| `eval/container.py` | `25361bd575dc28029a0e3270a362c17a91e590c00007b8e32f15ebe72a324a61` |
| `tests/quality/test_runner_admission.py` | `9a9f9ad5d1e4a5f00c617851e75581fd03a790a15d81df17119604234e216a65` |
| `runner-admission-codex-158-test-result.txt` | `5cb5465517d61a454422e85636970404e4e4356af90c38a4e7bce13182fd8d9b` |
| `runner-admission-codex-158-receipts.json` | `7ca63a0170583ba157ce84b9e1b7ae4bfc1fe3d6e168c3c1547054d372f0ea6a` |

## Remaining gates and rollout

Status: **isolated contract and known-fault repair**. No live adapter runner is
wired to the new contract and no quota enforcement was installed. The existing
byte-only Docker preflight now reports its limitations explicitly.

Independent backend work must still verify kernel byte/inode enforcement and
complete fresh observers, bind phase-specific manifests, bound snapshot worker and
daemon resources/commit growth, retain shared capacity reservations, atomically
apply cleanup decisions, and provide complete scorer/offline/artifact-export
closure. Hash syntax alone does not authenticate observations. Stateless checks
cannot reject replay under an identical binding. Existing runtime guards and the
benchmark blockers remain necessary.

Focused commit subject: `platform: add offline runner quota and cleanup admission contracts`.
