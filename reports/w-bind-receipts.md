# Native pristine task/run/trial binding - w-bind

The native pristine path now requires and enforces a selected task, outer run and
trial identity through bounded export, runtime admission and verdict consumption.
Foreign task/run/trial exports and verdicts are refused. E4 remains PARTIAL because
trusted source/writer custody through use is still missing. E5/E6 remain PARTIAL;
E1/E2/E3 retain only the empty-current-pristine-instance scope of
`reports/w-scope-pristine-applicability.md`. No shared or dataset blocker closes.

Worktree `/tmp/hg-bind`, branch `wg-bind`, baseline recorded in
`reports/w-bind-evidence/baseline-commit.txt`. No main commit, model, GPU, endpoint,
benchmark, dataset pilot or `runs/` write. All controls are authored local inputs.

## What the previous artifacts actually bind

Read first: `reports/w-quiesce2-receipts.md`, especially
`## Trial binding remains incomplete`, and the named raw packets. The parsed raw
review is `reports/w-bind-evidence/prior-artifact-review.json`; it reads the
`binding.json`, `events.json`, `docker-calls.json`, native `verdict.json` and binary
original/export/restored files of all three `reports/w-quiesce2-evidence/after/`
attempts, plus `reports/w-quiesce-evidence/audit.json`'s original/restored predicates.

At baseline `dc9a362`, `eval/run/runner.py:1042` owns the zero-based trial loop,
`:1050` passes outer `run_id` only into `run_one`, and `:525` passes just selected
`task_id` into `_verify`. `eval/verification/verifier.py:456` has no run/trial
arguments; `:474` dispatches only task and timeout. Baseline
`eval/verification/pristine.py:65` checks a supplied selected task against the
sealed contract; `:67` records that task and the generated runtime/export UUID,
with `outer_run_id=null`, `trial_id=null`, `outer_run_trial_binding=not_provided`.

Baseline `eval/admission/artifact_admission.py:367` emits v1 export receipts:
contract task, contract/source pins, exact selected file hashes and accounting,
and generated export `run_id`. `:384` rechecks those against caller contract and
requested runtime UUID. `:439`'s runtime admission rechecks both projections and
the inspected runtime before start. None receives an outer run or trial. Those
exact executed sources are archived under `reports/w-bind-evidence/before/sources/`.

In the prior mutation packet, the observer's `binding.json` names outer
`w-quiesce2-after-20261015T-observe-b1-source-aba-attempt-01`, task
`w-pristine-addition-control`, trial `1`. Native export/runtime/container identity
is `hg-pristine-b54a2ea99d614522a6f13cf53b0aaee4` instead. `events.json` proves a
wrong requested *export UUID* was refused, not an outer-run/trial mismatch.
`docker-calls.json` agrees with that generated container name. Native verdict
explicitly lacks outer run/trial. The passing unchanged packet uses distinct UUID
`hg-pristine-a5cbaeef81d84d07a4c39a980e2b8bb1` and likewise has no native outer binding.

Original and restored selected bytes are both `41\n`; the genuine export is also
`41\n`. The original, post-export and ABA predicates all read actual `41`, expected
`42`, completed_check=fail, exit `1` (prior audit results). The updated mutation
verdict correctly suppresses that numeric score (`difference_observed`, null,
unmeasured). The unchanged `42\n` packet genuinely passes. These predicate and
source-observation facts do not bind the observer's outer envelope to execution.

## Identity and enforcement now

- `eval/run/runner.py:916` derives `trial_id` as
  `round-{round_no}.harness-{harness_sha}.trial-{trial+1}`. Task and outer run come
  from the runner's own selected task and `run_id`; round and harness revision
  distinguish repeated ordinal trials within an outer run. `:1064`, `:167`, `:525`
  carry it through `run_one`, `_run_one`, `_verify` to pristine verification.
- `eval/verification/pristine.py:80` refuses missing/invalid task, run or string
  trial labels before export. `:93` requires contract task equality; `:95` records
  native `execution_binding` with all three labels and the generated runtime UUID.
- `eval/admission/artifact_admission.py:308` validates explicit identities. `:386`
  emits v2 receipts with `execution_binding={task_id,outer_run_id,trial_id}` while
  retaining runtime UUID, contract/source pins, bounded files, limits and hashes.
  `:405` compares the independent expected binding, schema and all old identity
  checks. `:472` still checks both projections and the complete runtime boundary
  before scorer start and records the checked binding in the runtime receipt.
- `eval/verification/pristine.py:36` rechecks returned verdict identity and its
  export/runtime/cleanup agreement. `_verify` invokes it at
  `eval/verification/verifier.py:474`; aggregation invokes it at
  `eval/run/runner.py:1087`. Cache hits are checked per expected trial, in order,
  at `:1035`; foreign/missing binding is invalid/unmeasured, never a zero.

V1 remains the unchanged unbound low-level control mode. A bound native call
cannot downgrade to v1, and a v2 receipt cannot be consumed without an independent
expected binding. No scorer predicate or completion protocol changed. Byte/inode
bounds, selected-source probes, both projection checks, exact environment/mount
admission and cleanup refusal remain enforced.

