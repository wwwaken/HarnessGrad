# Shared blocker reassessment - w-reassess2

**Neither blocker closes.** Against round 47's
`reports/w-reassess-shared-closures.md`, **E1/E2/E3 change PARTIAL → SATISFIED
only for the current empty pristine dataset instance set**. No S verdict changes.
The deciding clauses are **S1/S3/S4/S5/S6** and **E4/E5/E6**, all PARTIAL.

Reviewed HEAD: `13b26a640c43bcce1dd01edab4b3485eaa92de6a`, registered
`/tmp/hg-reassess2`, branch `wg-reassess2`, 2026-10-15. The user-named reports
were read in the requested order, starting with round 47's clause framework;
their conclusions were checked against current source and existing raw packets.
Independent read-only S/E audits in registered temporary worktrees agreed with
the parent review; those temporary worktrees were removed. No benchmark, scorer,
model, GPU, endpoint or container was executed, and no runtime evidence was
created. Only file/source inspection, hashing, the registry checker and its
source-only tests were used.

SATISFIED applies to the quoted clause's scope. Class exercise, import-payload
installation, component execution, dataset coverage and cleared pilot controls
are different facts. A fixed defect supplies neither new dataset coverage nor
retroactive validity to an old receipt.

## scorer-offline-closure

Own `next_action`, verbatim from `docs/dataset-blockers.json`:

> Provision dataset-specific pinned scorer closures and class-specific runtime evidence, including complete transitive image/ABI dependencies, official provenance/execution and trusted lifecycle/resource/cleanup observations; validate live controls before pilots, preserve snapshot/service connectivity and compare only matching known classes.

