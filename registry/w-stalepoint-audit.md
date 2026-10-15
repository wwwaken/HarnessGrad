# w-stalepoint: registry premise audit

## A. Stale-requirement audit

**FOUND:** 17 stale clauses across eight blocker fields: five `satisfied-selection`, three `satisfied-custody`, eight `withdrawn-shared`, one `other-contradiction` (the counts sum to 17). The complete scan covers 28 dataset records, 14 local blockers and zero global shared blockers. Reproduction: validation transcript command `python3 /mnt/20t/xubuqiang/hg-work/stalepoint/evidence/inspect.py`, whose full source and output are embedded there; `registry/dataset-blockers.json:1061` is `"shared_blockers": []`. No registry/status/history edits are proposed outside `next_action`.

Interpretation: the two shared requirements were **withdrawn**, not solved (`registry/withdrawn-requirements.md:18`, `:44`, `:218`). The source-review gates `pristine-verifier` and `runtime-observations` were recorded closed, not live-dataset validation (`tests/quality/test_dataset_blockers.py:446`, `:461`, `:462`); `independent-evaluator-source` is absent (`:413`, `:414`). Class `withdrawn-shared` below covers stale dependencies on that absent shared set, as requested; it does not relabel all five IDs as operator withdrawals. Retained future pristine opt-in contracts are explicit at `registry/withdrawn-requirements.md:60`. Actual dataset-specific dependency, metric and execution work stays open where requested; pristine-only execution is conditional on an explicit future opt-in. A precondition on a future diagnostic is identified below rather than silently treated as a blocker-closure requirement.

The selection limit is custody for five tasks, not representative sampling, eligibility, scoring or authorization (`registry/w-sel-manifests.md:3`). Seven packets are mixed-side; only TriviaQA is eval-only, and a future run must resolve applicable single-side selection/admission (`registry/w-sel-manifests.md:9`, `:11`). **UNKNOWN:** this audit does not freshly rehash payloads outside git or authenticate historical receipts. Findings of satisfaction mean the registry records and checked-in manifests hold that evidence, not that this worker repeated the original acquisition.

### Complete record coverage

Each row is a reviewed dataset record. “None” means no stale `next_action` clause was established, not production readiness. The exact observation/action text was read from the complete JSON. Line numbers refer to that unchanged file.

| Dataset | Blocker / result | Registry citation |
| --- | --- | --- |
| `agentdojo` | Empty blocker list; no `next_action` to audit | `registry/dataset-blockers.json:5` |
| `alfworld` | Empty blocker list; no `next_action` to audit | `registry/dataset-blockers.json:19` |
| `api_bank` | `retain-contract-refusal`; none established | `registry/dataset-blockers.json:45` |
| `appworld` | `successful-task-evidence`; none established | `registry/dataset-blockers.json:96` |
| `bfcl_v3` | `simple-ast-contract`; none established | `registry/dataset-blockers.json:195` |
| `bird_minidev` | Empty blocker list; no `next_action` to audit | `registry/dataset-blockers.json:209` |
| `chessbench_puzzles` | Empty blocker list; no `next_action` to audit | `registry/dataset-blockers.json:261` |
| `ds1000` | Empty blocker list; no `next_action` to audit | `registry/dataset-blockers.json:312` |
| `fever` | `dataset-journal-gap`; 4 stale clauses | `registry/dataset-blockers.json:376` |
| `gaia` | Empty blocker list; no `next_action` to audit | `registry/dataset-blockers.json:390` |
| `gsm8k` | Empty blocker list; no `next_action` to audit | `registry/dataset-blockers.json:442` |
| `hotpotqa` | `historical-comparison-receipts`; 1 stale clauses | `registry/dataset-blockers.json:491` |
| `jericho` | Empty blocker list; no `next_action` to audit | `registry/dataset-blockers.json:525` |
| `livecodebench` | Empty blocker list; no `next_action` to audit | `registry/dataset-blockers.json:539` |
| `musique` | Empty blocker list; no `next_action` to audit | `registry/dataset-blockers.json:551` |
| `nestful` | `retain-contract-refusal`; none established | `registry/dataset-blockers.json:574` |
| `physicsquestions` | `dataset-journal-gap`; 2 stale clauses | `registry/dataset-blockers.json:625` |
| `reasoning_gym` | `dataset-journal-gap`; 2 stale clauses | `registry/dataset-blockers.json:672` |
| `scienceworld` | Empty blocker list; no `next_action` to audit | `registry/dataset-blockers.json:687` |
| `sotuqa` | `retain-contract-refusal`; none established | `registry/dataset-blockers.json:729` |
| `sportsunderstanding` | `dataset-journal-gap`; 3 stale clauses | `registry/dataset-blockers.json:770` |
| `spreadsheetbench` | `dataset-journal-gap`; 2 stale clauses | `registry/dataset-blockers.json:832` |
| `strategyqa` | `dataset-journal-gap`; 2 stale clauses | `registry/dataset-blockers.json:876` |
| `tau2_bench` | `retain-contract-refusal`; none established | `registry/dataset-blockers.json:903` |
| `tau_bench` | Empty blocker list; no `next_action` to audit | `registry/dataset-blockers.json:918` |
| `terminal_bench` | Empty blocker list; no `next_action` to audit | `registry/dataset-blockers.json:933` |
| `triviaqa` | `hub-export-scorer-linkage`; 1 stale clauses | `registry/dataset-blockers.json:1000` |
| `twowikimultihopqa` | Empty blocker list; no `next_action` to audit | `registry/dataset-blockers.json:1014` |

No-change reasoning: AppWorld asks to review existing protocol evidence while its successful-task receipt remains unresolved (`registry/dataset-blockers.json:63`, `:96`); “review” does not prove a request for missing custody. BFCL explicitly distinguishes established archive/member/graph custody from missing runtime closure and official execution (`:137`, `:195`), so “technical source gate” is not conservatively declared satisfied. The four refusal values are retained verbatim at `:45`, `:574`, `:729`, `:903`; no adapter, payload or metric for those datasets was executed or changed.

### Exact stale clauses and clause-level proposals

#### A01. fever / dataset-journal-gap — `satisfied-custody`

Exact `next_action` clause (`registry/dataset-blockers.json:376`):

> bind the authenticated exact Hub revision/tree export metadata to actual export bytes

Exact `observed` sentence (`registry/dataset-blockers.json:348`):

> This supersedes only the actual-export-byte/installed-inventory part of the prior gap; producing conversion and original FEVER ID/complete evidence-group correspondence, flat-to-singleton metric comparability, independently supplied selection/export and chosen run split/side, actual pristine execution and shared evidence remain unmet.

