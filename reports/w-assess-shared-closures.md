# Shared blocker closure assessment - w-assess

**Neither blocker can close.** Assessment of existing disk evidence at
`d07f066a6835ff87d14f246c19eca9333b4bdc24`, registered worktree `/tmp/hg-assess`,
branch `wg-assess`, 2026-10-15. No benchmark, scorer replay, model, GPU, endpoint,
container or evidence-collection script was run for this assessment. Only the
requested registry checker and source-only registry tests are run for validation.

Both shared objects have `status="code-solvable"` and each has 23 dataset references.
Their own actions, not the names of already-closed adjacent review gates, determine
closure. SATISFIED means the quoted clause is met at its requested scope; PARTIAL
means a mechanism or subset exists but the clause is not fully met; UNSATISFIED
means no provisioned dataset evidence for that requirement was found. A satisfied
source-review/preservation clause does not discharge a separate live-validation clause.

## Evidence read and availability

Read all nine named reports and their available fixture/receipt bodies, the admission
contract, both shared/runtime reviews, the w-fix correction and current isolation
machinery. Also read the topology survey and `docs/enforcement-proof-decision.md`.
Read-only independent clause audits were reconciled against the parent inspection;
neither audit modified a file or ran a runtime.

| Body | Existing bytes and qualification |
| --- | --- |
| `reports/w-clo-actor-closures.md` + `tests/fixtures/hg_wclo_actor/` | All 19 dataset JSONs are present and read. Each has `closure_status="partial-local-byte-closure; not production offline closure"`; e.g. `datasets/fever.json:65-66` also says `class_evidence_kind="source route; no new executed observation"`. Report `:5-9` says “zero complete provisioned offline scorer closures are certified.” |
| `reports/w-clo-runtime-closures.md` + `tests/fixtures/hg_wclo_runtime/` | This checkout has only `build_host.py`, `check_closures.py`, `native-abi-byte-pins.json`; no dataset JSONs or manifest. Existing original `/tmp/hg-clo2/tests/fixtures/hg_wclo_runtime/datasets/` has all 23 JSONs: read all, each `closure_status="partial-byte-pins"`. Thus the evidence exists on disk, but is still explicitly partial. No originals were copied, repaired or executed. Report `:3-6,39-43,97-115` states the limits. |
| `reports/w-tbdep-transitive-inventory.md` + `tests/fixtures/hg_wtbdep/` | Source/import/static-ABI inventory, not installed offline closure (`:3,15-17,119-148`; fixture `README.md:3-5,38-44`). The existing audit `tests/fixtures/hg_wimg/capture/prior-fixture-audit.json` records 810 historical manifest entries, 125 present/matching and 685 absent; `reports/w-img-abi-custody.md:86` states the same. Absent preimages are not claimed as checked bytes. |
| `reports/w-img-abi-custody.md` + `tests/fixtures/hg_wimg/` | Read `summary.json`, ABI/custody records and prior-fixture audit. Summary has 94 rows, 91 `present=true` with RepoDigests, 91 `configured_pin="movable-tag"`, three `configured_pin="digest"` (AppWorld roles). TB has 60 Python, 26 shell-only, three unavailable records. These are saved base-image observations, not current Docker observations or actor-snapshot/post-bootstrap closure. |
| `reports/w-offscorer-equivalence.md` + `tests/fixtures/hg_woffscorer/` | Local packet has 67 files; read coverage summary and available raw outputs. Missing wrapper/source/executor preimages are disclosed at `reports/w-verify-adversarial.md:65`. The existing original `/tmp/hg-offscorer/tests/fixtures/hg_woffscorer/` retains the fuller packet; no replay or repair was attempted. Bounded counts are independently re-derived in the existing w-verify packet (`reports/w-verify-adversarial.md:31-55`). |
| `reports/w-net-receipts.md`, `reports/w-alf-receipts.md`, `reports/w-chess3-receipts.md` + their `reports/*-evidence/` | Read saved diagnostic receipts, raw results and resource/binding/cleanup observations. These establish three scoped live executions with raw zeros; all three staged receipts still publish null scores, zero measured trials, one unmeasured trial. Detailed class coverage is below. |

