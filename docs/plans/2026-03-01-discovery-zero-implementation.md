# Discovery Zero Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a self-directed mathematical discovery system powered by LLM + Lean + numerical experimentation, organized around a reasoning hypergraph with Bayesian belief propagation.

**Architecture:** A Python package (`discovery_zero`) provides the core infrastructure: hypergraph data model, persistence, Bayesian inference, and exploration strategy, exposed via CLI. Four Claude Code skills (plausible reasoning, experiment, lean proof, judge) guide the LLM agent through different reasoning modes. An orchestration skill ties it all together into a continuous exploration loop. The agent framework (Claude Code / OpenCode) handles shell interaction, file management, and execution.

**Tech Stack:** Python 3.11+, Pydantic v2 (data models + serialization), Typer (CLI), pytest (testing), JSON (persistence), Lean 4 + Mathlib (formal verification), Claude Code skills (`.skill.md` files)

---

## Phase 1: Project Foundation

### Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `src/discovery_zero/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `.gitignore`
- Create: `CLAUDE.md`

**Step 1: Initialize git repo**

Run: `cd /Users/kunchen/project/geometry_zero && git init`
Expected: `Initialized empty Git repository`

**Step 2: Create project structure**

```
geometry_zero/
├── pyproject.toml
├── CLAUDE.md
├── .gitignore
├── src/
│   └── discovery_zero/
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   └── conftest.py
├── skills/
│   └── (empty, skills added later)
└── docs/
    └── plans/
        └── (existing design doc)
```

`pyproject.toml`:
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "discovery-zero"
version = "0.1.0"
description = "Self-directed mathematical discovery via reasoning hypergraph"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.0",
    "typer>=0.9",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov",
]

[project.scripts]
dz = "discovery_zero.cli:app"

