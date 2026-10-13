# Staged receipt correctness audit — Codex 193

The current driver cannot produce a publication-ready staged receipt or curve.
Its successful evaluation path supplies `cleanup=unknown`, `snapshot=unknown`,
and `lifecycle=None`. Scores become unmeasured/null and the driver returns 2.
The offline lifecycle library can reach `publication_ready=true` with complete
supplied facts; synthetic fixtures demonstrate this structural capability only.
They do not establish real backend observations or production authorization.

Reviewed base: `a58b4b181193a2e2b201c6353722725ad77b597c`.
Workspace: `/tmp/hg-codex-193`, an existing isolated detached Git worktree.
Scope: source and authored synthetic tests. No dataset acquisition or released
task reads, heldout access, model requests, H0 execution, Docker/backend queries,
GPU work, paid endpoints, or method tuning. Synthetic runner tests stub launch
and verification; synthetic driver tests stub evaluation and dataset loaders.

## Correctness fixes

| Finding at the reviewed base | Narrow fix | Evidence |
| --- | --- | --- |
| A timeout is returned by `run_one` as exit -1. A trace containing usage can leave `harness_failed` empty, so the staged adapter classified the retained `per_task` score as measured. Other nonzero exits could have the same outcome. | `evaluation_outcomes` checks explicit `harness_output[task].exit_code`: nonzero integer exits are invalid/null; unknown or non-integer exits are unmeasured/null. Exit 0 preserves the scorer's metric, including real zero. | `eval/runner.py:428`, `eval/runner.py:632`, `eval/runner.py:1109`, `eval/diagnostic_policy.py:248`; tests traverse actual `run_one` and aggregation with a stubbed launch and scorer. |
| Reserving a fresh receipt directory did not reserve the workspace identity. The driver deleted an existing workspace under the same ID, including incomplete evidence from another run root. | Staged runs refuse existing workspaces and reserve their parent directory exclusively. Existing parent-only evidence also causes refusal. | `driver.py:826`; tests preserve sentinel evidence and the initial plan. |
| Fresh staged runs called `services.reap(run_id)`, a legacy crash-recovery operation which removes resources selected by run labels/names. A new receipt root does not prove ownership of those resources. | Staged runs skip legacy reaping. Ordinary runs retain their existing behavior. | `driver.py:926`, `eval/services.py:271`; synthetic driver tests forbid reaping. |
| JSON Schema accepted `status=passed, receipt_sha256=null` in an incomplete summary, while Python rejected it. The schema's measured-score conditional masked this mismatch in measured receipts only. | The shared summary definition now requires a string hash whenever status is passed. The existing SHA-256 pattern still applies. | `eval/diagnostic_receipt.schema.json:424`, `eval/diagnostic_policy.py:79`; tests cover gates, cleanup, and snapshot. |

The adapter change affects staged classification only. The general runner retains
its existing rule that a working artifact can receive a score after a harness
crash. No observer, fabricated passing evidence, or runtime authorization was added.

## Schema, validator, and write-path alignment

The JSON Schema is a shape check, not a substitute for `validate_receipt`.
This remains explicit in its description and in the original lifecycle contract.

| Layer | What it checks or supplies | Exact remaining gap |
| --- | --- | --- |
| JSON Schema | Required fields, types, enums, summary hash format, measured-score publication flags | `lifecycle.binding` has no required identity fields; `events` has no item schema or successful-sequence requirement. It does not replay events, verify digests, bind outcomes/scope, recompute coverage/means, enforce staged counts, or impose the lifecycle byte limit. A completed-looking lifecycle with its events removed passes shape validation but fails Python replay; a synthetic test records this distinction. |
| Python receipt validator | Recomputed coverage/mean, policy count, explicit full outcome rows, lifecycle replay and scope binding; measured rows require matching seal/cleanup/snapshot digests | Without the eligible ID list it cannot recompute the eligible-pool hash or prove deterministic selected IDs. `build_receipt` checks the actual selection, and `require_review` checks it against the current eligible pool. Neither a digest nor review text authenticates the observer/reviewer. |
| Python versus JSON scalar rules | Python `_text` requires some non-whitespace content and integer fields use exact `int` types | Schema `minLength=1` accepts whitespace-only text. JSON Schema regards integral numeric representations such as `1.0` as integers; Python rejects a deserialized float for trials/jobs/coverage. These differences remain reported rather than widening runtime acceptance. |
| Publication versus expansion | Measured publication requires a complete lifecycle and passed summaries; expansion additionally requires known provenance, endpoint, scorer hash and limits | Nullable provenance other than the lifecycle manifest can remain unknown in a structurally published receipt. A lifecycle's `publication_ready` flag alone does not authorize expansion. For receipts containing no measured rows, the validator checks lifecycle scope but does not bind the seal to the current withheld outcomes or summary hashes. Consumers must use the whole receipt/review contract. |
| Driver writer | Copies the supplied context, writes an initial plan and later adapts aggregate evaluation outcomes | It never passes a lifecycle to the builder, including if the policy-evidence object contains one. The passing gate hash is supplied evidence; the driver checks dataset/side and configured live endpoint, but does not recompute the asserted source/split/model/harness/manifest/scorer hashes or prove resource/budget enforcement. |

