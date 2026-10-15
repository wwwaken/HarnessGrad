"""Render the human review from measured acquisition/build/install receipts."""
import json
import pathlib
import subprocess

HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[2]
m=json.loads((HERE/'manifest.json').read_text())
b=json.loads((HERE/'built-artifacts.json').read_text())
deps=json.loads((HERE/'installed-distributions.json').read_text())
coverage=json.loads((HERE/'dataset-payloads.json').read_text())
index=json.loads((HERE/'payload-index.json').read_text())
installs=json.loads((HERE/'install-summary.json').read_text())
validation=json.loads((HERE/'payload-validation-final.txt').read_text())
base=json.loads((HERE/'review-baseline.json').read_text())['commit']
lines=[f'''# Offline scorer installation payloads — w-wheelhouse

Source baseline: `{base}`. Scope: the 19 surveyed actor-workdir / QA-command datasets. No production adapter/scoring logic changes; no benchmark task, scorer invocation, model, GPU computation, JVM launch or model-endpoint call.

## Payload-only coverage — w-wheelhouse

**Complete nonempty Python scorer-import installation profiles: chessbench_puzzles and scienceworld. Eight implemented scorers need no third-party distribution payload. Nine current-host import profiles remain partial. S1 remains PARTIAL and scorer-offline-closure remains open.** This is installation evidence, not an offline runtime/scorer certification or dataset-blocker closure.

The retained wheelhouse is `{m['payload_directory']}`. Acquisition/build/install receipts and manifests are committed under `tests/fixtures/hg_wwheelhouse/`; the binary payloads are retained **outside git** at that path. The evidence directory alone is not a portable wheelhouse archive. The user requested either artifacts or acquisition receipts; this delivers the receipts plus the local retained artifacts.

{len(m['artifacts'])} exact-version distribution requests comprise 102 source-led imported Python distributions, 12 Torch import-time native providers and six separate build-only tools. {len(m['artifacts'])-1} distributions were obtained; only `mkl-service==2.4.0` has no compatible wheel/sdist in the checked versioned PyPI response. All 11 obtained sdists were built into exact-version wheels with networking denied. The final wheelhouse has {validation['payloads_rehashed_twice']} accepted source/wheel artifacts, {validation['total_bytes']} bytes. Python hashlib and the independent `sha256sum` command recomputed their digests; wheel filenames, METADATA versions/names and host-compatible tags were checked. Failed/truncated transfers are excluded from accepted artifacts.

### How dependency scope was determined

Current source is read independently in `source-imports.json`, with file hashes and exact import statement lines. The earlier `hg_wclo_actor` records are path leads, not an authoritative dependency list. `audit.py` follows the current scorer roots and performs fresh package-only imports in new network namespaces, without importing adapters or running tasks. `installed-distributions.json` maps every Python distribution to source file+line witnesses; `audit/*.stdout.json` preserves actual loaded modules and errors. The audit includes the released DS-1000 scoring contexts, because `check.py:27-30` composes them and upstream `execution.py:49` executes them. `ds1000-context-imports.json` preserves only import statements with JSONL/context line locations, not questions, answers or complete task contexts.

Shared QA verification imports the staged adapter at `data/scaffolds/qa/verify/check.py:217` and dispatches structured/legacy scoring at `:238`/`:242`. `data/scaffolds/qa/base.py:438` calls `ensure()`, and `:209`/`:229` reach row loading. The helper, prediction, aggregation and evidence-scoring modules use the standard library. Import-time row-loading is disclosed separately from the comparison metric. No prospective BFCL official AST dependencies, actor tool packages, Reasoning Gym judge extras, arbitrary candidate imports or blanket environment metadata closure are vendored.

### Per-dataset source and installation coverage

“Complete” below means Python distribution payload coverage for the inspected import path only. It does not include base Python/stdlib, OS ABI, JRE, LibreOffice, selected-family/task behavior or execution custody.

| Dataset | Current source reason for third-party scoring imports | Payload coverage |
| --- | --- | --- |''']
rows={
'alfworld':('`data/datasets/alfworld/verify/check.py:62,159` → `data/datasets/alfworld/lib/gym_env.py:67-69`: TextWorld/Gym and ALFWorld replay wrappers; imported transitive packages listed below.','Partial: obtainable replay packages install/import; host MKL service artifact missing.'),
'bfcl_v3':('`data/datasets/bfcl_v3.py:69,217`: local name-only diagnostic scorer through stdlib QA scaffold; no official AST scorer import.','No third-party payload required for implemented diagnostic; official-scorer gap unchanged.'),
'bird_minidev':('`data/datasets/bird_minidev/verify/check.py:90`: direct stdlib SQLite execution/comparison; current checker import statements are in source-imports.json. Upstream psycopg2 is not imported by this path.','No third-party payload required; Python/SQLite ABI remains separate.'),
'chessbench_puzzles':('`data/datasets/chessbench_puzzles.py:25,309`: `import chess` and strict/upstream replay comparison.','Complete Python import payload: chess==1.11.2, built from exact sdist, offline install/import and pip check pass.'),
'ds1000':('`data/datasets/ds1000/verify/check.py:27-30,38-42,54`: trusted context plus candidate passed to released runner; upstream execution.py:49 executes it. Context census supplies each import’s JSONL and context line. Numeric/scientific libraries and Torch are scorer-context dependencies, not inferred from actor setup.','Partial: installed-version artifacts and native providers acquired; TensorFlow/XGBoost have no installed version to pin; Gensim/SciPy incompatibility persists.'),
'fever':('`data/datasets/fever.py:11-12,27,41`: local stdlib `fever_is_strictly_correct` / evidence scaffold.','No third-party payload required.'),
'gsm8k':('`data/datasets/gsm8k.py:257` → `:95-96` → `data/scaffolds/qa/read.py:106-107`: PyArrow startup before data-path failure; comparison at gsm8k.py:149 is stdlib.','Partial current-host startup set; public-wheel startup install/import succeeds, host MKL payload missing.'),
'hotpotqa':('`data/datasets/hotpotqa.py:104` → `:60-62` → `data/scaffolds/qa/read.py:106-107`: PyArrow startup conditional on data visibility; local comparison at :37/:54 is stdlib.','Partial conditional current-host startup set; same public-wheel profile succeeds.'),
'jericho':('`data/datasets/jericho/verify/check.py:45` → `data/datasets/jericho/lib/jer_env.py:40`: `from jericho import FrotzEnv`; installed jericho.py imports NumPy.','Partial current-host set; Jericho/NumPy wheels install/import, host MKL payload missing. Native replay not run.'),
'livecodebench':('`data/datasets/livecodebench/verify/check.py:86,191` imports pinned upstream `testing_util.py:13` and `pass_k_utils.py:1`, both NumPy. Exact upstream paths/hashes in source-imports.json.','Partial current-host set; public NumPy wheel install/import succeeds, host MKL payload missing. Candidate-specific imports unbounded.'),
'musique':('`data/datasets/musique.py:25,116,125,140`: stdlib answer/support comparison, prediction helper and aggregation contract.','No third-party payload required.'),
'physicsquestions':('`data/datasets/physicsquestions.py:47-50,103`: csv/re and stdlib QA scaffold.','No third-party payload required.'),
'reasoning_gym':('`data/datasets/reasoning_gym.py:108,114-115`: `create_dataset` and library score_answer. Installed reasoning_gym/__init__.py:5-20 eagerly imports all family categories.','Partial current-host set; public profile install/import succeeds; host MKL payload missing, selected-family execution/resources not certified.'),
'scienceworld':('`data/datasets/scienceworld/verify/check.py:59` → `data/datasets/scienceworld/lib/scw_env.py:125`: ScienceWorldEnv. Installed scienceworld/scienceworld.py:9 imports py4j.java_gateway.','Complete Python import payload: scienceworld==1.2.3 and py4j==0.10.9.9. Offline install/import and pip check pass; JVM closure separate.'),
'sportsunderstanding':('`data/datasets/sportsunderstanding.py:38-41,80`: csv/re and stdlib QA scaffold.','No third-party payload required.'),
'spreadsheetbench':('`data/datasets/spreadsheetbench/verify/check.py:165,256`: `import openpyxl`; installed openpyxl/compat/numbers.py:9 imports optional NumPy; lxml/Pillow/defusedxml/cffi load on the observed host import path.','Partial current-host Python set; public profile install/import succeeds, host MKL payload missing; LibreOffice/plugins remain separate.'),
'strategyqa':('`data/datasets/strategyqa.py:41-45,89`: csv/re/string and stdlib QA scaffold.','No third-party payload required.'),
'triviaqa':('`data/datasets/triviaqa.py:359` → `:240` → `data/scaffolds/qa/read.py:106-107`: PyArrow startup; alias comparison at triviaqa.py:160 is stdlib.','Partial current-host startup set; same public-wheel profile succeeds, host MKL payload missing.'),
'twowikimultihopqa':('`data/datasets/twowikimultihopqa.py:74-82,480,490,507`: stdlib answer/entity/support comparison, prediction and aggregation helpers.','No third-party payload required.'),
}
for name,(why,status) in rows.items(): lines.append(f'| `{name}` | {why} | {status} |')
lines+=['''
### Exact observed Python distribution sets

These are the source-led fresh-import observations, not all installed packages or a claim that every package executes for every selected task. Full versions, source witnesses and per-dataset artifact mappings are in `installed-distributions.json` and `dataset-payloads.json`. The eight empty sets are bfcl_v3, bird_minidev, fever, musique, physicsquestions, sportsunderstanding, strategyqa and twowikimultihopqa.
''']
for name in ['alfworld','chessbench_puzzles','ds1000','gsm8k','jericho','livecodebench','reasoning_gym','scienceworld','spreadsheetbench']:
    r=coverage[name]
    names=', '.join(f"`{k}=={v['version']}`" for k,v in r['packages'].items())
    title='gsm8k / hotpotqa (conditional) / triviaqa startup' if name=='gsm8k' else name
    lines.append(f'- **{title}:** {names}.')
