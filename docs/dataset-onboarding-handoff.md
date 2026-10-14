# Dataset onboarding handoff — filling the harness-function cross-table

This page is the entry point for someone joining to add datasets. It is self-contained: you do
not need the session that produced it. Read it top to bottom.

The job: the registry has 28 adapters, and the demand x harness-function matrix has cells with
no adapter behind them. Close them. While doing so, internalize whatever the work teaches the
shared platform, because that is a rule here and not an optional courtesy.

**Assignment (owner's decision, 2026-10-14): P1 and P2 only.** Those are the `memory` family and
the `safety` family, in §6. P3 (transfer peers) is not assigned yet, and P0 is deferred — the
owner is organizing the platform first. See §6 for what P0 is and why deferring it does not block
this work.

---

## 1. Two axes, and the one distinction that is easy to get wrong

Every adapter declares two separate things. They are not the same axis and must not be collapsed.

| | what it classifies | cardinality | where it lives |
| --- | --- | --- | --- |
| `demand` / `surface` | the **task**: what does this benchmark ask for | exactly one pair per adapter | `tools/dataset_classes.py::CAPABILITY` |
| `exercises` | the **harness**: which component, if changed, could move this adapter's score | a **set** per adapter | `tools/dataset_classes.py::EXERCISES` |

The rule, stated in `docs/dataset-blockers.md:6-8` and worth reading twice:

> An exercise means score sensitivity to a harness component, not an isolated measurement of that
> component. For example, Jericho's `memory` exercise does not make its task demand `memory`.

Three consequences you will need:

1. **Sensitivity, not isolation.** An `exercises` entry says "change this and the score can move".
   It does **not** say the adapter isolates the component. No adapter here isolates any component.
2. **Harness-relative.** Whether changing a component moves the score depends on whether the
   harness under test *has* that component. One adapter can carry a different set for a different
   harness family.
3. **A function that lives inside one demand is refused.** `_check_functions` rejects it, because
   such a function carries nothing the demand axis does not already have. (`reflection` was
   removed for exactly this: it held only the reasoning adapters.) A covered function must cross
   at least two demands.

Both axes are enforced. Run `python3 tools/dataset_classes.py` and read the two summaries at the
bottom before you choose anything.

---

## 2. The rule you are asking about: internalize the mechanism, then record it

Yes, this is a standing requirement, not a habit.

`docs/dataset-onboarding.md:4`:

> Every adapter entry must also update `docs/platform-improvement-log.md` when it teaches the
> shared platform a reusable capability.

And the design rule that gives it teeth, from `docs/platform-improvement-log.md`:

> Do not merge a dataset-specific runner when a shared lifecycle, evidence envelope, resource
> policy or endpoint contract can express the need.

### What the record must contain

Add a row to the **capability index** and a detailed `C-###` record. Six fields:

- the failure or repeated need that motivated it;
- the shared contract it adds or changes;
- the datasets that exposed it;
- tests or controls that validate it;
- rollout status: `planned`, `isolated`, `merged`, or `deferred`;
- the commit that introduced it.

### Commit discipline

Small commits, capability-oriented subject:

```text
platform: cap early pilots before H0 execution
runtime: separate verifier timeout from measured zero
runtime: prevent harness writes to platform checkout
adapter: add LiveCodeBench covered-train manifest
```

Body:

```text
Trigger:
Evidence:
Shared contract:
Validation:
Remaining gates:
```

A dataset result is not complete until the journal entry, the manifest hash, the run ID, the
archive status and the validation command agree.

**Current state, measured:** 34 journal entries, 22 carrying a `Platform change` line. The twelve
without are mostly audit and review entries, which legitimately internalize nothing. One dataset
entry is a genuine miss — `BFCL v3 — scorer/privacy controls` added a selected-only loader hook and
gold redaction but recorded no `Platform change`. Do not add to that pile.

---

## 3. Reading order

`docs/*` is mostly git-ignored; the third column says what you can actually get from a clone.

| # | document | what it gives you | tracked |
| --- | --- | --- | --- |
| 1 | `docs/dataset-onboarding.md` | the procedure and the five gates | **yes** |
| 2 | `docs/dataset-blockers.md` + `.json` | the per-dataset blocker registry, already carrying `demand`/`surface`/`exercises` | **yes** |
| 3 | `docs/platform-improvement-log.md` | the internalized mechanisms, index + 10 records | **yes** |
| 4 | `docs/adapter-integration-journal.md` | the per-adapter case record: Finding / Platform change / Remaining gates | **yes** |
| 5 | `docs/writing_a_harness.md` | what a harness must satisfy to be measured at all | **yes** |
| 6 | `docs/dataset-first-day.md` | the first-day orientation | **yes** |
| 7 | `docs/musique-output-contract.md`, `docs/chessbench-puzzles-evaluation.md` | two worked contracts, at opposite ends: metric composition and interactive protocol | **yes** |
| 8 | `docs/harness-functional-coverage.md` | why the function axis exists, the measured table, and the two classes of gap | local-only |
| 9 | `docs/handoff-tier1.md` | the five gates in table form plus the registration checklist | local-only |
| 10 | `docs/dataset-onboarding-skill.md` | the round-by-round lessons, including the failures | local-only |

If you cannot see 8-10, ask the owner to copy them over; the essentials are inlined below.

---

## 4. The five gates

A dataset is onboarded only when all five hold **and** the registration list in §5 is complete.
Gates 1 and 2 must pass **twice**: by hand, and through the platform by adding `--platform`.

| # | gate | how |
| --- | --- | --- |
| 1 | oracle control scores 1 | `python3 data/<name>/control.py --oracle` or `data/qa/control.py --dataset <name> --oracle` |
| 2 | do-nothing control scores 0 | same, `--noop` |
| 3 | the official scorer is transcribed verbatim + a differential test | `tests/quality/test_<name>_official_scorer.py` |
| 4 | `KIND = "dataset"` and the lint passes | `python3 tools/dataset_lint.py --dataset <name>` → rc 0 |
| 5 | it runs | `python3 tools/task_difficulty.py --dataset <name>` → rc 0 |

**A refusal is a valid outcome.** If a dataset cannot meet the gates, write the refusal properly
with its evidence rather than bending a gate. Four adapters in the registry are refusals and they
remain in the taxonomy, because a refusal is a statement about this platform's contract and not
about the benchmark.

---

## 5. Registration checklist

Once the gates pass, touch all of these or the tooling will fail somewhere later:

- `tools/dataset_classes.py` — `CAPABILITY[<name>] = (demand, surface)`, `EXERCISES[<name>]`
  (a tuple of functions), `EXPECTED_INTERACTION[<name>]`. If you are opening `memory`, **delete**
  its entry from `UNCOVERED_DEMANDS` in the same change; the tool refuses a demand left declared
  uncovered while holding adapters.
- `docs/dataset-blockers.json` — add the record. `tools/check_dataset_blockers.py` fails on a
  missing taxonomy or exercise assignment, a flat category, an unknown status or stale evidence.
- `tests/quality/test_dataset_controls.py` — a `ROWS` entry with `control` + `metric_tests`.
- `tests/quality/test_qa_dataset_contract.py::QA_DATASETS` — only for `qa`-shaped datasets.
- `python3 tools/datasets.py --write` — regenerates `DOWNLOADS.md`.
- `docs/adapter-integration-journal.md` — an entry with a `- Finding:` and a `- Platform change:`
  line.
- `docs/platform-improvement-log.md` — the capability row and `C-###` record, if you taught the
  platform something.
- `docs/dataset-onboarding-skill.md` — append the measured lesson, in the existing voice: numbers,
  not adjectives.
- Rerun `python3 tools/dataset_classes.py` and check the tool still accepts the vocabulary.

---

## 6. What to fill

Priorities, so you know what is in scope:

| | what | in scope now | why |
| --- | --- | --- | --- |
| **P0** | **Not a dataset task.** Re-baseline the existing adapters on an actor model with headroom, and enlarge eval sides to >=100 tasks. | **deferred by the owner** | See below. Do not start it. |
| **P1** | `memory` family: LoCoMo-MC10, LongMemEval retrieval-recall, MemoryAgentBench | **yes** | opens a demand with zero coverage, and is the instrument for R5 |
| **P2** | `safety` family: InjecAgent, TensorTrust | **yes** | takes safety from 1 adapter to 3, and gives a transfer pair |
| **P3** | transfer peers for the four cheap singleton surfaces | not assigned | unlocks R4 and R11 |
| **P4** | `pass@k` aggregation and a budget sweep | not assigned | needs no dataset |

### What P0 is, and why deferring it is safe for P1 and P2

P0 is not a purchase. It is two configuration decisions, both with a measured reason:

1. **Actor model.** 188 of the 220 runs on this machine used `qwen3.5-9b-local`, whose median score
   is **0.0000** with **53.7%** of runs scoring exactly zero. The same harness scores 0.4729 with
   `deepseek-flash` on the same tasks. R3 in `docs/claims.md` says headroom is a property of the
   harness, the benchmark and the model together, and that **without headroom sample efficiency is
   undefined** — so on the current model the paper's headline curves cannot be measured at all.
2. **Eval-set size.** M2 measured a floor of 1.30 tasks of spread on a twenty-task eval set, and
   the staircase needs roughly 100 eval tasks to be visible. Current pilots score 50.

Neither one changes an adapter, so **neither one blocks P1 or P2**. The onboarding gates are gate 1
and gate 2 — oracle scores 1, noop scores 0 — and those are model-free controls: the control sweeps
in the journal ran with `jobs=1, no model/H0`. You can onboard and verify a `memory` or `safety`
adapter completely without a model run. What P0 would add later is whether those adapters have any
headroom to measure, which is a separate question from whether they are correctly onboarded.

| gap | state | candidates already screened |
| --- | --- | --- |
| **`memory` as a demand** | 0 adapters, declared with two planned surfaces | `supplied_history`: LoCoMo-MC10 (240 MB, 10-way MC, literal integer gold, zero judges). `authored_store`: LongMemEval's retrieval-recall variant (`answer_session_ids` + `has_answer`, deterministic Recall@k/NDCG@k). Three more screened: PersonaMem v1, LaMP dev, MemoryAgentBench. Full screen in `docs/survey/notes/harnessgrad_memory_domain_report.md`. |
| **`safety` as a function** | 1 adapter (`agentdojo`), below the floor of 2 | **InjecAgent** (1,054 cases, ASR is pure regex), **TensorTrust** (string rules, exploits in-data), **CyberMetric / SecBench / SecEval** (2,730+ static MCQ, exact match, zero environment). All deterministic, no judge, no environment. |
| **`delegation`** | 0 | **No candidate passes the hard constraints.** `docs/survey/README.md:168` excludes the entire social-simulation family, MultiAgentBench, ToolSandbox and TheAgentCompany for judge headlines, and the three survey sources disagree about whether multi-agent is even a category. Leave it declared unless you are opening a new screen. |
| **`reliability`, `cost`** | 0 | **These need no dataset.** `pass@k` is a protocol: `eval/metrics.py` already has `mean` and `ci95`, so what is missing is the aggregation and the declaration. `cost` is a knob: the platform already costs every run, so what is missing is a budget-bounded run. Do not go looking for benchmarks to fill these two. |

**One thing not to repeat:** running an adapter is not the same as covering it. Most of the 220
runs on this machine are single Terminal-Bench tasks and probe tasks; only two registered adapters
have been run at 50-task scale. `docs/harness-functional-coverage.md` §3 separates the gaps the
platform could host from the ones its own constraints exclude, and the second class is not a
dataset gap at all.

---

## 7. Two worked cases, and one anti-case

**MuSiQue — when the metric is the finding.** The inherited scorer rewarded Answer F1 only, while
the official evaluator reports answer and support separately. The fix reports Answer F1, Answer EM
and Support F1 as separate columns; the platform scalar became `answer_f1 * support_f1`, labelled
in two places as **not an official metric**. Platform change: structured QA evidence transport and
redacted verifier gold. See `docs/musique-output-contract.md`.

**ChessBench — when the protocol is the finding.** Official puzzle accuracy is interactive: one
board, one move, then the evaluator applies the reference opponent reply before the next board. The
inherited one-shot sequence contract could not attest those observations, and `python-chess`
`Board.push()` does not check legality (verified: it accepts `e2e5` and corrupts the board), so an
impossible exact-reference move could score 1.0. Platform change: strict legal replay as the
default reward, the upstream unchecked loop retained as a diagnostic only, and a `StepwisePuzzle`
public contract. See `docs/chessbench-puzzles-evaluation.md`.

**GSM8K — the anti-case, worth knowing before you write a differential test.** The original test
transcribed the "official" extractor into the test file and then compared the adapter against it.
When the adapter's decimal handling was repaired, the test's reference was edited in lockstep, so
the test became circular: it compared the adapter against a copy of itself and could not fail.
That was fixed by pinning the *old* behaviour as a frozen fixture at an immutable commit with a
source SHA-256 (`tests/fixtures/gsm8k_original/`), and stating in the fixture that its upstream
attribution is **unverified**. MuSiQue's `tests/fixtures/musique_official/` is the same pattern.

**The rule: transcribe the official scorer into a pinned fixture, not into the test.** A reference
that moves with the adapter certifies nothing. Where the upstream source cannot be acquired, the
honest move is a gate that fails closed with a written acquisition contract — see
`tests/fixtures/triviaqa_upstream/README.md`, which declares "unacquired / provenance blocked"
rather than shipping a second transcription.

---

## 8. Validate before you hand back

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tools/check_dataset_blockers.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q \
  -p no:cacheprovider --basetemp=.scratch/blockers/pytest tests/quality/test_dataset_blockers.py
python3 tools/dataset_classes.py
python3 -m pytest -q tests/quality/test_dataset_classes.py      # ~14 min, run it anyway
```

The blocker registry test denies adapter imports, external reads, sockets and subprocesses, so it
is safe to run anywhere.

---

## 9. Operating rules that bind this work

- GPU0 is `http://127.0.0.1:8001/v1`; GPU1 is `http://127.0.0.1:8002/v1`. Bind each run to one
  endpoint and one fresh run ID. Total H0 concurrency `<=3`, `jobs=1`.
- One-task/one-trial diagnostic first, after all gates pass. Temporary reruns of blocked datasets
  select `min(30, ceil(10% * eligible))` tasks with `trials=1`, `jobs=1`. Do not silently revert to
  the historical `min(50, ...) x 3`.
- Invalid, unmeasured, timeout, scorer, provider, cleanup and snapshot failures **are not ordinary
  zero scores**.
- Preserve old and incomplete receipts. Never resume or overwrite a used run ID.
- No method tuning, paid endpoints, heldout leakage, score fabrication, or fake benchmark
  utilization.
- A passing synthetic control is not production authorization.
