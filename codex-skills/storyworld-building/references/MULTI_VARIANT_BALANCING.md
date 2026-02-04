# Multi-Variant Balancing

Use this when a storyworld needs multiple viable endings without oscillating
between a single dominant ending and dead-ends. The goal is to produce a
distribution that is robust across multiple random seeds and path samples.

## Targets (per variant)
- max ending share <= 30%
- min ending share >= 1%
- ending entropy >= 1.5 bits
- effective endings >= 4.0
- secret reachability in 2–8%
- dead-end rate <= 5%

## Procedure
1. Run Monte Carlo at 3 seeds (42, 43, 44).
2. Compare per-ending shares and entropy across variants.
3. If one ending dominates in any variant:
   - tighten its acceptability window (min+max),
   - lower desirability,
   - add counter‑effects in Act II/III to support alternatives.
4. If dead-ends spike:
   - widen the fallback gate or add a permissive ending.
5. Re-run and repeat until all seeds are within targets.

## Run
```
python scripts/multi_variant_balance.py <storyworld.json> --runs 5000 --seeds 42,43,44
```
