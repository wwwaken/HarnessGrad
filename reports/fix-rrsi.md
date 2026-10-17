# RRSI：保留轮次记录与候选池偏差复核

## 范围与来源

仅修改 `methods/rrsi/run.py`、`methods/rrsi/method.json`、新增
`tests/quality/test_rrsi_rule.py`，以及本任务指定的唯一报告。本分支为 `fix-rrsi`，
起点 `71acfbd3`；未修改 main，未 merge、push，未运行 driver、数据集或联网下载。

完整阅读 `_common.md` 和 `rrsi.md` 后，只读核对本机上游
`/mnt/20t/xubuqiang/Study/RRSI`。其 HEAD 为声明的
`e4d1a7a0388e02b388bc40eb0a125fcfc7123f8d`。上游存在无关的 `rrsi/llm.py`
修改和未跟踪探针；本次依据的 selection、loop、evaluate、calibrate 源文件未被修改，
本任务没有写上游目录。

## 原偏差与上游依据

- 上游 `rrsi/selection.py:97-121` 的 `judge` 先检查 `S' >= S* - delta`，
  再检查两支成本规则和 domain guards。成本两支见 `cost_rule`，`:81-94`。
- `rrsi/selection.py:124-137` 的 `select_round` 从 admissible 候选取最高分；
  没有合格候选返回 None。`rrsi/loop.py:327-340` 随后部署 winner，或保留 `H_t`。
- 移植版原来已有 `_adjudicate_incumbent`，但只记录上一候选的重裁决，所有报告出口都没有
  `incumbent_round`，平台曲线无法记录这条重裁决实际保留的历史轮次。
- `method.json` 原来的 unknown 项将“没有原生候选池”归因于协议只能返回一个候选，
  该理由已过时。上游真正要求的是 `rrsi/loop.py:290-307` 的顺序：从同一 incumbent
  草拟并筛选 m 个变体，测量存活变体，再调用 `select_round`。

## 修改与行为

`_retention` 只把既有重裁决转成记录，不更改噪声带、成本规则、退火预算或新增历史选优规则。
最新历史点作为已经测过的候选，其紧邻前一点是它实际替换前的 incumbent：
通过则记录最新点的 round，拒绝则记录前一点的 round。依据直接写在代码注释中：
`rrsi/selection.py:133-137` 和 `rrsi/loop.py:327-340`。

没有前一候选（空历史或 baseline）、没有 train 信号、成本未报且 floor 已通过时，
不会伪造 admissibility 或填 step 的 `incumbent_round`；
`method_reported.rrsi_rule.retention` 保留 null 和具体原因。选中点没有有效 round 时也不声明。
低于 floor 的拒绝不需要成本输入，这是原 `_judge` 的顺序，保持不变。

`editor.report` 没有 `incumbent_round` 参数；本次没有越界修改 editor。
方法内 `_report` 在存在保留轮次时调用单 step 的 `editor.report_many`，
将 `incumbent_round` 放入真实 step；没有判定时仍走 `editor.report`。
正常提案、no-change、不可用提案、critic 丢弃、修复后 no-change，以及提案应用失败、
provider 异常均携带已计算的历史记录。异常仍写 stderr，标 changed=false、stop=false。

## 候选池结论与 deviations

- `methods/editor.py:1485-1530`：`report_many` 可提交多个完整候选，逐步测量；
  一次提交的 steps 之间方法看不到反馈。
- `harnessgrad/loops/mode_a.py:524-544`：step 的 `incumbent_round` 写入
  `kept_round` 和对应 `kept_score`；该字段本身不执行恢复或部署。
- `harnessgrad/channel.py:427-450`：`states/index.json` 和 `states/round-N/`
  暴露成功 materialize 的历史树，受配置窗口限制。恢复历史树的基础能力已存在。

因此将原 unknown 改为具体的 **weaker**：本入口仍每次草拟一个候选，未组织同 incumbent
的 m-candidate pool，也未在测量后接通选优与部署；目前仅声明延迟的 singleton
重裁决保留结果。离线 `fidelity.py` 的池选择没有接入 `main()`。这部分是移植版尚未接线，
不能继续笼统声称平台没有候选池或无法表达历史保留。

同步更新 note、fidelity_profile 和运行时限制描述，移除旧的“平台没有多候选/保留能力”说法。
另外明确记录两条已有行为偏差：缺 token 不采用上游 `dC=0`（上游
`rrsi/evaluate.py:131-135`），以及 `_delta` 使用 override、当前点 trial spread 或显式 fallback，
并非上游 base calibration（`rrsi/calibrate.py:85-108`）。方法 JSON 不再含 unknown direction。

## 红检和验证

仓库原来没有 `tests/quality/test_rrsi_rule.py`，已有 `test_rrsi.py` 和
`test_rrsi_fidelity.py` 均未改动、未删除或降低断言。

先只新增测试，保留 HEAD 的旧 `run.py` 和 `method.json`，运行任务书的原命令：

```bash
python3 -m pytest tests/quality/test_rrsi_rule.py -q -p no:randomly --basetemp=/tmp/hg-pytest-rrsi
```

红检：退出码 1，`16 failed in 0.48s`。七个出口用例都在捕获到的报告参数上出现
`incumbent_round: None`，预期为更早的 round 1；另有真实 trajectory 字段缺失、
缺 `retention` 解释以及 unknown 元数据断言失败。没有导入错误或实际 provider 调用。

修改实现和元数据后，同一命令：退出码 0，`16 passed in 0.28s`。
最终复核同一命令：退出码 0，`16 passed in 0.20s`。
覆盖更早轮次、带内成本失败、带内节省 token 的可接受降分、带外增益、缺证据不声明、
training-only score 路由、各报告出口及元数据偏差。

```bash
python3 tools/method_lint.py | tail -3
```

输出末尾：`15 ok, 0 failed`。另做 `git diff --check`，无空白错误。
测试全部使用手写合成曲线和临时 harness；模型/提案入口打桩，无数据集、网络或真实运行。
最终复核后清理 `/tmp/hg-pytest-rrsi`，不保留 SSD 测试临时树。

## 未完成或未验证的部分

- 这不是 native RRSI reproduction；没有新增 m-candidate 生成、study-only evaluate_many、
  原生角色 dispatch、frontier、domain guards 或上游内循环 k trials。
- `incumbent_round` 是对**已经测量的历史候选**的延迟重裁决记录，不能判断本次刚提交的未测候选。
  本次没有读取 states/ 恢复树，也没有让下次提案改用所保留历史树；下一提案仍基于平台实际 base。
- 历史分数上界、组件计数仍沿平台实际测量/推进历史重建，不是恢复了上游跨轮拒绝后的 frontier。
  没有把不同 parent 的历史候选冒充同一轮候选池取 argmax。
- 末次测量后若无下一次方法调用，就没有对该末次候选的延迟保留记录。
- 依用户限制，仅运行上述 focused pytest 和任务书要求的 lint；未运行其他测试套件或端到端 driver。
  kept_round 的平台消费行为通过本地源码核对，本次测试验证实际 serializer 输出的 step 字段。
- report_many 的 stdout 是批量摘要；完整 rrsi_rule 在 trajectory 的 step.method_reported 中。
  单 step 不增加测量点数量，新增 selection_pool_size=1 属于该现有 serializer 的正常格式。
