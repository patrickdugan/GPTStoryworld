# Operation Set (Isolated Frame)

Use `SWMD-TRAIN-0.1` as the stable instruction frame around `SWMD-MICRO-0.1` payloads.

## Core transform ops
- `compile`: encounter prose/block -> canonical micro-spec.
- `compression`: reduce to <=5 agents and <=10 state vars.
- `repair`: fix broken schema/IDs/transitions.
- `targeted_edit`: add constraints or incentives without schema drift.

## High-value authoring ops
- `desirability_refine`
  - Input: valid micro-spec with weak desirability expressions.
  - Output: same spec with non-constant desirability formulas (>=2 vars), improved path diversity.
- `ore_saturation_design`
  - Input: under-saturated encounter graph.
  - Output: tuned options/reactions/effects targets (for example 3 / 2.5 / 4) with logic-only scripts.
- `spool_flow_rewrite`
  - Input: flat or inconsistent encounter flow.
  - Output: explicit spool/act graph with coherent progression and deterministic IDs.

## Structural/diagnostic ops
- `transition_extract`: emit irreversible transitions and terminal paths from the same source.
- `gate_schedule_edit`: enforce staged gating targets (for example Act III/IV/V percentages).
- `operator_mix_tune`: normalize effect operator mix (nudge-dominant, sparse blend/invert).
- `id_stability_repair`: recover deterministic encounter/option/reaction IDs.
- `schema_normalize`: canonical key order/newline/typing normalization.

## Frame pattern
```json
{
  "schema": "SWMD-TRAIN-0.1",
  "operation": "desirability_refine",
  "input_spec": { "...": "SWMD-MICRO-0.1 object" },
  "constraints": {
    "keep_ids_stable": true,
    "no_constant_desirability": true,
    "min_desirability_vars": 2
  }
}
```
