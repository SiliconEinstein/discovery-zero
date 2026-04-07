#!/usr/bin/env python3
"""Validate dz-mcp-server skill: imports, tool registration, server startup."""
import sys

errors: list[str] = []


def check(label: str, fn):
    try:
        fn()
        print(f"  [PASS] {label}")
    except Exception as e:
        errors.append(f"{label}: {e}")
        print(f"  [FAIL] {label}: {e}")


print("=== dz-mcp-server validation ===\n")

# --- Package imports ---
print("1. Package imports")
check("import dz_mcp", lambda: __import__("dz_mcp"))
check("import dz_mcp.server", lambda: __import__("dz_mcp.server"))
check("import mcp", lambda: __import__("mcp"))

# --- Server object ---
print("\n2. MCP Server object")


def check_server_object():
    from dz_mcp.server import mcp
    assert hasattr(mcp, "run"), "mcp object has no 'run' method"
    assert hasattr(mcp, "tool"), "mcp object has no 'tool' decorator"


check("FastMCP instance", check_server_object)

# --- Tool functions ---
print("\n3. Registered tool functions")

EXPECTED_TOOLS = [
    "dz_extract_claims",
    "dz_verify_claims",
    "dz_propagate_beliefs",
    "dz_analyze_gaps",
    "dz_load_graph",
    "dz_run_discovery",
]


def check_tool_exists(tool_name):
    import dz_mcp.server as srv
    fn = getattr(srv, tool_name, None)
    assert fn is not None, f"Function {tool_name} not found in dz_mcp.server"
    assert callable(fn), f"{tool_name} is not callable"


for tool_name in EXPECTED_TOOLS:
    check(f"tool: {tool_name}", lambda tn=tool_name: check_tool_exists(tn))

# --- Tool signatures ---
print("\n4. Tool signatures")
import inspect


def check_tool_sig(tool_name, required_params):
    import dz_mcp.server as srv
    fn = getattr(srv, tool_name)
    sig = inspect.signature(fn)
    params = set(sig.parameters.keys())
    missing = required_params - params
    assert not missing, f"Missing params in {tool_name}: {missing}"


check("dz_extract_claims params",
      lambda: check_tool_sig("dz_extract_claims", {"prose", "context", "source_memo_id"}))
check("dz_verify_claims params",
      lambda: check_tool_sig("dz_verify_claims", {"prose", "context", "graph_json_or_path", "source_memo_id"}))
check("dz_propagate_beliefs params",
      lambda: check_tool_sig("dz_propagate_beliefs", {"graph_json_or_path"}))
check("dz_analyze_gaps params",
      lambda: check_tool_sig("dz_analyze_gaps", {"graph_json_or_path", "target_node_id"}))
check("dz_load_graph params",
      lambda: check_tool_sig("dz_load_graph", {"path"}))
check("dz_run_discovery params",
      lambda: check_tool_sig("dz_run_discovery", {"graph_path", "target_node_id"}))

# --- Helper function ---
print("\n5. Internal helpers")


def check_load_helper():
    from dz_mcp.server import _load_graph_from_input
    import json, tempfile, pathlib
    from dz_hypergraph import create_graph, save_graph

    g = create_graph()
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        tmp = pathlib.Path(f.name)
    save_graph(g, tmp)
    graph, path = _load_graph_from_input(str(tmp))
    assert len(graph.nodes) == 0
    assert path == tmp
    tmp.unlink()

    graph2, path2 = _load_graph_from_input(json.dumps({"nodes": {}, "edges": {}}))
    assert path2 is None


check("_load_graph_from_input (file + JSON)", check_load_helper)

# --- Entry point ---
print("\n6. Entry point")


def check_main():
    from dz_mcp.server import main
    assert callable(main)


def check_cli_entry():
    import importlib.metadata
    eps = importlib.metadata.entry_points()
    console_scripts = eps.select(group="console_scripts") if hasattr(eps, "select") else eps.get("console_scripts", [])
    names = [ep.name for ep in console_scripts]
    assert "dz-mcp" in names, f"'dz-mcp' not in console_scripts: {names}"


check("main() callable", check_main)
check("dz-mcp console_scripts entry", check_cli_entry)

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
