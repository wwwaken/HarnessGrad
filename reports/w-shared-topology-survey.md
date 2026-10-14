# Shared-blocker scorer topology survey - w-shared

Source review date: 2026-10-15. Reviewed commit: `0b470b6` (includes scorer isolation option B).

This is a source-and-wiring review of the 23 datasets whose entries have shared
blocker references in `docs/dataset-blockers.json`. It does not certify an executed
run, provisioned dependencies, official scorer fidelity, or production readiness.
No dataset, model, GPU, endpoint, Docker, or pilot execution was performed. No
registry changes are requested by this survey.

## Registry scope and review limits

The shared blockers' current `observed` and `next_action` were read first:

- `runtime-observations`: observed backend observations were described as absent;
  the requested action is review of backend observation integration and refusals.
- `pristine-verifier`: observed rematerialization was described as insufficient;
  the requested action is independent identity/isolation review.
- `scorer-offline-closure`: option B is implemented, but complete transitive
  image/ABI closure and dataset runtime evidence remain absent; its action requires
  dataset-specific pinned closures and class-specific live evidence.
- `artifact-only-state-export`: generic bounded export is implemented for opt-in
  pristine scorers, while dataset private-input safety, ownership/quiescence, state
  equivalence and cleanup remain unestablished; its action requires per-task export
  contracts or class-specific snapshot/service review.

Those actions differ. A source topology finding cannot close either code-solvable
blocker or substitute for its required dataset evidence.

## How the route is established

The classes below describe the runtime route the code would execute for a valid
task reaching verification, not a measured historical runtime observation.

- **F: native `actor-workdir` command route.** After the actor subprocess returns
  (`eval/run/runner.py:494`), the runner separately invokes `_verify`
  (`eval/run/runner.py:525`). The dispatcher chooses `actor-workdir` for command
  scorers without services (`eval/verification/verifier.py:455`). It stages trusted
  verifier inputs (`eval/verification/verifier.py:519`) and launches another process:
  a read-only-workdir sandbox (`eval/verification/verifier.py:596`) or, when sandboxing
  is explicitly disabled and otherwise admitted, `subprocess.run`
  (`eval/verification/verifier.py:602`). **Sharing the actor's workdir does not mean
  sharing the actor's process.** Native runtime/network declarations can prohibit
  that unsandboxed branch (`eval/run/runner.py:224`).
- **Q: shared QA command scorer, also F.** `QASpec.VERIFIER_KIND` is `command`
  (`data/scaffolds/qa/base.py:478`), its verifier launches `python3` with the shared
  check (`data/scaffolds/qa/base.py:340`, `data/scaffolds/qa/base.py:342`), and its
  environment is `files` (`data/scaffolds/qa/base.py:444`). The child check imports
  the rematerialized adapter (`data/scaffolds/qa/verify/check.py:217`) and calls its
  `score`/`score_prediction` inside **that verifier child**, not the actor
  (`data/scaffolds/qa/verify/check.py:238`,
  `data/scaffolds/qa/verify/check.py:242`). A Python scorer function is not evidence
  that the platform's topology class is `in-process`.
- **S: container-snapshot `snapshot-service` route.** `state=container` dispatches
  into `_run_one_container_state` (`eval/run/runner.py:233`); it stops the actor
  container and commits its filesystem (`eval/containers/container_state.py:190`,
  `eval/containers/container_state.py:191`), then invokes `_verify_container_state`
  (`eval/containers/container_state.py:213`). Verification creates another container
  from that snapshot (`eval/verification/verifier.py:286`) and records
  `snapshot-service` (`eval/verification/verifier.py:249`). The class name also
  covers snapshots with no external scoring service.
- **V: services `snapshot-service` route.** `_verify` chooses `snapshot-service`
  when services exist (`eval/verification/verifier.py:456`). It launches a fresh
  verifier container, supplies recording mounts, and joins the task service network
  (`eval/verification/verifier.py:564`, `eval/verification/verifier.py:570`,
  `eval/verification/verifier.py:576`). AppWorld uses this route with mounted state,
  rather than an actor-image snapshot.

