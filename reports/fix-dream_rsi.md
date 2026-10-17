# Dream-RSI 论文核对与偏差记录修正

结论：保留的是 argmax 的数学结构，移植版的 V 并非论文定义的平均回放目标。仅凭
`guarantee_holds=True` 不能声称复现了论文的不退化保证。本次不改数值公式、默认系数、
历史选择或选基逻辑；修正有明确论文依据的声明和报告字段，补齐可核实的 deviations。

## 范围与来源

- 分支：`fix-dream_rsi`；开始时 HEAD 为 `71acfbd3ac9e2763b3d16ea00ec0d85a6fce94eb`，工作区干净。
- 已完整阅读 `_common.md` 和 `dream_rsi.md`。仅修改任务允许的三个方法/测试文件及本报告。
- 任务书列的根目录 `Dream-RSI.pdf` 实际不存在。本地 README 第 30 行指向
  `/mnt/20t/xubuqiang/Study/Dream-RSI/papers/Dream-RSI.pdf`，已用 `pdftotext -layout`
  成功提取并阅读全部 36 页，包括正文、参考文献、附录 A/B/C；页码为 PDF 的 1-based 页码，
  与正文印刷页码一致。不是仅阅读 README 后推断论文内容。
- PDF SHA256：`5701649cd9793b29cd5fb32d727d101ad21fb23639c0d9f33c9adef826194342`。
- README SHA256：`88d12a26bc683b49b74824488d40661ea91ad28feac25566aa4d1ef8fa064747`。
- 本地目录还有引用文件、图片及 Git 元数据，但没有可对照的 RSI 控制器/回放评分实现。
  README.md:64–65 明说代码待发布，126–135 行的 release plan 也将完整代码及复现脚本标为准备中。
  附录 C 的代码是发现出的 Lasso 求解器，不是 Dream-RSI 的控制器或评分器。
- 核查采用 `texra-scientific-skills:manuscript-review` 的证据审查流程；没有委派子任务。
  没有运行 driver、读取或执行数据集、调用真实模型、联网或下载任何内容。

## 论文的 V、M 和保证到底是什么

论文 §3（p.5–6）先在线执行一个固定探索策略，生成一棵 discovery tree，再在固定历史
`H_t={T_1,...,T_t}` 上离线评估策略版本。每个版本都从每棵树的根开始，只看到已揭示的前缀，
回放确定性地揭示已有子节点，不生成新的执行结果。

p.6，公式 (1)：

```text
N_i^m = |T_i^(m,terminal)| - 1
V_i^m = max_{v in T_i^(m,terminal)} s_v
        - beta1 * N_i^m + beta2 * N_i^m / max(1, k_i^(m,terminal))
V^m   = (1/t) * sum_{i=1..t} V_i^m
```

- `s_v` 是固定任务评分协议下的节点得分，越大越好（p.5）。第一项取回放已到达节点中的
  最佳解质量，不能直接称为某个版本的一次验证集均分。论文没有规定通用的 `[0,1]` 标度。
- `N` 是揭示的非根节点数，即轨迹代表的生成—评估请求数；并非 token 数，也不是回放时
  新调用的次数。第 7 页实验设置同样用 discovery-agent calls 量化发现成本。
- `k` 是完成的回放决策轮数，每个非空 batch 算一轮；`W` 才是并行 worker 上限。
  对非空回放，`N/max(1,k)` 奖励每轮平均请求数（p.5–6）。它不是除以并发分支数或 trials。
- `beta1,beta2 >= 0` 为固定系数，正文没有给出数值默认值（p.6）。两个非质量项既改变
  目标也改变排序，不仅是同分裁决。外层平均对历史世界等权，`t` 不是固定任务集的题目数。
- `M>=1` 指本轮离线阶段的已评估策略版本集合，编号 `0..M-1`，包含当前策略 `pi_t^0=pi_t`。
  版本之间可以看到 replay feedback；不是一次提交 M 个没有中间反馈的独立采样（p.5–6）。
- p.6 从这个集合取 `argmax V^m`，因此 `V_selected >= V_current`。保证明确限定在
  **同一个固定历史 H_t 的平均回放分数**。随后把选中的策略部署到新的在线 rollout，
  论文没有从这一不等式推出未来在线表现或某次新编辑不退化。

## 一致的部分

