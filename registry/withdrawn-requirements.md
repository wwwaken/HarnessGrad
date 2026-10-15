# Withdrawn requirements: proven-unobtainable evidence becomes a recorded limit

Operator decision, 2026-10-15. This file is the evidence record for every blocker
requirement withdrawn under this decision. It follows the same standard the operator
already applied to `paired-filesystem-quotas`, `snapshot-owned-cleanup` and
`official-scorer-identity`: **a requirement that cannot be satisfied here is recorded as a
limit with the search evidence attached, rather than left open forever.**

A requirement withdrawn here is one that no amount of further work in this repository can
satisfy — not one that is merely difficult. Each entry names what was searched and what
came back empty or impossible.

## Shared requirement withdrawn: S6 "validate live controls before pilots"

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

## Dataset requirements withdrawn as unobtainable

### `livecodebench / row-attestation`
**Asked for:** a metadata-only complete upstream catalogue/rank plus authenticated
row/pool/split/statement linkage.
**Searched:** the authoritative upstream source, repeatedly, across three separate rounds.
**Result:** **zero authoritative upstream row IDs obtainable**; the upstream count is not
published, so the locally declared 1,055 count cannot be corroborated from public sources.
Six pinned shard identities were linked to the adapter's own declarations, and the inert
selection and conditional split reproduce — that part is retained.

### `twowikimultihopqa / hub-data-provenance`
**Asked for:** metadata-only original-release archive/file digest custody and completeness
attestation.
**Searched:** exact-revision upload history, release/tag inventories, a zero-result
licence-issue search, and the original and later Dropbox HEAD receipts.
**Result:** the original release is advertised with an **opaque ETag and no content digest**
(a 259,216,602-byte attachment). An opaque ETag is not a digest and was explicitly refused
as a substitute. The paper claims 192,606 examples while the witness card carries
conflicting counts, so no coverage attestation can be derived either.

### `twowikimultihopqa / ujson-native-offline-closure`
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

## What this decision does not do

- It does not claim any withdrawn requirement was solved. Each is recorded with the search
  that failed.
- It does not touch the four permanent refusals (`api_bank`, `nestful`, `sotuqa`,
  `tau2_bench`), whose `retain-contract-refusal` entries stay exactly as they are.
- It does not touch the operator-decided trio: `gaia` (its own action says do not provision
  or run), `tau_bench` and `chessbench_puzzles/interruption-closure` (both say keep open).
- It does not withdraw anything whose evidence merely has not been collected yet. The
  `journal-coverage` family, `hotpotqa` and `triviaqa` stay open because what they need is an
  operator-supplied selected manifest, which is an input rather than an impossibility.
- Every withdrawn blocker's text, evidence list and historical record remain readable in the
  git history of `registry/dataset-blockers.json`; the removals are the diff.