Source: `eval/diagnostic_receipt.schema.json:318`,
`eval/diagnostic_policy.py:50`, `eval/diagnostic_policy.py:163`,
`eval/diagnostic_policy.py:200`, `eval/diagnostic_policy.py:265`,
`eval/lifecycle_receipt.py:157`, `driver.py:372`, `driver.py:414`,
`driver.py:572`. These are current source observations, not claims about measured
backend behavior.

## Actual runner shape and missing backend evidence

`run_one` returns a singular task result: `task_id`, `answer`, `trace`,
`exit_code`, `stderr`, `verdict`, `env_usage`, `harness_runtime`,
`runtime_boundary`, gateways, and identity. Refusals use `_invalid` with an
invalid-reason object and exit null. It does not return `trials`, `per_task`,
plural verdicts, or a shared lifecycle receipt.

`evaluate` aggregates these into `trials`, `per_task`, `verdicts`, `invalid`,
`not_run`, `cached_tasks`, `harness_failed`, `harness_output`, and other reporting
fields. `evaluation_outcomes` consumes this aggregate, not a raw `run_one`
result. Scorer-unmeasured failures enter the runner's `invalid` map before
aggregation, so the staged receipt usually counts them as invalid rather than
unmeasured. Both categories remain null scores; there is no invented zero.

The backend does not currently supply the independently observed facts needed
by the lifecycle: enforced resources/filesystems/network and read-only root,
exit/OOM/timeout observations, stopped-process proof, scorer/artifact linkage,
completed bounded snapshot worker/export, and exact owned-resource absence.
`runtime_boundary` records selected settings, not their enforcement. The native
return has no explicit OOM/running facts; timeout is represented as exit -1.
Cleanup warnings are printed, and `rmtree(ignore_errors=True)` does not prove
absence or produce a bound cleanup receipt. A zero exit cannot fill these gaps.

Policy-bearing tasks are also refused before manifest/backend access by
`_refuse_unobserved_policies`, including normalized exec defaults, declared
resource/network/filesystem policies, verifier timeouts, and container state.
Cached verdicts cannot substitute for observations. Legacy files tasks without
these declarations can still be scored by the general runner, but cannot make
the staged driver's lifecycle gate pass.

Source: `eval/runner.py:33`, `eval/runner.py:129`, `eval/runner.py:458`,
`eval/runner.py:480`, `eval/runner.py:974`, `eval/runner.py:1109`,
`eval/runner.py:1218`; `eval/lifecycle_receipt.py:94`.

## Failure persistence

| Failure point | Evidence retained by the staged driver |
| --- | --- |
| Before selection/narrowing completes and the run directory is reserved | No guaranteed plan. Dataset loading, selection, narrowing or early preflight can fail before the plan write. |
| After `staged_plan.json` is successfully written | The initial full selected-task plan remains unmeasured/null, with unknown cleanup/snapshot and lifecycle null. Runtime preparation refusals, workspace conflicts and raised evaluation errors preserve this file. |
| Evaluation returns an aggregate invalid/unmeasured/runtime-failed/cached result | A separate `diagnostic_receipt.json` is written before curve refusal. It records the selected outcomes and counts. The initial plan remains unchanged. |
| Evaluation returns otherwise successful scores | The final receipt withholds the scores because lifecycle evidence is unavailable. Both staged train and eval paths refuse curves. |
| Evaluation raises, is interrupted, or adaptation/validation fails before the final write | The initial plan survives; there is no guaranteed final diagnostic receipt or exception-specific outcome. Existing progress files may contain partial observations. |
| A process dies during the initial/final receipt write | Exclusive creation prevents overwrites, but direct `open('x')` writes are not atomic or fsynced. A partial/unparseable file is possible; a subsequent writer refuses the existing filename. No stronger crash-durability claim is justified. |

