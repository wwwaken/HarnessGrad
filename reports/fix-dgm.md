# DGM 过时记录修复

工作分支：`fix-dgm`；基线：`71acfbd3`。本次只修改 DGM 元数据、说明文字及规则回归测试，不改变执行规则或参数默认值。

## 原偏差与上游依据

上游根目录为 `/mnt/20t/xubuqiang/Study/methods_src/dgm/`，全部依据来自本机源码。

- `DGM_outer.py:90-100` 使用 `random.choices(..., k=selfimprove_size)` 按概率有放回抽父代；`:111-148` 为各父代选择改进目标；`:224` 的 `--selfimprove_size` 默认 **2**。
- 原 `method.json` 声称 `One candidate per round: no parallel children and no rejection.`，note 也声称“一轮一个子代”，与当前执行路径矛盾；它还漏记了移植版默认 **3** 的配置差异。
- 原 `run.py` 模块说明也保留了“parallel children collapse to one child per round”的旧描述；本次同步更正，未修改算法。

## 如何确认当前代码能提交多个 child

以下行号以本次修改后的文件为准；`run.py` 执行代码仅因顶部说明增加三行而移动行号。

1. `methods/dgm/run.py:378` 从 `HG_DGM_CHILDREN` 读取数量，默认字符串为 `"3"`；`:382-383` 根据剩余预算限制批量大小。
2. `:388-395` 在 child 循环内逐次调用 `select_parent(history, round_index + child)` 和 `choose_target(parent)`，共享本次调用开始时的历史归档。
3. `:275-285` 计算父代权重，并以 child 对应的轮次构造随机种子；抽样允许重复父代。`:346-353` 的 prompt 包含父代轮次、分数与目标，因此 prompt 可以随抽样结果变化，但不保证每个 child 都不同。
4. `:410-427` 为每个 child 使用独立候选路径、顺序调用 editor 并应用编辑；`:435` 开始累积 steps；`:488` 只保留有改动的 step；`:524-535` 将这些 steps 一次传给 `editor.report_many`。
5. 只读核对 `methods/editor.py:1485-1502`、`:1515-1534`：该函数接收候选列表，逐项验证并写入 trajectory 的多个 step。没有修改此文件。
6. 已有单元测试 `test_one_call_submits_a_whole_batch` 在 mock editor 下确认 3 次调用、3 个 step、3 个独立候选目录；本次实际运行通过。上述源码路径是批量提交结论的依据，未使用运行收据或数据集推测。

## 修改内容及 deviations 核对

- 将 note 和批量提交 deviation 改为实际行为：一次调用可提交多个 child，逐 child 抽父代并选择 target，顺序生成后批量提交；预算、缺失父代状态及无可用编辑均可能减少提交数量。
- 明确定义“没有 rejection”：当前方法没有根据新 child 的测量分数执行拒绝，也没有用 `incumbent_round` 指定回滚到早先 incumbent。`keep_all` / `keep_better` 作用于后续父代池，不等于拒绝已测量的子代。无改动编辑、无效历史，以及不安全、未测量、未编译的父代仍会被过滤，见 `run.py:159-182`、`:204-235`、`:488`。这不是“没有任何过滤”。
- 单列默认数量差异：`HG_DGM_CHILDREN` 默认 **3** 是移植版既有配置选择，同时是相对上游默认 **2** 的偏差；效果方向记为 `unknown`。没有将其改回 2，也没有声称其效果更好。
- `noise_leeway` 的“可配置”描述仍成立：`run.py:101` 从 `HG_DGM_NOISE_LEEWAY` 读取，默认 **0.1**，与上游 `DGM_outer.py:238` 相同。`run.py:204-220` 与上游 `:174-188` 一样，在 `keep_better` 下使用“初始分数减去 leeway”的门槛；默认 `keep_all`（移植版 `run.py:105`、上游 `:232`）绕过门槛。改写 why，删除无法从实现核实的“小任务集上跨越很多区间宽度”解释，明确没有按任务集重新校准或统计保证。
- 保留不提供 gold patch、private test patch 和官方测试日志的 deviation；当前 `build_prompt` 只构造父代及目标摘要，也没有新增读取这些上游诊断输入的路径。
- `run.py` 只修改模块 docstring 和相应说明注释；对基线和新文件移除模块 docstring 后比较 `ast.dump(..., include_attributes=False)`，执行 AST 完全一致。

## 红检与验证

先只新增 `test_method_metadata_records_multiple_children_and_default`，保持旧版 `method.json`、`run.py` 原样运行下述 focused pytest。实际退出码 **1**：**1 failed, 4 passed, 1 deselected**，失败点是 `assert "no parallel children" not in text`。随后修复记录，用相同选择条件运行：退出码 **0**，**5 passed, 1 deselected**。新测试还要求记录中明确出现 `HG_DGM_CHILDREN`、`default 3`、上游 `--selfimprove_size`、`default 2`，并禁止 note 中的旧中文单子代说法。

实际执行命令（红检、绿检各一次）：

```bash
PYTEST_ADDOPTS='-k not\ test_a_batch_becomes_one_curve_point_per_child' python3 -m pytest tests/quality/test_dgm_rule.py -q -p no:randomly --basetemp=/tmp/hg-pytest-dgm
```

为遵守本次用户明确的“不要运行 driver、不要用数据集”，通过 pytest 选择条件排除 `test_a_batch_becomes_one_curve_point_per_child`：它在文件内启动 `driver.py` 并指定 demo 数据集。该已有测试及全部原有断言保持原样，不将它计为通过。

另外执行公共任务书要求的 lint（开启 shell pipefail，避免 tail 掩盖失败）：

```bash
set -o pipefail
python3 tools/method_lint.py | tail -3
```

结果：退出码 **0**，**15 ok, 0 failed**。`git diff --check` 也通过。测试临时目录 `/tmp/hg-pytest-dgm` 在完成后清理。

## 没做及限制

- 未运行 driver、未加载数据集、未调用真实模型、未联网或下载；未执行上述 driver 集成测试，因此不提供新的端到端测量或生产运行结论。
- 未改变批量大小、父代采样、target 规则、归档保留、拒绝/回滚能力或任何执行行为；未验证默认 3 相对默认 2 的效果，也未实施 noise 统计校准。
- 多 child 是批量候选提交，生成流程仍为顺序循环；重复父代与相同编辑均可能发生，不声称真实线程并发或保证候选多样性。
- 未修改 main、平台、评分、数据集或 improver 配置，未 merge、未 push。提交仅位于本 worktree 的 `fix-dgm` 分支。
