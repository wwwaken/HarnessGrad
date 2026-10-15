# The other five partially tracked packets: measured residue

**FOUND:** 79 unique absent paths: 62 `restorable`, 11 `empty_body_legitimate`, 2 `recorded_404`, 3 `no_receipt_no_url`, and 1 `unknown`; 239 present pins verify and 4 present pins mismatch. Per-packet measured commands/output: `registry/w-provresidue-validation.txt:9`, `registry/w-provresidue-validation.txt:10`, `registry/w-provresidue-validation.txt:11`, `registry/w-provresidue-validation.txt:12`, `registry/w-provresidue-validation.txt:13`. No `pinned_error_payload` is proved in this population.

## Scope and interpretation

E3 and E2 were read from the assigned worktree at base `0365c9ab`. The three ignored hg_* packets contain only tracked README/inventory files in this worktree (command J, `registry/w-provresidue-validation.txt:502`). Their manifests/receipts/present bytes were therefore read **strictly read-only** from `/mnt/20t/xubuqiang/Study/HarnessGrad/tests/fixtures/{hg_wprov,hg_trivia,hg_bfcl}/`; no main-checkout file was changed. Commands A/K and the 89 verbatim metadata snapshots in validation retain the observed input evidence. All short original fixture citations below resolve against that stated source; portable citations point into the committed validation file.

**FOUND** means observed from these inputs. **ABSENT** means not a regular file at a path pinned by the seven enumerated SHA256SUMS files, using A's explicit resolver and `is_file()` check. **UNKNOWN** means the offline evidence does not decide it. No absence claim extends to other checkouts, installed roots or external stores. `restorable` uses the requested criterion (recorded HTTP 200 + URL + body digest matching the pin); it is **not** a measured promise that a new fetch reproduces identical bytes. No endpoint is classified as live/dynamic. A body's historical status/digest agreement does not authenticate its content or establish a production gate.

**Counting corrections:** all supplied pin/absent counts reproduce, but hg_wprov root already covers both nested manifests: 114 unique pins and 22 unique absences, not 200 and 43. A observes 24 E3 receipt files (`responses/*.json`) and 12 E2 receipt files (arrays containing 15 response hops and one refusal without a response), not zero. hg_wprov has 19 HTTP receipt files total; its 11 ReWOO + 8 Reasoning Gym are the same nested 19, not an additional population. See A outputs above and the schema-specific parser embedded at `registry/w-provresidue-validation.txt:6`.

Computed, rather than assumed, empty digests (command B, `registry/w-provresidue-validation.txt:87`): zero bytes `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`; `[]` `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`; `{}` `44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a`. No absent `{}` pin occurs in this population. Documented failure sentinels count as legitimate **empty historical evidence files**, never as successful upstream artifacts.

Each absent entry has exactly one class in the table below and in the JSON array. Paths in each packet table are relative to its named directory; full repo-relative paths, full pins, URLs, byte counts and receipt locators are in `registry/w-provresidue-disposition.json`. Each table citation is a committed snapshot of the deciding receipt; A independently establishes absence and pin equality.

## tests/fixtures/e3_bfcl_source

**FOUND:** 87 pins; 63 present and verified; 24 absent; no mismatch. All 24 receipts record status 200; all 24 body pins equal `response_body.sha256` (`registry/w-provresidue-validation.txt:9`). All 24 absent raw API envelopes are `restorable`; the 283-byte first envelope contains a decoded empty initializer but is itself **not empty** (receipt snapshot `registry/w-provresidue-validation.txt:845`).

