# BFCL v1.3/V3 custody operator packet — Task 208

**Status: blocked; metadata/code-only handoff, no production authorization.**
Task 195 retained seven original files; `ast_checker` and complete dependency,
archive/member, runtime/license and selected-index custody remain open. This
packet uses only local evidence. No acquisition, dataset read or model run is
requested here. Preserve the candidate and all earlier receipts unchanged.

## Fixed identity and delivery

- Repository: `https://github.com/ShishirPatil/gorilla`; tag: `v1.3`.
- Observed immutable commit: `ea13468e4423454d0c213704fb87cf7cb3990433`;
  tree: `b34aa53a73491f42dc69b8b18c92448d7c311f50`.
- Declared archive: `https://codeload.github.com/ShishirPatil/gorilla/tar.gz/refs/tags/v1.3`;
  SHA-256: `57854157e82aed5723a1458d2a4ac426e3256959ded4a20ddc4d627c22edb7fe`.
  **Archive digest and member bindings are unverified.** The observed lightweight
  tag and V3 release prose do not establish historical archive custody.

These upstream identities and release statements are retained Task 195
observations. The candidate records metadata response digests, but the response
bodies are not retained with it; this packet cannot independently reverify those
observations offline from this handoff. Local source/Git blob agreement checks
integrity against the candidate's declarations, not independent ref, archive or
member custody.

Deliver reviewed original code/license/specification bytes to
`tests/fixtures/bfcl_ast_source/files/<repository-relative-path>` and the approved
metadata receipt to `tests/fixtures/bfcl_ast_source/provenance.json`. These are
future handoff targets, currently absent. Archive, benchmark payload and custody
evidence stay with the trusted custodian outside actor state and this projection.
Supply only metadata attestations here; stop on any identity mismatch, without
repinning, downloading or opening an archive in this worktree.

## Exact source inventory

In this table, `B/` expands to the repository prefix
`berkeley-function-call-leaderboard/`; `E/` expands to `B/bfcl_eval/`.
Retained bytes are under `tests/fixtures/bfcl_ast_source/candidate-codex195/files/`.
Their exact sizes/SHA-256/Git blob identities are in the
[candidate provenance](../tests/fixtures/bfcl_ast_source/candidate-codex195/provenance.json).

| State | Original repository-relative files |
| --- | --- |
| Retained; independent custody still needed | `LICENSE`; `B/pyproject.toml` |
| Retained; independent custody still needed | `E/constants/type_mappings.py`; `E/eval_checker/eval_runner.py`; `E/eval_checker/eval_runner_helper.py`; `E/model_handler/base_handler.py`; `E/model_handler/utils.py` |
| Missing checker | `E/eval_checker/ast_eval/ast_checker.py` — observed Git blob `214f3ba55c012691761913b6aca68ab7bc4aa38b`; body/signature unresolved |
| Missing parser/style | `E/model_handler/parser/java_parser.py`; `E/model_handler/parser/js_parser.py`; `E/model_handler/model_style.py` |
| Missing constants/utilities | `E/constants/default_prompts.py`; `E/constants/category_mapping.py`; `E/constants/eval_config.py`; `E/constants/column_headers.py`; `E/constants/model_config.py`; `E/utils.py` |
| Known imported paths; review necessity for the permitted invocation | `E/eval_checker/multi_turn_eval/multi_turn_checker.py`; `E/eval_checker/multi_turn_eval/multi_turn_utils.py` |

Discover the actual transitive checker helpers under
`E/eval_checker/ast_eval/type_convertor/`, the intended concrete model handler's
`decode_ast`, package initialization files and all further required imports/calls.
Their complete filenames are unknown; enumerate from original source before
delivery. `BaseHandler.decode_ast` is abstract. Establish prompting versus native
function-calling decoding and exact Simple/language dispatch. Reject source with
embedded benchmark payload. Do not invent files, stub dependencies, delete
imports or substitute another release to manufacture closure.

