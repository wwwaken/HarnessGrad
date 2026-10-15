# Gaia and AppWorld Python profiles resolved offline - w-resolver4

**13/13 bounded profiles and 12/23 complete nonempty dataset Python profiles** now have demonstrations, carrying forward w-resolver3's 11/11 and 10/23. This packet adds Gaia and AppWorld at the same finite source-scoped Python metadata level. It closes no shared or dataset blocker and authorizes no production execution.

## Selection and requirement derivation

Selection rule: take the remaining nonempty profiles with finite declared scorer/service/image/preparation Python roots and an available matching interpreter minor version. This selects Gaia and AppWorld. Audit the other eleven remaining routes rather than manufacturing nonempty N/A solves or treating a dynamic per-task mixed-package-manager graph as a complete import-derived requirement. `selection.json` records the rule and its timing; it does not pretend to be a preregistration.

All packet-relative paths are under `tests/fixtures/hg_wresolver4/`. `source-audit.json` and `source/` retain fresh source preimages, hashes and exact AST import/declaration lines. `source-audit.stdout.txt` and `raw/source-sha256sum.stdout.txt` preserve raw output.

| Dataset | Actual source route and requirement | Exact candidate policy |
| --- | --- | --- |
| gaia | `data/datasets/gaia/verify/check.py:72` imports the upstream scorer; its retained `source/external/gaia/scorer.py:6` imports NumPy. `data/datasets/gaia/Dockerfile:16` targets Python 3.12; line 22 declares numpy, openpyxl, pillow, requests, beautifulsoup4, lxml. `data/datasets/gaia/prepare.py:113` conditionally imports pyarrow.parquet. All seven are included. | Bare source roots use freshly observed host versions, recorded in `observed-gaia.json`; these are reconstruction candidates, not claimed upstream exact pins or installed image versions. CPython 3.12.4. |
| appworld | `data/datasets/appworld/verify/check.py:44` imports AppWorld. `data/datasets/appworld/service.py:13`–15 import fastapi, munch and AppWorld. `data/datasets/appworld/Dockerfile:3` targets Python 3.11; line 4 declares appworld==0.1.3.post1 and uvicorn<1; line 5 invokes CLI install. Actual AppWorld METADATA requires fastapi, munch and uvicorn transitively; none is omitted. | Keep the exact source AppWorld pin and uvicorn bound. A 180-second wheel-only pip discovery on CPython 3.11.15 yields candidate versions; each exact wheel is then independently re-fetched using captured versioned PyPI JSON, rehashed, and frozen in constraints. No alternate root version, sdist, source build or dependency omission. |

The shipped `appworld/cli.py:112` dispatches to `install_package` for `--no-repo`; `appworld/install.py:42`–73 unpacks local application/test bundles, without installing another distribution or fetching source. The packet retains these exact wheel members and the unpack/decrypt implementation. `installer-audit.py` independently decodes only `.source/apps.bundle` as source and parses its AST without importing AppWorld: `installer-audit.stdout.txt` records 60 application source modules and their seven external import roots (faker, fastapi, inflection, munch, polyfactory, pydantic, sqlalchemy), all supplied by the resolved default dependency graph. The package-tests bundle is neither decrypted nor read. This source inspection resolves the uncertainty about additional installer package downloads for metadata scope; it does not execute the CLI or certify installed source/image/runtime equivalence.

## Exact artifacts and custody

Fresh acquisition stages 93 target-specific candidate wheels / 108,681,283 bytes: Gaia has 13 / 75,854,183 bytes; AppWorld has 80 / 32,827,100 bytes. `inputs-gaia.json`, `inputs-appworld.json`, `target-*.json`, `metadata/`, `metadata-appworld/`, `index/` and `index-appworld/` retain names, versions, actual METADATA/WHEEL members, interpreter hashes/tags, HTTP bodies/GET receipts and freshly recomputed digests. Independent `raw/*wheel-sha256sum.stdout.txt` files rehash every candidate. Public artifact tag intersections and dependency markers use each actual target interpreter, rather than the host target for both.

