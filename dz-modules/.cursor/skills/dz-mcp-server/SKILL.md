---
name: dz-mcp-server
description: >-
  管理 Discovery Zero MCP Server 的启动、配置和使用。MCP Server 暴露 Claim 验证、
  置信传播、信念缺口分析和 MCTS 发现等工具，可供任何 MCP 兼容的 AI Agent 调用。
  当用户需要启动 MCP 服务、配置 MCP 集成、或了解如何通过 MCP 协议使用 Discovery Zero 时使用。
---

# MCP Server 管理技能 (dz-mcp-server)

管理 Discovery Zero 的 MCP (Model Context Protocol) Server，为 Cursor、Claude Desktop 或其他 MCP 客户端提供推理增强工具。

## 前置条件

```bash
pip install dz-mcp
```

这会自动安装所有依赖（`dz-engine` → `dz-verify` → `dz-hypergraph`）。

## 启动 MCP Server

```bash
# 直接启动（stdio 模式）
dz-mcp

# 或通过 Python
python -m dz_mcp.server
```

## Cursor 集成

在项目根目录创建 `.cursor/mcp.json`：

```json
{
  "mcpServers": {
    "dz": {
      "command": "dz-mcp",
      "args": [],
      "env": {
        "LITELLM_PROXY_API_BASE": "https://your-proxy.example.com",
        "LITELLM_PROXY_API_KEY": "sk-...",
        "LITELLM_PROXY_MODEL": "gpt-4o"
      }
    }
  }
}
```

## 暴露的 MCP Tools

### `dz_extract_claims`
从推理文本中提取结构化断言。

**参数：**
- `prose` (string, 必需) — 推理文本
- `context` (string, 必需) — 问题上下文
- `source_memo_id` (string, 必需) — 来源标识
- `model` (string, 可选) — LLM 模型名称

**返回：** `{"claims": [{"claim_text": "...", "claim_type": "quantitative", ...}]}`

### `dz_verify_claims`
提取断言 + 验证 + 写回超图。

**参数：**
- `prose` (string, 必需) — 推理文本
- `context` (string, 必需) — 问题上下文
- `graph_json_or_path` (string, 必需) — 超图 JSON 字符串或文件路径
- `source_memo_id` (string, 必需) — 来源标识
- `model` (string, 可选) — LLM 模型名称

**返回：** `{"claims": [...], "results": [{"verdict": "verified", ...}]}`

### `dz_propagate_beliefs`
在超图上执行贝叶斯置信传播。

**参数：**
- `graph_json_or_path` (string, 必需) — 超图 JSON 字符串或文件路径
- `max_iterations` (int, 默认 50) — 最大迭代次数
- `damping` (float, 默认 0.5) — 阻尼系数
- `tol` (float, 默认 1e-6) — 收敛容差

**返回：** `{"iterations": 12, "num_nodes": 15, "num_edges": 8}`

### `dz_analyze_gaps`
分析推理链中置信度最薄弱的环节。

**参数：**
- `graph_json_or_path` (string, 必需) — 超图 JSON 字符串或文件路径
- `target_node_id` (string, 必需) — 目标节点 ID
- `top_k` (int, 默认 5) — 返回前 k 个缺口

**返回：** `{"gaps": [{"node_id": "...", "gain": 0.42}]}`

### `dz_load_graph`
加载超图并返回摘要信息。

**参数：**
- `path` (string, 必需) — 超图文件路径

**返回：** `{"summary": "...", "num_nodes": 15, "num_edges": 8}`

### `dz_run_discovery`
运行完整的 MCTS 发现流程。

**参数：**
- `graph_path` (string, 必需) — 超图文件路径
- `target_node_id` (string, 必需) — 目标节点 ID
- `config_json` (string, 可选) — MCTSConfig 的 JSON 配置
- `model` (string, 可选) — LLM 模型名称

**返回：**
```json
{
  "success": true,
  "iterations_completed": 25,
  "target_belief_initial": 0.3,
  "target_belief_final": 0.87
}
```

## 工作流程

1. 确认用户已安装 `dz-mcp` 包
2. 帮助用户创建 `.cursor/mcp.json` 配置文件
3. 确认环境变量（LLM API）已正确设置
4. 启动 MCP Server 并验证连接
5. 向用户解释可用的 6 个工具及其使用场景

## 验证脚本

```bash
python .cursor/skills/dz-mcp-server/scripts/validate.py
```
