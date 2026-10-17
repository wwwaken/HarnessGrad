# meta_harness 两阶段候选修复报告

工作目录：`/mnt/20t/xubuqiang/hg-wt/fix-meta_harness`。分支：`fix-meta_harness`。
起点：`71acfbd3`。修改限于任务书指定的三个文件与本报告；未操作 main、merge 或 push。

## 原偏差与本地上游依据

- `/tmp/mh-upstream/reference_examples/terminal_bench_2/meta_harness.py:431-456`：一次迭代启动一次 Claude Code proposer 会话，不传 temperature，以 `pending_eval.json` 存在判断成功；该函数不使用 `n_candidates`。
- `/tmp/mh-upstream/reference_examples/terminal_bench_2/.claude/skills/meta-harness-terminal-bench-2/SKILL.md:65-66`：每候选只验证一个机制、一个假说，机制应来自轨迹诊断。
- 同一上游 skill 的 `:70-98`：分析阶段深读失败与成功轨迹，返回候选名称、假说及具体 changes；实现阶段必须收到该候选的 name 和 changes。
- 同一上游 skill 的 `:101-117`：agent 将候选写入清单，而不是外层对同一 prompt 独立采样。
- 旧移植 `methods/meta_harness/run.py:396-403` 对所有 child 调用同一个 `build_prompt(...)`，没有候选描述。共享 editor 固定 `temperature=0.0`，重复调用并未提供设计层面的差异；旧 main docstring 却将批内多样性归于 sampling。
- 另经调用链检查发现：旧代码虽然先取 `childN` 路径，`propose_and_apply` 内部仍返回相同的 `workspace/candidate`。多个步骤会指向被后续候选覆盖的目录。

## 改动

1. 多候选时只调用一次设计层 `editor.ask`，要求默认三个、受剩余预算上限约束的候选，以 `candidates` JSON 数组返回非空字符串 `name / hypothesis / changes`，明确要求机制不同、每个只验证一个假说，并查看失败和成功证据。
2. 每个设计分别进入实现调用；实现 prompt 包含该候选的完整名称、假说与 changes，修复 prompt 也保留这些内容。所有候选继续从同一个 `edit_base` 实现。
3. 每个实现请求使用独立 workspace，实际结果位于 `childN/candidate`，防止步骤提交后被覆盖。测试同时检查原基底未改变及两个候选文件内容分别保留。
4. `HG_META_HARNESS_CANDIDATES=1` 或剩余预算仅够一个候选时，跳过设计调用，保留直接单候选路径。
5. 不修改 `frontier_of`、`update_frontier`、`base_round` 或既有 gate/选基底规则，也不修改 `methods/editor.py`。
6. `method_reported.meta_harness_design` 记录请求数、设计模式、有效去重候选与回退原因；成功步骤另存 `meta_harness_candidate`。
7. 移除 run.py 中 sampling 的错误说明。原 method.json 的 deviations 没有独立的 sampling 条目，因此没有伪称删除该条；更新 note 并新增准确的两阶段批量/设计 endpoint 偏差说明，同时保留原有模型、历史窗口、smoke gate 限制。

## 重复 changes 的处理与理由

按返回顺序保留有效条目；三个字段必须都是非空字符串。将 changes 的连续空白折叠并忽略大小写后去重，再按预算截断。模型返回三个设计但只有两个不同 changes 时，只实现这两个。

不足两个有效且不同的 changes 时，统一记录 `mode=single_fallback` 和 `fallback_reason`，只实现一次：若存在一个有效设计，就实现它；若一个也没有，就走直接提案。无法解析 JSON 的 `editor.UnparseableReply` 也按同样规则回退并记录原因。其他设计调用异常保持 error，不伪装成正常回退或零分。

这是任务书要求的重复预算保护及上游“一机制一候选”约束的实现，不根据分数、任务、数据集或模型表现选择规则；没有搜索或调整参数，也没有改变默认候选上限。

## 红检与测试结果

先只添加测试、保持 run.py 为 `71acfbd3` 旧实现，然后运行任务书指定命令：

```bash
python3 -m pytest tests/quality/test_meta_harness_rule.py -q -p no:randomly --basetemp=/tmp/hg-pytest-meta_harness
```

旧代码：`16 failed, 15 passed in 1.12s`，退出码 1。核心测试
`test_batch_implements_different_designed_mechanisms_from_the_same_base`
在 `len({call["prompt"] for call in calls}) == 2` 处失败，实际为 1，错误为
`children received identical prompts`。其他新增测试也在旧代码失败。原有 15 项全部通过，未删除测试或降低已有断言。

随后实现修复，以完全相同命令复跑：`31 passed in 0.27s`。覆盖不同 prompt 各含自身设计、修复 prompt 保留设计、同基底实现、输出目录不互相覆盖、默认三个及预算上限、单候选跳过设计、无效结构/重复 changes/不可解析回复回退，以及 no_change 时仍记录回退原因。

另运行任务书指定 lint：

```bash
python3 tools/method_lint.py | tail -3
```

使用 shell pipefail 检查整条管道退出码为 0，摘要：`15 ok, 0 failed`。`git diff --check` 通过。

## 未做与限制

- 没有运行 driver、数据集、真实模型、诊断或 pilot；没有联网或下载；没有复算任务书中的历史运行分数和 hash。通过的是本地假模型 focused 测试，不能宣称真实模型已产生不同实现或分数提升。
- 文本去重不识别同义改写，无法证明机制在语义上不同；不同 prompt 仍可能生成相同代码。独立目录保护候选状态，但本次未增加成品树内容去重。
- 设计阶段通过 `editor.ask(endpoint_only=True)` 获取 schema JSON，避免 CLI improver 将设计请求执行为文件编辑。因此批量路径新增共享 method endpoint 凭据要求；只有 CLI、没有 endpoint 的配置不能保证运行批量设计。单候选路径不增加该要求。此限制已写入 method.json。
- 共享 editor 仍会注入平台上下文及通用编辑格式提示；设计 prompt 明确要求只返回 candidates。未修改 editor，其内部解析重试和实现修复仍可能产生额外模型调用。
- 上游的两个自主 subagent、任意文件系统探索、完整历史树与 smoke test 没有恢复；设计层读取的是共享 editor 内联证据、frontier 与历史行。没有扩展任务书以外的平台能力。

测试临时目录 `/tmp/hg-pytest-meta_harness` 在测试完成后清理。
