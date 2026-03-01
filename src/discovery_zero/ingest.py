"""Ingest structured skill output into the reasoning hypergraph."""

from discovery_zero.models import HyperGraph, Hyperedge, Module

DEFAULT_CONFIDENCE = {
    Module.PLAUSIBLE: 0.5,
    Module.EXPERIMENT: 0.85,
    Module.LEAN: 0.99,
}


def ingest_skill_output(graph: HyperGraph, output: dict) -> Hyperedge:
    """Parse skill output JSON and add nodes/edges to the hypergraph."""
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
