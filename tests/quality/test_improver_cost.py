"""测量代价的记录：CLI improver 的花费是"未知"，不是"0"。

背景（实测）：九个方法都走 `editor.ask → _ask_cli`。CLI 的 provider 在 agent 进程内部，
它只吐 transcript 不吐 usage —— 所以平台拿不到 token。此前 `spent_tokens()` 把它求和成
**0**，曲线点上写着 `method_generation_tokens: 0`，读起来是"改进器一分钱没花"，而真相是
"没人数过"。做效率分析时这两件事差得很远。

同时 `_ask_cli` 把 improver 自己返回的 `reported`（退出码、秒数、改了哪些文件、环境白名单
剥掉了什么）**整块丢掉**了，于是"每轮 improver 花了多久"在记录里根本查不到。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import methods.editor as editor                                          # noqa: E402


@pytest.fixture(autouse=True)
def _clean():
    editor.reset_spent()
    editor._LAST_IMPROVER.clear()
    yield
    editor.reset_spent()
    editor._LAST_IMPROVER.clear()


class _Usage:
    def __init__(self, prompt, completion, model="m"):
        self.prompt_tokens, self.completion_tokens, self.model = prompt, completion, model


def test_a_cli_improvers_spend_is_unknown_not_zero():
    """CLI 路径必须记 `None`。0 是一个声明，而这里没人能做这个声明。"""
    editor._SPENT["source"] = "cli_unreported"
    assert editor.spent_tokens() is None
    assert editor.spend_source() == "cli_unreported"


def test_an_endpoint_reply_after_a_cli_call_restores_counting():
    """flag 不能越过它描述的那次调用活下去。"""
    editor._SPENT["source"] = "cli_unreported"
    editor._record_usage(_Usage(1500, 500), "m")
    assert editor.spend_source() == "endpoint"
    assert editor.spent_tokens() == 2000


def test_reset_clears_the_flag_too():
    editor._SPENT["source"] = "cli_unreported"
    editor.reset_spent()
    assert editor.spend_source() is None
    assert editor.spent_tokens() == 0


def test_the_improvers_own_account_rides_along_under_its_own_key():
    """方法的 key 不能和 improver 的 key 撞；没有 CLI improver 时整块不出现。"""
    editor._LAST_IMPROVER.update({"exit_code": 0, "seconds": 597.3, "files_changed": 1,
                                  "prompt_chars": 24000, "spend_reported": False})
    merged = editor._reported_with_improver({"sica_rule": {"x": 1}})
    assert merged["sica_rule"] == {"x": 1} and merged["improver_run"]["seconds"] == 597.3
    editor._LAST_IMPROVER.clear()
    assert "improver_run" not in editor._reported_with_improver({"sica_rule": {}})


def test_a_one_step_batch_puts_the_methods_record_on_the_envelope():
    """**这条是修一个既存缺陷**：`report_many` 的信封曾只写 `{"steps": n}`，
    于是 DGM / HyperAgents / Meta-Harness 这类批量提交的方法，它们自己的规则记录只落在
    step payload 里，曲线点上读不到。"""
    envelope = editor._batch_reported([{"method_reported": {"sica_rule": {"a": 1}}}], [{}])
    assert envelope["sica_rule"] == {"a": 1}
    assert envelope["steps"] == 1


def test_a_multi_step_batch_does_not_choose_between_its_steps():
    envelope = editor._batch_reported(
        [{"method_reported": {"a": 1}}, {"method_reported": {"a": 2}}], [{}, {}])
    assert envelope["per_step"] == [{"a": 1}, {"a": 2}]
    assert "a" not in envelope, "两个不同的记录不能被悄悄合并成一个"


def test_the_step_says_where_its_spend_numbers_came_from():
    step = editor._step_payload(harness_dir=ROOT / "methods" / "noop", label="x",
                                edit_kind="none", changed=False, tokens_now=None,
                                method_reported=None, incumbent_round=None)
    assert step["claimed_cost"]["generation_tokens"] is None
    assert "method_spend_source" in step["claimed_cost"]


def test_report_many_puts_the_methods_record_where_the_platform_reads_it(tmp_path, capsys):
    """端到端：`report_many` 的 stdout 信封必须带方法的记录。

    平台读的是方法进程的 stdout，所以信封就是曲线点 `method_reported` 的来源。
    红检：把信封改回 `{"steps": n}`，这条立刻失败 —— 那正是修复前的行为。
    """
    out = tmp_path / "traj.json"
    step = {"harness_dir": ROOT / "methods" / "noop", "changed": False, "label": "x",
            "edit_kind": "none", "method_reported": {"sica_rule": {"a": 1}},
            "hypothesis": "h"}
    editor.report_many({"trajectory_out": str(out)}, method="noop", steps=[step],
                       acceptance_rule="t")
    envelope = json.loads(capsys.readouterr().out)
    assert envelope["method_reported"]["sica_rule"] == {"a": 1}