| Absent path | Exactly one class | Recorded status / bytes | Deciding evidence |
| --- | --- | --- | --- |
| `responses/01-e69de29bb2d1d6434b8b29ae775ad8c2e48c5391.body` | `restorable` | 200 / 283 | `registry/w-provresidue-validation.txt:845` |
| `responses/02-67b896665bbc80c5f304f971134203ea6f7c3d16.body` | `restorable` | 200 / 6628 | `registry/w-provresidue-validation.txt:975` |
| `responses/03-b425bfe87a99c48dcb8aefc3d6262b26013b78df.body` | `restorable` | 200 / 16023 | `registry/w-provresidue-validation.txt:1105` |
| `responses/04-62994859a90cccd00ac07fa2888d8d138bbdbc17.body` | `restorable` | 200 / 14325 | `registry/w-provresidue-validation.txt:1235` |
| `responses/05-d9b15517a89f223bfdd721f7c069dede1d14bf7b.body` | `restorable` | 200 / 5066 | `registry/w-provresidue-validation.txt:1365` |
| `responses/06-3b5c3985525c4e433be52abbff5e1a16c61dd73a.body` | `restorable` | 200 / 5532 | `registry/w-provresidue-validation.txt:1495` |
| `responses/07-a27ad97a4d2c43dd9d55650e551a465570e24873.body` | `restorable` | 200 / 2222 | `registry/w-provresidue-validation.txt:1625` |
| `responses/08-dd81ed0ea398d36195afe9350c12290db70c05b6.body` | `restorable` | 200 / 7726 | `registry/w-provresidue-validation.txt:1755` |
| `responses/09-9bbbc1e122bac761a7ec62864aa50840b44782da.body` | `restorable` | 200 / 6466 | `registry/w-provresidue-validation.txt:1885` |
| `responses/10-2b303b50877122bcc508fe6eef30d7dcc40eac39.body` | `restorable` | 200 / 19041 | `registry/w-provresidue-validation.txt:2015` |
| `responses/11-fee6ab74def4523a97a9615c3350df53acdf9d8b.body` | `restorable` | 200 / 12624 | `registry/w-provresidue-validation.txt:2145` |
| `responses/12-2eb06b52459b21a59482ea7ced7195a2e6664a4b.body` | `restorable` | 200 / 7338 | `registry/w-provresidue-validation.txt:2275` |
| `responses/13-59c28c8a1567d4b08e607a359457500930d617a3.body` | `restorable` | 200 / 3706 | `registry/w-provresidue-validation.txt:2405` |
| `responses/14-9df2e225fb7bf3722a4cb14a94a72c9ce0a5016c.body` | `restorable` | 200 / 16035 | `registry/w-provresidue-validation.txt:2535` |
| `responses/15-861c852b11f7b8072c711d802bea2effef623db2.body` | `restorable` | 200 / 1463 | `registry/w-provresidue-validation.txt:2665` |
| `responses/16-d52b9207277b5d71d789612a316b8ff225164f32.body` | `restorable` | 200 / 28551 | `registry/w-provresidue-validation.txt:2795` |
| `responses/17-cc925980980bdc886756738337793b9ea7aab7ba.body` | `restorable` | 200 / 17755 | `registry/w-provresidue-validation.txt:2925` |
| `responses/18-71492c91d8a2c7bb2443e29cf48763bbbcc98b2a.body` | `restorable` | 200 / 3718 | `registry/w-provresidue-validation.txt:3055` |
| `responses/19-b52e05461cf54232e6b2a42e41b45ecd146507f6.body` | `restorable` | 200 / 13824 | `registry/w-provresidue-validation.txt:3185` |
| `responses/20-a1e7c45fc425121ca799d0b1a290c0d8990e8397.body` | `restorable` | 200 / 1551 | `registry/w-provresidue-validation.txt:3315` |
| `responses/21-66191d78a27a8917f3fde1095781375668866f34.body` | `restorable` | 200 / 17723 | `registry/w-provresidue-validation.txt:3445` |
| `responses/22-ddd3396f9e9272df84189d63b95c074e625cf195.body` | `restorable` | 200 / 7164 | `registry/w-provresidue-validation.txt:3575` |
| `responses/23-8850b4b6e2d5d481cf58e0c7baf4fedccf928c3d.body` | `restorable` | 200 / 7090 | `registry/w-provresidue-validation.txt:3705` |
| `responses/24-5904e3fdcfc70998c7d2cd35162e5b021528557f.body` | `restorable` | 200 / 10980 | `registry/w-provresidue-validation.txt:3835` |

