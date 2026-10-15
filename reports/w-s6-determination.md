# S6 determination - w-s6

**Conclusion (b): S6 is structurally gated on the admission it is being used to withhold.**
Under the current interpretation, more unobserved controls cannot satisfy
“validate live controls before pilots.” S6 requires a cleared dataset diagnostic
after applicable gates, while `scorer-offline-closure`, containing S6, remains one
of those gates. There are also concrete missing observer/publication connections
in source. This is a standing structural note, not ordinary remaining control
collection. S6 stays PARTIAL; neither shared blocker nor any dataset blocker closes.

Reviewed source baseline: `bf917b3b237e352ac46373fdba501d35004c7911`, branch
`wg-s6`, isolated worktree `/tmp/hg-s6`. The worktree initially held an older
detached revision without the requested files; inspection proceeded after switching
to the existing task branch. The pre-existing untracked `TRIAGE_B.md` was untouched.
All numerical observations below come from existing files read by commands retained
in `reports/w-s6-validation.txt`; no new runtime evidence was generated.

## What “valid and cleared” actually requires

There is **no supported true value for `enforcement.policy_enforcement_observed`
in this mode**. It is a marker of an unobserved execution permission, not an
observation accumulator that eventually passes when enough controls run.

| Field or condition | Exact producer/check and consequence |
| --- | --- |
| `enforcement.policy_enforcement_observed=false` | `eval/policy/unobserved_diagnostic.py:29-34`, `Authorization.record()`, assigns literal false together with `measured`, `comparable` and `production_authorized`. No backend condition is evaluated. |
| Invocation of that producer | `driver.py:600-603` constructs `Authorization` from the operator reason and calls `.record()`; `eval/run/runner.py:160-171` scope-checks and copies the same record into execution results. Chess's trusted launcher supplies `auth.record()` directly at `reports/w-chess3-evidence/launch.py:125-129`. |
| Attempting to set the field true | `validate_record()` at `eval/policy/unobserved_diagnostic.py:37-46` requires equality with `auth.record()` and requires all four booleans false. `eval/diagnostic_receipt.schema.json:396-410` independently fixes them to false. True cannot be supplied as valid evidence. |
| `outcomes[].status`, `outcomes[].score`, coverage and top-level score | `eval/policy/diagnostic_policy.py:181-187` converts every measured outcome under an enforcement record into `unmeasured`, `score=None`, reason `policy_enforcement_not_observed`, then recomputes coverage. A raw measurement cannot survive this branch. |
| `context.gates.status`, `cleanup.status`, `snapshot.status` | Ordinary measured publication requires all three `passed`, with valid receipt hashes: `eval/policy/diagnostic_policy.py:87-93,160-168,200-212`. Unknown/failed status withholds measured outcomes even without an enforcement record. |
| **`lifecycle.publication_ready=true`** | This is the actual publication readiness boolean that must become true. `eval/admission/lifecycle_receipt.py:127-152` sets it only at terminal cleanup after the ordered lifecycle remains passed. It is replay-validated, not trusted as a free-standing boolean. |
| Lifecycle identity and result binding | `eval/admission/lifecycle_receipt.py:181-200` requires exact run/manifest/scope, sealed outcome digest and cleanup/snapshot digest agreement. `eval/policy/diagnostic_policy.py:164-168` calls this publication check. |
| Valid diagnostic eligible for expansion | `eval/policy/diagnostic_policy.py:288-319` requires **no `enforcement` record**, matching eligible selection and dataset/side/metric/hashes/endpoint/limits/gates, known provenance and limits, measured_trials=1, invalid_trials=0, unmeasured_trials=0, a separate hash-bound approved review and a fresh pilot ID. |

Therefore the transition is **to an ordinary admitted diagnostic without the
unobserved enforcement record**, with genuinely passed applicable gates and a
completed bound lifecycle. It is not a false-to-true edit to the old record.
`production_authorized=true` is not a requirement: even the lifecycle constructor
and replay validator require production authorization to remain false
(`eval/admission/lifecycle_receipt.py:36-42,157-172`). Measured score publication,
matching metric/runtime scope and separate pilot review are distinct obligations.

## What the operator can supply, and what remains unwired

`--policy-evidence` supplies a context dictionary. `driver.py:402-413` checks its
dataset/side and normally demands `context.gates.status="passed"`.
`validate_lifecycle()` checks the status/hash/detail shape, not the truth or origin
of its contents. The module expressly says structural validation cannot
authenticate a gate or review (`eval/policy/diagnostic_policy.py:1-5`). A correctly
shaped claim or an invented receipt hash is not evidence that a gate passed.

`--authorize-unobserved-diagnostic` permits only the bound diagnostic/train/no-method
case (`driver.py:390-395`; one run/task/trial/job/round scope at
`eval/policy/unobserved_diagnostic.py:22-27`). It lets unknown gates enter the
execution attempt (`driver.py:409-412`), but necessarily installs the false
enforcement record. `require_review()` explicitly rejects its presence at
`eval/policy/diagnostic_policy.py:293-294`. Operator permission cannot change this.

