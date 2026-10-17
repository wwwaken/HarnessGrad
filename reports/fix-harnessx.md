# HarnessX 回滚修复

工作分支：`fix-harnessx`；修复基线：`71acfbd3`。仅修改任务允许的两个方法文件、新增指定规则测试，以及本报告。没有操作 main、merge、push，没有运行 driver、数据集、模型或联网下载。

## 原偏差与上游依据

上游源码根目录：`/mnt/20t/xubuqiang/Study/methods_src/harnessx/`。

- `recipe/gaia_evolver/run.py:1188-1208`：对照历史最佳，只有严格提升才替换最佳；同分保留最早最佳。`:1218-1257` 给出成本调整、容忍度及通过数噪声护栏；`:813-820` 实际把 `current_config` 恢复为最佳配置。`:277-293` 另有展示用历史最佳索引计算，本次没有把展示逻辑误当验收门。
- 旧移植版**已经有**复制历史最佳树的回滚分支，因此原 `method.json` 的 “The gate cannot revert anything” 并不准确。实际缺口是：使用旧变量 `HARNESSX_TOLERANCE`、默认容忍度 `0.03`、默认通过数护栏 `3`，导致小幅退步及缺少计数时继续接受；同时没有输出 `incumbent_round`。已有树复制能力得到保留并补足。
- **任务书与本机上游存在差异**：本机 `recipe/gaia_evolver/run.py:463-475` 的实际默认容忍度是 `0.03`，不是 `0.0`；`:1222-1236` 还有通过数变化少于 3 时不回滚的护栏。本次遵循任务书明确要求的严格默认值 `0.0`，并默认关闭通过数护栏。这是按任务书实施的策略差异，已在代码注释与 deviations 中披露，不能称为本机源码默认值的忠实复刻。
- 上游 shipping gate 不只是最终版本选择。`harnessx/meta_harness/validate_workflow.py:857-869`、`:909-933` 包括规范化、结构变更、处理器契约、replay、新颖性和证据检查；`harnessx/meta_harness/replay.py:64-151` 确实执行合成任务。原来 “platform does not execute the candidate” 的表述不成立：平台会测量候选，只是没有实现这些 HarnessX 专属检查。

## 修改内容

1. `HG_HARNESSX_REGRESSION_TOLERANCE` 优先，默认 `0.0`；未设置该变量时兼容旧 `HARNESSX_TOLERANCE`。非法、非有限、负数容忍度回到 `0.0`。没有根据分数调参。
2. 默认通过数噪声阈值为 `0`，不再因为只少过一题或没有计数而绕过严格回滚。显式设置正数 `HARNESSX_PASS_COUNT_NOISE_THRESHOLD` 仍能启用原有噪声策略；历史最佳重放、成本算术、同分不替换最佳的规则保留。
3. 退步超过容忍度时，复制最佳轮完整树，通过**单步** `editor.report_many` 提交并声明 `incumbent_round=<最佳轮>`；不调用编辑模型。`method_reported.harnessx_gate.reason` 记录候选轮、最佳轮、分数差、退步幅度和容忍度，例如 `reverted: candidate 3 ... best round 1 ... delta -0.125; drop 0.125 > tolerance 0.000`。
4. 有快照的回滚设置 `stop=False`，包括树已经相同的情形；快照缺失则记录所选轮及 `state_available=false`、`changed=false`、`stop=True`，诚实说明无法物理恢复，不继续在被拒绝的树上编辑。
5. 只用有限、已被平台测量的分数重建历史最佳；未测量、缺失或非有限分数记为 `NO_GATE`，不伪装成普通零分回归。
6. 重写不实的两个 deviation，补充回滚时机/预算、shipping gate 具体缺口、严格默认值与本机上游的差异、成本代理、可选通过数护栏及共享编辑层限制。相关代码注释标明上游路径与行号。

## 红检与验证

只运行任务书指定的 pytest 命令及 method lint。测试用临时合成 harness、人工历史分数与 stub editor，实际检查 stdout 和 trajectory；没有调用 driver 或真实模型。

```bash
python3 -m pytest tests/quality/test_harnessx_rule.py -q -p no:randomly --basetemp=/tmp/hg-pytest-harnessx
python3 tools/method_lint.py | tail -3
```

- 最初先添加 16 个测试、保持实现未改：`12 failed, 4 passed`，退出码 1。失败包含小幅退步、缺计数回滚、选择轮记录、容忍度配置、缺快照停止等；四个不应回滚的对照通过。
- 最终套件增加测量有效性检查后，用 `git show HEAD:methods/harnessx/run.py` 取得基线实现，临时替换**本分支**的方法文件，保持最终测试不变运行同一命令：`16 failed, 4 passed in 0.55s`，pytest 退出码 1。随后在 `finally` 中恢复修复实现；没有 stash、reset 或修改其他分支。
- 最终修复实现运行同一 focused pytest：`20 passed in 0.26s`，退出码 0。
- 覆盖：历史最佳不是上一轮、小退步/大退步/缺计数回滚、完整树文件恢复及清除候选残留、`incumbent_round`、原因记录、同分/提升/容忍范围/恰好边界不回滚、越界回滚、缺快照、相同树继续、配置默认/优先级/坏值，以及无效测量不作为零分或历史最佳。
- method lint：`15 ok, 0 failed`；以 `pipefail` 检查管道退出码为 0。
- `git diff --check` 通过。测试临时目录 `/tmp/hg-pytest-harnessx` 在验证后清理。

## 做不到或未做的部分

- 没有移植完整 shipping validator。具体缺口是 HarnessX YAML `HarnessConfig` 的规范化/结构 diff 集成、处理器 hook 契约执行、HarnessX runtime 合成任务 replay，以及 memo/journal 的 novelty/evidence 校验。保留 `weaker`；`incumbent_round` 只表达版本选择，不声称这些检查已经通过。
- 规则只能在下一次方法调用中验收刚测完的候选。若预算在最后一个候选测量后耗尽，没有下一次调用，最后候选仍未经本门验收；回滚提交也占用平台预算。只改方法三个文件无法消除该平台调度限制，已披露。
- 最佳状态未暂存时不能物理恢复；选择记录不会被描述为实际恢复成功。
- 成本仍是平台 token 字段代理而非 USD。可选计数护栏仍含旧聚合计数近似、缺计数时接受的限制；默认关闭时不影响严格规则。
- 未运行完整 suite、旧 `tests/quality/test_harnessx.py` 或任何额外 pytest 命令。旧测试仍含 `0.03/3` 默认值断言及没有计数时接受等历史预期；按本次文件边界原样保留，后续若运行广泛测试需同步评审这些预期，不能把本次 focused 通过说成全套通过。
- 未做诊断/pilot，没有新的性能、train/exam 或因果结论；不能据本次单元测试断言任务书提及的成绩差距已被解释或消除。