Conservative boundary: The installed byte-to-Hub binding is explicitly recorded; producing-conversion and group semantics remain open.

Proposed replacement clause: Retain the authenticated Hub-to-installed-export byte binding; bind the producing conversion separately. The complete standalone field value is under `fever` below and in every corresponding proposal entry.

#### A02. fever / dataset-journal-gap — `satisfied-custody`

Exact `next_action` clause (`registry/dataset-blockers.json:376`):

> establish installed bytes

Exact `observed` sentence (`registry/dataset-blockers.json:348`):

> Installed export-byte custody is already corroborated and selected manifest custody is now bound.

Conservative boundary: This is already held; neither this classification nor the selected packet authenticates the producing conversion.

Proposed replacement clause: Retain installed-byte custody. The complete standalone field value is under `fever` below and in every corresponding proposal entry.

#### A03. fever / dataset-journal-gap — `satisfied-selection`

Exact `next_action` clause (`registry/dataset-blockers.json:376`):

> selected manifest custody

Exact `observed` sentence (`registry/dataset-blockers.json:348`):

> Installed export-byte custody is already corroborated and selected manifest custody is now bound.

Manifest: `tests/fixtures/hg_wsel/fever.json:4` (selection identity), `tests/fixtures/hg_wsel/fever.json:6` (null runtime ID), `tests/fixtures/hg_wsel/fever.json:38` (five selected), `tests/fixtures/hg_wsel/fever.json:45` (declared split), `tests/fixtures/hg_wsel/fever.json:47` (side), `tests/fixtures/hg_wsel/fever.json:60` (external export), `tests/fixtures/hg_wsel/fever.json:62` (file hashes), `tests/fixtures/hg_wsel/fever.json:82` (per-task source/prompt/scorer-input hashes).

Conservative boundary: Only the bounded five-task custody request is satisfied, not a runnable single-side selection.

Proposed replacement clause: Retain the bounded first-five manifest/export and declared per-task sides; resolve future diagnostic split/side separately. The complete standalone field value is under `fever` below and in every corresponding proposal entry.

#### A04. fever / dataset-journal-gap — `withdrawn-shared`

Exact `next_action` clause (`registry/dataset-blockers.json:376`):

> establish scorer-offline-closure and pristine verifier evidence with all remaining shared gates before any separately authorized diagnostic.

Withdrawal/absence evidence: `registry/withdrawn-requirements.md:18`, `:44`; the actual empty shared list is `registry/dataset-blockers.json:1061`. The source-review/opt-in distinction is documented above.

Conservative boundary: Named and generic shared admission gates are absent. This sentence is a future-diagnostic precondition; retain actual selected scorer/runtime evidence for that future diagnostic under its declared runtime, and make pristine-specific work conditional on a future opt-in.

Proposed replacement clause: Document the metric and preserve dataset-specific execution obligations for a separately authorized diagnostic; do not restore shared closure gates. The complete standalone field value is under `fever` below and in every corresponding proposal entry.

#### A05. hotpotqa / historical-comparison-receipts — `withdrawn-shared`

Exact `next_action` clause (`registry/dataset-blockers.json:491`):

> and all existing shared gates remain required.

Withdrawal/absence evidence: `registry/withdrawn-requirements.md:18`, `:44`; the actual empty shared list is `registry/dataset-blockers.json:1061`. The source-review/opt-in distinction is documented above.

Conservative boundary: The current selected scorer/control admission and historical receipts are independent obligations. The shared portion cannot remain an active requirement.

Proposed replacement clause: Current selected scorer/control admission remains required for any separately authorized future diagnostic; withdrawn shared gates do not. The complete standalone field value is under `hotpotqa` below and in every corresponding proposal entry.

#### A06. physicsquestions / dataset-journal-gap — `satisfied-selection`

Exact `next_action` clause (`registry/dataset-blockers.json:625`):

> NEXT gate: bind an independently supplied run-specific selected manifest and selected-only export to the preserved installed CSV, row/task inventory and chosen split/side; no selection or run ID is supplied here.

Exact `observed` sentence (`registry/dataset-blockers.json:592`):

> Selected manifest/export to exact rows and declared per-task sides is now bound.

Manifest: `tests/fixtures/hg_wsel/physicsquestions.json:4` (selection identity), `tests/fixtures/hg_wsel/physicsquestions.json:6` (null runtime ID), `tests/fixtures/hg_wsel/physicsquestions.json:38` (five selected), `tests/fixtures/hg_wsel/physicsquestions.json:45` (declared split), `tests/fixtures/hg_wsel/physicsquestions.json:47` (side), `tests/fixtures/hg_wsel/physicsquestions.json:60` (external export), `tests/fixtures/hg_wsel/physicsquestions.json:62` (file hashes), `tests/fixtures/hg_wsel/physicsquestions.json:120` (per-task source/prompt/scorer-input hashes).

Conservative boundary: The prospective selection ID, split mode and per-task sides now exist; runtime_run_id stays null, and mixed-side launch resolution remains future work.

Proposed replacement clause: Retain the bounded first-five manifest/export and reserved selection identity; resolve future diagnostic split/side and runtime binding. The complete standalone field value is under `physicsquestions` below and in every corresponding proposal entry.

#### A07. physicsquestions / dataset-journal-gap — `withdrawn-shared`

Exact `next_action` clause (`registry/dataset-blockers.json:625`):

> Then establish scorer-offline-closure, pristine verifier execution and remaining shared evidence.

Withdrawal/absence evidence: `registry/withdrawn-requirements.md:18`, `:44`; the actual empty shared list is `registry/dataset-blockers.json:1061`. The source-review/opt-in distinction is documented above.

Conservative boundary: Do not turn absent shared gates into closure conditions. Actual scorer/runtime execution remains unobserved future-diagnostic evidence; pristine-only obligations apply on opt-in.

Proposed replacement clause: For a separately authorized diagnostic obtain selected scorer/runtime evidence under the declared runtime; preserve the future pristine opt-in boundary. The complete standalone field value is under `physicsquestions` below and in every corresponding proposal entry.

#### A08. reasoning_gym / dataset-journal-gap — `satisfied-selection`

Exact `next_action` clause (`registry/dataset-blockers.json:672`):

> bind an independently supplied run-specific selected manifest and selected-only export to exact pool rows and chosen split/side.

Exact `observed` sentence (`registry/dataset-blockers.json:644`):

> Selected frozen-row custody is now bound; no seed/family/order substitution, regeneration or pool overwrite occurred.

