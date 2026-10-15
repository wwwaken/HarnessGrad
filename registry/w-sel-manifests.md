# First-five selected manifests and selected-only exports - w-sel

**LIMIT OF THE CLAIM: bounded first-N in the adapter's declared order. NOT random and NOT representative.** Only these five tasks per dataset have an identifiable, hash-bound selection → export → scoring-input chain. Nothing about the remainder of any pool, scoring execution, eligibility, comparable performance or production admission follows.

The current next_actions do **not** say all eight are blocked only on selection: FEVER, HotpotQA, SpreadsheetBench and TriviaQA retain different independent obligations; Reasoning Gym also has generation and eligibility clauses. No blocker/status/next_action/history/shared gate is closed or changed. Four permanent refusals are untouched.

The operator supplied the selection policy: the first five of the FULL adapter presentation, before any side filter, without sorting, sampling, shuffle or replacement. Chosen split mode is `declared`. Seven prefixes span train and eval, so each task's side is retained and the manifest side is `mixed`; this is not an accepted single-side launch specification. TriviaQA's prefix is all eval. We do not turn the first five into a first-five-eval selection. For hash adapters, side is SHA256(task_id UTF-8).digest()[0] % 3 == 0 → eval, otherwise train (data/scaffolds/qa/base.py:122, :289; SpreadsheetBench :355, :370). This hash determines SIDE, not task ordering. `official` mode would put these non-study pools wholly in eval; it was not silently selected. TriviaQA's declared and official validation sides agree.

Each manifest `run_id` is a fresh prospective ID reserved for this selection packet, identical to `selection_id`; `run_state` says reserved selection only. `runtime_run_id=null`: no actual execution, diagnostic or pilot was launched. No historical run is resumed, reconciled or overwritten. A future authorized run must resolve applicable single-side selection and admission gates; these IDs are not runtime receipts. Per dataset: selected=5, unexecuted selected=5, executed trials=0, measured/invalid/unmeasured *execution* counts=0; eligible count is unknown. Those zeros are not successful task coverage and the five are not invalid or zero-score trials.

All payloads are external under the export paths below, with exactly the five selected rows and their per-task inputs. Git contains only this text report and the small manifest/digest/reproduction packet; no dataset rows, expected answers, workbook bytes or downloaded payloads. CSV exports retain original header/selected physical row bytes; JSONL exports retain original nonblank selected line bytes. Parquet exports are JSONL of precisely the decoded columns consumed by the adapter (TriviaQA projects question/answer). SpreadsheetBench exports a five-element rows.json plus exactly five initial/golden/task/goal input sets. Adapter construction reads the installed pool (including TriviaQA's declared train study sample) but exports no other rows. No scoring functions, model, server or network endpoint were invoked.

Digest domains: `row SHA-256` is UTF-8 json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(',',':'), allow_nan=False), without newline. For QA, `scorer input SHA-256` hashes EXACT gold.json UTF-8 bytes from QASpec.verifier (base.py:339), json.dumps(gold, ensure_ascii=False, sort_keys=True), including default spaces and no newline. These bytes are exported at inputs/<position>/gold.json. Manifests additionally bind exact question and goal bytes, so identical label-only gold digests on different tasks do not collapse task identity. For SpreadsheetBench the displayed scorer digest is the scorer_input inventory hash over golden.xlsx/task.json component digests (data/scaffolds/scorer_input.py:21), not a concatenation or direct workbook digest; component byte hashes are listed separately. No actor-generated result exists yet.

All values below come from actual bytes read by `python3 tests/fixtures/hg_wsel/packet.py --create --export-root ...` and independently reconstructed by `python3 tests/fixtures/hg_wsel/packet.py`; exact paths/commands/output, sha256sum verification and registry checks are in `registry/w-sel-validation.txt`. Five preserved ordered inventories are freshly compared for the selected rows only; full historical inventory files stay external and their size/hash is recorded. FEVER's earlier source custody is checked separately; HotpotQA/TriviaQA installed parquet pins are checked against adapter downloads declarations. Whole-pool custody is not inferred from selected-row comparison.

## fever

**Selection bound: YES (five tasks, scoring-input custody only). Blocker remains OPEN.** Bounded first-N selection in declared adapter order; NOT a random sample and NOT representative of the dataset. Establishes only identifiable, hash-bound selection -> export -> scoring-input custody for these five tasks, not scoring execution, eligibility, admission or claims about the rest of the pool.

Ordering: data/datasets/fever.py:46 reads valid.jsonl through base.jsonl_rows; data/scaffolds/qa/read.py:149 preserves nonblank JSONL line order. data/datasets/fever.py:54 declares validation; QASpec.records at data/scaffolds/qa/base.py:235 enumerates those rows, and :250 makes dataset/split/source-index IDs. First five are nonblank row offsets 0–4. Stable only while these pinned installed bytes stay fixed.

Source/split: `a6b8d891d393e97a4efac791afffb2d7de5e57c6`; `validation`. Split=`declared`, source=`hash`, selected side=`mixed`. Task sides appear in selection order below.

Installed file: `/mnt/20t/xubuqiang/datasets/fever/valid.jsonl` (6471611 bytes), SHA-256 `5da0ccc0ccf77f974611de13f8aac6f78c6bba6293912835099eb6029baa85d9`. Presented pool=15935; this is a row/task count, not eligible coverage.

Prospective run ID: `hg-wsel-exports-20261015T081758Z-e8bf2cb83f6f-fever`. Manifest: `tests/fixtures/hg_wsel/fever.json`. Export directory: `/tmp/hg-wsel-exports-20261015T081758Z-e8bf2cb83f6f/fever`; rows: `rows.jsonl`; row export SHA-256 `41189af8735e749797dd26415a69b7075adb7ba54692b6039a0879d20450f72b`. Complete selected-only file inventory digest: `f36b7123c34900ebdf782122a67dd1d7bf281e572cd5935cf178fa1dffed730b` (16 files).