**Test impact:** `tests/quality/test_dataset_blockers.py` reads only registry-selected metadata through its checker (`:19`, `:57-58`; `tools/check_dataset_blockers.py:118-119`). Missing bodies have **no effect** on those reads. The registry selects E3 inventory (`registry/dataset-blockers.json:171`), Trivia README (`:731`), or BFCL README/inventory (`:181`, `:186`) as appropriate. Missing selected hg_* metadata can explicitly skip whole-registry tests (`tests/quality/conftest.py:39-45`); this is not a body skip.

`tests/fixtures/e3_bfcl_source/verify.py:38` reads response bodies unguarded (would raise `FileNotFoundError`); it can first fail on inherited evidence at `:26`. It writes `static-audit.json` at `:113` and was not executed. `tests/fixtures/hg_bfclrt/collect.py:111` reads E3 inventory, then source modules at `:113-126`; it does not consume E3 response bodies.

## tests/fixtures/hg_wprov

**FOUND:** root 114 pins = 90 present verified + 2 present mismatches + 22 absent. Nested ReWOO 36 = 25 verified + 11 absent; nested Reasoning Gym 50 = 40 verified + 10 absent; these are overlapping subsets of the root. All 19 HTTP body pins agree with their receipts' normalized digest field (`sha256` or `body_sha256`). Statuses: 15 × 200, 2 × 404, 2 explicit null transport failures (`registry/w-provresidue-validation.txt:10`). The three additional missing local artifacts have local observation receipts but no recorded HTTP URL; that is what the requested `no_receipt_no_url` class denotes here.

| Absent path | Exactly one class | Recorded status / bytes | Deciding evidence |
| --- | --- | --- | --- |
| `installed/reasoning_gym.jsonl` | `no_receipt_no_url` | null / 3315981 | `registry/w-provresidue-validation.txt:4655` |
| `reasoning_gym/attempt-4-scratch-file.body` | `no_receipt_no_url` | null / 190 | `registry/w-provresidue-validation.txt:4787` |
| `reasoning_gym/installed-RECORD.body` | `no_receipt_no_url` | null / 33561 | `registry/w-provresidue-validation.txt:4807` |
| `reasoning_gym/responses/github-commit.body` | `restorable` | 200 / 2551 | `registry/w-provresidue-validation.txt:4822` |
| `reasoning_gym/responses/github-tag.body` | `restorable` | 200 / 357 | `registry/w-provresidue-validation.txt:4832` |
| `reasoning_gym/responses/github-tree.body` | `restorable` | 200 / 130180 | `registry/w-provresidue-validation.txt:4842` |
| `reasoning_gym/responses/pypi-0.1.25.body` | `restorable` | 200 / 12264 | `registry/w-provresidue-validation.txt:4852` |
| `reasoning_gym/responses/pypi-bdist_wheel-provenance.body` | `recorded_404` | 404 / 79 | `registry/w-provresidue-validation.txt:4862` |
| `reasoning_gym/responses/pypi-bdist_wheel.body` | `restorable` | 200 / 6985897 | `registry/w-provresidue-validation.txt:4872` |
| `reasoning_gym/responses/pypi-sdist-provenance.body` | `recorded_404` | 404 / 69 | `registry/w-provresidue-validation.txt:4882` |
| `reasoning_gym/responses/pypi-sdist.body` | `restorable` | 200 / 6789585 | `registry/w-provresidue-validation.txt:4892` |
| `rewoo/bigbench-sports-api.body` | `restorable` | 200 / 272314 | `registry/w-provresidue-validation.txt:4982` |
| `rewoo/bigbench-sports-raw-proxy.body` | `restorable` | 200 / 196765 | `registry/w-provresidue-validation.txt:5024` |
| `rewoo/bigbench-sports-raw.body` | `empty_body_legitimate` | null / 0 | `registry/w-provresidue-validation.txt:5037` |
| `rewoo/bigbench-tree.body` | `restorable` | 200 / 8257988 | `registry/w-provresidue-validation.txt:5080` |
| `rewoo/rewoo-evaluator-api.body` | `restorable` | 200 / 12800 | `registry/w-provresidue-validation.txt:5123` |
| `rewoo/rewoo-evaluator-raw-proxy.body` | `restorable` | 200 / 8584 | `registry/w-provresidue-validation.txt:5165` |
| `rewoo/rewoo-evaluator-raw.body` | `empty_body_legitimate` | null / 0 | `registry/w-provresidue-validation.txt:5178` |
| `rewoo/rewoo-physics-api.body` | `restorable` | 200 / 25813 | `registry/w-provresidue-validation.txt:5221` |
| `rewoo/rewoo-sports-api.body` | `restorable` | 200 / 191028 | `registry/w-provresidue-validation.txt:5264` |
| `rewoo/rewoo-strategy-api.body` | `restorable` | 200 / 277223 | `registry/w-provresidue-validation.txt:5307` |
| `rewoo/rewoo-tree.body` | `restorable` | 200 / 21179 | `registry/w-provresidue-validation.txt:5350` |

