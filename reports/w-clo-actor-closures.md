# Actor-workdir pinned scorer closure records — w-clo-actor

Source baseline: `19b700de8883360a19fe7ff9c5feb15959ce3210`. Review date: 2026-10-15.

**Disposition: `scorer-offline-closure` remains open.** There are 19 new partial local
byte-closure records; zero complete provisioned offline scorer closures are certified.
These records make the source, installed runtime/package members, and local expected-data
identities reviewable. They do not supply offline-installable runtime payloads, per-task
trusted materialization bindings, or new class-specific runtime observations.

## Scope established from the survey

The topology survey has **19 `actor-workdir` routes: 12 shared QA commands (Q) and seven
native commands (F)**. All are included, including Alfworld, BIRD Mini-Dev, ChessBench,
DS-1000, Jericho, LiveCodeBench, ScienceWorld and SpreadsheetBench in addition to the
eleven named QA adapters. AppWorld, GAIA, tau-bench and Terminal-Bench are the four
`snapshot-service` rows and are outside this inventory. ChessBench’s alternate trusted
stepwise controller is `in-process`; its default QA record does not cover that branch.
The survey predates its recorded-class fix; current controller source is independently
hashed in `common-sources.json`. Routes in this report describe source wiring, not new
executed observations. Full verbatim survey rows are preserved in each record.

Read first: `reports/w-shared-topology-survey.md`,
`reports/w-tbdep-transitive-inventory.md`, `tests/fixtures/hg_wtbdep/`,
`reports/w-net-receipts.md` and its committed evidence. The inherited dependency report
cites `hg_wtbdep/python/` and `hg_wtbdep/runtime/`, which are absent in this checkout.
Those missing fixture hashes are not reused. Existing inventory paths are leads for
new hashes of actual installed files, not a substitute for reading the bytes.

## Common interpreter, check and package custody

- `python3` currently resolves to `/mnt/8t/xubuqiang/anaconda3/bin/python3` → `/mnt/8t/xubuqiang/anaconda3/bin/python3.12`.
  Version: `3.12.4 | packaged by Anaconda, Inc. | (main, Jun 18 2024, 15:12:24) [GCC 11.2.0]`; SOABI `cpython-312-x86_64-linux-gnu`.
  Binary SHA-256: `0eb25a387ef43f21492b659f4865eae5bdaf8da30d6357097b2d9bb24873ebfb`.
- QA check entry: `data/scaffolds/qa/verify/check.py:137` (`main`),
  file SHA-256 `0840a2136787abf92d200944c94bc18060428d1be285b228695ce728b1b7b220`.
  Each QA record also resolves `base.QASpec.verifier`, gold read, adapter import,
  structured `score_prediction` and legacy `score` calls to exact source lines/hashes.
- These native files environments have no Docker image. `python3`/PATH, installed
  packages, libc/loader and host prefix are observations, not adapter-enforced locks.
- Guarded fresh imports execute only installed package imports, with networking denied
  and GPU visibility disabled. No adapter import, score call, constructor, submitted
  code, task, model, endpoint, Docker or benchmark run is performed. Preexisting
  startup/inspection packages are separated from requested package imports.
- 187 installed-distribution manifests cover observed imports plus
  recursive default metadata requirements (including TextWorld PDDL). Every existing
  metadata-enumerated member is hashed directly, excluding regenerable bytecode.
  RECORD’s claimed member hashes are never substituted for a fresh hash. A declared
  dependency superset is not a claim that every library executes in every task.
  Unlisted files, lazy/plugin selection and offline wheel payload custody remain open.
- `interpreter-files.json`, `native-files.json` and `jre-files.json` bind current
  stdlib/extension/library/JRE bytes. Native inventory is bounded by imported modules
  and existing ABI leads; it is not complete transitive OS/dlopen/plugin closure.

## Per-dataset closure table

Every row pins the implemented adapter/check bytes, interpreter observation and
source/expected-data files in the linked manifests. “Still unpinned” includes the
common gaps below in addition to the dataset-specific finding in the table.

