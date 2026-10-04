#!/usr/bin/env python3
"""The reference base harness: a minimal ReAct loop.

Deliberately the simplest thing that satisfies the contract in
`docs/writing_a_harness.md`. Its job is not to be strong -- it is to be:

  1. a valid starting point that a method can improve, and
  2. the proof that the contract is implementable at all.

A method may replace every file here. That is the point.

**What is deliberately absent, and why.** This harness has no context policy, no
output bounding and no memory. Those are *mechanisms*: named, switchable
behaviours that a method adds in order to improve the harness. Shipping a set of
them by default would mean shipping one particular experiment's design as if it
were the platform's, and would make "this harness is thin" a claim nobody can
check. A base harness with nothing in it is the honest starting point; what a
method adds on top is the measurement.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


#: How many model calls one task gets. **A floor on capability, not a tuning knob.**
#:
#: Measured at 8, on Terminal-Bench, 4 rounds x 5 tasks: four of the five tasks used all
#: eight and produced no graded artifact at all -- `build-pmars` was still installing
#: packages, `bn-fit-modify` had just finished installing pandas/numpy/sklearn and
#: printed one correlation matrix, `chess-best-move` had opened the PNG and never wrote
#: `/app/move.txt`. The score was 0.0 on every task in every round, which is not a weak
#: harness being measured: it is a floor effect, and a floor makes every method look
#: identical because there is no gradient for one to move.
#:
#: Raising this does not make the harness cleverer -- `adapters/harnessgrad_domain/`
#: already names this lever as the trap ("helps only if the model is already using the
#: steps it has"). Here the trace shows it *was* using them, which is exactly when the
#: lever is legitimate. What it costs is bounded by the task, not by this number: the
#: wall clock is capped by the environment's `agent_timeout_s` (900 s for most
#: Terminal-Bench tasks, 3600 s for `bn-fit-modify`). A step is fast (~0.2 s model round
#: trip through the local gateway), so the extra ceiling mostly buys back the steps that
#: environment setup eats. The loop still stops the moment the model answers -- the cap
#: is a ceiling, not a quota.
MAX_STEPS = int(os.environ.get("HG_AGENT_MAX_STEPS", "32"))

#: 模型说"我做完了"之后,允许它再被退回几次。
#:
#: 为什么需要这个:harness 以前**从不检查交付物**。模型回一句 {"answer": ...} 就被当成
#: 任务结束、退出循环。实测(2026-10-02,terminal_bench round 0):五道题的 agent 阶段是
#: 101s / 31s / 183s / **4.5s** / 105s —— 而步数上限是 32。4.5 秒等于一次模型调用就
#: "交卷"了,产物根本不存在;`cancel-async-tasks` 的判分因此是
#: `File /app/run.py does not exist`。
#:
#: 所以 0 分的机制不是"步数不够",而是"**harness 把模型说的完成当成了完成**"。
#: 一个会自己检查交付物、并把"文件不存在"退回给模型重试的 harness,才是这一步该有的样子。
SUBMIT_RETRIES = int(os.environ.get("HG_AGENT_SUBMIT_RETRIES", "2"))

#: 模型吐出一段**读不出动作**的回复之后,允许它再试几次。
#:
#: 和上面那条同源,方向相反:一条是"模型说做完了,但产物不在",一条是"模型说的话读不出
#: 动作"。两条以前都会让**整道题**结束。
#:
#: 为什么它必须由起点 harness 负责,而不是留给方法去发现 —— 这是数出来的,不是想出来的。
#: 统计所有跑道里"方法自己写了理由"的 35 个轮次:**16 个在修解析或格式容错**,而且几乎
#: 每条跑道的第一轮都在修它:
#:
#:   `loop-terminal_bench-26452c` 五道题各只调了一次模型就死在
#:   `parse_error: Extra data`(`calls: 1`),此后每一轮都从同一个不能用的 harness 出发;
#:   `flash-three-1/2`、`deepseek-eigen-2`、`strong-model-1` 的第一/第二轮全都写成
#:   "让一次读不懂的回复不再结束整道题"。
#:
#: 代价不只是浪费一轮。方法之间开始比"谁先想到修 parser":RRSI 的 leakage critic 两次把
#: 改 `_parse` 的候选判成 TASK-SPECIALIZATION / LEAKAGE 而拒绝,那一轮于是什么都没改。
#: 一个起点 harness 必须在被测量之前就活过一次跑题的回复,否则第一轮比较的不是解题能力,
#: 是管线运气。
PARSE_RETRIES = int(os.environ.get("HG_AGENT_PARSE_RETRIES", "2"))

#: 步数还剩这么多时,明确要求模型收尾。
#:
#: 数出来的,不是猜的:266 条历史轨迹里 **73 条(27%)跑满 32 步、一次都没交卷**,而那些
#: 轨迹的最后两步常常是同一条命令重复(抽样:`python /app/test_outputs.py 2>&1` 两次、
#: 同一条 `echo ... >` 两次、同一个 `cat > /app/run.py << 'EOF'` 两次)。那些任务不是
#: "做错了",是**没停下来交卷**:步数用完,`answer` 是空字符串,平台只能拿检查的判决当分数。
#: `improvers/skill.md` 早就把这条记成已知失败模式("预算用满、什么都没交"),但起点 harness
#: 一直没有对应动作。一个被测量的 harness 应该在预算耗尽前把话说完。
FINISH_NUDGE_STEPS = int(os.environ.get("HG_AGENT_FINISH_NUDGE_STEPS", "4"))

#: 同一条命令连续重复时提醒几次(每条跑道限量,免得把上下文塞满)。
REPEAT_NUDGE_LIMIT = int(os.environ.get("HG_AGENT_REPEAT_NUDGE_LIMIT", "2"))

SYSTEM = """You are an agent solving a task in a working directory.

