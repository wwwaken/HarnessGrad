# Splitting `data/`: scaffolds versus datasets

`data/` holds two different things under one namespace, and the namespace does not
say which is which:

* **28 dataset adapters** — `data/agentdojo.py`, `data/gsm8k.py`, … one per benchmark.
* **shared scaffolding** — `data/qa/` (8 modules), `data/registry.py`,
  `data/command_control.py`, `data/command_oracle_harness/`, `data/demo.py`,
  `data/probe_set.py`, `data/broken_service.py`, `data/verify_*.py`.

The confusion is visible in the directory list itself. `data/agentdojo/`,
`data/appworld/`, `data/tau_bench/` are **one adapter's own assets**, while
`data/qa/` is a **scaffold shared by 15 adapters**. Both are `data/<name>/`, so a
reader cannot tell a shared decision from a private one. That is the structural
defect, and it is why a change can cross adapters without anyone noticing.

## 1. Inventory

| Class | Paths |
| --- | --- |
| **adapter** (28) | `data/<name>.py` for every `name` in `data.registry.published()` |
| **scaffold** | `data/qa/` (`base`, `control`, `prediction`, `evidence_scorers`, …), `data/registry.py`, `data/command_control.py`, `data/command_oracle_harness/`, `data/__init__.py` |
| **adapter asset** (17 dirs) | `data/agentdojo/`, `data/alfworld/`, `data/api_bank/`, `data/appworld/`, `data/bird_minidev/`, `data/ds1000/`, `data/gaia/`, `data/jericho/`, `data/livecodebench/`, `data/nestful/`, `data/reasoning_gym/`, `data/scienceworld/`, `data/spreadsheetbench/`, `data/tau_bench/` (40 files), `data/pinchbench/` (empty) |
| **fixture / support** | `data/demo.py`, `data/probe_set.py`, `data/broken_service.py`, `data/verify_demo.py`, `data/verify_exec.py`, `data/verify_service.py` |

Counts: 131 Python files under `data/`; 31 top-level modules, of which 28 are
published adapters.

## 2. Blast radius, measured

Derived from an `ast` pass over `data/`, `eval/`, `tools/` and `driver.py`,
resolving `from data.qa import base` to the submodule it actually reaches:

| Scaffold | Adapters that import it | Which |
| --- | ---: | --- |
| `data.qa.base` | **15** | agentdojo, bfcl_v3, chessbench_puzzles, ds1000, fever, gsm8k, hotpotqa, musique, … |
| `data.registry` | 3 | bird_minidev, gaia, livecodebench |
| `data.qa.evidence_scorers` | 2 | fever, hotpotqa |
| `data.qa.prediction` | 1 | musique |
| `data.command_control` | 1 | ds1000 |
| **(none)** | 13 | the remaining adapters are self-contained |

**`data/qa/base.py` is the one that matters: 15 of 28 adapters depend on it.** Any
change there is a change to 15 benchmarks at once, and nothing in the layout says so.

## 3. Failure modes each scaffold enables

**3.1 `data/qa/` — the proven one.** A BFCL-driven widening of
`data/qa/control.py` silently changed the expected noop result for every adapter
that lacks a `functions` key, because the expected value was *inferred* from the
absence of that key rather than *declared* by the adapter. Six adapters changed
behaviour without being touched, and the fix (`4d41a4c`) had to narrow the rule back
to `module.__name__ == "data.bfcl_v3"`. The same commit also left MuSiQue and 2Wiki
disagreeing about the aggregating denominator. Root cause: the scaffold decides
something an adapter should declare.

**3.2 `data/registry.py` — imported by adapters.** Three adapters import the
registry, which is the discovery choke point. An adapter should not need to know how
datasets are discovered; importing it couples the adapter to the loader's internals
and makes the discovery order part of the adapter's contract.

**3.3 `data/command_control.py` — one shared control for a whole class.** It is the
control for every `command` dataset, so a change made for one of them is a change to
all of them, with the same invisibility as 3.1.