| Dataset / class | Scoring entry reached by source route | Expected-data bytes now pinned | Still unpinned / qualification |
| --- | --- | --- | --- |
| [`alfworld`](../tests/fixtures/hg_wclo_actor/datasets/alfworld.json) / actor-workdir F | `data/datasets/alfworld/verify/check.py:131` (`main`) | [134 released game files; stripped-game recipe](../tests/fixtures/hg_wclo_actor/gold/alfworld.json) | Stripped staged game binding; native dlopen/custody; control lacks complete resources/lifecycle |
| [`bfcl_v3`](../tests/fixtures/hg_wclo_actor/datasets/bfcl_v3.json) / actor-workdir Q | `data/datasets/bfcl_v3.py:217` (`score`) | [simple/irrelevance tables + simple answers](../tests/fixtures/hg_wclo_actor/gold/bfcl_v3.json) | Official AST scorer absent; selected-index/per-task custody |
| [`bird_minidev`](../tests/fixtures/hg_wclo_actor/datasets/bird_minidev.json) / actor-workdir F | `data/datasets/bird_minidev/verify/check.py:90` (`main`) | [question table + SQL gold + 11 SQLite databases](../tests/fixtures/hg_wclo_actor/gold/bird_minidev.json) | Per-task gold.sql binding; Python/SQLite ABI enforcement |
| [`chessbench_puzzles`](../tests/fixtures/hg_wclo_actor/datasets/chessbench_puzzles.json) / actor-workdir Q | `data/datasets/chessbench_puzzles.py:309` (`score`) | [puzzles.csv with FEN and moves](../tests/fixtures/hg_wclo_actor/gold/chessbench_puzzles.json) | Wheel/runtime enforcement; stepwise is a separate class/metric |
| [`ds1000`](../tests/fixtures/hg_wclo_actor/datasets/ds1000.json) / actor-workdir F | `data/datasets/ds1000/verify/check.py:20` (`main`) | [test.jsonl context tests + four seaborn CSVs](../tests/fixtures/hg_wclo_actor/gold/ds1000.json) | Actor context authentication; upstream environment mismatch; candidate imports/cache misses |
| [`fever`](../tests/fixtures/hg_wclo_actor/datasets/fever.json) / actor-workdir Q | `data/datasets/fever.py:41` (`score, score_prediction`) | [valid.jsonl labels + evidence](../tests/fixtures/hg_wclo_actor/gold/fever.json) | Hub export has no configured digest; official execution/custody |
| [`gsm8k`](../tests/fixtures/hg_wclo_actor/datasets/gsm8k.json) / actor-workdir Q | `data/datasets/gsm8k.py:149` (`score`) | [main test + train parquet answer source](../tests/fixtures/hg_wclo_actor/gold/gsm8k.json) | Adapter numeric metric differs from upstream EM; startup PyArrow visibility |
| [`hotpotqa`](../tests/fixtures/hg_wclo_actor/datasets/hotpotqa.json) / actor-workdir Q | `data/datasets/hotpotqa.py:54` (`score, score_prediction`) | [fullwiki validation answers + supporting facts](../tests/fixtures/hg_wclo_actor/gold/hotpotqa.json) | Conditional PyArrow startup; official joint execution/custody |
| [`jericho`](../tests/fixtures/hg_wclo_actor/datasets/jericho.json) / actor-workdir F | `data/datasets/jericho/verify/check.py:84` (`main`) | [57 archive ROM members (not an eligible-task count)](../tests/fixtures/hg_wclo_actor/gold/jericho.json) | Selected official-game/seed binding; Frotz/native custody |
| [`livecodebench`](../tests/fixtures/hg_wclo_actor/datasets/livecodebench.json) / actor-workdir F | `data/datasets/livecodebench/verify/check.py:138` (`main`) | [1,055 decoded test files + metadata pool](../tests/fixtures/hg_wclo_actor/gold/livecodebench.json) | Decoded-to-shard derivation not rerun; arbitrary candidate imports |
| [`musique`](../tests/fixtures/hg_wclo_actor/datasets/musique.json) / actor-workdir Q | `data/datasets/musique.py:125` (`score, score_prediction`) | [Ans v1.0 dev answers, aliases and support](../tests/fixtures/hg_wclo_actor/gold/musique.json) | Canonical mirror verification; platform joint vs legacy mode |
| [`physicsquestions`](../tests/fixtures/hg_wclo_actor/datasets/physicsquestions.json) / actor-workdir Q | `data/datasets/physicsquestions.py:103` (`score`) | [ReWOO accepted-spelling CSV](../tests/fixtures/hg_wclo_actor/gold/physicsquestions.json) | Direct upstream metric provenance/execution; staged gold |
| [`reasoning_gym`](../tests/fixtures/hg_wclo_actor/datasets/reasoning_gym.json) / actor-workdir Q | `data/datasets/reasoning_gym.py:106` (`score`) | [pool.jsonl entries + package resources](../tests/fixtures/hg_wclo_actor/gold/reasoning_gym.json) | 0.1.25 metadata vs 0.1.19 code; family construction/lazy resources not exercised |
| [`scienceworld`](../tests/fixtures/hg_wclo_actor/datasets/scienceworld.json) / actor-workdir F | `data/datasets/scienceworld/verify/check.py:125` (`main`) | [repository fold + package JAR/tasks/object data](../tests/fixtures/hg_wclo_actor/gold/scienceworld.json) | Selected JVM/IPC lifecycle and ABI; expected result is world state |
| [`sportsunderstanding`](../tests/fixtures/hg_wclo_actor/datasets/sportsunderstanding.json) / actor-workdir Q | `data/datasets/sportsunderstanding.py:80` (`score`) | [ReWOO label CSV](../tests/fixtures/hg_wclo_actor/gold/sportsunderstanding.json) | Ambiguous-label refusal differs from historical substring rule; staged gold |
| [`spreadsheetbench`](../tests/fixtures/hg_wclo_actor/datasets/spreadsheetbench.json) / actor-workdir F | `data/datasets/spreadsheetbench/verify/check.py:296` (`main`) | [400 golden workbooks + dataset.json](../tests/fixtures/hg_wclo_actor/gold/spreadsheetbench.json) | LibreOffice/plugin closure; formula branch vs read-only mount; staged task metadata |
| [`strategyqa`](../tests/fixtures/hg_wclo_actor/datasets/strategyqa.json) / actor-workdir Q | `data/datasets/strategyqa.py:89` (`score`) | [ReWOO Yes/No CSV](../tests/fixtures/hg_wclo_actor/gold/strategyqa.json) | Vendor-source metric provenance/execution; staged gold |
| [`triviaqa`](../tests/fixtures/hg_wclo_actor/datasets/triviaqa.json) / actor-workdir Q | `data/datasets/triviaqa.py:160` (`score`) | [rc.nocontext validation + train alias source](../tests/fixtures/hg_wclo_actor/gold/triviaqa.json) | Startup PyArrow; staged alias serialization; withheld test excluded |
| [`twowikimultihopqa`](../tests/fixtures/hg_wclo_actor/datasets/twowikimultihopqa.json) / actor-workdir Q | `data/datasets/twowikimultihopqa.py:490` (`score, score_prediction`) | [dev.json + entity alias table](../tests/fixtures/hg_wclo_actor/gold/twowikimultihopqa.json) | Official-release mirror provenance; joint vs legacy binding |

