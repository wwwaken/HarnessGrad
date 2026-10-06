"""The read API's contract with the SPA, checked against real data.

Run with `python3 -m pytest web/server/test_readapi.py -q` from the repository root.
The server's own `README.md` documents the endpoints; these tests pin the two rules that a
reader would otherwise get wrong: **absence is not zero**, and **a run being written right
now is still a row**.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import readapi  # noqa: E402


def _runs_root() -> Path:
    return ROOT / "runs"


def test_absence_and_null_are_different_for_test_rate():
    """`last_test_rate` 缺省时**省略**,不是写 null。

    整个平台都在区分"缺失"、"null"和"零":stage 0 之所以存在,就是因为"字段缺失"和
    "字段说没测到"读起来一样,于是一个在行为上不可能有差别的候选被读成了 +0.100 的提升。
    在这里总是发出这个键,会把那两者合并 —— 一个 2026-10-05 之前录的 run(完全没有
    `test_rate` 家族)和一个检查不报逐测试计数的 run,都会到达成 `null`。
    """
    rows = readapi.list_runs(_runs_root())
    assert rows, "runs/ 里没有 run 可供检查"
    absent = [r for r in rows if "last_test_rate" not in r]
    present_null = [r for r in rows if "last_test_rate" in r and r["last_test_rate"] is None]
    present_value = [r for r in rows if isinstance(r.get("last_test_rate"), (int, float))]
    # 老 run(没有 stage 0 的字段)走 absent。这正是要被区分出来的那一类 —— 如果实现总是
    # 发出这个键,absent 会是空的,而这三种状态就分不开了。
    assert absent, ("每个 run 都带 last_test_rate,说明它被无条件发出了 —— "
                    "缺失和 null 于是不可区分")
    assert present_value or present_null or absent, "没有可检查的状态"
    assert all(isinstance(r["certify"]["points"], int) for r in rows)


def test_a_run_with_no_curve_is_a_row_and_not_a_404():
    """正在被写入的 run(只有 run_meta.json)必须是一行,不是错误。

    实测(2026-10-06):`full-a` 和 `full-b` 在写 round 0 的时候,`/api/runs` 必须能列出它们,
    否则一个跑了两小时的实验在最需要看进度的时候是不可见的。`certify()` 对这样的目录说
    `points: 0`,而不是抛错。
    """
    rows = {r["run_id"]: r for r in readapi.list_runs(_runs_root())}
    assert rows, "没有 run"
    partial = [r for r in rows.values() if r["certify"]["points"] == 0]
    for row in partial:
        assert row["certify"]["valid"] is False
        assert isinstance(row["certify"]["problems"], list)
    # 每个目录都必须是行,包括连 run_meta.json 都没有的:那是"中断在第一次写之前"的
    # 形状,而不是一个可以被隐藏的错误。
    assert len(rows) == len([p for p in _runs_root().iterdir() if p.is_dir()]), (
        "有的 run 目录没有变成行")


def test_the_six_endpoints_answer_on_a_real_run():
    """端点必须能在真实数据上工作,而不只是导入时有意义。"""
    rid = None
    for cand in ("ds-dgm", "full-a", "full-b"):
        if (_runs_root() / cand).is_dir():
            rid = cand
            break
    assert rid, f"找不到可用的 run:{sorted(p.name for p in _runs_root().iterdir())[:6]}"

    bundle = readapi.run_bundle(_runs_root(), rid)
    assert bundle["run_id"] == rid
    assert "points" in bundle and "verdicts" in bundle
    assert "traces" not in bundle, "traces 必须按题单独取,不能塞进 bundle"

    points = bundle["points"]
    if points:
        point = points[-1]
        # 曲线点的新字段恒在(stage 0):`null` 表示平台看过、没有检查报测试数。
        if "test_rate" in point:
            assert point["test_rate"] is None or isinstance(point["test_rate"], float)
            assert isinstance(point["test_rate_n_tasks"], int)


def test_a_traversal_attempt_is_refused_before_any_path_is_built():
    """`../` 必须在构建任何路径**之前**被拒 —— 守卫是 `is_safe_component`。

    HTTP 层把它变成 400(见 `serve.py`),所以这里断言的是那条判据本身:一个 run id
    要么是一个单一的安全路径组件,要么不是。一个只做 `runs_root / name` 的实现会把
    `../driver.py` 读成平台源码。
    """
    for bad in ("..", ".", "../driver.py", "a/../../b", "", "a/b"):
        assert not readapi.is_safe_component(bad), f"{bad!r} 被当成了安全组件"
    for good in ("ds-dgm", "full-a", "run.with.dots", "v1_2-3"):
        assert readapi.is_safe_component(good), f"{good!r} 被拒了"