Manifest: `tests/fixtures/hg_wsel/reasoning_gym.json:4` (selection identity), `tests/fixtures/hg_wsel/reasoning_gym.json:6` (null runtime ID), `tests/fixtures/hg_wsel/reasoning_gym.json:38` (five selected), `tests/fixtures/hg_wsel/reasoning_gym.json:45` (declared split), `tests/fixtures/hg_wsel/reasoning_gym.json:47` (side), `tests/fixtures/hg_wsel/reasoning_gym.json:60` (external export), `tests/fixtures/hg_wsel/reasoning_gym.json:62` (file hashes), `tests/fixtures/hg_wsel/reasoning_gym.json:120` (per-task source/prompt/scorer-input hashes).

Conservative boundary: Only selected frozen-row custody is supplied; original generation metadata, exact reproduction and behavioral eligibility remain open.

Proposed replacement clause: Retain selected frozen-row custody and declared per-task sides; resolve future launch split/side. The complete standalone field value is under `reasoning_gym` below and in every corresponding proposal entry.

#### A09. reasoning_gym / dataset-journal-gap — `withdrawn-shared`

Exact `next_action` clause (`registry/dataset-blockers.json:672`):

> scorer-offline-closure and all remaining shared evidence

Withdrawal/absence evidence: `registry/withdrawn-requirements.md:18`, `:44`; the actual empty shared list is `registry/dataset-blockers.json:1061`. The source-review/opt-in distinction is documented above.

Conservative boundary: Retain dataset-specific deterministic transitive dependencies without scoring extras, metric/runtime validation and pristine execution on a future explicit opt-in, rather than deleting those obligations with the shared IDs.

Proposed replacement clause: Preserve dataset-specific dependency/metric/runtime obligations for a separately authorized diagnostic, without shared closure gates. The complete standalone field value is under `reasoning_gym` below and in every corresponding proposal entry.

#### A10. sportsunderstanding / dataset-journal-gap — `other-contradiction`

Exact `next_action` clause (`registry/dataset-blockers.json:770`):

> report the local text-label metric separately

Exact `observed` sentence (`registry/dataset-blockers.json:747`):

> Local text-label metric is explicitly separated here, satisfying that reporting alternative without resolving the underlying protocol difference.

Conservative boundary: The reporting alternative has been exercised. Keep separate reporting as an ongoing requirement; do not claim the protocol mismatch is resolved.

Proposed replacement clause: Continue reporting the local text-label metric separately; do not claim multiple_choice_grade equivalence. The complete standalone field value is under `sportsunderstanding` below and in every corresponding proposal entry.

#### A11. sportsunderstanding / dataset-journal-gap — `satisfied-selection`

Exact `next_action` clause (`registry/dataset-blockers.json:770`):

> Bind an independently supplied run-specific selected manifest and selected-only export to exact source rows and chosen split/side

Exact `observed` sentence (`registry/dataset-blockers.json:747`):

> Selected manifest/export and declared per-task sides are now bound.

Manifest: `tests/fixtures/hg_wsel/sportsunderstanding.json:4` (selection identity), `tests/fixtures/hg_wsel/sportsunderstanding.json:6` (null runtime ID), `tests/fixtures/hg_wsel/sportsunderstanding.json:38` (five selected), `tests/fixtures/hg_wsel/sportsunderstanding.json:45` (declared split), `tests/fixtures/hg_wsel/sportsunderstanding.json:47` (side), `tests/fixtures/hg_wsel/sportsunderstanding.json:60` (external export), `tests/fixtures/hg_wsel/sportsunderstanding.json:62` (file hashes), `tests/fixtures/hg_wsel/sportsunderstanding.json:120` (per-task source/prompt/scorer-input hashes).

Conservative boundary: This is satisfied only for first-five custody and per-task declared sides.

Proposed replacement clause: Retain the bounded first-five manifest/export; resolve future diagnostic launch split/side. The complete standalone field value is under `sportsunderstanding` below and in every corresponding proposal entry.

#### A12. sportsunderstanding / dataset-journal-gap — `withdrawn-shared`

Exact `next_action` clause (`registry/dataset-blockers.json:770`):

> then establish scorer-offline-closure, pristine runtime and all shared admission evidence before any separately authorized diagnostic.

Withdrawal/absence evidence: `registry/withdrawn-requirements.md:18`, `:44`; the actual empty shared list is `registry/dataset-blockers.json:1061`. The source-review/opt-in distinction is documented above.

Conservative boundary: This explicitly conditions a future diagnostic. Keep dataset-specific runtime validation for that diagnostic and conditional future pristine opt-in work, rather than treating it as a shared closure gate.

Proposed replacement clause: For a separately authorized diagnostic obtain selected scorer/runtime evidence under the declared runtime; retain conditional pristine boundaries. The complete standalone field value is under `sportsunderstanding` below and in every corresponding proposal entry.

#### A13. spreadsheetbench / dataset-journal-gap — `satisfied-custody`

Exact `next_action` clause (`registry/dataset-blockers.json:832`):

> independently authenticate complete installed workbook/mirror

Exact `observed` sentence (`registry/dataset-blockers.json:789`):

> Prior w-jc2 already established complete installed workbook/mirror custody; this packet freshly checks only selected bytes, and does not reopen or re-prove whole-mirror custody.

Conservative boundary: The mirror-to-original and installed pair custody work is recorded complete; scorer custody/execution is a distinct unsatisfied suffix.

Proposed replacement clause: Retain complete installed workbook/mirror-to-original custody; establish scorer custody/execution separately. The complete standalone field value is under `spreadsheetbench` below and in every corresponding proposal entry.

#### A14. spreadsheetbench / dataset-journal-gap — `withdrawn-shared`

Exact `next_action` clause (`registry/dataset-blockers.json:832`):

> and both shared gates (scorer-offline-closure and artifact-only-state-export) before a separately authorized diagnostic.

Withdrawal/absence evidence: `registry/withdrawn-requirements.md:18`, `:44`; the actual empty shared list is `registry/dataset-blockers.json:1061`. The source-review/opt-in distinction is documented above.

Conservative boundary: Remove the shared precondition on a future diagnostic only; authenticated eligibility, actual coverage, scorer execution and formula/LibreOffice offline runtime remain open.

Proposed replacement clause: Retain dataset-specific eligibility, execution and formula/LibreOffice runtime requirements for a separately authorized diagnostic; shared gates remain withdrawn. The complete standalone field value is under `spreadsheetbench` below and in every corresponding proposal entry.

#### A15. strategyqa / dataset-journal-gap — `satisfied-selection`