| ID / distinct quoted clause | Round 47 → now | Evidence, reason and remaining obligation |
| --- | --- | --- |
| S1 “Provision dataset-specific pinned scorer closures” | PARTIAL → **PARTIAL** | `reports/w-wheelhouse-payloads.md`, `tests/fixtures/hg_wwheelhouse/{manifest,built-artifacts,install-summary}.json`: two complete **nonempty Python import-payload profiles**, Chess and ScienceWorld; eight implemented scorers require no third-party distribution payload; nine host import profiles remain partial. The retained 130 payloads are available and hash-match, but interpreter/OS ABI, execution-selected task inputs and runtime custody are separate. `mkl-service==2.4.0` has no compatible artifact in the checked PyPI response; DS-1000 also has unpinned absent TensorFlow/XGBoost and a Gensim/SciPy incompatibility. `tests/fixtures/hg_wuvx/resolution.json` adds one tooling bootstrap, not a complete dataset scorer closure. Round 47's absence of provisioned portable dataset closures still holds. |
| S2 “class-specific runtime evidence” | SATISFIED → **SATISFIED** | Retain round 47's revised verdict at **class-exercise scope**: `reports/w-prifix-evidence/final-control/verdict.json` (pristine), `reports/w-alf-evidence/runtime-attempt/run-one-result.json` (actor-workdir), `reports/w-net-evidence/execution/diagnostic_execution.json` (actor snapshot), `reports/w-appworld-evidence/role-observations.json` (mounted service), and `reports/w-chess3-evidence/execution/task-result.json` (in-process). These exercise every known class and both reviewed snapshot/service shapes. No claim that every dataset or runtime branch ran follows. |
| S3 “including complete transitive image/ABI dependencies” | PARTIAL → **PARTIAL** | `reports/w-pin-image-digests.md` and current `data/datasets/{gaia,tau_bench}.py` confirm the defaults are digest-pinned, as round 47 already acknowledged. `reports/w-uvx-bootstrap.md` and `tests/fixtures/hg_wuvx/resolution.json` now pin and demonstrate offline tooling bootstrap for **1/89 TB tasks**: OpenSSL only, CPython 3.13.7, six wheels and 19 .debs under its cached base. The production script still fetches mutable inputs; the other **88/89** bootstraps are unresolved here. `reports/w-snapfix-receipts.md` repairs expected/consumed snapshot identity and actor startup before checker entry; this is **zero additional dataset coverage**. Remaining: TB's 89 movable declarations/three absent images in the retained inventory; execution-selected dependencies/providers/inputs, inherited-volume handling, actor-owned checker/interpreter/tool integrity and missing historical payloads. No fresh image inspection was performed in this reassessment. |
| S4 “official provenance/execution” | PARTIAL → **PARTIAL** | **Revise factual coverage 15 → 22 component-covered datasets**, using `tests/fixtures/hg_woffscorer3/coverage-summary.json` and the raw component results identified below; TB separately retains its one official task-script execution. **Revise the remaining AppWorld scope:** `tests/fixtures/hg_wawp/comparison.json` establishes **3/732 released predicates**, nine numeric/tracker agreements; **729 remain unexecuted**. BFCL complete imports still fail `tree_sitter`; Chess complete import fails `absl`; BIRD and BIG-bench retain selected-function rather than full-module evidence. Other family/task/input breadth and source/acquisition provenance remain bounded. Neither component presence nor 732/732 static AppWorld byte matches establishes complete official execution. |
| S5 “trusted lifecycle/resource/cleanup observations” | PARTIAL → **PARTIAL** | **Revise factual breadth:** `reports/w-jvm-evidence/observations.json` and its linked proc/trace/cleanup files add actual ScienceWorld JVM, Jericho libfrotz, SpreadsheetBench LibreOffice, DS-1000 children, LCB worker and BIRD in-process SQLite observations. Limits belong to the **collector's envelope**; ScienceWorld/LibreOffice cleanup includes external subreaper assistance. `reports/w-scratch-evidence/host-after/observation.json` and `reports/w-scratch-evidence/after/ds1000/scratch-observations.json` establish removal of the demonstrated DS wrapper leak, not broader production cleanup. Historical AppWorld `container-observations.jsonl`/`cgroup-live-observations.json` still show the uncapped service; `reports/w-caps-resource-custody.md` supplies no live post-change service observation. Remaining: applicable production envelopes/independent lifecycle and cleanup across uncovered runtime, timeout/error and dataset paths, including GAIA/Tau and the corrected service. |
| S6 “validate live controls before pilots” | PARTIAL → **PARTIAL** | Current `reports/w-{alf,net,chess3,appworld}-evidence/execution/diagnostic_receipt.json` each retains **measured=0, unmeasured=1, invalid=0, score=null**, `policy_enforcement_observed=false`, `non_comparable_reason=policy_enforcement_not_observed`, `production_authorized=false`. None clears this clause. Round 47's genuine authored pristine measured failure remains real; w-bind adds bound authored passing predicates, and newer packets add offline scorer controls. These are not valid matching dataset diagnostics after applicable gates. Raw numeric results, fixed snapshot startup and passive lifecycle observations do not rewrite staged publication. |
| S7 “preserve snapshot/service connectivity” | SATISFIED → **SATISFIED** | Current `eval/verification/verifier.py::_verify_container_state_inner` retains the owned network and declared bridge; `_verify_inner` retains running-service networking and `services_mod.mounts_for` recording binds. `reports/w-net-evidence/launch/resource-observation-receipt.json`, `reports/w-appworld-evidence/role-observations.json` and `reports/w-snapfix-evidence/scope-audit.json` corroborate the bounded observations/preserved source paths. Network-none pristine is not imposed on snapshot/service routes. |
| S8 “compare only matching known classes” | SATISFIED → **SATISFIED** | Current `eval/verification/isolation.py::{observed_class,common_class,require_comparable,record_class}` and `web/src/logic/compare.ts::{compareRuns,isolationProblem}` retain unknown/mixed comparison refusal and suppress invalid deltas. Homogeneous unknown records may survive as diagnostic records, not comparable scores. Other metric/split/model/policy matching obligations still apply. |

**Bottom line: NOT CLOSED. S1/S3/S4/S5/S6 decide it. No S verdict is revised.**
S2/S7/S8 remain satisfied at their original scopes.

### Official execution: what changed and what did not

The prior fifteen components remain `fever`, `physicsquestions`,
`sportsunderstanding`, `gsm8k`, `strategyqa`, `hotpotqa`, `triviaqa`, `musique`,
`twowikimultihopqa`, `reasoning_gym`, `bird_minidev`, `ds1000`,
`spreadsheetbench`, `jericho`, `scienceworld`. W-offscorer3 adds the following
seven; counts stay separate across metrics and caller profiles.

