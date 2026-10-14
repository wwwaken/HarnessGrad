# Adapter Integration Journal

This is the repository record of what each dataset taught the platform.

An adapter is not complete when it loads. It is complete when its scorer, runtime, split, evidence, privacy and resource boundaries are understood and recorded. Every new adapter entry must link the evidence artifacts, the platform change, the validation command and the commit that carries the change.

## Staged diagnostic receipt audit — 2026-10-14 — Codex 193

- Status: `preflight`; narrow correctness fixes verified, publication remains blocked by missing trusted observations.
- Scope: isolated `/tmp/hg-codex-193`, base `a58b4b181193a2e2b201c6353722725ad77b597c`; source and authored synthetic tests only; no model/H0, heldout reads, Docker/backend queries or GPU runs.
- Finding: explicit timeout/nonzero exits could appear measured in staged adaptation; fresh receipt directories could still delete old workspace evidence and reap stale resources; schema allowed passing summaries with null hashes that Python refused.
- Platform change: staged adapter checks explicit exit results; staged workspace identities reserve exclusively and refuse old evidence; fresh staged runs skip legacy reaping; schema requires hashes for all passing summaries.
- Evidence: [exact audit and retained gaps](../staged-receipt-audit-codex193-report.md), `tests/quality/test_staged_receipt_audit_codex193.py`, [captured test result](../staged-receipt-audit-codex193-test-result.txt).
- Failure persistence: plans survive post-write preparation failures and evaluation exceptions; returned outcomes produce a separate final receipt; exceptions do not guarantee a final failure receipt. Exclusive writes are not crash-atomic/fsynced.
- Remaining gates: driver has no lifecycle producer; backend admission/quiescence/snapshot/cleanup observations, provenance verification, selected-only/scorer closure, provisional progress publication integration and global ownership/concurrency remain unresolved.
- Validation: **479 passed**, no failures/skips, six focused synthetic suites; exact command in the report; `git diff --check` passed. Synthetic lifecycle success is not production authorization.
- Commit: carried by this worktree's scoped receipt-correctness change; no main merge.

## Shared lifecycle publication gate — 2026-10-14 — Codex 177

- Status: `preflight`; shared offline contract implemented, trusted backend observations pending
- Scope: isolated `/tmp/hg-codex-177`, base `e7acaa1`; code/schema and authored synthetic tests only; no dataset, model/H0, Docker or GPU execution
- Finding: staged receipts and curves could expose measured scores while cleanup/snapshot attestations were unknown; snapshot preflight and best-effort removal cannot prove lifecycle completion
- Evidence: [lifecycle review](../lifecycle-codex177-report.md), `eval/lifecycle_receipt.py`, `tests/quality/test_lifecycle_receipt_codex177.py`, `lifecycle-codex177-test-result.txt`
- Platform change: immutable `scope/admit/execute/quiesce/score/seal/cleanup` checkpoints, shared admission replay, snapshot-worker/completion evidence, failure-only cleanup path, scoped sealed-outcome publication gate, diagnostic v2 and staged curve refusal with unknown evidence
- Remaining gates: independent observer and quota enforcement, snapshot capacity reservation, scorer/artifact linkage and closure, complete cleanup/lease backend, legacy non-staged publication integration; synthetic passes confer no production authorization
- Validation: exact four-suite offline command in the review; **439 passed**, no failures/skips; `git diff --check` passed; production modules do not import synthetic lifecycle fixtures
- Commit: this commit, `fix: gate staged score publication on shared lifecycle receipts`; existing receipts preserved; no main merge

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

## TriviaQA — offline scorer provenance — 2026-10-14

- Status: `blocked` upstream acquisition; docs/tests repair complete, no model/H0
- Scope: fabricated scorer inputs and inert integrity-test bytes only; no released train/validation/test or heldout reads, no network requests
- Finding: the inherited “official” reference was a second local transcription, with no independent scorer commit or source bytes. The Hub dataset revision does not pin the GitHub evaluator; adapter “verbatim” claims remain unverified.
- Evidence: `tests/fixtures/triviaqa_upstream/README.md`; `tests/quality/test_triviaqa_official_scorer.py`; `DOWNLOADS.md` TriviaQA provenance notice; fresh `triviaqa-scorer-provenance-codex157-report.md`
- Platform change: test-only acquisition contract requiring original source/license bytes, a separate immutable commit, reviewed origin/linkage attestation, and SHA-256/Git blob pins. The regular suite skips the upstream differential when fixture is absent; `tools/check_triviaqa_provenance.py` is the explicit nonzero gate and never falls back to a local copy.
- Comparison limits: `rc.nocontext` supplies no documents; validation differs from test evaluation; current reward is alias-max EM only; row-position identity drops question/document grouping. Full upstream grouping, denominator and missing-prediction rules remain unverified. No upstream code or F1 was invented or added.
- Validation: after `mkdir -p .scratch/triviaqa-provenance`, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q tests/quality/test_triviaqa_official_scorer.py --basetemp=.scratch/triviaqa-provenance/pytest` — exit 1, **28 passed / 1 failed**, solely the absent-fixture provenance gate; no skips/errors. Adding `-k 'not test_em_components_match_pinned_upstream_fixture'` and using `--basetemp=.scratch/triviaqa-provenance/pytest-local` — exit 0, **28 passed / 1 deselected**, not upstream certification. `git diff --check` passed.
- Remaining gates: independently acquire and review the original fixture/license/commit linkage, resolve any measured EM drift, then separately verify full evaluator grouping and comparison identity. No production H0 authorization follows from these synthetic checks.
- Commit: carried by `test: fail closed on unacquired TriviaQA scorer provenance`; exact hash reported with delivery

## GSM8K — scorer contract

- Status: `complete` history; scorer correction pending new-run validation
- Scope: published `train`/`test` split; old H0 records use the scorer identity recorded at their run time
- Finding: the inherited integer-only flexible extractor turns `3.5` into `5` and `18.0` into `0`, while the task contract accepts decimal forms
- Evidence: `data/gsm8k.py`; `tests/quality/test_gsm8k_official_scorer.py`; 18 focused tests passed after the decimal-aware change
- Platform change: scorer identity must be explicit in evidence; decimal-aware extraction is now the current adapter contract and is not silently substituted into old archive records
- Remaining gates: rerun any GSM8K comparison under the new scorer identity before comparing it with old curves
- Commit: `d10b387 platform: cap early pilots and parse GSM8K decimals`

## GSM8K — scorer provenance repair — 2026-10-14

- Status: `preflight`; source/test provenance repaired, production validation remains pending
- Scope: source, synthetic scorer/verifier tests and documentation only; no model, H0, released-split reads or archive changes
- Finding: the decimal correction changed both the adapter and the purported original reference. Historical upstream attribution lacked a revision; stale docstrings also claimed upstream float equality, while the adapter uses an exclusive `1e-6` tolerance.
- Evidence: immutable `tests/fixtures/gsm8k_original/integer_extractor.json`, pinned to repository commit `f7ab62143108e120914b5ead34ed339d0c785ee9` with fixture SHA-256 `45c73aeb817878b5ba65709f45766f21eb7899182df4eba9a8101e9169d8276b`; `tests/quality/test_gsm8k_official_scorer.py`; `tests/quality/test_gsm8k_dataset.py`
- Platform change: preserved `decimal-aware-extract` behavior and compatibility fields; restored an independent integer-only reference with honest provenance, corrected scorer labels/docstrings and stale evidence assertion, and made focused checks independent of provisioned benchmark data
- Metric protocol: [provenance documentation](gsm8k-scorer-provenance.md) distinguishes the implemented trial-mean from verifier-selected test@N. test@N remains unimplemented; old receipts retain their recorded identities.
- Remaining gates: any production comparison still requires a separate approved diagnostic and matching scorer/protocol provenance. Synthetic test success does not authorize H0.
- Validation: `python -m pytest -q tests/quality/test_gsm8k_official_scorer.py tests/quality/test_gsm8k_dataset.py --basetemp=/tmp/hg-codex-156/.pytest_cache/gsm8k-tmp` — 58 passed; fixtures and subprocess table-reader stubs prevent released-split reads
- Commit: this commit, `fix: repair GSM8K scorer provenance`

## ALFWorld — embodied runtime

- Status: `complete` H0 archive
- Scope: 9 train-side pilot tasks, 3 trials, `jobs=1`
- Finding: task-level action limits, TextWorld assets and verifier state must be checked before measuring a curve
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/alfworld-oracle-control.log`; `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/alfworld-noop-control.log`; run `alfworld-h0-10pct-v4`
- Platform change: files sandbox, explicit action budget, structured task events and immutable artifact hashing became required evidence
- Remaining gates: do not rerun the completed generation without a new protocol
- Commit: archive record in `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/qa-h0-archive-v4/index.json`