**3.4 `data/<name>/` is ambiguous.** Scaffold directory and adapter asset directory
look identical. This is what let 3.1 go unnoticed: the diff touched `data/qa/`, which
reads like one dataset's folder.

## 4. Target layout

```
data/
  scaffolds/           # shared, reviewed as platform code
    __init__.py
    registry.py
    command_control.py
    command_oracle_harness/
    qa/
  datasets/            # one adapter and its own assets per dataset
    agentdojo.py
    agentdojo/
    gsm8k.py
    tau_bench.py
    tau_bench/
    ...
  demo.py  probe_set.py  broken_service.py  verify_*.py   # fixtures, unchanged
```

Rewrite: `data.qa` → `data.scaffolds.qa`, `data.registry` → `data.scaffolds.registry`,
`data.command_control` → `data.scaffolds.command_control`, `data.<name>` →
`data.datasets.<name>`.

## 5. What must be updated

| Surface | Why |
| --- | --- |
| `data/registry.py` | its discovery globs `data/*.py`; it must glob `data/datasets/*.py` and still publish the same 28 names |
| `tools/dataset_classes.py` | AST-reads module-level `KIND` from `data/*.py` |
| `tools/check_dataset_blockers.py` | same AST inventory, and `published_declarations()` globs `data/*.py` |
| `data/dataset.schema.json` | any `module`/path field that names an adapter |
| `tests/quality/test_dataset_controls.py` | `ROWS` keys and `registry.importlib.import_module(f"data.{name}")` |
| `tests/quality/test_test_scope.py` | scopes test files by dataset name; unaffected, but the guard must still pass |
| `docs/dataset-onboarding.md`, `docs/architecture.md` | both describe the current layout |
| `tests/quality/test_import_direction.py` | records `data → eval` edges by module path |
| every adapter's own imports | 22 adapter→scaffold edges |

## 6. Risk and staged rollout

The move is mechanical but wide, and the suite must stay green at each step.

**Stage A — make the boundary visible without touching an import (low risk).**
Move the scaffolds to `data/scaffolds/` and leave `data/qa`, `data/registry`,
`data/command_control` as thin documented re-export shims. Diff is small, no adapter
changes, and the reader can now see which directory is shared. Guard: a test that
asserts `data/scaffolds/` contains no adapter and that `data/<name>/` is only ever an
adapter's own assets.

**Stage B — fix the proven hazard (independent of the move).** Make the expected
noop an explicit per-adapter declaration instead of inferring it from a missing key,
and make the aggregating denominator explicit per adapter. This is the change that
actually prevents a repeat of 3.1, and it can land before any file moves.

**Stage C — rewire the 22 edges (mechanical).** Point the 15+ adapters at
`data.scaffolds.*`, delete the shims, extend the import guard to forbid
`data.datasets.*` importing another adapter and to allow adapters to import only
`data.scaffolds.*`.

**Stage D — move the adapters (mechanical, wide).** `data/<name>.py` and
`data/<name>/` into `data/datasets/`, update discovery in the four places above, and
add `data.<name>` compatibility shims only if something outside the repo imports them
(see §7).

Order matters: A and B are safe in either order; C must follow A; D must follow C.

## 7. What could not be determined from the tree

* **Whether anything outside this repository imports `data.<name>`.** A compatibility
  shim for 28 adapter paths is cheap insurance, but the decision needs to know whether
  the paths are used by another project on this machine; the tree cannot answer that.
* **Whether `data/registry.py`'s discovery order is externally observable.** It sorts
  its output, but any code depending on glob order would only fail at runtime.
* **`data/pinchbench/` is empty.** Whether it is a removed dataset's leftover or a
  planned one is not recorded anywhere I could find.
* **`data/tau_bench/` holds 40 files** and was not read in detail; whether all of it
  is adapter assets or some is vendored upstream code that should be treated
  differently needs its own review.

## 8. Recommendation

Do **Stage B first**, because it is the only step that fixes a demonstrated
cross-adapter defect rather than relabelling it. Then Stage A, then C, then D. If
only one step is ever taken, take B.
