# Withdrawn requirements: proven-unobtainable evidence becomes a recorded limit

Operator decision, 2026-10-15. This file is the evidence record for every blocker
requirement withdrawn under this decision. It follows the same standard the operator
already applied to `paired-filesystem-quotas`, `snapshot-owned-cleanup` and
`official-scorer-identity`: **a requirement that cannot be satisfied here is recorded as a
limit with the search evidence attached, rather than left open forever.**

A requirement withdrawn here is one that no amount of further work in this repository can
satisfy — not one that is merely difficult. Each entry names what was searched and what
came back empty or impossible.

The operator's further decision on 2026-10-15 extends this record to the three runtime
requirements below. Their evidence describes why they cannot be advanced in the current
scope; withdrawal does not assert that a future provisioned runtime could never be tested.
No new live run, receipt authentication or search result is claimed by these entries.

## Shared requirement withdrawn: `scorer-offline-closure`

The withdrawn shared requirement includes S6 "validate live controls before pilots".
The remaining clauses retain their bounded evidence and residual limits; withdrawal
does not certify complete transitive image/ABI closure or official metric equivalence.

**Why it cannot be satisfied by work.** The clause asks for live controls whose staged
receipts are *cleared*, but the observation flag that would clear them is hard-coded false:
`w-s6` traced the path and showed the flag only flips after the admission the clause itself
helps withhold. It is a cycle, not a gap.

**What is retained instead.** The control *evidence* exists and stays in the record at its
actual scope — real raw results, each still publishing `score=null`:

| class | control | raw result |
|---|---|---|
| actor-workdir | ALFWorld noop | reward 0.0 |
| snapshot-service | Terminal-Bench `openssl-selfsigned-cert` | reward 0.0, CTRF 5/6 passed |
| in-process | ChessBench stepwise | terminal exchange, controller 0.0 |
| pristine-offline | pristine control | measured 0.0 (answer 41 vs expected 42) |
| mounted-service | AppWorld | measured loss |
| JVM / LibreOffice / child-process | ScienceWorld, SpreadsheetBench, DS-1000, LiveCodeBench, BIRD | lifecycle/limit/cleanup observations |

Terminal-Bench verifier coverage reached 13/89 real measurements; the 45th-round live
control set is preserved in the journal and the run artifacts.

## Shared requirement withdrawn: `artifact-only-state-export`

**Searched:** `w-scope` reviewed all 28 declared datasets and the QA scaffold for
pristine applicability; `w-quiesce2`, `w-e5`, `w-wal` and `w-e6b` examined selected-file
custody, scoring equivalence and lifecycle observations at their recorded scopes.
**Result:** zero pristine-offline declarations or selections. E1/E2/E3 are
SATISFIED FOR THE CURRENT DATASET SET (zero applicable pristine datasets), but
no real-dataset pristine export, private-input safety or backend ownership validation is established.
Selected-file endpoint probes do not establish interval quiescence: the same-UID
directory-substitution/restore counterexample evades those probes. Main-only SQLite
export omitted committed WAL state and changed the authored BIRD EX result from 0 to 1;
the subsequent native bound-input path refuses WAL-format SQLite before scoring.
E4/E5/E6 remain PARTIAL as standing limits, rather than a claim of general equivalence
or complete lifecycle coverage. This records the operator's withdrawal; it does not
classify every unexercised branch as impossible to test.

**Retained future opt-in boundary:** Every future pristine opt-in must provision authoritative per-task export
and selected private-input/gold contracts, and validate actual backend/source/projection ownership.
The former next_action remains the scope of that work, not an active shared blocker:

> Provision authoritative per-task export and private-input contracts for pristine scorers;
> validate ownership, quiescence/trial binding, scoring equivalence and live lifecycle/cleanup.
> Review snapshot/service state and recording surfaces under their declared class without
> forcing an inferred artifact allowlist.

The original scope citation remains `/site/w-scope-pristine-applicability.md`,
locator `## Exact registry wording`; its carrier was the withdrawn shared blocker.

## Dataset requirements withdrawn as unobtainable

