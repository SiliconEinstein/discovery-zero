# Changelog

## [Unreleased] — 2026-03-31 Industrial Hardening

### Fixed

- **BP purity violation**: `propagate_verification_signals` no longer directly mutates `node.prior`/`node.belief`; it now acts as a pure BP trigger
- **Streaming byte counter**: `_StreamingTextRecorder` now tracks actual text content bytes instead of raw SSE bytes (which include JSON wrappers and thinking tokens), preventing premature truncation
- **Monitor target belief**: `monitor_runs.py` now correctly identifies the target node by matching its statement from `resolved_proof_config.json`, with a three-tier fallback (graph.json → snapshot → lowest unverified)
- **SIGHUP handler**: `benchmark.py` now properly saves and restores the previous SIGHUP handler instead of forcing `SIG_DFL`
- **Summary generation**: `_generate_partial_summary` moved into outermost `finally` block; proofs file restore and summary generation are independent — one failing does not block the other
- **Gaia BP docstrings**: corrected `CONJUNCTION` and `SOFT_IMPLICATION` parameter semantics in theory documentation

### Added

- **Decomposition edges in BP**: decomposition-type hyperedges now participate in belief propagation as `SOFT_IMPLICATION` factors, allowing evidence to flow through subgoal structures
- **MCTS exception safety**: per-iteration `try/except` catches action failures without losing graph state; action results checkpointed to `action_checkpoints/`
- **Timeout decoupling**: `post_action_budget_seconds` ensures ingestion and BP run before optional followups (bridge planning, verification) when iteration budget is tight
- **Target isolation detection**: when the target node has no incoming edges for 3+ consecutive iterations, the engine forces a PLAUSIBLE action on the root goal
- **SIGTERM + SIGHUP handling**: benchmark runner handles both termination signals for graceful shutdown (e.g., `screen -X quit`)
- **Bridge extraction model fallback**: Opus model automatically falls back to GPT-5.2 for structured JSON extraction

### Removed

- Dead `MODEL_WORD_LIMITS` dictionary and unused `_resolve_model_word_limit` function from `orchestrator.py`
- Artificial LLM output limits: per-model word limit prompts, `max_prose_bytes` hard cap, auto-continue byte ceiling

### Changed

- `claim_verifier.py`: uses `node.prior` instead of `node.belief` for soft evidence updates
- `ingest.py`: soft evidence paths (experiment results) only modify `node.prior`; hard Lean verdicts set both `state` + `prior` + `belief`
- `adapter_v2.py`: simplified to pure Gaia v2 factor mapping; removed legacy v1 compatibility paths
