# w-b5restore: verified public response restoration

FOUND: Restored and verified **12 of 87** initially missing B5 bodies: 11 replayed HTTP 200 responses and one deliberately empty HEAD body. The manifest now has 159 present entries and 75 absent entries; every present digest matches, and SHA256SUMS is unchanged. Evidence: `reports/w-b5restore-validation.txt:201`; per-body observations: `reports/w-b5restore-replay.jsonl:2` onward.

FOUND: The replay uses each body’s own receipt URL, method and request headers, disables redirects and proxy use, adds no credentials, sleeps two seconds between requests, sets a 15-second request timeout, and refuses bodies at the 999,999-byte cap. The recorded User-Agent is `HarnessGrad-public-provenance/1`. The HEAD body is written as zero bytes without a request. Policy and observed request fields: `reports/w-b5restore-replay.jsonl:1`, `reports/w-b5restore-replay.jsonl:2`, `reports/w-b5restore-replay.jsonl:3`; implementation: `tools/restore_external_provenance_b5_w_b5restore.py:51`.

FOUND: The fixture-body ignore rule requires explicitly adding the verified files; the rule was not edited. Evidence: `.gitignore:364`; exact `git check-ignore` output is in the validation transcript.

ABSENT: The 75 remaining entries are explicitly enumerated below. Scope is only the 234 entries in `tests/fixtures/external_provenance_b5/SHA256SUMS`, checked for on-disk existence by the exact verification command below. This is not a search of other worktrees, caches or git history. Evidence: `reports/w-b5restore-validation.txt:201`.

```sh
python3 tools/restore_external_provenance_b5_w_b5restore.py verify reports/w-b5restore-replay.jsonl
```

Exact observed output:

```json
{"manifest_entries": 234, "missing": 75, "present": 159, "present_digest_mismatches": [], "restored_verification_failures": [], "restored_verified": 12, "sha256sums_unchanged": true}
```

Restored bodies (paths are relative to `tests/fixtures/external_provenance_b5`; pinned SHA-256 and receipt hash are in the cited observation):

| Body | Bytes | Outcome | Evidence |
| --- | ---: | --- | --- |
| `responses/bfcl-archive-head.body` | 0 | deliberately empty HEAD; no fetch | `reports/w-b5restore-replay.jsonl:2` |
| `responses/triviaqa-added-tree.body` | 973 | HTTP 200; digest and length match | `reports/w-b5restore-replay.jsonl:74` |
| `responses/triviaqa-conversion-initial-commits.body` | 7052 | HTTP 200; digest and length match | `reports/w-b5restore-replay.jsonl:76` |
| `responses/triviaqa-initial-tree.body` | 483 | HTTP 200; digest and length match | `reports/w-b5restore-replay.jsonl:79` |
| `responses/triviaqa-input-tree.body` | 621 | HTTP 200; digest and length match | `reports/w-b5restore-replay.jsonl:80` |
| `responses/triviaqa-mirror-commits.body` | 7888 | HTTP 200; digest and length match | `reports/w-b5restore-replay.jsonl:81` |
| `responses/triviaqa-mirror-revision.body` | 25259 | HTTP 200; digest and length match | `reports/w-b5restore-replay.jsonl:83` |
| `responses/triviaqa-mirror-tree.body` | 1011 | HTTP 200; digest and length match | `reports/w-b5restore-replay.jsonl:84` |
| `responses/triviaqa-predecessor-loader.body` | 13317 | HTTP 200; digest and length match | `reports/w-b5restore-replay.jsonl:85` |
| `responses/triviaqa-predecessor-tree.body` | 392 | HTTP 200; digest and length match | `reports/w-b5restore-replay.jsonl:86` |
| `responses/triviaqa-predelete-tree.body` | 1204 | HTTP 200; digest and length match | `reports/w-b5restore-replay.jsonl:87` |
| `responses/triviaqa-selected-tree.body` | 973 | HTTP 200; digest and length match | `reports/w-b5restore-replay.jsonl:88` |

