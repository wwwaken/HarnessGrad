# Adapter Integration Journal

This is the repository record of what each dataset taught the platform.

An adapter is not complete when it loads. It is complete when its scorer, runtime, split, evidence, privacy and resource boundaries are understood and recorded. Every new adapter entry must link the evidence artifacts, the platform change, the validation command and the commit that carries the change.

## Fresh diagnostic dry-launch template — 2026-10-14 — Task 223

- Status: `planning`; no dataset/task selected; no run ID reserved; no model/H0 or endpoint execution.
- Scope: docs-only source review in `/tmp/hg-codex-223`, base `82459cfa6d16c323ca40f21db2daf597921aedb3`; driver staged policy, diagnostic schema, lifecycle/admission contracts and current run-metadata writer.
- Evidence: [unique dry template and checklist](task-223-dry-diagnostic-launch.md), including exact receipt/metadata fields, empty planning envelope, future coverage invariants and evidence bindings.
- Finding: the current driver still supplies unknown cleanup/snapshot and no lifecycle producer; metadata records a plan, not production completion. Trusted observation/integration and dataset gates remain pending. This document grants no launch or expansion authorization.
- Validation: static embedded-JSON/schema-key/link checks and `git diff --check`; no runtime imports, datasets, tests, backend or model calls. Validation details accompany the template.
- Commit: accompanying Task 223 docs-only change; no parent/main merge.

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

## TriviaQA — upstream evaluator acquired, adapter correction pending new identity — 2026-10-14

- Status: `source provenance acquired`; current adapter correction is isolated and historical runs remain unchanged
- Finding: public GitHub commit `ca43b5820b107f3970cf4b7d67f7db7a98117b79` supplies the original evaluator, helpers, Apache-2.0 license and Git-object evidence. The acquired differential found a real normalization mismatch: upstream replaces punctuation and underscores with spaces, while the old adapter removed and joined them.
- Platform change: `data/triviaqa.py` now follows the pinned upstream normalization for new runs; the scorer identity must change. Existing curves remain under their original identity and are not rewritten.
- Validation: synthetic upstream differential and provenance tests are rerun after the correction; no TriviaQA payload or heldout rows were read.
- Remaining gates: independent parent review of source equivalence, Hub dataset revision-to-scorer mapping, grouping/denominator semantics and fresh diagnostic authorization. This correction alone does not authorize a pilot.

## TriviaQA — scorer correction review — 2026-10-14 — Codex 205

- Status: `preflight`; synthetic EM component review passed, production comparison remains gated
- Scope: isolated `/tmp/hg-codex-205`, base `65b0f2a`; public scorer/license/Git evidence and fabricated test inputs only; no TriviaQA payload/heldout, model/H0, endpoint or GPU execution
- Finding: acquired source/license hashes and commit/tree linkage pass; merged normalization correction matches upstream. A remaining 200-alias cap loses a fabricated match at alias 201. Scorer evidence had no new explicit identity; fixture/download docs still described the old acquisition failure.
- Evidence: [unique review](../triviaqa-scorer-review-codex205-report.md), `tests/quality/test_triviaqa_scorer_review_codex205.py`, [focused result](../triviaqa-scorer-review-codex205-test-result.txt)
- Platform change: preserve every alias for the max; new verifier evidence records `triviaqa-alias-max-em-upstream-normalization-all-aliases-v2` and the pinned upstream reference. Docstrings distinguish matching EM semantics from local extensions. Original acquired source, acquisition receipt, historical reports/results and identities remain unchanged.
- Remaining gates: Hub revision-to-loader/scorer mapping, grouping/denominator comparability, actual scorer/harness hashes and all runtime/diagnostic admission requirements; source hashes alone do not establish full evaluator equivalence
- Validation: three focused offline synthetic suites — **38 passed**, no failures/skips; original full evaluator/CLI, source/license/linkage, normalization edges, alias-201 matches and shared-verifier identity on hit/miss; `git diff --check` passed. Exact command and before/after failures in the unique review.
- Commit: accompanying `fix: preserve TriviaQA aliases and record corrected scorer identity` commit; exact hash delivered with review

## TriviaQA — Hub conversion metadata review — Codex 225 — 2026-10-14

