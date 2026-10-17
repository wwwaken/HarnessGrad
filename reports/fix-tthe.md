# TTHE 文件 proposal card 修复报告

工作分支：`fix-tthe`；基线提交：`71acfbd3`。仅修改任务允许的四个代码/声明/测试文件，以及本报告。未操作 main、未 merge、未 push。

## 原偏差与上游依据

上游根目录：`/mnt/20t/xubuqiang/Study/methods_src/tthe/`，仅阅读本机源码。

- `text_to_sql/proposer.py:150-164`：确定卡片文件路径，`valid_proposal_card` 从磁盘读取 UTF-8 JSON；`:166-193` 检查身份字段和四个列表的类型。
- `text_to_sql/proposer.py:372-388`：prompt 要求将卡片写到指定文件；`:500-515`：没有合法卡片的子代返回 `None`。
- `text_to_sql/optimize.py:381-405`：固定分支由现任初始化，失败子代保留其父代。

旧移植版 `methods/tthe/run.py:597` 只读 `reply.get("proposal_card")`，而旧 `methods/editor.py::_ask_cli` 仅返回 `files` / `hypothesis` 或 `no_change`，不传回文件卡片。因此正常 CLI 编辑无法通过卡片闸门。

## 修改内容

1. `methods/editor.py` 增量增加 artifacts 通路：在 improver workspace 创建 `artifacts/`，将绝对目录及从 harness 工作目录访问它的 `../artifacts/<path>` 写入 CLI prompt。仅收集该目录的 UTF-8 普通文件，以相对路径为键返回 `reply["artifacts"]`。不解析、修复或截断内容，保留原始换行和 Unicode。
2. 收集上限为单文件 **256 KiB**、总计 **1 MiB**，按字节计量，超限明确抛错。路径拒绝绝对路径、父目录跳转、Windows 锚点/反斜杠及无效键；目录、文件及 artifacts 根目录的符号链接均拒绝。通过目录文件描述符和 `O_NOFOLLOW` 打开，避免链接替换引导到目录外；特殊文件也拒绝。
3. 原有 `files`、`hypothesis`、`no_change` 和删除编辑语义保持。仅有 artifact 而没有 harness 编辑，仍是 `no_change`；CLI 无编辑且非零退出，仍抛 `UnparseableReply`。
4. TTHE prompt 要求 CLI 写 `artifacts/proposal_card.json`，内容为四个列表组成的 JSON 对象，不包 `proposal_card` 外层。存在直接 `proposal_card` 字段时优先使用，即便其无效；仅在字段不存在时读取 `reply["artifacts"]["proposal_card.json"]`。控制器仍补齐原有身份字段。
5. `valid_proposal_card` 函数逐字未改，键集及类型没有放宽。新增诊断仅解释拒绝原因；无效卡片仍 `decision: stop`、`changed: false`、step 指向现任。记录增加 `proposal_card_source`，reason 包含回复/文件来源、缺项、类型或 JSON/路径错误。传输层无法读取的错误仍沿现有异常路径报告，不冒充正常 decline。
6. `method.json` 记录文件传输选择及限制，并按实际代码改写现有偏差：当前只提交一个挑战者，没有上游 judge，不能保证合法子代的分数不退步；拒绝卡片可能已花费 proposer 调用。基线 deviations 中本来没有单列“CLI 层产不出子代”的条目，因此没有虚构删除记录；修复后的声明不再把它列为限制。

## 红检与绿检

原仓库没有 `tests/quality/test_tthe_rule.py`，本次新增；现有 `test_tthe.py` 未改，复用其合成 fixture/helper，没有读取数据集。

最初在两个实现文件均未修改时新增测试，运行指定命令得到 `36 failed, 2 passed`。补齐兼容性检查后，用最终的 **44 项** 测试再次红检：将当前两个实现保存在内存，用 `git show HEAD:methods/editor.py` 与 `git show HEAD:methods/tthe/run.py` 暂时写回旧实现，运行同一命令，并在 `finally` 中恢复修复实现。结果：

```text
旧实现：41 failed, 3 passed in 2.16s，pytest exit 1
新实现：44 passed in 0.73s，pytest exit 0
```

关键红检证据：

- `test_cli_file_card_passes_gate_and_produces_a_step`：旧 CLI 返回值的 `artifacts` 为 `None`，不等于实际写出的卡片文件映射；新实现通过，并验证实际候选源码、轨迹 step 和合法完整卡片。
- `test_file_reply_alone_opens_gate`：直接提供合法 artifacts 卡片，旧 TTHE 仍 `changed=False`；新实现 `changed=True` 且 `decision=propose`。该用例独立钉住 run.py 的缺陷。
- `test_unsafe_artifact_paths_are_reported_and_rejected`：即使同时有合法卡片，包含 `../`、绝对路径及 Windows 路径的映射也明确拒绝并报告路径，保留现任。旧实现没有对应错误原因。
- 其余覆盖原文传回、根/目录/文件符号链接、字节上限与恰好到上限、非 UTF-8、错误 artifacts 类型、无效 JSON、缺项、四个列表的错误类型、直接字段优先、没有 artifact 时的兼容行为、删除编辑、decline 及 CLI 失败。
- 静态比较确认新旧 `valid_proposal_card` 函数源文本完全一致；测试额外确认完整卡片缺任一键或多出一键均拒绝。

实际运行的测试/检查命令仅为任务书指定项及静态 diff/源码核对：

```bash
python3 -m pytest tests/quality/test_tthe_rule.py -q -p no:randomly --basetemp=/tmp/hg-pytest-tthe
python3 tools/method_lint.py | tail -3
git diff --check
```

最终 lint 摘要：

```text
ok   tthe (published, 3 deviation(s), rule test test_tthe.py)

15 ok, 0 failed
```

`git diff --check` 无输出。pytest 临时树 `/tmp/hg-pytest-tthe` 已清理；测试将 CLI workspace 定向到该临时树，没有遗留本次的 `hg-cli-ask-*` 工作目录。

## 没做及限制

- 未运行 driver、数据集、真实 CLI improver、模型端点或 benchmark；没有联网或下载。测试 stub 外部 CLI，只验证 editor 文件通路到 TTHE 闸门、候选文件和 step 的本地闭环，不声称已经取得真实分数。
- 按要求仅运行指定 focused pytest 文件；未单独运行旧 `test_tthe.py`、共享 editor 的完整测试文件或全仓测试。旧测试文件及其断言完整保留。
- 没有移植 G×R 分支池、agentic judge、transductive 协议、上游专用 audit 或其他 label-free 代理，也没有调整方法超参数/评分规则。
- 文件只支持 UTF-8 普通文件，拒绝所有符号链接，超限拒绝而非截断；这是显式传输限制。安全打开采用当前 Linux 环境支持的 POSIX dir-fd / `O_NOFOLLOW`，未做 Windows 运行验证。
- 卡片的四个列表仍是模型自报内容；校验范围仍是既有键集/类型和控制器身份匹配，没有新增内部条目语义审查，也没有把合法卡片当作改进证明。
- 未改动已有 CLI 临时工作目录生命周期、平台调度或其他方法的流程。
