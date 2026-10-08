"""Small verbatim transcription of LiveCodeBench's published pass@k scorer."""
from __future__ import annotations

import math


def estimate_pass_at_k(n: int, c: int, k: int) -> float:
    """Transcribed from lcb_runner/evaluation/pass_k_utils.py:7-12."""
    if n - c < k:
        return 1.0
    product = 1.0
    for i in range(n - c + 1, n + 1):
        product *= 1.0 - k / i
    return 1.0 - product


def test_official_pass_at_k_examples():
    assert estimate_pass_at_k(1, 1, 1) == 1.0
    assert math.isclose(estimate_pass_at_k(2, 1, 1), 0.5)


def test_release_has_no_reference_solution_field():
    import json
    from pathlib import Path
    path = Path("/mnt/20t/xubuqiang/datasets/livecodebench/_src/test6.jsonl")
    row = json.loads(path.read_text().splitlines()[0])
    assert "reference_solution" not in row and "gold" not in row
