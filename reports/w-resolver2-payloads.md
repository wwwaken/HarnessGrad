# Missing resolver artifacts obtained - w-resolver2

**All three distributions were obtainable, merely absent from the previous retained corpus.** Fresh dependency-aware, network-denied resolution, hash-required installation and `pip check` pass for Jericho, Reasoning Gym and SpreadsheetBench. Removing each originally missing wheel makes its profile refuse resolution. No version substitution or dependency omission was needed.

Updated coverage is **3/3 targeted profiles; 6/6 bounded profiles when carrying forward the previous successes; 5/23 complete nonempty dataset Python metadata profiles**. The remaining **18/23** comprise eight N/A third-party profiles, nine untested profiles and Terminal-Bench's incomplete task coverage. These are metadata reconstruction fractions, not scorer/runtime closure or production authorization. Every shared and dataset blocker stays open; S1/S3/S4/S5/S6 remain PARTIAL.

## Requirements recomputed from actual source

Source pins identify acquisition versions; imports do not enforce versions. Transitive bounds below come from the actual retained wheel METADATA. Full current source and wheel-member preimages, hashes, exact line text and commands are in `tests/fixtures/hg_wresolver2/source-audit.json` and `source-audit.md`. Fresh lines supersede the previous report's now-stale repository line numbers.

| Dataset and scoring route | Actual missing-module import and requirement | Target and exact selected artifact |
| --- | --- | --- |
| Jericho: `data/datasets/jericho.py:257` launches checker; `data/datasets/jericho/verify/check.py:49` imports wrapper; `data/datasets/jericho/lib/jer_env.py:38` imports FrotzEnv. Root `jericho==3.3.1` is declared at `data/datasets/jericho.py:305`. | Preserved `tests/fixtures/hg_wresolver2/source/wheels/jericho/jericho/util.py:42` imports spaCy lazily. Jericho METADATA requires `spacy>=2.1.0`; no upper bound/extras. | spaCy 3.8.16; `spacy-3.8.16-cp312-cp312-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl`. |
| Reasoning Gym: `data/datasets/reasoning_gym.py:108` imports create_dataset; root version is at `data/datasets/reasoning_gym.py:67`. Eager package imports load game_of_life → cellpylib → matplotlib.pyplot. | Preserved `tests/fixtures/hg_wresolver2/source/wheels/matplotlib/matplotlib/contour.py:1507` imports contourpy during contour operations. Metadata chain: reasoning-gym 0.1.25 → cellpylib==2.4.0 → matplotlib>=3.0.2; retained matplotlib==3.8.4 → `contourpy>=1.0.1`. Matplotlib's exact version is a retained constraint, not a root source pin. | contourpy 1.2.0; `contourpy-1.2.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl`. |
| SpreadsheetBench: `data/datasets/spreadsheetbench.py:234` launches checker; `data/datasets/spreadsheetbench/verify/check.py:169` and `data/datasets/spreadsheetbench/verify/check.py:260` import openpyxl; root `openpyxl==3.1.2` is declared at `data/datasets/spreadsheetbench.py:285`. | Preserved `tests/fixtures/hg_wresolver2/source/wheels/openpyxl/openpyxl/xml/functions.py:36` imports et_xmlfile on the no-LXML branch. Openpyxl METADATA requires `et-xmlfile` unconditionally with no version bound/extras. | et-xmlfile 1.1.0; `et_xmlfile-1.1.0-py3-none-any.whl`. |

The experimental target remains CPython 3.12.4, SOABI `cpython-312-x86_64-linux-gnu`, Linux x86_64/glibc 2.35. Actual accepted tags are preserved in `target.json`; both manylinux artifacts intersect those tags and the pure Python artifact is accepted. The selected versions are the freshly observed installed versions, recorded in `observed-candidates.json`, and satisfy the actual bounds. They are new explicit reconstruction pins, not upstream exact requirements. All prior roots and constraints remain byte-for-byte prefixes of the new profiles.

The conditional imports remain conditional. Jericho's helper also loads or downloads `en_core_web_sm` at preserved util.py lines 44/46. That language model is outside its default Requires-Dist graph and was neither downloaded nor executed. No claim of dynamically exercising spaCy, contour operations, workbook comparison, world construction or scoring is made. In particular, a successful Python graph does not establish Jericho's optional language-model closure.

## Acquisition and independent digest evidence

The only package index queried was public PyPI. Exact versioned requests to `https://pypi.org/pypi/spacy/3.8.16/json`, `https://pypi.org/pypi/contourpy/1.2.0/json` and `https://pypi.org/pypi/et-xmlfile/1.1.0/json` each returned HTTP 200 with a compatible non-yanked wheel. Each selected `files.pythonhosted.org` artifact GET returned HTTP 200. This establishes obtainability directly; no negative claim about other indexes, Conda or caches is needed.