## Bird MiniDev — SQL measurement

- Status: `complete` H0 archive for v5; v4 is `incomplete`
- Scope: v5 planned 34 train-side tasks × 3 trials, `jobs=1`; only 28/34 tasks were measured (90 verify phases). The historical archive label `complete` does not certify full measurement coverage.
- Finding: a SQL verifier can distinguish a wrong query from an environment that cannot open `database.sqlite`; measured-zero and unmeasured must remain separate
- Evidence: `bird-minidev-h0-10pct-v5`; v5 score `0.3214285714`; v4 stalled and remains incomplete
- Platform change: structured verifier evidence and `effect=null` incomplete records are mandatory
- Remaining gates: preserve SQL engine errors and schema errors in per-task evidence
- Commit: archive record in `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/qa-h0-archive-v4/index.json`

## DS1000 — host slice and timeout evidence

- Status: final curve pending archive review
- Scope: 61-task train-side pilot from the adapter's 926/1000 host slice, 3 trials
- Finding: host availability is not full benchmark coverage; one task timeout cannot be relabeled as an ordinary wrong answer
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/61/report.md`; run `ds1000-h0-10pct-v4`; score `0.2076502732`
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
- Commit: patch candidate in `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/81/patch.diff`; not merged

## ScienceWorld — prevention source review — 2026-10-14 — Codex 186

- Status: `preflight`; code-solvable `prevent-platform-writes` review closed, current registry status `runtime`
- Scope: isolated `/tmp/hg-codex-186`, base `d21d79d` after `34a472a`; source review, inert synthetic fixtures and registry/journal updates only
- Finding: prevention already exists in `eval/sandbox.py`, the default native `eval/runner.py` launch and `harnessgrad/methods.py` call path. Protected platform paths are hidden before execution; required candidate/method inputs are restored read-only; an unavailable sandbox refuses the call. Explicit unsandboxed execution provides detection only. `34a472a` corrects writer attribution without weakening fatal mismatch detection; it adds no prevention implementation.
- Evidence: [unique review](../scienceworld-platform-writes-codex186-report.md), `tests/quality/test_scienceworld_platform_writes_codex186.py`, `tests/quality/test_scienceworld_integrity_codex181.py`, `tests/quality/test_dataset_blockers.py`
- Platform change: current machine-registry work status changes from `code-solvable` to `runtime`; no production source change. The external Codex 81 candidate remains an unverified historical citation and was not opened or applied.
- Remaining gates: trusted live enforcement, immutable platform provenance and every shared registry gate remain unresolved. Synthetic command construction cannot attest effective mounts or runtime lifecycle, and authorizes no model/H0 execution. Any future authorized run follows the staged AGENTS.md policy with a fresh ID.
- History: the V4 entry above, run `scienceworld-h0-10pct-v4`, 354/354 reported task-trials, diagnostic-only mean and pinned historical registry record remain unchanged; status `incomplete`, `effect=null`, writer unknown.
- Validation: **64 passed**, no failures/skips; registry valid (28 datasets, 8 shared blockers, 11 historical records, production unauthorized); exact offline command in the unique review. No real dataset/JVM/backend/model/H0/GPU execution or production source edits.
- Commit: accompanying `docs: close ScienceWorld prevention code review, retain runtime gate` commit; exact hash reported on delivery

## HotpotQA — structured evidence and time budget

- Status: `incomplete`, user-stopped
- Scope: 492 train-side tasks were mistakenly too large for the time budget; 94/1476 task-trials completed
- Finding: complex evidence tasks can spend 60 minutes on one task; malformed `predicted_evidence` is a schema failure, not a normal wrong answer
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/qa-h0-incomplete-index.json`; console timeout and schema-error lines
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
- Control sweep: Codex 113 measured 18/18 selected controls across the frozen 50-ID manifests: 3 oracle=1.0 and 3 noop=0.0 for each adapter, jobs=1, no model/H0, cleanup complete. Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/113/worktree/runs/no-model-controls-20261013/report.md`
- Pilot result: run `musique-pilot-h0-20261013` completed 50 selected train tasks × 3 trials, jobs=1, 150/150 measured trials, 0 invalid, score `0.12751114`, one task passed, wall-clock `1884.4s`; receipt `/mnt/20t/xubuqiang/Study/musique-pilot-20261013/runs/musique-pilot-h0-20261013/curve.jsonl`
- Remaining gates: released-data controls and model/H0 validation remain separate; platform joint reward is not an official single leaderboard column
- Commit: `4d41a4c fix: restore MuSiQue and 2Wiki evaluation fidelity`
## 2WikiMultihopQA — 2026-10-13 evaluation fidelity

- Status: `scorer_repaired`, synthetic validation complete; no model/H0
- Scope: this adapter's public output contract, trusted gold transport and official v1.1 scoring; fabricated fixtures only, no released dev/train/test, heldout payload, alias-table or mirror reads
- Pilot recovery: the original 50-task pilot had two malformed structured-output invalids. Generic transport repair commit `1f41891` passed 129 focused tests; rerunning `twowikimultihopqa/dev/1589` and `/2501` ×3 produced `invalid=0`, task scores `0.8` and `0.0`. Combined full 50-task score is `0.50383334`; receipt `/mnt/20t/xubuqiang/Study/twowiki-invalid-recovery-20261013/runs/twowiki-invalid-recovery-h0-20261013/curve.jsonl`
- Public contract: JSON in `answer.txt`, submitted directly or with `python3 qa/bin/qa submit @submission.json`: `{"schema_version":1,"answer":"...","supporting_facts":[["Title",0]],"evidence":[["subject","relation","object"]]}`. Context sentences display zero-based indices. Each channel can be omitted; omitted metrics and Joint are zero. Explicit empty sets retain upstream semantics. Plain text and `score_answer_only` remain explicitly labeled `legacy_answer_only`, with Ans F1 reward and no Sup/Evi/Joint claim. This adapter uses the existing text-file transport; shared `submit-json` remains the pair-only schema.
- Evidence: `data/twowikimultihopqa.py`; `tests/quality/test_twowikimultihopqa_structured.py`; updated legacy assertion in `tests/quality/test_twowikimultihopqa_official_scorer.py`
- Platform change: adapter-scoped `score_prediction`, validation and `evaluate_predictions`; trusted inline support/triples plus relevant subject/object aliases, with alias products expanded per scored row. Inputs remain immutable. Aggregate percentages sum in gold order, divide by the entire gold pool including missing predictions, then round once to two decimals. No shared scaffold or other adapter changed.
- Differential coverage: Counter-based duplicate answer tokens; support deduplication/title casing and sentence indices; triple order, punctuation/whitespace normalization, aliases/demonyms and duplicate triples; independently maximized answer precision/recall; multiplicative Joint precision/recall; each missing channel, absent prediction rows and ignored extra ids; explicit empty sets; malformed contracts; trusted-gold privacy; CLI-to-materialized-verifier full/partial/legacy/noop/error controls. Preserve upstream's pre-normalization support deduplication and evidence-alias recall-above-100% quirks without clipping.
- Validation: `python3 -m pytest -q tests/quality/test_twowikimultihopqa_structured.py tests/quality/test_twowikimultihopqa_official_scorer.py::test_legacy_answer_only_is_labeled_and_does_not_claim_joint --basetemp=.scratch/twowiki/pytest` — 40 passed. Synthetic tests suppress shared QASpec pool construction before both parent and verifier-child imports, so no provisioned payload is accessed. `git diff --check` passed.
- Remaining gates/blockers: no implementation blocker. Fetching the pinned upstream source from GitHub failed with curl exit 35 (connection reset); differential tests therefore execute the existing verbatim file evaluator, whose unchanged region is pinned to pre-patch SHA-256 `e18ccdf4b87d16c30e03a62b1dc9d0906c0b0130ae5eace17885d2a9ea1b13c9`. A fresh independent source-file comparison and released-data controls were not performed; real-data/model/H0 validation is outside this task.
- Commit: this entry is carried by `fix: restore 2WikiMultihopQA structured evaluation fidelity`; exact hash reported with the delivery

## Public Qwen3.5-9B baseline comparison — 2026-10-13

- Status: `comparison_archived`, no new benchmark run
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/qwen-baseline/report.md`; sources and local receipt summary beside it
- Public result recovered: Qwen's reviewed Qwen3.5-9B card reports LiveCodeBench v6 `65.6`; the reviewed card has no MuSiQue, 2WikiMultihopQA, GAIA or AppWorld row
- Local results: MuSiQue capped train pilot `0.12751114` over 50 tasks ×3 measured trials; 2Wiki original curve `0.5081597292` has 48 scored tasks and mixed legacy Answer F1/structured Joint F1; GAIA has no aggregate curve; AppWorld has repeated single-task measured zeros; LCB is smoke-only and row/scorer incomparable
- Interpretation: no direct public-versus-local ranking is valid. Local QA/AppWorld caps, prompts, splits and scorer policies differ from public benchmark recipes; Qwen card values are publisher-reported and not independent reproductions
- Commit: evidence archive only


