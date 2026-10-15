# Task-bound scorer inputs - w-tbi

**12/19 actor-workdir datasets now bind the consumed scorer input to the selected
task; 7/19 remain. All 12 different-task gold substitutions were refused.**
The implemented subset is all **12/12 shared QA-command routes**. This is input
consistency enforcement, not complete offline closure or production authorization.

Baseline: `13b26a6`, registered worktree `/tmp/hg-tbi`, branch `wg-tbi`.
Read `reports/w-reassess-shared-closures.md`, `reports/w-wheelhouse-payloads.md`,
`reports/w-clo-actor-closures.md`, the 19 actor closure records and relevant adapters,
and `reports/w-bind-receipts.md`. Historical closure manifests and receipts remain
unchanged. No benchmark scorer, model, GPU, endpoint, container or pilot was run.

## What was missing, and what changed

At baseline, `data/scaffolds/qa/base.py:337` serialized each record's gold into
`VERIFY.inputs`; its command supplied only the gold path, with no task or digest.
Baseline `data/scaffolds/qa/verify/check.py:166` parsed that path and passed the
result to the adapter at `:238`/`:242`. It neither recomputed a digest nor bound
the parsed gold to a selected task. The historical closure records identify source
artifacts, not this materialized gold. Baseline source remains available at the
baseline commit; the same test file was run in registered `/tmp/hg-tbi-before`.

Current source, with exact excerpts and complete-file hashes preserved in
`reports/w-tbi-evidence/input-source-audit.jsonl`:

- `data/scaffolds/qa/base.py:250` derives task IDs and gold from the same record.
  `:339` serializes the unchanged gold once, hashes its UTF-8 bytes, and declares
  `scorer_input={task_id,path,sha256}`; `:351` passes trusted task/digest arguments;
  `:357` supplies those same serialized bytes as `gold.json`.
- `eval/run/runner.py:527` already supplies its independently selected task ID to
  `_verify`. `eval/verification/verifier.py:491` now refuses a foreign spec or
  missing selected task before staging or execution. The existing staging at
  `:566` still overwrites actor copies using `eval/observe/tracing.py:324`.
- `data/scaffolds/qa/verify/check.py:171` reads one byte buffer, recomputes SHA-256,
  compares it with the trusted pin and records requested task, path, actual digest,
  expected digest and `verified`. `:180` refuses a mismatch before adapter import
  or scoring, with exit 3, `measured=false` and no reward. `:184` parses **that
  same buffer**, and `:256`/`:260` pass the resulting object to the unchanged
  structured/legacy scoring branches. A later file replacement cannot change the
  object passed to the scorer while leaving an identity for earlier bytes.
- `eval/verification/verifier.py:512` compares the returned receipt against the
  selected spec before accepting a reward. Missing/foreign/unverified evidence
  becomes explicitly unmeasured with `score=null`. `data/dataset.schema.json:56`
  documents the new optional verifier field. No scorer predicate, metric, gold
  fields, admission rule or isolation class was changed.

Old by-hand check calls with **neither** identity argument remain callable but
record `verified=false`, null task and null expected digest. They cannot satisfy
native bound dispatch: the downgrade control removes both arguments, obtains a
stub reward, and native consumption refuses it. `_verify_inner` and direct adapter
`score` calls are low-level APIs, not independently task-bound consumers.

## Per-dataset source confirmation and results

All rows below receive inline `gold.json` through the shared staging/read/consume
path above. Each historical expected-data manifest is
`tests/fixtures/hg_wclo_actor/gold/<dataset>.json`; the auditor freshly rehashed its
actual local source artifacts. **17/17 files, 214400530 bytes, match** the records.
These are local source identities, not new upstream provenance claims. Current
serialized gold is additionally digest-pinned and task-bound in every row.

Adapter paths in the source column are under `data/datasets/`. Each row identifies
the gold projection and its binding to the shared scaffold. No raw gold was copied
into these reports. Full recomputed task-input digests are in the raw test outputs.

