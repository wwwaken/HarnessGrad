# Task 198 — LiveCodeBench release and row provenance research

Research date: 2026-10-14 UTC. Workspace:
`/tmp/hg-codex-198`, isolated detached worktree based on
`16e3151f644cc1a0052e2bf09fa887d381066006`.

## Finding

**No qualifying official, independent metadata attestation was obtained binding
the local pool's row 740 to `abc360_a`. The row gate remains
`BLOCKED_EXTERNAL_ROW_ATTESTATION`.** This is a bounded search result, not proof
that no such attestation exists anywhere. The pinned Hugging Face metadata and
official loader contents could not be retrieved, so those search surfaces remain
unresolved.

The official GitHub API reports a verified signature for the pinned **source
commit**. That signature does not attest to the separately pinned dataset
revision, the local sorted pool, row 740, or the local training split. No positive
custodian record or reviewer approval was constructed.

## Release and index mechanism: what the evidence establishes

| Layer | Observed evidence | Meaning and limit |
| --- | --- | --- |
| Official source repository | The complete recursive tree at `LiveCodeBench/LiveCodeBench@28fef95ea8c9f7a547c8329f2cd3d32b92c1fa24` contains `lcb_runner/benchmarks/code_generation.py`. | Confirms the official benchmark-loader location; tree metadata does not reveal loader behavior. |
| GitHub release publication | The repository's Releases and Tags API requests each returned `[]`. | No GitHub Release/tag mechanism was exposed by these requests; does not exclude dataset-side release configurations. |
| Source pin and signature | Commit API returns matching SHA and `commit.verification.verified=true`, `reason=valid`; the commit concerns an Explorer URL typo. | GitHub's reported commit-signature status is observed. No independent PGP verification or row claim is established. |
| Current source lookup | A recursive `main` tree lookup resolved to the same pinned commit and was not truncated. | The inspected current and pinned source path inventories match at retrieval time. This was a read-only public URL lookup, not local main-branch work. |
| Dataset release pointer | Local `data/livecodebench.py` declares `livecodebench/code_generation_lite@0fe84c3912ea0c4d4a78037083943e8f0c4dd505`, calls it `release_v6`, and lists six shards. | Repository declarations identify the intended dataset pin. The corresponding official Hugging Face manifest/builder was not retrieved; these declarations are not independent release or row evidence. |
| Local pool construction | `prepare.py` unions `test.jsonl` through `test6.jsonl`, rejects duplicate `question_id`s, then returns `[rows[qid] for qid in sorted(rows)]`. | Local order is Python string sort by question ID, independent of any upstream physical ordinal. Code was read as text, never executed. |
| Local task numbering | The adapter skips one header, enumerates body records from zero, and names tasks `livecodebench/{index}`. | Local row 740 is sorted body position 740. Assuming the emitted one-record-per-line format, it is body ordinal 741 / physical JSONL line 742. No row was opened. |
| Local split | `registry.default_split` hashes the original task ID; `is_eval_id` tests byte zero modulo 3. The adapter declares `SPLIT_SOURCE="hash"`. | The requested `train` claim belongs to HarnessGrad's imposed split, not an upstream official training split. Its declared full split digest was not independently attested here. |

The intended dataset release lives separately from the signed source commit.
The complete official configuration/shard-composition mechanism, upstream
ordering and published metadata-index facilities remain unverified because the
dataset metadata and loader-content requests failed. In particular, this report
does **not** claim that an official `test[740]` equals local `livecodebench/740`,
or that `release_v6` is a Git tag or an officially published training split.

## Public signed/custodian metadata search

The inspected, non-truncated source trees contain no path advertised as a row
index, custody manifest, signature sidecar or attestation document. This is a
path-inventory observation, not a semantic inspection of all source files.
The empty GitHub Releases/Tags responses provide no release asset attestation to
inspect. The source commit signature covers its Git commit payload/tree; it
contains no explicit `740 -> abc360_a` claim, local pool digest or split digest.

Requests to Hugging Face's revision metadata, tree and refs APIs failed with
network-unreachable errors or timeouts. A candidate pinned builder-file request
also failed; its existence was not confirmed. Raw GitHub and GitHub code-page
requests failed with resets, network errors or timeouts. GitHub blob/contents
requests returned HTTP 403 rate-limit errors. These failures are **not** negative
evidence about what the uninspected dataset repository publishes.