You have one tool: run a shell command.

Reply with EXACTLY one of:
  {"tool": "bash", "command": "<shell command>"}
  {"answer": "<your final answer>"}

Rules:
- One action per reply. No prose outside the JSON.
- To inspect files use shell commands (ls, cat, grep, ...).
- Give the final answer only when you are confident.
"""


# ---------------------------------------------------------------- backends ---

def _backend() -> str:
    """Which completion backend to use.

    `mock` exists so the framework can be exercised end-to-end with zero network
    and zero cost. Any real curve must declare its backend and model on the curve
    point (INTERFACE.md §3, `identity.agent_model`).
    """
    return os.environ.get("HG_AGENT_BACKEND", "mock")


def _call_mock(messages: list[dict]) -> str:
    """Deterministic stand-in: read answer.txt if present, else list the dir."""
    task_text = messages[1]["content"] if len(messages) > 1 else ""
    if "answer.txt exists" in task_text or "already" in task_text:
        return json.dumps({"answer": "READ_FROM_FILE"})
    return json.dumps({"tool": "bash", "command": "ls -a"})


# --------------------------------------------------------------- usage ---

#: Token usage accumulated over the run, filled by whichever backend is active.
#: Read into the trace at the end. Recorded because a mechanism that spends model
#: calls (history_summary does) is only comparable against a free one if the
#: spend is visible -- and because a harness whose cost is unknown cannot be
#: ranked against a cheaper one that scores the same.
USAGE = {"calls": 0, "input_tokens": 0, "output_tokens": 0, "retries": 0}


def _record_usage(usage) -> None:
    """Fold provider token counts into the run's total.

    The call count is NOT incremented here: it is incremented by `_complete`,
    which is the one place every model call goes through. Counting calls at the
    provider boundary would miss the mock backend entirely -- and a mechanism that
    spends model calls on a mock run would then report zero cost, which is exactly
    the invisible-spend the usage block exists to prevent.
    """
    if usage is None:
        return
    # Provider fields that are absent stay absent rather than becoming zero: a
    # zero that means "not reported" is indistinguishable from a real zero.
    for attr, key in (("prompt_tokens", "input_tokens"),
                      ("completion_tokens", "output_tokens")):
        v = getattr(usage, attr, None)
        if isinstance(v, int):
            USAGE[key] += v


def _call_openai(messages: list[dict]) -> str:
    """One completion, with a deadline and bounded retries.

    A harness that dies on a transient provider error loses a whole task run, and
    an unbounded retry loop turns a provider outage into a hung experiment. Both
    failures are silent in a batch unless the harness is defensive here.
    """
    from openai import OpenAI

    # **每次请求用一条新连接,不复用。** 不是性能取舍,是正确性:
    #
    # 实测(2026-10-02,容器内复现):vLLM 的 uvicorn 默认 5 秒关掉空闲 keep-alive,而
    # 容器到模型之间还有平台发布的一层字节转发网关,它在上游 EOF 时会把 EOF 半关到
    # 客户端。于是"跑一条几十秒的命令、再发起下一次模型调用"就必然复用一条死连接 ——
    # `RemoteDisconnected` → openai 报 `APIConnectionError: Connection error`。
    # 实测那一次,两道题(跑 pandas 的、跑 PIL 的)就是这样死的,而平台把它们记成了 0 分。
    #
    # keep-alive 本身是 HTTP 客户端的正常行为,所以这是网关的缺陷(见 eval/modelgate.py);
    # 但一个 harness 不该把自己的测量押在"中间那一层是否正确处理空闲连接"上。一次本地
    # TCP 握手的代价可以忽略。
    #
    # **用 `default_headers`,不要 import httpx。** 第一版写的是
    # `http_client=httpx.Client(...)`,结果是每次调用都 `ModuleNotFoundError: No module
    # named 'httpx'` —— 这个平台的 harness 依赖由覆盖层提供,而这里 `openai` 3.22.1 依赖的
    # 是 `httpx2`(不是 `httpx`)。所以"顺手 import 一个我以为在的库"在这条路上是错的:
    # 唯一可以依赖的是 `requirements.txt` 声明的那个发行包自己的接口。
    client = OpenAI(
        base_url=os.environ["HG_AGENT_BASE_URL"],
        api_key=os.environ["HG_AGENT_API_KEY"],
        timeout=float(os.environ.get("HG_AGENT_TIMEOUT_S", "180")),
        max_retries=0,          # retried here, so the count is ours to record
        default_headers={"Connection": "close"},
    )
    model = os.environ["HG_AGENT_MODEL"]
    attempts = int(os.environ.get("HG_AGENT_RETRIES", "3"))
    last: Exception | None = None

    for attempt in range(attempts):
        try:
            resp = client.chat.completions.create(
                model=model, messages=messages, temperature=0.0,
            )
            _record_usage(getattr(resp, "usage", None))
            return resp.choices[0].message.content or ""
        except Exception as exc:                      # noqa: BLE001
            last = exc
            if attempt + 1 < attempts:
                USAGE["retries"] += 1
                time.sleep(min(2 ** attempt, 30))
    # Out of attempts: raise, so the caller records a harness failure rather than
    # scoring an empty answer as a wrong one.
    raise RuntimeError(f"{attempts} attempts failed, last: {last}") from last


def _complete(messages: list[dict]) -> str:
    """Every model call in this harness goes through here, so this is where the
    count is kept. Counting anywhere else means some caller is invisible."""
    USAGE["calls"] += 1
    return _call_mock(messages) if _backend() == "mock" else _call_openai(messages)


# ------------------------------------------------------------- the loop -----

def _parse(reply: str) -> dict:
    """The **first JSON object** in a reply, ignoring anything after it.

    Tolerant extraction is not a nicety here; this function decides whether a task runs
    at all, and one of its failure modes cost two whole runs.

    The first version tried `json.loads(reply)`, then fell back to slicing from the first
    `{` to the **last** `}`. Both fail on the same reply shape, and that shape is what the
    measured model actually emits: asked for one action, it sometimes answers with two or
    three JSON objects, one per line --

        {"tool": "bash", "command": "cat /app/filter.py"}}
        {"answer": ""}

    (note the stray brace as well). `json.loads` reports `Extra data: line 1 column 50`,
    and the `rfind` fallback slices `{...}}{...}`, which is not JSON either. The harness
    treats an unparseable reply as a harness failure and **breaks the loop**, so the task
    ends at step 0 with an empty answer and scores 0.

    Measured on `loop-terminal_bench-41133`, round 0: four of five tasks died this way
    after a single model call (`calls: 1`, `parse_error: Extra data`), and every round
    after it was the same because the round starts from a harness that cannot do anything.
    The old run `loop-terminal_bench-26452c` produced single-object replies and got 8
    calls per task -- same code, same prompt -- so this is a property of the model's
    output that the parser has to absorb, not something the parser caused.

    `raw_decode` from the first `{` is the whole fix: it returns the first complete
    object and says where it stopped, so trailing objects, stray braces and prose around
    the JSON all stop mattering. `base_harness/loop_rrsi_parse/` already shipped exactly
    this ; it is the same code, because a parser that differs between two base harnesses
    is a difference between two candidates that the platform made rather than the method.
    """
    reply = reply.strip()
    if reply.startswith("```"):
        reply = reply.split("```")[1]
        reply = reply[4:] if reply.startswith("json") else reply
    decoder = json.JSONDecoder()
    for i, ch in enumerate(reply):
        if ch != "{":
            continue
        try:
            obj, _ = decoder.raw_decode(reply[i:])
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            return obj
    raise ValueError("no JSON object found in reply")


#: goal 里形如 `/app/move.txt`、`/app/learned_dag.csv` 的路径。这是**通用**的:
#: 它不针对任何一道题,只看题面自己说了要写到哪个文件。
_PATH_RE = __import__("re").compile(r"/[A-Za-z0-9_./-]+\.[A-Za-z0-9]{1,6}\b")


def _missing_deliverables(task: dict, workdir: Path) -> list[str]:
    """题面点名要写、但现在**不存在**的文件。

    这是 `loop` 自带的交卷闸门,刻意做成通用的两条:

      * 只看题面(goal)里写出来的绝对路径 —— harness 没有任何途径知道判分脚本要什么
        (`task.json` 里只有 goal),所以它只能相信题面;
      * 只做 `exists` 检查,不执行任何东西。

    题面没提路径(比如"回答一个问题")时返回空列表,闸门不生效 —— 这时判断对错是平台
    的事,harness 不该假装知道。
    """
    goal = str(task.get("goal") or "")
    wanted = {m for m in _PATH_RE.findall(goal)}
    missing = []
    for raw in sorted(wanted):
        # 容器里绝对路径就是它自己;宿主上则落在 workdir 之内。两种都查,取存在的那个。
        candidates = [Path(raw)]
        try:
            candidates.append(workdir / Path(raw).relative_to("/app"))
        except ValueError:
            pass
        if not any(c.exists() for c in candidates):
            missing.append(raw)
    return missing


def run(task: dict, workdir: Path) -> str:
    """Execute one task. Returns the answer string.

    The trace written to <workdir>/trace.jsonl is what the framework collects
    and hands to the Trainer (INTERFACE.md §4.1).
    """
    trace_path = workdir / "trace.jsonl"
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": json.dumps(task)},
    ]

    answer = ""
    submits = 0
    parse_retries = 0
    repeats = 0
    last_cmd = ""
    with trace_path.open("w") as trace:
        for step in range(MAX_STEPS):
            reply = _complete(messages)
            trace.write(json.dumps({"step": step, "reply": reply}) + "\n")
            messages.append({"role": "assistant", "content": reply})

            try:
                action = _parse(reply)
            except Exception as exc:
                # 退回给模型,而不是结束整道题。trace 里记下第几次重试,因为平台看不到
                # 容器内部:没有这条记录,一次"读不懂的回复"在记录里和一次"一步就交卷"
                # 长得一样。次数用完仍然是 harness 失败(它确实读不出动作),但那时记录
                # 里已经有 N 次尝试,而不是一次。
                trace.write(json.dumps({"step": step, "parse_error": str(exc),
                                        "parse_retry": parse_retries}) + "\n")
                if parse_retries >= PARSE_RETRIES:
                    break
                parse_retries += 1
                messages.append({"role": "user", "content": (
                    f"Your reply could not be read as an action: {exc}\n"
                    "Reply with EXACTLY ONE JSON object and nothing else, one of:\n"
                    '  {"tool": "bash", "command": "<shell command>"}\n'
                    '  {"answer": "<your final answer>"}')})
                continue

            # **交卷闸门。** 顺序按"它想干什么"判断,而不是按哪个键先出现:
            # 一条回复里同时带 command 和 answer 时,以前"先看 answer"会让那条命令
            # 永远不执行(实测:`{"tool":"bash","command":"cat > /app/run.py …"}` 被当成
            # 空答案,文件从未创建)。所以:有命令就先执行命令;只有**没有**命令时才算交卷。
            cmd = action.get("command", "")
            if not cmd and "answer" in action:
                missing = _missing_deliverables(task, workdir)
                if missing and submits < SUBMIT_RETRIES:
                    submits += 1
                    note = ("You answered but these paths the task asks for do not exist: "
                            + ", ".join(missing)
                            + ". Create them first, then answer again.")
                    trace.write(json.dumps({"step": step, "submit_rejected": missing}) + "\n")
                    messages.append({"role": "user", "content": note})
                    continue
                trace.write(json.dumps({"step": step, "submitted": True,
                                        "missing": missing}) + "\n")
                answer = str(action["answer"])
                break
            proc = subprocess.run(
                cmd, shell=True, cwd=workdir, capture_output=True, text=True
            )
            out = proc.stdout + proc.stderr
            trace.write(json.dumps({"step": step, "command": cmd,
                                    "exit": proc.returncode, "output": out}) + "\n")
            messages.append({"role": "user", "content": f"exit={proc.returncode}\n{out}"})

            # **两条提醒,都放在命令跑完之后**,因为它们改变的是"下一步做什么"。
            #
            # 先记进 trace 再发出去:平台看不到容器内部,没有这两条记录,"模型在原地打转"
            # 在一次 32 步的运行里和"模型在认真工作"长得一模一样。
            if cmd and cmd == last_cmd and repeats < REPEAT_NUDGE_LIMIT:
                repeats += 1
                trace.write(json.dumps({"step": step, "repeat_nudge": cmd[:120]}) + "\n")
                messages.append({"role": "user", "content": (
                    "That is the same command as the previous step and its output has not "
                    "changed. Do something different, or finish now with "
                    '{"answer": "<your final answer>"} if the work is already done.')})
            last_cmd = cmd

            left = MAX_STEPS - (step + 1)
            # 只在进入收尾区和最后一步各说一次:每一步都重复同一句话不会更有用,
            # 只会把最近几轮的命令输出挤远。
            if left and (left == FINISH_NUDGE_STEPS or left == 1):
                trace.write(json.dumps({"step": step, "finish_nudge": left}) + "\n")
                messages.append({"role": "user", "content": (
                    f"You have {left} step(s) left. Stop exploring. Create every file the "
                    "task asks for now, then reply with exactly one JSON object: "
                    '{"answer": "<your final answer>"}')})

        # What the run cost. Kept because a harness that cannot say what it spent
        # cannot be compared with a cheaper one at the same score -- and because
        # `USAGE` is the only place the model calls are counted.
        trace.write(json.dumps({"usage": dict(USAGE)}) + "\n")

    (workdir / "answer.txt").write_text(answer)
    return answer


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--workdir", required=True)
    args = ap.parse_args()

    task = json.loads(Path(args.task).read_text())
    run(task, Path(args.workdir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
