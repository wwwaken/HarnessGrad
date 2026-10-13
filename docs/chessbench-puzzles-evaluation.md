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
and import namespace. The actor receives only the six fields shown above: no stored
line, expected solver move, future opponent move, line length, source row, puzzle ID,
gold answer or pre-setup FEN. Previously observed opponent effects are public board
state; future reference updates remain private. The controller owns the ordered
observations/submissions and termination record. An actor-written sequence or transcript
cannot attest that intermediate boards were delivered before decisions.

Importing the adapter does not read `puzzles.csv`. Accessing pool-backed `ENV`, `SPLIT`,
`SETUP`, `VERIFY`, `_RECORDS` or `load()` remains an explicit pool-loading operation;
those operations are not needed for synthetic contract tests. Verifier evidence redacts
the private gold, while retaining both score diagnostics.

## Current boundary and validation

The trusted stepwise session and public task/answer contract are implemented. The shared
QA runner still uses the offline `answer.txt` sequence interface; a future trusted
controller transport must connect successive observations to actor decisions before
an interactive official-accuracy claim is possible. This change does not launch a
model, H0 or release-data control, and does not access heldout puzzle payloads.

Focused synthetic tests cover legal replay, illegal/null/self-check moves, wrong order,
missing moves, setup/opponent legality, exact/alternate early mate, public field privacy,
lazy import and materialized-verifier diagnostics. Synthetic differential tests compare
the preserved diagnostic against the existing verbatim upstream function. Release-data
and source-archive tests remain available but are outside this validation scope.
