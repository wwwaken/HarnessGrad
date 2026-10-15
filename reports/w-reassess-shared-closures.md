# Shared blocker reassessment - w-reassess

**Neither shared blocker closes. Three verdicts change: S2 PARTIAL → SATISFIED;
E1 and E2 UNSATISFIED → PARTIAL.** The remaining work is S1/S3/S4/S5/S6 and
E1/E2/E3/E4/E5/E6, respectively. S7/S8/E7/E8 remain satisfied.

Assessment baseline: `56adfafb72461bb88c4c1668e45b1c6c8ae54fba`, registered
`/tmp/hg-reassess`, branch `wg-reassess`, 2026-10-15. Read
`reports/w-assess-shared-closures.md` in full first; its S1-S8/E1-E8 identifiers
are retained below. Verdicts apply to each clause's own scope: SATISFIED means
that clause is met, PARTIAL means only a subset/mechanism is established, and
UNSATISFIED means no provisioned instance was found. Class exercise, dataset
coverage, scorer measurement and staged publication are separate facts.

This assessment reads existing evidence and source only. No benchmark, scorer
replay, model, GPU, endpoint or container execution occurred. Independent
read-only clause audits were reconciled with parent receipt/source inspection.
The only execution for validation is the registry checker and its source-only
tests; no captured runtime command or fixture collection script was rerun.

## Evidence availability and changes since w-assess

All user-named reports were inspected, together with their relevant existing
receipt bodies and current isolation/admission/verifier code. Evidence on disk
is credited even where an integration omitted raw files from this checkout:

| Evidence | Existing bytes and actual scope |
| --- | --- |
| `reports/w-pristine-receipts.md`; `tests/fixtures/hg_wpristine/` | Original real production-dispatch pristine attempt, authored task `w-pristine-addition-control`. `evidence/measurement-audit.json` preserves **measured=0, invalid=1, unmeasured=0, score=null** after the unreadable-export failure. The original driver's erroneous measured count is not used. All 55 manifest-listed fixture files are present and hash-match. |
| `reports/w-prifix-receipts.md`; `reports/w-prifix-evidence/final-control/` | Same sealed fixture, fresh final run `w-prifix-final-20261014T231720Z-483ac92d`: `control-receipt.json` has **measured=1, invalid=0, unmeasured=0, score=0.0**. `docker-02.json` contains `expected=42`, `actual=41`, `completed_check=fail`; `verdict.json` retains native stopped State and removal. `final-audit.json` corroborates the final run, kernel samples, projection rechecks and independently attributable refusal follow-ups. This is a genuine predicate failure through the production backend, on a locally authored control; it adds no standard dataset closure. |
| `reports/w-appworld-receipts.md`; `reports/w-appworld-evidence/` | One train task `cf6abd2_2`, distinct pinned actor/service/verifier, real recording replay and `world.evaluate()`. `result-summary.json` and raw `execution/diagnostic_execution.json` record TGC **raw measured=1, invalid=0, unmeasured=0, score=0.0**, eight tests and no task success. Staged publication remains unmeasured. `role-observations.json`, `cgroup-live-observations.json` and `cleanup-observations.json` preserve topology, old resource configuration and bounded absence observations. |
| `reports/w-caps-resource-custody.md` | AppWorld service now declares 2 CPUs / 4096 MiB / 1024 PIDs through validated source plumbing and mocked command construction. **No post-change live observation.** The historical service remains recorded with NanoCpus=0, Memory=0, PidsLimit=null; its old cgroup samples are not relabeled as the new caps. |
| `reports/w-pin-image-digests.md` | GAIA/Tau defaults now use rehashed locally resolving OCI digests. Current `data/datasets/gaia.py` and `data/datasets/tau_bench.py` confirm this; overrides remain possible. Terminal-Bench still has 89 movable declarations, 86 present images and three absent images. This supersedes the old GAIA/Tau tag finding, not the rest of image/ABI closure. |
| `reports/w-offscorer2-coverage.md`; `tests/fixtures/hg_woffscorer2/coverage-summary.json` | Six new bounded components plus the prior nine = **15** official/local execution components. Of the root manifest's 236 entries, **105 are present and match here; 131 are absent here**. The registered original `/tmp/hg-offscorer2/tests/fixtures/hg_woffscorer2/` retains **236/236 matching files** against the same manifest. In particular, original `bird_ds/comparison.json` and `spreadsheetbench/comparison.json` were read there. No omitted file was repaired/copied or replayed. |
| `reports/w-verify-adversarial.md` | Independent re-derivation corroborates the prior nine scorer comparisons, 94 configured refs / 91 present images / 101 manifest blobs, and Terminal-Bench's raw 0.0, 6/5/1 tests and zero measured staged trials. Its GAIA/Tau movable-default observation predates and is superseded by w-pin. Re-derivation does not supply new production custody or broaden input coverage. |
| `reports/w-chess3-receipts.md`, `reports/w-net-receipts.md`, `reports/w-alf-receipts.md` | Existing controller, actor-snapshot and native-workdir controls remain real and bounded. Chess delivered a terminal wrong move, not the earlier incomplete exchange. Their raw zeros are distinct from their unchanged unmeasured staged receipts. Exact bodies are listed below. |

