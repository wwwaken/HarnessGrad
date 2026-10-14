# B10 shared scorer/export integration review — stopped at compatibility boundary

Review baseline: `906607202fe6d7674695a410a72eb7379b869e75`.
Workspace: `/tmp/hg-b10`, registered detached worktree. No other checkout changed.

**Neither shared blocker is closed. No production integration was made.**
The user's explicit stop condition applies: "If wiring either one reveals that it
cannot be integrated without changing behaviour in a way the platform depends on,
STOP and report rather than forcing it."

Mandatory use of the existing pristine, network-none, two-projection contract
conflicts with the platform's documented snapshot and service verification
semantics. Leaving those paths as fallbacks would leave both shared blockers
open; replacing them with a blanket refusal would change supported behavior
rather than implement compatible scoring. No gates were weakened, removed,
bypassed or relabeled. Both registry IDs and all dataset references remain active
with their original `code-solvable` status.

## scorer-offline-closure

Original `observed`, read before investigation:

> The local scorer bundle validator is not wired into production and does not attest transitive runtime/network closure.

Original `next_action`:

> Review generic integration of local closure checks and a dedicated offline scorer boundary using synthetic fixtures.

### Existing guarantees and proposed integration points

`eval/scorer_bundle.py` aliases `eval/admission/scorer_bundle.py`. `verify_bundle`
authenticates manifest bytes against an independently supplied pin, validates a
declared reachable dependency graph, and checks the exact local inventory, sizes,
hashes and regular-file/link constraints. Its receipt scope is
`local_declared_closure_integrity`. `network=none` in a manifest is a declaration,
not observed isolation. These checks neither discover imports/shared libraries
nor prove the pinned runtime image contains a complete transitive closure.

Production integration would have to precede **every** command dispatch in
`eval/verification/verifier.py::_verify_inner`, and snapshot runtime creation in
`_verify_container_state`. An optional declaration that leaves those existing
dispatches available cannot close the shared gate. The evidence-only
`eval/admission/scorer_backend.py::check_backend` is not an execution backend: it
requires trusted lifecycle/resource/runtime observations supplied by its caller.

### Compatibility stop

- `INTERFACE.md:887-927` specifies grading the actor's entire container snapshot,
  including output outside `/app`. `_verify_container_state` creates the scorer
  from that snapshot at `eval/verification/verifier.py:271`.
- `INTERFACE.md:1051` and `eval/verification/verifier.py:266-270` record that
  Terminal-Bench checks install dependencies during verification and that forcing
  network-none prevented them from running. These are historical source claims,
  **not fresh observations of all 89 checks** in this review.
- `eval/verification/verifier.py:527-546` deliberately supplies the task service
  network and service recording mounts to service-backed checks. The existing
  runtime helper requires a pristine pinned image, `network=none`, and exactly two
  platform projections. It cannot attest this different topology.
- `data/scaffolds/registry.py:600-602` has no verifier fields for pinned scorer
  bundles, task export contracts or trusted observer bindings. Adding unchecked
  truth-valued flags or treating actor/adapter dictionaries as trusted observations
  would not supply that missing evidence.

### Exact refusing controls and output

From the checked-in verbose test output
`reports/b10-shared-boundaries-focused-tests.txt`:

```text
tests/quality/test_scorer_bundle_codex170.py::test_unclosed_or_unsupported_declarations_fail_before_file_access[missing_dependency] PASSED
tests/quality/test_scorer_bundle_codex170.py::test_unclosed_or_unsupported_declarations_fail_before_file_access[network] PASSED
tests/quality/test_scorer_bundle_codex170.py::test_exact_bundle_inventory_and_local_bytes_are_required[missing] PASSED
```

These tests require `AdmissionError` for, respectively, an unresolved declared
dependency, a bridge-network manifest, and a missing pinned local dependency.
The malformed-declaration tests also require refusal before bundle inventory
access. `PASSED` here means the requested rejection occurred, not that a scorer
ran successfully. Runtime observation mutation `[network]` in
`test_terminal_artifact_admission.py` also requires refusal of a bridge-network
runtime observation.

**Closed gates:** no new production gate. Existing declared-local-closure and
supplied-runtime-observation refusal controls are reverified.

**Open gates:** mandatory production bundle admission; actual offline runtime
execution; independently authenticated runtime observations; complete transitive
runtime/image/ABI closure; official scorer provenance/execution; lifecycle,
resource enforcement and cleanup evidence. Compatibility needs an explicit
adapter migration to separately provisioned offline scorer runtimes and reviewed
service/replay contracts before changing these dispatches.

## artifact-only-state-export

Original `observed`, read before investigation:

> Artifact admission helpers have no production integration; complete actor trees or snapshots still reach verification.

Original `next_action`:

> Review allowlisted data-only export integration and bounded synthetic export controls.

