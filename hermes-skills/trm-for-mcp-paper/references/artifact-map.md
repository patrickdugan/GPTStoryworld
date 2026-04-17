# TRM For MCP Artifact Map

Use this reference to rebuild the paper from measured artifacts instead of prose notes.

## Paper Workspace

- Manuscript:
  - `papers/trm_for_mcp/trm_for_mcp_context_for_free.tex`
- Asset builder:
  - `papers/trm_for_mcp/build_assets.py`
- Generated outputs:
  - `papers/trm_for_mcp/figures/`
  - `papers/trm_for_mcp/generated/`
- Release bundles:
  - `papers/trm_for_mcp/releases/`
  - each bundle includes a `release_manifest.json` with provenance back to the exact run artifacts below

## Trivia Study Inputs

Primary frozen-slice runs:

- Base compact 2B:
  - `hermes-skills/pure-trm-trainer/runs/wiki_card_routerbench_qwen2b_4bit_full13_compact/summary.json`
  - `.../results.jsonl`
- Interrupted router checkpoint:
  - `hermes-skills/pure-trm-trainer/runs/wiki_card_routerbench_qwen2b_ckpt10/summary.json`
  - `.../results.jsonl`
- Final safe capped adapter:
  - `hermes-skills/pure-trm-trainer/runs/wiki_card_routerbench_qwen2b_safe_final_cap13/summary.json`
  - `.../scorecard.json`
  - `.../results.jsonl`

Interpretation rules:

- `closed_book_accuracy`, `stuffed_accuracy`, and `mcp_routed_accuracy` are answer metrics.
- `mcp_route_accuracy` is a routing-policy metric and must be reported separately.
- Prompt-token, evidence-token, and latency distributions come from `results.jsonl`.

## Storyworld Study Inputs

Selected bounded-context phase-event corpora:

- `hermes-skills/storyworld-conveyor/context_port_runs/usual_suspects_qwen2b_4gb_posttrain/reports/phase_events.jsonl`
- `hermes-skills/storyworld-conveyor/context_port_runs/abstract_letters_qwen2b_phase_only/reports/phase_events.jsonl`
- `hermes-skills/storyworld-conveyor/context_port_runs/usual_suspects_qwen2b_4gb_ultrasmall/reports/phase_events.jsonl`

Storyworld routing smoke:

- `hermes-skills/storyworld-conveyor/context_port_runs/mcp_trm_smoke_qwen35_2b/summary.json`

Representative output artifacts:

- `storyworlds/france_to_germany_machiavellian_p.json`
- `storyworlds/hive_to_glam_machiavellian.json`
- `storyworlds/shadow_to_bio_grudger.json`

Interpretation rules:

- Treat these as environment-study artifacts unless stronger replicated evals exist.
- Use `prompt_estimated_tokens`, `latency_ms`, `fallback_used`, and `budget.context_budget_tokens` for plots.
- Output file size is a proxy for externalized world-state scale, not proof of direct end-to-end authorship by the base model alone.