Residue: 70 HTTP 403 responses with `X-RateLimit-Remaining: 0`, one transport timeout, one HTTP 404, and three HTTP 200 digest mismatches. Each row names the remaining gap and cites the exact receipt-backed replay observation. No rejected body was written. The HTTP 404 body happens to match its historical pin but remains absent under the explicit non-200 rule. Evidence: the following complete table; HTTP 404: `reports/w-b5restore-replay.jsonl:82`.

| Missing body | Reason | Evidence |
| --- | --- | --- |
| `responses/bfcl-blob-base_oss_handler.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:3` |
| `responses/bfcl-blob-category_mapping.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:4` |
| `responses/bfcl-blob-column_headers.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:5` |
| `responses/bfcl-blob-default_prompts.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:6` |
| `responses/bfcl-blob-eval_config.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:7` |
| `responses/bfcl-blob-java_parser.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:8` |
| `responses/bfcl-blob-java_type_converter.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:9` |
| `responses/bfcl-blob-js_parser.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:10` |
| `responses/bfcl-blob-js_type_converter.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:11` |
| `responses/bfcl-blob-model_config.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:12` |
| `responses/bfcl-blob-model_style.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:13` |
| `responses/bfcl-blob-multi_turn_checker.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:14` |
| `responses/bfcl-blob-multi_turn_utils.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:15` |
| `responses/bfcl-blob-qwen.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:16` |
| `responses/bfcl-blob-utils.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:17` |
| `responses/bfcl-commit.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:18` |
| `responses/bfcl-handler-api_inference-claude.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:19` |
| `responses/bfcl-handler-api_inference-cohere.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:20` |
| `responses/bfcl-handler-api_inference-databricks.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:21` |
| `responses/bfcl-handler-api_inference-deepseek.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:22` |
| `responses/bfcl-handler-api_inference-dm_cito.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:23` |
| `responses/bfcl-handler-api_inference-fireworks.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:24` |
| `responses/bfcl-handler-api_inference-functionary.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:25` |
| `responses/bfcl-handler-api_inference-gemini.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:26` |
| `responses/bfcl-handler-api_inference-gogoagent.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:27` |
| `responses/bfcl-handler-api_inference-gorilla.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:28` |
| `responses/bfcl-handler-api_inference-grok.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:29` |
| `responses/bfcl-handler-api_inference-ling.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:30` |
| `responses/bfcl-handler-api_inference-mining.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:31` |
| `responses/bfcl-handler-api_inference-mistral.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:32` |
| `responses/bfcl-handler-api_inference-nemotron.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:33` |
| `responses/bfcl-handler-api_inference-nexus.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:34` |
| `responses/bfcl-handler-api_inference-nova.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:35` |
| `responses/bfcl-handler-api_inference-novita.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:36` |
| `responses/bfcl-handler-api_inference-nvidia.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:37` |
| `responses/bfcl-handler-api_inference-openai_completion.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:38` |
| `responses/bfcl-handler-api_inference-openai_response.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:39` |
| `responses/bfcl-handler-api_inference-qwen.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:40` |
| `responses/bfcl-handler-api_inference-writer.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:41` |
| `responses/bfcl-handler-api_inference-yi.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:42` |
| `responses/bfcl-handler-local_inference-arch.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:43` |
| `responses/bfcl-handler-local_inference-bielik.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:44` |
| `responses/bfcl-handler-local_inference-bitagent.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:45` |
| `responses/bfcl-handler-local_inference-deepseek.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:46` |
| `responses/bfcl-handler-local_inference-deepseek_coder.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:47` |
| `responses/bfcl-handler-local_inference-deepseek_reasoning.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:48` |
| `responses/bfcl-handler-local_inference-falcon_fc.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:49` |
| `responses/bfcl-handler-local_inference-gemma.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:50` |
| `responses/bfcl-handler-local_inference-glaive.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:51` |
| `responses/bfcl-handler-local_inference-glm.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:52` |
| `responses/bfcl-handler-local_inference-granite.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:53` |
| `responses/bfcl-handler-local_inference-granite_3.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:54` |
| `responses/bfcl-handler-local_inference-hammer.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:55` |
| `responses/bfcl-handler-local_inference-hermes.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:56` |
| `responses/bfcl-handler-local_inference-llama.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:57` |
| `responses/bfcl-handler-local_inference-llama_3_1.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:58` |
| `responses/bfcl-handler-local_inference-minicpm.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:59` |
| `responses/bfcl-handler-local_inference-minicpm_fc.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:60` |
| `responses/bfcl-handler-local_inference-mistral_fc.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:61` |
| `responses/bfcl-handler-local_inference-phi.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:62` |
| `responses/bfcl-handler-local_inference-phi_fc.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:63` |
| `responses/bfcl-handler-local_inference-quick_testing_oss.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:64` |
| `responses/bfcl-handler-local_inference-qwen_fc.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:65` |
| `responses/bfcl-handler-local_inference-salesforce_llama.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:66` |
| `responses/bfcl-handler-local_inference-salesforce_qwen.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:67` |
| `responses/bfcl-handler-local_inference-think_agent.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:68` |
| `responses/bfcl-release.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:69` |
| `responses/bfcl-root-tree.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:70` |
| `responses/bfcl-tag.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:71` |
| `responses/bfcl-tree.body` | fetch failure; HTTP 403; rate-limit remaining 0 | `reports/w-b5restore-replay.jsonl:72` |
| `responses/bfcl-web-bitagent.body` | fetch failure; TimeoutError: The read operation timed out | `reports/w-b5restore-replay.jsonl:73` |
| `responses/triviaqa-conversion-discussion.body` | digest mismatch; HTTP 200; 13106 bytes | `reports/w-b5restore-replay.jsonl:75` |
| `responses/triviaqa-dns-alidns.body` | digest mismatch; HTTP 200; 192 bytes | `reports/w-b5restore-replay.jsonl:77` |
| `responses/triviaqa-dns-dohpub.body` | digest mismatch; HTTP 200; 391 bytes | `reports/w-b5restore-replay.jsonl:78` |
| `responses/triviaqa-mirror-loader.body` | fetch failure; HTTP 404; 15 bytes | `reports/w-b5restore-replay.jsonl:82` |