| Root artifact | Bytes | Recomputed SHA-256 |
| --- | ---: | --- |
| numpy-1.26.4-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl | 17,950,613 | `675d61ffbfa78604709862923189bad94014bef562cc35cf61d3a07bba02a7ed` |
| openpyxl-3.1.2-py2.py3-none-any.whl | 249,985 | `f91456ead12ab3c6c2e9491cf33ba6d08357d802192379bb482f1033ade496f5` |
| pillow-10.3.0-cp312-cp312-manylinux_2_28_x86_64.whl | 4,514,536 | `ff61bfd9253c3915e6d41c651d5f962da23eda633cf02262990094a18a55371a` |
| requests-2.32.2-py3-none-any.whl | 63,902 | `fc06670dd0ed212426dfeb94fc1b983d917c4f9847c863f313c9dfaaffb7c23c` |
| beautifulsoup4-4.12.3-py3-none-any.whl | 147,925 | `b80878c9f40111313e55da8ba20bdba06d8fa3969fc68304167741bbf9e082ed` |
| lxml-5.2.1-cp312-cp312-manylinux_2_28_x86_64.whl | 4,939,879 | `f0a1bc63a465b6d72569a9bba9f2ef0334c4e03958e043da1920299100bc7c08` |
| pyarrow-23.0.0-cp312-cp312-manylinux_2_28_x86_64.whl | 47,557,396 | `b73519f8b52ae28127000986bf228fda781e81d3095cd2d3ece76eb5cf760e1b` |
| appworld-0.1.3.post1-py3-none-any.whl | 625,317 | `db77f8003982502383a50fa2974983894bd1c54f64e2fd3f7e1540d5edd037eb` |
| uvicorn-0.27.1-py3-none-any.whl | 60,809 | `5c89da2f3895767472a35556e539fd59f7edbe9b1e9c0e1c99eebeadc61838e4` |

`payloads/` commits 87 files / 59,711,006 bytes new to the committed fixture corpus. `retained-targets.json` maps all 93 candidate locations to either these payloads or 6 byte-identical prior committed fixture locations, all independently rehashed. The new packet plus those explicit prior fixture locations supplies both complete candidate sets; this packet alone is not claimed to be a standalone wheel archive. Temporary acquisition staging is intentionally retained; fresh offline venv/cache/negative roots are removed with cleanup receipts.

Bounds: at most 120 wheels and 320 MiB payload per profile, 64 MiB per HTTP wheel, 8 MiB per index body, 45 seconds per HTTP request and 180 seconds per subprocess. Exact reacquisition enforces the byte bounds. Initial wheel-only discovery has the subprocess bound and checks count/bytes afterward; it is not presented as an enforced pip download quota. All experiments are sequential; no model endpoint is called.

## Real network-denied resolution and refusal

Each final probe runs under `unshare -Urn` in a fresh namespace. Actual receipts show only loopback, no external routes, and an external connect failure `[Errno 101] Network is unreachable`. Each fresh venv disables system packages. Proxy/package environment and caches are cleared. Real pip uses `--ignore-installed --no-index --no-cache-dir --only-binary=:all:`, local candidate wheels, source roots and exact constraints with full dependency processing. There is no `--no-deps`. A JSON dry-run report generates the hash lock; an independent `--require-hashes` installation is followed by `pip check`.

| Profile / interpreter | Resolve | Hash install | pip check | Selected | Required wheel removed; refusal |
| --- | ---: | ---: | ---: | ---: | --- |
| gaia / CPython 3.12.4 | 0 | 0 | 0 | 13 | et-xmlfile==1.1.0; exit 1 |
| appworld / CPython 3.11.15 | 0 | 0 | 0 | 80 | munch==4.0.0; exit 1 |

Both negatives retain every other candidate and run after installation with `--ignore-installed`; an installed copy cannot hide the absent wheel. Raw stdout names `openpyxl 3.1.2 depends on et-xmlfile` and `appworld 0.1.3.post1 depends on munch<5.0.0 and >=4.0.0`, with their exact constraints. Raw stderr records `ResolutionImpossible`. `results-complete.json` contains only the completed Gaia capture and fresh AppWorld retry. No task, scorer, benchmark score, container, model/server or GPU operation occurs.

