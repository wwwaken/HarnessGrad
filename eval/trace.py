"""Compatibility adapter for the canonical trace reader in `eval.tracing`.

The implementation lives in `eval.tracing`: `first_object` parses model replies and
`loop_facts` summarizes JSON-lines traces. This module re-exports those functions and
the end-state constants for existing callers; it performs no parsing of its own.
New callers should import from `eval.tracing`.
"""
from __future__ import annotations

from eval.tracing import (
    ENDED_ANSWERED,
    ENDED_BUDGET,
    ENDED_CRASHED,
    ENDED_PARSE_ERROR,
    ENDED_UNKNOWN,
    _ended,
    first_object,
    loop_facts,
)

__all__ = ["first_object", "loop_facts", "ENDED_CRASHED", "ENDED_ANSWERED",
           "ENDED_PARSE_ERROR", "ENDED_BUDGET", "ENDED_UNKNOWN"]
