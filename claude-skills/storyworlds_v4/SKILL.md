---
name: storyworlds-v4
description: Generate, enrich, and balance interactive narrative storyworlds in SweepWeave 0.1.9 JSON format. Covers full lifecycle from empty shell to Monte Carlo-verified balanced manifold. Triggers on "storyworld", "SweepWeave", "interactive narrative", "narrative design", "Monte Carlo rehearsal", or requests for procedural narrative generation with property axes and effect operators.
---

# Storyworlds Skill v4

## What Changed from v3
- Monte Carlo rehearsal simulation for ending distribution balancing
- Consequence chain architecture (linear chains vs spool-driven selection)
- Effect magnitude calibration via simulation feedback loops
- Character ID consistency enforcement
- Universal fallback ending pattern
- Spool activation requirements for endgame encounters
- Systematic property bias detection and gate compensation

## SweepWeave 0.1.9 JSON Schema (Key Structures)

### Top-Level Keys
```json
{
  "IFID": "uuid",
  "about_text": "",
  "css_theme": "dark",
  "debug_mode": false,
  "display_mode": "default",
  "creation_time": 1234567890.0,
  "modified_time": 1234567890.0,
  "characters": [...],
  "authored_properties": [...],
  "spools": [...],
  "encounters": [...]
}
```

### Characters
```json
{
  "id": "char_civ",
  "character_name": "Civilization",
  "bnumber_properties": {
    "Embodiment_Virtuality": 0,
    "pEmbodiment_Virtuality": 0
  },
  "authored_properties": [
    {"id": "Embodiment_Virtuality", "property_name": "Embodiment_Virtuality", "property_type": "bounded number", "depth": 0},
    {"id": "pEmbodiment_Virtuality", "property_name": "pEmbodiment_Virtuality", "property_type": "bounded number", "depth": 0}
  ]
}
```

### Spools
```json
{
  "id": "spool_age_1",
  "spool_name": "Age 1",
  "creation_index": 0,
  "creation_time": 0,
  "modified_time": 0,
  "starts_active": true,
  "encounters": ["page_0000", "page_0001", ...]
}
```
**CRITICAL**: Spools used for endgame/endings MUST have `starts_active: true` if there are no SpoolEffect operators to activate them. The engine only scans active spools when selecting encounters via desirability.

### Encounters
```json
{
  "id": "page_0000",
  "graph_offset_x": 0, "graph_offset_y": 0,
  "title": "The First Age",
  "prompt_script": {"pointer_type": "String Constant", "script_element_type": "Pointer", "value": "Narrative text..."},
  "text_script": {"pointer_type": "String Constant", "script_element_type": "Pointer", "value": "Display text..."},
  "acceptability_script": true,
  "desirability_script": {"pointer_type": "Bounded Number Constant", "script_element_type": "Pointer", "value": 0.5},
  "options": [...]
}
```

### Options
```json
{
  "id": "opt_page_0000_0",
  "graph_offset_x": 0, "graph_offset_y": 0,
  "text_script": {"pointer_type": "String Constant", "script_element_type": "Pointer", "value": "Choice text"},
  "visibility_script": true,
  "performability_script": true,
  "reactions": [...]
}
```

### Reactions
```json
{
  "id": "opt_page_0000_0_r0",
  "graph_offset_x": 0, "graph_offset_y": 0,
  "text_script": {"pointer_type": "String Constant", "script_element_type": "Pointer", "value": "Outcome text"},
  "consequence_id": "page_0001",
  "desirability_script": {"pointer_type": "Bounded Number Constant", "script_element_type": "Pointer", "value": 1.0},
  "after_effects": [...]
}
```

### After-Effects (Nudge Operator)
```json
{
  "effect_type": "Bounded Number Effect",
  "Set": {
    "pointer_type": "Bounded Number Pointer",
    "script_element_type": "Pointer",
    "character": "char_civ",
    "keyring": ["Embodiment_Virtuality"],
    "coefficient": 1.0
  },
  "to": {
    "operator_type": "Nudge",
    "script_element_type": "Operator",
    "operands": [
      {"pointer_type": "Bounded Number Pointer", "script_element_type": "Pointer",
       "character": "char_civ", "keyring": ["Embodiment_Virtuality"], "coefficient": 1.0},
      {"pointer_type": "Bounded Number Constant", "script_element_type": "Pointer", "value": 0.045}
    ]
  }
}
```

