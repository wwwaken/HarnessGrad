"""ChessBench's 10,000-puzzle tactical slice.

Source: `google-deepmind/searchless_chess`, ChessBench paper (NeurIPS 2024,
arXiv:2402.04494), `puzzles.csv`.

The agent sees the position *after* the first move in `Moves`, because the first move is
the opponent's setup move. It submits the remaining solver moves as space-separated UCI
moves. The checker replays the fixed opponent moves and applies the official scorer's
rule: an exact expected move passes, and a different move also passes when it immediately
checkmates (Lichess accepts every mate-in-one).

This is an offline scripted-policy evaluation of the puzzle slice, not a replication of
ChessBench's neural-engine evaluation or its Elo results. The submitted sequence supplies
moves on successive calls to the official engine interface; fixed opponent continuations
stay private. As upstream does, the checker ignores unused trailing moves and terminates
immediately on a differing mate-in-one. An interactive engine can condition each move on
a newly observed board; this static interface cannot, and results must name this variant.
"""
from __future__ import annotations

import csv
from pathlib import Path

import chess
import chess.pgn

from data.qa import base

KIND = "dataset"

#: The oracle control submits the benchmark's own released reference; see
#: `data/dataset.schema.json` (`module.oracle_about`) for what the other value means.
ORACLE_SOURCE = "released"
DATASET_ROOT = Path("/mnt/20t/xubuqiang/datasets/chessbench_puzzles")
CSV_PATH = DATASET_ROOT / "_src" / "puzzles.csv"
CSV_MEMBER = "puzzles.csv"
REVISION = "90ae0e6b121673fc3079aaeffa047580bb600c0a"
CSV_SHA256 = "099d54e681a07b9e82b4462aaf5436a6e833edc6f56b92ea7c2d2413f7efbe48"


def _read_rows() -> list[dict]:
    with CSV_PATH.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 10000:
        raise ValueError(f"ChessBench expected 10000 rows, got {len(rows)}")
    return rows


def _presented_fen(row: dict) -> str:
    moves = row["Moves"].split()
    if not moves:
        raise ValueError(f"{row['PuzzleId']}: empty Moves")
    board = chess.Board(row["FEN"])
    board.push_uci(moves[0])
    return board.fen()


def _rows() -> dict[str, list[dict]]:
    out = []
    for row in _read_rows():
        moves = row["Moves"].split()
        out.append({
            "puzzle_id": row["PuzzleId"],
            "rating": int(row["Rating"]),
            "fen": row["FEN"],
            "presented_fen": _presented_fen(row),
            "moves": moves,
        })
    return {"test": out}


def _question(row: dict) -> str:
    return (
        "Solve this ChessBench tactical puzzle. The opponent's setup move has already "
        "been applied.\n\n"
        f"Position (FEN): {row['presented_fen']}\n\n"
        "Submit the solver's moves as space-separated UCI moves, for example "
        "`e2e4 g8f6`. Do not include the opponent's setup move."
    )


def _gold(row: dict) -> dict:
    return {
        "answer": " ".join(row["moves"][1::2]),
        "fen": row["fen"],
        "moves": row["moves"],
        "puzzle_id": row["puzzle_id"],
    }


def _goal(question: str, gold: dict) -> str:
    return (
        f"{question}\n\n"
        "Write the UCI move sequence alone to `answer.txt`; the qa submit command is "
        "`python3 qa/bin/qa submit \"<moves>\"`. "
        "The first move in the released solution is the opponent's move and must not be "
        "submitted."
    )


def _official_replay(board: chess.Board, moves: list[str], predicted: list[str]) -> bool:
    """The official `evaluate_puzzle_from_board` loop, with engine output supplied by us.

    Upstream source: `src/puzzles.py`, lines 74-94 at the pinned repository revision.
    `predicted` replaces `engine.play(board).uci()` so the dataset answer contract can carry
    a complete scripted sequence instead of a live engine object.
    """
    solver_index = 0
    for move_idx, move in enumerate(moves):
        # According to the Lichess puzzle format, index 0 is the opponent setup move and
        # index 1 is the first move presented to the player.
        if move_idx % 2 == 1:
            if solver_index >= len(predicted):
                return False
            predicted_move = predicted[solver_index]
            solver_index += 1
            if move != predicted_move:
                try:
                    board.push(chess.Move.from_uci(predicted_move))
                except ValueError:
                    return False
                # Lichess accepts any mate-in-one when it differs from the stored line.
                return board.is_checkmate()
            try:
                board.push(chess.Move.from_uci(predicted_move))
            except ValueError:
                return False
        else:
            try:
                board.push(chess.Move.from_uci(move))
            except ValueError:
                return False
    # Like an Engine, only requested moves count; trailing scripted moves are unused.
    return True