## Every failed attempt and obtainability limit

| Attempt | Exact exception or missing distribution | Disposition |
| --- | --- | --- |
| First AppWorld offline probe | `subprocess.CalledProcessError`: venv ensurepip command exited 1. | `probe-appworld.stderr.txt` preserves the wrapper traceback and `raw/appworld-cleanup.json` confirms removal. No resolver was reached. |
| Fresh bootstrap diagnostic | `ModuleNotFoundError: No module named 'encodings'`, fatal `init_fs_encoding` failure; the copied relocatable binary searched `/install/lib/python3.11`. | `raw/appworld-ensurepip-diagnostic.stderr.txt` preserves actual stderr. A new symlink-based venv locates the original interpreter correctly; explicit ensurepip, resolution and all final checks succeed. No standard-library wheel is invented. Diagnostic cleanup is retained. |
| Auxiliary Python 3.11 packaging-tool query | `ModuleNotFoundError: No module named 'packaging'`. | `raw/appworld-tooling-packaging-check.stderr.txt` is retained. Acquisition uses pip’s already available vendored packaging for target tags/markers; this is tool support, not an AppWorld dependency alteration. |
| Intentional Gaia/AppWorld wheel removals | Required `et-xmlfile==1.1.0` / `munch==4.0.0`; `ResolutionImpossible`, exit 1. | Expected refusals, retained as real negative outcomes, never scores or failed-final-profile zeros. |

Two independent-validator defects are also preserved in `attempts/validator-*.stderr.txt`: an `AssertionError` for sqlalchemy2-stubs==0.0.2a38 because the checker did not honor its existing exact prerelease constraint, and a `FileNotFoundError` for the retry runtime label. Validation now derives prerelease admission from the exact constraint accepted by pip; no requirement/gate changed. The runtime error exposed an in-session capture naming mistake: the executed retry wrote network/runtime/cleanup under the first attempt labels. `capture-recovery.json` and `recover-captures.stdout.txt` disclose it. Successful retry bytes were moved unchanged to distinct labels. The first attempt network/cleanup were recovered verbatim from the two retained original tool-output records; its overwritten pre-resolution runtime had never been exported and is unavailable. No replacement was fabricated. The failed first attempt is not counted; the successful retry has complete actual runtime/network/process/cleanup receipts. The executed retry recipe is retained, and the active recipe fixes the labels. No runs or frozen receipts were touched.

No final selected profile fails and no distribution is declared unobtainable. The earlier MKL and three resolver-wheel reversals make a public-index-only absence insufficient evidence. This packet checks retained exact candidates and independently re-fetches exact public AppWorld artifacts; all selected artifacts were obtained. DS1000 and the remaining Terminal-Bench graphs are unattempted under their distinct scope, so no missing distribution, exception or unobtainability conclusion is assigned to them.

## Updated fraction and each remaining gap

`coverage.py` derives `summary.json`, `dataset-coverage.json` and raw `coverage.stdout.txt` from actual process receipts, unchanged registry references, and w-resolver3's explicit inherited successes: new 2/2; cumulative 13/13 bounded profiles; 12/23 complete nonempty dataset Python metadata profiles. Terminal-Bench remains 1/89 tooling graphs. N/A cases remain in the denominator and are never counted as successful empty solves.

`remainder-audit.json` embeds fresh source preimages, exact file/line/text citations, hashes, generator source and independent sha256sum output for all eleven remaining datasets. `remainder-audit.stdout.txt` preserves raw commands, facts and output. The current Terminal-Bench task manifest/Dockerfile/test-script hashes match w-resolver3; no task payload or task context is read.