- Scope: isolated `/tmp/hg-codex-225`, base `61e7f82245c76e7c833740216940d1fcaf3b76be`; public historical code, license, manifest and Git/API metadata only. No dataset/task/heldout rows, parquet or archive access; no loader/scorer/model/H0/endpoint execution or main-branch mutation.
- Finding: exact Hub revision linkage remains unverified. Four retained exact-revision Hub requests failed with network unreachable. GitHub history supplied historical loader `413205c1a7247a2ff81cf709117ce93624fa6fd3`, preserved with Apache-2.0 license, original file hashes and reconstructed commit/tree/blob linkage. The loader trims normalized aliases but omits HumanAnswers and domain/verified flags; `rc.nocontext` combines sources and removes document lists. Its association with the requested Hub export is not established.
- Evidence: [unique review](../triviaqa-hub-linkage-codex225-report.md), [code/metadata fixture and exact request](../tests/fixtures/triviaqa_hub_codex225/README.md), `tests/fixtures/triviaqa_hub_codex225/acquisition.json`, `tools/check_triviaqa_hub_provenance_codex225.py`, `triviaqa-hub-linkage-codex225-validation.txt`.
- Platform change: refine the existing external `hub-export-scorer-linkage` request to require immutable export-to-loader association, human-answer preservation/absence/redundancy and source/selection/key/denominator mapping. Production code, metric identity, shared blockers and historical receipts remain unchanged.
- Validation: offline historical source integrity and changed/missing-source controls pass; original-scorer byte integrity passes; registry checker passes (28 datasets, eight shared gates, 11 historical records, no authorization); existing focused registry tests **52 passed**, no skips. Exact output is retained in the unique validation artifact. These are metadata/integrity checks, not benchmark measurements or production authorization.
- Commit: accompanying task-225 source/metadata review commit; exact hash delivered with handoff.

## TriviaQA — current scorer identity and registry review — Codex 215 — 2026-10-14

- Status: `preflight`; original evaluator source gate reviewed, no further adapter EM mismatch reproduced
- Scope: isolated `/tmp/hg-codex-215`, base `82459cf`; reviewed `fcbed17`/`4fa8481`, code-only fixture, registry and journal; fabricated inputs only, no dataset payload/heldout, network, model, H0 or GPU execution
- Finding: source/license/Git linkage and existing source/differential tests pass. The remaining repository-solvable mismatch was the active registry's obsolete upstream-acquisition blocker and pending-identity evidence anchor, despite the acquired source and already merged v2 identity.
- Evidence: [unique review](../triviaqa-review-codex215-report.md), `tests/quality/test_triviaqa_identity_codex215.py`, [focused results](../triviaqa-review-codex215-test-result.txt)
- Platform change: retire `upstream-evaluator-acquisition` from the active TriviaQA blocker list and name the actual external gate `hub-export-scorer-linkage`; retain all shared gates. Added fresh-interpreter checks of the actual materialized scorer/check inputs for text/structured hit and miss, empty and absent answers. Production scorer/check code, v2 identity, upstream bytes, acquisition receipt and historical records are unchanged.
- Remaining gates: independently pinned Hub export-to-loader/scorer mapping, grouping/denominator comparability, actual scorer/harness hashes and all runtime/diagnostic admission requirements; no production readiness or diagnostic authorization follows
- Validation: baseline source/differential suites **38 passed**; six materialized-verifier cases **6 passed**; final combined source/identity/registry suite **93 passed**, no failures/skips. Exact commands are recorded in the unique review; fixture integrity tool and registry checker exit 0, registry retains `production_authorized=false`, and `git diff --check` passes.
- Commit: accompanying `docs: align TriviaQA blocker with reviewed scorer identity` commit; exact hash delivered with review

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

## BFCL v1.3 checker blob retry — 2026-10-14 — Codex 227