No dataset viewer, `/rows`, `/first-rows`, Parquet, shard, pool, statement,
prompt/example, test, solution, or heldout-payload endpoint was used. No upstream
archive was fetched because it could contain prompt/example payloads. No mirror
or locally invented record was accepted as custodian evidence.

## Primary-source receipts

All retained responses and failed-request records are in
[`task-198-livecodebench-evidence/`](task-198-livecodebench-evidence/).
Fetch indexes record requested URL, retrieval time, result, and response
SHA-256/size where a response was saved. Those hashes preserve research evidence;
they do not establish custody of a dataset row.

| Source | Public URL | Result |
| --- | --- | --- |
| S1: pinned official source tree | https://api.github.com/repos/LiveCodeBench/LiveCodeBench/git/trees/28fef95ea8c9f7a547c8329f2cd3d32b92c1fa24?recursive=1 | HTTP 200; `truncated=false`. |
| S2: pinned official source commit | https://api.github.com/repos/LiveCodeBench/LiveCodeBench/commits/28fef95ea8c9f7a547c8329f2cd3d32b92c1fa24 | HTTP 200; GitHub reports a valid verified signature. |
| S3: official GitHub Releases | https://api.github.com/repos/LiveCodeBench/LiveCodeBench/releases?per_page=100 | HTTP 200; empty list. |
| S4: official GitHub Tags | https://api.github.com/repos/LiveCodeBench/LiveCodeBench/tags?per_page=100 | HTTP 200; empty list. |
| S5: current official source tree | https://api.github.com/repos/LiveCodeBench/LiveCodeBench/git/trees/main?recursive=1 | HTTP 200; same commit/tree inventory as S1. |
| S6: official pinned dataset metadata | https://huggingface.co/api/datasets/livecodebench/code_generation_lite/revision/0fe84c3912ea0c4d4a78037083943e8f0c4dd505 | Unreachable; IPv4 retry timed out. |
| S7: official pinned dataset file inventory | https://huggingface.co/api/datasets/livecodebench/code_generation_lite/tree/0fe84c3912ea0c4d4a78037083943e8f0c4dd505?recursive=true&expand=false | Unreachable; IPv4 retry timed out. |
| S8: official dataset refs | https://huggingface.co/api/datasets/livecodebench/code_generation_lite/refs | Unreachable. |

The remaining failed code/documentation URL attempts are preserved in the fetch
indexes. No source text was recovered from those attempts, and no quoted official
loader behavior is inferred from them.

Local code/documentation used only to define the requested claim:

- `data/livecodebench.py`: pins/constants at lines 74–96, pool header/body handling
  at 185–205, indexing/split declarations at 285–298.
- `data/livecodebench/prepare.py`: declared shards and `build()` transformation.
- `data/registry.py`: `split_sha`, `is_eval_id`, `default_split`.
- `tools/lcb740_identity.py`: strict metadata schema and independently supplied
  approval-digest requirement.
- `reports/LCB_GATE.md`, `DOWNLOADS.md` and the existing journal/blocker entries:
  historical declarations of the unresolved gate. They are local claims, not
  independent custody evidence. The public-statement file and all pool/source
  rows, tests and reference solutions were left unread.

## Custodian action

The unsent
[`task-198-livecodebench-custodian-request.md`](task-198-livecodebench-custodian-request.md)
contains the exact requested record fields, distinct upstream/local custody
claims, an authenticated detached-envelope request, separate reviewer approval,
index-base checks and a metadata-only verification protocol. It asks the
custodian to correct an unsupported mapping rather than endorse the proposed
values. Unavailable metadata catalogs or custody receipts leave the gate blocked.

## Scope and validation receipt

Only Task 198 documentation/evidence is added in this worktree. Existing gates,
receipts, source code, journals and launch manifests are unchanged. No adapter
was imported and no dataset construction or admission entry point was executed.
Research has no metric identity, eligible/selected benchmark coverage,
task/trial score, endpoint binding, model/harness run hash or GPU measurement:
all are not applicable, not zero. No H0/model/main work was performed.

Metadata/code requests used bounded reads and short request timeouts; successful
responses were small repository metadata. Request failures remain recorded.
Validation checks retained response hashes, complete source-tree inventories,
the commit identity/signature-report fields, requested-URL scope, documentation
links and diff whitespace. No benchmark or payload-reading tests are warranted
for this documentation-only change.