lines+=['''
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
| --- | --- | --- |''']
for name,r in installs.items():lines.append(f"| `{name}` | exit {r['install']['exit_code']} | exit {r['import']['exit_code']} |")
retry=json.loads((HERE/'ds1000-retry-summary.json').read_text())
lines.append(f"| DS-1000 native-provider retry in its previously fresh venv | exit {retry['install']['exit_code']} | exit {retry['import']['exit_code']}; per-module output preserves remaining errors |")
lines+=['''
The successful import-only profiles run no scoring calls or replay constructors. DS-1000 initial/retry failures are not scores. Torch's repaired import does not certify any task operation, model execution or selected runtime closure. Compatible public NumPy/PyArrow wheels are new install artifacts, not the original Conda wheel bytes or MKL provider. A successful public-wheel subset therefore does not certify the nine host closures.

## Imported Python packages: current source witnesses

Every imported Python distribution has at least one freshly read source import witness. One is printed below; all witnesses, loaded-module paths and source hashes are retained in the machine-readable evidence. A static witness plus package-only import observation is not execution-selected task custody. Absolute site-packages paths refer to the inspected host, not vendored task inputs.

| Distribution | Source file+line witness |
| --- | --- |''']
for k,r in sorted(deps.items()):
    w=r['source_witnesses'][0]
    lines.append(f"| `{r['name']}=={r['version']}` | `{w['path']}:{w['line']}`: `{w['text'].splitlines()[0].replace('|','&#124;')}` |")