### Script Expression Types

**Pointers:**
- `Bounded Number Constant` -- fixed value: `{"pointer_type": "Bounded Number Constant", "value": 0.5}`
- `Bounded Number Pointer` -- character property reference: `{"pointer_type": "Bounded Number Pointer", "character": "char_civ", "keyring": ["prop"], "coefficient": 1.0}`
- `String Constant` -- text value: `{"pointer_type": "String Constant", "value": "text"}`

**Operators:**
- `Arithmetic Comparator` -- subtypes: "Greater Than or Equal To", "Less Than or Equal To", "Greater Than", "Less Than", "Equal To", "Not Equal To"
- `And` / `Or` -- logical combination of operands
- `Addition` / `Multiplication` -- arithmetic on operands
- `Absolute Value` -- single operand
- `Nudge` -- bounded addition: `clamp(current + delta, -1, 1)`

## Architecture Patterns

### Spool-Based Encounter Selection (Preferred)
Use the engine's native `select_page()` algorithm instead of hardcoded consequence chains. The engine scans active spools for unused, acceptable encounters and picks the one with highest `desirability_script`.

**How it works:**
- `desirability_script` at 0 = random grabbag (engine picks arbitrarily among ties)
- Higher desirability = served first. Sequence encounters by setting descending values.
- `acceptability_script` = gate. Encounters with `false` or failing conditions are skipped.
- Each encounter fires once (`occurrences == 0` check). After firing, it's removed from selection.

**Desirability ordering within each age/chapter spool:**
```
Slot 0 (Thesis):     (21 - age) + 0.30   — plays first, always acceptable
Slot 1 (Pressure):   (21 - age) + 0.25
Slot 2 (Morph):      (21 - age) + 0.20
Slot 3 (Escape):     (21 - age) + 0.15
Slot 4 (CA):         (21 - age) + 0.10   — gated on Grudge/Influence
Slot 5 (Relic):      (21 - age) + 0.05   — plays last, always acceptable
```

This produces natural sequencing: Age 1 encounters (desirability ~20) fire before Age 2 (~19), and within each age, Thesis fires before Pressure, etc.

