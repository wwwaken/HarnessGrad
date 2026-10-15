# w-evidence2 disclosure row corrections

Audit target: the read-only disclosure snapshot from `/mnt/20t/xubuqiang/hg-wt/w-evidence/registry/w-evidence-disclosure.md`, identified by dataset name and exact old cell text. SHA-256 observed: `8800f44e9c304e7a4cc65539207b090db1f2cc46f17ae5d0704788d754447aec`; 10,766 bytes. The exact snapshot command/output is retained in `registry/w-evidence2-validation.txt:1`. No old table is created or edited in this worktree.

Source baseline: exact command `git rev-parse HEAD main` returned:
```text
0365c9abd5e96b4bb09b1b3f1d7faf37302c5768
0365c9abd5e96b4bb09b1b3f1d7faf37302c5768
```
All code citations below are to this assigned worktree at that baseline, not an uncommitted main-checkout file. The target worker's prose is older than this code. During audit main advanced to `786383c61dd757e0d25a00b16ad2154c2e4a6f06`; the observed name-status diff changes only documentation/registry files, and the target disclosure/qualification bytes are identical to the saved snapshots (exact diff/hash commands in validation). Its newly committed retained-source document was read through this worktree's Git object store and retained under the task's evidence scratch directory, without reading or writing the main checkout. Apply each cell replacement only if its verbatim old text still matches.

FOUND = actually read source/record, not execution. ABSENT = only an enumerated exact-path/line scope recorded below and in validation. UNKNOWN = not retrieved or not established. CURRENT certifies the readable claims/citations at their stated source scope, never execution. STALE takes precedence when an observed current mechanism disproves a cell; remaining inaccessible historical/paper support is explicitly UNKNOWN. A missing original line without a valid original citation is UNVERIFIABLE, even when a replacement mechanism was retrieved. One row has one tally status.

## All 28 rows

