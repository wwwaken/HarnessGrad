# SpreadsheetBench mirror-to-release custody - w-jc2

Read first: AGENTS.md and reports/w-journalcov-review.md. This packet satisfies the
journal-coverage report's single next concrete action at the exact installed
Verified 400 provenance scope. It does not close the registry blocker or any
shared gate, and provides no selection, run ID or measurement authorization.

## What moved

The original publisher's current repository independently corroborates the mirror.
The public pinned upstream README explicitly announces SpreadsheetBench Verified,
an expert annotated subset of 400, and links the KAKA22 Verified 400 archive:
`tests/fixtures/hg_wjc2/spread/responses/github-release-readme-pinned.decoded.md:11`.
This statement is acquired at commit
`49b73a94775fb489063f60ca1865e3a650079a79`; its decoded source SHA-256 is
`ba96370b14fa897a61d7a68f3ada6399391d0a4f5d4a8bb9be2a1a38a4316143`, independently
recomputed in `tests/fixtures/hg_wjc2/spread/command-22.stdout.txt:7`.
The public canonical API archive entry is retained losslessly in
`tests/fixtures/hg_wjc2/spread/responses/github-release-archive-metadata-pinned.body:1`.
The exact pinned tree and commit responses, headers, URLs and statuses are retained
beside it; discovery through movable main is followed by a commit-pinned tree,
README, archive metadata and raw archive download.

That independently downloaded upstream archive returned HTTP 200 and 14,958,255
bytes (`tests/fixtures/hg_wjc2/spread/command-20.stdout.txt:2`). Its SHA-256 is
`10ef893dd29cb13ab97143ea787e68cdc9574a13873ab9a54e50b31dc03fc949`, byte-equal to
the installed mirror archive, and its freshly recomputed Git blob SHA-1 is
`b6baaf0f23ef5adc1cd22078f4eeb3102b4a7c72`, matching the canonical publisher's
pinned tree/API (`tests/fixtures/hg_wjc2/spread/summary.json:2`). The canonical
Hugging Face pinned tree also advertises this archive's same LFS SHA-256 and size;
its raw response is `tests/fixtures/hg_wjc2/spread/responses/hub-tree-proxy.body:1`.
Independent archive SHA-256 output is in
`tests/fixtures/hg_wjc2/spread/command-22.stdout.txt:2` and
`tests/fixtures/hg_wjc2/spread/command-22.stdout.txt:3`.

The current installed metadata, SHA-256
`bcecaa89a005bd4e3bbe98da150a86e8062c27f262e575d5e47bd9861b3525e7`, and all 800
workbooks chosen by the unchanged loader match both the mirror and canonical
upstream archive members. `tests/fixtures/hg_wjc2/spread/summary.json:15` records
full member equality; `tests/fixtures/hg_wjc2/spread/summary.json:35` binds metadata;
`tests/fixtures/hg_wjc2/spread/summary.json:53` records chosen-workbook count.
`tests/fixtures/hg_wjc2/spread/member-mapping.json:3` starts the complete per-task
ordered row digest and exact member inventory, with explicit upstream equality
for every chosen workbook. These are full-pool custody records, not a selected
manifest, eligibility inventory or task/trial result table.

Task `283-32` remains in the released denominator. Its exact chosen pair and
fresh member digests are retained at
`tests/fixtures/hg_wjc2/spread/member-mapping.json:1059`, and its released
`Sheet3'!A:G,'Sheet4'!A:G` answer-position string remains unchanged at
`tests/fixtures/hg_wjc2/spread/member-mapping.json:1123`.
The current pinned publisher tree also preserves the same official parser/scorer
Git blob as the earlier acquired source. A fresh function-only AST projection
rechecks all metadata range components, with one rejected task/two A:G components:
`tests/fixtures/hg_wjc2/spread/parser-audit.json:2` and
`tests/fixtures/hg_wjc2/spread/command-25.stdout.txt:1`.
No workbook is opened or scored in this parser check. The official-range-zero
policy remains intact, and each installed task still uses its one deterministic
init/golden pair; no paper soft/hard aggregate is inferred.

## What did not move

Canonical release authentication is not per-row gradability. The publisher's
expert-annotation statement is a release description, not an execution-bound
eligibility or coverage record. No official comparator/workbook execution,
formula/LibreOffice runtime/offline closure, selected-only export, selected split
or side, trial denominator, pristine verifier, lifecycle/cleanup or shared-gate
closure is supplied. Actual run-specific fields remain null at
`tests/fixtures/hg_wjc2/spread/summary.json:57`; gradability and production
authorization remain false at `tests/fixtures/hg_wjc2/spread/summary.json:66`.

A separate historical comparison explains why the old 912 archive cannot be
substituted for this Verified release: all 400 IDs exist in that archive, but 226
metadata rows change and 94 of the chosen workbook bytes lack a same-task original
exact match. Counts and changed fields are in
`tests/fixtures/hg_wjc2/spread/summary.json:42` through line 56. This is a measured
byte comparison, not a semantic judgement or missing-producer assertion about the
now-authenticated Verified archive. The old archive's producer transformation
history is not authenticated and no original-912 metric comparability is claimed.

## Single remaining blocker to closure

The remaining dataset blocker requires an independently supplied selected-only
qualification/scoring evidence packet: an authorized fresh run ID, ordered task
IDs and explicit split/side must precede any selected export and valid execution.
That packet must establish actual row-level eligibility/coverage under the retained
range-zero policy and include required official-scorer/runtime/offline and shared
admission/lifecycle evidence. The assignment supplies none of those run inputs;
this packet cannot synthesize them from the full-pool custody inventory. The
provenance follow-up itself is now satisfied, so a producer mapping is not carried
forward as an unmet input for the exact Verified 400 release.

## Reproduction and preservation

`python3 tests/fixtures/hg_wjc2/spread/audit.py --check` recomputes archive SHA-256
and Git blob identities, checks the pinned canonical/API/Hub linkage, rehashes and
compares all chosen members, reproduces historical comparisons and the parser-only
check, and refuses changed JSON outputs without rewriting them. The source adapter
and checker hashes are independently captured at
`tests/fixtures/hg_wjc2/spread/command-22.stdout.txt:5` and line 6.
Both downloaded archives remain outside the repository at the paths recorded in
summary.json; their URL/status/header/command records are committed here. Preserve
those preimages for replay. Public transport failures are retained under distinct
response/command names; they do not masquerade as downloaded data. Header streams
and the mirror card use lossless JSON-string wrappers listed in
encoded-preimages.json so their original CRLF/trailing whitespace survives
without introducing staged whitespace errors; command-29 retains the original
failed whitespace check as a JSON-encoded raw output. Every wrapper binds the
original byte count and SHA-256, and `verify_preimages.py` checks these bytes plus
all received body digests against the response receipts.

Registry checks before and after are preserved in command-00 and command-23.
No registry, journal, production source, runs, frozen receipts or endpoint is
changed by this subpacket. The parent is responsible for final registry observation,
focused tests, journal review and integration.
