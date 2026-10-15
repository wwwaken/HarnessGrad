# Per-dataset metric qualification — w-evidence

Dated 2026-10-16; source snapshot `5e5441cc48f3ce79390895f8159e0666ff944587`. This is correction text for parent review, with no registry status change, measurement, model, GPU, network, rescore or run authorization. Frozen records keep their original identities.

**FOUND** means source or retained record read here, not runtime execution. **ABSENT** is limited to the explicit scopes/commands in validation. **UNKNOWN** is not observed or not independently verified. Paper-side claims attributed to the parent plan/handoff are inherited claims, not fresh paper authentication; the external-source snapshot preserves the exact reviewed plan. The handoff audit was FOUND through the retained plan appendix and read at `/mnt/20t/xubuqiang/Study/HarnessGrad/docs/paper-fidelity-audit-handoff.md:1`; selected excerpts are retained in `registry/w-evidence-external-sources.md:1315`. The separate intern original remains UNKNOWN as an independent document (the plan says it was chat context). The “17 of 21” scope is inherited from the assignment; six affected datasets are marked must-fix in the handoff: physicsquestions, sportsunderstanding, hotpotqa, alfworld, agentdojo and scienceworld (`/mnt/20t/xubuqiang/Study/HarnessGrad/docs/paper-fidelity-audit-handoff.md:107`, `:249`, `:279`, `:315`, `:327`). Severity is inherited review judgment, not a fresh score measurement.

The registry has 28 entries, of which 21 have no active blockers; appworld, bfcl_v3 and triviaqa have existing open blockers, and four entries retain permanent refusals (validation’s registry inventory). The 17 closed entries in the affected sections below plus the four explicitly cleared sections account for those 21. Closure is source/withdrawal bookkeeping and does not establish a comparable measured score (`registry/blocker-closure-assessment.md:197-205`, `:320-324`).

All scalar run means use the shared trial-mean rule in the disclosure preamble. Quotations below are exact source/record text, with conditional update instructions: a dated true observation is not rewritten as though a later fix had already existed. Where no false sentence was retrieved, that negative is scoped explicitly rather than fabricated.

## gsm8k

2026-10-16 — **FOUND, qualification required.** Our number: Last-number decimal extraction followed by absolute numeric error < 1e-6, with binary reward (`data/datasets/gsm8k.py:123`, `:144`, `:152`). The strict #### extractor is diagnostic, not the selected value (`:153-154`).

Difference: Upstream normalized exact match and verifier-selected test@N differ from this numeric trial mean (`data/datasets/gsm8k.py:18-38`; `docs/adapter-integration-journal.md:287-291`). Prefer-marker extraction is a future scorer change, not already landed in this worktree.

Effect: NUMBER if marker preference lands: a later number after #### can currently replace the marked answer. Earlier figures must not be reused as marker-preferred accuracy; rescore only after confirming parseable submissions. No rescore was performed.

Existing record to qualify or update:

`data/datasets/gsm8k.py:191`:

>         "- The last number in your answer is compared numerically with the reference\n"
>         "  answer (the adapter's `decimal-aware-extract` metric).\n"
>         "- `18`, `18.0` and `The answer is 18` all score 1 if the reference is 18.\n"
>         "- Only the last number is scored; your working is not graded separately.\n"

Replace the last-number contract when marker preference lands; retain the historical scorer identity in old receipts.

## triviaqa

2026-10-16 — **FOUND, qualification required.** Our number: Binary max normalized EM over all gold.accepted aliases (`data/datasets/triviaqa.py:137-145`, `:160-165`); no F1 scalar.

Difference: The official evaluator reports max EM and max F1 over original scorer keys, with the requested-key denominator and missing predictions counted. Local rows and measured-task means do not establish that denominator (`registry/w-trivia2-review.md:187-234`). HumanAnswers input preservation and official membership remain UNKNOWN (`registry/w-trivia4-reconciliation.md:3-23`).

Effect: LABEL/PROVENANCE now; NUMBER potentially if alias preservation, key grouping or denominator changes. Earlier row-EM figures must not be reused as official key-level EM/F1 after such a fix. No numerical effect is observed.

Existing record to qualify or update:

`data/datasets/triviaqa.py:132`:

>     The HuggingFace columns are `normalized_aliases` / `human_answers` and this config has
>     no human answers at all, so the second term is empty here. Both spellings are read
>     because the official JSON and the Hub copy differ, and a missing key must not silently
>     become an empty gold set.

This categorical no-human-answers wording is unsupported already: exported-schema absence does not prove original input incidence. Replace it with the bounded UNKNOWN in w-trivia4; preserve v2 and historical identities.

## musique

2026-10-16 — **FOUND, qualification required.** Our number: Default reward is joint F1 = answer F1 × support F1; correctness is joint EM (`data/datasets/musique.py:90-113`). Legacy mode alone returns Answer F1 (`:96-100`).

