# B5 external provenance acquisition — bfcl_v3 and triviaqa

Acquisition and local integrity checks do not supply independent custody or review. All three blockers remain `external`. Work is confined to `/tmp/hg-b5`; no dataset payloads, archive GET, upstream evaluator, model, GPU or H0 run.

## Starting requirements (verbatim)

### bfcl_v3 / release-index-custody

**observed**: Synthetic selected-span checks passed, but index hashes are unauthenticated and official release identity is unproven.

**next_action**: Obtain independently reviewed code-only evaluator provenance and custodian approval of metadata-only release/index bindings.

### bfcl_v3 / simple-ast-contract

**observed**: The pinned v1.3/V3 source and Apache-2.0 license are partially acquired with Git blob checks. ast_checker.py and type_mappings.py are present, but direct model_config, Java converter and JS converter helpers lack pinned blob identities/source; no archive binding or independent custodian receipt exists. Production remains function-name diagnostic-only.

**next_action**: Obtain independently approved v1.3 archive/tag/commit and original-file custody evidence, a code-only parser/checker/dispatch/helper/license projection and a separate exact receipt pin. Pass the explicit source gate, then derive the full-call contract from original symbols using fabricated differential calls; preserve the name diagnostic and selected/privacy boundaries. No production H0.

### triviaqa / hub-export-scorer-linkage

**observed**: Original evaluator acquisition is closed at source/test level; prior reviews retain the corrected triviaqa-alias-max-em-upstream-normalization-all-aliases-v2 identity and upstream reference. Task 225 pins historical HuggingFace loader/config/license at 413205c1a7247a2ff81cf709117ce93624fa6fd3 with reconstructed Git commit/tree/blob linkage. That loader copies and trims normalized aliases, omits HumanAnswers, combines Web/Wikipedia for rc.nocontext, removes documents and omits domain/verified flags. Four exact-revision Hub code/metadata requests failed with network unreachable, so association of that historical loader with Hub revision 0f7faf33a3908546c6fd5b73a660e0f8ff173c2f remains unverified. No dataset rows were read, no metric was changed and full answer-set/selection/grouping/denominator compatibility is not certified.

**next_action**: Obtain public exact-revision Hub commit/tree/config/split metadata and immutable conversion provenance identifying the loader actually used (including predecessor loader plus export receipt if absent at the export revision), original license and file hashes. Establish whether HumanAnswers are preserved, absent or redundant, and document Domain/VerifiedEval/source membership, duplicate handling, scorer-key mapping and denominator/aggregation; no rows or payloads are requested. Historical loader name/schema/count matches alone do not close this gate. Preserve v2 and historical identities; actual deployed hashes and all shared admission gates remain prerequisites to a separately authorized diagnostic.

## Established evidence and remaining decisions

See [the evidence review](../tests/fixtures/external_provenance_b5/README.md) for each blocker’s satisfied portion, exact remaining human decision, source-line findings and transport limits. [The inventory](../tests/fixtures/external_provenance_b5/inventory.json) records every original file’s SHA-256/Git blob/size/path, static dependencies and every request. [SHA256SUMS](../tests/fixtures/external_provenance_b5/SHA256SUMS) hashes all raw responses and their receipts, including failures. Earlier fixtures remain byte-identical.

### bfcl_v3 / release-index-custody

Acquired public tag/V3 release/signed commit/full tree and archive HEAD metadata. Commit bytes and all 93 trees reconstruct to the prior commit/tree pins; the HEAD establishes archive availability/name only. A human custodian must still attest historical archive digest/member and selected-index/span/split bindings; independent evaluator review remains required. No archive/member/index custody is self-approved.

### bfcl_v3 / simple-ast-contract

Acquired 42 additional original source files, reusing all eight unique prior source/license/specification files. The three previously missing direct checker helpers are acquired. Twenty-three remaining imported handler bodies returned 403; exact failures are preserved. Complete source/initializer/native-runtime closure, archive/member/license review and a separate human-approved exact receipt pin remain outstanding. The explicit source gate remains blocked.

