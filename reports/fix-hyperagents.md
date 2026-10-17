# HyperAgents deviation 记录修正

本任务只修改 `methods/hyperagents/method.json`、`methods/hyperagents/run.py` 的 docstring、`tests/quality/test_hyperagents_rule.py`，并新增本报告。方法行为和模型 prompt 均未改动。

## 逐条核实与修改

以下上游路径均相对于本机只读源码 `/mnt/20t/xubuqiang/Study/methods_src/hyperagents/`；移植版路径相对于当前 worktree。移植版行号为本次修改后的行号。

### 1. 多 child 提交与归档的真实限制

旧 deviation 的 `No real archive: one candidate per round` 与实现矛盾，已删除。上游 `utils/gl_utils.py:570-584` 将以前三名分数均值为中心的 sigmoid 乘上 `exp(-(child_count/8)^3)`，按归一化权重采样父代；移植版 `methods/hyperagents/run.py:220-230,245-269` 实际应用同一公式，不只是记录反事实选择。

`methods/hyperagents/run.py:343-353` 在调用前读取一次历史，默认请求 3 个 child，受剩余 epochs 限制；`:373-385` 分别生成候选目录并应用编辑；`:453,486-494` 只把 changed 候选交给 `editor.report_many`，可以一次提交多个 child。多个 child 可以抽到同一父代，代码不保证候选树各不相同，也可能因父代缺失、编辑不可用或调用错误而只形成部分 batch。

实际归档限制不是固定 newest 12。`harnessgrad/config/areas.py:107-110` 声明 `HG_METHOD_HISTORY_ROUNDS` 默认值为 **0**；`harnessgrad/channel.py:565-569` 定义 `HISTORY_ROUNDS` 和 `STATES_KEPT = HISTORY_ROUNDS or None`。因此默认 `STATES_KEPT=None`，暂存全部具备 harness hash 且能成功 materialize 的历史状态；显式配置正数 N 时，`:429-449` 才只暂存最新 N 个状态。没有可如实填写的固定正数 N。`:395-397` 仍导出所有历史轮次摘要，`methods/editor.py:117-134` 读取这些摘要。

`methods/hyperagents/run.py:309-318,362-371` 依赖 staged index 和实际目录；选择器并未预先按快照可用性过滤历史。若采样得到的父代未暂存，该 child 被跳过，不重新采样。另一个真实差异是上游 `generate_loop.py:900-925,1006-1017` 每代生成、评估、入档后再选父代；移植版同一次调用的 siblings 共享调用前历史，期间不获得新分数、不更新子代计数。这些限制均已写入第一条 deviation。

### 2. staged rescaling、agent/ensemble max、多域平均

旧记录笼统声称三者均“无对应物”，不够准确。上游 `utils/gl_utils.py:38-44` 在未 full eval 时按 domain staged fraction 缩放 agent/ensemble 分数，`:51-57` 取两者 max，`:523-530` 再跨 domain 求平均。

移植版 `methods/hyperagents/run.py:148-158,245-248` 的实际父代评分只读取 `protocol.studied_score`；`methods/protocol.py:137-141` 从 training 的 score 或其它记录的 train_score 取得一个标量，没有读取 agent/ensemble 或 per-domain 结果。`:363-368` 虽记录 staged 调度元数据，但传入 `staged_fraction=1.0`；`methods/hyperagents/staged_eval.py:30-40` 明确记录 `score_rescaling=none`。

同时，`methods/hyperagents/archive.py:57-61` **已有** agent/ensemble max 辅助实现；实际 `run.py` 父代选择没有调用它，而只在 `:396-399` 使用 archive 模块的 patch identity 功能。因此改为“实际选择路径未应用这些评分操作，max 辅助实现存在但未接入”，并将原先“full-set measurement”的宽泛理由改为运行所选任务集上的平台标量测量。

### 3. HG_HYPERAGENTS_SELECT

上游 `generate_loop.py:1068-1073` 的 CLI 默认是 `score_child_prop`，`utils/gl_utils.py:511` 的函数默认是 `best`；`select_next_parent.py:49-57` 计算子代数后直接均匀抽样。`generate_loop.py:1008-1017` 根据 `edit_select_parent` 决定执行哪个上游入口。

移植版 `methods/hyperagents/run.py:117` 在模块导入时读取环境变量，默认 `score_child_prop`。`:220-230,250-253` 支持本地固定权重分支 `score_child_prop`、`score_prop`、`uniform/random`、`best`，不会执行或演化上游 `select_next_parent.py`。未知值（包括 `latest`）使用 `score_child_prop` 权重，但仍在报告的 setting 中保留请求值；`:263-297` 使用基于 round 的确定性随机种子，并记录实际权重。第三条 deviation 已改写为上述可核实行为，而非暗示切换了两个上游程序。

## 红检与绿检

先仅新增两个 metadata 回归测试，保留 HEAD 的旧 `run.py` 和旧 `method.json`，运行：

```bash
python3 -m pytest tests/quality/test_hyperagents_rule.py -q -p no:randomly --basetemp=/tmp/hg-pytest-hyperagents
```

旧记录结果：**2 failed, 11 passed in 0.23s**。`test_metadata_describes_multiple_children_instead_of_a_single_candidate` 因命中 `one candidate per round` 失败；`test_metadata_archive_window_matches_the_configuration_default` 因缺少归档配置默认值而失败。红检发生在任何记录修订之前，无须 stash，原有 11 个测试全部通过。

修订记录与 docstring 后，同一命令结果：**13 passed in 0.07s**。新增测试在 `tests/quality/test_hyperagents_rule.py:209-234`：禁止单候选和无真实归档的过时措辞，要求说明多个 child、默认全部状态、正数 N 的窗口与跳过缺失父代；从 `MethodConfig().history_rounds` 直接读取源码声明的默认值，与记录中的数字比较，没有在断言中重复硬编码该数字。

另外运行任务书要求的命令（shell 开启 pipefail）：

```bash
python3 tools/method_lint.py | tail -3
```

结果：**15 ok, 0 failed**，退出码 0。另用静态 AST 比较确认：去除模块/函数 docstring 后，修改前后 `run.py` 的 AST 完全相同；`git diff --check` 通过。

## 没做与限制

- 没有改变归档、批量采样、selector fallback、评分或调度行为；缺失父代跳过、同批无中间反馈、未知 selector 的报告值与实际权重可能不一致等限制均保留并如实记录。
- 没有将辅助 max 接入实际选择器，没有增加 per-domain 或 staged/full 评估机制。
- 没有运行 driver、使用数据集、调用模型、启动诊断/pilot、联网或下载上游；任务书中的历史运行分数与树 hash 未重新验证，也未作为本次实测证据。
- 只运行指定 focused pytest 和 method lint，未运行其它 pytest 或集成测试；本次证明范围是记录回归、既有选择规则单测与静态代码核对，不证明生产运行表现。
- 仅在 `fix-hyperagents` worktree 分支提交，不操作 main、不 merge、不 push。
