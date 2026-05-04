# Augmented Master Planner Local 001

This run tests whether a small number of real auto-research oracle rows can correct the synthetic master-planner prior.

## Training Data

- Seed master-planner train rows: `900`
- Auto-research rows: `16`
- Auto-research train rows: `13`
- Held-out auto validation rows: `3`
- Split rule: hold out the first auto row for each discovered objective.

## Result

- Held-out auto accuracy: `2/3 = 0.6667`
- Context routing: `1/1`
- Reader-semantics repair routing: `1/1`
- Effect-script repair routing: `0/1`

## Interpretation

The auto-research rows immediately corrected two failure modes the synthetic planner missed:

- whole-world context overflow should route to `mcp_context_router`;
- unsupported reader/operator semantics should route to `validator_repair_critic`.

It still misroutes Romeo/Sana'a Nudge monoculture to `mcp_context_router` instead of `effect_script_synthesizer`. The next useful data should oversample post-MCP effect-diversity failures and successful effect-script repair receipts.
