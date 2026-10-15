# Blocker closure assessment — 14 open blockers, clause by clause

Parent assessment, 2026-10-15, at registry commit `21d6ebbf`. This document does not change the
registry. Its purpose is to answer one question for every open blocker: **which of its own
`next_action` obligations are already discharged, which are not, and what class the rest belong to** —
so that "14 open" becomes a set of concrete dispositions instead of a number.

The controlling rule is the objective's: a blocker closes only on the kind of evidence its own
`next_action` names. Nothing here is a claim that an obligation is met unless the record already holds
the artefact.

## Obligation classes used below

| class | meaning |
| --- | --- |
| `SATISFIED` | The named artefact exists in the record now (evidence file, bound hash, review document). |
| `WITHDRAWN` | The operator withdrew the requirement; it is recorded in `registry/withdrawn-requirements.md` and no longer exists as a gate. |
| `PRE-DIAGNOSTIC` | A precondition on a *future, separately authorized* diagnostic, not a condition on closing the blocker. Recorded so it is not lost. |
| `PENDING-WORK` | Repo-local analysis or artefact work that is genuinely obtainable and not yet done. |
| `PENDING-UPSTREAM` | Requires an artefact from an authoritative public source; a search is in flight or has returned a bounded negative. |
| `PENDING-RUN` | Requires a live measured execution under the staged pilot policy (authorization plus a run). |
| `PENDING-INPUT` | Requires an artefact only the operator or a third party can supply. |
| `LIMIT-CANDIDATE` | The original artefact no longer exists anywhere the record can reach; a candidate for the operator's proven-unobtainable standing-limit treatment. |
| `REFUSED` | Permanent refusal the operator instructed not to revisit. |

## Summary

| dataset / blocker | status | disposition | blocking class(es) |
| --- | --- | --- | --- |
| `api_bank / retain-contract-refusal` | external | permanent refusal | `REFUSED` |
| `nestful / retain-contract-refusal` | external | permanent refusal | `REFUSED` |
| `sotuqa / retain-contract-refusal` | external | permanent refusal | `REFUSED` |
| `tau2_bench / retain-contract-refusal` | external | permanent refusal | `REFUSED` |
| `physicsquestions / dataset-journal-gap` | measurement | **closure candidate** | none (`PRE-DIAGNOSTIC` only) |
| `sportsunderstanding / dataset-journal-gap` | measurement | **closure candidate** | none (`PRE-DIAGNOSTIC` only) |
| `appworld / successful-task-evidence` | measurement | open | `PENDING-RUN` (+ an operator decision, below) |
| `spreadsheetbench / dataset-journal-gap` | measurement | open | `PENDING-RUN`, `PENDING-WORK` |
| `bfcl_v3 / simple-ast-contract` | external | open | `PENDING-WORK`, then `PENDING-RUN` |
| `fever / dataset-journal-gap` | measurement | open | `PENDING-UPSTREAM`, one naming decision |
| `strategyqa / dataset-journal-gap` | measurement | open | `PENDING-UPSTREAM` |
| `reasoning_gym / dataset-journal-gap` | measurement | open | `PENDING-UPSTREAM`, `PENDING-WORK` |
| `triviaqa / hub-export-scorer-linkage` | external | open | `PENDING-UPSTREAM`, `PENDING-WORK` |
| `hotpotqa / historical-comparison-receipts` | measurement | open | `LIMIT-CANDIDATE` |

## The four permanent refusals

`api_bank`, `nestful`, `sotuqa`, `tau2_bench` each carry one 113-character clause: retain the explicit
refusal and exclusion, do not provision or run the dataset, do not substitute its metric. Each is
`SATISFIED` by retention and is `REFUSED` by operator instruction — the objective explicitly says not to
attempt closure. Unchanged.

## The two closure candidates

Both are `family: journal-coverage` with blocker id `dataset-journal-gap`. The journal gap they were
opened for is the coverage the journal must carry about the dataset's source, metric, custody and
selection. Every clause in their current `next_action` is now either satisfied or a precondition on a
future diagnostic:

**`physicsquestions / dataset-journal-gap`**