There are two additional source constraints, independent of the circular wording:

- **Runtime admission has no observed-success branch for policy-bearing tasks.**
  `_refuse_unobserved_policies()` at `eval/run/runner.py:39-86` returns
  `backend_observation_unavailable` when execution defaults, container state,
  resource/network/filesystem/artifact declarations trigger the hook. Its only
  ways through are no triggering declarations or scoped unobserved authorization.
  There is no trusted-observation input or successful-observer branch to populate
  `policy_enforcement_observed=true`. `verifier.timeout_s` alone deliberately does
  not trigger refusal (`:60-68`); this is not a claim that every native task refuses.
- **The driver cannot publish an ordinary staged score either.**
  `driver.py:605-620`, `save_policy_receipt()`, always passes unknown cleanup and
  snapshot summaries and omits `lifecycle`, whose default is None. It takes only
  `context` from policy evidence, so adding lifecycle/cleanup/snapshot objects to
  the input JSON cannot connect them. It then demands non-null publication-ready
  lifecycle for completion. Even with truthful passing dataset gates and no
  enforcement record, `build_receipt()` withholds measured outcomes at
  `eval/policy/diagnostic_policy.py:200-209`. The Chess launcher has the same
  unknown summaries/omitted lifecycle at `reports/w-chess3-evidence/launch.py:122-129`.

The pure lifecycle API can represent passed publication: stages are scope, admit,
execute, quiesce, score, seal, cleanup (`eval/admission/lifecycle_receipt.py:17`).
Runtime admission and cleanup recheck supplied policy/observations (`:45-74,135-136`);
execution/quiescence, score and seal check exit/timeout/OOM facts and bound outcome
and snapshot evidence (`:77-123`). A trusted collector would have to gather and
connect those actual facts. These APIs neither perform collection nor authorize
production (`:1-5`). Existing pure tests demonstrate the representation, not a live
cleared dataset control. Neither CLI option supplies the missing wiring.

## Evidence and the exact gate cycle

Read the requested reassessment and all five requested control reports. The current
packet contains **four** staged dataset receipts, including the later AppWorld
control. Direct JSON inspection gives:

| Existing staged receipt | Eligible tasks | Selected / expected trials | Measured / invalid / unmeasured trials | Score |
| --- | --- | --- | --- | --- |
| `reports/w-alf-evidence/execution/diagnostic_receipt.json` | 81 | 1 / 1 | 0 / 0 / 1 | null |
| `reports/w-net-evidence/execution/diagnostic_receipt.json` | 1 | 1 / 1 | 0 / 0 / 1 | null |
| `reports/w-chess3-evidence/execution/diagnostic_receipt.json` | 6615 | 1 / 1 | 0 / 0 / 1 | null |
| `reports/w-appworld-evidence/execution/diagnostic_receipt.json` | 147 | 1 / 1 | 0 / 0 / 1 | null |

All four retain `enforcement.policy_enforcement_observed=false`,
`enforcement.production_authorized=false`, `enforcement.comparable=false`,
`context.gates.status="unknown"`, unknown cleanup/snapshot and `lifecycle=null`.
Field locations are ALF `:15-18,41-80`, TB `:15-18,46-85`, Chess
`:15-18,44-83`, AppWorld `:16-19,51-90` in their respective JSON files.

The gate dependency is explicitly documented, not inferred from absent numbers:

| Dependency | Verbatim evidence and scope |
| --- | --- |
| Cleared S6 control requires applicable gates first | `AGENTS.md:61`: “First run a one-task/one-trial diagnostic after all dataset gates pass.” `reports/w-reassess2-shared-closures.md:36` interprets S6 as “valid matching dataset diagnostics after applicable gates.” Source enforces passing context gates at `driver.py:409-413` and `eval/policy/diagnostic_policy.py:160-168`. |
| Dataset gates include both shared blockers | The ALF, AppWorld, Chess and TB entries in `docs/dataset-blockers.json` each list `scorer-offline-closure` and `artifact-only-state-export` under `shared_blockers`. ALF's retained `context.gates.detail` says exactly: “Shared scorer-offline-closure and artifact-only-state-export remain open; no gate attestation.” TB's detail names both too. |
| Shared scorer closure includes S6 itself | `scorer-offline-closure.next_action` includes “validate live controls before pilots”; the reassessment's S6 row keeps that clause PARTIAL because staged receipts are unmeasured. Thus the admission prerequisite contains the condition whose evidence admission is supposed to produce. |
| Other shared clauses still independently gate readiness | S1 pinned dataset closures, S3 complete transitive image/ABI dependencies, S4 official provenance/execution and S5 trusted lifecycle/resource/cleanup remain PARTIAL in `reports/w-reassess2-shared-closures.md:31-36`. They supply substantive prerequisites for a future matched diagnostic. The applicable E4 quiescence/trial binding, E5 scoring equivalence and E6 lifecycle/cleanup obligations of `artifact-only-state-export` also remain partial; they do not imply pristine export contracts for datasets that do not opt in. |