- Status: preflight-required, no H0
- Scope: 1055 pool tasks; 3 train-side authored references and 4 eval-side references
- Finding: an authored reference proves scorer reachability for one task, not full benchmark coverage
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/79/report.md`; inert manifest selects `livecodebench/740`
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

### LiveCodeBench `/740` trusted metadata validation — 2026-10-14

- Status: `validator_hardened`, external row attestation still blocked; no H0
- Evidence: `LCB_GATE.md`; existing public statement and preserved prior inert selection/launch metadata
- Platform change: bounded UTF-8 metadata-only record, canonical independently supplied approval digest, strict JSON constants and custodian validation; pinned row/pool/split checks retained
- Verification: 80 focused identity tests passed; `git diff --check` passed; no network, mixed-pool/heldout payload reads, model calls or H0
- Remaining blocker: no externally custodied, independently approved record binding pinned pool row 740 to `abc360_a`; self-hashes and synthetic fixtures do not establish custody

### BFCL selected-only/privacy patch

- Status: `patch_integrated`, real controls blocked by unprovisioned release
- Scope: selected `simple/<index>` and `irrelevance/<index>` category loaders; no import-time mixed-pool read
- Finding: selected loader removes import-time mixed-pool reads; irrelevance empty/NONE semantics remain reward=1; trusted expected functions are redacted; generic noop expectation is category-aware
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/98/bfcl-selected-only-receipt.md`; isolated 2 synthetic tests passed/11 release-dependent skipped; main compatibility run `147 passed, 23 skipped`
- Platform change: `load_selected`, `setup_for`, `verify_for`, category-aware controls and BFCL-specific evidence redaction
- Remaining gates: local BFCL v1.3 release is unprovisioned, so selected reference identity and real oracle/noop controls remain unproven; no H0
- Commit: `c08c8a1 fix: make BFCL controls selected-only and redact gold`

