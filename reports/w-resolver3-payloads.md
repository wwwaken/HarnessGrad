# More dataset Python profiles resolved offline - w-resolver3

**Five additional profiles pass: ALFWorld, GSM8K, HotpotQA, TriviaQA and LiveCodeBench.** Each has dependency-aware kernel-network-denied resolution, a hash-required installation, `pip check`, and a required-wheel-removal refusal. Updated coverage is **11/11 bounded profiles and 10/23 complete nonempty dataset Python profiles**, carrying forward w-resolver2's six bounded/five complete successes explicitly. This does not close a shared or dataset blocker or authorize production.

## Selection and requirements recomputed from imports

Selection rule: take the remaining actor-workdir datasets with finite adapter-level nonempty Python roots, excluding DS-1000's dynamically executed task-context graph. This selects all five datasets above before resolution. Snapshot/service profiles and Terminal-Bench task graphs remain separate. The bound is 120 candidate artifacts, 320 MiB total payload, 64 MiB per HTTP artifact, 45 seconds per HTTP request, and the previous 180-second subprocess bound. No version substitution, dependency omission, source build or package execution is used.

All packet-relative paths below are under `tests/fixtures/hg_wresolver3/`. `source-audit.json` retains full fresh source preimages, recomputed hashes, exact import/declaration lines, actual wheel METADATA/WHEEL members and host version observations. `source-audit.stdout.txt` and `raw/source-sha256sum.stdout.txt` preserve raw output. `gap-audit.json`, `gap-audit.stdout.txt` and `gap-source/` independently document the other profiles.

| Dataset | Source-derived root and actual import | Exact version scope |
| --- | --- | --- |
| alfworld | Checker imports trusted `gym_env`; `data/datasets/alfworld/lib/gym_env.py:67` imports textworld, line 68 imports textworld.gym, line 69 imports AlfredDemangler/AlfredInfos from alfworld. | Adapter declares alfworld==0.4.2 and textworld==1.7.0. Actual ALFWorld wheel METADATA requires `textworld[pddl]>=1.6.1`; TextWorld's requested pddl extra requires `fast-downward-textworld` without a bound. Exact observed planner candidate is 20.6.4. |
| gsm8k | Its QA row route reaches `data/scaffolds/qa/read.py:106` and line 107: pyarrow and pyarrow.parquet. | Adapter declares pyarrow==23.0.0 at `data/datasets/gsm8k.py:228`. |
| hotpotqa | Its `_rows()` calls `base.parquet_rows(path)`, reaching the same conditional reader imports. | Source import has no version bound. pyarrow==23.0.0 is a freshly observed host reconstruction pin, recorded explicitly; no upstream exact pin is claimed. |
| triviaqa | QA table route reaches the same conditional reader imports. | Adapter declares pyarrow==23.0.0 at `data/datasets/triviaqa.py:330`. |
| livecodebench | `data/datasets/livecodebench.py:67` imports numpy. Actual pinned upstream testing_util.py and pass_k_utils.py also import numpy; both full source preimages and AST imports are retained. | No source exact NumPy pin; numpy==1.26.4 is the freshly observed host reconstruction candidate, equal to the previous retained candidate. |

QA imports remain conditional on Parquet reading; no table, gold payload, task or scorer was executed. Actual PyArrow 23.0.0 and public NumPy 1.26.4 wheel metadata declare no default Requires-Dist dependencies, so their four independent profiles each select one distribution. Imported host Conda providers such as mkl-service are not invented as default requirements of these public wheels. Native provider and installed-byte equivalence remain separate obligations. ALFWorld's mandatory *transitive* pddl extra is preserved; this is not an optional extra silently dropped to make the profile pass. `graph.json` records marker/extra-evaluated edges, and the validator independently traverses the actual pip selection with accumulated extras. All prior candidates' versions and digests are unchanged.

## Artifacts and the obtainability check