The opt-in pristine path requires a declared `pristine-offline` scorer bundle
(`eval/verification/verifier.py:457`, `eval/verification/verifier.py:462`). None of
these 23 adapters declares that class. AppWorld and Terminal-Bench declare
`snapshot-service`; the remaining standard routes are inferred by the dispatcher
from command/environment wiring, not presumed pristine. Admission, staging,
dependency or scorer failures can prevent a route from yielding a measurement;
the table is not a claim that all 23 are runnable. In particular, `run_one` calls
the existing backend-observation refusal hook before dispatch
(`eval/run/runner.py:160`). Policy-bearing paths, including exec defaults,
container state and declared native network/resource limits, are refused without
the required observation (`eval/run/runner.py:55`, `eval/run/runner.py:78`). A bound
operator-authorized diagnostic exception permits an explicitly unmeasured attempt
(`eval/run/runner.py:72`); it does not authorize a production measurement or pilot.

## Dataset-by-dataset survey

Each row cites the adapter's command/environment wiring and the scoring code it
reaches. F/Q/S/V refer to the dispatcher evidence above. “Actor-only flag” asks
the user's specific question: should either shared code-solvable blocker be called
irrelevant **because scoring never leaves the actor process**?

| Dataset | Executed code route/class | File + line establishing route | Scoring code reached | Actor-only flag |
| --- | --- | --- | --- | --- |
| `alfworld` | F: `actor-workdir` | `data/datasets/alfworld.py:343` command; `data/datasets/alfworld.py:345` check argv; `data/datasets/alfworld.py:532` files environment | `data/datasets/alfworld/verify/check.py:159` rebuilds/replays the environment; `data/datasets/alfworld/verify/check.py:178` reads replay success | No |
| `appworld` | V: `snapshot-service` | `data/datasets/appworld.py:270` declares class; `data/datasets/appworld.py:273` check argv; `data/datasets/appworld.py:298` mount state; `data/datasets/appworld.py:301` services | `data/datasets/appworld/verify/check.py:45` builds an AppWorld evaluator; `data/datasets/appworld/verify/check.py:52` replays calls; `data/datasets/appworld/verify/check.py:56` evaluates | No |
| `bfcl_v3` | Q: `actor-workdir` | `data/datasets/bfcl_v3.py:583` constructs Q verifier; `data/datasets/bfcl_v3.py:115` files environment | `data/datasets/bfcl_v3.py:217` function-name diagnostic scorer; `data/datasets/bfcl_v3.py:230` explicitly says it is not official BFCL score | No |
| `bird_minidev` | F: `actor-workdir` | `data/datasets/bird_minidev.py:254` command; `data/datasets/bird_minidev.py:255` check argv; `data/datasets/bird_minidev.py:308` files environment | `data/datasets/bird_minidev/verify/check.py:108` executes gold SQL; `data/datasets/bird_minidev/verify/check.py:119` executes prediction SQL; `data/datasets/bird_minidev/verify/check.py:125` computes EX | No |
| `chessbench_puzzles` | Default Q: `actor-workdir`; opt-in trusted-controller `in-process` branch (currently recorded `unknown`; see below) | `data/datasets/chessbench_puzzles.py:438` Q verifier; `data/datasets/chessbench_puzzles.py:385` files environment; `eval/run/runner.py:522` stepwise bypass | Offline: `data/datasets/chessbench_puzzles.py:309` strict/upstream scorer; interactive: `eval/run/chess_stepwise.py:49`, `eval/run/chess_stepwise.py:72` | No: neither branch is actor-process scoring |
| `ds1000` | F: `actor-workdir`, with another scorer child | `data/datasets/ds1000.py:194` command; `data/datasets/ds1000.py:195` check argv; `data/datasets/ds1000.py:168` files environment | `data/datasets/ds1000/verify/check.py:29` composes official tests; `data/datasets/ds1000/verify/check.py:53` launches the execution runner child | No |
| `fever` | Q: `actor-workdir` | `data/datasets/fever.py:53` QASpec binding; `data/datasets/fever.py:97` scaffold files environment | `data/datasets/fever.py:31` strict label/evidence check; `data/datasets/fever.py:43` legacy answer delegates to it | No |
| `gaia` | S: `snapshot-service` | `data/datasets/gaia.py:103` container state; `data/datasets/gaia.py:201` command; `data/datasets/gaia.py:202` check argv | `data/datasets/gaia/verify/check.py:72` imports upstream scorer; `data/datasets/gaia/verify/check.py:99` calls `question_scorer` | No |
| `gsm8k` | Q: `actor-workdir` | `data/datasets/gsm8k.py:238` QASpec binding; `data/datasets/gsm8k.py:245` scorer binding; `data/datasets/gsm8k.py:259` scaffold files environment | `data/datasets/gsm8k.py:149` scorer; `data/datasets/gsm8k.py:154` numeric comparison | No |
| `hotpotqa` | Q: `actor-workdir` | `data/datasets/hotpotqa.py:65` QASpec binding; `data/datasets/hotpotqa.py:105` scaffold files environment | `data/datasets/hotpotqa.py:37` answer/support scorer; `data/datasets/hotpotqa.py:46` joint score; `data/datasets/hotpotqa.py:55` legacy delegate | No |
| `jericho` | F: `actor-workdir` | `data/datasets/jericho.py:253` command; `data/datasets/jericho.py:255` check argv; `data/datasets/jericho.py:321` files environment with no network | `data/datasets/jericho/verify/check.py:109` fresh game; `data/datasets/jericho/verify/check.py:120` replay; `data/datasets/jericho/verify/check.py:130` score fraction | No |
| `livecodebench` | F: `actor-workdir`, with another scorer child | `data/datasets/livecodebench.py:264` command; `data/datasets/livecodebench.py:265` check argv; `data/datasets/livecodebench.py:287` files environment | `data/datasets/livecodebench/verify/check.py:169` starts a separate executor process; `data/datasets/livecodebench/verify/check.py:91` calls pinned `run_test` there | No |
| `musique` | Q: `actor-workdir` in both joint and legacy modes | `data/datasets/musique.py:227` Q verifier; `data/datasets/musique.py:275` trusted mode argv; `data/datasets/musique.py:240` files environment | `data/datasets/musique.py:88` mode-specific scorer; `data/datasets/musique.py:99` legacy reward; `data/datasets/musique.py:111` platform joint reward | No |
| `physicsquestions` | Q: `actor-workdir` | `data/datasets/physicsquestions.py:191` QASpec binding; `data/datasets/physicsquestions.py:198` scorer binding; `data/datasets/physicsquestions.py:222` scaffold files environment | `data/datasets/physicsquestions.py:103` accepted-spelling scorer; `data/datasets/physicsquestions.py:105` matching rule | No |
| `reasoning_gym` | Q: `actor-workdir` | `data/datasets/reasoning_gym.py:153` QASpec binding; `data/datasets/reasoning_gym.py:169` scaffold files environment | `data/datasets/reasoning_gym.py:108` imports installed package; `data/datasets/reasoning_gym.py:114` reconstructs family; `data/datasets/reasoning_gym.py:115` calls `score_answer` | No |
| `scienceworld` | F: `actor-workdir`, with JVM runtime | `data/datasets/scienceworld.py:307` command; `data/datasets/scienceworld.py:309` check argv; `data/datasets/scienceworld.py:452` files environment | `data/datasets/scienceworld/verify/check.py:157` builds a fresh world; `data/datasets/scienceworld/verify/check.py:170` replays actions; `data/datasets/scienceworld/verify/check.py:194` converts JVM score to reward | No |
| `sportsunderstanding` | Q: `actor-workdir` | `data/datasets/sportsunderstanding.py:166` QASpec binding; `data/datasets/sportsunderstanding.py:173` scorer binding; `data/datasets/sportsunderstanding.py:196` scaffold files environment | `data/datasets/sportsunderstanding.py:80` scorer; `data/datasets/sportsunderstanding.py:83` label rule | No |
| `spreadsheetbench` | F: `actor-workdir`; formula branch may launch LibreOffice | `data/datasets/spreadsheetbench.py:230` command; `data/datasets/spreadsheetbench.py:232` check argv; `data/datasets/spreadsheetbench.py:357` files environment | `data/datasets/spreadsheetbench/verify/check.py:165` loads workbooks; `data/datasets/spreadsheetbench/verify/check.py:348` formula branch; `data/datasets/spreadsheetbench/verify/check.py:235` recalculation subprocess | No |
| `strategyqa` | Q: `actor-workdir` | `data/datasets/strategyqa.py:176` QASpec binding; `data/datasets/strategyqa.py:183` scorer binding; `data/datasets/strategyqa.py:204` scaffold files environment | `data/datasets/strategyqa.py:89` scorer; `data/datasets/strategyqa.py:91` normalized exact match | No |
| `tau_bench` | S: `snapshot-service` | `data/datasets/tau_bench.py:186` container state; `data/datasets/tau_bench.py:340` command; `data/datasets/tau_bench.py:341` check argv | `data/datasets/tau_bench/verify/check.py:266` trusted replay; `data/datasets/tau_bench/verify/check.py:294` actor database read; `data/datasets/tau_bench/verify/check.py:309` hash/done/output reward | No |
| `terminal_bench` | S: `snapshot-service` | `data/datasets/terminal_bench.py:202` container state; `data/datasets/terminal_bench.py:233` declares class; `data/datasets/terminal_bench.py:234` task's `/tests/test.sh` command | `data/datasets/terminal_bench.py:238` stages per-task released tests; `eval/verification/verifier.py:308` executes the command in snapshot verifier container | No |
| `triviaqa` | Q: `actor-workdir` | `data/datasets/triviaqa.py:339` QASpec binding; `data/datasets/triviaqa.py:346` scorer binding; `data/datasets/triviaqa.py:361` scaffold files environment | `data/datasets/triviaqa.py:160` scorer; `data/datasets/triviaqa.py:163` alias maximum | No |
| `twowikimultihopqa` | Q: `actor-workdir` | `data/datasets/twowikimultihopqa.py:654` QASpec/scorer binding; `data/datasets/twowikimultihopqa.py:660` scaffold files environment | `data/datasets/twowikimultihopqa.py:490` routes structured/JSON predictions to joint scoring or legacy answer-only scoring | No |