### reasoning_gym / original-generation-process-receipt
Asked for: original pool generation invocation, interpreter/build and dependency-artifact lock, effective clock/timezone/date and hash state/order bound to c0ff4eaef318cd59afcc61472ebe206362fc0211c4b589ed0d53946a569bd177, and exact reproduction from recorded original inputs.
Searched: 733 enumerated Codex session snapshots plus ~/.codex/history.jsonl, ~/.bash_history and 5 archived files; 137 local branches and all 23773 stored main Git objects, reflogs/stash; 395197 enumerated Study regular files (393833 permitted raw files), 2149 resolved symlinks, 180 independent Study Git stores, 2 backup dot-git stores, 2 nested main Git stores and 985 magic-detected archives; own/main runs, discarded runs, state and fixtures;64859 census files. Scope excludes 1364 prohibited-dataset payload paths and 6 encrypted GPQA archive members; these contents remain UNKNOWN. Exact commands, per-scope hits/misses, manifests and explicit exclusions/errors are in registry/w-recgym-receipts.md and registry/w-recgym-validation.txt.
Result: the retained records did not capture the required original process fields; no original launch receipt is present in the searched readable/permitted corpus. The documented generator recipe and digest pin exist, but the original invocation, environment, clock/timezone and hash state remain UNKNOWN. Whether a record was never captured or later deleted is UNKNOWN; no historical or unrestricted-machine absence is asserted. Withdraw only the requirement to produce original records unavailable from this corpus; preserve the installed pool, seed/families/order, failed 84-row/six-family regeneration evidence and all independent behavioral/metric/runtime uncertainties. No exact reproduction, zero score, scorer closure, shared-gate reinstatement or diagnostic authorization is inferred.
**Why it cannot be advanced here:** the pool was generated **on this machine** from a declared recipe and seed; no upstream or third-party publication can hold the producing process record, and the entire readable/permitted on-machine corpus has been enumerated and is empty. The entry does not assert that the fields were never captured, and it does not assert any historical or unrestricted-machine absence.
**Retained:** the installed pool and its `c0ff4eae...` digest, the declared seed/families/order, the 84-row/six-family failed-regeneration evidence, and every independent behavioural, metric and runtime uncertainty remain recorded. No exact reproduction, zero score, scorer closure, shared-gate reinstatement or diagnostic authorization is inferred.


### `hotpotqa / historical-comparison-receipts / original-v4-receipts`
**Former status:** `measurement` within an active blocker that stays open; this sub-requirement is
withdrawn.
**Asked for:** the original user-stopped v4 run's selected-ID/trial/error/timeout receipts and its
source/split/manifest/model/harness provenance receipts, with measured/invalid/unmeasured counts and
lifecycle/cleanup reconciliation.
**Searched:** an enumerated on-machine scope. `w-hotpotrec` recorded a search over
`~/.codex/sessions/**` (722 transcripts), the repository's full object store, history, reflog and
stashes, `runs/`, `runs_discarded_*`, `.hashstate` state, `tests/fixtures/`, the named archives and
`/mnt/20t/xubuqiang/hg-census/`, plus adaptive existence checks on `/tmp/codex` and
`/tmp/harnessgrad-runs`. The parent re-checked on 2026-10-15: `HarnessGrad-evidence-archive/` holds
only `chess/`, `codex/` and `qwen-baseline/`; the two stranded pre-rewrite clones hold adapter source
only; and both `/tmp/codex` and `/tmp/harnessgrad-runs` are absent.
**Result:** the historical `ls` listing proves the v4 split file, console log and 1,179-byte budget
ledger **existed** at `/tmp/harnessgrad-runs/hotpotqa-h0-10pct-v4`, and a captured read of
`qa-h0-incomplete-index.json` binds the candidate ID `hotpotqa-h0-10pct-v4` to the dataset, the
`incomplete` status and that run directory. The files themselves are now absent over that scope and
the binding of the candidate ID to the reported 94/1382/1476 coverage is unresolved. The deletion
cause is **not** established and is not attributed: the recorded `/tmp` hygiene patterns
(`/tmp/hg-task-*`, `/tmp/harnessgrad-pytest-*`, the `hg-w*` scratch sets) do not cover
`/tmp/harnessgrad-runs` or `/tmp/codex`.
**Why it cannot be advanced here:** the v4 run was a **local pilot of this platform** - its run
directory is `/tmp/harnessgrad-runs/hotpotqa-h0-10pct-v4`, under this machine's own run-ID convention -
so no upstream or third-party publication can hold its receipts. Every on-machine source has been
enumerated and is empty. Unlike `bird_minidev` and `ds1000`, the wording "not present in this
repository and not published upstream" would **overstate** this case: the receipts existed and were
lost, rather than never being captured. The only conceivable remaining source is a machine-external
backup of `/tmp` predating the loss, which is outside this repository's reach.
**Retained:** the candidate ID, the historical filenames, the captured index tuple and the enumerated
absence are recorded in `registry/w-hotpotrec-receipts.md` and `registry/w-hotpotrec-evidence.json`.
`historical_runs` keeps `run_id=null` and `effect=null` and is never edited, resumed, rerun or
overwritten; unknown outcomes stay unmeasured and never become zeros. The blocker's remaining
obligations - current selected scorer/control admission, the retained first-five packet and the
synthetic timeout closure - are unchanged, and any separately authorized future diagnostic still uses
a fresh ID under the staged policy.