### triviaqa / hub-export-scorer-linkage

Acquired exact-revision metadata through the public hf-mirror.com mirror, the actual predecessor-revision script bytes, and conversion PR #8 history linking its parent and addition/deletion commits. The predecessor differs from task 225’s candidate. This closes acquisition of those public declarations, not authoritative Hub-origin authentication or actual converter execution provenance. A human custodian/reviewer must corroborate origin and supply a build/export receipt identifying code/runtime/input identities, then decide answer-set/selection/grouping/denominator compatibility. No rows are needed or claimed.

## Raw evidence SHA-256

All hashes below identify retained raw HTTP bodies. An empty archive HEAD body hash identifies zero bytes, never the archive. Failed transports have no response body; their receipts, not fictional responses, are hashed in SHA256SUMS.

| Dataset / artifact | SHA-256 |
| --- | --- |
| bfcl-tag | `8c0af1047736edde0312513fd217bb4168fc6fd052a221a1212cfba2d537a64f` |
| bfcl-release | `83290385b6160c577bb385d3c83bc990eead8fb57dfeeafb28071762c27592a7` |
| bfcl-commit | `e9f5ca4365d35fe97b3bf8c5497c3859e54625871dde06b05466609892d515f8` |
| bfcl-root-tree | `abc34da884e5821fe189f05aefcd29096e3c04846c391688564fd023d6f2f0bf` |
| bfcl-tree | `f903cf4935a1528bdab0726d8894072f9c69c42e2cc6c5a2e77eb56d64053b49` |
| bfcl-archive-head | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| bfcl-blob-model_config | `5c14b48ae4e3c41357a958c0955351bb6379234e6e359feb672ee6c250f8497b` |
| bfcl-blob-java_type_converter | `3a5dbae4438696e00bb9f175122072c296d6c15746a9072439a60b4026a3d34a` |
| bfcl-blob-js_type_converter | `6750f5e80af0839f9afb48e5b143476f5fa955915834b3f5958f6210bb93da12` |
| bfcl-blob-java_parser | `0a838fc321c5e36883fe56de22da811e9440ad0590fce60582b0a67654cbb53f` |
| bfcl-blob-js_parser | `5a86ea584f5f9426b009b7f4853a0658097d61f126b2616d2b7eed0c76d8284f` |
| triviaqa-mirror-revision | `fd58143bcbfe06d8d63b4caf0c1068c8865e3d936d5de6078dc41af34dbb3fe5` |
| triviaqa-mirror-tree | `8d14e07783c5dcf3ac5c8fd30a3a480f0e167bed0b77cbb819d1530b41bffc54` |
| triviaqa-selected-tree | `40b807247f15bb2f5522bc69d0c4c4a031f30eb23f2632a8526bfb53f8df1ce2` |
| triviaqa-mirror-commits | `0f1c890e59a5e2e69f8c46efe68eeefdf766a081a067bbd6339cf1b772c00396` |
| triviaqa-conversion-discussion | `05e099be1b56ef18dc1e022459536cd44114f93cd1e2bf7df5b666d6b19126db` |
| triviaqa-predecessor-tree | `992511505f49ef7de5bb405fe8c5ce529ca00ac139ffaf1a597b74e1ca58f53a` |
| triviaqa-predecessor-loader | `b80c2307a37cfb261b66b7c73157de5495ae18add3f91f5f7d62f86620edc137` |
| triviaqa-initial-tree | `450269716dfde3a4f30839f010e8c12c6bd832821ae58a67a5c2a667a116daf2` |
| triviaqa-predelete-tree | `1abf68dec2a986dd71ecf0ccfb969422de1ced2ef3ee5486a6bbb75e87ead583` |
| triviaqa-added-tree | `40b807247f15bb2f5522bc69d0c4c4a031f30eb23f2632a8526bfb53f8df1ce2` |
| triviaqa-input-tree | `53718ecab96ddc19f326194a90967b4c8f21987fcdceb38d60b6b0b59b1d67cb` |