## Source and expected-data manifest SHA-256s

The adapter hashes below are hashes of complete files, not functions. Native check
hashes and upstream child entry points are in each dataset record; the common QA
check hash is above. The expected-data manifest hash binds all individual full
SHA-256s, local paths, provenance pins and archive-member comparisons.

| Dataset | Adapter file SHA-256 | Expected-data manifest SHA-256 |
| --- | --- | --- |
| `alfworld` | `9a91e5f9b8a77815222996edcceb8a55feff8b194186e2f8590cfb92e04e1e91` | `8081ffb56a28da7262b3cbf8235f8b3869d3ddebbb253a4c5e2fbacd02055e61` |
| `bfcl_v3` | `de8f7efb844c39fa79632d42171d537e488f055dae7b5e1bceb583368e3bce17` | `df3ec7de414371b7785f05953a18968a10c500b92e4eed39c4d9815dfe5a62d3` |
| `bird_minidev` | `d6e26d4cf541f889a949992e823e446d52048eb5e05d99c3566bf4a95479667d` | `d108f8e1a17b5a9bf537b8ba5448e0d912d91ab048efd977e875ebc2368cb9d2` |
| `chessbench_puzzles` | `61165a5351b9068ebdac5e66f34cba1b6ed3c658ee1198ebdaf789be4e11b261` | `16edb4f7ee29a690cf104efdb2a0cdaf27db3a075b5847dcce728d87053665f9` |
| `ds1000` | `7a58535f566e58d23819cad86c0ad9b0620e16f11b33033d6645dfcb977fb9a5` | `5c308c0a1bf72930f3ea7f7dda4daee564d56fbf6a297788f0030e8d0bf497ad` |
| `fever` | `7c0cd67c7d82d9c71f2bde4c52e564f279930f6fc7f62aae4cdda5b7c27afcd0` | `a25973ac2af3c5621d2c26c08de7f01d9609b835da754a7befe5a3355d83e9fe` |
| `gsm8k` | `628dbf064bd7aa965d31b669247f3fae291de897dd17ad8c71b49c2614e630bb` | `eec033257e5379a3cb56c08a2e15911503cbd3b46545bc0b6fbf3d6f4abcf939` |
| `hotpotqa` | `1946c6cf56db9124cf1b8d4fed61eed43c61d2a4ff85f181ac8b2739946db6e1` | `f6717a7e74adf3a5f21ca34ce3339a14f6dc1b57e14f70a6c3ab41f8c0a6484a` |
| `jericho` | `3eec2472c4f6130ab7fc20fe0c7b397283247ee487831f8db2358ca6557f5074` | `f649bdb476dde1c836cf4f5970b229a180897ac3e6d0f2bd6cb2efc206e8bb00` |
| `livecodebench` | `69b06146ce29a1376f293436f9f0d050866be0d89a647f6e862cb664f7850ec2` | `f3bca9164e01cbbd3db3992e46a8fba93ade9f81e6f3cf31152df7237ab10cb3` |
| `musique` | `817af68df579bcf577c64a9613fa5b368424ee00dc4101f20ad00010c357e5f2` | `561e7e2b13feccde6ef4c442ce7bd082ec2668cec24252cb4c2252f1b7a85e69` |
| `physicsquestions` | `452d134d58a1900355112edb8dcc9837c39830c953d2d064db3b409d54c001cf` | `1ef5ca5f4ea339ae72acce5c221cbf4bd7ec370931be9ffdfaf88aedb6761657` |
| `reasoning_gym` | `fcf4be2daa187dc4d74395530bbbdaa308e317bc0173b346f7de0bb889ac7f33` | `4cd67772579d313f3426dd51992df195ec6bc58dbe6e18ca18615082b582ab70` |
| `scienceworld` | `e49b0c7ee0ddb5634214145cf7fff7726cdd1775ef7f97fb635cd47cf83f2366` | `6f1c394897e2a539b94fe083cae9c65f929f4dcdbeaca99342e88b3750e07bf6` |
| `sportsunderstanding` | `e44f856dda4c2761737ffe9d0b0b3fca59e149c1ec12e7451be33872df5d86ad` | `ae38c09c84b6c8387b99ce55c71eacc000580f81356d4685b65f22b51b787723` |
| `spreadsheetbench` | `8fdfad8f320bce041555ca3b4c8b769b79d07ad971af78f314852eb5f9799505` | `ec0b52037178eb9bc32349e8969558f072eeb284941e558095e4f7fd24c479d1` |
| `strategyqa` | `eaad45dfb944241fad84eb575882560ffcf7243de40c9d34fd0766a40c16a50a` | `2399b1791ad4fdefe013a39632ef8309980a1fd11ffc0b4fd0b1f76bf3fdd79a` |
| `triviaqa` | `c4c9e7121672f482abd5ec5527daa07d893f27bfbdcb7255841782332597413c` | `c98df922f68491e2b61ff605b4195bc047a03de15dcf96714970f6f0e11a46fb` |
| `twowikimultihopqa` | `55556cbb914e64bcdb644b5d96df6b89752a927c3b96a4b5d34f3dbbc3ceec21` | `92ae80ecb580ff0d3244543fd99e8f2436fab6b4c5dd91c0636a61262eb9867b` |

