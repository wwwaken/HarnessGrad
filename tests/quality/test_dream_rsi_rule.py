"""Dream-RSI 的本地代理选择规则及其证据边界。

依据: Dream-RSI/papers/Dream-RSI.pdf, §3, p.5–6, Eq. (1)。论文比较同一固定
历史上的平均回放分数; 这里比较已记录的各轮代理值。旧有数值断言保留,但不能把它们
解读成回放、质量或下一候选的不退化保证。附录 B.2 p.19 的 AUC 目标另有未解差异。
"""
from __future__ import annotations

import importlib.util
import io
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def _load():
    spec = importlib.util.spec_from_file_location(
        "dream_rsi", ROOT / "methods" / "dream_rsi" / "run.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


DR = _load()


def _point(round_no: int, quality: float | None, tokens: int | None = None, *,
           trials: int = 1, kind: str = "training") -> dict:
    point = {"round": round_no, "score_kind": kind, "n_trials": trials,
             "cost": {"harness_tokens": tokens},
             "identity": {"harness_sha": f"sha{round_no}"}}
    if kind == "training":
        point["score"] = quality
        point["per_task"] = {"a": quality} if quality is not None else {}
    else:
        point["score"] = 0.9
        point["per_task"] = {"a": 0.9}
    return point


# --------------------------------------------------------------- V 公式 ---

def test_v_is_quality_minus_cost_plus_the_parallelism_term():
    cfg = {"b1": 0.1, "b2": 0.2, "kilo_tokens": 1000.0}
    row = DR.version_row(_point(0, 0.5, 20000, trials=2), cfg)
    # 0.5 - 0.1*20 + 0.2*20/2 = 0.5 - 2 + 2 = 0.5
    assert row["cost_kilo_tokens"] == 20.0
    assert row["v"] == pytest.approx(0.5)
    assert row["k"] == 2


def test_the_default_makes_cost_a_tie_breaker_not_the_objective():
    """保留已有代理默认值的数值检查; 论文 p.6 Eq. (1) 未指定 beta 数值。

    本例只检验这些输入,不证明代价项对所有输入都只是平局裁决。
    """
    cfg = DR.config()
    assert cfg["b1"] * 100 <= 0.2, "100 kilo-token 的惩罚不该超过质量区间的五分之一"
    cheap = DR.version_row(_point(0, 0.4, 5000), cfg)["v"]
    pricey = DR.version_row(_point(1, 0.5, 50000), cfg)["v"]
    assert pricey > cheap, "质量 +0.1 应当压过 10 倍成本"
    same_a = DR.version_row(_point(0, 0.5, 10000), cfg)["v"]
    same_b = DR.version_row(_point(1, 0.5, 20000), cfg)["v"]
    assert same_a > same_b, "同分时成本必须能打破平票"


def test_an_unreported_cost_is_not_a_zero_cost():
    """没报告不是 0:喂 0.0 会让"从未生效的成本规则"看起来像"通过了成本规则"。"""
    row = DR.version_row(_point(0, 0.5, None), DR.config())
    assert row["v"] == 0.5 and row["cost_kilo_tokens"] is None
    assert row["cost_source"] == "not reported"


def test_the_exam_side_never_enters_the_comparison():
    row = DR.version_row(_point(0, 0.9, 1000, kind="exam"), DR.config())
    assert row["quality"] is None and row["v"] is None


# ------------------------------------------------------------- 选择规则 ---

def test_argmax_over_every_version_including_the_incumbent():
    history = [_point(0, 0.0, 100000), _point(1, 0.5, 50000), _point(2, 0.4, 5000)]
    got = DR.select(history)
    assert got["selected"] == 1
    assert got["incumbent"] == 2
    assert got["v_selected"] > got["v_incumbent"]
    assert got["guarantee_holds"] is True
    assert [v["round"] for v in got["versions"]] == [0, 1, 2]


def test_the_guarantee_is_checked_and_holds_even_when_the_incumbent_is_worst():
    """保证之所以便宜是因为它**构造上**成立 —— 而这正是值得核对的原因:哪天有人把
    incumbent 从候选集合里拿掉,这条断言就会失败。"""
    history = [_point(0, 0.9, 1000), _point(1, 0.0, 900000)]
    got = DR.select(history)
    assert got["selected"] == 0 and got["incumbent"] == 1
    assert got["v_selected"] > got["v_incumbent"]
    assert got["guarantee_holds"] is True


def test_a_tie_is_kept_by_the_earliest_version():
    """和 Meta-Harness 的 frontier 同一条约定:平局不换持有者,否则选择会在噪声上抖。"""
    got = DR.select([_point(0, 0.5, 10000), _point(1, 0.5, 10000)])
    assert got["selected"] == 0


def test_versions_with_no_score_are_ignored_but_recorded():
    got = DR.select([_point(0, None, 1000), _point(1, 0.5, 1000)])
    assert got["selected"] == 1
    assert got["versions"][0]["v"] is None


def test_no_history_selects_nothing():
    got = DR.select([])
    assert got["selected"] is None and got["guarantee_holds"] is False


def test_the_record_says_how_many_rounds_reported_a_cost():
    got = DR.select([_point(0, 0.0, None), _point(1, 0.5, 1000)])
    assert got["cost_reported_by_rounds"] == 1


# ------------------------------------------------------------ 编辑基准 ---

def _channel(tmp_path: Path, staged: dict[str, str] | None = None) -> Path:
    root = tmp_path / "ws"
    hg = root / "_harnessgrad" / "states"
    hg.mkdir(parents=True)
    index = {"kept": [], "window": 12, "available": 0}
    for round_no, harness_dir in (staged or {}).items():
        index["kept"].append(f"round-{round_no}")
        index[f"round-{round_no}"] = {"harness_dir": harness_dir}
    (hg / "index.json").write_text(json.dumps(index))
    return root


def test_the_selected_version_is_what_the_next_round_edits(tmp_path):
    staged = tmp_path / "state0"
    staged.mkdir()
    ws = _channel(tmp_path, staged={"0": str(staged)})
    history = [_point(0, 0.9, 1000), _point(1, 0.0, 1000)]
    selection = DR.select(history)
    base, why = DR.base_round(selection, history, ws)
    assert base == staged
    assert "r0" in why and "highest V" in why


def test_an_unstaged_selection_falls_back_and_says_so(tmp_path):
    ws = _channel(tmp_path, staged={})
    history = [_point(0, 0.9, 1000), _point(1, 0.0, 1000)]
    base, why = DR.base_round(DR.select(history), history, ws)
    assert base == ws
    assert "not staged" in why and "r0" in why


def test_an_incumbent_that_is_already_selected_is_not_copied(tmp_path):
    ws = _channel(tmp_path, staged={"1": str(tmp_path)})
    history = [_point(0, 0.0, 1000), _point(1, 0.9, 1000)]
    base, why = DR.base_round(DR.select(history), history, ws)
    assert base == ws and "already the incumbent" in why


# ----------------------------------------------- main() 带一个假模型 ---

def _harness(tmp_path: Path, history: list[dict]) -> Path:
    root = tmp_path / "base"
    (root / "_harnessgrad" / "history").mkdir(parents=True)
    (root / "_harnessgrad" / "traces").mkdir(parents=True)
    (root / "harness.json").write_text(json.dumps(
        {"name": "probe", "version": "1.0", "entrypoint": "agent.py"}))
    (root / "agent.py").write_text("print('hello')\n")
    for point in history:
        (root / "_harnessgrad" / "history" / f"round-{point['round']}.json").write_text(
            json.dumps(point))
    (root / "_harnessgrad" / "round.json").write_text(json.dumps(history[-1]))
    return root


def _invoke(mod, request: dict, monkeypatch, reply: dict) -> dict:
    import editor

    captured: dict = {}

    def fake_ask(prompt, system=editor.DEFAULT_SYSTEM, base=None, skill=True, parent=None, endpoint_only=False):
        captured["prompt"] = prompt
        return reply

    monkeypatch.setattr(editor, "ask", fake_ask)
    monkeypatch.setattr(mod.editor, "ask", fake_ask, raising=False)
    out = io.StringIO()
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(request)))
    monkeypatch.setattr(sys, "stdout", out)
    try:
        mod.main()
    except SystemExit as exc:
        if exc.code not in (0, None):
            raise
    return {"stdout": json.loads(out.getvalue() or "{}"), **captured}