The 19 standard `actor-workdir` datasets are alfworld, bfcl_v3, bird_minidev,
chessbench_puzzles, ds1000, fever, gsm8k, hotpotqa, jericho, livecodebench, musique,
physicsquestions, reasoning_gym, scienceworld, sportsunderstanding, spreadsheetbench,
strategyqa, triviaqa and twowikimultihopqa. The other four are appworld, gaia,
tau_bench and terminal_bench (`snapshot-service`). Chess additionally has a distinct
trusted-controller `in-process` branch. This is the surveyed/shared scope, not a
claim of 23 successful executions (`reports/w-shared-topology-survey.md:90-114,137-158`;
the old Chess unknown-observation finding is superseded by w-obs/w-fix and w-chess3).

## scorer-offline-closure

Own next_action, verbatim (`docs/dataset-blockers.json:75`):

> Provision dataset-specific pinned scorer closures and class-specific runtime evidence, including complete transitive image/ABI dependencies, official provenance/execution and trusted lifecycle/resource/cleanup observations; validate live controls before pilots, preserve snapshot/service connectivity and compare only matching known classes.

| ID / quoted distinct clause | Verdict | Existing evidence and exactly what remains |
| --- | --- | --- |
| S1 “Provision dataset-specific pinned scorer closures” | **PARTIAL** | 19 actor records and 23 original runtime records explicitly remain partial, as above. `reports/w-clo-runtime-closures.md:109-115` establishes no complete portable closure for any of the 23. Source/interpreter/package/expected-data hashes exist; offline installation payloads, complete execution-selected runtime custody and task-bound scorer inputs do not. Original `/tmp/hg-clo2/tests/fixtures/hg_wclo_runtime/datasets/tau_bench.json`, `not_pinned`, additionally states “Required committed data/datasets/tau_bench/db/airline.json and db/retail.json are absent in this checkout”; upstream tables do not replace them. No partial byte inventory may be called a provisioned closure. |
| S2 “class-specific runtime evidence” | **PARTIAL** | The actual subset in the requested w-* receipt bodies is ALFWorld noop / `actor-workdir`, one TB actor-snapshot task / `snapshot-service`, and Chess stepwise / `in-process`; raw paths/values are below. No production `pristine-offline` runtime control or AppWorld mounted-service control is supplied by these bodies. One actor-workdir noop cannot stand for the other native/QA runtimes; one TB task cannot stand for all 89 tasks or the other snapshot/service datasets. Source route labels and import probes are not live class evidence (`reports/w-clo-actor-closures.md:13-21,156-174`). |
| S3 “including complete transitive image/ABI dependencies” | **PARTIAL** | `reports/w-img-abi-custody.md:9,38-78` and saved `tests/fixtures/hg_wimg/summary.json` establish 94 refs/91 present, 91 recomputed RepoDigest roots and 101 manifest blobs; the existing independent review confirms those numbers (`reports/w-verify-adversarial.md:43-49`). GAIA/Tau and all 89 TB declarations remain movable tags; missing TB images are `mteb-leaderboard`, `pytorch-model-recovery`, `reshard-c4-data` (`present=false`, ABI/digest unavailable). AppWorld's three default digests are real pins. Complete dynamic imports/providers, native host dependencies, post-bootstrap `uvx` ABI, actor-snapshot integrity and offline resolver payloads remain incomplete (`reports/w-img-abi-custody.md:74-78`; `reports/w-clo-runtime-closures.md:81-95`). Static ELF/provider hashes and metadata dependency supersets do not fill these gaps. |
| S4 “official provenance/execution” | **PARTIAL** | Nine bounded QA components: fever, physicsquestions, sportsunderstanding, gsm8k, strategyqa, hotpotqa, triviaqa, musique, twowikimultihopqa (`reports/w-offscorer-equivalence.md:17-47`; raw `tests/fixtures/hg_woffscorer/coverage-summary.json`). Physics/Sports execute unchanged AST-selected functions; full BIG-bench import failed (`:154-170`). Complete-module results for the others are bounded to synthetic contracts/metrics. The other 14 surveyed datasets receive no execution evidence from that packet: alfworld, appworld, bfcl_v3, bird_minidev, chessbench_puzzles, ds1000, gaia, jericho, livecodebench, reasoning_gym, scienceworld, spreadsheetbench, tau_bench, terminal_bench. Existing TB separately supplies official `bash /tests/test.sh` execution for just `openssl-selfsigned-cert` (`reports/w-net-receipts.md:52-106`); ALF supplies only its noop/local empty-episode convention (`reports/w-alf-receipts.md:133-143`). Chess supplies controller scoring, not an upstream offline scorer comparison. Full dataset/metric provenance and execution remain unestablished outside these bounded results; manifest hashing is not official execution. |
| S5 “trusted lifecycle/resource/cleanup observations” | **PARTIAL** | Real, manifest-bound TB configuration/snapshot/owned-object absence observations and native ALF/Chess observations exist (coverage table below). They are credited at their actual scope. ALF samples launcher PIDs, not later scorer-engine resource usage; Chess establishes relay cleanup, not all native runtime resources. No pristine live observations or AppWorld/GAIA/Tau class-specific lifecycle controls occur in the named bodies; other actor/QA/JVM/LibreOffice/child-process and TB task runtimes are not covered. The three retained `lifecycle=null`/`status="unknown"` formal fields must not be relabeled, but are **not alone** the reason this clause remains partial. |
| S6 “validate live controls before pilots” | **PARTIAL** | Three real raw controls occurred, including the completed w-chess3 terminal exchange. Each saved staged diagnostic receipt has `score=null`, `measured_trials=0`, `unmeasured_trials=1`, `invalid_trials=0`, `policy_enforcement_observed=false`, `production_authorized=false`. Their raw results cannot be upgraded into cleared comparable pilot controls. The nine offline synthetic scorer controls explicitly retain `production_runtime_observation:false` (`reports/w-offscorer-equivalence.md:51-69,170`). Matching valid live controls after dataset gates, across the required runtime/metric scope, remain absent. |
| S7 “preserve snapshot/service connectivity” | **SATISFIED — preservation mechanism** | The contract explicitly preserves dependency/service networking and recording mounts (`docs/scorer-admission-contract.md:44-58`). Current `eval/verification/verifier.py:290-299` creates from the snapshot, retains its internal network and attaches declared bridge before start; `:575-590` retains service recordings and the running service network. `reports/w-net-receipts.md:106,193-243` corroborates successful dependency bootstrap and both networks for the one real TB task. No pristine/network-none rule is imposed on these routes. Live coverage limitations stay in S2/S5/S6; this preservation clause itself is met. |
| S8 “compare only matching known classes” | **SATISFIED — comparison mechanism** | `data/scaffolds/scorer_isolation.py:7` defines the four known classes plus `unknown`. `eval/verification/isolation.py:15-37` normalizes unsupported/missing observations to unknown, refuses mixed classes, and raises “scorer isolation class unknown: comparison invalid” for unknown comparison. `web/src/logic/compare.ts:117-129,146-158` also suppresses deltas for unknown/mixed point/task classes. `docs/w-fix-unknown-isolation-records.md:10-29,53-60` supersedes w-obs's unknown-only **recording** refusal: homogeneous unknown evidence persists with `scorer_isolation_comparable=false`; it still cannot be compared. Known-class compatibility is only the topology prerequisite, not proof of matching metrics/splits/models. |