### BFCL selected-index and failure-path privacy follow-up

- Status: source/privacy regression closure; production release gate remains unverified.
- Scope: `data/bfcl_v3.py`, shared QA controller/verifier, and `tests/quality/test_bfcl_selected.py`; fabricated JSONL/index fixtures and synthetic read guards only.
- Finding: category filtering still read every question and answer row; empty selection fell back to all categories; controls reloaded selected records and the platform path could load the full pool; scorer explanations and pre-import/unmeasured diagnostics could expose trusted gold.
- Change: canonical nonempty selection validation precedes metadata/payload access; a `selected-index.v1.json` declares tag/tarball identity, question identity and exact question/answer byte spans with SHA-256. This index is **not authenticated or independently custodied**; its hashes are corruption checks, not provenance/trust. Selected loading uses bounded unbuffered seeks/reads, preflights all selected spans, reuses file descriptors and detects ordinary changes during load; it has no scan/index-build/full-pool fallback. Controls reuse one selected record; verifier evidence redacts gold on measured and failure paths.
- Validation: focused selected/privacy/read-boundary suite **73 passed** after Codex 171 bounds review; earlier main suite 55 passed. All fixtures are synthetic; no release or external dataset path was read.
- Remaining gates: independent custodian approval of exact metadata-only index bytes and row/split binding; authenticated immutable release storage; pinned official AST/full-call evaluator source and complete argument/reference data. Current scorer remains function-name multiset diagnostic, not official BFCL Simple. No model/H0 or production controls authorized.

## AppWorld / GAIA / tau-bench — local state boundaries

- Status: preflight-required, no H0
- Scope: AppWorld reference-covered train subset; GAIA validation-only pool; tau-bench returned local pool
- Finding: service reset, database state, attachments, web access and evaluator secrecy cannot be inferred from adapter loadability
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/86/report.md`; `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/87/report.md`; inert manifests
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
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/101/deliverables/receipt.md`; `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/101/evidence/real-smoke/result.json`; `/mnt/20t/xubuqiang/Study/appworld-smoke-final-v4/runs/appworld-smoke-final-20261117-v4/events.jsonl`; fixed patch commit `a9e78d8`
- Platform change: explicit service command/entrypoint contract, duplicate overlay prevention, AppWorld CLI dispatch fix, service log preservation and invalid diagnostic trace retention
- Verification: 107 focused tests passed; a broader registry/scorer command exceeded the 120s command cap and was terminated, so it is not counted as passed
- Remaining gates: make the task-facing harness reliably issue an AppWorld API action without method-specific tuning, rerun one measured smoke with a nonempty API log, then launch 9x3 only after review
- Commit: `a9e78d8 fix: make AppWorld service and runner diagnostics explicit`

### AppWorld runtime tool protocol repair

- Status: `protocol_repaired`, H0 not launched
- Scope: public `SETUP.runtime_prompt` on train task `07b42fd_1`; unchanged generic `base_harness/loop`; one live smoke on GPU1/8002
- Finding: the prompt now teaches the adapter-declared `./aw init/action` contract, persistent `apis` namespace, documentation discovery, and action persistence without embedding a task answer or verifier data. The model made 4 authoritative calls: 3 documentation reads and `GET /spotify/artists`.
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/104/receipt/appworld-actor-protocol/receipt.json`; bundle SHA-256 `2ca5b8d1bf4508a93934c5b4005b509d35f49d3cbe73dfcc7ffe35978a8b1100`; patch SHA-256 `955d892d023062f46a3b8535e5b808d2ae4a2b46a3e1f773b2daeb8c81b18803`
- Verification: 63 focused tests passed; service initialized and returned 200 for all four execute requests; actor had no recording mount; cleanup had no owned containers/networks; measured verifier score remained 0.0 because the model did not submit a completed answer and later produced parse failures
- Platform change: adapter-scoped public runtime prompt contract, validated and delivered through files, exec mount, and container-state paths; no base harness branch or task-specific answer logic
- Remaining gates: improve generic action-loop robustness for long API results and shell quoting, then rerun one task to a completed measured answer; do not launch 9x3 from this unsolved smoke
- Commit: `87c6fc9 fix: provide adapter runtime tool instructions`

### AppWorld generic loop robustness repair

- Status: `protocol_partially_verified`, H0 not launched
- Scope: unchanged generic loop actor, one train task `07b42fd_1`, GPU1/8002, 8 steps, 2048 output tokens, jobs=1
- Finding: the actor now selects an explicit shell and tells the model whether Bash or POSIX syntax is available; structured JSON/list output is compacted with complete-record previews and exact full output saved separately; parser retries discard failed long replies from active context and request short actions. The smoke completed all 8 commands with no shell or parse error and recorded 7 API calls, but remained in API documentation discovery and made no state-changing call or final submission.
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/105/receipt/loop-robustness/smoke-receipt.json`; tests `20 new robustness + 62 existing focused = 82 passed`; patch isolated commit `77c573fa91f57ee6f1fe54c2497436baecddff99`
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
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/109/worktree/report.md`; merged commit `28eebef`; 59 focused boundary/admission tests passed, 7 unrelated production/data cases deselected
- Platform change: allowlisted agent runtime projection, runtime policy admission, explicit phase timeout minimum, no-egress sandbox and fresh log reset
- Remaining gates: production ROM controls must run from a work root outside the platform checkout; interactive model H0 remains blocked until that path is independently exercised
- Commit: `28eebef Repair Jericho agent runtime isolation and phase boundaries`

## BFCL v3 — scorer/privacy controls

- Status: `blocked`, no real controls
- Scope: 2 inert reference anchors (`simple/29`, `irrelevance/236`), 8 planned control arms
- Finding: importing the adapter reads mixed train/eval files; irrelevance correctly treats empty output as success, so generic noop=0 is invalid
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/89/manifest.inert.json`; 32 synthetic/privacy tests; scoped lazy-import patch hash `ed45acc026a036be46b2ab48d7dbe79504f68b2d7c135e942dde71b109e9bc56`
- Remaining gates: train-only source binding, category-aware controls, raw evidence redaction, finite reward/unmeasured classifier
- Commit: inert patch only

## Shared runner refusal gate — Codex 163