| 项目 | 论文依据 | 对照移植版的判断 |
| --- | --- | --- |
| argmax 选择形状 | p.6，§3 Policy improvement and selection | `select()` 在有分数的记录上取最大代理值；仅此结构一致，V 的语义不同。 |
| 当前项在比较集合内 | p.5–6，`pi_t^0=pi_t` 及 p.6 保证 | 最新轮有可用分数时，它包含在比较内，数值不等式可核对；未评分时有不同的 fallback。 |
| 质量减代价加奖励的代数形状 | p.6，公式 (1) | `version_row()` 符号和 `max(1,k)` 形式一致；量纲和变量语义不一致，默认关闭奖励。 |
| 默认系数非负 | p.6，公式 (1) 前的约束 | 默认 0.001、0.0 满足非负约束，但不能据此认为数值复现；环境覆盖没有约束检查。 |
| 择优后读取所选状态 | p.5 的父节点 saved workspace；p.6 的选策略 | `base_round()` 有 staged state 时使用该目录，方向上复用历史状态；后续编辑不等于部署选中策略。 |

移植版通过 `protocol.studied_score` 排除 exam 分数，是本平台的隔离约束；没有把它冒充
为论文与 HarnessGrad 分割语义一致的证据。

## 缺失、替代及旧记录覆盖情况

下列八条均已写入 `method.json`，每条有稳定 `id` 和可核实的 `source`。
`weaker` 指缺少机制；具体分数或排序的方向没有证据时使用 `unknown`。

| id / 判定 | 论文依据 | 当前实现及原有记录问题 |
| --- | --- | --- |
| `replay_simulator` / 缺失，weaker | p.5–6，§3 Offline evaluation；README:91–104 | 没有树、前缀揭示或确定性转移。旧记录承认缺 replay，却把 best-of rounds 误称为自然退化；现在删除这个等价暗示。 |
| `fixed_history` / 替代，unknown | p.6，公式 (1) 及 Policy improvement | `version_row()` 直接取某轮 studied score，不取节点 max，不构造每个世界的 V_i，也不将每个策略在相同 H_t 上重评。旧 JSON 未单列；旧头注将 t 说成任务数，现已纠正。 |
| `execution_cost` / 替代，unknown | p.6，公式 (1)；p.7，§4 | 使用 `harness_tokens/1000`，默认 b1=0.001、b2=0.0。缺失、非数值或非正 tokens 时回退纯 quality；覆盖参数不检查符号或有限性。旧条目只写 0.001 对 0.05，暗示后者是上游基准，证据不足；改写为请求数与 token 的语义偏差和未指定系数。 |
| `parallelism` / 替代，unknown | p.5–6，回放终止及公式 (1) | k 实际为 `int(n_trials or 1)`，分子还是 token 代理。默认 b2=0，非零也不是论文的平均请求/决策轮奖励。旧 note 把 k 等同 trials、头注解释成并发分支，deviations 没单列，现均纠正。 |
| `offline_revisions` / 缺失，weaker | p.5–6，Offline evaluation 与 Policy improvement | 每次 main 只有一次 proposer 流程（可有格式/应用修复重试），交一个候选给平台测量；没有冻结历史上的 M 版本反馈循环。旧条目已提及，现补充明确语义和出处。 |
| `policy_surface` / 替代，unknown | p.4–5，§3；p.19，Listing 2:1–3 | `main()` 让共享 editor 修改 harness，没有专用探索策略限定，也没有共享线上/回放的分支、batch、停止接口。原 deviations 未记录。 |
| `selection_scope` / 不等价，unknown | p.6，Policy improvement and selection | 未评分末轮被忽略，comparison incumbent 回退到最后有分数轮；正 tokens 的 V 保留 6 位小数，平局选最早轮。选中 state 未 staged 时回退实际 incumbent；有 state 时仍会再编辑。不发送 `incumbent_round`。原 note 反而宣称完整表达部署保证，现收窄为代理数值比较。 |
| `appendix_objective` / 缺失且关系不明，unknown | p.19，B.2 Listing 2:12–21；p.21–22:145–188；p.6，公式 (1) | 附录写 `pareto.reward = pareto.auc - lambda * parallel_penalty`，对行为 beta 扫描，用 attainment/work 曲线及平均 effective_sequential_rounds/total_probes 排序。当前既无 sweep 也无 AUC；旧记录完全没提。不能据附录擅自替换正文目标。 |

### 这次实际修改

`run.py` 的头注、`config()`、`version_row()`、`select()` 和 `base_round()` 文档改为准确描述
论文及当前行为，附 PDF 页码/公式号；清除“精确移植”“不需要拒绝步就完整表达”等过度声明。
纠正 system prompt、比较表后的说明和 acceptance rule，防止把代理比较解释成论文保证。
这会改变 proposer 收到的解释文字，不承诺真实模型提案与此前相同。