[tool.hatch.build.targets.wheel]
packages = ["src/discovery_zero"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

`src/discovery_zero/__init__.py`:
```python
"""Discovery Zero: Self-directed mathematical discovery via reasoning hypergraph."""
```

`tests/__init__.py`: empty file

`tests/conftest.py`:
```python
import pytest
from pathlib import Path
import tempfile


@pytest.fixture
def tmp_graph_dir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)
```

`.gitignore`:
```
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/
dist/
build/
.venv/
*.db
.DS_Store
```

`CLAUDE.md`:
```markdown
# Discovery Zero

Self-directed mathematical discovery system via reasoning hypergraph.

## Commands

- Install: `pip install -e ".[dev]"`
- Test: `pytest`
- CLI: `dz --help`

## Architecture

- `src/discovery_zero/` - Core Python package
- `skills/` - Claude Code skills (`.skill.md` files)
- `docs/plans/` - Design and implementation docs

## Key concepts

- **Hypergraph**: Nodes are propositions, hyperedges are reasoning steps
- **Hyperedge format**: `{premises, steps, conclusion, module, confidence}`
- **Three modules**: plausible reasoning, experiment, lean proof
- **Judge**: LLM-as-judge assigns confidence to each hyperedge
- **Belief propagation**: Bayesian inference over the hypergraph
```

**Step 3: Install project in dev mode**

Run: `cd /Users/kunchen/project/geometry_zero && python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"`
Expected: Successfully installed discovery-zero

**Step 4: Verify pytest runs (no tests yet)**

Run: `cd /Users/kunchen/project/geometry_zero && source .venv/bin/activate && pytest`
Expected: `no tests ran` or `0 items collected`

**Step 5: Commit**

```bash
git add pyproject.toml CLAUDE.md .gitignore src/ tests/ docs/
git commit -m "feat: initialize discovery-zero project scaffolding"
```

---

### Task 2: Hypergraph Data Model

**Files:**
- Create: `src/discovery_zero/models.py`
- Create: `tests/test_models.py`

**Step 1: Write failing tests for Node and Hyperedge**

`tests/test_models.py`:
```python
import pytest
from discovery_zero.models import Node, Hyperedge, HyperGraph, Module


class TestNode:
    def test_create_node(self):
        node = Node(statement="For all triangles, the angle sum is 180 degrees")
        assert node.statement == "For all triangles, the angle sum is 180 degrees"
        assert node.belief == 0.0
        assert node.id is not None

    def test_create_axiom_node(self):
        node = Node(statement="Two points determine a line", belief=1.0)
        assert node.belief == 1.0

    def test_node_ids_are_unique(self):
        n1 = Node(statement="A")
        n2 = Node(statement="B")
        assert n1.id != n2.id


class TestHyperedge:
    def test_create_hyperedge(self):
        edge = Hyperedge(
            premise_ids=["n1", "n2"],
            conclusion_id="n3",
            module=Module.PLAUSIBLE,
            steps=["step 1", "step 2"],
            confidence=0.6,
        )
        assert edge.module == Module.PLAUSIBLE
        assert edge.confidence == 0.6
        assert len(edge.premise_ids) == 2

    def test_confidence_clamped(self):
        edge = Hyperedge(
            premise_ids=["n1"],
            conclusion_id="n2",
            module=Module.EXPERIMENT,
            steps=[],
            confidence=1.5,
        )
        assert edge.confidence == 1.0


class TestHyperGraph:
    def test_add_node(self):
        g = HyperGraph()
        node = g.add_node("Two points determine a line", belief=1.0)
        assert node.id in g.nodes
        assert g.nodes[node.id].statement == "Two points determine a line"

    def test_add_hyperedge(self):
        g = HyperGraph()
        n1 = g.add_node("premise 1", belief=1.0)
        n2 = g.add_node("premise 2", belief=1.0)
        n3 = g.add_node("conclusion")
        edge = g.add_hyperedge(
            premise_ids=[n1.id, n2.id],
            conclusion_id=n3.id,
            module=Module.PLAUSIBLE,
            steps=["reasoning step"],
            confidence=0.5,
        )
        assert edge.id in g.edges
        assert n3.id in g.get_edges_to(n3.id)

    def test_add_hyperedge_invalid_node(self):
        g = HyperGraph()
        with pytest.raises(ValueError, match="not found"):
            g.add_hyperedge(
                premise_ids=["nonexistent"],
                conclusion_id="also_nonexistent",
                module=Module.PLAUSIBLE,
                steps=[],
                confidence=0.5,
            )

    def test_get_edges_to(self):
        g = HyperGraph()
        n1 = g.add_node("A", belief=1.0)
        n2 = g.add_node("B")
        e1 = g.add_hyperedge([n1.id], n2.id, Module.PLAUSIBLE, ["step"], 0.5)
        e2 = g.add_hyperedge([n1.id], n2.id, Module.EXPERIMENT, ["code"], 0.9)
        edges_to_b = g.get_edges_to(n2.id)
        assert len(edges_to_b) == 2

    def test_get_edges_from(self):
        g = HyperGraph()
        n1 = g.add_node("A", belief=1.0)
        n2 = g.add_node("B")
        n3 = g.add_node("C")
        g.add_hyperedge([n1.id], n2.id, Module.PLAUSIBLE, [], 0.5)
        g.add_hyperedge([n1.id], n3.id, Module.PLAUSIBLE, [], 0.5)
        edges_from_a = g.get_edges_from(n1.id)
        assert len(edges_from_a) == 2

    def test_summary(self):
        g = HyperGraph()
        g.add_node("A", belief=1.0)
        g.add_node("B")
        summary = g.summary()
        assert summary["num_nodes"] == 2
        assert summary["num_edges"] == 0
```

**Step 2: Run tests to verify they fail**

Run: `cd /Users/kunchen/project/geometry_zero && source .venv/bin/activate && pytest tests/test_models.py -v`
Expected: FAIL (ModuleNotFoundError)

**Step 3: Implement models**

`src/discovery_zero/models.py`:
```python
"""Core data model: Node, Hyperedge, HyperGraph."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Module(str, Enum):
    PLAUSIBLE = "plausible"
    EXPERIMENT = "experiment"
    LEAN = "lean"


class Node(BaseModel):
    """A proposition node in the reasoning hypergraph."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    statement: str
    formal_statement: Optional[str] = None
    belief: float = 0.0
    domain: Optional[str] = None
    discovered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("belief")
    @classmethod
    def clamp_belief(cls, v: float) -> float:
        return max(0.0, min(1.0, v))


class Hyperedge(BaseModel):
    """A reasoning step: premises -> conclusion with confidence."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    premise_ids: list[str]
    conclusion_id: str
    module: Module
    steps: list[str]
    confidence: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("confidence")
    @classmethod
    def clamp_confidence(cls, v: float) -> float:
        return max(0.0, min(1.0, v))


class HyperGraph(BaseModel):
    """The reasoning hypergraph: nodes (propositions) + edges (reasoning steps)."""

    nodes: dict[str, Node] = Field(default_factory=dict)
    edges: dict[str, Hyperedge] = Field(default_factory=dict)

    def add_node(
        self,
        statement: str,
        belief: float = 0.0,
        formal_statement: str | None = None,
        domain: str | None = None,
    ) -> Node:
        node = Node(
            statement=statement,
            belief=belief,
            formal_statement=formal_statement,
            domain=domain,
        )
        self.nodes[node.id] = node
        return node

    def add_hyperedge(
        self,
        premise_ids: list[str],
        conclusion_id: str,
        module: Module,
        steps: list[str],
        confidence: float,
    ) -> Hyperedge:
        for nid in premise_ids + [conclusion_id]:
            if nid not in self.nodes:
                raise ValueError(f"Node '{nid}' not found in hypergraph")
        edge = Hyperedge(
            premise_ids=premise_ids,
            conclusion_id=conclusion_id,
            module=module,
            steps=steps,
            confidence=confidence,
        )
        self.edges[edge.id] = edge
        return edge

    def get_edges_to(self, node_id: str) -> list[str]:
        return [eid for eid, e in self.edges.items() if e.conclusion_id == node_id]

    def get_edges_from(self, node_id: str) -> list[str]:
        return [eid for eid, e in self.edges.items() if node_id in e.premise_ids]

    def summary(self) -> dict:
        return {
            "num_nodes": len(self.nodes),
            "num_edges": len(self.edges),
            "num_axioms": sum(1 for n in self.nodes.values() if n.belief == 1.0),
            "num_proven": sum(
                1 for n in self.nodes.values() if n.belief >= 0.99 and n.belief < 1.0
            ),
        }
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/kunchen/project/geometry_zero && source .venv/bin/activate && pytest tests/test_models.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add src/discovery_zero/models.py tests/test_models.py
git commit -m "feat: add hypergraph data model (Node, Hyperedge, HyperGraph)"
```

---

### Task 3: Persistence (JSON save/load + CLI)

**Files:**
- Create: `src/discovery_zero/persistence.py`
- Create: `src/discovery_zero/cli.py`
- Create: `tests/test_persistence.py`
- Create: `tests/test_cli.py`

**Step 1: Write failing tests for persistence**

`tests/test_persistence.py`:
```python
from pathlib import Path

from discovery_zero.models import HyperGraph, Module
from discovery_zero.persistence import save_graph, load_graph


class TestPersistence:
    def test_save_and_load_empty(self, tmp_graph_dir):
        path = tmp_graph_dir / "graph.json"
        g = HyperGraph()
        save_graph(g, path)
        loaded = load_graph(path)
        assert loaded.summary()["num_nodes"] == 0

    def test_save_and_load_with_data(self, tmp_graph_dir):
        path = tmp_graph_dir / "graph.json"
        g = HyperGraph()
        n1 = g.add_node("axiom A", belief=1.0)
        n2 = g.add_node("conjecture B")
        g.add_hyperedge([n1.id], n2.id, Module.PLAUSIBLE, ["reasoning"], 0.6)
        save_graph(g, path)
        loaded = load_graph(path)
        assert loaded.summary()["num_nodes"] == 2
        assert loaded.summary()["num_edges"] == 1
        assert loaded.nodes[n1.id].statement == "axiom A"
        assert loaded.nodes[n1.id].belief == 1.0

    def test_load_nonexistent_returns_empty(self, tmp_graph_dir):
        path = tmp_graph_dir / "nonexistent.json"
        g = load_graph(path)
        assert g.summary()["num_nodes"] == 0
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_persistence.py -v`
Expected: FAIL (ImportError)

**Step 3: Implement persistence**

`src/discovery_zero/persistence.py`:
```python
"""JSON persistence for the reasoning hypergraph."""

from pathlib import Path

from discovery_zero.models import HyperGraph

DEFAULT_GRAPH_PATH = Path("./discovery_zero_graph.json")


def save_graph(graph: HyperGraph, path: Path = DEFAULT_GRAPH_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(graph.model_dump_json(indent=2))


def load_graph(path: Path = DEFAULT_GRAPH_PATH) -> HyperGraph:
    if not path.exists():
        return HyperGraph()
    return HyperGraph.model_validate_json(path.read_text())
```

**Step 4: Run persistence tests**

Run: `pytest tests/test_persistence.py -v`
Expected: All PASS

**Step 5: Write CLI tests**

`tests/test_cli.py`:
```python
from typer.testing import CliRunner

from discovery_zero.cli import app

runner = CliRunner()


class TestCLI:
    def test_init(self, tmp_graph_dir):
        path = tmp_graph_dir / "graph.json"
        result = runner.invoke(app, ["init", "--path", str(path)])
        assert result.exit_code == 0
        assert path.exists()

    def test_summary_empty(self, tmp_graph_dir):
        path = tmp_graph_dir / "graph.json"
        runner.invoke(app, ["init", "--path", str(path)])
        result = runner.invoke(app, ["summary", "--path", str(path)])
        assert result.exit_code == 0
        assert "0 nodes" in result.stdout

    def test_add_node(self, tmp_graph_dir):
        path = tmp_graph_dir / "graph.json"
        runner.invoke(app, ["init", "--path", str(path)])
        result = runner.invoke(
            app, ["add-node", "--path", str(path),
                  "--statement", "Two points determine a line",
                  "--belief", "1.0"]
        )
        assert result.exit_code == 0
        assert "Added node" in result.stdout

    def test_show_nodes(self, tmp_graph_dir):
        path = tmp_graph_dir / "graph.json"
        runner.invoke(app, ["init", "--path", str(path)])
        runner.invoke(
            app, ["add-node", "--path", str(path),
                  "--statement", "Axiom 1", "--belief", "1.0"]
        )
        result = runner.invoke(app, ["show", "--path", str(path)])
        assert result.exit_code == 0
        assert "Axiom 1" in result.stdout
```

**Step 6: Implement CLI**

`src/discovery_zero/cli.py`:
```python
"""CLI for managing the Discovery Zero hypergraph."""

from pathlib import Path
from typing import Optional

import typer

from discovery_zero.models import HyperGraph, Module
from discovery_zero.persistence import save_graph, load_graph, DEFAULT_GRAPH_PATH

app = typer.Typer(help="Discovery Zero: reasoning hypergraph manager")


@app.command()
def init(path: Path = typer.Option(DEFAULT_GRAPH_PATH, help="Graph file path")):
    """Initialize an empty hypergraph."""
    g = HyperGraph()
    save_graph(g, path)
    typer.echo(f"Initialized empty hypergraph at {path}")


@app.command()
def summary(path: Path = typer.Option(DEFAULT_GRAPH_PATH, help="Graph file path")):
    """Show hypergraph summary."""
    g = load_graph(path)
    s = g.summary()
    typer.echo(f"{s['num_nodes']} nodes, {s['num_edges']} edges, "
               f"{s['num_axioms']} axioms, {s['num_proven']} proven")


@app.command()
def add_node(
    statement: str = typer.Option(..., help="Proposition statement"),
    belief: float = typer.Option(0.0, help="Initial belief (1.0 for axioms)"),
    domain: Optional[str] = typer.Option(None, help="Mathematical domain"),
    path: Path = typer.Option(DEFAULT_GRAPH_PATH, help="Graph file path"),
):
    """Add a proposition node to the hypergraph."""
    g = load_graph(path)
    node = g.add_node(statement=statement, belief=belief, domain=domain)
    save_graph(g, path)
    typer.echo(f"Added node {node.id}: {statement}")


@app.command()
def add_edge(
    premises: str = typer.Option(..., help="Comma-separated premise node IDs"),
    conclusion: str = typer.Option(..., help="Conclusion node ID"),
    module: Module = typer.Option(..., help="Module: plausible/experiment/lean"),
    confidence: float = typer.Option(..., help="Confidence score"),
    steps: str = typer.Option("", help="Semicolon-separated reasoning steps"),
    path: Path = typer.Option(DEFAULT_GRAPH_PATH, help="Graph file path"),
):
    """Add a reasoning hyperedge."""
    g = load_graph(path)
    premise_ids = [p.strip() for p in premises.split(",")]
    step_list = [s.strip() for s in steps.split(";") if s.strip()]
    edge = g.add_hyperedge(premise_ids, conclusion, module, step_list, confidence)
    save_graph(g, path)
    typer.echo(f"Added edge {edge.id}: [{premises}] -> {conclusion} "
               f"({module.value}, conf={confidence})")


@app.command()
def show(
    path: Path = typer.Option(DEFAULT_GRAPH_PATH, help="Graph file path"),
):
    """Show all nodes and edges in the hypergraph."""
    g = load_graph(path)
    if not g.nodes:
        typer.echo("Empty hypergraph.")
        return
    typer.echo("--- Nodes ---")
    for nid, node in g.nodes.items():
        typer.echo(f"  [{nid}] (belief={node.belief:.2f}) {node.statement}")
    if g.edges:
        typer.echo("--- Edges ---")
        for eid, edge in g.edges.items():
            premise_stmts = [g.nodes[p].statement[:30] for p in edge.premise_ids]
            concl_stmt = g.nodes[edge.conclusion_id].statement[:30]
            typer.echo(f"  [{eid}] {premise_stmts} -> {concl_stmt} "
                       f"({edge.module.value}, conf={edge.confidence:.2f})")


if __name__ == "__main__":
    app()
```

**Step 7: Run all tests**

Run: `pytest tests/ -v`
Expected: All PASS

**Step 8: Verify CLI works end-to-end**

Run: `cd /Users/kunchen/project/geometry_zero && source .venv/bin/activate && dz --help`
Expected: Shows help text with available commands

**Step 9: Commit**

```bash
git add src/discovery_zero/persistence.py src/discovery_zero/cli.py tests/test_persistence.py tests/test_cli.py
git commit -m "feat: add JSON persistence and CLI for hypergraph management"
```

---

## Phase 2: Intelligence Layer

### Task 4: Bayesian Belief Propagation

**Files:**
- Create: `src/discovery_zero/inference.py`
- Create: `tests/test_inference.py`

**Step 1: Write failing tests**

`tests/test_inference.py`:
```python
import pytest
from discovery_zero.models import HyperGraph, Module
from discovery_zero.inference import propagate_beliefs


class TestBeliefPropagation:
    def test_axiom_stays_at_1(self):
        g = HyperGraph()
        n = g.add_node("axiom", belief=1.0)
        propagate_beliefs(g)
        assert g.nodes[n.id].belief == 1.0

    def test_single_edge_propagation(self):
        g = HyperGraph()
        n1 = g.add_node("axiom", belief=1.0)
        n2 = g.add_node("conclusion", belief=0.0)
        g.add_hyperedge([n1.id], n2.id, Module.PLAUSIBLE, [], 0.7)
        propagate_beliefs(g)
        assert abs(g.nodes[n2.id].belief - 0.7) < 0.01

    def test_multi_premise_edge(self):
        """Confidence * min(premise beliefs) as simple model."""
        g = HyperGraph()
        n1 = g.add_node("axiom 1", belief=1.0)
        n2 = g.add_node("axiom 2", belief=0.8)
        n3 = g.add_node("conclusion", belief=0.0)
        g.add_hyperedge([n1.id, n2.id], n3.id, Module.PLAUSIBLE, [], 0.6)
        propagate_beliefs(g)
        # belief(n3) = confidence * min(belief(n1), belief(n2)) = 0.6 * 0.8 = 0.48
        assert abs(g.nodes[n3.id].belief - 0.48) < 0.01

    def test_multi_path_enhancement(self):
        """Multiple independent edges to the same conclusion increase belief."""
        g = HyperGraph()
        n1 = g.add_node("axiom", belief=1.0)
        n2 = g.add_node("conclusion", belief=0.0)
        g.add_hyperedge([n1.id], n2.id, Module.PLAUSIBLE, [], 0.5)
        g.add_hyperedge([n1.id], n2.id, Module.EXPERIMENT, [], 0.9)
        propagate_beliefs(g)
        # Combined: 1 - (1-0.5)*(1-0.9) = 1 - 0.05 = 0.95
        assert g.nodes[n2.id].belief > 0.9

    def test_lean_proof_collapses_belief(self):
        g = HyperGraph()
        n1 = g.add_node("axiom", belief=1.0)
        n2 = g.add_node("conjecture", belief=0.3)
        g.add_hyperedge([n1.id], n2.id, Module.LEAN, [], 0.99)
        propagate_beliefs(g)
        assert g.nodes[n2.id].belief >= 0.99

    def test_chain_propagation(self):
        """A -> B -> C should propagate through the chain."""
        g = HyperGraph()
        a = g.add_node("axiom", belief=1.0)
        b = g.add_node("lemma", belief=0.0)
        c = g.add_node("theorem", belief=0.0)
        g.add_hyperedge([a.id], b.id, Module.LEAN, [], 0.99)
        g.add_hyperedge([b.id], c.id, Module.PLAUSIBLE, [], 0.6)
        propagate_beliefs(g)
        assert g.nodes[b.id].belief >= 0.99
        assert g.nodes[c.id].belief > 0.5

    def test_no_edges_belief_unchanged(self):
        g = HyperGraph()
        n = g.add_node("isolated conjecture", belief=0.3)
        propagate_beliefs(g)
        assert g.nodes[n.id].belief == 0.3
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_inference.py -v`
Expected: FAIL (ImportError)

**Step 3: Implement belief propagation**

`src/discovery_zero/inference.py`:
```python
"""Bayesian belief propagation on the reasoning hypergraph."""

from discovery_zero.models import HyperGraph


def _edge_belief(graph: HyperGraph, edge_id: str) -> float:
    """Compute the belief contribution of a single hyperedge.

    belief_contribution = confidence * product(premise beliefs)
    Using min instead of product for robustness with uncertain premises.
    """
    edge = graph.edges[edge_id]
    if not edge.premise_ids:
        return edge.confidence
    premise_beliefs = [graph.nodes[pid].belief for pid in edge.premise_ids]
    return edge.confidence * min(premise_beliefs)


def _combine_independent(beliefs: list[float]) -> float:
    """Combine multiple independent evidence paths.

    P(at least one path correct) = 1 - product(1 - belief_i)
    """
    if not beliefs:
        return 0.0
    prob_all_wrong = 1.0
    for b in beliefs:
        prob_all_wrong *= (1.0 - b)
    return 1.0 - prob_all_wrong


def propagate_beliefs(graph: HyperGraph, max_iterations: int = 20, tol: float = 1e-6) -> int:
    """Propagate beliefs through the hypergraph until convergence.

    Returns the number of iterations performed.
    """
    for iteration in range(max_iterations):
        max_change = 0.0
        for nid, node in graph.nodes.items():
            if node.belief == 1.0:  # axioms are fixed
                continue
            incoming_edges = graph.get_edges_to(nid)
            if not incoming_edges:
                continue
            edge_beliefs = [_edge_belief(graph, eid) for eid in incoming_edges]
            new_belief = _combine_independent(edge_beliefs)
            new_belief = max(0.0, min(1.0, new_belief))
            change = abs(new_belief - node.belief)
            max_change = max(max_change, change)
            node.belief = new_belief
        if max_change < tol:
            return iteration + 1
    return max_iterations
```

**Step 4: Run tests**

Run: `pytest tests/test_inference.py -v`
Expected: All PASS

**Step 5: Add `propagate` CLI command**

Add to `src/discovery_zero/cli.py`:
```python
from discovery_zero.inference import propagate_beliefs

@app.command()
def propagate(
    path: Path = typer.Option(DEFAULT_GRAPH_PATH, help="Graph file path"),
):
    """Run belief propagation on the hypergraph."""
    g = load_graph(path)
    iterations = propagate_beliefs(g)
    save_graph(g, path)
    typer.echo(f"Belief propagation converged in {iterations} iterations")
    for nid, node in g.nodes.items():
        typer.echo(f"  [{nid}] belief={node.belief:.4f} {node.statement[:50]}")
```

**Step 6: Run all tests**

Run: `pytest tests/ -v`
Expected: All PASS

**Step 7: Commit**

```bash
git add src/discovery_zero/inference.py tests/test_inference.py src/discovery_zero/cli.py
git commit -m "feat: add Bayesian belief propagation on reasoning hypergraph"
```

---

### Task 5: Exploration Strategy

**Files:**
- Create: `src/discovery_zero/strategy.py`
- Create: `tests/test_strategy.py`

**Step 1: Write failing tests**

`tests/test_strategy.py`:
```python
from discovery_zero.models import HyperGraph, Module
from discovery_zero.strategy import rank_nodes, suggest_module


class TestRankNodes:
    def test_high_value_low_belief_ranks_first(self):
        g = HyperGraph()
        n1 = g.add_node("proven theorem", belief=0.99)
        n2 = g.add_node("interesting conjecture", belief=0.3)
        ranked = rank_nodes(g)
        assert ranked[0][0] == n2.id  # n2 should rank higher

    def test_axioms_excluded(self):
        g = HyperGraph()
        g.add_node("axiom", belief=1.0)
        n2 = g.add_node("conjecture", belief=0.2)
        ranked = rank_nodes(g)
        assert len(ranked) == 1
        assert ranked[0][0] == n2.id

    def test_empty_graph(self):
        g = HyperGraph()
        ranked = rank_nodes(g)
        assert ranked == []


class TestSuggestModule:
    def test_low_belief_suggests_plausible(self):
        g = HyperGraph()
        n = g.add_node("wild guess", belief=0.1)
        module = suggest_module(g, n.id)
        assert module == Module.PLAUSIBLE

    def test_medium_belief_suggests_experiment(self):
        g = HyperGraph()
        n = g.add_node("promising conjecture", belief=0.5)
        module = suggest_module(g, n.id)
        assert module == Module.EXPERIMENT

    def test_high_belief_suggests_lean(self):
        g = HyperGraph()
        n = g.add_node("well-supported conjecture", belief=0.85)
        module = suggest_module(g, n.id)
        assert module == Module.LEAN
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_strategy.py -v`
Expected: FAIL

**Step 3: Implement exploration strategy**

`src/discovery_zero/strategy.py`:
```python
"""Exploration strategy: value-uncertainty trade-off and module selection."""

from discovery_zero.models import HyperGraph, Module


def _node_value(graph: HyperGraph, node_id: str) -> float:
    """Estimate the value of a node.

    Heuristic: nodes with more incoming edges (multiple evidence paths)
    are more "interesting" because multiple reasoning paths converge on them.
    Nodes with outgoing edges (used as premises) have high reuse potential.
    """
    incoming = len(graph.get_edges_to(node_id))
    outgoing = len(graph.get_edges_from(node_id))
    # Base value 1.0 + bonus for connectivity
    return 1.0 + 0.3 * incoming + 0.5 * outgoing


def rank_nodes(graph: HyperGraph) -> list[tuple[str, float]]:
    """Rank nodes by priority: value * (1 - belief).

    Returns list of (node_id, priority) sorted descending.
    Excludes axioms (belief == 1.0).
    """
    ranked = []
    for nid, node in graph.nodes.items():
        if node.belief == 1.0:
            continue
        value = _node_value(graph, nid)
        priority = value * (1.0 - node.belief)
        ranked.append((nid, priority))
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked


def suggest_module(graph: HyperGraph, node_id: str) -> Module:
    """Suggest which module to use for a given node based on its current belief."""
    belief = graph.nodes[node_id].belief
    if belief < 0.4:
        return Module.PLAUSIBLE
    elif belief < 0.8:
        return Module.EXPERIMENT
    else:
        return Module.LEAN
```

**Step 4: Run tests**

Run: `pytest tests/test_strategy.py -v`
Expected: All PASS

**Step 5: Add `next` CLI command**

Add to `src/discovery_zero/cli.py`:
```python
from discovery_zero.strategy import rank_nodes, suggest_module

@app.command(name="next")
def next_action(
    path: Path = typer.Option(DEFAULT_GRAPH_PATH, help="Graph file path"),
    top_n: int = typer.Option(5, help="Number of suggestions to show"),
):
    """Suggest the next exploration action based on value-uncertainty trade-off."""
    g = load_graph(path)
    ranked = rank_nodes(g)
    if not ranked:
        typer.echo("No nodes to explore. Add conjectures or run plausible reasoning.")
        return
    typer.echo("--- Suggested next actions ---")
    for nid, priority in ranked[:top_n]:
        node = g.nodes[nid]
        module = suggest_module(g, nid)
        typer.echo(
            f"  [{nid}] priority={priority:.2f} belief={node.belief:.2f} "
            f"-> use {module.value}\n"
            f"    {node.statement[:70]}"
        )
```

**Step 6: Run all tests**

Run: `pytest tests/ -v`
Expected: All PASS

**Step 7: Commit**

```bash
git add src/discovery_zero/strategy.py tests/test_strategy.py src/discovery_zero/cli.py
git commit -m "feat: add exploration strategy with value-uncertainty ranking"
```

---

## Phase 3: Skills

### Task 6: Judge Skill

**Files:**
- Create: `skills/judge.skill.md`

**Step 1: Write the Judge skill**

`skills/judge.skill.md`:
```markdown
---
name: judge
description: Evaluate a reasoning hyperedge and assign a confidence score (conditional probability)
---

# Judge Skill

You are evaluating a reasoning step for reliability. Your job is to estimate:

> P(conclusion is correct | all premises are correct)

## Input

You will receive a hyperedge in this format:

- **Premises**: A list of propositions assumed to be true
- **Steps**: The reasoning chain (natural language, code, or Lean proof)
- **Conclusion**: The derived proposition
- **Module**: Which module produced this (plausible / experiment / lean)

## Evaluation Process

1. **Read each premise carefully.** Assume they are all true.
2. **Trace through the steps.** For each step, ask:
   - Does this step logically follow from the previous state?
   - Are there hidden assumptions not stated in the premises?
   - Could there be edge cases or counterexamples?
3. **Assess the conclusion.** Does it actually follow from the steps?
4. **Consider the module type:**
   - `plausible`: Be skeptical. Look for logical gaps, unjustified leaps, unstated assumptions. Typical range: 0.3-0.7
   - `experiment`: Check if the experimental design is sound. Are there enough test cases? Could numerical precision be an issue? Typical range: 0.7-0.95
   - `lean`: If Lean accepted the proof, confidence should be ~0.99. Only lower if the formalization might not match the intended statement.

## Output Format

You MUST respond with a JSON block:

```json
{
  "confidence": 0.XX,
  "reasoning": "Brief explanation of why you assigned this score",
  "concerns": ["list of specific concerns, if any"],
  "suggestion": "optional suggestion for improving the reasoning"
}
```

## Calibration Guidelines

| Confidence | Meaning |
|---|---|
| 0.95-0.99 | Lean proof verified, or reasoning is airtight |
| 0.80-0.95 | Strong experimental evidence, or very solid reasoning |
| 0.60-0.80 | Reasonable argument with minor gaps |
| 0.40-0.60 | Plausible but significant uncertainty |
| 0.20-0.40 | Speculative, major logical gaps |
| 0.00-0.20 | Very likely wrong or unsupported |

## Important

- Be an independent evaluator. Do NOT rubber-stamp.
- If the reasoning is flawed, say so clearly and assign low confidence.
- A short, clear proof deserves high confidence. A long, hand-wavy argument deserves low confidence.
```

**Step 2: Commit**

```bash
git add skills/judge.skill.md
git commit -m "feat: add Judge skill for hyperedge confidence scoring"
```

---

### Task 7: Plausible Reasoning Skill

**Files:**
- Create: `skills/plausible_reasoning.skill.md`

**Step 1: Write the Plausible Reasoning skill**

`skills/plausible_reasoning.skill.md`:
```markdown
---
name: plausible-reasoning
description: Perform non-formal mathematical reasoning to generate conjectures and proof ideas
---

# Plausible Reasoning Skill

You are a creative mathematician exploring new ideas. Your goal is to use analogy, pattern recognition, induction, and intuition to generate conjectures or proof strategies.

## Input

You will receive:
- **Direction**: What area or question to explore
- **Context**: Relevant nodes from the hypergraph (known facts, axioms, existing conjectures)

## Process

1. **Survey the context.** What do you know? What patterns do you see?
2. **Generate ideas.** Use these techniques:
   - **Analogy**: "This reminds me of X, so maybe Y also holds"
   - **Generalization**: "This works for triangles, does it work for n-gons?"
   - **Specialization**: "What happens in the simplest case?"
   - **Dualization**: "What if we swap the roles of X and Y?"
   - **Induction**: "It holds for n=1,2,3,4... probably for all n"
3. **State your conjecture clearly.** Be precise about what you claim.
4. **Sketch a proof idea** if you have one.

## Output Format

You MUST produce output in this exact JSON format:

```json
{
  "premises": [
    {"id": "existing_node_id", "statement": "premise statement"},
    {"id": null, "statement": "new premise to add as node"}
  ],
  "steps": [
    "Step 1: reasoning step in natural language",
    "Step 2: ...",
    "Step 3: ..."
  ],
  "conclusion": {
    "statement": "The precise conjecture or result",
    "formal_statement": "Optional: Lean-style formal statement"
  },
  "module": "plausible",
  "domain": "geometry"
}
```

If a premise `id` is `null`, it means this is a new proposition that should be added to the hypergraph as a new node.

## Guidelines

- **Be creative but honest.** If you're guessing, say so in the steps.
- **One conjecture per output.** If you have multiple ideas, produce multiple outputs.
- **State assumptions explicitly.** Don't hide conditions.
- **Prefer simple, precise statements** over vague, grandiose ones.
```

**Step 2: Commit**

```bash
git add skills/plausible_reasoning.skill.md
git commit -m "feat: add Plausible Reasoning skill for conjecture generation"
```

---

### Task 8: Experiment Skill

**Files:**
- Create: `skills/experiment.skill.md`

**Step 1: Write the Experiment skill**

`skills/experiment.skill.md`:
```markdown
---
name: experiment
description: Design and run computational experiments to test mathematical conjectures
---

# Experiment Skill

You are an experimental mathematician. Your job is to test conjectures by writing code that evaluates them on concrete instances.

## Input

You will receive:
- **Conjecture**: The statement to test
- **Context**: Definitions and relevant known facts

## Process

1. **Understand the conjecture.** What are the free variables? What is being claimed?
2. **Write a test script** in Python that:
   - Generates random instances of the mathematical objects (random points, random integers, random matrices, etc.)
   - Evaluates whether the conjecture holds for each instance
   - Runs at least 100 random trials
   - Reports any counterexamples immediately
   - Reports the success rate and maximum numerical error
3. **Execute the script** using the shell.
4. **Interpret the results.**

## Output Format

You MUST produce output in this exact JSON format:

```json
{
  "premises": [
    {"id": "existing_node_id", "statement": "premise statement"}
  ],
  "steps": [
    "# Python code used for testing\nimport numpy as np\n...",
    "Results: 1000/1000 trials passed, max error = 1.2e-14",
    "No counterexamples found"
  ],
  "conclusion": {
    "statement": "Experimental evidence strongly supports: [conjecture]",
    "formal_statement": null
  },
  "module": "experiment",
  "domain": "geometry"
}
```

## Guidelines

- **Use random instances, not cherry-picked ones.** The test is only valuable if instances are general.
- **Watch for numerical precision.** Use a tolerance (e.g., 1e-10) for floating-point comparisons.
- **If a counterexample is found, report it immediately.** The conjecture is FALSE.
- **Test edge cases** (degenerate triangles, zero, negative numbers, etc.) in addition to random cases.
- **Keep the code simple and readable.** This is an experiment, not production code.

## Domain-Specific Tips

**Geometry:** Assign random coordinates to free points. Compute distances, angles, slopes, areas. Compare with tolerance.

**Number theory:** Test on random integers in a range. Test small cases exhaustively. Test large cases randomly.

**Linear algebra:** Generate random matrices. Compute eigenvalues, determinants, ranks. Compare.

**Combinatorics:** Enumerate small cases exhaustively. Sample larger cases randomly.
```

**Step 2: Commit**

```bash
git add skills/experiment.skill.md
git commit -m "feat: add Experiment skill for computational conjecture testing"
```

---

### Task 9: Lean Proof Skill

**Files:**
- Create: `skills/lean_proof.skill.md`

**Step 1: Write the Lean Proof skill**

`skills/lean_proof.skill.md`:
```markdown
---
name: lean-proof
description: Write and verify formal proofs in Lean 4 using Mathlib
---

# Lean Proof Skill

You are a formal verification specialist. Your job is to write a Lean 4 proof for a given conjecture and verify it compiles.

## Input

You will receive:
- **Conjecture**: The statement to prove (natural language + optional formal statement)
- **Context**: Relevant axioms and previously proven theorems

## Process

1. **Formalize the statement** in Lean 4 syntax if not already provided.
2. **Plan the proof.** Think about which Mathlib lemmas you might need.
3. **Write the Lean proof** in a `.lean` file.
4. **Run `lake build`** to verify the proof compiles.
5. **If it fails**, read the error, fix the proof, and try again. Iterate up to 5 times.
6. **If it succeeds**, extract the theorem statement.

## Lean File Template

```lean
import Mathlib

-- Statement of the theorem
theorem discovery_<name> <params> : <statement> := by
  <tactics>
```

## Output Format

On success, produce:

```json
{
  "premises": [
    {"id": "existing_node_id", "statement": "premise used"}
  ],
  "steps": [
    "theorem discovery_midline_parallel ...",
    "(full Lean proof code)"
  ],
  "conclusion": {
    "statement": "Formally verified: [theorem statement in natural language]",
    "formal_statement": "theorem discovery_midline_parallel ..."
  },
  "module": "lean",
  "domain": "geometry"
}
```

On failure after 5 attempts, produce:

```json
{
  "status": "failed",
  "last_error": "error message from Lean",
  "attempts": 5,
  "suggestion": "what might help (different approach, missing lemma, etc.)"
}
```

## Guidelines

- **Start with `import Mathlib`** to get access to the full library.
- **Use `exact?`, `apply?`, `simp?`** tactics to search for applicable lemmas.
- **Prefer short, tactic-based proofs** over term-mode proofs.
- **If you get stuck**, consider whether the statement needs reformulation.
- **Check that the Lean statement actually matches the intended conjecture** - a proof of the wrong statement is worthless.

## Prerequisites

A Lean 4 project must be set up in the workspace with Mathlib as a dependency. If not present, create one:

```bash
# In the project root
lake new lean_workspace math
cd lean_workspace
echo 'require mathlib from git "https://github.com/leanprover-community/mathlib4"' >> lakefile.lean
lake update
lake build
```
```

**Step 2: Commit**

```bash
git add skills/lean_proof.skill.md
git commit -m "feat: add Lean Proof skill for formal verification"
```

---

## Phase 4: Integration

### Task 10: Hyperedge Ingestion from Skill Output

**Files:**
- Create: `src/discovery_zero/ingest.py`
- Create: `tests/test_ingest.py`

This module parses the structured JSON output from skills and updates the hypergraph.

**Step 1: Write failing tests**

`tests/test_ingest.py`:
```python
import json
import pytest
from discovery_zero.models import HyperGraph, Module
from discovery_zero.ingest import ingest_skill_output


class TestIngest:
    def test_ingest_plausible_with_existing_premises(self):
        g = HyperGraph()
        n1 = g.add_node("triangle ABC", belief=1.0)
        n2 = g.add_node("M is midpoint of AB", belief=1.0)
        output = {
            "premises": [
                {"id": n1.id, "statement": "triangle ABC"},
                {"id": n2.id, "statement": "M is midpoint of AB"},
            ],
            "steps": ["By similarity..."],
            "conclusion": {
                "statement": "MN is parallel to BC",
                "formal_statement": None,
            },
            "module": "plausible",
            "domain": "geometry",
        }
        edge = ingest_skill_output(g, output)
        assert edge.module == Module.PLAUSIBLE
        assert edge.conclusion_id in g.nodes
        assert g.nodes[edge.conclusion_id].statement == "MN is parallel to BC"

    def test_ingest_creates_new_premise_nodes(self):
        g = HyperGraph()
        output = {
            "premises": [
                {"id": None, "statement": "Let X be a prime number"},
            ],
            "steps": ["By Fermat's little theorem..."],
            "conclusion": {
                "statement": "a^X = a mod X",
            },
            "module": "plausible",
            "domain": "number_theory",
        }
        edge = ingest_skill_output(g, output)
        assert len(g.nodes) == 2  # 1 new premise + 1 conclusion

    def test_ingest_experiment(self):
        g = HyperGraph()
        n1 = g.add_node("conjecture: sum of angles = 180", belief=0.5)
        output = {
            "premises": [
                {"id": n1.id, "statement": "conjecture: sum of angles = 180"},
            ],
            "steps": ["code...", "1000/1000 passed"],
            "conclusion": {
                "statement": "Experimental evidence supports: sum of angles = 180",
            },
            "module": "experiment",
        }
        edge = ingest_skill_output(g, output)
        assert edge.module == Module.EXPERIMENT

    def test_ingest_with_confidence(self):
        g = HyperGraph()
        output = {
            "premises": [],
            "steps": [],
            "conclusion": {"statement": "trivial"},
            "module": "plausible",
            "confidence": 0.42,
        }
        edge = ingest_skill_output(g, output)
        assert edge.confidence == 0.42

    def test_ingest_default_confidence(self):
        g = HyperGraph()
        output = {
            "premises": [],
            "steps": [],
            "conclusion": {"statement": "something"},
            "module": "plausible",
        }
        edge = ingest_skill_output(g, output)
        # Default confidence based on module
        assert edge.confidence == 0.5  # default for plausible
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_ingest.py -v`
Expected: FAIL

**Step 3: Implement ingestion**

`src/discovery_zero/ingest.py`:
```python
"""Ingest structured skill output into the reasoning hypergraph."""

from discovery_zero.models import HyperGraph, Hyperedge, Module

DEFAULT_CONFIDENCE = {
    Module.PLAUSIBLE: 0.5,
    Module.EXPERIMENT: 0.85,
    Module.LEAN: 0.99,
}


def ingest_skill_output(graph: HyperGraph, output: dict) -> Hyperedge:
    """Parse skill output JSON and add nodes/edges to the hypergraph.

    Returns the created Hyperedge.
    """
    module = Module(output["module"])

    # Resolve or create premise nodes
    premise_ids = []
    for p in output.get("premises", []):
        if p.get("id") and p["id"] in graph.nodes:
            premise_ids.append(p["id"])
        else:
            node = graph.add_node(
                statement=p["statement"],
                belief=1.0 if module == Module.LEAN else 0.5,
                domain=output.get("domain"),
            )
            premise_ids.append(node.id)

    # Create or find conclusion node
    conclusion = output["conclusion"]
    conclusion_statement = conclusion if isinstance(conclusion, str) else conclusion.get("statement", "")
    formal = None if isinstance(conclusion, str) else conclusion.get("formal_statement")

    # Check if a node with this exact statement already exists
    existing = [nid for nid, n in graph.nodes.items() if n.statement == conclusion_statement]
    if existing:
        conclusion_id = existing[0]
    else:
        conclusion_node = graph.add_node(
            statement=conclusion_statement,
            formal_statement=formal,
            domain=output.get("domain"),
        )
        conclusion_id = conclusion_node.id

    # Create hyperedge
    confidence = output.get("confidence", DEFAULT_CONFIDENCE[module])
    steps = output.get("steps", [])

    edge = graph.add_hyperedge(
        premise_ids=premise_ids,
        conclusion_id=conclusion_id,
        module=module,
        steps=steps,
        confidence=confidence,
    )
    return edge
```

**Step 4: Run tests**

Run: `pytest tests/test_ingest.py -v`
Expected: All PASS

**Step 5: Add `ingest` CLI command**

Add to `src/discovery_zero/cli.py`:
```python
import json
from discovery_zero.ingest import ingest_skill_output

@app.command()
def ingest(
    json_str: str = typer.Argument(..., help="JSON string of skill output"),
    path: Path = typer.Option(DEFAULT_GRAPH_PATH, help="Graph file path"),
):
    """Ingest a skill output (JSON) into the hypergraph."""
    g = load_graph(path)
    output = json.loads(json_str)
    edge = ingest_skill_output(g, output)
    save_graph(g, path)
    typer.echo(f"Ingested edge {edge.id} ({edge.module.value}, conf={edge.confidence:.2f})")
```

**Step 6: Run all tests**

Run: `pytest tests/ -v`
Expected: All PASS

**Step 7: Commit**

```bash
git add src/discovery_zero/ingest.py tests/test_ingest.py src/discovery_zero/cli.py
git commit -m "feat: add skill output ingestion into hypergraph"
```

---

### Task 11: Exploration Loop Orchestration Skill

**Files:**
- Create: `skills/exploration_loop.skill.md`

**Step 1: Write the orchestration skill**

`skills/exploration_loop.skill.md`:
```markdown
---
name: exploration-loop
description: Orchestrate the Discovery Zero exploration loop - continuously discover new mathematical knowledge
---

# Discovery Zero Exploration Loop

You are an autonomous mathematical discovery agent. You operate in a continuous loop, building a reasoning hypergraph of mathematical knowledge.

## Available Tools

You have access to these CLI commands and skills:

**CLI (via shell):**
- `dz summary --path <path>` - View hypergraph summary
- `dz show --path <path>` - View all nodes and edges
- `dz next --path <path>` - Get suggested next actions (ranked by priority)
- `dz propagate --path <path>` - Run belief propagation
- `dz ingest '<json>' --path <path>` - Add a skill output to the hypergraph

**Skills:**
- `/plausible-reasoning` - Generate conjectures via non-formal reasoning
- `/experiment` - Test conjectures with computational experiments
- `/lean-proof` - Formally verify conjectures in Lean 4
- `/judge` - Evaluate a reasoning step and assign confidence

## Exploration Loop

Repeat the following cycle:

### 1. Assess State

```bash
dz summary --path graph.json
dz next --path graph.json
```

Read the suggestions. Understand what the highest-priority targets are.

### 2. Choose Action

Based on the `next` output:
- If a node has **low belief and no evidence** -> use `/plausible-reasoning` to form initial conjectures
- If a node has **medium belief** -> use `/experiment` to test it computationally
- If a node has **high belief** -> use `/lean-proof` to formally verify
- If the graph is **empty or sparse** -> use `/plausible-reasoning` to explore a new area
- If you are **stuck** -> try a different domain or a different approach

### 3. Execute Skill

Invoke the chosen skill. The skill will produce structured JSON output.

### 4. Judge the Result

After each skill produces output, invoke `/judge` to evaluate the reasoning quality and assign a confidence score. Update the skill output JSON with the judge's confidence.

### 5. Ingest into Hypergraph

```bash
dz ingest '<skill_output_json>' --path graph.json
```

### 6. Propagate Beliefs

```bash
dz propagate --path graph.json
```

### 7. Repeat

Go back to step 1. Continue exploring.

## Startup: Seeding the Hypergraph

If the hypergraph is empty, start by seeding it with axioms. Choose a domain and add its foundational axioms:

**Example for Euclidean geometry:**
```bash
dz add-node --statement "Two distinct points determine a unique line" --belief 1.0 --domain geometry --path graph.json
dz add-node --statement "A line segment can be extended indefinitely" --belief 1.0 --domain geometry --path graph.json
dz add-node --statement "Given a point and a radius, a circle can be drawn" --belief 1.0 --domain geometry --path graph.json
dz add-node --statement "All right angles are equal" --belief 1.0 --domain geometry --path graph.json
dz add-node --statement "Parallel postulate: through a point not on a line, exactly one parallel exists" --belief 1.0 --domain geometry --path graph.json
```

Then start exploring with `/plausible-reasoning`.

## Key Principles

- **Be curious.** Don't just verify known results - try to discover new connections.
- **Be systematic.** Use the priority ranking to guide your effort.
- **Be honest.** If a conjecture fails an experiment, accept it and move on.
- **Build on discoveries.** Use newly proven theorems as premises for further exploration.
- **Diversify.** Don't get stuck in one sub-area. Explore broadly.
```

**Step 2: Commit**

```bash
git add skills/exploration_loop.skill.md
git commit -m "feat: add exploration loop orchestration skill"
```

---

### Task 12: End-to-End Smoke Test

**Files:**
- Create: `tests/test_e2e.py`

This test verifies the full pipeline works: create graph, add axioms, ingest skill outputs, propagate beliefs, rank nodes.

**Step 1: Write the end-to-end test**

`tests/test_e2e.py`:
```python
"""End-to-end smoke test for the Discovery Zero pipeline."""

from discovery_zero.models import HyperGraph, Module
from discovery_zero.ingest import ingest_skill_output
from discovery_zero.inference import propagate_beliefs
from discovery_zero.strategy import rank_nodes, suggest_module


def test_full_discovery_pipeline():
    """Simulate a mini discovery session:
    1. Seed with axioms
    2. Plausible reasoning produces a conjecture
    3. Experiment supports the conjecture
    4. Lean proof confirms it
    5. Belief propagation reflects the progression
    """
    g = HyperGraph()

    # Step 1: Seed axioms
    ax1 = g.add_node("Two points determine a line", belief=1.0, domain="geometry")
    ax2 = g.add_node("Midpoint divides segment into two equal parts", belief=1.0, domain="geometry")

    # Step 2: Plausible reasoning
    plausible_output = {
        "premises": [
            {"id": ax1.id, "statement": ax1.statement},
            {"id": ax2.id, "statement": ax2.statement},
        ],
        "steps": [
            "Consider triangle ABC with midpoints M, N of sides AB, AC",
            "By similarity of triangles AMN and ABC (ratio 1:2)",
            "MN should be parallel to BC and half its length",
        ],
        "conclusion": {
            "statement": "Triangle midline is parallel to the third side and half its length",
            "formal_statement": None,
        },
        "module": "plausible",
        "confidence": 0.55,
        "domain": "geometry",
    }
    e1 = ingest_skill_output(g, plausible_output)
    propagate_beliefs(g)

    conjecture_id = e1.conclusion_id
    assert g.nodes[conjecture_id].belief > 0.0
    assert g.nodes[conjecture_id].belief < 0.7

    # Should suggest experiment next
    assert suggest_module(g, conjecture_id) in (Module.PLAUSIBLE, Module.EXPERIMENT)

    # Step 3: Experiment
    experiment_output = {
        "premises": [
            {"id": conjecture_id, "statement": g.nodes[conjecture_id].statement},
        ],
        "steps": [
            "import numpy as np\n# 1000 random triangles tested",
            "Results: 1000/1000 passed, max error = 2.1e-15",
        ],
        "conclusion": {
            "statement": "Triangle midline is parallel to the third side and half its length",
        },
        "module": "experiment",
        "confidence": 0.93,
        "domain": "geometry",
    }
    ingest_skill_output(g, experiment_output)
    propagate_beliefs(g)

    assert g.nodes[conjecture_id].belief > 0.8

    # Should suggest Lean proof now
    assert suggest_module(g, conjecture_id) == Module.LEAN

    # Step 4: Lean proof
    lean_output = {
        "premises": [
            {"id": ax2.id, "statement": ax2.statement},
        ],
        "steps": [
            "theorem midline_parallel (A B C : Point) : ...",
            "(full lean proof)",
        ],
        "conclusion": {
            "statement": "Triangle midline is parallel to the third side and half its length",
            "formal_statement": "theorem midline_parallel ...",
        },
        "module": "lean",
        "confidence": 0.99,
        "domain": "geometry",
    }
    ingest_skill_output(g, lean_output)
    propagate_beliefs(g)

    # After Lean proof, belief should be ~1.0
    assert g.nodes[conjecture_id].belief >= 0.99

    # Summary check
    s = g.summary()
    assert s["num_nodes"] >= 3  # 2 axioms + 1 conjecture (now proven)
    assert s["num_edges"] >= 3  # plausible + experiment + lean


def test_multi_conjecture_ranking():
    """Test that the ranking correctly prioritizes high-value low-belief nodes."""
    g = HyperGraph()
    ax = g.add_node("axiom", belief=1.0)
    c1 = g.add_node("easy conjecture", belief=0.9)
    c2 = g.add_node("hard conjecture", belief=0.2)
    c3 = g.add_node("medium conjecture", belief=0.5)

    ranked = rank_nodes(g)
    ids = [r[0] for r in ranked]

    # c2 (lowest belief) should rank highest (most room for improvement)
    assert ids[0] == c2.id
```

**Step 2: Run the e2e test**

Run: `pytest tests/test_e2e.py -v`
Expected: All PASS

**Step 3: Run full test suite**

Run: `pytest tests/ -v --tb=short`
Expected: All tests PASS

**Step 4: Commit**

```bash
git add tests/test_e2e.py
git commit -m "test: add end-to-end smoke test for full discovery pipeline"
```

---

## Summary

| Phase | Task | What it builds |
|---|---|---|
| 1 | Task 1 | Project scaffolding, git, deps |
| 1 | Task 2 | Node, Hyperedge, HyperGraph data model |
| 1 | Task 3 | JSON persistence + CLI (init, show, add-node, add-edge) |
| 2 | Task 4 | Bayesian belief propagation |
| 2 | Task 5 | Exploration strategy (value-uncertainty ranking) |
| 3 | Task 6 | Judge skill |
| 3 | Task 7 | Plausible Reasoning skill |
| 3 | Task 8 | Experiment skill |
| 3 | Task 9 | Lean Proof skill |
| 4 | Task 10 | Skill output ingestion into hypergraph |
| 4 | Task 11 | Exploration loop orchestration skill |
| 4 | Task 12 | End-to-end smoke test |

After completing all tasks, the system is ready for its first real exploration session: seed with axioms, run the exploration loop skill, and start discovering mathematics.