**Bottom line: OPEN. Exact remaining clause set: S1, S2, S3, S4, S5, S6.**
S7 and S8 are satisfied; they are not remaining work. Neither shared object nor any
of its 23 references is removed or reworded.

## Actual live subset and its limits

These existing observations support S2/S5/S6 and E4/E6 below. No captured command
was executed during this assessment.

| Class / run and exact artifact paths | Existing raw values | Limits of coverage |
| --- | --- | --- |
| `actor-workdir`: `w-alf-noop-20261014T202206Z-13b61fc3`; `reports/w-alf-evidence/runtime-attempt/run-one-result.json`, `reports/w-alf-evidence/artifact-bindings.json`, `reports/w-alf-evidence/resource-observations.json`, `reports/w-alf-evidence/cleanup-observations.json` | Selected task `pick_heat_then_place_in_recep-Tomato-None-GarbageCan-10__trial_T20190908_225046_020282`; raw `score=0.0`, scorer `measured=true`, `actions_replayed=0`, `oracle_actions_present=false`. Materialized input hashes have `equal=true`. Executed deadlines 3600/300 s and action budget 30; sampled bwrap PIDs 219098/219109 have unlimited CPU/RSS/address-space rlimits. Three observed temp directories have `exists_after=false`, both sampled PIDs `exists=false`. | One noop/reset/local empty-log convention; no successful action replay. Launcher samples do not establish scorer-engine limits; private tmpfs/engine scratch not inventoried (`reports/w-alf-receipts.md:117-222`). Does not cover the other 18 standard actor-workdir datasets or their runtime branches. |
| `snapshot-service`, actor snapshot: `w-net-terminal-bench-20261014T200818Z-fd0c4d1e`; `reports/w-net-evidence/execution/diagnostic_execution.json`, `reports/w-net-evidence/ctrf.json`, `reports/w-net-evidence/launch/resource-observation-receipt.json`, `reports/w-net-evidence/launch/snapshot-observation-receipt.json`, `reports/w-net-evidence/launch/cleanup-observation-receipt.json` | Task `openssl-selfsigned-cert`; raw reward `0.0`, CTRF `tests=6, passed=5, failed=1`. Both roles: `NanoCpus=1000000000`, `Memory=2147483648`, `PidsLimit=1024`, bridge plus owned internal network. Binding has `trial_id="openssl-selfsigned-cert:1"`, `manifest_sha256="27e0890e47bd3e1385e96590fe7d38f760bca5461e560230cb8dcecaf3ed5366"`. Snapshot ID `sha256:59c94f3462a248e5af5909b2249cba07e2e46574eee4fd362896d7c048eac779`; exact saved post-run probes report both containers/snapshot absent, scoped listings empty. | Genuine raw official task failure and bounded cleanup observations. Limits are Docker configuration observations, not peak usage or infallibility proof. No AppWorld mounted-service, GAIA/Tau or other 88 TB task controls supplied here (`reports/w-net-receipts.md:193-243,314-425`). |
| `in-process`, trusted platform controller: `w-chess3-stepwise-20261014T222208Z-728e7478`; `reports/w-chess3-evidence/execution/task-result.json`, `reports/w-chess3-evidence/execution/cleanup-observation.json` | Task `chessbench_puzzles/test/1287`; actor `exit_code=0`, raw controller `score=0.0`, outer `evidence.measured=true`; inner transport `status="terminal"`, `submissions=1`, terminal `failed/wrong_move`. Relay `server_closed=true`, `thread_joined=true`, `socket_removed=true`; observed task/socket paths `exists=false`. One connection, 256 maximum submissions, 4096 message bytes, 300 s actor deadline. | Actual completed losing puzzle, superseding the **older** zero-submission/incomplete Chess observation cited by w-clo-runtime. Inner transport `measured=false` means delivery does not score; it does not negate the outer controller measurement. No offline strict-replay comparison or native CPU/RAM attestation (`reports/w-chess3-receipts.md:148-219,347-434`). |
| `pristine-offline`; AppWorld mounted-service subtype | No production live control for these in the named evidence. | Generic pristine controls use a Docker double (`docs/w-shared-verifier-review.md:165-181`). Image inspection/import containers are ABI inspection, not production scorer lifecycle evidence (`reports/w-img-abi-custody.md:78-88`). |

