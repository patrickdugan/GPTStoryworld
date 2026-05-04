# Small-Model Storyworld Builder Scorecard

- Manifest: `C:\projects\GPTStoryworld\benchmarks\storyworld_builder_small_model\sample_manifest.jsonl`
- Rows: `4`

| Rank | Run | Model | Condition | Score | Weakest Fix |
|---:|---|---|---|---:|---|
| 1 | `macbeth_native_schema_reference` | `scaffold` | `packet_author_native` | 0.9112 | Run bounded prose rewrite packets after mechanics pass. |
| 2 | `romeo_sanaa_qwen27b_packet_native` | `Qwen3.5-27B-Q4` | `packet_author_native` | 0.9058 | Run bounded prose rewrite packets after mechanics pass. |
| 3 | `tier5_causal_compiler_council` | `unknown` | `tier5_eval_reference` | 0.7750 | Run MCP preflight and keep every packet under the context budget. |
| 4 | `politburo_shehada_repaired` | `unknown` | `reference_repaired` | 0.7642 | Run MCP preflight and keep every packet under the context budget. |

## Interpretation

Use this as a fast optimization target for small-model runs. A low component score should become the next bounded packet or native-schema repair target, not a larger one-shot prompt.