**Superseded 2026-10-15:** the sentence above describes the state when this limit was recorded.
The blocker itself was afterwards **closed** under reading (A) once the parent filed it as a closure
candidate and the operator confirmed it; the closure note is in `registry/dataset-blockers.json`
(`review.notes`) and the clause table is in `registry/blocker-closure-assessment.md`. This withdrawal
entry, its enumerated scope and its retained limits are unchanged, and nothing here is reopened: the v4
run stays incomplete with `run_id=null` and `effect=null`, and no diagnostic is authorized.


### `livecodebench / row-attestation`
**Asked for:** a metadata-only complete upstream catalogue/rank plus authenticated
row/pool/split/statement linkage.
**Searched:** the authoritative upstream source, repeatedly, across three separate rounds.
**Result:** **zero authoritative upstream row IDs obtainable**; the upstream count is not
published, so the locally declared 1,055 count cannot be corroborated from public sources.
Six pinned shard identities were linked to the adapter's own declarations, and the inert
selection and conditional split reproduce — that part is retained.

### `twowikimultihopqa / hub-data-provenance`
**Former family:** `source-provenance`.
**Asked for:** metadata-only original-release archive/file digest custody and completeness
attestation.
**Searched:** exact-revision upload history, release/tag inventories, a zero-result
licence-issue search, and the original and later Dropbox HEAD receipts.
**Result:** the original release is advertised with an **opaque ETag and no content digest**
(a 259,216,602-byte attachment). An opaque ETag is not a digest and was explicitly refused
as a substitute. The paper claims 192,606 examples while the witness card carries
conflicting counts, so no coverage attestation can be derived either.

### `twowikimultihopqa / ujson-native-offline-closure`
**Former family:** `scorer-dependency-network`.
**Asked for:** authenticated linkage from the published wheel to its source/build inputs,
including the double-conversion build selection.
**Searched:** PyPI build attestation (**404, "No provenance available"**) and then a full
**reproducible rebuild** from the pinned commit `59875e08` inside the pinned image.
**Result:** the rebuild **did not reproduce** — all six member names match and LICENSE,
METADATA and `top_level` are byte-identical, but the compiled extension, `WHEEL` and
`RECORD` differ. The embedded double-conversion implementation is confirmed present; the
original vendored-versus-external-static selection is not observable in the artifact. The
image-bound runtime closure that *is* obtainable (network-denied import, resolved loader and
symbol providers, synthetic evaluator) was completed and retained.

### `bird_minidev / sql-coverage-reconciliation`
**Asked for:** original selected-ID/phase/trial/error metadata binding the 90 phases to
actual measurements.
**Searched:** the tracked-source inventory.
**Result:** only summaries exist; the original phase/trial/error ledger is **not present in
this repository** and is not published upstream. The v4 incomplete record,
the v5 historical complete label and the partial-measurement/effect=null state are preserved
rather than reinterpreted.

### `ds1000 / host-slice-archive-review`
**Asked for:** original selected-ID/split/host-pool provenance plus original trial outcomes
and timeout/error/lifecycle records.
**Searched:** the same inventory.
**Result:** those records **do not exist in the repository**; `ds1000-v4-pending-review` is
preserved with `effect=null`. Archive acceptance stays blocked in the sense that no
measurement is claimed from it — what is withdrawn is the requirement to *produce* records
that were never captured.

