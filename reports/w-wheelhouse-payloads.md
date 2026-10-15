# Offline scorer installation payloads — w-wheelhouse

Source baseline: `56adfafb72461bb88c4c1668e45b1c6c8ae54fba`. Scope: the 19 surveyed actor-workdir / QA-command datasets. No production adapter/scoring logic changes; no benchmark task, scorer invocation, model, GPU computation, JVM launch or model-endpoint call.

## Payload-only coverage — w-wheelhouse

**Complete nonempty Python scorer-import installation profiles: chessbench_puzzles and scienceworld. Eight implemented scorers need no third-party distribution payload. Nine current-host import profiles remain partial. S1 remains PARTIAL and scorer-offline-closure remains open.** This is installation evidence, not an offline runtime/scorer certification or dataset-blocker closure.

The retained wheelhouse is `/tmp/hg-wwheelhouse-payloads-e5uywviu`. Acquisition/build/install receipts and manifests are committed under `tests/fixtures/hg_wwheelhouse/`; the binary payloads are retained **outside git** at that path. The evidence directory alone is not a portable wheelhouse archive. The user requested either artifacts or acquisition receipts; this delivers the receipts plus the local retained artifacts.

120 exact-version distribution requests comprise 102 source-led imported Python distributions, 12 Torch import-time native providers and six separate build-only tools. 119 distributions were obtained; only `mkl-service==2.4.0` has no compatible wheel/sdist in the checked versioned PyPI response. All 11 obtained sdists were built into exact-version wheels with networking denied. The final wheelhouse has 130 accepted source/wheel artifacts, 3110412863 bytes. Python hashlib and the independent `sha256sum` command recomputed their digests; wheel filenames, METADATA versions/names and host-compatible tags were checked. Failed/truncated transfers are excluded from accepted artifacts.

### How dependency scope was determined

Current source is read independently in `source-imports.json`, with file hashes and exact import statement lines. The earlier `hg_wclo_actor` records are path leads, not an authoritative dependency list. `audit.py` follows the current scorer roots and performs fresh package-only imports in new network namespaces, without importing adapters or running tasks. `installed-distributions.json` maps every Python distribution to source file+line witnesses; `audit/*.stdout.json` preserves actual loaded modules and errors. The audit includes the released DS-1000 scoring contexts, because `check.py:27-30` composes them and upstream `execution.py:49` executes them. `ds1000-context-imports.json` preserves only import statements with JSONL/context line locations, not questions, answers or complete task contexts.

Shared QA verification imports the staged adapter at `data/scaffolds/qa/verify/check.py:217` and dispatches structured/legacy scoring at `:238`/`:242`. `data/scaffolds/qa/base.py:438` calls `ensure()`, and `:209`/`:229` reach row loading. The helper, prediction, aggregation and evidence-scoring modules use the standard library. Import-time row-loading is disclosed separately from the comparison metric. No prospective BFCL official AST dependencies, actor tool packages, Reasoning Gym judge extras, arbitrary candidate imports or blanket environment metadata closure are vendored.

### Per-dataset source and installation coverage

“Complete” below means Python distribution payload coverage for the inspected import path only. It does not include base Python/stdlib, OS ABI, JRE, LibreOffice, selected-family/task behavior or execution custody.

| Dataset | Current source reason for third-party scoring imports | Payload coverage |
| --- | --- | --- |
| `alfworld` | `data/datasets/alfworld/verify/check.py:62,159` → `data/datasets/alfworld/lib/gym_env.py:67-69`: TextWorld/Gym and ALFWorld replay wrappers; imported transitive packages listed below. | Partial: obtainable replay packages install/import; host MKL service artifact missing. |
| `bfcl_v3` | `data/datasets/bfcl_v3.py:69,217`: local name-only diagnostic scorer through stdlib QA scaffold; no official AST scorer import. | No third-party payload required for implemented diagnostic; official-scorer gap unchanged. |
| `bird_minidev` | `data/datasets/bird_minidev/verify/check.py:90`: direct stdlib SQLite execution/comparison; current checker import statements are in source-imports.json. Upstream psycopg2 is not imported by this path. | No third-party payload required; Python/SQLite ABI remains separate. |
| `chessbench_puzzles` | `data/datasets/chessbench_puzzles.py:25,309`: `import chess` and strict/upstream replay comparison. | Complete Python import payload: chess==1.11.2, built from exact sdist, offline install/import and pip check pass. |
| `ds1000` | `data/datasets/ds1000/verify/check.py:27-30,38-42,54`: trusted context plus candidate passed to released runner; upstream execution.py:49 executes it. Context census supplies each import’s JSONL and context line. Numeric/scientific libraries and Torch are scorer-context dependencies, not inferred from actor setup. | Partial: installed-version artifacts and native providers acquired; TensorFlow/XGBoost have no installed version to pin; Gensim/SciPy incompatibility persists. |
| `fever` | `data/datasets/fever.py:11-12,27,41`: local stdlib `fever_is_strictly_correct` / evidence scaffold. | No third-party payload required. |
| `gsm8k` | `data/datasets/gsm8k.py:257` → `:95-96` → `data/scaffolds/qa/read.py:106-107`: PyArrow startup before data-path failure; comparison at gsm8k.py:149 is stdlib. | Partial current-host startup set; public-wheel startup install/import succeeds, host MKL payload missing. |
| `hotpotqa` | `data/datasets/hotpotqa.py:104` → `:60-62` → `data/scaffolds/qa/read.py:106-107`: PyArrow startup conditional on data visibility; local comparison at :37/:54 is stdlib. | Partial conditional current-host startup set; same public-wheel profile succeeds. |
| `jericho` | `data/datasets/jericho/verify/check.py:45` → `data/datasets/jericho/lib/jer_env.py:40`: `from jericho import FrotzEnv`; installed jericho.py imports NumPy. | Partial current-host set; Jericho/NumPy wheels install/import, host MKL payload missing. Native replay not run. |
| `livecodebench` | `data/datasets/livecodebench/verify/check.py:86,191` imports pinned upstream `testing_util.py:13` and `pass_k_utils.py:1`, both NumPy. Exact upstream paths/hashes in source-imports.json. | Partial current-host set; public NumPy wheel install/import succeeds, host MKL payload missing. Candidate-specific imports unbounded. |
| `musique` | `data/datasets/musique.py:25,116,125,140`: stdlib answer/support comparison, prediction helper and aggregation contract. | No third-party payload required. |
| `physicsquestions` | `data/datasets/physicsquestions.py:47-50,103`: csv/re and stdlib QA scaffold. | No third-party payload required. |
| `reasoning_gym` | `data/datasets/reasoning_gym.py:108,114-115`: `create_dataset` and library score_answer. Installed reasoning_gym/__init__.py:5-20 eagerly imports all family categories. | Partial current-host set; public profile install/import succeeds; host MKL payload missing, selected-family execution/resources not certified. |
| `scienceworld` | `data/datasets/scienceworld/verify/check.py:59` → `data/datasets/scienceworld/lib/scw_env.py:125`: ScienceWorldEnv. Installed scienceworld/scienceworld.py:9 imports py4j.java_gateway. | Complete Python import payload: scienceworld==1.2.3 and py4j==0.10.9.9. Offline install/import and pip check pass; JVM closure separate. |
| `sportsunderstanding` | `data/datasets/sportsunderstanding.py:38-41,80`: csv/re and stdlib QA scaffold. | No third-party payload required. |
| `spreadsheetbench` | `data/datasets/spreadsheetbench/verify/check.py:165,256`: `import openpyxl`; installed openpyxl/compat/numbers.py:9 imports optional NumPy; lxml/Pillow/defusedxml/cffi load on the observed host import path. | Partial current-host Python set; public profile install/import succeeds, host MKL payload missing; LibreOffice/plugins remain separate. |
| `strategyqa` | `data/datasets/strategyqa.py:41-45,89`: csv/re/string and stdlib QA scaffold. | No third-party payload required. |
| `triviaqa` | `data/datasets/triviaqa.py:359` → `:240` → `data/scaffolds/qa/read.py:106-107`: PyArrow startup; alias comparison at triviaqa.py:160 is stdlib. | Partial current-host startup set; same public-wheel profile succeeds, host MKL payload missing. |
| `twowikimultihopqa` | `data/datasets/twowikimultihopqa.py:74-82,480,490,507`: stdlib answer/entity/support comparison, prediction and aggregation helpers. | No third-party payload required. |

### Exact observed Python distribution sets

These are the source-led fresh-import observations, not all installed packages or a claim that every package executes for every selected task. Full versions, source witnesses and per-dataset artifact mappings are in `installed-distributions.json` and `dataset-payloads.json`. The eight empty sets are bfcl_v3, bird_minidev, fever, musique, physicsquestions, sportsunderstanding, strategyqa and twowikimultihopqa.

