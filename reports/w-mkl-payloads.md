# MKL installation payloads — w-mkl

**MKL is obtainable, including the exact recorded host build. Eight previously partial dataset import profiles are now complete; DS-1000 remains partial for three non-MKL import failures.** This extends `reports/w-wheelhouse-payloads.md`; it does not change that historical packet or close a runtime/scorer/dataset blocker.

Baseline: `bf917b3`; target CPython 3.12.4, Linux x86_64, glibc 2.35. The prior compatible wheel-tag list is re-established in `tests/fixtures/hg_wmkl/target.json`. Conda's corresponding platform is `linux-64`, with Python packages built for `py312`.

## Exact missing providers and import witnesses

The recorded evidence is `tests/fixtures/hg_wwheelhouse/installed-distributions.json:12`: distribution `mkl-service==2.4.0`, import root `mkl`, witness `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/numpy/_distributor_init.py:13: import mkl`. This is NumPy's **Conda distributor initialization**, not a direct dataset `import mkl` and not the public OpenBLAS NumPy wheel.

The newly retained numbered sources under `tests/fixtures/hg_wmkl/` make the chain explicit:

- `numpy-init.numbered.txt:127`: host `numpy/__init__.py:127` imports `_distributor_init`.
- `numpy-distributor-init.numbered.txt:13-14`: host `_distributor_init.py:13` imports `mkl`, then `:14` calls `mkl.get_version()`.
- `mkl-init.numbered.txt:49,54`: host `mkl/__init__.py` imports the native `_mklinit` and `_py_mkl_service` extensions. This namespace is supplied by **mkl-service**, not by the **mkl** native runtime distribution.
- `numpy-core-readelf.stdout.txt:4` and `mkl-init-readelf.stdout.txt:4`: both the installed NumPy core and `_mklinit` have `DT_NEEDED libmkl_rt.so.2`. Their exact ELF paths, hashes and commands are in the adjacent receipts. The **mkl** package supplies that runtime. Its declared native providers are `intel-openmp 2023.*` and `tbb 2021.*`; GCC/C++ support is also retained.

NumPy catches `ImportError` from the Python service and warns (`_distributor_init.py:15-22`); that does not supply the missing service or eliminate NumPy core's native MKL dependency. `mkl-payload-files.txt` contains native runtime files and no `site-packages/mkl/`; `mkl-service-payload-files.txt` contains the real Python namespace/extensions. No shim or relabeled wheel is used.

`profile-evidence.json` preserves the earlier observed module origins and distribution sets for all seven affected grouped profiles, including their current source paths. The shared QA startup group maps to gsm8k, conditional hotpotqa startup, and triviaqa. It does not change their stdlib comparison metrics.

## Public indexes actually checked

Every HTTP response body, headers, stderr, command array, exit code and recomputed body digest is retained in `tests/fixtures/hg_wmkl/index/`; `index-summary.json` derives compatible tags from those bodies.

| Checked URL | Actual result | Meaning |
| --- | --- | --- |
| `https://pypi.org/pypi/mkl-service/2.4.0/json` | HTTP 200; 21 artifacts; zero compatible wheels; zero sdists | Exact **PyPI** version still cannot install on this target. This is an index/version-specific limit. |
| `https://pypi.org/pypi/mkl-service/json` | HTTP 200; 11 versions, 106 artifacts; 8 host-compatible wheels; zero sdists | Alternatives exist: 2.4.2, 2.5.0, 2.5.2, 2.6.0, 2.6.1, 2.7.0, 2.7.2, 2.8.0. |
| `https://pypi.org/pypi/mkl/json` | HTTP 200; 32 versions, 106 artifacts; 28 compatible wheels; zero sdists | Native-runtime alternatives exist; this alone does not supply the Python service namespace. |
| `https://api.anaconda.org/package/anaconda/mkl-service` | HTTP 200; six exact-version Linux `py312` artifacts, builds `_1`, `_2`, `_3`, each `.conda` and `.tar.bz2` | The exact recorded `_1.conda` build is public. These `.tar.bz2` files are binary Conda packages, not sdists. |
| `https://repo.anaconda.com/pkgs/main/linux-64/` + exact filenames from `host-conda-records.json` | Complete, digest-matching transfers for 12 of 14 Conda payloads; MKL and libstdcxx transfers timed out incomplete | Public artifact requests, not hypothetical resolver availability. Failed bytes and curl exit 28 receipts are preserved in `quarantine/` and `index/`. |
| `https://api.anaconda.org/download/anaconda/mkl/2023.1.0/linux-64/mkl-2023.1.0-h213fc3f_46344.conda` and the corresponding recorded libstdcxx retry URL | Redirected HTTP 200 complete bodies; independently recomputed hashes match host package records | Both failed transfers were replaced with complete accepted artifacts; incomplete bytes never enter installation. |