| Addition / exact evidence under `tests/fixtures/hg_woffscorer3/` | Actual measured scope |
| --- | --- |
| `gaia_tau/comparison.json` | GAIA full pinned scorer: 20/20 numeric agreements, three gold-sentinel refusals. Tau full Env on authored retail state: 9/10 agree, one output-replay divergence, one unfinished/classification boundary. No new production snapshot-route observation. |
| `bfcl/compare.json` | Selected authentic parser/Simple checker functions: 11/16 numeric agreements, five name-only/full-call divergences, seven official exceptions; full imports fail. |
| `code_chess/comparison.json` | LCB full runtime/aggregation: 10/10 numeric agreements, two malformed local-unmeasured boundaries; twelve strict-profile IPC failures preserved separately. Chess selected official function: 6/10 strict numeric agreements, four divergences, five input/supplier exceptions. |
| `worlds/comparison.json` | ALF full installed evaluator/native authored game: 5/5 numeric agreements plus upstream empty-horizon exception. AppWorld generic evaluator/authored predicate: 6/6 agreements; those six do not exercise released predicates. |

W-awp **separately** executes unchanged released AppWorld predicates
`82e2fac_1`, `50e1ac9_1`, `cf6abd2_2`: `tests/fixtures/hg_wawp/comparison.json`
and `raw/<case-id>/<official|local>/` retain nine common-input numeric and tracker
agreements, no final unmeasured/exit failures. Each route executes 36 checks,
12 pass/24 fail. Two injected gold-answer controls pass answer-only predicates;
the note-edit predicate still fails. These are scorer controls, not actor task
success. `reachability.json` leaves **729/732** unexecuted, including all 585
held-out predicates. No execution of held-out predicates is proposed as a closure
requirement; the fraction prevents a claim of complete released coverage.

The round-47 statement that BFCL/GAIA/LCB/Tau lack any official component
execution is now stale. W-offscorer3's own “released AppWorld predicates
unexecuted” statement is superseded at **3/732** scope by w-awp. The older fifteen
components retain all raw divergences/errors, including SpreadsheetBench's
official0/local-recalculated1 workflow divergence. W-verify's independent earlier
numbers remain evidence, not additional coverage; its movable GAIA/Tau defaults
finding was already superseded by w-pin.

Snapshot reports form a separate defect sequence: w-snap2 confirms unchanged
image identity did not prevent startup mutation, and corrects identity admission
and race claims; w-snapfix refuses foreign expected/consumed identity and prevents
pre-check actor startup. The authoritative fixed packet is
`reports/w-snapfix-evidence/w-snapfix-after-20261015T022454Z-7fca9e19/summary.json`
(two passed binding checks with an actual checker read). The earlier
unsupported-infinity attempt did not run its checker and supplies no successful
control. The repair does not close checker-time custody, inherited volumes,
missing historical layer replay, S3 as a whole, or any dataset-coverage clause.

## artifact-only-state-export

Own `next_action`, verbatim from `docs/dataset-blockers.json`:

> Provision authoritative per-task export and private-input contracts for pristine scorers; validate ownership, quiescence/trial binding, scoring equivalence and live lifecycle/cleanup. Review snapshot/service state and recording surfaces under their declared class without forcing an inferred artifact allowlist.

