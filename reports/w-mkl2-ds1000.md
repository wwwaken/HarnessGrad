# DS-1000 import profile — w-mkl2

**DS-1000 is complete at the recorded source-led scorer-import payload scope**, using the upstream-compatible Gensim/SciPy pair and upstream's explicit TensorFlow/XGBoost pins. A fresh CPython 3.12.4 prefix installed retained local payloads under kernel network denial; all 19 module probes pass. This supersedes the DS-1000 partial finding in `reports/w-mkl-payloads.md` at this installation-only scope. The original host stack remains incompatible and unchanged. No shared or dataset blocker closes.

## Exact Gensim/SciPy reproduction and repair

`offline/host-original-pair.stdout.txt` records Gensim 4.3.2 and SciPy 1.13.1 on the host. The executed script's failing statement is `reproduce.py:8: import gensim`. Full raw stderr is retained, ending verbatim:

```text
ImportError: cannot import name 'triu' from 'scipy.linalg' (/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/scipy/linalg/__init__.py)
```

The dependency chain is explicit:

- `data/datasets/ds1000/verify/check.py:46` reads trusted `context.json`; `:49-51` composes the released context and `test_execution(code)`; `:61,63,76-77` invokes the upstream runner in its child.
- `/mnt/20t/xubuqiang/datasets/ds1000/_src/DS-1000-b39aab71/execution.py:49` executes that program.
- `/mnt/20t/xubuqiang/datasets/ds1000/_src/test.jsonl:937` and `:938` have `from gensim.models import Word2Vec` at **context line 3**, and `from gensim.test.utils import common_texts` at **context line 4**. Row indices are zero-based 936/937; file lines are one-based.
- Host `gensim/__init__.py:11` → `corpora/__init__.py:6` → `corpora/indexedcorpus.py:14` → `interfaces.py:19` → **`gensim/matutils.py:20: from scipy.linalg import get_blas_funcs, triu`**. SciPy 1.13.1 does not export that `triu`; the original failure is repeated in the freshly installed prefix in `offline/fresh-original-pair.*`.

The numbered adapter/checker/upstream sources are retained in `source/`; `context-flow-sites.json` retains the referenced string-definition/helper/exec lines; `source-audit.json` retains fresh source digests and only relevant import statements/locations, without questions or reference solutions. `installed-source-hashes.json` and numbered host/installed `gensim/matutils.py` prove that Gensim's import source bytes are unchanged. The repair changes the SciPy dependency, without a shim, monkeypatch or scorer edit.

A compatible pinned pair is **Gensim 4.3.2 + SciPy 1.12.0**, declared by upstream `environment.yml:9,17`. SciPy 1.12.0 exports the needed function; the retained installed `_special_matrices.py` defines it, and both Gensim root and the exact Word2Vec/common_texts imports pass. Upstream declares Python 3.10 (`environment.yml:8`); this packet independently demonstrates imports on **this host's CPython 3.12.4/Linux x86_64/glibc 2.35**, without claiming reproduction of the full upstream environment.

## TensorFlow/XGBoost: required per released context, already excluded from offered tasks

Fresh host metadata/spec inspection (`host.json`, raw `source-audit.stdout.txt`) finds no TensorFlow, tensorflow-cpu, tensorflow-gpu, tf-nightly, tf-nightly-cpu or XGBoost distribution, and no tensorflow/xgboost module spec. There was therefore no **installed host** version to pin. That is an environment absence, not proof that the released scorer can omit them.

The released import sites are real, required imports without an ImportError fallback:

- `/mnt/20t/xubuqiang/datasets/ds1000/_src/test.jsonl:380,381`: context line 3, `import tensorflow as tf`.
- JSONL lines 667–711: TensorFlow imports. Most are top-level context line 1. **JSONL line 707 (row 706)** instead imports TensorFlow at **context line 33**, then `Sequential` at **34** and `Dense` at **35**, inside the `exec_context` string. Its `test_execution` executes that string at **context line 82**. The earlier AST-only census missed this row's imports; the new audit parses constant strings without executing them.
- JSONL lines **838,839**, context line **3**: `import xgboost.sklearn as xgb`; the same import also occurs inside `exec_context` at context line **52**, executed by the helper at **68**.

The static source census finds 1000 released rows, 74 excluded and 926 offered. All 47 TensorFlow, 2 XGBoost and 2 Gensim context-dependent rows are already excluded; each has **zero offered rows**. `data/datasets/ds1000.py:102-103` names the Gensim/XGBoost exclusions, and `:109,133-147` derives TensorFlow exclusions. Thus these packages are task-conditioned requirements for the full release, rather than unconditional startup requirements for the currently offered pool. This packet changes no exclusion, eligibility rule, task, gate or admission/refusal.

To complete the prior **released-context import payload scope**, use the actual upstream declarations: **`xgboost==2.0.3`** (`environment.yml:19`) and **`tensorflow-cpu==2.16.1`** (`:22`, supplying the `tensorflow` namespace). These are explicit upstream compatibility pins, not fabricated installed-host versions. They install and import on the observed CPython 3.12 target, including the exact `xgboost.sklearn`, `Sequential` and `Dense` import statements. No model is constructed or executed.

