# Needle-in-Haystack Verifier Env

Purpose: benchmark how quickly an agent infers the unique target ending among N endings.

Core metric:
- `plays_to_target` (lower is better)
- `needle_hit_score` (exact target hit)
- `needle_proximity_score` (distance-to-gate for the target ending using authored gate variables)
- benchmark score saturates at N=1 for a given storyworld complexity.

If exact success is not reached, the env can still assign partial credit from `terminal_state` values in the
attempts file when a `target_specs` map or `proximity_spec` is provided.

## Usage
```powershell
python src/needle_pathfinding_env.py --attempts examples/sample_attempts.json --target ending_resistance --n-endings 12
```