The baseline inventories remain partial: 19 standard `actor-workdir` datasets and
23 command/container datasets overall (`reports/w-clo-actor-closures.md`,
`reports/w-clo-runtime-closures.md`). Original runtime dataset records remain at
`/tmp/hg-clo2/tests/fixtures/hg_wclo_runtime/datasets/`; source/byte inventories
are not provisioned portable scorer installations. The newer authored pristine
control is additional to those 23, not a dataset converted to pristine.

## scorer-offline-closure

Own `next_action`, verbatim from `docs/dataset-blockers.json`:

> Provision dataset-specific pinned scorer closures and class-specific runtime evidence, including complete transitive image/ABI dependencies, official provenance/execution and trusted lifecycle/resource/cleanup observations; validate live controls before pilots, preserve snapshot/service connectivity and compare only matching known classes.

| ID / distinct quoted clause | Previous → current verdict | Evidence, revision and remaining work |
| --- | --- | --- |
| S1 “Provision dataset-specific pinned scorer closures” | PARTIAL → **PARTIAL** | Unchanged verdict. The 19/23 inventories still explicitly disclaim complete portable closure. The sealed three-file addition control in `tests/fixtures/hg_wpristine/task-contract.json` and the successful w-prifix execution provision that authored control only. The six new official execution components do not provision their transitive offline installations or selected-task inputs. Remaining: actual dataset-specific available, pinned scorer/runtime/input closures; Tau's required committed `db/airline.json` and `db/retail.json` gaps in the original runtime inventory are not repaired by image defaults. |
| S2 “class-specific runtime evidence” | PARTIAL → **SATISFIED** | **Revised.** The prior assessment lacked real pristine and AppWorld mounted-service observations. `reports/w-prifix-evidence/final-control/verdict.json` now supplies real completed production `pristine-offline` execution, and `reports/w-appworld-evidence/role-observations.json` supplies mounted-service execution. Together with ALF `actor-workdir`, TB actor-snapshot `snapshot-service` and Chess `in-process`, every known class is exercised, including both surveyed snapshot/service shapes. This clause says class-specific evidence; it does not say every dataset in a class has run. Dataset/task breadth, provisioning and valid pilot controls remain incomplete under S1/S4/S5/S6. |
| S3 “including complete transitive image/ABI dependencies” | PARTIAL → **PARTIAL** | Unchanged verdict; **revise the previous factual GAIA/Tau movable-default claim** using `reports/w-pin-image-digests.md`, “Recomputed references and local resolution”. Their defaults are digest-pinned; AppWorld's three roles already were. TB's **89 tags** and absent `mteb-leaderboard`, `pytorch-model-recovery`, `reshard-c4-data` remain. `reports/w-img-abi-custody.md` and w-pin still leave dynamic imports/providers, native host dependencies, post-bootstrap `uvx` ABI, actor-snapshot custody and offline resolver payloads incomplete. Base-image inspection and a control's kernel samples do not close those transitive gaps. |
| S4 “official provenance/execution” | PARTIAL → **PARTIAL** | Unchanged verdict; **revise nine covered components to fifteen**, with the exact covered/uncovered lists below. New source/installed-package identities, preserved official/local execution and comparisons are in `tests/fixtures/hg_woffscorer2/coverage-summary.json` and the original raw bodies identified above. BIRD full import fails; BIG-bench uses unchanged selected functions; family/task breadth and installed-world acquisition/source provenance remain bounded. AppWorld's one live official TGC evaluation and TB's one official script execution also count at their actual scope. Remaining: official provenance and execution for uncovered components and uncovered dataset/metric/runtime breadth. Fifteen component packets cannot certify the other datasets. |
| S5 “trusted lifecycle/resource/cleanup observations” | PARTIAL → **PARTIAL** | Unchanged verdict; **withdraw the prior absence of pristine/AppWorld observations**. W-prifix supplies actual Docker configuration, kernel CPU/memory/PID/tmpfs samples, native stopped result/removal and post-return absence (`final-control/{docker-02,verdict,post-removal-inspect,post-return-projection}.json`). AppWorld supplies three-role/network/path/PID observations and historical cgroup samples. W-caps repairs service declarations **without a live capped-service rerun**. ALF samples launcher resources, Chess relay bounds/cleanup; neither establishes all native scorer-resource branches. Remaining: dataset/runtime-scoped resource and lifecycle observations beyond these controls, including the corrected AppWorld service envelope and GAIA/Tau routes. No peak/infallibility or exhaustive namespace proof is demanded. |
| S6 “validate live controls before pilots” | PARTIAL → **PARTIAL** | Unchanged verdict; **revise the old statement that pristine has no valid measured predicate control**. `reports/w-prifix-evidence/final-control/control-receipt.json` genuinely records 1/0/0 measured/invalid/unmeasured, score 0.0. It is `benchmark=false`, `staged_pilot=false`, `production_authorized=false`; it is not a dataset diagnostic after dataset gates. ALF/TB/Chess/AppWorld each retain staged measured=0/unmeasured=1/invalid=0 and null score. Remaining: valid matching dataset controls after their applicable gates before pilots; neither raw zeros nor synthetic official comparisons authorize expansion. |
| S7 “preserve snapshot/service connectivity” | SATISFIED → **SATISFIED** | Unchanged verdict. `eval/verification/verifier.py::_verify_container_state_inner` retains the owned network and adds declared bridge before start; `_verify_inner` retains running service networking and `services_mod.mounts_for` recording mounts. `reports/w-net-evidence/launch/resource-observation-receipt.json` corroborates TB's two attachments; `reports/w-appworld-evidence/role-observations.json` and `network-observations.jsonl` now corroborate the separate verifier sharing the live internal service network and RO recording bind. Pristine network-none is not imposed on these routes. |
| S8 “compare only matching known classes” | SATISFIED → **SATISFIED** | Unchanged verdict after rereading `data/scaffolds/scorer_isolation.py`, `eval/verification/isolation.py::{observed_class,common_class,require_comparable,record_class}` and `web/src/logic/compare.ts::{compareRuns,isolationProblem}`. Unsupported/missing observations normalize to unknown; mixed classes refuse; unknown comparison refuses; the UI suppresses deltas. Homogeneous unknown recording survives with comparability false per `docs/w-fix-unknown-isolation-records.md`. Known class is only the topology prerequisite: matching metric/split/model/policy is still needed. D2's preservation of an underlying unmeasured reason does not weaken this boundary. |