| Position | Task ID (source index) | Native row ID | Declared side | Row SHA-256 | Scorer input SHA-256 |
| --- | --- | --- | --- | --- | --- |
| 0 | `fever/validation/0` (0) | `e9a7305690bde211b7434ccd53b3a763` | train | `3089f3936d16aa292cd3df2e9777d7db2532c68d6e68c8c6420c06597edb2e12` | `4f25c1ca5756408dd82f17ff1757afe5ec1982d405326869d5ff895c040cba21` |
| 1 | `fever/validation/1` (1) | `82caf51ce8a246f1b5244cc1fd8ca9d4` | eval | `acdb1be775ba1853995ceabae7014f72eec5d0199df15fb21b1e08c4cb658101` | `e1d804cccd806c5d50a4eabbb0b1c4512439dffe3d172545810009c210509e1f` |
| 2 | `fever/validation/2` (2) | `b8182754eb4410163c45b97ddb3b6de1` | train | `9f0bb9ff57ff857ecae1ddd22e67d1ac670aa1708596e824a686eb01bafd001e` | `a346faf754cc26c891d88468f5a2a742b039b38a74db5397193a57a943bca24e` |
| 3 | `fever/validation/3` (3) | `2ab70646fffa23b2c2546796d6d85fd3` | eval | `2380b8b61b4108828cef9b055aad4497612447da5cdc530e9db0f499bfe10413` | `73d42e0505825789348baeb368eae9154a35fdc8718cd44a2364b2d8480a9f2e` |
| 4 | `fever/validation/4` (4) | `95bcef60842dc24a2d9b18ae25020303` | eval | `d85db8e5ff549bd77df5a844c8f25777fdc71ae39e3b47246216418128621a11` | `c2d1f23d10359627dbc1b917d5bb59cba095a5e78a39542c59190df6ef74f1d2` |

Metric boundary: Current local strict label/evidence metric, five predicted evidence pairs and NEI exemption (fever.py:27; qa/evidence_scorers.py). This is not a claim that installed flat/singleton evidence is equivalent to complete original FEVER groups; acquired scorer source pin 4801615100fbf6327f8e99b5dbaefe5dd890e869 is retained, with no named release invented.

**Remaining unmet clauses:** Producing-conversion revision and execution/ID-assignment/split/filter/omission/NEI-input provenance; complete original FEVER ID/evidence-group correspondence and flat-to-singleton metric comparability (earlier mapping corroborates rows but leaves 51 omitted alternative groups and 1,395 structurally insufficient singleton rows); actual pristine verifier execution and scorer-offline-closure; both shared gates. Installed export-byte custody is already corroborated and selected manifest custody is now bound. Exact scorer-source identity is retained, not executed.

Unchanged full next_action audited: > NEXT gate remains source-provenance and metric-comparability: bind the authenticated exact Hub revision/tree export metadata to actual export bytes, the producing conversion and original FEVER ID/evidence-group correspondence; establish installed bytes and selected manifest custody. Use the acquired exact scorer source revision without inventing a release or claiming singleton equivalence. Document the actual metric and establish scorer-offline-closure and pristine verifier evidence with all remaining shared gates before any separately authorized diagnostic. The official-scorer-identity proof obligation stays withdrawn.

## hotpotqa

**Selection bound: YES (five tasks, scoring-input custody only). Blocker remains OPEN.** Bounded first-N selection in declared adapter order; NOT a random sample and NOT representative of the dataset. Establishes only identifiable, hash-bound selection -> export -> scoring-input custody for these five tasks, not scoring execution, eligibility, admission or claims about the rest of the pool.

Ordering: data/datasets/hotpotqa.py:58 reads fullwiki/validation parquet, declared at :100. data/scaffolds/qa/read.py:144 preserves decoded parquet row order; data/scaffolds/qa/base.py:235 enumerates it and :250 constructs IDs. First five are file row offsets 0–4. No random ordering or sampling.

Source/split: `1908d6afbbead072334abe2965f91bd2709910ab`; `validation`. Split=`declared`, source=`hash`, selected side=`mixed`. Task sides appear in selection order below.

Installed file: `/mnt/20t/xubuqiang/datasets/hotpotqa/fullwiki/validation-00000-of-00001.parquet` (28041820 bytes), SHA-256 `78933c0a31a5f7b420d4effdf4cd4eed573b28c6a3da6179dcf7a02b39e51d03`. Presented pool=7405; this is a row/task count, not eligible coverage.

Prospective run ID: `hg-wsel-exports-20261015T081758Z-e8bf2cb83f6f-hotpotqa`. Manifest: `tests/fixtures/hg_wsel/hotpotqa.json`. Export directory: `/tmp/hg-wsel-exports-20261015T081758Z-e8bf2cb83f6f/hotpotqa`; rows: `rows.jsonl`; row export SHA-256 `0cfe16ffdf0984132e537236d1e701900217984d3219889eeeca43fc3356ec01`. Complete selected-only file inventory digest: `753a8d2f30f72650ce33e942113bbd53fdd223c63ebdbe1adf944e798d76b900` (16 files).