For **each** of the first three rows, the corresponding
`reports/w-net-evidence/execution/diagnostic_receipt.json`,
`reports/w-alf-evidence/execution/diagnostic_receipt.json` and
`reports/w-chess3-evidence/execution/diagnostic_receipt.json` records
`selected_tasks=1`, `expected_trials=1`, `measured_trials=0`, `unmeasured_trials=1`,
`invalid_trials=0`, `score=null`, `enforcement.comparable=false`,
`enforcement.non_comparable_reason="policy_enforcement_not_observed"`,
`cleanup.status="unknown"`, `snapshot.status="unknown"`, `lifecycle=null`.
Eligible tasks are respectively 1, 81 and 6615. Raw scorer/controller measurements
and staged publication are different facts; neither may overwrite the other.

The table is the requested w-* receipt subset, not a claim that no older local
controls exist. The pinned registry tests also point to `reports/runtime-blockers-b7.md`
and `reports/jericho-runtime-b7.json`: selected `acorncourt`, two standalone native
controls, noop `score=0/max_score=30`, oracle `score=30/max_score=30`, both
`measured=true`, two task directories `absent=true`; the production admission still
has `status="blocked"`, `reason="backend_observation_unavailable"`. Its selected
metadata/dependency/provenance scope is explicit. `reports/scienceworld-runtime-b7.json`
records `benchmark_episodes=0` and native mount probes, not a JVM scoring episode.
These existing bounded observations add no pristine production export control or
complete scorer closure, and do not change S1-S6/E1-E6. No b7 command was rerun.

