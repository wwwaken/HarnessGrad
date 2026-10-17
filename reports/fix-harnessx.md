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

## 第二轮修复（基线 `ff40b78f`）

本节按 `harnessx-round2.md` 纠正第一轮结论；上面的第一轮过程记录保留，但其中「当前默认 0.0 / 计数护栏关闭」以及「未运行旧验收文件」不再描述本轮最终状态。没有重写历史。本轮仅修改 `methods/harnessx/run.py`、`methods/harnessx/method.json`、`tests/quality/test_harnessx_rule.py` 并追加本报告；`tests/quality/test_harnessx.py` 原样保留。

### 三个问题的根因与修复

1. **默认值错误。** 本机上游 `/mnt/20t/xubuqiang/Study/methods_src/harnessx/recipe/gaia_evolver/run.py:463-475` 的默认容忍度是 `0.03`，理由是吸收典型 2–3 个百分点的评估随机噪声，避免无关任务翻转导致有效代码修复被丢弃；历史最佳仍只在严格提升时更新，不随容忍度下漂。计数护栏默认 `3` 的依据是同文件 `:1184`、`:1222-1236` 及 `recipe/gaia_evolver/defaults.py:23`。本轮恢复 `0.03 / 3` 默认值及坏配置回退值，同步模块说明、环境变量说明和 `ACCEPTANCE_RULE`。保留显式 `0.0` 容忍度、显式 `0` 计数阈值、HG 环境变量优先于旧别名的行为；负容忍度仍下限截到 `0.0`，不误称为回退 `0.03`。没有依据成绩调参。
2. **预注册记录缺失。** 验收中的 `0.90 → 0.89` 本应接受，但旧默认值使其提前回滚，根本没有调用 stub editor，因而新提案的预注册没有生成；恢复默认值后，原有接受分支会正常记录完整声明及非法 lever。同时补齐真正回滚路径：保留被验收候选的原预注册，来源标为 `previous_round_record`；如果历史没有声明，则输出完整字段形状及 `source=unavailable`、包含被验收轮次的缺失原因，不伪造 hypothesis。快照有无两条路径都如此。上游依据为 `recipe/gaia_evolver/run.py:813-839`：恢复 `current_config` 后仍查找并回填同一轮 journal。回滚改变提交树和选择轮，不删除分数、历史或候选原声明，也不生成新的编辑提案。
3. **provider 原因未进入记录。** 同样是提前回滚导致 provider stub 从未被调用，不能说异常被 `editor.fail` 吞掉；已有 `editor.fail` 实际会把异常类型和文本写进 `method_reported.error`。本轮修正分支条件，保留原异常出口，并新增集成红检：计数差恰好达到 3、分数下降仍在默认容忍度内时，确认确实调用 editor，记录精确的 `RuntimeError: 503 no available channel`，同时保留 `ACCEPTED` gate、预注册字段与 `changed=false / stop=false`。没有放宽 `503` 断言，也没有修改共享 editor。

`method.json` 已删除「任务书要求比上游严格的默认值」这一不再成立的 deviation；记录当前 `0.03 / 3` 默认值、回滚与预注册的关系、明确缺失来源和实际 provider 错误出口。保留计数缺失时接受、token 成本代理、下一次调用才验收、shipping validator 尚未移植等真实限制。

### 测试调整的逐项依据

没有删除测试或降低原有验收断言；旧 `test_harnessx.py` 未改。规则文件中必须随第二轮改正的地方：

- 原 `test_strict_defaults_and_invalid_tolerance_fallback` 改名为 `test_upstream_defaults_invalid_tolerance_fallback_and_negative_clamp`：未设置、拼错、NaN、Inf 的容忍度期望从 `0.0` 改为 `0.03`，计数阈值期望从 `0` 改为 `3`。依据为上述上游 `run.py:463-475`、`:1184`；负数截为 `0.0` 的断言保留。
- 一题退步恢复完整树的测试显式设置容忍度 `0.0` 和计数阈值 `0`，保留其全部原断言，包括 `> tolerance 0.000`；缺计数仍回滚、超过配置容忍度回滚、无效高分不成为最佳这三个测试显式将计数阈值设为 `0`，原回滚断言全部保留。依据为上游 `run.py:468` 明确支持严格容忍度、`:1227` 的计数阈值算术（设为 0 不会命中小计数豁免）。这些测试检验显式严格策略，不再把它当上游默认策略。
- 新增默认容忍度内、恰在边界、超过边界三个集成情形；全部使用通过数差至少 3 的历史，避免计数护栏掩盖容忍度错误，并检查历史最佳不下漂。新增四种回滚预注册组合（快照有/无 × 原声明有/无），以及真正进入 provider 的精确错误原因测试。

### 红检与最终验证

只执行任务书指定的两个 focused pytest 文件以及 method lint；没有调用 driver、使用数据集、调用真实模型或联网。pytest 中的分数和任务标识仅为临时合成测试输入。

```bash
python3 -m pytest tests/quality/test_harnessx.py -q -p no:randomly --basetemp=/tmp/hg-pytest-harnessx
python3 -m pytest tests/quality/test_harnessx_rule.py -q -p no:randomly --basetemp=/tmp/hg-pytest-harnessx
python3 tools/method_lint.py | tail -3
```

- 修改实现前，原验收文件复现 `7 failed, 10 passed in 0.15s`（退出码 1），与任务书失败项目一致；任务书总数 `7 failed / 30 passed` 包含第一轮 20 个规则测试。
- 先完成本轮规则测试改动、仍保持 `ff40b78f` 实现不变，再运行规则文件：`11 failed, 17 passed in 0.55s`（退出码 1）。失败覆盖默认/坏配置回退、三个默认容忍度情形、两个缺失原声明的回滚出口，以及 provider 未调用。两个已有原声明的回滚对照通过，确认那部分原本已有能力。
- 修复实现后，同一规则文件：`28 passed in 0.51s`（退出码 0）。
- 修复实现后，未修改的原验收文件：`17 passed in 0.17s`（退出码 0）。两文件合计 **45 passed**。
- method lint 使用 `pipefail` 确认命令本身成功：`15 ok, 0 failed`（退出码 0）。
- `git diff --check` 通过；验证后清理专用 `/tmp/hg-pytest-harnessx` 临时目录。

### 尚未完成或本轮未做

- 没有迁移完整 shipping validator、HarnessX runtime replay、处理器契约或 journal novelty/evidence 验证；这些仍是明确的 weaker deviation。
- 真正回滚时不会再调用 editor 生成一份新声明；它保留的是被验收候选的历史声明。历史缺失时只能如实标记缺失，不能恢复不存在的原预测。
- 本轮没有改变下一次调用才验收、最后候选可能没有验收调用、回滚占用提交预算和缺快照无法物理恢复的限制。
- 缺少通过数时默认正数噪声护栏仍接受且不更新最佳；旧曲线聚合近似、token 成本代理仍存在，已在 deviations 中保留。未额外扩展这些机制。
- 未运行完整测试套件或任何真实诊断/pilot；focused 通过不构成性能、训练/考试成绩或生产运行授权的结论。
