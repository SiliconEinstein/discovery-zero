---
name: dz-verify-reasoning
description: >-
  对 LLM 推理输出进行 Claim 提取和多路径验证（Python 实验 / Lean 形式证明 / LLM 评判），
  并将验证结果写回推理超图更新置信度。当用户要求验证推理过程、检查数学证明、
  提取并验证断言、或对 LLM 输出进行事实核查时使用此技能。
---

# 推理验证技能 (dz-verify-reasoning)

对 LLM 产生的自然语言推理进行结构化验证：提取断言 → 分类 → 多路径验证 → 结果回注超图。

## 前置条件

```bash
pip install dz-verify dz-hypergraph
```

需要设置环境变量 `LITELLM_PROXY_API_BASE` 和 `LITELLM_PROXY_API_KEY`（LLM 接口）。

## 核心 API

### 1. 仅提取 Claims（不验证）

```python
from dz_verify import extract_claims

claims = extract_claims(
    prose="由欧拉公式 e^(iπ) + 1 = 0，可得 cos(π) = -1...",
    context="复分析基础",
    source_memo_id="step_3",
)
for c in claims:
    print(f"[{c.claim_type.value}] {c.claim_text}")
```

返回 `list[Claim]`，每个 Claim 包含：
- `claim_text`: 断言文本
- `claim_type`: `quantitative`（可用代码验证）、`structural`（可用 Lean 验证）、`heuristic`（需 LLM 评判）
- `node_id`: 对应超图节点 ID

### 2. 提取 + 验证 + 写回超图

```python
from dz_hypergraph import create_graph, save_graph
from dz_verify import verify_claims

graph = create_graph()
summary = verify_claims(
    prose="对于 n > 2，x^n + y^n = z^n 无正整数解...",
    context="费马大定理相关讨论",
    graph=graph,
    source_memo_id="memo_1",
)

for r in summary.results:
    print(f"{r.claim.claim_text[:40]}... → {r.verdict}")

save_graph(graph, "verified_graph.json")
```

返回 `VerificationSummary`，包含：
- `claims`: 提取到的所有 Claim
- `results`: 每个 Claim 的验证结果（`verified` / `refuted` / `inconclusive`）

### 3. 自定义验证器

```python
from dz_verify.claim_verifier import ClaimVerifier
from dz_verify import verify_claims

verifier = ClaimVerifier()
summary = verify_claims(
    prose="...", context="...", graph=graph,
    source_memo_id="s1", claim_verifier=verifier,
)
```

## 验证路径说明

| Claim 类型 | 验证方式 | 说明 |
|---|---|---|
| `quantitative` | Python 沙箱实验 | 生成代码执行并检查 `passed` 字段 |
| `structural` | Lean 4 形式证明 | 构建 Lean 证明，编译验证 |
| `heuristic` | LLM Judge | 由另一次 LLM 调用评判合理性 |

## 工作流程

1. 获取用户要验证的推理文本
2. 调用 `verify_claims()` 执行完整管线
3. 检查 `summary.results` 中每个断言的验证结果
4. 如果有 `refuted` 的断言，向用户报告哪些推理步骤存在问题
5. 如果需要更新超图置信度，随后调用 `propagate_beliefs(graph)`

## 验证脚本

运行以下脚本确认环境配置正确：

```bash
python .cursor/skills/dz-verify-reasoning/scripts/validate.py
```