## ChessBench's additional controller branch

An explicit `task.interaction=chessbench_puzzles.stepwise.v1` selects the interactive
branch (`eval/run/chess_stepwise.py:21`). It requires a native files sandbox
(`eval/run/chess_stepwise.py:32`) and constructs `StepwisePuzzle` from inline
verifier-owned gold in the trusted runner (`eval/run/chess_stepwise.py:37`,
`eval/run/chess_stepwise.py:43`). The actor is launched separately
(`eval/run/runner.py:494`) and communicates through the relay; after it exits,
`chess_stepwise.finish` grades the controller receipt instead of launching `_verify`
(`eval/run/runner.py:522`, `eval/run/runner.py:523`). Thus this opt-in branch is
physically **trusted-platform `in-process`**, not actor `in-process`.

Its verdict currently has no `scorer_isolation_class`
(`eval/run/chess_stepwise.py:64`, `eval/run/chess_stepwise.py:72`); the common result
wrapper inserts `unknown` (`eval/run/runner.py:167`). The report distinguishes that
recorded class from the topology visible in source. This is an observation gap,
not evidence to relabel a run. The offline default still uses the QA command route
(`eval/run/chess_stepwise.py:25`, `data/datasets/chessbench_puzzles.py:438`).

## Applicability finding

The standard routes comprise **19 `actor-workdir` and 4 `snapshot-service`**
datasets; none opts into `pristine-offline`. ChessBench additionally supports the
trusted-platform controller branch above. **No dataset meets the requested
actor-process-only condition**, so none is flagged as having either
`scorer-offline-closure` or `artifact-only-state-export` rendered irrelevant for
that reason.

Calling a scorer inside a verifier Python process is different from scoring inside
the actor Python process. The QA scaffold makes that separation explicit. Even
simple string-comparison scorers still need a trustworthy interpreter, trusted gold
and scorer provenance. The native `actor-workdir` routes share actor-created
artifacts and therefore retain workdir/input/dependency integrity questions without
requiring a container snapshot. For interactive ChessBench, a container snapshot
or post-run artifact-export mechanism is not exercised, but trusted gold/controller
isolation and package closure still matter. This is a branch-specific applicability
note, not the actor-process condition and not a registry closure.

AppWorld's mounted service recording is also distinct from a container snapshot;
both deliberately live in `snapshot-service`. The two shared code-solvable blockers'
actions already require class-specific treatment, so a blanket demand for
pristine artifact export would misdescribe these routes. This report leaves all
registry decisions to the separately requested blocker reviews.
