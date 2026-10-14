# Task 195 — BFCL v1.3/V3 public code provenance

**Result: partial code acquisition completed; official full-call scorer closure
remains blocked.** Work is confined to `/tmp/hg-codex-195`. Production adapter,
scorer, registry and main worktree are unchanged. No H0/model run or benchmark
task/answer/heldout/external dataset-root access occurred.

## Authoritative findings

The Berkeley BFCL site links to `ShishirPatil/gorilla`. The public `v1.3`
lightweight tag resolved to immutable commit
`ea13468e4423454d0c213704fb87cf7cb3990433` (tree
`b34aa53a73491f42dc69b8b18c92448d7c311f50`). The repository's release, published
2025-07-17, explicitly identifies V3. The release has no attached assets;
`target_commitish=main` is a branch label, not an immutable commit pin.

Seven original files (126,311 bytes) were acquired through the public GitHub
contents API at that commit: root LICENSE, BFCL pyproject.toml, type_mappings.py,
eval_runner.py, eval_runner_helper.py, base_handler.py and model_handler/utils.py.
Each SHA-256, byte count, original path, URL, commit-qualified raw URL and Git blob
SHA-1 is preserved in the
[candidate provenance record](tests/fixtures/bfcl_ast_source/candidate-codex195/provenance.json).
Returned code bytes match the upstream Git blob hashes. The original Apache-2.0
license is preserved, with the pinned package's matching license declaration.
Original source/license bytes are unchanged.

Verified partial semantics: the default prompting parser retains dotted names
and collects keyword arguments; model-specific decoding is separate. The category
runner records binary AST-checker validity, with accuracy
`correct_count / len(model_result)` and decode/format failures in the denominator.
The leaderboard's non-live Simple AST score averages Python `simple`, `java` and
`javascript` category accuracies equally; a Python-only selected subset is a
different metric scope. Internal scores are fractions, rendered as percentages.
All source symbols, line citations, exception behavior and limits are documented
in the [candidate source review](tests/fixtures/bfcl_ast_source/candidate-codex195/README.md).

## Unresolved findings and exact handoff

The pinned directory metadata identifies
`bfcl_eval/eval_checker/ast_eval/ast_checker.py`, Git blob
`214f3ba55c012691761913b6aca68ab7bc4aa38b`. Its source body and transitive helper
graph remain unacquired. Public API requests for the checker and remaining
constants/helpers returned rate-limit HTTP 403; the GitHub code page timed out.
Raw-host source fetches failed with network-unreachable errors before the allowed
contents API successfully supplied the retained files. Failed requests are not
evaluator receipts or benchmark scores.

The checker's signature and full-call matching rules, concrete selected-handler
decoder, parser/native grammar dependencies, complete import/runtime/license
closure and actual category constants remain unresolved. The repository release
prose verifies the v1.3/V3 relationship; it does not replace review of those files.
The locally declared tar.gz digest
`57854157e82aed5723a1458d2a4ac426e3256959ded4a20ddc4d627c22edb7fe` and
archive-member bindings are **unverified**. No archive was requested or opened.

The [exact custodian request](tests/fixtures/bfcl_ast_source/candidate-codex195/CUSTODIAN_REQUEST.md)
specifies missing original source, dependency discovery, independent historical
tag/archive/member custody, offline/runtime/license closure and a separately
approved exact receipt pin. It requests code and metadata only. No confirmation,
substitute release, fabricated license/helper, source-derived self-approval or
official full-call metric claim has been supplied.

The candidate has a deliberately different schema and explicit
`status=blocked`, `measured=false`, `production_authorized=false`,
`custodian_approved=false`. The approved parent receipt remains absent and the
registry remains external. The existing fixture README now acknowledges the
candidate without promoting it. Remaining index/privacy/runtime/export/quota/
cleanup and diagnostic review gates are independent.

## Validation

- Existing source-contract suite: **37 passed**. Plugin autoload, bytecode and
  pytest cache were disabled; temporary files stayed in this worktree.
- Static audit: all seven sizes/SHA-256/Git blob identities, original license,
  source syntax and acquired entrypoint line numbers verified. No upstream module
  was imported or executed.
- Explicit existing source gate: expected exit **2**, fixed blocked result,
  `measured=false`, `production_authorized=false`.
- Candidate negative admission: even with its computed integrity digest supplied
  for this negative check, the existing gate rejects its schema **before any
  projected source read**. This digest is not independent custody approval.
- Diff review: authored documents and metadata pass whitespace checks. Three
  trailing-whitespace lines in original upstream `model_handler/utils.py`
  (181–183) are retained to preserve the verified original file bytes.
- No benchmark controls, tasks/trials, score generation, provider/model calls,
  GPU activity, archive/data downloads, package installs or production changes.

The parent should review this task's exact diff and commit before any merge.