## Retained payloads and network-denied demonstration

| Pin | Selected artifact | Recomputed SHA-256 |
| --- | --- | --- |
| `gensim==4.3.2` | `gensim-4.3.2-cp312-cp312-linux_x86_64.whl` | `c7bc5a082bfd1cb4005a445143009c64887ab9d46b6f964b787eeabc4cde8e76` |
| `scipy==1.12.0` | `scipy-1.12.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl` | `a7ebda398f86e56178c2fa94cad15bf457a218a54a35c2a7b4490b9f9cb2676c` |
| `tensorflow-cpu==2.16.1` | `tensorflow_cpu-2.16.1-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl` | `aea6520308b1f15511e69bd40b52ba9478143e6e1e8e49d57cd36410321b7b6f` |
| `xgboost==2.0.3` | `xgboost-2.0.3-py3-none-manylinux2014_x86_64.whl` | `30bd5f789fad467fd49e04e5d19e04238b931682c3951a514da5c2410b3bf59c` |

`acquire/*.{stdout.txt,stderr.txt,receipt.json}` preserve actual public PyPI acquisition commands/output. `selected-wheel-metadata.json`, `metadata/` and `offline/plan.json` preserve actual selected wheel identities, Python requirements, tags and dependency declarations. The Gensim CPython 3.12 wheel is the earlier packet's real offline-built artifact, freshly rehashed here. `existing-pins.constraints.txt` preserves the other original DS-1000 Python pins; SciPy alone changes version among those pins.

`offline.py` runs under `unshare -Urn`: only namespace-local `lo`, no routes, external connect fails with **ENETUNREACH (101)**. It creates a new local Conda cache/prefix, installs the exact retained MKL/NumPy/native payloads using `conda create --offline --no-deps`, builds a venv with `system_site_packages=False`, then installs the original DS-1000 Python lock with `pip --no-index --no-cache-dir --no-deps --require-hashes`. Negative venv controls cannot import Gensim/TensorFlow/XGBoost. Host and fresh-prefix original-pair failures are both retained before replacement.

The dependency-enabled **local-only dry-run resolver** selects the added scientific roots against the unchanged existing pins; `additions.lock` pins its newly needed packages plus SciPy with archive hashes. The installation then uses local bytes with `--no-index --no-deps --require-hashes`. `offline/retry-network.json` independently confirms network denial for the completion retry. Final `offline/retry-completed-imports.*` shows every recorded module passing with prefix-local origins, exact key versions and prefix-local MKL providers. `offline/exact-named-imports.*` passes the six exact import statements and checks installed versions against the selected scientific dependency graph's active metadata requirements. This is not a full metadata solve for the rest of DS-1000's original source-led profile.

Failed attempts remain intact: `offline-launch.*` is a collector directory-creation error before installation; `offline-launch-retry.*` includes a successful install followed by TensorFlow's missing-termcolor failure because the collector mistakenly treated packages retained for *other* profiles as installed here. `initial-additions.lock` and the failing module tracebacks are preserved. `retry.py` corrects that package-set check, installs the previously skipped dependencies, and re-imports in another denied namespace; no package or scorer source is patched. The final routine `offline.py` contains the corrected check for reproducibility.

New wheels remain at **`/tmp/hg-wmkl2-payloads-2rjzdzfz`**, with original earlier-packet artifacts at the exact paths in `reused-and-downloaded-artifacts.json`; no large duplicate wheel set is committed. **`EXTERNAL_SHA256SUMS`** pins all retained/reused candidate bytes, including unused first-download alternatives; the committed packet contains commands, metadata, local locks, source evidence and raw outputs. Replaying on another machine requires those retained payload bytes plus the external base interpreter/stdlib/OS ABI. Fresh prefixes/caches are intentionally retained for review; namespace processes exited. This packet is not a self-contained portable runtime archive.

## DS-1000 import profile completion - w-mkl2

Final DS-1000 state: **complete recorded source-led import payload profile**, using Gensim 4.3.2, SciPy 1.12.0, TensorFlow CPU 2.16.1, XGBoost 2.0.3 and the previously completed MKL/NumPy payloads. This is a compatible reconstruction; the unchanged host Gensim/SciPy pair still fails. The historical 19-dataset import inventory is now **11 complete nonempty profiles, 8 requiring no third-party payload, 0 partial**, at this explicitly limited scope (`coverage.json`). Other profiles are inherited, not rerun or broadened by this packet.

All 74 exclusions and the offered 926-row pool remain unchanged. Import success supplies no score or evidence of task API compatibility, full upstream environment reproduction, selected-task resource custody, scorer execution, portable transitive runtime/image/ABI closure, privacy/provenance or lifecycle/cleanup certification. S1/S3/S4/S5/S6 remain PARTIAL; both shared blockers and all dataset blockers/statuses/next_actions/history remain unchanged, with production_authorized=false. Only the shared scorer-offline-closure observation/evidence gains this narrow result. No benchmark scoring, model construction/execution, GPU operation, endpoint or paid call ran; no `runs/`, frozen receipt or production code changed.