| dataset | result | deciding evidence / remaining boundary |
| --- | --- | --- |
| agentdojo | STALE | FOUND: `data/datasets/agentdojo/bridge.py:17` imports `load_attack`; `:23` names `ignore_previous`; `:56-58` loads and invokes it; `:79-83` returns utility and attack_success separately. `data/datasets/agentdojo.py:62-73` builds goals without the former warning and derives task count from rows; `:90-92` derives TASK_COUNT lazily. The paper-attacker distinction is explicitly documented in `data/datasets/agentdojo/bridge.py:6-7`; independent paper authentication is UNKNOWN. |
| alfworld | STALE | FOUND: `data/datasets/alfworld/lib/gym_env.py:41-44` documents upstream 50 and sets `STEP_BUDGET = 50`; `:122-128` bounds replay and accumulates won. `data/datasets/alfworld/verify/check.py:184-185` separates budget_reached from budget_exhausted; `:191` scores won. `data/datasets/alfworld/cli/alf:93-99` makes look free; `data/datasets/alfworld.py:535-540` retains harness/check resource limits. The original group counts were not recomputed; the replacement uses the local documented source and removes the unverified 47/2.85x detail. |
| api_bank | CURRENT | FOUND refusal only: `registry/dataset-blockers.json:34-45` retains the exact reason and exclusion. No refused dataset code or payload was opened. |
| appworld | CURRENT | FOUND local metric and aggregate: `data/datasets/appworld/verify/check.py:64-71`; `eval/policy/appworld_reporting.py:165-210`. During audit main advanced to 786383c6 and made the cited retained handoff readable from this worktree's object store; exact git-show command/output is in validation, with a retained on-disk excerpt at `/mnt/20t/xubuqiang/hg-work/evidence2/main-786383c6-w-evidence-external-sources.md:1326-1327` confirming pooled Test-N/Test-C and existing per-split report. `registry/dataset-blockers.json:60-63` retains the successful-task gate. CURRENT is source/attribution checking, not a successful-run claim. |
| bfcl_v3 | STALE | FOUND: `data/datasets/bfcl_v3.py:199-220` drops blank lines and NONE/no tool/no function markers, accepts bare/dotted ASCII identifiers or lines containing a call-shaped identifier, and retains those entire lines. `:230-234` compares sorted bare-name lists, preserving multiplicity. `:237-241` explicitly distinguishes this from full-call scoring. UNKNOWN: actual official scorer execution; this static audit cannot prove its global absence. |
| bird_minidev | CURRENT | FOUND: `data/datasets/bird_minidev/verify/check.py:137-138` still scores SQL EX; `:12-23` separates gold failures and Soft-F1/R-VES; `:120-133` implements unmeasured gold errors versus prediction zeros. `docs/adapter-integration-journal.md:307-310` still records partial historical coverage. Receipt authentication/re-execution is UNKNOWN. |
| chessbench_puzzles | CURRENT | FOUND: `data/datasets/chessbench_puzzles.py:6-16` still separates interactive accuracy and offline strict replay; `:309-321` returns strict reward with upstream replay diagnostic. No runtime or leaderboard comparability is established. |
| ds1000 | STALE | FOUND: `data/datasets/ds1000.py:184-189` emits only task.json with task_id/prompt; `:192-208` stages context.json under VERIFY.inputs; `:224-227` appends only solution-file instructions. `:6-16` documents prompt-only input, scorer construction and subset coverage. `data/datasets/ds1000/verify/check.py:79-89` still emits binary test_execution plus conditional test_string. |
| fever | STALE | FOUND: `data/scaffolds/qa/evidence_scorers.py:158-161` wraps a flat row as one group with `groups = [groups]`; `:165` requires all sentences. Its `:159-160` comments explicitly limit recovery of other original groups. `data/datasets/fever.py:37` names the metric; `:20-22` records claim-only input. `:53-67` retains classification counts separately from strict reward; reward is not label F1. |
| gaia | CURRENT | FOUND: `data/datasets/gaia/verify/check.py:2-14` identifies the upstream predicate and normalization branches; `:96-107` still calls question_scorer and emits binary reward. The row's source-predicate-only verdict remains appropriate; actual current execution/whole-run equivalence is UNKNOWN. |
| gsm8k | STALE | FOUND: `data/datasets/gsm8k.py:137-141` partitions at the first marker and requires STRICT_RE there; `:159-163` selects strict extraction whenever a marker exists. `:151` keeps exclusive 1e-6 tolerance; `:39-40` discloses trial averaging versus test@N. A malformed first marker does not trigger fallback (`:135-140`). |
| hotpotqa | STALE | FOUND: `data/datasets/hotpotqa.py:19` names answer F1; `:52` sets reward=f1 and correct from answer EM; `:53-58` records support and joint diagnostics. `:75-83` supplies the question and still requests supporting facts. `data/scaffolds/qa/evidence_scorers.py:111-121` still defines joint EM/F1, but that helper no longer selects the reward. |
| jericho | CURRENT | FOUND: `data/datasets/jericho/verify/check.py:7-15` states the ratio; `:142-155` still takes final replay score and divides via score_fraction. The row explicitly leaves paper selection/budget/execution UNKNOWN. |
| livecodebench | STALE | FOUND: `data/datasets/livecodebench/verify/check.py:177` is `cap = (PER_TEST_TIMEOUT + 1) * total + 5`; `:181-186` joins/kills at that cap; `:62` sets PER_TEST_TIMEOUT=6. `:201-202` calls upstream metric helper with k_list=[1]. `data/datasets/livecodebench.py:281` retains timeout_s=900. The brief's suggested :178 is now Queue construction; cite :177. |
| musique | CURRENT | FOUND: `data/datasets/musique.py:106-111` and `docs/musique-output-contract.md:26-38` still support product reward, separate official columns and scalar-only limits. The newly committed retained handoff explicitly attributes 0.3064 to a joint MuSiQue mean (`/mnt/20t/xubuqiang/hg-work/evidence2/main-786383c6-w-evidence-external-sources.md:1334-1336`, exact git-show command/output in validation). CURRENT as a handed-off attribution; historical numerical/receipt authentication remains UNKNOWN. |
| nestful | CURRENT | FOUND refusal only: `registry/dataset-blockers.json:488-499` retains the exact reason and exclusion. No refused dataset code or payload was opened. |
| physicsquestions | STALE | FOUND: `data/datasets/physicsquestions.py:100` strips whitespace/trailing periods on both sides. The old asymmetric statement in `registry/w-metriccmp-comparability.md:145-154` is itself stale relative to that code; its upstream unchanged-membership excerpt at `:125-131` still supports the remaining difference. |
| reasoning_gym | CURRENT | FOUND: `data/datasets/reasoning_gym.py:114-120` still calls family score_answer with partial reward. The newly committed retained parent plan expressly leaves max+mean unconfirmed (`/mnt/20t/xubuqiang/hg-work/evidence2/main-786383c6-w-evidence-external-sources.md:1203-1204`, exact git-show command/output in validation). The row accurately preserves that UNKNOWN; no universal official aggregate was authenticated. |
| scienceworld | STALE | FOUND: `data/datasets/scienceworld/lib/scw_env.py:42-45` sets 100 and documents truncation. `data/datasets/scienceworld.py:72-84` distinguishes the platform micro mean and separate macro; `:264-296` implements both, leaves paper_30_type_average=None, and records 29/30 coverage. `:52-56` names the missing type. The row's external handoff and fresh paper authentication remain UNKNOWN; the replacement explicitly attributes the paper description to the adapter. |
| sotuqa | CURRENT | FOUND refusal only: `registry/dataset-blockers.json:568-579` retains the exact reason and exclusion. No refused dataset code or payload was opened. |
| sportsunderstanding | STALE | FOUND: `data/datasets/sportsunderstanding.py:95-107` maps immediate negators to the complementary label and requires one resolved choice; `:89-91` enumerates excluded grammar forms. `registry/w-metriccmp-comparability.md:191-207` still shows upstream candidate-likelihood multiple_choice_grade. The row's old :71-87 now spans the helper and negation-parser documentation, not the current reward calculation. |
| spreadsheetbench | STALE | FOUND locator drift: the old `data/datasets/spreadsheetbench/verify/check.py:470-472` now prints cannot-measure and returns 3. Reward/evidence are at `:473-479`. `registry/w-metriccmp-comparability.md:390-409` still defines the three-variant soft/hard rule. This is STALE as a file:line audit even though the one-variant formula is unchanged. |
| strategyqa | CURRENT | FOUND: `data/datasets/strategyqa.py:89-100` still uses normalized whole-string EM (`:66-86`); `registry/w-stratqa-receipts.md:115-149` still documents raw JSON-value equality, and `registry/w-stratsplit-membership.md:1-15` documents installed original Train. This audits those readable sources, not a new membership replay. |
| tau2_bench | CURRENT | FOUND refusal only: `registry/dataset-blockers.json:632-643` retains the exact reason and exclusion. No refused dataset code or payload was opened. |
| tau_bench | UNVERIFIABLE | UNVERIFIABLE original line citation: `data/datasets/tau_bench/verify/check.py:307-309` does not exist; the inspected file has 297 lines (path/line census in validation). FOUND replacement mechanism: `:96-107` stops at first done/terminating tool, `:118-135` validates service recording, `:240-259` grades recorded database hash, termination and outputs. `data/datasets/tau_bench.py:28-32`, `:53-57` states service ownership and refusal of post-termination actions. Thus the old post-done/trust description is also disproved, but this row remains UNVERIFIABLE for its nonexistent original citation. |
| terminal_bench | CURRENT | FOUND: `data/datasets/terminal_bench.py:126-128`, `:231-241` still name test.sh and reward-file scoring. The row qualifies source-channel alignment only; no current runtime/snapshot success or historical score reclassification is established. |
| triviaqa | CURRENT | FOUND: `data/datasets/triviaqa.py:160-165` still returns alias-max EM; `registry/w-trivia2-review.md:216-231` still documents official key-level max EM/F1 and denominator. `registry/w-trivia4-reconciliation.md:3-23` retains whole-input/export UNKNOWNs. No new payload/key audit is claimed. |
| twowikimultihopqa | STALE | FOUND: `data/datasets/twowikimultihopqa.py:90` now declares EVIDENCE_AWARE=True; `:486-492` refuses predicted_evidence pairs; `:494-507` selects structured Joint F1 or plain-text legacy scoring. `:38-41` explicitly documents pair refusal and zero Joint for structured answer-only objects. `data/scaffolds/qa/verify/check.py:254-265` routes evidence-aware objects and classifies scorer refusal as unmeasured. The original :480-496 range now spans joint calculation and pair refusal, not legacy dispatch. |

