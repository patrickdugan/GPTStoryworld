# Small-Model Storyworld Builder Bench

This benchmark is for testing whether smaller models build better storyworlds when they are used inside the MCP + native-schema + TRM conveyor rather than as one-shot JSON authors.

The key claim to test is not "a small model becomes a great novelist." The claim is:

> A small model can bench better as a bounded local proposal engine when native control routing, MCP packetization, deterministic materialization, and verifier-driven repair own the hard control-plane work.

## Conditions To Compare

Use the same source prompt or adaptation target across conditions:

1. `naive_json`: ask the small model for the whole storyworld JSON.
2. `packet_author`: ask the model for bounded design packets only.
3. `packet_author_native`: use bounded packets plus the native master-control schema.
4. `packet_author_native_repair`: add verifier-visible repair loops and commit/veto.
5. `packet_author_native_trm`: distill native routing and repair outcomes into learned TRM control rows.

The expected result is that smaller models improve most when they stop owning:

- whole-world planning;
- schema mechanics;
- commit/veto;
- context selection;
- effect/gate repair policy.

## Metrics

The offline scorecard separates:

- `validity`: parseable JSON and core SweepWeave fields.
- `scale`: encounter and ending count.
- `branching`: options, reactions, and effects per local unit.
- `control_logic`: gated choices, operator variety, and nonconstant effects.
- `text_surface`: local text length and uniqueness.
- `small_model_readiness`: whether the artifact has evidence of bounded context use.
- `native_schema`: whether native routing agreement is available for the run.

This is intentionally not a final human-quality judge. It is a fast optimization target for small-model runs.

## Smoke Run

```powershell
python benchmarks\storyworld_builder_small_model\score_small_model_storyworld_builder.py `
  --manifest benchmarks\storyworld_builder_small_model\sample_manifest.jsonl `
  --out-dir benchmarks\storyworld_builder_small_model\runs\smoke_001
```

Outputs:

- `scorecard.json`
- `scorecard.csv`
- `scorecard.md`

## How This Helps Smaller Models

Use the scorecard to find the worst component, then route the next small-model call narrowly:

- Low `validity`: do not ask the LLM for JSON; ask for packet fields and materialize deterministically.
- Low `branching`: ask for option/reaction/effect slots only.
- Low `control_logic`: route through `effect_script_synthesizer` or `gate_secret_route_designer`.
- Low `text_surface`: ask for bounded prose rewrites only after mechanics are stable.
- Low `small_model_readiness`: run MCP preflight before any model call.
- Low `native_schema`: run the native schema planner and append teacher rows.

This creates a repeatable path for turning 3B/9B failures into training rows rather than subjective postmortems.
