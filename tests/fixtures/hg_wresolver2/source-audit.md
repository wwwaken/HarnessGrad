# Actual scorer import and metadata requirements - w-resolver2

Inspected current repository source and retained wheel members without importing dependency packages or running scorers. Original source bytes and recomputed SHA-256 digests are preserved in `source-audit.json`; literal source excerpts, wheel digest command output and current interpreter tags are in `source/excerpts.stdout.txt`. The generator is `source/generate-source-audit.py`; its successful raw output is `source/generate.stdout.txt` and empty stderr is `source/generate.stderr.txt`.

The previous packet targets CPython 3.12 Linux x86_64. A fresh interpreter observation records `CPython` with SOABI `cpython-312-x86_64-linux-gnu`, executable `/mnt/8t/xubuqiang/anaconda3/bin/python3` and all accepted wheel tags in `source/runtime.json`. Platform-dependent candidates must match these tags. Pure Python `py3-none-any` (or compatible `py2.py3-none-any`) wheels are also accepted. This is an experimental resolver target, not production runtime custody.

Each profile uses default requirements with no extra enabled. Source pins constrain the root distribution; wheel METADATA provides the transitive version bounds. Python import sites themselves do not enforce distribution version pins.

## jericho

Root requirement: `jericho==3.3.1`, declared at `data/datasets/jericho.py:305`. Missing resolver requirement: `spacy>=2.1.0`.

Scoring/source route:

- `data/datasets/jericho.py:257`: `"python3", "check.py",`. Preimage: `tests/fixtures/hg_wresolver2/source/repository/data/datasets/jericho.py:257`.
- `data/datasets/jericho/verify/check.py:49`: `import jer_env  # noqa: E402`. Preimage: `tests/fixtures/hg_wresolver2/source/repository/data/datasets/jericho/verify/check.py:49`.
- `data/datasets/jericho/lib/jer_env.py:38`: `from jericho import FrotzEnv`. Preimage: `tests/fixtures/hg_wresolver2/source/repository/data/datasets/jericho/lib/jer_env.py:38`.

Actual missing-module import site: `/tmp/hg-wwheelhouse-payloads-e5uywviu/jericho-3.3.1-py3-none-any.whl:jericho/util.py:42`: `import spacy`. Preimage: `tests/fixtures/hg_wresolver2/source/wheels/jericho/jericho/util.py:42`.

Resolver metadata chain:

- `/tmp/hg-wwheelhouse-payloads-e5uywviu/jericho-3.3.1-py3-none-any.whl:jericho-3.3.1.dist-info/METADATA:12`: `Requires-Dist: spacy>=2.1.0`. Preimage: `tests/fixtures/hg_wresolver2/source/wheels/jericho/jericho-3.3.1.dist-info/METADATA:12`.

spaCy is a lazy util dependency. The wrapper replay path calls env.step; this source audit does not execute a game or attest a spaCy import. The normal metadata edge remains required for dependency-aware resolution.

The same lazy helper loads `en_core_web_sm` and downloads it if its load raises `OSError` (wheel `jericho/util.py:44` and `:46`). A resolved spaCy wheel graph does not provision that language model. The implemented replay wrapper calls `env.step(action)` at current `data/datasets/jericho/lib/jer_env.py:113`; no world construction or replay occurred in this audit.

## reasoning_gym

Root requirement: `reasoning-gym==0.1.25`, declared at `data/datasets/reasoning_gym.py:67`. Missing resolver requirement: `contourpy>=1.0.1`.

Scoring/source route:

- `data/datasets/reasoning_gym.py:108`: `from reasoning_gym import create_dataset`. Preimage: `tests/fixtures/hg_wresolver2/source/repository/data/datasets/reasoning_gym.py:108`.
- `/tmp/hg-wwheelhouse-payloads-e5uywviu/reasoning_gym-0.1.25-py3-none-any.whl:reasoning_gym/__init__.py:7`: `algorithmic,`. Preimage: `tests/fixtures/hg_wresolver2/source/wheels/reasoning-gym/reasoning_gym/__init__.py:7`.
- `/tmp/hg-wwheelhouse-payloads-e5uywviu/reasoning_gym-0.1.25-py3-none-any.whl:reasoning_gym/algorithmic/__init__.py:16`: `from .game_of_life import GameOfLifeConfig, GameOfLifeCurriculum, GameOfLifeDataset`. Preimage: `tests/fixtures/hg_wresolver2/source/wheels/reasoning-gym/reasoning_gym/algorithmic/__init__.py:16`.
- `/tmp/hg-wwheelhouse-payloads-e5uywviu/reasoning_gym-0.1.25-py3-none-any.whl:reasoning_gym/algorithmic/game_of_life.py:6`: `import cellpylib as cpl`. Preimage: `tests/fixtures/hg_wresolver2/source/wheels/reasoning-gym/reasoning_gym/algorithmic/game_of_life.py:6`.
- `/tmp/hg-wwheelhouse-payloads-e5uywviu/cellpylib-2.4.0-py3-none-any.whl:cellpylib/__init__.py:12`: `from .ca_functions import BaseRule, AsynchronousRule, ReversibleRule, binary_rule, init_simple, nks_rule, \`. Preimage: `tests/fixtures/hg_wresolver2/source/wheels/cellpylib/cellpylib/__init__.py:12`.
- `/tmp/hg-wwheelhouse-payloads-e5uywviu/cellpylib-2.4.0-py3-none-any.whl:cellpylib/ca_functions.py:1`: `import matplotlib.pyplot as plt`. Preimage: `tests/fixtures/hg_wresolver2/source/wheels/cellpylib/cellpylib/ca_functions.py:1`.

Actual missing-module import site: `/tmp/hg-wwheelhouse-payloads-e5uywviu/matplotlib-3.8.4-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl:matplotlib/contour.py:1507`: `import contourpy`. Preimage: `tests/fixtures/hg_wresolver2/source/wheels/matplotlib/matplotlib/contour.py:1507`.

Resolver metadata chain:

- `/tmp/hg-wwheelhouse-payloads-e5uywviu/reasoning_gym-0.1.25-py3-none-any.whl:reasoning_gym-0.1.25.dist-info/METADATA:16`: `Requires-Dist: cellpylib==2.4.0`. Preimage: `tests/fixtures/hg_wresolver2/source/wheels/reasoning-gym/reasoning_gym-0.1.25.dist-info/METADATA:16`.
- `/tmp/hg-wwheelhouse-payloads-e5uywviu/cellpylib-2.4.0-py3-none-any.whl:cellpylib-2.4.0.dist-info/METADATA:18`: `Requires-Dist: matplotlib>=3.0.2`. Preimage: `tests/fixtures/hg_wresolver2/source/wheels/cellpylib/cellpylib-2.4.0.dist-info/METADATA:18`.
- `/tmp/hg-wwheelhouse-payloads-e5uywviu/matplotlib-3.8.4-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl:matplotlib-3.8.4.dist-info/METADATA:42`: `Requires-Dist: contourpy >=1.0.1`. Preimage: `tests/fixtures/hg_wresolver2/source/wheels/matplotlib/matplotlib-3.8.4.dist-info/METADATA:42`.

Reasoning Gym eagerly imports game_of_life and cellpylib; contourpy is a deferred contour-operation import in retained Matplotlib. Matplotlib 3.8.4 is the retained candidate, not a root source pin. The normal contourpy metadata edge remains required even without calling contour operations.

## spreadsheetbench

Root requirement: `openpyxl==3.1.2`, declared at `data/datasets/spreadsheetbench.py:285`. Missing resolver requirement: `et-xmlfile`.

Scoring/source route:

- `data/datasets/spreadsheetbench.py:234`: `"python3", "check.py",`. Preimage: `tests/fixtures/hg_wresolver2/source/repository/data/datasets/spreadsheetbench.py:234`.
- `data/datasets/spreadsheetbench/verify/check.py:169`: `import openpyxl`. Preimage: `tests/fixtures/hg_wresolver2/source/repository/data/datasets/spreadsheetbench/verify/check.py:169`.
- `data/datasets/spreadsheetbench/verify/check.py:260`: `import openpyxl`. Preimage: `tests/fixtures/hg_wresolver2/source/repository/data/datasets/spreadsheetbench/verify/check.py:260`.

Actual missing-module import site: `/tmp/hg-wwheelhouse-payloads-e5uywviu/openpyxl-3.1.2-py2.py3-none-any.whl:openpyxl/xml/functions.py:36`: `from et_xmlfile import xmlfile`. Preimage: `tests/fixtures/hg_wresolver2/source/wheels/openpyxl/openpyxl/xml/functions.py:36`.

Resolver metadata chain:

- `/tmp/hg-wwheelhouse-payloads-e5uywviu/openpyxl-3.1.2-py2.py3-none-any.whl:openpyxl-3.1.2.dist-info/METADATA:26`: `Requires-Dist: et-xmlfile`. Preimage: `tests/fixtures/hg_wresolver2/source/wheels/openpyxl/openpyxl-3.1.2.dist-info/METADATA:26`.

et_xmlfile is imported on openpyxl's no-LXML branch. openpyxl declares et-xmlfile unconditionally and without a version bound; optional lxml availability does not remove the resolver metadata obligation.

Branch conditions are preserved at wheel `openpyxl/xml/functions.py:13` and `:27`, with LXML availability computed at `openpyxl/xml/__init__.py:26`. Resolving et-xmlfile remains necessary for the declared dependency graph even when an installed optional lxml provider would bypass its runtime import.

## Source changes since the inherited packet

The fresh current-source lines supersede the old report citations: Jericho command/pin/wrapper import are now 257/305/49; SpreadsheetBench command/pin/openpyxl imports are now 234/285/169 and 260. Their exact bytes and hashes are preserved. Two failed initial generator attempts are retained in `source/generate-attempt1.*` and `source/generate-attempt2.*`; they rejected stale line assumptions before the successful audit. These failures are evidence-collection assertions, not resolver or task scores.

No registry, journal, old fixture, run or frozen receipt was modified by this source audit. No blockers or gates changed.

## Acquired-candidate platform check

The parent acquisition packet supplies these candidate metadata preimages. This audit independently rereads and hashes METADATA/WHEEL and checks each selected version against the missing requirement, Requires-Python against the actual interpreter, and WHEEL tags against the freshly computed target tags. All checks return true in `source-audit.json` and `source/generate.stdout.txt`. Artifact acquisition/digest and network-denied solver claims belong to the parent receipt.

- `spacy==3.8.16`: Requires-Python `<3.15,>=3.9`; WHEEL tags `cp312-cp312-manylinux_2_24_x86_64`, `cp312-cp312-manylinux_2_28_x86_64`.
- `contourpy==1.2.0`: Requires-Python `>=3.9`; WHEEL tags `cp312-cp312-manylinux_2_17_x86_64`, `cp312-cp312-manylinux2014_x86_64`.
- `et-xmlfile==1.1.0`: Requires-Python `>=3.6`; WHEEL tags `py3-none-any`.