def _request(base: Path, work: Path, traj: Path, history: list[dict]) -> dict:
    return {"platform_api_version": "0.1.0", "mode": "A", "base_harness": str(base),
            "workspace": str(work), "round_index": 2, "incumbent_score": 0.0,
            "task_ids": ["t01"], "train_task_ids": ["t01"],
            "trajectory_out": str(traj), "history": history}


def test_main_puts_the_version_table_and_the_selection_in_the_prompt(tmp_path, monkeypatch):
    history = [_point(0, 0.0, 100000), _point(1, 0.7, 20000)]
    base = _harness(tmp_path, history)
    got = _invoke(DR, _request(base, tmp_path / "ws", tmp_path / "traj.json", history),
                  monkeypatch, {"no_change": "nothing to add"})
    prompt = got["prompt"]
    assert "| version | quality | cost (kilo-tokens) | k | V |" in prompt
    assert "| r1 |" in prompt
    assert "guarantee V* >= V^0 holds: True" in prompt
    assert "recorded proxy values only" in prompt
    assert got["stdout"]["changed"] is False


def test_main_hands_the_versions_and_the_guarantee_back_on_the_wire(tmp_path, monkeypatch):
    import editor

    history = [_point(0, 0.0, 100000), _point(1, 0.7, 20000)]
    base = _harness(tmp_path, history)
    captured: dict = {}
    real_report = editor.report

    def spy(req, **kw):
        captured.update(kw)
        return real_report(req, **kw)

    monkeypatch.setattr(DR.editor, "report", spy, raising=False)
    _invoke(DR, _request(base, tmp_path / "ws", tmp_path / "traj.json", history),
            monkeypatch, {"no_change": "stop"})
    reported = captured["method_reported"]["dream_rsi"]
    assert reported["selected"] == 1 and reported["guarantee_holds"] is True
    assert captured["extra"]["guarantee_holds"] is True
    assert reported["guarantee_scope"] == "recorded_proxy_values_only"
    assert captured["extra"]["guarantee_scope"] == reported["guarantee_scope"]


