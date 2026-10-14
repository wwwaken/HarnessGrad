# User setup and score claims

Ordinary use on a supported Linux host needs **no sudo and no dedicated volume**.
Use your normal account and writable directories. Optional administrator-managed
infrastructure can support stronger formal evidence once implemented and verified.

## Check the existing setup

The platform needs Python 3.10+, Git, and working bubblewrap with host support for
unprivileged namespaces. From the repository root:

```bash
./install.sh --check
python3 driver.py --help
python3 driver.py --show-config
```

These commands do not evaluate H0, call a model, or run a benchmark. The installer
check includes a namespace self-test. `--show-config` incorporates `.env`; API
keys appear only as present/absent. The default agent backend is `mock`.

`./install.sh` may try passwordless sudo for missing system packages. If packages
or namespace support are unavailable, ask an administrator for a supported host.
`--no-sandbox` produces a different, non-comparable execution configuration.
Harness dependencies and dataset services/images are additional requirements;
see the [README dependency setup](../README.md#if-your-harness-has-dependencies).
Container-backed datasets also need their supported runtime and access permissions.

Records default to `runs/<run-id>/`; checkpoint working trees default to
`../harnessgrad_work/<run-id>/workspace/`. Both can use ordinary existing storage.
`--runs-root` moves records; `--work-root` moves working trees and **must remain
outside the platform checkout**. Keep checkpoint trees until harness export, and
use a fresh run ID while preserving old or incomplete records.

## Current CLI and dataset gates

`python3 driver.py` executes a run. Its default `--sampling diagnostic` requires
`--policy-evidence` with passing dataset gates and a matching live local endpoint:
one task, `--trials 1`, `--jobs 1`, `--rounds 0`, no improver. Setup success alone
does not admit a dataset. The driver still lacks the trusted lifecycle producer
needed for staged publication; see the [readiness review](task-234-diagnostic-readiness.md).

Expansion with `--sampling pilot_10pct` needs separate review of a valid measured
diagnostic: preselect `min(30, ceil(10% * eligible))` tasks, one trial, one job,
zero rounds. Changing sampling closes no gates. `--mode A/B` is deprecated and
ignored; the engine is unified. There is no additional evidence/strict CLI mode.

## What an ordinary score says

| Evidence available | Claim supported |
| --- | --- |
| Valid local measurement | Performance on the stated tasks, split, metric, model, harness and runtime, with reported coverage and uncertainty. |
| `score_kind=training` | Progress on tasks visible to the method; no held-out generalization claim. `score_kind=exam` identifies a separate eval-side measurement, still subject to scope/provenance review. |
| Mock/demo or synthetic test | Demo/contract behavior; no live-model, production-enforcement or benchmark-equivalence claim. |

Report eligible/selected/measured task and trial coverage, invalid and unmeasured
counts, metric/scorer identity, source/split/manifest/model/harness hashes,
endpoint, resource/budget limits, and cleanup/snapshot status, including unknowns.
Comparisons need matching protocols and compatible evidence. A small sample or
one trial cannot establish reliable improvement or full-benchmark ranking.
Leaderboard equivalence needs matching official scoring, task scope and protocol.

Ordinary score records alone do **not** prove enforced storage limits, complete
isolation, authenticated observations, bounded snapshots or verified cleanup.
Timeout, provider, scorer, snapshot and cleanup failures remain invalid/unmeasured
rather than ordinary zero scores; later cleanup does not validate a failed trial.

## Optional administrator backend

The backend needs independently owned enforced allocated-byte **and inode** limits,
trusted readback for every writer before staging, bounded snapshots/exports and
verified cleanup. Coverage includes workspaces/`.git`, scratch, verifier, daemon,
exports, logs and evidence. A dedicated volume is one administrator provisioning
option. Free space, reservations, Docker size flags or valid JSON do not prove
enforcement.

Use the [administrator checklist](task-222-quota-administrator-checklist.md) and
[backend requirements](filesystem-quota-backends.md) for that separate work.
The complete connected quota backend and production runner wiring remain pending;
the [authenticated readback design](task-233-quota-readback-authentication.md) is a
proposal, not an installed verifier. Host provisioning alone closes neither gap.
This infrastructure can strengthen formal resource/lifecycle evidence; it does
not improve scores or establish scorer correctness. Formal publication still
needs dataset/provenance, official scorer, runtime, artifact export, snapshot
and cleanup evidence together.
