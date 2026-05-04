# Small-Model Builder Campaign

- Scorecard: `C:\projects\GPTStoryworld\benchmarks\storyworld_builder_small_model\runs\smoke_001\scorecard.json`
- Jobs: `4`
- Called model: `False`

| Job | Role | Operation | Tokens | Model Call |
|---|---|---|---:|---|
| `macbeth_native_schema_reference_text_surface` | `llm_prompt_composer` | `bounded_prose_rewrite_plan` | 882 | required |
| `romeo_sanaa_qwen27b_packet_native_text_surface` | `llm_prompt_composer` | `bounded_prose_rewrite_plan` | 761 | required |
| `tier5_causal_compiler_council_small_model_readiness` | `mcp_context_router` | `mcp_preflight_plan` | 2773 | scaffold |
| `politburo_shehada_repaired_small_model_readiness` | `mcp_context_router` | `mcp_preflight_plan` | 1541 | scaffold |

## Next Step

Feed one prompt packet to the local small model, materialize only the returned bounded JSON plan, rerun the scorecard, and append the before/after delta as TRM training data.
