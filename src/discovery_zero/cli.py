"""CLI for managing the Discovery Zero hypergraph."""

from pathlib import Path
from typing import Optional

import typer

from discovery_zero.models import HyperGraph, Module
from discovery_zero.persistence import save_graph, load_graph, DEFAULT_GRAPH_PATH
from discovery_zero.inference import propagate_beliefs
from discovery_zero.strategy import rank_nodes, suggest_module

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


if __name__ == "__main__":
    app()