- Status: `fail_closed_refusal_added`; backend enforcement remains blocked.
- Scope: runner-mediated tasks declaring exec/container, network, CPU/memory/deadline, resource/filesystem, or artifact policies; unknown backend observations refuse before dispatch/cache reuse.
- Change: `eval.runner._refuse_unobserved_policies` returns invalid/unmeasured admission receipts with no score and prevents these declared-policy tasks from reaching a passing verdict without a trusted backend observer. No adapter/caller-provided observation can override the refusal.
- Validation: synthetic early-refusal, cache-preservation and undeclared legacy-files compatibility tests; combined parent suite **263 passed** across runner admission, error paths and trials/unmeasured behavior.
- Limits: undeclared legacy tasks and direct backend/verifier entrypoints remain outside the hook; driver image preflight can occur earlier; no resource/network/quota/cleanup observer is wired, so declared-policy exec/container tasks intentionally remain blocked. This is a refusal boundary, not production admission or a pilot authorization.
- Evidence: `SHARED_ADMISSION_WIRING.md`, `tests/quality/test_shared_admission_wiring_codex163.py`
- Commit: `39883d8 refuse tasks without enforced runtime observations`



- Status: `admission_hardened`, benchmark execution blocked
- Scope: inherited six cached train images, jobs=1; synthetic local runtime controls only
- Finding: admission now rejects empty device observations, negative reservations, unsafe mount flags, runtime-envelope mismatches before start, image-ID mismatches, and ambiguous cleanup absence; leases quarantine on uncertainty and retain capacity
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/112/report.md`; final offline review tests `199 passed`, no real Docker/model/H0/heldout access; merged implementation commit `b3e5409`
- Platform change: manifest-bound resource ledger, exact image pin checks, fixed no-network/no-pull runtime, fail-closed cleanup and trusted artifact mount
- Remaining gates: each scorer still lacks verified offline dependency closure/trusted runtime/state export; benchmark disk/inode quotas are not enforced; no official benchmark execution
- Commit: `b3e5409 fix: harden cached pilot admission boundaries`

### Shared runner admission follow-up — Codex 158

- Status: `isolated_contract`, filesystem enforcement remains a runtime blocker.
- Finding: reservations and snapshot free-space preflight cannot prove byte/inode quota enforcement. Unbounded or incomplete snapshot/resource/cleanup facts must stay unmeasured.
- Platform change: reusable `eval.runner_admission` runtime/network/filesystem/snapshot/cleanup contracts with fresh binding checks, bounded receipts and fail-closed cleanup release; byte-only legacy snapshot admission explicitly reports that no quota is enforced.
- Evidence: `runner-admission-codex-158-report.md`; synthetic observations only, subprocess/socket execution denied in new tests, existing persistent lease regressions retained.
- Remaining gates: real byte/inode enforcement and trusted complete observers, bounded snapshot worker/daemon resources and growth, atomic receipt-to-lease integration, official scorer/offline closure and artifact-only export. The new scorer-bundle validator checks local declared file closure only and is not called by driver/runner/verifier; it does not establish official origin, image ABI, runtime execution or H0 readiness. Passing synthetic receipts authorize no H0.
- Commit: accompanying `platform: add offline runner quota and cleanup admission contracts` commit.

## AgentDojo — selected-only split controls

- Status: `controls_passed`, production H0 not launched
- Scope: pinned runtime registry 949 pairs; 615 train / 334 eval across 97 user groups; selected 4 complete train groups, 35 pairs, 70 oracle/noop arms
- Finding: targeted `control_task(task_id)` now reads only `prepared/<id>/case.json`; `ENV`, `SETUP`, `VERIFY` use fixed metadata maps without importing the mixed prompt catalog. Explicit task IDs are required before any targeted control read. User-group split remains suite/user based with zero cross-side overlap.
- Evidence: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/97/evidence/summary.json`; 70 measured controls, 35 oracle=1, 35 noop=0, attacker_success=0; no mixed catalog/heldout payload opened
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
- Validation: `python3 -m pytest -q tests/quality/test_chessbench_puzzles_strict_replay.py tests/quality/test_chessbench_puzzles_official_scorer.py::test_synthetic_upstream_diagnostic_matches_verbatim tests/quality/test_chessbench_puzzles_official_scorer.py::test_alternate_mate_and_nonmate_against_official_function --basetemp=/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/codex/108/worktree/.chessbench-test-tmp` → **42 passed in 0.49s**. `git diff --cached --check` passed before the implementation commit. Owned temporary test files were removed after validation.
- Commit: `d8d44a6 fix: enforce ChessBench puzzle replay legality and define stepwise contract`
- Validation: platform train-side control `chessbench_puzzles/test/0` oracle=1.0/noop=0.0; strict replay passed 42 focused tests
- Pilot interruption: run `chess-pilot-h0-20261013` is incomplete; 19 task-trials completed, 0 failed envelopes, then events stopped during `chessbench_puzzles/test/1270` trial 2 at agent elapsed 70s. Model services remained healthy and no final task verdict/aggregate curve exists. Preserve this run; do not resume or overwrite its run ID until an independent termination audit identifies the cause
- Recovery result: `chess-pilot-h0-20261013-recovery-01` reached 149/150 task-trials with 0 failed envelopes, then its final `chessbench_puzzles/test/9967` trial remained active past 620s. The parent stopped the driver to protect GPU time; no terminal verdict/curve exists for that last trial. Preserve recovery as incomplete and do not synthesize a 150-trial score or resume the run ID. Future pilots use a smaller diagnostic budget before any 50×3 expansion
- Interruption audit: termination authority is undetermined; receipts show no timeout/failure/cleanup/snapshot closure, and the path was native bwrap/files rather than Docker snapshot. Preserve the original and recovery IDs, receipt hashes and incomplete statuses. Every future attempt must use a genuinely new unique run ID; never resume or overwrite any used run ID, including `chess-pilot-h0-20261013` and `chess-pilot-h0-20261013-recovery-01`. Launch only under a persistent host supervisor after source/H0/split identity checks and the current AGENTS.md gates. Audit: `/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/chess/interruption-audit.md`, SHA-256 `db357459d4160a5058b022ef5483227f8e01629e24cdf528017db5e7d418de4f`


### AppWorld reporting review — Codex 169

