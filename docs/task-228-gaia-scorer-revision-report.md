# GAIA scorer full-revision discrepancy — Task 228

**Disposition: `BLOCKED_CANONICAL_FULL_REVISION_RELATIONSHIP_UNRESOLVED`.**
Canonical Hugging Face API and Git-advertisement requests returned no HTTP
response. Neither full upstream commit nor their relationship was authenticated.
No production pin correction is recommended on the available evidence; both
identities and the expected scorer checksum are retained unchanged.

## Scope and evidence

Work was confined to `/tmp/hg-codex-228`, initially at HarnessGrad commit
`61e7f82245c76e7c833740216940d1fcaf3b76be`, tree
`d74461cdd2e3cd6a06f76d2b5b09160f1883dd20`. Inputs were repository source,
documentation, local Git metadata and anonymous requests for public leaderboard
Space metadata/scorer code. No dataset endpoint, questions, answers, attachments,
annotator payload or private gold was accessed. No adapter/scorer import,
dependency installation, Docker, H0, model, benchmark run or main-branch change
was performed.

| Identity | Value | Status |
| --- | --- | --- |
| Adapter Space pin | `9f133d71362ecb0a1c7ff6b4dcfc2a6b9f8ffd1e` | Directly read from source, unchanged |
| Observed candidate | `9f133d71362e77b3539f1514f31b9c101a545fec` | Historical task-200 mirror claim only |
| Expected scorer SHA-256 | `0d44c07f3046eec521697c22e3eaca8719cc81e422a8eaf32695c5f22bdac6e2` | Directly read from source, unchanged |
| Candidate scorer Git blob / size | `ede7ece61d26cc93bf440a86a527163d617e7c12` / 3,212 bytes | Historical task-200 mirror claim only |

The full IDs differ after their common 12-character prefix `9f133d71362e`.
They are distinct 40-character IDs, not short/full forms of one identity.
The historical matching scorer checksum identifies claimed file bytes; it does
not establish commit equality, ancestry, an alias, or the cause of the discrepancy.
No candidate scorer bytes were successfully downloaded or rehashed in task 228.

Machine-readable evidence is in
[the decision record](task-228-gaia-scorer-revision-evidence/decision.json),
[local Git metadata](task-228-gaia-scorer-revision-evidence/local-git-metadata.json),
[canonical request results](task-228-gaia-scorer-revision-evidence/canonical-requests.json),
and [IPv4 retry results](task-228-gaia-scorer-revision-evidence/canonical-ipv4-requests.json).

## Fresh observations versus inherited claims

1. Source-only AST inspection found the adapter pin and expected checksum above.
   `git log -S` traces the pin to the original GAIA adapter commit
   `52077a3ccb90e5c2f0e26d52fb3ce99f2e4ab826`; its declarations equal today's.
   The subsequent adapter commit changes platform web integration and provides
   no revision reconciliation. Neither upstream ID is an object in the local
   HarnessGrad Git object database. That local absence says nothing about
   existence in the upstream Space repository.
2. The task-200 metadata was read directly from Git commit
   `3cc2deed72d83b3a873f98f6cc2ec2111cd281a8`, blob
   `docs/gaia-public-source-research-codex200-metadata.json`. That commit is not
   an ancestor of this task's base. Its claimed candidate API identity,
   scorer/tree/blob/checksum match and pin-specific mirror 404s are preserved
   as inherited observations, with exact Git blob and SHA-256 in the local
   metadata record. They were not reacquired. A mirror 404 does not establish
   canonical nonexistence.
3. On 2026-10-14, 04:18:45–04:19:00 UTC, five anonymous HTTPS requests targeted
   `huggingface.co`: both full-revision Space API lookups, the candidate root
   tree, revision-specific `scorer.py`, and the Space Git upload-pack refs
   advertisement. All failed with `URLError`, `[Errno 101] Network is
   unreachable`, before any HTTP response. Each had a 15-second socket timeout
   and 1 MiB response cap; no token or credential helper was used.
4. At 04:20:26–04:20:31 UTC, both revision API requests were repeated with
   IPv4-only `curl -q`, five-second connection and ten-second total limits.
   Both returned curl exit 28, connection timeout, without an HTTP status.
   These are transport failures, neither HTTP 404s nor revision-existence tests.

## Exact unresolved gate and handoff

**Gate:** canonical evidence must bind a reviewed full Space commit to the exact
expected scorer and adjudicate the adapter pin discrepancy. The current evidence
does not satisfy this gate. A common prefix, checksum equality, local object
absence and mirror-only metadata cannot substitute for it.

The remaining evidence is: successful canonical full-revision responses for both
IDs (retaining any genuine HTTP errors); accepted commit/root-tree metadata and
the exact `scorer.py` path/blob binding; revision-specific code bytes with measured
size, Git blob ID and SHA-256 matching the expected checksum; and an explicit
reviewed disposition of the declared pin versus the candidate. If the old ID
cannot be resolved, record that fact without inventing ancestry or a typo history.
Any commit/tree reconstruction must preserve actual file modes and object bytes.

After that evidence exists, a separately reviewed change may recommend an
accepted full revision and revision-specific acquisition URL. This task makes
no such correction and leaves the existing `resolve/main/scorer.py` declaration
unchanged. Successful source adjudication alone would not close dependency,
license/custody, selected-only, pristine-verifier, snapshot or cleanup gates.

## Validation and execution boundary

All 29 metadata checks passed: JSON parsing, exact source declarations, source
SHA-256 preservation against the base, historical metadata blob/digest binding,
request outcomes, decision/evidence digests, local report links and append-only
journal preservation. `git diff --check` passed. This is document and
metadata validation, not a scorer test or measured diagnostic. There is no model
endpoint binding, run ID, task/trial coverage, metric result or runtime cleanup
receipt; those fields remain null in the decision record. Production authorization
is false. Parent review and integration remain separate.
