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
