# Eight stage runtime

The shared runtime lives in `harnessgrad.runtime`.  It defines typed values for
stage IDs, scopes, owners, artifact refs, parent lineage, lifecycle/evidence,
implementation modes, stage results, and immutable event envelopes.  The JSON
schema is `schemas/eight_stage_protocol.schema.json`; `validate_events` performs
the cross-event checks that JSON Schema cannot express.

The validator guarantees:

* exactly one phase-0 bootstrap from the framework or recorder;
* event IDs and idempotency keys are stable, causal references may arrive late,
  and causal cycles or conflicting retries are rejected;
* candidate root state and parent state are mutually exclusive, while typed
  base/donor/peer/crossover edges preserve multi-parent archives;
* `study_evaluation` and `heldout_score` have separate score kinds and producer
  authority; any held-out ancestor is tainted when passed to feedback, proposal,
  or selection;
* selection records are method claims/decisions and deployment records are
  framework/deployer facts, so selecting zero, many, tentative, or rollback is
  representable;
* default/custom/delegated/skip contracts, replay execution, nested training
  scopes, feedback consumers, partial/staged/full completeness, and deployment
  epochs are typed; a measured skip needs independent evidence;
* subject failures are measured and infrastructure failures are unobserved;
  healthy empty results remain measured.

`LegacyCompatibilityWrapper` invokes the historical one JSON stdin/stdout
entrypoint once and writes a sidecar stream.  It preserves the old response and
trajectory, records a `legacy_response` artifact, maps only the observed output
to an unverified proposal claim, and writes unobserved empty records for the
other stages.  It never infers deployment, archive, parallelism, acceptance, or
stage compliance from `changed`, `steps`, or a trajectory shape.

The runtime does not implement RRSI, DGM, LightRSI, scoring, filesystem
isolation, or trusted broker authentication.  `visibility`, producer metadata,
and lineage taint are semantic checks; the platform still owns actual mounts,
broker events, and held-out evaluator isolation.