**Bottom line: NOT CLOSED. Deciding clauses: S1, S3, S4, S5, S6 (all PARTIAL).**
S2 is now satisfied at class-exercise scope; S7/S8 remain satisfied.

### Class exercise and the publication boundary

| Executed class / existing task | Exact receipt bodies | What is established and what is not |
| --- | --- | --- |
| `pristine-offline`, authored addition | `reports/w-prifix-evidence/final-control/{control-receipt,verdict,docker-02,projection-rechecks}.json`; `reports/w-prifix-evidence/final-audit.json` | Genuine measured 0.0, 1 selected task/trial, 41 vs 42, both projections rechecked, user 65534:1026, two RO binds/network none, CPU 1 / memory 512 MiB / PID 128 kernel samples, bounded tmpfs and observed removal/projection absence. No standard dataset or model; lifecycle=null and no snapshot used. Original w-pristine remains invalid and preserved. |
| `actor-workdir`, ALF noop | `reports/w-alf-evidence/runtime-attempt/run-one-result.json`, `artifact-bindings.json`, `resource-observations.json`, `cleanup-observations.json` | Real native reset/local empty-episode zero, zero replayed actions, input hashes equal, bounded path/PID cleanup. Launcher resource samples do not attest later scorer-engine resource use or other native/QA/JVM/LibreOffice branches. |
| `snapshot-service`, TB actor snapshot | `reports/w-net-evidence/execution/diagnostic_execution.json`, `reports/w-net-evidence/ctrf.json`, `reports/w-net-evidence/launch/{resource,snapshot,cleanup}-observation-receipt.json` | `openssl-selfsigned-cert` official raw 0.0; six tests, five pass/one fails; distinct snapshot verifier, owned internal + bridge network, CPU/memory/PID configuration and scoped owned-object absence. One task does not cover the other 88 or GAIA/Tau. |
| `snapshot-service`, AppWorld mounted service | `reports/w-appworld-evidence/execution/diagnostic_execution.json`, `role-observations.json`, `cgroup-live-observations.json`, `cleanup-observations.json`, `cleanup-processes-and-relay.json` | `cf6abd2_2` official TGC measured failure, live service + fresh verifier/RO recording, bounded three-role/network/PID/path absence. Actor/verifier caps were 2 CPUs/4 GiB/1024; service was uncapped in that run. W-caps source changes are not historical runtime observations. One train task is not coverage of 732 evaluators or an authentic task success. |
| `in-process`, Chess trusted controller | `reports/w-chess3-evidence/execution/{task-result,cleanup-observation}.json` | Task `chessbench_puzzles/test/1287`: actor exit0, one submission, delivered `failed/wrong_move`, outer controller measured=true/raw0.0; relay closed/joined/socket removed, observed paths absent. Inner transport measured=false describes delivery, not controller scoring. No strict-replay equivalence, model accuracy or native CPU/RAM attestation. |