- **alfworld:** `alfworld==0.4.2`, `fast-downward-textworld==20.6.4`, `jericho==3.3.1`, `mementos==1.3.1`, `mkl-service==2.4.0`, `networkx==3.4.2`, `numpy==1.26.4`, `prompt-toolkit==3.0.43`, `psutil==5.9.0`, `tatsu==5.8.3`, `termcolor==3.3.0`, `textworld==1.7.0`, `tqdm==4.66.4`, `wcwidth==0.8.2`.
- **chessbench_puzzles:** `chess==1.11.2`.
- **ds1000:** `asttokens==2.0.5`, `bcrypt==3.2.0`, `boto3==1.42.49`, `botocore==1.42.49`, `bottleneck==1.3.7`, `brotli==1.2.0`, `certifi==2024.6.2`, `cffi==1.16.0`, `chardet==4.0.0`, `charset-normalizer==2.0.4`, `cloudpickle==2.2.1`, `colorama==0.4.6`, `comm==0.2.1`, `cryptography==42.0.5`, `cycler==0.11.0`, `decorator==5.1.1`, `defusedxml==0.7.1`, `dill==0.4.0`, `executing==0.8.3`, `gensim==4.3.2`, `idna==3.7`, `ipykernel==6.28.0`, `ipython==8.25.0`, `ipython-genutils==0.2.0`, `ipywidgets==7.8.1`, `jedi==0.18.1`, `jmespath==1.0.1`, `joblib==1.4.2`, `jupyter-client==8.6.0`, `jupyter-core==5.7.2`, `kiwisolver==1.4.4`, `lz4==4.3.2`, `matplotlib==3.8.4`, `mkl-service==2.4.0`, `numexpr==2.8.7`, `numpy==1.26.4`, `nvidia-ml-py==12.575.51`, `packaging==23.2`, `pandas==2.2.2`, `parso==0.8.3`, `patsy==0.5.6`, `pickleshare==0.7.5`, `pillow==10.3.0`, `platformdirs==3.10.0`, `prompt-toolkit==3.0.43`, `psutil==5.9.0`, `pure-eval==0.2.2`, `pyarrow==23.0.0`, `pygments==2.15.1`, `pyopenssl==24.0.0`, `pyparsing==3.0.9`, `pysocks==1.7.1`, `python-dateutil==2.9.0.post0`, `pytz==2024.1`, `pyyaml==6.0.3`, `pyzmq==25.1.2`, `requests==2.32.2`, `s3transfer==0.16.0`, `scikit-learn==1.8.0`, `scipy==1.13.1`, `seaborn==0.13.2`, `simplejson==4.1.1`, `six==1.16.0`, `smart-open==5.2.1`, `stack-data==0.2.0`, `statsmodels==0.14.2`, `threadpoolctl==3.6.0`, `torch==2.5.1`, `tornado==6.4.1`, `tqdm==4.66.4`, `traitlets==5.14.3`, `typing-extensions==4.15.0`, `unicodedata2==15.1.0`, `urllib3==2.2.2`, `wcwidth==0.8.2`, `zstandard==0.22.0`, `nvidia-cublas-cu12==12.4.5.8`, `nvidia-cuda-cupti-cu12==12.4.127`, `nvidia-cuda-nvrtc-cu12==12.4.127`, `nvidia-cuda-runtime-cu12==12.4.127`, `nvidia-cudnn-cu12==9.1.0.70`, `nvidia-cufft-cu12==11.2.1.3`, `nvidia-curand-cu12==10.3.5.147`, `nvidia-cusolver-cu12==11.6.1.9`, `nvidia-cusparse-cu12==12.3.1.170`, `nvidia-nccl-cu12==2.21.5`, `nvidia-nvjitlink-cu12==12.4.127`, `nvidia-nvtx-cu12==12.4.127`.
- **gsm8k / hotpotqa (conditional) / triviaqa startup:** `cloudpickle==2.2.1`, `mkl-service==2.4.0`, `numpy==1.26.4`, `pyarrow==23.0.0`, `typing-extensions==4.15.0`.
- **jericho:** `jericho==3.3.1`, `mkl-service==2.4.0`, `numpy==1.26.4`.
- **livecodebench:** `mkl-service==2.4.0`, `numpy==1.26.4`.
- **reasoning_gym:** `arckit==0.1.0`, `bfi==1.0.4`, `cellpylib==2.4.0`, `cffi==1.16.0`, `cycler==0.11.0`, `defusedxml==0.7.1`, `drawsvg==2.4.2`, `kiwisolver==1.4.4`, `magiccube==0.3.0`, `matplotlib==3.8.4`, `mkl-service==2.4.0`, `mpmath==1.3.0`, `numpy==1.26.4`, `packaging==23.2`, `pillow==10.3.0`, `pycosat==0.6.6`, `pyfiglet==1.0.2`, `pyparsing==3.0.9`, `python-dateutil==2.9.0.post0`, `pytz==2024.1`, `pyyaml==6.0.3`, `reasoning-gym==0.1.25`, `rich==15.0.0`, `six==1.16.0`, `sympy==1.13.1`, `tabulate==0.9.0`, `wcwidth==0.8.2`, `zss==1.2.0`.
- **scienceworld:** `py4j==0.10.9.9`, `scienceworld==1.2.3`.
- **spreadsheetbench:** `cffi==1.16.0`, `defusedxml==0.7.1`, `lxml==5.2.1`, `mkl-service==2.4.0`, `numpy==1.26.4`, `openpyxl==3.1.2`, `pillow==10.3.0`.

## Obtainable and missing artifacts

`index/mkl-service.json` is the preserved actual https://pypi.org/pypi/mkl-service/2.4.0/json response. It has old CPython wheel tags (through cp310) and no sdist; none matches this CPython 3.12 Linux x86_64 target. **No usable target artifact was obtained from that index.** This is an index-scoped finding, not a claim that every possible private/Conda source was exhausted. The host is a Conda build; no new version or reconstructed host wheel is substituted. Its missing payload keeps all nine NumPy-bearing current-host profiles partial.

DS-1000 has further context-selected gaps: static released context imports include TensorFlow and XGBoost, but `pip show tensorflow xgboost` reports neither installed (`absent-context-packages.txt`). There is no installed exact version to acquire, and this work does not invent one. The census is an import surface, not proof that every listed helper executes for every task. Installed Gensim 4.3.2 raises `ImportError: cannot import name 'triu' from 'scipy.linalg'` against installed SciPy 1.13.1; the exact Gensim sdist builds successfully, but matching version payloads do not repair compatibility.

The first DS-1000 public-wheel import failed on `libcudart.so.12` / `libcublas.so.*`. Source `torch/__init__.py:285,289-325,366` explicitly loads twelve native providers with ctypes during import. `native_providers.py` obtains those **installed exact versions**, rather than adding unused Torch extras or a different CPU build. Nine transfers succeeded first time; three returned truncated HTTP-200 bodies. `truncated-downloads.json` preserves their wrong lengths/recomputed prefix hashes and quarantine paths. `retry_downloads.py` obtained complete replacements, matching both recomputed SHA-256 and advertised lengths; no prefix is accepted. No native CUDA library is evidence of GPU computation.

All other requested installed-version distributions have accepted artifacts. Build-only additions are setuptools==82.0.0, wheel==0.43.0, cmake==3.29.6, setuptools-scm==8.1.0, cppy==1.2.1 and pkgconfig==1.5.5. The latter four are explicitly chosen, versioned build-tool payloads required by sdist build declarations/errors, not claimed installed scorer versions. Initial missing-CMake/missing-build-helper failures and the LZ4 wrong-version wheel attempt remain in `offline/build-*` and `built-artifacts.json`; only the successful exact-version retries enter the wheelhouse. Locally built native wheels keep their actual `linux_x86_64` tags; they are not relabeled manylinux.

## Network-denied installation demonstration

Executed commands (raw command arrays, exit codes, stdout and stderr are in `offline/`):

```sh
python3 tests/fixtures/hg_wwheelhouse/audit.py
python3 tests/fixtures/hg_wwheelhouse/refine_witnesses.py
python3 tests/fixtures/hg_wwheelhouse/obtain.py
python3 tests/fixtures/hg_wwheelhouse/supplement.py
unshare -Urn python3 tests/fixtures/hg_wwheelhouse/offline.py build
unshare -Urn python3 tests/fixtures/hg_wwheelhouse/offline.py build-retry
unshare -Urn python3 tests/fixtures/hg_wwheelhouse/offline.py install
python3 tests/fixtures/hg_wwheelhouse/native_providers.py
python3 tests/fixtures/hg_wwheelhouse/retry_downloads.py
unshare -Urn python3 tests/fixtures/hg_wwheelhouse/torch_retry.py
python3 tests/fixtures/hg_wwheelhouse/validate.py
```

