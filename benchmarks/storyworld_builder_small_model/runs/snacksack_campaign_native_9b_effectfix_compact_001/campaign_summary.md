# Small-Model Builder Campaign

- Scorecard: `/home/snacksack/projects/GPTStoryworld/benchmarks/storyworld_builder_small_model/runs/snacksack_score_native_effectfix_001/scorecard.json`
- Jobs: `5`
- Called model: `True`

| Job | Role | Operation | Tokens | Model Call |
|---|---|---|---:|---|
| `snacksack_romeo_juliet_spooltight_text_surface` | `llm_prompt_composer` | `bounded_prose_rewrite_plan` | 1076 | ok |
| `snacksack_scarlet_letter_focus5_text_surface` | `llm_prompt_composer` | `bounded_prose_rewrite_plan` | 1105 | ok |
| `snacksack_macbeth_validated_text_surface` | `llm_prompt_composer` | `bounded_prose_rewrite_plan` | 914 | ok |
| `snacksack_politburo_shehada_text_surface` | `llm_prompt_composer` | `bounded_prose_rewrite_plan` | 928 | ok |
| `snacksack_first_and_last_men_text_surface` | `llm_prompt_composer` | `bounded_prose_rewrite_plan` | 721 | ok |

## Next Step

Feed one prompt packet to the local small model, materialize only the returned bounded JSON plan, rerun the scorecard, and append the before/after delta as TRM training data.