Tally derived from the 28 dataset keys above: **CURRENT 14 / STALE 13 / UNVERIFIABLE 1**. All eight mechanisms named in the assignment are STALE; none was cleared by copying the assignment's assertion. Additional stale rows are physicsquestions, scienceworld, sportsunderstanding, spreadsheetbench (locator only), and twowikimultihopqa.

## agentdojo — STALE

FOUND: `data/datasets/agentdojo/bridge.py:17` imports `load_attack`; `:23` names `ignore_previous`; `:56-58` loads and invokes it; `:79-83` returns utility and attack_success separately. `data/datasets/agentdojo.py:62-73` builds goals without the former warning and derives task count from rows; `:90-92` derives TASK_COUNT lazily. The paper-attacker distinction is explicitly documented in `data/datasets/agentdojo/bridge.py:6-7`; independent paper authentication is UNKNOWN.

Cell: **our metric (file:line)**

Verbatim old:
```text
Utility under custom fixed injection (`data/datasets/agentdojo/bridge.py:21`, `:74-80`)
```

Exact replacement:
```text
Utility under registered ignore_previous injection (`data/datasets/agentdojo/bridge.py:23`, `:56-58`, `:77-83`)
```

Cell: **why not, if not**

Verbatim old:
```text
Warning in goal, custom attack and hard-coded inventory; utility is separate from targeted attacker success.
```

Exact replacement:
```text
Registered ignore_previous differs from the paper's important_instructions; utility is separate from targeted attacker success.
```

Effect: NUMBER/CONDITION: attack input and defence treatment changed. Earlier custom-template/warning figures must not be reused as registered-ignore_previous utility or ASR. No changed value was measured.

Comparable verdict: No headline comparison. One registered attack still differs from the documented paper attacker/suite, and utility and attacker success are separate predicates.