| Dataset | Adapter gold projection; scaffold binding | Selected task → actual foreign task used | Digest pinned / task bound before → after | Mismatch outcome after |
| --- | --- | --- | --- | --- |
| bfcl_v3 | `bfcl_v3.py:468` record gold, `:529` QASpec, `:582` selected verifier | `simple/0` → `simple/1` | source only / no → consumed bytes / yes | exit 3; no scorer call or reward |
| chessbench_puzzles | `chessbench_puzzles.py:129` FEN/moves/puzzle ID, `:370` QASpec, `:437` selected verifier | `chessbench_puzzles/test/0` → `chessbench_puzzles/test/1` | source only / no → consumed bytes / yes | exit 3; no scorer call or reward |
| fever | `fever.py:58` label/evidence, `:53` QASpec | `fever/validation/0` → `fever/validation/1` | source only / no → consumed bytes / yes | exit 3; no scorer call or reward |
| gsm8k | `gsm8k.py:104` answer/verbatim projection, `:238` QASpec | `gsm8k/test/0` → `gsm8k/test/1` | source only / no → consumed bytes / yes | exit 3; no scorer call or reward |
| hotpotqa | `hotpotqa.py:23` answer/supporting facts, `:65` QASpec | `hotpotqa/validation/0` → `hotpotqa/validation/1` | source only / no → consumed bytes / yes | exit 3; no scorer call or reward |
| musique | `musique.py:182` answer/aliases/supporting facts, `:226` inherited verifier, `:271` selected verifier | `musique/dev/0` → `musique/dev/1` | source only / no → consumed bytes / yes | exit 3; no scorer call or reward |
| physicsquestions | `physicsquestions.py:135` accepted spellings, `:191` QASpec | `physicsquestions/test/0` → `physicsquestions/test/1` | source only / no → consumed bytes / yes | exit 3; no scorer call or reward |
| reasoning_gym | `reasoning_gym.py:94` family/index/entry including answer and metadata, `:153` QASpec | `reasoning_gym/eval/0` → `reasoning_gym/eval/1` | source only / no → consumed bytes / yes | exit 3; no scorer call or reward |
| sportsunderstanding | `sportsunderstanding.py:112` label, `:166` QASpec | `sportsunderstanding/test/0` → `sportsunderstanding/test/3` | source only / no → consumed bytes / yes | exit 3; no scorer call or reward |
| strategyqa | `strategyqa.py:118` label, `:176` QASpec | `strategyqa/test/0` → `strategyqa/test/1` | source only / no → consumed bytes / yes | exit 3; no scorer call or reward |
| triviaqa | `triviaqa.py:252` canonical answer/all aliases, `:339` QASpec | `triviaqa/validation/0` → `triviaqa/validation/1` | source only / no → consumed bytes / yes | exit 3; no scorer call or reward |
| twowikimultihopqa | `twowikimultihopqa.py:569` answer/aliases/support/evidence, `:654` QASpec | `twowikimultihopqa/dev/0` → `twowikimultihopqa/dev/1` | source only / no → consumed bytes / yes | exit 3; no scorer call or reward |

Each native substitution also returns `score=null` and an unmeasured reason. The
selected/foreign IDs above came from actual local adapter records, chosen before
execution as the first record and the next record with different gold. Consequently
Sports uses index 3, not an invented index 1. Test output records every actual hash.

## Remaining 7/19 and why

These native routes do not use QASpec and gain no task-input coverage from this
change. File+line inspection confirms the distinct input contracts below; byte
inventories or an incidental task label do not establish a consumed-input binding.
No native engine, database query, candidate program or workbook scorer was run.

| Dataset | Delivery and actual consumption | Why still unbound |
| --- | --- | --- |
| alfworld | `data/datasets/alfworld.py:356` inline stripped game; `data/datasets/alfworld/verify/check.py:159` passes its path into replay | Needs selected-task digest of the stripped PDDL actually loaded by the native engine |
| bird_minidev | `data/datasets/bird_minidev.py:263` gold SQL plus `:264` SQLite DB; `data/datasets/bird_minidev/verify/check.py:99` reads SQL and `:105` opens DB | Needs a task-bound SQL **and database** identity through SQLite use |
| ds1000 | `data/datasets/ds1000.py:187` context only in actor setup; `:198` verifier inputs omit it; `data/datasets/ds1000/verify/check.py:26` reads actor-workdir context | Context/test authentication and trusted rematerialization are missing; executor pin does not bind the context |
| jericho | `data/datasets/jericho.py:266` task/ROM/seed JSON plus ROM file; `data/datasets/jericho/verify/check.py:109` calls load_game; `data/datasets/jericho/lib/jer_env.py:55` reads JSON | Task label is serialized but not independently compared; needs ROM/seed/config identities through engine load |
| livecodebench | `data/datasets/livecodebench.py:271` selected tests file; `data/datasets/livecodebench/verify/check.py:150` reads test text | Metadata test hashes are not recomputed/checked by the consuming check against selected task |
| scienceworld | `data/datasets/scienceworld.py:320` task-name/variation/simplifications JSON; `data/datasets/scienceworld/verify/check.py:162` calls load_task; `data/datasets/scienceworld/lib/scw_env.py:140` reads JSON | Needs task/variation/config binding plus world payload identity through JVM load |
| spreadsheetbench | `data/datasets/spreadsheetbench.py:245` golden workbook plus task JSON; `data/datasets/spreadsheetbench/verify/check.py:323` reads metadata and `:373` compares workbook | Evidence echoes metadata task_id without independent comparison or consumed golden-workbook digest |