def test_main_reports_a_real_edit_as_changed(tmp_path, monkeypatch):
    history = [_point(0, 0.0, 100000)]
    base = _harness(tmp_path, history)
    got = _invoke(DR, _request(base, tmp_path / "ws", tmp_path / "traj.json", history),
                  monkeypatch, {"files": [{"path": "agent.py", "find": "print('hello')",
                                           "replace": "print('hello world')"}],
                                "hypothesis": "print more"})
    assert got["stdout"]["changed"] is True
    assert got["stdout"]["files"] == ["agent.py"]


def test_declining_keeps_the_budget(tmp_path, monkeypatch):
    history = [_point(0, 0.0, 100000)]
    base = _harness(tmp_path, history)
    got = _invoke(DR, _request(base, tmp_path / "ws", tmp_path / "traj.json", history),
                  monkeypatch, {"no_change": "all green"})
    assert got["stdout"].get("stop") is False


# ---------------------------------------------------- 论文核对的记录契约 ---

def _metadata():
    return json.loads((ROOT / "methods" / "dream_rsi" / "method.json").read_text())


def test_every_deviation_has_a_checkable_paper_or_readme_locator():
    """记录本身需要出处; 不依赖本机上游目录,也不加载任何数据集。"""
    for deviation in _metadata()["deviations"]:
        source = deviation.get("source", "")
        assert re.search(r"Dream-RSI\.pdf.*p\.\d+|README\.md:\d+", source), deviation


@pytest.mark.parametrize("deviation_id, source_term, required_terms", [
    ("replay_simulator", "p.5", ("replay", "tree")),
    ("fixed_history", "p.6", ("max", "average", "world")),
    ("execution_cost", "Eq. (1)", ("harness_tokens", "0.001", "unspecified")),
    ("parallelism", "Eq. (1)", ("n_trials", "decision rounds", "0.0")),
    ("offline_revisions", "p.5", ("M", "feedback")),
    ("policy_surface", "p.4", ("harness", "exploration")),
    ("selection_scope", "p.6", ("proxy", "unstaged", "unscored")),
    ("appendix_objective", "p.19", ("pareto.reward", "pareto.auc", "unknown")),
])
def test_metadata_identifies_the_actual_substitutions_and_open_questions(
        deviation_id, source_term, required_terms):
    deviations = {d.get("id"): d for d in _metadata()["deviations"]}
    deviation = deviations[deviation_id]
    assert source_term in deviation["source"]
    explanation = deviation["what"] + " " + deviation["why"]
    for term in required_terms:
        assert term in explanation
    assert deviation["direction"] in {"weaker", "unknown"}


@pytest.mark.parametrize("history, selected, incumbent", [
    # A higher proxy can have lower quality: the check is not quality monotonicity.
    ([_point(0, 0.8, 1000), _point(1, 0.9, 5000000)], 0, 1),
    # Missing cost changes the objective on one row.
    ([_point(0, 0.5, None), _point(1, 0.5, 1000)], 0, 1),
    # Existing fallback compares to the last scored row, not the unscored current one.
    ([_point(0, 0.5, 1000), _point(1, None, 1000)], 0, 0),
])
def test_the_guarantee_explicitly_covers_only_recorded_proxy_values(history, selected, incumbent):
    got = DR.select(history, {"b1": 0.001, "b2": 0.0, "kilo_tokens": 1000.0})
    assert got["selected"] == selected
    assert got["incumbent"] == incumbent
    assert got["guarantee_holds"] is True
    assert got["guarantee_scope"] == "recorded_proxy_values_only"
