# Monte Carlo Balancing Task

Run `tools/monte_carlo_rehearsal.py` against the target storyworld JSON to get ending distributions, then iteratively tune ending gates and effect magnitudes.

## Usage
```bash
python tools/monte_carlo_rehearsal.py path/to/storyworld.json --runs 10000
```

## Tuning Targets
- Dead-end rate < 5% (add universal fallback ending if violated)
- No single ending > 30%
- All endings reachable (> 1%)
- Late-game blocking 10-30%

## Tuning Levers
1. **Ending acceptability gates** — AND of Arithmetic Comparators on character properties
2. **Effect magnitudes** — Nudge operator delta values in after_effects
3. **Desirability formulas** — on endings, controls tiebreaking when multiple pass
4. **Late-game encounter gates** — cumulative property thresholds on acceptability_script

## Iteration Pattern
1. Run Monte Carlo → read histogram
2. Dominant ending → raise its gate thresholds toward mean + 1 std
3. Unreachable ending → lower thresholds toward mean
4. Dead ends → widen fallback ending gate or add `acceptability_script: true`
5. Re-run → repeat 3-5 times

## Key Gotchas
- Counter-Archivist properties accumulate monotonically — don't scale them same as civ
- Character IDs must match exactly (e.g., `char_counter_archivist` not `counter_archivist`)
- Endgame spool needs `starts_active: true` if no SpoolEffect activates it
- Consequence chains bypass spool selection — spools only matter at "wild" terminus