## Defeat attempts and raw evidence

Commands (fresh exclusive labels; no old run resumed or overwritten):

```sh
python3 reports/w-bind-evidence/collect.py --work-root /tmp/hg-wbind-runtime --run-id w-bind-before-20261015-a1
python3 reports/w-bind-evidence/collect.py --work-root /tmp/hg-wbind-runtime --run-id w-bind-after-20261015-b1
python3 reports/w-bind-evidence/collect.py --work-root /tmp/hg-wbind-runtime --run-id w-bind-after-20261015-b2
python3 reports/w-bind-evidence/collect.py --work-root /tmp/hg-wbind-runtime --run-id w-bind-after-20261015-b3
```

The executed collector bytes and production bytes are pinned by each `launch.json`
and retained in each packet's `sources/`; the collector was extended between
launches. `before/`, `after-initial/`, `after-incomplete/`, `after/` under
`reports/w-bind-evidence/` preserve the packets. The external originals remain
under `/tmp/hg-wbind-runtime/<run-id>/packet`. Copy-provenance manifests record
actual source/destination paths and byte hashes. The incomplete b2 packet retains
its exception in `collect-after-final.txt`; it has no retrospectively invented
summary or original packet seal.

The hostile export producer calls the real bounded `export_state` with another
identity but the *current expected runtime UUID* and unchanged answer bytes. Thus
runtime-UUID refusal alone cannot pass the outer-run/trial attacks. A different
task also gets its own genuinely resealed contract; no receipt is invented or
modified after export. The consumer still runs genuine bundle/contract admission,
source probes, both projection checks and Docker runtime inspection.

`before/foreign-export-trial_id/` was measured `1.0`; missing outer identity was
also measured `1.0`. Baseline task export mismatch was already refused. Baseline
foreign outer-run export happened to hit the existing environment-order runtime
refusal, so that case is **not** evidence of baseline binding. All three baseline
foreign-verdict consumers accepted the genuine control verdict under another
task/run/trial (`before/foreign-verdict-*.json`).

In updated `foreign-export-{task_id,outer_run_id,trial_id}/`, actual exported
receipts are refused with `state export receipt identity mismatch`, score null,
outcome unmeasured, **no Docker start**. Each attempted container is removed and
an independent inspect reports absence. Updated missing-identity refuses before
export/create. The unchanged control measures `1.0` with matching native execution,
export and runtime identities. Its genuine verdict is then presented to each
foreign consumer: all three `foreign-verdict-*.json` have empty `per_task` and
explicit execution-binding invalid reasons. Unit controls also reject a foreign
verdict returned by pristine dispatch, stale outer-run cached scores and v1
downgrade; distinct trials are checked through the outer runner.

Each case retains requested/producer identity, actual export receipt and selected
binary where exported, events, full Docker commands/results, native verdict and
absence check. Native outer-run attempts additionally retain actual agent source,
requested round/revision/trials, raw exports, Docker calls and aggregate result.
Real Docker environment-order admission failures remain unmeasured and preserved;
none was normalized, counted as a zero or used as proof of the new binding.

The complete native outer run is `after/native-outer-attempt-03/`: outer
`w-bind-after-20261015-b3-outer-attempt-03`, task `w-pristine-addition-control`,
round `3`, harness-source SHA-256
`74d75732a062c9a7a22ee34947013661df34834982d286461641364684e8398e`, trial ordinals
`1` and `2`. Native runtime/export IDs are respectively
`hg-pristine-0896eba23e114db7b79e2c43345aae68` and
`hg-pristine-9c5e8e871d4c421590a306fc2b56d873` (`result.json`, `events.json`,
`verdict-1.json`, `verdict-2.json`, `requested.json`, `docker-calls.json`). Both
measure `1.0`; the aggregate is `1.0`. The first two fresh outer attempts in this
packet are genuine environment-order refusals, with no measured trial. Earlier b2
retains three failed aggregate attempts; its second attempt completed one passing
scorer before the next trial was refused. Its aggregate stays invalid and the
collector exception stays preserved. No old run was resumed.

`audit.json` verifies **230 byte-identical copied files**. Completed packet seals
cover 50 before, 46 after-initial and 68 final-after files; the incomplete packet
is covered by byte-copy provenance without claiming a completed launch seal.
Across the four packets, respectively: created/removed `5/5`, `4/4`, `8/8`, `8/8`;
started/completed passing predicates `3/3`, `1/1`, `2/2`, `3/3`. Saved native verdicts
are measured/unmeasured `3/2`, `1/4`, `1/4`, `3/6`; the incomplete packet did not
retain its outer-loop native verdicts, so its two starts are not both counted as
saved native measurements. None of these authored-control counts is a dataset
score or valid pilot. Baseline accepted replay/foreign-trial results are unsafe
acceptance evidence, not credited measurements.

