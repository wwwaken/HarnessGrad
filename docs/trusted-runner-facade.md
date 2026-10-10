# TrustedRunnerFacade

`harnessgrad.trusted_runner.TrustedRunnerFacade` is the Task23 local facade for an
offline or scratch integration. It uses a run directory, frozen local parent trees,
and a fake or existing evaluator seam. It does not open a service endpoint, call a
model, submit paid requests, run a benchmark, or change the legacy method
stdin/stdout protocol.

## Construction

```python
facade = TrustedRunnerFacade(
    run_dir,
    parent_snapshots={"sha256:...": parent_directory},
    runner=fake_runner,
    current_snapshot_sha="sha256:...",
)
facade.issue_capability("cap-study", {
    "task_set_id": "study-1", "task_set_sha": "sha256:...",
    "visibility": "study", "adaptation_visible": True,
    "capability_id": "cap-study", "scorer_revision": "offline-v1",
    "task_ids": ["task-a"],
})
```

`parent_snapshots` is a trusted mapping from snapshot hash to a local directory. The
facade recomputes the tree hash and refuses a mismatched ref. Parent refs are sorted
canonically and `parent_set_sha` is the SHA-256 of that canonical array. A candidate
must name a base in the set and include a matching `base` lineage edge. A root
candidate must set `root: true` and include a `root` parent ref. Evidence parents may
remain unused; every other declared parent must be used. Each proposal carries an
`edits` list (or `files`/`tree` mapping), and the artifact `content_sha` is recomputed
from those bytes. Each candidate gets a separate workspace beneath `run_dir/workspaces`.

```python
build = facade.build_validate({
    "operation": "build_validate", "run_id": "run-1", "iteration_id": "iter-1",
    "parents": parents, "parent_set_sha": parent_set_sha,
    "proposals": proposals, "idempotency_key": "build-1",
})
```

The response contains immutable candidate snapshot refs, one validation result per
proposal, and `valid_candidate_ids`. Invalid candidates are retained as validation
facts and cannot enter evaluation.

## Evaluation capabilities

`evaluate_candidates` accepts only an exact task-set value previously passed to
`issue_capability`. Study and validation capabilities must be adaptation-visible;
unknown, altered, duplicate, or final-exam task sets are rejected. The evaluator seam
may be a callable or expose `run`/`evaluate` with `(workspace, task, trial)` (a
two-argument fake is also accepted). Its raw scores and costs are preserved per
candidate, task, and trial. Infrastructure failures never receive a score. The facade
does not rescale staged values.

Final reports require a private `final_exam` capability, a selection, a deployment
fact, and the selection's `finalization_seal` returned by `finalize(selection_id)`.
They are returned only as `final_report_private` artifacts and are excluded from
selection and deployment records.

## Selection, deployment, rollback

`select_deploy({"action": "select", ...})` records a deterministic selection from
stored eligible study/validation evaluations. It ignores method-reported scores and
deployment claims. `action="deploy"` reads that selection, checks
`expected_from_snapshot_sha` against the current platform snapshot, and creates a
platform deployment fact with immutable before/after hashes. A failed or tentative
status can be requested for local state-machine tests. `action="rollback"` requires
the deployment ID and validation/runtime-health evidence; final-report evidence is
rejected.

Every operation uses `(operation, idempotency_key)`. A retry with identical canonical
JSON returns the stored byte-equivalent response. Reusing the key with changed bytes
raises `IdempotencyConflict`. Records are JSON files under `run_dir`; no database is
required.

## Current boundary

This facade is intentionally a deterministic integration seam. It does not provide
the broker/recorder isolation, container snapshot lifecycle, task registry, or real
benchmark scorer needed for a production run. Real benchmark execution, model calls,
paid APIs, endpoint POSTs, and LightRSI remain unavailable in this task.
