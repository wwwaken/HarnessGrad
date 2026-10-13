# Adapter Integration Journal

This is the repository record of what each dataset taught the platform.

An adapter is not complete when it loads. It is complete when its scorer, runtime, split, evidence, privacy and resource boundaries are understood and recorded. Every new adapter entry must link the evidence artifacts, the platform change, the validation command and the commit that carries the change.

## Entry format

```markdown
## Dataset — YYYY-MM-DD

- Status: `preflight` | `pilot` | `complete` | `blocked` | `incomplete`
- Scope: exact pool, split, pilot size and trial protocol
- Finding: what the dataset exposed
- Evidence: files, tests, controls or run IDs
- Platform change: reusable capability added or corrected
- Remaining gates: unresolved decisions or runtime requirements
- Validation: exact commands and results
- Commit: commit or `uncommitted artifact`
```

Do not record a partial score as a complete result. Use `incomplete` when execution stopped, timed out before measurement, or crossed a platform-integrity boundary. Keep diagnostic numbers separate from archive effects.

## GSM8K — scorer contract

- Status: `complete` history; scorer correction pending new-run validation
- Scope: published `train`/`test` split; old H0 records use the scorer identity recorded at their run time
- Finding: the inherited integer-only flexible extractor turns `3.5` into `5` and `18.0` into `0`, while the task contract accepts decimal forms
- Evidence: `data/gsm8k.py`; `tests/quality/test_gsm8k_official_scorer.py`; 18 focused tests passed after the decimal-aware change
- Platform change: scorer identity must be explicit in evidence; decimal-aware extraction is now the current adapter contract and is not silently substituted into old archive records
- Remaining gates: rerun any GSM8K comparison under the new scorer identity before comparing it with old curves
- Commit: `d10b387 platform: cap early pilots and parse GSM8K decimals`

## ALFWorld — embodied runtime

- Status: `complete` H0 archive
- Scope: 9 train-side pilot tasks, 3 trials, `jobs=1`
- Finding: task-level action limits, TextWorld assets and verifier state must be checked before measuring a curve
- Evidence: `/tmp/codex/alfworld-oracle-control.log`; `/tmp/codex/alfworld-noop-control.log`; run `alfworld-h0-10pct-v4`
- Platform change: files sandbox, explicit action budget, structured task events and immutable artifact hashing became required evidence
- Remaining gates: do not rerun the completed generation without a new protocol
- Commit: archive record in `/tmp/codex/qa-h0-archive-v4/index.json`

## Bird MiniDev — SQL measurement

- Status: `complete` H0 archive for v5; v4 is `incomplete`
- Scope: v5 planned 34 train-side tasks × 3 trials, `jobs=1`; only 28/34 tasks were measured (90 verify phases). The historical archive label `complete` does not certify full measurement coverage.
- Finding: a SQL verifier can distinguish a wrong query from an environment that cannot open `database.sqlite`; measured-zero and unmeasured must remain separate
- Evidence: `bird-minidev-h0-10pct-v5`; v5 score `0.3214285714`; v4 stalled and remains incomplete
- Platform change: structured verifier evidence and `effect=null` incomplete records are mandatory
- Remaining gates: preserve SQL engine errors and schema errors in per-task evidence
- Commit: archive record in `/tmp/codex/qa-h0-archive-v4/index.json`

## DS1000 — host slice and timeout evidence

- Status: final curve pending archive review
- Scope: 61-task train-side pilot from the adapter's 926/1000 host slice, 3 trials
- Finding: host availability is not full benchmark coverage; one task timeout cannot be relabeled as an ordinary wrong answer
- Evidence: `/tmp/codex/61/report.md`; run `ds1000-h0-10pct-v4`; score `0.2076502732`
- Platform change: archive records carry source-pool coverage and task-level timeout evidence
- Remaining gates: append only after verifying all sample IDs, trial coverage and timeout classification
- Commit: archive not yet appended

## ScienceWorld — platform integrity

