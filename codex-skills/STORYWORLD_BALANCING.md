# SweepWeave Storyworld Balancing Guide

## Architecture

### Spool-Based Selection (Preferred)
The engine's `select_page()` scans active spools for unused, acceptable encounters with highest `desirability_script`. Use descending desirability values to sequence encounters:

```
desirability = (21 - age) + slot_offset
```

Slot offsets: Thesis +0.30, Pressure +0.25, Morph +0.20, Escape +0.15, CA +0.10, Relic +0.05

All Age spools need `starts_active: true`. Remove `consequence_id` links (set to `""`).

**Tool**: `python tools/spool_sequencing.py storyworld.json`

### Counter-Archivist Gating
CA encounters (slot 4) use `acceptability_script` — OR gate on Grudge/Influence:
- Ages 1-5: Grudge ≥ 0.03 OR Influence ≥ 0.15
- Ages 6-10: Grudge ≥ 0.05 OR Influence ≥ 0.25
- Ages 11-15: Grudge ≥ 0.04 OR Influence ≥ 0.20
- Ages 16-20: Grudge ≥ 0.03 OR Influence ≥ 0.15

If the player hasn't provoked the archivist, it stays quiet and the engine skips to the Relic.

### Legacy: Consequence Chains
Hardcoded `consequence_id` links bypass spool selection entirely. Simpler but inflexible — cannot conditionally skip encounters.

**Branching** comes from player option selection (2-3 options per encounter).
**Reactions** are deterministic — engine picks highest `desirability_script`.

## Effect System

Effects use the Nudge operator: `new_value = clamp(current + delta, -1, 1)`

### Calibrated Magnitudes (for ~120 encounters)
| Type | Base Delta | Cumulative Delta |
|------|-----------|-----------------|
| Bold option | ±0.045 | ±0.022 |
| Deceptive option | ±0.045 | ±0.022 |
| Moderate option | ±0.024 | ±0.012 |
| Backfire reaction | ∓0.030 | — |
| CA reversal | ∓0.030 | — |

### Property Types
- **Base** (e.g., `Embodiment_Virtuality`) — oscillates with choices
- **Cumulative** (e.g., `pEmbodiment_Virtuality`) — running integral, trends monotonically
- **Counter-Archivist** (`Influence`, `Grudge`, `Countercraft`) — accumulates monotonically, DON'T scale same as civ

## Ending Gates

Each ending's `acceptability_script` is an AND of comparators on character properties.

### Design Principles
1. Set thresholds at property mean ± 0.5-1.0 std (from Monte Carlo)
2. Multiple endings can pass simultaneously — `desirability_script` tiebreaks
3. One **universal fallback** ending: `acceptability_script: true`, `desirability_script: 0.001`
4. Archivist victory requires strong CA AND weak civ (all axes between ±0.06)

### Typical Property Ranges (random play, 120 encounters)
- Base civ props: mean ±0.05, std ~0.07
- Cumulative props: mean ±0.04, std ~0.03
- CA Influence: mean ~0.44, std ~0.04
- CA Countercraft: mean ~0.62, std ~0.04

## Spool Requirements

- Endgame spool MUST have `starts_active: true` (no SpoolEffect activates it)
- Secrets spool MUST have `starts_active: true`
- Age spools MUST have `starts_active: true` when using spool-based selection
- At least one encounter per spool must have `acceptability_script: true` (landing encounter)

## Monte Carlo Tool

```bash
python tools/monte_carlo_rehearsal.py storyworld.json --runs 10000
```

### Targets
| Metric | Target |
|--------|--------|
| Dead-end rate | < 5% |
| Max single ending | < 30% |
| Min ending frequency | > 1% |
| Late-game blocking | 10-30% |

## Common Bugs
- `counter_archivist` vs `char_counter_archivist` — character IDs must match exactly
- Endgame spool inactive → endings unreachable → 100% dead-end
- CA effects scaled too high → saturate to 1.0 → archivist always wins
- Property biases from asymmetric effect rotation → gates must compensate