Decoded checker helpers’ original-byte SHA-256 (distinct from the API response hash):

- `LICENSE`: `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`.
- `berkeley-function-call-leaderboard/bfcl_eval/constants/model_config.py`: `26bff7e39e1ea018c5fd5a55882a0020a98f63f76068ece29e68f4ff6e8c4cb1`.
- `berkeley-function-call-leaderboard/bfcl_eval/eval_checker/ast_eval/type_convertor/java_type_converter.py`: `2fd4f4b0443b3dd974a1723bb4e45c086d7b352631062da7807ad1ad40706604`.
- `berkeley-function-call-leaderboard/bfcl_eval/eval_checker/ast_eval/type_convertor/js_type_converter.py`: `a114e9ff75c025cb52787ac33d6c2fbaa390905c6125a2b3c6afebab232bb5e4`.
- `berkeley-function-call-leaderboard/bfcl_eval/model_handler/parser/java_parser.py`: `78aa38dcfae655b5e3a982d0aaadf72aad0bb64a62cc4db4d7b7aa2185e666f5`.
- `berkeley-function-call-leaderboard/bfcl_eval/model_handler/parser/js_parser.py`: `65eea903e538cc2afa5f37e15cccfc303462f750ca45556ee654f6722f4b1e52`.

The original TriviaQA scorer remains SHA-256 `51785a3bc2e02a8f1ebf9db3aa18834c6a5daa5089ee5d435c99e0babf4be682`; predecessor loader is `b80c2307a37cfb261b66b7c73157de5495ae18add3f91f5f7d62f86620edc137`. Original Apache license text reused from task 225 is `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`.

## Validation

`PYTHONDONTWRITEBYTECODE=1 python3 tools/check_dataset_blockers.py` returned
`valid=true`, 28 datasets, eight shared blockers, 11 historical records and
`production_authorized=false`.

The following focused command passed **99 tests**, with no skips (4.10 seconds):

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
  python3 -m pytest -q -p no:cacheprovider \
  tests/quality/test_external_provenance_b5.py \
  tests/quality/test_dataset_blockers.py \
  tests/quality/test_bfcl_ast_source_contract.py \
  tests/quality/test_triviaqa_source_provenance_codex196.py
```

Pytest used its default temporary directory outside the platform; no in-tree
`--basetemp` was supplied. The original scorer's existing focused tests execute
only fabricated inputs. No acquired BFCL or predecessor-loader code was run.
The existing BFCL contract tests confirm unapproved source-gate refusal.
Changed-code/tree controls cannot reproduce the pinned Git identities.

Final review compares the registry structurally with base `9066072`: only the
three owned blockers' `observed`, `next_action` and evidence additions may differ.
Other datasets, shared blockers, review metadata, historical records, production
adapters and prior fixtures remain unchanged. No whole-suite run.

Final documentation/inventory recheck: **6/6 acquisition tests pass** (0.15s).
The structural scope comparison passes: only the three owned blockers differ;
original source fixtures and all adapters match the base commit. Authored files
pass the staged whitespace check. The full check reports 20 whitespace notices
in unchanged original upstream source bytes, which are deliberately preserved
and Git-blob verified.

The bundle retains 100 request receipts: 63 HTTP 200 responses (including the
archive HEAD), 23 HTTP 403 responses, one mirror HTTP 404 and 13 transport
failures without response bodies. All 87 received bodies and all 100 receipts
have SHA-256 coverage.

Final inventory SHA-256:
`3270eb704cc6c92f18acf4b3d95f9ca121a98205de858c70dff55aa7ff01ecf4`.
Final SHA256SUMS-file SHA-256 (local integrity only):
`aebf74434643e759983e0483787d069d6562873492d4c3c618a47cd9269ea30b`.

No human custodian or independent reviewer has made the outstanding decisions.
No blocker is declared fully closed by this acquisition.
