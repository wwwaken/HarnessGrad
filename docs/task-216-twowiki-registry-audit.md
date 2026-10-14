# Task 216: 2Wiki registry audit after source-gate closure

The current registry correctly reflects the Codex 206 source-gate closure;
no registry correction is needed. Three source-only regression tests now protect
the remaining blockers, historical metric boundary and separate taxonomy axes.

Audit scope: isolated `/tmp/hg-codex-216`, starting commit
`82459cfa6d16c323ca40f21db2daf597921aedb3`. Reviewed local registry, taxonomy,
history baseline, source-gate review and code-only provenance fixture/tests.
No adapter import, benchmark payload or external receipt read, network request,
dependency installation, model execution or pilot was performed.

- `independent-evaluator-source` is absent from 2Wiki's active blockers and
  shared references. Its historical documentation remains intact.
- `ujson-native-offline-closure` remains `external` in
  `scorer-dependency-network`: wheel/sdist custody, installed-extension origin,
  native loader/transitive closure and fresh offline deployment remain open.
- `hub-data-provenance` remains `external` in `source-provenance`:
  Hub/release revision, split/selected manifest, alias custody, dataset rights
  and release-to-evaluator linkage remain open. Both external blockers cite the
  [source-gate review](task-206-twowiki-provenance-review.md).
- `recovery-comparability` remains `measurement`; all eight shared gates remain
  active and `production_authorized=false`.
- The original pilot record still reports 48 scored tasks, two invalids and mixed
  legacy Answer F1/structured Joint F1, with `status=partial-measurement`, unknown
  run ID and `effect=null`. Its full content matches the independently pinned
  historical baseline. No original/recovery receipt was reopened or rescored.
- Task capability remains `demand=evidence` × `surface=information_seeking`;
  harness `exercises=[context]` remains separate.

The new tests in
[test_dataset_blockers.py](../tests/quality/test_dataset_blockers.py) run under
the existing source-only guard, which denies adapter imports, external reads,
sockets and subprocess execution. The unchanged provenance suite verifies exact
source/license/metadata pins and executes both upstream evaluators with real
installed `ujson==5.10.0` on fabricated inputs.

Verification used CPython 3.12.4, Linux x86_64 and pytest 7.4.4:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tools/check_dataset_blockers.py
mkdir -p .scratch/registry-provenance-codex216-final
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q \
  -p no:cacheprovider --tb=short \
  --basetemp=/tmp/harnessgrad-pytest-registry-provenance-codex216-final-pytest \
  tests/quality/test_dataset_blockers.py \
  tests/quality/test_twowikimultihopqa_provenance_codex197.py
```

The checker exited 0: **28 datasets, 8 shared blockers, 11 historical records**,
`valid=true`, `production_authorized=false`. The final suite exited 0:
**90 passed in 3.10s** (52 registry, 38 provenance), with no failures or skips.
Before the additions, the suites passed **87 tests in 3.54s**. An initial
invocation omitted the scratch parent directory and exited 1 with 13 passes and
74 temporary-directory setup errors; creating the parent resolved those errors.

Byte comparisons against the starting commit confirm the registry JSON/docs,
history baseline, taxonomy, checker, adapter, provenance tests and every fixture
file are unchanged. The earlier integration journal remains an unchanged prefix.
`git diff --check` passes. Only the three regression tests, this audit receipt
and an appended journal entry are changed.

Cleanup receipt: both task-owned scratch roots were absent before creation and
removed after testing, then verified absent:
`.scratch/registry-provenance-codex216-baseline` and
`.scratch/registry-provenance-codex216-final`. This records local test cleanup;
source/synthetic checks establish no fresh dependency custody, benchmark result
or production runtime readiness. Parent review/integration remains separate.
