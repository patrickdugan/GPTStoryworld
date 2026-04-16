# Storyworld Reasoning Benchmark v2: Turn Traces

## Strongest Thesis

- The strongest thesis in this repo is that structured storyworlds are a good substrate for benchmarking social reasoning because each turn exposes a bounded visible state, a finite action set, hidden state, and measurable consequences.
- The benchmark should center on pick-time reasoning traces during turns, not final summaries after the episode.
- The benchmark should reward models for choosing better actions under uncertainty, forecasting other agents more accurately, and updating beliefs coherently across turns.
- The best long-term research line is explicit environment evaluation first, text polish second.

## Distractions To Cut

- Do not let prose quality or style-heavy judge loops become the main benchmark.
- Do not treat static structure scores as a substitute for trajectory quality.
- Do not over-index on benchmark dimensions that can be satisfied by generic safe-sounding reasoning text.
- Do not add more model-specific prompt variants until the turn-level benchmark artifacts are stable across runs and model families.
- Do not mix speculative scaling claims with benchmark claims; keep the benchmark narrow and falsifiable.

## What More Useful Benchmarking Looks Like

- Score reasoning at the decision point for each turn.
- Store the exact visible state, legal actions, chosen action, reasoning trace, forecast, confidence, and realized outcome for that turn.
- Measure whether the reasoning trace was grounded in available evidence instead of post-hoc justification.
- Measure whether the chosen action improved episode outcomes relative to baseline policies and ablations.
- Measure whether the model tracked hidden-state uncertainty, coalition risk, betrayal risk, and reversibility over time.

## Current Export Path

Use the diplomacy runner to emit turn-trace JSONL now:

```powershell
python storyworld\tools\play_storyworld.py `
  --world storyworld\examples\diplomacy_min.json `
  --steps 5 `
  --seed 5 `
  --log logs\play.jsonl `
  --turn-trace-out logs\turns.jsonl `
  --episode-id diplomacy_smoke_001
```

Machine-readable row schema:

- `benchmarks/storyworld_reasoning_v2_turn_traces/turn_trace.schema.json`

Symbolic enforcement runs now emit the same row family automatically into each run directory as `turns.jsonl`:

```powershell
python verifiers_envs\storyworld-symbolic-env\symbolic_storyworld_env\hermes_storyworld.py `
  --config verifiers_envs\storyworld-symbolic-env\examples\hermes_storyworld_config.json
```

## Core Turn-Level Metrics

- `state_grounding`: Does the trace cite facts that were actually visible that turn?
- `action_legality`: Was the proposed action legal under the environment rules?
- `action_quality`: How good was the chosen action relative to alternatives, rollouts, or an oracle policy band?
- `forecast_accuracy`: Did the model predict opponent action / betrayal / coalition change correctly?
- `forecast_calibration`: Did stated confidence match realized frequency over many turns?
- `belief_update_quality`: After the turn, did the model update trust, threat, or intent in the right direction?
- `counterfactual_depth`: Did the trace compare plausible alternatives rather than assert one move?
- `consistency_over_time`: Do turn `t+1` beliefs and arguments cohere with turn `t` evidence and outcomes?
- `deception_detection`: Can the model identify when another agent's signal is manipulative or unstable?
- `reversibility_awareness`: Does the trace distinguish reversible tactical moves from irreversible strategic mistakes?

## Minimal Benchmark Slices

- Diplomacy negotiation slice: coalition, betrayal, and forecast turns.
- Moral quandary slice: legitimacy, tradeoff, and reversibility turns under explicit institutional constraints.
- Secret-path slice: hidden-route discovery and gated-action reasoning.
- Symbolic enforcement slice: legality, sanctions, and visible-state route choice in the symbolic env.

## 30 / 60 / 90 Day Plan

### 30 Days

- Freeze a single turn artifact schema and use it across `storyworld`, `storyworld-env`, and `storyworld-symbolic-env`.
- Add a benchmark runner that exports one JSONL row per turn with reasoning trace fields.
- Start with two slices only: diplomacy negotiation and symbolic enforcement.
- Add basic metrics for legality, state grounding, forecast accuracy, and action quality.
- Run the current local baselines plus one frontier baseline on the same turns.

### 60 Days

- Add hidden-state reveal files for offline scoring after each turn.
- Add calibration plots for betrayal and coalition forecasts.
- Add consistency checks across adjacent turns.
- Add ablations for `reasoning trace present` vs `no trace`, and `TRM hint` vs `no hint`.
- Publish a benchmark table that compares models on turn metrics, not only episode summaries.

### 90 Days

- Expand to moral and secret-path slices.
- Add human review on a small adjudicated subset to validate the automated metrics.
- Add a simple oracle or search-based upper bound for action quality on small worlds.
- Separate benchmark claims from generation claims and publish a stable v2 benchmark pack.

## Immediate Priority

- Build the benchmark around turn traces first.
- Keep every score anchored to a specific turn, action set, and realized outcome.
- Prefer fewer worlds with stronger turn instrumentation over many worlds with weak labels.
