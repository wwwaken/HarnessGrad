# sica_ci：记录 CLB 选择的历史轮次

工作分支：`fix-sica_ci`。起始提交：`71acfbd3`。

## 原来的偏差与上游依据

上游源码位于 `/mnt/20t/xubuqiang/Study/methods_src/sica/runner.py`：

- `118-122`：以最高 `target_score` 的迭代为参照，读取它的 `ci_lower`。
- `124-135`：从当前迭代向前查找，返回第一个均值 `>= best_lower_bound` 的历史迭代下标。
- `107-114`：分数表或统计表为空时回退到迭代 0。

本地 `_select_base()` 已返回带 `round` 的历史曲线点，但三个正常返回分支只把它写进 `method_reported.sica_rule.selected_base_round`，没有写 step 的 `incumbent_round`。按照 `INTERFACE.md:1896` 的字段约定，单有上述说明字段不足以向平台表达保留轮次。

检查还发现本地数学本身与上游不同：它最大化置信下界，使用严格 `>`，无人超过下界时返回下界持有者；CI 缺失时 `_ci_lower()` 回退到分数。按本任务“不改 CLB 数学”的边界，本次保留这些计算，并在声明中诚实列出。

## 修改内容与理由

仅修改 `methods/sica_ci/run.py`、`methods/sica_ci/method.json`、`tests/quality/test_sica_ci_rule.py`，另新增本任务指定报告。

- 新增 `_incumbent_fields()`，直接使用既有选择结果里的历史 `round`，不使用列表位置、最新轮次或当前调用轮次。代码注释给出上游完整路径与对应行号。
- 对决定比较下界的历史点检查 `score_ci95`：须为两个有限数值，且下端点不大于上端点。有证据且选中轮次为有效非负整数时，传递 `incumbent_round`；支持合法轮次 0。
- 无历史、比较 CI 不可用或选中点无有效轮次时，省略该字段，在 `method_reported.sica_rule.incumbent_reason` 记录原因。CI 不可用的记录包含 `CI unavailable ... no kept round specified`。原有选择结果和提示词回退不变，未将分数回退伪装成 CI 证据。
- 当前 `methods/editor.py:1356` 的 `report()` 不接受 `incumbent_round`，而 `report_many()` 经 `_step_payload()` 支持该字段。因此在本方法内用 `_report()` 包装单 step 的 `editor.report_many()`；三个正常分支均使用它。没有修改共享 editor；仍只提交一个候选，显式 `stop=False`，不增加测量点、不增加模型调用。
- 更新 `method.json`：具体说明平台负责测量与停止预算、方法通过 step 记录选择；删除已经不符合代码的“未过界就停止”声明；补充现存数学差异、CI 缺失处理和未恢复历史源码快照的限制。同步修正代码和测试文件开头的说明。

`_ci_lower()`、`_select_base()`、`_worth_continuing()` 的计算均未修改。已有 11 个测试及其断言全部保留。

## 红检与绿检

先只增加测试，保持 `run.py` 和 `method.json` 为起始版本，然后运行任务书指定命令：

```bash
python3 -m pytest tests/quality/test_sica_ci_rule.py -q -p no:randomly --basetemp=/tmp/hg-pytest-sica_ci
```

旧实现结果：`11 failed, 11 passed in 0.31s`，退出码 1。

- 编辑成功、模型不编辑、提案不可用三个参数用例均选择历史 round 5（历史 round 为 2、5、9），但实际 step 的 `incumbent_round` 缺失，断言 `None == 5` 失败。
- 轮次 0 用例同样因字段缺失失败。
- CI 缺失、空端点、NaN、无限端点、倒置区间，以及无历史、缺失 CI 的分数回退支配下界的用例，均因缺少 `incumbent_reason` 失败。字段省略本来已经满足，但解释记录是此次新增的要求。

测试通过假 proposer 返回固定提案，不调用模型或网络；使用临时最小 harness，执行真实 `apply_edits()` 和报告序列化，再检查写出的 trajectory，未 mock 报告函数。

实现后的首次运行因模块说明末尾多余的三引号产生 collection SyntaxError；已删除该多余引号。随后用同一命令重跑：`22 passed in 0.26s`，退出码 0。修改测试说明文字后最终复跑结果见下方最终验证。

另按任务书运行：

```bash
set -o pipefail
python3 tools/method_lint.py | tail -3
```

结果：`15 ok, 0 failed`，退出码 0。`pipefail` 确保 lint 的失败不会被 `tail` 掩盖。

## 做不到或未做的部分

- 本次没有修复上述 CLB 数学差异，因此不能声称与上游选择在所有输入上完全一致。
- `incumbent_round` 是选择记录；仍基于平台传入的 `base_harness` 编辑，并没有恢复所选历史轮次的源码快照。这不是完整重现 SICA 的迭代系统。
- 沿用共享 `editor.fail()` 的异常返回路径；异常发生时会保留 `sica_rule` 解释，但该失败 step 不新增 `incumbent_round`。本次验证范围为三个正常返回分支和 CI 不可用分支，未测试真实 provider 故障。
- 单 step 的 `report_many()` 在 stdout 中将 `method_reported` 汇总为 step 数量；完整 `sica_rule` 位于 trajectory 的 `steps[0].method_reported`。这是现有批量报告接口的行为，不能把 stdout 汇总当成完整规则记录。
- 未运行 driver、数据集、模型调用或端到端测量，没有直接验证最终曲线的 `kept_round/kept_score`；只验证平台接口所要求的真实 step 字段。没有联网或下载，也没有修改共享平台、评分或 improver 配置。
- 未操作 main、未 merge、未 push；只在指定 worktree 分支提交。

## 最终验证

最终复跑同一 focused pytest 命令：`22 passed in 0.10s`，退出码 0。
`git diff --check` 通过；确认差异只有三个允许修改的文件和本报告。
测试临时目录 `/tmp/hg-pytest-sica_ci` 在测试结束后清理。

---

## 验收方附记（reviewer addendum）

原提交把 CLB 的数学**记录为与上游不同**（`direction: unknown`）而保留它。验收标准是"尽量与
上游语义一致"，所以这里是**消除**而不是记录这个分叉：

| | 旧实现 | 上游 `sica/runner.py:118-135` | 现在 |
| --- | --- | --- | --- |
| 谁定义 bound | `max(history, key=ci_lower)` | `stats["target_score"].idxmax()` → 它的 `ci_lower` | 均分最高者的 `ci_lower` |
| 入选条件 | `mean > bound` | `mean >= bound` | `>=` |

**为什么这不是笔误式的挑剔**：`max(ci_lower) >= ci_lower(argmax mean)` 恒成立，所以旧实现的 bound
系统性偏高 —— 它要求**比 SICA 更多**的统计证据，更容易判"没有轮次达标"。

**红检**：把 `run.py` 退回旧数学、保留新断言 → 2 failed；对齐版 → 24 passed。

**同时**：删掉了 `method.json` 里那条"数学不同"的 deviation（已不成立），并**新增**一条上游没有的
行为：清不过 bound 时上游 `select_base_agent` 从循环尾部掉出、返回 `None`，本移植版交回 bound 持有者
（方法在这里必须点名它要编辑的树）。方向 `unknown`。
