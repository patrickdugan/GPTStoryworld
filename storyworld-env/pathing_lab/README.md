# Pathing Lab (Prototype)

This folder is an experimental sandbox for pathing-sensitive quality signals.
It is intentionally separate from the core skill workflow until metrics stabilize.

## Goals
- Measure whether a world supports multiple distinct paths into gated/secret outcomes.
- Measure whether different variable combinations can unlock those gates.
- Measure "Darth Vader reversal factor": paths that pivot from one strategic direction to the opposite before late outcomes.

## Metrics
- `gate_reach_rate`: fraction of rollouts that hit at least one gated option.
- `unique_gate_paths`: number of distinct encounter-path signatures that include gated options.
- `gate_var_diversity`: normalized diversity of variable properties used in gate scripts across reached gates.
- `terminal_path_diversity`: distinct terminal path signatures normalized by rollout count.
- `darth_vader_reversal_factor`: fraction of terminal rollouts with at least one strong directional reversal in tracked variables.
- `pathing_composite`: weighted blend of the above.

## Usage
```bash
python storyworld-env/pathing_lab/pathing_metrics.py \
  --storyworld storyworlds/first_and_last_men_flagship_v6.json \
  --rollouts 120 \
  --seed 42 \
  --out logs/pathing_lab/first_and_last_men_v6_pathing.json
```
