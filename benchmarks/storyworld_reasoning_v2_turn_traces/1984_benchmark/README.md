# 1984 Storyworld Benchmark

## Inputs
- One-shot: `C:\projects\GPTStoryworld\storyworlds\generated\1984_benchmark\1984_one_shot.json`
- N-shot: `C:\projects\GPTStoryworld\storyworlds\generated\1984_benchmark\1984_n_shot.json`

## Validator
- One-shot errors: 0
- N-shot errors: 0

## Core Deltas
- `options_per_encounter`: one-shot `3.0` -> n-shot `3.3125` (delta `0.3125`)
- `reactions_per_option`: one-shot `2.0` -> n-shot `3.0` (delta `1.0`)
- `effects_per_reaction`: one-shot `4.0` -> n-shot `5.3774` (delta `1.3774`)
- `desirability_vars_per_reaction`: one-shot `3.0` -> n-shot `4.2201` (delta `1.2201`)
- `avg_encounter_words`: one-shot `17.375` -> n-shot `60.4` (delta `43.025`)
- `avg_reaction_words`: one-shot `19.375` -> n-shot `23.5031` (delta `4.1281`)
- `pvalue_refs`: one-shot `0.0` -> n-shot `450.0` (delta `450.0`)
- `p2value_refs`: one-shot `0.0` -> n-shot `138.0` (delta `138.0`)
- `desirability_operator_variety`: one-shot `3.0` -> n-shot `5.0` (delta `2.0`)
- `desirability_script_complexity`: one-shot `1.0` -> n-shot `1.4151` (delta `0.4151`)
- `effect_operator_variety`: one-shot `1.0` -> n-shot `3.0` (delta `2.0`)
- `effect_script_complexity`: one-shot `1.0` -> n-shot `1.2632` (delta `0.2632`)
- `validator_errors`: one-shot `0` -> n-shot `0` (delta `0`)

## Interpretation
- The N-shot pass now encodes first-order and second-order belief mechanics around O'Brien, Julia, and entrapment resistance, while also restoring iconic 1984 beats: the hate session, Julia's note and paperweight, and Goldstein's book.
- The O'Brien spycraft lane is now explicitly two-step: `page_scene_obrien_false_read` sets the mask, and `page_scene_obrien_followup` tests whether that mask survives a quieter second read.
- The benchmark now scores full false-read plus follow-up paths instead of a single direct scene hop.
- The best aggregate path in both the 5-state canonical benchmark and the 576-state sweep is `opt_obrien_false_read -> opt_obrien_followup_clerical_noise`.
- That path now rewards subtle counterintelligence rather than blunt refusal: it is secret-acceptable in `balanced_trap`, `already_suspicious`, and `paperweight_memory`, but it loses that status in `julia_compromised` and `near_conversion`.
- `opt_obrien_false_read -> opt_obrien_followup_sustain` now opens a genuine conversion hazard: `page_end_0205` becomes acceptable in the `near_conversion` benchmark state.
- The N-shot variant still passes the direct quality benchmark that the one-shot version fails, while the false-read lane now shows state-contingent tradeoffs instead of a single dominant answer.

## Next Passes
- Differentiate the three authored reactions per spycraft option with distinct effect payloads; right now the benchmarked reaction combos still collapse too often to the same state update.
- Add a Julia-repair lane so the `julia_compromised` basin has a subtle recovery path instead of defaulting to harder, less elegant play.
- Extend the benchmark beyond hand-authored baselines into upstream scene traces so the late O'Brien path is measured against states that actually arise from play, not only synthetic overrides.