`docs/enforcement-proof-decision.md` accepts best-effort snapshot/cleanup with
uncertainty retained. This assessment does not restore withdrawn requirements for
atomic lease proof, exhaustive namespace absence, peak bounds or infallible enforcement.
The gaps above are absent dataset/class/runtime coverage and unvalidated contracts,
not a demand that every unknown formal lifecycle field become a proof certificate.

## artifact-only-state-export

Own next_action, verbatim (`docs/dataset-blockers.json:109`):

> Provision authoritative per-task export and private-input contracts for pristine scorers; validate ownership, quiescence/trial binding, scoring equivalence and live lifecycle/cleanup. Review snapshot/service state and recording surfaces under their declared class without forcing an inferred artifact allowlist.

| ID / quoted distinct clause | Verdict | Existing evidence and exactly what remains |
| --- | --- | --- |
| E1 “Provision authoritative per-task export” | **UNSATISFIED — dataset provisioning** | No authoritative dataset/task pristine export contract was found in the named bodies. Generic independently pinned bundle/task schema, bounded export and exact mount checks exist (`docs/scorer-admission-contract.md:17-30,60-83`); they consume a contract supplied by a trusted caller, not supply authoritative per-task dataset contracts. None of the 23 standard surveyed adapters opts into pristine (`reports/w-shared-topology-survey.md:69-81`). This is not a reason to discard the shared gate as vacuous or force snapshot/service routes into pristine export. Remaining: authoritative task-defined projections for applicable pristine scorers. |
| E2 “private-input contracts for pristine scorers” | **UNSATISFIED — dataset provisioning** | Source-data and projection hashes exist, but are explicitly not execution-bound generated `gold.json`, `gold.sql`, stripped PDDL, `task.json` or `context.json` contracts (`reports/w-clo-actor-closures.md:143-147`; `reports/w-clo-runtime-closures.md:39-43`). `docs/w-shared-verifier-review.md:174-181` expressly leaves selected/private input safety unverified. ALF's one captured stripped game and Chess's trusted private controller record do not provision authoritative private-input contracts across applicable pristine tasks. Remaining: selected-task private inputs, authority, exclusion and scorer binding. |
| E3 “validate ownership” | **PARTIAL** | Independent pins, actor-external closure paths, exclusive platform projections and safe-file checks are implemented (`docs/w-shared-verifier-review.md:124-153`). `eval/admission/artifact_admission.py:264-267` explicitly says destination/parent ownership and source quiescence must be supplied by the caller. `docs/scorer-admission-contract.md:32-37` says the facade cannot establish ownership. No dataset-specific pristine export/backend ownership validation is provided by byte inventories or the three differently scoped controls. |
| E4 “quiescence/trial binding” | **PARTIAL** | Export receipt binds task/run/contract/source and is rechecked (`eval/admission/artifact_admission.py:306-311,323-336`). The one TB observation has the exact run/trial/manifest binding above; ALF materialized inputs have `equal=true` (`reports/w-alf-evidence/artifact-bindings.json`). These are useful existing bindings, not evidence of pristine export quiescence through scoring or all selected-task/trial custody. The helper says “Metadata checks detect observable source changes; they cannot establish quiescence.” (`eval/admission/artifact_admission.py:267`). Remaining: trusted source quiescence through export/use and execution-bound trial inputs for applicable tasks. |
| E5 “scoring equivalence” | **PARTIAL** | Nine synthetic official/local comparisons exist, independently checked by `reports/w-verify-adversarial.md:33-42`. Raw `tests/fixtures/hg_woffscorer/coverage-summary.json` records FEVER 16/17 strict plus three API errors; Physics 8/12; Sports 7/12 paired channels; GSM8K 6/16; StrategyQA 5/12 raw with separate Boolean projection 4/4; Hotpot 12/13; Trivia 10/10 numeric plus one error; MuSiQue 12/12 common metrics with four reward-policy differences; 2Wiki 13/13 across 16 columns. These are valuable bounded comparisons, not production pre/post-export state equivalence. Divergences, errors, different response channels and rounding qualifications remain; other datasets and applicable export transformations lack equivalence validation (`reports/w-offscorer-equivalence.md:150-170,244-305,338-344,455,490-508`). |
| E6 “live lifecycle/cleanup” | **PARTIAL** | The three actual controls and their exact cleanup observations are credited above. They do not execute a production pristine export lifecycle; the AppWorld recording/mounted-service path and remaining dataset/runtime branches lack such live validation in these bodies. Generic runtime identity/refusal/cleanup tests are synthetic; ownership/quiescence/private-input/equivalence remain backend obligations (`docs/w-shared-verifier-review.md:165-181`; `docs/scorer-admission-contract.md:95-106`). Retained unknown formal lifecycle fields are not silently upgraded, and uncertainty alone is not treated as a new gate. |
| E7 “Review snapshot/service state and recording surfaces under their declared class” | **SATISFIED — source review** | The four surfaces are reviewed explicitly in `reports/w-tbdep-transitive-inventory.md:25-28`: GAIA actor-snapshot `answer.txt`; Tau actor-snapshot `db.json`/`tau_calls.jsonl`; TB full filesystem/executable/service snapshot plus trusted post-stop `/tests`; AppWorld separate verifier, service-recorded API log, per-task evaluator and start/end DBs. `reports/w-shared-topology-survey.md:54-81,154-158` distinguishes snapshot vs mounted-service state. AppWorld/TB explicitly declare `snapshot-service`; GAIA/Tau have unknown declarations and source-selected snapshot-service execution, not fabricated explicit declarations (`eval/verification/verifier.py:239-252`). Current AppWorld `data/datasets/appworld.py:270,278-299` preserves the recording log, separate verifier and mounted service. Identifying custody/lifecycle gaps completes this **review** clause without falsely claiming they are validated. |
| E8 “without forcing an inferred artifact allowlist” | **SATISFIED — class-specific treatment** | `docs/scorer-admission-contract.md:44-58,73-83` confines bounded data-only projection to explicit pristine opt-in and keeps snapshot/service backends. Current `eval/verification/verifier.py:244-252,575-590` preserves those routes/recordings; `reports/w-shared-topology-survey.md:154-158` explicitly rejects blanket pristine export for them. No inferred allowlist has been introduced by this assessment. Per-task state contracts/ownership/trial/equivalence obligations above remain, within each actual class. |

