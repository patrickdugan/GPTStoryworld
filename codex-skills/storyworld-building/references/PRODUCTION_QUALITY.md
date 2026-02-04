# Production-Quality Storyworld Checklist

Use this checklist when generating or upgrading a full storyworld in one pass.
Treat it as a quality floor, not a stretch goal.

## Required Content
- Each encounter has a `title` and a 1–3 sentence `text_script`/`prompt_script`.
- Each encounter has `acceptability_script` and `desirability_script`.
- Each encounter is connected to at least one spool in `connected_spools`.
- Each option has `text_script`, `visibility_script`, `performability_script`.
- Each non-ending encounter has at least 2 options.
- Each option has at least 2 reactions.
- Each reaction has `text_script`, `desirability_script`, `consequence_id`, and non-empty `after_effects`.
- Each reaction desirability script must incorporate relevant variables (not a constant).
- Each reaction must include at least 3 effects (plus any spool changes or direct encounter transitions).
- Effects must move at least one authored bounded number property by a meaningful `Nudge`.

## Structure and Flow
- At least 3 spools (act1/act2/act3) plus an endings spool.
- Each act spool has >= 6 encounters.
- Endings spool has >= 3 endings.
- Endings have explicit `acceptability_script` thresholds and `desirability_script` formulas.
- No dangling encounter ids in spools or consequence chains.
 
## Variability and Gating
- Act II/III must include encounter acceptability/desirability scripts to create divergent paths.
- Some options must be gated with `visibility_script` to create variable experiences.
- Effects should accumulate to create measurable divergence by late Act III.

## Modeling and Balance
- Each authored property is touched by effects in >= 3 encounters.
- Every choice has a consequence path toward at least one ending.
- Provide at least one late-game gate (acceptability threshold) to prevent a single dominant ending.

## Validation and Tuning
- Run `scripts/sweepweave_validator.py` before and after edits.
- Run `tools/monte_carlo_rehearsal.py` with >= 5000 runs.
- If any ending > 30% or < 1%, adjust gates or effects and re-run Monte Carlo.

## Reference Example
- Use `C:/projects/GPTStoryworld/storyworlds/robert_of_st_albans.json` as a structure and scripting reference.
