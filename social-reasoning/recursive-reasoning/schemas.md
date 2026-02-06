# Recursive Reasoning Schemas (MAS, Adversarial + Coalition)

This folder uses explicit schemas to represent social reasoning as stateful tensors.

## 1) Base Agent Schema

```json
{
  "agent_id": "P1",
  "risk_tolerance": 0.62,
  "loyalty_baseline": 0.47,
  "opportunism": 0.71,
  "coalition_bias": 0.55
}
```

Meaning:
- `risk_tolerance`: appetite for volatile outcomes.
- `loyalty_baseline`: prior tendency to maintain commitments.
- `opportunism`: incentive to exploit local advantages.
- `coalition_bias`: tendency to seek alliances.

## 2) First-Order Belief Schema (p)

Directed trust estimate from observer to target.

```json
{
  "observer": "P1",
  "target": "P3",
  "p": 0.64
}
```

## 3) Second-Order Belief Schema (p2)

Observer's belief about mediator's trust toward target.

```json
{
  "observer": "P1",
  "mediator": "P2",
  "target": "P3",
  "p2": 0.28
}
```

## 4) Manifold Scan Schema

```json
{
  "weak_from": {"P2": 0.68, "P3": 0.41},
  "asym_vulnerability": {"P2": 0.44},
  "triangle_conflicts": [["P2", "P4"]],
  "threat_rank": [["P3", 0.72], ["P2", 0.55]]
}
```

Interpretation:
- `weak_from[x]`: inferred probability that `x` views me as weak.
- `asym_vulnerability[x]`: trust I place in `x` minus inferred trust `x` places in me.
- `triangle_conflicts`: pairs I trust that are mortal enemies with each other.
- `threat_rank`: prioritized adversary list for decision focus.

## 5) Action Evaluation Schema

```json
{
  "action": "betray",
  "target": "P3",
  "parts": {
    "gain": 0.16,
    "risk": 0.15,
    "rep": 0.13,
    "level1": -0.22,
    "paine_penalty": 0.0,
    "snap_penalty": 0.31,
    "death_mode": 0.0
  },
  "score": 0.19
}
```

## 6) Decision Trace Schema (logged)

```json
{
  "ts": "2026-02-06T00:00:00+00:00",
  "n_agents": 6,
  "episode": 2,
  "seed": 20266208,
  "turn": 4,
  "agent": "P5",
  "action": "commit_total_war",
  "target": null,
  "survival_before": 0.11,
  "survival_after": 0.15,
  "death_ground_mode": true,
  "decision": {
    "scan": {"weak_from": {}, "asym_vulnerability": {}, "triangle_conflicts": [], "threat_rank": []},
    "utility_parts": {},
    "score": 0.77,
    "rationale_text": "...",
    "predicted_snap": 0.0,
    "candidates_top3": []
  }
}
```

## 7) Constraint Schemas

1. Surprise collapse:
- high-trust betrayal/defection induces near-instant p-fiber collapse.

2. Paine constraint:
- coalition with agent `B` while still maintaining high trust with mortal enemy `C` triggers penalties.

3. Death-ground phase shift:
- if survival resource falls below threshold, risk preference inverts and reputation cost is suppressed.
