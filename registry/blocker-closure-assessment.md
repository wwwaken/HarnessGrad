# Blocker closure assessment — open blockers, clause by clause

Parent assessment, 2026-10-15, opened at registry commit `21d6ebbf` and updated as blockers closed. This document does not change the
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
| `appworld / successful-task-evidence` | measurement | open | `PENDING-RUN`; one authorized diagnostic ran and did **not** confirm the guidance hypothesis; completion-aware control now implemented |
| `spreadsheetbench / dataset-journal-gap` | measurement | open | `PENDING-RUN`, `PENDING-WORK` |
| `bfcl_v3 / simple-ast-contract` | external | open | `PENDING-WORK`, then `PENDING-RUN` |
| `fever / dataset-journal-gap` | measurement | open | `PENDING-UPSTREAM` (w-fevhub in flight) |
| `strategyqa / dataset-journal-gap` | measurement | open | original scorer FOUND and DIFFERENT; split membership `PENDING-UPSTREAM` |
| `reasoning_gym / dataset-journal-gap` | measurement | open | generation receipt `LIMIT-RECORDED`; behavioural eligibility DONE |
| `triviaqa / hub-export-scorer-linkage` | external | open | membership/scorer/denominator review DONE; execution receipt `PENDING-UPSTREAM` |
| `hotpotqa / historical-comparison-receipts` | measurement | open | `LIMIT-RECORDED` |

## The four permanent refusals

`api_bank`, `nestful`, `sotuqa`, `tau2_bench` each carry one 113-character clause: retain the explicit
refusal and exclusion, do not provision or run the dataset, do not substitute its metric. Each is
`SATISFIED` by retention and is `REFUSED` by operator instruction — the objective explicitly says not to
attempt closure. Unchanged.

## Closed under reading A, 2026-10-15 — `physicsquestions` and `sportsunderstanding`

The operator chose reading **(A)**: a `dataset-journal-gap` is discharged when the journal coverage its
own `next_action` names exists, and the diagnostic-time clauses are preconditions on a *future,
separately authorized* diagnostic rather than conditions on closure. Both blockers are therefore
**closed** and removed from the active registry; the pre-closure texts stay readable in this file's
git history and the decision is recorded in the registry's own `review.notes`.

At closure, every clause of each `next_action` was satisfied or withdrawn:

| clause | class | where it stood |
| --- | --- | --- |
| Retain installed-to-ReWOO and ordered pinned-BIG-bench row linkage | `SATISFIED` | `tests/fixtures/hg_wprov/README.md` |
| Retain the bounded first-five selected-only custody record | `SATISFIED` | `tests/fixtures/hg_wsel/physicsquestions.json`, `.../sportsunderstanding.json` |
| Cite the dataset's own migrated review | `SATISFIED` | `docs/dataset-reviews/<dataset>.md`, provisioned as `/site/dataset-reviews/<dataset>.md` |
| Report the local metric separately, with no upstream-equivalence claim | `SATISFIED` | `registry/w-metriccmp-comparability.md` - physicsquestions is asymmetric normalized accepted-spelling exact match, **different** from BIG-bench `exact_str_match`; sportsunderstanding is generated-text ASCII-letter-boundary label accuracy, **different** from candidate-log-probability `multiple_choice_grade` |
| Do not infer a historical converter revision or runtime execution | constraint | recorded in the same document |
| For any separately authorized diagnostic: reconcile the run-specific manifest/export, exact rows and split mode/side; establish offline dependencies and dataset-specific trusted/pristine execution; record eligible/selected/task/trial/invalid/unmeasured coverage | `PRE-DIAGNOSTIC` | statement only; **no diagnostic is authorized** and none of it is waived by this closure |
| Preserve the withdrawn `official-scorer-identity` decision and the shared-requirement withdrawals | `WITHDRAWN` | `registry/withdrawn-requirements.md` |

**This closes no measurement and claims no score.** Neither dataset has ever had a measured run, no
coverage count is asserted anywhere, and the diagnostic-time obligations above remain requirements of
any future diagnostic - which still needs its own authorization, a fresh run ID, a split/side binding
and the staged policy. The closure removes a bookkeeping blocker, not a verification step.

**The rule is now fixed, so it does not need re-deciding.** It does **not** generalise to the other
four journal-coverage blockers, and the registry note says why: `fever` still owes an upstream
producing-execution receipt, `reasoning_gym` an original generation receipt plus behavioural family
eligibility, `strategyqa` the original scorer/split definition, and `spreadsheetbench` measured
coverage plus scorer and formula/LibreOffice runtime evidence. Each of those is a named artefact that
does not exist yet, not a diagnostic-time precondition.

## The ten that need something

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

**`hotpotqa / historical-comparison-receipts`** — `LIMIT-RECORDED` (2026-10-15). The candidate v4 ID
`hotpotqa-h0-10pct-v4` is recovered, and the historical `ls` listing proves the v4 split, console log and
budget ledger **existed**; the original per-trial ledger is absent in the documented local scope and the
binding to the reported 94/1382/1476 coverage is unresolved. Timeout classification is `SATISFIED` and
the frozen record keeps `run_id=null` / `effect=null`. Unlike `bird_minidev` and `ds1000`, the files are
not "not present in this repository and not published upstream" — they existed on this machine and are
gone — so the existing withdrawal wording would overstate it and `w-hotpotrec` correctly refused to
propose one. This was the clearest candidate for the operator's standing-limit rule, and it is now
**recorded** under it in `registry/withdrawn-requirements.md` as
`hotpotqa / historical-comparison-receipts / original-v4-receipts`, with wording that does not
overstate the case: the receipts existed and were lost, the run was a local pilot so no upstream
source can hold them, the enumerated scope is named, and the deletion cause is left unattributed.
The candidate ID, the filenames and the enumerated absence stay recorded; the blocker's remaining
obligations are unchanged and it stays open.

