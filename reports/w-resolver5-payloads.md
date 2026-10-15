# DS1000 and bounded Terminal-Bench tooling resolved offline - w-resolver5

**17/17 bounded profiles and 13/23 complete nonempty dataset Python metadata profiles** now have demonstrations, carrying forward merged w-resolver4's 13/13 and 12/23. DS1000 adds the dataset profile; three Terminal-Bench additions are bootstrap-only. No shared or dataset blocker closes and no production execution is authorized.

## Selection and source derivation

Selection rule: work on the two remaining datasets with nonempty external Python graphs, rather than count the nine stdlib-only N/A routes. For DS1000, first derive direct and parseable-literal static import roots from **all 1000 released `code_context` fields**, preserve the declared Python 3.10 target and all environment version pins, and attempt the finite union. For Terminal-Bench, sort task IDs with a finite exact direct `pip install` declaration, skip duplicate root-pin sets, and stop at three distinct bootstrap profiles. The skipped prefix entry is fix-code-vulnerability; only build-cython-ext, headless-terminal and hf-model-inference receive new receipts. This is the executed selection rule, not a claim of external preregistration.

The primary packet is `tests/fixtures/hg_wresolver5/`; Terminal-Bench's compact subpacket is `tests/fixtures/hg_wresolver5_tb/`. `source.py`, `source.json`, `source.stdout.txt`, `context_literals.py` and `context-literals.json` retain the derivation and exact import sites/hashes. DS1000 checker `data/datasets/ds1000/verify/check.py:49` constructs the program from `code_context`; the retained upstream `execution.py` executes it. The source path, release SHA-256, actual declaration/import lines and independent `sha256sum` are in `source.json` and `raw/source-sha256sum.stdout.txt`. The audit parses only context metadata, discards other JSON fields, exports no prompt/gold/reference code or test bodies, and executes no context/candidate. There are no AST syntax failures. Arbitrary generated-candidate imports are outside this finite source-scoped reconstruction, just as arbitrary candidate behavior is outside a default dependency lock.

| Import root → distribution | First freshly derived source site |
| --- | --- |
| PIL → pillow | `test.jsonl:512`, `code_context:3` (`PIL`) |
| gensim → gensim | `test.jsonl:937`, `code_context:3` (`gensim.models`) |
| matplotlib → matplotlib | `test.jsonl:512`, `code_context:2` (`matplotlib.pyplot`) |
| numpy → numpy | `test.jsonl:1`, `code_context:2` (`numpy`) |
| pandas → pandas | `test.jsonl:1`, `code_context:1` (`pandas`) |
| scipy → scipy | `test.jsonl:351`, `code_context:3` (`scipy.stats`) |
| seaborn → seaborn | `test.jsonl:513`, `code_context:4` (`seaborn`) |
| sklearn → scikit-learn | `test.jsonl:487`, `code_context:3` (`sklearn.preprocessing`) |
| tensorflow → tensorflow-cpu | `test.jsonl:380`, `code_context:3` (`tensorflow`) |
| torch → torch | `test.jsonl:378`, `code_context:3` (`torch`) |
| xgboost → xgboost | `test.jsonl:838`, `code_context:3` (`xgboost.sklearn`) |
| yaml → PyYAML | `test.jsonl:16`, `code_context:3` (`yaml`) |

The all-context literal-string audit additionally finds `statsmodels` and `mpl_toolkits` → matplotlib, already covered by the declared union. All original declared version pins remain exact: the full root list is `profile/roots.in`. Pillow and PyYAML were unpinned imports; their candidates are freshly observed host versions, explicitly reconstruction choices rather than upstream/image version claims. `environment.yml` declares `pytorch::pytorch==2.2.0` with `pytorch::cpuonly`. The official CPU `torch==2.2.0+cpu` wheel satisfies original `==2.2.0` under PEP 440; the independent validator checks this. It preserves the CPU selector for this Python metadata mapping, without asserting Conda build/channel/native equivalence. Conda `yaml` denotes native libyaml and is **not** relabeled as a pip distribution: actual `import yaml` supplies the separate PyYAML Python root, while native libyaml custody remains a gap. The explicit pip tooling wheel is separately hash-pinned and locally seeds a fresh no-system-packages Python 3.10 venv; it is not invented as a scorer dependency.

## Exact artifacts outside the repository

DS1000 acquired **67 wheels / 914,231,609 bytes** outside git. `artifacts.json` records exact versioned index URL/status/digest, artifact URL, filename, size, recomputed SHA-256 and only the relevant METADATA/WHEEL graph fields. `raw/wheel-sha256sum.stdout.txt` independently rehashes every actual candidate. Final hashes match the exact offered index entries; real target tags, Requires-Python and active dependency markers are independently validated on the recorded CPython 3.10.12 target. The original complete pip discovery set is used; partial redundant transfers are excluded.

