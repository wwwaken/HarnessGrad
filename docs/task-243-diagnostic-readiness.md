# Task 243 — first-diagnostic readiness with optional ordinary-user quotas

**No dataset currently supports a justified first diagnostic through the reviewed
staged production path: 28 datasets, 24 blocked, four excluded, zero ready.**
This conclusion survives removing filesystem-quota backend availability as an
ordinary-user launch requirement. It rests on independent source, scoring,
admission and receipt-production gaps, not on an assertion that ordinary users
must provision quotas.

Reviewed 2026-10-14 in isolated, detached `/tmp/hg-codex-243` at HEAD
`0930d99cc882c5a049c98f9123e9427470e7e818`, tree
`40e0f4964805ce98bad2441833b80712c9b58bdc`. Initial worktree was clean.
This is a source/metadata review, not a diagnostic receipt or runtime observation.
Only task-243 review artifacts are added; production code, registry, shared journal,
main, payloads, models, H0 and backends are unchanged. No adapter import, dataset
root access, task selection, endpoint query, host inspection or run allocation occurred.

## Policy applied

| Question | Task-243 interpretation |
| --- | --- |
| Must an ordinary user have a filesystem-quota backend? | No. Missing paired byte/inode enforcement is not, by itself, grounds to reject an ordinary diagnostic. No quota capability or host-state conclusion is inferred. |
| What if formal resource-enforcement evidence is claimed? | The applicable enforcement backend, authenticated effective readback, complete writer coverage and fresh ownership/cleanup evidence remain necessary. Declared limits, capacity checks, relocation, schema checks and synthetic passes cannot establish enforcement. |
| Does optional quota waive unrelated gates? | No. Selected-only/privacy and source custody, honest metric identity, supported execution/scoring, budgets, endpoint/run binding and valid diagnostic evidence still matter. Quota-related subrequirements are removed from the ordinary-user assessment, including those nested in snapshot/resource documentation. |
| Does the old registry override this policy? | No. Its 23 eight-shared-blocker reference sets are retained as inventory, not copied as a blanket current admission rule. The registry is not edited by this task. AgentDojo retains its separate route gate. |
| Is a completed first diagnostic needed before starting it? | No. The production path to collect valid execution, scoring, snapshot/export and cleanup evidence must exist first; final observations are collected during and after execution. |

Resource/budget declarations must remain honest. Without evidence, record enforcement
as unknown/unverified and make no formal enforcement claim. Optional quota does not
turn a declaration into proof or supply an implemented ordinary-user admission path.

## Quota-independent findings

