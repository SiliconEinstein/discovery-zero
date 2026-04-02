"""BP v2 — belief propagation aligned with theory and Gaia IR (vendored).

Theory: docs/foundations/theory/06-factor-graphs.md, 07-belief-propagation.md

Eight factor types: six deterministic operators, SOFT_ENTAILMENT (↝ with p1,p2),
CONDITIONAL (full CPT). String variable IDs, Cromwell clamping, Junction Tree /
GBP / loopy BP / exact enumeration, InferenceEngine.

Note: Gaia IR lowering (lower_local_graph) lives in upstream gaia-bp only;
Discovery Zero builds FactorGraph via discovery_zero.graph.adapter_v2.
"""

from gaia_bp.factor_graph import CROMWELL_EPS, Factor, FactorGraph, FactorType
from gaia_bp.bp import BeliefPropagation, BPDiagnostics, BPResult
from gaia_bp.exact import comparison_table, exact_inference
from gaia_bp.engine import EngineConfig, InferenceEngine, InferenceResult
from gaia_bp.gbp import GeneralizedBeliefPropagation, detect_short_cycles
from gaia_bp.junction_tree import JunctionTreeInference, jt_treewidth

__all__ = [
    "BeliefPropagation",
    "BPDiagnostics",
    "BPResult",
    "CROMWELL_EPS",
    "EngineConfig",
    "Factor",
    "FactorGraph",
    "FactorType",
    "GeneralizedBeliefPropagation",
    "InferenceEngine",
    "InferenceResult",
    "JunctionTreeInference",
    "comparison_table",
    "detect_short_cycles",
    "exact_inference",
    "jt_treewidth",
]