- Status: `incomplete` despite 354/354 task-trials completing
- Scope: 118 train-side tasks, 3 trials
- Finding: a platform content mismatch invalidates the run-level integrity claim even when every task has a verifier score. The error message `harness modified the platform` does not establish who wrote the changed files; concurrent developer changes are an alternative cause.
- Evidence: final event note in `scienceworld-h0-10pct-v4/events.jsonl`; diagnostic mean `0.1380508475` is for human inspection only
- Platform change: sandbox/mount integrity must prevent writes before execution; end-of-run hashing alone is too late
- Remaining gates: apply and review the isolated integrity patch, then rerun a capped pilot before any full sample
- Commit: patch candidate in `/tmp/codex/81/patch.diff`; not merged

## HotpotQA — structured evidence and time budget

- Status: `incomplete`, user-stopped
- Scope: 492 train-side tasks were mistakenly too large for the time budget; 94/1476 task-trials completed
- Finding: complex evidence tasks can spend 60 minutes on one task; malformed `predicted_evidence` is a schema failure, not a normal wrong answer
- Evidence: `/tmp/codex/qa-h0-incomplete-index.json`; console timeout and schema-error lines
- Platform change: early capped pilots; separate timeout, invalid and measured-zero states; evidence schema validation
- Remaining gates: do not rerun the old full-size protocol; use the capped pilot default and a repaired scorer boundary
- Commit: incomplete record only

## MuSiQue — answer/support evaluation fidelity — 2026-10-13

- Status: `scorer_repaired`, synthetic validation complete; no model/H0
- Scope: MuSiQue-Ans dev adapter; structured answer plus public support citations; explicit legacy answer-only mode retained
- Finding: prior reward measured Answer F1 only. Default structured scoring now reports Answer F1, Answer EM, Support F1/EM and a labeled platform joint policy; missing support yields zero support, and trusted evidence is verifier-only
- Evidence: `data/musique.py`; `docs/musique-output-contract.md`; public pinned evaluator fixtures; combined scorer validation
- Platform change: structured QA evidence transport and redacted verifier gold support
- Validation: combined MuSiQue/2Wiki/Chess suites passed `209 tests`; platform train-side controls: MuSiQue `musique/dev/0` oracle=1.0/noop=0.0; 2Wiki `twowikimultihopqa/dev/3` oracle=1.0/noop=0.0
- Remaining gates: released-data controls and model/H0 validation remain separate; platform joint reward is not an official single leaderboard column
- Commit: `4d41a4c fix: restore MuSiQue and 2Wiki evaluation fidelity`


- Status: `scorer_repaired`, synthetic validation complete; no model/H0
- Scope: this adapter's public output contract, trusted gold transport and official v1.1 scoring; fabricated fixtures only, no released dev/train/test, heldout payload, alias-table or mirror reads
- Finding: the inherited adapter rewarded answers alone despite the official answer, supporting-sentence, evidence-triple and Joint metrics. Structured submissions now report all 16 metrics and earn Joint F1, with Joint EM correctness. Joint precision/recall multiply the three component values before the harmonic mean; multiplying component F1s is different.
- Public contract: JSON in `answer.txt`, submitted directly or with `python3 qa/bin/qa submit @submission.json`: `{"schema_version":1,"answer":"...","supporting_facts":[["Title",0]],"evidence":[["subject","relation","object"]]}`. Context sentences display zero-based indices. Each channel can be omitted; omitted metrics and Joint are zero. Explicit empty sets retain upstream semantics. Plain text and `score_answer_only` remain explicitly labeled `legacy_answer_only`, with Ans F1 reward and no Sup/Evi/Joint claim. This adapter uses the existing text-file transport; shared `submit-json` remains the pair-only schema.
- Evidence: `data/twowikimultihopqa.py`; `tests/quality/test_twowikimultihopqa_structured.py`; updated legacy assertion in `tests/quality/test_twowikimultihopqa_official_scorer.py`
- Platform change: adapter-scoped `score_prediction`, validation and `evaluate_predictions`; trusted inline support/triples plus relevant subject/object aliases, with alias products expanded per scored row. Inputs remain immutable. Aggregate percentages sum in gold order, divide by the entire gold pool including missing predictions, then round once to two decimals. No shared scaffold or other adapter changed.
- Differential coverage: Counter-based duplicate answer tokens; support deduplication/title casing and sentence indices; triple order, punctuation/whitespace normalization, aliases/demonyms and duplicate triples; independently maximized answer precision/recall; multiplicative Joint precision/recall; each missing channel, absent prediction rows and ignored extra ids; explicit empty sets; malformed contracts; trusted-gold privacy; CLI-to-materialized-verifier full/partial/legacy/noop/error controls. Preserve upstream's pre-normalization support deduplication and evidence-alias recall-above-100% quirks without clipping.
- Validation: `python3 -m pytest -q tests/quality/test_twowikimultihopqa_structured.py tests/quality/test_twowikimultihopqa_official_scorer.py::test_legacy_answer_only_is_labeled_and_does_not_claim_joint --basetemp=.scratch/twowiki/pytest` — 40 passed. Synthetic tests suppress shared QASpec pool construction before both parent and verifier-child imports, so no provisioned payload is accessed. `git diff --check` passed.
- Remaining gates/blockers: no implementation blocker. Fetching the pinned upstream source from GitHub failed with curl exit 35 (connection reset); differential tests therefore execute the existing verbatim file evaluator, whose unchanged region is pinned to pre-patch SHA-256 `e18ccdf4b87d16c30e03a62b1dc9d0906c0b0130ae5eace17885d2a9ea1b13c9`. A fresh independent source-file comparison and released-data controls were not performed; real-data/model/H0 validation is outside this task.
- Commit: this entry is carried by `fix: restore 2WikiMultihopQA structured evaluation fidelity`; exact hash reported with the delivery

