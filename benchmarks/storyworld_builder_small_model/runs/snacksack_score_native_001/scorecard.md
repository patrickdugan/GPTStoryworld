# Small-Model Storyworld Builder Scorecard

- Manifest: `/home/snacksack/projects/GPTStoryworld/benchmarks/storyworld_builder_small_model/snacksack_manifest.jsonl`
- Rows: `5`

| Rank | Run | Model | Condition | Score | Weakest Fix |
|---:|---|---|---|---:|---|
| 1 | `snacksack_romeo_juliet_spooltight` | `reference` | `adaptation_reference_native` | 0.9287 | Use native routes for gates/effects; oversample effect and secret-route repair rows. |
| 2 | `snacksack_scarlet_letter_focus5` | `reference` | `adaptation_reference_native` | 0.9287 | Use native routes for gates/effects; oversample effect and secret-route repair rows. |
| 3 | `snacksack_macbeth_validated` | `scaffold` | `packet_author_native_reference` | 0.9112 | Run bounded prose rewrite packets after mechanics pass. |
| 4 | `snacksack_politburo_shehada` | `Qwen3.5-27B-Q4` | `hermes_storyworld_reference_native` | 0.8802 | Run bounded prose rewrite packets after mechanics pass. |
| 5 | `snacksack_first_and_last_men` | `reference` | `long_reference_native` | 0.8633 | Run bounded prose rewrite packets after mechanics pass. |

## Interpretation

Use this as a fast optimization target for small-model runs. A low component score should become the next bounded packet or native-schema repair target, not a larger one-shot prompt.
