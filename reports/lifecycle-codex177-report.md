# Shared lifecycle receipt review — Codex 177

Base: `e7acaa1`; isolated worktree: `/tmp/hg-codex-177`.
Scope: receipt contracts, staged score publication and synthetic regression tests.
No dataset acquisition, model/provider requests, H0, Docker execution, GPU work or
production observation collector was run or added.

## Findings

- `driver.save_policy_receipt` supplied unknown cleanup/snapshot evidence but
  returned success based solely on measured task count. This allowed a staged
  measured curve before either attestation passed.
- `eval.diagnostic_policy` validated cleanup/snapshot structure and required passes
  for expansion review, but could build/write a receipt containing measured scores
  while those lifecycle fields were unknown or failed.
- `eval.runner_admission` already provides binding, resource/filesystem, snapshot
  preflight and exact cleanup absence checks. These checks are offline contracts;
  supplied facts require an independent trusted observer.
- `eval.container.snapshot_admission` is explicitly byte-only capacity preflight.
  `stop`/`commit` check command completion and image identity but do not produce
  the full shared lifecycle evidence. `remove_container` and `remove_image` swallow
  timeout/OS errors and ignore unsuccessful removal statuses. The `finally` in
  `container_state` performs teardown, but neither it nor a successful removal
  command verifies absence across every owned namespace.
- `eval.gaia_snapshot_attestation` compares source/runtime compatibility only and
  explicitly grants no lifecycle authorization; it cannot replace completion or
  cleanup evidence. Legacy curve/store schema likewise has no lifecycle contract.

## Implemented contract

`eval.lifecycle_receipt.start_lifecycle(binding, scope_sha256)` freezes scope.
`transition(checkpoint, stage, evidence)` returns a new checkpoint and leaves inputs
unchanged. `validate_lifecycle_receipt` replays the entire sequence and rechecks
event receipt digests and derived state. Checkpoints contain no numeric score.

Bindings use the existing exact `adapter_id`, fresh `run_id`, `trial_id` and
`manifest_sha256` contract. The manifest must freeze policies and ownership intent;
the diagnostic scope digest additionally names stage, eligible-pool digest,
selected IDs and the full context, including metric, endpoint and limits.

| State | Evidence required to advance successfully |
| --- | --- |
| scope | Valid binding and frozen pre-execution scope digest |
| admit | Original `policy`/`observed` facts passing `admit_runtime` |
| execute | Bound attestation: integer exit 0, no OOM or timeout |
| quiesce | Bound attestation: stopped, integer exit 0, no OOM or timeout |
| score | Bound scoring evidence receipt and canonical normalized outcomes digest |
| seal | Same outcomes digest; bound snapshot/export completion attestation |
| cleanup | Original facts passing `admit_cleanup`, including complete absence inventory |

Execution, quiescence, scoring, sealing and snapshot completion use
`harnessgrad.lifecycle-attestation.v1` with exactly `schema`, `binding`, `stage`,
`status`, `receipt_sha256`, `facts` and bounded `detail`. Snapshot facts require
`completed=true`, `artifact_sha256`, integer exit 0, no OOM/timeout, `preflight`
facts passing `admit_snapshot`, and `runtime` facts passing `admit_runtime` for
the snapshot worker. The hash names the resulting immutable image/export identity.
Scoring and sealing must name the same normalized outcomes. The backend remains
responsible for linking the scorer's actual inputs to that artifact.

Skipped/repeated stages and transitions after cleanup are refused. Failed/unknown
attestations contain no passing facts and allow only a cleanup attempt. Admission
refusals persist bounded refusal receipts, without copying rejected raw observations.
Cleanup uncertainty retains the gate's `lease_action=quarantine`; successful cleanup
after an earlier failure does not restore publication readiness. Cleanup is terminal
for this receipt; any later resource-recovery operation needs its own evidence record
and must not resume the measurement or erase the old checkpoint. The state machine
does not release leases or delete resources. At most six transition events and
128 KiB of serialized lifecycle evidence are accepted; shared admission bounds apply.

`require_publication` requires all stages to pass and binds run/manifest/scope,
sealed outcomes, the actual cleanup receipt digest and snapshot attestation digest.
`production_authorized` remains false: structural validity cannot authenticate
supplied observations or grant production H0 approval.

Diagnostic receipts are now `harnessgrad.diagnostic-receipt.v2` and carry `lifecycle`
or explicit null. `build_receipt` withholds provisional measured scores as
unmeasured/null until the lifecycle and summary attestations pass, recalculates
coverage, and retains preexisting invalid/unmeasured outcomes. A ready lifecycle
with mismatched scope, result or attestation hashes is rejected. Validation and
exclusive writing refuse manually restored measured fields without matching
lifecycle evidence. The JSON schema also rejects measured fields when the
lifecycle/summary gates are pending; Python replay enforces semantic consistency.

The staged driver has no trusted lifecycle producer. It continues to record unknown
facts, supplies no fabricated observations, and refuses both train and eval staged
curve publication. Existing v1/incomplete receipts are not overwritten or upgraded
by assertion; v1 is unsupported as new v2 expansion evidence. Later attested v2
receipts must use new filenames and receive separate hash-bound expansion review.

## Validation and limits

439 focused tests passed, with no skips or failures. Tests cover valid measured
zeros, every pending checkpoint, ordering, failure cleanup, admission refusals,
cross-binding evidence, snapshot completion/worker failures, digest/scope changes,
schema/writer publication refusal, exclusive writes and the eval-side publication
callback. New lifecycle tests forbid subprocesses and sockets; fixtures are authored
only in `tests/quality/lifecycle_fixtures_codex177.py`, never imported by runtime code.
The first validation run had 428 passes and one failure due to the now-earlier scope
check; its expected error was corrected, and the final suite adds further regressions.

Validation command (all temporary artifacts stay in this worktree):

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
TMPDIR=/tmp/hg-codex-177/.scratch/lifecycle-codex177 \
python3 -m pytest -q \
  tests/quality/test_lifecycle_receipt_codex177.py \
  tests/quality/test_diagnostic_policy.py \
  tests/quality/test_runner_admission.py \
  tests/quality/test_shared_admission_wiring_codex163.py \
  --basetemp=/tmp/hg-codex-177/.scratch/lifecycle-codex177/pytest
```

`git diff --check` passed. This change does not provision quota enforcement, build
an observer, enforce concurrent snapshot capacity reservations, pin an official
scorer closure, repair Docker teardown, or retrofit non-staged legacy publications.
Those backend/legacy paths remain independent work. Synthetic passing evidence
does not prove any of those production gates. No main-branch merge was attempted.