Exact `next_action` clause (`registry/dataset-blockers.json:876`):

> next bind an independently supplied run-specific selected manifest and selected-only export to exact source rows and chosen split/side

Exact `observed` sentence (`registry/dataset-blockers.json:853`):

> Selected exact-row export and declared per-task sides are now bound.

Manifest: `tests/fixtures/hg_wsel/strategyqa.json:4` (selection identity), `tests/fixtures/hg_wsel/strategyqa.json:6` (null runtime ID), `tests/fixtures/hg_wsel/strategyqa.json:38` (five selected), `tests/fixtures/hg_wsel/strategyqa.json:45` (declared split), `tests/fixtures/hg_wsel/strategyqa.json:47` (side), `tests/fixtures/hg_wsel/strategyqa.json:60` (external export), `tests/fixtures/hg_wsel/strategyqa.json:62` (file hashes), `tests/fixtures/hg_wsel/strategyqa.json:120` (per-task source/prompt/scorer-input hashes).

Conservative boundary: Only first-five selected custody is satisfied; original benchmark comparability and actual execution remain open.

Proposed replacement clause: Retain the first-five exact-row manifest/export and declared per-task sides; resolve future diagnostic launch split/side. The complete standalone field value is under `strategyqa` below and in every corresponding proposal entry.

#### A16. strategyqa / dataset-journal-gap — `withdrawn-shared`

Exact `next_action` clause (`registry/dataset-blockers.json:876`):

> pristine verifier/runtime and all shared admission evidence before any separately authorized diagnostic.

Withdrawal/absence evidence: `registry/withdrawn-requirements.md:18`, `:44`; the actual empty shared list is `registry/dataset-blockers.json:1061`. The source-review/opt-in distinction is documented above.

Conservative boundary: Deterministic offline dependencies and actual execution-equivalence remain dataset-local future-diagnostic work. Pristine runtime is conditional on an explicit future opt-in.

Proposed replacement clause: Keep deterministic offline dependencies and selected scorer/runtime execution evidence for a separately authorized diagnostic, with pristine-specific work conditional on future opt-in; do not restore shared gates. The complete standalone field value is under `strategyqa` below and in every corresponding proposal entry.

#### A17. triviaqa / hub-export-scorer-linkage — `withdrawn-shared`

Exact `next_action` clause (`registry/dataset-blockers.json:1000`):

> and all shared admission gates

Withdrawal/absence evidence: `registry/withdrawn-requirements.md:18`, `:44`; the actual empty shared list is `registry/dataset-blockers.json:1061`. The source-review/opt-in distinction is documented above.

Conservative boundary: The provenance, metadata-only compatibility and identity-preservation clauses remain open/retained; selected five-row custody does not discharge them.

Proposed replacement clause: Preserve v2 and historical identities; withdrawn shared gates do not condition closure or admission. The complete standalone field value is under `triviaqa` below and in every corresponding proposal entry.

### Clauses deliberately retained

HotpotQA’s “original selected-ID/trial/error/timeout” requirement concerns historical receipts (`registry/dataset-blockers.json:491`); the appended observation explicitly says the first-five packet does not recover historical selection or run ID (`:458`). It is not `satisfied-selection`. TriviaQA’s next action never requested a new selection (`:1000`); its converter-execution and without-rows provenance obligations remain open despite the new packet (`:952`).

Reasoning Gym’s “No independent seed-specific pool release or selected run manifest was authenticated from the acquired public sources.” is source-qualified (`registry/dataset-blockers.json:672`); an operator-supplied packet does not contradict that historical public-source finding. Original generation/reproduction and reference=1/empty=0 behavioral eligibility remain open (`:644`). SpreadsheetBench’s coverage clause includes eligible/task/trial/invalid/unmeasured execution coverage (`:832`); selected=5 alone does not satisfy that compound request (`:789`), so it is not classified wholesale as stale. Its scorer custody/execution and formula/LibreOffice offline runtime likewise stay open. FEVER’s complete group/converter correspondence and singleton comparability are not solved by installed-byte or first-five custody (`:348`).

### Complete standalone replacement values

These are proposals for parent review, not claims that a blocker is closed. The JSON has one entry per stale clause. Entries for the same dataset/blocker intentionally repeat the **same complete replacement** so mechanical assignment is idempotent and independent of entry order. All other registry fields remain outside this proposal.

#### fever

Retain the authenticated exact Hub revision/tree-to-installed-export byte binding and installed inventory, and the bounded operator first-five selected manifest/export and declared per-task sides in tests/fixtures/hg_wsel/fever.json. The mixed-side packet is custody evidence, not an accepted single-side diagnostic specification. Bind the producing conversion, revision/execution, ID assignment, split/filter/omission and NEI inputs, and resolve complete original FEVER ID/evidence-group correspondence and flat-to-singleton metric comparability; the existing row mapping does not recover omitted alternative groups or establish singleton equivalence. Use the acquired exact scorer source revision without inventing a release. Document the actual metric. For any separately authorized diagnostic, resolve applicable split/side and run binding and obtain actual selected scorer/runtime execution evidence under the declared runtime; no execution is established by custody. Any future pristine opt-in must meet the retained per-task export/private-input and backend/source/projection ownership boundary in registry/withdrawn-requirements.md. The withdrawn shared gates do not condition closure or admission, and the official-scorer-identity proof obligation stays withdrawn. No diagnostic is authorized by this record.

#### hotpotqa

Historical comparison requires original selected-ID/trial/error/timeout and source/split/manifest/model/harness provenance receipts, with measured/invalid/unmeasured counts and lifecycle/cleanup reconciliation. Preserve the old full-size protocol as incomplete, unknown run ID and effect=null; do not resume or rerun it. Timeout classification/persistence/aggregation is synthetically closed. Retain the bounded first-five selected manifest/export and declared per-task sides in tests/fixtures/hg_wsel/hotpotqa.json; this mixed-side packet does not recover historical selection, the unknown historical run ID or historical coverage. Current selected scorer/control admission remains a requirement for any separately authorized future diagnostic, which uses a fresh ID and resolves applicable split/side under the current staged policy. Withdrawn shared gates do not condition closure or admission.

#### physicsquestions

