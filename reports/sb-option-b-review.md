# Option B: declared scorer classes and class-compatible records

Workspace: `/tmp/hg-sb`, registered detached worktree, baseline `9e62198`.
Read `reports/b10-shared-boundary-review.md` before implementation. Only this
worktree was changed; no whole test suite, real dataset scorer, model, endpoint,
GPU, pilot or Docker daemon execution was used. No production authorization.

## Original shared entries, read verbatim before implementation

`scorer-offline-closure.observed`:
> The local scorer bundle validator is not wired into production and does not attest transitive runtime/network closure.

`scorer-offline-closure.next_action`:
> Review generic integration of local closure checks and a dedicated offline scorer boundary using synthetic fixtures.

`artifact-only-state-export.observed`:
> Artifact admission helpers have no production integration; complete actor trees or snapshots still reach verification.

`artifact-only-state-export.next_action`:
> Review allowlisted data-only export integration and bounded synthetic export controls.

## Declaration, execution and recording

The verifier reads `scorer_bundle.isolation_class` from the platform task's
verifier specification. Terminal-Bench and AppWorld explicitly declare
`snapshot-service`. Their network, snapshot, argv, reward-file semantics and
mount dispatch arguments are preserved. No generic artifact allowlist is inferred
for them. Unknown declarations are kept separately from observations; old native
commands and answer checks still run, with observed classes `actor-workdir` and
`in-process`. Unsupported explicit declarations are refused, never relabeled.

Sealed `harnessgrad.scorer-bundle.v2` manifests require `isolation_class` and bind
it into their pin. V1 validators and receipt shapes remain compatible. The new
opt-in `eval/verification/pristine.py` path authenticates the v2 pristine bundle
and exact local bytes, binds an independently pinned task export contract, copies
only bounded allowlisted regular non-executable files, and creates a fresh pinned
runtime. It inspects the stopped instance with the existing runtime checker,
requiring `network=none`, exactly the two read-only platform projections and
contract-bounded writable tmpfs. No adapter-supplied observation is accepted.
It executes only the sealed command and reads final container state, then records
container removal. Failures to create/inspect/export/finish/clean up are unmeasured,
not ordinary zero. The exit-status backend is deliberately opt-in; it does not
replace Terminal-Bench reward files or service-backed scoring.

`scorer_isolation_class` travels with verdicts, progress, saved verdicts/trials,
evaluation results and every curve point. `scorer_isolation_declared` records the
separate declaration; pristine verdicts carry bundle, export, inspected-runtime
and cleanup evidence. `per_task_scorer_isolation` travels with task scores.
Missing observations are `unknown`; existing records are never rewritten.

Before averaging trials or tasks, the evaluator requires a single class, including
cached observations. Cache keys bind explicit bundle declarations. The curve
writer independently checks per-task classes and refuses histories crossing
classes before opening the curve file. The UI comparison returns `valid=false`
with an explicit reason for mixed or unknown classes, suppresses score/test-rate
deltas and task movements, and displays the reason. Matching known classes alone
does not certify metric/split/provenance comparability.

## Focused evidence and refusing output

Final focused Python run: **221 passed, 1 skipped in 13.42s**, exit 0.
Exact commands, named files/node IDs and output are preserved in
`reports/sb-option-b-focused-tests.txt`. The skip is the existing optional
`runs/smoke-stage1` historical record test; that local run is absent.
Only the named files and node IDs were run, never the whole suite.

After final import-direction review, the declaration vocabulary moved to
`data/scaffolds/scorer_isolation.py`, shared by registry and verifier without a
new `data -> eval` dependency. Follow-up focused execution of
`test_scorer_isolation_option_b.py`, `test_import_direction.py` and
`test_dataset_blockers.py`: **86 passed in 13.62s**, exit 0. Commands and full
output are in `reports/sb-option-b-review-tests.txt`.

The new controls actually run a synthetic pinned scorer locally through a Docker
test double, against the real allowlisted export, for both correct and wrong
answers. A second control reaches the pristine path through `run_one` and
`evaluate`, then constructs a curve point. Service/snapshot controls assert the
original dependency network, service network, recording mounts and snapshot image
are forwarded unchanged and record `snapshot-service` on the point. These tests
do not demonstrate kernel isolation or execution of a real Docker image.

Refusing control output:

```text
tests/quality/test_scorer_isolation_option_b.py::test_comparison_across_two_classes_is_refused_with_reason REFUSED: scorer isolation class mismatch: pristine-offline, snapshot-service
PASSED
```

Additional negative controls reject bridge networking, a third projection, a
snapshot image, task/command/pin mismatch, a pristine declaration on a snapshot,
mixed trial/task/cache classes, a mixed external point and mixed curve history.
Cleanup failure cannot produce a zero. The wrong-answer control establishes that
a completed failing scorer does produce zero under the same pristine class.

`web/src/logic/compare.test.ts`: **15 passed**, including cross-class refusal,
unknown legacy refusal and internally mixed-point refusal. Output:
`reports/sb-option-b-web-tests.txt`.

Full TypeScript checking remains blocked by the existing missing
`web/src/i18n/parts` module and dependent symbol-type errors. Checking unmodified
HEAD sources in a temporary directory under this worktree reproduces the same
diagnostics; see `reports/sb-option-b-typecheck.txt`. No unrelated frontend source
was repaired. No build/deployment claim is made.

## scorer-offline-closure

**Left open, status `code-solvable`.** Closed the generic opt-in bundle-validator
integration and class attribution/comparison implementation gaps. The pristine
dispatcher performs local pinned closure checking and inspected offline runtime
validation; the synthetic controls prove those code paths and their refusals.
The global pristine-only requirement is superseded by the operator's option B.
Dataset-specific complete transitive image/ABI dependency closure, official
scorer provenance/execution, trusted resource/lifecycle observations and live
runtime/cleanup evidence are still missing. Snapshot/service points make no
offline claim. A structural class label cannot close those remaining requirements.

Remaining action: provision and validate dataset-specific scorer closures and
class-specific runtime evidence, with live controls before any pilot; preserve
snapshot/service connectivity and compare only matching known classes.

## artifact-only-state-export

**Left open, status `code-solvable`.** Closed the generic opt-in allowlisted-export
integration gap for `pristine-offline`. Synthetic controls demonstrate selected
data projection, real scorer consumption, and refusal of extra mounts. Full actor
trees/snapshots and service recordings intentionally remain available under their
recorded classes. This is an explicit supported topology, not evidence of data-only
equivalence or private-input safety. Dataset-specific authoritative allowlists,
quiescence/ownership/trial binding, private-input contracts, service recording/replay
semantics and live cleanup/equivalence evidence are not supplied here.

Remaining action: provision authoritative per-task export/private-input contracts
for pristine scorers and validate ownership, quiescence, lifecycle, cleanup and
scoring equivalence; independently review snapshot/service state surfaces under
their declared class. Do not force existing tasks into an inferred data allowlist.

Both shared IDs, statuses and dataset references remain active. Their observations
and next actions are updated to distinguish completed generic integration from
remaining dataset/live evidence. Registry validation is preserved in
`reports/sb-option-b-registry-check.txt`.
