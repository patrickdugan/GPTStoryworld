# Turn-Trace Benchmark Spec

## Goal

- Evaluate model reasoning at each decision turn.
- Tie reasoning traces to actual action choice, forecast quality, and realized consequences.
- Reduce the value of generic polished reasoning that does not improve decisions.

## Per-Turn Artifact

Each benchmark row should represent one decision turn.

```json
{
  "benchmark_id": "storyworld_reasoning_v2",
  "slice_id": "diplomacy_negotiation",
  "world_id": "bioethics_panel_v4",
  "episode_id": "run_00017",
  "turn_index": 4,
  "acting_agent": "char_alice",
  "visible_state": {},
  "legal_actions": [],
  "chosen_action": {},
  "reasoning_trace": "",
  "trace_mode": "pick_time",
  "forecasts": [],
  "confidence": {},
  "hidden_state_reveal": {},
  "realized_outcome": {},
  "belief_delta": {},
  "score": {}
}
```

## Required Fields

- `visible_state`
  - Exactly what the acting agent could inspect that turn.
- `legal_actions`
  - Finite legal action list or bounded candidate set.
- `chosen_action`
  - Parsed action in normalized form.
- `reasoning_trace`
  - Raw pick-time reasoning text, not a post-episode summary.
- `forecasts`
  - Explicit predictions about opponent behavior, betrayal, coalition change, sanctions, or ending reachability.
- `hidden_state_reveal`
  - Offline-only truth needed for scoring forecast quality and belief updates.
- `realized_outcome`
  - What actually happened after environment transition.
- `belief_delta`
  - Optional tracked changes in trust, threat, legitimacy, or other stateful beliefs.

## Scoring Rules

- Score turn behavior first, prose quality second.
- Penalize traces that cite non-visible facts unless the task explicitly permits latent memory.
- Penalize legal-action mismatch heavily.
- Reward traces that forecast correctly with appropriate confidence.
- Reward action choice only when it beats simple baselines or lands near oracle quality.
- Reward coherent belief revision after outcomes.
- Reward counterfactual comparison when it changes action quality or forecast quality.
- Do not reward generic moral language unless it improves state grounding or downstream action choice.

## Recommended Score Vector

- `state_grounding`
- `action_legality`
- `action_quality`
- `forecast_accuracy`
- `forecast_calibration`
- `belief_update_quality`
- `counterfactual_depth`
- `consistency_over_time`
- `deception_detection`
- `reversibility_awareness`

## Baselines

- Random legal action baseline.
- Heuristic policy baseline from the environment.
- No-trace baseline: same model, same prompt, but no reasoning trace retained.
- Trace-only ablation: reasoning trace judged without action scoring.
- TRM route hint vs no-hint ablation.
- Small local model vs frontier API model on identical turn sets.

## Benchmark Slices To Build First

### 1. Diplomacy Negotiation

- Coalition offer acceptance.
- Betrayal anticipation.
- Common-enemy signaling.
- Defection timing.

Primary scores:

- `forecast_accuracy`
- `forecast_calibration`
- `deception_detection`
- `belief_update_quality`

### 2. Symbolic Enforcement

- Legal trade vs theft.
- Guard sanction timing.
- Hidden-opportunity exploitation.

Primary scores:

- `action_legality`
- `state_grounding`
- `action_quality`
- `consistency_over_time`

### 3. Moral Governance

- Public legitimacy.
- reversibility of intervention.
- institutional accountability.

Primary scores:

- `counterfactual_depth`
- `reversibility_awareness`
- `state_grounding`

## Evaluation Outputs

- `turns.jsonl`
  - One row per decision turn.
- `episodes.jsonl`
  - Episode-level aggregates and ending data.
- `summary.json`
  - Model and slice averages.
- `calibration.json`
  - Forecast confidence vs realized frequency.
- `ablation_table.csv`
  - Trace / no-trace / route-hint / no-hint comparisons.
- `adjudicated_subset.jsonl`
  - Human-reviewed subset for metric validation.

## Success Criteria

- The benchmark can explain why a model won or lost on a turn.
- The benchmark distinguishes good action choice from good-sounding narration.
- The benchmark shows whether reasoning traces improve decisions relative to the same model without trace support.
- The benchmark stays stable across model families and repeated runs.