Tests cover score return, invalid return, raised evaluation error, preservation of
old workspace evidence, and unchanged plans on run-ID reuse. Existing tests cover
an interruption at console attachment and the eval-side receipt callback.
No test resumes an old ID. Later trusted evidence needs a new filename and its
own exact-hash review; no existing receipt was overwritten.

Source: `driver.py:550`, `driver.py:564`, `driver.py:572`, `driver.py:588`,
`driver.py:1076`, `harnessgrad/loops/eval_side.py:122`,
`eval/diagnostic_policy.py:297`.

## Safety and integration gaps retained for separate work

- Progress artifacts still expose the general runner's provisional `score`,
  `trial_scores`, and `complete=true` before staged lifecycle publication.
  A timeout with usage can leave such a progress row even though the fixed staged
  adapter marks it invalid. The synthetic shape test demonstrates this. Progress
  completeness describes task reporting; consumers must not treat it as publication
  readiness. Closing this requires explicit staged context and consumer integration
  (`eval/tracing.py:159`, especially lines 221–229).
- Source/provenance/gate/review hashes bind supplied objects but do not authenticate
  their origin. The driver does not independently verify all asserted pins against
  this execution. No trusted collector or attested later-receipt write path exists.
- Dataset and setup/verifier/environment loaders run before narrowing
  (`driver.py:436`, `driver.py:491`, `driver.py:550`). This audit does not establish
  selected-only/privacy closure or official scorer dependency/network closure.
- Receipt limits are declarations and comparison inputs. This policy has no global
  H0 concurrency lease, filesystem quota enforcement, cleanup quarantine action,
  or snapshot capacity reservation. `jobs=1` alone does not enforce global concurrency.
- Run/ workspace exclusivity is local to the chosen roots. Skipping staged reaping
  prevents deletion by this path; it does not create a global backend ownership
  registry or prove globally unique resource names.
- Explicit non-staged sampling keeps the existing legacy curve paths. The shared
  lifecycle gate is not a repository-wide publication guarantee.

These are source-backed missing capabilities. No live observation or production
measurement was attempted, and no synthetic pass authorizes diagnostic expansion.

## Validation

New regression module: `tests/quality/test_staged_receipt_audit_codex193.py`.
It blocks subprocesses, sockets, and Docker calls; the one permitted launch path
is replaced with an authored file-writing stub. All scratch writes stay in this
worktree. Before fixes, the initial regression run had **18 failed, 4 passed**.
The first post-fix attempt exposed three missing test-fixture manifest stubs;
those were corrected without changing production behavior. The final suite has
**479 passed**, no failures or skips, with exit 0. `git diff --check` passed.

```bash
mkdir -p /tmp/hg-codex-193/.scratch/staged-audit-codex193/tmp
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
TMPDIR=/tmp/hg-codex-193/.scratch/staged-audit-codex193/tmp \
python -m pytest -q -p no:cacheprovider \
  --basetemp=/tmp/hg-codex-193/.scratch/staged-audit-codex193/final \
  tests/quality/test_staged_receipt_audit_codex193.py \
  tests/quality/test_diagnostic_policy.py \
  tests/quality/test_lifecycle_receipt_codex177.py \
  tests/quality/test_pilot_sampling.py \
  tests/quality/test_shared_admission_wiring_codex163.py \
  tests/quality/test_runner_admission.py
```

Captured result: [staged-receipt-audit-codex193-test-result.txt](staged-receipt-audit-codex193-test-result.txt).
The tests certify these offline correctness contracts only. No main merge or
backend deployment was performed.

Visual companion: [staged-receipt-audit-codex193.html](staged-receipt-audit-codex193.html),
rendered locally with the `answer-me-with-html` skill. Task-created synthetic
scratch directories were inspected and removed after validation.