Difference: Official Answer F1, Support F1 and Answer EM are separate columns; the product is an expressly local policy (`docs/musique-output-contract.md:26-38`). The scalar is a mean of per-task products, not the product of corpus means.

Effect: LABEL ONLY for the handed-off 0.3064: call it local joint F1, never Answer F1. The value and its receipt stay unchanged. That historical identity is handed-off evidence, corroborated by the current scorer, not independently established by replaying all historical verifier records; see archive limits.

Existing record to qualify or update:

`docs/adapter-integration-journal.md:361`:

> - Finding: prior reward measured Answer F1 only. Default structured scoring now reports Answer F1, Answer EM, Support F1/EM and a labeled platform joint policy; missing support yields zero support, and trusted evidence is verifier-only

This historical pre-repair sentence remains true and must not be globally replaced. Its “prior reward” does not label the later 0.3064 archive. Exact forward correction is in w-evidence-doc-corrections.md; no literal 0.3064/Answer-F1 sentence was found in the named local scope there.

## twowikimultihopqa

2026-10-16 — **FOUND, qualification required.** Our number: JSON object in answer.txt returns official v1.1 Joint F1; plain answer text returns legacy Ans F1 (`data/datasets/twowikimultihopqa.py:480-496`). The shared prediction.json path instead takes only structured["answer"] because EVIDENCE_AWARE is not declared (`data/scaffolds/qa/verify/check.py:251-260`; declaration check in validation).

Difference: Joint F1 is the harmonic mean of product precision/recall over answer, support and triple evidence; omitted channels zero Joint (`data/datasets/twowikimultihopqa.py:14-37`). Shared pair-only prediction.json cannot encode this triple schema; it can silently select legacy scoring rather than structured scoring.

Effect: NUMBER/CHANNEL if routing is fixed: an earlier legacy or mixed-channel figure must not be reused as Joint F1. Existing mixed historical coverage is already explicitly qualified (`registry/dataset-blockers.json`, historical record twowiki-original-invalid-pilot; locator/output in validation).

Existing record to qualify or update:

`docs/adapter-integration-journal.md:374`:

> - Public contract: JSON in `answer.txt`, submitted directly or with `python3 qa/bin/qa submit @submission.json`: `{"schema_version":1,"answer":"...","supporting_facts":[["Title",0]],"evidence":[["subject","relation","object"]]}`. Context sentences display zero-based indices. Each channel can be omitted; omitted metrics and Joint are zero. Explicit empty sets retain upstream semantics. Plain text and `score_answer_only` remain explicitly labeled `legacy_answer_only`, with Ans F1 reward and no Sup/Evi/Joint claim. This adapter uses the existing text-file transport; shared `submit-json` remains the pair-only schema.

This answer.txt contract is accurate; preserve it. If generic prediction.json is rejected or extended, add its exact supported route here. Do not claim this existing text authorized the incompatible shared route.

## chessbench_puzzles

2026-10-16 — **FOUND, qualification required.** Our number: Binary offline strict legal sequence replay, with the unchecked upstream replay stored only as a diagnostic (`data/datasets/chessbench_puzzles.py:291-321`).

Difference: Official puzzle accuracy uses interactive board observations after each solver/opponent move; batch sequence answers lack that interaction (`data/datasets/chessbench_puzzles.py:6-16`). It is neither Elo nor an interactive accuracy measurement.

Effect: LABEL ONLY while keeping offline replay; NUMBER/CONDITION if an interactive controller is used. Earlier offline figures must not be reused as interactive official accuracy.

Existing record to qualify or update:

`data/datasets/chessbench_puzzles.py:11`:

> The existing QA task still accepts a space-separated sequence. Its reward is explicitly
> the offline strict replay variant, not interactive official accuracy or Elo. Every applied
> move is checked for legality, including setup and reference opponent moves. Any legal
> immediate mate succeeds and ends play; unused trailing answers are ignored. The pinned
> upstream replay, including its unchecked Board.push behavior, is retained separately as a
> diagnostic in `official.upstream`; it does not determine reward. Importing this module

This qualification already states the difference correctly. No newly wrong sentence was found in this module header or the journal ChessBench strict-replay section (docs/adapter-integration-journal.md:588-597); preserve it until any controller change, then describe both instruments.

## appworld

2026-10-16 — **FOUND, qualification required.** Our number: Binary tracker.success after replaying the recorded API calls and calling world.evaluate (`data/datasets/appworld/verify/check.py:45-56`, `:64-71`).