Install work uses new venvs with `system_site_packages=False`, `--no-index --no-cache-dir --no-deps --require-hashes --find-links=<retained wheelhouse>`, and empty CUDA visibility. A new user+network namespace has an empty routing table, only loopback in the namespace-local interface query, and an attempted connection to documentation-only address 198.51.100.1:443 returns `ENETUNREACH` (errno 101). Therefore the result does not rely solely on pip flags or disabled proxy settings. The first build’s interface list came from host-mounted sysfs and is explicitly not used to assert namespace-local devices; later receipts use socket.if_nameindex(). Namespace route/connect observations are preserved for both builds and both installation stages.

`--no-deps` is intentional: only imports justified by this scorer path are installed, rather than unused CLI/actor/extras or all upstream metadata declarations. This is not a complete upstream Requires-Dist resolver lock. The two complete nonempty profiles also pass `pip check` without missing declared requirements.

| Fresh-venv profile | Offline pip install | Import-only check |
| --- | --- | --- |
| `chessbench_puzzles` | exit 0 | exit 0 |
| `scienceworld` | exit 0 | exit 0 |
| `livecodebench-public-numpy` | exit 0 | exit 0 |
| `qa-parquet-public-wheels` | exit 0 | exit 0 |
| `jericho-public-wheels` | exit 0 | exit 0 |
| `alfworld-partial-public-wheels` | exit 0 | exit 0 |
| `reasoning_gym-partial-public-wheels` | exit 0 | exit 0 |
| `spreadsheetbench-partial-public-wheels` | exit 0 | exit 0 |
| `ds1000-partial-public-wheels` | exit 0 | exit 1 |
| DS-1000 native-provider retry in its previously fresh venv | exit 0 | exit 1; per-module output preserves remaining errors |

The successful import-only profiles run no scoring calls or replay constructors. DS-1000 initial/retry failures are not scores. Torch's repaired import does not certify any task operation, model execution or selected runtime closure. Compatible public NumPy/PyArrow wheels are new install artifacts, not the original Conda wheel bytes or MKL provider. A successful public-wheel subset therefore does not certify the nine host closures.

## Imported Python packages: current source witnesses

Every imported Python distribution has at least one freshly read source import witness. One is printed below; all witnesses, loaded-module paths and source hashes are retained in the machine-readable evidence. A static witness plus package-only import observation is not execution-selected task custody. Absolute site-packages paths refer to the inspected host, not vendored task inputs.