| Position | Task ID (source index) | Native row ID | Declared side | Row SHA-256 | Scorer input SHA-256 |
| --- | --- | --- | --- | --- | --- |
| 0 | `hotpotqa/validation/0` (0) | `5a8b57f25542995d1e6f1371` | train | `66a844cc7b09e70907b2077ae232146c209b33c8e143286615f8d91e605aea50` | `496f379ebdbe94d738dbccbd7f5be5228d8a133f1248243bfd8d14c4da770bc2` |
| 1 | `hotpotqa/validation/1` (1) | `5a8c7595554299585d9e36b6` | train | `e6707a73232f3321e948751a6fa6a8a1796f6832e69cefa31b6cc9547cedf672` | `08fcfad039524654f2ac28777dd8c1222b8d0150a670d041d55e1ea3a57aba74` |
| 2 | `hotpotqa/validation/2` (2) | `5a85ea095542994775f606a8` | eval | `1dd0ab88f6e3a894a6c2d98d0a078e30c1b7bc9ae37f151c5a55b62271449a2d` | `8dddf51756e383d070b12e18149cb7f5159361df97d48b4130f7b053115d0a82` |
| 3 | `hotpotqa/validation/3` (3) | `5adbf0a255429947ff17385a` | train | `fef0d15cc8266622aa992bca0fea0d2bfc503767970a57973ec0c79b144b2bcd` | `7f433eac614d88b3b7c3e18fb1c3ff702a912ba1b3910ae9b7a44847042b0ca4` |
| 4 | `hotpotqa/validation/4` (4) | `5a8e3ea95542995a26add48d` | eval | `ce5c1584a7ac9667429c8001b54ab29966bac7ad8240fbe8ccd776c08cc4293b` | `981d56be264f12e6c7a574f1cf89489e9cfdfd831de655e8bcc6b6ff81bbb832` |

Metric boundary: Current local HotpotQA joint EM (supporting-fact exact set semantics), with answer/support/joint F1 components (hotpotqa.py:36). Hashes bind the full supporting-facts gold, not answer text alone. No score was computed.

**Remaining unmet clauses:** ORIGINAL historical selected-ID/trial/error/timeout receipts and original source/split/manifest/model/harness provenance; historical measured/invalid/unmeasured counts and lifecycle/cleanup reconciliation; current selected scorer/control admission; both shared gates. Fresh first-five selection does not recover the historical selection or unknown historical run ID. Preserve the incomplete full-size protocol, effect=null and existing timeout synthetic closure; no old run resumes and any separately authorized diagnostic must follow current staged policy.

Unchanged full next_action audited: > Historical comparison requires original selected-ID/trial/error/timeout and source/split/manifest/model/harness provenance receipts, with measured/invalid/unmeasured counts and lifecycle/cleanup reconciliation. Preserve the old full-size protocol as incomplete, unknown run ID and effect=null; do not resume or rerun it. Timeout classification/persistence/aggregation is synthetically closed; current selected scorer/control admission and all existing shared gates remain required. Any separately authorized future diagnostic uses a fresh ID under the current staged policy.

## physicsquestions

**Selection bound: YES (five tasks, scoring-input custody only). Blocker remains OPEN.** Bounded first-N selection in declared adapter order; NOT a random sample and NOT representative of the dataset. Establishes only identifiable, hash-bound selection -> export -> scoring-input custody for these five tasks, not scoring execution, eligibility, admission or claims about the rest of the pool.

Ordering: data/datasets/physicsquestions.py:120 uses csv.DictReader in physical CSV order and discards blank input rows at :125. _SPEC at :194 maps those rows to test, declared at :214. data/scaffolds/qa/base.py:235 enumerates the filtered rows. First five are filtered offsets 0–4; selected CSV bytes are checked against the corresponding adapter records. The source-filter order is retained, not a numeric/lexical sort.

Source/split: `ReWOO@9cd0283043ff4be0c9d614fda2789d143ca6ffd1`; `test`. Split=`declared`, source=`hash`, selected side=`mixed`. Task sides appear in selection order below.

Installed file: `/mnt/20t/xubuqiang/datasets/physicsquestions/ReWOO-9cd0283043ff4be0c9d614fda2789d143ca6ffd1/data/bigbench/physics_question.csv` (17953 bytes), SHA-256 `7747cf185111aaa58493b5d804ba7b496cb152a6ae89a69a66a0c443adfd34aa`. Presented pool=53; this is a row/task count, not eligible coverage.

Prospective run ID: `hg-wsel-exports-20261015T081758Z-e8bf2cb83f6f-physicsquestions`. Manifest: `tests/fixtures/hg_wsel/physicsquestions.json`. Export directory: `/tmp/hg-wsel-exports-20261015T081758Z-e8bf2cb83f6f/physicsquestions`; rows: `rows.csv`; row export SHA-256 `7ab817d5ea33b40aee19e753bf439f0b19b25f42d6dadc6e3d62829de4c6b8a2`. Complete selected-only file inventory digest: `94518f5d3f53f23b41e55397a5715329cdfb854bb63c189414c544f91716f093` (16 files).

| Position | Task ID (source index) | Native row ID | Declared side | Row SHA-256 | Scorer input SHA-256 |
| --- | --- | --- | --- | --- | --- |
| 0 | `physicsquestions/test/0` (0) | `positional` | train | `b124901b8715b9fa496e96665dde7d21055f26a2edb4f8f9c3db401b4c47fe69` | `d7e4af51a0ac9bf8429c2e26c004267f5965fb1de0757ce3627c891d4167b9da` |
| 1 | `physicsquestions/test/1` (1) | `positional` | train | `3d98b6f72c888761e149524a2c7d9b938ddcea60e8785d2988c32eeac1696f5a` | `28c2127b6214532abb4d159f711c51eab1c17c39390a9a01d5746e6ad099ae98` |
| 2 | `physicsquestions/test/2` (2) | `positional` | train | `0c561bc62feee1e68f0c14f9916d8c1c996ea6ba3fb9deb85cef35063e3d87ae` | `b14deeafaa1741dd300253596fa58e2858492a85fb8f516e90c253427cc3ed92` |
| 3 | `physicsquestions/test/3` (3) | `positional` | eval | `e4faff03f85f123222c2df62227bf3eaabdae57a5e6f95aff0742c02e5e04647` | `7f9afda7f51a9e1053dbf9861803d2f66a6c37e59f0b9046c04f5aa9daf11e9f` |
| 4 | `physicsquestions/test/4` (4) | `positional` | train | `f7dc58cad1fd0166e3239a2a986bb96ee1807296c7550329d5aacecb3e0e8a7c` | `367f715b004916a5dc598a5e770048700aa870253ad7751c9028765b910ee0d0` |