For **each** ALF/TB/Chess/AppWorld staged
`reports/w-{alf,net,chess3,appworld}-evidence/execution/diagnostic_receipt.json`,
`coverage` retains selected_tasks=1, expected_trials=1, measured_trials=0,
unmeasured_trials=1, invalid_trials=0; score=null. Eligible counts are respectively
81/1/6615/147. `enforcement` retains policy_enforcement_observed=false,
comparable=false, non_comparable_reason=`policy_enforcement_not_observed`,
production_authorized=false. Cleanup/snapshot stay unknown and lifecycle=null.
These stored fields are not retroactively upgraded by passive observations.

### Exact official-execution coverage

The **15 components in the two official/local comparison packets** are:
`fever`, `physicsquestions`, `sportsunderstanding`, `gsm8k`, `strategyqa`,
`hotpotqa`, `triviaqa`, `musique`, `twowikimultihopqa`, **`reasoning_gym`,
`bird_minidev`, `ds1000`, `spreadsheetbench`, `jericho`, `scienceworld`**.
Bold entries are the six additions to w-assess's nine.

The **eight outside those packets** are: `alfworld`, `appworld`, `bfcl_v3`,
`chessbench_puzzles`, `gaia`, `livecodebench`, `tau_bench`, `terminal_bench`.
This is not a claim that all eight have no executed scorer: AppWorld now has the
one official TGC evaluation above; TB already has its one official `/tests/test.sh`;
ALF has the local empty-log convention; Chess has the trusted controller. None
supplies broad official/local comparison or dataset closure. In the reviewed
packets/controls, BFCL, GAIA, LiveCodeBench and Tau still lack official-execution
evidence. Each existing evidence type keeps its own provenance and metric scope.