Every launch pins production/collector sources, unchanged fixture bundle,
contract/source/image hashes and metric (`authored addition control`, explicit
completion/exit protocol). Every export pins the selected answer bytes. Split and
model/endpoint are inapplicable/null: no benchmark task pool or model is used.
Declared direct limits are 60 seconds, 512 MiB, one CPU and 128 PIDs; native outer
calls use the default 3600-second agent/verifier budgets
(`eval/run/runner.py:220`, `eval/policy/runtime_policy.py:22`) and the same
inspected runtime caps; each actual Docker call remains bounded by the verifier
deadline, with a separate 30-second cleanup budget.
Actual quota tmpfs and environment/mount configuration are in the raw create and
inspect observations. `requested.json` records the two-trial native control's
coverage and jobs=1. Cleanup and independent absence are checked for every created
container. These are same-fixture before/after binding controls, not evidence of
real-dataset equivalence or H0 authorization.

## Remaining caller obligations and E4 boundary

Bound now: the selected contract task, supplied outer run and trial label, generated
runtime/export UUID and existing contract/source/file seals, checked at export
consumption and native verdict aggregation/cache consumption. Native runner trial
labels include round, supplied harness revision and one-based ordinal.

Still supplied/trusted: correct unique outer run labels; truthful task/source/trial
association; direct callers' trial labels (including retry/attempt distinctions);
correct harness revision/round inputs; authoritative contracts/private inputs and
pins; platform-owned receipts/projection parent; trusted host, runtime observations
and platform code. This is native consistency enforcement, not authentication of
arbitrary external JSON. It cannot detect a trusted caller deliberately relabeling
a wrong source consistently or reusing the same semantic identity. Persisted
verdict consumers outside the native runner must pass independent expected labels
to `enforce_verdict_binding`; reading `score` alone is not a checked consumption.
Model/endpoint, seed, dataset split/manifest authority and actor-state lineage are
not newly attested identity dimensions.

E4's native binding half is implemented under these trusted-caller assumptions.
E4 still needs trusted source/writer custody through use: endpoint probes miss the
already demonstrated transient directory substitution and are not continuous
quiescence. The `export_state` caller-quiescence obligation remains at
`eval/admission/artifact_admission.py:330`. E5 dataset transformation/private-input/
metric equivalence and E6 live backend lifecycle/cleanup remain PARTIAL. E1/E2/E3
are satisfied only for today's zero applicable pristine dataset instances.

## Exact registry observation - w-bind

Native pristine trial binding 2026-10-15 - w-bind: the opt-in native pristine path now requires selected task_id, outer run_id and trial_id, propagates the runner's round/harness-revision/one-based-trial label, emits v2 bounded exports with execution_binding, compares the independent expected identity before scorer start, records it in native verdict/export/runtime evidence and rechecks returned and cached verdicts before aggregation. Authored real-Docker controls refuse foreign task/run/trial exports before start and foreign verdicts before aggregation; focused controls also refuse missing identities and v1 downgrade. This establishes task/run/trial consistency under trusted caller labels, pins, platform receipt custody and runtime observations, not external-JSON authentication, source-lineage proof or global run-label uniqueness. Direct callers still supply truthful unique run/trial/source mappings and trusted custody. E4 remains PARTIAL because trusted source/writer custody through use and actual quiescence remain unestablished; E5/E6 remain PARTIAL. E1/E2/E3 retain only the current empty pristine-instance scope from w-scope. artifact-only-state-export remains OPEN/code-solvable with its full next_action unchanged; no dataset blocker closes and production_authorized remains false.

## Validation

`reports/w-bind-evidence/tests-before.txt`: **20 failed**, the unchanged new test
file against baseline (missing APIs/native identity). `tests-after.txt`: **20
passed**, the same file after implementation. The real baseline controls above
independently demonstrate unsafe acceptance rather than merely an absent API.
`tests-focused-initial.txt` preserves **83 passed, 1 failed**: an older cache test
supplied a bare synthetic pristine score. It now uses a genuine bound native
control while retaining its class/cache assertions. `tests-focused-second.txt`
preserves a command with incorrect test filenames (**no tests ran**).
`tests-focused-third.txt`: **303 passed**, including all binding, prior quiescence,
pristine completion/DAC/cleanup, artifact/scorer admission, registry, ordinary
verifier and trial/unmeasured regressions. Exact final commands/checker/test output
are in `reports/w-bind-validation.txt`. `audit.py` verifies raw packet and source
seals, actual score protocol, identity checks, replay results and cleanup receipts;
its output is `reports/w-bind-evidence/audit.json`. The auditor’s initial
case-sensitive Docker absence-message assertion failed on actual lowercase
`error: no such object`; `audit-initial-failure.txt` preserves that failure. The
corrected auditor recognizes the actual message without changing any receipt or
production gate.

The staged whitespace check flags trailing spaces in the preserved raw baseline
pytest traceback (`tests-before.txt`) only; those receipt bytes were retained.
The staged implementation, docs and remaining artifacts pass whitespace checking.