- Status: partial official code acquisition; full-call scorer, archive custody and production route remain blocked.
- Scope: fixed v1.3 commit Git-blob API only; code/license/spec metadata. No task, answer, reference, archive, heldout or external dataset-root access; no H0/model.
- Finding: `ast_checker.py`, `type_mappings.py`, LICENSE and `pyproject.toml` were acquired and their Git blob SHA-1/byte counts verified. The checker itself is 24,916 bytes. Static imports still require missing `model_config.py`, Java type converter and JavaScript type converter; their pinned blob SHAs were absent from allowed path metadata, so requests were not guessed.
- Evidence: `bfcl-blob-retry-codex227-report.md`, `tests/fixtures/bfcl_ast_source/retry-codex227/provenance.json`, and exact request/response receipts in that fixture. Candidate remains `status=blocked`, `measured=false`, `custodian_approved=false`, `production_authorized=false`.
- Remaining gate: obtain independently pinned helper path/blob identities and licenses; bind the complete source projection to v1.3/V3 and the declared archive/index through independent approval; then derive/test full-call semantics on fabricated inputs only. Current function-name metric remains diagnostic-only.

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

## BFCL custody operator packet — Codex 208 — 2026-10-14

- Status: documentation-only; official full-call source/runtime and archive/index custody remain blocked. No production authorization or new approval pin.
- Artifact: [operator packet](bfcl-codex208-operator-packet.md), linked from the source acquisition contract. It enumerates retained/missing original paths, unknown transitive discovery, approved receipt delivery and independent trusted-channel pin, license/offline runtime closure, separate exact-index/storage/split approval and ordered verification/stop conditions.
- Finding retained: the current source gate checks approved projection integrity only; the selected reader has no independent index-pin admission. Neither source acquisition nor passing synthetic controls closes the remaining runtime/export/quota/snapshot/cleanup and diagnostic-review gates.
- Validation: **165 passed** across source-contract, selected/privacy and registry regressions; unpinned source gate exits **2**, `measured=false`, `production_authorized=false`. Rechecked all seven retained size/SHA-256/Git blob identities (126,311 bytes) and local document links.
- Scope: `/tmp/hg-codex-208` only; no benchmark files, archives, external dataset roots, network fetch, package install, upstream evaluator execution or model/GPU run. Candidate bytes, provenance, adapter, scorer and registry are unchanged.

## BFCL packet/provenance review — Codex 217 — 2026-10-14

- Status: docs/test correction only; full-call source/runtime and independent archive/index custody remain blocked. No production authorization or approval pin.
- Findings: the Task 208 packet omitted exact receipt/index field names and reader bounds; metadata response bodies are not retained with the Task 195 candidate, so recorded upstream observations cannot be independently reverified offline from this handoff. Clarified those limits and the source gate's commit-shape/declared-edge scope.
- Evidence: [unique review report](../bfcl-packet-review-codex217-report.md), [corrected operator packet](bfcl-codex208-operator-packet.md), and a source-contract regression confirming the retained candidate's blocked flags and refusal before projected-source access even with its integrity digest.
- Validation: **87 passed** across source-contract and registry tests only; unpinned source gate exited **2** with `measured=false`, `production_authorized=false`. Source-only registry validation passed with 28 datasets, 8 shared blockers and 11 historical records.
- Scope: `/tmp/hg-codex-217` only; no dataset payload/answers/heldout/archive/external dataset-root access, network, upstream execution, installation or model/GPU work. Candidate, production code, registry and earlier receipts are unchanged.

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

## LiveCodeBench custody operator packet — Codex 207 — 2026-10-14

- Status: `BLOCKED_EXTERNAL_ROW_ATTESTATION`; task-198 request remains unsent. No external custody record, signature or independent approval is supplied.
- Scope: docs only in isolated `/tmp/hg-codex-207`, base `65b0f2a5bf95fdafd218ca54198843c27b9fffbe`; local instructions, source and documentation only. No network, pool/statement/test/solution/heldout payload reads, adapter import, model/H0 or main-branch changes.
- Deliverable: [operator packet](task-207-livecodebench-operator-packet.md) gives the exact 12-key target JSON template, separate authenticated custody/reviewer signature channels, offline OpenPGP commands, bounded metadata-only preflight, failure dispositions and the no-payload boundary. The template is not an issued receipt; no attestation or approval artifact was created.
- Validation: target keys, values and types match AST-read admission constants; original-ID train calculation matches. Shell syntax and embedded Python compilation pass; all three packet links resolve; `git diff --check` passes. Verification commands were not executed and no payload-reading tests were run.
- Limit: existing `identity(statement, ...)` cannot run in this scope. Preflight cannot authenticate provenance by itself or set `row_attested`; independent review and later separately authorized production admission remain required. Fresh pool verification stays false, and other execution gates are unchanged. Parent review/integration remains separate.

