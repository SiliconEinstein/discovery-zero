import pytest
from discovery_zero.models import Node, Hyperedge, HyperGraph, Module


class TestNode:
    def test_create_node(self):
        node = Node(statement="For all triangles, the angle sum is 180 degrees")
        assert node.statement == "For all triangles, the angle sum is 180 degrees"
        assert node.belief == 0.0
        assert node.id is not None

    def test_create_axiom_node(self):
        node = Node(statement="Two points determine a line", belief=1.0)
        assert node.belief == 1.0

    def test_node_ids_are_unique(self):
        n1 = Node(statement="A")
        n2 = Node(statement="B")
        assert n1.id != n2.id


class TestHyperedge:
    def test_create_hyperedge(self):
        edge = Hyperedge(
            premise_ids=["n1", "n2"],
            conclusion_id="n3",
            module=Module.PLAUSIBLE,
            steps=["step 1", "step 2"],
            confidence=0.6,
        )
        assert edge.module == Module.PLAUSIBLE
        assert edge.confidence == 0.6
        assert len(edge.premise_ids) == 2

    def test_confidence_clamped(self):
        edge = Hyperedge(
            premise_ids=["n1"],
            conclusion_id="n2",
            module=Module.EXPERIMENT,
            steps=[],
            confidence=1.5,
        )
        assert edge.confidence == 1.0


class TestHyperGraph:
    def test_add_node(self):
        g = HyperGraph()
        node = g.add_node("Two points determine a line", belief=1.0)
        assert node.id in g.nodes
        assert g.nodes[node.id].statement == "Two points determine a line"

    def test_add_hyperedge(self):
        g = HyperGraph()
        n1 = g.add_node("premise 1", belief=1.0)
        n2 = g.add_node("premise 2", belief=1.0)
        n3 = g.add_node("conclusion")
        edge = g.add_hyperedge(
            premise_ids=[n1.id, n2.id],
            conclusion_id=n3.id,
            module=Module.PLAUSIBLE,
            steps=["reasoning step"],
            confidence=0.5,
        )
        assert edge.id in g.edges
        assert edge.id in g.get_edges_to(n3.id)

    def test_add_hyperedge_invalid_node(self):
        g = HyperGraph()
        with pytest.raises(ValueError, match="not found"):
            g.add_hyperedge(
                premise_ids=["nonexistent"],
                conclusion_id="also_nonexistent",
                module=Module.PLAUSIBLE,
                steps=[],
                confidence=0.5,
            )

    def test_get_edges_to(self):
        g = HyperGraph()
        n1 = g.add_node("A", belief=1.0)
        n2 = g.add_node("B")
        e1 = g.add_hyperedge([n1.id], n2.id, Module.PLAUSIBLE, ["step"], 0.5)
        e2 = g.add_hyperedge([n1.id], n2.id, Module.EXPERIMENT, ["code"], 0.9)
        edges_to_b = g.get_edges_to(n2.id)
        assert len(edges_to_b) == 2

    def test_get_edges_from(self):
        g = HyperGraph()
        n1 = g.add_node("A", belief=1.0)
        n2 = g.add_node("B")
        n3 = g.add_node("C")
        g.add_hyperedge([n1.id], n2.id, Module.PLAUSIBLE, [], 0.5)
        g.add_hyperedge([n1.id], n3.id, Module.PLAUSIBLE, [], 0.5)
        edges_from_a = g.get_edges_from(n1.id)
        assert len(edges_from_a) == 2

    def test_summary(self):
        g = HyperGraph()
        g.add_node("A", belief=1.0)
        g.add_node("B")
        summary = g.summary()
        assert summary["num_nodes"] == 2
        assert summary["num_edges"] == 0