## alfworld — STALE

FOUND: `data/datasets/alfworld/lib/gym_env.py:41-44` documents upstream 50 and sets `STEP_BUDGET = 50`; `:122-128` bounds replay and accumulates won. `data/datasets/alfworld/verify/check.py:184-185` separates budget_reached from budget_exhausted; `:191` scores won. `data/datasets/alfworld/cli/alf:93-99` makes look free; `data/datasets/alfworld.py:535-540` retains harness/check resource limits. The original group counts were not recomputed; the replacement uses the local documented source and removes the unverified 47/2.85x detail.

Cell: **our metric (file:line)**

Verbatim old:
```text
Won within 30 actions (`data/datasets/alfworld/lib/gym_env.py:43`; `data/datasets/alfworld/verify/check.py:188`)
```

Exact replacement:
```text
Won within 50 actions (`data/datasets/alfworld/lib/gym_env.py:44`; `data/datasets/alfworld/verify/check.py:184-197`)
```

Cell: **official metric**

Verbatim old:
```text
Success on 134 valid_unseen; 50-action protocol (retained parent plan §1.1)
```

Exact replacement:
```text
Success on 134 valid_unseen; documented upstream 50-action limit (`data/datasets/alfworld.py:110`; `data/datasets/alfworld/lib/gym_env.py:41-44`)
```

Cell: **why not, if not**

Verbatim old:
```text
30 vs 50 plus free-look/harness limits; 47 groups affect uncertainty, not a 2.85x score dilution.
```

Exact replacement:
```text
Both use 50 actions; free-look and harness resource limits remain to be matched.
```

Effect: NUMBER/CONDITION: 30→50 changes the instrument. Earlier 30-action figures must not be reused as 50-action success; no actual score delta was measured.

Comparable verdict: No protocol. Free-look and remaining harness resource conditions still need matching; a 50-action match does not certify the whole protocol.

## bfcl_v3 — STALE

FOUND: `data/datasets/bfcl_v3.py:199-220` drops blank lines and NONE/no tool/no function markers, accepts bare/dotted ASCII identifiers or lines containing a call-shaped identifier, and retains those entire lines. `:230-234` compares sorted bare-name lists, preserving multiplicity. `:237-241` explicitly distinguishes this from full-call scoring. UNKNOWN: actual official scorer execution; this static audit cannot prove its global absence.

Cell: **our metric (file:line)**

Verbatim old:
```text
Bare-name multiset equality (`data/datasets/bfcl_v3.py:223-234`)
```

Exact replacement:
```text
Bare-name multiset equality (`data/datasets/bfcl_v3.py:224-234`)
```

Cell: **official metric**

Verbatim old:
```text
Full AST call and arguments; irrelevance no-call rule (`data/datasets/bfcl_v3.py:231`; retained plan §2.3.5)
```

Exact replacement:
```text
Full call including arguments; irrelevance no-call rule (`data/datasets/bfcl_v3.py:227-241`)
```

Cell: **why not, if not**

Verbatim old:
```text
Arguments ignored; arbitrary nonempty refusal lines counted as names; no official execution.
```

Exact replacement:
```text
Arguments ignored; identifier/call-shaped line filter with explicit no-call markers; no official execution established in this source review.
```

Effect: NUMBER: the irrelevance parser changed. Earlier permissive-parser name-list figures must not be reused as filtered-parser results or official AST/full-call scores. Arguments remain ungraded; no value change was measured.

Comparable verdict: No. Filtering names still does not grade arguments.

## ds1000 — STALE

FOUND: `data/datasets/ds1000.py:184-189` emits only task.json with task_id/prompt; `:192-208` stages context.json under VERIFY.inputs; `:224-227` appends only solution-file instructions. `:6-16` documents prompt-only input, scorer construction and subset coverage. `data/datasets/ds1000/verify/check.py:79-89` still emits binary test_execution plus conditional test_string.

Cell: **official metric**

Verbatim old:
```text
Prompt-only test pass protocol (retained parent plan §4.2; scorer construction `data/datasets/ds1000.py:6-10`)
```

Exact replacement:
```text
Prompt-only solver input; test_execution plus conditional test_string (`data/datasets/ds1000.py:6-12`)
```

Cell: **why not, if not**

Verbatim old:
```text
Actor-visible code_context/tests and host subset; no independent paper-input authentication in this review.
```

Exact replacement:
```text
Prompt-only SETUP; private code_context in VERIFY.inputs; host subset remains.
```

Effect: NUMBER/CONDITION: hiding private tests changes the task. Earlier actor-visible-test figures must not be reused as prompt-only DS-1000, even if their numeric value was zero. No old run was rescored.

Comparable verdict: No. Prompt-only visibility is repaired, but the adapter still reports only its host subset.

## fever — STALE