## 2WikiMultihopQA source-gate review — Codex 206 — 2026-10-14

- Status: independent evaluator source gate closed for the pinned code-only fixture; fresh dependency, Hub/data provenance, historical metric comparability and shared runtime gates remain blocked. No production authorization.
- Scope: only `/tmp/hg-codex-206`, base `65b0f2a5bf95fdafd218ca54198843c27b9fffbe`; reviewed merged source fixture commit `349d74f1d930bcb4c6664b1f6521571f118a619a`, exact evaluator code, provenance metadata, focused tests and current registry. No benchmark task/answer/alias/split/heldout payload or external benchmark receipt reads, adapter imports, production scorer edits, network, model/H0 or controls/pilots.
- Source finding: original v1.0 and v1.1 evaluator bytes, exact Apache-2.0 license/requirements, and GitHub commit/root-tree metadata bind to upstream commit `209e761834d1ce055856fc11072c0a5aab47601d` and root tree `545a956af257f0c79c68c39a358086de7cbf243b`. Fresh tests reconstruct tree/blob identities and check independent SHA-256 pins; the v1.1 transcription region matches without importing the adapter. The unsigned commit's observed origin still relies on the preserved GitHub HTTPS acquisition metadata; no new acquisition or archive revalidation was performed.
- Metric boundary: upstream `f1` is Answer F1; `joint_f1` is the harmonic mean of product precision/recall across answer/support/evidence. Both remain distinct. Synthetic v1.1 alias/evidence quirks are preserved, including possible values above 100; finite fabricated-input checks do not certify production wrapper or leaderboard equivalence.
- Registry change: retired stale `independent-evaluator-source` because the active-only schema has no closed status; added explicit `ujson-native-offline-closure` and `hub-data-provenance` external blockers. `recovery-comparability`, all eight shared blocker references, the original partial-measurement record and its null effect remain unchanged. This supersedes only the earlier journal's missing-source finding, not its historical fetch failure, metrics or receipts.
- Dependency boundary: unchanged programs execute with real installed `ujson==5.10.0`, without transitive Python runtime requirements. Published wheel/sdist hashes are metadata only; payload acquisition, installation-origin linkage, supported Python/native image identity, native loader/transitive closure and a fresh offline installation/import/synthetic run remain required. No dependency was installed or substituted.
- Data boundary: code provenance and its license do not bind the Hub/data revision, split/selected manifest, alias artifact identity/completeness, dataset rights or release-to-evaluator mapping. Metadata-only custodian evidence remains required; no payload access is authorized by this closure.
- Evidence: [unique task 206 review and test receipt](task-206-twowiki-provenance-review.md), `tests/quality/test_twowikimultihopqa_provenance_codex197.py`, `tests/fixtures/twowikimultihopqa_upstream_codex197/provenance.json`, and the machine-readable blocker registry.
- Validation: fresh provenance suite **38 passed in 0.24s**, registry suite **49 passed in 2.92s** (**87 total**, no failures/skips), with plugin autoload/bytecode/cache disabled and source/synthetic-only guards. Registry checker: valid, 28 datasets, 8 shared blockers, 11 historical records, `production_authorized=false`. In-memory base comparison confirms only 2Wiki active blockers changed; all historical/shared/recovery objects and the complete earlier journal are preserved. Existing fixture, tests and production code are unchanged; `git diff --check` passed.
- Cleanup: fresh task-owned `.scratch/twowikimultihopqa-codex206` and `.scratch/blocker-registry-codex206` were removed after preserving results and verified absent. This is local test-file cleanup, not a runtime/snapshot receipt.
- Integration: focused documentation/registry/journal commit; parent integration remains separate.

## 2WikiMultihopQA registry audit — Codex 216 — 2026-10-14