Metric boundary: Local asymmetric normalized accepted-spelling EM (physicsquestions.py:73, :93, :103), reported separately from matched BIG-bench processing/aggregation. Upstream ReWOO/BIG-bench lineage is retained; no historical converter or execution inferred.

**Remaining unmet clauses:** Actual scorer-offline-closure, pristine verifier execution and both shared gates; actual invalid/unmeasured task/trial execution coverage. Installed/ReWOO/ordered BIG-bench linkage is retained and local EM is explicitly reported separately. Selected manifest/export to exact rows and declared per-task sides is now bound. This mixed-side packet is not a ready single-side diagnostic or authorization.

Unchanged full next_action audited: > NEXT gate: bind an independently supplied run-specific selected manifest and selected-only export to the preserved installed CSV, row/task inventory and chosen split/side; no selection or run ID is supplied here. Then establish scorer-offline-closure, pristine verifier execution and remaining shared evidence. Retain the installed-to-ReWOO and ordered pinned-BIG-bench linkage, report local normalized accepted-spelling EM separately from matched BIG-bench processing/aggregation, and do not infer a historical converter revision or runtime execution. Preserve invalid/unmeasured coverage and withdrawn official-scorer-identity proof decision; no diagnostic is authorized.

## reasoning_gym

**Selection bound: YES (five tasks, scoring-input custody only). Blocker remains OPEN.** Bounded first-N selection in declared adapter order; NOT a random sample and NOT representative of the dataset. Establishes only identifiable, hash-bound selection -> export -> scoring-input custody for these five tasks, not scoring execution, eligibility, admission or claims about the rest of the pool.

Ordering: data/datasets/reasoning_gym.py:80 reads the preserved pool.jsonl using base.jsonl_rows, and :162 declares the source key eval. data/scaffolds/qa/read.py:149 preserves nonblank line order, and data/scaffolds/qa/base.py:235 enumerates it. The selected rows are family ab, family indices 0–4. This is the frozen family-major file order, NOT a regenerated seed-specific order. Prior provenance work found generation date/hash-order/dependency uncertainty and 84 differing regenerated rows; this selection does not repair or reproduce generation.

Source/split: `reasoning-gym==0.1.25; seed=20261008; per_family=20; preserved pool, not regenerated`; `eval`. Split=`declared`, source=`hash`, selected side=`mixed`. Task sides appear in selection order below.

Installed file: `/mnt/20t/xubuqiang/datasets/reasoning_gym/pool.jsonl` (3315981 bytes), SHA-256 `c0ff4eaef318cd59afcc61472ebe206362fc0211c4b589ed0d53946a569bd177`. Presented pool=1780; this is a row/task count, not eligible coverage.

Prospective run ID: `hg-wsel-exports-20261015T081758Z-e8bf2cb83f6f-reasoning_gym`. Manifest: `tests/fixtures/hg_wsel/reasoning_gym.json`. Export directory: `/tmp/hg-wsel-exports-20261015T081758Z-e8bf2cb83f6f/reasoning_gym`; rows: `rows.jsonl`; row export SHA-256 `0d00e9c9517e549af76bfda59d0183f5682c3eacab0fb35597753664d87d863f`. Complete selected-only file inventory digest: `9529aac306a9450f10c894282bba41f912b8b28e2bd6322643ab94a662c127b2` (16 files).

| Position | Task ID (source index) | Native row ID | Declared side | Row SHA-256 | Scorer input SHA-256 |
| --- | --- | --- | --- | --- | --- |
| 0 | `reasoning_gym/eval/0` (0) | `ab/0` | train | `6a088ed3f0faba4ef70706e9611d5c88c0d819cc308feb920d636d4a40fa3ee7` | `3a1ad75316cfbfd5c8ef3d68eaebdf472e1ecbc87e09cf8c0177eefff4fdc54b` |
| 1 | `reasoning_gym/eval/1` (1) | `ab/1` | train | `3b20109cad0508c1610099be00629ca8c86c9cfaa89cdb5af1df65b12699e477` | `558794148fb33f99f643369924266c5882319282c9f500e528bfa5519e394b06` |
| 2 | `reasoning_gym/eval/2` (2) | `ab/2` | eval | `3f78c76d5b743f198ffb14ba18712ce5f6d5285e2bb11b77e3bcb2d0bc5266e7` | `02bacf660571f552f0ccd99fb69912dc71d5762504d35646f8f436b9b52a6d9d` |
| 3 | `reasoning_gym/eval/3` (3) | `ab/3` | train | `199e1d04705a8fb005f4a4895fa00d87bb0dda0de7c0262edd00c5a2e22e782d` | `c0be328d2aafcf2bf683a10cf780623cf8b7819434d319b52724f54fbda68ed9` |
| 4 | `reasoning_gym/eval/4` (4) | `ab/4` | train | `9888a02feb92f879180ff8313d5fdd3ae7ad061f6ca4f802c9126e9763d34541` | `8f7b7c61d23a04e9a70c8d1033fc9d2e72e893009d1a9e95e902a33919150ac6` |

Metric boundary: Library family score_answer(answer, entry) under reasoning-gym 0.1.25, seed 20261008, per_family 20 (reasoning_gym.py:107). Selected gold includes family/index/full entry. The library scorer was not invoked; package/dependency/runtime equivalence and family eligibility are unproved by this packet.