FOUND: `data/scaffolds/qa/evidence_scorers.py:158-161` wraps a flat row as one group with `groups = [groups]`; `:165` requires all sentences. Its `:159-160` comments explicitly limit recovery of other original groups. `data/datasets/fever.py:37` names the metric; `:20-22` records claim-only input. `:53-67` retains classification counts separately from strict reward; reward is not label F1.

Cell: **our metric (file:line)**

Verbatim old:
```text
Strict-at-5 with flat gold singleton alternatives (`data/scaffolds/qa/evidence_scorers.py:150-169`)
```

Exact replacement:
```text
Exported-row conjunctive strict-at-5 (`data/datasets/fever.py:37`, `:43-67`; `data/scaffolds/qa/evidence_scorers.py:155-169`)
```

Cell: **why not, if not**

Verbatim old:
```text
Flattened evidence changes conjunction; neither label F1 nor authenticated original full FEVER strict score.
```

Exact replacement:
```text
One complete exported group required; missing original alternatives and claim-only input prevent original full FEVER strict-score equivalence.
```

Effect: NUMBER: singleton alternatives became a conjunction. Earlier singleton figures must not be reused as exported-row conjunctive strict-at-5 or original full FEVER strict score; no score delta was measured.

Comparable verdict: No. Conjunction repair does not recover missing original alternatives or provide retrieval.

## gsm8k — STALE

FOUND: `data/datasets/gsm8k.py:137-141` partitions at the first marker and requires STRICT_RE there; `:159-163` selects strict extraction whenever a marker exists. `:151` keeps exclusive 1e-6 tolerance; `:39-40` discloses trial averaging versus test@N. A malformed first marker does not trigger fallback (`:135-140`).

Cell: **our metric (file:line)**

Verbatim old:
```text
Decimal-aware numeric accuracy (`data/datasets/gsm8k.py:144-156`)
```

Exact replacement:
```text
First-marker decimal-aware numeric accuracy (`data/datasets/gsm8k.py:132-169`)
```

Cell: **official metric**

Verbatim old:
```text
Normalized exact match; verifier-selected test@N (`data/datasets/gsm8k.py:18-38`)
```

Exact replacement:
```text
Normalized exact match; verifier-selected test@N (`data/datasets/gsm8k.py:18-40`)
```

Cell: **why not, if not**

Verbatim old:
```text
Last-number selection, numeric tolerance and shared trial-mean differ.
```

Exact replacement:
```text
First #### marker, last-number fallback only without a marker; numeric tolerance and shared trial-mean still differ.
```

Effect: NUMBER: extraction precedence changed. Earlier last-number figures must not be reused as first-marker decimal-aware accuracy. The value change for historical submissions is UNKNOWN; no rescore occurred.

Comparable verdict: No. Marker preference still leaves numeric tolerance and non-test@N aggregation.

## hotpotqa — STALE

FOUND: `data/datasets/hotpotqa.py:19` names answer F1; `:52` sets reward=f1 and correct from answer EM; `:53-58` records support and joint diagnostics. `:75-83` supplies the question and still requests supporting facts. `data/scaffolds/qa/evidence_scorers.py:111-121` still defines joint EM/F1, but that helper no longer selects the reward.

Cell: **our metric (file:line)**

Verbatim old:
```text
Joint EM; separate joint F1 diagnostic (`data/datasets/hotpotqa.py:46-51`)
```

Exact replacement:
```text
Answer F1 reward; answer EM correctness; support/joint diagnostics (`data/datasets/hotpotqa.py:42-58`)
```

Cell: **comparable?**

Verbatim old:
```text
Formula conditional; run no
```

Exact replacement:
```text
No official joint comparison
```

Cell: **why not, if not**

Verbatim old:
```text
Reward is joint EM, not joint F1; retained context/protocol and incomplete-receipt concerns remain.
```

Exact replacement:
```text
Question-only input; reward is answer F1; joint metrics are diagnostic only.
```

Effect: NUMBER: joint EM→answer F1 changes the statistic, not just its label. Earlier joint-EM figures must not be reused as answer F1 or joint F1. No numerical delta was measured.

Comparable verdict: No official joint comparison. Answer F1 is not the support-dependent joint statistic.

## livecodebench — STALE

FOUND: `data/datasets/livecodebench/verify/check.py:177` is `cap = (PER_TEST_TIMEOUT + 1) * total + 5`; `:181-186` joins/kills at that cap; `:62` sets PER_TEST_TIMEOUT=6. `:201-202` calls upstream metric helper with k_list=[1]. `data/datasets/livecodebench.py:281` retains timeout_s=900. The brief's suggested :178 is now Queue construction; cite :177.

Cell: **our metric (file:line)**

Verbatim old:
```text
One-generation pass@1, 600s-clamped global timeout (`data/datasets/livecodebench/verify/check.py:178`, `:194-203`)
```