### `gaia / frozen-lifecycle-receipt`
**Former family:** `snapshot-cleanup`. **Former status:** `runtime`.
**Asked for:** independently authenticated selected-only/source-lock, verifier/dependency
and artifact-only export evidence, plus resolution of the frozen V2/V3 lifecycle gaps.
**Evidence reviewed:** the former blocker's own next_action starts
"Retain policy refusal: do not provision or run GAIA." Its observed record says compatibility
only compares supplied identities, without validating receipts or authorizing reuse;
`eval/policy/gaia_snapshot_attestation.py` explicitly records
`"receipt_validation": "not-performed"`. Historical citations remain
`/site/adapter-integration-journal.md` (`## GAIA lifecycle wiring audit — Codex 165`),
`/site/preserved-lifecycle-review-b8.md` (`## GAIA / frozen-lifecycle-receipt`),
`/site/gaia-operator-packet-codex210.md`
(`## Required operator deliveries, in dependency order`) and
`/site/enforcement-proof-decision.md` (`Snapshot/cleanup uncertainty alone is not a new`).
**Why it cannot be advanced here:** the requirement withholds readiness pending live
evidence while its own action forbids provisioning or running GAIA. No permitted live run
can supply that evidence here. The operator withdraws this requirement as a standing limit;
this does not lift the policy refusal or authenticate the frozen receipts.
**Retained:** `gaia-validation-pilot-h0-20261117-v2` and
`gaia-validation-pilot-h0-20261117-v3`, their original receipts and historical records stay
untouched: never resume, rerun or overwrite either ID. V2's 9 persisted trials versus
10 done events and unknown API-timeout usage remain unresolved; V3's pre-verification
snapshot exit 137 remains unresolved. Both records remain incomplete with `effect=null`;
unknown outcomes stay unmeasured and no aggregate score is valid. Their original receipt
citations remain in `historical_runs`:
`/mnt/20t/xubuqiang/Study/gaia-h0-launch-v2-evidence/GAIA_H0_V2_RECEIPT.json` and
`/mnt/20t/xubuqiang/Study/gaia-h0-launch-v3/runs/gaia-validation-pilot-h0-20261117-v3/events.jsonl`.
Best-effort snapshots/cleanup retain uncertainty; known failures remain recorded.

### `tau_bench / local-state-lifecycle`
**Former family:** `snapshot-cleanup`. **Former status:** `runtime`.
**Asked for:** "Keep the runtime gate open." Require selected-only custody plus independent
run/trial/manifest-bound clean-state restoration, database/image identity, evaluator secrecy,
effective backend limits and artifact-only state export before a readiness claim.
**Evidence reviewed:** the former observed record says import reads the full ground-truth
pool (`data/datasets/tau_bench.py`, `_ALL_GT: list[dict] = _read_gt()`), both clean databases
are absent in the reviewed worktree, and no independent selected runtime/lifecycle receipt
was located in the reviewed repository metadata. The late verifier-input declaration
(`def _verifier(record: dict) -> dict:`) is source evidence, not reset/secrecy observation.
Historical citations remain `/site/adapter-integration-journal.md`
(`## AppWorld / GAIA / tau-bench — local state boundaries`),
`/site/preserved-lifecycle-review-b8.md` (`## tau_bench / local-state-lifecycle`),
`/site/tau-bench-vendoring.md`
(`3. **Two recorded generated databases are absent, intentionally ignored by git.**`) and
`/site/enforcement-proof-decision.md` (`Snapshot/cleanup uncertainty alone is not a new`).
**Why it cannot be advanced here:** the cited source/inventory cannot establish selected-only
custody or independently observed run/trial/manifest-bound restoration. The reviewed record
has neither the clean database pair nor that independent receipt; repeating declarations
or synthetic contracts cannot supply the missing observation. The operator now withdraws
the keep-open requirement and records those missing runtime facts as limits. This is an
operator scope decision, not proof that a future provisioned runtime could never be tested.
**Retained:** the full-pool import, missing database pair and unobserved custody, reset,
secrecy, backend-limit and export properties remain limits. `historical_runs` stays empty;
no frozen tau-bench run or independent receipt is invented. Existing vendoring and lifecycle
citations stay historical evidence, without a runtime pass, readiness claim or production
authorization. Best-effort snapshots/owned cleanup retain uncertainty; known failures still
refuse, and evidence outside the cited review remains unknown.

