from __future__ import annotations

from discovery_zero.config import CONFIG
from discovery_zero.graph.models import HyperGraph
from discovery_zero.graph.semantic_dedup import find_semantic_match, resolve_node_by_statement


def test_find_semantic_match_skips_llm_when_no_coarse_candidates(monkeypatch):
    graph = HyperGraph()
    node = graph.add_node("A finite group has identity.", belief=0.5, prior=0.5)

    def _should_not_call_llm(*args, **kwargs):
        raise AssertionError("LLM should not be called when coarse filter has no candidates")

    monkeypatch.setattr("discovery_zero.graph.semantic_dedup.chat_completion", _should_not_call_llm)

    match = find_semantic_match(
        graph,
        "Quantum Hall conductance is quantized.",
        max_candidates=8,
        jaccard_threshold=0.15,
    )
    assert match is None
    assert node.id in graph.nodes


def test_find_semantic_match_returns_yes_candidate(monkeypatch):
    graph = HyperGraph()
    target = graph.add_node(
        "The Fermi-Hubbard Hamiltonian on a D-dimensional lattice defines Green's function dynamics.",
        belief=0.5,
        prior=0.5,
    )
    graph.add_node("A compact operator has discrete spectrum.", belief=0.5, prior=0.5)

    def _mock_llm(*args, **kwargs):
        return {
            "choices": [
                {
                    "message": {"role": "assistant", "content": "YES"},
                    "finish_reason": "stop",
                }
            ]
        }

    monkeypatch.setattr("discovery_zero.graph.semantic_dedup.chat_completion", _mock_llm)

    match = find_semantic_match(
        graph,
        "The Fermi-Hubbard model on a D-dimensional lattice determines the same Green's function behavior.",
        max_candidates=8,
        jaccard_threshold=0.1,
    )
    assert match == target.id


def test_resolve_node_by_statement_respects_semantic_toggle(monkeypatch):
    graph = HyperGraph()
    node = graph.add_node("Theorem: every finite field has prime power order.", belief=0.5, prior=0.5)

    monkeypatch.setattr(CONFIG, "semantic_dedup_enabled", False, raising=False)
    monkeypatch.setattr("discovery_zero.graph.semantic_dedup.find_semantic_match", lambda *args, **kwargs: node.id)
    assert resolve_node_by_statement(
        graph,
        "Every finite field has order p^n for some prime p.",
        semantic=True,
    ) is None

    monkeypatch.setattr(CONFIG, "semantic_dedup_enabled", True, raising=False)
    assert (
        resolve_node_by_statement(
            graph,
            "Every finite field has order p^n for some prime p.",
            semantic=True,
        )
        == node.id
    )
