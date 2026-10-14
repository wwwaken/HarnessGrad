# ChessBench live stepwise runner wiring (c1)

## Change

`eval/run/runner.py::run_one` recognizes the explicit per-task
`interaction = "chessbench_puzzles.stepwise.v1"` marker, constructs the existing
`StepwisePuzzle` using trusted inline verifier gold, and starts `StepwiseRelay`
before the blocking harness launch. The relay reuses the Unix model relay's server
and allowance/receipt/cleanup pattern, calling the existing `transport_stepwise`
without weakening its exact public-field allowlist or message bounds.

The native sandbox projects a read-only socket directory and exports
`HG_STEPWISE_SOCKET`. The actor receives board/status/verdict JSON and submits one
UCI answer at a time; neither the reference line nor the session is materialized.
The absolute agent deadline, 4096-byte messages, 256 submissions and one connection
bound the exchange. Shutdown closes active I/O, joins handlers, removes the socket,
and removes the temporary directory. Interrupted exchanges, invalid references and
unclean actor exits have incomplete, unmeasured receipts without a score. Generic
provider-error classification preserves this receipt instead of replacing it.

Existing policy refusals still run first. Interactive tasks additionally require
the native files sandbox, including before any interactive cache hit. No production
admission gate has been removed or relaxed. The ordinary offline scorer and its
reward rule are unchanged.

## Protocol identity

- `verdict.protocol` and interactive `verdict.evidence.protocol` identify the point's
  protocol; the verdict saver preserves them.
- Curve points carry `evaluation_protocols[task_id]` and
  `protocol_comparability` through base, candidate and eval-side point construction.
- Offline evidence retains `official.protocol = "offline strict sequence; not
  interactive official accuracy"`, with both existing replay diagnostics.
- Interactive cache keys are separate. Evaluation refuses a mixed ChessBench
  aggregate; the plotter refuses cross-protocol comparison and changes within a curve.
- Incomplete evaluations persist `invalid[task_id].receipt`, without a per-task score
  or cache entry.

Usage and the actor wire contract are documented in
`docs/chessbench-puzzles-evaluation.md`.

## Focused validation

Only these files were run:

```text
tests/quality/test_chessbench_stepwise_runner.py
tests/quality/test_chessbench_puzzles_official_scorer.py
tests/quality/test_chessbench_puzzles_strict_replay.py
tests/quality/test_chessbench_selected_control.py
tests/quality/test_split.py
```

The new tests use fabricated puzzles with real sandboxed actor subprocesses. They
cover successive boards, reference/private-field read refusal, unexpected public
fields, killed/disconnected exchanges, partial-message absolute deadlines including
trickled bytes, oversized messages, failed launch, invalid trusted reference,
no connection, reconnect allowance, saved incomplete receipts, protocol cache
separation, refusal before cache reuse, unchanged offline reward/evidence and curve
comparison refusal. They forbid CSV/pool reads. Existing ChessBench tests also
exercise the pinned upstream scorer and released replay controls.

Final focused run: **102 passed, 1 skipped**. The skip is
`test_the_rrsi_domain_reads_the_platforms_split_instead_of_assuming_none` because
the optional `/tmp/rrsi-run` checkout is absent. No whole-suite invocation was used.

## Limits of this evidence

No model-driven interactive diagnostic or H0/pilot was launched. These tests do not
establish interactive accuracy on the released slice, compatibility with an existing
harness's move-selection loop, a valid measured diagnostic receipt, or production
authorization. Those require a separately gated real run. The local model endpoint
was not used or modified.