| clause | class | where it stands |
| --- | --- | --- |
| Retain installed-to-ReWOO and ordered pinned-BIG-bench row linkage, and the bounded first-five selected-only custody record | `SATISFIED` | `tests/fixtures/hg_wprov/README.md`, `tests/fixtures/hg_wsel/physicsquestions.json` |
| Report the local asymmetric normalized accepted-spelling exact-match reward separately | `SATISFIED` | `registry/w-metriccmp-comparability.md` |
| Do not claim BIG-bench `exact_str_match`, BLEU or matched generation/processing/aggregation equivalence | constraint | recorded in the same document; the difference is shown with a synthetic discriminating pair |
| Do not infer a historical converter revision or runtime execution | constraint | recorded |
| For any separately authorized diagnostic: reconcile the run-specific manifest/export, exact rows and split mode/side, and establish deterministic offline dependencies and dataset-specific trusted/pristine verifier execution | `PRE-DIAGNOSTIC` | statement only; no diagnostic is authorized |
| Record eligible/selected/task/trial/invalid/unmeasured coverage and fresh execution identities | `PRE-DIAGNOSTIC` | scoped to the same future diagnostic |
| Preserve the withdrawn `official-scorer-identity` decision and the shared-requirement withdrawals | `WITHDRAWN` | `registry/withdrawn-requirements.md` |

**`sportsunderstanding / dataset-journal-gap`** — identical shape: installed-to-ReWOO and pinned
BIG-bench row linkage retained (`tests/fixtures/hg_wprov/README.md`,
`tests/fixtures/hg_wsel/sportsunderstanding.json`); the separate local generated-text label-accuracy
statement adopted (`registry/w-metriccmp-comparability.md`); non-equivalence to
candidate-log-probability `multiple_choice_grade` recorded; the diagnostic-time clauses are
`PRE-DIAGNOSTIC`; the shared-requirement withdrawals are `WITHDRAWN`.

### Why they are not closed here, and what closing requires

Two things must be true before closing either one, and both are decisions rather than more work:

1. **A stale-`observed` problem must be superseded, not ignored.** Both records still contain earlier
   worker sentences that read as current: physicsquestions says "all shared gates remain open" and
   "Remaining next_action obligations: Actual scorer-offline-closure, pristine verifier execution and
   both shared gates"; sportsunderstanding says "Selected run manifest/export custody, offline/pristine
   runtime and measured coverage remain open with every shared gate". Those sentences were accurate when
   written and were **superseded by the withdrawal** — the shared gates no longer exist. Rather than
   edit dated worker notes, a registry-level clarification note was appended to `review.notes` in this
   same commit stating that those names in an `observed` field are not current obligations. Closing a
   blocker while a reader can still find "all shared gates remain open" in its own `observed` field
   would be a misreading trap.
2. **A closure-semantics decision is needed.** Both blockers carry `status: measurement`, and the
   registry's own taxonomy says the status "classifies the work needed, not benchmark readiness". Under
   reading **(A)** — the blocker is `dataset-journal-gap`, so it closes when the journal coverage named
   in its `next_action` exists — both are closeable now. Under reading **(B)** — `status: measurement`
   means the blocker is not discharged until a measured diagnostic has actually run — both stay open,
   and so do `fever`, `reasoning_gym`, `strategyqa` and `spreadsheetbench`, because none of the six has
   ever had a measured run. Reading (B) makes six of the ten real blockers dependent on a model run that
   no one has authorized, which is the circular shape the operator asked to have removed; reading (A)
   closes two now and leaves the other four blocked on their own documents and executions.

The parent has deliberately not chosen between (A) and (B) on the operator's behalf: closing two
blockers is a visible change to the headline count, and the two readings are both defensible. Under
either reading the *work* that remains is the same, and it is listed below.

## The eight that need something

**`appworld / successful-task-evidence`** — `PENDING-RUN`. Retained receipts, the incomplete Docker
exit-125 attempt, the raw-versus-staged distinction and the generic protocol review are all
`SATISFIED`. The gate itself is explicit: "only a genuine successful measured actor task under the
staged pilot policy can do so". The review additionally found a **task-independent** completion-guidance
gap (`data/datasets/appworld.py:234-236` versus `data/datasets/appworld/verify/check.py:45-56`) whose
harness-side remedy would change the measurement instrument; that is an operator decision and was not
applied. Two operator decisions are therefore outstanding: whether to authorize a diagnostic, and
whether the actor guidance may be changed.

