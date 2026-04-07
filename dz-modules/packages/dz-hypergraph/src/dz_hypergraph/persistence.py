"""JSON persistence for the reasoning hypergraph and Gaia IR artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dz_hypergraph.bridge import BridgeResult, bridge_to_gaia
from dz_hypergraph.models import HyperGraph

DEFAULT_GRAPH_PATH = Path("./discovery_zero_graph.json")


# ------------------------------------------------------------------ #
# Core save / load (Zero-native JSON)                                  #
# ------------------------------------------------------------------ #

def save_graph(graph: HyperGraph, path: Path = DEFAULT_GRAPH_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(graph.model_dump_json(indent=2))


def load_graph(path: Path = DEFAULT_GRAPH_PATH) -> HyperGraph:
    if not path.exists():
        return HyperGraph()
    return HyperGraph.model_validate_json(path.read_text())


def export_as_gaia_ir(
    graph: HyperGraph,
    *,
    namespace: str = "dz",
    package_name: str = "discovery_zero",
    warmstart: bool = False,
) -> BridgeResult:
    """Compile the hypergraph into real Gaia IR artifacts."""
    return bridge_to_gaia(
        graph,
        namespace=namespace,
        package_name=package_name,
        warmstart=warmstart,
    )


def save_gaia_artifacts(
    graph: HyperGraph,
    output_dir: Path,
    *,
    namespace: str = "dz",
    package_name: str = "discovery_zero",
    warmstart: bool = False,
    source_id: str = "dz_bridge",
) -> BridgeResult:
    """Write compiled Gaia artifacts to ``output_dir/.gaia``."""
    bridged = export_as_gaia_ir(
        graph,
        namespace=namespace,
        package_name=package_name,
        warmstart=warmstart,
    )
    gaia_dir = output_dir / ".gaia"
    gaia_dir.mkdir(parents=True, exist_ok=True)
    (gaia_dir / "ir.json").write_text(
        bridged.compiled.graph.model_dump_json(indent=2),
        encoding="utf-8",
    )
    (gaia_dir / "ir_hash").write_text(bridged.compiled.graph.ir_hash or "", encoding="utf-8")

    reviews_dir = gaia_dir / "reviews" / source_id
    reviews_dir.mkdir(parents=True, exist_ok=True)
    (reviews_dir / "parameterization.json").write_text(
        json.dumps(
            {
                "ir_hash": bridged.compiled.graph.ir_hash,
                "priors": bridged.node_priors,
                "strategy_params": bridged.strategy_params,
                "source_id": source_id,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (gaia_dir / "beliefs.json").write_text(
        json.dumps(
            {
                "ir_hash": bridged.compiled.graph.ir_hash,
                "beliefs": {
                    bridged.dz_id_to_qid[nid]: max(0.0, min(1.0, node.belief))
                    for nid, node in graph.nodes.items()
                    if nid in bridged.dz_id_to_qid
                },
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return bridged


def export_as_gaia_local_graph(
    graph: HyperGraph,
    package_name: str = "discovery_zero",
    version: str = "0.1.0",
):
    """Backward-compatible alias returning `(LocalCanonicalGraph, params_dict)`."""
    _ = version  # package version is produced by Gaia compiler.
    bridged = export_as_gaia_ir(graph, package_name=package_name)
    return bridged.compiled.graph, {
        "priors": bridged.node_priors,
        "strategy_params": bridged.strategy_params,
    }
