# Needle-in-Haystack Verifier Env

Purpose: benchmark how quickly an agent infers the unique target ending among N endings.

Core metric:
- `plays_to_target` (lower is better)
- benchmark score saturates at N=1 for a given storyworld complexity.

## Usage
```powershell
python src/needle_pathfinding_env.py --attempts examples/sample_attempts.json --target ending_resistance --n-endings 12
```
