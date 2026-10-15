# Does the τ-bench defect class recur? A trust-anchor audit of every verifier

Parent record, 2026-10-16 (goal round 7). Static code audit; **no verifier was executed, no dataset was run.**

## Why this audit exists

Item 17a fixed a specific and serious defect: τ-bench decided success from `done`, the required-output
predicates and the database state read out of `/app/tau_calls.jsonl` — **a file the agent can write** — so
two JSONL lines could forge the communication half of the score. The fix made the recording service-owned
and read-only (`14866a0c`). The obvious follow-up question, and the reason this file exists, is whether the
same class appears anywhere else: **a verifier that treats an agent-writable file as evidence of
completion.** If it does, that is a must-fix of the same severity; if it does not, that is a result worth
recording so nobody re-audits it next phase.

## The distinction that makes the audit decidable

"Reads a file the agent can write" is **not** the defect. Every replay-based verifier here reads the agent's
action log, and that is correct. The defect is narrower:

* **Sound:** the agent-writable file carries the agent's **actions or output**, and the verifier
  **re-executes** them in a world the agent no longer controls. The agent can only get credit for what it
  actually did, because the state that is scored is re-derived, not read.
* **Defect:** the agent-writable file carries **evidence of completion** — a done flag, a state assertion,
  a database, a required-output marker — and the verifier **accepts** it. Then the agent scores by
  assertion rather than by action.

## Result: the class occurs once, and it is fixed

| verifier | what decides success | where that comes from | verdict |
| --- | --- | --- | --- |
| `alfworld` | `won` after replaying the agent's actions in a freshly built env | agent's action log, **re-executed**; code states prints "are never consulted -- the log holds actions and actions are re-executed" (`data/datasets/alfworld.py:53-55`) | sound |
| `jericho` | the game's own score, after replaying the agent's commands | "**It reads one thing from the agent: the ordered commands**", then rebuilds from a **trusted** `jer_game.json` **and a trusted ROM**, both re-materialized by the platform immediately before it runs (`jericho/verify/check.py:2-7`) | sound |
| `scienceworld` | the JVM's score, after replaying the agent's actions in a **fresh** world (`scienceworld/verify/check.py:2`) | agent's action log, re-executed | sound |
| `appworld` | `world.evaluate()` on a fresh world after replaying the recorded API calls (`appworld/verify/check.py:45-56`, `:64-71`) | `--log` points **inside the platform recording mount** (`data/datasets/appworld.py:285`); the service is task-bound, rejects a foreign task id with 403, and initialises with `load_ground_truth=False, ground_truth_mode="minimal"` so **ground truth is never in the agent-facing process** (`appworld/service.py`) | sound |
| `agentdojo` | utility from replaying `action.json` | file docstring: "Trusted verifier: replay action.json, **not subject-supplied state or observations**" (`agentdojo/verify/check.py:1`) | sound |
| `tau_bench` | service-recorded DB hash × first termination × required outputs | `/recordings/tau/episode.json`, service-owned and mounted read-only — the file states it outright: "**Agent-local db.json and tau_calls.jsonl are not inputs to grading**", and events after the first termination never contribute (`tau_bench/verify/check.py:2-12`) | **sound — this was the defect, now fixed** |
| `ds1000`, `livecodebench` | the verifier executes its own tests against the agent's artifact | verifier side | sound |
| `spreadsheetbench` | LibreOffice recalculation in private scratch | verifier side (`f5af0f78`) | sound |
| `bird_minidev` | predicted vs gold SQL, both executed by the verifier | `--db` and `--gold` are declared **verifier inputs** (`bird_minidev/verify/check.py:97-98`, `:104`) | sound |
| `gaia` | the official `question_scorer` on the agent's answer | verifier side | sound |
| `scaffolds/qa` | the evidence scorers on the agent's answer and evidence | verifier side | sound |

**No instance of the defect class exists outside τ-bench.** Twelve entrypoints (11 datasets plus
`data/scaffolds/qa/verify/check.py`); every success predicate either re-derives state in a fresh
world/service from the agent's actions, executes the verifier's own tests or queries against trusted
inputs, or scores the agent's answer with the official scorer. Item 17a was a single instance, and it is
closed.

## Two things worth keeping, found while looking

* **`appworld` is the strongest boundary in the set, and it was not obvious from the adapter name.** The
  upstream environment server exposes `initialize`, evaluation, task, state and log-management endpoints;
  the shipped `service.py` deliberately exposes only the action surface and *says so in its docstring*. It
  also refuses a task id that is not its own, and never loads ground truth into the agent-facing world — the
  verifier builds a separate `AppWorld` with the official evaluator after the recording is complete. That
  is the τ-bench fix plus a ground-truth separation, and it is what makes appworld's future diagnostic
  measurable rather than forgeable.
* **`jericho` re-materializes the game *and the ROM* immediately before the check runs.** Trusting a
  re-materialized copy rather than whatever is on disk after the agent has been running is the detail that
  makes the replay meaningful; it is worth copying if another replay-based adapter is ever added.

## Limits of this audit

* **Static reading only.** No verifier was executed and no dataset was run; each verdict is a reading of the
  declared inputs and the code that consumes them, not an observed run.
* The scope is the **12 verifier entrypoints the platform declares** (`data/datasets/*/verify/check.py` and
  `data/scaffolds/*/verify/check.py`). A scorer reached through some other path would not be covered.
* A coarse `stdout`/`print` sweep across those files matched six of them; that is not evidence of
  print-trust in any of the six — `print` is normally used to publish the reward or to keep the check's
  output on the verdict. I verified the posture only where a file states it (alfworld explicitly, jericho
  explicitly), and I did not trace every print statement to its consumer.
* Nothing here re-opens or re-closes any blocker, and nothing here is a measurement. It is a source-level
  audit of where each verifier's success predicate comes from.