## Independent approval, license and runtime closure

The acquisition owner supplies the exact
[`harnessgrad.bfcl-ast-source.v1` contract](../tests/fixtures/bfcl_ast_source/README.md#required-code-only-handoff),
including nonempty reviewer/evidence identities for tag-to-commit linkage,
archive/member custody, code-only closure and entrypoint contract. Each file row
has exactly `path`, `role`, `bytes`, `sha256`, `archive_member`, `requires`;
member bindings must be independently verified as `gorilla-1.3/<path>`.
Preserve original bytes; enumerate every required in-repository edge and all
three source-derived parser/checker/dispatch entrypoints. Receipt limits are
1 MiB, 256 files and 16 MiB total projected bytes. Follow the linked exact schema;
do not add runtime/index records to it or rename the candidate schema.

The approved receipt's exact top-level fields are `schema`, `repository`,
`repo_tag`, `archive_sha256`, `commit`, `review`, `entrypoints`, `files`.
`review` has exactly `reviewed_by`, `tag_commit_binding`,
`archive_member_binding`, `code_only_closure`, `entrypoint_contract`, each a
nonempty reviewer/evidence identity string. `entrypoints` has exactly
`parser`, `checker`, `dispatch`; each has exactly `path`, `symbol` and names a
declared source file. Independent review must bind `commit` to the observed pin
above: the gate checks only nonzero 40-character lowercase hexadecimal shape,
not equality to that pin. It checks declared dependency edges, not discovery of
the actual complete import/call graph or symbol definitions.

An independent reviewer supplies the SHA-256 of the **exact approved receipt
bytes through a separate trusted channel**, with reviewer and custody evidence
identity recorded outside the receipt/projection. The caller authenticates that
channel and freezes the projection during verification. A locally computed
candidate/receipt hash establishes integrity only; it cannot grant approval.
Any receipt edit requires renewed independent review and a new exact pin. No
approval pin has been supplied in Task 195 or Task 208.

Retain the original Apache-2.0 `LICENSE` and pinned package declaration; review
the entire delivered closure for applicable LICENSE/NOTICE, attribution and
redistribution obligations. Task 195 observed no alternate root/package-root
NOTICE, which does not settle nested or third-party coverage. Separately supply
a reviewed metadata-only offline runtime lock and license inventory: concrete
handler/invocation, full import/call graph, Python version/ABI/platform, immutable
image identity, every package/wheel/native grammar version and hash, and original
license/notice coverage. Record exact evidence identities and an independent
approval of these runtime artifacts. `pyproject.toml` requires Python >=3.10 and
pins `tree_sitter==0.21.3`, `tree-sitter-java==0.21.0` and
`tree-sitter-javascript==0.21.4`; it is not a complete lock. Account for build and
import-time dependencies, including optional imports actually required by the
chosen invocation. Missing offline artifacts, unreviewed expression-evaluation
branches or network/install requirements remain blockers; run no upstream module
or package installation in this documentation task.

## Separate selected-index and release-storage custody

The custodian must independently approve the exact bytes, size and SHA-256 of
`selected-index.v1.json`, binding them to the release above and authenticated
immutable source storage. Metadata must attest `schema_version=1`, `repo_tag`,
`tarball_sha256`, and a `tasks` object keyed by selected canonical task ID.
IDs are `simple/<index>` (0–399) or `irrelevance/<index>` (0–239), with decimal
indices and no leading zeros except the single digit `0`.
Each entry has a nonempty string `question_id`, a `question` span and (for Simple)
an `answer` span; each span has `offset`, `length`, `sha256`. Offsets and lengths
are integers excluding booleans: offset >= 0, 0 < length <= 1 MiB, and
offset + length <= min(sys.maxsize, 2**63 - 1), as well as within the fixed
source file's size. Digests are 64 lowercase hexadecimal characters. These
are local reader limits, not measured release maxima. Bind IDs/spans to
original member identities, row identities and the declared split/selection
manifest. The adapter fixes payload paths via `SIMPLE`, `IRRELEVANCE` and
`SIMPLE_ANSWERS` in [data/bfcl_v3.py](../data/bfcl_v3.py); the index cannot choose
paths. Custody must also attest complete selected raw schemas/reference
alternatives for the future trusted full-call verifier, without exporting them.

Supply index approval independently of source-receipt approval. Keep index bytes,
payloads and split verification in trusted custody; deliver metadata evidence
only to this worktree. The current selected reader validates caller-authored
release fields/spans, **not an independently approved index digest**. This packet
adds no admission implementation. An authenticated pre-read index/storage gate
still needs separate implementation and review; source-gate success cannot close
it. No full-pool scan, index-build fallback or external dataset-root inspection
is permitted here.

## Verification order and stop conditions

1. Review the retained evidence and the custodian's identities, code-only scope,
   original file inventory, licenses and archive/tag/member attestations. Missing
   bytes, unresolved imports or any mismatch stop admission. Reconcile the seven
   retained file hashes against independent custody; Git blob agreement alone
   does not bind compressed archive bytes.
2. Check the current fail-closed source gate and fabricated regressions from
   `/tmp/hg-codex-208` with scratch confined to this worktree:

   ```sh
   PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 \
     tests/quality/test_bfcl_ast_source_contract.py
   # Expected exit 2: blocked, measured=false, production_authorized=false.
   mkdir -p .scratch/bfcl-codex208
   PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
     python3 -m pytest -q -p no:cacheprovider \
     --basetemp=.scratch/bfcl-codex208/pytest \
     tests/quality/test_bfcl_ast_source_contract.py \
     tests/quality/test_bfcl_selected.py tests/quality/test_dataset_blockers.py
   ```

3. **Only after delivery and independent approval**, supply the trusted-channel
   pin as `BFCL_APPROVED_SOURCE_RECEIPT_SHA256` and run:

   ```sh
   PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 \
     tests/quality/test_bfcl_ast_source_contract.py \
     --receipt-sha256 "${BFCL_APPROVED_SOURCE_RECEIPT_SHA256:?independent approved pin required}"
   ```

   Require exit 0 and scope `approved_code_projection_integrity`; it remains
   `measured=false`, `production_authorized=false`. The test-only gate neither
   imports source nor authenticates reviewer identity, semantics or runtime.
4. Separately review original checker/decoder/dispatch rules with symbol/line
   citations, then validate offline runtime/license closure and fabricated
   differential controls in a later authorized isolated verifier task. No
   benchmark predictions are executed by this packet. Python-only selected
   accuracy differs from the non-live Simple AST mean over Python/Java/JavaScript;
   keep the existing function-name metric explicitly nonofficial.
5. Independently close selected-index/storage/split admission, full-call reference
   preservation, trusted verifier isolation, artifact-only export, quota,
   snapshot lifecycle and cleanup. Only after every dataset gate and separate
   authorization may a fresh one-task/one-trial diagnostic run. Review its valid
   measured receipt separately before any expansion; failures/unmeasured results
   are not ordinary zero scores. This packet authorizes no H0 or pilot.

Evidence: [Task 195 report](../bfcl-source-provenance-codex195-report.md),
[source review](../tests/fixtures/bfcl_ast_source/candidate-codex195/README.md),
[custodian request](../tests/fixtures/bfcl_ast_source/candidate-codex195/CUSTODIAN_REQUEST.md),
source contract/gate above and selected-reader source/regressions. Historical
403/timeouts are failed acquisition attempts, not evaluator receipts or scores.

Task 208 validation: **165 passed** across the three modules above; unpinned
source gate exited **2** with the fixed blocked result. All seven retained
size/SHA-256/Git blob identities (126,311 bytes) and local document links were
rechecked. No benchmark files, archive, external dataset root, network fetch,
upstream evaluator execution, package installation or model/GPU run was used.
