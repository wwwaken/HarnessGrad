# Repository architecture

This is the repository map for the current source tree. Start with the
[area map](#area-map), then follow the links to implementation files. The
[interface specification](../INTERFACE.md) defines the measurement contract;
this page describes where its implementation lives and which way dependencies
should point.

Navigate: [areas](#area-map) · [execution runtime](#runtime-navigation) ·
[datasets](#dataset-navigation) · [import edges](#observed-import-edges-and-exceptions) ·
[known structural problems](#known-structural-problems).

`A -> B` means **A depends on B**, not that data flows from A to B. A
**leaf/contract** provides shared definitions or low-level helpers without
importing repository consumers. A **consumer** composes those definitions or
executes work. These are module-level roles: a package name alone does not
establish a boundary. The allowed directions below are maintenance rules;
[observed exceptions](#observed-import-edges-and-exceptions) are called out
explicitly rather than presented as a clean, enforced layering.

The enforced dependency directions, the observed import edges and their reviewed
exceptions are recorded separately in [import direction](import-direction.md),
with an automated guard in `tests/quality/test_import_direction.py`.

## Area map

| Area | Purpose and entry points | Role | Allowed dependency direction |
| --- | --- | --- | --- |
| [Root entry points](../driver.py) | `driver.py` parses arguments and composes dataset loading, scheduling, measurement and recording. [install.sh](../install.sh) provisions/checks prerequisites. | Consumers/composition roots. | `driver -> harnessgrad` orchestration/loops, `eval`, dataset registry, `ckpt` and operational helpers. Lower layers must not depend on the driver to implement ordinary execution. |
| [harnessgrad/runtime/](../harnessgrad/runtime/) | Eight-stage event types, recording, schema/semantic validation and the legacy-method compatibility wrapper; start at [events.py](../harnessgrad/runtime/events.py) and [validator.py](../harnessgrad/runtime/validator.py). | Leaf/contracts, despite the word “runtime.” | Consumers -> these contracts; their modules may use sibling definitions and external libraries, never `eval`, driver, tools or method implementations. See the package-initialization caveat below. |
| [harnessgrad/config/](../harnessgrad/config/) | Typed configuration declarations in [areas.py](../harnessgrad/config/areas.py), loading/snapshots in [loader.py](../harnessgrad/config/loader.py). | Leaf/contracts. | Runtime and orchestration -> config; config -> its own declarations and standard library. No imports back into runtime consumers. |
| [Top-level harnessgrad/*.py](../harnessgrad/) | Platform orchestration: [environments.py](../harnessgrad/environments.py), [methods.py](../harnessgrad/methods.py), [channel.py](../harnessgrad/channel.py), [records.py](../harnessgrad/records.py), identity and budget integration. | Consumers of `eval/` as an area, with contract aliases and standalone helpers mixed in. **Not a leaf package.** | Orchestration -> `eval`, config/contracts, `ckpt`, dataset registry and lower-level orchestration helpers. Do not infer permission for `eval ->` these orchestration modules. |
| [harnessgrad/loops/](../harnessgrad/loops/) | Scheduling in [mode_a.py](../harnessgrad/loops/mode_a.py) and [eval_side.py](../harnessgrad/loops/eval_side.py); Mode B coordination also lives in `driver.py`. There is no `loops/mode_b.py`. | Consumers. | Driver -> loops -> orchestration helpers, `eval.runner`, candidate validation and `ckpt`. Runtime primitives must not import schedules. |
| [harnessgrad/store/](../harnessgrad/store/) | Run-record validation, reading and certification in [schema.py](../harnessgrad/store/schema.py). | Leaf/record contract and reader. | Record consumers, validators and web read API -> store; store -> standard library, not execution/scheduling code. |
| [eval/](../eval/) | **Platform execution runtime, despite the name**: task execution, environments, model gateway, verification/scoring, admission, progress and traces. Start at [runner.py](../eval/runner.py). | Consumer of low-level contracts/helpers; provider to orchestration. Not a test suite. | Orchestration -> `eval`; `eval` -> runtime peers, config, `ckpt` and external execution backends. Keep method algorithms and scheduling above it. Existing imports from `tools` are listed below. |
| [data/](../data/) | **Shared scaffolding PLUS 28 dataset adapters**, fixture modules, and dataset-specific preparation/check/control assets. This directory mixes infrastructure with integrations. Start at [registry.py](../data/registry.py) and [qa/](../data/qa/). | Mixed: scaffold/contracts, adapter consumers and runtime-consuming controls. **Not a leaf directory.** | Driver/tools -> registry -> selected `data.<name>` adapter; adapters -> shared scaffolding. Controls may call `eval`; existing adapter/reporting coupling is listed below. Runtime should consume task/verifier declarations instead of discovering datasets itself. |
| [methods/](../methods/) | External improvement methods and controls, plus shared [protocol.py](../methods/protocol.py), editor/application helpers and per-method `run.py` entry points. | Consumers of method/harness exchange contracts; supplies candidates, not platform scores. | Platform invokes methods through subprocess entry points and JSON/artifacts. Methods -> their own helpers, supplied workspace/channel and declared model/tool dependencies; shared runtime compatibility contracts are available. Do not import method algorithms into the referee. |
| [base_harness/](../base_harness/) | Runnable starting artifacts: `loop`, `loop_plain`, `loop_rrsi_parse`, CLI/Codex/DSH wrappers, and `oracle` control. Each has `harness.json` and `agent.py`. See [writing a harness](writing_a_harness.md). | Consumers of task/model/file contracts; measured artifacts, not platform libraries. | Platform stages and executes manifest entry points; harnesses use their own code/dependencies and supplied task/environment contracts. No platform imports of harness implementation code. |
| [ckpt/](../ckpt/) | [git_state.py](../ckpt/git_state.py) stages, commits, restores and materializes harness states and manifests. | Low-level helper leaf. | Driver, orchestration and execution -> `ckpt` -> standard library/external Git. No reverse imports into runtime or orchestration. |
| [tools/](../tools/) | Operator CLIs/services for validation, datasets, model services, setup, reporting and inspection. [serve_ui.py](../tools/serve_ui.py) is the retained operations service; the frontend is in `web/`. | Mostly consumers, with shared runtime helpers mixed in. Not a leaf area. | Tools -> platform APIs/contracts and artifacts; services may launch driver subprocesses. Runtime reuse of selected helpers already exists, so do not assume a strict one-way `tools -> eval` boundary. |
| [improvers/](../improvers/) | [improvers.json](../improvers/improvers.json) catalogs improver configuration; [skill.md](../improvers/skill.md) is the default method-facing guidance. | Configuration/reference leaves, not Python implementations. | Resolver/channel code -> these data files; these files do not import platform code. |
| [adapters/](../adapters/) | Historical external-method replay/compilation route, with a separate RRSI measurement integration in [harnessgrad_domain/](../adapters/harnessgrad_domain/). These are **not dataset adapters**. | Historical consumers; domain integration is a runtime consumer. | Replay/compiler scripts -> external artifacts and their own helpers. Domain integration -> driver setup, dataset registry and `eval.runner`; core execution must not depend on this route. See [its status](../adapters/README.md). |
| [web/](../web/) | React/TypeScript SPA in [src/](../web/src/), Python read API in [server/](../web/server/), and fixture generation in [scripts/](../web/scripts/). | Consumers/observers of run records and schemas. | SPA -> HTTP/fixtures; read API -> stored run files and `harnessgrad.store.schema`. Launch-option discovery reads source/config files and probes driver help in a subprocess. Execution code must not depend on the frontend. |
| [tests/](../tests/) | [quality/](../tests/quality/) covers platform boundaries/integrations; [runtime/](../tests/runtime/) covers event/budget APIs; [blockers/](../tests/blockers/) and [fixtures/](../tests/fixtures/) hold focused checks and test material. Web also has colocated tests. | Test consumers. | Tests -> subjects under test and fixtures. Production code should not import test helpers; one existing tooling exception is listed below. |
| [reports/](../reports/) | Audit reports, evidence/receipt JSON, test transcripts and review summaries, **moved out of the repository root**. | Audit/evidence leaves, not executable libraries. | Reviews/documentation -> evidence artifacts. Some runtime/admission paths consume evidence files explicitly; those are file/receipt dependencies, not Python imports. Preserve provenance and avoid treating historical reports as current measurements. |
| [docs/](./) and root documentation | Architecture, setup, contributor guidance, contract proposals and onboarding/audit material; [README](../README.md), [INTERFACE](../INTERFACE.md), [DOWNLOADS](../DOWNLOADS.md) and [AGENTS](../AGENTS.md) are root references. | Documentation/reference contracts and evidence. | Readers/contributors -> documentation; documentation links to source/evidence. Schemas and evidence loaded as files are explicit artifact contracts, not executable dependencies. |
| `legacy/` | **Absent in this checkout.** Historical external-method code remains under `adapters/`; compatibility wrappers are under `harnessgrad/runtime/`. | No current area to classify. | Do not invent a dependency or migration destination under this name. |

## Runtime navigation

Follow these responsibilities within the flat `eval/` directory:

| Responsibility | Implementation |
| --- | --- |
| Execute a task and aggregate a task set | [runner.py](../eval/runner.py); container-filesystem task path in [container_state.py](../eval/container_state.py) |
| Build execution environments and harness dependencies | [container.py](../eval/container.py), [sandbox.py](../eval/sandbox.py), [harness_runtime.py](../eval/harness_runtime.py), [services.py](../eval/services.py) |
| Model access and transport | [modelgate.py](../eval/modelgate.py), [stepwise_transport.py](../eval/stepwise_transport.py), [unix_model_relay.py](../eval/unix_model_relay.py) |
| Run checks and interpret verdicts | [verifier.py](../eval/verifier.py), with declared task instructions in [task_contract.py](../eval/task_contract.py) |
| Validate candidate artifacts and admission evidence | [candidate.py](../eval/candidate.py), [runner_admission.py](../eval/runner_admission.py), [artifact_admission.py](../eval/artifact_admission.py), [scorer_admission.py](../eval/scorer_admission.py), [scorer_bundle.py](../eval/scorer_bundle.py) |
| Record execution facts and progress | [tracing.py](../eval/tracing.py), [progress.py](../eval/progress.py), [console.py](../eval/console.py); trace interpretation also lives in [trace.py](../eval/trace.py) |
| Measurement integrity and statistics | [integrity.py](../eval/integrity.py), [metrics.py](../eval/metrics.py), [diagnostic_policy.py](../eval/diagnostic_policy.py) |

The separate [eight-stage runtime guide](eight_stage_runtime.md) describes the
event protocol implemented by `harnessgrad/runtime/`. That contract layer is
distinct from the execution engine in `eval/`.

## Dataset navigation

The count **28** comes from top-level `data/*.py` modules declaring
`KIND = "dataset"`, not from counting directories or assuming every Python file
is an adapter. It includes refused/unavailable integrations; it is not a claim
that 28 datasets are ready to run. [registry.published()](../data/registry.py)
discovers declarations through imports, while the web read API's
[launch-option scanner](../web/server/launch.py) uses AST detection of a
zero-argument `load()` function. Those are different discovery mechanisms.

The dataset adapter modules are:

| Dataset adapter | Dataset adapter | Dataset adapter | Dataset adapter |
| --- | --- | --- | --- |
| [agentdojo](../data/agentdojo.py) | [alfworld](../data/alfworld.py) | [api_bank](../data/api_bank.py) | [appworld](../data/appworld.py) |
| [bfcl_v3](../data/bfcl_v3.py) | [bird_minidev](../data/bird_minidev.py) | [chessbench_puzzles](../data/chessbench_puzzles.py) | [ds1000](../data/ds1000.py) |
| [fever](../data/fever.py) | [gaia](../data/gaia.py) | [gsm8k](../data/gsm8k.py) | [hotpotqa](../data/hotpotqa.py) |
| [jericho](../data/jericho.py) | [livecodebench](../data/livecodebench.py) | [musique](../data/musique.py) | [nestful](../data/nestful.py) |
| [physicsquestions](../data/physicsquestions.py) | [reasoning_gym](../data/reasoning_gym.py) | [scienceworld](../data/scienceworld.py) | [sotuqa](../data/sotuqa.py) |
| [sportsunderstanding](../data/sportsunderstanding.py) | [spreadsheetbench](../data/spreadsheetbench.py) | [strategyqa](../data/strategyqa.py) | [tau2_bench](../data/tau2_bench.py) |
| [tau_bench](../data/tau_bench.py) | [terminal_bench](../data/terminal_bench.py) | [triviaqa](../data/triviaqa.py) | [twowikimultihopqa](../data/twowikimultihopqa.py) |

Shared infrastructure sits beside those adapters: registry/split handling,
[dataset.schema.json](../data/dataset.schema.json), [qa/base.py](../data/qa/base.py)
and QA verification/prediction helpers, [command_control.py](../data/command_control.py),
and the [command oracle harness](../data/command_oracle_harness/).
[demo.py](../data/demo.py), [probe_set.py](../data/probe_set.py) and
[broken_service.py](../data/broken_service.py) explicitly declare fixtures.
Same-stem directories such as `data/gaia/` contain supporting assets/scripts;
their presence does not add another dataset to the module count.

## Observed import edges and exceptions

The source tree was checked using Python AST imports (including relative and
function-local imports), with dynamic dataset loading and subprocess/file
boundaries inspected separately. The following concrete edges explain why a
single directory-level dependency DAG would be misleading:

- **Execution consumers:** `harnessgrad/environments.py -> eval.container` and
  `eval.harness_runtime`; `harnessgrad/records.py -> eval.metrics` and
  `eval.tracing`; `harnessgrad/channel.py -> eval.trace` and `eval.tracing`.
  Loops call `eval.runner`. These modules are above execution, not leaves.
- **Leaf initialization caveat:** source files in `harnessgrad/runtime/`,
  `config/` and `store/` do not import repository consumers. However,
  [harnessgrad/__init__.py](../harnessgrad/__init__.py) eagerly exports
  `trusted_runner`, which imports `eval.candidate`. An ordinary import of a
  leaf subpackage executes that parent initializer. Their source-level leaf
  status therefore does not imply an execution-free transitive import.
- **Top-level exceptions:** `protocol.py`, `events.py`, `validator.py` and
  `compat.py` re-export `harnessgrad.runtime` APIs; `budget_dispatch.py`,
  `code_metrics.py` and `policies.py` are standalone helpers. Treating all
  `harnessgrad/*.py` as consumers or all as contracts would both be inaccurate.
- **Runtime/tool back-edges:** `eval.candidate -> tools.validate_harness`,
  `eval.runner -> tools.improver`, and `eval.runner`/`container_state ->
  tools.web_gateway`. Tools also import runtime APIs. These reusable helpers
  currently live in the CLI directory.
- **Dataset/runtime coupling:** `data/appworld.py -> eval.appworld_reporting`;
  `data/command_control.py` and several dataset `control.py` scripts call
  `eval.runner`. The registry dynamically imports `data.<name>`. Thus neither
  all of `data/` nor the whole adapter/control surface is a leaf.
- **Methods and tests:** method scripts use shared local modules via their
  script search paths; `methods/compatibility.py` imports the runtime contract
  wrapper. [tools/validate_method.py](../tools/validate_method.py) imports
  `methods.protocol`, not a method algorithm.
  [tools/check_triviaqa_provenance.py](../tools/check_triviaqa_provenance.py)
  imports a test helper, an existing exception to the test-consumer direction.
- **Web boundary:** `web/server/readapi.py -> harnessgrad.store.schema`;
  [launch.py](../web/server/launch.py) reads catalog/config files and invokes
  `driver.py --help` rather than importing the driver. The SPA consumes the
  resulting HTTP records or fixture records.

[Boundary tests](../tests/quality/test_boundaries.py) check specific platform
rules, including avoiding imports of method/harness implementations. They do
not establish every architectural direction in this map.

## Known structural problems

- **`adapters/` historical route:** its replay/compiler modules remain in an
  active-looking top-level directory. Its README marks the route unmaintained,
  while `harnessgrad_domain/` is explicitly excepted as the RRSI measurement
  integration. The name also collides conceptually with dataset adapters in
  `data/`.
- **`data/` scaffold-vs-adapter mixing:** registry/schema/QA scaffolding,
  fixtures, 28 adapter modules and dataset-specific scripts share one area.
  Moving or classifying the directory as a unit obscures their different roles
  and the existing control/reporting dependencies on runtime.
- **`eval/` flat layout:** execution, containers, verification, admission,
  transport, metrics, reporting and trace utilities are sibling modules. The
  name suggests evaluation-only code, but it contains the execution engine.
- **`trace.py`/`tracing.py` overlap:** `trace.py` parses harness replies and
  derives loop facts; `tracing.py` reads identity/usage, materializes fixtures
  and writes progress/task paths. Their trace-related names overlap even
  though the functions differ, and consumers such as `channel.py` need both.
- **`harnessgrad` half-leaf, half-consumer naming:** contracts/configuration
  and orchestration share one package; public aliases further blur the roles.
  The parent initializer additionally pulls execution code into leaf imports.
- **Root cleanup now under `reports/`:** audit/evidence files now live there;
  cleanup commit `ad57926` updates references to that location. Root-level
  report paths are historical; `reports/` is the evidence destination. Audit material also remains in
  `docs/`, so the move has not created a complete documentation/evidence split.
  Generated `runs/`, dataset payloads and web build output are separate from
  this source map; see [.gitignore](../.gitignore).
