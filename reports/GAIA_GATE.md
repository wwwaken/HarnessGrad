# GAIA frozen source / snapshot lifecycle gate

**Disposition: compatibility tooling and admission regressions implemented;
measured lifecycle gate remains BLOCKED.** No GAIA lifecycle pass or receipt reuse
is asserted. This delivery does not authorize a diagnostic, pilot or H0 run.

Work is confined to the isolated `/tmp/hg-codex-151` worktree. Dataset payloads,
heldout data, model artifacts/configuration and H0 run artifacts were not opened.
No model calls, Docker commands, controls, network requests, downloads, image
builds or benchmark trials were executed. Existing repository control code and
tests were inspected; external receipt paths were not followed.

## Observed source and evidence boundary

The inspected base is commit
`8fcdcb80b90f43ab1c76c1f572c5cf70a6504e11`, tree
`9cc14105b4dc30c7f41e21bdc19fd6c5df71346d`. Its complete 752-entry Git metadata
manifest has canonical SHA-256
`19ee130630b4d1b2c199a0bec641b1c9dc985879af17a264f36093ad74b84a55` under
`harnessgrad.gaia-source.v1`. These are source observations, not run evidence.

No GAIA control/lifecycle receipt is present in this checkout. The inherited
`report.md` describes a different cached-pilot admission library and is not GAIA
evidence. Historical journal statements are pointers to external evidence, not
receipts validated here. No historical source, runtime, coverage, score or
cleanup claim was promoted to a current GAIA gate pass.

The following findings come from source inspection:

- `eval/container.py::snapshot_admission` checks writable-layer size and Docker
  disk headroom before commit. Defaults are 16 GiB maximum writable bytes and
  1 GiB reserve; effective environment overrides also matter. These checks are
  observations, not filesystem quotas or an atomic host reservation.
- `eval/container_state.py` stops the actor, commits it, then verifies against
  the returned immutable image identity. `SnapshotUnavailable` produces an
  invalid snapshot result without a score and executes teardown in `finally`.
- Cleanup helpers attempt removal and suppress exceptions; they do not prove
  that owned objects are absent. A commit timeout can leave a tag/image even
  when no image ID was returned. Existing teardown cannot provide the required
  verified cleanup receipt by itself.
- `data/gaia/control.py` delegates to `data/command_control.py`. Existing GAIA
  tests exercise oracle and noop controls using real containers and external
  data; they were not run here. The shared control uses a fixed run ID and does
  not seal structured source/admission/snapshot/cleanup evidence. It also
  defaults a missing verdict to zero, so its noop exit status alone cannot
  distinguish an invalid snapshot from a measured zero.
- GAIA lacks a selected-only `control_task` hook: the shared picker calls
  `load()` even with an explicit task ID. Existing full-pool preparation/scorer
  tests also read external data. Neither path is an authorized privacy-safe
  control for this task.

## Implemented compatibility contract

`eval/gaia_snapshot_attestation.py` is an independent offline review library,
not integrated into a runner or control. `collect_source(repo, full_commit,
require_checkout=True)` checks that the candidate HEAD matches a full SHA-1
commit and that its tracked/untracked nonignored checkout is clean. It reads
Git object types and complete tree metadata, never blob contents. It rejects
submodules, malformed paths, missing critical source entries and noncommit
objects. Historical collection without `require_checkout` describes only the
named commit; it cannot reconstruct the checkout used by a historical run.

`attest_compatibility(reference, candidate, reference_runtime,
candidate_runtime, reference_receipt_sha256=...)` produces canonical source and
runtime hashes, all changed paths, runtime-affecting paths and changed binding
fields. It compares every tracked entry, including file modes, additions and
deletions. Only the exact nonexecutable regular files `reports/GAIA_GATE.md` and
`tests/quality/test_gaia_snapshot_attestation.py` are review-only exceptions.
Other docs, tests, unknown paths and the attestation implementation itself
require fresh controls when changed. No caller-supplied exemptions are accepted.

The strict `harnessgrad.gaia-runtime.v1` binding requires all of:

- The dataset revision and `split=validation`; pool, split and preselected
  manifest SHA-256 identities.
- Scorer, no-model harness, dependency closure, web policy, artifact export
  contract and quota policy SHA-256 identities.
