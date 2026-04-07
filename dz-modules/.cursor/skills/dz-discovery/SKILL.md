---
name: dz-discovery
description: >-
  运行完整的 MCTS 科学发现引擎：蒙特卡洛树搜索 + Bridge 规划 + 多模态探索（类比/特化/分解）+
  Claim 验证 + BP 传播的迭代循环。当用户要求探索数学猜想、科学假设、开放问题，
  或需要系统性地增强推理链条时使用此技能。
---

# MCTS 发现引擎技能 (dz-discovery)

运行完整的 MCTS 迭代发现流程：选择探索节点 → Bridge 规划 → 执行动作（实验/证明/类比/分解）→ Claim 验证 → BP 更新 → 反馈搜索。

## 前置条件

```bash
pip install dz-engine dz-verify dz-hypergraph
```

需要设置环境变量：
- `LITELLM_PROXY_API_BASE` + `LITELLM_PROXY_API_KEY`（LLM 接口，必需）
- `GAIA_API_BASE`（Gaia BP 后端，可选）
- `EMBEDDING_API_BASE`（向量检索，可选）
- `DISCOVERY_ZERO_LEAN_WORKSPACE`（Lean 4 工作区，可选）

## 核心 API

### 1. 高层 API（推荐）

```python
from pathlib import Path
from dz_engine import run_discovery, MCTSConfig

result = run_discovery(
    graph_path=Path("my_graph.json"),
    target_node_id="conjecture_1",
    config=MCTSConfig(
        max_iterations=30,
        max_time_seconds=3600,
        c_puct=1.4,
        enable_evolutionary_experiments=True,
        enable_continuation_verification=True,
        enable_retrieval=True,
        enable_problem_variants=False,
    ),
    model="gpt-4o",
)
print(f"迭代: {result.iterations_completed}")
print(f"置信度: {result.target_belief_initial:.3f} → {result.target_belief_final:.3f}")
print(f"耗时: {result.elapsed_ms / 1000:.1f}s")
```

### 2. 底层 API（完全控制）

```python
from pathlib import Path
from dz_engine.mcts_engine import MCTSDiscoveryEngine, MCTSConfig
from dz_verify.claim_verifier import ClaimVerifier
from dz_verify.claim_pipeline import ClaimPipeline

engine = MCTSDiscoveryEngine(
    graph_path=Path("my_graph.json"),
    target_node_id="conjecture_1",
    config=MCTSConfig(max_iterations=20),
    claim_verifier=ClaimVerifier(),
    claim_pipeline=ClaimPipeline(),
    model="gpt-4o",
)
result = engine.run()
```

### 3. MCTSConfig 参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `max_iterations` | 30 | 最大 MCTS 迭代次数 |
| `max_time_seconds` | 14400 | 最大运行时间（秒） |
| `c_puct` | 1.4 | UCB 探索系数 |
| `num_simulations_per_expand` | 3 | 每次扩展的模拟次数 |
| `enable_evolutionary_experiments` | True | 启用实验进化（失败实验变异重试） |
| `enable_continuation_verification` | True | 启用连续验证 |
| `enable_retrieval` | True | 启用知识检索 |
| `enable_problem_variants` | True | 启用问题变体生成 |
| `specialization_threshold` | 3 | 连续失败后触发特化 |
| `replan_on_stuck` | 2 | 连续无进展后重新规划 |

### 4. MCTSDiscoveryResult 结构

```python
result.success                  # bool: 是否达成目标
result.iterations_completed     # int: 完成的迭代次数
result.target_belief_initial    # float: 初始目标置信度
result.target_belief_final      # float: 最终目标置信度
result.traces                   # list: 每轮迭代的跟踪记录
result.best_bridge_plan         # BridgePlan: 最优 Bridge 规划
result.elapsed_ms               # float: 总耗时（毫秒）
result.experiences              # list: 专家迭代经验记录
```

## 探索模块说明

引擎在每轮迭代中根据 UCB 选择以下模块之一：

| 模块 | 说明 |
|---|---|
| `bridge_planning` | LLM 生成多步推理计划 |
| `experiment` | 生成并执行 Python 实验代码 |
| `lean_proof` | 构建并验证 Lean 4 形式证明 |
| `plausible_reasoning` | 合情推理（类比、归纳） |
| `analogy` | 类比推理，从已知领域迁移 |
| `specialize` | 问题特化/泛化 |
| `decompose` | 子问题分解 |
| `knowledge_retrieval` | 从超图中检索相关知识 |

## 工作流程

1. 确认用户要探索的问题，在超图中创建目标节点
2. 根据问题复杂度设置 `MCTSConfig`（简单问题 10-20 轮，复杂问题 30-50 轮）
3. 调用 `run_discovery()` 启动迭代探索
4. 检查 `result.target_belief_final` 判断是否达到满意的置信度
5. 如果 `result.best_bridge_plan` 不为空，展示最优推理路径

## 验证脚本

```bash
python .cursor/skills/dz-discovery/scripts/validate.py
```
