# Dataset blocker registry

[dataset-blockers.json](dataset-blockers.json) is the source-only review index of
all 28 publishable dataset declarations at this revision. It records task
`demand` and `surface` separately from harness `exercises`, using the literal
declarations in `tools/dataset_classes.py`. An exercise means score sensitivity
to a harness component, not an isolated measurement of that component. For
example, Jericho's `memory` exercise does not make its task demand `memory`.

Each dataset has explicit current `blockers` and references to applicable
`shared_blockers`. Expand those references to obtain its complete blocker list.
Every blocker has an ID, family, work status, observed finding, evidence paths
with text locators, and a next review or repair action. Multiple statuses can
apply to one dataset; no aggregate category replaces these independent facts.

| Status | Meaning |
| --- | --- |
| `code-solvable` | Repository implementation or documentation work can make progress; success still requires independent review. |
| `external` | Independent provenance, custody, source acquisition or an unavailable benchmark contract prevents closure. |
| `runtime` | Actual backend enforcement or lifecycle observations are missing; synthetic contracts do not close the gate. |
| `measurement` | Coverage, metric comparability, receipt review or current dataset-specific evidence remains unresolved. |

Families cover selected-only privacy/provenance, offline scorer closure, trusted
verification, artifact export, paired filesystem quotas, official scoring,
snapshot/cleanup, measurement and adapter-specific contracts. Refused datasets
remain represented with their refusal evidence. Adapters without a specific
journal entry have an explicit `journal-coverage` gap, rather than an inferred
passing status. AgentDojo's code-solvable selected metadata/privacy and defensive
detection review is closed by the synthetic controls documented in
[the Codex 180 report](../agentdojo-metadata-privacy-codex180-report.md). The active
`production-route-admission` runtime blocker preserves the separate unresolved
production route. No production `run_one` or H0 readiness follows from these
tests, and no adversarial execution is delegated by this index.

Repository evidence locators are validated against local source text. Absolute
external paths are citations from the journal and are never opened by the
checker. Historical scores and receipt outcomes remain reported claims; this
review did not authenticate the external artifacts or measure any benchmark.
The registry never authorizes production execution.

`historical_runs` preserves 11 incomplete, partially measured or pending-review
records, including both chess interruptions, both GAIA failures, Bird v4 and
v5's coverage limit, ScienceWorld's integrity failure, HotpotQA's stopped run,
the original invalid 2Wiki pilot, the initial AppWorld infrastructure smoke and
DS1000's pending review. Unknown run IDs stay `null`. All these registry effects
stay `null`; a later repair, recovery or measured zero does not rewrite them.
The committed [review baseline](../tests/fixtures/dataset_blockers/history-codex178.json)
is independently SHA-256 pinned by the checker. Existing records must remain
byte-equivalent in content; new historical records may be appended. Changing
the baseline pin is an explicit historical migration requiring review, not a
routine blocker-status update.

The review originally flagged two documentation conflicts: historical 50-task
pilot guidance in the platform log, and a chess audit sentence recommending an
already used recovery ID. The Chess future-launch guidance is now corrected,
so `recovery-id-conflict` is removed from the current blocker list. Every future
attempt must use a genuinely new unique run ID; never resume or overwrite any
used run ID, including `chess-pilot-h0-20261013` and
`chess-pilot-h0-20261013-recovery-01`. Both historical IDs, receipts and incomplete
statuses remain unchanged; termination and runtime gates remain unresolved.
Current planning follows `AGENTS.md`: a one-task/one-trial diagnostic after all
gates, separate receipt review, then at most `min(30, ceil(10% * eligible))` tasks
with one trial and one job for temporary reruns. A registry entry closes none of
those gates.

Validate without importing adapters or loading a task pool:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tools/check_dataset_blockers.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q \
  -p no:cacheprovider --basetemp=.scratch/blocker-registry-codex178/pytest \
  tests/quality/test_dataset_blockers.py
```

Coverage uses an AST read of module-level literal `KIND = "dataset"` declarations,
not `data.registry.published()`, whose imports can read mixed pools or hide
unprovisioned modules. This is a conservative source inventory of everything
the chooser may publish. New datasets, missing taxonomy/exercise assignments,
flat categories, unknown statuses, stale evidence and history changes fail
validation. Tests deny adapter imports, external reads, sockets and subprocesses.
