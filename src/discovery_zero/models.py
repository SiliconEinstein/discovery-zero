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