- Scope: isolated `/tmp/hg-codex-169`; code review and fabricated receipt/events only. No real AppWorld task payload/run receipt, smoke/H0, model or runtime execution.
- Finding: saved verdicts preserve scorer evidence for TGC and guarded same-trial SGC; current progress drops it and task events lack explicit trial IDs/evidence. Source Test-N/Test-C labels remain declared manifest facts. This metric report cannot certify diagnostic provenance, endpoint, budgets, cleanup or snapshots.
- Change: report schema 2 separates measured/invalid/present-unmeasured/missing cells, preserves task/per-trial nonmeasurement flags, adds `recorded_unmeasured_task_trials` while retaining aggregate nonmeasurement coverage, and explains input/trial/output limits in CLI help.
- Evidence: `appworld-reporting-codex169-report.md`; unique integration tests use current writers and guarded reporting CLI with fabricated inputs exclusively. Live receipt/event measurement integration remains unsupported; no writer or runner format changed.
- Validation: focused reporting/integration suite **30 passed in 0.96s**; diff whitespace check passed. Owned test scratch was removed after validation.
- Commit: merged follow-up `a80f68f`; parent validation 45 passed

## AppWorld reporting receipt integration audit — Codex 169

- Status: saved-verdict reporting supported; progress/events not sufficient for measured TGC/SGC
- Scope: fabricated Console/Reporter/progress/verdict events and guarded report CLI only; no real AppWorld payload, run receipt, smoke, H0, model or service execution
- Finding: current `verdicts/round-N/<task>.json` retains scorer evidence and can produce measured TGC and same-trial SGC with Test-N/Test-C manifest labels. Progress records keep only generic scores/trial means; events lack scorer evidence and explicit trial IDs. They cannot reconstruct TGC or same-trial SGC.
- Evidence: `appworld-reporting-codex169-report.md`, `tests/quality/test_appworld_receipt_integration_codex169.py`
- Validation: fabricated writer/CLI integration tests passed; parent combined suite 45 passed. No runner writer format was changed.
- Remaining gate: persist minimal trusted scorer evidence plus original trial IDs at the trusted writer; establish manifest/run/model/source/lifecycle identity before diagnostic use. Never infer TestTracker success from generic score or event `passed`.

## AgentDojo selected production route reassessment — Codex 164

- Status: `blocked`; no production diagnostic/H0
- Scope: selected-control metadata interfaces only; mixed catalog, prompts, gold/actions, heldout, runtime and external archive were not opened or executed
- Finding: `control_task` selection still routes through command-control and platform QA verifiers; neither offers a verifier-free, non-scoring selected admission receipt. Existing 70 selected oracle/noop controls are historical claims, not a fresh production `run_one` proof.
- Evidence: `agentdojo-reassessment-codex164-report.md`; metadata privacy regression `tests/quality/test_agentdojo_metadata_privacy.py`
- Validation: 3 metadata privacy tests passed. This proves the tested metadata path avoids guarded reads; it does not prove case materialization, trusted attack verifier, runtime, cleanup or measurement.
- Remaining gate: define and independently review a selected-only, non-scoring production admission interface, or provision a coherent trusted attack-evaluation runtime and run approved oracle/noop controls; then run the staged one-task diagnostic. Do not bypass attack scoring with a synthetic verifier.

## GAIA lifecycle wiring audit — Codex 165

- Status: `blocked`; compatibility library is not a lifecycle receipt or runner authorization
- Scope: source/runtime wiring analysis and synthetic tests only; no Docker, model/H0, heldout, or production lifecycle run
- Finding: `eval.gaia_snapshot_attestation` compares supplied frozen source/runtime identities but does not collect/verify historical receipts or enforce a coherent source lock through runner execution. Fresh cleanup/absence, trusted verifier, dependency closure, artifact export and quota/backend observations remain missing.
- Evidence: `GAIA_LIFECYCLE_WIRING.md`
- Required before diagnostic: metadata-only selected manifest, coherent source lock before adapter import, fresh verifier/dependency/image identity, bounded snapshot and artifact export, observed backend limits/network, and verified owned cleanup, all bound in an immutable lifecycle receipt.

## BFCL official call scorer review — Codex 166

- Status: selected-read/privacy hardening complete; official Simple AST metric and index custody blocked
- Finding: current metric compares function-name multisets and drops argument/reference-value alternatives. The selected index and per-row hashes are not externally authenticated; hashes do not establish release identity or confidentiality.
- Evidence: `bfcl-ast-contract-codex166-report.md`; bounded span hardening in `data/bfcl_v3.py`; `tests/quality/test_bfcl_selected.py`
- Validation: 73 selected-span/privacy tests passed. No official release payload, AST scorer, model/H0 or heldout was read/run.
- Remaining gate: obtain pinned code-only official evaluator source and trusted archive/index custodian approval. Then preserve complete selected call/reference info, implement the source-derived AST contract, keep name metric diagnostic-only, and run fresh release-bound controls.

## BFCL Simple AST source acquisition review — Codex 184 — 2026-10-14

- Status: `external`; official full-call AST semantics, independent source acquisition and release/index custody remain blocked. No production H0.
- Scope: local source/registry review and docs/tests only in `/tmp/hg-codex-184`; no external release/archive or heldout reads, download, evaluator execution, model/endpoint calls or production controls.
- Finding: `simple-ast-contract` was classified code-solvable despite its prerequisite of independently acquired official source. The adapter declares gorilla v1.3/archive SHA-256 but provides no locally verified parser/checker/dispatch symbol contract; its function-name multiset diagnostic discards complete reference arguments. Acceptable-value alternatives alone do not make full-call scoring impossible.
- Change: registry status is now `external`, with an exact code-only handoff requirement: independently verified archive/tag/immutable commit/member linkage, original parser/checker/dispatch/helpers/licenses, reviewed closure and a separately approved exact receipt pin. The new test-only gate refuses missing/unpinned/malformed acquisition and checks all declared metadata and inventory before projected source reads; it neither imports nor executes acquired code. Original AST rules and signatures remain unresolved until source review.
- Evidence: [source acquisition contract](../tests/fixtures/bfcl_ast_source/README.md), `tests/quality/test_bfcl_ast_source_contract.py`, `tests/quality/test_bfcl_selected.py`, and the BFCL-specific registry regression in `tests/quality/test_dataset_blockers.py`. No acquired fixture or completed provenance receipt is supplied; simulated approvals and inert bytes occur only in fabricated tests.
- Validation: **164 passed** across those three focused test modules, with plugin autoload/bytecode/cache disabled and scratch files confined to `.scratch/bfcl-codex184`. The initial test invocation failed during temporary-directory setup because its parent was absent; creating that local parent resolved it. The explicit source gate without an approved pin exits **2**, `status=blocked`, `measured=false`, `production_authorized=false`. Registry validation passes with 28 datasets, 8 shared blockers and 11 unchanged historical records.
- Retained boundaries: production adapter/scorer code is unchanged; function-name diagnostic, lazy import, exact selected spans and measured/unmeasured gold redaction regressions pass. Full-call schemas/references and answer syntax still require future source-derived integration. Source integrity cannot establish reviewer authenticity, semantic equivalence, third-party offline closure, index custody or pristine runtime/export/quota/cleanup; all remain independent gates.