| ID / distinct quoted clause | Round 47 → now | Evidence, reason and remaining obligation |
| --- | --- | --- |
| E1 “Provision authoritative per-task export” | PARTIAL → **SATISFIED (current empty pristine dataset set only)** | **Revised.** Recheck of all 28 literal dataset declarations and current factories/scaffolds confirms w-scope: **0/28** published and **0/23** surveyed datasets declare or select pristine; the only explicit dataset isolation declarations are AppWorld/TB snapshot-service. `eval/verification/verifier.py::_verify` requires explicit pristine opt-in. `tests/fixtures/hg_wpristine/{task-contract,task-source,trusted-pins}.json` and observed production controls supply the authored mechanism, not a 29th dataset. Round 47 incorrectly kept conditional dataset provisioning partial despite zero instances. Future opt-ins owe their own authoritative projections; no real-dataset export is certified. |
| E2 “private-input contracts for pristine scorers” | PARTIAL → **SATISFIED (same empty scope only)** | **Revised.** Same current instance check; `tests/fixtures/hg_wpristine/task-contract.json` separately binds private `expected.txt`, `closure/check.sh` reads it separately from exported `answer.txt`, and `reports/w-prifix-evidence/final-control/projection-rechecks.json` excludes unselected data. Supported mechanism plus no applicable dataset instances satisfies today's conditional clause, as recorded in `reports/w-scope-pristine-applicability.md`. Future opt-ins owe authoritative selected private/gold contracts, exclusion, scorer binding and actor-private-input safety. No general actor-safety certification follows. |
| E3 “validate ownership” | PARTIAL → **SATISFIED (same empty scope only)** | **Revised.** `eval/admission/artifact_admission.py::{export_state,_verify_artifact_runtime}`, `eval/verification/pristine.py::_platform_path`, and `reports/w-prifix-evidence/final-control/inspect-01.json` establish the control ownership/access mechanism under the documented trusted-caller custody/pins. There are still zero dataset/backend pristine instances requiring validation. The corrected verdict adopts w-scope's conditional scope; it does not claim that the DAC repair validates real dataset ownership, excludes same-UID writers, or discharges E4. Future opt-ins must validate actual source/projection/backend ownership. |
| E4 “quiescence/trial binding” | PARTIAL → **PARTIAL** | **Revise the factual binding deficiency:** native selected-task/outer-run/trial consistency is now enforced through export/runtime/verdict/cache/aggregation (`reports/w-bind-receipts.md`, current `runner.py`, `pristine.py`, `artifact_admission.py`). `reports/w-bind-evidence/after/native-outer-attempt-03/verdict-1.json` and `verdict-2.json` genuinely measure 1.0 with matching v2 identities and distinct UUID/trial ordinals; foreign task/run/trial exports and verdicts are refused. **Remaining: actual source/writer custody through use.** Both passing verdicts explicitly retain `quiescence_established=false`; the selected-file probes still miss the current same-UID directory-swap counterexample in `tests/quality/test_quiesce2_regressions.py::test_transient_directory_swap_is_explicitly_outside_file_probe_scope`. Trusted labels enforce consistency, not truthful source lineage or global uniqueness. |
| E5 “scoring equivalence” | PARTIAL → **PARTIAL** | **Revise the round-47 absence of paired pre/post-export evaluation:** `reports/w-quiesce-evidence/final-control/pre-state-attempt-01/result.json` and `post-export-attempt-01/verdict.json` compare original selected-only versus exported bytes with identical submitted41/private42/scorer/image, completed failure/exit1/score0.0 despite path/inode/permission changes. `reports/w-quiesce-evidence/audit.json` explicitly retains `dataset_equivalence_established=false`. New official comparisons reach 22 bounded components, with AppWorld released-predicate replay at 3/732 and unresolved metric/profile divergences. Remaining: applicable real-dataset state/private-input transformations and matching official metric/profile equivalence under current routes; future pristine opt-ins owe their own paired validation. Snapshot startup repair does not supply this. |
| E6 “live lifecycle/cleanup” | PARTIAL → **PARTIAL** | Existing pristine and mounted-service lifecycle observations count fully for their controls. **Revise breadth** with `reports/w-jvm-evidence/observations.json`'s six local scoring runtimes, bound native-control removal in `reports/w-bind-evidence/after/`, and fixed DS wrapper cleanup in `reports/w-scratch-evidence/host-after/observation.json`. They retain collector ownership/assisted-reaping and timeout/error limits. Remaining: applicable current backend/runtime lifecycle/cleanup validation beyond those controls, including production child-process envelopes, GAIA/Tau routes and post-change AppWorld service caps. An empty pristine dataset set does not make current-route lifecycle obligations empty. Neither lifecycle=null alone nor lack of an infallible absence proof decides this verdict. |
| E7 “Review snapshot/service state and recording surfaces under their declared class” | SATISFIED → **SATISFIED** | `reports/w-shared-topology-survey.md`, `reports/w-tbdep-transitive-inventory.md`, current GAIA/Tau/TB/AppWorld adapters and verifier review retain answer, DB/call logs, whole actor filesystem/trusted tests, and service recording/start-end DB surfaces. AppWorld/TB explicitly declare snapshot-service; GAIA/Tau execute that route without inventing declarations. W-snap2/w-snapfix sharpen integrity limits and the repaired entry boundary. Review is complete at class scope, not all-route live validation. |
| E8 “without forcing an inferred artifact allowlist” | SATISFIED → **SATISFIED** | `docs/scorer-admission-contract.md`, “Per-bundle isolation (option B)”, and current dispatcher preserve explicit pristine opt-in and native/snapshot/service routes. No dataset is relabeled or assigned a platform-inferred narrow artifact allowlist. |

