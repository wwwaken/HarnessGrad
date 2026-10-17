# AHE Best-of-2 修复报告

工作分支：`fix-ahe`；起点：`71acfbd3`。修改范围为 `methods/ahe/run.py`、
`methods/ahe/method.json`、新增的 `tests/quality/test_ahe_rule.py` 和本报告。

## 原偏差与上游依据

本机上游源码：`/mnt/20t/xubuqiang/Study/methods_src/ahe/evolve.py`。

- `evolve.py:3123-3151`：从同一 workspace 创建各变体的独立 worktree。
- `evolve.py:3715-3758`：默认 Best-of-N 的 `n=2`，分别分配 strategy hint；
  `evolve.py:2913-2917` 把它写成各变体的明确策略约束。
- `evolve.py:3857-3875`：并发启动各变体的 evolve agent。
- `evolve.py:3313-3336`：按 pass_rate 选择 winner，同分时优先较少异常，再优先较低索引。
- `evolve.py:3185-3223`：只 merge winner，给 loser 打标签，并采用 winner 的 manifest。

旧移植版只调用一次 `editor.ask`，只通过 `editor.report` 提交一个候选；
`method.json` 把候选宽度缩为一版的限制与每任务 rollout 数混在同一条 deviation 中。
上游的 Best-of-N 候选数 `n` 与 Harbor 每任务试验数 `k` 是不同参数；本次任务恢复的是
两候选的提案宽度，不是每任务重复试验或 all-k-pass 聚合。

## 实现

1. 使用 `ThreadPoolExecutor(max_workers=2)` 并发调用共享 editor。两个 prompt 包含不同的
   实质策略指令：变体 1 直接修复失败组件的实现；变体 2 从不同组件或不同已观察失败模式
   提出预防检查或恢复路径。两者都必须预注册 changes，不能只改编号来声称多样性。
2. 两个候选分别写入 `candidate`、`candidate-v2`，都从同一个 `edit_dir` 构建，
   并向 `editor.ask` 显式传递 `parent=edit_dir`，使 HARMFUL 回滚时的编辑上下文一致。
3. 两个提案有效且不同则一次 `editor.report_many` 提交 2 个 step，`stop=False`，
   允许后续调用读取平台测量结果。每个候选 step 保留 `ahe_manifest`、`ahe_attribution`、
   原有 `ahe_rule`，增加 `variant=1/2` 和 `ahe_rollouts`。
4. 在补全 manifest 的 files 字段前比较规范化 changes，忽略 changes 列表顺序；相同则
   确定性保留第一个有效候选，记录 `fallback_reason=identical_changes`。
   即使声明不同，若应用后的文件内容相同，也以 `identical_candidates` 退回单候选。
   拒绝修改、无效编辑、provider 异常均记录各变体状态和原因；只有一个有效变体时保留它。
   没有有效候选且存在 provider 异常时仍沿用 `editor.fail`，不伪装成两个有效候选。
5. 记录共同基底轮号，归因时各自与基底比较，避免将两个兄弟候选之间的差异当成回归；
   HARMFUL 回滚沿该基底找状态。换层规则按 manifest 的调用迭代号计数，避免同批两个变体
   被误算为两次失败迭代。
6. 更新模块说明和 `method.json`，删除过时的「只能一候选」声明，分别列明平台 winner、
   确定性回退、每任务单分数、共享编辑器及整候选回滚等实际限制。新增代码没有引入
   `HG_AHE_*` 之外的环境变量依赖，也没有任务 ID、分数或数据集专用决策。

## 红检与通过结果

指定的 `tests/quality/test_ahe_rule.py` 原来不存在。本次新增该入口，并导入
`test_ahe.py` 的全部原有测试，使同一条指定命令同时保留原有判决、回滚、manifest、
停止及异常路径的断言；原测试文件及断言未改。

验证顺序：先只新增测试，保持 `run.py` 和 `method.json` 为起点旧版，运行下列 focused
pytest。结果为 **12 failed, 18 passed in 5.62s**，退出码 1。首个新增测试明确失败于
`assert len(steps) == 2`，实际为 1；其余新增检查涵盖并发、重复回退、单变体失败保留、
共同回滚基底、兄弟候选归因和迭代计数，也全部在旧实现上失败。

完成实现后原样运行同一命令：

```bash
python3 -m pytest tests/quality/test_ahe_rule.py -q -p no:randomly --basetemp=/tmp/hg-pytest-ahe
```

结果：**30 passed in 0.48s**，退出码 0。并发测试使用双线程 barrier，串行调用无法通过。
模型调用全部 monkeypatch，候选和历史均为临时合成夹具；没有访问数据集或模型 endpoint。

另按公共任务书执行（启用 pipefail，以免 tail 隐藏 lint 的退出码）：

```bash
python3 tools/method_lint.py | tail -3
```

结果：**15 ok, 0 failed**，退出码 0。`git diff --check` 通过。
仅运行上述 focused pytest 和要求的 method lint；pytest 临时目录在测试后清理。

## 做不到或未做的部分

- **winner 的选择仍由平台按 train 分数做，AHE 自己的 winner 规则无法在 mode A 表达。**
  方法在提交同批两个 step 时还看不到分数，因此没有实现上游的异常数 tie-break、
  winner-only merge、loser git 标签或冠军 manifest 接续规则。这一偏差已写入
  `method.json`，方向为 `weaker`。
- 未恢复每任务 k 次 rollout 的 all-k-pass 聚合、上游 pass@1 估计、完整 evolve-agent
  工具循环或跨变体 debugger。两候选并不等于每任务两次试验。
- 策略差异不能保证模型遵从；声明或实际编辑重复时会减少为一个候选，拒绝、无效或异常
  也可能使本次没有有效新候选。相应结果在 `ahe_rollouts.variant_outcomes` 中保留。
- 归因仍依赖平台提供的历史和状态；旧记录不带共同基底字段，或记录的基底点已不在
  提供的历史中时，保留原来的相邻点解释。严格的共同基底归因需要基底点仍然可见，
  这项限制也已记入 `method.json`。本次没有改变平台保留历史、状态或预算截断的策略。
- 未运行 driver、真实模型调用、数据集诊断或 pilot，也未做联网下载。测试证明提交结构与
  决策分支，不构成实际 benchmark 测量或两候选改善分数的证据。
