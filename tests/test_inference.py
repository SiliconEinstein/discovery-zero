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
        g = HyperGraph()
        n1 = g.add_node("axiom 1", belief=1.0)
        n2 = g.add_node("axiom 2", belief=0.8)
        n3 = g.add_node("conclusion", belief=0.0)
        g.add_hyperedge([n1.id, n2.id], n3.id, Module.PLAUSIBLE, [], 0.6)
        propagate_beliefs(g)
        assert abs(g.nodes[n3.id].belief - 0.48) < 0.01

    def test_multi_path_enhancement(self):
        g = HyperGraph()
        n1 = g.add_node("axiom", belief=1.0)
        n2 = g.add_node("conclusion", belief=0.0)
        g.add_hyperedge([n1.id], n2.id, Module.PLAUSIBLE, [], 0.5)
        g.add_hyperedge([n1.id], n2.id, Module.EXPERIMENT, [], 0.9)
        propagate_beliefs(g)
        assert g.nodes[n2.id].belief > 0.9

    def test_lean_proof_collapses_belief(self):
        g = HyperGraph()
        n1 = g.add_node("axiom", belief=1.0)
        n2 = g.add_node("conjecture", belief=0.3)
        g.add_hyperedge([n1.id], n2.id, Module.LEAN, [], 0.99)
        propagate_beliefs(g)
        assert g.nodes[n2.id].belief >= 0.99

    def test_chain_propagation(self):
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
