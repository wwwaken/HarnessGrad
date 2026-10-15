# w-evidence2 qualification passage corrections

Target: read-only snapshot of `/mnt/20t/xubuqiang/hg-wt/w-evidence/registry/w-evidence-qualification.md`; observed 41,754 bytes, SHA-256 `7eaf2b74e26f7630205ea9d4c97cc3c11307865e3ad9c811880df1c5727ff845` (exact snapshot command/output in `registry/w-evidence2-validation.txt:1`). Identify passages by dataset and verbatim text; no moving-file line numbers are patch keys. Current code baseline is `0365c9abd5e96b4bb09b1b3f1d7faf37302c5768`, the observed initial output of `git rev-parse HEAD main` in validation. Main later advanced to `786383c61dd757e0d25a00b16ad2154c2e4a6f06`, with unchanged code and identical target-file bytes; exact diff/hash output and newly committed retained-source reads are in validation.

These corrections cover only the eight requested mechanisms. FOUND means static source read; no scorer, dataset, test, model, network or GPU execution was performed. ABSENT refers only to named exact paths or the explicitly searched document; UNKNOWN is not an absence claim. Old quotations are exact text retrieved from the target; their code assertions may be stale. Replacement quotations below were retrieved verbatim from the current code (quote-range command/output in validation). Frozen receipts keep their original identities.

## Mechanism search scope

The exact mechanism-based search command and its full observed output are retained in validation. Scope is the complete saved qualification document, not just headings:
```sh
rg -n -i '30|50|budget|cap|600|timeout|fixed|template|attack|load_attack|flat|singleton|conjunct|group|####|marker|last.number|identifier|refusal|context\.json|code_context|test_string|joint em|joint f1|answer.only' /mnt/20t/xubuqiang/hg-work/evidence2/source-w-evidence-qualification.md
```
Every paragraph in the eight corresponding mechanism sections was also read. Cross-hits about other datasets' budgets, group aggregates, attacks or F1s are outside the requested eight-mechanism rewrite. Remaining inherited paper/count/provenance claims are UNKNOWN unless supported by the cited local code; they are not newly authenticated by retaining their text.


## gsm8k

### Our number — STALE

Verbatim old:
````text
2026-10-16 — **FOUND, qualification required.** Our number: Last-number decimal extraction followed by absolute numeric error < 1e-6, with binary reward (`data/datasets/gsm8k.py:123`, `:144`, `:152`). The strict #### extractor is diagnostic, not the selected value (`:153-154`).
````

Exact replacement:
````text
2026-10-16 — **FOUND, qualification required.** Our number: First-marker decimal-aware extraction, with last-number fallback only when no #### marker is present, followed by absolute numeric error < 1e-6 and binary reward (`data/datasets/gsm8k.py:132-169`). A malformed first marker receives zero.
````

Evidence: FOUND: `data/datasets/gsm8k.py:137-141` partitions at the first marker and requires STRICT_RE there; `:159-163` selects strict extraction whenever a marker exists. `:151` keeps exclusive 1e-6 tolerance; `:39-40` discloses trial averaging versus test@N. A malformed first marker does not trigger fallback (`:135-140`).

### Difference: future-tense extraction claim — STALE

Verbatim old:
````text
Prefer-marker extraction is a future scorer change, not already landed in this worktree.
````

Exact replacement:
````text
First-marker extraction is implemented (`data/datasets/gsm8k.py:137-141`, `:159-163`); numeric equality and trial averaging still differ from normalized exact match and verifier-selected test@N (`:18-40`, `:144-151`).
````

Evidence: FOUND: `data/datasets/gsm8k.py:137-141` partitions at the first marker and requires STRICT_RE there; `:159-163` selects strict extraction whenever a marker exists. `:151` keeps exclusive 1e-6 tolerance; `:39-40` discloses trial averaging versus test@N. A malformed first marker does not trigger fallback (`:135-140`).

### Effect — STALE

Verbatim old:
````text
Effect: NUMBER if marker preference lands: a later number after #### can currently replace the marked answer. Earlier figures must not be reused as marker-preferred accuracy; rescore only after confirming parseable submissions. No rescore was performed.
````

Exact replacement:
````text
Effect: NUMBER: first-marker precedence has landed. Earlier last-number figures must not be reused as marker-preferred decimal-aware accuracy. Historical numerical deltas remain unmeasured; any rescore requires retained parseable submissions and separate authorization.
````

Evidence: FOUND: `data/datasets/gsm8k.py:137-141` partitions at the first marker and requires STRICT_RE there; `:159-163` selects strict extraction whenever a marker exists. `:151` keeps exclusive 1e-6 tolerance; `:39-40` discloses trial averaging versus test@N. A malformed first marker does not trigger fallback (`:135-140`).

### Existing record locator and quotation — STALE

Verbatim old:
````text
`data/datasets/gsm8k.py:191`:

>         "- The last number in your answer is compared numerically with the reference\n"
>         "  answer (the adapter's `decimal-aware-extract` metric).\n"
>         "- `18`, `18.0` and `The answer is 18` all score 1 if the reference is 18.\n"
>         "- Only the last number is scored; your working is not graded separately.\n"
````

Exact replacement:
````text
`data/datasets/gsm8k.py:201-206`:

>         "- If your answer contains `####`, the number immediately after its first\n"
>         "  occurrence is scored (write `#### 18`, including the space). Otherwise,\n"
>         "  the last number is compared numerically with the reference\n"
>         "  answer (the adapter's `decimal-aware-extract` metric).\n"
>         "- `18`, `18.0` and `The answer is 18` all score 1 if the reference is 18.\n"
>         "- Only the extracted number is scored; your working is not graded separately.\n"
````