**Remaining unmet clauses:** Original generation process/environment/date/hash-order/dependency metadata and exact frozen-pool reproduction with recorded original inputs; independent behavioral reference=1/empty=0 family eligibility; deterministic transitive dependencies without scoring extras in the actual pristine verifier; metric/runtime validation, scorer-offline-closure and both shared gates. Selected frozen-row custody is now bound; no seed/family/order substitution, regeneration or pool overwrite occurred. No independent public seed-specific pool release is newly authenticated.

Unchanged full next_action audited: > Retain authenticated distribution/source/installed-member custody and declared pool hash/family/order evidence; recover original generation environment/date/order metadata and reproduce the declared pool with recorded inputs, without changing its seed/families or overwriting original bytes; independently establish behavioral reference=1/empty=0 family eligibility and bind an independently supplied run-specific selected manifest and selected-only export to exact pool rows and chosen split/side. No independent seed-specific pool release or selected run manifest was authenticated from the acquired public sources. Establish deterministic transitive dependencies without scoring extras in the actual pristine verifier, metric identity, scorer-offline-closure and all remaining shared evidence; the official-scorer-identity proof obligation stays withdrawn. No diagnostic is authorized.

## sportsunderstanding

**Selection bound: YES (five tasks, scoring-input custody only). Blocker remains OPEN.** Bounded first-N selection in declared adapter order; NOT a random sample and NOT representative of the dataset. Establishes only identifiable, hash-bound selection -> export -> scoring-input custody for these five tasks, not scoring execution, eligibility, admission or claims about the rest of the pool.

Ordering: data/datasets/sportsunderstanding.py:101 uses list(csv.DictReader(handle)) unchanged at :106; _SPEC maps it to test at :169 and declares test at :188. data/scaffolds/qa/base.py:235 enumerates it. First five are physical parsed CSV rows 0–4, no blank filtering, sorting or shuffle.

Source/split: `ReWOO@9cd0283043ff4be0c9d614fda2789d143ca6ffd1`; `test`. Split=`declared`, source=`hash`, selected side=`mixed`. Task sides appear in selection order below.

Installed file: `/mnt/20t/xubuqiang/datasets/sportsunderstanding/ReWOO-9cd0283043ff4be0c9d614fda2789d143ca6ffd1/data/bigbench/sports_understanding.csv` (137846 bytes), SHA-256 `5cfc24702b7a809409f42634f0b958f0d61c4d5aec8d732fd89889281c63d45e`. Presented pool=1000; this is a row/task count, not eligible coverage.

Prospective run ID: `hg-wsel-exports-20261015T081758Z-e8bf2cb83f6f-sportsunderstanding`. Manifest: `tests/fixtures/hg_wsel/sportsunderstanding.json`. Export directory: `/tmp/hg-wsel-exports-20261015T081758Z-e8bf2cb83f6f/sportsunderstanding`; rows: `rows.csv`; row export SHA-256 `7aac56567d1b27d589ef1c87928736ffba0168f13a61711326058a8f31e414dd`. Complete selected-only file inventory digest: `77d3b2bfa3f6e004eac6061c652472574eee9e49c52adce762ddd3fa1b02f75b` (16 files).

| Position | Task ID (source index) | Native row ID | Declared side | Row SHA-256 | Scorer input SHA-256 |
| --- | --- | --- | --- | --- | --- |
| 0 | `sportsunderstanding/test/0` (0) | `positional` | train | `e434c3cbe76696f5584602ab5cbc228e0bf6b2d2942473ce5f2adf70e294ad06` | `84aae3b8b93374b61016a847d0b59910a1cd2df101f979c04352fddffeb252dc` |
| 1 | `sportsunderstanding/test/1` (1) | `positional` | eval | `8866f5a5716067f96da1d678a4c8934091aee45e797d28aeab08fd600889c686` | `84aae3b8b93374b61016a847d0b59910a1cd2df101f979c04352fddffeb252dc` |
| 2 | `sportsunderstanding/test/2` (2) | `positional` | train | `643e91916edf97604e6dabe45df16f86887cdb7c6860f03a25297c00074f6e43` | `84aae3b8b93374b61016a847d0b59910a1cd2df101f979c04352fddffeb252dc` |
| 3 | `sportsunderstanding/test/3` (3) | `positional` | train | `33bdb5d08ed907fb090a7a6dac9eade1304db8d7ef9a24c8455c1e0d79f2c6d7` | `0b316498690671df4dc5553af217c425178dd658ff6b30f085120d0b3285f0b2` |
| 4 | `sportsunderstanding/test/4` (4) | `positional` | eval | `940a13cd0dd0b2b25089456421174655a64b0b685c6a5e81a73235d5454bef37` | `0b316498690671df4dc5553af217c425178dd658ff6b30f085120d0b3285f0b2` |

Metric boundary: LOCAL text-label substring-choice reward with a both-labels rejection rule (sportsunderstanding.py:63, :80). Reported separately; NOT equivalent to candidate-log-probability multiple_choice_grade. The adapter's legacy official metric label does not establish that equivalence. This explicitly satisfies the next_action alternative of separately reporting the local metric, while leaving execution gates open.

**Remaining unmet clauses:** Actual scorer-offline-closure, pristine runtime and both shared admission gates; actual measured/invalid/unmeasured execution coverage. Retain installed-to-ReWOO/pinned BIG-bench row linkage. Local text-label metric is explicitly separated here, satisfying that reporting alternative without resolving the underlying protocol difference. Selected manifest/export and declared per-task sides are now bound.

