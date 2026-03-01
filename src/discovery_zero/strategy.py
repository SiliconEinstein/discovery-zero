"""Exploration strategy: value-uncertainty trade-off and module selection."""

from discovery_zero.models import HyperGraph, Module


def _node_value(graph: HyperGraph, node_id: str) -> float:
    incoming = len(graph.get_edges_to(node_id))
    outgoing = len(graph.get_edges_from(node_id))
    return 1.0 + 0.3 * incoming + 0.5 * outgoing


def rank_nodes(graph: HyperGraph) -> list[tuple[str, float]]:
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
    belief = graph.nodes[node_id].belief
    if belief < 0.4:
        return Module.PLAUSIBLE
    elif belief < 0.8:
        return Module.EXPERIMENT
    else:
        return Module.LEAN