Even the fifteen are not full dataset coverage. W-offscorer2 adds Reasoning Gym
24 numeric agreements on three families (plus three paired KeyErrors), BIRD
9 agreements/2 divergences/1 local-unmeasured classification, DS-1000 9 agreements
with explicit local UNIX IPC, SpreadsheetBench 15 direct and 16 strict-caller
numeric agreements **plus a separate official0/local1 formula-workflow divergence**,
Jericho 5 agreements including one labeled study-reference positive, and
ScienceWorld 4 zero-trace agreements only. BIRD's missing psycopg2 import, strict
socket/LibreOffice and initial Java failures stay preserved. Installed world bytes
do not authenticate an upstream Git revision. Prior divergences/errors remain as
independently re-derived in `reports/w-verify-adversarial.md`; no agreement rate is
pooled across unlike metrics, channels or profiles.

## artifact-only-state-export

Own `next_action`, verbatim from `docs/dataset-blockers.json`:

> Provision authoritative per-task export and private-input contracts for pristine scorers; validate ownership, quiescence/trial binding, scoring equivalence and live lifecycle/cleanup. Review snapshot/service state and recording surfaces under their declared class without forcing an inferred artifact allowlist.

| ID / distinct quoted clause | Previous → current verdict | Evidence, revision and remaining work |
| --- | --- | --- |
| E1 “Provision authoritative per-task export” | UNSATISFIED → **PARTIAL** | **Revised.** `tests/fixtures/hg_wpristine/{task-source,task-contract,trusted-pins}.json` now provisions an authoritative **authored-control** contract for `w-pristine-addition-control`: sole data file `answer.txt`, max_bytes16/max_inodes2, selected source/bundle/image pins. W-prifix actually exports and scores it (`final-control/verdict.json`, `projection-rechecks.json`). The prior claim of no provisioned per-task instance is stale. Remaining: authoritative applicable dataset/task export projections; none of the 23 surveyed standard adapters opts into pristine (current source search and `reports/w-shared-topology-survey.md`). A synthetic task contract does not provision dataset contracts or make this gate vacuous. |
| E2 “private-input contracts for pristine scorers” | UNSATISFIED → **PARTIAL** | **Revised.** The same task contract explicitly seals `expected.txt` as a scorer dependency, separately from exported `answer.txt`; `closure/check.sh` reads private42 and submitted41 through the two distinct roots. `trusted-pins.json`, original `evidence/launch.json` and final projection inventories bind the control's selected/private files and exclude `unselected.txt` from export. This is an actual control-only instance, not merely schema support. Remaining: authoritative selected-task private-input/gold generation, exclusion and scorer binding for applicable datasets; no actual actor was launched in this control, so actor-private-input safety is not certified generally. |
| E3 “validate ownership” | PARTIAL → **PARTIAL** | Unchanged verdict. W-prifix D1 fixes DAC readability with export UID1026/mode0640, distinct scorer UID65534/platform group, read-only mounts and access validation (`eval/admission/artifact_admission.py::{export_state,_verify_artifact_runtime}`, `final-control/{inspect-01,projection-rechecks}.json`). That is real observed custody/access for this control. It does not establish dataset/backend ownership boundaries against actor/external writers; preparation uses the platform UID and no actor is launched. `docs/scorer-admission-contract.md`, “Checks and trust inputs”, still assigns ownership/custody to trusted callers. Remaining: actual applicable backend/source/projection ownership validation. A permission defect repair alone is not that validation. |
| E4 “quiescence/trial binding” | PARTIAL → **PARTIAL** | Unchanged verdict; stronger binding evidence now exists. `final-control/verdict.json` binds the export to task/source/contract and runtime/export ID `hg-pristine-7a190109f07e43859e3ac605e25a95e4`; `final-control/launch.json` and `final-audit.json` bind the fresh outer run. `projection-rechecks.json` records both post-inspection integrity rechecks. W-pristine explicitly disclaims exclusion of a same-UID writer; no active actor shutdown/freeze or source quiescence through use is established. Remaining: execution-bound dataset/trial inputs and trusted quiescence at the actual export boundary. `export_state` still says metadata checks cannot establish quiescence. D1/D3 do not discharge it. |
| E5 “scoring equivalence” | PARTIAL → **PARTIAL** | Unchanged verdict; update nine bounded official/local components to fifteen, with all divergences/errors above retained. `tests/fixtures/hg_woffscorer2/coverage-summary.json` and original comparison bodies establish those bounded comparisons, not production pre/post-export equivalence. Final `completed_check=fail` proves the authored predicate completed on the exported bytes; it supplies no paired original-state/exported-state dataset evaluation. Remaining: equivalence of applicable dataset state/private-input transformations and the chosen official metric/profile, with unsupported channels/workflows resolved or explicitly constrained. D2 repairs measurement classification, not equivalence. |
| E6 “live lifecycle/cleanup” | PARTIAL → **PARTIAL** | Unchanged verdict; **withdraw the prior absence of a live production pristine export and AppWorld mounted-service lifecycle**. `final-control/{verdict,post-removal-inspect,post-return-projection}.json` shows native stopped-result/removal and object/projection absence after a genuine measured check; AppWorld's `cleanup-observations.json` and `cleanup-processes-and-relay.json` show bounded role/network/PID/path absence. These count fully for their controls. Remaining: live lifecycle/cleanup validation bound to actual applicable dataset export/input contracts and uncovered backend/runtime surfaces; the authored task alone cannot establish those. Formal lifecycle=null is preserved, not used alone to deny satisfaction or to demand an infallible cleanup certificate. |
| E7 “Review snapshot/service state and recording surfaces under their declared class” | SATISFIED → **SATISFIED** | Unchanged verdict. `reports/w-tbdep-transitive-inventory.md` and `reports/w-shared-topology-survey.md` already review GAIA answer, Tau DB/call log, TB full actor filesystem/trusted tests and AppWorld service recordings/start-end DBs. W-appworld adds actual mounted-service observation. AppWorld/TB explicitly declare snapshot-service; GAIA/Tau execute that route while declarations remain unknown, not fabricated explicit declarations (`eval/verification/verifier.py::_verify_container_state`). This review clause is complete; broader validation remains separately partial. |
| E8 “without forcing an inferred artifact allowlist” | SATISFIED → **SATISFIED** | Unchanged verdict. `docs/scorer-admission-contract.md`, “Per-bundle isolation (option B)”, and `eval/verification/verifier.py` keep pristine projection an explicit opt-in while preserving snapshot/service/recording routes. `data/datasets/appworld.py` retains mounted service state, and w-appworld observes those recording mounts. No new inferred allowlist, adapter conversion or global pristine requirement is introduced. |

