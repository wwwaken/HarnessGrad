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

## LiveCodeBench — authored references

- Status: preflight-required, no H0
- Scope: 1055 pool tasks; 3 train-side authored references and 4 eval-side references
- Finding: an authored reference proves scorer reachability for one task, not full benchmark coverage
- Evidence: `/tmp/codex/79/report.md`; inert manifest selects `livecodebench/740`
- Platform change: reference coverage, public-only authoring and covered-subset manifests are separate from official benchmark claims
- Remaining gates: train metadata attestation, public-only export, independent review and official test verification
- Commit: inert artifacts only

## AppWorld / GAIA / tau-bench — local state boundaries

- Status: preflight-required, no H0
- Scope: AppWorld reference-covered train subset; GAIA validation-only pool; tau-bench returned local pool
- Finding: service reset, database state, attachments, web access and evaluator secrecy cannot be inferred from adapter loadability
- Evidence: `/tmp/codex/86/report.md`; `/tmp/codex/87/report.md`; inert manifests
- Platform change: one shared lifecycle for scope, admission, restore, readiness, execution, quiescence, scoring, sealing and cleanup
- Remaining gates: real local controls after shared runtime repair; no fallback simulator or hidden web access
- Commit: inert artifacts only

## AgentDojo / BFCL / SpreadsheetBench / ChessBench

- Status: preflight-required or blocked, no H0
- Scope: exact inert manifests only
- Finding: AgentDojo splits must preserve user groups; BFCL irrelevance tasks may reward empty output; Spreadsheet golden files and recalculation need trusted boundaries; Chess move legality and gold privacy need proof
- Evidence: `/tmp/codex/85/report.md`; `/tmp/codex/67/report.md`; `/tmp/codex/63/report.md`
- Platform change: dataset-specific semantics belong in scorer contracts, while isolation, evidence and reset belong in shared platform controls
- Remaining gates: real controls and production-path tests
- Commit: inert artifacts only

## Terminal-Bench — image, network and disk admission

- Status: preflight-required, no H0
- Scope: 52 imposed train tasks; 51 cached images; one missing image
- Finding: per-task TOML timeouts and image dependencies must survive into admission; Docker root headroom is a benchmark gate, not an afterthought
- Evidence: `/tmp/codex/88/report.md`; `/tmp/codex/80/schedule.md`; Docker cleanup record
- Platform change: shared resource admission, disk reservation, snapshot cleanup and scorer network policy
- Remaining gates: missing image, test dependency/network policy, disk reserve and trusted snapshot verifier
- Commit: inert artifacts only

## Process rule

Before launching any new adapter, add or update its entry here and add the corresponding platform capability to `docs/platform-improvement-log.md`. The launch review must cite the entry, the exact manifest hash and the runtime gate receipt.