**FOUND present-but-mismatched:** `tests/fixtures/hg_wprov/check_registry_scope.py`; pin `0ae2aa5f327f77ea82150e8b0f0a0ac6c49a906860ace6d764cb09e140e2c569`; recomputed `49116ca38d26c6c3102cdd78e173afb62c94104589645f93511b5cb1440bd9a9`. Source pin `tests/fixtures/hg_wprov/SHA256SUMS:3`; exact observed comparison `registry/w-provresidue-validation.txt:10`. Fetching absent bodies cannot correct these local bytes.

**FOUND present-but-mismatched:** `tests/fixtures/hg_wprov/verify.py`; pin `96601c8edfc34f67e65b0a7fb2e0cd2ebcf4430279d9a58ec09e844598fec7aa`; recomputed `dd0b5be4e38c40b016b9ec33e89300478157035833cb6e179ea5cc7a3cea237d`. Source pin `tests/fixtures/hg_wprov/SHA256SUMS:114`; exact observed comparison `registry/w-provresidue-validation.txt:10`. Fetching absent bodies cannot correct these local bytes.

**Empty cohort (2):** `rewoo/bigbench-sports-raw.body` and `rewoo/rewoo-evaluator-raw.body` both pin `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, zero bytes. Their receipts explicitly label `body_kind: "transport-failure-sentinel"`, with null status and a connection-reset error. The packet explains this at `rewoo/README.md:72` (portable `registry/w-provresidue-validation.txt:4897`). Recreate only a historical empty sentinel if authorized later; a successful GET would be different evidence. These are not a shared upstream error payload.

**Recorded 404s (2), with recorded URLs quoted verbatim:**

- `reasoning_gym/responses/pypi-bdist_wheel-provenance.body`: `https://pypi.org/integrity/reasoning-gym/0.1.25/reasoning_gym-0.1.25-py3-none-any.whl/provenance`; 79 bytes; pin `6af0383a2e6d6f0c6cc880004c73cea2c771299b4c49801f5c33d0ddf46139b4`; `registry/w-provresidue-validation.txt:4862`.
- `reasoning_gym/responses/pypi-sdist-provenance.body`: `https://pypi.org/integrity/reasoning-gym/0.1.25/reasoning_gym-0.1.25.tar.gz/provenance`; 69 bytes; pin `0a4885f2e0580b4d9ba42944297a0c064be0c3a1a0cb363ff7b7943f4c700c11`; `registry/w-provresidue-validation.txt:4882`.

**ABSENT replay URL for three named local artifacts, within the enumerated packet only:** command F-scope lists all 93 existing files (`registry/w-provresidue-validation.txt:116`); F-search scans this entire packet, ignoring ignore rules, for the three paths and their recorded aliases (`registry/w-provresidue-validation.txt:214`). Exact command and all matching lines are retained there. Matching README, manifest, JSON and script references identify local source paths and hashes; none associates a replay URL with these files. This is not a claim that no local copy exists elsewhere.

