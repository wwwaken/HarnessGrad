"""DGM's staged small -> medium -> full evaluation schedule."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Stage:
    name: str
    budget: int
    full: bool = False


@dataclass(frozen=True)
class Evaluation:
    node_id: str
    stage: str
    submitted: int
    resolved: int
    score: float | None = None

    @property
    def completion(self) -> float:
        return self.submitted and self.resolved / self.submitted or 0.0


@dataclass(frozen=True)
class DGMStagedScheduler:
    """Immutable scheduler matching DGM's additional-evaluation gate."""

    stages: tuple[Stage, ...] = (Stage("small", 0), Stage("medium", 0),
                                  Stage("full", 0, True))
    escalation_threshold: float = 0.4

    def __post_init__(self) -> None:
        if not self.stages:
            raise ValueError("at least one stage is required")
        if not 0 <= self.escalation_threshold <= 1:
            raise ValueError("escalation threshold must be in [0, 1]")

    def next_stage(self, evaluations: Iterable[Evaluation], node_id: str) -> Stage | None:
        done = [e for e in evaluations if e.node_id == node_id]
        if not done:
            return self.stages[0]
        current = max((self._index(e.stage) for e in done), default=-1)
        latest = max(done, key=lambda e: self._index(e.stage))
        if latest.completion < self.escalation_threshold:
            return None
        return self.stages[current + 1] if current + 1 < len(self.stages) else None

    def budget_plan(self, evaluations: Iterable[Evaluation], node_id: str) -> dict:
        nxt = self.next_stage(evaluations, node_id)
        return {"node_id": node_id, "next_stage": nxt.name if nxt else None,
                "stage_index": self._index(nxt.name) if nxt else None,
                "escalation_threshold": self.escalation_threshold,
                "score_provenance": "study_only_until_full"}

    def consume(self, evaluations: Iterable[Evaluation], node_id: str,
                available: int) -> tuple[Stage | None, int, dict]:
        """Reserve only the next stage's budget; never charge full eval twice."""
        if available < 0:
            raise ValueError("available budget cannot be negative")
        nxt = self.next_stage(evaluations, node_id)
        if nxt is None:
            return None, 0, {"node_id": node_id, "budget_before": available,
                             "budget_after": available, "consumed": 0}
        consumed = min(available, max(0, nxt.budget))
        return nxt, consumed, {"node_id": node_id, "stage": nxt.name,
                               "budget_before": available,
                               "budget_after": available - consumed,
                               "consumed": consumed,
                               "truncated": consumed < nxt.budget}

    def full_eval_threshold(self, scores: Iterable[float], baseline: float) -> float:
        values = [float(baseline), *(float(s) for s in scores)]
        values.sort(reverse=True)
        return max(values[1] if len(values) > 1 else values[0], 0.4)

    def _index(self, name: str) -> int:
        for i, stage in enumerate(self.stages):
            if stage.name == name:
                return i
        raise ValueError(f"unknown DGM evaluation stage {name!r}")
