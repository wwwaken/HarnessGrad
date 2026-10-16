# Handover: onboarding a Harbor dataset into HarnessGrad

**Audience:** whoever adapts datasets. **Status:** process agreed, two platform-side
prerequisites outstanding (listed at the end).

This file is the **Harbor-specific overlay** on the dataset process. It deliberately does not
repeat the five gates or the ten steps — those live in [`dataset-onboarding.md`](dataset-onboarding.md)
and that file stays the single source of truth for them. What is here is only what changes when the
dataset comes from Harbor, plus the decision that has to be made before any work starts.

The container-side blocker is specified separately in
[`runtime-observation-brief.md`](runtime-observation-brief.md).

## 0. The decision that comes first: port, or wrap?

**Every Harbor adapter is container-first.** Each one declares `environment: type: docker` (or a
cloud container host). So "use Harbor's datasets" has a consequence that is easy to miss:

* **wrap** — call `harbor run` from a HarnessGrad adapter. Everything lands on the container path,
  so **every** dataset is refused at admission until the runtime-observation work lands. Including
  the ones whose tasks need no container at all.
* **port** — read Harbor's task definition and metric, and re-express them in our own native
  shape. Nothing calls Harbor. These run today.

Harbor's value to us is therefore **its task definitions and metric implementations**, not its
execution. Borrow those; do not inherit the execution model.

### The per-adapter table

Fill this in once per adapter before touching code. Four questions decide everything.

| adapter | container needed? | delivery | `parity_experiment.json`? | Harbor is the upstream? | route | runnable today? |
| --- | --- | --- | --- | --- | --- | --- |
| `aime` | no (text + exact match) | one-shot | ? | no — the metric is the paper's | **port** | yes |
| `gpqa-diamond` | no | one-shot | ? | no | **port** | yes |
| `hle` | no | one-shot | ? | no | **port** | yes |
| `simpleqa` | no | one-shot | ? | no | **port** | yes |
| `locomo` | no | one-shot, whole transcript | yes | no — upstream is `snap-research/locomo` | **port** | yes |
| `swebench` | yes | environment | ? | **no** — upstream is the SWE-bench package | wrap | no — blocked |
| `terminal-bench` | yes | environment | ? | **yes** — Harbor is the official harness | wrap | no — blocked |
| `osworld`, `theagentcompany`, `tau3-bench`, `mlgym-bench`, `swelancer` | yes | environment | ? | no | wrap | no — blocked |

`?` means unverified. Run the check described in §3 to fill it.

**Rule of thumb:** if the task is "read this text, answer this question, compare to gold", port it
and it runs today. If the task is "work inside an environment and leave artifacts for a verifier",
it is blocked on the admission work no matter how it is adapted.

## 1. The delivery shape decides the label, not the dataset's name

`tools/dataset_classes.py` defines `memory` as *"the Harness must maintain a representation of
information that arrives **over time and changes**"*, and contrasts it with `evidence`, which
*"asks it to select from a **static set**"*.

So before labelling anything, answer: **does the material arrive all at once, or incrementally?**

* **one-shot delivery** → the material is in context, the questions come with it, and retaining
  anything cannot change the score. This is `evidence` on a long-context surface. **Labelling it
  `memory` would be a claim the run does not support.**
* **incremental delivery** (material in sequence, later material withheld) → retention is required,
  and `memory` is the right demand, with `authored_store` if the Harness builds the store or
  `supplied_history` if the history is provided and must be preserved.

`locomo` is the worked example of the first case. Its name says long-term memory, and its
**upstream evaluation is a closed-book single call with the full transcript in context** — see
`adapters/locomo/README.md` ("the agent receives the full text-only transcript plus the question
list in its instruction") and `adapter_metadata.json` ("Upstream eval is a closed-book LLM call …
batch size 200 so all questions for a conversation are answered in one call"). Retention is not
exercised and the metric cannot see it, so it is not a `memory` dataset here.

That does not make it worthless. "A long-context task where a memory mechanism is available but
unnecessary — does the Harness use it anyway, and does that help or hurt?" is a real question. It
is a **platform capability**, not a labelling choice: answering it needs a recorded field for
whether the Harness wrote to a store. `.state/` is a per-task tmpfs and never reaches the curve,
so today that question has no answer in the data.

**Also check coverage when labelling.** Today `exercises` never uses `delegation`, `reliability` or
`cost` across all 28 datasets, and `demand: memory` has no dataset at all. A new dataset that fills
one of those is worth more than one that duplicates an existing cell.

## 2. What a Harbor adapter is made of

```
adapters/<name>/
  README.md                    what it adapts, the metric, the upstream link
  adapter_metadata.json        upstream split/size/harness + the Harbor side + parity record
  parity_experiment.json       the adapter-vs-upstream comparison, with agents and cost
  <name>.yaml                  the run config (agents:, datasets:, environment: type: docker)
  src/<name>/
    adapter.py                 download + task generation
    main.py                    CLI entry
    metric.py                  ★ the metric implementation
    task-template/             the task the agent receives
```

**`metric.py` is the artifact gate 3 is about.** It is Harbor's own implementation of the
benchmark's number, and `adapter_metadata.json` states which upstream file it mirrors (for
`locomo`: *"mirrors upstream `task_eval/evaluation.py`"*). Reading it replaces digging through the
upstream repository.