Fresh staging contains **87 wheels / 197,615,777 bytes** at `/tmp/hg-wresolver3-payloads-mpgpd22h/wheels`. It rehashes the previous candidates and retained wheelhouse payloads and downloads exact public hashids 1.3.1 and more-itertools 10.1.0 wheels. Actual PyPI JSON bodies, selected compatible artifacts and HTTP GET records are in `index/`. `inputs.json` records every artifact's byte count, recomputed digest, metadata, target-tag intersection and provenance. `raw/wheel-sha256sum.stdout.txt` independently rehashes all staged wheels. Actual target remains CPython 3.12.4 / Linux x86_64; target SOABI/tags/interpreter digest are in `target.json`.

| Exact artifact | Bytes | Recomputed SHA-256 |
| --- | ---: | --- |
| alfworld-0.4.2-py3-none-any.whl | 356,333 | `29affbea28f6041d1e8516ed3efd6b55becd52cfca4fb9dd5c75b9d6b8a56c2f` |
| textworld-1.7.0-py3-none-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl | 4,418,558 | `ca7486cff540c4d90865c54a3465e948c2790357aa78ad64de4406387854cbc8` |
| fast_downward_textworld-20.6.4-py3-none-any.whl | 12,212,665 | `08efdf7ef0a9078a7d8e16a8baca6dcb7f585f32caca5fe045d89625397bbb8d` |
| pyarrow-23.0.0-cp312-cp312-manylinux_2_28_x86_64.whl | 47,557,396 | `b73519f8b52ae28127000986bf228fda781e81d3095cd2d3ece76eb5cf760e1b` |
| numpy-1.26.4-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl | 17,950,613 | `675d61ffbfa78604709862923189bad94014bef562cc35cf61d3a07bba02a7ed` |
| hashids-1.3.1-py2.py3-none-any.whl | 6,556 | `8bddd1acba501bfc9306e7e5a99a1667f4f2cacdc20cbd70bcc5ddfa5147c94c` |
| more_itertools-10.1.0-py3-none-any.whl | 55,824 | `64e0735fcfdc6f3464ea133afe8ea4483b1c5fe3a3d69852e6503b43a0b222e6` |

The first acquisition stopped at the exact exception `AssertionError: No compatible exact wheel: fast-downward-textworld==20.6.4; investigate other sources`. `attempts/obtain-attempt1.py`, `.stderr.txt`, `.stdout.txt` and `progress.json` preserve that attempt. The fresh versioned PyPI response offers only `fast_downward_textworld-20.6.4.tar.gz`; **this did not establish unobtainability**. Checking retained payloads and original build receipts found the exact existing wheel at `/tmp/hg-wwheelhouse-payloads-e5uywviu/fast_downward_textworld-20.6.4-py3-none-any.whl`. Its freshly recomputed digest matches the original successful build stdout. `acquisition-chain/` retains that stdout/stderr/receipt and source archive. The sdist is rehashed to `ceeed05692ac6a4023de196ca3f8cfeffe80d23070ca8fda5991b7b46f8cb752`, matching the fresh PyPI body. No new build, alternate version or invented wheel is used; no unobtainable distribution is asserted.

The inherited planner wheel advertises a pure Python tag despite containing compiled planner payloads; `raw/planner-elf-members.stdout.txt` records the archive member with actual ELF magic. Acceptance by pip here demonstrates metadata resolution for this target, not portable native compatibility. The prior Jericho dependency also retains the unexecuted optional spaCy language-model obligation described in w-resolver2.

`payloads/` commits all **ten candidates new to w-resolver2's corpus / 66,830,227 bytes**, including the planner wheel and PyArrow. `retained-targets.json` and `raw/retained-target-sha256sum.stdout.txt` bind them. NumPy and the other inherited candidates remain externally retained and rehashed; this packet's committed wheel subset alone is not a complete portable archive. Full artifact versions/hashes, including the other new TextWorld dependencies, are in `inputs.json` and `profiles/*/resolved.lock`.