- `installed/reasoning_gym.jsonl`: local receipt records `/mnt/20t/xubuqiang/datasets/reasoning_gym/pool.jsonl`, 3,315,981 bytes (`registry/w-provresidue-validation.txt:4655`). No public pool URL is authenticated; the packet records regeneration did not reproduce it (`registry/w-provresidue-validation.txt:4711`). A matching preserved local copy would settle recoverability; that source was not opened here.
- `reasoning_gym/installed-RECORD.body`: local `installed-members.json` records 33,561 installed bytes and a different 20,047-byte wheel RECORD (`registry/w-provresidue-validation.txt:4807`). Fetching the wheel cannot supply this pinned rewritten RECORD. A hash-matching installed/captured copy would settle local recovery; not searched outside the packet.
- `reasoning_gym/attempt-4-scratch-file.body`: cleanup recovery records the local 190-byte CSV and `cleanup_complete: true` (`registry/w-provresidue-validation.txt:4787`). Its scratch path is a historical string, not a checked current location. No replay URL is recorded; a preserved hash-matching copy would settle recovery.

**Test impact:** no direct suite reader and no registry-mediated reader of this packet was found in the named searches below. Missing bodies have **no observed suite path to fail or skip** in that static scope.

The standalone root helper (`tests/fixtures/hg_wprov/verify.py:14-19`) asserts containment/no-symlink at `:18`, then reads bytes at `:19`: an absent regular path would raise `FileNotFoundError` if reached; an earlier present mismatch can raise `AssertionError` first. ReWOO helper `rewoo/verify.py:116-118` and Reasoning Gym helper `reasoning_gym/verify.py:34-36` use unguarded body reads (would raise `FileNotFoundError` if reached). These are fixture utilities, not discovered suite tests, and were not run.

## tests/fixtures/upstream_provenance_e2

**FOUND:** 47 pins = 31 verified + 1 present mismatch + 15 absent. All 15 body pins agree with the corresponding receipt hop's `sha256` (this schema has no `response_body` wrapper). Twelve receipt files record 16 operations: 11 × 200, 3 × 302, 1 × 307; one allowlist refusal has no status/body digest and no pinned body. Nine legitimate empties are seven HEAD bodies and two empty API lists (`registry/w-provresidue-validation.txt:11`).

| Absent path | Exactly one class | Recorded status / bytes | Deciding evidence |
| --- | --- | --- | --- |
| `lcb-pinned-card/hop-0.body` | `unknown` | 307 / 317 | `registry/w-provresidue-validation.txt:5422` |
| `lcb-pinned-card/hop-1.body` | `restorable` | 200 / 3390 | `registry/w-provresidue-validation.txt:5436` |
| `lcb-pinned-history/hop-0.body` | `restorable` | 200 / 4605 | `registry/w-provresidue-validation.txt:5453` |
| `lcb-refs/hop-0.body` | `restorable` | 200 / 136 | `registry/w-provresidue-validation.txt:5470` |
| `twowiki-later-archive-head/hop-0.body` | `empty_body_legitimate` | 302 / 0 | `registry/w-provresidue-validation.txt:5487` |
| `twowiki-later-archive-head/hop-1.body` | `empty_body_legitimate` | 200 / 0 | `registry/w-provresidue-validation.txt:5501` |
| `twowiki-later-download-followup-head/hop-0.body` | `empty_body_legitimate` | 200 / 0 | `registry/w-provresidue-validation.txt:5518` |
| `twowiki-later-download-head/hop-0.body` | `empty_body_legitimate` | 302 / 0 | `registry/w-provresidue-validation.txt:5535` |
| `twowiki-later-download-head/hop-1.body` | `empty_body_legitimate` | 302 / 0 | `registry/w-provresidue-validation.txt:5549` |
| `twowiki-license-issues/hop-0.body` | `restorable` | 200 / 79 | `registry/w-provresidue-validation.txt:5575` |
| `twowiki-original-archive-head/hop-0.body` | `empty_body_legitimate` | 200 / 0 | `registry/w-provresidue-validation.txt:5592` |
| `twowiki-original-download-head/hop-0.body` | `empty_body_legitimate` | 200 / 0 | `registry/w-provresidue-validation.txt:5609` |
| `twowiki-pinned-history/hop-0.body` | `restorable` | 200 / 570 | `registry/w-provresidue-validation.txt:5626` |
| `twowiki-releases/hop-0.body` | `empty_body_legitimate` | 200 / 2 | `registry/w-provresidue-validation.txt:5643` |
| `twowiki-tags/hop-0.body` | `empty_body_legitimate` | 200 / 2 | `registry/w-provresidue-validation.txt:5660` |