- Scope: isolated `/tmp/hg-codex-216`, base `82459cfa6d16c323ca40f21db2daf597921aedb3`; local source/docs and code-only synthetic tests. No adapter imports, benchmark payload/external receipt reads, network, dependency installation, model/H0 or pilots.
- Finding: the current registry already retires `independent-evaluator-source`; `ujson-native-offline-closure` and `hub-data-provenance` remain `external`, `recovery-comparability` remains `measurement`, all eight shared gates remain active and production authorization remains false. No registry edit was needed.
- Change: three source-only registry regressions protect those blocker states, the unchanged original 48-scored/two-invalid mixed Answer F1/Joint F1 pilot with null effect, and separate `demand=evidence`, `surface=information_seeking`, `exercises=[context]` axes. Registry, history baseline, taxonomy, checker, evaluator and provenance fixture/tests are byte-identical to the base; the earlier journal is an unchanged prefix.
- Validation: registry checker valid (28 datasets, 8 shared blockers, 11 historical records); combined registry/provenance suites **90 passed in 3.10s** (52 + 38), no failures/skips. Baseline suites passed 87 tests. An initial missing scratch-parent setup error was corrected and is recorded separately in the [task 216 audit receipt](task-216-twowiki-registry-audit.md). `git diff --check` passed.
- Cleanup: task-owned `.scratch/registry-provenance-codex216-baseline` and `.scratch/registry-provenance-codex216-final` removed and verified absent. Local test cleanup and source/synthetic success establish no deployment, benchmark or production readiness. Docs/tests-only commit; parent review/integration remains separate.
## GAIA operator-packet contract review — Codex 219 — 2026-10-14

- Status: BLOCKED; task-210 clarification only. Task-212 readiness matrix is unavailable in this checkout/visible history, its path/commit was requested, and reconciliation remains pending. Task-202 evidence is still pending. No execution approval or gate closure.
- Scope: only `/tmp/hg-codex-219`, base `82459cfa6d16c323ca40f21db2daf597921aedb3`; repository source/docs/Git metadata and authored synthetic tests. No benchmark task/answer/attachment/heldout or external receipt reads; no Docker, network, model, H0, benchmark control or official scorer execution.
- Finding: task 210 contains no direct authorization or contradictory execution instruction, but omits explicit dry-preflight input/exit boundaries, diagnostic-v2 serialization/replay, lifecycle scope/outcome/snapshot/cleanup binding, no-model null encoding and the distinction between structural publication and production authorization.
- Change: [task-210 packet](gaia-operator-packet-codex210.md) now states those contracts and final-candidate comparison requirements; [unique review](gaia-contract-review-codex219.md) records findings, missing input and limits. No implementation/schema/admission exception or reusable platform capability changed.
- Validation: focused authored preflight, compatibility/snapshot, lifecycle and diagnostic-policy regressions: **285 passed, 11 driver/eval-side tests deselected in 2.08s**, no skips; `git diff --check` passed. These are synthetic regression results, not dataset/runtime receipts.
- Integration: narrow documentation commit in the isolated worktree; parent review/integration and task-212 review remain separate. Documentation paths remain conservatively runtime-affecting under the existing compatibility contract; no historical receipt reuse.

## ujson wheel provenance and offline package install — Codex 226 — 2026-10-14


