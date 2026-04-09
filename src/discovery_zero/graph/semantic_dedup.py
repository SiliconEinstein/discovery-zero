from __future__ import annotations

import logging
import re
import unicodedata
from typing import Optional

from discovery_zero.config import CONFIG
from discovery_zero.graph.models import HyperGraph
from discovery_zero.tools.llm import chat_completion, extract_text_content

logger = logging.getLogger(__name__)

_TOKEN_RE = re.compile(r"[^\W_]+|[^\w\s]", re.UNICODE)
_SEMANTIC_DEDUP_PROMPT = """You are a strict mathematical proposition comparator.

Proposition A:
{statement_a}

Proposition B:
{statement_b}

Are A and B expressing the EXACT SAME mathematical proposition (possibly with different wording, notation, or level of detail)?

Rules:
- Two propositions are the same ONLY if they make the same mathematical claim.
- If one is strictly more general or more specific than the other, answer NO.
- If they concern different objects, variables, or conditions, answer NO.
- When in doubt, answer NO.

Answer with exactly one word: YES or NO.
"""


def _tokenize_math_aware(statement: str) -> set[str]:
    normalized = unicodedata.normalize("NFKC", statement or "").casefold()
    return {tok for tok in _TOKEN_RE.findall(normalized) if tok.strip()}


def _jaccard_similarity(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def find_semantic_match(
    graph: HyperGraph,
    statement: str,
    *,
    model: str | None = None,
    max_candidates: int = 8,
    jaccard_threshold: float = 0.15,
) -> str | None:
    """Find an existing node with semantically equivalent proposition text."""
    text = (statement or "").strip()
    if not text:
        return None

    query_tokens = _tokenize_math_aware(text)
    if not query_tokens:
        return None

    if max_candidates <= 0:
        return None

    coarse_candidates: list[tuple[float, str, str]] = []
    for node_id, node in graph.nodes.items():
        candidate_tokens = _tokenize_math_aware(node.statement)
        score = _jaccard_similarity(query_tokens, candidate_tokens)
        if score >= jaccard_threshold:
            coarse_candidates.append((score, node_id, node.statement))

    if not coarse_candidates:
        return None

    coarse_candidates.sort(key=lambda x: x[0], reverse=True)
    effective_model = (model or CONFIG.semantic_dedup_model or "").strip() or None

    for _score, node_id, candidate_statement in coarse_candidates[:max_candidates]:
        prompt = _SEMANTIC_DEDUP_PROMPT.format(
            statement_a=text,
            statement_b=candidate_statement,
        )
        try:
            response = chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model=effective_model,
                temperature=0.0,
                stream=False,
                max_output_tokens=5,
            )
            verdict = extract_text_content(response).strip().upper()
            if verdict.startswith("YES"):
                return node_id
        except Exception as exc:
            logger.warning("Semantic dedup judge failed for node %s: %s", node_id, exc)
            continue

    return None


def resolve_node_by_statement(
    graph: HyperGraph,
    statement: str,
    *,
    semantic: bool = True,
    model: Optional[str] = None,
) -> str | None:
    """Try exact/canonical match first, then semantic match if enabled."""
    matches = graph.find_node_ids_by_statement(statement)
    if matches:
        return matches[0]
    if not semantic or not CONFIG.semantic_dedup_enabled:
        return None
    return find_semantic_match(
        graph,
        statement,
        model=model or CONFIG.semantic_dedup_model,
        max_candidates=int(CONFIG.semantic_dedup_max_candidates),
        jaccard_threshold=float(CONFIG.semantic_dedup_jaccard_threshold),
    )