Retain the independently supplied bounded operator first-five manifest and selected-only export bound to the preserved installed CSV, exact rows and declared per-task sides in tests/fixtures/hg_wsel/physicsquestions.json. The reserved selection ID is not a runtime receipt; this mixed-side packet is not an accepted single-side diagnostic specification. Retain installed-to-ReWOO and ordered pinned-BIG-bench linkage, report local normalized accepted-spelling EM separately from matched BIG-bench processing/aggregation, and do not infer a historical converter revision or runtime execution. For any separately authorized diagnostic, resolve applicable split/side and run binding and obtain actual selected scorer/runtime execution evidence under the declared runtime, with explicit invalid/unmeasured coverage. Apply the retained pristine export/private-input and ownership boundary only to a future pristine opt-in; do not restore withdrawn scorer-offline-closure or other absent shared gates. Preserve the withdrawn official-scorer-identity proof decision; no diagnostic is authorized.

#### reasoning_gym

Retain authenticated distribution/source/installed-member custody and declared pool hash/family/order evidence; recover original generation environment/date/order metadata and reproduce the declared pool with recorded inputs, without changing its seed/families or overwriting original bytes. Independently establish behavioral reference=1/empty=0 family eligibility. Retain the bounded operator first-five selected manifest/export bound to exact frozen pool rows and declared per-task sides in tests/fixtures/hg_wsel/reasoning_gym.json; this mixed-side packet is not an accepted single-side diagnostic specification. No independent seed-specific pool release or selected run manifest was authenticated from the acquired public sources; the operator selection packet is separate evidence. For any separately authorized diagnostic, resolve applicable split/side and run binding, establish deterministic transitive dependencies without scoring extras and metric identity, and obtain actual selected scorer/runtime execution evidence under the declared runtime. Actual pristine execution is a future diagnostic obligation only if that runtime is explicitly opted in, subject to the retained export/private-input and ownership boundary; absent shared gates do not condition closure or admission. The official-scorer-identity proof obligation stays withdrawn. No diagnostic is authorized.

#### sportsunderstanding

Retain authenticated installed-to-ReWOO and pinned BIG-bench sports row linkage. Continue reporting the local text-label metric separately; its candidate-log-probability multiple_choice_grade mismatch is unresolved and no equivalence is claimed. Retain the bounded operator first-five selected manifest/export bound to exact source rows and declared per-task sides in tests/fixtures/hg_wsel/sportsunderstanding.json; this mixed-side packet is not an accepted single-side diagnostic specification. For any separately authorized diagnostic, resolve applicable split/side and run binding and obtain actual selected scorer/runtime execution evidence under the declared runtime. Actual pristine execution applies only to a future explicit pristine opt-in with the retained export/private-input and ownership boundary; withdrawn shared gates do not condition closure or admission. Report invalid/unmeasured coverage explicitly. No diagnostic is authorized.

#### spreadsheetbench

Establish authenticated row-level gradable eligibility and actual eligible/task/trial/invalid/unmeasured execution coverage under the explicit official-range-zero compatibility policy. Retain the already established complete installed workbook/mirror-to-original custody and the bounded operator first-five selected manifest/export with workbook/task-input digests and declared per-task sides in tests/fixtures/hg_wsel/spreadsheetbench.json; selected=5 is not eligibility or executed coverage, and the mixed-side packet is not an accepted single-side diagnostic specification. Scorer custody/execution and formula/LibreOffice offline runtime remain open dataset-specific work for a separately authorized diagnostic, which must resolve applicable split/side and run binding. The withdrawn scorer-offline-closure and artifact-only-state-export shared gates do not condition closure or admission; retain their recorded limits and future pristine opt-in boundary. Retain the official-equivalent measured-zero denominator for released parser-rejected ranges, distinguish it from completed comparisons, and never publish infrastructure failures as scores. Keep one-variant scores distinct from paper soft/hard aggregates and do not promote repaired synthetic/local controls to production evidence.

#### strategyqa

Retain authenticated installed CSV/member/revision and ReWOO evaluator identity, and the bounded operator first-five selected manifest/export bound to exact source rows and declared per-task sides in tests/fixtures/hg_wsel/strategyqa.json. The mixed-side packet is not an accepted single-side diagnostic specification. Resolve original-benchmark metric/split comparability beyond the vendored table. For any separately authorized diagnostic, resolve applicable split/side and run binding, establish deterministic offline dependencies and obtain actual selected scorer/runtime execution evidence under the declared runtime. Actual pristine execution applies only to a future explicit pristine opt-in with the retained export/private-input and ownership boundary; withdrawn shared gates do not condition closure or admission. Acquired evaluator bytes are not an execution-equivalence receipt; retain EM identity and explicit invalid/unmeasured task/trial coverage. No diagnostic is authorized.

#### triviaqa

Obtain immutable build/export provenance binding Hub export 0f7faf33a3908546c6fd5b73a660e0f8ff173c2f to the loader/converter actually executed, source/license hashes, runtime/writer versions and consumed input revision/hashes; the inspected authoritative public record supplies ancestry/output declarations but no execution receipt. PR ancestry, identical predecessor blobs and similarly named converter artifacts do not attest execution. Review HumanAnswers preservation/absence/redundancy, Domain/VerifiedEval/source membership, duplicates, scorer-key mapping and denominator/aggregation without rows. Retain the bounded operator first-five eval-side manifest/export and scoring-input custody in tests/fixtures/hg_wsel/triviaqa.json without treating it as converter-execution or metadata-only provenance evidence. Preserve v2 and historical identities; withdrawn shared admission gates do not condition closure or admission. No production authorization.

## B. Orphaned-citation audit

**FOUND:** 48 `external-reference` entries, 29 distinct absolute paths: **5 readable / 24 unreadable**. Of those, 22 distinct `/site/...` paths are all unreadable; seven other absolute paths split 5/2. Exact command: `python3 /mnt/20t/xubuqiang/hg-work/stalepoint/evidence/external.py`; full script, output and exit code are embedded in validation. Scope: recursively every object in the current registry with `kind == "external-reference"`, including historical runs. “Readable” means `open(path, "rb")` followed by `read(0)` succeeded; no receipt body was read. Every unreadable result below was `errno=2 No such file or directory`. This is a machine accessibility observation, not authentication or evidence of a missing fact.

This evidence kind is **unverifiable from the repository alone**: the checker requires an absolute path and deliberately bypasses existence/locator validation for it (`tools/check_dataset_blockers.py:109`, `:111`, `:112`). A readable historical receipt still requires separate authentication; an unreadable `/site/...` placeholder proves nothing about the cited observation. The registry itself retains that warning at `registry/dataset-blockers.json:1045`.

