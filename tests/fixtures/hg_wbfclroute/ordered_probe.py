#!/usr/bin/env python3
"""Preserve upstream import order; importing chess.engine is not a dependency shim."""
import chess.engine
from execute import run
run('import', 'searchless_chess.src.engines.stockfish_engine')