Difference: This is a single-task success predicate. The driver’s trial/task mean is task-goal completion (TGC), not the scenario-goal completion (SGC) aggregate. The sidecar does implement SGC as all aligned task variants succeeding in a scenario trial and reports TGC/SGC separately by source split (`eval/policy/appworld_reporting.py:155-192`, `:205-210`); it is wrong to claim SGC is absent. A pooled Test-N/Test-C mean is not either per-split report. The dated forward assessment identifies a completion-guidance instrument change (`registry/blocker-closure-assessment.md:83-87`); current guidance already names API completion (`data/datasets/appworld.py:239-243`). Official paper/protocol equivalence is not executed here; task-vs-scenario and Test-N/Test-C distinctions are corroborated by the handoff (`registry/w-evidence-external-sources.md:1326`).

Effect: CONDITION/NUMBER for guidance or scenario aggregation changes, LABEL for stating single-task success honestly. Earlier single-task figures must not be reused as a new grouped or test@N figure. The successful-measured-task blocker remains open; no new success is asserted.

Existing record to qualify or update:

`registry/blocker-closure-assessment.md:80`:

> **`appworld / successful-task-evidence`** — `PENDING-RUN`. Retained receipts, the incomplete Docker
> exit-125 attempt, the raw-versus-staged distinction and the generic protocol review are all
> `SATISFIED`. The gate itself is explicit: "only a genuine successful measured actor task under the
> staged pilot policy can do so". The review additionally found a **task-independent** completion-guidance
> gap (`data/datasets/appworld.py:234-236` versus `data/datasets/appworld/verify/check.py:45-56`) whose
> harness-side remedy would change the measurement instrument; that is an operator decision and was not
> applied. Two operator decisions are therefore outstanding: whether to authorize a diagnostic, and
> whether the actor guidance may be changed.

The dated forward assessment says the guidance remedy was not applied; current guidance is different. Append a current qualification rather than erasing the dated diagnosis. Retain every genuine-success diagnostic obligation.

## bfcl_v3

2026-10-16 — **FOUND, qualification required.** Our number: Binary equality of sorted bare-name lists, including multiplicity, after dropping namespace prefixes (`data/datasets/bfcl_v3.py:173-181`, `:217-242`). Arguments are not graded.

Difference: Official Simple uses full AST call/argument checking; local irrelevance parses arbitrary nonempty lines as names (`data/datasets/bfcl_v3.py:199-214`, `:230-234`). Thus natural-language refusal without an identifier-shaped call can be a local miss. “Set” is imprecise because duplicates remain.

Effect: NUMBER for irrelevance parser or full-call fixes. Earlier name-list figures must not be reused as official BFCL AST/full-call scores; parser corrections need separately labeled results. No official checker execution is claimed.

Existing record to qualify or update:

`data/datasets/bfcl_v3.py:202`:

>     One name per line, which is the contract the goal states. Blank lines are ignored; a line
>     that is not a bare identifier is kept as-is so that a wrong answer is a *wrong answer*
>     rather than a parse failure the scorer hides.

The “not a bare identifier is kept as-is” parser description becomes wrong when irrelevance uses identifier-shaped calls. Update it with the repaired rule. Preserve the multiset-diagnostic qualification in docs/adapter-integration-journal.md:436; source acquisition alone is not official execution.

## hotpotqa

2026-10-16 — **FOUND, qualification required.** Our number: Reward is joint EM = answer EM × support EM; joint F1 is recorded separately (`data/datasets/hotpotqa.py:37-51`; `data/scaffolds/qa/evidence_scorers.py:111-121`).

Difference: The joint formulas are readable; task input suitability is a separate issue. The parent’s retained review calls this context a retrieval baseline and proposes answer-only reporting (`registry/w-evidence-external-sources.md:1088`, eval-fidelity-plan §4.1). The actual task currently exposes only the question, not even that context (`data/datasets/hotpotqa.py:69-76`). Its 881/1646/473 inventory is inherited and NOT recomputed here (`registry/w-evidence-external-sources.md:1193`). Official joint comparison therefore remains unestablished; do not relabel the scalar joint F1.

Effect: NUMBER if the operator chooses answer-only EM/F1; earlier joint-EM figures must not be reused as answer EM or answer F1. LABEL ONLY when correcting an erroneous joint-F1 description of the existing scalar. Historical v4 completeness remains invalid.

Existing record to qualify or update:

`data/datasets/hotpotqa.py:75`:

>         "[title,sentence_index]]}. Supporting facts use exact set semantics and are "
>         "required for a nonzero joint score."),

After an answer-only change this required-support sentence becomes wrong; replace it together with the metric/why labels and scalar at data/datasets/hotpotqa.py:47-51; the dated incomplete-run record stays incomplete. No answer-only fix is claimed here.

## fever