## Installed third-party imports

Full versions, METADATA/WHEEL/RECORD hashes, installed-member hashes and default
dependency graphs are linked in the dataset records. These are current local
identities; no lock file is represented as an offline payload. The following
table lists every distribution observed during the requested imports, separating
them from preexisting startup/inspection modules. Conditional startup surfaces
(PyArrow) are explicitly included; declaration-only requirements remain separate.

| Dataset(s) | Installed distributions observed in requested imports |
| --- | --- |
| `bfcl_v3`, `bird_minidev`, `fever`, `musique`, `physicsquestions`, `sportsunderstanding`, `strategyqa`, `twowikimultihopqa` | No special third-party comparison/replay import observed; BIRD still uses SQLite native ABI. |
| `alfworld` | `TatSu==5.8.3`, `alfworld==0.4.2`, `fast_downward_textworld==20.6.4`, `jericho==3.3.1`, `mementos==1.3.1`, `mkl-service==2.4.0`, `networkx==3.4.2`, `numpy==1.26.4`, `prompt-toolkit==3.0.43`, `psutil==5.9.0`, `termcolor==3.3.0`, `textworld==1.7.0`, `tqdm==4.66.4`, `wcwidth==0.8.2` |
| `chessbench_puzzles` | `chess==1.11.2` |
| `ds1000` | `Bottleneck==1.3.7`, `PyYAML==6.0.3`, `Pygments==2.15.1`, `asttokens==2.0.5`, `cffi==1.16.0`, `cloudpickle==2.2.1`, `colorama==0.4.6`, `comm==0.2.1`, `cycler==0.11.0`, `decorator==5.1.1`, `defusedxml==0.7.1`, `dill==0.4.0`, `executing==0.8.3`, `ipykernel==6.28.0`, `ipython==8.25.0`, `ipython-genutils==0.2.0`, `ipywidgets==7.8.1`, `jedi==0.18.1`, `joblib==1.4.2`, `jupyter_client==8.6.0`, `jupyter_core==5.7.2`, `kiwisolver==1.4.4`, `lz4==4.3.2`, `matplotlib==3.8.4`, `mkl-service==2.4.0`, `numexpr==2.8.7`, `numpy==1.26.4`, `nvidia-ml-py==12.575.51`, `packaging==23.2`, `pandas==2.2.2`, `parso==0.8.3`, `patsy==0.5.6`, `pickleshare==0.7.5`, `pillow==10.3.0`, `platformdirs==3.10.0`, `prompt-toolkit==3.0.43`, `psutil==5.9.0`, `pure-eval==0.2.2`, `pyarrow==23.0.0`, `pyparsing==3.0.9`, `python-dateutil==2.9.0.post0`, `pytz==2024.1`, `pyzmq==25.1.2`, `scikit-learn==1.8.0`, `scipy==1.13.1`, `seaborn==0.13.2`, `six==1.16.0`, `stack-data==0.2.0`, `statsmodels==0.14.2`, `threadpoolctl==3.6.0`, `torch==2.5.1`, `tornado==6.4.1`, `tqdm==4.66.4`, `traitlets==5.14.3`, `typing_extensions==4.15.0`, `wcwidth==0.8.2` |
| `gsm8k` | `cloudpickle==2.2.1`, `mkl-service==2.4.0`, `numpy==1.26.4`, `pyarrow==23.0.0`, `typing_extensions==4.15.0` |
| `hotpotqa` | `cloudpickle==2.2.1`, `mkl-service==2.4.0`, `numpy==1.26.4`, `pyarrow==23.0.0`, `typing_extensions==4.15.0` |
| `jericho` | `jericho==3.3.1`, `mkl-service==2.4.0`, `numpy==1.26.4` |
| `livecodebench` | `mkl-service==2.4.0`, `numpy==1.26.4` |
| `reasoning_gym` | `PyYAML==6.0.3`, `arckit==0.1.0`, `bfi==1.0.4`, `cellpylib==2.4.0`, `cffi==1.16.0`, `cycler==0.11.0`, `defusedxml==0.7.1`, `drawsvg==2.4.2`, `kiwisolver==1.4.4`, `magiccube==0.3.0`, `matplotlib==3.8.4`, `mkl-service==2.4.0`, `mpmath==1.3.0`, `numpy==1.26.4`, `packaging==23.2`, `pillow==10.3.0`, `pycosat==0.6.6`, `pyfiglet==1.0.2`, `pyparsing==3.0.9`, `python-dateutil==2.9.0.post0`, `pytz==2024.1`, `reasoning_gym==0.1.25`, `rich==15.0.0`, `six==1.16.0`, `sympy==1.13.1`, `tabulate==0.9.0`, `wcwidth==0.8.2`, `zss==1.2.0` |
| `scienceworld` | `py4j==0.10.9.9`, `scienceworld==1.2.3` |
| `spreadsheetbench` | `cffi==1.16.0`, `defusedxml==0.7.1`, `lxml==5.2.1`, `mkl-service==2.4.0`, `numpy==1.26.4`, `openpyxl==3.1.2`, `pillow==10.3.0` |
| `triviaqa` | `cloudpickle==2.2.1`, `mkl-service==2.4.0`, `numpy==1.26.4`, `pyarrow==23.0.0`, `typing_extensions==4.15.0` |

