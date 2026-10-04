"""一次读不懂的回复,不该结束整道题。

**这是数出来的,不是想出来的。** 统计所有跑道里"方法自己写了理由"的 35 个轮次,
**16 个在修解析或格式容错**,而且几乎每条跑道的第一轮都在修它:

    flash-three-2 r1      Stop one unparseable reply from ending the task
    deepseek-eigen-2 r1   ...unparseable model reply is fed back as an observation and retried
    strong-model-1 r2     Changing parse errors from terminating the loop into a user-facing retry
    loop-terminal_bench-26452c r1   Fixed the JSON parsing logic in `_parse()` to be more robust

而 `loop-terminal_bench-26452c` 的轨迹说明死得多干净:五道题,每道题**只调了一次模型**
(`calls: 1`),就写着 `parse_error: Extra data`,整道题结束。那一轮的每一次实验,都从
同一个不能用的 harness 出发。

更贵的代价在方法之间:RRSI 的 leakage critic 两次把"修 `_parse`"的候选判成
TASK-SPECIALIZATION / LEAKAGE 并拒绝 —— 一轮就这样没了。方法们开始比"谁先想到修 parser",
而这不是我们要测的能力。

所以修在起点 harness 里。三次测试:能救回来、救不回来时记录里有 N 次尝试、
而"第一个 JSON 对象"的容错仍然照旧。
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _load():
    path = ROOT / "base_harness" / "loop" / "agent.py"
    spec = importlib.util.spec_from_file_location("hg_loop_parse", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def agent():
    return _load()


def _scripted(agent, replies: list[str]):
    """按剧本回复的假模型,同时记下每次发过去的历史长度。"""
    seen: list[int] = []

    def fake(messages):
        seen.append(len(messages))
        return replies[min(len(seen) - 1, len(replies) - 1)]

    return fake, seen


def _events(workdir: Path) -> list[dict]:
    return [json.loads(l) for l in (workdir / "trace.jsonl").read_text().splitlines()]


def test_a_prose_reply_is_fed_back_and_the_task_continues(agent, tmp_path, monkeypatch):
    """模型先说了一段话,然后才给出动作。以前这里整道题就结束了。"""
    fake, seen = _scripted(agent, [
        "I will inspect the directory first.",              # 读不出动作
        '{"tool": "bash", "command": "true"}',               # 一个合法动作
        '{"answer": "done"}',
    ])
    monkeypatch.setattr(agent, "_complete", fake)
    assert agent.run({"goal": "say done"}, tmp_path) == "done"

    events = _events(tmp_path)
    retries = [e for e in events if "parse_error" in e]
    assert len(retries) == 1, events
    assert retries[0]["parse_retry"] == 0
    # 退回的消息真的发出去了:第二次调用时历史更长(assistant + user 两条)
    assert seen[1] >= seen[0] + 2, seen


def test_when_it_never_parses_the_record_shows_every_attempt(agent, tmp_path, monkeypatch):
    """救不回来时,记录里要看得见试了几次 —— 一次尝试和 N 次尝试不是同一件事。"""
    fake, seen = _scripted(agent, ["still just talking"])
    monkeypatch.setattr(agent, "_complete", fake)
    assert agent.run({"goal": "unreachable"}, tmp_path) == ""

    events = _events(tmp_path)
    retries = [e for e in events if "parse_error" in e]
    assert len(retries) == agent.PARSE_RETRIES + 1, (len(retries), agent.PARSE_RETRIES)
    assert [e["parse_retry"] for e in retries] == list(range(agent.PARSE_RETRIES + 1))
    assert len(seen) == agent.PARSE_RETRIES + 1, "每次重试都必须真的再调一次模型"


def test_the_first_json_object_is_still_extracted(agent, tmp_path, monkeypatch):
    """容错那条路不能被这次改动弄坏:两个对象、外加散文,取第一个。"""
    fake, _ = _scripted(agent, [
        'Sure:\n{"tool": "bash", "command": "true"}}\n{"answer": ""}\n',
        '{"answer": "ok"}',
    ])
    monkeypatch.setattr(agent, "_complete", fake)
    assert agent.run({"goal": "ok"}, tmp_path) == "ok"
    assert not [e for e in _events(tmp_path) if "parse_error" in e], _events(tmp_path)


# ------------------------------------------------ 收尾提醒与重复提醒 ---

def _run_scripted(agent, tmp_path, monkeypatch, replies, *, max_steps=6, nudge=2):
    """跑一次脚本化的 run(),把 MAX_STEPS 缩小,返回 trace 事件。"""
    monkeypatch.setattr(agent, "MAX_STEPS", max_steps)
    monkeypatch.setattr(agent, "FINISH_NUDGE_STEPS", nudge)
    fake, _ = _scripted(agent, replies)
    monkeypatch.setattr(agent, "_complete", fake)
    agent.run({"goal": "say done"}, tmp_path)
    return _events(tmp_path)


def test_a_repeated_command_gets_a_nudge(agent, tmp_path, monkeypatch):
    """266 条历史轨迹里 73 条跑满步数、0 条交卷,而最后两步常是同一条命令。

    实测抽样:`python /app/test_outputs.py 2>&1` 两次、同一条 `echo ... >` 两次、
    同一个 `cat > /app/run.py << 'EOF'` 两次。模型不是做错了,是没停下来。
    """
    same = '{"tool": "bash", "command": "true"}'
    events = _run_scripted(agent, tmp_path, monkeypatch, [same, same, same], max_steps=6)
    nudges = [e for e in events if "repeat_nudge" in e]
    assert len(nudges) == agent.REPEAT_NUDGE_LIMIT, nudges
    assert nudges[0]["repeat_nudge"] == "true"


def test_different_commands_do_not_trigger_the_repeat_nudge(agent, tmp_path, monkeypatch):
    replies = ['{"tool": "bash", "command": "true"}',
               '{"tool": "bash", "command": "echo hi"}',
               '{"answer": "done"}']
    events = _run_scripted(agent, tmp_path, monkeypatch, replies, max_steps=6)
    assert not [e for e in events if "repeat_nudge" in e], events


def test_the_finish_nudge_fires_once_entering_the_zone_and_once_at_the_last_step(
        agent, tmp_path, monkeypatch):
    """收尾区进一次、最后一步再一次 —— 每步都喊同一句话只会挤掉最近的输出。"""
    reply = '{"tool": "bash", "command": "echo x"}'
    events = _run_scripted(agent, tmp_path, monkeypatch, [reply], max_steps=6, nudge=2)
    lefts = [e["finish_nudge"] for e in events if "finish_nudge" in e]
    assert lefts == [2, 1], lefts


def test_the_nudges_are_written_to_the_trace_before_they_are_sent(agent, tmp_path,
                                                                 monkeypatch):
    """平台看不到容器内部,只有 trace。没有这两条记录,"原地打转"和"认真工作"长得一样。"""
    same = '{"tool": "bash", "command": "true"}'
    events = _run_scripted(agent, tmp_path, monkeypatch, [same], max_steps=6, nudge=2)
    kinds = [k for e in events for k in ("repeat_nudge", "finish_nudge") if k in e]
    assert "repeat_nudge" in kinds and "finish_nudge" in kinds, kinds