| Root artifact | Bytes | Recomputed SHA-256 |
| --- | ---: | --- |
| gensim-4.3.2-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl | 26,506,991 | `5e34ee6f8a318fbf0b65e6d39a985ecf9e9051febfd1221ae6255fff1972c547` |
| matplotlib-3.8.4-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl | 11,608,003 | `ecd79298550cba13a43c340581a3ec9c707bd895a6a061a78fa2524660482fc0` |
| numpy-1.26.4-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl | 18,240,889 | `ffa75af20b44f8dba823498024771d5ac50620e6915abac414251bd971b4529f` |
| pandas-1.5.3-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl | 12,062,104 | `7a0a56cef15fd1586726dace5616db75ebcfec9179a3a55e78f72c5639fa2a23` |
| pillow-10.3.0-cp310-cp310-manylinux_2_28_x86_64.whl | 4,499,372 | `b14f16f94cbc61215115b9b1236f9c18403c15dd3c52cf629072afa9d54c1cbf` |
| pyyaml-6.0.3-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl | 770,293 | `9c7708761fccb9397fe64bbc0395abcae8c4bf7b0eac081e12b809bf47700d0b` |
| scikit_learn-1.4.0-1-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl | 12,113,336 | `e98632da8f6410e6fb6bf66937712c949b4010600ccd3f22a5388a83e610cc3c` |
| scipy-1.12.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl | 38,441,046 | `5e32847e08da8d895ce09d108a494d9eb78974cf6de23063f93306a3e419960c` |
| seaborn-0.13.2-py3-none-any.whl | 294,914 | `636f8336facf092165e27924f223d3c62ca560b1f2bb5dff7ab7fad265361987` |
| statsmodels-0.14.1-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl | 10,831,895 | `c0564d92cb05b219b4538ed09e77d96658a924a691255e1f7dd23ee338df441b` |
| tensorflow_cpu-2.16.1-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl | 214,013,229 | `10daa2bda40c85f7b0ed8d036e6c0394fe24e1806bec0835b5331f8a451e182d` |
| torch-2.2.0+cpu-cp310-cp310-linux_x86_64.whl | 186,748,552 | `5f907293f5a58619c1c520380f17641f76400a136474a4b1a66c363d2563fe5e` |
| xgboost-2.0.3-py3-none-manylinux2014_x86_64.whl | 297,094,586 | `30bd5f789fad467fd49e04e5d19e04238b931682c3951a514da5c2410b3bf59c` |

Terminal-Bench independently acquires **13 unique wheels / 2,787,959 bytes**, also outside git. Exact pinned declaration lines, task test import-only AST excerpts, plugin import-only audit, wheel digests and process receipts are in its subpacket. Detailed bounded findings: `reports/w-resolver5-tb-notes.md`. Both packets include `refetch.py` scripts which refuse repository destinations and re-fetch only the recorded exact URLs, checking size and digest. DS1000's script receives a successful one-artifact flatbuffers smoke check (`refetch-smoke.json` and raw output); its complete-set default is available but was not executed as that smoke check. Terminal-Bench's script actually re-fetches and verifies its entire captured set. No wheel/package/archive, saved HTTP response body, bulk import dump or multi-MB JSON is committed.

DS1000 bounds: 150 wheels, 1610612736 bytes per candidate set, 402653184 bytes per individual exact fetch, 8 MiB per index response, 45-second socket operation timeouts; pip discovery has a 900-second subprocess bound and **post-download** count/size checks. A socket timeout is not a total wall-clock HTTP deadline and no enforced streaming pip quota is claimed. Final resolve/check/refusal subprocesses have 300-second bounds, install 600 seconds. Temporary offline venv/cache/negative roots are removed with actual cleanup receipts. Acquisition payloads and incomplete transfer evidence remain outside git, separate from runs/ and frozen receipts.

## Network denial, installation and mandatory-wheel refusal

Actual `unshare -Urn` receipts show loopback only, no external route, and external connect errno 101 (`Network is unreachable`). Each probe uses a fresh venv with system packages disabled, cleared proxy/package environment and isolated empty cache. Real pip uses `--ignore-installed --no-index --no-cache-dir --only-binary=:all:`, exact constraints and full dependency processing. No `--no-deps` is used. A dependency-aware dry-run generates the hash lock; a separate `--require-hashes` installation and `pip check` follow. The DS1000 full temporary pip report is deliberately reduced to selected graph fields plus its original digest/size; the report body is removed with the disposable workdir, not represented as a retained full report.