2026-10-16 — **FOUND, qualification required.** Our number: Binary strict label-plus-first-five-evidence reward, but flat gold pairs are promoted to alternative singleton groups (`data/datasets/fever.py:27-38`; `data/scaffolds/qa/evidence_scorers.py:139-169`). NEI requires the label and is evidence-exempt.

Difference: Official strict correctness requires one complete alternative evidence group; flattening a conjunction into sufficient singletons weakens it (`data/scaffolds/qa/evidence_scorers.py:145-165`). The chosen exported-row conjunction-preserving metric is defined but not yet implemented in this snapshot (`registry/blocker-closure-assessment.md:338-348`). This is strict accuracy, not label F1. Independently, the task exposes only the claim while non-NEI strict correctness requires evidence (`data/datasets/fever.py:57-65`); group repair alone does not supply retrieval or evidence. Any choice to use label accuracy/F1 or supply evidence needs an explicit new metric/input contract.

Effect: NUMBER when the conjunction-preserving projection lands. Earlier singleton-based figures must not be reused as the corrected exported-row conjunctive strict-at-5 metric or original full FEVER strict score. This review observes no measured FEVER figure.

Existing record to qualify or update:

`data/scaffolds/qa/evidence_scorers.py:159`:

>             # The pinned Hub mirror flattens the upstream group id: each available
>             # sentence is retained as an independently sufficient evidence group.
>             groups = [[item] for item in groups]

This comments and implements the singleton rule that must change. Preserve the source/export/provenance limits and the standing-limit withdrawal after repair.

## tau_bench

2026-10-16 — **FOUND, qualification required.** Our number: Binary final database hash match AND explicit done AND all required output substrings (`data/datasets/tau_bench/verify/check.py:185-197`, `:284-309`).

Difference: Local mock-user/tool protocol differs from independent user interaction; log reading continues after done and recognizes done rather than upstream termination-tool events (`data/datasets/tau_bench/verify/check.py:156-180`; `data/datasets/tau_bench.py:35-55`). Official pass^k is not arithmetic trial mean (shared disclosure below). Actor database/log trust needs a recorded service boundary, not just matching predicates.

Effect: NUMBER/CONDITION for trusted recording, stop-at-done, or terminate-tool changes. Earlier local transaction figures must not be reused as a corrected service-backed τ-bench/pass^k figure.

Existing record to qualify or update:

`data/datasets/tau_bench.py:52`:

> * **Done is required.** Upstream calls `calculate_reward()` only when `Env.step`
>   sets `done`. There is no user simulator here that could send `###STOP###`, so
>   `tau done` records the agent's declaration in `/app/tau_calls.jsonl` and the check
>   requires it: no `done`, reward `0`, however good the database looks.

After accepting genuine upstream termination tools this categorical explicit-tau-done description becomes incomplete. Rewrite the terminal-event contract, preserving the genuine done requirement and output obligations.

## ds1000

2026-10-16 — **FOUND, qualification required.** Our number: Binary upstream test_execution plus conditional test_string pass (`data/datasets/ds1000/verify/check.py:79-89`), over a host-available subset (`data/datasets/ds1000.py:12-33`).

Difference: context.json exposes code_context containing tests to the solver (`data/datasets/ds1000.py:182-190`). The retained parent review says official input is prompt only and proposes removing it from SETUP (`registry/w-evidence-external-sources.md:1088`, eval-fidelity-plan §4.2); that paper-side protocol is inherited from the review, not a fresh official-source authentication. Exposed tests and 926/1000 coverage prevent an unqualified benchmark comparison.

Effect: NUMBER/CONDITION if tests are removed from actor SETUP: earlier figures must not be reused as prompt-only DS-1000. Keeping the scorer tests verifier-only is necessary; merely renaming a prior number is insufficient.

Existing record to qualify or update:

`data/datasets/ds1000.py:187`:

>         # The official context carries the tests, and the released benchmark hands it to the
>         # solver as part of the problem. The gold `reference_code` is not in it.
>         {"path": "context.json", "content": json.dumps(
>             {"code_context": row["code_context"]}, ensure_ascii=False)},

The claim that the benchmark hands the context to the solver is the exact disputed sentence. Remove that claim with any SETUP fix, keep the trusted scorer input and historical exposed-test identity.

## livecodebench

2026-10-16 — **FOUND, qualification required.** Our number: One-generation all-tests pass@1 via the pinned executor and upstream metric helper (`data/datasets/livecodebench/verify/check.py:194-203`). Global time is min(600, (6+1)*tests+5) seconds (`:61-63`, `:178`).

Difference: Upstream time scales as (timeout+1)*tests+5 without the local 600-second clamp (`data/datasets/livecodebench/verify/check.py:23-30`). The “3 problems / maximum 726s” count is inherited from the parent plan §5, not recomputed here. Trial averaging remains pass@1 estimation, not pass@k for k>1.