## What is not in doubt

Two blockers were closed under reading (A) on 2026-10-15 and both are recorded above with their
clause-by-clause basis; that closure waived no verification step. For every blocker that remains open,
nothing here is discharged by a review that has not been done: every `SATISFIED` entry names an artefact
that exists, every `PRE-DIAGNOSTIC` entry is labelled as such rather than counted as closure, and no measured score is asserted anywhere. The four permanent refusals are untouched.

## Reverse audit — is every cleared dataset cleared for a recorded reason?

A forward assessment of the 14 open blockers says nothing about the 14 datasets that currently carry
none. If a blocker had ever been dropped without a disposition, the registry would show a dataset as
clear for no recorded reason, which is a worse defect than an open blocker. The reverse audit compared
the blocker set per dataset at `db32421c` (before the withdrawal wave) and at `1825cd0e^` (before the
bulk `reports/`/`docs/` deletion) against `HEAD`:

* `1825cd0e^` and `db32421c`: 28 datasets, **22** blockers. `HEAD`: 28 datasets, **14** blockers.
  Eight blockers were removed and eight withdrawal entries exist in
  `registry/withdrawn-requirements.md`, one per removal: `livecodebench/row-attestation`,
  `twowikimultihopqa/hub-data-provenance`, `twowikimultihopqa/ujson-native-offline-closure`,
  `bird_minidev/sql-coverage-reconciliation`, `ds1000/host-slice-archive-review`,
  `gaia/frozen-lifecycle-receipt`, `tau_bench/local-state-lifecycle` and
  `chessbench_puzzles/interruption-closure`.
* A mechanical check found **zero** removals not explained by either a withdrawal entry or the
  separately recorded `twowikimultihopqa/recovery-comparability` review closure.
* The remaining seven cleared datasets - `agentdojo`, `alfworld`, `gsm8k`, `jericho`, `musique`,
  `scienceworld`, `terminal_bench` - carried no blocker at either baseline, so their clearance predates
  this phase's registry and is not a result of anything removed here.

Conclusion: no dataset is currently clear because a blocker was silently dropped. `22 - 8 = 14`
accounts for every one of those removals, and the two closures under reading (A) on 2026-10-15
(`physicsquestions` and `sportsunderstanding`) take the active set to **12**. Both are recorded above
and in the registry's `review.notes`, so the count is accounted for in two documented steps rather than
one unexplained drop.

## Correction and update, 2026-10-15 — a family-level contract the forward assessment missed

The forward assessment above read each blocker's `next_action` and stopped there. That was
incomplete: the `journal-coverage` **family** carries a contract enforced by the test suite rather
than by the prose, and for three datasets it was not met.

* `tests/quality/test_dataset_journal_coverage.py:43-62` requires every `journal-coverage` blocker's
  `evidence` to contain a **per-dataset** reference `/site/dataset-reviews/<dataset>.md` with the
  locator `# <dataset> source-only journal review`, and pinned `sportsunderstanding`,
  `spreadsheetbench` and `strategyqa` as `xfail(strict=True)` in a `_KNOWN_JOURNAL_GAPS` set whose
  comment reads "Strict xfail makes a resolved gap fail until its stale exception is removed".
  Those three pointed only at the combined `/site/dataset-source-reviews-b2.md`, so they carried a
  real, recorded journal-coverage debt that no `next_action` mentioned.
* The two test files also encode two filing conventions, which is why this was invisible from the
  registry alone: `tests/quality/test_dataset_blockers.py:132-138` maps the b2 three to the combined
  document and asserts that entry is present (it was), while the family guard above demands a
  per-dataset one.

**Resolved in this commit.** The b2 document's three sections
(`## sportsunderstanding source-only review`, `## spreadsheetbench source-only review`,
`## strategyqa source-only review`) were extracted **verbatim** into
`docs/dataset-reviews/{sportsunderstanding,spreadsheetbench,strategyqa}.md`, each with a provenance
comment stating that this is a filing split and not a new review, plus the title line the per-dataset
convention requires. The carriers were provisioned at the conftest resolver path with
`PROVENANCE.json` entries recording `source_path: docs/dataset-source-reviews-b2.md`,
`source_commit: 1825cd0e^` and an explicit `transform` note, and the exact evidence entry was added to
each of the three blockers. `_KNOWN_JOURNAL_GAPS` is now empty, with its purpose and its "never add a
dataset here just to make an omitted review pass" warning retained.

**Effect on the dispositions above.** `spreadsheetbench` and `strategyqa` stay open on their own
`next_action` items (measured coverage plus scorer/formula runtime; the original scorer and split).
`sportsunderstanding` is now a closure candidate on exactly the same footing as `physicsquestions`:
its `next_action` obligations were already satisfied, and the family-level debt that silently sat
beside them is now discharged. The closure-semantics question at the end of the "two closure
candidates" section is unchanged and still belongs to the operator; what changed is that
`sportsunderstanding` no longer has a second, hidden reason to stay open.

**Method note.** A blocker can be gated by its family's contract as well as by its own `next_action`.
Any future pass over this registry must read the family guards in `tests/quality/` alongside the
registry text, and a strict `xfail` in those guards is debt, not a passing state.