The compatible alternative `mkl_service-2.4.2-0-cp312-cp312-manylinux_2_28_x86_64.whl` was also downloaded and preserved. SHA-256: `d6c46e525babf5514c5ab7b8568a81865f107142c276228416c6057b4e332928`. Its archive contains `mkl/`; its preserved METADATA declares `Requires-Dist: mkl`. It is an inspected alternative, **not installed in place of the exact host version**, and has no independent offline certification here. No sdist build or broader index search is needed after exact host artifacts succeed.

## Obtained exact payloads

All 14 Conda artifacts (219054852 bytes), the alternative wheel, their original advertised and newly computed digests, package metadata and failed-transfer evidence are committed under `tests/fixtures/hg_wmkl/`. Main payloads:

| Artifact | Recomputed SHA-256 |
| --- | --- |
| `mkl-service-2.4.0-py312h5eee18b_1.conda` | `4b83fa638e1be68f0772b9cc1b0d453fa607dd4fa1863d52ea5a04b2d8e8346b` |
| `mkl-2023.1.0-h213fc3f_46344.conda` | `74453e0d9e072ef8e60e48a734380c238f9df2cf0191ad9a2db6dbf9f8391034` |
| `intel-openmp-2023.1.0-hdb19cb5_46306.conda` | `b73c169115156c76d439211b956b3a12e69f9ad533ba46b8444693f1c9941277` |
| `tbb-2021.8.0-hdb19cb5_0.conda` | `c4667f31fd0f7ed35796f2f9b4e7f00bf2ec6ccafb67bd8fe1bd9dd488ad8f75` |
| `numpy-1.26.4-py312hc5e2394_0.conda` | `0207cc348f64b8adf828454b7b3488de082bb25c1965058b46585b4117367a11` |
| `numpy-base-1.26.4-py312h0da6c21_0.conda` | `6cbb90df64063ef66000a63e7920951abf0ec635c9c361197710c35bf47709ea` |

The other eight exact host packages are `libgcc-ng==11.2.0`, `libstdcxx-ng==11.2.0`, `libgomp==11.2.0`, `libffi==3.4.4`, `zlib==1.2.13`, `_openmp_mutex==5.1`, `_libgcc_mutex==0.1`, `blas==1.0`. Exact builds, filenames, URLs, digests and declared dependencies are in `support-artifacts.json` and independently parsed `conda-package-metadata.json`. `SHA256SUMS` covers the entire new fixture except itself and ignored bytecode; independent `sha256sum --check` output is in `reports/w-mkl-validation.txt`.

## Network-denied install/import demonstration

`offline.py` ran in `unshare -Urn`, with a fresh task-local Conda cache and seven new prefixes, followed by isolated venv setup with `system_site_packages=False`. It installed only the retained local Conda archives with `conda create --offline --no-deps`, then the earlier packet's remaining exact Python payloads with `pip --no-index --no-cache-dir --no-deps --require-hashes`. All reused wheel bytes were freshly rehashed; `reused-artifacts.json` identifies their retained external location `/tmp/hg-wwheelhouse-payloads-e5uywviu`. This packet extends that wheelhouse; it does not duplicate its roughly 3 GB of artifacts or bundle Python/stdlib/OS ABI.

`offline/network.json` and `offline/retry-import-network.json` record only namespace-local `lo`, no routes, and an external connect refused with `ENETUNREACH` (101). Proxy variables and Python/native search overrides were removed. A fresh negative-control venv could not `import mkl`. All seven positive profiles resolve `mkl`, NumPy and loaded `libmkl*`/`libiomp*` from their new prefix, not host site-packages or host MKL libraries. NumPy's installed distributor-init bytes match the recorded host hash. Runtime version reports **2023.0.1** from the **2023.1.0** Conda package, matching the independently sampled host runtime (`host-runtime-retry.json`); the two version conventions are preserved.

