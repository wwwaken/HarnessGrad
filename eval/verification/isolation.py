"""Executed scorer topology and class-compatible score aggregation.

Declarations select a runtime; they never attest that it ran. Only the verifier
sets the observed class. Legacy records without observations remain unknown.
"""
from __future__ import annotations

from data.scaffolds.scorer_isolation import CLASSES, declared_class


class IsolationMismatch(ValueError):
    pass


def observed_class(record: dict | None) -> str:
    value = (record or {}).get("scorer_isolation_class")
    return value if isinstance(value, str) and value in CLASSES else "unknown"


def common_class(classes) -> str:
    values = {c if isinstance(c, str) and c in CLASSES else "unknown" for c in classes}
    if len(values) > 1:
        raise IsolationMismatch("scorer isolation class mismatch: " + ", ".join(sorted(values)))
    return next(iter(values), "unknown")


def require_comparable(left: dict, right: dict) -> str:
    value = common_class([observed_class(left), observed_class(right)])
    if value == "unknown":
        raise IsolationMismatch("scorer isolation class unknown: comparison invalid")
    return value


def record_class(verdict: dict, spec: dict | None, actual: str) -> dict:
    declared = declared_class(spec)
    verdict = {**verdict, "scorer_isolation_class": actual,
               "scorer_isolation_declared": declared}
    if declared not in ("unknown", actual):
        verdict.update(passed=False, score=None,
                       unmeasured=f"scorer isolation class mismatch: declared {declared}, ran {actual}")
    return verdict
