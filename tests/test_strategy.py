from discovery_zero.models import HyperGraph, Module
from discovery_zero.strategy import rank_nodes, suggest_module


class TestRankNodes:
    def test_high_value_low_belief_ranks_first(self):
        g = HyperGraph()
        n1 = g.add_node("proven theorem", belief=0.99)
        n2 = g.add_node("interesting conjecture", belief=0.3)
        ranked = rank_nodes(g)
        assert ranked[0][0] == n2.id

    def test_axioms_excluded(self):
        g = HyperGraph()
        g.add_node("axiom", belief=1.0)
        n2 = g.add_node("conjecture", belief=0.2)
        ranked = rank_nodes(g)
        assert len(ranked) == 1
        assert ranked[0][0] == n2.id

    def test_empty_graph(self):
        g = HyperGraph()
        ranked = rank_nodes(g)
        assert ranked == []


class TestSuggestModule:
    def test_low_belief_suggests_plausible(self):
        g = HyperGraph()
        n = g.add_node("wild guess", belief=0.1)
        module = suggest_module(g, n.id)
        assert module == Module.PLAUSIBLE

    def test_medium_belief_suggests_experiment(self):
        g = HyperGraph()
        n = g.add_node("promising conjecture", belief=0.5)
        module = suggest_module(g, n.id)
        assert module == Module.EXPERIMENT

    def test_high_belief_suggests_lean(self):
        g = HyperGraph()
        n = g.add_node("well-supported conjecture", belief=0.85)
        module = suggest_module(g, n.id)
        assert module == Module.LEAN
