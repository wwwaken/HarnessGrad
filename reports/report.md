# Terminal cached pilot admission hardening

The six reported admission findings are repaired in the focused library, with
**199 passing offline tests**. Benchmark admission remains **BLOCKED** by scorer,
dependency, export, and quota gates. No benchmark-readiness claim is made.

## Scope and source

All writes and validation were confined to `/tmp/codex/112/worktree`, starting
detached at `5890b987991f07ac1cc2e950672d94855de41204`. No main branch or main
checkout was edited. No images were pulled or built; no real Docker commands,
benchmark/model/H0/heldout reads, model calls, or benchmark trials were performed.

The requested `/tmp/codex/111/report.md` was absent. The report was located at
`/tmp/codex/111/worktree/report.md` and read as the finding source. Both draft
entrypoints were absent from this fresh worktree. The prior
`eval/pilot_admission.py`, `tools/cached_pilot_admission.py`, and review tests
under `/tmp/codex/111/worktree` were inspected read-only. No prior manifest,
benchmark payload, model configuration, or runtime receipt was opened.

This delivery adds `eval/pilot_admission.py` and
`tests/quality/test_cached_pilot_admission.py`, plus this report and
`focused-test-result.txt`. It adapts the admission draft into a self-contained
library without importing generic container code or dataset adapters. The runtime
CLI, production runner, generic container helpers, scorer, and manifest are not
introduced or modified. The two findings originally exercised through generic
container helpers are repaired at this library's local-image and owned-cleanup
boundary; this does not claim changes to generic helpers outside this scope.

## Six repairs

| Finding | Repair and offline evidence |
| --- | --- |
| Empty device observations admit a lease | Require a nonempty observation mapping with valid device identities and byte/inode quantities before locking or writing. Rejection creates no ledger. |
| Negative reservations accepted | Validate all declared reservation and host/device quantities as nonnegative integers, excluding booleans, fractions, nonfinite numbers, and missing values. Validate allocations before persistence and on reload/update. Invalid acquisition/update leaves existing ledger bytes unchanged. |
| Mounts allow network override | Preserve the draft mount-pair interface, admitting only an optional read-only bind to `/control-input` with a normalized absolute source. Reject unrelated flags, extra options, unsafe destinations, and malformed pairs before ownership intent or create. Commands retain `--pull=never` and `--network none`. |
| Runtime envelope not checked before start | Inspect and verify exact ID/name/image/owner/task, created-and-stopped state, network, read-only root, memory/swap/CPU/PID bounds, capabilities, privilege/security settings, tmpfs size/inodes/options, bounded logging, and expected artifact mounts before start. Mismatches retain ownership and quarantine the lease, with zero start calls. |
| Bare image ID mismatch accepted | `LocalDocker.require_local_image` compares bare pins to inspected `.Id` automatically, checks ID syntax, enforces any explicit expected ID and repository digest, and reinspects every request. Inspect timeout/OS/parser failures become admission refusals. |
| Cleanup accepts unrelated daemon absence | Accept only a complete canonical not-found response naming the exact queried object, with failure code 1 and empty object output. Cleanup checks recorded ID/name and owner/task labels before removing the exact ID, then proves that ID absent and the owner namespace empty. Daemon errors, unrelated/mixed absence text, changed identities, removal failures, and unrecorded owned objects retain/quarantine capacity. |

## Atomicity and ownership

The cooperative ledger uses `flock`, validated records, temporary-file fsync,
atomic replacement, and parent-directory fsync. Tests cover concurrent capacity
claims, device-alias deduplication, disk/inode floors, host reservations, corrupt
records, rejected updates, and active/crash/quarantined leases retaining capacity
across reopening. Quarantined leases cannot be reset to active; released records
are immutable.

Ownership intent is persisted before create; start intent is persisted before
start. Injected persistence failures prevent the next daemon mutation. A
create-time timeout retains a name-only intent that can reconcile an exact
matching owner. Runtime mismatches and start timeouts persist quarantine. Failed
file fsync or pre-replacement writes leave no partial ledger; failed quarantine
or release replacement retains the old allocation. Temporary write files are
removed. Verified cleanup releases capacity and repeated cleanup is idempotent.

Cleanup never sweeps unknown objects: it removes only recorded objects whose
identity and labels match. An unknown object in the owner namespace quarantines
the lease; an unrelated object's presence is untouched. Successful cleanup is
also tested using canonical absence of the exact removed ID.

This remains workspace-local cooperative accounting, not a host-wide reservation
service or filesystem quota. The offline suite validates refusal and accounting
logic using fabricated daemon responses; it does not attest a real daemon or
filesystem enforcement.

## Focused validation

```bash
env PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q \
  tests/quality/test_cached_pilot_admission.py \
  --basetemp=/tmp/codex/112/worktree/.admission-tests -p no:cacheprovider
```

Final result: **199 passed in 5.06s**, exit code 0, no skips or expected failures.
The result is saved in `focused-test-result.txt`. `git diff --cached --check`
passed before commit. The autouse fixture rejects real subprocess execution and
socket creation. Test manifests, reports, artifacts, and Docker responses are
synthetic; temporary files stay beneath the local basetemp and are removed after
validation. No broad test collection or integration tests ran.

The first run found a misplaced test fragment (166 passed, 1 failed); it was
corrected before the passing runs. Additional ownership, start-timeout, and
malformed-inspection cases passed in the final run.

## Remaining scorer and dependency blockers

The source review reports the following unresolved gates for each inherited task:
`git-multibranch`, `mailman`, `cobol-modernization`, `git-leak-recovery`,
`build-pmars`, and `financial-document-processor`:

- The scorer shell fetches dependencies while scorer network policy is `none`;
  a pinned, verified offline dependency/package/artifact closure is missing.
- Trusted scorer shell/interpreter/dependencies/grading implementation have not
  been verified independently of actor snapshots.
- An artifact-only state export contract supplying the trusted official scorer's
  required inputs has not been verified.

Those are 18 task-specific gates. Writable benchmark disk/inode quotas remain
unavailable, and official scorer execution remains outside the admitted synthetic
scope, giving two further unconditional blockers. The library retains those
blockers even when the three per-task declaration booleans are set true. Missing
or invalid scorer reports remain unmeasured, with no reward inferred from a
process exit code. Cached images and successful admission-unit tests do not
establish scorer readiness. These dependency claims are inherited from the source
review, not newly verified against external artifacts here.

The fresh worktree also lacks the pilot manifest and runtime CLI. This delivery
intentionally provides only the focused admission library and offline regression
suite; it does not activate a pilot or authorize benchmark execution.