- Status: exact package acquisition/RECORD and fresh offline installation verified; `ujson-native-offline-closure` remains `external`. No supported-image, loader/transitive native closure, native import, bundled-component notice clearance or production authorization.
- Scope: only `/tmp/hg-codex-226`, base `61e7f82245c76e7c833740216940d1fcaf3b76be`; public official PyPI JSON/wheel and repository code/metadata only. No benchmark dataset payload, adapter import, scorer, model, endpoint, H0, pilot or sdist/build acquisition. Native extension was never loaded; no `ldd` or native loader execution.
- Artifact: recorded target CPython 3.12.4/Linux x86_64 with glibc >=2.17; exact `ujson-5.10.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl`, 53,686 bytes, SHA-256 `f8ccb77b3e40b151e20519c6ae6d89bfe3f4c14e8e210d910287f778368bb3d1`. Official PyPI JSON binds URL/hash; original response, acquisition time/headers, wheel and static ELF reports retained in `tests/fixtures/ujson_pypi_codex226`. HTTPS metadata remains the origin trust boundary; no independent publisher signature is claimed.
- Dependency correction: this published extension hash differs from the task-197 installed extension. Static readelf records five direct libraries (`libstdc++.so.6`, `libm.so.6`, `libgcc_s.so.1`, `libpthread.so.0`, `libc.so.6`), required GLIBC/GLIBCXX/CXXABI/GCC versions, no RPATH/RUNPATH and no bundled shared libraries. Old three-library observations cannot attest this artifact. No declared transitive Python runtime requirements.
- Notices: exact combined 5,975-byte license retained, including Electronic Arts/ESN, MODP_ASCII and Tcl-derived terms. Defined double_conversion symbols have no corresponding notice in the wheel license; authoritative bundled source/revision/license and required-notice review remain open. No notice text or clearance was invented.
- Installation: two fresh task-local venvs used local-wheel-only, exact-hash, binary-only, no-dependency/no-cache/no-version-check/no-bytecode installation. The final replay also set `PIP_CONFIG_FILE=/dev/null` because `--isolated` still permits global/site configuration. Pip 24.0 reports and original non-RECORD file identities are retained; all five files byte-match the wheel. This is package installation on the current glibc 2.35 host, without an OS network namespace or immutable image attestation.
- Change: [task-226 report and reproducible offline procedure](task-226-ujson-wheel-report.md), [focused package provenance tests](../tests/quality/test_ujson_pypi_codex226.py), [HTML evidence summary](../ujson-wheel-codex226-overview.html), and a narrow ujson-blocker observation/evidence/next-action refresh. External status, all histories/taxonomy/shared gates/other datasets and production authorization remain unchanged; earlier receipts/journal entries are preserved.
- Validation: final **61 passed in 4.03s** (9 package + 52 registry), no failures/skips. Registry checker valid: 28 datasets, 8 shared blockers, 11 historical records, `production_authorized=false`. The initial run's new-test version ordering mistake and nonliteral evidence locator caused 23 failures/38 passes; both were corrected and initial output retained separately. [Final result](../ujson-wheel-codex226-test-result.txt); original JSON/wheel/acquisition pins and actual ELF metadata are checked offline without importing package or dataset code.
- Remaining handoff: platform owner must bind this wheel to a supported immutable Python/native image, attest resolved loader/library paths/hashes and recursive symbol providers, complete bundled-component notices, and observe a fresh network-denied image-bound install/native import/fabricated JSON round trip. Any later scorer synthetic run needs its own wheel/image-bound receipt.
- Cleanup: task-owned extracted ELF, both venvs, local HTML settings and pytest temporary files removed after preserving evidence; see `tests/fixtures/ujson_pypi_codex226/local-cleanup.json`. This is local file cleanup only. Focused task commit is for parent diff review/integration; no main merge or runtime gate change.
- Diff review: authored source/docs pass the focused staged whitespace check; raw readelf reports and initial pytest output preserve tool-emitted trailing spaces. All new relative documentation links resolve. The task-197 fixture/tests and all production code remain byte-identical to the base.
## GAIA scorer full-revision discrepancy — Codex 228 — 2026-10-14

- Status: `BLOCKED_CANONICAL_FULL_REVISION_RELATIONSHIP_UNRESOLVED`; no pin correction recommended on current evidence, no production authorization.
- Scope: only `/tmp/hg-codex-228`, base `61e7f82245c76e7c833740216940d1fcaf3b76be`; repository metadata/code and anonymous canonical public Space metadata/scorer requests. No dataset questions/answers/attachments/private gold, adapter/scorer import, dependencies, Docker, model/H0, benchmark execution or main-branch changes.
- Finding: adapter pin `9f133d71362ecb0a1c7ff6b4dcfc2a6b9f8ffd1e` and candidate `9f133d71362e77b3539f1514f31b9c101a545fec` differ after a shared 12-character prefix. The expected scorer SHA-256 is `0d44c07f3046eec521697c22e3eaca8719cc81e422a8eaf32695c5f22bdac6e2`. Local Git traces the unchanged declaration to the original GAIA adapter commit and contains neither upstream object; it cannot authenticate their relationship. Task-200 mirror checksum/tree/blob observations remain inherited claims.
- Canonical evidence: both revision API lookups, candidate root-tree/scorer requests and Git refs advertisement failed with network-unreachable errors before HTTP; both IPv4-only API retries timed out, also without HTTP. No canonical absence, alias, ancestry or typo claim is established.
- Deliverables: [unique report](task-228-gaia-scorer-revision-report.md) and [decision/evidence index](task-228-gaia-scorer-revision-evidence/decision.json) preserve exact IDs, failed requests, historical Git provenance, limits and required canonical commit/tree/scorer evidence. Production source, pins, mutable acquisition URL and admission gates are unchanged.
- Validation: all 29 metadata/source-integrity, historical Git binding, evidence hash, report link and append-only journal checks passed; `git diff --check` passed. No scorer or benchmark tests were run. These checks provide no run, runtime-cleanup or lifecycle receipt; execution fields are null. Parent review/integration remains separate.
## AppWorld canonical public source review — Codex 229 — 2026-10-14