**`spreadsheetbench / dataset-journal-gap`** — `PENDING-RUN` plus `PENDING-WORK`. Custody, the
one-variant metric statement and the official-range-zero policy are `SATISFIED`. Still required:
authenticated row-level gradable eligibility and eligible/selected/task/trial/invalid/unmeasured
coverage (a run), and complete dataset-specific scorer custody/execution with formula/LibreOffice
offline runtime evidence (work).

**`bfcl_v3 / simple-ast-contract`** — `PENDING-WORK`, then `PENDING-RUN`. Archive/tag/commit/member
acquisition and the code-only graph review are `SATISFIED`. Still required: exact offline
third-party/native runtime custody, the concrete local-model handler and response grammar, integrity
pins for the code-only projection, containment of expression evaluation, the fabricated-differential
full-call contract, and finally actual official scorer execution. `w-bfclrt` is working the custody
half.

**`fever / dataset-journal-gap`** — `PENDING-UPSTREAM` plus one naming decision. The flat-versus-
singleton question is now **determined** at source level, and the 51 omitted alternative groups / 42 IDs
and the unauthenticated NEI-input decisions are recorded limits. Two things remain: the producing
conversion's execution provenance, which the local search found ABSENT but which requires the upstream
search now running as `w-fevhub` before any standing-limit decision; and an explicit choice between a
conjunctive per-exported-row metric and complete original-group scoring with declared
original-claim weighting.

**`strategyqa / dataset-journal-gap`** — `PENDING-UPSTREAM`. Custody, the local EM statement and the
EM-identity limit are `SATISFIED`; the original scorer and split definition remain **undetermined**
because they are not in the enumerated local scope. Obtain readable authoritative scorer/split
definitions and bind their scope.

**`reasoning_gym / dataset-journal-gap`** — `PENDING-UPSTREAM` plus `PENDING-WORK`. Distribution,
source and installed-member custody, the declared pool hash and the frozen family/order inventory are
`SATISFIED`. Still required: the original generation environment/date/order metadata and a reproduction
of the declared pool from recorded inputs (`w-recgym` is searching every on-machine scope; the earlier
bounded regeneration differed in 84 rows across six families), and the independent behavioural
`reference=1 / empty=0` family eligibility determination — the second is repo-local work that needs no
model and no GPU.

**`triviaqa / hub-export-scorer-linkage`** — `PENDING-UPSTREAM` plus `PENDING-WORK`. The bound first-five
eval-side manifest/export, the v2 identity and the retained Hub/scorer bytes are `SATISFIED`. Still
required: the metadata-only HumanAnswers / membership / duplicate / scorer-key / denominator review, and
an enumerated re-inspection of the authoritative record for an immutable build/export execution receipt.
Both are `w-trivia2`'s task; the withdrawn-gate boundary does not condition closure.

**`hotpotqa / historical-comparison-receipts`** — `LIMIT-CANDIDATE`. The candidate v4 ID
`hotpotqa-h0-10pct-v4` is recovered, and the historical `ls` listing proves the v4 split, console log and
budget ledger **existed**; the original per-trial ledger is absent in the documented local scope and the
binding to the reported 94/1382/1476 coverage is unresolved. Timeout classification is `SATISFIED` and
the frozen record keeps `run_id=null` / `effect=null`. Unlike `bird_minidev` and `ds1000`, the files are
not "not present in this repository and not published upstream" — they existed on this machine and are
gone — so the existing withdrawal wording would overstate it and `w-hotpotrec` correctly refused to
propose one. This is the clearest candidate for the operator's standing-limit rule, and it needs an
explicit decision because the correct wording differs from the precedent.

## What is not in doubt

No blocker in this document can be closed by a source-only or metadata-only review, and none has been.
Every `SATISFIED` entry above names an artefact that exists; every `PRE-DIAGNOSTIC` entry is labelled as
such rather than counted as closure; no measured score is asserted anywhere; and the four refusals are
untouched.
