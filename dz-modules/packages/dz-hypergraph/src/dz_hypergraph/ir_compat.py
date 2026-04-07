"""Compatibility IR models for legacy Zero->Gaia export paths.

These models preserve the old export schema used by Discovery Zero without
depending on removed legacy packages.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SourceRef(BaseModel):
    package: str
    version: str
    module: str
    knowledge_name: str


class LocalCanonicalNode(BaseModel):
    local_canonical_id: str
    package: str
    knowledge_type: str
    representative_content: str
    source_refs: list[SourceRef] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class FactorNode(BaseModel):
    factor_id: str
    type: str
    premises: list[str] = Field(default_factory=list)
    conclusion: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class LocalCanonicalGraph(BaseModel):
    package: str
    version: str
    knowledge_nodes: list[LocalCanonicalNode] = Field(default_factory=list)
    factor_nodes: list[FactorNode] = Field(default_factory=list)

    def graph_hash(self) -> str:
        payload = self.model_dump(mode="json")
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class FactorParams(BaseModel):
    conditional_probability: float = Field(ge=0.0, le=1.0)


class LocalParameterization(BaseModel):
    graph_hash: str
    node_priors: dict[str, float] = Field(default_factory=dict)
    factor_parameters: dict[str, FactorParams] = Field(default_factory=dict)


class BeliefSnapshot(BaseModel):
    knowledge_id: str
    version: int
    belief: float = Field(ge=0, le=1)
    bp_run_id: str
    computed_at: datetime