- Scope: only isolated `/tmp/hg-codex-229`, base `61e7f82245c76e7c833740216940d1fcaf3b76be`; local source/docs and allowlisted official GitHub public code/docs/metadata. No repository archive, protected bundle, task/split payload, external benchmark receipt, wheel or image access; no adapter import, official task/scorer/runtime, model or H0 execution.
- Source: official `v0.1.3.post1` annotated tag `efac79081936323733f68fd78260dab6981f195a` peels to `66ad8099e12188ece0d3fe45e661dbc01880813b`, root tree `bbe398b91767a9a068add36eb84bdf936eed372f`, matching the local Dockerfile's requested package version. Eight original public code/docs/license files, raw contents-API responses, release/tag/commit/tree metadata and SHA-256 acquisition receipts are preserved. Failed raw-host requests and a tag-object API rate limit remain recorded; successful source acquisition used exact-commit official GitHub API responses. Official GitHub `git ls-remote` supplies tag/peeled-ref linkage; the annotated tag object itself was not acquired/rehashed. HTTPS acquisition is the origin basis, not independent custody/signature evidence.
- Mapping: pinned evaluator defines task/scenario goal completion and percentage output; local TGC/SGC use fractions, selected measured coverage, fixed-three variants and guarded original trial alignment. `test_normal` maps to local Test-N and `test_challenge` to Test-C; source keys and source splits stay separate from the harness train/eval partition. Public code identifies data version/URL `0.1.0`, but neither authenticates the adapter's bundle checksum/counts nor proves deployed image/package/evaluator contents. README short metric keys differ from actual implementation long keys.
- License: original public Apache-2.0 license is preserved. Upstream README separately adds encrypted-public-redistribution requirements for protected task/app/API-specific bundles; this review acquires no protected artifact and makes no blanket data-license claim.
- Remaining gap: current checker/runner supplies no original numeric trial identity to saved verdicts; the writer correctly marks anonymous cells unaligned, so current production-source flow cannot establish aligned SGC. Actual source/package/image/evaluator binding, split/manifest custody, coverage, budgets, endpoint, lifecycle/snapshot and cleanup receipts remain absent. No scorer/writer/adapter/registry behavior changed, no gate retired and no production authorization.
- Evidence: [task-229 report](../appworld-canonical-source-codex229-report.md), [local adapter audit](appworld-local-adapter-audit-codex229.md), and [public-source manifest](evidence/appworld-codex229/source-provenance.json).
- Validation: offline custody checker passes 32 pinned-file digests, four reconstructed Git trees and eight public code/docs blobs; 27 local report links resolve within the worktree. Parent source/diff review and whitespace check pass. No upstream program, benchmark or synthetic scoring code executed and no score was generated. Focused local commit is for separate parent review/integration.
## Quota readback authentication review — Codex 233 — 2026-10-14

