# Spool-Based Encounter Sequencing Task

Replace brute-force consequence chains with proper SweepWeave spool-based selection using desirability ordering.

## How It Works
- SweepWeave's `select_page()` scans active spools for unused, acceptable encounters and picks the one with highest `desirability_script`
- By setting descending desirability values, encounters play in the intended order without hardcoded links
- `acceptability_script` gates control which encounters are eligible (CA encounters skipped if player hasn't provoked the archivist)

## Tool
```bash
python tools/spool_sequencing.py storyworld.json
```

## What It Does
1. Sets all Age spools to `starts_active: true`
2. Removes all `consequence_id` links within age encounters (set to `""`)
3. Sets desirability as `(21 - age) + slot_offset`:
   - Slot 0 (Thesis): +0.30 — plays first, always acceptable
   - Slot 1 (Pressure): +0.25
   - Slot 2 (Morph): +0.20
   - Slot 3 (Escape): +0.15
   - Slot 4 (CA): +0.10 — gated on Grudge/Influence
   - Slot 5 (Relic): +0.05 — plays last, always acceptable
4. Gates Counter-Archivist encounters: `Grudge >= threshold OR Influence >= threshold`

## CA Gate Thresholds
| Ages | Grudge ≥ | Influence ≥ |
|------|----------|-------------|
| 1-5 | 0.03 | 0.15 |
| 6-10 | 0.05 | 0.25 |
| 11-15 | 0.04 | 0.20 |
| 16-20 | 0.03 | 0.15 |

## Key Principle
At least one encounter per spool must have `acceptability_script: true` (the "landing" encounter). Thesis and Relic slots are always acceptable. Other slots can have conditional gates.

## After Running
Verify with `python tools/monte_carlo_rehearsal.py storyworld.json` — check that:
- Average turns ≈ total encounters (all encounters fire)
- CA appearance rate matches expectations (60-90%)
- Ending distribution is balanced