1. **The staged driver cannot produce a measured first-diagnostic receipt.**
   [`save_policy_receipt`](../driver.py#L572) always passes unknown cleanup and
   snapshot summaries and omits `lifecycle`, regardless of extra fields in supplied
   policy evidence. [`build_receipt`](../eval/policy/diagnostic_policy.py#L163) consequently
   withholds provisional measured scores as unmeasured/null; the driver refuses
   staged publication. This is a known missing producer/integration, not a demand
   for future cleanup facts before launch. It remains independent of quota policy.

2. **The simplest QA candidates also encounter a concrete non-quota refusal.**
   [`QASpec.verifier`](../data/qa/base.py#L317) declares a verifier timeout;
   [`_refuse_unobserved_policies`](../eval/run/runner.py#L33) refuses that declaration
   without trusted observations, before execution and cache lookup. A `files`
   environment therefore does not establish that GSM8K, Reasoning Gym, Physics
   Questions, Sports Understanding or StrategyQA has an admitted ordinary route.
   These source paths were inspected without materializing tasks. Existing guards
   remain unchanged; optional quota alone does not change their behavior.

3. **Current selection/provenance and scoring evidence remains incomplete.**
   Driver loading precedes diagnostic narrowing. `QASpec.records` constructs
   question/gold records for its loaded tables; GSM8K's `_rows` reads both published
   splits. A selected-only run manifest and independently reviewed data/scorer
   custody cannot be inferred from narrowing afterward. A version, seed, pool hash
   or historical test claim is useful provenance metadata, not fresh selected-run
   controls or proof of the installed scorer/runtime. No payload was opened to
   infer local availability or close these gaps.

The scorer backend now composes standalone lifecycle/resource/scorer/export
preflight checks. This supersedes older absolute claims that no composition exists,
but it does not supply the missing trusted production observer, driver integration
or actual official scoring invocation. Synthetic acceptance remains unmeasured.

## Current dataset dispositions

Every blocked row below has the staged receipt-production gap above. Dataset
notes identify additional ordinary-user concerns without carrying forward quota
as a universal gate. A journal gap means evidence is insufficient, not that an
adapter is proven defective. `demand × surface` and separate `exercises` values
are preserved in the companion JSON.

| Dataset | Disposition | Additional evidence or integration still needed |
| --- | --- | --- |
| agentdojo | Blocked | Selected-group manifest/custody and current production verifier/lifecycle/cleanup admission; metadata privacy controls do not admit execution. |
| alfworld | Blocked | Current selected runtime/control identity; a complete historical generation is not a current admission receipt. |
| api_bank | Excluded | Explicit operating-rule exclusion and unresolved released metric contract. |
| appworld | Blocked | Selected state reset/service/gold/scorer controls and installed production identity. The successful-task requirement belongs to expansion, not a demand for a positive first score. |
| bfcl_v3 | Blocked | Independent release/index custody and complete parser/checker/dispatch/helper contract. Task 227 acquired checker/type-mapping source but left helper and archive/custodian gaps. Name-only scoring is not official full-call accuracy. |
| bird_minidev | Blocked | Current selected SQL/schema/scorer reachability and failure classification. Old 28/34 coverage is a comparison issue, not a prior-run prerequisite. |
| chessbench_puzzles | Blocked | Trusted production stepwise transport/official scoring and current owned-resource admission; interrupted IDs remain immutable. |
| ds1000 | Blocked | Intended source/host-slice custody, current controls and timeout semantics; old archive comparability remains separate. |
| fever | Blocked | Current dataset-specific provenance/privacy/scorer/control review; QA refusal also applies. |
| gaia | Blocked | Full scorer-revision discrepancy, selected attachment/gold custody, dependency closure and supported runtime/export/lifecycle remain unresolved. |
| gsm8k | Blocked | QA refusal, selected-only custody and current metric/scorer binding. Decimal-aware extraction is a defined local metric; test@N and old integer-score equivalence are not required for a clearly scoped new local diagnostic. |
| hotpotqa | Blocked | Current structured-evidence scorer/control and timeout classification; QA refusal also applies. |
| jericho | Blocked | Independently reviewed selected runtime boundary and controls outside the platform checkout. |
| livecodebench | Blocked | Authenticated row/pool/split custody and official wrapped-function scoring/runtime route. |
| musique | Blocked | Freeze Answer/Support/local-joint semantics, selected denominator and custody; QA refusal also applies. |
| nestful | Excluded | Explicit operating-rule exclusion and unresolved released execution metric. |
| physicsquestions | Blocked | Current dataset-specific source/scorer/control review and QA refusal. |
| reasoning_gym | Blocked | Current generated-pool/package/scorer custody and selected controls; QA refusal. Declared seed/version/hash and historical offline-family claims do not authenticate the deployed runtime. |
| scienceworld | Blocked | Current effective protected mounts/platform identity and selected runtime controls; source prevention review alone is insufficient. |
| sotuqa | Excluded | Explicit operating-rule exclusion and unavailable headline judge metric. |
| sportsunderstanding | Blocked | Current dataset-specific source/scorer/control review and QA refusal. |
| spreadsheetbench | Blocked | Current dataset-specific source/scorer/runtime/control review. |
| strategyqa | Blocked | Current dataset-specific source/scorer/control review and QA refusal. |
| tau2_bench | Excluded | Explicit operating-rule exclusion and unavailable independent user/judge assertions. |
| tau_bench | Blocked | Selected service reset/database state, evaluator secrecy and lifecycle controls. |
| terminal_bench | Blocked | Selected dependency/trusted-runtime/export/scoring and production receipt writer. Task 230's public Harbor reference does not establish selected-task correctness or installed/historical runner binding. |
| triviaqa | Blocked | Exact Hub-export/loader/scorer/selection/grouping/denominator linkage. Task 225's historical loader is not authenticated as the converter of the pinned export; retain metric v2. |
| twowikimultihopqa | Blocked | Hub/release/split custody and image-bound Python/native scorer closure. Task 226 acquired a wheel and package-only offline installation; native transitive/runtime and notice closure remain open. |

## What changed relative to Task 234

The ordinary-user quota premise changes; the launch count does not. Task 234's
reviewed runtime/driver/adapter source pins still match current files. Five pinned
documentation/registry inputs changed: the journal, JSON and Markdown blocker
indexes, quota-backend document and task-222 checklist. The companion JSON records
their current hashes and all drift explicitly, rather than reusing an old report
as current evidence.

The latest registry now records the partial BFCL checker acquisition (227), the
historical TriviaQA loader and failed exact-Hub metadata acquisition (225), and
the acquired ujson wheel with incomplete image/native closure (226). GAIA 228,
AppWorld 229 and Terminal-Bench 230 add source evidence while explicitly leaving
their production gates unresolved. Quota readback proposal 233 is a specification,
not installed enforcement evidence. None supplies a new measured run or repairs
the unchanged staged driver.

No network failure is treated as proof of source absence or incompatibility.
No historical receipt, cached image or source test is promoted into current
runtime admission. The 11 registry historical records and their null effects are
preserved and not authenticated by this review.

## First diagnostic, completion and expansion

A future first diagnostic needs an admitted selected-only route, reviewed scorer
and metric, actual source/split/manifest/model/harness pins, a fresh run identity,
one local endpoint, concrete budgets and ownership/concurrency evidence. Use one
task, one trial, one job, zero rounds and no improver; total H0 concurrency stays
at most three. Ordinary users need not supply formal filesystem-quota evidence
unless they claim formal enforcement. Final execution/scoring/export/cleanup
observations are produced afterward through the reviewed trusted receipt path.

Expansion still requires a separate digest-bound review of one valid measured
diagnostic with zero invalid/unmeasured trials, matching scope and passing
lifecycle evidence. Only then does the temporary pilot cap become
`min(30, ceil(0.10 * eligible))`, one trial and one job. Old metric equivalence,
old interrupted-pilot completion and a nonzero first score are not universal
first-diagnostic prerequisites. A current successful-task expansion gate remains
specific to AppWorld.

GPU0 and GPU1 have the same no-start decision from source readiness; their live
availability and current global concurrency were not queried. No model-free GPU
workload is justified merely to occupy capacity.

## Validation and deliverables

The source-only registry checker passes: 28 datasets, eight inventory shared
blockers, 11 historical records, `production_authorized=false`. Static source
checks verify the driver receipt gap, QA timeout/refusal path, selected-before-run
but loaded-before-selection ordering, exact taxonomy and history preservation.
These checks import no adapter and execute no scorer or runtime. No new test is
added; no benchmark, model, H0 or backend test is run for this documentation review.

See the [metadata and current input pins](task-243-diagnostic-readiness.json),
[validation record](task-243-readiness-validation.txt) and
[one-page summary](task-243-readiness-overview.html). Review-input hashes are not
run provenance. With no task selected, eligible coverage and run identities remain
unknown, and no score or diagnostic receipt is created.