def score(prediction: str, gold: dict) -> dict:
    tokens = prediction.strip().split()
    moves = list(gold["moves"])
    board = chess.Board(gold["fen"])
    if not moves:
        return {"reward": 0.0, "correct": False, "official": {"metric": "invalid empty Moves"},
                "why": "released puzzle has no Moves"}
    try:
        hit = _official_replay(board, moves, tokens)
    except (ValueError, AssertionError):
        hit = False
    return {
        "reward": 1.0 if hit else 0.0,
        "correct": hit,
        "official": {
            "metric": "ChessBench official puzzle replay",
            "puzzle_id": gold["puzzle_id"],
            "solver_moves": len(moves[1::2]),
            "prediction_moves": len(tokens),
            "alternate_mate_in_one": True,
        },
        "why": "official move replay accepted" if hit else "official move replay failed",
    }


def downloads() -> list[dict]:
    return [
        {
            "kind": "http",
            "name": "ChessBench puzzles.csv",
            "version": REVISION,
            "url": "https://storage.googleapis.com/searchless_chess/data/puzzles.csv",
            "size": "4,705,735 bytes",
            "sha256": CSV_SHA256,
            "dst": "_src/puzzles.csv",
            "note": "Canonical ChessBench slice. Trap: the first Moves token is the opponent setup move; the scorer predicts only odd-indexed solver moves and accepts alternate immediate mates.",
        },
        {
            "kind": "http",
            "name": "ChessBench official scorer source",
            "version": REVISION,
            "url": "https://codeload.github.com/google-deepmind/searchless_chess/tar.gz/" + REVISION,
            "size": "~2.2 MB compressed",
            "sha256": "9cf0832b04024a9e0a6edb59f0dee62aeadee3b9b97799b9a7521b2221f7d39a",
            "dst": "_src/searchless_chess.tar.gz",
            "extract_to": "_src",
            "note": "Pins src/puzzles.py lines 74-94 for the verbatim scorer and drift check. Fetch this small source archive, not the terabyte-scale ChessBench training corpus.",
        },
        {
            "kind": "pip",
            "name": "python-chess",
            "version": "1.11.2",
            "package": "chess",
            "size": "~148 KB wheel",
            "note": "Parses FEN, PGN and UCI moves. Pin this dependency because board legality and checkmate are part of the official metric, not optional parsing convenience.",
        },
    ]


def provision_status() -> dict:
    return {
        "root": str(DATASET_ROOT),
        "present": CSV_PATH.is_file() and CSV_PATH.stat().st_size == 4705735,
        "split_dir": str(DATASET_ROOT),
        "files": [str(CSV_PATH)],
        "present_files": [str(CSV_PATH)] if CSV_PATH.is_file() else [],
        "tasks": 10000,
    }


_SPEC = base.QASpec(
    name="chessbench_puzzles",
    root=DATASET_ROOT,
    rows=_rows,
    question=_question,
    gold=_gold,
    goal=_goal,
    score=score,
    downloads=downloads,
    split="test",
    source="google-deepmind/searchless_chess@" + REVISION + " data/puzzles.csv",
)

_BUILT = _SPEC.build()
DEFAULT_ENV = _BUILT["DEFAULT_ENV"]
ENV = _BUILT["ENV"]
SPLIT = _BUILT["SPLIT"]

#: The benchmark's own evaluation set, within this adapter's pool. The pool is the whole released `puzzles.csv` (10,000), which is the
#: benchmark's puzzle slice.
#:
#: Read from `QASpec.division()` -- the one place that decides what this pool's
#: division is -- and `None` because the benchmark released no study split for this
#: table: the pool **is** the scored split, so every task in it belongs to the
#: evaluation set, and that claims nothing about whether the pool is the whole of it.
#: `--split official --side eval` scores the whole pool, which is the comparable run;
#: `--split declared` keeps the platform's hash third (`SPLIT_SOURCE == "hash"`).
OFFICIAL_EVAL = _BUILT["OFFICIAL_EVAL"]

#: Which rule produced `SPLIT`: `"hash"` here -- the benchmark published no study
#: split, so the platform imposes one. See `data/qa/base.py::division`.
SPLIT_SOURCE = _BUILT["SPLIT_SOURCE"]


def __getattr__(name: str):
    return base.module_getattr(_SPEC, name)


def load() -> tuple[list[dict], dict[str, str]]:
    return _SPEC.load()


__all__ = ["KIND", "DATASET_ROOT", "REVISION", "load", "downloads", "score", "SPLIT", "ENV"]
