# Idea Factory One-Shot Contract (v0)

Use this when asking a model to generate a production-ready storyworld in one pass.
Goal: high-entropy creative voice with deterministic structural quality.

## Creative Direction
- Theme blend should be explicit and intentional, not random.
- Satire blends are allowed (for example absurd small-town lampoon + cutaway non sequitur energy), but keep original plot substance and coherent stakes.
- Every act must escalate conflict, not only style.

## Hard Output Contract
- Output one valid SweepWeave JSON storyworld only.
- Stable IDs for all generated entities:
  - Encounters: `enc_*` or `page_*`
  - Options: `opt_*`
  - Reactions: `rxn_*`
- Include at least 3 act spools (`act1`, `act2`, `act3`) plus an endings spool.
- Non-ending encounters must each have at least 2 options.
- Each option must have at least 2 reactions.
- Each reaction must have non-empty `after_effects`.

## Density Targets
- Average options per encounter: >= 3.2
- Average reactions per option: >= 2.5
- Average effects per reaction: >= 4.5
- Average unique variable refs per reaction desirability script: >= 1.6

## Script Artistry Targets
- Reaction desirability scripts cannot be constant-only.
- Use meaningful operator variety (for example `Addition`, `Multiplication`, `Arithmetic Mean`, threshold checks).
- Use both first-order and second-order beliefs where relevant:
  - `pValue` pointers for direct beliefs
  - `p2Value` keyrings for beliefs about beliefs
- At least one coalition path and one defection path should be representable by script logic.

## Text Quality Targets
- Encounter text length: 50-300 words.
- Reaction text length: 20-150 words.
- Keep voice consistent, but vary rhetoric across factions/characters.

## Secret/Ending Discipline
- Include explicit terminal endings.
- If secret endings are used, gate them with availability logic using at least two variables.
- Keep one fallback ending reachable.

## Required Post-Generation Checks
1. `python codex-skills/storyworld-building/scripts/sweepweave_validator.py validate <storyworld.json>`
2. `python codex-skills/storyworld-building/scripts/storyworld_quality_gate.py --storyworld <storyworld.json> --strict --report-out <report.json>`
3. `python codex-skills/storyworld-building/scripts/json_to_swmd.py <storyworld.json> <storyworld.swmd.min.md> --mode minified`

## One-Shot Prompt Template
```
Create one complete SweepWeave storyworld JSON using this brief:
- Premise: <premise>
- Tone blend: <style blend>
- Setting + factions: <setting>
- Core conflict: <conflict>
- Required endings: <ending list>

Hard constraints:
- Deterministic IDs for encounters/options/reactions.
- >= 3 act spools + endings spool.
- Non-ending encounters: >=2 options each; options: >=2 reactions each; reactions: non-empty after_effects.
- Target density: options/encounter >=3.2, reactions/option >=2.5, effects/reaction >=4.5.
- Reaction desirability scripts must use relevant variables and include pValue + p2Value logic where applicable.
- Encounter text 50-300 words; reaction text 20-150 words.
- Must load in SweepWeave validator without errors.

Return only JSON.
```
