"""Bayesian belief propagation on the reasoning hypergraph."""

from discovery_zero.models import HyperGraph


def _edge_belief(graph: HyperGraph, edge_id: str) -> float:
    edge = graph.edges[edge_id]
    if not edge.premise_ids:
        return edge.confidence
    premise_beliefs = [graph.nodes[pid].belief for pid in edge.premise_ids]
    return edge.confidence * min(premise_beliefs)


def _combine_independent(beliefs: list[float]) -> float:
    if not beliefs:
        return 0.0
    prob_all_wrong = 1.0
    for b in beliefs:
        prob_all_wrong *= (1.0 - b)
    return 1.0 - prob_all_wrong


def propagate_beliefs(graph: HyperGraph, max_iterations: int = 20, tol: float = 1e-6) -> int:
    for iteration in range(max_iterations):
        max_change = 0.0
        for nid, node in graph.nodes.items():
            if node.belief == 1.0:
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
