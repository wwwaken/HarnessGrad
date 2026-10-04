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


def test_the_trace_is_on_disk_before_the_next_command_runs(agent, tmp_path, monkeypatch):
    """行缓冲:命令跑起来之前,上一步的事件已经落盘。

    实测那一次(本地模型跑 `bn-fit-modify`):harness 跑了 8 分钟、正在装 pandas,而
    `trace.jsonl` 是 0 字节、fd 的 `pos: 0` —— 默认的 8KB 块缓冲把一切都留在内存里。
    代价是实时轨迹看不见,而且被超时杀掉的题会丢掉缓冲区里的尾巴。
    """
    replies = [
        '{"tool": "bash", "command": "cp trace.jsonl step0_snapshot.txt"}',
        '{"answer": "done"}',
    ]
    fake, _ = _scripted(agent, replies)
    monkeypatch.setattr(agent, "_complete", fake)
    agent.run({"goal": "snapshot"}, tmp_path)
    snapshot = (tmp_path / "step0_snapshot.txt").read_text()
    assert '"step": 0' in snapshot, "第 0 步的事件在命令执行前没有落盘"


# --------------------------------------------- 上下文管理(本地模型那次) ---

def test_a_huge_command_output_is_clipped_with_a_marker(agent, tmp_path, monkeypatch):
    """实测:3 道题死于 `maximum context length is 32768 tokens ... at least 32769`。

    起点 harness 把每条命令的**完整**输出一直往历史里追加:一道题里单条输出 11773 字符。
    那不是模型的问题,是 harness 没有上下文管理。截断必须留痕 —— 悄悄改变模型所见历史的
    harness 和被测量的 harness 不是同一件事。
    """
    monkeypatch.setattr(agent, "OUTPUT_LIMIT", 200)
    replies = ['{"tool": "bash", "command": "head -c 2000 /dev/zero | tr \\"\\\\0\\" x"}',
               '{"answer": "done"}']
    fake, _ = _scripted(agent, replies)
    monkeypatch.setattr(agent, "_complete", fake)
    agent.run({"goal": "big output"}, tmp_path)
    events = _events(tmp_path)
    clipped = [e for e in events if "output_clipped" in e]
    assert clipped, "超长输出没有被截断"
    assert clipped[0]["output_clipped"] >= 2000 and clipped[0]["shown"] <= 260, clipped[0]
    # 历史里的那条消息也确实短了
    big = [e for e in events if e.get("exit") is not None]
    assert big and len(str(big[0]["output"])) >= 2000, "轨迹里仍保留完整输出(给读记录的人)"


def test_the_history_is_trimmed_and_the_trim_is_recorded(agent, tmp_path, monkeypatch):
    """历史超预算就丢最旧的成对消息,并在轨迹里记下丢了几条。"""
    monkeypatch.setattr(agent, "CONTEXT_CHAR_BUDGET", 800)
    monkeypatch.setattr(agent, "OUTPUT_LIMIT", 400)
    reply = '{"tool": "bash", "command": "head -c 400 /dev/zero | tr \\"\\\\0\\" y"}'
    fake, seen = _scripted(agent, [reply])
    monkeypatch.setattr(agent, "_complete", fake)
    monkeypatch.setattr(agent, "MAX_STEPS", 8)
    agent.run({"goal": "grow"}, tmp_path)
    events = _events(tmp_path)
    dropped = [e for e in events if "history_dropped" in e]
    assert dropped, "历史没有被修剪"
    # 修剪之后,历史长度不再单调增长 —— 这正是它要保证的
    assert max(seen) < 8, seen
