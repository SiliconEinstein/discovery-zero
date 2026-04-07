#!/usr/bin/env python3
"""Validate dz-verify-reasoning skill: imports, class instantiation, API surface."""
import sys

errors: list[str] = []


def check(label: str, fn):
    try:
        fn()
        print(f"  [PASS] {label}")
    except Exception as e:
        errors.append(f"{label}: {e}")
        print(f"  [FAIL] {label}: {e}")


print("=== dz-verify-reasoning validation ===\n")

# --- Package imports ---
print("1. Package imports")
check("import dz_verify", lambda: __import__("dz_verify"))
check("import dz_hypergraph", lambda: __import__("dz_hypergraph"))

# --- Public API surface ---
print("\n2. Public API surface")


def check_extract_claims():
    from dz_verify import extract_claims
    import inspect
    sig = inspect.signature(extract_claims)
    required = {"prose", "context", "source_memo_id"}
    assert required.issubset(sig.parameters.keys()), f"Missing params: {required - set(sig.parameters.keys())}"


def check_verify_claims():
    from dz_verify import verify_claims
    import inspect
    sig = inspect.signature(verify_claims)
    required = {"prose", "context", "graph", "source_memo_id"}
    assert required.issubset(sig.parameters.keys()), f"Missing params: {required - set(sig.parameters.keys())}"


def check_verification_summary():
    from dz_verify import VerificationSummary
    assert hasattr(VerificationSummary, "__dataclass_fields__")
    fields = set(VerificationSummary.__dataclass_fields__.keys())
    assert {"claims", "results"}.issubset(fields), f"Missing fields: {{'claims', 'results'}} - {fields}"


def check_claim_pipeline():
    from dz_verify.claim_pipeline import ClaimPipeline
    p = ClaimPipeline()
    assert hasattr(p, "extract_claims")


def check_claim_verifier():
    from dz_verify.claim_verifier import ClaimVerifier, VerifiableClaim, ClaimVerificationResult
    v = ClaimVerifier()
    assert hasattr(v, "verify_claims")
    assert "claim_text" in VerifiableClaim.__dataclass_fields__


def check_continuation_verifier():
    from dz_verify.continuation_verifier import ContinuationVerifier
    assert hasattr(ContinuationVerifier, "verify_step") or hasattr(ContinuationVerifier, "verify_bridge_plan")


def check_lean_feedback():
    from dz_verify.lean_feedback import LeanFeedbackParser, StructuralClaimRouter
    assert callable(LeanFeedbackParser)
    assert callable(StructuralClaimRouter)


check("extract_claims signature", check_extract_claims)
check("verify_claims signature", check_verify_claims)
check("VerificationSummary fields", check_verification_summary)
check("ClaimPipeline instantiation", check_claim_pipeline)
check("ClaimVerifier instantiation", check_claim_verifier)
check("ContinuationVerifier class", check_continuation_verifier)
check("LeanFeedbackParser class", check_lean_feedback)

# --- Claim type enum ---
print("\n3. Claim types")


def check_claim_types():
    from dz_hypergraph.memo import ClaimType
    assert hasattr(ClaimType, "QUANTITATIVE")
    assert hasattr(ClaimType, "STRUCTURAL")
    assert hasattr(ClaimType, "HEURISTIC")


check("ClaimType enum values", check_claim_types)

# --- Graph integration ---
print("\n4. Graph integration")


def check_graph_create():
    from dz_hypergraph import create_graph
    g = create_graph()
    assert hasattr(g, "nodes")
    assert hasattr(g, "edges")
    return g


def check_ingest():
    from dz_hypergraph.ingest import ingest_verified_claim
    assert callable(ingest_verified_claim)


check("create_graph()", check_graph_create)
check("ingest_verified_claim callable", check_ingest)

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