Exact mismatches (all rejected; no bytes saved):

| Label | Pinned SHA-256 | Observed SHA-256 | Bytes | Status | Evidence |
| --- | --- | --- | ---: | ---: | --- |
| `triviaqa-conversion-discussion` | `05e099be1b56ef18dc1e022459536cd44114f93cd1e2bf7df5b666d6b19126db` | `7254bad8c17b9570d1556b16c8de84d8a1cee1b2c0a6d446f22ca5e05a35d8a8` | 13106 | 200 | `reports/w-b5restore-replay.jsonl:75` |
| `triviaqa-dns-alidns` | `6e2ad4e2be0c13a8a25663fb7d316276207a7f59ea59e6a0ead7b6ac8d364628` | `9f046e4efd476e4304118a5ae602c50e513500115b6e770679b994a0f7c359c6` | 192 | 200 | `reports/w-b5restore-replay.jsonl:77` |
| `triviaqa-dns-dohpub` | `4096d066d405a32f3422cadafd7ceaefbb33e62a0fcf77316d236e581ae908c4` | `166022710e6562f7e1a2c6c0ff134bf581f1696c739b7b0a6725ed66a2caa311` | 391 | 200 | `reports/w-b5restore-replay.jsonl:78` |

FOUND: The baseline combined test run was **6 failed, 74 passed** (`reports/w-b5restore-validation.txt:190`); after restoration it was **5 failed, 75 passed** (`reports/w-b5restore-validation.txt:372`). B5 therefore changed from 6 failed / 0 passed to 5 failed / 1 passed; `test_dataset_blockers.py` remains 74 passed / 0 failed. Both exact commands and full failure traces are retained in the validation transcript.