## Gold/provenance and remaining findings

- 1687 source/expected-data files are hashed,
  with no missing expected-data pattern. 611 local members were independently
  matched byte-for-byte to local provenance archives without extraction or task execution.
  Direct configured digest matches are marked individually. Archive-member equality
  establishes local extraction identity, not independent upstream authenticity.
- QA `gold.json` is inline JSON constructed by the hashed adapter/scaffold and read by
  the shared check. This inspection hashes its source data and projection code, not a
  fabricated run-specific gold file. Native staged gold.sql, stripped PDDL, task.json
  and context.json likewise require trusted selected-task bindings. No raw expected
  answers, test contents or references are copied into this fixture directory.
- Reasoning Gym family entry-point candidates and package resources are inventoried
  statically. No family constructor or `score_answer` is called. Complete runtime
  lazy-import/resource behavior is not inferred from successful package import.
- FEVER’s Hub export has a revision but no configured byte digest. This work adds a
  current local byte pin without claiming immutable export reconstruction. MuSiQue
  and 2Wiki retain their mirror-provenance qualifications. GSM8K and BFCL retain their
  explicit adapter/diagnostic metric identities, not an official-equivalence claim.

## Existing class evidence and blocker disposition

`prior-evidence.json` recomputes the identities of existing reports and ALFWorld
review copies. The ALFWorld noop result records a real `actor-workdir` verifier
with raw `score=0.0` and scorer `measured=true`, but enforcement publication is
unmeasured/non-comparable; CPU/RAM enforcement and formal lifecycle remain unknown.
It is relevant partial runtime evidence, not proof for every actor-workdir scorer.
The Terminal-Bench report provides official raw scorer/image/resource/snapshot/cleanup
observations in `snapshot-service`, with publication withheld. It is a model for
receipts and cannot be transferred across isolation classes. No old receipt is
edited, rerun, resumed or upgraded.

**Still unmet in the shared blocker’s own next_action:** complete provisioned
transitive runtime/image/ABI closures and trusted byte custody; official provenance
and execution for the required dataset/metric; class-specific resource/lifecycle/
cleanup observations and valid live offline controls before pilots. The four
snapshot/service datasets remain outside this work; their connectivity and snapshot
semantics must be retained. Comparisons still require matching known classes.
No manifest here establishes those execution requirements or licenses a pilot.

Registry change is limited to appending this partial inventory to the shared
blocker’s `observed` and adding a literal report evidence locator. Status, its full
`next_action`, every dataset/shared reference, dataset-local blocker and historical
record remain unchanged. Dataset-local changes are unwarranted because no local
blocker’s requested runtime/official-execution result was produced.

Validation commands and outputs: `reports/w-clo-actor-validation.txt`. Fixtures and
their complete SHA-256 inventory: `tests/fixtures/hg_wclo_actor/SHA256SUMS`.