- Exact actor and verifier image IDs of the form `sha256:<64 lowercase hex>`.
- Container plan, effective snapshot maximum/reserve bytes and positive integer
  CPU, memory-MB and PID limits.

Missing bindings, mutable image tags, placeholders, booleans used as integer
limits and mismatches are rejected. These hashes must come from reviewed
observations; syntactically valid hashes do not establish their contents or
enforcement. The library compares identities without executing or reading the
external inputs. It intentionally does not bind model settings or authorize a
model run.

`compatible=true` means only that these supplied source/runtime identities
compare successfully. Every report has `receipt_validation=not-performed`,
`evidence_reusable=false`, `lifecycle_authorized=false` and a blocked lifecycle
status, even when a reference receipt digest is provided. The digest names
evidence for separate review; it does not authenticate it. Manually supplied
source dictionaries are trusted inputs; use and preserve the complete
`collect_source()` output rather than inventing manifests.

The caller must hold the checkout fixed through execution and sealing. The
library does not lock it or attest an ignored/external input. Those inputs need
independent hashes and runtime enforcement. Source collection is not itself a
lifecycle receipt.

This delivery changes `eval/container.py` and adds executable attestation code.
Any earlier source must be compared to the final committed candidate. The
changes cannot be labeled documentation-only or retroactively credited to
earlier controls.

## Admission repairs and offline evidence

`snapshot_admission` now rejects negative writable sizes and absent/relative
Docker roots instead of accepting negative quantities or assuming a root path.
Inspection and Docker-info timeouts/OS errors become `SnapshotUnavailable`,
preserving the runner's invalid snapshot result and teardown path.

The new offline suite blocks subprocess execution, sockets and host disk
inspection, then supplies explicit synthetic responses. It covers complete
bindings, all runtime field changes, source additions/deletions/modes, exact
review exceptions, metadata collection failures, dirty/wrong checkouts, invalid
observations, headroom boundaries, prevention of commit after refusal, and
runner invalid/no-score behavior with attempted owned teardown. Teardown tests
assert calls only; they never attest real resource absence. Temporary runner
directories stay under this worktree's pytest basetemp.

Run the focused suite from this worktree:

```bash
mkdir -p /tmp/hg-codex-151/.pytest_cache
env PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q \
  tests/quality/test_gaia_snapshot_attestation.py \
  tests/quality/test_container.py::test_snapshot_admission_rejects_writable_layer_before_commit \
  tests/quality/test_container.py::test_commit_exit_137_is_classified_as_oom \
  tests/quality/test_container.py::test_commit_disk_and_resource_errors_are_classified \
  --basetemp=/tmp/hg-codex-151/.pytest_cache/gaia-offline -p no:cacheprovider
```

The initial 84-test suite passed. The first expanded run had three fixture setup
errors because the basetemp parent was absent; creating the local parent resolved
them. Final validation: **91 passed in 0.28s**, exit 0, with no skips or expected
failures (88 new offline tests and three existing mocked snapshot regressions).
`git diff --check` passed. These results are synthetic regression evidence only.

## Required measured closure, outside this delivery

Before claiming closure, separately review an authentic no-model receipt from
one coherent, clean, frozen candidate. Preserve all old/incomplete receipts and
use fresh IDs. A receipt must bind the exact source and runtime manifests above
and demonstrate selected-only provenance without accessing excluded data.

It must record the official metric identity, eligible/selected/task/trial
coverage, invalid and unmeasured counts; independently measured oracle/noop
outcomes; owned actor/network identity; stopped state; writable bytes and Docker
free/reserve observations; successful snapshot image ID; verifier/runtime and
dependency closure; artifact-only state export; resource/quota enforcement;
sealing; and exact owned container/image/network absence after cleanup. An
uncertain failure retains its ownership record and blocks reuse. Record limits,
budgets, endpoint binding when applicable and comparability notes explicitly.

No such receipt was generated or validated here. In particular, the current
shared-control stdout/exit code and best-effort cleanup are insufficient. A
valid source comparison and passing synthetic tests cannot substitute for those
observations. Production lifecycle admission remains blocked until the separate
receipt review and the privacy, verifier, export, quota and cleanup gates pass.
Only then can a separately authorized one-task/one-trial diagnostic be considered;
expansion requires a distinct review of its valid measured receipt.
