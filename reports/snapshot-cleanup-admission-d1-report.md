**Snapshot and cleanup admission — operator ruling implementation (2026-10-15)**

Worktree: `/tmp/hg-d1`, starting at `f1d563b`. All work and the commit stay in this
registered worktree; no main-checkout edits or merges.

`eval/admission/runner_admission.py::admit_snapshot` and `admit_cleanup` now check
available observations best-effort. Missing/null lifecycle facts, evidence hashes,
owned-object observations/identity components and namespace coverage no longer block admission by
themselves. Passing evidence carries `best_effort=true` and deterministic
`uncertainties` field paths. Unknown quantities stay null; cleanup reports only
actually observed namespace checks and requests release even with uncertainty.
Neither function certifies bounded snapshot peak usage, exact owned absence or
atomic lease closure.

Known-bad observations still refuse with a bounded, unmeasured failure receipt:
nonzero exit/OOM/running worker, size/headroom violations, deadline mismatch,
present owned objects, nonempty owned namespaces, unexpected or duplicate
identities, malformed supplied facts/hashes and stale bindings. Cleanup refusals
still request quarantine. Coverage gaps never short-circuit these checks.

Updated `docs/enforcement-proof-decision.md` and the current runner admission
contract to describe retained uncertainty. Updated blocker next actions for
ChessBench, GAIA and tau_bench, and terminal_bench's obsolete claim that all
uncertainty quarantines. Removed remaining next-action demands for the withdrawn
official-scorer-identity proof in FEVER, Physics Questions and Reasoning Gym while
retaining source provenance, metric identity and offline/pristine requirements.
Added decision citations. Historical run records and null effects are unchanged;
GAIA remains policy-refused and the index authorizes no production work.

Updated the old refusal assertions explicitly: null snapshot quantities and
cleanup deadlines, missing owned rows and missing namespace coverage now have
positive uncertainty tests. Known failures retain negative tests. Updated the
stale AppWorld registry assertion to require the exact four remaining shared
blockers and explicitly exclude the withdrawn pair. Renamed the shared schema
test to distinguish malformed/unbound input from incomplete bound observations.

Deliberately left all of `eval/admission/pilot_admission.py` unchanged, including:

- `scorer egress is not authorized`: pinned cache image/digest and scorer-network
  integrity catch a mutated manifest and protect metric validity.
- `ownership label mismatch; refusing removal`: ownership checks protect other
  leases' and users' resources from removal.

Snapshot/cleanup execution, existing ledger persistence, `admit_runtime`, legacy
container snapshot preflight and the independent pilot control are unchanged.
The change removes a proof gate; the mechanisms continue to run. Binding/schema
checks still reject malformed or unbound input, rather than inventing trusted facts.

The two requested focused regression tests and their observed output:

```text
$ python3 -m pytest -q tests/quality/test_runner_admission.py::test_known_bad_lifecycle_observation_is_refused_despite_incomplete_evidence --basetemp=/tmp/harnessgrad-pytest-d1-known-bad
...............                                                          [100%]
15 passed in 0.08s

$ python3 -m pytest -q tests/quality/test_runner_admission.py::test_incomplete_lifecycle_observation_proceeds_with_uncertainty --basetemp=/tmp/harnessgrad-pytest-d1-incomplete
................................................                         [100%]
48 passed in 0.09s
```

Other named, focused validation (no whole-suite run):

```text
$ python3 -m pytest -q tests/quality/test_runner_admission.py tests/quality/test_lifecycle_receipt_codex177.py tests/quality/test_shared_admission_wiring_codex163.py tests/quality/test_dataset_blockers.py tests/quality/test_appworld_trusted_trial_writer_codex183.py::test_registry_closes_only_the_saved_writer_blocker --basetemp=/tmp/harnessgrad-pytest-d1-regressions
464 passed in 3.80s

$ python3 -m pytest -q tests/quality/test_cached_pilot_admission.py::test_scorer_network_change_is_refused tests/quality/test_cached_pilot_admission.py::test_cleanup_refuses_changed_owned_identity tests/quality/test_cached_pilot_admission.py::test_cleanup_never_removes_unrelated_container_or_unknown_owned_object tests/quality/test_cached_pilot_admission.py::test_cleanup_uncertainty_quarantines_and_retains_capacity --basetemp=/tmp/harnessgrad-pytest-d1-protected
10 passed in 0.68s

$ python3 tools/check_dataset_blockers.py
{"valid": true, "datasets": 28, "shared_blockers": 4, "historical_records": 11, "production_authorized": false}

$ git diff --check
(no output; exit 0)
```

The two new test groups are included in the 464-test focused run, not additional
unique cases. Tests use synthetic observations and fake clients; no benchmark,
model, GPU, real container or pilot was launched.
