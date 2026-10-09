# Task 18 report

Implemented the generic eight-stage runtime in `harnessgrad.runtime` and kept
method algorithms and drivers unchanged.

## Delivered

* `schemas/eight_stage_protocol.schema.json` carries bootstrap phase 0, typed
  scopes, stage modes, producer/visibility metadata, multi-parent lineage,
  patch/full-file/tree/prompt/skill/memory/policy/checkpoint artifacts,
  study/held-out score namespaces, replay, partial/staged/full completeness,
  nested scope fields, deployment epoch, and async attempt/idempotency fields.
* `harnessgrad.runtime.events` provides stdlib dataclasses, immutable artifact
  references, `StageResult`, hashing, a phase `EventRecorder`, and reconciliation
  records. Retries with the same idempotency key are exactly-once; a changed
  semantic payload is rejected. Late events stay in the append-only stream.
* `harnessgrad.runtime.validator` validates schema plus causal DAG, duplicate and
  idempotency conflicts, typed parent/crossover rules, root/parent consistency,
  delegate declarations, skip evidence, failure/evidence classification,
  producer authority, selection/deployment separation, and indirect held-out
  lineage taint into adaptation stages.
* `harnessgrad.runtime.compat` and `harnessgrad.compat` provide a legacy wrapper
  around the existing one JSON stdin/stdout entrypoint. It preserves stdout,
  stderr, exit code, trajectory, and old `changed`/`steps` values as claims;
  missing stage behavior is `custom`, `unverified`, and `unobserved`.

## Invariants

Platform facts are only emitted by trusted framework/deployer/evaluator/recorder
roles. A method cannot turn a reported score or acceptance into a deployment
fact. Held-out artifacts are private and cannot flow through arbitrary derived
artifact ancestry to feedback, proposal, or selection. A healthy empty result is
measured; recorder/evaluator/delegate outages are unobserved. A skip needs a
reason, preconditions, invariants, and independent measurement when marked
measured. Event arrival order has no causal meaning; explicit causal references
and reconciliation preserve asynchronous runs.

The validator checks metadata and lineage semantics only. It does not provide
filesystem isolation, broker authentication, or evaluator secrecy; those remain
platform/task14 responsibilities. No RRSI, DGM, or LightRSI algorithm was added.

## Validation

Machine-readable results are in `test_outputs.json`. Focused runtime tests cover
multi-parent DGM archive, Dream replay, full-file SICA artifacts, nested proposer
training, async late events and retries, multiple/none/tentative selection,
healthy empty results, indirect held-out taint, forged deployment, and legacy
compatibility. All passed without paid APIs or full-suite execution.