| Artifact | Downloaded bytes | Recomputed SHA-256, equal to PyPI's advertised digest |
| --- | ---: | --- |
| spaCy 3.8.16 wheel above | 35,496,883 | `8d0f63c3124d0a34a37e9b519d004cee1269744be07f91f843902e6c9f3e557a` |
| contourpy 1.2.0 wheel above | 303,937 | `6e739530c662a8d6d42c37c2ed52a6f0932c2d4a3e8c1f90692ad0ce1274abe0` |
| et-xmlfile 1.1.0 wheel above | 4,688 | `a2ba85d1d6a74ef63837eed693bcb89c3f752169b0e3e7ae5b16ca5e1b3deada` |

All fixture-relative paths in this report are under `tests/fixtures/hg_wresolver2/`. `index/*-VERSION.json` contains the actual PyPI bodies, `.http.json` records request/final URLs, status, headers, size and SHA-256, and `*-selection.json` records compatible exact candidates. Artifact GET records retain the full selected URL and response facts. Wheel bytes and extracted METADATA/WHEEL bytes are independently checked against those responses. `raw/wheel-sha256sum.stdout.txt` independently hashes every staged wheel; `raw/retained-target-sha256sum.stdout.txt` hashes the committed copies of the three requested wheels under `payloads/`.

The full candidate directory is `/tmp/hg-wresolver2-payloads-3pw9kdeg/wheels`: **77 wheels / 130,785,550 bytes**, with **33 new public artifact downloads**. It combines rehashed previous candidates, available inherited transitive candidates and missing default dependencies. The traversal additionally obtains fonttools and markdown-it-py and spaCy's default transitive graph; acquiring only the three first failures would not have supplied the complete graphs. Every selected version/hash and provenance source is recorded in `inputs.json`. `obtain.stdout.txt`, `obtain.stderr.txt`, `observed-candidates.json` and `graph.json` preserve collection output, candidate observations and literal marker-evaluated edges.

Acquisition is bounded to 100 artifacts, 256 MiB total payload, 64 MiB per HTTP artifact and a 45-second HTTP timeout. Only existing wheels are accepted; no sdists/builds, arbitrary substitutes, extras or models. The three requested wheels are committed. The full graph corpus remains externally retained at the recorded location; the three committed wheels alone do not constitute a portable complete-profile archive. No old wheel, fixture, frozen receipt or run ID was overwritten.

## Fresh network-denied reconstruction

`unshare -Urn python3 tests/fixtures/hg_wresolver2/probe.py` runs the real pip resolver inside a new kernel network namespace. `raw/network.json` records only loopback, no routes and a real documentation-address connect refusal with errno 101. Each profile uses a separate fresh venv without system site packages, cleared proxy/package configuration and no package cache. No model address, GPU or service endpoint is queried.

pip uses `--ignore-installed --no-index --no-cache-dir --only-binary=:all:` with dependency processing enabled, roots and constraints, local `--find-links` and a JSON selection report. Successful selections generate exact hash locks; a separate install uses `--require-hashes` and is followed by `pip check`. No `--no-deps` shortcut is used. `raw/*-pip-version.stdout.txt` records pip 24.0; `raw/runtime.json` pins the interpreter and namespace target. Each subprocess has a 180-second bound. The actual scripts and all stdout/stderr/argv/exit records are preserved.

| Profile | Dependency-aware dry run | Hash-required install | pip check | Selected distributions | Remove original missing wheel |
| --- | ---: | ---: | ---: | ---: | ---: |
| jericho | 0 | 0 | 0 | 45 | spaCy removal: exit 1 |
| reasoning_gym | 0 | 0 | 0 | 29 | contourpy removal: exit 1 |
| spreadsheetbench | 0 | 0 | 0 | 2 | et-xmlfile removal: exit 1 |

These are process exits and resolver refusals, not task scores. Each negative reconstructs with every other candidate still present after installation; `--ignore-installed` prevents the installed copy from hiding the absent wheel. The raw `negative-*.stdout.txt` outputs name the expected missing dependency and its exact constraint; stderr records `ResolutionImpossible`. `raw/cleanup.json` records removal of the fresh venv/cache/negative directories. Acquired payloads are intentionally retained. No container, image pull, benchmark scorer, submitted task program, model, GPU computation or endpoint call ran.

The source audit preserves two initial stale-line assertion failures in `source/generate-attempt1.*` and `source/generate-attempt2.*`; neither reaches a resolver or scorer. Its successful fresh-source audit is retained separately. The first packet-validation attempt expected pip's missing-distribution wording; constrained pip instead reports the missing dependency/constraint conflict on stdout and `ResolutionImpossible` on stderr. A second validator attempt treated an archive-member locator as an ordinary path. Both validator failures are preserved in the validation log; corrected checks assert the actual dependency, exact constraint and refusal, and compare ZIP members to source preimages without rerunning or altering resolver captures. No failure is converted to a zero score. The old packet's failures remain intact as historical corpus-scoped results.