## Fresh network-denied resolution and refusal

The real pip resolver runs under `unshare -Urn`. Fresh namespace receipts record only loopback, no routes and an actual external connect failure `[Errno 101] Network is unreachable`. Each profile uses its own fresh venv with system packages disabled, cleared proxy/package environment, no package cache and local wheels only. pip uses dependency processing, `--ignore-installed --no-index --no-cache-dir --only-binary=:all:`, roots and exact constraints; there is no `--no-deps`. Its JSON report generates a digest lock; a separate `--require-hashes` install is followed by `pip check`.

| Profile | Resolve exit | Install exit | pip check exit | Selected distributions | Required wheel removed; refusal exit |
| --- | ---: | ---: | ---: | ---: | --- |
| alfworld | 0 | 0 | 0 | 55 | fast-downward-textworld==20.6.4; 1 |
| gsm8k | 0 | 0 | 0 | 1 | pyarrow==23.0.0; 1 |
| hotpotqa | 0 | 0 | 0 | 1 | pyarrow==23.0.0; 1 |
| triviaqa | 0 | 0 | 0 | 1 | pyarrow==23.0.0; 1 |
| livecodebench | 0 | 0 | 0 | 1 | numpy==1.26.4; 1 |

The negative directory contains every other candidate. Negatives run after successful installation with `--ignore-installed`, so ambient/previously installed copies cannot hide the missing wheel. Raw stdout names the exact root/constraint or `textworld[pddl] 1.7.0 depends on fast-downward-textworld; extra == "pddl"`; stderr preserves `ResolutionImpossible`. These are resolver/process outcomes, not benchmark scores.

The initial probe completed ALFWorld/GSM8K and HotpotQA's positive checks, then raised `FileExistsError` because two QA negatives shared the same directory name. Its exact traceback, partial results, installed-process receipts and successful cleanup are preserved. A separate fresh namespace/venv experiment completes HotpotQA, TriviaQA and LiveCodeBench using dataset-specific negative directories; raw labels are `retry-*`. `results-complete.json` combines only the two completed first-pass profiles and three completed second-pass profiles. No old capture, run ID or frozen receipt was resumed or overwritten. Both fresh venv/cache/negative roots are removed, with cleanup receipts. Staged acquisition payloads remain intentionally retained. No model endpoint/server, GPU work, container, scorer or task ran.

## Updated coverage and every remaining gap

`coverage.py` derives the counts in `summary.json`, `dataset-coverage.json` and raw `coverage.stdout.txt` from actual final process receipts and inherited successes.

| Scope | Fraction | Meaning |
| --- | --- | --- |
| New selected profiles | **5/5** | Complete at the finite source-scoped Python metadata profile level, including mandatory transitive extras. |
| Cumulative bounded profiles | **11/11** | Prior 6/6 carried forward plus these five; includes one Terminal-Bench tooling profile. |
| Complete nonempty dataset Python profiles among unchanged shared references | **10/23** | Prior five plus alfworld, gsm8k, hotpotqa, triviaqa and livecodebench. |
| Terminal-Bench task tooling | **1/89** | Only the previous OpenSSL tooling profile; other 88 graphs remain undemonstrated. |

The remaining **13/23** are **nine N/A**, **three untested nonempty profiles**, and **one incomplete Terminal-Bench dataset**. The denominator remains 23; N/A cases never become fabricated successful empty solves.

