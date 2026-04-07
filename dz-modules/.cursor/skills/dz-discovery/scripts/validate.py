#!/usr/bin/env python3
"""Validate dz-discovery skill: imports, MCTSConfig, engine instantiation."""
import sys

errors: list[str] = []


def check(label: str, fn):
    try:
        fn()
        print(f"  [PASS] {label}")
    except Exception as e:
        errors.append(f"{label}: {e}")
        print(f"  [FAIL] {label}: {e}")


print("=== dz-discovery validation ===\n")

# --- Package imports ---
print("1. Package imports")
check("import dz_engine", lambda: __import__("dz_engine"))
check("import dz_verify", lambda: __import__("dz_verify"))
check("import dz_hypergraph", lambda: __import__("dz_hypergraph"))

# --- High-level API ---
print("\n2. High-level API")


def check_run_discovery():
    from dz_engine import run_discovery
    import inspect
    sig = inspect.signature(run_discovery)
    params = set(sig.parameters.keys())
    required = {"graph_path", "target_node_id"}
    assert required.issubset(params), f"Missing params: {required - params}"


check("run_discovery signature", check_run_discovery)

# --- MCTSConfig ---
print("\n3. MCTSConfig")


def check_mcts_config():
    from dz_engine import MCTSConfig
    c = MCTSConfig()
    assert c.max_iterations == 30
    assert c.max_time_seconds == 14400.0
    assert c.c_puct == 1.4
    assert isinstance(c.enable_evolutionary_experiments, bool)
    assert isinstance(c.enable_continuation_verification, bool)
    assert isinstance(c.enable_retrieval, bool)
    assert isinstance(c.enable_problem_variants, bool)


def check_mcts_config_custom():
    from dz_engine import MCTSConfig
    c = MCTSConfig(max_iterations=10, max_time_seconds=60, c_puct=2.0)
    assert c.max_iterations == 10
    assert c.max_time_seconds == 60.0
    assert c.c_puct == 2.0


check("MCTSConfig defaults", check_mcts_config)
check("MCTSConfig custom values", check_mcts_config_custom)

# --- MCTSDiscoveryResult ---
print("\n4. MCTSDiscoveryResult")


def check_result_class():
    from dz_engine.mcts_engine import MCTSDiscoveryResult
    r = MCTSDiscoveryResult(
        success=False,
        iterations_completed=0,
        target_belief_initial=0.5,
        target_belief_final=0.5,
    )
    assert hasattr(r, "traces")
    assert hasattr(r, "best_bridge_plan")
    assert hasattr(r, "elapsed_ms")
    assert hasattr(r, "experiences")


check("MCTSDiscoveryResult instantiation", check_result_class)

# --- Engine class ---
print("\n5. MCTSDiscoveryEngine")


def check_engine_class():
    from dz_engine.mcts_engine import MCTSDiscoveryEngine, MCTSConfig
    import inspect
    sig = inspect.signature(MCTSDiscoveryEngine.__init__)
    params = set(sig.parameters.keys()) - {"self"}
    required = {"graph_path", "target_node_id", "config"}
    assert required.issubset(params), f"Missing: {required - params}"
    optional_expected = {
        "claim_verifier", "claim_pipeline", "model", "backend",
        "analogy_engine", "specialize_engine", "decompose_engine",
    }
    for p in optional_expected:
        assert p in params, f"Missing optional param: {p}"


check("MCTSDiscoveryEngine constructor", check_engine_class)

# --- Sub-engines ---
print("\n6. Sub-engines")


def check_sub(name, module, cls_name):
    mod = __import__(module, fromlist=[cls_name])
    cls = getattr(mod, cls_name)
    assert callable(cls), f"{cls_name} not callable"


check("AnalogyEngine", lambda: check_sub("analogy", "dz_engine.analogy", "AnalogyEngine"))
check("SpecializeEngine", lambda: check_sub("specialize", "dz_engine.specialize", "SpecializeEngine"))
check("DecomposeEngine", lambda: check_sub("decompose", "dz_engine.decompose", "DecomposeEngine"))
check("BridgePlan model", lambda: check_sub("bridge", "dz_engine.bridge", "BridgePlan"))
check("ExperimentEvolver", lambda: check_sub("evolver", "dz_engine.experiment_evolution", "ExperimentEvolver"))
check("KnowledgeRetriever", lambda: check_sub("retriever", "dz_engine.knowledge_retrieval", "KnowledgeRetriever"))

# --- Search components ---
print("\n7. Search components")


def check_search():
    from dz_engine.search import SearchState, RMaxTSSearch, select_module_ucb, rank_frontiers
    s = SearchState()
    assert hasattr(s, "visit_counts")


def check_htps():
    from dz_engine.htps import HTPSState, htps_select, htps_backup
    assert callable(htps_select)
    assert callable(htps_backup)


check("SearchState + UCB", check_search)
check("HTPS state + select + backup", check_htps)

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