lines+=['''
## Pinned artifact identities

The following are accepted payloads only. `manifest.json` binds every download filename to its **actual full source URL**, versioned index JSON URL/response hash, HTTP metadata, installed WHEEL/direct_url observations, host-compatible tags, length and independently computed digest. `built-artifacts.json` binds generated wheels to source URL/hash, command, build logs and exact WHEEL tags. `payload-index.json` unifies them; `sha256sum.command.json` preserves the exact independent command and `sha256sum.payloads.txt` its raw output. All URLs came from preserved PyPI responses. Source archives have no platform tag. Host-compatible public tags are not an identity claim for the original Conda distribution artifact.

| Distribution / role | Obtained or built filename | Actual artifact tags | Recomputed SHA-256 |
| --- | --- | --- | --- |''']
for r in index['artifacts']:
    tags=', '.join(r.get('verified_tags',[])) or 'sdist (no platform tag)'
    role=r.get('role','locally-built from pinned sdist')
    lines.append(f"| `{r['name']}=={r['version']}` / {role} | `{r['filename']}` | `{tags}` | `{r['sha256']}` |")
lines+=['''
## Shared blocker decision and validation

S1 still requires complete execution-selected runtime custody and task-bound scorer inputs. S3/S4/S6 remain partial; no shared or dataset blocker closes. Four snapshot/service families (appworld, gaia, tau_bench, terminal_bench) are outside this installation-payload task and gain no payload coverage. Full official provenance/execution, transitive OS/native/image/ABI closure, JVM/LibreOffice lifecycle and trusted class-specific observations remain governed by their existing evidence and gates. A synthetic or import-only success does not authorize H0.

`reports/w-wheelhouse-validation.txt` records exact commands and the current dataset-blocker checker output. `validate.py` verifies retained payload sizes, two independent hash computations, wheel archive identity/versions/target tags, and all 4,435 read source hashes plus file+line witnesses. No production code, historical report/receipt, run directory, dataset blocker status or next_action is changed.
''']
(ROOT/'reports/w-wheelhouse-payloads.md').write_text('\n'.join(lines).rstrip()+'\n')
print('report written',len(lines),'sections/table rows')