Unchanged full next_action audited: > Retain authenticated installed-to-ReWOO and pinned BIG-bench sports row linkage. Resolve the measured source-level metric/protocol mismatch or report the local text-label metric separately; do not call it equivalent to candidate-log-probability multiple_choice_grade. Bind an independently supplied run-specific selected manifest and selected-only export to exact source rows and chosen split/side, then establish scorer-offline-closure, pristine runtime and all shared admission evidence before any separately authorized diagnostic. Report invalid/unmeasured coverage explicitly.

## spreadsheetbench

**Selection bound: YES (five tasks, scoring-input custody only). Blocker remains OPEN.** Bounded first-N selection in declared adapter order; NOT a random sample and NOT representative of the dataset. Establishes only identifiable, hash-bound selection -> export -> scoring-input custody for these five tasks, not scoring execution, eligibility, admission or claims about the rest of the pool.

Ordering: data/datasets/spreadsheetbench.py:107 reads dataset.json and iterates its JSON array unchanged at :115; task_id is str(row["id"]) at :116. load() at :345 preserves record order at :351. First five JSON-array entries are 13-1, 17-35, 22-47, 23-24, 24-23. Workbook filename fallback sorting at :167 selects a file within a task and does not reorder tasks.

Source/split: `ab0b742b0fc95b946f212d80ac7771b5531272e4`; `verified_400`. Split=`declared`, source=`hash`, selected side=`mixed`. Task sides appear in selection order below.

Installed file: `/mnt/20t/xubuqiang/datasets/spreadsheetbench/spreadsheetbench_verified_400/dataset.json` (306533 bytes), SHA-256 `bcecaa89a005bd4e3bbe98da150a86e8062c27f262e575d5e47bd9861b3525e7`. Presented pool=400; this is a row/task count, not eligible coverage.

Prospective run ID: `hg-wsel-exports-20261015T081758Z-e8bf2cb83f6f-spreadsheetbench`. Manifest: `tests/fixtures/hg_wsel/spreadsheetbench.json`. Export directory: `/tmp/hg-wsel-exports-20261015T081758Z-e8bf2cb83f6f/spreadsheetbench`; rows: `rows.json`; row export SHA-256 `395b1fff129d8de3ba59b79ed09b7c20bebd74560d9377ec3e147cd7170f6c50`. Complete selected-only file inventory digest: `ee60ef16c7fcb0a248a1450885130af48a16c77ed06f9471a098df8374c6944f` (21 files).

| Position | Task ID (source index) | Native row ID | Declared side | Row SHA-256 | Scorer input SHA-256 |
| --- | --- | --- | --- | --- | --- |
| 0 | `13-1` (0) | `13-1` | train | `7f20332a4a7cbc778e1779496a62d31ac5eb929d56d94b522aa00e5317b2e602` | `9cbb070ac434b7c1a73554dc5c57e1164e6e92dc68e3491907f056104e79ee4c` |
| 1 | `17-35` (1) | `17-35` | train | `deab9a53a887f73a881be4d8d88932604052e95407a5ed8feb46f62266d60224` | `6f3ca83c4356e3f214170b9cae54286bb8e366ce75a1e4d1bb86b622d1978a37` |
| 2 | `22-47` (2) | `22-47` | train | `ccfe9e6e59ecd90e275ec6df01f58146ae0bdced15c0772935e91f7beea4f753` | `0fda9279dff83cff65c70a290d1cb5dfcb3ad15484e62f923d6325ed24848d91` |
| 3 | `23-24` (3) | `23-24` | eval | `95b2468f44602d72d761f5413d00bfc94883e1d67ac9c8ed6ec110bb1130b318` | `40ee20d4d3c1b74c189ddc52c0ea6ff6f83eeefcf438ded2a666c7a50cef3cb9` |
| 4 | `24-23` (4) | `24-23` | train | `0012c64d26820a0efb51a753986d02099b536418befff73939ab28c4a1341a13` | `692dbfc0fec8717f22a7bf79f5ca737e6578439bb68ef424eaeb10290efe76fa` |

Exact selected workbook/scorer component byte digests:

| Task | Initial workbook SHA-256 | Golden workbook SHA-256 | task.json SHA-256 |
| --- | --- | --- | --- |
| `13-1` | `36e7e5238ac29a506d06a27b73aab4ac6249530c9cfd4b1c40835c7823a39da5` | `a8eaf5ec1991c35ae785fb82efce2ecd24f6268410a8a89f78ca07843fcaf140` | `a8a0039e0c42fca97d1574a21706a34c14ef9246543bb7fee1a4eaff061d3e1a` |
| `17-35` | `50ba7b30308e0579e4141120349c0c97103fb6b58b315051e9bafd3764c75feb` | `2e35c3957c9025cc60a3b4bd10984b709037eb674c1ab26e18805c99f9543ce4` | `fec79b694b4bc3329a325963edd23883fd3d85d68003ad3b2f5b391876a5c744` |
| `22-47` | `d06080c377499133d6ccb6a0efc9a88f78cfa98b3ea76b53c2443acbf21afa6e` | `2dd6719f5d3b37eca3b51e3d3cbc57f1f4791bc194e30f3932f2ce0acd4695c8` | `0338b0a05f80f427325fbfc9d84ee3fe7f95c2d904ed2149d0ce77b790bca5b3` |
| `23-24` | `9edd14173d1e42f481a909f07e9ad9e56c2c38c0782f20a25cf6280020ce9cd5` | `f0aed39194734eb7c471aa80fb5a0ec9677ba60a35b7b7fb1c10de38dc21b2b6` | `e21c3e0026cfc9264b23c8509aba6aa8493ca35d2a237184e50e6f7740256830` |
| `24-23` | `ad398fa79f63391cbfeb808d96e9af8b0c8d6e98de29c096c9d6f4a53f204a1a` | `150050ea865c40456eeae47ccbb8a5cc5d9f064313220b664303c851c7ef7351` | `4e70c968a19643a8da3596cf8c4b30023e704965c9706bda377aab1ba4ca5037` |

