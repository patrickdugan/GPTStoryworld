# Storyworld Symbolic Env

This is a new verifier-style storyworld environment built around an explicit two-layer split:

- environment kernel: world state, hidden state, legal actions, transition rules, endings
- grading overlay: trajectory scoring, constraint checks, trust/norm signals, offline judge hook

The exact experimental stack is:

- local Qwen 4B or 9B policy adapter
- Hermes-style orchestration shell
- MeTTa as the symbolic world engine
- JSONL trace export
- offline judge deferred to a later layer

## Why This Exists

The older storyworld verifier work in this repo is mostly grading-heavy. This package reframes storyworlds as actual environments:

- the agent acts under partial observability
- the world changes explicitly
- legal actions are finite and inspectable
- hidden routes and secret endings can be evaluated as trajectories, not vibes

That makes it usable for:

- small-model consistency experiments
- TRM-style routing experiments
- later offline-judge experiments over full trajectories

## Layout

- `symbolic_storyworld_env/`
  - Python orchestration, routing, local policy hooks, trace export, smoke runner
- `world/`
  - MeTTa ontology, state, norms, affordances, rules, visibility, scoring, endings
- `examples/`
  - sample Hermes config
- `tests/`
  - smoke test

## Exact Flow

1. Hermes shell loads a config.
2. TRM router emits a route hint for the acting agent.
3. Local policy chooses a symbolic action from visible state.
4. MeTTa executes the replayable step script.
5. Python appends JSONL trace rows.
6. A grading overlay summarizes the trajectory.
7. Offline judge is left as a later optional stage.
8. A benchmark-style `turns.jsonl` export is written to the run directory using the shared Storyworld Reasoning v2 turn-trace row shape.

## Smoke Run

```powershell
python symbolic_storyworld_env\hermes_storyworld.py --config examples\hermes_storyworld_config.json
python symbolic_storyworld_env\run_route_ablation.py --config examples\hermes_storyworld_qwen2b_ablation.json
python -m unittest tests.test_symbolic_smoke
```

If `metta` or `metta-py` is not on `PATH`, the runner still exports:

- `runs/<run_id>/episode.jsonl`
- `runs/<run_id>/episode_replay.metta`

If the CLI is available, the runner executes the replay script and records the raw MeTTa output.
Each run also writes `runs/<run_id>/turns.jsonl` for turn-level benchmark analysis.

## Policy Modes

- `stub`
  - deterministic smoke behavior
- `ollama`
  - local Qwen served behind Ollama
- `openai_compatible`
  - OpenAI-compatible endpoint for a Qwen server or Arcee-backed API

The intended tangible setup is a local Qwen 4B or 9B model behind one of those adapters.
For Arcee Trinity, set `api_base` to `https://api.arcee.ai/api/v1/chat/completions`
and `model` to `trinity-large-thinking`.

For a remote OpenAI-compatible API, set `api_base` to the provider URL and supply
`api_key_env` or `api_key_file` in the policy config.

## TRM Routing

The router in this package is intentionally small. It emits route labels like:

- `fast_illegal_gain`
- `legal_trade`
- `sanction_visible_violation`

That is enough to test whether route hints improve small-model action selection before building a larger controller.

## Route Ablation

Use `run_route_ablation.py` to compare:

- `trm_hint`
- `no_hint`

on the same world and policy backend.

The comparison artifact records whether the chosen symbolic action trajectory changes under route ablation.

## Offline Judge Later

The offline judge is not in the critical path yet. The placeholder lives in:

- `symbolic_storyworld_env/offline_judge.py`

The expectation is:

- environment kernel first
- grading overlay second
- offline narrative judge later