Exact replacement:
```text
One-generation pass@1, upstream-scaled child timeout (`data/datasets/livecodebench/verify/check.py:177-186`, `:193-210`)
```

Cell: **official metric**

Verbatim old:
```text
All-tests pass@1/pass@k under upstream timeout (`data/datasets/livecodebench/verify/check.py:13-30`)
```

Exact replacement:
```text
All-tests pass@1/pass@k under upstream timeout (`data/datasets/livecodebench/verify/check.py:13-31`)
```

Cell: **comparable?**

Verbatim old:
```text
Not fully
```

Exact replacement:
```text
Per-generation rule aligned; not pass@N for N>1
```

Cell: **why not, if not**

Verbatim old:
```text
600s clamp differs; shared N trials are not pass@N for N>1.
```

Exact replacement:
```text
Child budget is (PER_TEST_TIMEOUT+1)*tests+5; outer verifier bound remains; shared N trials are not pass@N for N>1.
```

Effect: NUMBER/CONDITION: removing the inner 600-second clamp can change results of affected submissions. Earlier capped pass@1 figures must not be reused as the revised timeout instrument. No submissions were rerun.

Comparable verdict: Per-generation rule aligned; not pass@N for N>1. One generation supports k=1, while trial averaging does not implement success-at-least-once for N>1.

## physicsquestions — STALE

FOUND: `data/datasets/physicsquestions.py:100` strips whitespace/trailing periods on both sides. The old asymmetric statement in `registry/w-metriccmp-comparability.md:145-154` is itself stale relative to that code; its upstream unchanged-membership excerpt at `:125-131` still supports the remaining difference.

Cell: **our metric (file:line)**

Verbatim old:
```text
Asymmetric accepted-spelling exact match (`data/datasets/physicsquestions.py:100-108`)
```

Exact replacement:
```text
Symmetric trailing-period/whitespace exact match (`data/datasets/physicsquestions.py:94-108`)
```

Cell: **why not, if not**

Verbatim old:
```text
Reference-only trailing-period stripping; generation preprocessing also unaligned.
```

Exact replacement:
```text
Both sides strip trailing periods and whitespace; BIG-bench uses unchanged target membership; generation processing remains unaligned.
```

Effect: NUMBER: prediction-side normalization changed. Earlier asymmetric-match figures must not be reused as symmetric-normalization results or unchanged BIG-bench target membership. No value delta was measured.

Comparable verdict: No. Symmetric normalization still differs from unchanged target membership.

## scienceworld — STALE

FOUND: `data/datasets/scienceworld/lib/scw_env.py:42-45` sets 100 and documents truncation. `data/datasets/scienceworld.py:72-84` distinguishes the platform micro mean and separate macro; `:264-296` implements both, leaves paper_30_type_average=None, and records 29/30 coverage. `:52-56` names the missing type. The row's external handoff and fresh paper authentication remain UNKNOWN; the replacement explicitly attributes the paper description to the adapter.

Cell: **our metric (file:line)**

Verbatim old:
```text
Final JVM score/100, task mean, 1000 moves (`data/datasets/scienceworld/verify/check.py:205-206`; `data/datasets/scienceworld/lib/scw_env.py:46`)
```

Exact replacement:
```text
Final JVM score/100; task micro mean; 100 moves; separate observed-type macro (`data/datasets/scienceworld/verify/check.py:205-206`; `data/datasets/scienceworld/lib/scw_env.py:45`; `data/datasets/scienceworld.py:239-296`)
```

Cell: **official metric**

Verbatim old:
```text
100-move, type-macro test-fold score (retained parent plan §2/§3)
```

Exact replacement:
```text
100-move, full 30-type macro Average (adapter source description `data/datasets/scienceworld.py:72-79`)
```

Cell: **why not, if not**

Verbatim old:
```text
Budget, task/type weighting, test-only selection, 29/30 type coverage and unaided-action status must accompany any number (`/mnt/20t/xubuqiang/Study/HarnessGrad/docs/paper-fidelity-audit-handoff.md:321-355`).
```

Exact replacement:
```text
100-move limit now matches the documented paper budget; micro and observed-type macro differ; released fold has 29/30 types and long paths truncate.
```

Effect: NUMBER/CONDITION for 1000→100 and NUMBER for micro→macro if that reporting choice is made; the default run scalar remains micro. Earlier 1000-move/task-weighted figures must not be reused as 100-move/type-macro or full 30-type Average. No historical budget or score was recomputed.

Comparable verdict: No. The implemented observed-type macro still cannot fill the missing thirtieth type.

## sportsunderstanding — STALE

FOUND: `data/datasets/sportsunderstanding.py:95-107` maps immediate negators to the complementary label and requires one resolved choice; `:89-91` enumerates excluded grammar forms. `registry/w-metriccmp-comparability.md:191-207` still shows upstream candidate-likelihood multiple_choice_grade. The row's old :71-87 now spans the helper and negation-parser documentation, not the current reward calculation.