| Remaining dataset | Exact reason outside the complete nonempty numerator |
| --- | --- |
| ds1000 | Checker constructs and executes task `code_context`; a complete import-derived per-context requirement graph is absent. Upstream environment.yml targets Python 3.10, Conda `pytorch::cpuonly` / `pytorch::pytorch==2.2.0` and pip `tensorflow-cpu==2.16.1`, rather than an unchanged CPython 3.12 wheel graph. A faithful mapping/target and context-source derivation are required; no acquisition/resolve attempted, no missing-artifact claim. |
| terminal_bench | Each task chooses its own image and `/tests/test.sh`, with distinct Python/native/bootstrap graphs. The audit rehashes all 89 task manifests, Dockerfiles and verifier scripts. Only prior OpenSSL tooling is demonstrated (1/89); 88 others and full per-image roots remain undemonstrated. No new task resolution or missing-artifact claim. |
| tau_bench | N/A: fresh AST audit of 40 verifier/CLI/vendored-tool files finds 134 imports and zero third-party absolute imports. Dynamic domains are vendored; Python 3.11 Dockerfile declares no pip install. No nonempty wheel solve exists on this route. |
| bfcl_v3 | N/A: inspected JSONL route uses stdlib json/local scaffolds. |
| bird_minidev | N/A: inspected route uses stdlib json/csv/sqlite3/local scaffolds; SQLite native custody is separate. |
| fever | N/A: inspected JSONL route uses scaffold stdlib json reader. |
| musique | N/A: inspected JSONL route uses stdlib json/local scaffolds. |
| physicsquestions | N/A: inspected CSV route uses stdlib csv/local scaffolds. |
| sportsunderstanding | N/A: inspected CSV route uses stdlib csv/local scaffolds. |
| strategyqa | N/A: inspected CSV route uses stdlib csv/local scaffolds. |
| twowikimultihopqa | N/A: inspected JSON route uses stdlib json; its Parquet witness is outside this row/scorer route. |

The nine N/A routes do not establish interpreter/source/native custody. Default Python metadata closure does not establish installed-image byte equivalence, native providers, CLI execution, models, selected resources, provenance, official scorer execution, trusted verifier/lifecycle, quotas, cleanup enforcement or live controls. No adapter adopts these reconstruction locks. All shared/dataset statuses, next actions, references, historical receipts and gates remain unchanged; S1/S3/S4/S5/S6 remain PARTIAL.

## Exact registry observation - w-resolver4

Resolver profile extension 2026-10-15 - w-resolver4: Gaia and AppWorld each pass dependency-aware kernel-network-denied resolution, hash-required installation and pip check, selecting 13/80 distributions respectively. Removing et-xmlfile==1.1.0 or munch==4.0.0 produces two real resolver refusals after installation with --ignore-installed. Requirements are recomputed from exact scorer/service/image/preparation import and declaration sites; AppWorld uses the Python 3.11 target, and its bundled application source/installer receives static inspection without executing AppWorld or reading the package-tests bundle. The initial copied-interpreter venv failure (CalledProcessError; diagnostic ModuleNotFoundError: encodings) and successful fresh symlink-venv retry are preserved. An in-session receipt naming error is disclosed: first-attempt network/cleanup are recovered verbatim from exported tool stdout, its overwritten pre-resolution runtime is unavailable, and the successful retry retains complete actual receipts. Updated scope is 13/13 bounded profiles and 12/23 complete nonempty dataset Python metadata profiles, carrying w-resolver3 forward explicitly. Remaining 11/23 are nine N/A routes, DS1000's dynamic task-context/mixed Python 3.10 Conda graph, and incomplete Terminal-Bench coverage (1/89 prior tooling graphs). Every remaining reason has fresh source/hash evidence. No artifact is declared unobtainable, no source pin is substituted and no dependency is omitted. No task, scorer, container, model, GPU or endpoint executes; installed-image/source/native/runtime equivalence and production authorization remain unestablished. All shared/dataset statuses, next_actions, references, history and gates remain unchanged; S1/S3/S4/S5/S6 remain PARTIAL.

Validation: `reports/w-resolver4-validation.txt`. The packet validator checks artifact custody, HTTP/tag/METADATA/marker/extra edges, exact source and decoded application import citations, real final/failed/refusal/cleanup receipts, coverage arithmetic, all evidence locators, and a semantic assertion that only this shared blocker’s additive observed/evidence fields changed.