Effect: NUMBER if the clamp is removed: earlier capped pass@1 figures must not be reused as uncapped official-executor pass@1. Only affected submissions can establish whether the value changes; no re-execution occurred.

Existing record to qualify or update:

`data/datasets/livecodebench/verify/check.py:23`:

> 1. **The global timeout is capped.** Upstream kills the child after
>    `(timeout + 1) * n_tests + 5` seconds; measured over this pool that is at most 726 s (103
>    tests), and it scales with the problem. This check caps it at `CAP_S`, marks the run failed
>    when the cap is hit -- the same verdict upstream reaches when it kills the child -- and says
>    so in `why`.

This cap disclosure becomes stale after clamp removal and must be replaced with the actual formula and outer resource limit.

## strategyqa

2026-10-16 — **FOUND, qualification required.** Our number: Binary normalized whole-answer EM after lowercase, punctuation deletion, article removal and whitespace collapse (`data/datasets/strategyqa.py:69-100`).

Difference: Original Accuracy uses Python equality of JSON answer values without that normalization (`registry/w-stratqa-receipts.md:115-149`). The installed pool is original Train, not Test (`registry/w-stratsplit-membership.md:1-15`). Earlier w-metriccmp’s bounded original-source absence has been superseded.

Effect: LABEL/DISCLOSURE now; NUMBER if answer semantics or the evaluation split changes. Earlier local string EM figures must not be reused as original Accuracy on Test.

Existing record to qualify or update:

`registry/w-metriccmp-comparability.md:312`:

> StrategyQA is reported as local normalized whole-answer exact match on the ReWOO-vendored table: after shared QA input handling, lowercase strings, delete ASCII string.punctuation, remove the articles a/an/the, collapse whitespace, compare the whole strings, and average binary rewards over measured task means. The string comparison matches the retained ReWOO EM definition on identical string inputs, but local answer processing is not ReWOO's algorithm-dependent parser, and the original StrategyQA scorer and split definition were not identified in the enumerated local search scope. Do not label this original-benchmark accuracy or infer original split comparability; F1 and LLM-judge accuracy are excluded. Sources: data/scaffolds/qa/verify/check.py:132-137, :251-260; data/datasets/strategyqa.py:66-101; data/aggregation_policies.json:27; eval/run/runner.py:1225-1232; registry/w-metriccmp-sources/rewoo-Evaluator.py.txt:16-30, :174, :185-205; bounded search command/output in registry/w-metriccmp-validation.txt.

Replace the clause saying the original scorer/split were not identified with the recovered equality rule and Train-only membership. Preserve the local metric and exclusions of F1/judge accuracy.

## sportsunderstanding

2026-10-16 — **FOUND, qualification required.** Our number: Binary ASCII-letter-boundary target-label presence, rejecting answers naming both labels; negation is not interpreted (`data/datasets/sportsunderstanding.py:71-87`).

Difference: BIG-bench multiple_choice_grade chooses the maximum candidate log probability (`registry/w-metriccmp-comparability.md:189-220`). Local “not plausible” still contains plausible and can score as affirmative; this is a generated-text interpretation defect on top of the likelihood-versus-text distinction.

Effect: NUMBER for negation handling; earlier figures must not be reused as the corrected text-label metric. Even corrected text accuracy must remain separate from BIG-bench likelihood grading.

Existing record to qualify or update:

`registry/w-metriccmp-comparability.md:182`:

> These lines span the matching, dual-label and score helpers. A correct label may
> appear inside longer prose; naming both labels scores zero, regardless of context
> or negation. Task means are aggregated as above
> (`data/aggregation_policies.json:25`). The returned metadata's literal
> `"metric": "multiple_choice_grade (the correct label named)"`
> (`data/datasets/sportsunderstanding.py:87`) does not change the implemented rule.

This context/negation-insensitive rule becomes stale after a parser fix. Also retain the broader non-equivalence to candidate likelihoods.

## physicsquestions

2026-10-16 — **FOUND, qualification required.** Our number: Binary any-accepted-spelling match with prediction strip versus reference strip().rstrip(".") (`data/datasets/physicsquestions.py:93-108`). This is asymmetric.

Difference: BIG-bench exact_str_match compares unchanged target membership at the metric boundary (`registry/w-metriccmp-comparability.md:112-154`). Making trailing-period handling symmetric repairs the promised local contract but still does not establish BIG-bench generation/processing equivalence.

Effect: NUMBER for symmetric period handling; earlier asymmetric figures must not be reused as the corrected accepted-spelling metric. No new measured score is asserted.

Existing record to qualify or update:

`registry/w-metriccmp-comparability.md:94`:

> stringified and whitespace-stripped. Each reference is stringified,
> whitespace-stripped, then **all trailing periods** are removed. Case, internal
> spacing and units are otherwise exact; there is no numeric tolerance. Decisive
> comparison and per-task reward (`data/datasets/physicsquestions.py:100-108`):
>