## LiveCodeBench — authored references

- Status: preflight-required, no H0
- Scope: 1055 pool tasks; 3 train-side authored references and 4 eval-side references
- Finding: an authored reference proves scorer reachability for one task, not full benchmark coverage
- Evidence: `/tmp/codex/79/report.md`; inert manifest selects `livecodebench/740`
- Platform change: reference coverage, public-only authoring and covered-subset manifests are separate from official benchmark claims
- Remaining gates: train metadata attestation, public-only export, independent review and official test verification
- Commit: inert artifacts only

### LiveCodeBench `/740` executable smoke

- Status: `smoke_passed`, H0 not authorized
- Scope: public `abc360_a` statement, one local-model smoke, external-process scorer variant
- Finding: 7/7 synthetic relay/privacy gates passed; local model smoke measured reward 1.0 with 6/6 tests and one request. The candidate agent stayed network-none and verifier stayed network-none.
- Evidence: `/mnt/20t/xubuqiang/Study/lcb_candidate_evidence/launch.json`; candidate path isolated checkout; production endpoint calls during synthetic validation were zero
- Platform change: agent-only Unix relay with max 4 calls and max 512 requested tokens; candidate/scorer/verdict separation
- Remaining gates: mixed-pool row/index binding remains unverified; scorer path differs from official wrapped-function execution; no H0
- Commit: `e2f9613 fix: harden LCB740 identity and relay admission`
- Verification: 79 focused tests passed; production endpoint/model requests=0; synthetic approved-row fixtures never became real evidence

### BFCL selected-only/privacy patch

- Status: `patch_integrated`, real controls blocked by unprovisioned release
- Scope: selected `simple/<index>` and `irrelevance/<index>` category loaders; no import-time mixed-pool read
- Finding: selected loader removes import-time mixed-pool reads; irrelevance empty/NONE semantics remain reward=1; trusted expected functions are redacted; generic noop expectation is category-aware
- Evidence: `/tmp/codex/98/bfcl-selected-only-receipt.md`; isolated 2 synthetic tests passed/11 release-dependent skipped; main compatibility run `147 passed, 23 skipped`
- Platform change: `load_selected`, `setup_for`, `verify_for`, category-aware controls and BFCL-specific evidence redaction
- Remaining gates: local BFCL v1.3 release is unprovisioned, so selected reference identity and real oracle/noop controls remain unproven; no H0
- Commit: `c08c8a1 fix: make BFCL controls selected-only and redact gold`

## AppWorld / GAIA / tau-bench — local state boundaries

- Status: preflight-required, no H0
- Scope: AppWorld reference-covered train subset; GAIA validation-only pool; tau-bench returned local pool
- Finding: service reset, database state, attachments, web access and evaluator secrecy cannot be inferred from adapter loadability
- Evidence: `/tmp/codex/86/report.md`; `/tmp/codex/87/report.md`; inert manifests
- Platform change: one shared lifecycle for scope, admission, restore, readiness, execution, quiescence, scoring, sealing and cleanup
- Remaining gates: real local controls after shared runtime repair; no fallback simulator or hidden web access
- Commit: inert artifacts only

