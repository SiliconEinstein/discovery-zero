---
name: dz-belief-propagation
description: >-
  在推理超图上运行贝叶斯置信传播 (BP)，更新所有节点的置信度，识别推理链中的薄弱环节。
  当用户需要评估推理可信度、分析推理链薄弱点、运行 BP 推理、或在验证后更新置信度时使用此技能。
---

# 置信传播技能 (dz-belief-propagation)

在推理超图上执行贝叶斯置信传播 (Belief Propagation)，让验证结果和先验知识沿超图传播，自动更新所有命题的置信度。

## 前置条件

```bash
pip install dz-hypergraph
```

需要设置环境变量（如果使用 Gaia v2 后端）：
- `GAIA_API_BASE` — Gaia BP 服务地址（可选，默认使用本地 energy-based 推理）

## 核心 API

### 1. 置信传播

```python
from dz_hypergraph import load_graph, propagate_beliefs, save_graph

graph = load_graph("my_reasoning.json")
iterations = propagate_beliefs(
    graph,
    max_iterations=50,  # 最大迭代次数
    damping=0.5,        # 阻尼系数，防止振荡
    tol=1e-6,           # 收敛容差
)
print(f"BP 在 {iterations} 轮后收敛")
save_graph(graph, "my_reasoning.json")
```

### 2. 信念缺口分析

```python
from dz_hypergraph import load_graph, analyze_belief_gaps

graph = load_graph("my_reasoning.json")
gaps = analyze_belief_gaps(
    graph,
    target_node_id="final_answer",  # 目标节点
    top_k=5,                        # 返回前 k 个薄弱环节
)
for node_id, info_gain in gaps:
    node = graph.nodes[node_id]
    print(f"  {node.statement[:50]}... belief={node.belief:.3f} gain={info_gain:.3f}")
```

返回 `list[tuple[str, float]]`：每项为 `(node_id, information_gain)`，按信息增益降序排列。

### 3. 验证信号传播

```python
from dz_hypergraph.inference import propagate_verification_signals

propagate_verification_signals(graph)
```

将验证结果（verified/refuted）沿超图边传播，更新下游节点置信度。

### 4. 检查节点置信度

```python
from dz_hypergraph import load_graph

graph = load_graph("my_reasoning.json")
for nid, node in graph.nodes.items():
    print(f"[{node.belief:.3f}] {node.statement[:60]}...")
```

## 配置参数

| 环境变量 | 默认值 | 说明 |
|---|---|---|
| `DISCOVERY_ZERO_BP_BACKEND` | `gaia_v2` | BP 后端：`gaia_v2` / `energy` |
| `DISCOVERY_ZERO_BP_MAX_ITERATIONS` | `50` | 最大 BP 迭代次数 |
| `DISCOVERY_ZERO_BP_DAMPING` | `0.5` | 阻尼系数 |
| `DISCOVERY_ZERO_BP_TOLERANCE` | `1e-6` | 收敛容差 |
| `DISCOVERY_ZERO_BP_INCREMENTAL` | `true` | 增量 BP（仅传播受影响子图） |

## 工作流程

1. 加载或创建超图
2. 如果刚完成验证操作，先调用 `propagate_verification_signals(graph)` 传播验证结果
3. 调用 `propagate_beliefs(graph)` 执行完整 BP
4. 调用 `analyze_belief_gaps(graph, target_node_id, top_k)` 找出薄弱环节
5. 将结果报告给用户，建议针对低置信度节点补充论证

## 验证脚本

```bash
python .cursor/skills/dz-belief-propagation/scripts/validate.py
```