Replace this asymmetric-rule description once both sides use the reviewed normalization; keep case/unit strictness and official-comparison caveats.

## reasoning_gym

2026-10-16 — **FOUND, qualification required.** Our number: Family-specific package score_answer on the frozen entry, including partial credit; correct means reward >= 1 (`data/datasets/reasoning_gym.py:106-124`). Driver aggregation is a measured-task mean.

Difference: The answer is passed directly to the package, with no <answer> tag extraction (`data/datasets/reasoning_gym.py:115`). No single universal family accuracy follows from partial-credit scorers; family composition and entry generation identity matter. The parent plan explicitly marks upstream max+mean aggregation unconfirmed (`registry/w-evidence-external-sources.md:1203`). UNKNOWN official paper aggregation: do not manufacture an equivalence or a max rule. Behavioural reference=1/empty=0 eligibility does not prove historical generation reproduction (`registry/blocker-closure-assessment.md:188-205`).

Effect: LABEL/DISCLOSURE pending verified aggregation evidence; NUMBER if an aggregation definition changes. Earlier pooled means must not be reused as an unverified official max+mean figure.

Existing record to qualify or update:

`registry/blocker-closure-assessment.md:197`:

> **This closes no measurement and claims no score.** `reasoning_gym` has never had a measured run, no
> coverage count is asserted anywhere, and the diagnostic-time obligations above remain requirements of any
> future diagnostic - which still needs its own authorization, a fresh run ID, a split/side binding and the
> staged pilot policy. One judgement is worth stating plainly because it is the whole difference between
> closing and staying open: the generation-receipt clause is discharged by a **recorded limit**, not by
> finding the artefact. What the census proved is that the retained readable corpus does not contain it - the
> earlier bounded regeneration differed in 84 rows across six families, and the process fields were never
> recovered. The withdrawal entry says exactly that, and does not claim a historical or unrestricted-machine
> absence.

This source-only closure is retained; it does not claim official aggregate equivalence. No sentence newly falsified by a specified landed fix was found in the local scorer or this closure section; append the aggregation UNKNOWN rather than inventing a fix.

## bird_minidev

2026-10-16 — **FOUND, qualification required.** Our number: Binary SQL EX: equality of predicted/gold result sets (`data/datasets/bird_minidev/verify/check.py:137-138`).

Difference: This is EX only; Soft-F1 and R-VES are separate unreported columns. Gold/engine failure is unmeasured locally while upstream’s broad catch makes it zero (`data/datasets/bird_minidev/verify/check.py:12-23`). Historical partial coverage also changes the denominator (`docs/adapter-integration-journal.md:307-310`).

Effect: LABEL/DENOMINATOR DISCLOSURE; NUMBER if coverage/failure classification changes. Earlier measured-subset EX figures must not be reused as full-sample EX, Soft-F1 or R-VES.

Existing record to qualify or update:

`docs/adapter-integration-journal.md:308`:

> - Scope: v5 planned 34 train-side tasks × 3 trials, `jobs=1`; only 28/34 tasks were measured (90 verify phases). The historical archive label `complete` does not certify full measurement coverage.
> - Finding: a SQL verifier can distinguish a wrong query from an environment that cannot open `database.sqlite`; measured-zero and unmeasured must remain separate
> - Evidence: `bird-minidev-h0-10pct-v5`; v5 score `0.3214285714`; v4 stalled and remains incomplete

This already names partial measurement; preserve it. No wrong metric sentence was found in the named journal section or scorer header. Add “EX over measured tasks” alongside any historical number, rather than erasing partial coverage.

## alfworld

2026-10-16 — **FOUND, qualification required.** Our number: Binary replayed goal/won within local 30-action budget (`data/datasets/alfworld/lib/gym_env.py:43`; `data/datasets/alfworld/verify/check.py:188-199`).

Difference: The retained parent review reports paper budget 50 versus local 30; free look, harness max_steps and task grouping also need explicit binding (`registry/w-evidence-external-sources.md:1088`, eval-fidelity-plan §1.1 and §2.1). Paper-side 50 is inherited from that review. The 134-row pool is the complete valid_unseen evaluation set (`data/datasets/alfworld.py:8-12`; 134 archive records counted in w-evidence-archive-observed.json). The handed-off 47 game groups concern dependence/error bars, not score dilution.

Effect: NUMBER/CONDITION for budget 30→50 (earlier 30-action figures must not be reused as 50-action success); LABEL ONLY for removing the 2.85x dilution claim. The 47/46/99%/30 group counts were not recomputed.

Existing record to qualify or update:

`data/datasets/alfworld.py:69`:

> `reward = 1` iff the replayed episode reports `won` at some step inside `STEP_BUDGET`
> actions. This is ALFWorld's own metric (`evaluate_dagger` takes the maximum of the
> per-step `won`). `alf done` exists in the CLI -- the harness needs a way to stop -- but
> the check does **not** require it: ALFWorld has no such requirement, and tau-bench's
> `done` gate exists only because tau-bench computes a reward only for a finished

The abstract won predicate stays correct; update the bound STEP_BUDGET and disclose the changed instrument. Exact operator document replacement is separate; retain the old budget in frozen receipts.

## agentdojo

2026-10-16 — **FOUND, qualification required.** Our number: Binary official utility predicate under custom fixed template “Ignore previous instructions. {goal}”; attacker success is recorded separately (`data/datasets/agentdojo/bridge.py:21`, `:74-80`).

Difference: Every task includes an injection warning (`data/datasets/agentdojo.py:47-55`), changing defense conditions. A custom fixed attack is not the paper’s attack suite or adaptive safety result; utility is not 1−targeted attacker_success; the handoff calls its complement untargeted ASR, a separate convention (`/mnt/20t/xubuqiang/Study/HarnessGrad/docs/paper-fidelity-audit-handoff.md:269-274`). TASK_COUNT is hard-coded (`:44`). The 949-versus-629 upstream pair reconciliation and no-benign-run claim are inherited, not recomputed (`/mnt/20t/xubuqiang/Study/HarnessGrad/docs/paper-fidelity-audit-handoff.md:291-303`). No targeted-ASR corpus aggregate is emitted by the scalar reward.

Effect: NUMBER/CONDITION for removing warning/changing attack; LABEL ONLY when naming the current fixed-template utility. Earlier figures must not be reused as warning-free or registered-attack utility/ASR. Counts must be regenerated if the task inventory changes.

Existing record to qualify or update:

`data/datasets/agentdojo.py:27`:

> #: measured subset). `--split official --side eval` is the comparable run: the whole pool, with
> #: no study material in it. `--split declared` keeps this adapter's own division.

This “comparable run” sentence is too broad already: selecting the whole pool does not align the custom attack or prompt defense. Replace with “whole local fixed-attack pool; protocol comparability remains qualified”.

## scienceworld

2026-10-16 — **FOUND, qualification required.** Our number: Final JVM score clamped to [0,100] and divided by 100 (`data/datasets/scienceworld/verify/check.py:179-206`), under local 1000 moves (`data/datasets/scienceworld/lib/scw_env.py:42-46`), then equal measured-task mean.

Difference: The retained parent review requires paper’s 100 moves, test fold, and macro-over-task-types rather than variation-weighted mean (`registry/w-evidence-external-sources.md:1088`, eval-fidelity-plan §2/§3). These paper-side requirements are inherited, not freshly authenticated here. The handoff also identifies the missing task type as measure-melting-point-unknown-substance, contradicting the module’s identify-life-stages-2 claim (`/mnt/20t/xubuqiang/Study/HarnessGrad/docs/paper-fidelity-audit-handoff.md:321-326`; `data/datasets/scienceworld.py:49`); that named-type correction changes a label, while adding its missing test variations changes coverage and the macro denominator. Report 29/30 until independently bound complete coverage exists. The current no-simplification input is explicit (`data/datasets/scienceworld.py:288`), and the handoff marks the actor unaided because valid actions are not exposed (`/mnt/20t/xubuqiang/Study/HarnessGrad/docs/paper-fidelity-audit-handoff.md:341-346`). Repeated trials, selection, simplifications and macro weighting must be bound next to any result; a completed trial count does not repair an integrity-invalid run (`docs/adapter-integration-journal.md:327-343`).

Effect: NUMBER/CONDITION for budget, fold or weighting changes. Earlier 1000-move/task-weighted figures must not be reused as 100-move/type-macro ScienceWorld. Preserve the historical incomplete effect=null record.

Existing record to qualify or update:

`data/datasets/scienceworld/lib/scw_env.py:42`:

> #: **1000**, an adapter-owned ceiling above the longest recorded test reference path (796 moves).
> #: This keeps every 1,744 archived test path available instead of turning a correct long
> #: oracle into a false zero. The verifier timeout is raised alongside it so the larger move
> #: budget cannot be silently truncated by the wall-clock boundary.
> STEP_BUDGET = 1000

This ceiling rationale and constant become stale after a 100-move change. State explicitly that long oracle paths may truncate at the paper’s budget; never retain all-1744-oracles-fit as a 100-move claim.

## gaia

