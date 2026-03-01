import json
import pytest
from discovery_zero.models import HyperGraph, Module
from discovery_zero.ingest import ingest_skill_output


class TestIngest:
    def test_ingest_plausible_with_existing_premises(self):
        g = HyperGraph()
        n1 = g.add_node("triangle ABC", belief=1.0)
        n2 = g.add_node("M is midpoint of AB", belief=1.0)
        output = {
            "premises": [
                {"id": n1.id, "statement": "triangle ABC"},
                {"id": n2.id, "statement": "M is midpoint of AB"},
            ],
            "steps": ["By similarity..."],
            "conclusion": {
                "statement": "MN is parallel to BC",
                "formal_statement": None,
            },
            "module": "plausible",
            "domain": "geometry",
        }
        edge = ingest_skill_output(g, output)
        assert edge.module == Module.PLAUSIBLE
        assert edge.conclusion_id in g.nodes
        assert g.nodes[edge.conclusion_id].statement == "MN is parallel to BC"

    def test_ingest_creates_new_premise_nodes(self):
        g = HyperGraph()
        output = {
            "premises": [
                {"id": None, "statement": "Let X be a prime number"},
            ],
            "steps": ["By Fermat's little theorem..."],
            "conclusion": {
                "statement": "a^X = a mod X",
            },
            "module": "plausible",
            "domain": "number_theory",
        }
        edge = ingest_skill_output(g, output)
        assert len(g.nodes) == 2  # 1 new premise + 1 conclusion

    def test_ingest_experiment(self):
        g = HyperGraph()
        n1 = g.add_node("conjecture: sum of angles = 180", belief=0.5)
        output = {
            "premises": [
                {"id": n1.id, "statement": "conjecture: sum of angles = 180"},
            ],
            "steps": ["code...", "1000/1000 passed"],
            "conclusion": {
                "statement": "Experimental evidence supports: sum of angles = 180",
            },
            "module": "experiment",
        }
        edge = ingest_skill_output(g, output)
        assert edge.module == Module.EXPERIMENT

    def test_ingest_with_confidence(self):
        g = HyperGraph()
        output = {
            "premises": [],
            "steps": [],
            "conclusion": {"statement": "trivial"},
            "module": "plausible",
            "confidence": 0.42,
        }
        edge = ingest_skill_output(g, output)
        assert edge.confidence == 0.42

    def test_ingest_default_confidence(self):
        g = HyperGraph()
        output = {
            "premises": [],
            "steps": [],
            "conclusion": {"statement": "something"},
            "module": "plausible",
        }
        edge = ingest_skill_output(g, output)
        assert edge.confidence == 0.5  # default for plausible
