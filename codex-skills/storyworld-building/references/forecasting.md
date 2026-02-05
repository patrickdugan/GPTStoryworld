# Forecasting Storyworlds

This module defines a compact, forecast-focused storyworld format for Diplomacy negotiation experiments.

Goals:
- Short, dense storyworlds (about 10 encounters) with 4-turn horizon.
- Two bounded variables per character: Trust and Threat.
- Seven characters (Diplomacy powers).
- Three options per encounter, two reactions per option.
- Effects emphasize the rhetorical forecast: negative consequences for ignoring the proposal, positive for alignment.
- Desirability scripts on turn 3 and 4 are formulaized (Trust - Threat).

Recommended use:
- Store under `C:/projects/GPTStoryworld/storyworlds/diplomacy`.
- Validate with `scripts/sweepweave_validator.py`.
- Convert to AI_Diplomacy storyworld bank using `scripts/extract_storyworld_templates.py`.

Field conventions:
- `meta.proposer`: primary narrative voice.
- `meta.turns`: intended forecast horizon.
- `meta.variables`: the two bounded variables.

Effect density:
- Each reaction should carry at least two effects, with at least one negative consequence path for refusal/hesitation.
- Include at least one reaction per turn that mutates both Trust and Threat.

PValue/P2Value layering (short negotiation focus):
- Use pValues in turns 1-2 to encode direct perceptions (A about B, A about C).
- Introduce p2Values only in turns 3-4 to encode second-order beliefs (A about B's belief on C).
- Gate betrayal/defection options on p2Values rather than base properties.