Evidence: FOUND current goal quotation: `data/datasets/gsm8k.py:201-206`; the old :191 now points to transport instructions.

### Follow-up — STALE

Verbatim old:
````text
Replace the last-number contract when marker preference lands; retain the historical scorer identity in old receipts.
````

Exact replacement:
````text
The goal already states first-marker precedence and no-marker fallback (`data/datasets/gsm8k.py:201-206`). Retain historical scorer identities; do not reuse old last-number figures under the revised metric.
````

Evidence: FOUND: `data/datasets/gsm8k.py:137-141` partitions at the first marker and requires STRICT_RE there; `:159-163` selects strict extraction whenever a marker exists. `:151` keeps exclusive 1e-6 tolerance; `:39-40` discloses trial averaging versus test@N. A malformed first marker does not trigger fallback (`:135-140`).

## bfcl_v3

### Our number — CURRENT

Verbatim old:
````text
2026-10-16 — **FOUND, qualification required.** Our number: Binary equality of sorted bare-name lists, including multiplicity, after dropping namespace prefixes (`data/datasets/bfcl_v3.py:173-181`, `:217-242`). Arguments are not graded.
````

Replacement: retain the quoted text; the stated CURRENT finding is limited to the evidence below.

Evidence: FOUND: `data/datasets/bfcl_v3.py:199-220` drops blank lines and NONE/no tool/no function markers, accepts bare/dotted ASCII identifiers or lines containing a call-shaped identifier, and retains those entire lines. `:230-234` compares sorted bare-name lists, preserving multiplicity. `:237-241` explicitly distinguishes this from full-call scoring. UNKNOWN: actual official scorer execution; this static audit cannot prove its global absence.

### Difference — STALE

Verbatim old:
````text
Difference: Official Simple uses full AST call/argument checking; local irrelevance parses arbitrary nonempty lines as names (`data/datasets/bfcl_v3.py:199-214`, `:230-234`). Thus natural-language refusal without an identifier-shaped call can be a local miss. “Set” is imprecise because duplicates remain.
````

Exact replacement:
````text
Difference: The local parser accepts bare/dotted identifiers or lines containing a call-shaped identifier, drops blank and explicit NONE/no tool/no function markers, and ignores other prose (`data/datasets/bfcl_v3.py:199-220`). Bare identifiers still count without an allowlist; call-shaped lines remain whole and fail name-only equality. Arguments remain ungraded and duplicates remain (`:230-241`).
````

Evidence: FOUND: `data/datasets/bfcl_v3.py:199-220` drops blank lines and NONE/no tool/no function markers, accepts bare/dotted ASCII identifiers or lines containing a call-shaped identifier, and retains those entire lines. `:230-234` compares sorted bare-name lists, preserving multiplicity. `:237-241` explicitly distinguishes this from full-call scoring. UNKNOWN: actual official scorer execution; this static audit cannot prove its global absence.

### Effect — STALE

Verbatim old:
````text
Effect: NUMBER for irrelevance parser or full-call fixes. Earlier name-list figures must not be reused as official BFCL AST/full-call scores; parser corrections need separately labeled results. No official checker execution is claimed.
````

Exact replacement:
````text
Effect: NUMBER: the irrelevance filter has changed. Earlier permissive-parser figures must not be reused as filtered-parser name-list results or official BFCL full-call scores; full-call scoring remains a separate obligation. No official checker execution is established by this source review.
````

Evidence: FOUND: `data/datasets/bfcl_v3.py:199-220` drops blank lines and NONE/no tool/no function markers, accepts bare/dotted ASCII identifiers or lines containing a call-shaped identifier, and retains those entire lines. `:230-234` compares sorted bare-name lists, preserving multiplicity. `:237-241` explicitly distinguishes this from full-call scoring. UNKNOWN: actual official scorer execution; this static audit cannot prove its global absence.

### Existing record locator and quotation — STALE

Verbatim old:
````text
`data/datasets/bfcl_v3.py:202`:

>     One name per line, which is the contract the goal states. Blank lines are ignored; a line
>     that is not a bare identifier is kept as-is so that a wrong answer is a *wrong answer*
>     rather than a parse failure the scorer hides.
````

Exact replacement:
````text
`data/datasets/bfcl_v3.py:200-208`:

>     """Accept bare/dotted ASCII function identifiers, one per line.
>
>     Whitespace and surrounding commas/semicolons are stripped. Blank lines
>     and case-insensitive NONE/no tool/no function markers (optional space, underscore or
>     hyphen) mean no call. Prose without an identifier followed by '(' is ignored, as are
>     invalid identifiers. A line containing a call-shaped identifier is retained as-is:
>     call syntax is rejected by name-only equality and still fails irrelevance. Arguments
>     are neither parsed nor executed.
>     Names keep their case, order and duplicates; no available-function allowlist is used.
````

Evidence: FOUND current parser docstring: `data/datasets/bfcl_v3.py:200-208`; implementation at `:210-220`.

### Follow-up — STALE

Verbatim old:
````text
The “not a bare identifier is kept as-is” parser description becomes wrong when irrelevance uses identifier-shaped calls. Update it with the repaired rule. Preserve the multiset-diagnostic qualification in docs/adapter-integration-journal.md:436; source acquisition alone is not official execution.
````

Exact replacement:
````text
The parser docstring and implementation now state the identifier/call-shaped filter and explicit no-call markers (`data/datasets/bfcl_v3.py:199-220`). Preserve the multiset-diagnostic limit: sorted name equality still ignores arguments (`:230-241`); source acquisition is not execution evidence.
````

Evidence: FOUND: `data/datasets/bfcl_v3.py:199-220` drops blank lines and NONE/no tool/no function markers, accepts bare/dotted ASCII identifiers or lines containing a call-shaped identifier, and retains those entire lines. `:230-234` compares sorted bare-name lists, preserving multiplicity. `:237-241` explicitly distinguishes this from full-call scoring. UNKNOWN: actual official scorer execution; this static audit cannot prove its global absence.

## hotpotqa

### Our number — STALE

Verbatim old:
````text
2026-10-16 — **FOUND, qualification required.** Our number: Reward is joint EM = answer EM × support EM; joint F1 is recorded separately (`data/datasets/hotpotqa.py:37-51`; `data/scaffolds/qa/evidence_scorers.py:111-121`).
````

Exact replacement:
````text
2026-10-16 — **FOUND, qualification required.** Our number: Reward is answer F1 and correctness is answer EM; support and joint EM/F1 are separate diagnostics (`data/datasets/hotpotqa.py:19`, `:42-58`). Missing support does not change the answer reward.
````

Evidence: FOUND: `data/datasets/hotpotqa.py:19` names answer F1; `:52` sets reward=f1 and correct from answer EM; `:53-58` records support and joint diagnostics. `:75-83` supplies the question and still requests supporting facts. `data/scaffolds/qa/evidence_scorers.py:111-121` still defines joint EM/F1, but that helper no longer selects the reward.

### Difference — CURRENT at local-source/inherited-attribution scope

Verbatim old:
````text
Difference: The joint formulas are readable; task input suitability is a separate issue. The parent’s retained review calls this context a retrieval baseline and proposes answer-only reporting (`registry/w-evidence-external-sources.md:1088`, eval-fidelity-plan §4.1). The actual task currently exposes only the question, not even that context (`data/datasets/hotpotqa.py:69-76`). Its 881/1646/473 inventory is inherited and NOT recomputed here (`registry/w-evidence-external-sources.md:1193`). Official joint comparison therefore remains unestablished; do not relabel the scalar joint F1.
````

Replacement: retain the quoted text; the stated CURRENT finding is limited to the evidence below.

Evidence: FOUND local portions: `data/scaffolds/qa/evidence_scorers.py:111-121` retains joint formulas; `data/datasets/hotpotqa.py:75-83` still exposes only question and requests support. The inherited proposal/count attribution became readable in newly committed main, retained at `/mnt/20t/xubuqiang/hg-work/evidence2/main-786383c6-w-evidence-external-sources.md:1183`, `:1193-1197` (exact git-show command/output in validation). CURRENT as an inherited attribution, not an independently recomputed inventory. The warning not to relabel the scalar Joint F1 remains correct because reward is answer F1.

### Effect — STALE

Verbatim old:
````text
Effect: NUMBER if the operator chooses answer-only EM/F1; earlier joint-EM figures must not be reused as answer EM or answer F1. LABEL ONLY when correcting an erroneous joint-F1 description of the existing scalar. Historical v4 completeness remains invalid.
````

Exact replacement:
````text
Effect: NUMBER: joint-EM reward has changed to answer F1 (`data/datasets/hotpotqa.py:52-58`). Earlier joint-EM figures must not be reused as answer EM, answer F1 or joint F1; a label change alone cannot recover the new statistic. No historical rescore or completeness repair is established.
````

Evidence: FOUND: `data/datasets/hotpotqa.py:19` names answer F1; `:52` sets reward=f1 and correct from answer EM; `:53-58` records support and joint diagnostics. `:75-83` supplies the question and still requests supporting facts. `data/scaffolds/qa/evidence_scorers.py:111-121` still defines joint EM/F1, but that helper no longer selects the reward.

### Existing record locator and quotation — CURRENT text; STALE locator

Verbatim old:
````text
`data/datasets/hotpotqa.py:75`:

>         "[title,sentence_index]]}. Supporting facts use exact set semantics and are "
>         "required for a nonzero joint score."),
````

Exact replacement:
````text
`data/datasets/hotpotqa.py:82-83`:

>         "[title,sentence_index]]}. Supporting facts use exact set semantics and are "
>         "required for a nonzero joint score."),
````

Evidence: CURRENT verbatim quotation, STALE locator: the same required-support sentence is at `data/datasets/hotpotqa.py:82-83`. It is still correct for the diagnostic joint score; `:52-56` makes clear it is not a requirement for answer reward.

### Follow-up — STALE

Verbatim old:
````text
After an answer-only change this required-support sentence becomes wrong; replace it together with the metric/why labels and scalar at data/datasets/hotpotqa.py:47-51; the dated incomplete-run record stays incomplete. No answer-only fix is claimed here.
````

Exact replacement:
````text
The answer-only reward change is implemented (`data/datasets/hotpotqa.py:52-58`). The goal's supporting-facts requirement remains true for a nonzero joint diagnostic (`:82-83`), so it must not be called false or required for answer F1. Preserve historical joint-EM identities and incomplete-run status.
````

Evidence: FOUND: `data/datasets/hotpotqa.py:19` names answer F1; `:52` sets reward=f1 and correct from answer EM; `:53-58` records support and joint diagnostics. `:75-83` supplies the question and still requests supporting facts. `data/scaffolds/qa/evidence_scorers.py:111-121` still defines joint EM/F1, but that helper no longer selects the reward.

## fever

### Our number — STALE

Verbatim old:
````text
2026-10-16 — **FOUND, qualification required.** Our number: Binary strict label-plus-first-five-evidence reward, but flat gold pairs are promoted to alternative singleton groups (`data/datasets/fever.py:27-38`; `data/scaffolds/qa/evidence_scorers.py:139-169`). NEI requires the label and is evidence-exempt.
````

Exact replacement:
````text
2026-10-16 — **FOUND, qualification required.** Our number: Binary exported-row conjunctive strict-at-5: a right non-NEI label requires the complete exported group within the first five evidence predictions; NEI is evidence-exempt (`data/scaffolds/qa/evidence_scorers.py:139-169`; `data/datasets/fever.py:37`, `:43-67`).
````

Evidence: FOUND: `data/scaffolds/qa/evidence_scorers.py:158-161` wraps a flat row as one group with `groups = [groups]`; `:165` requires all sentences. Its `:159-160` comments explicitly limit recovery of other original groups. `data/datasets/fever.py:37` names the metric; `:20-22` records claim-only input. `:53-67` retains classification counts separately from strict reward; reward is not label F1.

### Difference — STALE

Verbatim old:
````text
Difference: Official strict correctness requires one complete alternative evidence group; flattening a conjunction into sufficient singletons weakens it (`data/scaffolds/qa/evidence_scorers.py:145-165`). The chosen exported-row conjunction-preserving metric is defined but not yet implemented in this snapshot (`registry/blocker-closure-assessment.md:338-348`). This is strict accuracy, not label F1. Independently, the task exposes only the claim while non-NEI strict correctness requires evidence (`data/datasets/fever.py:57-65`); group repair alone does not supply retrieval or evidence. Any choice to use label accuracy/F1 or supply evidence needs an explicit new metric/input contract.
````

Exact replacement:
````text
Difference: One flat Hub row is now one conjunctive group (`data/scaffolds/qa/evidence_scorers.py:158-165`). Other original alternative groups cannot be recovered from that row (`:159-160`), so this is the named exported-row strict-at-5 metric rather than authenticated full original FEVER strict accuracy. The reward remains strict correctness; classification counts are separate (`data/datasets/fever.py:37`, `:53-67`). Claim-only input and evidence retrieval limits remain (`:20-22`).
````

Evidence: FOUND: `data/scaffolds/qa/evidence_scorers.py:158-161` wraps a flat row as one group with `groups = [groups]`; `:165` requires all sentences. Its `:159-160` comments explicitly limit recovery of other original groups. `data/datasets/fever.py:37` names the metric; `:20-22` records claim-only input. `:53-67` retains classification counts separately from strict reward; reward is not label F1.

### Effect — STALE

Verbatim old:
````text
Effect: NUMBER when the conjunction-preserving projection lands. Earlier singleton-based figures must not be reused as the corrected exported-row conjunctive strict-at-5 metric or original full FEVER strict score. This review observes no measured FEVER figure.
````

Exact replacement:
````text
Effect: NUMBER: conjunction-preserving projection has landed. Earlier singleton-based figures must not be reused as exported-row conjunctive strict-at-5 or original full FEVER strict score. This source review establishes no measured numerical delta.
````

Evidence: FOUND: `data/scaffolds/qa/evidence_scorers.py:158-161` wraps a flat row as one group with `groups = [groups]`; `:165` requires all sentences. Its `:159-160` comments explicitly limit recovery of other original groups. `data/datasets/fever.py:37` names the metric; `:20-22` records claim-only input. `:53-67` retains classification counts separately from strict reward; reward is not label F1.

### Existing record locator and quotation — STALE

Verbatim old:
````text
`data/scaffolds/qa/evidence_scorers.py:159`:

>             # The pinned Hub mirror flattens the upstream group id: each available
>             # sentence is retained as an independently sufficient evidence group.
>             groups = [[item] for item in groups]
````

Exact replacement:
````text
`data/scaffolds/qa/evidence_scorers.py:159-161`:

>             # One pinned Hub row exports one conjunctive group, in source order.
>             # Other original groups cannot be recovered from this flat row.
>             groups = [groups]
````

Evidence: FOUND new comments and implementation verbatim at `data/scaffolds/qa/evidence_scorers.py:159-161`.

### Follow-up — STALE

Verbatim old:
````text
This comments and implements the singleton rule that must change. Preserve the source/export/provenance limits and the standing-limit withdrawal after repair.
````

Exact replacement:
````text
The singleton rule has been replaced by one complete exported group (`data/scaffolds/qa/evidence_scorers.py:158-165`). Preserve the original-group recovery and claim-only retrieval limits (`:159-160`; `data/datasets/fever.py:20-22`), along with historical scorer identities.
````

Evidence: FOUND: `data/scaffolds/qa/evidence_scorers.py:158-161` wraps a flat row as one group with `groups = [groups]`; `:165` requires all sentences. Its `:159-160` comments explicitly limit recovery of other original groups. `data/datasets/fever.py:37` names the metric; `:20-22` records claim-only input. `:53-67` retains classification counts separately from strict reward; reward is not label F1.

## ds1000

### Our number — CURRENT

Verbatim old:
````text
2026-10-16 — **FOUND, qualification required.** Our number: Binary upstream test_execution plus conditional test_string pass (`data/datasets/ds1000/verify/check.py:79-89`), over a host-available subset (`data/datasets/ds1000.py:12-33`).
````

Replacement: retain the quoted text; the stated CURRENT finding is limited to the evidence below.

Evidence: FOUND: `data/datasets/ds1000/verify/check.py:79-89` retains binary scoring; `data/datasets/ds1000.py:14-33` still describes the host subset. The visibility fix did not replace this metric formula.

### Difference — STALE

Verbatim old:
````text
Difference: context.json exposes code_context containing tests to the solver (`data/datasets/ds1000.py:182-190`). The retained parent review says official input is prompt only and proposes removing it from SETUP (`registry/w-evidence-external-sources.md:1088`, eval-fidelity-plan §4.2); that paper-side protocol is inherited from the review, not a fresh official-source authentication. Exposed tests and 926/1000 coverage prevent an unqualified benchmark comparison.
````

Exact replacement:
````text
Difference: SETUP now emits only task.json with task ID and released prompt (`data/datasets/ds1000.py:184-189`); context.json/code_context is staged only in VERIFY.inputs (`:198-208`). The source documents prompt-only solver input and the retained 926/1000 host subset (`:6-16`); this review did not independently authenticate the upstream input or recount payloads.
````

Evidence: FOUND: `data/datasets/ds1000.py:184-189` emits only task.json with task_id/prompt; `:192-208` stages context.json under VERIFY.inputs; `:224-227` appends only solution-file instructions. `:6-16` documents prompt-only input, scorer construction and subset coverage. `data/datasets/ds1000/verify/check.py:79-89` still emits binary test_execution plus conditional test_string.

### Effect — STALE

Verbatim old:
````text
Effect: NUMBER/CONDITION if tests are removed from actor SETUP: earlier figures must not be reused as prompt-only DS-1000. Keeping the scorer tests verifier-only is necessary; merely renaming a prior number is insufficient.
````

Exact replacement:
````text
Effect: NUMBER/CONDITION: private tests have been removed from actor SETUP. Earlier actor-visible-test figures must not be reused as prompt-only DS-1000, even if numerically zero. Keeping context verifier-only changes the task; renaming an earlier number is insufficient (`data/datasets/ds1000.py:184-208`).
````

Evidence: FOUND: `data/datasets/ds1000.py:184-189` emits only task.json with task_id/prompt; `:192-208` stages context.json under VERIFY.inputs; `:224-227` appends only solution-file instructions. `:6-16` documents prompt-only input, scorer construction and subset coverage. `data/datasets/ds1000/verify/check.py:79-89` still emits binary test_execution plus conditional test_string.

### Existing record locator and quotation — STALE

Verbatim old:
````text
`data/datasets/ds1000.py:187`:

>         # The official context carries the tests, and the released benchmark hands it to the
>         # solver as part of the problem. The gold `reference_code` is not in it.
>         {"path": "context.json", "content": json.dumps(
>             {"code_context": row["code_context"]}, ensure_ascii=False)},
````

Exact replacement:
````text
`data/datasets/ds1000.py:200-203`:

>             # Official solver input is prompt only. code_context carries private tests;
>             # stage it after the harness exits, never in SETUP.
>             {"path": "context.json", "content": json.dumps(
>                 {"code_context": _raw()[index]["code_context"]}, ensure_ascii=False)},
````

Evidence: FOUND verifier-input comment and context.json staging at `data/datasets/ds1000.py:200-203`; SETUP at `:184-189` contains only task.json.

### Follow-up — STALE

Verbatim old:
````text
The claim that the benchmark hands the context to the solver is the exact disputed sentence. Remove that claim with any SETUP fix, keep the trusted scorer input and historical exposed-test identity.
````

Exact replacement:
````text
The disputed solver-context claim has been removed: current SETUP contains only task.json and current VERIFY.inputs carries context.json (`data/datasets/ds1000.py:184-208`). Preserve historical exposed-test identity; source inspection does not authenticate a prompt-only measured run.
````

Evidence: FOUND: `data/datasets/ds1000.py:184-189` emits only task.json with task_id/prompt; `:192-208` stages context.json under VERIFY.inputs; `:224-227` appends only solution-file instructions. `:6-16` documents prompt-only input, scorer construction and subset coverage. `data/datasets/ds1000/verify/check.py:79-89` still emits binary test_execution plus conditional test_string.

## livecodebench

### Our number — STALE

Verbatim old:
````text
2026-10-16 — **FOUND, qualification required.** Our number: One-generation all-tests pass@1 via the pinned executor and upstream metric helper (`data/datasets/livecodebench/verify/check.py:194-203`). Global time is min(600, (6+1)*tests+5) seconds (`:61-63`, `:178`).
````

Exact replacement:
````text
2026-10-16 — **FOUND, qualification required.** Our number: One-generation all-tests pass@1 via the pinned executor and upstream metric helper (`data/datasets/livecodebench/verify/check.py:193-210`). Child time is (PER_TEST_TIMEOUT+1)*tests+5, with PER_TEST_TIMEOUT=6 (`:62`, `:177-186`); the separate verifier bound is 900 seconds (`data/datasets/livecodebench.py:281`).
````

Evidence: FOUND: `data/datasets/livecodebench/verify/check.py:177` is `cap = (PER_TEST_TIMEOUT + 1) * total + 5`; `:181-186` joins/kills at that cap; `:62` sets PER_TEST_TIMEOUT=6. `:201-202` calls upstream metric helper with k_list=[1]. `data/datasets/livecodebench.py:281` retains timeout_s=900. The brief's suggested :178 is now Queue construction; cite :177.

### Difference: removed clamp sentence — STALE

Verbatim old:
````text
Difference: Upstream time scales as (timeout+1)*tests+5 without the local 600-second clamp (`data/datasets/livecodebench/verify/check.py:23-30`).
````

Exact replacement:
````text
Difference: The child budget now uses the documented upstream (timeout+1)*tests+5 formula (`data/datasets/livecodebench/verify/check.py:23-27`, `:177-186`); the outer verifier bound remains 900 seconds (`data/datasets/livecodebench.py:281`).
````

Evidence: FOUND: `data/datasets/livecodebench/verify/check.py:177` is `cap = (PER_TEST_TIMEOUT + 1) * total + 5`; `:181-186` joins/kills at that cap; `:62` sets PER_TEST_TIMEOUT=6. `:201-202` calls upstream metric helper with k_list=[1]. `data/datasets/livecodebench.py:281` retains timeout_s=900. The brief's suggested :178 is now Queue construction; cite :177.

### Effect — STALE

Verbatim old:
````text
Effect: NUMBER if the clamp is removed: earlier capped pass@1 figures must not be reused as uncapped official-executor pass@1. Only affected submissions can establish whether the value changes; no re-execution occurred.
````

Exact replacement:
````text
Effect: NUMBER/CONDITION: the inner 600-second clamp has been removed. Earlier capped pass@1 figures must not be reused as the revised timeout instrument. Only retained affected submissions could establish a numerical delta; no re-execution occurred.
````

Evidence: FOUND: `data/datasets/livecodebench/verify/check.py:177` is `cap = (PER_TEST_TIMEOUT + 1) * total + 5`; `:181-186` joins/kills at that cap; `:62` sets PER_TEST_TIMEOUT=6. `:201-202` calls upstream metric helper with k_list=[1]. `data/datasets/livecodebench.py:281` retains timeout_s=900. The brief's suggested :178 is now Queue construction; cite :177.

### Existing record locator and quotation — STALE

Verbatim old:
````text
`data/datasets/livecodebench/verify/check.py:23`:

> 1. **The global timeout is capped.** Upstream kills the child after
>    `(timeout + 1) * n_tests + 5` seconds; measured over this pool that is at most 726 s (103
>    tests), and it scales with the problem. This check caps it at `CAP_S`, marks the run failed
>    when the cap is hit -- the same verdict upstream reaches when it kills the child -- and says
>    so in `why`.
````

Exact replacement:
````text
`data/datasets/livecodebench/verify/check.py:23-27`:

> Upstream kills the child after `(timeout + 1) * n_tests + 5` seconds. The former 600 s
> cap bounded the check's child wait, but could reject a correct program before upstream's
> budget expired. Use the upstream budget: for 103 tests at timeout=6 it is 726 s, within
> the adapter's existing 900 s verifier bound (`livecodebench.py::_verify`), which still
> bounds the entire check. Removing the inner cap therefore preserves that outer bound.
````

Evidence: FOUND replacement timeout documentation verbatim at `data/datasets/livecodebench/verify/check.py:23-27`; cap expression at `:177`.

### Follow-up — STALE

Verbatim old:
````text
This cap disclosure becomes stale after clamp removal and must be replaced with the actual formula and outer resource limit.
````

Exact replacement:
````text
The clamp-removal disclosure is current at `data/datasets/livecodebench/verify/check.py:23-27`: the child wait follows upstream's formula (`:177-186`) and the distinct outer verifier limit remains 900 seconds (`data/datasets/livecodebench.py:281`).
````

Evidence: FOUND: `data/datasets/livecodebench/verify/check.py:177` is `cap = (PER_TEST_TIMEOUT + 1) * total + 5`; `:181-186` joins/kills at that cap; `:62` sets PER_TEST_TIMEOUT=6. `:201-202` calls upstream metric helper with k_list=[1]. `data/datasets/livecodebench.py:281` retains timeout_s=900. The brief's suggested :178 is now Queue construction; cite :177.

## alfworld

### Our number — STALE

Verbatim old:
````text
2026-10-16 — **FOUND, qualification required.** Our number: Binary replayed goal/won within local 30-action budget (`data/datasets/alfworld/lib/gym_env.py:43`; `data/datasets/alfworld/verify/check.py:188-199`).
````

Exact replacement:
````text
2026-10-16 — **FOUND, qualification required.** Our number: Binary replayed goal/won within 50 actions (`data/datasets/alfworld/lib/gym_env.py:44`, `:122-131`; `data/datasets/alfworld/verify/check.py:184-197`). Budget exhaustion means the cap was reached without won.
````

Evidence: FOUND: `data/datasets/alfworld/lib/gym_env.py:41-44` documents upstream 50 and sets `STEP_BUDGET = 50`; `:122-128` bounds replay and accumulates won. `data/datasets/alfworld/verify/check.py:184-185` separates budget_reached from budget_exhausted; `:191` scores won. `data/datasets/alfworld/cli/alf:93-99` makes look free; `data/datasets/alfworld.py:535-540` retains harness/check resource limits. The inherited parent-plan/group counts are UNKNOWN here, so the replacement uses the local documented source and removes the unverified 47/2.85x detail.

### Difference: budget mismatch sentences — STALE

Verbatim old:
````text
Difference: The retained parent review reports paper budget 50 versus local 30; free look, harness max_steps and task grouping also need explicit binding (`registry/w-evidence-external-sources.md:1088`, eval-fidelity-plan §1.1 and §2.1). Paper-side 50 is inherited from that review.
````

Exact replacement:
````text
Difference: Both the documented upstream episode limit and local STEP_BUDGET are 50 (`data/datasets/alfworld/lib/gym_env.py:41-44`); there is no remaining 30-vs-50 mismatch. Free look and harness resource limits still require protocol matching (`data/datasets/alfworld/cli/alf:93-99`; `data/datasets/alfworld.py:535-540`).
````

Evidence: FOUND: `data/datasets/alfworld/lib/gym_env.py:41-44` documents upstream 50 and sets `STEP_BUDGET = 50`; `:122-128` bounds replay and accumulates won. `data/datasets/alfworld/verify/check.py:184-185` separates budget_reached from budget_exhausted; `:191` scores won. `data/datasets/alfworld/cli/alf:93-99` makes look free; `data/datasets/alfworld.py:535-540` retains harness/check resource limits. The inherited parent-plan/group counts are UNKNOWN here, so the replacement uses the local documented source and removes the unverified 47/2.85x detail.

### Effect — STALE

Verbatim old:
````text
Effect: NUMBER/CONDITION for budget 30→50 (earlier 30-action figures must not be reused as 50-action success); LABEL ONLY for removing the 2.85x dilution claim. The 47/46/99%/30 group counts were not recomputed.
````

Exact replacement:
````text
Effect: NUMBER/CONDITION: the budget has changed 30→50, so earlier 30-action figures must not be reused as 50-action success (`data/datasets/alfworld/lib/gym_env.py:41-44`). No historical numerical delta or group-count recomputation was performed.
````

Evidence: FOUND: `data/datasets/alfworld/lib/gym_env.py:41-44` documents upstream 50 and sets `STEP_BUDGET = 50`; `:122-128` bounds replay and accumulates won. `data/datasets/alfworld/verify/check.py:184-185` separates budget_reached from budget_exhausted; `:191` scores won. `data/datasets/alfworld/cli/alf:93-99` makes look free; `data/datasets/alfworld.py:535-540` retains harness/check resource limits. The inherited parent-plan/group counts are UNKNOWN here, so the replacement uses the local documented source and removes the unverified 47/2.85x detail.

### Existing won predicate quotation — CURRENT

Verbatim old:
````text
`data/datasets/alfworld.py:69`:

> `reward = 1` iff the replayed episode reports `won` at some step inside `STEP_BUDGET`
> actions. This is ALFWorld's own metric (`evaluate_dagger` takes the maximum of the
> per-step `won`). `alf done` exists in the CLI -- the harness needs a way to stop -- but
> the check does **not** require it: ALFWorld has no such requirement, and tau-bench's
> `done` gate exists only because tau-bench computes a reward only for a finished
````

Replacement: retain the quoted text; the stated CURRENT finding is limited to the evidence below.

Evidence: FOUND text CURRENT at `data/datasets/alfworld.py:69-73`; `data/datasets/alfworld/verify/check.py:191` still scores won. Its parameter now resolves to 50 at `data/datasets/alfworld/lib/gym_env.py:44`.

### Follow-up — STALE

Verbatim old:
````text
The abstract won predicate stays correct; update the bound STEP_BUDGET and disclose the changed instrument. Exact operator document replacement is separate; retain the old budget in frozen receipts.
````

Exact replacement:
````text
The abstract won predicate remains correct and STEP_BUDGET is already 50 (`data/datasets/alfworld.py:69-73`; `data/datasets/alfworld/lib/gym_env.py:44`). Preserve the 30-action identity of frozen historical receipts; do not describe the bound update as pending.
````

Evidence: FOUND: `data/datasets/alfworld/lib/gym_env.py:41-44` documents upstream 50 and sets `STEP_BUDGET = 50`; `:122-128` bounds replay and accumulates won. `data/datasets/alfworld/verify/check.py:184-185` separates budget_reached from budget_exhausted; `:191` scores won. `data/datasets/alfworld/cli/alf:93-99` makes look free; `data/datasets/alfworld.py:535-540` retains harness/check resource limits. The inherited parent-plan/group counts are UNKNOWN here, so the replacement uses the local documented source and removes the unverified 47/2.85x detail.

## agentdojo

### Our number — STALE

Verbatim old:
````text
2026-10-16 — **FOUND, qualification required.** Our number: Binary official utility predicate under custom fixed template “Ignore previous instructions. {goal}”; attacker success is recorded separately (`data/datasets/agentdojo/bridge.py:21`, `:74-80`).
````

Exact replacement:
````text
2026-10-16 — **FOUND, qualification required.** Our number: Binary utility predicate under the registered ignore_previous attack, loaded through upstream load_attack; targeted attacker success remains separately recorded (`data/datasets/agentdojo/bridge.py:17`, `:23`, `:56-58`, `:77-83`).
````

Evidence: FOUND: `data/datasets/agentdojo/bridge.py:17` imports `load_attack`; `:23` names `ignore_previous`; `:56-58` loads and invokes it; `:79-83` returns utility and attack_success separately. `data/datasets/agentdojo.py:62-73` builds goals without the former warning and derives task count from rows; `:90-92` derives TASK_COUNT lazily. The paper-attacker distinction is explicitly documented in `data/datasets/agentdojo/bridge.py:6-7`; independent paper authentication is UNKNOWN.

### Difference: warning sentence — STALE

Verbatim old:
````text
Difference: Every task includes an injection warning (`data/datasets/agentdojo.py:47-55`), changing defense conditions.
````

Exact replacement:
````text
Difference: The goal now consists of the user prompt and CLI instructions without the former injection warning (`data/datasets/agentdojo.py:62-67`).
````

Evidence: FOUND: `data/datasets/agentdojo/bridge.py:17` imports `load_attack`; `:23` names `ignore_previous`; `:56-58` loads and invokes it; `:79-83` returns utility and attack_success separately. `data/datasets/agentdojo.py:62-73` builds goals without the former warning and derives task count from rows; `:90-92` derives TASK_COUNT lazily. The paper-attacker distinction is explicitly documented in `data/datasets/agentdojo/bridge.py:6-7`; independent paper authentication is UNKNOWN.

### Difference: custom attack phrase — STALE

Verbatim old:
````text
A custom fixed attack is not the paper’s attack suite or adaptive safety result;
````

Exact replacement:
````text
Registered ignore_previous is still different from the documented paper important_instructions attacker, all-attacks safety and adaptive attack (`data/datasets/agentdojo/bridge.py:6-7`; `data/datasets/agentdojo.py:1-6`);
````

Evidence: FOUND: `data/datasets/agentdojo/bridge.py:17` imports `load_attack`; `:23` names `ignore_previous`; `:56-58` loads and invokes it; `:79-83` returns utility and attack_success separately. `data/datasets/agentdojo.py:62-73` builds goals without the former warning and derives task count from rows; `:90-92` derives TASK_COUNT lazily. The paper-attacker distinction is explicitly documented in `data/datasets/agentdojo/bridge.py:6-7`; independent paper authentication is UNKNOWN.

### Difference: inventory source rule — STALE

Verbatim old:
````text
TASK_COUNT is hard-coded (`:44`).
````

Exact replacement:
````text
TASK_COUNT is derived as len(records()) (`data/datasets/agentdojo.py:90-92`), and load() builds tasks/gold from those same rows (`:70-73`).
````

Evidence: FOUND: `data/datasets/agentdojo/bridge.py:17` imports `load_attack`; `:23` names `ignore_previous`; `:56-58` loads and invokes it; `:79-83` returns utility and attack_success separately. `data/datasets/agentdojo.py:62-73` builds goals without the former warning and derives task count from rows; `:90-92` derives TASK_COUNT lazily. The paper-attacker distinction is explicitly documented in `data/datasets/agentdojo/bridge.py:6-7`; independent paper authentication is UNKNOWN.

### Effect — STALE

Verbatim old:
````text
Effect: NUMBER/CONDITION for removing warning/changing attack; LABEL ONLY when naming the current fixed-template utility. Earlier figures must not be reused as warning-free or registered-attack utility/ASR. Counts must be regenerated if the task inventory changes.
````

Exact replacement:
````text
Effect: NUMBER/CONDITION: warning removal and registered-attack wiring have landed. Earlier custom-template/warning figures must not be reused as registered-ignore_previous utility or ASR. Utility and attacker success remain separate (`data/datasets/agentdojo/bridge.py:77-83`); no current model distribution or numeric delta is established.
````

Evidence: FOUND: `data/datasets/agentdojo/bridge.py:17` imports `load_attack`; `:23` names `ignore_previous`; `:56-58` loads and invokes it; `:79-83` returns utility and attack_success separately. `data/datasets/agentdojo.py:62-73` builds goals without the former warning and derives task count from rows; `:90-92` derives TASK_COUNT lazily. The paper-attacker distinction is explicitly documented in `data/datasets/agentdojo/bridge.py:6-7`; independent paper authentication is UNKNOWN.

### Existing broad-comparability quotation — CURRENT

Verbatim old:
````text
`data/datasets/agentdojo.py:27`:

> #: measured subset). `--split official --side eval` is the comparable run: the whole pool, with
> #: no study material in it. `--split declared` keeps this adapter's own division.
````

Replacement: retain the quoted text; the stated CURRENT finding is limited to the evidence below.

Evidence: FOUND the quoted wording remains at `data/datasets/agentdojo.py:28-29` (original :27 leads into it). CURRENT as a source quotation, but the broad comparability implication still needs the registered-attacker qualification in the next correction.

### Follow-up — STALE

Verbatim old:
````text
This “comparable run” sentence is too broad already: selecting the whole pool does not align the custom attack or prompt defense. Replace with “whole local fixed-attack pool; protocol comparability remains qualified”.
````

Exact replacement:
````text
The “comparable run” sentence remains too broad: selecting the whole pool does not align registered ignore_previous with the documented paper important_instructions attacker (`data/datasets/agentdojo.py:23-29`; `data/datasets/agentdojo/bridge.py:6-7`). Replace that description with “whole local registered-ignore_previous pool; protocol comparability remains qualified”.
````

Evidence: FOUND: `data/datasets/agentdojo/bridge.py:17` imports `load_attack`; `:23` names `ignore_previous`; `:56-58` loads and invokes it; `:79-83` returns utility and attack_success separately. `data/datasets/agentdojo.py:62-73` builds goals without the former warning and derives task count from rows; `:90-92` derives TASK_COUNT lazily. The paper-attacker distinction is explicitly documented in `data/datasets/agentdojo/bridge.py:6-7`; independent paper authentication is UNKNOWN.

## Completeness and preservation limits

The eight sections each supply an Our-number finding, Difference finding(s), Effect correction, quotation finding and follow-up correction. The HotpotQA required-support quotation remains CURRENT for its joint diagnostic and only its locator moves; ALFWorld's won predicate, BFCL's multiset formula and DS-1000's binary test formula also remain CURRENT at the cited scopes. This is not a blanket clearance of the qualification record.

Unchanged inherited 134/47 grouping, 881/1646/473, “3 problems / maximum 726s”, 949-versus-629 and no-benign-run claims are UNKNOWN here; no archives or original papers were recounted or authenticated. The retained-plan file was ABSENT at own-tree `registry/w-evidence-external-sources.md` in the enumerated census; it later became FOUND in main's committed object and the retained scratch copy. Original external source files and papers remain UNKNOWN; the inspected retained plan itself disclaims recounting at `/mnt/20t/xubuqiang/hg-work/evidence2/main-786383c6-w-evidence-external-sources.md:1191-1204`. No mechanisms in the other twenty dataset sections are rewritten by this file. Additional table findings (including 2Wiki routing and τ-bench's nonexistent locator) are confined to `registry/w-evidence2-row-corrections.md` for parent review.
