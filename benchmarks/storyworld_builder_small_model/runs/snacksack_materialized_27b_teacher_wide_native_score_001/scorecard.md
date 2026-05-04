# Small-Model Storyworld Builder Scorecard

- Manifest: `/home/snacksack/projects/GPTStoryworld/benchmarks/storyworld_builder_small_model/runs/snacksack_materialized_27b_teacher_wide_native_001/candidate_manifest.jsonl`
- Rows: `3`

| Rank | Run | Model | Condition | Score | Weakest Fix |
|---:|---|---|---|---:|---|
| 1 | `snacksack_macbeth_validated_text_surface_candidate` | `teacher_materialized` | `bounded_prose_rewrite_candidate_native` | 0.9112 | Run bounded prose rewrite packets after mechanics pass. |
| 2 | `snacksack_politburo_shehada_text_surface_candidate` | `teacher_materialized` | `bounded_prose_rewrite_candidate_native` | 0.8808 | Run bounded prose rewrite packets after mechanics pass. |
| 3 | `snacksack_first_and_last_men_text_surface_candidate` | `teacher_materialized` | `bounded_prose_rewrite_candidate_native` | 0.8655 | Use native routes for gates/effects; oversample effect and secret-route repair rows. |

## Interpretation

Use this as a fast optimization target for small-model runs. A low component score should become the next bounded packet or native-schema repair target, not a larger one-shot prompt.
