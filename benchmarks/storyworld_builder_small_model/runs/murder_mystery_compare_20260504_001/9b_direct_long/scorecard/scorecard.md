# Small-Model Storyworld Builder Scorecard

- Manifest: `/home/snacksack/projects/GPTStoryworld/benchmarks/storyworld_builder_small_model/runs/murder_mystery_compare_20260504_001/9b_direct_long/manifest.jsonl`
- Rows: `1`

| Rank | Run | Model | Condition | Score | Weakest Fix |
|---:|---|---|---|---:|---|
| 1 | `9b_direct_long` | `Qwen_Qwen3.5-9B-Q4_K_M.gguf` | `9b_direct_long` | 0.7727 | Run MCP preflight and keep every packet under the context budget. |

## Interpretation

Use this as a fast optimization target for small-model runs. A low component score should become the next bounded packet or native-schema repair target, not a larger one-shot prompt.
