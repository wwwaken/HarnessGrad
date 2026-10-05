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


def test_the_hard_rules_state_the_consequence_and_push_for_a_structural_change():
    """「不许」要带着后果,否则它只是一句礼貌话。

    入口那一句必须点名平台**怎么调用**它(`--task`/`--workdir`),因为这次踩的正是这个:
    被删掉的那份文件仍然是个能跑的 Python 程序,只是不认识平台的命令行。

    规模那一段改了两次,两次都是被实测推着改的:

    * `Change as little as you can` 止住了 635 行的重写,但把改动压到一行;
    * `...and no larger` / `a few lines` / `still a local change` 更糟 —— `v7` 两轮六次
      尝试**一次文件都没写**(诊断全对);
    * 现在这一版把"小心"全部撤掉,只留契约,并且**点名"用常量回答结构缺陷"这条路已经
      失败三次**:`FINISH_NUDGE_STEPS` 4->8 掉 0.2、同窗口内多提醒没变化、
      `OUTPUT_LIMIT` 4000->20000 掉 0.1。
    """
    assert "rejects" in ci.HARD_RULES, "没写违反的后果"
    assert "--task" in ci.HARD_RULES and "--workdir" in ci.HARD_RULES
    # 反向:不许再把规模压回去
    assert "Change as little" not in ci.HARD_RULES
    assert "and no larger" not in ci.HARD_RULES
    assert "a few lines" not in ci.HARD_RULES
    # 正向:激进 + 点名常量这条路
    assert "Be bold" in ci.HARD_RULES and "not a baseline to protect" in ci.HARD_RULES
    assert "Do not answer a structural defect with a constant" in ci.HARD_RULES
    assert "FINISH_NUDGE_STEPS" in ci.HARD_RULES and "OUTPUT_LIMIT" in ci.HARD_RULES, (
        "没有把三次常量改动失败写进去,它没有理由相信这句话")
    # 新失败模式(v9):写进一个没人 import 的新文件 = 什么都没改
    assert "A file nothing loads changes nothing" in ci.HARD_RULES
    assert "import closure" in ci.HARD_RULES
    # 激进要用验证兜住:改动大就自己跑一遍入口
    assert "must exit 0" in ci.HARD_RULES
    assert "A candidate that cannot start is rejected" in ci.HARD_RULES


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


def test_propose_does_not_overwrite_the_harness_own_gitignore(tmp_path, monkeypatch):
    """平台自己写的 `.gitignore` 不许算成改进器的改动。

    实测两次(`v3-smoke`、`v4-dgm` round 1):harness 树本来就带一个 `.gitignore`
    (`ckpt/git_state.py` 写 5 行,第一行空行),`propose` 又把它覆盖成 4 行,于是
    `_changed_files` 把**平台自己造成的**差异报成"改进器改了 `.gitignore`" —— 一个
    什么都没改的候选因此变成 `changed=True`,被当成新候选提交并被测量(sha 变了,
    行为一模一样)。
    """
    class _Proc:
        returncode = 0
        stdout = ""
        stderr = ""

    monkeypatch.setattr(ci, "_stage_evidence", lambda *a, **k: None)
    monkeypatch.setattr(ci, "_improver_command", lambda req: ["codex"])
    monkeypatch.setattr(ci.subprocess, "run", lambda argv, **kw: _Proc())

    parent = tmp_path / "parent"
    parent.mkdir()
    (parent / "harness.json").write_text("{}")
    (parent / "agent.py").write_text("print('x')\n")
    platform_gitignore = "\n_harnessgrad/\n__pycache__/\n*.pyc\n.state/\n"   # 平台 stage 的那份
    (parent / ".gitignore").write_text(platform_gitignore)

    workspace = tmp_path / "ws"
    workspace.mkdir()
    req = {"workspace": str(workspace), "candidate": str(tmp_path / "cand")}
    result = ci.propose(req, parent, prompt="rule prompt here")

    assert (result["candidate"] / ".gitignore").read_text() == platform_gitignore, (
        "平台把自己写的 .gitignore 覆盖了 —— 这会产生一个假的候选改动")
    assert ci._changed_files(result["candidate"], parent) == [], (
        "_changed_files 把平台自己的文件报成了改进器的改动")


