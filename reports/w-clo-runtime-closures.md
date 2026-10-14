# Dataset scorer byte closures — w-clo-runtime

**Shared `scorer-offline-closure` remains open. Complete pinned offline closures established: none.**
All 23 surveyed datasets now have explicit `partial-byte-pins` records, including
available scorer/gold/runtime byte identities and findings for unavailable pins.
These records do not constitute portable offline installations or runtime approval.
Inspection started at `19b700d`, in registered worktree `/tmp/hg-clo2`.

## Scope and evidence semantics

The scope was derived from `reports/w-shared-topology-survey.md`, not the requested
minimum list: **19 `actor-workdir` command routes and four `snapshot-service`
routes**. This covers all 23 datasets referring to the shared blocker. AgentDojo
is outside that survey/shared scope. The survey describes the route selected by
source wiring, not a measurement proving every dataset has run successfully.
Chess additionally has a separate trusted-platform `in-process` controller.
Current source and its retained incomplete receipt identify that class; the older
survey's recorded-unknown note is preserved as historical context.

Each linked record contains exact adapter/check/helper entrypoint `path`, `line`,
`symbol` and newly computed full-file `sha256`; all reached QA records include
`data/scaffolds/qa/verify/check.py` and `QASpec.verifier`. Native/container records
explicitly identify their dataset-specific check instead. Terminal-Bench adds
every available task shell entrypoint and `test_*` function; AppWorld adds all
732 available host task evaluator entrypoints. The installed AppWorld class body
is unavailable and is explicitly not pinned. Literal source lines are collected
in `tests/fixtures/hg_wclo_runtime/evidence-locators.json`.

Hashes are computed from this checkout's files or explicitly identified absolute
external dataset/installed-runtime paths. External payloads are not copied into
the fixture. Source revision/archive/image declarations are labelled separately
from measured content hashes. Available archive-member comparisons strengthen
the QA extracted-file provenance; content matches do not establish independent
canonical custody or official execution. Missing preimages have null hashes.
No historical hash was reused as a newly computed identity.

## Per-dataset closure table

In addition to each row's findings, **all rows lack a complete execution-bound
transitive runtime/ABI and offline installation closure, and the complete trusted
lifecycle/resource/cleanup observations required by the shared action**. Generated
per-task gold/input custody remains unbound unless an individual retained artifact
is explicitly identified. A source-pool hash is not a hash of staged `gold.json`.

