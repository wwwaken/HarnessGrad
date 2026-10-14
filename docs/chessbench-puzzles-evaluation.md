# ChessBench Puzzles evaluation contract

Official puzzle accuracy is interactive: the engine receives a board at each solver
turn, answers with one UCI move, and receives another board after the trusted evaluator
applies the reference opponent response. A single precomputed solver sequence cannot
demonstrate that protocol. Neither puzzle replay metric is an Elo estimate.

## Metrics and the existing batch task

`data.chessbench_puzzles.score(prediction, gold)` grades the existing `answer.txt`
sequence using **ChessBench strict legal puzzle replay v1**. Its top-level `reward`,
`correct` and `verdict` come from strict replay. The public goal names this as the
offline strict sequence variant and asks for solver moves only, excluding setup and
opponent moves.

The shared verifier persists both metrics inside its legacy `official` evidence
envelope:

- `official.strict`: strict metric identity, reward, correctness, verdict and number
  of solver moves applied.
- `official.upstream`: **ChessBench upstream puzzle replay (unchecked push)**,
  preserving the pinned `src/puzzles.py:74–94` loop at revision
  `90ae0e6b121673fc3079aaeffa047580bb600c0a`. This is a diagnostic, and never supplies
  the task reward.

Report/aggregate the two rewards separately, with their metric identities and the
offline protocol. Do not relabel either sequence replay result as measured interactive
official puzzle accuracy. `score_strict()` and `score_upstream()` also expose each
scorer independently.

Strict replay parses each requested move and checks membership in `board.legal_moves`
before `Board.push()`. This includes the opponent setup and subsequent reference
opponent moves. It rejects null moves, wrong-side moves and moves that expose the
solver's king. A legal wrong reference choice fails unless it immediately checkmates.
Every legal solver checkmate ends the episode, including an exact reference move that
mates before the stored line ends. Complete reference replay also succeeds. Tokens
after either success are unused, matching the engine's requested-move semantics;
they are not checked or executed.

Terminal verdicts are `reference_complete`, `checkmate`, `alternate_mate_in_one`,
`wrong_move`, `illegal_move`, `invalid_move`, `invalid_answer`, `missing_move` and
`invalid_reference`. The first three succeed. `invalid_reference` identifies a
malformed/illegal trusted board, setup or opponent continuation; it must be investigated
before drawing a benchmark conclusion. A syntactically valid illegal solver move
returns zero with `illegal_move`, rather than being pushed onto a corrupted board.

## Public stepwise task and answer

The executable contract is `chessbench_puzzles.stepwise.v1`, implemented by
`StepwisePuzzle`. The controller constructs a session from verifier-owned gold and
passes only `session.public_task()` to the actor. An initial public task looks like
this synthetic opening, after White's setup move:

```json
{
  "contract": "chessbench_puzzles.stepwise.v1",
  "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
  "solver_turn": 0,
  "status": "awaiting_move",
  "verdict": "awaiting_move"
}
```

The answer is exactly one JSON object with exactly one string field, for example:

```json
{"uci": "e7e5"}
```

The controller calls `session.submit(answer)`. On a matching legal solver move,
the session applies the next private reference opponent move, if one is requested,
and returns the next public task with the resulting FEN and incremented `solver_turn`.
The actor chooses its next move from that observation. `status` is `awaiting_move`,
`solved` or `failed`. Terminal responses carry the verdict; later submissions raise
an error. Multiple UCI tokens, extra JSON fields and non-string UCI values are rejected.
The controller calls `session.result()` for the strict score after termination.

The session and its gold must live in a trusted process outside the actor's filesystem
and import namespace. The actor receives only the five fields shown above: no stored
line, expected solver move, future opponent move, line length, source row, puzzle ID,
gold answer or pre-setup FEN. Previously observed opponent effects are public board
state; future reference updates remain private. The controller owns the ordered
observations/submissions and termination record. An actor-written sequence or transcript
cannot attest that intermediate boards were delivered before decisions.