### `chessbench_puzzles / interruption-closure`
**Former family:** `termination-audit`. **Former status:** `runtime`.
**Asked for:** "Keep the runtime gate open pending independent audit/receipt authentication
and termination/quiescence review." Preserve both historical IDs, original receipts and null
effects; never resume, rerun or overwrite either ID, or turn missing outcomes into zeros.
**Evidence reviewed:** the former observed record reports 19 and 149/150 completed
task-trials with no terminal verdict/aggregate or cleanup closure. Termination authority
remains undetermined on the native bwrap/files path; an audit digest does not authenticate
either external run receipt. Former citations remain `data/datasets/chessbench_puzzles.py`
(`KIND = "dataset"`), `/site/adapter-integration-journal.md`
(`- Interruption audit: termination authority is undetermined`),
`/site/preserved-lifecycle-review-b8.md` (`## chessbench_puzzles / interruption-closure`),
`/site/chess-recovery-id-conflict-codex182-report.md` (`Both historical IDs`) and
`/site/enforcement-proof-decision.md` (`Snapshot/cleanup uncertainty alone is not a new`).
**Why it cannot be advanced here:** the independent-approval requirement was already
withdrawn by the operator in `docs/independent-review-deferred.md` (now cited as
`/site/independent-review-deferred.md`). That standalone exported source is not available
in this worktree; the existing journal's "Parent review and merge — w-trivia — 2026-10-15"
entry corroborates that the operator withdrew the independent-approval gates and instructed
workers not to re-impose human sign-off. Neither that decision nor source review supplies
authentication or missing terminal/quiescence observations for frozen runs. The operator's
new decision withdraws the remaining keep-open requirement; those unknowns remain limits.
**Retained:** `chess-pilot-h0-20261013` and
`chess-pilot-h0-20261013-recovery-01`, their original receipts, historical records and
`/mnt/20t/xubuqiang/Study/HarnessGrad-evidence-archive/chess/interruption-audit.md`
citation stay untouched. Never resume, rerun or overwrite either ID. Both records remain
incomplete with `effect=null`; the 19 and 149/150 coverage, missing terminal outcomes,
undetermined termination authority and unproven cleanup remain as recorded. Unknown
outcomes are unmeasured, not measured zeros or complete coverage. Future attempts still
require new unique IDs and separately applicable admission; withdrawal is no rerun or pilot
authorization. Best-effort cleanup retains uncertainty without requiring proof of exact
owned absence or atomic lease closure.

## What this decision does not do

- It does not claim any withdrawn requirement was solved. Each is recorded with its
  supporting evidence and retained limits.
- It does not touch the four permanent refusals (`api_bank`, `nestful`, `sotuqa`,
  `tau2_bench`), whose `retain-contract-refusal` entries stay exactly as they are.
- The operator's further decision on 2026-10-15 withdraws the three runtime requirements
  above, superseding the earlier decision to leave this trio untouched. Their limits and
  historical receipts remain; `appworld` and `bfcl_v3` stay real remaining work unchanged.
- It does not withdraw anything whose evidence merely has not been collected yet. The
  `journal-coverage` family, `hotpotqa` and `triviaqa` stay open because what they need is an
  operator-supplied selected manifest, which is an input rather than an impossibility.
- Every withdrawn blocker's text, evidence list and historical record remain readable in the
  git history of `registry/dataset-blockers.json`; the removals are the diff.

## Assertion migration - w-wd

The former `/site/task-206-twowiki-provenance-review.md` locator membership checks
(`38 passed in 0.24s` and `Hub/data provenance remains blocked`) no longer apply to
the active registry: their only carriers were the withdrawn TwoWiki blockers.
The tests instead pin each withdrawn ID, its former family and its failed search
in this record. The old locators and evidence lists remain in git history; no
historical run, partial measurement or null effect is reclassified.

The combined registry validation also exposes stale B6 and B3 pins for these
withdrawn carriers. `/site/b6-dataset-blocker-review.md` locator membership for
`## 2Wiki: ujson-native-offline-closure`, `## 2Wiki: hub-data-provenance` and
`## LiveCodeBench: row-attestation` no longer applies to active blockers. Likewise,
`/site/measurement-coverage-hg-b3-review.md` locators
`## Bird MiniDev: label/semantics review closed; metadata reconciliation open` and
`## DS1000: host-pool interpretation closed; archive acceptance open` belonged only
to the removed BIRD/DS1000 blockers. Their historical text remains available; tests
pin the corresponding absence and failed searches here. HotpotQA's live gate and
its citation, all archive-integrity tests and all frozen historical checks stay intact.
