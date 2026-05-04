# Research Stimulus MCP Smoke

## Purpose

Verify that compact research cards can be built from source material and injected into the MCP/TRM constraint packet before any model load.

## Command Shape

```powershell
python hermes-skills/storyworld-conveyor/scripts/prepare_mcp_conveyor_config.py `
  --storyworld hermes-skills/storyworld-conveyor/working_worlds/nine_lantern_expanded_kalam_exam/nine_lantern_expanded_kalam_exam.json `
  --world-json hermes-skills/storyworld-conveyor/working_worlds/nine_lantern_expanded_kalam_exam/nine_lantern_expanded_kalam_exam.json `
  --quality-report hermes-skills/storyworld-conveyor/working_worlds/nine_lantern_expanded_kalam_exam/quality_gate.json `
  --out-config hermes-skills/storyworld-conveyor/working_worlds/nine_lantern_expanded_kalam_exam/research_stimulus_smoke/mcp_research_config.json `
  --artifact-root hermes-skills/storyworld-conveyor/working_worlds/nine_lantern_expanded_kalam_exam/research_stimulus_smoke/context_port_runs `
  --run-id kalam_research_constraints `
  --max-encounters 4 `
  --context-budget-tokens 8192 `
  --max-new-tokens 256 `
  --research-source hermes-skills/storyworld-conveyor/working_worlds/nine_lantern_expanded_kalam_exam/brief.md `
  --research-topic "Mutazili Kalam qadi exam Yusuf Lin" `
  --research-card-count 4 `
  --research-card-token-budget 160

python hermes-skills/storyworld-conveyor/scripts/run_small_model_storyworld_port.py `
  --config hermes-skills/storyworld-conveyor/working_worlds/nine_lantern_expanded_kalam_exam/research_stimulus_smoke/mcp_research_config.json `
  --constraints-only
```

## Result

- Status: `constraints_completed`
- Research cards: 1 compact card from local Kalam brief
- MCP budget: 4 encounter packets selected, worst prompt 5446 tokens, 0 overflow with `max_new_tokens=256`
- TRM constraints include `hilbert_pathing`, `research_stimulus`, and `profile.research_stimulus_mode=compact_cards`
- Model load: none

## Interpretation

This gives the conveyor a safe "researcher" lane: source material is compressed into bounded cards, ranked against the topic and storyworld terms, and made available to the small model through MCP constraints. The model can use cards to stimulate local prose, questions, clues, and option/reaction ideas, but the card contract forbids treating excerpts as exhaustive authority or overriding validators.