Cell: **our metric (file:line)**

Verbatim old:
```text
Generated-text label presence accuracy (`data/datasets/sportsunderstanding.py:71-87`)
```

Exact replacement:
```text
Generated-text label accuracy with immediate-negation handling (`data/datasets/sportsunderstanding.py:81-119`)
```

Cell: **why not, if not**

Verbatim old:
```text
Text/likelihood mismatch plus negation false positive.
```

Exact replacement:
```text
Generated-text labels differ from candidate likelihoods; immediate negation is handled; broader negation forms remain outside the parser.
```

Effect: NUMBER: immediate-negation interpretation changed. Earlier label-presence figures must not be reused as revised-parser accuracy or candidate-likelihood multiple_choice_grade. No numerical delta was measured.

Comparable verdict: No. Text parsing still does not select the candidate with maximum likelihood.

## spreadsheetbench — STALE

FOUND locator drift: the old `data/datasets/spreadsheetbench/verify/check.py:470-472` now prints cannot-measure and returns 3. Reward/evidence are at `:473-479`. `registry/w-metriccmp-comparability.md:390-409` still defines the three-variant soft/hard rule. This is STALE as a file:line audit even though the one-variant formula is unchanged.

Cell: **our metric (file:line)**

Verbatim old:
```text
One-variant named-cell binary result (`data/datasets/spreadsheetbench/verify/check.py:470-472`)
```

Exact replacement:
```text
One-variant named-cell binary result (`data/datasets/spreadsheetbench/verify/check.py:473-479`)
```

Effect: LABEL/CITATION ONLY for this correction: move the locator. No changed score is inferred from line drift.

Comparable verdict: No unqualified aggregate. One variant still cannot implement the cited three-variant aggregate.

## twowikimultihopqa — STALE

FOUND: `data/datasets/twowikimultihopqa.py:90` now declares EVIDENCE_AWARE=True; `:486-492` refuses predicted_evidence pairs; `:494-507` selects structured Joint F1 or plain-text legacy scoring. `:38-41` explicitly documents pair refusal and zero Joint for structured answer-only objects. `data/scaffolds/qa/verify/check.py:254-265` routes evidence-aware objects and classifies scorer refusal as unmeasured. The original :480-496 range now spans joint calculation and pair refusal, not legacy dispatch.

Cell: **our metric (file:line)**

Verbatim old:
```text
JSON answer.txt Joint F1; text/prediction.json legacy Ans F1 (`data/datasets/twowikimultihopqa.py:480-496`; `data/scaffolds/qa/verify/check.py:251-260`)
```

Exact replacement:
```text
JSON answer.txt Joint F1; plain-text legacy Ans F1; pair-schema prediction.json refused (`data/datasets/twowikimultihopqa.py:486-507`)
```

Cell: **why not, if not**

Verbatim old:
```text
Channel must be fixed and named; shared pair schema loses triples; mixed earlier figures are not Joint F1.
```

Exact replacement:
```text
Channel must be fixed and named; pair-schema prediction.json is unmeasured; answer-only structured objects have missing-channel Joint zero; earlier mixed figures are not Joint F1.
```

Effect: NUMBER/CHANNEL: the shared JSON path no longer silently returns legacy Ans F1. Pair-schema submissions become unmeasured; structured answer-only submissions have missing-channel Joint zero. Earlier legacy/mixed-channel figures must not be reused as revised Joint F1. No historical result was rescored.

Comparable verdict: Conditional formula only. The distinct structured/legacy/refused channels remain different contracts.

## tau_bench — UNVERIFIABLE original locator; observed code correction

The original :307-309 citation is outside this file's 297-line extent. Do not count this as a CURRENT row. The replacement is supported by newly read current lines, not by the missing original citation.

Cell: **our metric (file:line)**

Verbatim old:
```text
DB hash × done × required-output predicates (`data/datasets/tau_bench/verify/check.py:307-309`)
```

Exact replacement:
```text
Service-recorded DB hash × first termination × required-output predicates (`data/datasets/tau_bench/verify/check.py:96-115`, `:240-259`)
```

Cell: **why not, if not**

Verbatim old:
```text
Mock interaction, trust/termination boundary, post-done log handling and shared trial mean.
```

Exact replacement:
```text
Service owns database/log and stops at first done/terminating tool; no independent interactive user; shared trial mean is not pass^k.
```

FOUND deciding source: `data/datasets/tau_bench.py:28-32`, `:34-42`, `:53-62`; `data/datasets/tau_bench/verify/check.py:96-135`, `:240-259`. Keep comparable? = No: service custody and termination fixes do not add independent user interaction or pass^k aggregation. NUMBER/CONDITION: earlier actor-owned/post-done figures must not be reused as the service-recorded first-termination instrument. Actual numerical change and runtime boundary validation are UNKNOWN here.

