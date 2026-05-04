# Native Master Control Schema

This is the symbolic teacher policy for the storyworld factory control plane.

The learned master planner failed because the first baseline tried to infer control flow from sparse synthetic rows. The native schema fixes the control-plane floor by routing from explicit diagnostic predicates. TRMs should learn this schema first, then improve it with real repair outcomes.

## Routing Rules

Priority order:

1. `context_overflow` -> `mcp_context_router`
2. `insufficient_neighbor_context` -> `mcp_context_router`
3. `dangling_consequence` -> `validator_repair_critic`
4. `unsupported_reader_operator` -> `validator_repair_critic`
5. `schema_parse_error` -> `validator_repair_critic`
6. `effect_nudge_monoculture` -> `effect_script_synthesizer`
7. `missing_pvalue_refs` -> `effect_script_synthesizer`
8. `missing_p2value_refs` -> `effect_script_synthesizer`
9. `unreachable_secret` -> `gate_secret_route_designer`
10. `gate_threshold_unforeshadowed` -> `gate_secret_route_designer`
11. `reaction_collapse` -> `reaction_dynamics_mapper`
12. `option_blandness` -> `option_manifold_planner`
13. `too_much_llm_freeform` -> `llm_prompt_composer`
14. `no_metric_delta` -> `commit_veto_controller`

## Design Principle

The native schema is not a replacement for TRMs. It is the minimum viable reasoning skeleton:

- It gives the factory a correct first move.
- It creates clean teacher labels.
- It prevents the LLM from self-certifying.
- It makes 9B viable by routing context before authoring.
- It exposes where learned control should outperform rules.

## Lightning Result

On `master_control_planner_native_schema_local_001`, the native schema routes all current auto-research rows correctly:

```text
16/16 = 1.0 planner agreement
```

This result is not a learned-generalization claim. It is a proof that the control plane needs a native symbolic floor before TRM learning.