**FOUND present-but-mismatched:** `tests/fixtures/upstream_provenance_e2/verify.py`; pin `eda7f157198816f72ffc4326a3ca7ea8e3c8a606de83ce03e003171ff3473e73`; recomputed `3d52940b038ddea45b5882952d9e4573b44e9b34b911dc4f13b675a73372d18e`. Source pin `tests/fixtures/upstream_provenance_e2/SHA256SUMS:47`; exact observed comparison `registry/w-provresidue-validation.txt:11`. Fetching absent bodies cannot correct these local bytes.

**Empty cohorts:** the seven table entries with digest `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` are explicitly HEAD/zero-byte observations (packet explanation `registry/w-provresidue-validation.txt:5369`). `twowiki-releases/hop-0.body` and `twowiki-tags/hop-0.body` both pin `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`, two bytes, status 200; the offline verifier explicitly expects `[]` for these two APIs (`registry/w-provresidue-validation.txt:5692`). Sharing these legitimate empty digests is expected.

**UNKNOWN, not a proved hole:** `lcb-pinned-card/hop-0.body` records status 307 and 317 bytes, with a matching pin; the following hop records status 200 and a different body (`registry/w-provresidue-validation.txt:5422`, `registry/w-provresidue-validation.txt:5436`). A no-follow replay returning exactly the pinned 317 bytes would settle byte recoverability. No such fetch occurred here; no dynamic-resource claim is made.

**Measured mismatch provenance:** command H shows the earlier verifier and the exact two registry-path replacements between `21a7d7f3` and `0365c9ab` (`registry/w-provresidue-validation.txt:272`, `registry/w-provresidue-validation.txt:476`). Command N (`registry/w-provresidue-validation.txt:5711`) computes that earlier Git object's SHA-256 as `eda7f157198816f72ffc4326a3ca7ea8e3c8a606de83ce03e003171ff3473e73`. This explains the stale local helper pin without silently rewriting historical evidence.

**Test impact:** no direct suite reader and no registry-mediated reader of this packet was found in the named searches below. Missing bodies have **no observed suite path to fail or skip** in that static scope.

The standalone `tests/fixtures/upstream_provenance_e2/verify.py:65-67` reads recorded bodies unguarded (would raise `FileNotFoundError` if reached); it first checks inherited inputs at `:54-56`. It was not run.

## tests/fixtures/hg_trivia

**FOUND:** 53 pins = 40 present verified + 13 absent; no mismatch. All 13 receipts record 200 and each body pin equals its `sha256`; body size is recorded as `size_bytes` (`registry/w-provresidue-validation.txt:12`). All 13 absences qualify as `restorable`.

| Absent path | Exactly one class | Recorded status / bytes | Deciding evidence |
| --- | --- | --- | --- |
| `responses/hub-added-selected-tree.body` | `restorable` | 200 / 973 | `registry/w-provresidue-validation.txt:4177` |
| `responses/hub-commits.body` | `restorable` | 200 / 7888 | `registry/w-provresidue-validation.txt:4198` |
| `responses/hub-discussion-8.body` | `restorable` | 200 / 13106 | `registry/w-provresidue-validation.txt:4219` |
| `responses/hub-initial-commits.body` | `restorable` | 200 / 7052 | `registry/w-provresidue-validation.txt:4240` |
| `responses/hub-input-tree.body` | `restorable` | 200 / 621 | `registry/w-provresidue-validation.txt:4261` |
| `responses/hub-predecessor-loader.body` | `restorable` | 200 / 13317 | `registry/w-provresidue-validation.txt:4282` |
| `responses/hub-predecessor-tree.body` | `restorable` | 200 / 392 | `registry/w-provresidue-validation.txt:4303` |
| `responses/hub-recursive-tree.body` | `restorable` | 200 / 46138 | `registry/w-provresidue-validation.txt:4324` |
| `responses/hub-revision.body` | `restorable` | 200 / 25259 | `registry/w-provresidue-validation.txt:4345` |
| `responses/hub-root-tree.body` | `restorable` | 200 / 1011 | `registry/w-provresidue-validation.txt:4366` |
| `responses/hub-selected-tree.body` | `restorable` | 200 / 973 | `registry/w-provresidue-validation.txt:4387` |
| `responses/upstream-license.body` | `restorable` | 200 / 11340 | `registry/w-provresidue-validation.txt:4408` |
| `responses/upstream-scorer.body` | `restorable` | 200 / 5710 | `registry/w-provresidue-validation.txt:4429` |