def test_a_gitignore_edit_alone_is_not_a_candidate_change(tmp_path):
    """codex 只改 `.gitignore` 不算候选改动 —— 它改变不了 harness 被测量时的行为。"""
    import shutil

    parent = tmp_path / "p"
    child = tmp_path / "c"
    parent.mkdir()
    (parent / "agent.py").write_text("print('x')\n")
    (parent / ".gitignore").write_text("*.pyc\n")
    shutil.copytree(parent, child)
    (child / ".gitignore").write_text("*.pyc\n*.log\n")

    assert ci._changed_files(child, parent) == [], "只改 .gitignore 被当成了候选改动"
    (child / "agent.py").write_text("print('y')\n")
    assert ci._changed_files(child, parent) == ["agent.py"]


def test_a_tool_output_line_is_not_recorded_as_the_methods_reason():
    """改进器的"理由"不能是终端输出。

    实测(`v7-dgm`,2026-10-05):某个 child 被记录下来的理由是

        -rw-r--r-- 1 xubuqiang xubuqiang    12 Oct  5 15:32 requirements.txt

    —— 一行 `ls -l`。74 个字符,不以旧过滤器认识的任何前缀开头,于是一份目录列表进了曲线,
    摆在"方法声明的假设"那个位置。散文是字母和空格,终端输出不是,比例能干净地分开
    (那份轨迹里实测:真诊断 1.000,`ls -l` 0.794,一行 Python 0.584)。
    """
    transcript = "\n".join([
        "tokens used 1234",
        "Looking at the implementation more carefully, when a duplicate key is "
        "encountered the code adds it to the repeated list and continues",
        "-rw-r--r-- 1 xubuqiang xubuqiang    12 Oct  5 15:32 requirements.txt",
    ])
    got = ci._summary_of(transcript)
    assert got.startswith("Looking at the implementation"), got


def test_a_transcript_with_only_tool_output_has_no_reason():
    """只有工具输出时,宁可没有理由,也不要编一个出来。"""
    transcript = "\n".join([
        "-rw-r--r-- 1 xubuqiang xubuqiang    12 Oct  5 15:32 requirements.txt",
        "_PATH_RE = __import__(\"re\").compile(r\"/[A-Za-z0-9_./-]+\\.[A-Za-z0-9]{1,6}\\b\")",
    ])
    assert ci._summary_of(transcript) == ""


def test_the_hard_rules_require_the_edit_to_be_on_disk():
    """规则必须说清:提交的是磁盘上的文件,不是分析。

    实测(`v7`):两轮六次尝试各自给出了**正确的诊断**(重复 JSON 键丢掉第二个 `Action`;
    重复提醒只抓紧挨着的重复),但**一次文件都没写**。诊断对了,什么都没交。
    """
    assert "The submission is the file on disk" in ci.HARD_RULES
    assert "not the analysis" in ci.HARD_RULES


def test_the_ask_comes_first_and_the_evidence_is_a_path_not_a_copy():
    """**要求在最前,证据只给路径。**

    实测(`v4`-`v10`,58,160 字符的指令):那 54 个字符的要求("propose one change, or say
    no_change")占 0.1%,排在 89.7% 的原始证据**之后**,硬规则更后。小模型读得最轻的正好是
    唯一告诉它要做什么的那句 —— v7 一轮里 `no_change` 这个免费出口被走了五次。

    这条测试钉两件事:顺序(事实→要求→规则→证据→规则自己的话),以及证据是**路径**。
    按真实规模(51 题、多文件 harness)编译内容是 ~230 KB,而整条指令是一个 argv 参数,
    Linux 上限 128 KB:那样工具根本起不来。
    """
    full = ci.instruction("RULE'S OWN PROMPT", facts="FACTS-BLOCK",
                          evidence="EVIDENCE-POINTER")
    order = [full.index(x) for x in ("FACTS-BLOCK", "## What to produce", "Hard rules",
                                     "EVIDENCE-POINTER", "RULE'S OWN PROMPT")]
    assert order == sorted(order), f"顺序不对: {order}"
    assert "apply them to the tree" in full
    assert "as many independent edits as it takes" in full
    assert "one change" not in full, "又写成'一个改动'了"
    # no_change 不再是免费出口
    assert "name the\nmechanism you checked" in full or "name the mechanism you checked" in full