| Dataset / record | Source route | Byte identities now pinned | Still unpinned or unestablished |
| --- | --- | --- | --- |
| [alfworld](../tests/fixtures/hg_wclo_runtime/datasets/alfworld.json) | actor-workdir | Adapter/check/helpers; 134 eligible game and matching trajectory sources; one retained stripped selected input; fast-downward/imported package bytes; existing noop receipt copies | Other stripped verifier inputs and custody; native ABI, enforced caps and successful action replay evidence. Existing raw noop zero has unmeasured publication. |
| [appworld](../tests/fixtures/hg_wclo_runtime/datasets/appworld.json) | snapshot-service, mounted service state | Adapter/check/service; encrypted release bundle/pool; 732 evaluator functions and available host expected-data bytes; configured image reference retained as declaration | Installed `world.evaluate()` body, image interpreter/packages/ABI/data; unpacked-to-bundle/image equivalence; service recording custody, quiescence and live lifecycle evidence. |
| [bfcl_v3](../tests/fixtures/hg_wclo_runtime/datasets/bfcl_v3.json) | actor-workdir, QA | Adapter/shared check; simple/irrelevance/possible-answer files and archive-member matches; archive bytes | Configured selected index absent; implemented name-only diagnostic is explicitly not official BFCL scoring; official scorer closure/execution absent. |
| [bird_minidev](../tests/fixtures/hg_wclo_runtime/datasets/bird_minidev.json) | actor-workdir | Adapter/check; gold SQL, task mapping/schema, all 11 SQLite DBs; evaluation/source archives | Generated per-task SQL custody, native SQLite/runtime binding and live evidence; local EX transcription is distinguished from upstream exception behavior. |
| [chessbench_puzzles](../tests/fixtures/hg_wclo_runtime/datasets/chessbench_puzzles.json) | actor-workdir, QA; separate in-process controller | Adapter/shared check/controller; chess 1.11.2 identities; CSV/source archive and upstream member; retained incomplete controller receipt | Command-class runtime controls and selected gold custody; interactive terminal exchange/measurement absent. Strict replay, unchecked replay and interactive metrics cannot be conflated. |
| [ds1000](../tests/fixtures/hg_wclo_runtime/datasets/ds1000.json) | actor-workdir, scorer child | Adapter/check/official execution runner; release tests, four offline CSVs and environment/source bytes; included/excluded import inventory | Scientific native ABI and official-stack differences; actor-visible `context.json` custody; arbitrary candidate imports and child/scratch cleanup. 926 included / 74 excluded rows remain explicit. |
| [fever](../tests/fixtures/hg_wclo_runtime/datasets/fever.json) | actor-workdir, QA | Adapter/shared check/evidence helpers; local `valid.jsonl` content identity and revision declaration | Adapter had no file digest; independent canonical export identity and official execution remain unestablished. |
| [gaia](../tests/fixtures/hg_wclo_runtime/datasets/gaia.json) | snapshot-service, actor snapshot | Adapter/check; official local `question_scorer`; pool and released metadata Parquet bytes; matching declared source pins | Floating image/base, actual snapshot Python/NumPy/OpenBLAS/ABI; generated gold/custody and runtime observations. **Do not provision or run GAIA remains in force.** |
| [gsm8k](../tests/fixtures/hg_wclo_runtime/datasets/gsm8k.json) | actor-workdir, QA | Adapter/shared check; train/test Parquet matching declared pins; host PyArrow identities | Import-time loader/Arrow ABI and sandbox visibility; selected gold custody. Adapter numeric comparison retains documented reference differences. |
| [hotpotqa](../tests/fixtures/hg_wclo_runtime/datasets/hotpotqa.json) | actor-workdir, QA | Adapter/shared check/evidence helpers; fullwiki validation Parquet; host PyArrow identities | Conditional import-time loader visibility/ABI and official joint answer/support execution. |
| [jericho](../tests/fixtures/hg_wclo_runtime/datasets/jericho.json) | actor-workdir | Adapter/check/helpers; 56 ROMs, game table, constructor-dependent verb counts and libfrotz; imported runtime files | ROM source commit; generated seed/denominator custody, native resolution and runtime evidence. Absent sherbet remains excluded; lazy spaCy tokenizer/download is not plain replay. |
| [livecodebench](../tests/fixtures/hg_wclo_runtime/datasets/livecodebench.json) | actor-workdir, scorer child | Adapter/check/official executor and aggregation; 1,055 decoded test files/pool; six release shards and archive | Release-to-decoded transformation custody; NumPy ABI, candidate imports, selected-input/timeouts/child cleanup. Executor source imports NumPy, not pyext. |
| [musique](../tests/fixtures/hg_wclo_runtime/datasets/musique.json) | actor-workdir, QA | Adapter/shared check; dev JSONL, archive and evaluator member identity | Canonical mirror identity; default answer/support and legacy answer-only modes need separate runtime identity/evidence. |
| [physicsquestions](../tests/fixtures/hg_wclo_runtime/datasets/physicsquestions.json) | actor-workdir, QA | Adapter/shared check; extracted CSV matching recomputed ReWOO archive member | Official scoring execution and native/input custody evidence. |
| [reasoning_gym](../tests/fixtures/hg_wclo_runtime/datasets/reasoning_gym.json) | actor-workdir, QA | Adapter/shared check/generation source; pool; installed eager-import and static-source/package identities | Family-specific lazy imports/resources and native closure. Distribution version 0.1.25 differs from installed `__version__` string 0.1.19; neither is treated as runtime attestation. |
| [scienceworld](../tests/fixtures/hg_wclo_runtime/datasets/scienceworld.json) | actor-workdir, JVM | Adapter/check/helpers; simulator JAR/task/object data/fold; complete available prepared JRE tree/archive and package identities | Fold-origin source custody, host ABI/override behavior, JVM/Py4J bidirectional connectivity and process/error-path lifecycle. Expected score is a simulator predicate, not a separate answer file. |
| [sportsunderstanding](../tests/fixtures/hg_wclo_runtime/datasets/sportsunderstanding.json) | actor-workdir, QA | Adapter/shared check; extracted CSV matching recomputed ReWOO archive member | Official scoring execution and native/input custody evidence. |
| [spreadsheetbench](../tests/fixtures/hg_wclo_runtime/datasets/spreadsheetbench.json) | actor-workdir, conditional LibreOffice | Adapter/check; 400 gold workbooks, cell-range metadata and release archive; openpyxl import identities and LibreOffice launcher | Full LibreOffice/plugins/fonts/ABI/configuration and formula controls; transcription lacks upstream commit declaration; generated task metadata custody. |
| [strategyqa](../tests/fixtures/hg_wclo_runtime/datasets/strategyqa.json) | actor-workdir, QA | Adapter/shared check; extracted CSV matching recomputed ReWOO archive member | Official scoring execution and native/input custody evidence. |
| [tau_bench](../tests/fixtures/hg_wclo_runtime/datasets/tau_bench.json) | snapshot-service, actor snapshot | Adapter/check/vendored hash/tools; all 165 committed GT files; upstream reward/task/table bytes as derivation evidence | **Required committed `db/airline.json` and `db/retail.json` are absent.** Upstream tables do not substitute. Floating image, actual snapshot Python/stdlib/OpenSSL/libc and state/log lifecycle evidence remain unpinned. |
| [terminal_bench](../tests/fixtures/hg_wclo_runtime/datasets/terminal_bench.json) | snapshot-service, actor snapshot | All 89 task manifests/checks/test-function locations/build contexts; 285 test/expected files; matching checkout commit; historical w-net receipt copies | Per-task images/interpreters/wheels/system ABI; online apt/curl/uv/uvx/data acquisition; controls for remaining runtimes. One official raw scorer execution does not establish measured comparable publication. |
| [triviaqa](../tests/fixtures/hg_wclo_runtime/datasets/triviaqa.json) | actor-workdir, QA | Adapter/shared check; validation/train Parquet matching declared pins; host PyArrow identities | Incidental loader/Arrow ABI, sandbox visibility and selected gold custody. |
| [twowikimultihopqa](../tests/fixtures/hg_wclo_runtime/datasets/twowikimultihopqa.json) | actor-workdir, QA | Adapter/shared check; dev/alias/witness bytes, source archive and evaluator member | Canonical official release identity remains inferred from witness; witness is not scoring input. Official execution and selected-gold custody remain unestablished. |