## ALFWorld budget inconsistency / discrepancy sentence

The requested inconsistency is present verbatim in the old row: metric cell “Won within 30 actions” and why-not cell “30 vs 50 plus free-look/harness limits; 47 groups affect uncertainty, not a 2.85x score dilution.” Both carry the old local 30 premise. Current `data/datasets/alfworld/lib/gym_env.py:41-44` says the documented upstream and local episode budgets are 50; `data/datasets/alfworld/verify/check.py:184-185` classifies reaching/exhausting that budget. The corrected discrepancy sentence is exactly:

> Both use 50 actions; free-look and harness resource limits remain to be matched.

Free look and resource limits are separately supported at `data/datasets/alfworld/cli/alf:93-99` and `data/datasets/alfworld.py:535-540`. No budget mismatch remains in that sentence. The 47-group premise was not independently checked and is not republished as a new finding.

## Official scorer / platform scope preamble correction

Do **not** add the proposed blanket inference that every “no official execution” is only a platform-scope limitation. FOUND: `eval/verification/verifier.py:534-555` dispatches by declared/actual route and checks selected-task binding; `:573-589` explicitly describes receipt consistency under trusted custody, not arbitrary-JSON authentication. `registry/known-red-tests.md:147-155` records a concrete selected-task admission refusal. `docs/enforcement-proof-decision.md:8-10`, `:41-46` withdraws the universal proof blocker while retaining metric documentation and realtime refusal. BFCL additionally retains a dataset-specific preflight obligation in its current next_action (`registry/dataset-blockers.json:195`; exact command/output and proposal-prefix check in validation). The proposal preserves that string and main's later append. Therefore universal proof withdrawal does not discharge dataset-specific official-execution work.

Exact sentence to add immediately **after** the existing trials paragraph, leaving that paragraph unchanged:

> Official scorer execution uses the platform's declared verifier route and applicable input/runtime admission; “no official execution established” records this review's evidence limit, while dataset-specific scorer/contract obligations remain (`eval/verification/verifier.py:490-520`, `:534-555`, `:573-589`; `docs/enforcement-proof-decision.md:41-46`; `registry/known-red-tests.md:147-155`).

UNKNOWN: actual execution of any official scorer in this audit; none was invoked. ABSENT is not asserted globally.

## Exact scope of missing evidence

The path census command and exact output are preserved in `registry/w-evidence2-validation.txt:1`. Its explicitly enumerated own-tree scope is `registry/w-evidence-external-sources.md`, `docs/paper-fidelity-audit-handoff.md`, `registry/w-evidence-disclosure.md`, and `registry/w-evidence-qualification.md`; each returned “ABSENT (exact path in own tree)”. This says nothing about the main checkout or another worker's other files. Later, main's committed retained-source document became FOUND through the own-worktree git-show read documented above; original external handoff files and original papers remain UNKNOWN. Only the three task-authorized files in the other worker's worktree were read, through read-only source snapshots; newly committed evidence was additionally read through this worktree's object store. Current row corrections never imply original-paper, receipt, runtime, split or denominator authentication.

## BFCL proposal validation

FOUND current obligation (verbatim, `registry/dataset-blockers.json:195`):

> The preflight gate is deliberately unwired in the platform (see this record's observed field, parent decision 2026-10-16); a future official-scorer execution uses `guarded_decode` from tests/fixtures/hg_bfclguard/gate.py or records why it does not.

The refused source proposal omitted this sentence. Its reproduced default dry run returned exit 1 and reported two uncovered clauses (0.21 and 0.43 coverage); semicolons are sentence boundaries under `tools/apply_blocker_proposal.py:43`, `:64-74`. The new fragment keeps the worktree's entire current next_action verbatim, then main 786383c6's already-integrated qualification append, then adds this worker's qualification. Exact-prefix checks and both successful dry-run outputs are in validation. No `--force`, `--acknowledge` or `--apply` was used.

The tool accepts the requested single-record shape (`tools/apply_blocker_proposal.py:12-13`, `:122-129`), checks sentence obligations (`:148-167`), and returns before the registry write without `--apply` (`:192-193`, `:223-233`). FOUND successful dry runs: worktree 3369→4350 next_action characters; committed-main registry snapshot 3799→4350. These are string lengths, not measurements or scorer receipts.

Final observed main is `722a129ebb8a28053832a47fd5a1715f1a90131d`. Exact `git diff --exit-code` output in validation is empty with exit 0 for `data eval tools registry/dataset-blockers.json registry/w-evidence-disclosure.md registry/w-evidence-qualification.md registry/w-evidence-external-sources.md` between 786383c6 and 722a129e. Thus the audited mechanisms, target bytes and proposal obligations also hold at that observed main. Later main revisions are UNKNOWN; the parent must recheck exact old-cell matches and current obligations at application time.