| Distribution | Source file+line witness |
| --- | --- |
| `alfworld==0.4.2` | `data/datasets/alfworld/lib/gym_env.py:69`: `from alfworld.agents.environment.alfred_tw_env import AlfredDemangler, AlfredInfos` |
| `arckit==0.1.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/reasoning_gym/arc/arc_agi.py:5`: `import arckit` |
| `asttokens==2.0.5` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/executing/executing.py:412`: `from asttokens import ASTTokens` |
| `bcrypt==3.2.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/cryptography/hazmat/primitives/serialization/ssh.py:43`: `from bcrypt import kdf as _bcrypt_kdf` |
| `bfi==1.0.4` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/reasoning_gym/code/bf.py:5`: `import bfi` |
| `boto3==1.42.49` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/smart_open/s3.py:17`: `import boto3` |
| `botocore==1.42.49` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/boto3/docs/__init__.py:15`: `from botocore.docs import DEPRECATED_SERVICE_NAMES` |
| `Bottleneck==1.3.7` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/bottleneck/__init__.py:1`: `from bottleneck.benchmark.bench import bench` |
| `brotli==1.2.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/urllib3/response.py:24`: `import brotli` |
| `cellpylib==2.4.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/reasoning_gym/algorithmic/game_of_life.py:6`: `import cellpylib as cpl` |
| `certifi==2024.6.2` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/botocore/httpsession.py:96`: `from certifi import where` |
| `cffi==1.16.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/PIL/Image.py:119`: `import cffi` |
| `chardet==4.0.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/pygments/lexer.py:212`: `import chardet` |
| `charset-normalizer==2.0.4` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/requests/__init__.py:48`: `from charset_normalizer import __version__ as charset_normalizer_version` |
| `chess==1.11.2` | `data/datasets/chessbench_puzzles.py:25`: `import chess` |
| `cloudpickle==2.2.1` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/cloudpickle/__init__.py:1`: `from cloudpickle.cloudpickle import *` |
| `colorama==0.4.6` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/IPython/terminal/interactiveshell.py:864`: `import colorama` |
| `comm==0.2.1` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/ipykernel/comm/comm.py:10`: `import comm.base_comm` |
| `cryptography==42.0.5` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/OpenSSL/_util.py:6`: `from cryptography.hazmat.bindings.openssl.binding import Binding` |
| `cycler==0.11.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/matplotlib/pyplot.py:54`: `from cycler import cycler` |
| `decorator==5.1.1` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/IPython/core/formatters.py:19`: `from decorator import decorator` |
| `defusedxml==0.7.1` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/PIL/Image.py:63`: `from defusedxml import ElementTree` |
| `dill==0.4.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/torch/utils/_import_utils.py:36`: `import dill` |
| `drawsvg==2.4.2` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/arckit/vis.py:1`: `import drawsvg` |
| `executing==0.8.3` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/IPython/core/ultratb.py:798`: `from executing.executing import NotOneValueFound` |
| `fast_downward_textworld==20.6.4` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/textworld/envs/pddl/logic/__init__.py:9`: `import fast_downward` |
| `gensim==4.3.2` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/gensim/parsing/preprocessing.py:26`: `from gensim import utils` |
| `idna==3.7` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/requests/models.py:401`: `import idna` |
| `ipykernel==6.28.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/IPython/__init__.py:101`: `from ipykernel.embed import embed_kernel as real_embed_kernel` |
| `ipython==8.25.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/comm/base_comm.py:186`: `from IPython import get_ipython` |
| `ipython-genutils==0.2.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/ipywidgets/widgets/interaction.py:26`: `from ipython_genutils.py3compat import string_types, unicode_type` |
| `ipywidgets==7.8.1` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/seaborn/widgets.py:6`: `from ipywidgets import interact, FloatSlider, IntSlider` |
| `jedi==0.18.1` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/IPython/core/completer.py:250`: `import jedi` |
| `jericho==3.3.1` | `data/datasets/jericho.py:133`: `import jericho.game_info as info` |
| `jmespath==1.0.1` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/boto3/docs/utils.py:15`: `import jmespath` |
| `joblib==1.4.2` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/sklearn/utils/parallel.py:12`: `import joblib` |
| `jupyter_client==8.6.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/ipykernel/connect.py:12`: `import jupyter_client` |
| `jupyter_core==5.7.2` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/jupyter_client/channels.py:12`: `from jupyter_core.utils import ensure_async` |
| `kiwisolver==1.4.4` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/matplotlib/_layoutgrid.py:20`: `import kiwisolver as kiwi` |
| `lxml==5.2.1` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/networkx/readwrite/graphml.py:165`: `import lxml.etree as lxmletree` |
| `lz4==4.3.2` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/joblib/compressor.py:18`: `import lz4` |
| `magiccube==0.3.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/reasoning_gym/cognition/rubiks_cube.py:6`: `from magiccube.cube import Cube, CubeMove, CubeMoveType` |
| `matplotlib==3.8.4` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/cellpylib/ca_functions.py:1`: `import matplotlib.pyplot as plt` |
| `mementos==1.3.1` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/textworld/logic/__init__.py:21`: `from mementos import memento_factory, with_metaclass` |
| `mkl-service==2.4.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/numpy/_distributor_init.py:13`: `import mkl` |
| `mpmath==1.3.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/sympy/__init__.py:22`: `import mpmath` |
| `networkx==3.4.2` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/textworld/generator/graph_networks.py:7`: `import networkx as nx` |
| `numexpr==2.8.7` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/pandas/core/computation/engines.py:113`: `import numexpr as ne` |
| `numpy==1.26.4` | `data/datasets/livecodebench.py:65`: `import numpy as np` |
| `nvidia-ml-py==12.575.51` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/torch/cuda/__init__.py:61`: `import pynvml` |
| `openpyxl==3.1.2` | `data/datasets/spreadsheetbench/verify/check.py:165`: `import openpyxl` |
| `packaging==23.2` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/PIL/Image.py:701`: `from packaging.version import parse as parse_version` |
| `pandas==2.2.2` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/networkx/algorithms/centrality/group.py:344`: `import pandas as pd` |
| `parso==0.8.3` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/jedi/api/__init__.py:13`: `import parso` |
| `patsy==0.5.6` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/statsmodels/base/_constraints.py:363`: `from patsy import DesignInfo` |
| `pickleshare==0.7.5` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/IPython/core/interactiveshell.py:41`: `from pickleshare import PickleShareDB` |
| `pillow==10.3.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/matplotlib/animation.py:36`: `from PIL import Image` |
| `platformdirs==3.10.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/jupyter_core/paths.py:22`: `import platformdirs` |
| `prompt-toolkit==3.0.43` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/IPython/terminal/debugger.py:13`: `from prompt_toolkit.application import create_app_session` |
| `psutil==5.9.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/ipykernel/kernelbase.py:39`: `import psutil` |
| `pure-eval==0.2.2` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/stack_data/core.py:17`: `from pure_eval import Evaluator, is_expression_interesting` |
| `py4j==0.10.9.9` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/scienceworld/scienceworld.py:9`: `from py4j.java_gateway import JavaGateway, GatewayParameters, launch_gateway, CallbackServerParameters` |
| `pyarrow==23.0.0` | `data/scaffolds/qa/read.py:106`: `import pyarrow as pa` |
| `pycosat==0.6.6` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/reasoning_gym/logic/contrib/logic_puzzle/sat_utils.py:9`: `import pycosat` |
| `pyfiglet==1.0.2` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/reasoning_gym/cognition/figlet_fonts.py:6`: `import pyfiglet` |
| `Pygments==2.15.1` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/IPython/core/oinspect.py:55`: `from pygments import highlight` |
| `pyOpenSSL==24.0.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/urllib3/contrib/pyopenssl.py:43`: `import OpenSSL.SSL` |
| `pyparsing==3.0.9` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/matplotlib/_fontconfig_pattern.py:15`: `from pyparsing import (` |
| `PySocks==1.7.1` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/urllib3/contrib/socks.py:44`: `import socks` |
| `python-dateutil==2.9.0.post0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/botocore/compat.py:31`: `from dateutil.tz import tzlocal` |
| `pytz==2024.1` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/pandas/core/dtypes/dtypes.py:22`: `import pytz` |
| `PyYAML==6.0.3` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/numpy/__config__.py:113`: `import yaml` |
| `pyzmq==25.1.2` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/comm/base_comm.py:18`: `from zmq.eventloop.zmqstream import ZMQStream` |
| `reasoning_gym==0.1.25` | `data/datasets/reasoning_gym.py:108`: `from reasoning_gym import create_dataset` |
| `requests==2.32.2` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/pyarrow/util.py:241`: `import requests` |
| `rich==15.0.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/arckit/data.py:6`: `from rich import print` |
| `s3transfer==0.16.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/boto3/compat.py:21`: `from s3transfer.manager import TransferConfig` |
| `scienceworld==1.2.3` | `data/datasets/scienceworld/lib/scw_env.py:125`: `from scienceworld import ScienceWorldEnv` |
| `scikit-learn==1.8.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/sklearn/__check_build/__init__.py:52`: `from sklearn.__check_build._check_build import check_build` |
| `scipy==1.13.1` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/gensim/utils.py:36`: `import scipy.sparse` |
| `seaborn==0.13.2` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/seaborn/_base.py:14`: `from seaborn._core.data import PlotData` |
| `simplejson==4.1.1` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/requests/compat.py:48`: `import simplejson as json` |
| `six==1.16.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/asttokens/asttokens.py:20`: `import six` |
| `smart-open==5.2.1` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/gensim/utils.py:37`: `from smart_open import open` |
| `stack-data==0.2.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/IPython/core/ultratb.py:104`: `import stack_data` |
| `statsmodels==0.14.2` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/seaborn/regression.py:11`: `import statsmodels` |
| `sympy==1.13.1` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/networkx/algorithms/polynomials.py:153`: `import sympy` |
| `tabulate==0.9.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/reasoning_gym/logic/contrib/logic_puzzle/generate.py:12`: `from tabulate import tabulate` |
| `TatSu==5.8.3` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/multiprocessing/util.py:476`: `from test import support` |
| `termcolor==3.3.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/alfworld/agents/environment/alfred_tw_env.py:6`: `from termcolor import colored` |
| `textworld==1.7.0` | `data/datasets/alfworld/lib/gym_env.py:67`: `import textworld` |
| `threadpoolctl==3.6.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/numpy/lib/utils.py:65`: `from threadpoolctl import threadpool_info` |
| `torch==2.5.1` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/scipy/_lib/array_api_compat/common/_helpers.py:38`: `import torch` |
| `tornado==6.4.1` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/cloudpickle/cloudpickle.py:635`: `from tornado import gen` |
| `tqdm==4.66.4` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/alfworld/agents/environment/alfred_tw_env.py:5`: `from tqdm import tqdm` |
| `traitlets==5.14.3` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/IPython/core/alias.py:27`: `from traitlets.config.configurable import Configurable` |
| `typing_extensions==4.15.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/IPython/core/completer.py:261`: `from typing_extensions import TypedDict, NotRequired, Protocol, TypeAlias, TypeGuard` |
| `unicodedata2==15.1.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/charset_normalizer/utils.py:2`: `import unicodedata2 as unicodedata` |
| `urllib3==2.2.2` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/botocore/awsrequest.py:18`: `import urllib3.util` |
| `wcwidth==0.8.2` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/IPython/terminal/ptutils.py:11`: `from wcwidth import wcwidth` |
| `zss==1.2.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/reasoning_gym/code/codeio.py:7`: `import zss` |
| `zstandard==0.22.0` | `/mnt/8t/xubuqiang/anaconda3/lib/python3.12/site-packages/urllib3/response.py:29`: `import zstandard as zstd` |

## Pinned artifact identities

The following are accepted payloads only. `manifest.json` binds every download filename to its **actual full source URL**, versioned index JSON URL/response hash, HTTP metadata, installed WHEEL/direct_url observations, host-compatible tags, length and independently computed digest. `built-artifacts.json` binds generated wheels to source URL/hash, command, build logs and exact WHEEL tags. `payload-index.json` unifies them; `sha256sum.command.json` preserves the exact independent command and `sha256sum.payloads.txt` its raw output. All URLs came from preserved PyPI responses. Source archives have no platform tag. Host-compatible public tags are not an identity claim for the original Conda distribution artifact.

| Distribution / role | Obtained or built filename | Actual artifact tags | Recomputed SHA-256 |
| --- | --- | --- | --- |
| `alfworld==0.4.2` / scoring-import | `alfworld-0.4.2-py3-none-any.whl` | `py3-none-any` | `29affbea28f6041d1e8516ed3efd6b55becd52cfca4fb9dd5c75b9d6b8a56c2f` |
| `arckit==0.1.0` / scoring-import | `arckit-0.1.0-py3-none-any.whl` | `py3-none-any` | `5a22619309d2c29b04796eadf2a58792e563d6b811ee021e5d8ca97880ebbe80` |
| `asttokens==2.0.5` / scoring-import | `asttokens-2.0.5-py2.py3-none-any.whl` | `py2-none-any, py3-none-any` | `0844691e88552595a6f4a4281a9f7f79b8dd45ca4ccea82e5e05b4bbdb76705c` |
| `bcrypt==3.2.0` / scoring-import | `bcrypt-3.2.0-cp36-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.manylinux_2_24_x86_64.whl` | `cp36-abi3-manylinux2014_x86_64, cp36-abi3-manylinux_2_17_x86_64, cp36-abi3-manylinux_2_24_x86_64` | `a0584a92329210fcd75eb8a3250c5a941633f8bfaf2a18f81009b097732839b7` |
| `bfi==1.0.4` / scoring-import | `bfi-1.0.4-py3-none-any.whl` | `py3-none-any` | `d58a10b1f3ba2c7cfd9a9ebba3756455850a0cf9e63223c67e88438676c28579` |
| `boto3==1.42.49` / scoring-import | `boto3-1.42.49-py3-none-any.whl` | `py3-none-any` | `99e1df4361c3f6ff6ade65803c043ea96314826134962dd3b385433b309eb819` |
| `botocore==1.42.49` / scoring-import | `botocore-1.42.49-py3-none-any.whl` | `py3-none-any` | `1c33544f72101eed4ccf903ebb667a803e14e25b2af4e0836e4b871da1c0af37` |
| `Bottleneck==1.3.7` / scoring-import | `Bottleneck-1.3.7.tar.gz` | `sdist (no platform tag)` | `e1467e373ad469da340ed0ff283214d6531cc08bfdca2083361a3aa6470681f8` |
| `brotli==1.2.0` / scoring-import | `brotli-1.2.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl` | `cp312-cp312-manylinux2014_x86_64, cp312-cp312-manylinux_2_17_x86_64` | `072e7624b1fc4d601036ab3f4f27942ef772887e876beff0301d261210bca97f` |
| `cellpylib==2.4.0` / scoring-import | `cellpylib-2.4.0.tar.gz` | `sdist (no platform tag)` | `e23ff7b5f647c23958748727c899b4e57b667c9f18cbc66d7577dbfaab3729ef` |
| `certifi==2024.6.2` / scoring-import | `certifi-2024.6.2-py3-none-any.whl` | `py3-none-any` | `ddc6c8ce995e6987e7faf5e3f1b02b302836a0e5d98ece18392cb1a36c72ad56` |
| `cffi==1.16.0` / scoring-import | `cffi-1.16.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl` | `cp312-cp312-manylinux2014_x86_64, cp312-cp312-manylinux_2_17_x86_64` | `e715596e683d2ce000574bae5d07bd522c781a822866c20495e52520564f0969` |
| `chardet==4.0.0` / scoring-import | `chardet-4.0.0-py2.py3-none-any.whl` | `py2-none-any, py3-none-any` | `f864054d66fd9118f2e67044ac8981a54775ec5b67aed0441892edb553d21da5` |
| `charset-normalizer==2.0.4` / scoring-import | `charset_normalizer-2.0.4-py3-none-any.whl` | `py3-none-any` | `0c8911edd15d19223366a194a513099a302055a962bca2cec0f54b8b63175d8b` |
| `chess==1.11.2` / scoring-import | `chess-1.11.2.tar.gz` | `sdist (no platform tag)` | `a8b43e5678fdb3000695bdaa573117ad683761e5ca38e591c4826eba6d25bb39` |
| `cloudpickle==2.2.1` / scoring-import | `cloudpickle-2.2.1-py3-none-any.whl` | `py3-none-any` | `61f594d1f4c295fa5cd9014ceb3a1fc4a70b0de1164b94fbc2d854ccba056f9f` |
| `colorama==0.4.6` / scoring-import | `colorama-0.4.6-py2.py3-none-any.whl` | `py2-none-any, py3-none-any` | `4f1d9991f5acc0ca119f9d443620b77f9d6b33703e51011c16baf57afb285fc6` |
| `comm==0.2.1` / scoring-import | `comm-0.2.1-py3-none-any.whl` | `py3-none-any` | `87928485c0dfc0e7976fd89fc1e187023cf587e7c353e4a9b417555b44adf021` |
| `cryptography==42.0.5` / scoring-import | `cryptography-42.0.5-cp39-abi3-manylinux_2_28_x86_64.whl` | `cp39-abi3-manylinux_2_28_x86_64` | `cd2030f6650c089aeb304cf093f3244d34745ce0cfcc39f20c6fbfe030102e2a` |
| `cycler==0.11.0` / scoring-import | `cycler-0.11.0-py3-none-any.whl` | `py3-none-any` | `3a27e95f763a428a739d2add979fa7494c912a32c17c4c38c4d5f082cad165a3` |
| `decorator==5.1.1` / scoring-import | `decorator-5.1.1-py3-none-any.whl` | `py3-none-any` | `b8c3f85900b9dc423225913c5aace94729fe1fa9763b38939a95226f02d37186` |
| `defusedxml==0.7.1` / scoring-import | `defusedxml-0.7.1-py2.py3-none-any.whl` | `py2-none-any, py3-none-any` | `a352e7e428770286cc899e2542b6cdaedb2b4953ff269a210103ec58f6198a61` |
| `dill==0.4.0` / scoring-import | `dill-0.4.0-py3-none-any.whl` | `py3-none-any` | `44f54bf6412c2c8464c14e8243eb163690a9800dbe2c367330883b19c7561049` |
| `drawsvg==2.4.2` / scoring-import | `drawsvg-2.4.2-py3-none-any.whl` | `py3-none-any` | `b1c101e187aa395cb13c039549e4f26fb7b7ee03974f53dc9798436463781bf1` |
| `executing==0.8.3` / scoring-import | `executing-0.8.3-py2.py3-none-any.whl` | `py2-none-any, py3-none-any` | `d1eef132db1b83649a3905ca6dd8897f71ac6f8cac79a7e58a1a09cf137546c9` |
| `fast_downward_textworld==20.6.4` / scoring-import | `fast_downward_textworld-20.6.4.tar.gz` | `sdist (no platform tag)` | `ceeed05692ac6a4023de196ca3f8cfeffe80d23070ca8fda5991b7b46f8cb752` |
| `gensim==4.3.2` / scoring-import | `gensim-4.3.2.tar.gz` | `sdist (no platform tag)` | `99ac6af6ffd40682e70155ed9f92ecbf4384d59fb50af120d343ea5ee1b308ab` |
| `idna==3.7` / scoring-import | `idna-3.7-py3-none-any.whl` | `py3-none-any` | `82fee1fc78add43492d3a1898bfa6d8a904cc97d8427f683ed8e798d07761aa0` |
| `ipykernel==6.28.0` / scoring-import | `ipykernel-6.28.0-py3-none-any.whl` | `py3-none-any` | `c6e9a9c63a7f4095c0a22a79f765f079f9ec7be4f2430a898ddea889e8665661` |
| `ipython==8.25.0` / scoring-import | `ipython-8.25.0-py3-none-any.whl` | `py3-none-any` | `53eee7ad44df903a06655871cbab66d156a051fd86f3ec6750470ac9604ac1ab` |
| `ipython-genutils==0.2.0` / scoring-import | `ipython_genutils-0.2.0-py2.py3-none-any.whl` | `py2-none-any, py3-none-any` | `72dd37233799e619666c9f639a9da83c34013a73e8bbc79a7a6348d93c61fab8` |
| `ipywidgets==7.8.1` / scoring-import | `ipywidgets-7.8.1-py2.py3-none-any.whl` | `py2-none-any, py3-none-any` | `29f7056d368bf0a7b35d51cf0c56b58582da57c78bb9f765965fef7c332e807c` |
| `jedi==0.18.1` / scoring-import | `jedi-0.18.1-py2.py3-none-any.whl` | `py2-none-any, py3-none-any` | `637c9635fcf47945ceb91cd7f320234a7be540ded6f3e99a50cb6febdfd1ba8d` |
| `jericho==3.3.1` / scoring-import | `jericho-3.3.1.tar.gz` | `sdist (no platform tag)` | `032dde60a155dd9984d6db05b2c6ac22897446fb13a6a248cff8086001185571` |
| `jmespath==1.0.1` / scoring-import | `jmespath-1.0.1-py3-none-any.whl` | `py3-none-any` | `02e2e4cc71b5bcab88332eebf907519190dd9e6e82107fa7f83b1003a6252980` |
| `joblib==1.4.2` / scoring-import | `joblib-1.4.2-py3-none-any.whl` | `py3-none-any` | `06d478d5674cbc267e7496a410ee875abd68e4340feff4490bcb7afb88060ae6` |
| `jupyter_client==8.6.0` / scoring-import | `jupyter_client-8.6.0-py3-none-any.whl` | `py3-none-any` | `909c474dbe62582ae62b758bca86d6518c85234bdee2d908c778db6d72f39d99` |
| `jupyter_core==5.7.2` / scoring-import | `jupyter_core-5.7.2-py3-none-any.whl` | `py3-none-any` | `4f7315d2f6b4bcf2e3e7cb6e46772eba760ae459cd1f59d29eb57b0a01bd7409` |
| `kiwisolver==1.4.4` / scoring-import | `kiwisolver-1.4.4.tar.gz` | `sdist (no platform tag)` | `d41997519fcba4a1e46eb4a2fe31bc12f0ff957b2b81bac28db24744f333e955` |
| `lxml==5.2.1` / scoring-import | `lxml-5.2.1-cp312-cp312-manylinux_2_28_x86_64.whl` | `cp312-cp312-manylinux_2_28_x86_64` | `f0a1bc63a465b6d72569a9bba9f2ef0334c4e03958e043da1920299100bc7c08` |
| `lz4==4.3.2` / scoring-import | `lz4-4.3.2.tar.gz` | `sdist (no platform tag)` | `e1431d84a9cfb23e6773e72078ce8e65cad6745816d4cbf9ae67da5ea419acda` |
| `magiccube==0.3.0` / scoring-import | `magiccube-0.3.0-py3-none-any.whl` | `py3-none-any` | `a8da38cac53dff1667949c9a12485bebb9d62c01ae73db41eb7aba1bc1c8a00c` |
| `matplotlib==3.8.4` / scoring-import | `matplotlib-3.8.4-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl` | `cp312-cp312-manylinux2014_x86_64, cp312-cp312-manylinux_2_17_x86_64` | `f51c4c869d4b60d769f7b4406eec39596648d9d70246428745a681c327a8ad30` |
| `mementos==1.3.1` / scoring-import | `mementos-1.3.1-py2.py3-none-any.whl` | `py2-none-any, py3-none-any` | `fee20b2440a06657bb942b8d935f0c3d468b5ad58b07b33b609fd92fe864bc7f` |
| `mpmath==1.3.0` / scoring-import | `mpmath-1.3.0-py3-none-any.whl` | `py3-none-any` | `a0b2b9fe80bbcd81a6647ff13108738cfb482d481d826cc0e02f5b35e5c88d2c` |
| `networkx==3.4.2` / scoring-import | `networkx-3.4.2-py3-none-any.whl` | `py3-none-any` | `df5d4365b724cf81b8c6a7312509d0c22386097011ad1abe274afd5e9d3bbc5f` |
| `numexpr==2.8.7` / scoring-import | `numexpr-2.8.7-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl` | `cp312-cp312-manylinux2014_x86_64, cp312-cp312-manylinux_2_17_x86_64` | `a371cfc1670a18eea2d5c70abaa95a0e8824b70d28da884bad11931266e3a0ca` |
| `numpy==1.26.4` / scoring-import | `numpy-1.26.4-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl` | `cp312-cp312-manylinux2014_x86_64, cp312-cp312-manylinux_2_17_x86_64` | `675d61ffbfa78604709862923189bad94014bef562cc35cf61d3a07bba02a7ed` |
| `nvidia-ml-py==12.575.51` / scoring-import | `nvidia_ml_py-12.575.51-py3-none-any.whl` | `py3-none-any` | `eb8641800d98ce40a22f479873f34b482e214a7e80349c63be51c3919845446e` |
| `openpyxl==3.1.2` / scoring-import | `openpyxl-3.1.2-py2.py3-none-any.whl` | `py2-none-any, py3-none-any` | `f91456ead12ab3c6c2e9491cf33ba6d08357d802192379bb482f1033ade496f5` |
| `packaging==23.2` / scoring-import | `packaging-23.2-py3-none-any.whl` | `py3-none-any` | `8c491190033a9af7e1d931d0b5dacc2ef47509b34dd0de67ed209b5203fc88c7` |
| `pandas==2.2.2` / scoring-import | `pandas-2.2.2-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl` | `cp312-cp312-manylinux2014_x86_64, cp312-cp312-manylinux_2_17_x86_64` | `eee3a87076c0756de40b05c5e9a6069c035ba43e8dd71c379e68cab2c20f16ad` |
| `parso==0.8.3` / scoring-import | `parso-0.8.3-py2.py3-none-any.whl` | `py2-none-any, py3-none-any` | `c001d4636cd3aecdaf33cbb40aebb59b094be2a74c556778ef5576c175e19e75` |
| `patsy==0.5.6` / scoring-import | `patsy-0.5.6-py2.py3-none-any.whl` | `py2-none-any, py3-none-any` | `19056886fd8fa71863fa32f0eb090267f21fb74be00f19f5c70b2e9d76c883c6` |
| `pickleshare==0.7.5` / scoring-import | `pickleshare-0.7.5-py2.py3-none-any.whl` | `py2-none-any, py3-none-any` | `9649af414d74d4df115d5d718f82acb59c9d418196b7b4290ed47a12ce62df56` |
| `pillow==10.3.0` / scoring-import | `pillow-10.3.0-cp312-cp312-manylinux_2_28_x86_64.whl` | `cp312-cp312-manylinux_2_28_x86_64` | `ff61bfd9253c3915e6d41c651d5f962da23eda633cf02262990094a18a55371a` |
| `platformdirs==3.10.0` / scoring-import | `platformdirs-3.10.0-py3-none-any.whl` | `py3-none-any` | `d7c24979f292f916dc9cbf8648319032f551ea8c49a4c9bf2fb556a02070ec1d` |
| `prompt-toolkit==3.0.43` / scoring-import | `prompt_toolkit-3.0.43-py3-none-any.whl` | `py3-none-any` | `a11a29cb3bf0a28a387fe5122cdb649816a957cd9261dcedf8c9f1fef33eacf6` |
| `psutil==5.9.0` / scoring-import | `psutil-5.9.0.tar.gz` | `sdist (no platform tag)` | `869842dbd66bb80c3217158e629d6fceaecc3a3166d3d1faee515b05dd26ca25` |
| `pure-eval==0.2.2` / scoring-import | `pure_eval-0.2.2-py3-none-any.whl` | `py3-none-any` | `01eaab343580944bc56080ebe0a674b39ec44a945e6d09ba7db3cb8cec289350` |
| `py4j==0.10.9.9` / scoring-import | `py4j-0.10.9.9-py2.py3-none-any.whl` | `py2-none-any, py3-none-any` | `c7c26e4158defb37b0bb124933163641a2ff6e3a3913f7811b0ddbe07ed61533` |
| `pyarrow==23.0.0` / scoring-import | `pyarrow-23.0.0-cp312-cp312-manylinux_2_28_x86_64.whl` | `cp312-cp312-manylinux_2_28_x86_64` | `b73519f8b52ae28127000986bf228fda781e81d3095cd2d3ece76eb5cf760e1b` |
| `pycosat==0.6.6` / scoring-import | `pycosat-0.6.6.tar.gz` | `sdist (no platform tag)` | `a376cfae20b16fcfbef24bf3c047a8a294c35032bb051fa98842c12bbab6f0ff` |
| `pyfiglet==1.0.2` / scoring-import | `pyfiglet-1.0.2-py3-none-any.whl` | `py3-none-any` | `889b351d79c99e50a3f619c8f8e6ffdb27fd8c939fc43ecbd7559bd57d5f93ea` |
| `Pygments==2.15.1` / scoring-import | `Pygments-2.15.1-py3-none-any.whl` | `py3-none-any` | `db2db3deb4b4179f399a09054b023b6a586b76499d36965813c71aa8ed7b5fd1` |
| `pyOpenSSL==24.0.0` / scoring-import | `pyOpenSSL-24.0.0-py3-none-any.whl` | `py3-none-any` | `ba07553fb6fd6a7a2259adb9b84e12302a9a8a75c44046e8bb5d3e5ee887e3c3` |
| `pyparsing==3.0.9` / scoring-import | `pyparsing-3.0.9-py3-none-any.whl` | `py3-none-any` | `5026bae9a10eeaefb61dab2f09052b9f4307d44aee4eda64b309723d8d206bbc` |
| `PySocks==1.7.1` / scoring-import | `PySocks-1.7.1-py3-none-any.whl` | `py3-none-any` | `2725bd0a9925919b9b51739eea5f9e2bae91e83288108a9ad338b2e3a4435ee5` |
| `python-dateutil==2.9.0.post0` / scoring-import | `python_dateutil-2.9.0.post0-py2.py3-none-any.whl` | `py2-none-any, py3-none-any` | `a8b2bc7bffae282281c8140a97d3aa9c14da0b136dfe83f850eea9a5f7470427` |
| `pytz==2024.1` / scoring-import | `pytz-2024.1-py2.py3-none-any.whl` | `py2-none-any, py3-none-any` | `328171f4e3623139da4983451950b28e95ac706e13f3f2630a879749e7a8b319` |
| `PyYAML==6.0.3` / scoring-import | `pyyaml-6.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl` | `cp312-cp312-manylinux2014_x86_64, cp312-cp312-manylinux_2_17_x86_64, cp312-cp312-manylinux_2_28_x86_64` | `ba1cc08a7ccde2d2ec775841541641e4548226580ab850948cbfda66a1befcdc` |
| `pyzmq==25.1.2` / scoring-import | `pyzmq-25.1.2-cp312-cp312-manylinux_2_28_x86_64.whl` | `cp312-cp312-manylinux_2_28_x86_64` | `f8429b17cbb746c3e043cb986328da023657e79d5ed258b711c06a70c2ea7537` |
| `reasoning_gym==0.1.25` / scoring-import | `reasoning_gym-0.1.25-py3-none-any.whl` | `py3-none-any` | `7f17a3eddb13c015d7d4a755ed576a061df889faf9468bcc2cca334ebe9e0435` |
| `requests==2.32.2` / scoring-import | `requests-2.32.2-py3-none-any.whl` | `py3-none-any` | `fc06670dd0ed212426dfeb94fc1b983d917c4f9847c863f313c9dfaaffb7c23c` |
| `rich==15.0.0` / scoring-import | `rich-15.0.0-py3-none-any.whl` | `py3-none-any` | `33bd4ef74232fb73fe9279a257718407f169c09b78a87ad3d296f548e27de0bb` |
| `s3transfer==0.16.0` / scoring-import | `s3transfer-0.16.0-py3-none-any.whl` | `py3-none-any` | `18e25d66fed509e3868dc1572b3f427ff947dd2c56f844a5bf09481ad3f3b2fe` |
| `scienceworld==1.2.3` / scoring-import | `scienceworld-1.2.3-py3-none-any.whl` | `py3-none-any` | `e9737b9d099bfaad90ef053ad6ac1d795e2063ed320efdfc0e9d9c8b5bebf419` |
| `scikit-learn==1.8.0` / scoring-import | `scikit_learn-1.8.0-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl` | `cp312-cp312-manylinux_2_27_x86_64, cp312-cp312-manylinux_2_28_x86_64` | `a0bcfe4d0d14aec44921545fd2af2338c7471de9cb701f1da4c9d85906ab847a` |
| `scipy==1.13.1` / scoring-import | `scipy-1.13.1-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl` | `cp312-cp312-manylinux2014_x86_64, cp312-cp312-manylinux_2_17_x86_64` | `de3ade0e53bc1f21358aa74ff4830235d716211d7d077e340c7349bc3542e884` |
| `seaborn==0.13.2` / scoring-import | `seaborn-0.13.2-py3-none-any.whl` | `py3-none-any` | `636f8336facf092165e27924f223d3c62ca560b1f2bb5dff7ab7fad265361987` |
| `setuptools==82.0.0` / sdist-build-only | `setuptools-82.0.0-py3-none-any.whl` | `py3-none-any` | `70b18734b607bd1da571d097d236cfcfacaf01de45717d59e6e04b96877532e0` |
| `simplejson==4.1.1` / scoring-import | `simplejson-4.1.1-cp312-cp312-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl` | `cp312-cp312-manylinux1_x86_64, cp312-cp312-manylinux_2_28_x86_64, cp312-cp312-manylinux_2_5_x86_64` | `45ec18e337fec538b7e902d489505c450b2454653d1290f3f50385e6fd8aa607` |
| `six==1.16.0` / scoring-import | `six-1.16.0-py2.py3-none-any.whl` | `py2-none-any, py3-none-any` | `8abb2f1d86890a2dfb989f9a77cfcfd3e47c2a354b01111771326f8aa26e0254` |
| `smart-open==5.2.1` / scoring-import | `smart_open-5.2.1-py3-none-any.whl` | `py3-none-any` | `71d14489da58b60ce12fc3ecb823facc59a8b23cd1b58edb97175640350d3a62` |
| `stack-data==0.2.0` / scoring-import | `stack_data-0.2.0-py3-none-any.whl` | `py3-none-any` | `999762f9c3132308789affa03e9271bbbe947bf78311851f4d485d8402ed858e` |
| `statsmodels==0.14.2` / scoring-import | `statsmodels-0.14.2-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl` | `cp312-cp312-manylinux2014_x86_64, cp312-cp312-manylinux_2_17_x86_64` | `55d1742778400ae67acb04b50a2c7f5804182f8a874bd09ca397d69ed159a751` |
| `sympy==1.13.1` / scoring-import | `sympy-1.13.1-py3-none-any.whl` | `py3-none-any` | `db36cdc64bf61b9b24578b6f7bab1ecdd2452cf008f34faa33776680c26d66f8` |
| `tabulate==0.9.0` / scoring-import | `tabulate-0.9.0-py3-none-any.whl` | `py3-none-any` | `024ca478df22e9340661486f85298cff5f6dcdba14f3813e8830015b9ed1948f` |
| `TatSu==5.8.3` / scoring-import | `TatSu-5.8.3-py2.py3-none-any.whl` | `py2-none-any, py3-none-any` | `0a836692e67247cad9f251e083b045b13345cc715e69a7fbc16522beaa0f2163` |
| `termcolor==3.3.0` / scoring-import | `termcolor-3.3.0-py3-none-any.whl` | `py3-none-any` | `cf642efadaf0a8ebbbf4bc7a31cec2f9b5f21a9f726f4ccbb08192c9c26f43a5` |
| `textworld==1.7.0` / scoring-import | `textworld-1.7.0-py3-none-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl` | `py3-none-manylinux1_x86_64, py3-none-manylinux2014_x86_64, py3-none-manylinux_2_17_x86_64, py3-none-manylinux_2_5_x86_64` | `ca7486cff540c4d90865c54a3465e948c2790357aa78ad64de4406387854cbc8` |
| `threadpoolctl==3.6.0` / scoring-import | `threadpoolctl-3.6.0-py3-none-any.whl` | `py3-none-any` | `43a0b8fd5a2928500110039e43a5eed8480b918967083ea48dc3ab9f13c4a7fb` |
| `torch==2.5.1` / scoring-import | `torch-2.5.1-cp312-cp312-manylinux1_x86_64.whl` | `cp312-cp312-manylinux1_x86_64` | `ed231a4b3a5952177fafb661213d690a72caaad97d5824dd4fc17ab9e15cec03` |
| `tornado==6.4.1` / scoring-import | `tornado-6.4.1-cp38-abi3-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl` | `cp38-abi3-manylinux1_x86_64, cp38-abi3-manylinux2014_x86_64, cp38-abi3-manylinux_2_17_x86_64, cp38-abi3-manylinux_2_5_x86_64` | `613bf4ddf5c7a95509218b149b555621497a6cc0d46ac341b30bd9ec19eac7f3` |
| `tqdm==4.66.4` / scoring-import | `tqdm-4.66.4-py3-none-any.whl` | `py3-none-any` | `b75ca56b413b030bc3f00af51fd2c1a1a5eac6a0c1cca83cbb37a5c52abce644` |
| `traitlets==5.14.3` / scoring-import | `traitlets-5.14.3-py3-none-any.whl` | `py3-none-any` | `b74e89e397b1ed28cc831db7aea759ba6640cb3de13090ca145426688ff1ac4f` |
| `typing_extensions==4.15.0` / scoring-import | `typing_extensions-4.15.0-py3-none-any.whl` | `py3-none-any` | `f0fa19c6845758ab08074a0cfa8b7aecb71c999ca73d62883bc25cc018c4e548` |
| `unicodedata2==15.1.0` / scoring-import | `unicodedata2-15.1.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl` | `cp312-cp312-manylinux2014_x86_64, cp312-cp312-manylinux_2_17_x86_64` | `bcdcd195484ba8ef19bef04ec14dcd8b1f8d6560fc517462ee0e010f5f545d75` |
| `urllib3==2.2.2` / scoring-import | `urllib3-2.2.2-py3-none-any.whl` | `py3-none-any` | `a448b2f64d686155468037e1ace9f2d2199776e17f0a46610480d311f73e3472` |
| `wcwidth==0.8.2` / scoring-import | `wcwidth-0.8.2-py3-none-any.whl` | `py3-none-any` | `d63947694a0539a1d51e01eda7caf800c291020e6cdd7e28ad7b14dd33ad4f85` |
| `wheel==0.43.0` / sdist-build-only | `wheel-0.43.0-py3-none-any.whl` | `py3-none-any` | `55c570405f142630c6b9f72fe09d9b67cf1477fcf543ae5b8dcb1f5b7377da81` |
| `zss==1.2.0` / scoring-import | `zss-1.2.0.tar.gz` | `sdist (no platform tag)` | `07bb937441929ccb82961f4f7b80fbce9e2b20d0e46ddcbcbc1fcb094f585b50` |
| `zstandard==0.22.0` / scoring-import | `zstandard-0.22.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl` | `cp312-cp312-manylinux2014_x86_64, cp312-cp312-manylinux_2_17_x86_64` | `466e6ad8caefb589ed281c076deb6f0cd330e8bc13c5035854ffb9c2014b118c` |
| `cmake==3.29.6` / sdist-build-only | `cmake-3.29.6-py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64.whl` | `py3-none-manylinux2014_x86_64, py3-none-manylinux_2_17_x86_64` | `9d468a28e433278843e026d1e57ceba06df2cc3569219245b38731a5a9e307fa` |
| `setuptools-scm==8.1.0` / sdist-build-only | `setuptools_scm-8.1.0-py3-none-any.whl` | `py3-none-any` | `897a3226a6fd4a6eb2f068745e49733261a21f70b1bb28fce0339feb978d9af3` |
| `cppy==1.2.1` / sdist-build-only | `cppy-1.2.1-py3-none-any.whl` | `py3-none-any` | `c5b5eac3d3f42593a07d35275b0bc27f447b76b9ad8f27c62e3cfa286dc1988a` |
| `pkgconfig==1.5.5` / sdist-build-only | `pkgconfig-1.5.5-py3-none-any.whl` | `py3-none-any` | `d20023bbeb42ee6d428a0fac6e0904631f545985a10cdd71a20aa58bc47a4209` |
| `nvidia-cublas-cu12==12.4.5.8` / torch-import-time-native-provider | `nvidia_cublas_cu12-12.4.5.8-py3-none-manylinux2014_x86_64.whl` | `py3-none-manylinux2014_x86_64` | `2fc8da60df463fdefa81e323eef2e36489e1c94335b5358bcb38360adf75ac9b` |
| `nvidia-cudnn-cu12==9.1.0.70` / torch-import-time-native-provider | `nvidia_cudnn_cu12-9.1.0.70-py3-none-manylinux2014_x86_64.whl` | `py3-none-manylinux2014_x86_64` | `165764f44ef8c61fcdfdfdbe769d687e06374059fbb388b6c89ecb0e28793a6f` |
| `nvidia-cuda-nvrtc-cu12==12.4.127` / torch-import-time-native-provider | `nvidia_cuda_nvrtc_cu12-12.4.127-py3-none-manylinux2014_x86_64.whl` | `py3-none-manylinux2014_x86_64` | `a178759ebb095827bd30ef56598ec182b85547f1508941a3d560eb7ea1fbf338` |
| `nvidia-cuda-runtime-cu12==12.4.127` / torch-import-time-native-provider | `nvidia_cuda_runtime_cu12-12.4.127-py3-none-manylinux2014_x86_64.whl` | `py3-none-manylinux2014_x86_64` | `64403288fa2136ee8e467cdc9c9427e0434110899d07c779f25b5c068934faa5` |
| `nvidia-cuda-cupti-cu12==12.4.127` / torch-import-time-native-provider | `nvidia_cuda_cupti_cu12-12.4.127-py3-none-manylinux2014_x86_64.whl` | `py3-none-manylinux2014_x86_64` | `9dec60f5ac126f7bb551c055072b69d85392b13311fcc1bcda2202d172df30fb` |
| `nvidia-cufft-cu12==11.2.1.3` / torch-import-time-native-provider | `nvidia_cufft_cu12-11.2.1.3-py3-none-manylinux2014_x86_64.whl` | `py3-none-manylinux2014_x86_64` | `f083fc24912aa410be21fa16d157fed2055dab1cc4b6934a0e03cba69eb242b9` |
| `nvidia-curand-cu12==10.3.5.147` / torch-import-time-native-provider | `nvidia_curand_cu12-10.3.5.147-py3-none-manylinux2014_x86_64.whl` | `py3-none-manylinux2014_x86_64` | `a88f583d4e0bb643c49743469964103aa59f7f708d862c3ddb0fc07f851e3b8b` |
| `nvidia-nvjitlink-cu12==12.4.127` / torch-import-time-native-provider | `nvidia_nvjitlink_cu12-12.4.127-py3-none-manylinux2014_x86_64.whl` | `py3-none-manylinux2014_x86_64` | `06b3b9b25bf3f8af351d664978ca26a16d2c5127dbd53c0497e28d1fb9611d57` |
| `nvidia-cusparse-cu12==12.3.1.170` / torch-import-time-native-provider | `nvidia_cusparse_cu12-12.3.1.170-py3-none-manylinux2014_x86_64.whl` | `py3-none-manylinux2014_x86_64` | `ea4f11a2904e2a8dc4b1833cc1b5181cde564edd0d5cd33e3c168eff2d1863f1` |
| `nvidia-cusolver-cu12==11.6.1.9` / torch-import-time-native-provider | `nvidia_cusolver_cu12-11.6.1.9-py3-none-manylinux2014_x86_64.whl` | `py3-none-manylinux2014_x86_64` | `19e33fa442bcfd085b3086c4ebf7e8debc07cfe01e11513cc6d332fd918ac260` |
| `nvidia-nccl-cu12==2.21.5` / torch-import-time-native-provider | `nvidia_nccl_cu12-2.21.5-py3-none-manylinux2014_x86_64.whl` | `py3-none-manylinux2014_x86_64` | `8579076d30a8c24988834445f8d633c697d42397e92ffc3f63fa26766d25e0a0` |
| `nvidia-nvtx-cu12==12.4.127` / torch-import-time-native-provider | `nvidia_nvtx_cu12-12.4.127-py3-none-manylinux2014_x86_64.whl` | `py3-none-manylinux2014_x86_64` | `781e950d9b9f60d8241ccea575b32f5105a5baf4c2351cab5256a24869f12a1a` |
| `Bottleneck==1.3.7` / locally-built from pinned sdist | `bottleneck-1.3.7-cp312-cp312-linux_x86_64.whl` | `cp312-cp312-linux_x86_64` | `5c670643134c6edc71d8cd2a277840262e14f7311933e11a9c06b3314daec5aa` |
| `cellpylib==2.4.0` / locally-built from pinned sdist | `cellpylib-2.4.0-py3-none-any.whl` | `py3-none-any` | `7d24c32060e17752c24b77e3185af426b8a1593e54fc716db36cd39243d1d316` |
| `chess==1.11.2` / locally-built from pinned sdist | `chess-1.11.2-py3-none-any.whl` | `py3-none-any` | `5322aea261a51bf9283882dac95789676130ae6d96ed656beb897bbbc71d5a87` |
| `fast_downward_textworld==20.6.4` / locally-built from pinned sdist | `fast_downward_textworld-20.6.4-py3-none-any.whl` | `py3-none-any` | `08efdf7ef0a9078a7d8e16a8baca6dcb7f585f32caca5fe045d89625397bbb8d` |
| `gensim==4.3.2` / locally-built from pinned sdist | `gensim-4.3.2-cp312-cp312-linux_x86_64.whl` | `cp312-cp312-linux_x86_64` | `c7bc5a082bfd1cb4005a445143009c64887ab9d46b6f964b787eeabc4cde8e76` |
| `jericho==3.3.1` / locally-built from pinned sdist | `jericho-3.3.1-py3-none-any.whl` | `py3-none-any` | `7cceee841274af004628024d04a9032cc37a08ab60b8095cdff82d5ddd73ed31` |
| `kiwisolver==1.4.4` / locally-built from pinned sdist | `kiwisolver-1.4.4-cp312-cp312-linux_x86_64.whl` | `cp312-cp312-linux_x86_64` | `e561bf14715bca7f327123da0cf26d371824553f3a50786653549ddc5b456e2f` |
| `lz4==4.3.2` / locally-built from pinned sdist | `lz4-4.3.2-cp312-cp312-linux_x86_64.whl` | `cp312-cp312-linux_x86_64` | `6b7a67dfc6dc26a8bfa5d75bd3683e076baf611576e1dd48e774f7f790c1d9b4` |
| `psutil==5.9.0` / locally-built from pinned sdist | `psutil-5.9.0-cp312-cp312-linux_x86_64.whl` | `cp312-cp312-linux_x86_64` | `afdd5631bb8453bdd59fdb900428bc9747d64ff11e269a4d1826b0994a17c208` |
| `pycosat==0.6.6` / locally-built from pinned sdist | `pycosat-0.6.6-cp312-cp312-linux_x86_64.whl` | `cp312-cp312-linux_x86_64` | `47e5eb9e102cba21ba3de4fb3a965e375106f43ab61a52844887ce0a3cab37cf` |
| `zss==1.2.0` / locally-built from pinned sdist | `zss-1.2.0-py3-none-any.whl` | `py3-none-any` | `df3d1e7db8bc7028c1b1574b7c5a7cc9753146302c1f4b41e51088a666e8c5b0` |

## Shared blocker decision and validation

S1 still requires complete execution-selected runtime custody and task-bound scorer inputs. S3/S4/S6 remain partial; no shared or dataset blocker closes. Four snapshot/service families (appworld, gaia, tau_bench, terminal_bench) are outside this installation-payload task and gain no payload coverage. Full official provenance/execution, transitive OS/native/image/ABI closure, JVM/LibreOffice lifecycle and trusted class-specific observations remain governed by their existing evidence and gates. A synthetic or import-only success does not authorize H0.

`reports/w-wheelhouse-validation.txt` records exact commands and the current dataset-blocker checker output. `validate.py` verifies retained payload sizes, two independent hash computations, wheel archive identity/versions/target tags, and all 4,435 read source hashes plus file+line witnesses. No production code, historical report/receipt, run directory, dataset blocker status or next_action is changed.