- Status: documentation proposal complete; host provisioning, observer/verifier implementation, allocation/runner wiring and runtime enforcement remain blocked. No checklist completion or production authorization.
- Scope: only `/tmp/hg-codex-233`, base `61e7f82245c76e7c833740216940d1fcaf3b76be`; reviewed quota schema/backend requirements, task-222 administrator checklist and runner/lifecycle source contracts. No host inspection/changes, network, Docker, key/signature generation, quota/runtime receipts, enforcement probes, models/H0 or pilots.
- Findings: current IDs/hashes and lifecycle replay authenticate no origin; historical root maintenance evidence is distinct from fresh run-bound provisioning/scope observations. Runner documentation requests distinct worker bindings while nested lifecycle snapshot checks use the enclosing binding; an explicit reviewed integration decision remains required.
- Change: [unique task-233 review](task-233-quota-readback-authentication.md) specifies enrolled Ed25519 roles and exact signed bytes, external closed statement bodies, challenge/lease/allocation joins, independent host/final-namespace collection, durable consumption and cleanup release. It preserves existing closed schemas, reason codes and false authorization flags. Existing checklist/backend/runner docs link the proposal; the [local HTML companion](task-233-quota-readback-overview.html) summarizes it.
- Validation: 24 local links across the four reviewed Markdown documents resolve; schema field/phase comparison passed; quota schema and both runner/lifecycle implementation files are byte-identical to base. Local HTML render completed with four panels and zero writing warnings; no external asset references. `git diff --check` passed. No runtime tests or host queries were run for this docs-only change.
- Cleanup/integration: only task-owned local HTML-render state was temporary; no runtime resource cleanup is claimed. Parent diff review and integration remain separate; no merge or gate closure.

## Current blocker observation audit — Codex 240 — 2026-10-14

- Scope: only `/tmp/hg-codex-240`, reviewed merged HEAD `0930d99cc882c5a049c98f9123e9427470e7e818`; source/provenance reports, metadata and current registry. No dataset payload/external receipt, adapter import, network, host query, scorer/runtime, model, GPU or diagnostic execution.
- Findings: mark AgentDojo's directory inventory as inherited metadata rather than authenticated current custody; distinguish the missing connected quota backend from unknown host quota capability/enforcement. Add merged report anchors. Both machine blockers remain `runtime`.
- Guide corrections: BFCL's partial code/checker acquisition in tasks 195/227 and ujson's exact wheel/offline package installation in task 226 supersede two old acquisition statements. Complete source/custody, notice/image/native closure and runtime gates remain open; no external blocker is downgraded.
- Preservation: independent comparison permits only those two machine `observed`/`evidence` pairs to differ. Every blocker ID/family/status/action, shared reference, taxonomy/review field and all 11 historical records match reviewed HEAD; earlier journal content is unchanged. No production code, tests, provenance fixtures or historical reports/receipts are edited.
- Validation: checker valid, 28 datasets / eight shared blockers / 11 historical records, `production_authorized=false`; existing guarded registry suite **52 passed in 2.66s**, no skips. Baseline passed 52 tests after creating the initially omitted scratch parent; the first invocation's setup errors are recorded in the [unique task-240 audit](task-240-blocker-registry-audit.md). Diff whitespace and local-link checks pass. Test-file cleanup is local housekeeping, not a runtime cleanup receipt. Parent review/integration remains separate.

## Ordinary GPU entrypoints and sandbox audit — Task 242 — 2026-10-14

- Scope: isolated `/tmp/hg-codex-242`, base `0930d99cc882c5a049c98f9123e9427470e7e818`; docs, CLI help and mocked tests only. No model/H0, endpoint, GPU, Docker or host-quota execution.
- Finding: ordinary entrypoints have no universal strict filesystem-quota/backend-observer prerequisite. Existing staged-policy requirements and the Task-163 declared-policy refusal remain; the UI explicitly chooses general sampling. Sandbox failure still refuses, and `--no-sandbox` remains explicit, warned, recorded and non-comparable, retaining the exec container boundary.
- Change: clarify CLI help and README scope; make local demo sampling explicit; add six capture-only/pre-execution controls. Runtime execution, CLI defaults, schemas and admission behavior are unchanged; an AST comparison confirms the driver diff changes only parser description/help text.
- Evidence: [task-242 audit](task-242-gpu-entrypoint-audit.md), `tests/quality/test_gpu_entrypoint_contract_codex242.py`, [focused result](../gpu-entrypoint-codex242-test-result.txt). Four focused pure/mocked suites: **156 passed**, no failures/skips; three shell entrypoints pass `bash -n`; `git diff --check` passes. Initial missing-scratch setup errors, the corrected six-test result and the earlier focused output are retained. Final verification binds both pytest and stdlib temporary paths inside the worktree.
- Limits: authored model/sandbox successes are not live observations, quota enforcement, dataset-gate closure or production/H0 authorization. Unknown lifecycle/cleanup/snapshot evidence and current production gates remain unchanged.
