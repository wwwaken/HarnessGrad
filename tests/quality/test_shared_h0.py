"""共用的 round 0：九个方法必须看到**同一个**第一分。

**为什么需要它。** 方法的第一条输入是 round 0 —— 平台在原始 harness 上的测量。每个 run 各测
一次时，批次组成不同会让浮点累加顺序不同，偶尔翻一个 token，于是方法 A 看到 0.53、方法 B
看到 0.51，而记录上两者都写"round 0"。方法读到的 trace 也可能不是同一批。比较的前提是
它们被提供了同一份证据，而不是"通常一样"。

`--h0-from RUN` 让一个 run 复用另一个 run 的 round-0 测量：分数、逐题结果、身份（它是**怎么**
被测出来的）、以及 trace 一起搬过来，点上的 `shared_from` 说明出处。两个 run 的 base 树不同
时**拒绝**，因为那已经不是同一个起点。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _run(tmp_path: Path, run_id: str, *extra: str) -> subprocess.CompletedProcess:
    argv = [sys.executable, "driver.py", "--harness", "loop_plain", "--mode", "A",
            "--rounds", "0", "--dataset", "demo", "--sampling", "all", "--jobs", "1",
            "--run-id", run_id, "--runs-root", str(tmp_path / "runs"),
            "--work-root", str(tmp_path / f"work-{run_id}"),
            "--method-entrypoint", f"{sys.executable} {ROOT / 'methods/noop/run.py'}",
            *extra]
    return subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=600,
                          env={**os.environ, "HG_AGENT_BACKEND": "mock"})


def _first_point(tmp_path: Path, run_id: str) -> dict:
    path = tmp_path / "runs" / run_id / "curve.jsonl"
    return json.loads(path.read_text().splitlines()[0])


def test_a_run_reuses_another_runs_round_zero(tmp_path):
    """复用之后：分数与逐题结果**一模一样**，并且点自己说出它来自谁。"""
    donor = _run(tmp_path, "donor")
    assert donor.returncode == 0, donor.stderr[-800:]
    assert (tmp_path / "runs" / "donor" / "h0.json").is_file(), "donor 必须留下可复用的测量"

    consumer = _run(tmp_path, "consumer", "--h0-from", "donor")
    assert consumer.returncode == 0, consumer.stderr[-800:]

    a, b = _first_point(tmp_path, "donor"), _first_point(tmp_path, "consumer")
    assert b["per_task"] == a["per_task"], "逐题结果必须完全相同"
    assert b["score"] == a["score"]
    assert b["shared_from"]["run_id"] == "donor"
    assert b["run_id"] == "consumer", "点仍属于本 run，出处写在 shared_from 里"
    # 身份描述的是"这个数是怎么产生的"，所以它保持 donor 的，不是本 run 的
    assert b["identity"] == a["identity"]


def test_reusing_a_measurement_from_a_different_base_tree_is_refused(tmp_path):
    """base 树不同就不是同一个起点，必须拒绝而不是悄悄换一个分数。"""
    donor = _run(tmp_path, "donor")
    assert donor.returncode == 0, donor.stderr[-600:]
    payload = tmp_path / "runs" / "donor" / "h0.json"
    data = json.loads(payload.read_text())
    data["h0_sha"] = "0" * 40
    payload.write_text(json.dumps(data))

    consumer = _run(tmp_path, "consumer", "--h0-from", "donor")
    assert consumer.returncode != 0
    assert "base" in consumer.stderr and "refusing" in consumer.stderr


def test_a_missing_donor_is_refused(tmp_path):
    consumer = _run(tmp_path, "consumer", "--h0-from", "no-such-run")
    assert consumer.returncode != 0
    assert "refusing" in consumer.stderr