| Profile / target | Selected | Resolve / hash install / pip check | Required transitive wheel removed; refusal |
| --- | ---: | --- | --- |
| ds1000 / CPython 3.10.12 | 67 | 0 / 0 / 0 | flatbuffers==25.12.19; 1, ResolutionImpossible |
| build-cython-ext / CPython 3.12.4 bootstrap only | 6 | 0 / 0 / 0 | pluggy==1.6.0; 1, ResolutionImpossible |
| headless-terminal / CPython 3.12.4 bootstrap only | 11 | 0 / 0 / 0 | pluggy==1.6.0; 1, ResolutionImpossible |
| hf-model-inference / CPython 3.12.4 bootstrap only | 12 | 0 / 0 / 0 | pluggy==1.6.0; 1, ResolutionImpossible |

Each negative removes only the named required wheel, retains every other candidate, and runs **after installation** with `--ignore-installed`; installed copies cannot hide absence. DS1000 stdout names `tensorflow-cpu 2.16.1 depends on flatbuffers>=23.5.26` and exact constraint `flatbuffers==25.12.19`. Terminal-Bench stdout names `pytest 8.4.1 depends on pluggy<2 and >=1.5`. Raw stderr preserves `ResolutionImpossible`. These are refusals, not scores. No scorer, benchmark task, image/container, model, GPU, endpoint or server runs.

The Terminal-Bench target distinction is material: these are host CPython 3.12.4 **bootstrap metadata** reconstructions. Build-cython-ext's actual image declares Python 3.13/numpy and its test imports pyknotid; hf-model-inference's image declares transformers/torch/flask and Python 3.13; headless-terminal imports the task-produced headless_terminal. Those application/image/native roots remain outside the finite bootstrap proof. Build-cython shares pytest/plugin root pins with prior OpenSSL, but is a new direct-pip/task/target receipt; it is not claimed a globally new root-pin set or a complete task graph.

## Every failed or incomplete attempt

| Attempt | Exact distribution, exception or disposition | Evidence |
| --- | --- | --- |
| Initial redundant DS1000 refetch | Agent-owned acquisition process deliberately received SIGTERM; shell exit 143, not a resolver or artifact-obtainability failure. A gensim==4.3.2 redundant transfer had stalled; complete discovery wheel already existed. | `acquire.stdout.txt`, `acquire.stderr.txt`, `attempts/acquisition-correction.json`, executed initial script retained. Partial bytes remain outside git and are excluded. |
| Two initial small index digest captures | flatbuffers==25.12.19 and gast==0.7.0 index JSON were hashed before buffer flush, yielding the empty-file digest. These two captured values are invalid and never used as final index identities. | Exact old/new recomputed values in `attempts/acquisition-correction.json`; `finalize.py`, `finalize.stdout.txt` and independent `raw/index-sha256sum.stdout.txt` correct them after close. Active acquisition flushes before hashing. |
| DS1000 missing-wheel control | Required flatbuffers==25.12.19; ResolutionImpossible; exit 1. | `raw/negative.*`, omission inventory and post-install command receipts. |
| Three Terminal-Bench missing-wheel controls | Required pluggy==1.6.0; ResolutionImpossible; exit 1 for each. | Subpacket `raw/negative-*` and `results.json`. |

All final selected profiles succeed. No distribution is declared unobtainable. In particular, the CPU PyTorch artifact was checked at the official CPU index and its linked download-r2 host instead of inferring absence from the default PyPI graph. No version pin, dependency edge, admission gate or refusal is weakened. Source/native/image/production gaps below are unattempted scopes, not missing-wheel exceptions. Raw upstream metadata whitespace and pip-output blank lines are preserved; any corresponding full-diff whitespace warnings are evidence formatting, while source/report whitespace receives a separate clean check.

## Updated fraction and every remaining dataset gap

`summary.json` and raw `write-report.stdout.txt` derive arithmetic from actual successful/refusal receipts and merged w-resolver4's inherited summary. This phase adds **4 successful bounded profiles**, including **one complete finite Python metadata dataset profile**: 17/17 bounded, 13/23 complete nonempty dataset Python metadata profiles. Inherited demonstrations are carried from their merged receipts, not falsely presented as freshly rerun after the payload-history repair. Terminal-Bench has 4/89 demonstrated task tooling routes across the explicitly different targets; this is not 4 complete task/image closures. N/A datasets stay in the denominator and are never successful empty solves.

`remainder.py`, `remainder.json` and `raw/remainder-sha256sum.stdout.txt` freshly audit all N/A adapter/verifier/vendored routes and hash every Terminal-Bench task manifest, Dockerfile and verifier bootstrap. Each remaining gap is:

| Remaining dataset | Reason outside the complete nonempty numerator |
| --- | --- |
| bfcl_v3 | JSONL route uses stdlib json and local scaffolds; no nonempty third-party wheel graph to count. |
| bird_minidev | JSON/CSV/sqlite3 route uses stdlib/local scaffolds. SQLite native custody is separate; no empty solve is counted. |
| fever | Inspected JSONL/scaffold reader and local score route use stdlib; no nonempty third-party wheel solve. |
| musique | Inspected JSONL/scaffold route uses stdlib json and local helpers; no nonempty wheel solve. |
| physicsquestions | Inspected CSV route uses stdlib csv/local scaffolds; no nonempty wheel solve. |
| sportsunderstanding | Inspected CSV route uses stdlib csv/local scaffolds; no nonempty wheel solve. |
| strategyqa | Inspected CSV route uses stdlib csv/local scaffolds; no nonempty wheel solve. |
| tau_bench | Fresh verifier/CLI/vendored-domain import audit is stdlib/local only; Dockerfile declares no pip install. Interpreter/image/data custody is separate; no empty solve is counted. |
| terminal_bench | Only 4/89 task tooling routes have demonstrations across explicitly stated targets; 85 other tooling routes and full per-task image/ML/native/application graphs remain undemonstrated. Shared bootstrap pins do not transfer a success to another task. New test import gaps include build-cython-ext numpy/pyknotid, headless-terminal's task-produced headless_terminal, and hf-model-inference transformers/torch/flask image dependencies. These are unattempted scopes, not unobtainable distributions or observed ModuleNotFoundErrors. |
| twowikimultihopqa | Inspected row/scorer route uses stdlib JSON/local helpers. The Parquet witness is outside this route; no empty solve is counted. |

DS1000 is now inside the numerator **only at the finite declared/static-import Python metadata scope**. Native Conda channel/build equivalence, cpuonly/libyaml providers, interpreter/ABI/image custody, arbitrary candidate imports, external resources, official scorer compatibility/execution, provenance/privacy, quotas, snapshots, cleanup enforcement and valid live controls remain unestablished. This packet does not modify an adapter or adopt these reconstruction locks. All shared/dataset statuses, complete next_actions, dataset/history records and gates remain unchanged.

## Exact registry observation - w-resolver5

Resolver profile extension 2026-10-15 - w-resolver5: DS1000's finite declared/static-import Python metadata profile passes kernel-network-denied dependency-aware resolution, hash-required installation and pip check on CPython 3.10.12, selecting 67 distributions. A metadata-only AST pass over 1000 released code_context fields records exact JSONL/context import lines and hashes without exporting prompts, gold/reference code or task/test bodies; parseable import-bearing literal strings add no distribution outside the declared union. Original version pins are preserved. Conda pytorch==2.2.0 plus cpuonly maps explicitly to the official torch==2.2.0+cpu wheel for Python metadata only; Conda yaml/native libyaml custody remains a gap and actual import yaml is supplied by PyYAML. Removing flatbuffers==25.12.19 after installation produces ResolutionImpossible/exit 1. Three distinct selected Terminal-Bench direct-pip bootstrap profiles (build-cython-ext, headless-terminal, hf-model-inference) pass the same host CPython 3.12.4 checks, selecting 6/11/12 distributions; each missing pluggy==1.6.0 refuses. These are tooling reconstructions, not full task/image graphs. Updated cumulative scope is 17/17 bounded profiles and 13/23 complete nonempty dataset Python metadata profiles, carrying merged w-resolver4 receipts forward explicitly. Terminal-Bench has 4/89 demonstrated task tooling routes; no success is extrapolated to duplicate bootstraps. Remaining 10 datasets are nine stdlib-only N/A routes and incomplete Terminal-Bench task/image/native graphs. All payloads/index bodies/bulk dumps remain outside git; compact text receipts contain URLs, filenames, sizes, recomputed hashes and re-fetch scripts. Initial redundant acquisition was SIGTERMed (exit 143); two unflushed-small-index digest errors are preserved and independently corrected, not treated as artifact absence. No artifact is declared unobtainable. No benchmark task, official scorer, container, model, endpoint, GPU or server is executed. No shared/dataset blocker closes; all statuses, full next_actions, dataset/history records, gates and production_authorized=false remain unchanged.

Validation: `reports/w-resolver5-validation.txt`. Independent validation checks source lines/hashes, every exact external candidate, target markers/tags, every active dependency edge including extras, real process/network/refusal/cleanup receipts, coverage arithmetic, all registry evidence locators, the unchanged protected registry projection and commit file sizes. The Terminal-Bench child diff was reviewed, its validator rerun, size checked, and its safe commit cherry-picked only into this isolated worker branch; no main write occurs.
