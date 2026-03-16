# TRM Hybrid Notes

## Goal

Test a hybrid Hermes workflow on `samac` where:

- `Qwen 9B MLX` handles reasoning-oriented phases
- `Trinity Nano MLX` handles local authoring attempts
- `TRM` provides structure and rebalance guidance

## What Was Built

- A bounded Hermes port around the small storyworld builder
- MLX backend support for the Hermes phase pipeline on macOS
- Reasoning-only 9B Mac configs for safe Hermes use
- Trinity Nano Mac authoring configs for bounded `encounter_build` probes
- Monte Carlo + quality-gate -> TRM advice packet generation
- A local authoring TRM packet generator that narrows global failures into encounter-level hints
- A repaired-block quality score in the Hermes phase loop

## Main Results

### Qwen 9B On Mac

- Qwen 9B MLX was viable for Hermes reasoning phases.
- It completed planning/characterization-style work reliably enough.
- It was not reliable for first-pass SWMD block authoring.
- `encounter_build` and `late_stage_holistic` frequently required fallback.

Conclusion:

- Use Qwen 9B as a reasoning assistant, not as the direct block author.

### Trinity Nano On Mac

- Trinity Nano MLX ran successfully inside Hermes on `samac`.
- It performed better than the tested Qwen runs for bounded authoring.
- It still did not produce fully parse-clean first-pass encounter blocks.
- However, repair could often salvage the output into a valid block without hard fallback.

Conclusion:

- Trinity Nano is the best tested Mac-side authorship model in this repo so far.
- It is usable only with a repair layer.

## TRM Guidance Experiments

Three Trinity Nano authoring comparisons were run on the same Usual Suspects slice:

1. No TRM packet
2. Global Monte Carlo-derived TRM packet
3. Localized TRM packet derived from global failures plus encounter index rows

### Baseline: No TRM

- `page_scene_01`: repaired block quality score `0.75`
- `page_scene_02`: repaired block quality score `0.90`

### Global Monte Carlo TRM

The Monte Carlo probe for the Usual Suspects world was severe:

- `100%` timeout / dead-end
- unreachable endings
- no useful ending distribution

That global packet mainly pushed:

- restore reachability
- reduce dead ends
- increase script/operator variety

Result:

- `page_scene_01`: `0.75`
- `page_scene_02`: `0.75`

This was worse than baseline on `page_scene_02`.

### Localized TRM Packet

The localized packet converted the global failures into encounter-level hints such as:

- make local reactions more specific
- avoid consequence collapse
- reduce pure `NUDGE` monoculture
- add `P(...)` / `P2(...)` references when natural

Result:

- `page_scene_01`: `0.75`
- `page_scene_02`: `0.75`

This was cleaner than the global packet conceptually, but still did not beat the no-TRM baseline.

## Current Interpretation

- TRM is useful for reasoning, audit, and rebalance control.
- TRM did not improve direct local block authorship for Trinity Nano in these tests.
- The main successful hybrid split is:
  - `Qwen 9B` for reasoning
  - `Trinity Nano` for local authorship
  - deterministic repair/validation after authorship

## Practical Recommendation

For near-term Hermes use:

1. Keep `Qwen 9B` in reasoning phases only.
2. Keep `Trinity Nano` as the authoring model for bounded encounter edits.
3. Keep repair enabled.
4. Use TRM packets primarily to steer reasoning and selection, not as heavy prompt overlays for direct authorship.

## Next Step

If this hybrid line is resumed later, the next thing to build should be:

- a deterministic second-pass rewrite/optimizer that applies local TRM constraints onto the repaired Trinity block

That is a better bet than adding more prompt-only TRM guidance to first-pass authoring.