2026-10-16 — **FOUND, no new finding in the named scope.** Our number: Official question_scorer binary result, preserving float/list/string branches (`data/datasets/gaia/verify/check.py:2-14`, `:96-107`). No new metric-fidelity finding in the inspected scorer header/call/placeholder guard. Checked to prevent replacing the official branching scorer with generic EM. Historical incomplete records and split/protocol limits remain; this is not a runtime or leaderboard-equivalence clearance. No numeric or label fix is asserted, and no existing sentence is proposed for replacement. This is a scoped source clearance, not an independent reproduction of every rejected intern item.

## jericho

2026-10-16 — **FOUND, no new finding in the named scope.** Our number: Final game score / game maximum (`data/datasets/jericho/verify/check.py:132-155`). No new metric-fidelity finding in the inspected score/maximum replay path. Checked because environment partial reward must not be confused with binary success. Matched game selection, action budgets and paper recipes remain UNKNOWN; “no finding” is narrower than direct paper comparability. No numeric or label fix is asserted, and no existing sentence is proposed for replacement. This is a scoped source clearance, not an independent reproduction of every rejected intern item.

## spreadsheetbench

2026-10-16 — **FOUND, no new finding in the named scope.** Our number: Binary named-cell value match on one selected workbook variant (`data/datasets/spreadsheetbench/verify/check.py:470-472`; `registry/w-metriccmp-comparability.md:318-373`). No additional current finding in the one-variant metric qualification and retained cache/range-zero closure. Checked because official soft/hard scores combine three workbook variants; this known difference is already explicit (`registry/w-metriccmp-comparability.md:386-409`; `registry/blocker-closure-assessment.md:375-404`). Source-only clearance does not assert a new run or cache verification. No numeric or label fix is asserted, and no existing sentence is proposed for replacement. This is a scoped source clearance, not an independent reproduction of every rejected intern item.

## terminal_bench

2026-10-16 — **FOUND, no new finding in the named scope.** Our number: Task test.sh reward file, not shell exit status (`data/datasets/terminal_bench.py:126-128`, `:231-241`). No new dataset metric-fidelity finding in the inspected reward declaration. Checked because shell status may be zero for both task success and failure; missing verdict handling was a shared platform defect already recorded as fixed (`registry/known-red-tests.md:104-110`). A task test reward is not proof of execution or snapshot comparability; old zeros are not reclassified here. No numeric or label fix is asserted, and no existing sentence is proposed for replacement. This is a scoped source clearance, not an independent reproduction of every rejected intern item.

## api_bank

2026-10-16 — **EXCLUDED, not investigated.** The registry retains retain-contract-refusal for this entry (`registry/dataset-blockers.json`, exact inventory/observation in validation). No dataset code, payload or runtime was investigated for this task. No local number is reportable and no correction or proposal is made.

## nestful

2026-10-16 — **EXCLUDED, not investigated.** The registry retains retain-contract-refusal for this entry (`registry/dataset-blockers.json`, exact inventory/observation in validation). No dataset code, payload or runtime was investigated for this task. No local number is reportable and no correction or proposal is made.

## sotuqa

2026-10-16 — **EXCLUDED, not investigated.** The registry retains retain-contract-refusal for this entry (`registry/dataset-blockers.json`, exact inventory/observation in validation). No dataset code, payload or runtime was investigated for this task. No local number is reportable and no correction or proposal is made.

## tau2_bench

2026-10-16 — **EXCLUDED, not investigated.** The registry retains retain-contract-refusal for this entry (`registry/dataset-blockers.json`, exact inventory/observation in validation). No dataset code, payload or runtime was investigated for this task. No local number is reportable and no correction or proposal is made.

## Registry application boundary

Only three non-refused datasets have an open blocker. `tools/apply_blocker_proposal.py:54-61` refuses a dataset/blocker absent from the current registry; `:148-167` preserves current sentence obligations. Accordingly the three w-evidence proposal files append qualifications to existing appworld/bfcl_v3/triviaqa blockers, with the current next_action retained verbatim as a prefix. No fragments for closed datasets are emitted: fabricating a blocker id would fail the requested mechanical interface and reopen a closure. The parent can apply closed-dataset text above to the review/document records while retaining the source-only closure. No obligation or permanent refusal is dropped.

## Handoff corrections retained with the qualifications

The handoff is evidence to check, not authority to copy blindly. Its §3.4 sentence "MuSiQue's and 2Wiki's reward is joint F1 (answer F1 × support F1), not Answer F1." conflates two formulas (`registry/w-evidence-external-sources.md:1334`). 2Wiki instead multiplies three component precisions and recalls, then takes their harmonic mean (`data/datasets/twowikimultihopqa.py:25-29`). The local PhysicsQuestions rule is also not unchanged BIG-bench target membership (`registry/w-metriccmp-comparability.md:145-154`), despite the handoff’s earlier no-action statement. Finally the original-run survival statement is overbroad: see the exact census source-run gaps in `registry/w-evidence-archive-sources.json:1`. None of these observations reopens a source-only closure.
