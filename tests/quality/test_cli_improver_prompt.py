"""CLI 改进器的提示词:**规则说什么要改,平台说什么不许坏,两件事不能互相替换。**

实测(`codex-dgm`,2026-10-05,codex 驱动本地 9B):DGM 给了 codex 一段自己的提示词,codex
把 635 行的 harness 删到 179 行,新文件在平台传 `--task` 的地方读 `sys.argv[1]`。两轮十道
题全部在启动时崩掉,曲线上是两个 0.000 —— 一个「跑起来但输了」的数字,用来表示「一次都
没跑起来」。

原因是一行代码:`propose` 写的是 `prompt or PROMPT`。规则一旦自带提示词,平台那几条硬
规则就整段消失了,包括「`harness.json` 不许改」和「入口必须还能跑」。默认提示词里一直有
这些规则 —— 有,但不生效,这比没有更坏:它让「平台规定了契约」这件事只在一个没人走的
分支上成立。
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import methods.cli_improver as ci  # noqa: E402


def test_a_rules_prompt_cannot_drop_the_hard_rules():
    """规则提示词 + 硬规则,两条都在;不是二选一。"""
    text = ci.instruction("DGM round 1: target the failure on cancel-async-tasks.")
    assert "target the failure" in text, "规则自己的话丢了"
    for rule in ("harness.json", "env_kinds", "--task", "--workdir", "answer.txt"):
        assert rule in text, f"硬规则里的 {rule!r} 没送到改进器"


def test_the_shipped_prompt_is_used_when_a_rule_supplies_none():
    assert ci.instruction(None) == ci.PROMPT
    assert ci.instruction("") == ci.PROMPT
    assert ci.HARD_RULES in ci.PROMPT, "默认提示词自己都不含硬规则"


def test_the_hard_rules_state_the_consequence_and_the_size_rule():
    """「不许」要带着后果,否则它只是一句礼貌话。

    入口那一句必须点名平台**怎么调用**它(`--task`/`--workdir`),因为这次踩的正是这个:
    被删掉的那份文件仍然是个能跑的 Python 程序,只是不认识平台的命令行。
    """
    assert "rejects" in ci.HARD_RULES, "没写违反的后果"
    assert "--task" in ci.HARD_RULES and "--workdir" in ci.HARD_RULES
    assert "Change as little" in ci.HARD_RULES, "没有「少改」这条"


def test_the_instruction_is_what_the_improver_is_actually_run_with(monkeypatch, tmp_path):
    """端到端:送进 argv 的必须是 `instruction(...)`,不是 `prompt or PROMPT`。"""
    seen: dict = {}

    class _Proc:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_run(argv, **kw):
        seen["argv"] = argv
        return _Proc()

    # 只换掉两件与提示词无关的事:证据怎么摆、改进器这条命令怎么拼。
    monkeypatch.setattr(ci, "_stage_evidence", lambda *a, **k: None)
    monkeypatch.setattr(ci, "_improver_command", lambda req: ["codex"])
    monkeypatch.setattr(ci.subprocess, "run", fake_run)
    parent = tmp_path / "parent"
    parent.mkdir()
    (parent / "harness.json").write_text("{}")
    workspace = tmp_path / "ws"
    workspace.mkdir()
    req = {"workspace": str(workspace), "candidate": str(tmp_path / "cand")}
    ci.propose(req, parent, prompt="rule prompt here")
    assert seen["argv"], "没真的调用改进器"
    tail = seen["argv"][-1]
    assert "rule prompt here" in tail
    assert "harness.json" in tail and "--workdir" in tail, (
        "规则自带提示词时,硬规则又没有跟着走")