Metric boundary: One released workbook variant, local official-range-zero compatibility policy: released parser-rejected ranges retain official-equivalent measured-zero denominator treatment, distinct from completed comparisons. Infrastructure failures remain invalid/unmeasured, never scores. This is not paper soft/hard aggregation and no eligibility/comparison/scoring or LibreOffice execution took place.

**Remaining unmet clauses:** Authenticated row-level gradable eligibility and actual eligible/task/trial/invalid/unmeasured execution coverage; scorer custody/execution; formula/LibreOffice offline runtime; both scorer-offline-closure and artifact-only-state-export. Selected=5 and workbook/task-input digests are now bound, but are not eligibility or score coverage. Prior w-jc2 already established complete installed workbook/mirror custody; this packet freshly checks only selected bytes, and does not reopen or re-prove whole-mirror custody. Retain range-zero denominator and one-variant restrictions; no synthetic controls promoted.

Unchanged full next_action audited: > Establish authenticated row-level gradable eligibility and eligible/selected/task/trial/invalid/unmeasured coverage under the explicit official-range-zero compatibility policy; independently authenticate complete installed workbook/mirror and scorer custody/execution, formula/LibreOffice offline runtime and both shared gates (scorer-offline-closure and artifact-only-state-export) before a separately authorized diagnostic. Retain the official-equivalent measured-zero denominator for released parser-rejected ranges, distinguish it from completed comparisons, and never publish infrastructure failures as scores. Keep one-variant scores distinct from paper soft/hard aggregates and do not promote repaired synthetic/local controls to production evidence.

## strategyqa

**Selection bound: YES (five tasks, scoring-input custody only). Blocker remains OPEN.** Bounded first-N selection in declared adapter order; NOT a random sample and NOT representative of the dataset. Establishes only identifiable, hash-bound selection -> export -> scoring-input custody for these five tasks, not scoring execution, eligibility, admission or claims about the rest of the pool.

Ordering: data/datasets/strategyqa.py:107 reads list(csv.DictReader(handle)) unchanged at :112; _SPEC maps it to test at :179, declared at :197. data/scaffolds/qa/base.py:235 enumerates it. First five are physical parsed CSV rows 0–4, with no sorting/sampling/shuffling.

Source/split: `ReWOO@9cd0283043ff4be0c9d614fda2789d143ca6ffd1`; `test`. Split=`declared`, source=`hash`, selected side=`mixed`. Task sides appear in selection order below.

Installed file: `/mnt/20t/xubuqiang/datasets/strategyqa/ReWOO-9cd0283043ff4be0c9d614fda2789d143ca6ffd1/data/bigbench/strategy_qa.csv` (200453 bytes), SHA-256 `c1fd0c271bf98741b68ac1ea3d167c5ccf2ed46da66645d5fc0ed6222e45f055`. Presented pool=2290; this is a row/task count, not eligible coverage.

Prospective run ID: `hg-wsel-exports-20261015T081758Z-e8bf2cb83f6f-strategyqa`. Manifest: `tests/fixtures/hg_wsel/strategyqa.json`. Export directory: `/tmp/hg-wsel-exports-20261015T081758Z-e8bf2cb83f6f/strategyqa`; rows: `rows.csv`; row export SHA-256 `18bb5a754bbe04124b73396b1b7b80b522d3a59b525a6173d0d06914086bd1ba`. Complete selected-only file inventory digest: `394d0323d407000ee4a73301f8a30c688d7ea3f1d8997935130818fbc88350ee` (16 files).

| Position | Task ID (source index) | Native row ID | Declared side | Row SHA-256 | Scorer input SHA-256 |
| --- | --- | --- | --- | --- | --- |
| 0 | `strategyqa/test/0` (0) | `positional` | train | `8c6302d32f0c9464ab72ca5a97b4f88886d15d359ffa5d874056b767d9204141` | `cff9d5e72adf611516ac710d89c9a03e0425882e14d024b4ceb68002224cbe83` |
| 1 | `strategyqa/test/1` (1) | `positional` | train | `44e3996dba6587ce1c01bca18f6e2cdedd517181010eb1aaafee4da93a8b62a6` | `f7aaf09b54e1832b32bc6cfed983ebb0755a35b0ac15382e247d23a77cd5f2db` |
| 2 | `strategyqa/test/2` (2) | `positional` | train | `ac6f9ae52f740787faa1948ebc22e94b271fe5864df4facc6f5a1c1a38c56f76` | `f7aaf09b54e1832b32bc6cfed983ebb0755a35b0ac15382e247d23a77cd5f2db` |
| 3 | `strategyqa/test/3` (3) | `positional` | eval | `041517daad5de5e05265c95f50d59199a31a551249ca9abc18902d8f123fd42c` | `cff9d5e72adf611516ac710d89c9a03e0425882e14d024b4ceb68002224cbe83` |
| 4 | `strategyqa/test/4` (4) | `positional` | train | `fe0ab42fa33f249fde932ae5abc28fc5562d92e9abca5a342f3d07fa97df14af` | `f7aaf09b54e1832b32bc6cfed983ebb0755a35b0ac15382e247d23a77cd5f2db` |

Metric boundary: Local normalized whole-answer EM with retained ReWOO evaluator identity (strategyqa.py:66, :89). No F1/judge or original-benchmark split/metric equivalence is asserted.

**Remaining unmet clauses:** Original-benchmark metric/split comparability beyond the vendored table; deterministic offline dependencies; pristine verifier/runtime; both shared admission gates; actual execution-equivalence and invalid/unmeasured task/trial coverage. Installed CSV/member/revision and acquired ReWOO evaluator identity are retained. Selected exact-row export and declared per-task sides are now bound.