## BFCL v1.3/V3 public code provenance — Codex 195 — 2026-10-14

- Status: incomplete code-only candidate acquired; full-call checker/helper/runtime and independent archive/member custody remain `external`. No H0/model run; main worktree and production code are unchanged.
- Evidence: Berkeley's site links to `ShishirPatil/gorilla`; the public lightweight `v1.3` tag points to `ea13468e4423454d0c213704fb87cf7cb3990433`; the official release explicitly labels V3. Seven original source/license/specification files (126,311 bytes) were acquired at that commit with matching Git blob identities and recorded SHA-256/URLs. Apache-2.0 source license is preserved. The declared compressed-archive digest remains unverified; no archive or benchmark task/answer/heldout/external dataset root was accessed.
- Finding: acquired runner uses binary checker validity divided by prediction count, with decoding/format failures in the denominator. Non-live Simple AST aggregates Python, Java and JavaScript category accuracies by arithmetic mean. Complete checker acceptance rules remain unresolved: API rate-limit HTTP 403 blocked checker/helpers; no substitute semantics were invented.
- Artifacts: [unique report](../bfcl-source-provenance-codex195-report.md), [source review](../tests/fixtures/bfcl_ast_source/candidate-codex195/README.md), candidate provenance and exact code-only custodian request alongside unchanged original files. Candidate schema is deliberately inadmissible; no approved receipt pin was generated.
- Validation: 37 existing source-contract tests passed; static source/size/SHA-256/Git-blob/license/symbol audit passed; explicit gate remains blocked (exit 2); candidate schema refusal precedes any projected source read. No upstream evaluator code was imported or executed. Registry, adapter and scorer remain unchanged.

## TriviaQA adapter impact review — Codex 167

- Status: production scorer unchanged; upstream source provenance blocked
- Finding: provenance commits changed tests/docs only; adapter blob and scorer behavior are unchanged. Regular suite reports 28 passed / 1 skipped; explicit `tools/check_triviaqa_provenance.py` exits 2 until acquired source exists.
- Evidence: `TRIVIAQA_ADAPTER_IMPACT.md`; `tests/fixtures/triviaqa_upstream/README.md`
- Remaining gate: independently acquire and review original evaluator bytes/license/commit linkage. This does not certify grouping, F1 or official full evaluator behavior.

## Filesystem quota backend audit — Codex 168

- Status: `documented_blocker`; no production quota authorization.
- Scope: source only in `/tmp/hg-codex-168`, base `10e983fc5fcb006c5afdbce1ef851dad71e953f2`; no mounts, quota operations, Docker queries, dataset/model/H0 or benchmark execution.
- Finding: bwrap/files writable binds and bare tmpfs, Docker exec writable roots/scratch, and host/method workspaces lack a complete paired byte/inode enforcement backend. Inert-control bounded tmpfs is a separate capability; `statvfs`, disk usage, reservations and snapshot preflight cannot close the gap.
- Evidence: [backend audit and exact OS/backend requirements](filesystem-quota-backends.md), [task report](../filesystem-quota-codex168-report.md), [source hashes](../filesystem-quota-codex168-source-evidence.json), [synthetic results](../filesystem-quota-codex168-test-result.txt).
- Validation: 252 existing synthetic runner/artifact tests passed; temporary files stayed in the worktree and were removed. Runtime source and tests are unchanged.
- Remaining work: OS project-quota provisioning or bounded scratch allocation, actual daemon/snapshotter support for paired hard limits, complete trusted observers, admission before staging/writes, snapshot/export bounds and verified cleanup. No capability detector was added without an implemented backend.

## Process rule

Before launching any new adapter, add or update its entry here and add the corresponding platform capability to `docs/platform-improvement-log.md`. The launch review must cite the entry, the exact manifest hash and the runtime gate receipt.


### GAIA frozen source / snapshot compatibility — Codex 151

- Scope: isolated `/tmp/hg-codex-151`, base `8fcdcb80b90f43ab1c76c1f572c5cf70a6504e11`; source/control inspection and synthetic offline regressions only. No dataset/heldout/model/H0 run artifact reads or runtime execution.
- Change: added complete Git-tree/runtime compatibility review with explicit refusal to authorize lifecycle or reuse receipts; repaired snapshot admission handling for negative sizes, missing/relative Docker roots and observation exceptions.
- Validation: 91 focused offline tests passed (88 new, three existing mocked snapshot regressions); runner failures preserve invalid/no-score semantics and attempt owned teardown.
- Evidence: `GAIA_GATE.md` documents observed base metadata, compatibility inputs and remaining measured closure. No local GAIA lifecycle receipt was available; no lifecycle evidence was created.
- Gate: production lifecycle remains BLOCKED pending selected-only provenance, coherent frozen-source controls, trusted verifier/dependencies, artifact export, quota enforcement and verified owned cleanup. Current stdout/exit codes and best-effort removal are insufficient.

## Dataset blocker registry — Codex 178 — 2026-10-14