| Exact absolute path | Entries | Registry path line(s) | Observed accessibility |
| --- | ---: | --- | --- |
| `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/chess/interruption-audit.md` | 2 | registry/dataset-blockers.json:282, registry/dataset-blockers.json:301 | READABLE |
| `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/101/deliverables/receipt.md` | 1 | registry/dataset-blockers.json:122 | READABLE |
| `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/61/report.md` | 1 | registry/dataset-blockers.json:333 | READABLE |
| `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/qa-h0-archive-v4/index.json` | 2 | registry/dataset-blockers.json:231, registry/dataset-blockers.json:250 | UNREADABLE errno=2 No such file or directory |
| `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/qa-h0-incomplete-index.json` | 1 | registry/dataset-blockers.json:514 | UNREADABLE errno=2 No such file or directory |
| `/mnt/20t/xubuqiang/Study/gaia-h0-launch-v2-evidence/GAIA_H0_V2_RECEIPT.json` | 1 | registry/dataset-blockers.json:412 | READABLE |
| `/mnt/20t/xubuqiang/Study/gaia-h0-launch-v3/runs/gaia-validation-pilot-h0-20261117-v3/events.jsonl` | 1 | registry/dataset-blockers.json:431 | READABLE |
| `/site/adapter-integration-journal.md` | 13 | registry/dataset-blockers.json:72, registry/dataset-blockers.json:92, registry/dataset-blockers.json:141, registry/dataset-blockers.json:362, registry/dataset-blockers.json:462, registry/dataset-blockers.json:606, registry/dataset-blockers.json:658, registry/dataset-blockers.json:761, registry/dataset-blockers.json:803, registry/dataset-blockers.json:828, registry/dataset-blockers.json:867, registry/dataset-blockers.json:956, registry/dataset-blockers.json:996 | UNREADABLE errno=2 No such file or directory |
| `/site/b9-appworld-protocol-and-pilot-guidance-review.md` | 1 | registry/dataset-blockers.json:77 | UNREADABLE errno=2 No such file or directory |
| `/site/bfcl-blob-retry-codex227-report.md` | 1 | registry/dataset-blockers.json:151 | UNREADABLE errno=2 No such file or directory |
| `/site/dataset-reviews/fever.md` | 1 | registry/dataset-blockers.json:357 | UNREADABLE errno=2 No such file or directory |
| `/site/dataset-reviews/physicsquestions.md` | 1 | registry/dataset-blockers.json:601 | UNREADABLE errno=2 No such file or directory |
| `/site/dataset-reviews/reasoning_gym.md` | 1 | registry/dataset-blockers.json:653 | UNREADABLE errno=2 No such file or directory |
| `/site/dataset-source-reviews-b2.md` | 3 | registry/dataset-blockers.json:756, registry/dataset-blockers.json:798, registry/dataset-blockers.json:862 | UNREADABLE errno=2 No such file or directory |
| `/site/e1-fever-physics-bird-review.md` | 2 | registry/dataset-blockers.json:372, registry/dataset-blockers.json:616 | UNREADABLE errno=2 No such file or directory |
| `/site/e3-bfcl-simple-source-review.md` | 1 | registry/dataset-blockers.json:166 | UNREADABLE errno=2 No such file or directory |
| `/site/enforcement-proof-decision.md` | 3 | registry/dataset-blockers.json:367, registry/dataset-blockers.json:611, registry/dataset-blockers.json:663 | UNREADABLE errno=2 No such file or directory |
| `/site/independent-review-deferred.md` | 1 | registry/dataset-blockers.json:191 | UNREADABLE errno=2 No such file or directory |
| `/site/measurement-coverage-hg-b3-review.md` | 1 | registry/dataset-blockers.json:467 | UNREADABLE errno=2 No such file or directory |
| `/site/triviaqa-hub-linkage-codex225-report.md` | 1 | registry/dataset-blockers.json:976 | UNREADABLE errno=2 No such file or directory |
| `/site/triviaqa-review-codex215-report.md` | 1 | registry/dataset-blockers.json:966 | UNREADABLE errno=2 No such file or directory |
| `/site/w-appworld-receipts.md` | 1 | registry/dataset-blockers.json:82 | UNREADABLE errno=2 No such file or directory |
| `/site/w-appworld2-receipts.md` | 1 | registry/dataset-blockers.json:87 | UNREADABLE errno=2 No such file or directory |
| `/site/w-bfcl-review.md` | 1 | registry/dataset-blockers.json:176 | UNREADABLE errno=2 No such file or directory |
| `/site/w-hotpot-timeout-closure.md` | 1 | registry/dataset-blockers.json:477 | UNREADABLE errno=2 No such file or directory |
| `/site/w-hotpot-validation.txt` | 1 | registry/dataset-blockers.json:487 | UNREADABLE errno=2 No such file or directory |
| `/site/w-spread2-evidence/audit-output.txt` | 1 | registry/dataset-blockers.json:818 | UNREADABLE errno=2 No such file or directory |
| `/site/w-spread2-reconciliation.md` | 1 | registry/dataset-blockers.json:813 | UNREADABLE errno=2 No such file or directory |
| `/site/w-trivia-review.md` | 1 | registry/dataset-blockers.json:986 | UNREADABLE errno=2 No such file or directory |

## C. Test-pin audit

**ABSENT in the enumerated scope:** no assertion in the complete 657-line `tests/quality/test_dataset_blockers.py` requires a withdrawn shared ID to be present, or asserts that the eight first-five selections/manifests/run IDs are still absent. Scope and reproduction: the full-file AST assertion inventory in validation (`inspect.py` source and stdout). Below are all assertions that pin the relevant withdrawn/closed shared IDs, their retained evidence, empty sets, or earlier withdrawn shared IDs. They currently **pass** in the requested file; pass does not extend to skipped tests or external evidence.

`tests/quality/test_dataset_blockers.py:99` — **PASS**:

```python
assert set(shared) == set()
```

`tests/quality/test_dataset_blockers.py:104` — **PASS**:

```python
assert "**Searched:** `w-scope` reviewed all 28 declared datasets" in observed
```

`tests/quality/test_dataset_blockers.py:107` — **PASS**:

```python
assert former_action == (
        "Provision authoritative per-task export and private-input contracts for pristine scorers; "
        "validate ownership, quiescence/trial binding, scoring equivalence and live lifecycle/cleanup. "
        "Review snapshot/service state and recording surfaces under their declared class without "
        "forcing an inferred artifact allowlist.")
```

`tests/quality/test_dataset_blockers.py:121` — **PASS**:

```python
assert boundary in observed
```

`tests/quality/test_dataset_blockers.py:122` — **PASS**:

```python
assert "`/site/w-scope-pristine-applicability.md`,\nlocator `## Exact registry wording`" in observed
```

`tests/quality/test_dataset_blockers.py:125` — **PASS**:

```python
assert "`w-s6` traced the path" in scorer
```

`tests/quality/test_dataset_blockers.py:126` — **PASS**:

```python
assert "flag only flips after the admission the clause itself\nhelps withhold" in scorer
```

`tests/quality/test_dataset_blockers.py:127` — **PASS**:

```python
assert "directory-substitution/restore counterexample evades those probes" in observed
```

`tests/quality/test_dataset_blockers.py:325` — **PASS**:

```python
assert set(target["shared_blockers"]) == set()
```

`tests/quality/test_dataset_blockers.py:328` — **PASS**:

```python
assert blocker_id not in {item["id"] for item in document["shared_blockers"]}
```

`tests/quality/test_dataset_blockers.py:329` — **PASS**:

```python
assert f"## Shared requirement withdrawn: `{blocker_id}`" in withdrawal
```

`tests/quality/test_dataset_blockers.py:330` — **PASS**:

```python
assert "flag only flips after the admission the clause itself\nhelps withhold" in withdrawal
```

`tests/quality/test_dataset_blockers.py:331` — **PASS**:

```python
assert "directory-substitution/restore counterexample evades those probes" in withdrawal
```

`tests/quality/test_dataset_blockers.py:361` — **PASS**:

```python
assert target["shared_blockers"] == shared, f"{name}: shared gates drifted"
```

`tests/quality/test_dataset_blockers.py:413` — **PASS**:

```python
assert "independent-evaluator-source" not in blockers
```

`tests/quality/test_dataset_blockers.py:414` — **PASS**:

```python
assert "independent-evaluator-source" not in target["shared_blockers"]
```

`tests/quality/test_dataset_blockers.py:453` — **PASS**:

```python
assert set(target["shared_blockers"]) == set()
```

`tests/quality/test_dataset_blockers.py:456` — **PASS**:

```python
assert blocker_id not in {b["id"] for b in document["shared_blockers"]}
```

`tests/quality/test_dataset_blockers.py:457` — **PASS**:

```python
assert f"## Shared requirement withdrawn: `{blocker_id}`" in withdrawal
```

`tests/quality/test_dataset_blockers.py:458` — **PASS**:

```python
assert "`w-s6` traced the path" in withdrawal
```

`tests/quality/test_dataset_blockers.py:459` — **PASS**:

```python
assert "flag only flips after the admission the clause itself\nhelps withhold" in withdrawal
```

`tests/quality/test_dataset_blockers.py:460` — **PASS**:

```python
assert "directory-substitution/restore counterexample evades those probes" in withdrawal
```

`tests/quality/test_dataset_blockers.py:461` — **PASS**:

```python
assert "pristine-verifier" not in {b["id"] for b in document["shared_blockers"]}
```

`tests/quality/test_dataset_blockers.py:462` — **PASS**:

```python
assert "runtime-observations" not in {b["id"] for b in document["shared_blockers"]}
```

`tests/quality/test_dataset_blockers.py:464` — **PASS**:

```python
assert "pristine-verifier review action closed" in notes
```

`tests/quality/test_dataset_blockers.py:465` — **PASS**:

```python
assert "runtime-observations source-review action closed" in notes
```

`tests/quality/test_dataset_blockers.py:468` — **PASS**:

```python
assert gone not in target["shared_blockers"]
```

Loop/alias scope for the exact assertions above: `observed` is the artifact-only withdrawal section (`tests/quality/test_dataset_blockers.py:101`); the line-121 `boundary` tuple is at `:112` and preserves zero applicable pristine datasets, future opt-in contracts and partial standing limits. `scorer` is the scorer withdrawal section (`:123`). `blocker_id` is each of the two withdrawn IDs at `:327` and `:455`. Line 361 runs for Jericho and ScienceWorld and compares each empty list against the live global empty list (`:358`, `:359`), so it passes vacuously as a gate-presence check; its test name/docstring still says “shared ones stand” (`:341`, `:342`) but is not a stale positive assertion. Line 468 loops over paired-filesystem-quotas, pilot-guidance-conflict (completed), official-scorer-identity and snapshot-owned-cleanup (`:466`).

The pristine applicability guards at `tests/quality/test_dataset_blockers.py:76`, `:84`, `:88` also **PASS**. They inspect declarations/QA scaffold for an explicit pristine opt-in, rather than asserting no selected tasks exist. The phrase “zero pristine-offline declarations or selections” at `:113` is withdrawal evidence, not a pre-w-sel selection premise. Source-review closure pins `:464` and `:465` check historical notes; they do not require a shared gate.

Exact requested command (environment `TMPDIR=/mnt/20t/xubuqiang/hg-work/stalepoint/tmp`):

```sh
python3 -m pytest tests/quality/test_dataset_blockers.py -q --basetemp=/mnt/20t/xubuqiang/hg-work/stalepoint/pytest
```

Exact observed output, exit 0:

```text
s...ssssss..sssssssssssssssss..s..sss.s..sss.sssssssssssssssssssss....s. [ 97%]
.s                                                                       [100%]
19 passed, 55 skipped in 0.68s
```

A follow-up `-ra` run used the same file/basetemp to diagnose the previously unexplained skips (full exact output in validation): **19 passed, 55 skipped in 0.47s**. Of the skips, **40** are caused by the four absent registry-cited `repository` observations below, and **15** by 13 distinct absent mapped site-source files. No fixtures were supplied or substituted. Absence scope for repository observations: all 26 distinct `kind=repository` paths recursively cited by current local/shared blockers and historical runs; exact enumerated scope/output is in validation. The four paths are:

- `tests/fixtures/hg_bfcl/README.md`
- `tests/fixtures/hg_bfcl/inventory.json`
- `tests/fixtures/hg_trivia/README.md`
- `tests/fixtures/hg_wprov/README.md`

The fixture tests this subset at `tests/quality/conftest.py:37` through `:45`. The 40 skipped instances are at `tests/quality/test_dataset_blockers.py:57` (1), `:203` (17), `:509` (7), `:532` (1), `:539` (11), `:553` (1), `:562` (1), `:649` (1), as reported by pytest.

The 13 absent site-source fixture paths are the exact scope listed next; `tests/quality/conftest.py:22` through `:26` maps `/site/<suffix>` to `tests/fixtures/hg_migration_site/<suffix>`. These are repository-local optional mirrors, distinct from probing absolute `/site` paths in B. Each is 1 skipped instance except `dataset-source-reviews-b2.md` (3):

- `tests/fixtures/hg_migration_site/dataset-reviews/fever.md`

- `tests/fixtures/hg_migration_site/dataset-reviews/physicsquestions.md`

- `tests/fixtures/hg_migration_site/dataset-reviews/reasoning_gym.md`

- `tests/fixtures/hg_migration_site/dataset-source-reviews-b2.md`

- `tests/fixtures/hg_migration_site/agentdojo-metadata-privacy-codex180-report.md`

- `tests/fixtures/hg_migration_site/runtime-blockers-b7.md`

- `tests/fixtures/hg_migration_site/jericho-runtime-b7.json`

- `tests/fixtures/hg_migration_site/scienceworld-runtime-b7.json`

- `tests/fixtures/hg_migration_site/independent-review-deferred.md`

- `tests/fixtures/hg_migration_site/w-shared-verifier-review.md`

- `tests/fixtures/hg_migration_site/w-obs-runtime-review.md`

- `tests/fixtures/hg_migration_site/b6-dataset-blocker-review.md`

- `tests/fixtures/hg_migration_site/dataset-blockers.md`

The mandatory standalone checker did **not** report valid on this fresh worktree. Exact command `python3 tools/check_dataset_blockers.py`, exit 2, exact output:

```json
{"valid": false, "error": "bfcl_v3: missing evidence tests/fixtures/hg_bfcl/README.md"}
```

The checker does not share pytest’s skip fixture and requires each repository evidence file (`tools/check_dataset_blockers.py:118`). This audit-only diff cannot repair missing observation packets. Achieving `valid: true` here would require the parent to provision authentic missing evidence; no such evidence is fabricated and no checker/registry rule is relaxed.

## D. Reverse audit

Reproducible search scope: all **925 tracked files** from `git ls-files tests tools eval docs`, fully enumerated in validation. Search command:

```sh
git grep -n -I -E 'shared_blockers|scorer-offline-closure|artifact-only-state-export|pristine-verifier|runtime-observations|independent-evaluator-source|shared gates|shared blockers' -- tests tools eval docs
```

All matching lines and inspected source excerpts are captured in validation. This covers tracked source and historical fixtures, not ignored/untracked files. Findings below distinguish a reproduced failure from static historical dependencies.

### Active test failure — reproduced

**FOUND:** `tests/quality/test_appworld_trusted_trial_writer_codex183.py:245` through `:247` still requires the two withdrawn gates:

```python
assert set(appworld["shared_blockers"]) == {
        "scorer-offline-closure", "artifact-only-state-export",
    }
