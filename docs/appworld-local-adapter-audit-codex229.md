# AppWorld local adapter audit — Codex 229

Date: 2026-10-14. Scope: code/docs only in `/tmp/hg-codex-229`.

This audit reads source text only. It does not import `data.appworld`, read task
payloads or production run receipts, execute the scorer, start a service/container,
call a model, or authorize an official task, diagnostic, pilot or H0. The historical
Codex 155/169/183 reports supply context; their reported tests and closure claims
are not independently verified measurement evidence here.

## Release and scorer declarations actually present

| Item | Current code declaration | Evidence |
| --- | --- | --- |
| Data release | `data-0.1.0.bundle`; declared SHA-256 `fd9f9608c2ec71ed0ac25c3633a738b9129a318a129e31230425b9188e508250` | [adapter](../data/appworld.py#L327), lines 327–338 |
| Public download URL | `https://s3.us-west-2.amazonaws.com/appworld.dev/data-0.1.0.bundle` | [adapter](../data/appworld.py#L333), line 333 |
| Package requested by service Docker build | `appworld==0.1.3.post1`; `appworld.cli install --no-repo` follows | [Dockerfile](../data/appworld/Dockerfile#L3), lines 3–5 |
| Agent image default | `harnessgrad/appworld-agent@sha256:d3a04ec8e295710347e978d8e58c663161d829e7dfa544da4d82d0d67abbd8eb` | [adapter](../data/appworld.py#L53), lines 53–56 |
| Action service image default | `harnessgrad/appworld-service@sha256:db09e34ec90347e7d5271d95445f360222ba1aef3ca0eaa5614ce768bf23aca4` | [adapter](../data/appworld.py#L57), lines 57–60 |
| Verifier image default | `harnessgrad/appworld-service@sha256:f3cb916b9bdc297d4c73dd9646e9550befb7c6e23827d937b90a0640373e97ca` | [adapter](../data/appworld.py#L61), lines 61–64 |
| Local pool pin | SHA-256 `970c39331bc350ce9d3ed91a75fd32b554c257fc48fc31633dfccdde74164e65` | [adapter](../data/appworld.py#L65), lines 65 and 159–165 |
| Scoring call | Fresh `AppWorld(..., ground_truth_mode="minimal")`, replay recorded API requests, then `world.evaluate()` | [checker](../data/appworld/verify/check.py#L38), lines 38–60 |
| Task scalar | `1.0` iff `tracker.success`, otherwise `0.0` | [checker](../data/appworld/verify/check.py#L61), lines 61–75 |

The image values are configurable through `HG_APPWORLD_IMAGE`,
`HG_APPWORLD_SERVICE_IMAGE` and `HG_APPWORLD_VERIFIER_IMAGE`; the defaults alone
do not establish a particular production run's effective images. The service
Dockerfile pins a package version but has no package archive hash or upstream
source commit, and its base image is a tag rather than a digest. No separate
verifier Dockerfile appeared in the bounded Docker/build filename inspection.
The adapter docstring says “AppWorld 0.1.3” while the build specifies
`0.1.3.post1`; neither statement proves the contents of the verifier image.

The adapter describes `ground_truth/evaluation.py` and
`appworld.evaluator.TestTracker` as the released scoring authority
([adapter](../data/appworld.py#L49), lines 49–51). The checker delegates to
`world.evaluate()` rather than naming an evaluator source hash. These local
declarations alone do not authenticate the canonical upstream release, evaluator
implementation, or license. The separate [canonical public-source review](../reports/appworld-canonical-source-codex229-report.md)
supplies pinned public code/license evidence; task evaluator payloads were not
inspected and actual production-image correspondence remains unverified.

## Current split and metric mapping

| Declared source split | Local public report label | Harness side | Declared count |
| --- | --- | --- | --- |
| `train` | Train | train | 90 |
| `dev` | Dev | train | 57 |
| `test_normal` | Test-N | eval | 168 |
| `test_challenge` | Test-C | eval | 417 |

Counts and `SPLIT_SOURCE="declared"` are constants in
[adapter](../data/appworld.py#L44), lines 44–47; the harness partition is in
[adapter](../data/appworld.py#L194), lines 194–199. The report's labels are in
[reporter](../eval/appworld_reporting.py#L13), lines 13–17. These are source-code
declarations, not a fresh validation of bundle contents or split coverage. The
paper-era train/dev counts in the adapter docstring are an attributed historical
claim; this audit does not use them as verified release facts.

The checker records metric `appworld.task_goal_completion`, display name `TGC`,
task ID, and supplied source split. A measured result includes Boolean
`tracker.success` and tracker test details; missing logs, unreadable logs and
environment failures produce `measured=false` and exit 3
([checker](../data/appworld/verify/check.py#L12), lines 12–18, 29–37 and 59–74).

The current reporter's TGC is the fraction of measured task/trial Boolean
successes. Its SGC identity is `appworld.scenario_goal_completion`; SGC is the
fraction of same-trial conjunctions of all three variants of each scenario.
Scenario and variant are parsed from task ID suffix `_1`, `_2`, `_3`, and
cross-split scenarios are rejected
([reporter](../eval/appworld_reporting.py#L20), lines 20–41 and 155–182).
Incomplete variant selection, nonmeasured cells, or unaligned trials withhold
SGC. A conjunction of task means is never used. The separate canonical review
confirms upstream task/scenario metric terminology and all-variant aggregation.
The acquired generic source does not itself fix the variant count at three;
release-wide membership remains unverified in this payload-free scope.

Measured report cells require `measured is True`, the exact TGC metric identity,
Boolean `success`, and no invalid/unmeasured override. Generic `passed`, scalar
scores, or means cannot supply these facts. The report rejects explicit
task/split/trial contradictions but permits absent evidence task/split fields
([reporter](../eval/appworld_reporting.py#L120), lines 120–153). Report fractions
exclude missing, invalid and unmeasured cells and publish coverage separately.
`recorded_unmeasured_task_trials` is a disjoint count;
`unmeasured_task_trials` is the aggregate of invalid + missing + recorded
unmeasured ([reporter](../eval/appworld_reporting.py#L184), lines 184–219).

## Saved writer capability and exact production evidence gap

The current saved-verdict writer copies supplied `trial`, `invalid`,
`unmeasured`, `evidence`, and scorer test tallies. A verdict without `trial` on
itself or its evidence becomes `trial_aligned=false`. It persists selected tasks
with scores, final verdicts, histories or nonmeasurement flags; malformed
evidence and explicit histories survive for report refusal
([writer](../harnessgrad/records.py#L506), lines 506–523 and 542–588). This is an
input-preservation capability, not scorer-origin authentication.

The current AppWorld checker emits no original numeric `trial` identity, run ID,
round, canonical source commit, evaluator hash, effective package/image receipt,
model/harness identity, endpoint binding, eligible-pool count, resource/budget
receipt, snapshot receipt or cleanup receipt in its metadata/evidence
([checker](../data/appworld/verify/check.py#L29), lines 29–30 and 61–74).

The production runner iterates `for trial in range(trials)` but does not pass
that number into `run_one` or add it to the returned verdict. Provider failures
after a successful trial may be skipped. Multi-trial histories are lists of the
surviving verdict dictionaries, without original numeric identity added
([runner](../eval/runner.py#L915), lines 915–926, 948–959 and 1096–1098).
Consequently the saved writer cannot establish same-trial SGC from this route's
new anonymous checker verdicts, even if all three variants are selected and
their TGC cells are measured; single anonymous verdicts are also unaligned.
The reporter's legacy complete-anonymous ordering compatibility remains in
lines 92–100, but explicit writer unaligned markers prevent that compatibility
from inventing identity for new records.

The progress writer persists generic score/trial scores, last `passed`,
`kind`, `detail`, `tests`, wall clock and completion status; it omits final and
per-trial metric evidence and original trial identity
([progress writer](../eval/tracing.py#L210), lines 210–237). These files cannot
replace measured AppWorld receipts.

The separate trusted-runner facade invokes an injected runner with a trial
index and emits string `trial_id` values, but removes nested `verdict` from its
output. It does not project nested AppWorld scorer evidence or a one-based
numeric `trial` into the saved-verdict/report contract
([trusted runner](../harnessgrad/trusted_runner.py#L393), lines 393–448 and
497–509). Its generic score/status cannot fill missing TGC evidence.

The shared verifier does preserve a JSON evidence file on the command/reward
path and marks a missing evidence file unmeasured
([verifier](../eval/verifier.py#L598), lines 598–641). That preservation neither
creates missing original trial IDs nor binds the scorer source to production.

Exact unresolved production writer requirement: a trusted producer must supply
and persist each selected task's original one-based trial identity and the
actual scorer's metric/measured/Boolean success/task/split facts, including
explicit invalid and unmeasured cells, without rebuilding any fact from scalar
score, `passed`, survivor ordering or string-ID parsing. A separately bound
receipt must attest effective evaluator/package/image source, declared split
and manifest hashes, source/model/harness hashes, endpoint, eligible and selected
coverage, limits/budgets, snapshot lifecycle and cleanup. The current code-only
audit supplies none of those production receipts and makes no production
readiness or successful-task measurement claim.

Validation for this document is source inspection and `git diff --check` only;
no synthetic test result is promoted to a production measurement.