**Bottom line: NOT CLOSED. Deciding clauses: E1, E2, E3, E4, E5, E6 (all PARTIAL).**
E1/E2 now have control-task instances; E7/E8 remain satisfied.

## Decision, scope limits and validation

Registry change: **none**. Both original shared objects/statuses/next_actions,
all 23 references to each (46 total), all dataset/historical records and the pinned
assertions in `tests/quality/test_dataset_blockers.py` stay byte-for-byte unchanged.
No clause is deleted, downgraded or reworded to manufacture a closure. Partial
progress and the satisfied S2 clause are recorded here without removing the
blocker's remaining requirements. No production code, adapter, frozen receipt or
historical evidence is modified. Commit is confined to this isolated worktree.

`docs/enforcement-proof-decision.md` remains governing: snapshot/cleanup are
best-effort with uncertainty retained; known failures/binding mismatches still
refuse. This reassessment does not restore withdrawn filesystem-quota proof,
atomic leases, exhaustive absence, peak bounds or infallible enforcement as new
gates. The remaining clauses concern missing dataset contracts, available
dependencies, actual provenance/measurement scope and applicable live validation.

It would be false to keep saying pristine/AppWorld have no real controls, GAIA/Tau
defaults remain movable, or only nine official/local components were executed.
It would also be false to turn class exercise into dataset breadth, fifteen bounded
components into all-dataset coverage, fixed access/measurement/evidence-retention
defects into ownership/quiescence/equivalence validation, or AppWorld's new service
flags into historical live caps. The invalid original pristine attempt remains
invalid; the fixed final control is genuinely measured; the four staged dataset
diagnostics remain unmeasured publications.

Validation commands and exact checker/test output are recorded in
`reports/w-reassess-validation.txt`: checker **valid=true**, 28 datasets, two
shared blockers, 11 historical records, production_authorized=false; **54 focused
registry tests passed** with pytest basetemp outside the platform tree. These
source-only checks validate registry structure, verbatim evidence locators and
preserved history, not runtime readiness.