`select()` 新增 `guarantee_scope="recorded_proxy_values_only"`，随 method_reported 和
extra 传出；保留旧 `guarantee_holds` 字段及其原来的数值计算，兼容已有读取者。
没有改 `version_row()` 算式、系数、精度、平局规则、缺分/缺成本处理及 `base_round()` 行为。
JSON 的 title/note 和八条 deviations 与这些实际行为逐项对应。

## 我无法核实的东西

1. **没有 Dream-RSI 的上游控制器、回放器、评分器、运行配置或原始 trace 可读。**
   PDF/README 足以核对定义，但不足以核对实际代码、实验默认参数或发布版本。
   附录 C 只有对象层 Lasso 求解器，不能拿来充当 RSI 实现。
2. **正文公式 (1) 与附录 B.2 的目标关系无法打通。** 正文是带请求数惩罚和每轮请求数奖励
   的单次回放终值，附录是行为 beta sweep 的 AUC/并行惩罚曲线目标；两者是否先后版本、
   近似、不同实验阶段或共同使用，没有源码或明确说明可证实。
   附录的单一行为 beta（p.21–22）与公式里的 beta1/beta2 也不能混同。
3. **M 的实现计数存在文字边界不清。** p.5 说构建 M 个版本 `0..M-1`；p.6 又说
   对 `m=0..M-1` 生成下一版本 `m+1`，末句仍从 M 个已评估版本 `0..M-1` 选择。
   我能核实最终明示的选择集合，不能替作者决定具体循环是否多生成一个未选版本。
4. **没有确认 beta1/beta2 的真实数值、token 到请求数的换算或分数标度换算。**
   通读正文和附录没有找到足以确定本移植默认值的依据。0.001 和历史移植值 0.05
   都不能称为论文默认值。没有做新调参或所谓“测下来”的实验。
5. **不主张这些替代必然让最终分数变高或变低。** token、trial、quality 以及 AUC
   改变了比较对象和目标；没有同世界回放证据就不能判定排名方向或数值可比性。
6. PDF 使用文字提取阅读；公式、图注、表格和附录文本已读，未逐页渲染核对图片细节，
   也没有独立复现实验数值、访问参考文献或检查论文之外的材料。
7. 没实现回放树、M 阶段、世界重评、策略专用接口、AUC 或真实部署/保留机制；
   没新增 `incumbent_round`、修复缺分 fallback、参数校验或缺成本处理。
   本任务以精确判定和诚实记录为主，这些仍是公开限制。加 scope 不是补齐这些功能。
8. 新增出处测试只检查记录的完整性和定位形式，不自动证明论文内容支持文字；支持关系
   由本次人工逐项阅读建立。`guarantee_holds` 仍可能在实际末轮无分数时为 True，
   所有消费者应连同 scope 和 versions 理解，不能只读布尔值。

## 红检与验证

红检直接在旧生产代码上完成，无需 stash：先只编辑测试（保留所有原测试和数值断言），
当时 `run.py` 和 `method.json` 仍是开始 HEAD 的内容，然后执行下面的 focused pytest。
结果为 **14 failed, 15 passed in 0.39s**，退出码 1。

- 两个既有 main 测试新增的断言失败：prompt 没有限定范围、报告没有 `guarantee_scope`。
- 新增的出处检查及八种偏差记录检查失败：旧 metadata 没有 source 和相应 id/记录。
- 三种范围用例在旧实现上因缺 scope 失败：高代理值但低质量、成本缺失与有成本混比、
  末轮未评分时 comparison incumbent 回退。这些用例保持原来选出的轮数，说明本次
  是准确报告既有行为，不是把新算法写入测试。

同一测试文件在修订后为 **29 passed in 0.13s**，最终说明文字复查后重跑为
**29 passed in 0.11s**；共保留原有 17 个用例、增加 12 个
参数展开后的用例，其中两个原有用例增补了范围断言。没有删除测试或降低任何原断言。
所有 main 测试使用本地临时最小 harness 和 fake ask，没有实际模型/数据集调用。

仅执行任务书允许的测试/检查命令：

```bash
python3 -m pytest tests/quality/test_dream_rsi_rule.py -q -p no:randomly --basetemp=/tmp/hg-pytest-dream_rsi
python3 tools/method_lint.py | tail -3
```

method lint 输出末行：**15 ok, 0 failed**，使用 `set -o pipefail` 确认退出码 0。
提交前另做只读 diff 审查和 `git diff --check`，并清理本次使用的 `/tmp` 测试目录及文字提取文件。
没有运行其他 pytest、driver、基准试验或下载命令；没有碰 main、merge 或 push。