**Shared-digest counterexample:** `responses/hub-added-selected-tree.body` and `responses/hub-selected-tree.body` share `40b807247f15bb2f5522bc69d0c4c4a031f30eb23f2632a8526bfb53f8df1ce2`, 973 bytes, two recorded 200s. The two retained views contain the same three file metadata objects (verbatim view snapshot `registry/w-provresidue-validation.txt:4476`); command G serializes each view with `ensure_ascii=False, separators=(',', ':')` and obtains **exactly 973 bytes and the pinned digest** for both (`registry/w-provresidue-validation.txt:259`). These two paths represent identical content at two revisions. The rule “two distinct paths share a digest, therefore error payload” has a concrete false positive here; both remain `restorable`. This proves no new upstream retrieval and no dataset-row content was read.

**Test impact:** `tests/quality/test_dataset_blockers.py` reads only registry-selected metadata through its checker (`:19`, `:57-58`; `tools/check_dataset_blockers.py:118-119`). Missing bodies have **no effect** on those reads. The registry selects E3 inventory (`registry/dataset-blockers.json:171`), Trivia README (`:731`), or BFCL README/inventory (`:181`, `:186`) as appropriate. Missing selected hg_* metadata can explicitly skip whole-registry tests (`tests/quality/conftest.py:39-45`); this is not a body skip.

The standalone `tests/fixtures/hg_trivia/verify.py:51-56` reads each recorded body unguarded (would raise `FileNotFoundError`); it was not run.

## tests/fixtures/hg_bfcl

**FOUND:** 21 pins = 15 present verified + 1 present mismatch + 5 absent. All five receipts record `http_status: "200"`; normalized integer status is 200. All five pins match `body.sha256` (`registry/w-provresidue-validation.txt:13`). All five absences qualify as `restorable`, including the recorded 44,552,456-byte archive. No archive body was opened or fetched.

| Absent path | Exactly one class | Recorded status / bytes | Deciding evidence |
| --- | --- | --- | --- |
| `responses/archive.body` | `restorable` | 200 / 44552456 | `registry/w-provresidue-validation.txt:3906` |
| `responses/commit.body` | `restorable` | 200 / 3047 | `registry/w-provresidue-validation.txt:3954` |
| `responses/license-blob.body` | `restorable` | 200 / 15937 | `registry/w-provresidue-validation.txt:4002` |
| `responses/release.body` | `restorable` | 200 / 19950 | `registry/w-provresidue-validation.txt:4050` |
| `responses/tag.body` | `restorable` | 200 / 335 | `registry/w-provresidue-validation.txt:4098` |

**FOUND present-but-mismatched:** `tests/fixtures/hg_bfcl/acquire.py`; pin `ec4b6599ffa0f9f6d9136b0113c3c70d64e85bf73e73a6b7cb898fc313f0721c`; recomputed `0e17ca9780309a44e8166f4429caa1b5e360a1744d6cf98ee78c415c5ca44d04`. Source pin `tests/fixtures/hg_bfcl/SHA256SUMS:3`; exact observed comparison `registry/w-provresidue-validation.txt:13`. Fetching absent bodies cannot correct these local bytes.

