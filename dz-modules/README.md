# Discovery Zero 模块化工具包

> 从 [Discovery-Zero-v2](https://github.com/SiliconEinstein/discovery-zero) 解耦出的工业级推理增强组件，为 AI Agent 和开发者提供 **可验证推理**、**贝叶斯置信传播** 和 **MCTS 科学发现引擎**。

## 系统架构

```
┌─────────────────────────────────────────────────────┐
│                   dz-mcp (MCP Server)               │
│          Cursor / Claude / 任何 MCP Agent           │
├─────────────────────────────────────────────────────┤
│                   dz-engine (核心引擎)               │
│   MCTS · Bridge 规划 · 类比/特化/分解 · 专家迭代     │
├──────────────────────┬──────────────────────────────┤
│    dz-verify         │      dz-hypergraph           │
│  Claim 提取·验证·    │  超图模型 · BP 推理 ·         │
│  Lean 形式化证明     │  工具链 · LLM · 沙箱          │
├──────────────────────┴──────────────────────────────┤
│                 gaia-lang (外部依赖)                  │
│            贝叶斯超图推理引擎 (Gaia BP)               │
└─────────────────────────────────────────────────────┘
```

依赖方向严格单向：`dz-hypergraph` ← `dz-verify` ← `dz-engine` ← `dz-mcp`。

## 四大组件

### [`dz-hypergraph`](packages/dz-hypergraph/) — 推理超图层

推理的数据基础设施。管理命题节点、推理步骤超边、置信度传播、以及所有底层工具（LLM 调用、代码沙箱、Lean 接口、向量检索）。

**核心能力：**
- **超图数据模型** — `Node`（命题）+ `Hyperedge`（推理步骤），支持序列化/持久化
- **贝叶斯置信传播 (BP)** — 基于 Gaia v2 的消息传递推理，支持增量传播
- **信念缺口分析** — 识别推理链中置信度最薄弱的环节
- **LLM 工具链** — 统一的 LLM 调用层，支持流式输出、自动续写、结构化输出、Token 预算控制
- **实验沙箱** — 安全执行 LLM 生成的 Python 代码，支持受控数据注入
- **Lean 4 接口** — 形式化证明的构建和验证
- **23 个 Skill Prompt** — 覆盖 Claim 提取、实验设计、Bridge 规划、类比推理等全部任务类型

### [`dz-verify`](packages/dz-verify/) — 验证层

确保推理过程中每一步都经过验证，将 LLM 的自然语言推理转化为可检验的断言。

**核心能力：**
- **Claim 提取管线** — 从推理文本中提取断言，分类为 quantitative / structural / heuristic
- **多路径验证** — quantitative → Python 实验，structural → Lean 形式化证明，heuristic → LLM 评判
- **验证结果回注** — 验证结果自动写回超图，更新节点置信度
- **Lean 反馈解析** — 将 Lean 编译器错误转化为结构化修复建议
- **连续验证** — 采样多条推理续写，通过一致性检测评估推理可靠性

### [`dz-engine`](packages/dz-engine/) — 核心引擎

完整的 MCTS 科学发现引擎，协调所有模块进行迭代式探索。

**核心能力：**
- **MCTS 搜索** — 蒙特卡洛树搜索，带 UCB 选择、渐进加宽、虚拟损失
- **HTPS 路径选择** — 图感知的叶节点选择，优先探索高信息增益路径
- **Bridge 规划** — LLM 生成的多步推理计划，带结构化验证
- **多模态探索** — 类比推理、问题特化/泛化、子问题分解、知识检索
- **实验进化** — 对失败的实验进行变异和重试
- **专家迭代** — 收集经验记录，支持 offline RL 训练

### [`dz-mcp`](packages/dz-mcp/) — MCP Server

面向 AI Agent 的标准化接口，让 Cursor、Claude Desktop 或任何 MCP 兼容客户端直接调用全部能力。

**暴露的 MCP Tools：**

| Tool 名称 | 功能 |
|---|---|
| `dz_extract_claims` | 从推理文本提取 Claims |
| `dz_verify_claims` | Claim 提取 + 验证 + 写回超图 |
| `dz_propagate_beliefs` | 贝叶斯置信传播 |
| `dz_analyze_gaps` | 信念缺口分析 |
| `dz_load_graph` | 加载超图 |
| `dz_run_discovery` | 运行完整 MCTS 发现流程 |

## 快速开始

### 安装

```bash
# 从源码安装（开发模式）
cd dz-modules
pip install -e packages/dz-hypergraph
pip install -e packages/dz-verify
pip install -e packages/dz-engine
pip install -e packages/dz-mcp
```

### 环境变量

在项目根目录创建 `.env.local`：

```bash
# 必需：LLM 接口
LITELLM_PROXY_API_BASE=https://your-llm-proxy.example.com
LITELLM_PROXY_API_KEY=sk-...
LITELLM_PROXY_MODEL=gpt-4o          # 或其他支持的模型

# 可选：Gaia BP 后端
GAIA_API_BASE=http://localhost:8080

# 可选：Lean 4 工作区
DISCOVERY_ZERO_LEAN_WORKSPACE=/path/to/lean_workspace

# 可选：向量检索
EMBEDDING_API_BASE=https://your-embedding-api.example.com
```

所有配置项均可通过 `DISCOVERY_ZERO_*` 前缀的环境变量覆盖，完整列表参见 [`ZeroConfig`](packages/dz-hypergraph/src/dz_hypergraph/config.py)。

### 使用方式一：Python SDK

```python
from dz_hypergraph import create_graph, propagate_beliefs, analyze_belief_gaps, save_graph
from dz_verify import extract_claims, verify_claims
from dz_engine import run_discovery, MCTSConfig

# 创建超图
graph = create_graph()

# 对 LLM 输出进行 Claim 验证，结果自动写回超图
summary = verify_claims(
    prose="通过泰勒展开，sin(x) ≈ x - x³/6 对小 x 成立...",
    context="三角函数近似问题",
    graph=graph,
    source_memo_id="step_1",
)
print(f"验证了 {len(summary.results)} 个断言")

# BP 传播，更新全图置信度
iterations = propagate_beliefs(graph)

# 找出推理链中最薄弱的环节
gaps = analyze_belief_gaps(graph, target_node_id="final_answer", top_k=5)

# 保存超图
save_graph(graph, "my_reasoning.json")
```

### 使用方式二：完整 MCTS 发现

```python
from pathlib import Path
from dz_engine import run_discovery, MCTSConfig

result = run_discovery(
    graph_path=Path("my_reasoning.json"),
    target_node_id="conjecture_1",
    config=MCTSConfig(
        max_iterations=30,
        max_time_seconds=3600,
        enable_evolutionary_experiments=True,
        enable_continuation_verification=True,
    ),
)
print(f"完成 {result.iterations_completed} 轮迭代")
print(f"目标置信度: {result.target_belief_initial:.3f} → {result.target_belief_final:.3f}")
```

### 使用方式三：MCP Server（Agent 集成）

```bash
# 启动 MCP Server
dz-mcp

# 或在 Cursor 中配置 .cursor/mcp.json:
# {
#   "mcpServers": {
#     "dz": {
#       "command": "dz-mcp",
#       "args": []
#     }
#   }
# }
```

启动后，Cursor Agent 即可直接调用 `dz_verify_claims`、`dz_propagate_beliefs` 等工具。

### 使用方式四：Cursor Skill（智能体技能）

将 `.cursor/skills/` 目录下的 Skill 文件放入你的项目，Cursor Agent 会在合适的时机自动识别和调用：

```
.cursor/skills/
├── dz-verify-reasoning/SKILL.md    # 推理验证技能
├── dz-belief-propagation/SKILL.md  # 置信传播技能
├── dz-discovery/SKILL.md           # MCTS 发现技能
└── dz-mcp-server/SKILL.md          # MCP 服务管理技能
```

详细说明见 [`.cursor/skills/`](.cursor/skills/) 目录。

## 开发

```bash
# 运行测试
cd dz-modules
python -m pytest tests/ -x -q

# 类型检查
python -m mypy packages/dz-hypergraph/src packages/dz-verify/src packages/dz-engine/src
```

## 设计原则

1. **零简化** — 从 Discovery-Zero-v2 完整复制，不删减任何功能路径
2. **单向依赖** — 严格的层级依赖，无循环引用
3. **配置集中管理** — 所有阈值、超参数通过 `ZeroConfig` 统一管控，支持环境变量覆盖
4. **真实执行** — 不存在任何模拟、虚拟、默认通过的代码路径
5. **行为兼容** — 解耦后的模块组合行为与原始单体完全一致

## 许可

与上游 Discovery-Zero-v2 保持一致。
