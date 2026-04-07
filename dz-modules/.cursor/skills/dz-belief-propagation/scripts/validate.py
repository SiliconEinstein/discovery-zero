#!/usr/bin/env python3
"""Validate dz-belief-propagation skill: imports, graph ops, BP execution."""
import sys

errors: list[str] = []


def check(label: str, fn):
    try:
        fn()
        print(f"  [PASS] {label}")
    except Exception as e:
        errors.append(f"{label}: {e}")
        print(f"  [FAIL] {label}: {e}")


print("=== dz-belief-propagation validation ===\n")

# --- Package imports ---
print("1. Package imports")
check("import dz_hypergraph", lambda: __import__("dz_hypergraph"))

# --- Graph creation and node operations ---
print("\n2. Graph operations")


def check_graph_roundtrip():
    import json
    from dz_hypergraph import create_graph, save_graph, load_graph
    from dz_hypergraph.models import Node

    g = create_graph()
    n = Node(
        id="test_node_1",
        statement="2 + 2 = 4",
        state="unverified",
        belief=0.5,
    )
    g.nodes[n.id] = n
    assert len(g.nodes) == 1

    import tempfile, pathlib
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        tmp = pathlib.Path(f.name)
    save_graph(g, tmp)
    g2 = load_graph(tmp)
    assert "test_node_1" in g2.nodes
    assert abs(g2.nodes["test_node_1"].belief - 0.5) < 1e-9
    tmp.unlink()


check("graph create → save → load roundtrip", check_graph_roundtrip)

# --- BP API ---
print("\n3. Belief Propagation API")


def check_propagate_beliefs_signature():
    from dz_hypergraph import propagate_beliefs
    import inspect
    sig = inspect.signature(propagate_beliefs)
    params = set(sig.parameters.keys())
    assert "graph" in params, f"Missing 'graph' param, got {params}"


def check_propagate_verification_signals():
    from dz_hypergraph.inference import propagate_verification_signals
    assert callable(propagate_verification_signals)


def check_signal_accumulator():
    from dz_hypergraph.inference import SignalAccumulator
    assert callable(SignalAccumulator)


check("propagate_beliefs signature", check_propagate_beliefs_signature)
check("propagate_verification_signals callable", check_propagate_verification_signals)
check("SignalAccumulator class", check_signal_accumulator)

# --- BP on a small graph ---
print("\n4. BP execution on trivial graph")


def check_bp_runs():
    from dz_hypergraph import create_graph, propagate_beliefs
    from dz_hypergraph.models import Node, Hyperedge, Module

    g = create_graph()
    g.nodes["a"] = Node(id="a", statement="premise A", state="unverified", belief=0.9)
    g.nodes["b"] = Node(id="b", statement="conclusion B", state="unverified", belief=0.5)
    g.edges["e1"] = Hyperedge(
        id="e1", premise_ids=["a"], conclusion_id="b",
        module=Module.PLAUSIBLE, steps=["a implies b"],
        edge_type="heuristic", confidence=0.8,
    )
    iters = propagate_beliefs(g, max_iterations=10, damping=0.5, tol=1e-4)
    assert isinstance(iters, int) and iters >= 0, f"Expected int >= 0, got {iters}"
    assert g.nodes["b"].belief >= 0.0


check("BP converges on 2-node graph", check_bp_runs)

# --- Belief gap analysis ---
print("\n5. Belief gap analysis")


def check_belief_gaps():
    from dz_hypergraph import create_graph, analyze_belief_gaps
    from dz_hypergraph.models import Node, Hyperedge, Module

    g = create_graph()
    g.nodes["p1"] = Node(id="p1", statement="weak premise", state="unverified", belief=0.2)
    g.nodes["p2"] = Node(id="p2", statement="strong premise", state="unverified", belief=0.9)
    g.nodes["c"] = Node(id="c", statement="conclusion", state="unverified", belief=0.5)
    g.edges["e1"] = Hyperedge(id="e1", premise_ids=["p1"], conclusion_id="c", module=Module.PLAUSIBLE, steps=["p1 implies c"], edge_type="heuristic", confidence=0.7)
    g.edges["e2"] = Hyperedge(id="e2", premise_ids=["p2"], conclusion_id="c", module=Module.PLAUSIBLE, steps=["p2 implies c"], edge_type="heuristic", confidence=0.7)
    gaps = analyze_belief_gaps(g, target_node_id="c", top_k=3)
    assert isinstance(gaps, list)


check("analyze_belief_gaps returns list", check_belief_gaps)

# --- Config ---
print("\n6. Configuration")


def check_config():
    from dz_hypergraph.config import CONFIG
    assert hasattr(CONFIG, "bp_backend")
    assert hasattr(CONFIG, "bp_max_iterations")
    assert hasattr(CONFIG, "bp_damping")
    assert hasattr(CONFIG, "bp_tolerance")
    assert hasattr(CONFIG, "bp_incremental")


check("ZeroConfig BP fields exist", check_config)

# --- Summary ---
print(f"\n{'=' * 40}")
if errors:
    print(f"FAILED: {len(errors)} check(s)")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("ALL CHECKS PASSED")
    sys.exit(0)