| Remaining dataset(s) | Exact reason for absence from the complete nonempty numerator |
| --- | --- |
| ds1000 | Checker constructs/executes task `code_context`; a host imported-wheel inventory does not derive all context requirements. Fresh upstream environment.yml targets Python 3.10 and Conda channel-qualified PyTorch/CPU packages plus pip tensorflow-cpu, differing from this CPython 3.12 target. No faithful full metadata solve was attempted; no missing-artifact claim. |
| appworld | Verifier imports AppWorld from its separate scorer image. Checked-in service Dockerfile is Python 3.11-slim, declares appworld==0.1.3.post1 and uvicorn<1, then invokes the AppWorld CLI installer. Image-matching complete metadata and installer-output reconstruction remains unperformed; these finite roots are not claimed unobtainable. |
| gaia | Upstream scorer directly imports NumPy; Python 3.12-slim task-image Dockerfile declares numpy, openpyxl, pillow, requests, beautifulsoup4 and lxml, plus separate native apt dependencies. Preparation additionally imports pyarrow.parquet. A source-scoped scorer/image/preparation graph and image-matching candidate versions remain unreconstructed; no missing-artifact claim. |
| terminal_bench | Fresh source scan retains 89 task manifests, Dockerfiles and verifier scripts. Different scripts use uvx, pip, uv pip and native apt dependencies. Prior OpenSSL tooling resolves one graph; 88 other task/bootstrap/image-specific graphs remain undemonstrated. |
| tau_bench | Corrected N/A: fresh AST audit of 40 vendored verifier/CLI/tool Python files yields 134 import records and zero third-party absolute imports. Dynamic tool imports stay within the two vendored domains. Python 3.11-slim Dockerfile copies lib and declares no pip install. No nonempty external wheel requirement exists on this inspected route; source/image/runtime custody remains separate. |
| bfcl_v3, bird_minidev, fever, musique, physicsquestions, sportsunderstanding, strategyqa, twowikimultihopqa | Prior eight N/A inspected paths carried forward unchanged: no third-party resolver requirement. Interpreter/source/native/task custody is not established by an empty metadata graph. |

Full source preimages, exact line text, hashes and reasons for the first five rows are in `gap-audit.json`. No new failed final profile remains. The initial acquisition assertion and probe exception above remain explicit failed attempts, neither counted as successful profiles nor converted to scores. Source imports still consume installed bytes; adapters do not adopt these reconstruction locks. Default Python metadata closure does not certify native providers, models, JRE/LibreOffice, selected resources, upstream provenance, official execution, trusted lifecycle, quotas, cleanup enforcement or live controls. S1/S3/S4/S5/S6 remain PARTIAL. No shared or dataset blocker is closed.

## Exact registry observation - w-resolver3

Resolver profile extension 2026-10-15 - w-resolver3: five additional finite source-scoped dataset Python profiles (alfworld, gsm8k, hotpotqa, triviaqa, livecodebench) pass dependency-aware kernel-network-denied resolution, hash-required installation and pip check, selecting 55/1/1/1/1 distributions respectively; required-wheel removal produces five real resolver refusals. Actual import sites and wheel METADATA derive the roots, including ALFWorld's mandatory transitive textworld[pddl] extra. The exact fast-downward-textworld 20.6.4 wheel was found in retained successful build payloads and freshly rehashed after the public-wheel-only acquisition assertion; no unobtainability claim, version substitution or dependency omission is made. Updated scope is 11/11 bounded profiles and 10/23 complete nonempty dataset Python metadata profiles, carrying prior evidence forward explicitly. The remaining 13/23 are nine N/A inspected routes (Tau-Bench newly source-audited as stdlib/vendored only), three untested image/context profiles (appworld, ds1000, gaia), and Terminal-Bench's incomplete task coverage (1/89 tooling graphs). Fresh failures, source preimages, actual HTTP bodies/digests, real missing-wheel refusals and cleanup receipts are preserved. No task, scorer, container, model, GPU or endpoint was executed; no runtime/native/image closure or production authorization follows. All shared/dataset statuses, next_actions, references, history and gates remain unchanged; S1/S3/S4/S5/S6 remain PARTIAL.

Validation: `reports/w-resolver3-validation.txt`; packet validator checks byte custody, all metadata edges/extras, exact source citations, real process/refusal/cleanup receipts, denominator arithmetic and a semantic assertion that only this shared blocker's additive observed/evidence fields changed.