The five remaining B5 failures are FileNotFoundError at the following missing input; no assertion was changed. Evidence: `reports/w-b5restore-validation.txt:372` and its preceding failure traces.

| Test | First missing input after restoration | Recorded replay reason |
| --- | --- | --- |
| `test_inventory_and_every_raw_response_are_intact` | `responses/bfcl-blob-base_oss_handler.body` | HTTP 403 rate limit |
| `test_bfcl_tag_signed_commit_and_all_original_git_trees` | `responses/bfcl-tag.body` | HTTP 403 rate limit |
| `test_bfcl_projection_matches_tree_and_retained_blob_bodies` | `responses/bfcl-tree.body` | HTTP 403 rate limit |
| `test_changed_tree_and_code_cannot_reproduce_original_identities` | `responses/bfcl-root-tree.body` | HTTP 403 rate limit |
| `test_triviaqa_predecessor_and_conversion_history_do_not_self_attest_execution` | `responses/triviaqa-conversion-discussion.body` | HTTP 200 digest mismatch |

FOUND: `python3 tools/check_dataset_blockers.py` returned `{"valid": true, "datasets": 28, "shared_blockers": 0, "historical_records": 11, "production_authorized": false}`. Evidence: `reports/w-b5restore-validation.txt:196`. No registry proposal is warranted by response-body restoration.

Secondary scope was report-only. Counts below distinguish manifest-covered present files from the extra SHA256SUMS file; the initial audit command enumerated exactly the named packet directories and their SHA256SUMS entries. Evidence: `reports/w-b5restore-audit.json:1`; exact audit source/output is retained in the validation transcript.

| Packet | Manifest entries | Present in manifest | Present including SHA256SUMS / tracked | Missing bodies | With matching receipt | Method |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `e3_bfcl_source` | 87 | 63 | 64 / 64 | 24 | 24 | 24 GET |
| `upstream_provenance_e2` | 47 | 32 | 33 / 33 | 15 | 15 | 8 GET, 7 HEAD |

FOUND: For E3, all 24 missing `.body` entries have sibling `responses/<stem>.json` receipts with request headers and matching manifest digests; receipt-driven GET replay and strict verification apply. For E2, all 15 missing `.body` entries map to their directory’s `receipt.json` hop array and agree with its digest; seven HEAD entries pin zero bytes. The same method-aware digest discipline applies, but its receipts do not embed request headers, its acquire.py supplies headers, it records redirect hops, and it names a historical proxy. No E2 proxy was used here and no E2 or E3 body was restored. Evidence: `reports/w-b5restore-audit.json:1` (complete missing-entry enumeration with receipt mappings and header-presence flags); `tests/fixtures/upstream_provenance_e2/acquire.py:60`, `tests/fixtures/upstream_provenance_e2/acquire.py:72`, `tests/fixtures/upstream_provenance_e2/acquire.py:98`.

UNKNOWN: Whether the pinned GitHub API responses will be obtainable byte-for-byte after the shared unauthenticated rate limit resets is the main uncertainty for review. This replay observed only HTTP 403 on those 70 API requests; it did not retry after reset. Whether the three mismatches can ever reproduce their historical bytes is also unknown. Their current bytes were hashed and discarded. Evidence: `reports/w-b5restore-replay.jsonl:3` onward and the mismatch table above.

The validation transcript lists the deliberately unverified scope, exact focused commands/outputs, frozen-input checks, cleanup and byte sizes of every committed file. No independent origin/custody approval follows from digest restoration; the packet itself limits its pin to local integrity (`tests/fixtures/external_provenance_b5/README.md:9`).
