# Secret Ending Gates

Use this pattern when you want secret endings that require accumulated
metric distance across 1-3 variables. The gate should be reachable but
not accidental, and should be tied to a gated option leading to a gated
reaction that provides a meaningful effect boost or spool trigger.

## Core Pattern

1) Encounter acceptability gate:
- Use 1-3 variable thresholds with Arithmetic Comparators or AND.
- Example: Faith_Doubt >= 0.06 AND Honor_Expediency >= 0.04.

2) Gated option visibility:
- The option must have a visibility_script that references the same
  variables as the encounter gate (or tighter).
- This ensures the player sees the secret only after accumulation.

3) Gated reaction with boosted effects:
- Each gated option must have at least 2 reactions.
- Each reaction desirability_script must use variables (not constants).
- Each reaction must apply >= 3 after_effects with meaningful Nudges.
- One reaction should give a higher boost or trigger a spool change.

## Threshold Guidance
- Use thresholds in the 0.02–0.08 range for bounded numbers (tune per world).
- A single variable gate can be higher (e.g., 0.08).
- Multi-variable gates can be lower per variable (e.g., 0.03 + 0.03).

## Example (Conceptual)
- Encounter: `page_act3_oathbreak`
- Acceptability: Loyalty_Betrayal >= 0.04 AND Honor_Expediency >= 0.03
- Option visibility: same gates or tighter
- Reaction A: boosts Loyalty_Betrayal +0.03, Faith_Doubt +0.02, triggers
  an ending spool (or a secret encounter)
- Reaction B: smaller boosts, different consequence_id

## Validation
Run:
`python scripts/sweepweave_validator.py validate <storyworld.json>`
Then:
`python scripts/secret_endings_gates.py <storyworld.json>`
