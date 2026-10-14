# Task 230 — Terminal-Bench public verifier source audit

**Disposition: official runner identity and reference-source metadata established;
official selected-task scorer, historical version binding and offline dependency
closure remain incomplete. No source fixture or execution authorization added.**

Worktree: `/tmp/hg-codex-230`, base
`61e7f82` (see the exact base in the
[evidence inventory](task-230-terminal-source-evidence.json)). Audit date:
2026-10-14. Production code, adapter declarations, admission gates, main and the
parent integration journal are unchanged.

## Official source and version identity

The adapter declares dataset commit
`2fd12b88aafdd04a52c298e3940bcb189f9766d6` in
[`data/terminal_bench.py`](../data/terminal_bench.py). Public GitHub Git metadata
resolves that commit in `harbor-framework/terminal-bench-2` to root tree
`ec7c02c7f0b59ce8ed2f7c88d1e70cda7427edfa`.
The [README at that exact commit](https://github.com/harbor-framework/terminal-bench-2/blob/2fd12b88aafdd04a52c298e3940bcb189f9766d6/README.md)
identifies Terminal-Bench 2.0 and explicitly directs users to Harbor to evaluate
it. Its installation examples are **unversioned**. They establish the official
framework relationship, not an exact historical or locally installed runner.
No README command was executed.

The public `harbor-framework/harbor` repository identifies itself as an agent
evaluation framework. The observed latest release is `v0.24.0`, published
2026-10-05. The tags response maps it to immutable commit
`b53b8134e1241686dca7759af188f987ecc48e8b`, whose Git commit message and project
version both identify 0.24.0. Root tree:
`53f5cf4afcf87f9fd53e183e13b06bdfc8c63cb4`.

**This release is an explicitly selected audit reference.** Neither the dataset
README nor the local adapter binds the historical run to 0.24.0. A mutable tag,
release `target_commitish="main"`, or an unversioned install instruction cannot
supply that missing binding. No installed Harbor package, dataset registry
mapping or external dataset checkout was inspected.

The historical `laude-institute/terminal-bench` repository metadata now returns
`harbor-framework/terminal-bench-1`. That legacy repository is a separate code
line; its verifier is not evidence of the TB2 runner. Only its repository
metadata was requested.

## What the acquired official verifier actually establishes

Reviewed unchanged
[`src/harbor/verifier/verifier.py`](https://github.com/harbor-framework/harbor/blob/b53b8134e1241686dca7759af188f987ecc48e8b/src/harbor/verifier/verifier.py)
and its
[`base.py`](https://github.com/harbor-framework/harbor/blob/b53b8134e1241686dca7759af188f987ecc48e8b/src/harbor/verifier/base.py)
as source, without importing or executing them.

| Reference-source observation | Evidence and practical limit |
| --- | --- |
| Grading belongs to task-owned scripts. | `Verifier._resolve_tests`, lines 124–163, discovers task/step test paths or selects tests already in a verifier image. `verify`, lines 172–187, uploads the resolved test directories when required. These are runner mechanics, not the task's correctness predicate. No test directory or test body was retrieved. |
| The runner builds and delegates script execution. | Lines 205–232 call `build_execution_command` and environment methods. The command-building helper, environment implementation and dispatch/factory bodies remain unacquired. The exact shell invocation is therefore not established by these two files alone. |
| Reward files carry the grade. | Lines 257–268 prefer a JSON reward file over text, raise `RewardFileNotFoundError` when both are absent and return `VerifierResult(rewards=...)`. Text parsing at lines 67–87 returns a numeric `reward`; lines 89–122 parse JSON. Empty, malformed and non-finite values have explicit error paths. No task pass rule or benchmark aggregation is established. |
| Environment and result handling have further dependencies. | Source imports include task/trial/result models, an environment base, environment resolution, command helpers and logging. Seven directly imported internal module bodies remain absent. The two acquired files are not a closed executable verifier. |

`VerifierResult`'s body, verifier factory, metric mean/factory, task configuration
and path implementations were not acquired. Tree metadata pins several of these
files but cannot substitute for their source. No claim is made about the full
runner's failure accounting, denominator, aggregate metric, historical behavior
or exact installed configuration.

## Adapter shell and tests are a separate identity

The local adapter declares `argv=["bash", "/tests/test.sh"]`, copies a checkout
task's `tests/` into `/tests`, reads `/logs/verifier/reward.txt` and asks for
`/logs/verifier/ctrf.json` as evidence. These declarations were reviewed as
platform source; the adapter was never imported.

[`eval/verifier.py`](../eval/verifier.py) parses a numeric text reward and
constructs `passed=bool(score)`. Its container-state path also uses its own CTRF
evidence handling. The acquired Harbor source instead exposes a named-reward
result and JSON-before-text precedence. These observations distinguish the
implementations; they do not establish either equivalence or a measured scoring
disagreement on the selected dataset. Task scripts, their dependencies, the
result model and aggregation logic are still needed for such an assessment.

The adapter and verifier comments contain historical claims about task counts,
dependency installation and script exit codes. **Those claims were not
independently verified here.** Generic runner source cannot establish how every
task's shell or Python tests behave.

## License and dependency closure

Seven public files were acquired, totaling 1,131,599 decoded bytes: TB2's root
README and LICENSE; Harbor's LICENSE, `pyproject.toml`, `uv.lock`, concrete
verifier and base verifier. Every file's decoded size, SHA-256 and Git blob
SHA-1 matches the corresponding pinned Git tree entry. The evidence inventory
records commit-qualified source URLs and acquisition attempts. Original source
bytes and raw responses remain in the ignored, worktree-local audit cache;
they are not a committed source fixture or an approved scorer bundle.

| Closure dimension | Verified | Still missing |
| --- | --- | --- |
| Root licenses | Both exact root LICENSE files contain Apache-2.0 and have SHA-256 `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`. Harbor declares `license="Apache-2.0"`, `license-files=["LICENSE"]`. Neither reviewed root tree has a `NOTICE` entry. | Transitive package, workspace, OS/image, task-specific license and notice inventory. Root licensing alone does not close these obligations. |
| Framework declaration | Harbor 0.24.0 requires Python `>=3.12`, declares 23 core requirements, and builds with `uv_build>=0.8.4,<0.9.0`. Exact requirements are preserved in the metadata inventory. | Concrete selected runtime, build inputs, complete source import graph and ABI compatibility. Optional backends and development requirements are not assumed necessary for grading. |
| Lock metadata | The unchanged `uv.lock` parses as format 1/revision 3 with 345 package records. It includes editable Harbor, `packages/harbor-langsmith` and `packages/rewardkit`. | The 345 records cover the workspace and optional/development dependencies; they are not a minimal verifier closure. No workspace packages, wheels, sdists, package license corpus or OS artifacts were acquired or installed. |
| Task scorer | The official framework delegates to task-owned scripts. | Exact selected test/scorer bytes, shell/Python/native tools, downloads, image/runtime files, dependency hashes and their licenses. Task/test retrieval was excluded by this task. No offline closure can be certified from the permitted acquisition alone. |

The internal module bodies missing from the acquired verifiers are enumerated
with available tree identities in the JSON inventory. Project and lock metadata
are genuine declarations, not evidence that an offline installation or official
scorer invocation succeeds. A lockfile does not include task-script package
installation or image contents merely because it belongs to the framework.

## Live admission obligations remain independent

The [existing integration review](../reports/TERMINAL_INTEGRATION_REVIEW.md) and current
local source continue to describe a snapshot-based platform path:
[`eval/container_state.py`](../eval/container_state.py) stops and commits actor
state; the verifier creates a grader from that snapshot. That is separate from
official runner provenance and from a bounded artifact-only export.

| Obligation | Task 230 disposition |
| --- | --- |
| Complete official scorer and selected source provenance | Open. Framework identity is known; task-specific bytes, runtime/dependency closure and historical runner binding are not. |
| Trusted pristine runtime | Open. No created-runtime observation, independently sealed scorer image or ABI check was obtained. Public source retrieval cannot authenticate a live runtime. |
| Artifact-only state export | Open. No selected-file projection, quiescence/export binding or export receipt was produced. Whole-filesystem snapshots do not establish that contract. |
| Filesystem byte/inode quotas and resource ownership | Open. No host, backend, mount, quota or observer state was queried or changed. |
| Production enforcement and official execution | Open. No production wiring was changed, scorer invoked or diagnostic admitted. `benchmark_blockers` still retains its unconditional task and execution blockers. |
| Snapshot lifecycle and cleanup | Open. No workload ran and no runtime cleanup/absence receipt exists. Worktree-local retrieval files are not a production cleanup receipt. |

Future closure requires independently reviewed selected-task source custody,
version/registry/image binding and complete dependencies/licenses, followed by
separate runtime/export/quota/lifecycle evidence and an authorized official
execution. Nothing in this audit promotes a synthetic control into H0 admission.

## Failed attempts, validation and scope

There were 39 code/metadata HTTP requests: 17 completed and 22 failed. The initial
Git commit request using `main` returned HTTP 404; the release SHA request
succeeded. A recursive root-tree request ended with `IncompleteRead`; separate
root and recursive `src/` tree requests succeeded with complete responses.
Eight helper-source Git API requests returned HTTP 403 rate limits; twelve
commit-qualified raw-source requests failed with connection resets. These
failures are recorded, not filled with reconstructed helpers. They are not
evidence that the public source does not exist, and are not benchmark failures
or scores. No credentials, rate-limit circumvention or alternate benchmark
payload acquisition was used.

Validation checked all seven source blob identities and sizes, parsed both
Python source files without executing them, parsed project/lock TOML, and checked
local source pins. Existing offline synthetic suites passed:

```text
env PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q \
  tests/quality/test_terminal_artifact_admission.py \
  tests/quality/test_scorer_bundle_codex170.py \
  --basetemp=/tmp/harnessgrad-pytest-codex230-task230-source-audit-pytest-tmp \
  -p no:cacheprovider
84 passed in 0.33s
```

These tests use inert authored fixtures and guard subprocess/socket execution.
They validate existing local contract behavior, not acquired Harbor execution
or official scorer completeness. No new synthetic source fixture was fabricated.
Metadata consistency checks and `git diff --check` also passed. The optional
[local review page](_build/task230-source-audit/overview.html) rendered with
three panels and zero prose warnings; parsing found no remote active assets.
Its draft, generated page, source cache and captured test output remain ignored
under this worktree's `docs/_build/task230-source-audit/` directory.

Eligible task count is unknown; selected/executed tasks and trials are zero.
Invalid/unmeasured trial counts are zero because there were no trials. No
endpoint, run ID, model, selected-task manifest, benchmark measurement, runtime
budget or cleanup receipt exists for this audit. All authorization and
measurement flags in the inventory are false.

All writes stayed in this isolated worktree. No tasks, tests, solutions, dataset
archives, package artifacts or images were downloaded. No external dataset root,
task instruction or test payload was opened; no upstream code, Docker, model or
H0 ran. Parent review, merge and journal integration remain separate.