Initial attempts are retained: one probe wrongly required a route header when the route file was empty; the first installed-profile probes looked for `numpy.__mkl_version__` instead of `numpy._distributor_init.__mkl_version__`. The corrected probes also serialize the version dictionary's bytes as text. `retry_imports.py` rechecked the same fresh installed prefixes in another denied network namespace, without repeating installs or altering package code. Final raw outputs/command arrays are `offline/retry-import-*.{stdout.txt,stderr.txt,receipt.json}` and `final-summary.json`.

## Updated installation coverage

“Complete” means the **recorded scorer-import payload scope**, using the same source-led `--no-deps` scope as the earlier packet. It is not a full Requires-Dist resolver lock, reproduction of every host binary, selected-task scoring/resource certification or portable runtime/ABI closure.

| Dataset profile | Conda / pip install | Final import | Updated scope and remaining limitation |
| --- | --- | --- | --- |
| alfworld | 0 / 0 | 0 | Complete recorded Python/MKL import payload; native replay, Gym runtime and execution custody remain separate. |
| gsm8k | 0 / 0 | 0 | Complete recorded PyArrow startup import payload; scoring/task custody unchanged. |
| hotpotqa | 0 / 0 | 0 | Complete conditional recorded PyArrow startup import payload; data visibility and runtime unchanged. |
| triviaqa | 0 / 0 | 0 | Complete recorded PyArrow startup import payload; scoring/task custody unchanged. |
| jericho | 0 / 0 | 0 | Complete recorded Python/MKL import payload; native replay unexecuted. |
| livecodebench | 0 / 0 | 0 | Complete recorded NumPy/MKL import payload; candidate-specific imports remain unbounded. |
| reasoning_gym | 0 / 0 | 0 | Complete recorded eager-import payload; family construction/scoring/resources remain uncertified. |
| spreadsheetbench | 0 / 0 | 0 | Complete recorded Python/MKL import payload; LibreOffice/plugins/formula execution remain separate. |
| ds1000 | 0 / 0 | 1 | **Partial. MKL resolved.** Gensim 4.3.2 still cannot import `triu` from SciPy 1.13.1. TensorFlow and XGBoost remain absent; the recorded host has no versions to pin. No versions or scores invented. |

chessbench_puzzles and scienceworld retain their earlier complete Python payload status. bfcl_v3, bird_minidev, fever, musique, physicsquestions, sportsunderstanding, strategyqa and twowikimultihopqa retain no-third-party-payload-required status for their implemented paths. Thus the 19-dataset inventory now has **10 complete nonempty import payload profiles, 8 requiring no third-party payload, and 1 partial profile (DS-1000)**. No profile remains partial because MKL is unobtainable. The earlier packet's historical nine-partial statement remains preserved, superseded at this installation-only scope.

## MKL payload obtainability and offline import coverage - w-mkl

Exact host MKL payloads are publicly obtainable: mkl-service 2.4.0 py312h5eee18b_1 and mkl 2023.1.0 h213fc3f_46344, with the matching Conda NumPy build and native support, are retained with recomputed SHA-256 digests. Kernel-network-denied local installs succeed for all seven grouped profiles; final imports complete eight previously partial dataset profiles (alfworld, gsm8k, hotpotqa, jericho, livecodebench, reasoning_gym, spreadsheetbench, triviaqa). DS-1000's MKL import succeeds but its profile remains PARTIAL because Gensim/SciPy is incompatible and TensorFlow/XGBoost have no recorded installed versions. This raises the 19-dataset installation inventory to 10 complete nonempty import payload profiles, eight requiring no third-party payload, and one partial profile. It does not establish full metadata-resolved dependencies, execution-selected scorer/runtime/image/ABI custody, official scoring coverage, task resources or live controls. S1, S3, S4, S5 and S6 remain PARTIAL; scorer-offline-closure and every dataset blocker remain open. All statuses, next_actions, dataset/history records, gates and production_authorized=false are unchanged. No benchmark scoring run, model, GPU computation, endpoint call, production adapter/scoring change, runs/ edit or frozen-receipt modification occurred.