```

Exact command, environment and complete failure output are embedded in validation:

```sh
TMPDIR=/mnt/20t/xubuqiang/hg-work/stalepoint/reverse/tmp PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest tests/quality/test_appworld_trusted_trial_writer_codex183.py::test_registry_closes_only_the_saved_writer_blocker -q -p no:cacheprovider --basetemp=/mnt/20t/xubuqiang/hg-work/stalepoint/reverse/pytest
```

Exit 1; final exact output: `1 failed in 0.15s`. Actual set is empty in the assertion diff. This test requires parent migration; no test edit is part of this worker’s proposal.

### Historical packet scripts — static dependencies, not run

- **FOUND:** `tests/fixtures/hg_wresolver5/write_report.py:149` through `:157` searches `scorer-offline-closure`, otherwise raises `AssertionError('Missing shared blocker')`. If that branch is reached with the current empty list it fails. It mutates registry/journal and historical artifacts (`:143`, `:145`, `:158`), so it was not run. Earlier independent failures may occur before this branch; no observed execution is claimed.
- **FOUND:** `tests/fixtures/hg_wresolver5/validate.py:152` through `:158` skips the scorer observation checks when the list is empty, then asserts `registry==boundary['protected_registry']`. That frozen boundary contains the old shared set (see exact boundary-summary command in validation); current empty-list comparison cannot pass if reached. This is a historical snapshot equality check, not production admission. Not run.
- **FOUND:** `tests/fixtures/hg_we6b/audit_packet.py:111` through `:118` requires old dataset/review equality and old/new shared cardinality using `zip(..., strict=True)`. It depends on its frozen baseline; if its frozen baseline has a nonempty shared list and reaches the empty-list zip it cannot complete. Not run; prior receipt/baseline reads and the earlier equality check may fail first.
- `tests/fixtures/hg_we6b/source_inventory.py:17` through `:19` derives participants from `artifact-only-state-export`; current participants are empty. That is consistent with withdrawal, not independently proof of lost dataset coverage. No historical generator or packet was modified/rerun.

### Empty-list-safe paths and bounded negative findings

- `tools/check_dataset_blockers.py:147` through `:152` accepts an empty shared list, and `:168`/`:169` accepts empty per-dataset references. The observed checker failure is missing repository evidence, not empty shared blockers. `tests/quality/conftest.py:37` through `:45` safely concatenates an empty shared-owner list.
- `tests/quality/test_measurement_coverage_hg_b3.py:204`/`:205` and `:210` compare against the live shared set, so neither assertion requires a nonempty set (static review; this file’s tests were not run). `tests/quality/test_dataset_blockers.py:361` has the same empty-list-safe equality, despite its stale docstring.
- **ABSENT in enumerated tracked `eval/` scope:** both searches below returned exit 1 and no output. This establishes no textual references under these patterns, not that all indirect runtime dependencies are impossible.

```sh
git grep -n -I -E 'shared_blockers|scorer-offline-closure|artifact-only-state-export|pristine-verifier|runtime-observations|independent-evaluator-source|shared gates|shared blockers' -- eval
git grep -n -I -E 'dataset.blockers|dataset_blockers|blocker.*registry|registry.*blocker' -- eval
```

- Tracked `docs/` scope contains only `docs/adapter-integration-journal.md` (enumeration in validation). Earlier “both shared blockers remain open” statements are dated history, e.g. `docs/adapter-integration-journal.md:3192` through `:3199`; the later withdrawal migration is recorded at `:4309`/`:4311` and zero shared blockers at `:4321`. **No active documentation requirement was established** by this search; do not rewrite dated history.
- Outside A’s next_action scope, review notes still retain earlier shared-state prose (`registry/dataset-blockers.json:1051`, `:1052`, `:1054`) with some superseding context at `:1055`; these are historical/additive notes, not a separate proposed registry change.

**UNKNOWN / not verified:** full-suite behavior; indirect dynamically constructed registry references beyond these patterns; ignored/untracked docs/code; execution of historical packet validators/generators; actual dataset scorer/runtime/provenance truth beyond cited records; freshness/existence/hash verification of w-sel payloads outside git. No GPU, server, model/API endpoint, benchmark diagnostic or historical run was used. Review should especially challenge preservation of dataset-local future-diagnostic obligations when removing generic shared language.