**`parity_experiment.json` is the equivalence evidence.** It records the comparison against the
upstream implementation, including the matched agents and the cost of the run. Where it exists,
"is our number the benchmark's number?" has a recorded answer rather than an assertion.

Neither is guaranteed to exist for all 85 adapters. Check per adapter.

## 3. The flow

Same ten steps and five gates as [`dataset-onboarding.md`](dataset-onboarding.md), with these five
Harbor-specific changes.

| step | what changes for Harbor |
| --- | --- |
| **0. triage** | Answer the four questions in §0. Container + environment-shaped → **stop**, it is blocked. Also check for `parity_experiment.json`. |
| **1. read the source, not the README** | Read **`src/<name>/metric.py`** and **`parity_experiment.json`**. You do not need the upstream repository. Also settle the **delivery shape** (§1) — it decides the label. |
| **2. choose the gate-3 form** | Call Harbor's `metric.py` and pin the commit; or transcribe a published table column; or refuse. Where a parity record exists, cite it as the equivalence evidence. |
| **3. `downloads()`** | Pin the Harbor commit and, where the adapter fetches upstream data at run time (as `locomo` does), pin the upstream URL and digest too. |
| **6. scorer into a test + drift test** | **Pin the Harbor commit, quote `metric.py` line numbers, cite the parity record, and add the drift test** so a Harbor change breaks our test rather than our number. |
| **7. label and register** | As in the base doc, **plus** a `source` field pointing at Harbor — which needs the schema change listed under prerequisites. The registry row is an exact set of seven fields today and is drift-checked against `tools/dataset_classes.py`. |

The three hard gates are unchanged: **step 0** (can it be done at all), **step 5** (oracle → 1 and
noop → 0, by hand *and* through the platform), **step 6** (metric identity).

Two of them are worth stating plainly because they are where a Harbor adaptation is most likely to
look finished while being wrong:

* **Step 5 cannot be satisfied by Harbor's own controls.** Harbor ships `oracle` and `nop` agents
  (`src/harbor/agents/oracle.py`, `nop.py`), and `locomo.yaml` runs with `agents: - name: oracle`.
  That proves the *task* is reachable inside Harbor. Our gate 5 asks whether *our platform*, driving
  *our harness*, gets 1 and 0 — a different question. It must be run through
  `tools/task_difficulty.py` and the `--platform` control path.
* **Step 6 is not satisfied by an upstream link in a README.** It is satisfied by a test that fails
  when the metric moves.

## 4. What the platform side owes (prerequisites, in order)

1. **Container admission** — the runtime observation producer, and the model-transport change for
   `exec` tasks. Nothing environment-shaped runs before this. Specified in
   [`runtime-observation-brief.md`](runtime-observation-brief.md).
2. **The `source` field.** Dataset rows are an exact set of seven fields
   (`tools/check_dataset_blockers.py`), so adding provenance is a schema change across the checker,
   the applier and their tests. Methods already carry `source_commit`, so the pattern exists.
3. **The shared harness-launch module.** The contract is already fixed and documented —
   `entrypoint --task <path> --workdir <path>` (`eval/run/runner.py:380`, INTERFACE.md §1.2) — and
   the pieces exist (`driver.py:1054 stage_workspace`, `runner.py:96 harness_env`,
   `runner.py:182 _run_one`, `eval/containers/harness_runtime.py`,
   `tools/configure_harness.py`). Extracting them into one reusable module is what keeps "any
   harness" implemented **once** rather than once natively and once inside a Harbor agent adapter.
   Without it the two paths will drift, and "the same harness, two executions" stops being
   comparable. 17 test files cover those functions; they must stay green.

## 5. What the dataset side owes, per adapter

* the §0 table filled in;
* the label (`demand`, `surface`, `exercises`) with the delivery shape as evidence;
* the three files touched together: `data/datasets/<name>.py`, `tools/dataset_classes.py`,
  `registry/dataset-blockers.json` — the last two are drift-checked against each other, so a
  mismatch fails the suite;
* the gate-3 test, quoting `metric.py` lines and citing the parity record;
* `REFUSED` rather than a nearby number, if the metric cannot be carried. A refusal must be reached
  by **measurement** — run the gold through the scorer and report what came back. "It looked hard"
  is not a refusal.

## 6. Definition of done

```sh
python3 data/datasets/<name>/control.py --oracle              # reward 1
python3 data/datasets/<name>/control.py --noop                # reward 0
python3 data/datasets/<name>/control.py --oracle --platform   # reward 1 through the platform
python3 data/datasets/<name>/control.py --noop   --platform   # reward 0 through the platform
python3 tools/dataset_lint.py                                 # ok <name>
python3 tools/datasets.py --write                             # DOWNLOADS.md regenerated
python3 tools/task_difficulty.py --dataset <name>             # rc 0
python3 -m pytest tests/quality -q                            # suite stays green
```

## 7. Open questions, stated rather than assumed

* **How many of the 85 adapters ship `parity_experiment.json`?** That number decides how many can
  clear gate 3 on recorded equivalence rather than on our own measurement. Unverified.
* **Does `metric.py` ever diverge from the upstream it mirrors?** The metadata claims it mirrors;
  the parity record is the evidence. Where neither exists, we measure.
* **Which adapters are genuinely text-only?** Harbor wraps everything in Docker, so the §0 table's
  second column is a claim about the *task*, not about the adapter's config, and it needs checking
  per adapter rather than inferring from the name.