### GAIA V2 real-model pilot attempt

- Status: `incomplete`, infrastructure-stopped
- Scope: 17-task validation-only pilot, 3 trials, `jobs=1`, GPU1/8002, frozen source `92f6b10`
- Finding: the first smoke exposed UTF-8 subprocess decoding; after the isolated fix, smoke reached the model and verifier normally. The pilot then stopped on `gaia/49` after an API timeout; partial trials are evidence of a stopped run, not a complete curve.
- Evidence: `/mnt/20t/xubuqiang/Study/gaia-h0-launch-v2/runs/gaia-validation-pilot-h0-20261117-v2`; sealed receipt `/mnt/20t/xubuqiang/Study/gaia-h0-launch-v2-evidence/GAIA_H0_V2_RECEIPT.json` reports 9 completed trial traces, 45 calls, 47,511 input and 3,219 output tokens. Event envelopes contain 10 done events, including `gaia/53`; this count differs from the persisted trace/usage receipt and must not be silently reconciled as full coverage. Timed-out request usage is unknown.
- Platform change: subprocess output decoding must tolerate arbitrary bytes; a per-request output cap is needed because steps/context limits do not bound one generation. Preserve measured scorer zero separately from actor failure.
- Remaining gates: enforce a bounded model output/token policy before another GAIA pilot; reconcile event versus persisted trial coverage; do not resume this run ID
- Commit: isolated harness fix `92f6b10`; pilot is incomplete and sealed

### GAIA V3 real-model pilot attempt

- Status: `incomplete`, infrastructure-stopped
- Scope: same 17-task validation-only pilot, 3 trials, `jobs=1`, GPU1/8002, source `cde983ff` with output cap `2048`
- Finding: 11 trials completed normally; `gaia/49` third trial reached agent completion at 228.6s, then its snapshot container exited 137 before verification. No aggregate score is valid.
- Evidence: `/mnt/20t/xubuqiang/Study/gaia-h0-launch-v3/runs/gaia-validation-pilot-h0-20261117-v3/events.jsonl`; `gaia/16`, `gaia/32`, `gaia/45` completed 3/3; `gaia/49` completed 2/3; owned interrupted resource was removed
- Platform change: snapshot/container exit codes must become explicit infrastructure outcomes; a task reaching agent completion does not imply a scorable attempt
- Remaining gates: determine why snapshot exits 137 and add resource/snapshot admission before any retry; never resume this run ID
- Commit: source `cde983ff`; pilot incomplete

## AppWorld — scoped train controls