The cycle is: **S6 outstanding → shared scorer gate outstanding → applicable
dataset gates cannot truthfully pass → no cleared ordinary S6 diagnostic → S6
outstanding.** The unobserved exception permits evidence collection around this
cycle, but its output is categorically excluded from clearing S6 as currently
interpreted. S5's runtime/lifecycle prerequisites and the missing observer/driver
connections add constraints; they do not remove the self-dependency.

This is a policy/admission-order cycle. The driver does **not** load the registry
and recursively evaluate clause IDs: `context.gates` is an opaque trusted-caller
attestation. Changing its string to passed would bypass the truth obligation, not
disprove the cycle. Dataset-local issues are not the sole explanation: ALFWorld
and TB currently have empty local blocker lists but retain both shared references.
AppWorld also retains `successful-task-evidence`, and Chess `interruption-closure`;
resolving those local issues alone would leave the shared dependency intact.

## Why neither (a) nor (c) follows

More passive observations, component comparisons or unobserved execution attempts
can advance other clauses at their actual scope. They cannot change an
authorization record that hard-codes non-observation, nor supply the driver's
omitted lifecycle. Producing a cleared S6 diagnostic would require resolving the
admission ordering and implementing/connecting truthful runtime/lifecycle evidence,
followed by a fresh, matching, separately reviewed diagnostic. That is structural
and integration work, not a precisely missing additional control arm that can be
run under today's unchanged contract. No such change or run is authorized here.

Conclusion (c) lacks its necessary evidence. All inspected staged dataset scores
are null. The original pristine attempt is explicitly invalid in
`tests/fixtures/hg_wpristine/evidence/measurement-audit.json`: score=null,
measured_trials=0, invalid_trials=1, unmeasured_trials=0, reason
`scorer_failed_before_control_check`. Its historical native zero and original
measured count are superseded, not erased. The corrected authored control at
`reports/w-prifix-evidence/final-control/control-receipt.json` genuinely publishes
0.0 with measured_trials=1, but also declares `benchmark=false`,
`staged_pilot=false`, and “Authored exact-answer control only; no dataset/method
equivalence or H0 authorization”. That is not a matching staged dataset receipt.

Nothing here restores withdrawn enforcement-proof requirements.
`docs/enforcement-proof-decision.md:31-55` accepts best-effort cleanup/snapshot
uncertainty, preserves known-failure/binding refusals and explicitly leaves the
runtime refusal contract intact. No infallibility, atomic lease, exhaustive absence
or quota proof is proposed as a new gate. The finding is about existing control
publication/admission wiring and ordering, not an added proof obligation.

## Proposed registry wording and disposition

Append only this observed clarification, with repository evidence pointing here:

> Standing structural note - w-s6: S6 is structurally gated on the admission it is being used to withhold. The current S6 assessment requires a cleared staged dataset diagnostic after applicable gates, including scorer-offline-closure itself. Unobserved authorization hard-codes policy_enforcement_observed=false and excludes measured publication/expansion; ordinary driver receipts also lack connected lifecycle evidence. Neither --policy-evidence nor --authorize-unobserved-diagnostic supplies that missing connection. More controls under the unchanged contract cannot clear S6. Retain PARTIAL as a structural admission-order/publication dependency; this note closes nothing and changes no gate, status, next_action, dataset reference or historical receipt.

This append is more accurate than an unqualified “valid live controls remain
unmet”: it explains why repeating the permitted controls cannot satisfy the
criterion. Preserve both shared objects/statuses/full next_actions, every dataset
blocker/reference and all history. Resolving the dependency is a future policy and
implementation decision; this determination neither grants admission nor changes
the S6 verdict.

## Validation boundary

`reports/w-s6-validation.txt` preserves commands, inspected source lines/receipt
fields, helper source and raw results. Existing pure registry/policy/lifecycle
tests passed: **246 passed**; after the documentation/registry update, the final
registry suite passed **56 tests**. Read-only checks validate all four existing staged
receipts against Python and JSON schema; in-memory attempts to set
`policy_enforcement_observed=true` are rejected by both, and original receipts
are refused for expansion. Those mutations are test objects only, never written
back. Final registry, verbatim-locator, preserved-state and diff checks are recorded
in the same validation file. No benchmark/scorer run, model, GPU, endpoint,
container, `runs/` modification or frozen-receipt edit occurred.

The unrestricted staged whitespace check flags trailing whitespace emitted by raw
line-numbering commands in the validation transcript. Those command outputs are
preserved unchanged; the authored report/registry/journal whitespace check passes.
