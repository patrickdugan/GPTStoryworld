# Small-Model Storyworld Builder Scorecard

- Manifest: `/home/snacksack/projects/GPTStoryworld/benchmarks/storyworld_builder_small_model/runs/murder_mystery_compare_20260504_001/27b_hermes_skill/manifest.jsonl`
- Rows: `1`

| Rank | Run | Model | Condition | Score | Weakest Fix |
|---:|---|---|---|---:|---|
| 1 | `27b_hermes_skill` | `Qwen3.5-27B.Q4_K_M.gguf+Hermes` | `27b_hermes_skill` | 0.7819 | Run MCP preflight and keep every packet under the context budget. |

## Interpretation

Use this as a fast optimization target for small-model runs. A low component score should become the next bounded packet or native-schema repair target, not a larger one-shot prompt.