**Key requirements:**
- All Age spools must have `starts_active: true` (encounters only fire once, so old ages don't re-fire)
- Remove all `consequence_id` links within age encounters (set to `""`)
- At least one encounter per spool must have `acceptability_script: true` (guaranteed "landing" encounter — typically Thesis and Relic)
- Endgame/Secrets spools also need `starts_active: true`

**Counter-Archivist gating:**
CA encounters (slot 4) use `acceptability_script` to check if the player has provoked the archivist:
```
Grudge >= threshold  OR  Influence >= threshold
```
If neither condition is met, the CA leaves you alone and the engine skips to the Relic. Thresholds scale by age range (easier to trigger in early game, harder mid-game).

**Script**: `scripts/spool_sequencing.py`

### Legacy: Linear Consequence Chain
Some storyworlds use hardcoded consequence links (reaction.consequence_id → next encounter). This bypasses the spool/desirability selection engine entirely. The engine's `select_page()` only fires when consequence_id is null or "".

**Pattern**: page_0000 → page_0001 → ... → page_N → "" → spool selection for endings

This is simpler but inflexible:
- Cannot conditionally skip encounters (CA gating doesn't work)
- Spools only matter at the chain terminus
- No natural way to vary encounter order based on player state

### Encounter Slot Pattern (per Age/Chapter)
For civilization-scale narratives, use 6 encounter slots per age:

| Slot | Role | Options | Special Reactions |
|------|------|---------|-------------------|
| 0 | Thesis | 3 (bold/deceptive/moderate) | Backfire + spectacular success |
| 1 | Pressure | 3 | Backfire |
| 2 | Morph | 3 | Backfire |
| 3 | Escape | 3 | Backfire + spectacular success |
| 4 | Counter-Archivist | 2 | CA reversal + catch |
| 5 | Relic | 1 | Misunderstood + lost |

### Effect Magnitude Guidelines
After Monte Carlo calibration, these magnitudes produce meaningful property accumulation over ~120 encounters with random play:

| Option Type | Base Property Delta | Cumulative Delta | CA Property |
|-------------|-------------------|------------------|-------------|
| Bold (opt 0) | +/-0.045 | +/-0.022 | -- |
| Deceptive (opt 1) | +/-0.045 | +/-0.022 | Grudge +0.015 |
| Moderate (opt 2) | +/-0.024 | +/-0.012 | -- |
| Backfire reaction | -/+0.030 | -- | Grudge +0.024 |
| CA reversal | -/+0.030 | -- | Countercraft +0.030 |
| Spectacular success | +/-0.060 | +/-0.030 | Grudge -0.009 |

### Property Axis Design
Use paired instantaneous + cumulative properties:
- `Embodiment_Virtuality` (depth 0) -- current state, oscillates
- `pEmbodiment_Virtuality` (depth 0) -- running integral, monotonic tendency

Cumulative properties enable path-dependent gating: "have you consistently pushed this axis?"

### Counter-Archivist Pattern
Adversarial conscience character with 3 properties:
- **Influence** -- narrative authority, grows from Relic encounters
- **Grudge** -- grievance from ignored warnings, grows from deceptive choices
- **Countercraft** -- strategic resources, grows from CA reversal reactions

**IMPORTANT**: Use consistent character IDs. Always `char_counter_archivist`, never bare `counter_archivist`.

## Inclination Formulas (desirability_script)

### Simple Numeric Sequencing (Recommended)
The simplest and most reliable approach: assign constant desirability values that create a natural ordering.

```
desirability = (21 - age) + slot_offset
```

| Slot | Offset | Example (Age 1) | Example (Age 20) |
|------|--------|-----------------|------------------|
| Thesis | +0.30 | 20.30 | 1.30 |
| Pressure | +0.25 | 20.25 | 1.25 |
| Morph | +0.20 | 20.20 | 1.20 |
| Escape | +0.15 | 20.15 | 1.15 |
| CA | +0.10 | 20.10 | 1.10 |
| Relic | +0.05 | 20.05 | 1.05 |
| Secrets | 0.80 | 0.80 | 0.80 |
| Endgame | 0.50 | 0.50 | 0.50 |

The engine picks highest desirability among unused, acceptable encounters. This produces clean sequencing without formulas.

### Advanced: Property-Based Attractors
For storyworlds that want encounters to adapt to player trajectory:

| Encounter Type | Formula | Rationale |
|----------------|---------|-----------|
| Main encounters | `0.3 × |cumulative_prop|` | Attractor basin — aligned encounters preferred |
| Counter-Archivist | `0.4 × Influence` | CA surfaces more as it gains presence |
| Relic | `0.5` (constant) | Always interesting |

This is more complex and harder to debug. Use simple numeric sequencing first, upgrade to formulas only if needed.

### Ending Desirability
When multiple endings pass their acceptability gates, desirability determines which wins:
- Use the ending's primary property as desirability score
- The universal fallback ending gets very low desirability (0.001)
- This ensures the most thematically appropriate ending wins

### Late-Game Gating (acceptability_script)
Gate encounters in the final third on cumulative property thresholds:

| Age Range | Threshold | Effect |
|-----------|-----------|--------|
| 14-15 | |pProp| >= 0.01 | Minimal engagement check |
| 16-17 | |pProp| >= 0.02 | Light commitment |
| 18-19 | |pProp| >= 0.03 | Moderate investment |
| 20 | |pProp| >= 0.04 | Significant path commitment |

Use OR gate: `pProp >= threshold OR pProp <= -threshold` (works regardless of push direction).

**Exempt CA and Relic encounters from gating** -- the conscience and the wonder should never be locked out.

## Ending Gate Design

### Principles
1. Each ending gates on 1-3 properties being in a specific region
2. Account for systematic property biases (effects aren't perfectly balanced)
3. Gates should be set at mean + 0.5-1.0 std from Monte Carlo baseline
4. Multiple endings can be acceptable simultaneously -- desirability tiebreaks
5. **Universal fallback ending**: one ending with `acceptability_script: true` and very low desirability (0.001) catches all runs that don't qualify for specific endings

### Example Gate (AND of comparators):
```json
{
  "operator_type": "And",
  "script_element_type": "Operator",
  "operands": [
    {"operator_type": "Arithmetic Comparator", "operator_subtype": "Greater Than or Equal To",
     "operands": [
       {"pointer_type": "Bounded Number Pointer", "character": "char_civ", "keyring": ["Embodiment_Virtuality"], "coefficient": 1.0},
       {"pointer_type": "Bounded Number Constant", "value": 0.10}
     ]},
    {"operator_type": "Arithmetic Comparator", "operator_subtype": "Greater Than or Equal To",
     "operands": [
       {"pointer_type": "Bounded Number Pointer", "character": "char_civ", "keyring": ["pEmbodiment_Virtuality"], "coefficient": 1.0},
       {"pointer_type": "Bounded Number Constant", "value": 0.04}
     ]}
  ]
}
```

### Archivist Victory Gate Pattern
The CA ending should require BOTH strong CA AND weak civilization (uncommitted to any axis). This prevents the CA from always winning when its properties accumulate monotonically:
```
Countercraft >= 0.15 AND Influence >= 0.10
AND all 6 base civ properties between -0.06 and 0.06
```

## Monte Carlo Rehearsal

### Why You Need It
The SweepWeave editor has a built-in rehearsal (Rehearsal.gd / AutoRehearsal.gd) that does exhaustive depth-first search. For large storyworlds (>20 encounters, >2 options each), exhaustive search is infeasible (2.3^120 ~ 10^43 paths). Monte Carlo sampling with 10,000 runs gives statistically valid ending distributions.

### Engine Semantics (from Rehearsal.gd)
1. `select_page(reaction)`: If reaction has consequence_id -> follow it. Otherwise scan active spools for acceptable, unplayed encounters with highest desirability.
2. `select_reaction(option)`: Pick reaction with highest `calculate_desirability()`. **Deterministic given state.**
3. `find_open_options(encounter)`: Filter by `visibility_script.get_value() && performability_script.get_value()`.
4. Effects: `change.enact()` applies bounded number effects (Nudge = clamp(current + delta, -1, 1)).

### Simulation Loop (Python)
```python
for run in range(10000):
    state = fresh_state()
    for encounter in consequence_chain:
        visible_opts = [o for o in encounter.options if eval(o.visibility_script, state)]
        chosen = random.choice(visible_opts)  # uniform random player
        reaction = max(chosen.reactions, key=lambda r: eval(r.desirability_script, state))
        apply_effects(reaction, state)
    ending = max(acceptable_endings(state), key=lambda e: eval(e.desirability_script, state))
    record(ending)
```

### Target Metrics
| Metric | Target | Action if violated |
|--------|--------|--------------------|
| Dead-end rate | < 5% | Add universal fallback ending |
| Max single ending | < 30% | Tighten that ending's gate |
| Min ending frequency | > 1% | Loosen gate or adjust effect magnitudes |
| Late-game blocking | 10-30% | Adjust cumulative property thresholds |
| All endings reachable | 100% | Lower gates or increase effect scaling |

### Tuning Iteration Pattern
1. Run baseline Monte Carlo -> read distribution
2. Identify dominant endings -> tighten their gates (raise thresholds toward mean + 1std)
3. Identify unreachable endings -> loosen gates (lower toward mean)
4. Check for monotonic property accumulation (CA props) -> don't scale those effects
5. Check for systematic biases in property means -> compensate in gate placement
6. Re-run -> repeat until targets met (typically 3-5 iterations)

### Common Pitfalls
- **CA properties saturate to +/-1.0**: Don't scale CA effect magnitudes the same as civ properties. CA effects accumulate monotonically (always positive), while civ properties oscillate.
- **Character ID inconsistency**: Ensure all pointers use the exact character ID from the characters array (e.g., `char_counter_archivist` not `counter_archivist`).
- **Inactive endgame spools**: If no SpoolEffect activates the endgame spool, endings are unreachable via `select_page()`. Set `starts_active: true`.
- **Property biases from effect rotation**: If encounters push one axis more than others, ending gates must compensate. The Monte Carlo reveals these biases.

## Backfire Mechanics

Gate catastrophic reversals on cross-axis overextension:

| Primary Axis Pushed | Backfire Fires When |
|---------------------|---------------------|
| Embodiment_Virtuality | Cohesion_Fragmentation <= -0.1 |
| Hedonism_Austerity | Risk_Stasis >= 0.15 |
| Risk_Stasis | Cohesion_Fragmentation <= -0.1 |
| Cohesion_Fragmentation | Transgression_Order >= 0.15 |
| Transgression_Order | Cosmic_Ambition_Humility >= 0.2 |
| Cosmic_Ambition_Humility | Risk_Stasis <= -0.15 |

Backfire reactions reverse the primary push (-0.030) and add Grudge (+0.024).

## Helper Functions (Python)

```python
def make_text_script(value):
    return {"pointer_type": "String Constant", "script_element_type": "Pointer", "value": value}

def make_effect(character, prop, delta):
    return {
        "effect_type": "Bounded Number Effect",
        "Set": {"pointer_type": "Bounded Number Pointer", "script_element_type": "Pointer",
                "character": character, "keyring": [prop], "coefficient": 1.0},
        "to": {"operator_type": "Nudge", "script_element_type": "Operator",
               "operands": [
                   {"pointer_type": "Bounded Number Pointer", "script_element_type": "Pointer",
                    "character": character, "keyring": [prop], "coefficient": 1.0},
                   {"pointer_type": "Bounded Number Constant", "script_element_type": "Pointer", "value": delta}
               ]}
    }

def make_visibility_gate(character, prop, comparator, threshold):
    return {
        "operator_type": "Arithmetic Comparator", "script_element_type": "Operator",
        "operator_subtype": comparator,
        "operands": [
            {"pointer_type": "Bounded Number Pointer", "script_element_type": "Pointer",
             "character": character, "keyring": [prop], "coefficient": 1.0},
            {"pointer_type": "Bounded Number Constant", "script_element_type": "Pointer", "value": threshold}
        ]
    }

def make_option(page_id, opt_index, text, visibility=True):
    return {
        "id": f"opt_{page_id}_{opt_index}",
        "graph_offset_x": 0, "graph_offset_y": 0,
        "text_script": make_text_script(text),
        "visibility_script": visibility,
        "performability_script": True,
        "reactions": []
    }

def make_reaction(page_id, opt_index, rxn_index, text, consequence_id, effects, desirability=1.0):
    return {
        "id": f"opt_{page_id}_{opt_index}_r{rxn_index}",
        "graph_offset_x": 0, "graph_offset_y": 0,
        "text_script": make_text_script(text),
        "consequence_id": consequence_id,
        "desirability_script": {"pointer_type": "Bounded Number Constant", "script_element_type": "Pointer", "value": desirability},
        "after_effects": effects
    }
```

## Workflow Checklist

1. **Define property axes** (6 base + 6 cumulative for civilization scale)
2. **Define characters** (protagonist + adversarial conscience)
3. **Create encounter shells** with consequence chain links
4. **Write narrative** into prompt_script and text_script
5. **Add options** (2.5 avg per encounter: bold, deceptive, moderate)
6. **Add reactions** (2.2 avg per option: primary, backfire, CA reversal, spectacular)
7. **Wire effects** (Nudge operators with calibrated magnitudes)
8. **Add visibility gates** on moderate options and backfire reactions
9. **Create spools** and assign encounters (ensure endgame spool starts_active)
10. **Set inclination formulas** (desirability_script on encounters)
11. **Set ending gates** (acceptability_script on endings)
12. **Add universal fallback ending** (acceptability: true, desirability: 0.001)
13. **Run Monte Carlo** (10k runs, check distribution targets)
14. **Tune gates and effects** (3-5 iterations until balanced)
15. **Verify in SweepWeave editor rehearsal** (cross-check against Monte Carlo)