**Bottom line: OPEN. Exact remaining clause set: E1, E2, E3, E4, E5, E6.**
E7 and E8 are satisfied; the final source-review sentence is not remaining work.

## Registry decision, false claims avoided and validation

Registry change: **none**. Both objects, original next_actions/statuses and all 46
dataset references remain byte-for-byte unchanged. Partial clauses cannot be deleted
from an action to manufacture closure. The pinned remaining blocker assertions in
`tests/quality/test_dataset_blockers.py` therefore need no change. Production code,
adapters, frozen receipts and historical runs are untouched. There is no merge to main.

It would be false to call any of the 19/23 byte inventories a complete provisioned
closure; to generalize nine official QA components to all datasets or selected-function
execution to a successful full BIG-bench import; to call three raw zeros measured
staged publications; to transfer one TB task's custody/lifecycle evidence to AppWorld
or every runtime class; or to describe w-chess3 as still having no terminal exchange.
It would also be false to say that comparison safety or the snapshot/service source
review is still missing: S7/S8/E7/E8 are satisfied at the scopes specified above.

Exact commands, checker output and focused test output are recorded in
`reports/w-assess-validation.txt`: checker `valid=true`, 28 datasets, two shared
blockers, 11 historical records, `production_authorized=false`; **54 tests passed**.
Those validate the unchanged registry and evidence
locators; they produce no new benchmark/runtime evidence and authorize no pilot.
