# Trace output bounding — 在**归档层**削减,不动 harness

2026-10-16。状态:**已实施**,待应用(`--apply` 尚未跑)。

> **修正记录。** 本文第一版把落点写成 `base_harness/loop/agent.py`。**那是错的,已撤回。**
> `base_harness` 是 **candidate(被测仪器)** —— 改它意味着前面所有实验的 harness 变了,必须
> 全部重跑,而且 trace 里的 `harness_identity` 会让两批 run 引用不同版本。落点已改为**归档层**。

## 一、问题(实测)

`base_harness/loop/agent.py:697` 把命令的**原始输出**写进 trace:

```python
out = proc.stdout + proc.stderr
trace.write({... "output": out})          # ← 原始,无上限
shown = _clip_output(out)                 # ← 给模型的只有 4000 字符(OUTPUT_LIMIT)
```

两种病态形态,**都不是评分问题**(模型只看到 4000 字符):

| 形态 | 实测 | 命令 |
|---|---|---|
| **`cat` 二进制** | agentdojo **22 GB**;151 条 `>10 MB`;`>500 KB` 输出中 **97% 是二进制**(ELF 91% + 含 NUL 5%) | `cat dojo_runtime/bin/python dojo.py tools` —— 把 30 MB 解释器 cat 出来,一条 trace 重复 4 次 |
| **`cat` 自己的 trace** | musique **252 MB**;6 条 `>10 MB` | `cat trace.jsonl \| grep -i "cardinale" \| head -50 \| grep -i "pessac"` —— **自引用膨胀**,每步的 trace 包含上一步的 trace,8.7 MB 文本 |

`>10 MB` 的文件全归档共 **157 个 / 21 GB**,其中 agentdojo 151 个。

## 二、落点为什么必须是归档层

三条约束,只有第三个位置同时满足:

| 候选落点 | 改 candidate? | 改方法行为? | 需要重跑? |
|---|---|---|---|
| `base_harness/loop/agent.py` | ❌ **会** | 不会 | ⚠️ **全部要重跑** |
| `eval/run/runner.py`(平台收集层) | 不会 | ⚠️ **会** —— `methods/llm_improver/run.py:7` 明写 improver 读平台 staged 的 `_harnessgrad/traces/` | 可能 |
| **归档层(`fold_nightly.py` + `bound_archive_traces.py`)** | ✅ **不会** | ✅ **不会** | ✅ **不需要** |

**harness 一个字节都不动 → candidate 不变 → 前面所有实验继续可比。**

## 三、实现的变换

对 trace 里的**命令行**逐条判断;`output` 超限则改写该行:

```
len(output) ≤ 256 KB            → 不动(整行逐字节原样写出)
是文本 且 ≤ 2 MB                → 不动(正当长日志保留)
其他(二进制 或 > 2 MB)         → 削减
```

削减时该行变成:

| 字段 | 含义 |
|---|---|
| `output` | 首 2048 + 标记 + 末 2048 字符 |
| `output_bytes` | 原始字节数 |
| `output_sha256` | 完整原始输出的 SHA-256 |
| `output_kind` | `"binary"` \| `"text"` |
| `output_stored` | `"reduced"` |
| `output_view_note` | 指向同 `step` 的兄弟记录:那里是**模型实际看到的**内容 |

**关键性质:**

- **未超限的行逐字节不变** —— `bound_trace_line()` 对不改动的行返回**同一个对象**,
  所以「哪些行被改了」可以靠对象身份计数,不需要比字符串。这让这个变换对除病态记录外的
  一切都是**可证明无操作**的。
- **模型实际看到的内容没有被动过**:harness 在裁剪时另写一条同 `step` 的记录,
  字段 `output_view` = `shown`(≤4000 字符)。它很小,本工具不碰它。
- **幂等**:削减后行变小,再跑一次不会被处理 —— 所以 `fold_nightly.py` 的入口削减与本工具
  的原地削减可以任意次序执行,不会互相重复处理。

## 四、两个工具,一个变换

| 工具 | 场景 | 原始字节去哪 |
|---|---|---|
| `fold_nightly.py`(新增入口削减) | **未来**的折叠 —— 它本来就是 copy 不是 move | 源 run 留在 `hg-census/runs/`,天然保留 |
| `bound_archive_traces.py`(原地削减) | **已归档**的 12 个,含 4 个旧形态归档 | **先 gzip 到 `hg-census/pre-bound-traces/`**(不发布),再覆盖 |

第二类的存在是必需的:agentdojo 等 4 个是旧脚本 `fold_runs.py`/`fold_to_full.py` 折的,
那两个脚本 **move + rmtree**,源 run 已销毁 —— **归档那份是唯一副本**,所以必须先留底。

`bound_archive_traces.py` 默认 dry run,`--apply` 才写;只写确实有改动的文件,
其余连临时文件都不留。

## 五、为什么安全

- **不碰 candidate**:harness 源码、行为、`harness_identity` 全不变 → **不需要任何重跑**。
- **不碰评分路径**:连 `shown` 都不动。
- **不丢可检验的东西**:`sha256 + bytes` 保留了「这条命令确实吐了 N 字节、内容是这个哈希」;
  原始字节在 `runs/`(新折叠)或 `pre-bound-traces/`(旧归档)里可查。
- **两类病态都是实测的**:97% 二进制是猫出来的解释器,另一类是模型读自己的 trace。

## 六、被否决的替代方案

- **只 gzip**:22 GB → 3.2 GB,下载者解压出来还是垃圾。**变小了,没解决。**
- **改 harness 在写入前截断**:改动 candidate → 全部实验失效。**被操作者否决,理由正确。**
- **改 runner 在收集时截断**:improver 读的就是 collected traces,会改变方法行为。
- **让 harness 拒绝 `cat` 二进制 / 拒绝读 `trace.jsonl`**:改变模型可见环境 → 改变 `shown` 和
  分数 → 要全部重跑。
- **在子进程层限制输出**:会改变 exit code 与可见输出(提前关管道给子进程 SIGPIPE)。

## 七、遗留的真实问题(不在本提案范围)

1. `subprocess.run(..., capture_output=True)` 把 30 MB **缓冲在 runner 的 RSS 里**,`jobs=40`
   时是内存风险。
2. `loop` 的 bash **没有单命令超时**,也没有对 `cat <二进制>` 或读自身 trace 的任何约束 ——
   这两类病态都是模型驱动的,平台侧只能记录,不能阻止。

修这两条**都要动 harness**,所以本提案不做 —— 单独评估,并且如果要做,必须承认那是一次
仪器变更,与前序 run 不可比。
