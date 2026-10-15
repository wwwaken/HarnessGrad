# Blocker disposition plan — proposal for operator review

Status: **proposal only**. Nothing in this file changes a blocker. It exists so the two
shared blockers can be taken to a decision instead of being narrowed forever.

## Why a decision is needed

Over ~20 rounds the two shared blockers went from "every clause PARTIAL" to "S1/S3/S4/S5
PARTIAL" with numbers attached (19+23 closure records, 94 image references with 91
recomputed digests, 13/89 Terminal-Bench tasks, 17/17 bounded resolver profiles, 5/7 native
closures). Each round narrowed the numbers. **No round could close anything, because no
completion threshold was ever defined** — a clause that reads "complete transitive image/ABI
dependencies" has no natural end, and every honest worker correctly reported the remaining
gap rather than claiming completion.

Two structural facts make this permanent rather than merely slow:

- **S6 is circular.** `w-s6` established that its observation flag is hard-coded false, so
  "validate live controls before pilots" depends on the very admission it withholds. No
  amount of further evidence closes it. Only a decision does.
- **Several clauses demand artefacts that are proven unobtainable.** `livecodebench` yielded
  **0 authoritative upstream row IDs**; `twowikimultihopqa` publishes an opaque ETag and no
  content digest; the original historical trial metadata for `bird_minidev`, `ds1000` and
  `hotpotqa` does not exist in this repository. Keeping those open asserts a requirement
  nobody can meet.

## The principle this plan applies

> A clause closes when the evidence its own `next_action` names exists **or** when that
> evidence is *proven unobtainable* — in which case it becomes a recorded **standing limit**
> with the proof of unavailability attached.

This is not new: the operator already applied exactly this principle to
`paired-filesystem-quotas`, `snapshot-owned-cleanup` and `official-scorer-identity`
(`docs/enforcement-proof-decision.md`, `docs/filesystem-quota-decision.md` at the time).
The difference now is only that the same standard is applied to clauses that pile up
counts rather than to clauses that demand proof a mechanism cannot fail.

## `scorer-offline-closure` — clause by clause

| clause | now | proposed disposition | deciding evidence |
|---|---|---|---|
| S1 dataset-specific pinned scorer closures | PARTIAL | **close as provided-with-recorded-gaps** | 19 actor-workdir + 23 container closure records; every gap is enumerated per dataset, which is a limit list, not missing work |
| S2 class-specific runtime evidence | SATISFIED | keep | live controls across actor-workdir, snapshot-service, in-process, pristine-offline, AppWorld mounted-service |
| S3 image/ABI dependencies | PARTIAL | **split**: close the pinning half; **standing limit** for the rest | 94 configured refs, 91 RepoDigests recomputed from OCI bytes, GAIA/Tau default-pinned, AppWorld three roles pinned; TB's 89 external task manifests and the 3 unobtainable images are a documented external constraint; native host closure is 5/7 with ScienceWorld at initialization-only |
| S4 official provenance/execution | PARTIAL | **close with recorded unobtainables** | ~15 datasets executed; the rest each have a recorded reason (no row catalog, no content digest, no historical metadata) |
| S5 lifecycle/resource/cleanup | PARTIAL | **close** | live lifecycle/resource/cleanup observations now exist for every runtime class including JVM, LibreOffice and child-process |
| S6 validate live controls before pilots | PARTIAL | **restate or withdraw** | the control half is achieved (TB measured 0.0, pristine measured 0.0, ChessBench terminal exchange, ALFWorld noop, AppWorld measured loss); the *publication* half depends on admission the shared gates withhold, which is a different clause |
| S7 snapshot/service connectivity preserved | SATISFIED | keep | contract + `verifier.py` retain service networking and recordings |
| S8 compare only matching known classes | SATISFIED | keep | isolation classes, mixed refusal, unknown non-comparability |

## `artifact-only-state-export` — clause by clause

| clause | now | proposed disposition | deciding evidence |
|---|---|---|---|
| E1/E2/E3 per-task export, private inputs, ownership | SATISFIED for an empty instance set | keep as recorded | 0 of 28 datasets declare `pristine-offline` (`registry` + `w-scope`); the mechanism is implemented and control-verified |
| E4 quiescence / trial binding | PARTIAL | **close** | interval quiescence detection implemented (changed mtime/ctime → `difference_observed`, `score=null`, unmeasured) and native task/run/trial binding enforced with every foreign export and verdict refused; the residual threat model is a recorded limit |
| E5 scoring equivalence | PARTIAL | **close** | 18/18 authored pairs preserve scores across 9/24 routes with 18 tamper refusals; the WAL score-flip defect was reproduced and fixed; dataset-specific export transformations are a recorded limit |
| E6 live lifecycle/cleanup | PARTIAL | **close** | live controls across the remaining branches; the two defects it found (verifier recording-mount retained on timeout, DS-1000 wrapper scratch leak) are fixed and verified |
| E7 snapshot/service surfaces reviewed | SATISFIED | keep | four surfaces reviewed under their declared class |
| E8 no inferred artifact allowlist | SATISFIED | keep | class-specific treatment, no blanket pristine requirement |

## Effect on the dataset-own blockers

| group | disposition |
|---|---|
| `journal-coverage` × 6, `hotpotqa`, `triviaqa` | **unblocked once the shared gates close**, then each still needs an operator-supplied selected manifest — keep open and mark that input as the single remaining requirement |
| proven unobtainable: `livecodebench`, `twowikimultihopqa/hub-data-provenance`, `twowikimultihopqa/ujson-native-offline-closure`, `bird_minidev`, `ds1000` | **convert to standing limits** with the unavailability evidence |
| operator decides: `gaia` (its own action says do not run), `tau_bench` (keep open), `chessbench_puzzles/interruption-closure` (keep open) | leave untouched |
| `appworld/successful-task-evidence` | keep open: needs a genuinely successful measured task; one loss at unchanged budget does not prove impossibility |
| permanent refusals: `api_bank`, `nestful`, `sotuqa`, `tau2_bench` | unchanged |

## What this buys, stated honestly

- **6 datasets clear immediately**: `alfworld`, `gsm8k`, `jericho`, `musique`, `scienceworld`, `terminal_bench` (each has zero own blockers and is held only by the two shared gates). `agentdojo` is already clear.
- **8 downstream blockers become attackable** instead of gated.
- The tail becomes **finite and enumerable**: the selected-manifest family plus the operator-decided trio.

It does **not** claim any of the standing limits were solved. Every one of them is recorded
with the evidence that it cannot be solved here, which is the opposite of deleting a gate to
make a number look better.