- Status: `isolated`, source/journal index validated; no execution authorization
- Scope: `/tmp/hg-codex-178`, reviewed base `e7acaa1126c4c63c8ddc338bd9a7f4988f43ffdf`; repository taxonomy, adapter declarations, journal and tracked source-audit documents only. No adapter imports, external receipt/task-payload reads, model/H0, heldout, network, Docker, or main edits.
- Finding: all 28 publishable declarations need coverage, including refused/unprovisioned adapters. Current blocker work and historical run outcomes are independent. Missing dataset-specific journal entries are evidence gaps, not passing gates.
- Evidence: [machine-readable registry](dataset-blockers.json), [format and review limits](dataset-blockers.md), `tools/check_dataset_blockers.py`, `tests/quality/test_dataset_blockers.py`, pinned `tests/fixtures/dataset_blockers/history-codex178.json`.
- Platform change: AST-only coverage validation against existing `CAPABILITY` and `EXERCISES`; eight reusable shared blockers plus dataset-specific families/statuses/evidence/actions. Task `demand x surface` remains separate from harness `exercises`.
- Historical preservation: 11 incomplete/partial/pending-review observations are independently pinned and must remain unchanged; effects remain null. Unknown exact run IDs remain null. External receipts/scores are journal citations, not newly verified facts. Both chess and GAIA interruptions remain separate records.
- Documentation conflicts: the platform log's historical 50-task sizing and the chess audit's already-used recovery-ID advice are explicitly indexed. Current planning follows AGENTS.md; no old receipt or historical paragraph was rewritten.
- Validation: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_dataset_blockers.py` reports valid, 28 datasets, 8 shared blockers, 11 historical records, production_authorized=false. `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider --basetemp=.scratch/blocker-registry-codex178/pytest-final tests/quality/test_dataset_blockers.py` — **45 passed**. Tests deny adapter imports, external file reads, sockets and subprocess execution.
- Remaining gates: this registry records unresolved requirements; it authenticates no external receipt and closes no runtime/scorer/measurement gate. Parent review/merge remains separate.
- Commit: accompanying focused docs/code/tests commit; exact hash reported with delivery.

## AgentDojo selected metadata privacy closure — Codex 180 — 2026-10-14

- Status: code-solvable selected `ENV`/`SETUP`/`VERIFY` metadata privacy/detection review closed; separate production-route admission remains `blocked`.
- Scope: isolated `/tmp/hg-codex-180`, base `e8dd6f62aff3acdc10e92bb8e1cff84075cec3b7`; adapter Python source and synthetic metadata controls only. No adapter/data edits, catalog or `cases.json` reads, prompt/gold/action payload reads, runtime/verifier execution, attacks, model/H0, network or main edits.
- Finding: fixed synthetic metadata keys and selected setup/input path identities require no catalog/task/reference hooks; invalid selections raise `KeyError` with no fallback. Fresh module-body execution uses an inert QA dependency stub under I/O/import guards; it does not validate real dependency imports or production admission.
- Detection: all 13 guarded file/JSON/catalog/task/reference seams are deliberately probed for each of the three metadata maps and stop before underlying reads. Valid/rejected selected lookups record zero guarded attempts; verifier `argv` stays opaque.
- Evidence: [unique focused report](../agentdojo-metadata-privacy-codex180-report.md), `tests/quality/test_agentdojo_metadata_privacy.py`, and the source-only registry boundary regression in `tests/quality/test_dataset_blockers.py`.
- Registry: retired the completed `selected-metadata-review` action from the active list because the schema has no closed status. The separate `production-route-admission` runtime blocker retains Codex 164's production-route evidence and adds this limited metadata closure; global production authorization remains false.
- Validation: **109 passed** (63 metadata controls plus 46 registry regressions). `tools/check_dataset_blockers.py` reports valid, 28 datasets, 8 shared blockers, 11 historical records and `production_authorized=false`.
- Remaining boundary: no production `run_one` or H0 readiness claim, case materialization proof, trusted verifier/runtime receipt, cleanup observation or benchmark measurement. Historical controls remain unverified claims; no route was repaired or executed.
- Commit: focused tests/docs/report on the isolated worktree; parent review and integration remain separate.

## AgentDojo metadata-only provenance reconciliation — Codex 190 — 2026-10-14

- Status: `production-route-admission` remains blocked; no production authorization or registry/code change.
- Scope: isolated `/tmp/hg-codex-190`, base `a58b4b181193a2e2b201c6353722725ad77b597c`; checkout declarations and Git/source metadata only. No external dataset/receipt inspection, cases/prompts/prepared payloads/gold/actions/heldout/runtime binary reads, adapter import, runtime/scorer/network/model/H0, or main edits.
- Finding: inherited `_src/runtime/agent_runtime/prepared` presence claims agree with declared path roles but authenticate no release or selected rows. Adapter and generated `DOWNLOADS.md` agree on commit `089ed468cf3ed0322acc66b0211f26d9d90dbf60` and expected archive SHA-256; package `0.1.35` and suite `v1.2.2` are separate axes. No independent exact-release/selected-group/runtime manifest is available in the checkout.
- Evidence: [unique report](../agentdojo-provenance-codex190-report.md), [scoped metadata/hash record](../agentdojo-provenance-codex190-metadata.json). Git identities and local declaration hashes are freshly computed; external presence, split counts and historical controls remain inherited, unverified claims.
- Remaining gate: authenticated metadata-only release/selected-group custody and protected artifact/dependency/runtime identities, plus independently reviewed selected-only non-scoring admission and fresh identity-bound runtime/lifecycle evidence. Codex 180 privacy closure does not supply either part.
- Validation: static pin reconciliation, scoped Git/hash recomputation, JSON consistency and diff whitespace review; no execution tests or production measurement.
- Integration: local documentation/metadata outputs only; parent review and main integration remain separate.

## Filesystem quota operator/backend checklist — Codex 191 — 2026-10-14

- Status: `documented_blocker`; documentation/schema only. Host provisioning, backend observers/allocators, runner integration and live enforcement remain external/runtime work; no production authorization.
- Scope: only `/tmp/hg-codex-191`, base `a58b4b181193a2e2b201c6353722725ad77b597c`; repository guidance, quota documentation and admission source contracts. No mounts/quota operations, live host configuration inspection, Docker/model/H0 execution or task-payload reads.
- Change: [operator/backend checklist](filesystem-quota-backends.md) assigns owners and gates for XFS/ext4 hard block+inode limits, paired tmpfs bounds, pre-staging workspace allocation, actual Docker driver/snapshotter storage, bounded snapshot/export and verified cleanup/quarantine. All implementation checkboxes remain open. Historical Codex 168 source findings and 252-test claim are preserved as historical evidence.
- Evidence contract: [Draft 2020-12 JSON Schema](filesystem-quota-evidence.schema.json) specifies closed, metadata-only run/source/policy/observer-bound records for provisioning, project/tmpfs scopes, writer inventories, Docker storage, snapshots and cleanup. Required trust/freshness/arithmetic/ownership checks and projection limits are documented separately; no semantic validator or runtime integration is implemented. Current runtime admission still refuses writable actor roots.
- Validation: installed `jsonschema.Draft202012Validator.check_schema` plus `FormatChecker` under `python -B`: **32 synthetic in-memory shapes/lexical controls accepted, 262 malformed shapes/lexical controls rejected**. All seven document links and 169 local schema references resolve; historical audit table and validation text match the base; no checkbox is checked. `git diff --check` passes. These are schema/document checks, not live observations or OS enforcement tests; no observation receipts were created.
- Commit: accompanying docs-only commit; parent review/integration and external provisioning remain separate.