Unchanged full next_action audited: > Retain authenticated installed CSV/member/revision and ReWOO evaluator identity; next bind an independently supplied run-specific selected manifest and selected-only export to exact source rows and chosen split/side, and resolve original-benchmark metric/split comparability beyond the vendored table. Establish deterministic offline dependencies, pristine verifier/runtime and all shared admission evidence before any separately authorized diagnostic. Acquired evaluator bytes are not an execution-equivalence receipt; retain EM identity and explicit invalid/unmeasured task/trial coverage.

## triviaqa

**Selection bound: YES (five tasks, scoring-input custody only). Blocker remains OPEN.** Bounded first-N selection in declared adapter order; NOT a random sample and NOT representative of the dataset. Establishes only identifiable, hash-bound selection -> export -> scoring-input custody for these five tasks, not scoring execution, eligibility, admission or claims about the rest of the pool.

Ordering: data/datasets/triviaqa.py:239 projects question/answer from the rc.nocontext parquet; :348 declares validation as the scored split and :353 declares train as study. data/scaffolds/qa/base.py:235 presents validation FIRST, then sampled train; data/scaffolds/qa/read.py:144 preserves validation parquet order. First five are validation file offsets 0–4, all before any train rows. The adapter's built-in 2,000-row train even-stride sample (:243; read.py:119) is irrelevant to this prefix and is not used to select these five.

Source/split: `0f7faf33a3908546c6fd5b73a660e0f8ff173c2f`; `validation`. Split=`declared`, source=`declared`, selected side=`eval`. Task sides appear in selection order below.

Installed file: `/mnt/20t/xubuqiang/datasets/triviaqa/rc.nocontext/validation-00000-of-00001.parquet` (7335321 bytes), SHA-256 `48a5005c0eb4f8a4ae5b9868644297fd5bf1e694aeb3dc9c8ab958cac0d5b201`. Presented pool=19944; this is a row/task count, not eligible coverage.

Prospective run ID: `hg-wsel-exports-20261015T081758Z-e8bf2cb83f6f-triviaqa`. Manifest: `tests/fixtures/hg_wsel/triviaqa.json`. Export directory: `/tmp/hg-wsel-exports-20261015T081758Z-e8bf2cb83f6f/triviaqa`; rows: `rows.jsonl`; row export SHA-256 `0b1b6ad5db09414a3b1316b4cd04f9b1f9c27ced671f730e85c01203b36dbf5c`. Complete selected-only file inventory digest: `3de29925f6bf457160102e756ae0427bcd351bca48977c2148360cb1f5e07e0f` (16 files).

| Position | Task ID (source index) | Native row ID | Declared side | Row SHA-256 | Scorer input SHA-256 |
| --- | --- | --- | --- | --- | --- |
| 0 | `triviaqa/validation/0` (0) | `positional` | eval | `ba45110eed574abfc61b04ef76f4857fa75a645894637bc952021c8b6c7239a6` | `9259788e9162f97b630000d5e8bb2a8c8c4cfbf9875d098c96d6f87e1d6db715` |
| 1 | `triviaqa/validation/1` (1) | `positional` | eval | `cd5e615dad714343161338ed1b20cfff937bbf44e3d3cd1d57247271b6384878` | `4401266f67049c7fc15b36d591cd00eb94d43bdb8ddaf7f81afa36521452ce0a` |
| 2 | `triviaqa/validation/2` (2) | `positional` | eval | `d6491bd758619f6ffcfcfa2fcdc8d2ccd8b40c00b02068a5760e1572fc68111a` | `da0735bc8d9cb9dc3375346c1bcc546447efe47662ec4dce9b7281ae010f57c4` |
| 3 | `triviaqa/validation/3` (3) | `positional` | eval | `8f47db55d07b2cb1870ea5a1061d9b9190a9da646e657723769d66d181c79041` | `f0d50314982d21592223c4fd48d51881677af320c3f1eca59f6c477a8e92a483` |
| 4 | `triviaqa/validation/4` (4) | `positional` | eval | `9566114d0d7ecd6abd37cc6e8740a2e5131a289634e2833e102a8d0ae9fed057` | `cb217fac1d1f8c731a2f0ae25d50b052721cacaf7d3947572cd63e734ee667be` |

Metric boundary: Retain triviaqa-alias-max-em-upstream-normalization-all-aliases-v2 (triviaqa.py:90, :160), with all accepted aliases. No score or Hub converter-execution equivalence is established.

**Remaining unmet clauses:** Immutable build/export EXECUTION provenance binding Hub 0f7faf33a3908546c6fd5b73a660e0f8ff173c2f to the loader/converter actually executed, source/license hashes, runtime/writer versions and consumed input revision/hashes; metadata-only HumanAnswers preservation/absence/redundancy, Domain/VerifiedEval/source membership, duplicates, scorer-key and denominator/aggregation review WITHOUT rows; both shared admission gates. First-five rows were read solely to satisfy this requested selection, not to satisfy the separate without-rows provenance obligation. Preserve v2 and historical identities; no ancestry/converter-name inference or production authorization.

Unchanged full next_action audited: > Obtain immutable build/export provenance binding Hub export 0f7faf33a3908546c6fd5b73a660e0f8ff173c2f to the loader/converter actually executed, source/license hashes, runtime/writer versions and consumed input revision/hashes; the inspected authoritative public record supplies ancestry/output declarations but no execution receipt. PR ancestry, identical predecessor blobs and similarly named converter artifacts do not attest execution. Review HumanAnswers preservation/absence/redundancy, Domain/VerifiedEval/source membership, duplicates, scorer-key mapping and denominator/aggregation without rows. Preserve v2 and historical identities and all shared admission gates; no production authorization.