## Updated denominator and every remaining gap

`coverage.py` derives `summary.json` and `dataset-coverage.json` from actual new process receipts, prior successful receipts and the unchanged registry references. Raw derived values are in `coverage.stdout.txt`. ChessBench, ScienceWorld and the one Terminal-Bench tooling profile are carried forward from w-resolver, not silently rerun.

| Scope | Updated fraction | Remaining gap |
| --- | --- | --- |
| Targeted failed profiles | **3/3** | No remaining default metadata-resolution failure in these three profiles. |
| Previous bounded profile denominator | **6/6**, previously 3/6 | Includes only one Terminal-Bench task; not six complete datasets. |
| Complete nonempty dataset Python profiles among shared references | **5/23**, previously 2/23 | ChessBench, ScienceWorld, Jericho, Reasoning Gym and SpreadsheetBench demonstrated; remaining 18/23 classified below. |
| Terminal-Bench task tooling | **1/89** | OpenSSL tooling only; other 88 task-specific bootstrap/resolver graphs remain undemonstrated. |

| Remaining dataset(s) | Reason it is absent from the complete nonempty numerator |
| --- | --- |
| alfworld | Not resolved in either packet; imported-wheel evidence does not reconstruct the default TextWorld/Jericho dependency graph. |
| ds1000 | Not resolved in either packet; broad imported-wheel/native inventories are not a complete metadata solve, and context dependencies remain separate. |
| gsm8k | Conditional QA Parquet import profile not reconstructed here; prior import-only inventory is insufficient. |
| hotpotqa | Conditional QA Parquet import profile not reconstructed here; prior import-only inventory is insufficient. |
| livecodebench | Its inspected import profile was not reconstructed by these resolver experiments; NumPy/import inventories are insufficient. |
| triviaqa | Conditional QA Parquet import profile not reconstructed here; prior import-only inventory is insufficient. |
| appworld | Existing package/image observation is not a dependency-aware reconstruction of the scorer image's metadata graph. |
| gaia | Existing snapshot/image packages and build-time pip declarations were not reconstructed as a finite local metadata graph. |
| tau_bench | Vendored scorer and image imports were not reconstructed as a finite local distribution graph. |
| terminal_bench | Only 1/89 task tooling graphs demonstrated; task-specific installers/Python/apt/runtime requirements remain. |
| bfcl_v3, bird_minidev, fever, musique, physicsquestions, sportsunderstanding, strategyqa, twowikimultihopqa | Eight N/A profiles: no third-party resolver requirement on the inspected path. They are not fabricated successful nonempty solves; interpreter/source/native/task custody remains separate. |

No evidence in this packet changes the MKL/Conda inventory, production installation or native provider compatibility. Successful default Python resolution does not certify execution-selected imports/native libraries, language models, JRE/LibreOffice, task resources, official scoring, upstream provenance, snapshot/trusted lifecycle, quotas or live controls. Source imports still consume installed bytes; no adapter adopts these new locks. The full scorer-offline-closure gate remains open with its existing next_action.

## Exact registry observation - w-resolver2

Resolver obtainability follow-up 2026-10-15 - w-resolver2: all three previously failed profiles now pass dependency-aware kernel-network-denied resolution, hash-required installation and pip check with their original roots/constraints preserved. Public PyPI supplies exact host-observed spaCy 3.8.16, contourpy 1.2.0 and et-xmlfile 1.1.0 wheels for the recorded CPython 3.12 Linux x86_64 target; actual HTTP bodies/GET records, recomputed matching digests and committed copies prove these were missing from the retained corpus rather than unobtainable. Complete default transitive graphs select 45 distributions for jericho, 29 for reasoning_gym and two for spreadsheetbench; removing each original missing wheel produces a real resolver refusal despite installed copies. Carrying forward earlier successes updates bounded profile coverage to 6/6 and complete nonempty dataset Python metadata profiles to 5/23, with 18/23 remaining: eight N/A third-party profiles, nine untested profiles and Terminal-Bench limited to 1/89 task tooling graphs. The full candidate corpus remains externally retained; these are metadata reconstruction results, not portable runtime/scorer closure, optional language-model provisioning or production adoption. Only this observed/evidence sub-scope is superseded; S1/S3/S4/S5/S6 remain PARTIAL, scorer-offline-closure and every dataset blocker remain open, and all statuses, next_actions, dataset/history records, gates and production_authorized=false remain unchanged.

Validation commands and raw output are in `reports/w-resolver2-validation.txt`. The packet validator checks actual wheel bytes and independent hashes, saved PyPI responses, accepted tags, unchanged root/constraint prefixes, active default Requires-Dist edges, real pip selections, hash installs, refusals, namespace denial, cleanup, current source citations and the exact additive-only registry diff. Full diff whitespace findings on copied upstream bytes are preserved separately; authored changes receive their own whitespace check without normalizing evidence or weakening a gate.