The denominator is the historical **19 actor-workdir routes**, not all 28 registry
entries. AppWorld, GAIA, tau-bench and Terminal-Bench are the four snapshot/service
routes outside this input-binding assessment; no new coverage is credited to them.
Chess's alternate in-process controller is also outside this QA-route claim.

## Fails before / passes after and raw evidence

The exact same final test file against baseline: **132 failed, 24 passed**.
After implementation: **156 passed**. The 12 pre-change direct foreign-gold cases
all reached a scorer spy and produced its sentinel reward; afterward all 12
refused before any spy call. Native foreign-gold cases similarly accepted the
sentinel before and return null/unmeasured afterward. These are unsafe acceptance
controls, never credited benchmark measurements.

There are 13 controls per dataset: generated task/digest contract; buffer identity
despite replacement after read; foreign gold; foreign spec; four receipt defects;
matching native receipt; missing selected task; native unchanged/foreign/unbound
check execution. Native integration uses real `_materialize`, real shared check
and real verdict-file consumption, intercepting only process launch and scorer
import. The spy returns 0.25 solely to detect whether a scorer was reached and
whether native dispatch preserved or suppressed its output. **No dataset `score`,
`score_prediction`, family constructor or game engine is called.**

- `reports/w-tbi-evidence/tests-before.txt`: final 156-test baseline receipt.
- `reports/w-tbi-evidence/tests-after.txt`: final 156-test updated receipt, including
  every selected/foreign task/digest and all native integration outcomes.
- `reports/w-tbi-evidence/tests-before-initial.txt` and `tests-after-initial.txt`:
  preserved initial 108-test receipts (96 failed/12 passed → 108 passed).
- `reports/w-tbi-evidence/tests-regression.txt`: **113 passed**, ordinary verifier,
  unmeasured/trials, pristine binding and source-only registry regressions.
- `reports/w-tbi-evidence/audit.py` and `input-source-audit.jsonl`: freshly rehashed
  source artifacts, manifests, implementation bytes and exact source excerpts.
- `reports/w-tbi-validation.txt`: exact commands, checker and full focused output.

Socket connections are denied and CUDA visibility is disabled by the new controls.
All pytest basetemps are outside the platform tree. The temporary baseline worktree
is removed after preserving its raw output. `runs/` and frozen receipts are untouched.

## Scope limits and exact registry observation

This binds the bytes consumed by the shared check to the expected bytes of its
trusted selected verifier spec and checks the task label independently at native
dispatch. It does not authenticate an arbitrary spec or receipt, prove upstream
row provenance, or defeat a trusted caller consistently relabeling the wrong record.
Identical gold bytes from two tasks are indistinguishable as bytes and need not
change scoring; task association still relies on the trusted record-to-spec mapping.
Complete execution-selected interpreter/import/native custody and lifecycle are
not established. Legacy cached verdicts and external readers are not retroactively
upgraded; consumers bypassing native `_verify` must enforce their own independent
expected identity. Source-only provisioning and scorer/input controls do not
authorize an H0 pilot.

Task-bound scorer inputs 2026-10-15 - w-tbi: 12/19 actor-workdir routes (all 12 shared QA-command datasets) now pin the exact serialized gold bytes in a task-scoped verifier spec, recompute SHA-256 on the single buffer actually parsed for scoring, record actual/expected input identity, compare the selected task before dispatch and refuse missing/foreign/unverified input receipts before accepting a reward. Offline controls using real local task records and scorer spies refuse all 12 different-task gold substitutions before any scorer call; native mismatches are explicitly unmeasured with score=null. The same final controls change from 132 failed/24 passed to 156 passed; 113 regression tests pass. The seven native routes alfworld, bird_minidev, ds1000, jericho, livecodebench, scienceworld and spreadsheetbench remain without this binding and need their own consumed-payload contracts. This is consistency under trusted selected specs/checks, not upstream authentication, runtime custody or production authorization. S1 remains PARTIAL: complete execution-selected runtime custody and remaining task-bound inputs are still needed; S3/S4/S6 remain PARTIAL. scorer-offline-closure and every dataset blocker remain open with statuses and next_actions unchanged.