Importing the adapter does not read `puzzles.csv`. Accessing pool-backed `ENV`, `SPLIT`,
`SETUP`, `VERIFY`, `_RECORDS` or `load()` remains an explicit pool-loading operation;
those operations are not needed for synthetic contract tests. Verifier evidence redacts
the private gold, while retaining both score diagnostics.

## Opt-in runner wiring

The task must explicitly carry `"interaction": "chessbench_puzzles.stepwise.v1"`.
For example, a trusted caller that already has a selected public task and its private
control record can opt in without loading the full pool:

```python
interactive_task = {**public_task, "interaction": chessbench.STEPWISE_CONTRACT}
result = run_one(
    harness_repo, interactive_task, sandbox=True,
    setup=chessbench.setup_for(selected_record),
    verifier=chessbench.verify_for(selected_record),
)
```

`eval.run.runner.run_one` constructs `StepwisePuzzle` from the inline `gold.json`
entry in the trusted verifier spec. It does not materialize verifier inputs for the
actor. It replaces the offline goal with the interactive socket instructions and
exports `HG_STEPWISE_SOCKET`. The harness connects once using AF_UNIX/SOCK_STREAM,
reads a newline-delimited JSON observation, writes one newline-delimited JSON UCI
answer, and repeats until it reads a terminal observation. A harness must implement
this live interface to use the mode; an existing answer-file-only harness will leave
an incomplete exchange.

The controller starts `StepwiseRelay` immediately before the harness launch and stays
live while the runner waits for the harness. The relay uses the model relay's Unix
server and its allowance/receipt/cleanup pattern, delegating observations and answers
to the existing `transport_stepwise`. The reviewed allowlist remains exactly
`contract`, `fen`, `solver_turn`, `status`, `verdict`. The socket directory is mounted
read-only, with no session, gold, or private receipt files inside it. One connection,
256 submissions, 4096 bytes per message and the absolute agent deadline bound an
exchange. Reconnecting cannot reset the session or allowance. The runner closes the
connection, joins server/handler threads, removes the socket and removes its temporary
directory on exit, including actor timeout and launch failure.

Only a delivered terminal exchange, a clean actor exit, and successful channel cleanup
can yield a score. Invalid trusted references are unmeasured. Disconnection, actor
termination, timeout, oversized/malformed transport messages and submission-limit
failure produce incomplete receipts without score/reward. The controller-owned
terminal verdict determines interactive puzzle accuracy; `answer.txt` and
actor-authored transcripts do not determine it.

This binding requires the native `files` sandbox. Existing admission and refusal gates
remain in force, including policy-observation refusals; selecting this mode grants no
production authorization. Tasks without the explicit interaction marker continue to
use the unchanged offline strict replay reward and verifier.

## Receipts, caching and comparison

`verdict.protocol` names the protocol and is preserved by the verdict saver. Interactive
`verdict.evidence.protocol` is `chessbench_puzzles.stepwise.v1`; the receipt includes
`status`, `measured`, limits, cleanup facts and the controller's bounded transport
events. An incomplete task reaches `evaluate().invalid[task_id].receipt` and is excluded
from `per_task` and the cache. Offline evidence retains
`official.protocol = "offline strict sequence; not interactive official accuracy"`
and both existing replay diagnostics.

Curve points carry `evaluation_protocols[task_id]` and `protocol_comparability`.
Interactive measurements use separate cache keys. Evaluation refuses to aggregate
interactive and offline ChessBench tasks into one point, and `tools/plot_curve.py`
rejects comparison across those protocols or a protocol change within one curve.
Historical ChessBench points without this field belong to the existing offline path.

`tests/quality/test_chessbench_stepwise_runner.py` exercises real sandboxed actor
processes with fabricated puzzles, including private-field requests, polluted public
observations, interrupted exchanges, partial-message deadlines, oversized messages,
cache separation, offline evidence, saved incomplete receipts and comparison refusal.
These tests establish execution wiring and isolation for those probes. They do not
establish model-driven interactive accuracy on the released slice, compatibility with
an existing harness's move-selection loop, a real diagnostic receipt, or pilot
authorization. A diagnostic/pilot still needs its normal dataset, provenance,
resource, coverage and cleanup gates.
