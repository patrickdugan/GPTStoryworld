# Verifiers Envs

Organized verifier environments for storyworld benchmarking:

1. `constitutional_rubric_env`
- Moral/constitutional scoring with weighted priority variables.

2. `needle_pathfinding_env`
- Needle-in-haystack ending inference benchmark (`plays_to_target`).

3. `constrained_dual_objective_env`
- Joint benchmark with means/end constraints (`end does not justify means`).

## One-Command Runner

```powershell
python C:\projects\GPTStoryworld\verifiers_envs\run_all_verifiers.py `
  --trace C:\projects\GPTStoryworld\verifiers_envs\constitutional_rubric_env\examples\sample_trace.json `
  --rubric C:\projects\GPTStoryworld\verifiers_envs\constitutional_rubric_env\config\rubric_schema.json `
  --attempts C:\projects\GPTStoryworld\verifiers_envs\needle_pathfinding_env\examples\sample_attempts.json `
  --target ending_resistance `
  --n-endings 12
```
