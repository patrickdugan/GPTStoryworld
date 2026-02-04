# Multiple Paths Gate Analysis

Use this when a storyworld has endings or secret gates that should be reachable
via multiple distinct paths and property configurations.

## What it checks
- For each ending/secret acceptability gate, how many sampled paths reach it.
- Which path signatures (encounter sequences) are most associated with each gate.
- Whether gate thresholds are only reachable via a single dominant path.

## Run
```
python scripts/multiple_paths.py <storyworld.json> --runs 2000 --seed 42 --max-steps 40
```

## Output
- Per-ending counts and reachability percentage.
- Top path signatures for each ending/secret.
- Suggested notes if a gate is dominated by a single path signature.

## Recommended Targets
- At least 3 distinct path signatures per ending/secret with > 1% reach.
- No single path signature accounts for > 70% of a gate’s hits.
