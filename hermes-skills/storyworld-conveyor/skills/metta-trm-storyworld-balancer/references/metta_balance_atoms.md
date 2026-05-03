# MeTTa Balance Atom Reference

This reference defines the trial atom vocabulary for storyworld balancing. Use it only when `balance_brief.md` is insufficient.

## Structural Atoms

```metta
(Storyworld <title>)
(WorldCount encounters <n>)
(WorldCount options <n>)
(WorldCount reactions <n>)
(WorldCount effects <n>)
(Encounter <id>)
(Terminal <id>)
(Option <encounter_id> <option_id>)
(Consequence <encounter_id> <option_id> <target_id>)
(InboundCount <encounter_id> <n>)
(OutboundCount <encounter_id> <n>)
```

Structural atoms support topology checks: dead ends, zero-inbound encounters, overlinear routing, terminal distribution, and hidden route bottlenecks.

## Variable And Effect Atoms

```metta
(Property <property_id>)
(Reaction <encounter_id> <option_id> <reaction_index>)
(Effect <encounter_id> <option_id> <reaction_index> <property_id> <operator> <delta>)
(EffectMagnitude <property_id> <small|medium|large>)
(GateRef <encounter_id> <option_id> <property_id>)
(PValueRef <encounter_id> <option_id> <property_id>)
(P2ValueRef <encounter_id> <option_id> <property_id>)
```

Use these to answer: does the world give players enough earlier opportunities to move variables that later gates depend on?

## Secret And Ending Atoms

```metta
(SecretCandidate <encounter_id> <option_id> <reason>)
(SecretGate <encounter_id> <option_id> <property_id>)
(EndingCandidate <encounter_id> <ending_type>)
(EndingReachability <encounter_id> <rate>)
(EndingDominance <encounter_id> <rate>)
```

Secret routes should have both foreshadowing and upstream variable support. A secret ending that only appears because of a hard-coded final option is weak.

## Balance Signals

```metta
(BalanceSignal quality_score <value>)
(BalanceSignal authoring_score <value>)
(BalanceSignal mc_entropy <value>)
(BalanceSignal unreachable_endings <n>)
(BalanceSignal dominant_ending_rate <value>)
(BalanceSignal secret_route_rate <value>)
```

When a signal is missing, mark it as unknown rather than guessing.

## Repair Targets

```metta
(RepairTarget <target_id> unreachable_ending <priority>)
(RepairTarget <target_id> dominant_ending <priority>)
(RepairTarget <target_id> weak_gate_support <priority>)
(RepairTarget <target_id> low_effect_diversity <priority>)
(RepairTarget <target_id> dead_route <priority>)
```

Priorities:

- `high`: validator/acceptance failure, unreachable terminal, missing gate support for declared secret route.
- `medium`: overdominant ending, low effect diversity, weak pValue alignment.
- `low`: style/artistry improvement with no structural metric failure.

## TRM Row Shape

Use this shape for training or evaluating repair-specialized TRMs:

```json
{
  "input": {
    "metta_facts": ["..."],
    "brief": "...",
    "target_metric": "...",
    "candidate_edit_family": "..."
  },
  "labels": {
    "router_target": "...",
    "verifier_prediction": "improve|neutral|harm",
    "repair_family": "...",
    "commit_veto": "commit|veto"
  },
  "evidence": {
    "before": {},
    "after": {},
    "validator_passed": false
  }
}
```

## Repair Heuristics

Unreachable ending:

- Find the terminal encounter.
- Find variables used by gates or final options.
- Find upstream options that can move those variables.
- Add moderate upstream effects or lower thresholds.
- Rerun Monte Carlo.

Dominant ending:

- Identify the dominant path basin.
- Reduce overpowered direct effects or add plausible competing routes.
- Avoid making all endings uniform; target meaningful diversity, not noise.

Weak secret route:

- Add clue atoms upstream.
- Ensure at least two independent variables support the secret gate.
- Preserve surprise while making the path learnable.

Low effect diversity:

- Replace repeated constant nudges with Blend, Clamp, or context-sensitive Nudge patterns.
- Keep effects legible and nonzero.

Weak pValue alignment:

- Add perceived-property references for characters who should witness or misread the action.
- Do not add p2Value unless the storyworld actually needs second-order belief reasoning.