**Test impact:** `tests/quality/test_dataset_blockers.py` reads only registry-selected metadata through its checker (`:19`, `:57-58`; `tools/check_dataset_blockers.py:118-119`). Missing bodies have **no effect** on those reads. The registry selects E3 inventory (`registry/dataset-blockers.json:171`), Trivia README (`:731`), or BFCL README/inventory (`:181`, `:186`) as appropriate. Missing selected hg_* metadata can explicitly skip whole-registry tests (`tests/quality/conftest.py:39-45`); this is not a body skip.

The standalone `tests/fixtures/hg_bfcl/verify.py:39-43` reads receipt body paths unguarded; `:87` opens the absent archive. A missing body would raise `FileNotFoundError` if reached; earlier inherited reads can also fail. It was not run.

## Test search and the fetching question

**ABSENT direct suite references** within all Python under `tests/` except `tests/fixtures/**`: exact command C (`registry/w-provresidue-validation.txt:95`) returned empty output, exit 1. Expanded named-helper search D, scoped to `test*.py` and `conftest.py` anywhere in `tests/`, also returned empty output, exit 1 (`registry/w-provresidue-validation.txt:101`). Registry reference search E (`registry/w-provresidue-validation.txt:107`) returns only the four metadata locators named above. These scopes do not prove absence of every conceivable runtime-generated path. Tests and standalone verifiers were not executed; runtime outcomes are **UNKNOWN**.

**For which of these five packets will red tests never clear by fetching?** No suite red attributable to these five packets' missing bodies is established by the searched code: the only identified suite reader uses metadata. Therefore none can honestly be named as a measured “red that will never clear.” If “red” means the standalone packet integrity checks, **hg_wprov, upstream_provenance_e2 and hg_bfcl cannot become fully hash-clean merely by fetching absent remote bodies**: they already contain present mismatches; hg_wprov additionally lacks replay URLs for three historical local artifacts and records two absent 404 payloads. E3 and Trivia have no measured integrity defect beyond missing receipt-qualified 200 bodies. E2's 307 remains unknown, not “never fetchable.” Evidence: A summaries, per-entry rows, and cited helper reads.

## Population and minimal guard dispositions

Unique paths only; hg_wprov nested duplicate pins are not added again. `present-verified` excludes mismatches. Each absent class is mutually exclusive. Source: A/K and the per-entry JSON.

| packet | present-verified | restorable | pinned_error_payload | empty_body_legitimate | recorded_404 | no_receipt_no_url | unknown | present-but-mismatched |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `e3_bfcl_source` | 63 | 24 | 0 | 0 | 0 | 0 | 0 | 0 |
| `hg_wprov` | 90 | 15 | 0 | 2 | 2 | 3 | 0 | 2 |
| `upstream_provenance_e2` | 31 | 5 | 0 | 9 | 0 | 0 | 1 | 1 |
| `hg_trivia` | 40 | 13 | 0 | 0 | 0 | 0 | 0 | 0 |
| `hg_bfcl` | 15 | 5 | 0 | 0 | 0 | 0 | 0 | 1 |
| **total** | **239** | **62** | **0** | **11** | **2** | **3** | **1** | **4** |

- `e3_bfcl_source`: assert 24 enumerated missing bodies have matching recorded-200 evidence; skip only checks that need those bodies; do not claim fresh-byte restoration.
- `hg_wprov`: assert 15 recorded-200 absences, 2 empty failure sentinels, 2 historical 404s, and 3 local artifacts without replay URLs; preserve failure evidence and reject/flag the 2 present mismatches separately.
- `upstream_provenance_e2`: assert 5 recorded-200 absences and 9 documented empties; retain 1 unknown redirect disposition and flag the present verifier mismatch.
- `hg_trivia`: assert all 13 absences have matching recorded-200 evidence; the identical pair has exact locally reconstructible metadata bytes. No structural remote error is proved.
- `hg_bfcl`: assert all 5 absences have matching recorded-200 evidence; flag the present acquisition-helper mismatch, so “all residue restorable” does not imply a clean packet.

These are proposed guard assertions only; no guard, fixture, registry state, historical receipt or test was modified. `registry/dataset-blockers.json` and the journal remain parent-owned. No dataset-blocker state change is warranted by a missing-file classification alone.
