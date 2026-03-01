# Discovery Zero

Self-directed mathematical discovery system via reasoning hypergraph.

## Commands

- Install: `pip install -e ".[dev]"`
- Test: `pytest`
- CLI: `dz --help`

## Architecture

- `src/discovery_zero/` - Core Python package
- `skills/` - Claude Code skills (`.skill.md` files)
- `docs/plans/` - Design and implementation docs

## Key concepts

- **Hypergraph**: Nodes are propositions, hyperedges are reasoning steps
- **Hyperedge format**: `{premises, steps, conclusion, module, confidence}`
- **Three modules**: plausible reasoning, experiment, lean proof
- **Judge**: LLM-as-judge assigns confidence to each hyperedge
- **Belief propagation**: Bayesian inference over the hypergraph