- Status: `controls_passed`, H0 not launched
- Scope: 90 declared train/reference-covered tasks; deterministic pilot selects 9; 18 no-model controls cover 9 oracle and 9 noop arms
- Finding: full-pool import was unsafe for selected-only execution; a pinned train manifest and single-task sanitized controller fixed the boundary. Actor sees no ground truth, services use network none, images are pinned and pull=never.
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-appworld-controls-20261117/deliverables/appworld-offline-v2-report.md`; receipt SHA-256 `f62b8a830c31a889bfe44346c4084055f867b292ce49fb775b7beed19d0900fb`; frozen commit `d600378`
- Platform change: selected-only manifest custody, fresh actor/verifier state, owned labels, and cleanup receipts are reusable adapter controls
- Remaining gates: real-model smoke and production launch record on a frozen checkout before 9x3 H0
- Commit: `d600378 adapter: scope AppWorld to pinned train manifest`

### AppWorld real-model smoke blocker

- Status: `incomplete`, infrastructure repaired; actor protocol still blocked
- Scope: fresh one-task smoke on `07b42fd_1`, one trial, jobs=1, GPU1/8002, bounded generation 2048
- Finding: the original actor never started because the runner mounted the dependency overlay twice and Docker rejected the launch with exit 125. A second client bug passed unsupported argparse `choices`; the service image also now has an explicit `/usr/local/bin/appworld-server` command. After repair, the actor ran 8 model calls, service initialize returned 200, three execute requests returned 200, and the API-call log existed. The model still made zero AppWorld API calls, so the measured smoke score was 0.0 across 5 checks; this is actor/task protocol behavior, not a missing-log infrastructure failure.
- Evidence: `/tmp/codex/101/deliverables/receipt.md`; `/tmp/codex/101/evidence/real-smoke/result.json`; `/mnt/20t/xubuqiang/Study/appworld-smoke-final-v4/runs/appworld-smoke-final-20261117-v4/events.jsonl`; fixed patch commit `a9e78d8`
- Platform change: explicit service command/entrypoint contract, duplicate overlay prevention, AppWorld CLI dispatch fix, service log preservation and invalid diagnostic trace retention
- Verification: 107 focused tests passed; a broader registry/scorer command exceeded the 120s command cap and was terminated, so it is not counted as passed
- Remaining gates: make the task-facing harness reliably issue an AppWorld API action without method-specific tuning, rerun one measured smoke with a nonempty API log, then launch 9x3 only after review
- Commit: `a9e78d8 fix: make AppWorld service and runner diagnostics explicit`

### AppWorld runtime tool protocol repair

- Status: `protocol_repaired`, H0 not launched
- Scope: public `SETUP.runtime_prompt` on train task `07b42fd_1`; unchanged generic `base_harness/loop`; one live smoke on GPU1/8002
- Finding: the prompt now teaches the adapter-declared `./aw init/action` contract, persistent `apis` namespace, documentation discovery, and action persistence without embedding a task answer or verifier data. The model made 4 authoritative calls: 3 documentation reads and `GET /spotify/artists`.
- Evidence: `/tmp/codex/104/receipt/appworld-actor-protocol/receipt.json`; bundle SHA-256 `2ca5b8d1bf4508a93934c5b4005b509d35f49d3cbe73dfcc7ffe35978a8b1100`; patch SHA-256 `955d892d023062f46a3b8535e5b808d2ae4a2b46a3e1f773b2daeb8c81b18803`
- Verification: 63 focused tests passed; service initialized and returned 200 for all four execute requests; actor had no recording mount; cleanup had no owned containers/networks; measured verifier score remained 0.0 because the model did not submit a completed answer and later produced parse failures
- Platform change: adapter-scoped public runtime prompt contract, validated and delivered through files, exec mount, and container-state paths; no base harness branch or task-specific answer logic
- Remaining gates: improve generic action-loop robustness for long API results and shell quoting, then rerun one task to a completed measured answer; do not launch 9x3 from this unsolved smoke
- Commit: `87c6fc9 fix: provide adapter runtime tool instructions`

### AppWorld generic loop robustness repair

- Status: `protocol_partially_verified`, H0 not launched
- Scope: unchanged generic loop actor, one train task `07b42fd_1`, GPU1/8002, 8 steps, 2048 output tokens, jobs=1
- Finding: the actor now selects an explicit shell and tells the model whether Bash or POSIX syntax is available; structured JSON/list output is compacted with complete-record previews and exact full output saved separately; parser retries discard failed long replies from active context and request short actions. The smoke completed all 8 commands with no shell or parse error and recorded 7 API calls, but remained in API documentation discovery and made no state-changing call or final submission.
- Evidence: `/tmp/codex/105/receipt/loop-robustness/smoke-receipt.json`; tests `20 new robustness + 62 existing focused = 82 passed`; patch isolated commit `77c573fa91f57ee6f1fe54c2497436baecddff99`
- Platform change: generic shell dialect identity, lossless structured-output preview, persisted exact output, robust block parser and bounded parse-retry context
- Remaining gates: get one generic loop smoke to complete a real task-facing state change and measured answer; no method/task-specific hardcoding; no 9x3 yet
- Commit: `df8beec fix: harden generic loop shell output and parse recovery`

### AppWorld sixteen-step smoke

- Status: `measured_smoke`, H0 not launched
- Scope: declared AppWorld split `147 train / 585 eval`, selected train task `07b42fd_1`, one trial, jobs=1, GPU1/8002, `max_steps=16`, `max_output_tokens=2048`
- Finding: actor completed normally in 41s and produced 15 authoritative API calls; verifier returned `measured=true`, score `0.0`. The earlier smoke split file covered only a partial manifest and was rejected before execution; this smoke used the complete declared split.
- Evidence: `/mnt/20t/xubuqiang/Study/appworld-smoke-final-v6/runs/appworld-smoke-final-v6-20261117/events.jsonl`; progress record reports `complete=true`, `n_trials=1`, `trial_scores=[0.0]`; API log is 1507 bytes with 15 calls
- Platform change: complete split admission is now verified separately from selected task execution; no payload or heldout task content was needed to build the split metadata
- Remaining gates: a successful measured actor task remains required before 9x3; do not convert this measured zero into a full pilot
- Commit: runtime evidence only

### AppWorld thirty-two-step smoke

- Status: `measured_smoke`, H0 not launched
- Scope: declared split `147 train / 585 eval`, selected train task `07b42fd_1`, one trial, jobs=1, GPU1/8002, `max_steps=32`, `max_output_tokens=2048`
- Finding: actor completed normally in 57s and produced 26 authoritative API calls; verifier returned measured score `0.0`. The runtime remained healthy with no infrastructure invalidation, but the model still did not complete the task. Increasing the step ceiling did not close the task gate.
- Evidence: `/mnt/20t/xubuqiang/Study/appworld-smoke-final-v7/runs/appworld-smoke-final-v7-20261117/events.jsonl`; progress record reports `complete=true`, `n_trials=1`, `trial_scores=[0.0]`; API log is 2638 bytes with 26 calls
- Decision: do not keep increasing the budget or tune the method to this task. AppWorld has stable platform/scorer protocol but no successful measured task smoke, so 9x3 remains unauthorized
- Commit: runtime evidence only

## Jericho — runtime boundary repair

- Status: `controls_passed`, model H0 still blocked
- Scope: two selected train study games (`905`, `acorncourt`), local/platform oracle/noop controls remain 16/16; no heldout or model execution
- Finding: the prior runtime exposed reference-bearing `game_info.py` walkthroughs, ignored declared timeout limits, reused action logs, and did not enforce native network isolation. The repaired path projects only public Jericho code/native library, strips reference bindings/walkthroughs/docs/bytecode, uses explicit 300s agent/verifier bounds, fresh logs, and refuses live agents under `network=none` before staging
- Evidence: `/tmp/codex/109/worktree/report.md`; merged commit `28eebef`; 59 focused boundary/admission tests passed, 7 unrelated production/data cases deselected
- Platform change: allowlisted agent runtime projection, runtime policy admission, explicit phase timeout minimum, no-egress sandbox and fresh log reset
- Remaining gates: production ROM controls must run from a work root outside the platform checkout; interactive model H0 remains blocked until that path is independently exercised
- Commit: `28eebef Repair Jericho agent runtime isolation and phase boundaries`

## BFCL v3 — scorer/privacy controls

- Status: `blocked`, no real controls
- Scope: 2 inert reference anchors (`simple/29`, `irrelevance/236`), 8 planned control arms
- Finding: importing the adapter reads mixed train/eval files; irrelevance correctly treats empty output as success, so generic noop=0 is invalid
- Evidence: `/tmp/codex/89/manifest.inert.json`; 32 synthetic/privacy tests; scoped lazy-import patch hash `ed45acc026a036be46b2ab48d7dbe79504f68b2d7c135e942dde71b109e9bc56`
- Remaining gates: train-only source binding, category-aware controls, raw evidence redaction, finite reward/unmeasured classifier
- Commit: inert patch only

## Terminal-Bench — cached pilot admission controls

- Status: `admission_hardened`, benchmark execution blocked
- Scope: inherited six cached train images, jobs=1; synthetic local runtime controls only
- Finding: admission now rejects empty device observations, negative reservations, unsafe mount flags, runtime-envelope mismatches before start, image-ID mismatches, and ambiguous cleanup absence; leases quarantine on uncertainty and retain capacity
- Evidence: `/tmp/codex/111/report.md`; isolated review tests 47 passed/6 expected failures; merged implementation commit `b3e5409`
- Platform change: manifest-bound resource ledger, exact image pin checks, fixed no-network/no-pull runtime, fail-closed cleanup and trusted artifact mount
- Remaining gates: each scorer still lacks verified offline dependency closure/trusted runtime/state export; benchmark disk/inode quotas are not enforced; no official benchmark execution
- Commit: `b3e5409 fix: harden cached pilot admission boundaries`

## AgentDojo — selected-only split controls

- Status: `controls_passed`, production H0 not launched
- Scope: pinned runtime registry 949 pairs; 615 train / 334 eval across 97 user groups; selected 4 complete train groups, 35 pairs, 70 oracle/noop arms
- Finding: targeted `control_task(task_id)` now reads only `prepared/<id>/case.json`; `ENV`, `SETUP`, `VERIFY` use fixed metadata maps without importing the mixed prompt catalog. Explicit task IDs are required before any targeted control read. User-group split remains suite/user based with zero cross-side overlap.
- Evidence: `/tmp/codex/97/evidence/summary.json`; 70 measured controls, 35 oracle=1, 35 noop=0, attacker_success=0; no mixed catalog/heldout payload opened
- Verification: 20 focused/official/bridge tests passed on main
- Platform change: selected-only adapter control hook and explicit-ID enforcement
- Remaining gates: full mixed-catalog-to-registry alignment is intentionally unattested because `cases.json` remains unopened; no model H0 or platform run_one claim
- Commit: `80bc61f fix: make AgentDojo controls selected-only`

## ChessBench Puzzles — strict replay and public stepwise contract — 2026-10-13

- Status: `complete` synthetic scorer/contract repair; interactive official accuracy remains unmeasured
- Scope: ChessBench Puzzles adapter only, pinned upstream revision `90ae0e6b121673fc3079aaeffa047580bb600c0a`; fabricated boards and reference lines only. No model/H0, release controls, heldout puzzle payload reads, or changes to other adapters.
- Finding: official puzzle accuracy requests one move per observed board, then updates the board with reference opponent responses. The inherited one-shot sequence contract cannot attest those observations. `python-chess` `Board.push()` does not enforce legality: an impossible exact-reference pawn move can receive upstream reward 1.0; strict replay returns 0.0 with `illegal_move` on that synthetic case.
- Evidence: [contract and boundary](chessbench-puzzles-evaluation.md); [strict replay/session tests](../tests/quality/test_chessbench_puzzles_strict_replay.py); [verbatim upstream synthetic differential tests](../tests/quality/test_chessbench_puzzles_official_scorer.py); materialized-verifier diagnostics and shared QA rematerialization checks use synthetic gold exclusively.
- Platform change: default reward is `ChessBench strict legal puzzle replay v1`; preserved upstream unchecked-push reward is diagnostic-only in `official.upstream`, with strict details in `official.strict`. Setup, solver and applied reference opponent moves are legality-checked; malformed/illegal/wrong/missing moves have explicit verdicts; exact and alternate legal early mates terminate immediately. The trusted `StepwisePuzzle` contract exposes only current FEN, solver-turn number, contract, status and verdict, accepts exactly one UCI answer, and applies private opponent updates before the next decision. Adapter import is lazy and verifier evidence redacts gold. The shared QA contract test now honors declared evidence redaction; no shared runner or other adapter implementation changed.
- Remaining gates: no blocker to this patch. A trusted runner transport must deliver successive public observations before actor decisions to claim interactive official puzzle accuracy; the current QA runner remains explicitly offline. Release-pool replay, source-archive drift checks and real controls are intentionally unvalidated under the no-heldout/no-model scope, rather than inferred from synthetic success.
- Validation: `python3 -m pytest -q tests/quality/test_chessbench_puzzles_strict_replay.py tests/quality/test_chessbench_puzzles_official_scorer.py::test_synthetic_upstream_diagnostic_matches_verbatim tests/quality/test_chessbench_puzzles_official_scorer.py::test_alternate_mate_and_nonmate_against_official_function --basetemp=/tmp/codex/108/worktree/.chessbench-test-tmp` → **42 passed in 0.49s**. `git diff --cached --check` passed before the implementation commit. Owned temporary test files were removed after validation.
- Commit: `d8d44a6 fix: enforce ChessBench puzzle replay legality and define stepwise contract`
- Validation: platform train-side control `chessbench_puzzles/test/0` oracle=1.0/noop=0.0; strict replay passed 42 focused tests

## Process rule

Before launching any new adapter, add or update its entry here and add the corresponding platform capability to `docs/platform-improvement-log.md`. The launch review must cite the entry, the exact manifest hash and the runtime gate receipt.