## Interpreter, packages and prior evidence

`tests/fixtures/hg_wclo_runtime/host-runtime.json` identifies the inspection
interpreter at `/mnt/8t/xubuqiang/anaconda3/bin/python3`, CPython **3.12.4**,
SOABI `cpython-312-x86_64-linux-gnu`, by actual executable hash. It also binds
available standard-library files and installed distribution payloads. Package
records contain installed versions, newly hashed METADATA/RECORD files, requirements
and a deterministic digest of every available RECORD-listed non-bytecode member.
The algorithm and unavailable-member handling are recorded in `build_host.py`.

This catalog includes observed import roots plus a conservative metadata dependency
superset. It is not a claim that every catalog package is imported by every scorer.
DS-1000's excluded-only imports, Jericho's dormant tokenizer requirements and QA
loader imports are distinguished explicitly. Available package payload hashes do
not provide offline wheels, installation provenance, future PATH/import integrity
or a snapshot interpreter identity. For the four container/service datasets,
actual installed interpreter paths/versions/package hashes unavailable from current
bytes are **unknown**, with no host substitution. Image digest references retained
from source are declarations, not image hashes computed by this inspection.

`import-byte-pins.json` rehashes files selected by earlier import-only observations
without rerunning those imports. `native-abi-byte-pins.json` hashes native objects
and static ELF dependency candidates, including interpreter/stdlib and available
LibreOffice objects. Candidate resolution is not observed loader resolution;
dynamic loads, task executables, platform ABI and enforcement remain incomplete.

The old `hg_wtbdep/SHA256SUMS` lists **810 files: 125 present and matching after
recomputation, 685 absent** in this checkout. `prior-evidence-audit.json` names each
one. Missing image projections, package metadata and Terminal-Bench appendices were
not restored, fetched, fabricated or treated as valid pins. Existing historical
receipts, runs and archives were not changed. No `runs/` tree was accessed.

## Shared blocker decision — remains open

The blocker's original `next_action` is preserved verbatim:

> Provision dataset-specific pinned scorer closures and class-specific runtime evidence, including complete transitive image/ABI dependencies, official provenance/execution and trusted lifecycle/resource/cleanup observations; validate live controls before pilots, preserve snapshot/service connectivity and compare only matching known classes.

It is **not satisfied**. No complete portable offline closure is established for
any of the 23 datasets. Complete transitive image/interpreter/native dependencies,
offline installation media and selected materialized-input binding remain absent;
Tau additionally lacks the two required clean DB artifacts. Official provenance
or official scorer identity/execution remains unresolved where explicitly listed.
Matching live controls and complete trusted lifecycle/resource/cleanup observations
have not been established across these datasets/classes.

The retained `w-net` copies prove one official Terminal-Bench raw scorer reward
and image/resource/snapshot/cleanup observations for `openssl-selfsigned-cert`.
Its published diagnostic remains `score=null`, one unmeasured trial,
`policy_enforcement_not_observed`. ALFWorld's retained noop raw zero similarly has
unmeasured publication and incomplete enforcement/closure. Chess's separate
controller receipt has zero submissions and `answer_receive_failed`; it is not a
completed measurement. None supplies another task's runtime closure or authorizes
pilot expansion. Snapshot/service connectivity and matching-known-class comparison
requirements remain intact; no new runtime or comparison was attempted here.

Registry change: append these precise partial-closure observations and this report
to the shared blocker's evidence. Its status, original observation, `next_action`,
all dataset-specific blockers/refusals and every historical record are preserved.
No dataset-specific text change was warranted: these inventories do not discharge
the separate existing dataset requirements.

## Validation and review

`reports/w-clo-runtime-validation.txt` records exact collection/check commands and
outputs. Collection uses AST/metadata/archive reads and byte hashing, without
adapter/scorer imports, tasks, worlds, models, GPUs, containers or endpoint calls.
The parent reviewed the three isolated worktree diffs, corrected Jericho auxiliary
constructor-dependency wording, merged only fixture commits into `wg-clo2`, and
recomputed their outputs/byte identities. Production scoring code is unchanged.
The fixture-wide `SHA256SUMS` covers every new fixture file except itself.
Registry and focused source-only registry checks are recorded in validation.