**Bottom line: NOT CLOSED. E4/E5/E6 decide it.** E1/E2/E3 are the **only verdict
revisions**, PARTIAL → SATISFIED for today's empty pristine dataset instance set;
E7/E8 remain satisfied. E1–E3 do not certify any future opt-in or real-dataset
export/private-input/ownership validation.

W-quiesce2's detected write/restore remains valid evidence:
`reports/w-quiesce2-evidence/after/source-aba-attempt-01/verdict.json` records
`difference_observed`, score=null; `after/unchanged-attempt-02/verdict.json`
genuinely measures 1.0 with no_change_observed. Both honestly record quiescence
false. Their null native outer-run/trial fields are historical facts, superseded
for current native execution by w-bind rather than retrospectively rewritten.
Endpoint file probes remain sequential samples, not a source freeze. E4's
remaining requirement concerns a demonstrated custody gap, not a newly invented
atomic/infallible lease theorem. W-bind's native outer `result.json` also retains
`harness_failed`/`startup_failure` for an absent harness trace alongside its
measured predicate scores. The binding controls establish verifier consistency;
they are not cleared dataset/pilot controls under S6.

## Current-disk custody, registry and validation

Read-only digest checks confirm existing bytes; no capture/validator script that
writes receipts or executes scorers was rerun. Manifest coverage is not whole
image/layer custody.

| Existing packet | Current-disk check |
| --- | --- |
| `tests/fixtures/hg_woffscorer2/SHA256SUMS` | 105/236 present and matching here; 131 absent here. Original registered `/tmp/hg-offscorer2/tests/fixtures/hg_woffscorer2/` retains 236/236 matching; missing comparison bodies were read there without copying/repair. |
| `tests/fixtures/hg_woffscorer3/SHA256SUMS`; `tests/fixtures/hg_wawp/SHA256SUMS` | 267/267 and 583/583 matching here. |
| `tests/fixtures/hg_wuvx/SHA256SUMS`; `reports/w-snapfix-evidence/SHA256SUMS` | 324/324 and 531/531 matching here; deleted image-layer archives remain unavailable. |
| `reports/w-bind-evidence/SHA256SUMS`; `reports/w-quiesce2-evidence/SHA256SUMS`; `reports/w-quiesce-evidence/SHA256SUMS` | 249/249, 84/84 and 97/97 matching here. |
| `reports/w-jvm-evidence/SHA256SUMS`; `reports/w-scratch-evidence/SHA256SUMS` | 338/338 and 138/138 matching here; fixed DS scratch does not erase pre-fix leftovers. |
| `tests/fixtures/hg_wwheelhouse/{manifest,built-artifacts}.json` | All 130 accepted payloads, 3,110,412,863 bytes, remain available under `/tmp/hg-wwheelhouse-payloads-e5uywviu` and independently rehash correctly. These external payloads are not committed portable image/runtime closures. |

**Registry change: none.** The existing w-scope annotation already records the
only newly adopted satisfied clauses, with their exact empty-instance boundary.
Both shared objects stay code-solvable/open with full next_actions unchanged;
each retains all 23 dataset references (46 total). Dataset records, historical
records and pinned tests stay byte-for-byte unchanged. There is no closure to
remove or pinned closure assertion to update; neither blocker is deleted,
downgraded or reworded. This commit contains only this report, the appended
w-reassess2 journal entry and the validation log.

`docs/enforcement-proof-decision.md` remains governing: best-effort uncertainty
is accepted, known failure/mismatched binding still refuses. This review adds no
withdrawn filesystem-quota proof, exhaustive absence or infallibility condition.
The user's explicit S6 publication boundary remains decisive even when raw
scoring and passive cleanup observations exist.

Validation: `reports/w-reassess2-validation.txt` records the exact checker and
focused source-only registry test commands/output. The checker reports
**valid=true, 28 datasets, two shared blockers, 11 historical records,
production_authorized=false**; **56 focused tests pass**, with pytest basetemp
outside the platform tree. These checks validate registry consistency and
verbatim evidence locators, not runtime readiness or pilot authorization.