### Existing guarantees and proposed integration points

`eval/artifact_admission.py` aliases `eval/admission/artifact_admission.py`.
`export_state` reads only contract-allowlisted files into an exclusive separate
destination, rejects executable-mode files, links and special files, enforces
per-file/total byte and directory-inclusive inode limits, and removes a partial
projection on failure. `verify_state_export` rechecks identity, exact inventory
and content. This meaning of data-only is structural; it is not a proof that
arbitrary bytes cannot be interpreted as code by a downstream scorer.
Quiescence, trusted contract pins and platform ownership remain caller duties.

The required production seams are the whole `workdir` passed to
`container_mod.run`/`sandbox_mod.run`/`subprocess.run` in `_verify_inner`, and the
snapshot passed by `eval/containers/container_state.py:213` to
`_verify_container_state`. Neither helper is wired at those points by this change.

### Compatibility stop

`INTERFACE.md:914-927` expressly says the graded state includes anything the
harness touched and that some task outputs live outside `/app`. The current
contract supplies no per-task artifact allowlist or extractor for that state.
Exporting only `answer.txt` or `/app` would change what is graded; exporting the
whole snapshot would fail the requested artifact-only guarantee.

`eval/verification/verifier.py:532-546` mounts verifier service recordings, and
`data/datasets/appworld.py:278` explicitly consumes an action log under
`/recordings/appworld/...`. The helper's runtime boundary at
`eval/admission/artifact_admission.py:430-436` accepts exactly `/control-input`
and `/control-scorer`. It cannot preserve this path contract by simply adding an
unreviewed extra mount. Correct integration needs task-specific bounded selected
data projections, trusted scorer/private-input contracts and compatible scorer
path/replay semantics, not an inferred generic allowlist.

### Exact refusing controls and output

```text
tests/quality/test_terminal_artifact_admission.py::test_state_export_refuses_toolchain_links_special_or_missing_files[executable] PASSED
tests/quality/test_terminal_artifact_admission.py::test_export_enforces_both_byte_and_inode_limits[per_file] PASSED
tests/quality/test_terminal_artifact_admission.py::test_export_enforces_both_byte_and_inode_limits[total] PASSED
tests/quality/test_terminal_artifact_admission.py::test_export_enforces_both_byte_and_inode_limits[inodes] PASSED
tests/quality/test_terminal_artifact_admission.py::test_runtime_requires_pristine_offline_readonly_boundary_and_hard_quotas[actor_closure] PASSED
```

The bounded fixture allows only `results/answer.txt`, at most 16 bytes and three
inodes including directories. The executable-mode control requires
`AdmissionError` and absence of the failed destination. The per-file control
offers 17 bytes and must be refused. The other controls reject aggregate byte or
inode overflow and an actor tree substituted for the trusted scorer projection.
The positive helper control also verifies that unselected actor files are not
copied. These are local helper tests, **not production refusal tests**.

**Closed gates:** no new production gate. Existing bounded data-only export and
supplied-runtime mount-refusal controls are reverified.

**Open gates:** production-only artifact projection; authoritative per-task data
allowlists; quiescence/trial/ownership binding; pristine runtime integration;
private trusted input projection; service recording/replay migration; cleanup and
dataset-specific scoring equivalence. Complete actor trees/snapshots still reach
the existing direct verifier paths.

## Focused execution and review limits

Only these named focused tests were run:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
python3 -m pytest -vv --color=no -p no:cacheprovider \
  --basetemp=/tmp/harnessgrad-pytest-b10-shared-boundaries \
  tests/quality/test_scorer_bundle_codex170.py \
  tests/quality/test_terminal_artifact_admission.py \
  tests/quality/test_verifier.py::test_a_setup_and_a_command_verifier_work_end_to_end
```

Exit 0: **85 passed in 0.39s**. Full output is checked in alongside this report.
The last test invokes a synthetic native command through `run_one` without a
bundle/export contract and passes. It confirms an existing supported behavior
that mandatory refusal would change; it does not establish safe scorer admission.
The two helper test files disable subprocess/network execution in their fixtures.
The one native compatibility test runs local Python only. No whole suite,
benchmark payload, model endpoint, Docker runtime, real pilot, scorer package
installation or network diagnostic was executed. No dataset readiness or H0
authorization follows from these results.

The existing runner admission hook remains intact. Its refusal of declared
policies/exec modes is not bypassed, and its lack of trusted backend observations
is not repaired by synthetic facts. Source-only independent review confirmed the
snapshot/network/service conflicts; all edits and test execution stayed in this
worktree, with pytest scratch outside the platform as required by `AGENTS.md`.

Both active registry entries retain their status and original findings/actions;
this report and the test output are appended as evidence. The registry checker
result is recorded in `reports/b10-shared-boundaries-registry-check.txt`.
